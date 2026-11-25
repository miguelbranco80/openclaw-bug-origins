#!/usr/bin/env python3
"""Question 23. Do changes cause more bugs when they edit files that other people have also been editing, or files
the author has not touched before?

Reads: commits.tsv, sampled_fixes.jsonl. Only commits that edit existing code files are compared.
  shared: for each code file the commit edits, the number of other authors who changed that file in the 14 days
          before, averaged over the commit's edited files. Commits before 24 Sep 2026 are left out, because the
          commit list starts on 10 Sep and has no earlier history to look back on.
  familiar: of the code files the commit edits, how many the same author had already changed since 10 Sep.
          Commits before 1 Oct 2026 are left out for the same reason.
Method: `compare_commits` in common.py.

Usage: python3 questions/q23_do_files_many_people_edit_cause_more_bugs.py
"""
import charts
from common import Result, compare_commits, load_commits, recent_causes

SHARED = [("low", "Fewer than 1 other person per file in the last 14 days"), ("mid", "1 to 2 other people per file"),
          ("high", "2 or more other people per file")]
FAMILIAR = [("all", "The author had changed every edited file before"), ("some", "Some of them"), ("none", "None of them")]


def shared(commit):
    if commit["edited_code_files"] == 0 or commit["committed_at"] < "2026-09-24":
        return None
    others = commit["other_recent_authors_per_file"]
    return "low" if others < 1 else "mid" if others < 2 else "high"


def familiar(commit):
    if commit["edited_code_files"] == 0 or commit["committed_at"] < "2026-10-01":
        return None
    share = commit["familiar_code_files"] / commit["edited_code_files"]
    return "none" if share == 0 else "all" if share == 1 else "some"


def main(quiet=False):
    commits = load_commits()
    causes = recent_causes(commits)
    out = Result("q23")
    compare_commits(out, "shared", commits, causes, shared, SHARED, "low")
    compare_commits(out, "familiar", commits, causes, familiar, FAMILIAR, "all")
    out.chart(charts.bars(
        "q23-bugs-by-how-many-people-edit-the-files", "Bugs per 100 changes, by how many other people were editing the same files",
        [{"label": label, "value": out.value("shared_rate_" + key),
          "note": f"{out.value('shared_bugs_' + key)} sampled bugs, {out.value('shared_share_' + key)}% of all commits"}
         for key, label in SHARED], unit="", top=None),
        "Each bar is the number of bugs per 100 changes of that kind. The first row is changes to files that mostly "
        "only their author had been editing; the rows below are changes to files that other people had also changed "
        "in the previous two weeks. Longer bars mean more bugs per change.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
