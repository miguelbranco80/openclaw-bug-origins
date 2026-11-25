#!/usr/bin/env python3
"""Question 9. What would a reviewer have needed in front of them to see each bug?

Reads: blind_review.jsonl (each of the 30 cases carries a reader's tag: the changed lines alone, other code in the
repository, or knowledge from outside the repository).
Answer in short: nine of the 30 needed outside knowledge, and no reviewer named any of those. One reader's
judgment on few cases.

Usage: python3 questions/q09_could_the_bug_be_seen_by_reading.py
"""
import charts
from common import Result, load

NEEDS = (("diff", "The changed lines alone"), ("repo", "Other code in the repository"),
         ("outside", "Knowledge from outside the repository"))


def main(quiet=False):
    data = load("blind_review.jsonl")
    caught = lambda r: any(v["flagged"] == "exact" for v in r["arms"].values())
    out = Result("q09")
    for needs, label in NEEDS:
        mine = [r for r in data if r["needs"] == needs]
        out.add("needs_cases", "needs_" + needs, label, len(mine))
        out.add("needs_named", "needs_named_" + needs, label, sum(caught(r) for r in mine))
    small = [r for r in data if r["files_changed"] <= 7]
    large = [r for r in data if r["files_changed"] > 7]
    out.add("size", "small_cases", "Changes of 7 files or fewer", len(small))
    out.add("size", "small_named", "Of those, bug named by a reviewer", sum(caught(r) for r in small))
    out.add("size", "large_cases", "Changes of more than 7 files", len(large))
    out.add("size", "large_named", "Of those, bug named by a reviewer", sum(caught(r) for r in large))

    cases = {r["label"]: r["value"] for r in out.group("needs_cases")}
    named = {r["label"]: r["value"] for r in out.group("needs_named")}
    out.chart(charts.part_of(
        "q09-what-each-bug-needed", "What a reviewer needed to see the bug, and how many were named",
        [{"label": label, "part": named[label], "whole": cases[label]} for _, label in NEEDS],
        "Named by at least one reviewer", "Cases"),
        "The gray bar is the number of bugs of that kind, out of 30. The blue part is how many of them any reviewer named.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
