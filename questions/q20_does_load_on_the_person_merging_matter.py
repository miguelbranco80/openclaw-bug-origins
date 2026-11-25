#!/usr/bin/env python3
"""Question 20. Do pull requests cause more bugs when the person who merged them merged a great many that day?

Reads: commits.tsv, pull_requests.tsv (who merged each pull request and when), sampled_fixes.jsonl.
For every commit that came from a pull request, the load is the number of pull requests the same person merged on
the same UTC day. Commits made straight to main are left out.
Method: `compare_commits` in common.py.

Usage: python3 questions/q20_does_load_on_the_person_merging_matter.py
"""
import collections
import statistics

from common import Result, compare_commits, load_commits, load_pull_requests, recent_causes, utc_day

LOAD = [("1to5", "The merger merged 1 to 5 pull requests that day"), ("6to20", "6 to 20 that day"),
        ("21to50", "21 to 50 that day"), ("51to150", "51 to 150 that day"), ("over150", "Over 150 that day")]


def main(quiet=False):
    commits = load_commits()
    pulls = load_pull_requests()
    merged = {number: pull for number, pull in pulls.items() if pull["merged_by"] and pull["merged_at"]}
    per_day = collections.Counter((pull["merged_by"], utc_day(pull["merged_at"])) for pull in merged.values())
    people_per_day = collections.defaultdict(set)
    for pull in merged.values():
        people_per_day[utc_day(pull["merged_at"])].add(pull["merged_by"])

    def level(commit):
        pull = merged.get(commit["pr_number"])
        if not pull:
            return None
        n = per_day[(pull["merged_by"], utc_day(pull["merged_at"]))]
        return "1to5" if n <= 5 else "6to20" if n <= 20 else "21to50" if n <= 50 else "51to150" if n <= 150 else "over150"
    out = Result("q20")
    compare_commits(out, "load", commits, recent_causes(commits), level, LOAD, "1to5")
    out.add("size", "pulls", "Merged pull requests with a known merger", len(merged))
    out.add("size", "mergers", "Distinct people who merged at least one", len({p["merged_by"] for p in merged.values()}))
    out.add("size", "people_per_day", "Median number of people merging on a day",
            int(statistics.median(len(people) for people in people_per_day.values())))
    top = collections.Counter(p["merged_by"] for p in merged.values()).most_common(3)
    out.add("size", "top_pct", "Share merged by the most active merger, %", round(100 * top[0][1] / len(merged), 1))
    out.add("size", "top3_pct", "Share merged by the three most active, %", round(100 * sum(n for _, n in top) / len(merged), 1))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
