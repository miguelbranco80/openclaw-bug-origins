#!/usr/bin/env python3
"""Question 14. Do changes cause more bugs depending on who opened them, whether the author merged their own change,
whether a person reviewed it, or how quickly it merged?

Reads: changes.jsonl, commits.tsv, sampled_fixes.jsonl. Method as in question 12.
"Maintainer" means GitHub lists the author as owner, member or collaborator of the repository. This compares kinds
of change, not people.

Usage: python3 questions/q14_does_who_lands_the_change_matter.py
"""
import charts
from common import Result, compare, load

AUTHOR = [("outside contributor", "Opened by an outside contributor"), ("maintainer", "Opened by a maintainer"),
          ("automation", "Opened by an automation account")]
MERGE = [("other", "Merged by someone else"), ("self", "Merged by its own author")]
HUMAN = [("yes", "A person reviewed it before merge"), ("no", "No person's review before merge")]
OPEN = [("day", "Open a day or more"), ("hours", "Open 1 to 24 hours"), ("hour", "Open under an hour")]


def main(quiet=False):
    changes = load("changes.jsonl")
    out = Result("q14")
    compare(out, "author", changes, lambda c: c["author_group"], AUTHOR, "outside contributor")
    compare(out, "merge", changes, lambda c: "self" if c["self_merged"] else "other", MERGE, "other")
    compare(out, "human", changes, lambda c: "yes" if c["human_review_before_merge"] else "no", HUMAN, "yes")
    compare(out, "open", changes,
            lambda c: "hour" if c["minutes_open"] < 60 else "hours" if c["minutes_open"] < 1440 else "day", OPEN, "day")
    out.chart(charts.bars(
        "q14-bugs-by-time-open", "Bugs per 100 changes, by how long the pull request was open",
        [{"label": label, "value": out.value("open_rate_" + key),
          "note": f"{out.value('open_bugs_' + key)} sampled bugs; {out.value('open_share_' + key)}% of changes"}
         for key, label in OPEN]),
        "Each bar is a rate: bugs fixed in the period studied that trace back to pull requests open that long, per 100 "
        "such pull requests. The three groups cover every pull request.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
