#!/usr/bin/env python3
"""Question 4. Do large changes cause more bugs: per change, and per file changed?

Reads: sampled_fixes.jsonl, commits.tsv.
Method: every commit on main since 10 Sep 2026 is put in a size group by files changed. A "bug" is one sampled fix
traced to a causing commit in that list, scaled from the sample of 300 to all 3,996 fixes in the period. So the
rates are "bugs fixed in the three weeks, per 100 commits made since 10 September".
Answer in short: per change, yes, steeply. Per file changed, no: the rate is roughly flat.

Usage: python3 questions/q04_do_large_changes_cause_more_bugs.py
"""
import collections

import charts
from common import SCALE, Result, load, load_commits, traced

GROUPS = [("1to5", "1 to 5 files", 0, 5), ("6to30", "6 to 30 files", 6, 30), ("31to100", "31 to 100 files", 31, 100),
          ("over100", "Over 100 files", 101, 10 ** 9)]


def group_of(size):
    return next(key for key, _, low, high in GROUPS if low <= size <= high)


def main(quiet=False):
    commits = load_commits()
    causes = [f["cause_sha"] for f in traced(load("sampled_fixes.jsonl")) if f["cause_sha"] in commits]
    count = collections.Counter(group_of(c["files_changed"]) for c in commits.values())
    files = collections.Counter()
    for c in commits.values():
        files[group_of(c["files_changed"])] += c["files_changed"]
    bugs = collections.Counter(group_of(commits[sha]["files_changed"]) for sha in causes)
    out = Result("q04")
    out.add("size", "bugs", "Sampled bugs with a causing commit since 10 Sep 2026", len(causes))
    for key, label, _, _ in GROUPS:
        out.add("commits", "commits_" + key, label, count[key])
        out.add("bugs", "bugs_" + key, label, bugs[key])
        out.add("per_commit", "per_commit_" + key, label, round(100 * bugs[key] * SCALE / count[key], 2))
        out.add("per_file", "per_file_" + key, label, round(1000 * bugs[key] * SCALE / files[key], 2))
    small, large = out.value("per_commit_1to5"), out.value("per_commit_over100")
    out.add("size", "per_commit_ratio", "Bugs per commit, over 100 files against 1 to 5 files", round(large / small))
    per_file = [r["value"] for r in out.group("per_file")]
    out.add("size", "per_file_low", "Lowest bugs per 1,000 files changed across size groups", min(per_file))
    out.add("size", "per_file_high", "Highest bugs per 1,000 files changed across size groups", max(per_file))

    notes = {key: f"{bugs[key]} sampled bugs from {count[key]:,} commits" for key, _, _, _ in GROUPS}
    out.chart(charts.bars("q04-bugs-per-100-commits", "Bugs per 100 commits, by size of the change",
                          [{"label": r["label"], "value": r["value"], "note": notes[r["metric"].replace("per_commit_", "")]}
                           for r in out.group("per_commit")]),
              "Each bar is a rate: bugs fixed in the three weeks that trace back to commits of that size, per 100 such "
              "commits made since 10 September. The four sizes cover every commit.")
    out.chart(charts.bars("q04-bugs-per-1000-files", "Bugs per 1,000 files changed, by size of the change",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("per_file")]),
              "The same bugs, divided by the total number of files those commits changed instead of by the number of "
              "commits.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
