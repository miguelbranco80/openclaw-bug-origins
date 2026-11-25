"""GitHub reads through the `gh` command, with the failures that long runs meet handled in one place.

Everything here is read-only. A call either returns data or raises Paused with what to do:
  not signed in        -> Paused at once ("run: gh auth login")
  hourly limit reached -> waits for the reset when it is within limits.max_wait_minutes, else Paused
  secondary limit, network error, server error -> retried with growing pauses, then Paused
"""
import json
import subprocess
import time

from .settings import Paused, say, settings

AUTH = ("gh auth login", "authentication", "HTTP 401", "Bad credentials", "not logged in")
LIMIT = ("rate limit", "API rate limit exceeded", "RATE_LIMITED")
SECONDARY = ("secondary rate limit", "abuse", "HTTP 403", "HTTP 429")
TRANSIENT = ("HTTP 5", "timeout", "timed out", "connection", "EOF", "TLS", "temporarily", "something went wrong",
             "could not resolve host", "network")


def _call(args, stdin=None):
    run = subprocess.run(["gh", *args], capture_output=True, text=True, input=stdin)
    return run.returncode, run.stdout, run.stderr


def budget(resource="graphql"):
    """(calls left this hour, seconds until the limit resets) for 'graphql' or 'core' (REST)."""
    code, out, err = _call(["api", "rate_limit"])
    if code != 0:
        if any(mark.lower() in err.lower() for mark in AUTH):
            raise Paused("the GitHub command line tool is not signed in. Run: gh auth login")
        raise Paused(f"cannot reach GitHub ({err.strip()[:200]})")
    limits = json.loads(out)["resources"][resource]
    return limits["remaining"], max(0, limits["reset"] - int(time.time()))


def _wait_for_budget(resource):
    limits = settings()["limits"]
    remaining, seconds = budget(resource)
    if remaining > limits["github_reserve"]:
        return
    if seconds > limits["max_wait_minutes"] * 60:
        raise Paused(f"GitHub's hourly {resource} limit is used up; it resets in {seconds // 60} minutes")
    say(f"  GitHub {resource} limit nearly used ({remaining} left); waiting {seconds // 60 + 1} minutes for the reset")
    time.sleep(seconds + 5)


def _run(args, resource, tolerate_errors=False):
    """Run one gh api call and return parsed JSON."""
    pause = 5
    for attempt in range(7):
        code, out, err = _call(args)
        text = (err + out[:2000]).lower()
        data = None
        try:
            data = json.loads(out) if out.strip() else None
        except ValueError:
            pass
        if any(mark.lower() in text for mark in AUTH):
            raise Paused("the GitHub command line tool is not signed in. Run: gh auth login")
        limited = any(mark.lower() in text for mark in LIMIT + SECONDARY)
        if data is not None and not limited and (code == 0 or tolerate_errors):
            return data
        if limited:
            _wait_for_budget(resource)
        elif code != 0 and not any(mark.lower() in text for mark in TRANSIENT):
            raise RuntimeError(f"gh {' '.join(args)[:120]} failed: {err.strip()[:300]}")
        time.sleep(pause)
        pause = min(pause * 2, 300)
    raise Paused(f"GitHub kept failing ({(err or out).strip()[:200]})")


def graphql(query, tolerate_errors=False, **variables):
    """A GraphQL query. Integer variables are sent as numbers. With tolerate_errors, partial data is returned
    (GitHub answers "not found" for one alias with an error beside the data for the others)."""
    args = ["api", "graphql", "-f", "query=" + query]
    for name, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", f"{name}={value}"]
    return _run(args, "graphql", tolerate_errors)


def rest(path):
    """A REST GET, for example repos/openclaw/openclaw/pulls/123."""
    return _run(["api", path], "core")
