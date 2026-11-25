#!/usr/bin/env python3
"""Question 10. Did one of the project's written rules already cover what went wrong?

Reads: named_cause_study.json, the figures of the first study (29 bugs whose fix names the causing change; see
detection-check/report.md). Those figures were entered from that report, not computed here.
Answer in short: in 24 of 29, no rule covered it. The sample favors quickly fixed bugs.

Usage: python3 questions/q10_did_a_written_rule_cover_it.py
"""
import charts
from common import Result, load


def main(quiet=False):
    out = Result("q10")
    for row in load("named_cause_study.json"):
        out.add(row["group"], row["metric"], row["label"], row["value"])
    out.chart(charts.bars("q10-did-a-rule-cover-it", "Whether a written rule covered what went wrong, of 29 bugs",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("rules")]),
              "Each bar is a number of bugs. The four bars add up to 29.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
