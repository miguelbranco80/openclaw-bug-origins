#!/usr/bin/env python3
"""The one command that runs the study. PROTOCOL.md explains every stage; this runs them.

  python3 study.py doctor              check the clone, the sign-ins and the quotas before starting
  python3 study.py status              what is done and what is left, stage by stage
  python3 study.py run <stage>         run one stage (see `status` for the names), or `run all`
  python3 study.py judge <step>        run one model-judging step on the cases that have no answer yet
  python3 study.py rebuild             recompute every number, chart and the report from the stored answers
  python3 study.py compare <git-ref>   list the numbers and claims that changed since an earlier commit
  python3 study.py reset --yes         delete everything generated, to start a new study from nothing

Every stage skips work that is already done, so any command can be stopped and run again. A command that stops
because a tool is signed out or a quota is used up exits with code 75 and says what to do; then run it again.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from pipeline import gh, judge, model  # noqa: E402
from pipeline.settings import (FIX, PAUSED, PILOT, WORK, Paused, clone, frame_ranges, git_env, history_dir,  # noqa: E402
                               population, sampled_ranks, say, settings, stop_paused)

SCRIPTS = os.path.join(FIX, "scripts")


def script(path, *args, cwd=None, env=None, quiet=False):
    """Run one of the study's scripts; stop the stage if it fails. Exit code 75 (paused) is passed up."""
    command = [sys.executable, os.path.join(ROOT, path), *map(str, args)]
    done = subprocess.run(command, cwd=cwd or ROOT, env=env or git_env(),
                          stdout=subprocess.DEVNULL if quiet else None)
    if done.returncode == PAUSED:
        sys.exit(PAUSED)
    if done.returncode != 0:
        raise SystemExit(f"FAILED: {path} {' '.join(map(str, args))} (exit {done.returncode})")


def lines(path):
    return sum(1 for _ in open(path)) if os.path.exists(path) else 0


def in_clone(path, *args, **kwargs):
    script(path, *args, cwd=clone(), **kwargs)


def need_clone():
    problems = [p for level, p in clone_checks() if level == "STOP"]
    if problems:
        raise SystemExit("The openclaw clone is not usable:\n  " + "\n  ".join(problems) + "\nSee PROTOCOL.md, step 0.")
    if not os.path.isdir(history_dir()):
        os.makedirs(WORK, exist_ok=True)
        subprocess.run(["sh", os.path.join(SCRIPTS, "fullhist.sh"), history_dir(), settings()["tip"]], cwd=clone(),
                       check=True, env=git_env(), stdout=subprocess.DEVNULL)


def judged(step, **options):
    """Run a judging step; stop the stage when cases are left unanswered."""
    done, failed, waiting = judge.run_step(step, **options)
    if failed or waiting:
        raise SystemExit(f"{step}: {failed} failed, {waiting} waiting for a subagent. Fix or answer them, then run "
                         "the same command again. Failure notes are under work/failures/.")


# ---- the stages, in order -----------------------------------------------------------------------------------

def stage_frame():
    """List every fix in each period in a fixed random order, and every commit on main."""
    need_clone()
    in_clone("fix-origins/scripts/sample.py")
    in_clone("fix-origins/scripts/commit_list.py")


def stage_evidence():
    """For each sampled fix: which earlier commits last touched the lines it changed, and one evidence file."""
    need_clone()
    for low, high in frame_ranges():
        in_clone("fix-origins/scripts/blame.py", "--from", low, "--to", high)
        in_clone("fix-origins/scripts/evidence.py", "--from", low, "--to", high, "--out", os.path.join(FIX, "evidence"))


def stage_origin():
    """A model reads each fix and says what it repaired and which change caused it; a second reads about 15%."""
    need_clone()
    env = dict(git_env(), FIX_ORIGINS_FULL_GIT_DIR=history_dir())
    judged("origin")
    for low, high in frame_ranges():
        in_clone("fix-origins/scripts/assemble.py", "--reads", os.path.join(FIX, "reads"), "--from", low, "--to", high, env=env)
    judged("origin_second")
    for low, high in frame_ranges():
        in_clone("fix-origins/scripts/assemble.py", "--reads", os.path.join(FIX, "reads-second"), "--from", low,
                 "--to", high, "--second", env=env)
    missing = set(sampled_ranks()) & set(population()) - {json.loads(line)["rank"] for line in open(os.path.join(FIX, "cases.jsonl"))}
    if missing:
        raise SystemExit(f"{len(missing)} sampled fixes have no accepted answer (ranks {sorted(missing)[:10]}...). "
                         "See the PROBLEM lines above, delete those answers under fix-origins/reads/ and rerun.")


def stage_bot():
    """What the review bot had written on each causing pull request, and a model's reading of whether it named the bug."""
    script("fix-origins/scripts/clawsweeper_fetch.py", cwd=FIX)
    script("fix-origins/scripts/clawsweeper_table.py", cwd=FIX)
    judged("flag")
    script("fix-origins/clawsweeper/assemble_results.py")


def stage_facts():
    """Who opened, merged and reviewed every pull request, and a random comparison sample of ordinary ones."""
    need_clone()
    script("fix-origins/population/fetch_pull_requests.py")
    script("fix-origins/comparison/fetch.py")
    script("fix-origins/comparison/fetch_proof.py")
    in_clone("fix-origins/comparison/paths.py")
    script("fix-origins/comparison/build_changes.py")


def stage_rereads():
    """A model from a different maker re-reads a slice of the fixes and every bot review."""
    need_clone()
    judged("origin_reread")
    judged("flag_reread")


def stage_pilot():
    """The blind review experiment: several models review causing changes with no hint; graders and checkers follow."""
    need_clone()
    data, exports = os.path.join(PILOT, "data"), judge.EXPORTS
    os.makedirs(data, exist_ok=True)
    script("fix-origins/review-pilot/select_cases.py")
    script("fix-origins/review-pilot/fetch_descriptions.py")
    ranks, bodies = os.path.join(data, "pilot_ranks.json"), os.path.join(data, "pilot_pr_bodies.json")
    in_clone("fix-origins/review-pilot/export.py", exports, ranks, bodies)
    judged("review")
    script("fix-origins/review-pilot/grade_bundles.py", os.path.join(data, "runs"), os.path.join(data, "grade"))
    os.replace(os.path.join(data, "grade", "findings.jsonl"), os.path.join(PILOT, "findings.jsonl"))
    judged("grade")
    judged("tags")
    script("fix-origins/review-pilot/assemble_results.py")
    script("fix-origins/review-pilot/control_cases.py")
    in_clone("fix-origins/review-pilot/export.py", exports, os.path.join(data, "pilot_control_ranks.json"), bodies, "fix")
    if not os.path.exists(os.path.join(data, "verify", "key.json")):
        in_clone("fix-origins/review-pilot/verify_bundles.py", os.path.join(data, "verify"), *settings()["pilot"]["verify_arms"])
    judged("refute_gpt")
    judged("refute_opus")
    judged("laterfix")
    judged("grade_reread")


def stage_report():
    """From the stored answers to the dataset, the numbers, the charts and the report."""
    done = subprocess.run(["sh", os.path.join(ROOT, "rebuild.sh")], cwd=ROOT)
    if done.returncode != 0:
        raise SystemExit("FAILED: rebuild.sh")


STAGES = [("frame", stage_frame), ("evidence", stage_evidence), ("origin", stage_origin), ("bot", stage_bot),
          ("facts", stage_facts), ("rereads", stage_rereads), ("pilot", stage_pilot), ("report", stage_report)]


# ---- doctor and status --------------------------------------------------------------------------------------

def clone_checks():
    """(level, message) pairs about the openclaw clone; level is OK, NOTE or STOP."""
    path, tip, out = clone(), settings()["tip"], []
    git = lambda *args: subprocess.run(["git", "-C", path, *args], capture_output=True, text=True, env=git_env())
    if not os.path.isdir(os.path.join(path, ".git")) and not os.path.isfile(os.path.join(path, ".git")):
        return [("STOP", f"no git clone at {path}. Set OPENCLAW_CLONE to a clone of {settings()['repository']}.")]
    if git("cat-file", "-e", tip + "^{commit}").returncode != 0:
        return [("STOP", f"the clone at {path} does not contain the pinned commit {tip[:12]}. Fetch it.")]
    out.append(("OK", f"clone at {path} contains the pinned commit {tip[:12]}"))
    oldest = git("log", "--first-parent", "--format=%cI", tip).stdout.strip().splitlines()[-1]
    needed = min([settings()["commits_since"]] + [frame["since"] for frame in settings()["frames"]])
    level = "OK" if oldest[:10] <= needed[:10] else "STOP"
    out.append((level, f"history on main reaches back to {oldest[:10]}; the settings need {needed[:10]}"))
    shallow = git("rev-parse", "--is-shallow-repository").stdout.strip() == "true"
    if shallow:
        out.append(("NOTE", f"the clone is shallow: causes older than {oldest[:10]} cannot be traced by git alone, "
                    "and readers are told so"))
    return out


def doctor():
    say("Settings")
    data = settings()
    for frame, (low, high) in zip(data["frames"], frame_ranges()):
        say(f"  OK    frame {frame['id']}: fixes from {frame['since'][:10]} to {frame['until'][:10] if frame.get('until') else 'the pinned commit'}, "
            f"sample {frame['sample']} (ranks {low} to {high})")
    say("The openclaw clone")
    stop = False
    for level, message in clone_checks():
        say(f"  {level:5} {message}")
        stop |= level == "STOP"
    say("GitHub (read-only)")
    try:
        for resource in ("graphql", "core"):
            remaining, seconds = gh.budget(resource)
            say(f"  OK    {resource}: {remaining} calls left this hour, resets in {seconds // 60} min")
    except Paused as pause:
        say(f"  STOP  {pause}")
        stop = True
    say("Model tools")
    used = set()
    for configured in data["judging"].values():
        for config in configured if isinstance(configured, list) else [configured]:
            used.add(config["backend"])
    for backend in ("codex", "claude"):
        ok, detail = model.signed_in(backend)
        needed = "needed by the settings" if backend in used else "not needed by the settings"
        level = "OK" if ok else ("STOP" if backend in used else "NOTE")
        stop |= level == "STOP"
        say(f"  {level:5} {backend}: {detail} ({needed})")
        if not ok and backend in used:
            say(f"        Sign in ({model.SIGN_IN[backend]}), or run its steps with --backend agent or another model. "
                "Steps already answered are not affected.")
    free = shutil.disk_usage(ROOT).free // 2 ** 30
    say(f"Disk\n  {'OK' if free > 20 else 'NOTE':5} {free} GB free (the blind review exports need about 5 GB)")
    say("\n" + ("Something above says STOP. Clear it before running the stage that needs it." if stop else "Ready."))
    return 1 if stop else 0


def status():
    fixes, ranks = population(), sampled_ranks()
    wanted = [rank for rank in ranks if rank in fixes]
    say("Collection")
    say(f"  fixes in the periods: {len(fixes)}; sampled: {len(wanted)} of {len(ranks)} asked for")
    say(f"  blame done: {lines(os.path.join(FIX, 'blame.jsonl'))}; evidence files: "
        f"{len(glob.glob(os.path.join(FIX, 'evidence', '*.md')))}; fixes with an accepted answer: {lines(os.path.join(FIX, 'cases.jsonl'))}")
    say(f"  commits listed: {max(0, lines(os.path.join(ROOT, 'dataset', 'commits.tsv')) - 1)}; pull requests fetched: "
        f"{max(0, lines(os.path.join(ROOT, 'dataset', 'pull_requests.tsv')) - 1)}; comparison sample fetched: "
        f"{len(glob.glob(os.path.join(FIX, 'comparison', 'raw', '*.json')))}")
    say("Model judging (answered of cases; cases appear as earlier stages produce their inputs)")
    for label, who, cases, answered in judge.status():
        say(f"  {'done' if cases and cases == answered else '    '}  {label:34} {answered:4} of {cases:4}   {who}")
    say("Stages, in order: " + ", ".join(name for name, _ in STAGES))


# ---- compare and reset --------------------------------------------------------------------------------------

def compare(ref):
    """Numbers whose value left their earlier plausible range, or changed by more than a tenth where there is none."""
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "q*.json"))):
        name = os.path.basename(path)
        if name.endswith(".charts.json"):
            continue
        old = subprocess.run(["git", "show", f"{ref}:results/{name}"], capture_output=True, text=True, cwd=ROOT)
        if old.returncode != 0:
            say(f"{name}: not in {ref} (new question)")
            continue
        before = {row["metric"]: row for row in json.loads(old.stdout)}
        for row in json.load(open(path)):
            was = before.get(row["metric"])
            if not was or not isinstance(row["value"], (int, float)) or not isinstance(was["value"], (int, float)):
                continue
            if was["low"] is not None and was["high"] is not None:
                moved = not was["low"] <= row["value"] <= was["high"]
            else:
                moved = abs(row["value"] - was["value"]) > 0.1 * max(abs(was["value"]), 1e-9) and row["group"] not in ("size",)
            if moved:
                changed += 1
                span = f" (was plausibly {was['low']} to {was['high']})" if was["low"] is not None else ""
                say(f"{name[:3]} {row['label'][:70]:70} {was['value']} -> {row['value']}{span}")
    say(f"\n{changed} numbers moved. Read the report's sentences about them against the new values (PROTOCOL.md, "
        "\"What a rerun cannot do for you\").")


GENERATED = ["fix-origins/population.tsv", "fix-origins/blame.jsonl", "fix-origins/cases.jsonl",
             "fix-origins/second_reads.jsonl", "fix-origins/judging-log.jsonl", "fix-origins/evidence",
             "fix-origins/reads", "fix-origins/reads-second", "fix-origins/pr-cache", "fix-origins/rechecks.jsonl",
             "fix-origins/clawsweeper/raw", "fix-origins/clawsweeper/bundles", "fix-origins/clawsweeper/reads",
             "fix-origins/clawsweeper/table.jsonl", "fix-origins/clawsweeper/results.jsonl",
             "fix-origins/comparison/raw", "fix-origins/comparison/proof.json", "fix-origins/comparison/areas.json",
             "fix-origins/population/raw", "fix-origins/audit/raw", "fix-origins/audit/origin-second-reads.jsonl",
             "fix-origins/audit/flag-second-reads.jsonl", "fix-origins/audit/grade-second-reads.jsonl",
             "fix-origins/review-pilot/data", "fix-origins/review-pilot/findings.jsonl",
             "fix-origins/review-pilot/results.jsonl", "fix-origins/review-pilot/verify-results.jsonl",
             "fix-origins/review-pilot/verify-control.jsonl", "results", "charts", "work/run", "work/logs",
             "work/orders", "work/failures", "work/exports", "work/history.git"]


def reset(yes):
    keep = {"README.md", "build.py", "named_cause_study.json"}
    targets = [os.path.join(ROOT, path) for path in GENERATED]
    targets += [path for path in glob.glob(os.path.join(ROOT, "dataset", "*")) if os.path.basename(path) not in keep]
    targets = [path for path in targets if os.path.lexists(path)]
    if not yes:
        say("This would delete every stored answer and generated file:\n  " + "\n  ".join(os.path.relpath(p, ROOT) for p in targets))
        say("\nRun it again with --yes to do it. The published study stays in git history.")
        return
    for path in targets:
        if os.path.islink(path) or os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
    say(f"Deleted {len(targets)} generated files and folders. Edit study.json, then: python3 study.py run all")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor")
    commands.add_parser("status")
    run = commands.add_parser("run")
    run.add_argument("stage", choices=[name for name, _ in STAGES] + ["all"])
    one = commands.add_parser("judge")
    one.add_argument("step", choices=judge.STEPS)
    one.add_argument("--cases", help="comma-separated case numbers; default every case without an answer")
    one.add_argument("--backend", choices=["codex", "claude", "agent"], help="override the settings for this run")
    one.add_argument("--model", help="override the settings for this run")
    one.add_argument("--jobs", type=int)
    one.add_argument("--limit", type=int, help="run at most this many cases")
    commands.add_parser("rebuild")
    commands.add_parser("compare").add_argument("ref")
    commands.add_parser("reset").add_argument("--yes", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            sys.exit(doctor())
        elif args.command == "status":
            status()
        elif args.command == "run":
            for name, stage in STAGES:
                if args.stage in (name, "all"):
                    say(f"\n== stage: {name} == {stage.__doc__.strip()}")
                    stage()
        elif args.command == "judge":
            need_clone()
            only = {f"{int(c):04d}" for c in args.cases.split(",")} if args.cases else None
            done, failed, waiting = judge.run_step(args.step, only=only, backend=args.backend, model_name=args.model,
                                                   jobs=args.jobs, limit=args.limit)
            say(f"{args.step}: {done} answered now, {failed} failed, {waiting} waiting for a subagent")
            sys.exit(1 if failed or waiting else 0)
        elif args.command == "rebuild":
            stage_report()
        elif args.command == "compare":
            compare(args.ref)
        elif args.command == "reset":
            reset(args.yes)
    except Paused as pause:
        stop_paused(pause)


if __name__ == "__main__":
    main()
