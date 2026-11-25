#!/usr/bin/env python3
"""Question 17. Are the bugs spread evenly over changes, or concentrated in changes one could point at beforehand?

Reads: changes.jsonl. Three warning signs, each visible before or at merge:
  the review bot said "blocked" or "needs changes";
  the pull request had been open a day or more;
  the change touched more than 30 files.
For each sign, and for combinations, this reports what share of ordinary changes carry it and what share of the
sampled bugs came from changes that carry it.
The three signs were chosen after seeing findings 4, 12 and 14 on this same data, so the figures describe this
period; they are not a tested prediction.

Usage: python3 questions/q17_how_concentrated_are_the_bugs.py
"""
import charts
from common import Result, load

SIGNS = {
    "objected": lambda c: c["bot_verdict_at_merge"] in ("blocked", "needs-changes"),
    "long": lambda c: c["minutes_open"] >= 1440,
    "big": lambda c: c["files_changed"] > 30,
}
GROUPS = [
    ("objected", "The bot objected", SIGNS["objected"]),
    ("long", "Open a day or more", SIGNS["long"]),
    ("big", "More than 30 files", SIGNS["big"]),
    ("any", "At least one of the three signs", lambda c: sum(sign(c) for sign in SIGNS.values()) >= 1),
    ("two", "At least two of the three signs", lambda c: sum(sign(c) for sign in SIGNS.values()) >= 2),
    ("none", "None of the three signs", lambda c: sum(sign(c) for sign in SIGNS.values()) == 0),
]


def main(quiet=False):
    changes = load("changes.jsonl")
    sample = [c for c in changes if c["in_comparison_sample"]]
    causing = [c for c in changes if c["sampled_bugs"]]
    total = sum(c["sampled_bugs"] for c in causing)
    out = Result("q17")
    out.add("size", "bugs", "Sampled bugs traced to a fetched pull request", total)
    out.add("size", "sample", "Ordinary pull requests in the comparison sample", len(sample))
    for key, label, test in GROUPS:
        bugs = sum(c["sampled_bugs"] for c in causing if test(c))
        out.add("changes_pct", "changes_pct_" + key, label, round(100 * sum(test(c) for c in sample) / len(sample), 1))
        out.add("bugs_pct", "bugs_pct_" + key, label, round(100 * bugs / total))
        out.add("bugs", "bugs_" + key, label, bugs)
    out.chart(charts.bars(
        "q17-share-of-bugs-by-warning-sign", "Share of the traced bugs that came from changes with each warning sign",
        [{"label": label, "value": out.value("bugs_pct_" + key),
          "note": f"these are {out.value('changes_pct_' + key)}% of all changes"} for key, label, _ in GROUPS],
        unit="%", top=100),
        "Each bar is the percentage of traced bugs whose causing change had that sign. The gray note says how common "
        "such changes are. A bar much longer than its note's percentage means bugs are concentrated there. The first "
        "three rows overlap; the last three are combinations of them.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
