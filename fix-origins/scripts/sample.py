#!/usr/bin/env python3
"""Build the ranked sampling frame for the fix-origins study.

Population: first-parent commits on TIP since SINCE whose subject starts with
"fix" (any case) and that change at least one non-test file under a product
directory. Rank = order of sha256("fix-origins-v1:" + full sha).

Usage (from the repo root):
    python3 research/fix-origins/scripts/sample.py > research/fix-origins/population.tsv

The frame is fixed by TIP and SINCE. Do not change them when extending the
sample; take the next ranks instead.
"""
import hashlib
import os
import subprocess

# The checkout is a partial clone: a missing object must fail, never trigger a network fetch.
os.environ["GIT_NO_LAZY_FETCH"] = "1"
import sys

TIP = "e6b42e31bc1522b8596958fbdd85c394b23fca7b"
SINCE = "2026-11-01T00:00:00Z"  # explicit UTC so the frame does not depend on the local time zone
SALT = "fix-origins-v1:"
PRODUCT_DIRS = ("src/", "ui/", "extensions/", "packages/", "apps/")
TEST_MARKERS = (".test.", "/test/", "test-support", "fixtures")


def is_product_file(path: str) -> bool:
    return path.startswith(PRODUCT_DIRS) and not any(m in path for m in TEST_MARKERS)


def main() -> None:
    # One git log call: header line per commit, then its changed paths.
    out = subprocess.run(
        ["git", "log", "--first-parent", f"--since={SINCE}", "--no-renames",
         "--format=\x01%H\x02%cI\x02%s", "--name-only", TIP],
        check=True, capture_output=True, text=True).stdout
    total = fixes = 0
    rows = []
    for block in out.split("\x01")[1:]:
        lines = block.split("\n")
        sha, date, subject = lines[0].split("\x02", 2)
        total += 1
        if not subject.lower().startswith("fix"):
            continue
        fixes += 1
        if any(is_product_file(p) for p in lines[1:] if p):
            key = hashlib.sha256((SALT + sha).encode()).hexdigest()
            rows.append((key, sha, date, subject))
    rows.sort()
    print("rank\tsha\tdate\tsubject")
    for i, (_, sha, date, subject) in enumerate(rows, 1):
        print(f"{i}\t{sha}\t{date}\t{subject.replace(chr(9), ' ')}")
    print(f"commits={total} fix_subjects={fixes} population={len(rows)}", file=sys.stderr)


if __name__ == "__main__":
    main()
