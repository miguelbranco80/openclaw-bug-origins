"""Every step of the study in which a model makes a judgment, defined in one place.

A judging step is: a list of cases, a brief (a Markdown file in this repository), what the model may read, where its
answer is stored, and what a valid answer looks like. `python3 study.py judge <step>` runs the cases that have no
valid answer yet, so it can be stopped and rerun at any point.

Steps and their briefs:
  origin, origin_second, origin_reread   fix-origins/reader-prompt.md             what a fix repaired, and its cause
  flag, flag_reread                      fix-origins/clawsweeper/reader-prompt.md did the review bot name the bug
  review                                 review-pilot/prompt-whole.md, prompt-per-file.md   blind review of a change
  grade, grade_reread                    review-pilot/grader-prompt.md            did a reviewer name the known bug
  tags                                   review-pilot/tag-prompt.md               what seeing the bug needed
  refute_gpt, refute_opus                review-pilot/refute-prompt.md            is each reported problem real
  laterfix                               review-pilot/laterfix-prompt.md          was each reported problem later fixed
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from . import model
from .settings import (FIX, PILOT, WORK, Paused, clone, frame_ranges, history_dir, population, sampled_ranks, say,
                       settings)

ORIGINS = {"regression", "never-worked", "latent", "not-a-defect", "unclear"}
VISIBLE = {"yes", "internal", "unclear"}
IMPACT = {"failed-every-time", "sequence-or-timing", "permissions", "slower-or-heavier", "presentation",
          "data-loss-or-duplication", "other"}
AREA = {"gateway", "agents", "channels", "ui", "plugins", "models/providers", "cron", "update", "storage", "cli",
        "apps", "other"}
FINAL = ("End with exactly one JSON object as your final message and nothing after it. Do not write any file.")
EXPORTS = os.path.join(WORK, "exports")
STEPS = ["origin", "origin_second", "origin_reread", "flag", "flag_reread", "review", "grade", "grade_reread",
         "tags", "refute_gpt", "refute_opus", "laterfix"]


class Case:
    """One judgment to make. `out` is where the answer lives; `style` is 'json' (a JSON file) or 'last' (a folder
    holding last.txt, the model's final message as text)."""

    def __init__(self, key, prompt, cwd, out, style, check, *, files=None, read_dirs=(), git=False, gh=False,
                 finish=None, also_done=()):
        self.key, self.prompt, self.cwd, self.out, self.style, self.check = key, prompt, cwd, out, style, check
        self.files, self.read_dirs, self.git, self.gh = files or {}, read_dirs, git, gh
        self.finish, self.also_done = finish, also_done

    def answer_path(self):
        return self.out if self.style == "json" else os.path.join(self.out, "last.txt")

    def done(self):
        for path in (self.answer_path(), *self.also_done):
            if os.path.exists(path) and os.path.getsize(path) > 0:
                return True
        return False


def brief(*parts):
    """The text of a brief file, from the line after its first '---' when it has a preamble."""
    text = open(os.path.join(*parts)).read()
    return text.split("\n---\n", 1)[1].strip() if "\n---\n" in text else text.strip()


def brief_id(text):
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def scratch(step, key):
    path = os.path.join(WORK, "run", step, key)
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path)
    return path


def graft_point():
    """(short id, date) of the commit where the clone's history on main begins; a full clone gives its root."""
    import subprocess
    from .settings import git_env
    out = subprocess.run(["git", "-C", clone(), "log", "--first-parent", "--format=%H %cI", settings()["tip"]],
                         capture_output=True, text=True, env=git_env()).stdout.strip().splitlines()
    sha, date = out[-1].split() if out else ("unknown", "unknown")
    return sha[:12], date[:10]


# ---- what a fix repaired -------------------------------------------------------------------------------------

def second_reader(sha):
    """About 15% of fixes get an independent second read; the rule depends only on the fix (scripts/second.py)."""
    return int(hashlib.sha256(("fix-origins-second-v1:" + sha).encode()).hexdigest()[:8], 16) / 2 ** 32 < 0.15


def reread_ranks():
    """Per frame, the first `reread` sampled fixes in the order of sha256("audit-v1:" + sha)."""
    fixes, chosen = population(), []
    for frame, (low, high) in zip(settings()["frames"], frame_ranges()):
        ranks = [rank for rank in range(low, high + 1) if rank in fixes]
        ranks.sort(key=lambda rank: hashlib.sha256(("audit-v1:" + fixes[rank]["sha"]).encode()).hexdigest())
        chosen += ranks[:frame.get("reread", 0)]
    return sorted(chosen)


def check_origin(answer):
    problems = []
    if answer.get("origin") not in ORIGINS:
        problems.append("origin must be one of " + ", ".join(sorted(ORIGINS)))
    if answer.get("origin") in ("regression", "never-worked"):
        if not re.fullmatch(r"[0-9a-f]{40}", str(answer.get("cause_sha") or "")):
            problems.append("cause_sha must be a full 40-character commit id for regression and never-worked")
        if answer.get("confidence") not in ("high", "medium", "low"):
            problems.append("confidence must be high, medium or low when a cause is named")
    return problems


def check_origin_full(answer):
    problems = check_origin(answer)
    for field, allowed in (("user_visible", VISIBLE), ("impact", IMPACT), ("area", AREA)):
        if answer.get(field) not in allowed:
            problems.append(f"{field} must be one of " + ", ".join(sorted(allowed)))
    for field in ("user_saw", "summary", "reasoning"):
        if not answer.get(field):
            problems.append(f"{field} is missing")
    return problems


def origin_cases(step, config):
    fixes = population()
    graft, graft_date = graft_point()
    text = (brief(FIX, "reader-prompt.md").replace("{tip}", settings()["tip"][:11])
            .replace("{graft}", graft).replace("{graft_date}", graft_date))
    online = config["backend"] != "codex"  # the codex sandbox has no network
    look = f"python3 {model.LOOK}"
    lookups = f"""In this run, `git` and `gh` themselves are not available. Use the read-only lookup tool instead:

- where the brief shows `git <subcommand> ...`, run `{look} git <subcommand> ...` (no `GIT_NO_LAZY_FETCH` prefix
  and no `-C`; the tool adds them);
- for the full-history git directory, run `{look} history log ...`;
- for `gh api repos/.../commits/<sha>`, run `{look} commit <sha>`;
- for `gh api repos/.../pulls/<n>`, run `{look} pull <n>`;
- for blame beyond the graft, run `{look} blame <sha> <path>`.
""" if online else f"""In this run you have read-only `git` and no network. Use `git -C {clone()} ...` for every git command, and
`git --git-dir={history_dir()} log ...` for the full-history directory. GitHub lookups (`gh api`) are not
available: where the brief says to use `gh`, skip that step and answer with lower confidence or `unclear` instead.
"""
    if step == "origin":
        ranks = sampled_ranks()
    elif step == "origin_second":
        ranks = [rank for rank in sampled_ranks() if rank in fixes and second_reader(fixes[rank]["sha"])]
    else:
        ranks = reread_ranks()
    cases = []
    for rank in ranks:
        bundle = os.path.join(FIX, "evidence", f"{rank:04d}.md")
        if rank not in fixes or not os.path.exists(bundle):
            continue
        sha = fixes[rank]["sha"]
        task = f"""

## Your task

Classify one fix.

- Fix: rank {rank}, commit `{sha}`
- Evidence bundle: `./bundle.md` in the current directory
- The checkout: `{clone()}`

{lookups}
Read only the bundle and what the brief allows in the checkout. Do not read any folder named `research` in the
checkout, any other reader's answer, or any file of the study that produced this bundle. Your judgment must be your
own.

"""

        def finish(answer, rank=rank, sha=sha):
            answer.update({"rank": rank, "sha": sha, "rubric": "v1.2"})
            return answer
        if step == "origin_reread":
            out, style, check = os.path.join(FIX, "audit", "raw", "origin", f"{rank:04d}"), "last", check_origin
        else:
            folder = "reads" if step == "origin" else "reads-second"
            out, style, check = os.path.join(FIX, folder, f"{rank}.json"), "json", check_origin_full
        cases.append(Case(f"{rank:04d}", text + task, None, out, style, check, files={"bundle.md": bundle},
                          read_dirs=(clone(), history_dir()), git=True, gh=online, finish=finish))
    return cases


# ---- what the review bot had said ---------------------------------------------------------------------------

def check_flag(answer):
    return [] if answer.get("flagged") in ("exact", "related", "none") else ["flagged must be exact, related or none"]


def flag_cases(step, config):
    folder = os.path.join(FIX, "clawsweeper", "bundles")
    text = brief(FIX, "clawsweeper", "reader-prompt.md")
    task = ("\n\n## Your task\n\nJudge the one bundle in the current directory: `./bundle.md`, and `./full.md` if you "
            "need the whole review text. Read nothing else on this machine and do not use the network.\n\n")
    cases = []
    # The second-maker check covers the bot reviews of the frames marked `reread_bot` in study.json (default: all).
    checked = {frame["id"] for frame in settings()["frames"] if frame.get("reread_bot", True)}
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if name.endswith(".full.md"):
            continue
        key = name[:-3]
        if step == "flag_reread" and (int(key) - 1) // 100000 + 1 not in checked:
            continue
        files = {"bundle.md": os.path.join(folder, name)}
        if os.path.exists(os.path.join(folder, key + ".full.md")):
            files["full.md"] = os.path.join(folder, key + ".full.md")
        if step == "flag":
            out, style = os.path.join(FIX, "clawsweeper", "reads", f"{int(key)}.json"), "json"
        else:
            out, style = os.path.join(FIX, "audit", "raw", "flag", key), "last"
        cases.append(Case(key, text + task, None, out, style, check_flag, files=files,
                          finish=lambda answer, rank=int(key): dict(answer, rank=rank)))
    return cases


# ---- the blind review experiment ----------------------------------------------------------------------------

TEST_RE = re.compile(r"(\.test\.|\.spec\.|\.e2e\.|/__tests__/|/test/|/tests/|^test/|/fixtures/|\.snap$)")
CODE_EXT = (".ts", ".tsx", ".js", ".mjs", ".cjs", ".css", ".swift", ".kt", ".py", ".sh", ".sql", ".json", ".yml", ".yaml")
GROUP = 3  # files per run in the per-file arm


def pilot_ranks():
    path = os.path.join(PILOT, "data", "pilot_ranks.json")
    return json.load(open(path)) if os.path.exists(path) else []


def export(rank, tree="cases"):
    return os.path.join(EXPORTS, tree, f"{rank:04d}")


def changed_code_files(folder):
    files = []
    with open(os.path.join(folder, ".review", "change.diff"), errors="replace") as handle:
        for line in handle:
            if line.startswith("+++ b/"):
                path = line[6:].strip()
                if path.endswith(CODE_EXT) and not TEST_RE.search(path) and not path.startswith("docs/"):
                    files.append(path)
    return files


def check_review(answer):
    return [] if isinstance(answer.get("findings"), list) else ["the answer must have a `findings` list"]


def review_cases(step, arm):
    name = f"{arm['model']}__{arm['mode']}"
    runs = os.path.join(PILOT, "data", "runs", name)
    cases = []
    for rank in pilot_ranks():
        folder = export(rank)
        key = f"{rank:04d}"
        if arm["mode"] != "whole" and not os.path.isdir(folder):
            # Without the code export the file groups cannot be worked out; show the stored runs as they are.
            stored = sorted(name for name in os.listdir(runs) if name.startswith(key + ".")) if os.path.isdir(runs) else []
            for part in stored or [key + ".00"]:
                cases.append(Case(part, "", folder, os.path.join(runs, part), "last", check_review))
            continue
        if arm["mode"] == "whole":
            cases.append(Case(key, brief(PILOT, "prompt-whole.md"), folder, os.path.join(runs, key), "last",
                              check_review, also_done=(os.path.join(runs, key + ".json"),)))
            continue
        files, template = changed_code_files(folder), brief(PILOT, "prompt-per-file.md")
        for index in range(0, len(files), GROUP):
            chunk = "\n".join(f"- `{path}`" for path in files[index:index + GROUP])
            part = f"{key}.{index // GROUP:02d}"
            cases.append(Case(part, template.replace("{FILES}", chunk), folder, os.path.join(runs, part), "last",
                              check_review))
    return cases


def check_grade(answer):
    reviewers = answer.get("reviewers")
    if not isinstance(reviewers, dict) or not reviewers:
        return ["the answer must have a `reviewers` object with one entry per reviewer letter"]
    return [f"reviewer {letter}: flagged must be exact, related or none" for letter, verdict in reviewers.items()
            if not isinstance(verdict, dict) or verdict.get("flagged") not in ("exact", "related", "none")]


def grade_cases(step, config):
    folder = os.path.join(PILOT, "data", "grade", "bundles")
    text = brief(PILOT, "grader-prompt.md")
    task = ("\n\n## Your task\n\nGrade the one bundle in the current directory: `./bundle.md`. Read nothing else on "
            "this machine and do not use the network.\n\n")
    cases = []
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        key = name[:4]

        def check(answer, path=os.path.join(folder, name)):
            letters = set(re.findall(r"(?m)^#+ Reviewer ([A-Z])\b", open(path).read()))
            missing = sorted(letters - set((answer.get("reviewers") or {})))
            return check_grade(answer) + ([f"reviewers missing from the answer: {', '.join(missing)}"] if missing else [])
        if step == "grade":
            out, style = os.path.join(PILOT, "data", "grade", "reads", key + ".json"), "json"
        else:
            out, style = os.path.join(FIX, "audit", "raw", "grade", key), "last"
        cases.append(Case(key, text + task, None, out, style, check, files={"bundle.md": os.path.join(folder, name)},
                          finish=lambda answer, rank=int(key): dict(answer, rank=rank)))
    return cases


def tag_cases(step, config):
    folder = os.path.join(PILOT, "data", "grade", "bundles")
    text = brief(PILOT, "tag-prompt.md")
    cases = []
    for rank in pilot_ranks():
        key = f"{rank:04d}"
        bundle = os.path.join(folder, key + ".md")
        if not os.path.exists(bundle):
            continue
        described = open(bundle).read().split("\n## Reviewer", 1)[0].split("\n### Reviewer", 1)[0]
        task = ("\n\n## Your task\n\nTag one case. The current directory is the export directory. The bug is described "
                "below; the reviewers' findings are left out.\n\n" + described.strip() + "\n\n")
        cases.append(Case(key, text + task, export(rank), os.path.join(PILOT, "data", "grade", "tags", key + ".json"),
                          "json", lambda a: [] if a.get("needs") in ("diff", "repo", "outside") else
                          ["needs must be diff, repo or outside"],
                          finish=lambda answer, rank=rank: dict(answer, rank=rank)))
    return cases


def check_findings(field, allowed, listing):
    ids = sorted(set(re.findall(r"\bF\d+\b", listing)), key=lambda name: int(name[1:]))

    def check(answer):
        findings = answer.get("findings")
        if not isinstance(findings, dict):
            return ["the answer must have a `findings` object keyed by finding id"]
        problems = [f"{name} is missing" for name in ids if name not in findings]
        problems += [f"{name}: {field} must be one of {', '.join(allowed)}" for name, verdict in findings.items()
                     if not isinstance(verdict, dict) or verdict.get(field) not in allowed]
        return problems
    return check


def refute_cases(step, config):
    """Each reported problem checked against the exported code; the control ranks again on the fixed code."""
    slot = step.split("_")[1]  # gpt or opus: the two checkers, kept apart by these folder names
    verify = os.path.join(PILOT, "data", "verify")
    text = brief(PILOT, "refute-prompt.md")
    path = os.path.join(PILOT, "data", "pilot_control_ranks.json")
    control = set(json.load(open(path))) if os.path.exists(path) else set()
    cases = []
    folder = os.path.join(verify, "refute")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        key = name[:4]
        listing = open(os.path.join(folder, name)).read()
        for tree in ("cases", "fixed-cases"):
            if tree == "fixed-cases" and int(key) not in control:
                continue
            target = os.path.join(verify, f"refute-{slot}" + ("" if tree == "cases" else "-fixed-cases"))
            task = ("\n\n## Your task\n\nThe repository directory is the current directory. Stay inside it: do not "
                    "read files anywhere else on this machine.\n\n" + listing + "\n\n")
            style = "last" if slot == "gpt" else "json"
            out = os.path.join(target, key) if style == "last" else os.path.join(target, key + ".json")
            cases.append(Case(key if tree == "cases" else key + "-fixed", text + task, export(int(key), tree), out, style,
                              check_findings("verdict", ("confirmed", "refuted", "unclear"), listing),
                              finish=lambda answer, key=key: dict(answer, case=key)))
    return cases


def laterfix_cases(step, config):
    verify = os.path.join(PILOT, "data", "verify")
    text = brief(PILOT, "laterfix-prompt.md")
    folder = os.path.join(verify, "laterfix")
    cases = []
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        key = name[:4]
        listing = open(os.path.join(folder, name)).read()
        how = (f"`git -C {clone()} show ...`" if config["backend"] == "codex"
               else f"`python3 {model.LOOK} git show ...` (the lookup tool adds the checkout and the "
                    "`GIT_NO_LAZY_FETCH` setting; plain `git` is not available in this run)")
        task = (f"\n\n## Your task\n\nThe checkout is `{clone()}`: run the two allowed commands as {how}. "
                "Your bundle follows.\n\n" + listing + "\n\n")
        cases.append(Case(key, text + task, None, os.path.join(verify, "laterfix-reads", key + ".json"), "json",
                          check_findings("fixed", ("yes", "partly", "no"), listing), read_dirs=(clone(),), git=True,
                          finish=lambda answer, key=key: dict(answer, case=key)))
    return cases


BUILDERS = {"origin": origin_cases, "origin_second": origin_cases, "origin_reread": origin_cases,
            "flag": flag_cases, "flag_reread": flag_cases, "review": review_cases, "grade": grade_cases,
            "grade_reread": grade_cases, "tags": tag_cases, "refute_gpt": refute_cases, "refute_opus": refute_cases,
            "laterfix": laterfix_cases}


def slots(step, backend=None, model_name=None):
    """(label, config, cases) for each model that answers this step: one, except for the review arms."""
    configured = settings()["judging"][step]
    out = []
    for config in configured if isinstance(configured, list) else [configured]:
        config = dict(config, backend=backend or config["backend"], model=model_name or config["model"])
        label = step if "mode" not in config else f"{step} {config['model']}__{config['mode']}"
        out.append((label, config, BUILDERS[step](step, config)))
    return out


# ---- running ------------------------------------------------------------------------------------------------

def store(case, answer, text):
    target = case.answer_path()
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target + ".part", "w") as handle:
        handle.write(json.dumps(answer, indent=2) + "\n" if case.style == "json" else text.strip() + "\n")
    os.replace(target + ".part", target)


def accept(case, text):
    """Parse and check a model's final message; store it and return [] when valid, else the problems."""
    answer = model.extract_json(text)
    if answer is None:
        return ["the final message held no JSON object"]
    problems = case.check(answer)
    if problems:
        return problems
    store(case, case.finish(answer) if case.finish else answer, text)
    return []


def log(step, case, config, seconds):
    with open(os.path.join(FIX, "judging-log.jsonl"), "a") as handle:
        handle.write(json.dumps({"step": step, "case": case.key, "backend": config["backend"],
                                 "model": config["model"], "effort": settings()["limits"]["effort"],
                                 "brief": brief_id(case.prompt.split("## Your task")[0]),
                                 "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                                 "seconds": seconds}) + "\n")


def prepare(label, case):
    """The folder the model works in: the case's own, or a fresh one holding only the case's input files."""
    if case.cwd:
        if not os.path.isdir(case.cwd):
            raise model.RunFailed(f"the code export {case.cwd} does not exist; `python3 study.py run pilot` makes it")
        return case.cwd
    folder = scratch(label.replace(" ", "_"), case.key)
    for name, source in case.files.items():
        text = open(source, errors="replace").read()
        if name == "bundle.md":
            text = re.sub(r"(?m)^- Full text of this review version: .*$",
                          "- Full text of this review version: ./full.md", text)
        with open(os.path.join(folder, name), "w") as handle:
            handle.write(text)
    return folder


def run_case(label, case, config, stop):
    limits = settings()["limits"]
    waited, pause, problems = 0, 60, []
    for attempt in range(2):
        while True:
            if stop.is_set():
                return "not started"
            if case.done():
                return "done"  # answered meanwhile, for example by another run of the same step
            try:
                started = time.time()
                text = model.run(config["backend"], config["model"], case.prompt + FINAL + "\n", prepare(label, case),
                                 os.path.join(WORK, "logs", label.replace(" ", "_"), case.key),
                                 effort=limits["effort"], read_dirs=case.read_dirs, git=case.git, gh=case.gh)
                break
            except model.Limited as limit:
                if waited + pause > limits["max_wait_minutes"] * 60:
                    stop.set()
                    raise Paused(f"{limit} (waited {waited // 60} minutes)")
                say(f"  {label} {case.key}: limit reached, waiting {pause // 60} min ({limit})"[:200])
                time.sleep(pause)
                waited, pause = waited + pause, min(pause * 3, 1800)
            except model.RunFailed as failure:
                text, problems = None, [str(failure)]
                break
            except Paused:
                stop.set()
                raise
        if text is not None:
            problems = accept(case, text)
            if not problems:
                log(label, case, config, round(time.time() - started))
                return "done"
    failure = os.path.join(WORK, "failures", label.replace(" ", "_"), case.key + ".txt")
    os.makedirs(os.path.dirname(failure), exist_ok=True)
    with open(failure, "w") as handle:
        handle.write("\n".join(problems) + "\n")
    return "failed: " + "; ".join(problems)[:160]


def orders(label, cases, config):
    """The `agent` backend: take in answers that subagents wrote, then write a work order for each case left."""
    folder = os.path.join(WORK, "orders", label.replace(" ", "_"))
    os.makedirs(folder, exist_ok=True)
    waiting = []
    for case in cases:
        answer = os.path.join(folder, case.key + ".answer.txt")
        if os.path.exists(answer):
            problems = accept(case, open(answer, errors="replace").read())
            if not problems:
                log(label, case, config, None)
                os.remove(answer)
                os.remove(os.path.join(folder, case.key + ".md"))
                continue
            say(f"  {label} {case.key}: answer rejected ({'; '.join(problems)[:160]}); order kept")
        work = prepare(label, case)
        allowed = [f"`{work}` (your working directory)"] + [f"`{path}`" for path in case.read_dirs]
        with open(os.path.join(folder, case.key + ".md"), "w") as handle:
            handle.write(case.prompt + f"""Work in `{work}`. You may read only: {', '.join(allowed)}.
{"Run git only as your task section says." if case.git else "Do not run git."}
{"Use the network only for the GitHub lookups your task section names." if case.gh else "Do not use the network."}
Write exactly one JSON object, and nothing else, to `{answer}`. Write no other file.
""")
        waiting.append(case.key)
    return folder, waiting


def run_step(step, only=None, backend=None, model_name=None, jobs=None, limit=None):
    """Run every case of a step that has no answer. Returns (done, failed, waiting) counts over all its slots."""
    done = failed = waiting = 0
    for label, config, cases in slots(step, backend, model_name):
        if only:
            cases = [case for case in cases if case.key in only or case.key.split(".")[0] in only]
        todo = [case for case in cases if not case.done()][:limit]
        say(f"{label}: {len(cases)} cases, {len(cases) - len([c for c in cases if not c.done()])} answered, "
            f"{len(todo)} to run with {config['backend']} {config['model']}")
        if not todo:
            continue
        if config["backend"] == "agent":
            folder, left = orders(label, todo, config)
            waiting += len(left)
            if left:
                say(f"  {len(left)} work orders in {folder}: give each .md file to a fresh subagent as its whole "
                    "task, then run this command again")
            continue
        ok, detail = model.signed_in(config["backend"])
        if not ok:
            raise Paused(f"`{config['backend']}` is {detail}. Sign in ({model.SIGN_IN.get(config['backend'], 'install it')}), or run this "
                         "step with another backend: --backend codex, --backend claude or --backend agent")
        stop = threading.Event()
        with ThreadPoolExecutor(jobs or settings()["limits"]["jobs"]) as pool:
            futures = [(case, pool.submit(run_case, label, case, config, stop)) for case in todo]
            paused = None
            for case, future in futures:
                try:
                    outcome = future.result()
                except Paused as pause:
                    paused, outcome = pause, "paused"
                say(f"  {label} {case.key}: {outcome}")
                done += outcome == "done"
                failed += outcome.startswith("failed")
            if paused:
                raise paused
    return done, failed, waiting


def status():
    """Rows of (label, cases, answered) for every judging step, from the files on disk."""
    rows = []
    for step in STEPS:
        for label, config, cases in slots(step):
            rows.append((label, f"{config['backend']} {config['model']}", len(cases), sum(c.done() for c in cases)))
    return rows
