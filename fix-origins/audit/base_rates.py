#!/usr/bin/env python3
"""Measure what an ordinary commit on main looks like, for comparison with the bug-causing commits.

Reads only local git history (first-parent of the pinned tip). Writes audit/base-rates.json.
Usage (from the repo root): GIT_NO_LAZY_FETCH=1 python3 research/fix-origins/audit/base_rates.py
"""
import collections
import json
import os
import re
import statistics
import subprocess

TIP = "e6b42e31bc1522b8596958fbdd85c394b23fca7b"
SINCE = "2026-09-10"  # local history is complete from here; older commits sit behind the clone's graft
HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    out = subprocess.run(
        ["git", "log", "--first-parent", f"--since={SINCE}", "--no-renames", "--format=COMMIT %s", "--name-only", TIP],
        capture_output=True, text=True, env=env, check=True,
    ).stdout
    prefixes = collections.Counter()
    sizes = []
    for line in out.splitlines():
        if line.startswith("COMMIT "):
            match = re.match(r"([a-zA-Z]+)", line[7:])
            prefixes[match.group(1).lower() if match else "other"] += 1
            sizes.append(0)
        elif line:
            sizes[-1] += 1
    total = len(sizes)
    result = {
        "since": SINCE,
        "tip": TIP,
        "commits": total,
        "titled_fix": prefixes["fix"],
        "titled_feat": prefixes["feat"],
        "pct_fix": round(100 * prefixes["fix"] / total, 1),
        "pct_feat": round(100 * prefixes["feat"] / total, 1),
        "median_files": statistics.median(sizes),
        "pct_over_30_files": round(100 * sum(size > 30 for size in sizes) / total, 1),
        "pct_over_100_files": round(100 * sum(size > 100 for size in sizes) / total, 1),
    }
    with open(os.path.join(HERE, "base-rates.json"), "w") as handle:
        json.dump(result, handle, indent=1)
    print(result)


if __name__ == "__main__":
    main()
