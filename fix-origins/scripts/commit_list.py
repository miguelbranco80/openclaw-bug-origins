#!/usr/bin/env python3
"""List every commit on main since 2026-09-10 (UTC) with its size and title facts: dataset/commits.tsv.

Run from the root of an openclaw/openclaw clone, with this repository checked out as `research/`.
Columns: sha, committed_at, files_changed, pr_number (empty when the title carries none), title_prefix.

Usage: python3 research/fix-origins/scripts/commit_list.py
"""
import os
import re
import subprocess

TIP = "e6b42e31bc1522b8596958fbdd85c394b23fca7b"
SINCE = "2026-09-10T00:00:00Z"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "dataset", "commits.tsv")


def main():
    log = subprocess.run(
        ["git", "log", "--first-parent", f"--since={SINCE}", "--no-renames", "--format=COMMIT %H %cI %s",
         "--name-only", TIP],
        capture_output=True, text=True, check=True, env=dict(os.environ, GIT_NO_LAZY_FETCH="1"),
    ).stdout
    rows = []
    for line in log.splitlines():
        if line.startswith("COMMIT "):
            _, sha, date, subject = (line.split(" ", 3) + [""])[:4]
            prefix = re.match(r"([a-zA-Z]+)", subject)
            number = re.search(r"\(#(\d+)\)\s*$", subject)
            rows.append([sha, date, 0, number.group(1) if number else "", prefix.group(1).lower() if prefix else "other"])
        elif line:
            rows[-1][2] += 1
    with open(OUT, "w") as handle:
        handle.write("sha\tcommitted_at\tfiles_changed\tpr_number\ttitle_prefix\n")
        for row in rows:
            handle.write("\t".join(map(str, row)) + "\n")
    print(len(rows), "commits")


if __name__ == "__main__":
    main()
