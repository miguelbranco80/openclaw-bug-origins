#!/usr/bin/env python3
"""Mechanical blame candidates for sampled fixes.

For each fix in the rank range, for every non-test product file it changes:
  - hunks that remove or modify lines: blame the removed lines at <fix>^;
  - hunks that only add lines: blame CONTEXT lines either side at <fix>^
    and count them as "context only".
Blame runs `git blame -w -M -C --porcelain <fix>^ -L ... -- <old path>`.
Lines are aggregated per blamed commit; the top five are kept.

Usage (from the repo root):
    python3 research/fix-origins/scripts/blame.py --from 1 --to 50

Appends one JSON line per fix to research/fix-origins/blame.jsonl and skips
ranks already present, so a crashed run can simply be restarted.
"""
import argparse
import json
import os
import re
import subprocess

# The checkout is a partial clone: a missing object must fail, never trigger a network fetch.
os.environ["GIT_NO_LAZY_FETCH"] = "1"
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
POP = os.path.join(ROOT, "population.tsv")
OUT = os.path.join(ROOT, "blame.jsonl")
CONTEXT = 10
TOP = 5
WORKERS = 4
BLAME_TIMEOUT = 300
PRODUCT_DIRS = ("src/", "ui/", "extensions/", "packages/", "apps/")
TEST_MARKERS = (".test.", "/test/", "test-support", "fixtures")
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_meta_cache: dict = {}
GRAFTS: set = set()  # shallow-graft commits: lines blamed here are older than the local history


def git(*args: str, timeout: int | None = None) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True,
                          text=True, errors="replace", timeout=timeout).stdout



def is_product_file(path: str) -> bool:
    return path.startswith(PRODUCT_DIRS) and not any(m in path for m in TEST_MARKERS)


def changed_hunks(sha: str):
    """Yield (old_path, removed_ranges, context_ranges, old_line_count) per product file."""
    diff = git("diff", "-U0", "-M", "--no-color", "--no-ext-diff", f"{sha}^", sha)
    files: dict = {}
    old = new = None
    for line in diff.split("\n"):
        if line.startswith("diff --git "):
            old = new = None
        elif line.startswith("--- "):
            old = None if line == "--- /dev/null" else line[6:]
        elif line.startswith("+++ "):
            new = None if line == "+++ /dev/null" else line[6:]
            if old and (is_product_file(old) or (new and is_product_file(new))):
                files.setdefault(old, ([], []))
        elif line.startswith("@@") and old in files:
            m = HUNK.match(line)
            start, count = int(m.group(1)), int(m.group(2) or "1")
            if count > 0:
                files[old][0].append((start, start + count - 1))
            else:  # pure addition after old line `start`
                files[old][1].append((max(1, start - CONTEXT + 1), start + CONTEXT))
    return files


def blame_ranges(sha: str, path: str, ranges) -> tuple[dict, str | None]:
    """Return ({commit: lines}, error) for the given old-side ranges."""
    if not ranges:
        return {}, None
    try:
        n = int(git("cat-file", "-p", f"{sha}^:{path}").count("\n")) or 1
    except subprocess.CalledProcessError:
        return {}, "missing"
    args = []
    for a, b in ranges:
        a, b = min(a, n), min(b, n)
        args += ["-L", f"{a},{b}"]
    try:
        out = git("blame", "-w", "-M", "-C", "--porcelain", *args, f"{sha}^", "--", path,
                  timeout=BLAME_TIMEOUT)
    except subprocess.TimeoutExpired:
        return {}, "timeout"
    except subprocess.CalledProcessError as e:
        return {}, f"error: {e.stderr.strip()[:200]}"
    counts: dict = {}
    for line in out.split("\n"):
        m = re.match(r"^([0-9a-f]{40}) \d+ \d+ (\d+)$", line)
        if m:
            counts[m.group(1)] = counts.get(m.group(1), 0) + int(m.group(2))
    return counts, None


def merge_ranges(ranges):
    out = []
    for a, b in sorted(ranges):
        if out and a <= out[-1][1] + 1:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def shallow_roots() -> set:
    path = git("rev-parse", "--git-path", "shallow").strip()
    if not os.path.isabs(path):
        path = os.path.join(git("rev-parse", "--show-toplevel").strip(), path)
    return set(open(path).read().split()) if os.path.exists(path) else set()


def commit_meta(c: str) -> dict:
    if c not in _meta_cache:
        date, author, subject = git("log", "-1", "--format=%cI%x02%an%x02%s", c).strip().split("\x02", 2)
        nfiles = len([p for p in git("show", "--format=", "--name-only", "--no-renames", c).split("\n") if p])
        pr = re.findall(r"\(#(\d+)\)", subject)
        _meta_cache[c] = {"date": date, "author": author, "subject": subject,
                          "pr": int(pr[-1]) if pr else None, "files_changed": nfiles}
    return dict(_meta_cache[c])


def process(rank: int, sha: str) -> dict:
    files = changed_hunks(sha)
    removed: dict = {}
    context: dict = {}
    errors = []
    for path, (rem, ctx) in files.items():
        for kind, ranges, acc in (("removed", rem, removed), ("context", ctx, context)):
            counts, err = blame_ranges(sha, path, merge_ranges(ranges))
            if err:
                errors.append(f"{path} ({kind}): {err}")
            for c, n in counts.items():
                acc[c] = acc.get(c, 0) + n
    commits = set(removed) | set(context)
    ranked = sorted(commits, key=lambda c: (-removed.get(c, 0), -context.get(c, 0), c))
    cands = []
    for c in ranked[:TOP]:
        meta = commit_meta(c)
        cands.append({"sha": c, "removed_lines": removed.get(c, 0),
                      "context_lines": context.get(c, 0),
                      "context_only": removed.get(c, 0) == 0,
                      "graft": c in GRAFTS, **meta})
    return {"rank": rank, "sha": sha, "product_files": len(files),
            "removed_lines_blamed": sum(removed.values()),
            "context_lines_blamed": sum(context.values()),
            "distinct_commits": len(commits), "blame_errors": errors,
            "candidates": cands}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="lo", type=int, required=True)
    ap.add_argument("--to", dest="hi", type=int, required=True)
    a = ap.parse_args()
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            done = {json.loads(l)["rank"] for l in f if l.strip()}
    todo = []
    with open(POP) as f:
        next(f)
        for line in f:
            rank, sha = line.split("\t")[:2]
            if a.lo <= int(rank) <= a.hi and int(rank) not in done:
                todo.append((int(rank), sha))
    GRAFTS.update(shallow_roots())
    with ThreadPoolExecutor(WORKERS) as pool:
        results = list(pool.map(lambda t: process(*t), todo))
    with open(OUT, "a") as f:
        for r in sorted(results, key=lambda r: r["rank"]):
            f.write(json.dumps(r) + "\n")
    print(f"fixes newly blamed: {len(results)}")


if __name__ == "__main__":
    main()
