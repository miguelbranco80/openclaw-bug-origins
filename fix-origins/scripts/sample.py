#!/usr/bin/env python3
"""Build the ranked sampling frame: fix-origins/population.tsv.

Population: first-parent commits on the pinned commit, in each period ("frame") of study.json, whose subject starts
with "fix" (any case) and that change at least one non-test file under a product directory.

Within a frame, fixes are ordered by sha256("fix-origins-v1:" + full sha), which is as good as a lottery, and the
first `sample` of them are the sample. Frame 1 has ranks 1, 2, 3, ...; frame 2 has ranks 100001, 100002, ...; so a
fix keeps its rank when a frame is added or a sample is enlarged, and stored answers stay valid.

Run from the root of the openclaw clone (study.py does this): python3 <study>/fix-origins/scripts/sample.py
"""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pipeline.settings import FIX, frame_offset, git_env, settings  # noqa: E402

SALT = "fix-origins-v1:"
PRODUCT_DIRS = ("src/", "ui/", "extensions/", "packages/", "apps/")
TEST_MARKERS = (".test.", "/test/", "test-support", "fixtures")


def is_product_file(path: str) -> bool:
    return path.startswith(PRODUCT_DIRS) and not any(m in path for m in TEST_MARKERS)


def frame_rows(frame, tip):
    # One git log call: header line per commit, then its changed paths.
    command = ["git", "log", "--first-parent", f"--since={frame['since']}", "--no-renames",
               "--format=\x01%H\x02%cI\x02%s", "--name-only"]
    if frame.get("until"):
        command.append(f"--until={frame['until']}")
    out = subprocess.run(command + [frame.get("tip") or tip], check=True, capture_output=True, text=True,
                         env=git_env()).stdout
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
            rows.append((hashlib.sha256((SALT + sha).encode()).hexdigest(), sha, date, subject))
    rows.sort()
    print(f"frame {frame['id']}: commits={total} fix_subjects={fixes} population={len(rows)} sample={frame['sample']}")
    return rows


def main() -> None:
    data = settings()
    seen = set()
    with open(os.path.join(FIX, "population.tsv"), "w") as out:
        out.write("rank\tsha\tdate\tsubject\n")
        for frame in data["frames"]:
            rows = [row for row in frame_rows(frame, data["tip"]) if row[1] not in seen]
            seen.update(row[1] for row in rows)
            for i, (_, sha, date, subject) in enumerate(rows, 1):
                out.write(f"{frame_offset(frame) + i}\t{sha}\t{date}\t{subject.replace(chr(9), ' ')}\n")


if __name__ == "__main__":
    main()
