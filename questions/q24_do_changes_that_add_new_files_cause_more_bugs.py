#!/usr/bin/env python3
"""Question 24. Do changes that add new code files cause more bugs than changes that only edit existing ones?

Reads: commits.tsv (`new_code_files`: code files the commit adds; a code file is a non-test file under src/, ui/,
extensions/, packages/ or apps/), sampled_fixes.jsonl. Only commits that change code are compared.
Method: `compare_commits` in common.py.

Usage: python3 questions/q24_do_changes_that_add_new_files_cause_more_bugs.py
"""
import charts
from common import Result, compare_commits, load_commits, recent_causes

LEVELS = [("edits", "Only edits existing code files"), ("adds", "Adds at least one new code file")]


def level(commit):
    if commit["code_files"] == 0:
        return None
    return "adds" if commit["new_code_files"] > 0 else "edits"


def main(quiet=False):
    commits = load_commits()
    causes = recent_causes(commits)
    out = Result("q24")
    compare_commits(out, "new", commits, causes, level, LEVELS, "edits")
    out.add("size", "bugs_pct_adds", "Share of the sampled bugs from changes that add a code file, %",
            round(100 * out.value("new_bugs_adds") / len(causes)))
    out.chart(charts.bars(
        "q24-bugs-by-whether-the-change-adds-files", "Bugs per 100 changes, by whether the change adds new code files",
        [{"label": label, "value": out.value("new_rate_" + key),
          "note": f"{out.value('new_bugs_' + key)} bugs, from {out.value('new_share_' + key)}% of commits"}
         for key, label in LEVELS], unit="", top=None),
        "Each bar is the number of bugs per 100 changes of that kind. The gray note gives how many of the sampled "
        "bugs came from such changes and how common such changes are.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
