"""Run one prompt through one model, and tell apart the ways a run can fail.

Three ways to run a prompt ("backends"), chosen per judging step in study.json:
  codex   the Codex command line tool, headless, read-only sandbox, no network, the user's config ignored
  claude  the Claude Code command line tool, headless, with only reading tools (and read-only git when allowed)
  agent   no tool is called: the prompt is written to a file as a work order for the operating agent to hand to a
          fresh subagent (see PROTOCOL.md, "Model steps without a command line tool")

A run ends in one of four ways:
  an answer            the model's final message, returned as text
  Paused               the tool is signed out: nothing more can run until someone signs in
  Limited              a usage or rate limit: the caller waits and retries, then pauses
  RunFailed            anything else (timeout, crash, empty answer): the caller retries once, then records a failure
"""
import json
import os
import re
import shutil
import subprocess

from .settings import Paused, git_env

AUTH_MARKS = ("failed to authenticate", "oauth session expired", "not logged in", "please run /login",
              "invalid api key", "401 unauthorized", "authentication_error", "codex login", "log in again",
              "token is expired", "refresh token")
LIMIT_MARKS = ("usage limit", "rate limit", "rate_limit", "429", "too many requests", "quota", "overloaded",
               "529", "at capacity", "try again in", "try again at", "limit reached", "credit balance")
SIGN_IN = {"codex": "codex login", "claude": "claude auth login (or start `claude` and type /login)"}


class Limited(Exception):
    """A usage or rate limit was hit; trying again later may work."""


class RunFailed(Exception):
    """The run produced no usable answer for a reason that is not sign-in or a limit."""


def signed_in(backend):
    """(True/False/None, detail). None means the tool is not installed."""
    if backend == "agent":
        return True, "work orders for the operating agent; no tool needed"
    if not shutil.which(backend):
        return None, f"`{backend}` is not installed"
    if backend == "codex":
        run = subprocess.run(["codex", "login", "status"], capture_output=True, text=True)
        text = (run.stdout + run.stderr).strip()
        return run.returncode == 0 and "logged in" in text.lower(), text.splitlines()[0] if text else "no answer"
    run = subprocess.run(["claude", "auth", "status"], capture_output=True, text=True)
    try:
        return bool(json.loads(run.stdout).get("loggedIn")), run.stdout.strip().replace("\n", " ")[:120]
    except ValueError:
        return False, (run.stdout + run.stderr).strip()[:120]


def _classify(backend, text):
    low = text.lower()
    if any(mark in low for mark in AUTH_MARKS):
        raise Paused(f"`{backend}` is signed out. Run: {SIGN_IN[backend]}")
    if any(mark in low for mark in LIMIT_MARKS):
        raise Limited(f"`{backend}` reported a usage or rate limit: {_tail(text)}")


def _tail(text, size=240):
    return " ".join(text.split())[-size:]


def run(backend, model, prompt, cwd, log_dir, *, effort="medium", timeout=1800, read_dirs=(), git=False, gh=False):
    """Return the model's final message. `cwd` is where it works; `read_dirs` are other folders it may read.
    `git` allows read-only git commands; `gh` allows read-only GitHub lookups (claude only: codex runs offline)."""
    os.makedirs(log_dir, exist_ok=True)
    if backend == "codex":
        return _codex(model, prompt, cwd, log_dir, effort, timeout)
    if backend == "claude":
        return _claude(model, prompt, cwd, log_dir, effort, timeout, read_dirs, git, gh)
    raise ValueError(f"unknown backend {backend!r}")


def _codex(model, prompt, cwd, log_dir, effort, timeout):
    last = os.path.join(log_dir, "last.txt")
    if os.path.exists(last):
        os.remove(last)
    command = [
        "codex", "exec", "-m", model, "-s", "read-only", "--skip-git-repo-check", "--ephemeral",
        "--ignore-user-config", "--ignore-rules", "--json",
        "-c", f"model_reasoning_effort={effort}", "-c", "project_doc_max_bytes=0", "-c", 'web_search="disabled"',
        "-C", cwd, "-o", last, prompt,
    ]
    events, errors = os.path.join(log_dir, "events.jsonl"), os.path.join(log_dir, "stderr.txt")
    with open(events, "w") as out, open(errors, "w") as err:
        try:
            code = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=out, stderr=err, timeout=timeout,
                                  env=git_env()).returncode
        except subprocess.TimeoutExpired:
            raise RunFailed(f"no answer within {timeout // 60} minutes")
    answer = open(last, errors="replace").read().strip() if os.path.exists(last) else ""
    if code == 0 and answer:
        return answer
    noise = open(errors, errors="replace").read()[-4000:] + " " + _codex_errors(events)
    _classify("codex", noise)
    raise RunFailed(f"codex exited {code} with no answer: {_tail(noise)}")


def _codex_errors(events):
    """The tool's own error events. The rest of the event log is the model's reading matter and is not searched:
    a fix about rate limits must not look like a rate limit."""
    found = []
    with open(events, errors="replace") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            kind = str(event.get("type", "")).lower() if isinstance(event, dict) else ""
            if "error" in kind or "failed" in kind:
                found.append(json.dumps(event)[:600])
    return " ".join(found[-5:])


LOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "look.py")


def _claude(model, prompt, cwd, log_dir, effort, timeout, read_dirs, git, gh):
    # Never raw git or gh: a reader works from strangers' text. Lookups go through look.py, which can only read.
    tools = ["Read", "Grep", "Glob"]
    if git or gh:
        tools += [f"Bash(python3 {LOOK}:*)"]
    command = ["claude", "-p", "--model", model, "--output-format", "json", "--no-session-persistence",
               "--strict-mcp-config", "--effort", effort, "--allowedTools", *tools,
               "--disallowedTools", "Edit", "Write", "NotebookEdit", "WebFetch", "WebSearch", "Agent"]
    for folder in read_dirs:
        command += ["--add-dir", folder]
    try:
        done = subprocess.run(command, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=cwd,
                              env=git_env())
    except subprocess.TimeoutExpired:
        raise RunFailed(f"no answer within {timeout // 60} minutes")
    with open(os.path.join(log_dir, "claude.json"), "w") as handle:
        handle.write(done.stdout)
    with open(os.path.join(log_dir, "stderr.txt"), "w") as handle:
        handle.write(done.stderr)
    try:
        result = json.loads(done.stdout)
    except ValueError:
        result = {}
    answer = (result.get("result") or "").strip()
    api_error = result.get("terminal_reason") == "api_error" or result.get("api_error_status")
    failed = done.returncode != 0 or result.get("is_error") or api_error
    if answer and not failed:
        return answer
    # On an API error the tool puts its own error text in `result`; otherwise `result` is the model's and is not searched.
    noise = (answer if api_error or not result else "") + " " + done.stderr[-4000:]
    _classify("claude", noise)
    raise RunFailed(f"claude exited {done.returncode} with no answer: {_tail(noise)}")


def extract_json(text):
    """The JSON object in a model's final message: the whole message, a fenced block, or the outermost braces."""
    text = text.strip()
    candidates = [text] + re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    if "{" in text and "}" in text:
        candidates.append(text[text.find("{"):text.rfind("}") + 1])
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None
