#!/usr/bin/env python3
"""First look at two follow-up questions, from data already collected.

1. Do large changes cause more bugs, per change and per file changed?
2. Do changes committed straight to main, without a pull request, cause more bugs?

Uses the sampled fixes traced to a causing change (../cases.jsonl) and one row per commit on main since
2026-09-10 (commit-sizes.tsv: files changed, whether the title carries a PR number). A bug counts once per sampled
fix; counts are scaled from the sample of 300 to the 3,996 fixes in the period. Writes size-and-route.json.

To rebuild commit-sizes.tsv from a clone of openclaw/openclaw, run from the clone:
  git log --first-parent --since=2026-09-10 --no-renames --format='COMMIT %H %s' --name-only e6b42e31bc1
and count the file lines under each COMMIT line.

Usage: python3 fix-origins/audit/size_and_route.py
"""
import collections
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCALE = 3996 / 300
BUCKETS = [("1 to 5 files", 1, 5), ("6 to 30 files", 6, 30), ("31 to 100 files", 31, 100), ("Over 100 files", 101, 10 ** 9)]


def bucket(size):
    return next(name for name, low, high in BUCKETS if low <= max(size, 1) <= high)


def main():
    commits = {}
    with open(os.path.join(HERE, "commit-sizes.tsv")) as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            commits[row["sha"]] = (int(row["files_changed"]), row["has_pr_number"] == "1")
    cases = [json.loads(line) for line in open(os.path.join(ROOT, "cases.jsonl"))]
    causes = [c["cause_sha"] for c in cases if c.get("cause_sha") and c["cause_sha"] in commits]
    total = collections.Counter(bucket(size) for size, _ in commits.values())
    files = collections.Counter()
    for size, _ in commits.values():
        files[bucket(size)] += size
    bugs = collections.Counter(bucket(commits[sha][0]) for sha in causes)
    by_size = []
    for name, _, _ in BUCKETS:
        by_size.append({
            "size": name, "commits": total[name], "sampled_bugs": bugs[name],
            "bugs_per_100_commits": round(100 * bugs[name] * SCALE / total[name], 2),
            "bugs_per_1000_files_changed": round(1000 * bugs[name] * SCALE / files[name], 2),
        })
    direct = [sha for sha, (_, has_pr) in commits.items() if not has_pr]
    direct_bugs = sum(not commits[sha][1] for sha in causes)
    with_pr = len(commits) - len(direct)
    by_route = [
        {"route": "Through a pull request", "commits": with_pr, "sampled_bugs": len(causes) - direct_bugs,
         "bugs_per_100_commits": round(100 * (len(causes) - direct_bugs) * SCALE / with_pr, 2)},
        {"route": "Straight to main", "commits": len(direct), "sampled_bugs": direct_bugs,
         "bugs_per_100_commits": round(100 * direct_bugs * SCALE / len(direct), 2)},
    ]
    result = {"commits": len(commits), "traced_bugs": len(causes), "by_size": by_size, "by_route": by_route}
    with open(os.path.join(HERE, "size-and-route.json"), "w") as handle:
        json.dump(result, handle, indent=1)
    for row in by_size + by_route:
        print(row)


if __name__ == "__main__":
    main()
