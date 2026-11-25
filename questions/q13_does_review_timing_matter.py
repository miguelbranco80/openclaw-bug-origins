#!/usr/bin/env python3
"""Question 13. Do changes cause more bugs when the bot reviewed only an earlier revision, or when they merged within
minutes of its review?

Reads: changes.jsonl, commits.tsv, sampled_fixes.jsonl. Method as in question 12.

Usage: python3 questions/q13_does_review_timing_matter.py
"""
import charts
from common import Result, compare, load

COVERAGE = [("merged", "Bot reviewed the revision that merged"), ("earlier", "Bot reviewed only an earlier revision"),
            ("none", "No bot review before merge")]
SPEED = [("later", "Merged an hour or more after the bot's review"), ("hour", "Merged 10 to 60 minutes after it"),
         ("fast", "Merged within 10 minutes of it")]


def coverage(change):
    return {"reviewed the merged revision": "merged", "reviewed an earlier revision": "earlier",
            "no review before merge": "none"}[change["bot_review"]]


def speed(change):
    gap = change["minutes_bot_review_to_merge"]
    if gap is None:
        return None
    return "fast" if gap < 10 else "hour" if gap < 60 else "later"


def main(quiet=False):
    changes = load("changes.jsonl")
    out = Result("q13")
    compare(out, "coverage", changes, coverage, COVERAGE, "merged")
    compare(out, "speed", changes, speed, SPEED, "later")
    out.chart(charts.bars("q13-bugs-by-review-coverage", "Bugs per 100 changes, by which revision the bot reviewed",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("coverage_rate")]))
    out.chart(charts.bars("q13-bugs-by-time-to-merge", "Bugs per 100 changes, by time from the bot's review to merge",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("speed_rate")]))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
