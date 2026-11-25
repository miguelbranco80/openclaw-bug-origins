#!/usr/bin/env python3
"""Write one Markdown evidence bundle per sampled fix for the model readers.

Each bundle holds the fix's message, file list, product diff, and the blame
candidates with their messages and their diffs restricted to the files the fix
touched. Long sections are truncated; readers can run read-only git commands
for more.

Usage (from the repo root):
    python3 research/fix-origins/scripts/evidence.py --from 1 --to 50 --out <dir>
"""
import argparse
import json
import os
import re
import subprocess

# The checkout is a partial clone: a missing object must fail, never trigger a network fetch.
os.environ["GIT_NO_LAZY_FETCH"] = "1"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pipeline import gh  # noqa: E402
from pipeline.settings import Paused, settings, stop_paused  # noqa: E402
PRODUCT_DIRS = ("src/", "ui/", "extensions/", "packages/", "apps/")
TEST_MARKERS = (".test.", "/test/", "test-support", "fixtures")
FIX_DIFF_LINES = 700
CAND_DIFF_LINES = 220
CAND_DETAIL = 3
PR_CACHE = os.path.join(ROOT, "pr-cache")  # candidates shown with message and diff; the rest as one line


def git(*args: str, timeout: int = 120) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True,
                          text=True, errors="replace", timeout=timeout).stdout



def is_product_file(path: str) -> bool:
    return path.startswith(PRODUCT_DIRS) and not any(m in path for m in TEST_MARKERS)


def fix_pr(sha: str) -> dict | None:
    """Fetch (and cache) the fix's PR via gh. Public read only."""
    subject = git("log", "-1", "--format=%s", sha)
    nums = re.findall(r"\(#(\d+)\)", subject)
    if not nums:
        return None
    os.makedirs(PR_CACHE, exist_ok=True)
    path = os.path.join(PR_CACHE, f"{nums[-1]}.json")
    if not os.path.exists(path):
        try:
            pr = gh.rest(f"repos/{settings()['repository']}/pulls/{nums[-1]}")
        except RuntimeError:
            return None
        keep = {"number": pr["number"], "title": pr["title"], "body": pr.get("body") or "",
                "user": pr["user"]["login"], "created_at": pr["created_at"], "merged_at": pr.get("merged_at")}
        with open(path, "w") as f:
            json.dump(keep, f)
    with open(path) as f:
        return json.load(f)


def cap(text: str, n: int) -> str:
    lines = text.rstrip("\n").split("\n")
    if len(lines) <= n:
        return "\n".join(lines)
    return "\n".join(lines[:n]) + f"\n... [truncated {len(lines) - n} more lines; run git for the rest]"


def candidate_diff(sha: str, paths: list) -> str:
    """Diff of a candidate limited to paths; skips paths whose blobs are missing from the partial clone."""
    if not paths:
        return ""
    try:
        return git("show", "--format=", "--no-color", "--no-renames", sha, "--", *paths, timeout=60)
    except subprocess.TimeoutExpired:
        return "[diff unavailable: git show timed out]\n"
    except subprocess.CalledProcessError:
        parts = []
        for p in paths:
            try:
                parts.append(git("show", "--format=", "--no-color", "--no-renames", sha, "--", p, timeout=60))
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                parts.append(f"[diff of {p} unavailable: object missing from the partial clone]\n")
        return "".join(parts)


def pr_section(pr: dict | None) -> list:
    if not pr:
        return ["## Fix PR", "", "(no PR number in subject, or fetch failed)", ""]
    return [f"## Fix PR #{pr['number']} description (by {pr['user']}, opened {pr['created_at']})", "",
            "```text", cap(pr["body"], 120), "```", ""]


def bundle(rec: dict) -> str:
    sha = rec["sha"]
    head = git("log", "-1", "--format=%H%n%cI%n%an%n%s", sha).split("\n")
    body = git("log", "-1", "--format=%b", sha)
    files = [p for p in git("show", "--format=", "--name-only", "-M", sha).split("\n") if p]
    product = [p for p in files if is_product_file(p)]
    old_paths = sorted({p for p in git("diff", "--name-only", "-M", f"{sha}^", sha, "--diff-filter=MRD").split("\n") if p}
                       | set(product))
    diff = git("diff", "-M", "--no-color", f"{sha}^", sha, "--", *product) if product else ""
    out = [f"# Fix rank {rec['rank']}: {head[3]}", "",
           f"- sha: `{head[0]}`", f"- date: {head[1]}", f"- author: {head[2]}",
           f"- parent: `{sha}^`", "", "## Fix message body", "", "```text", cap(body, 160), "```", "",
           *pr_section(fix_pr(sha)),
           "## Files changed (all, including tests)", "", "```text", cap("\n".join(files), 80), "```", "",
           f"## Product diff (non-test files under src/ ui/ extensions/ packages/ apps/)", "",
           "```diff", cap(diff, FIX_DIFF_LINES), "```", "",
           "## Blame candidates", "",
           f"Blame of lines the fix removed or modified, at the fix's parent (`git blame -w -M -C`). "
           f"Removed lines blamed: {rec['removed_lines_blamed']}; context lines blamed (for pure additions, "
           f"{10} lines either side): {rec['context_lines_blamed']}; distinct commits: {rec['distinct_commits']}."
           + (f" Blame errors: {rec['blame_errors']}" if rec["blame_errors"] else ""), "",
           "| # | sha | removed lines | context lines | date | files | subject |",
           "|---|---|---|---|---|---|---|"]
    for i, c in enumerate(rec["candidates"], 1):
        graft = (f" **(shallow graft: code older than {c['date'][:10]}; not the real cause)**"
                 if c.get("graft") else "")
        out.append(f"| {i} | `{c['sha'][:12]}`{graft} | {c['removed_lines']} | {c['context_lines']} | "
                   f"{c['date'][:10]} | {c['files_changed']} | {c['subject'].replace('|', '/')} |")
    out.append("")
    for i, c in enumerate([c for c in rec["candidates"] if not c.get("graft")][:CAND_DETAIL], 1):
        cbody = git("log", "-1", "--format=%b", c["sha"])
        cdiff = candidate_diff(c["sha"], old_paths)
        out += [f"### Candidate {i}: `{c['sha']}`", "", f"{c['subject']} ({c['date']}, {c['author']}, "
                f"{c['files_changed']} files)", "", "Message (truncated):", "", "```text", cap(cbody, 40), "```", "",
                "Its diff, limited to files the fix touched:", "", "```diff", cap(cdiff, CAND_DIFF_LINES), "```", ""]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="lo", type=int, required=True)
    ap.add_argument("--to", dest="hi", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    n = 0
    with open(os.path.join(ROOT, "blame.jsonl")) as f:
        for line in f:
            rec = json.loads(line)
            path = os.path.join(a.out, f"{rec['rank']:04d}.md")
            if a.lo <= rec["rank"] <= a.hi and not (os.path.exists(path) and os.path.getsize(path)):
                text = bundle(rec)
                with open(path + ".part", "w") as o:
                    o.write(text)
                os.replace(path + ".part", path)
                n += 1
    print(f"wrote {n} new bundles to {a.out} (existing ones are kept)")


if __name__ == "__main__":
    try:
        main()
    except Paused as pause:
        stop_paused(pause)
