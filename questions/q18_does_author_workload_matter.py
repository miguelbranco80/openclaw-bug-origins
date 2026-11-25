#!/usr/bin/env python3
"""Question 18. Do changes cause more bugs when their author is landing a great many changes that day, landing them
minutes apart, or having a heavier day than their own usual?

Reads: commits.tsv (every commit on main since 10 Sep 2026, with how many commits the same author landed that UTC
day, the minutes since that author's previous commit, and the author's rank), sampled_fixes.jsonl.
An author's usual day is the median number of commits over the days they landed anything; that comparison uses
authors active on ten or more days, and is repeated without the single most active author, who lands over half of
all commits.
Method: `compare_commits` in common.py: bugs per 100 commits at each level, and the rate relative to a baseline with
the size and kind of the change held equal.

Usage: python3 questions/q18_does_author_workload_matter.py
"""
import collections
import statistics

from common import Result, compare_commits, load_commits, recent_causes, utc_day

LOAD = [("1to5", "Author landed 1 to 5 changes that day"), ("6to20", "6 to 20 that day"),
        ("21to50", "21 to 50 that day"), ("51to150", "51 to 150 that day"), ("over150", "Over 150 that day")]
GAP = [("hour", "An hour or more after the author's previous change"), ("tens", "10 to 60 minutes after it"),
       ("fast", "Under 10 minutes after it")]
OWN = [("light", "A light day for that author (under three quarters of their usual)"),
       ("usual", "A usual day for that author"), ("heavy", "A heavy day (over one and a half times their usual)")]


def load_level(commit):
    n = commit["author_commits_that_day"]
    return "1to5" if n <= 5 else "6to20" if n <= 20 else "21to50" if n <= 50 else "51to150" if n <= 150 else "over150"


def gap_level(commit):
    gap = commit["minutes_since_author_previous"]
    if gap is None:
        return None
    return "fast" if gap < 10 else "tens" if gap < 60 else "hour"


def main(quiet=False):
    commits = load_commits()
    causes = recent_causes(commits)
    days = collections.defaultdict(dict)
    for commit in commits.values():
        days[commit["author_rank"]][utc_day(commit["committed_at"])] = commit["author_commits_that_day"]
    usual = {author: statistics.median(loads.values()) for author, loads in days.items() if len(loads) >= 10}

    def own_level(commit):
        if commit["author_rank"] not in usual:
            return None
        ratio = commit["author_commits_that_day"] / usual[commit["author_rank"]]
        return "light" if ratio < 0.75 else "usual" if ratio <= 1.5 else "heavy"
    out = Result("q18")
    compare_commits(out, "load", commits, causes, load_level, LOAD, "1to5")
    compare_commits(out, "gap", commits, causes, gap_level, GAP, "hour")
    compare_commits(out, "own", commits, causes, own_level, OWN, "light")
    compare_commits(out, "ownrest", commits, causes, lambda c: None if c["author_rank"] == 1 else own_level(c), OWN, "light")
    loads = [c["author_commits_that_day"] for c in commits.values()]
    gaps = [c["minutes_since_author_previous"] for c in commits.values() if c["minutes_since_author_previous"] is not None]
    out.add("size", "commits", "Commits on main since 10 Sep 2026", len(commits))
    out.add("size", "bugs", "Sampled bugs whose causing commit is among them", len(causes))
    out.add("size", "authors", "Distinct commit authors", len(days))
    out.add("size", "steady_authors", "Authors active on ten or more days", len(usual))
    out.add("size", "median_author_load", "For the median commit, changes its author landed that day", int(statistics.median(loads)))
    out.add("size", "median_gap", "Median minutes since the same author's previous change", round(statistics.median(gaps), 1))
    out.add("size", "over50_pct", "Share of commits whose author landed over 50 that day, %",
            round(100 * sum(n > 50 for n in loads) / len(loads)))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
