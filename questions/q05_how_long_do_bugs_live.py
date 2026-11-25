#!/usr/bin/env python3
"""Question 5. How long did a bug stay on main before it was fixed?

Reads: sampled_fixes.jsonl, named_cause_study.json.
Days are the commit time of the fix minus the commit time of the causing change.
Answer in short: about three weeks for a working thing broken later, unless the fix says what caused it, in which
case it was fixed within a day.

Usage: python3 questions/q05_how_long_do_bugs_live.py
"""
import statistics

import charts
from common import POPULATION, SAMPLE, Result, load, traced, wilson


def main(quiet=False):
    bugs = traced(load("sampled_fixes.jsonl"))
    never = [f for f in bugs if f["origin"] == "never-worked"]
    broke = [f for f in bugs if f["origin"] == "regression"]
    days = [f["cause"]["days_to_fix"] for f in broke]
    out = Result("q05")
    for metric, label, test in (
        ("age_day", "Under a day", lambda d: d < 1), ("age_week", "1 to 7 days", lambda d: 1 <= d < 7),
        ("age_month", "7 to 30 days", lambda d: 7 <= d < 30), ("age_more", "Over 30 days", lambda d: d >= 30),
    ):
        out.add("age", metric, label, sum(test(d) for d in days))
    named = [f["cause"]["days_to_fix"] for f in broke if f["fix_names_cause"]]
    unnamed = [f["cause"]["days_to_fix"] for f in broke if not f["fix_names_cause"]]
    out.add("lifetime", "median_broke", "Working things broken later, all", round(statistics.median(days), 1))
    out.add("lifetime", "median_named", "Broken later, fix says what caused it", round(statistics.median(named), 1))
    out.add("lifetime", "median_unnamed", "Broken later, fix does not say", round(statistics.median(unnamed), 1))
    out.add("lifetime", "median_never", "New code that never worked",
            round(statistics.median(f["cause"]["days_to_fix"] for f in never), 1))
    out.add("size", "named_count", "Broken-later fixes that say what caused the bug", len(named))
    out.add("size", "broke_count", "Broken-later bugs in the sample", len(broke))
    low, high = wilson(len(broke), SAMPLE)
    out.add("size", "broke_scaled", "Broken-later bugs fixed in the three weeks, scaled from the sample",
            int(round(len(broke) / SAMPLE * POPULATION, -1)), int(round(low / 100 * POPULATION, -1)),
            int(round(high / 100 * POPULATION, -1)))
    out.add("size", "first_study_median_days", "Median days in the first, wording-based study",
            next(r["value"] for r in load("named_cause_study.json") if r["metric"] == "median_days"))

    out.chart(charts.bars("q05-age-of-broken-later-bugs", "Broken-later bugs, by time from cause to fix",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("age")]),
              f"Each bar is a number of broken-later bugs. The four bars add up to {len(broke)}.")
    out.chart(charts.bars(
        "q05-median-days-to-fix", "Median days from the causing change to the fix, for three kinds of bug",
        [{"label": "Broken later, and the fix says what caused it", "value": out.value("median_named"),
          "note": f"{len(named)} bugs"},
         {"label": "Broken later, and the fix does not say", "value": out.value("median_unnamed"),
          "note": f"{len(unnamed)} bugs"},
         {"label": "New code that never worked", "value": out.value("median_never"), "note": f"{len(never)} bugs"}],
        unit=" days"),
        "Each bar is the middle value of days on main before the fix, for one group of bugs. The three groups do not "
        "overlap.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
