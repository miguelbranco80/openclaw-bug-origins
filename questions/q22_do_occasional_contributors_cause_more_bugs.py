#!/usr/bin/env python3
"""Question 22. Do changes from people who contribute rarely cause more bugs than changes from the most active?

Reads: commits.tsv (author_rank: 1 for the author with the most commits since 10 Sep 2026), sampled_fixes.jsonl.
Authors are grouped by how many commits they landed in the period. Authors are told apart by commit email, so one
person using two addresses counts as two.
Method: `compare_commits` in common.py.

Usage: python3 questions/q22_do_occasional_contributors_cause_more_bugs.py
"""
import collections

from common import Result, compare_commits, load_commits, recent_causes

GROUPS = [("top", "The single most active author"), ("core", "Other authors with over 500 commits"),
          ("regular", "Authors with 21 to 500 commits"), ("occasional", "Authors with 20 commits or fewer")]


def main(quiet=False):
    commits = load_commits()
    total = collections.Counter(c["author_rank"] for c in commits.values())

    def group(commit):
        if commit["author_rank"] == 1:
            return "top"
        n = total[commit["author_rank"]]
        return "core" if n > 500 else "regular" if n > 20 else "occasional"
    out = Result("q22")
    compare_commits(out, "who", commits, recent_causes(commits), group, GROUPS, "top")
    for key, label in GROUPS:
        out.add("authors", "authors_" + key, label, len({c["author_rank"] for c in commits.values() if group(c) == key}))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
