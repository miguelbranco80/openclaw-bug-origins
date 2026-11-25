#!/usr/bin/env python3
"""Question 19. Do changes landed on the project's busiest days, or at weekends, cause more bugs?

Reads: commits.tsv, sampled_fixes.jsonl. Days are UTC days. A day's load is the number of commits on main that day;
days are split into three equal groups.
Method: `compare_commits` in common.py.

Usage: python3 questions/q19_does_the_day_matter.py
"""
import collections

from common import Result, compare_commits, load_commits, recent_causes, utc_day

WEEK = [("weekday", "Landed Monday to Friday"), ("weekend", "Landed Saturday or Sunday")]


def main(quiet=False):
    commits = load_commits()
    causes = recent_causes(commits)
    day_of = lambda commit: utc_day(commit["committed_at"])
    per_day = collections.Counter(day_of(c) for c in commits.values())
    ordered = sorted(per_day.values())
    low, high = ordered[len(ordered) // 3], ordered[2 * len(ordered) // 3]
    busy = [("quiet", f"Quiet days for the project (under {low} commits)"), ("middle", f"Middle days ({low} to {high - 1})"),
            ("busy", f"Busy days ({high} or more)")]

    def busy_level(commit):
        n = per_day[day_of(commit)]
        return "quiet" if n < low else "middle" if n < high else "busy"
    out = Result("q19")
    compare_commits(out, "busy", commits, causes, busy_level, busy, "quiet")
    compare_commits(out, "week", commits, causes, lambda c: "weekend" if day_of(c).weekday() >= 5 else "weekday", WEEK, "weekday")
    out.add("size", "days", "Days covered", len(per_day))
    out.add("size", "median_day", "Median commits on main per day", ordered[len(ordered) // 2])
    out.add("size", "max_day", "Most commits on main in one day", max(ordered))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
