#!/usr/bin/env python3
"""Validate reader answers and append them, with mechanical fields, to the dataset.

Usage (from the repo root):
    python3 research/fix-origins/scripts/assemble.py --reads <dir> --from 1 --to 50
    python3 research/fix-origins/scripts/assemble.py --reads <dir> --from 1 --to 300 --second

<dir> holds one <rank>.json per fix, written by a reader (see reader-prompt.md).
Primary answers go to cases.jsonl, second-reader answers to second_reads.jsonl.
Both files are append-only: ranks already present are skipped, never rewritten.
Missing or invalid answers are reported and not written.
"""
import argparse
import json
import os
import re
import subprocess

# The checkout is a partial clone: a missing object must fail, never trigger a network fetch.
os.environ["GIT_NO_LAZY_FETCH"] = "1"
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PR_CACHE = os.path.join(ROOT, "pr-cache")
ORIGINS = {"regression", "never-worked", "latent", "not-a-defect", "unclear"}
CONF = {"high", "medium", "low"}
VISIBLE = {"yes", "internal", "unclear"}
IMPACT = {"failed-every-time", "sequence-or-timing", "permissions", "slower-or-heavier", "presentation",
          "data-loss-or-duplication", "other"}
AREA = {"gateway", "agents", "channels", "ui", "plugins", "models/providers", "cron", "update", "storage", "cli",
        "apps", "other"}
TEST_PATH = re.compile(r"(\.test\.|/test/|test-support|fixtures|test-helpers|/__tests__/|\.e2e\.|/e2e/|\.spec\.)")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True, errors="replace").stdout



def commit_info(sha: str) -> dict:
    date, author, subject = git("log", "-1", "--format=%cI%x02%an%x02%s", sha).strip().split("\x02", 2)
    files = [p for p in git("show", "--format=", "--name-only", "--no-renames", sha).split("\n") if p]
    pr = re.findall(r"\(#(\d+)\)", subject)
    m = re.match(r"^\s*([A-Za-z]+)", subject)
    word = m.group(1).lower() if m else ""
    prefix = word if word in {"feat", "fix", "refactor", "perf"} else "other"
    return {"date": date, "author": author, "subject": subject, "pr": int(pr[-1]) if pr else None,
            "prefix": prefix, "files": files}


def fix_text(sha: str, pr: int | None) -> str:
    text = git("log", "-1", "--format=%B", sha)
    if pr is not None:
        path = os.path.join(PR_CACHE, f"{pr}.json")
        if os.path.exists(path):
            with open(path) as f:
                text += "\n" + json.load(f)["body"]
    return text


def names(text: str, sha: str, pr: int | None) -> bool:
    if pr is not None and re.search(rf"(#|/pull/){pr}\b", text):
        return True
    return any(re.search(rf"\b{sha[:n]}", text) for n in (7, 8, 9, 10, 11, 12))


def validate(a: dict) -> list:
    errs = []
    if a.get("origin") not in ORIGINS:
        errs.append(f"origin {a.get('origin')!r}")
    if a.get("user_visible") not in VISIBLE:
        errs.append(f"user_visible {a.get('user_visible')!r}")
    if a.get("impact") not in IMPACT:
        errs.append(f"impact {a.get('impact')!r}")
    if a.get("area") not in AREA:
        errs.append(f"area {a.get('area')!r}")
    if a.get("origin") in {"regression", "never-worked"}:
        if not re.fullmatch(r"[0-9a-f]{40}", a.get("cause_sha") or ""):
            errs.append(f"cause_sha {a.get('cause_sha')!r}")
        if a.get("confidence") not in CONF:
            errs.append(f"confidence {a.get('confidence')!r}")
        if not a.get("cause_quote"):
            errs.append("cause_quote missing")
    for key in ("cause_sha", "trigger_sha"):
        if a.get(key):
            try:
                a[key] = git("rev-parse", "--verify", a[key] + "^{commit}").strip()
            except subprocess.CalledProcessError:
                errs.append(f"{key} {a[key]!r} not a commit")
    return errs


def build(a: dict, blame: dict, pop: dict) -> dict:
    sha = pop["sha"]
    fix = commit_info(sha)
    rec = {"rank": pop["rank"], "sha": sha, "fix_date": fix["date"], "fix_subject": fix["subject"],
           "fix_pr": fix["pr"], "fix_author": fix["author"], "fix_files_changed": len(fix["files"]),
           "fix_adds_test": any(TEST_PATH.search(p) for p in fix["files"])}
    for k in ("rubric", "origin", "cause_sha", "cause_pr", "confidence", "cause_quote", "trigger_sha",
              "user_visible", "user_saw", "impact", "area", "summary", "reasoning", "reader"):
        rec[k] = a.get(k)
    cands = blame["candidates"]
    rec["cause"] = None
    rec["fix_of_fix"] = rec["fix_names_cause"] = rec["blame_agrees"] = rec["blame_in_top5"] = None
    if a.get("cause_sha") and a["origin"] in {"regression", "never-worked"}:
        c = commit_info(a["cause_sha"])
        days = (datetime.fromisoformat(fix["date"]) - datetime.fromisoformat(c["date"])).total_seconds() / 86400
        # The checkout is shallow; ancestry of causes older than the graft needs the full-history dir.
        full = os.environ.get("FIX_ORIGINS_FULL_GIT_DIR")
        cmd = ["git", *([f"--git-dir={full}"] if full else []), "merge-base", "--is-ancestor", a["cause_sha"], sha]
        ancestor = subprocess.run(cmd).returncode == 0
        rec["cause"] = {"date": c["date"], "days_to_fix": round(days, 2), "prefix": c["prefix"],
                        "subject": c["subject"], "pr": c["pr"], "author": c["author"],
                        "files_changed": len(c["files"]), "is_ancestor_of_fix": ancestor}
        if rec["cause_pr"] is None:
            rec["cause_pr"] = c["pr"]
        rec["fix_of_fix"] = c["prefix"] == "fix"
        rec["fix_names_cause"] = names(fix_text(sha, fix["pr"]), a["cause_sha"], c["pr"])
        rec["blame_agrees"] = bool(cands) and cands[0]["sha"] == a["cause_sha"]
        rec["blame_in_top5"] = any(x["sha"] == a["cause_sha"] for x in cands)
    rec["blame"] = {k: blame[k] for k in ("product_files", "removed_lines_blamed", "context_lines_blamed",
                                          "distinct_commits", "blame_errors", "candidates")}
    return rec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reads", required=True)
    ap.add_argument("--from", dest="lo", type=int, required=True)
    ap.add_argument("--to", dest="hi", type=int, required=True)
    ap.add_argument("--second", action="store_true")
    ap.add_argument("--reader", default=None, help="label stored in the 'reader' field")
    args = ap.parse_args()
    out = os.path.join(ROOT, "second_reads.jsonl" if args.second else "cases.jsonl")
    done = set()
    if os.path.exists(out):
        with open(out) as f:
            done = {json.loads(l)["rank"] for l in f if l.strip()}
    pop = {}
    with open(os.path.join(ROOT, "population.tsv")) as f:
        next(f)
        for line in f:
            r, sha = line.split("\t")[:2]
            pop[int(r)] = {"rank": int(r), "sha": sha}
    blames = {}
    with open(os.path.join(ROOT, "blame.jsonl")) as f:
        for line in f:
            b = json.loads(line)
            blames[b["rank"]] = b
    written, problems = 0, []
    with open(out, "a") as o:
        for rank in range(args.lo, args.hi + 1):
            path = os.path.join(args.reads, f"{rank}.json")
            if rank in done or not os.path.exists(path):
                if rank not in done and not args.second:
                    problems.append(f"{rank}: no answer")
                continue
            with open(path) as f:
                a = json.load(f)
            if a.get("sha") != pop[rank]["sha"]:
                problems.append(f"{rank}: sha mismatch {a.get('sha')}")
                continue
            errs = validate(a)
            if errs:
                problems.append(f"{rank}: " + "; ".join(errs))
                continue
            a["reader"] = args.reader or ("second" if args.second else "primary")
            o.write(json.dumps(build(a, blames[rank], pop[rank])) + "\n")
            written += 1
    print(f"wrote {written} to {out}")
    for p in problems:
        print("PROBLEM", p)


if __name__ == "__main__":
    main()
