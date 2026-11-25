#!/usr/bin/env python3
"""Question 15. How does this project review and merge changes, in numbers?

Reads: commits.tsv (every commit on main since 10 Sep 2026), changes.jsonl (the 400 pull requests of the random
comparison sample). Everything here is counted from git and GitHub; nothing is judged.
This is a description, to set beside what published studies report for other projects.

Usage: python3 questions/q15_how_does_the_project_review_and_merge.py
"""
import collections
import statistics
from datetime import datetime

import charts
from common import Result, load, load_commits


def main(quiet=False):
    commits = list(load_commits().values())
    sample = [c for c in load("changes.jsonl") if c["in_comparison_sample"]]
    n, m = len(commits), len(sample)
    times = sorted(datetime.fromisoformat(c["committed_at"]) for c in commits)
    days = (times[-1] - times[0]).total_seconds() / 86400
    sizes = [c["files_changed"] for c in commits]
    share = lambda count, total: round(100 * count / total, 1)
    out = Result("q15")
    out.add("size", "commits", "Commits on main, 10 Sep to 22 Nov 2026", n)
    out.add("size", "commits_per_day", "Commits per day", round(n / days))
    out.add("size", "fix_title_pct", "Share of commits titled fix", share(sum(c["title_prefix"] == "fix" for c in commits), n))
    out.add("size", "under_10_files_pct", "Share of commits changing fewer than 10 files", share(sum(s < 10 for s in sizes), n))
    out.add("size", "over_100_files_pct", "Share of commits changing more than 100 files", share(sum(s > 100 for s in sizes), n))
    out.add("size", "mean_files", "Mean files changed per commit", round(statistics.mean(sizes), 1))
    out.add("size", "median_files", "Median files changed per commit", int(statistics.median(sizes)))
    out.add("size", "sample", "Pull requests in the random comparison sample", m)

    out.add("practice", "self_merged_pct", "Merged by its own author", share(sum(c["self_merged"] for c in sample), m))
    out.add("practice", "no_human_review_pct", "Merged with no review by a person",
            share(sum(not c["human_review_before_merge"] for c in sample), m))
    out.add("practice", "bot_reviewed_pct", "Reviewed by the bot before merge",
            share(sum(c["bot_review"] != "no review before merge" for c in sample), m))
    out.add("practice", "bot_objected_pct", "Merged while the bot said blocked or needs changes",
            share(sum(c["bot_verdict_at_merge"] in ("blocked", "needs-changes") for c in sample), m))
    out.add("practice", "under_hour_pct", "Merged within an hour of being opened", share(sum(c["minutes_open"] < 60 for c in sample), m))
    out.add("size", "human_review_pct", "Share with a review by a person before merge",
            share(sum(c["human_review_before_merge"] for c in sample), m))
    out.add("size", "median_minutes_open", "Median minutes from opening a pull request to merging it",
            round(statistics.median(c["minutes_open"] for c in sample)))
    gaps = [c["minutes_bot_review_to_merge"] for c in sample if c["minutes_bot_review_to_merge"] is not None]
    out.add("size", "median_minutes_after_bot", "Median minutes from the bot's review to the merge", round(statistics.median(gaps)))
    out.add("size", "mergers", "Distinct people who merged a fetched pull request",
            len({c["merged_by"] for c in load("changes.jsonl") if c["merged_by_group"] == "maintainer"}))
    authors = collections.Counter(c["author"] for c in sample)
    out.add("size", "top_author_pct", "Share of sampled pull requests opened by the most active account",
            share(authors.most_common(1)[0][1], m))
    by_group = collections.Counter(c["author_group"] for c in sample)
    for key, label in (("maintainer", "Opened by a maintainer"), ("automation", "Opened by an automation account"),
                       ("outside contributor", "Opened by an outside contributor")):
        out.add("authors", "authors_" + key.replace(" ", "_"), label, share(by_group[key], m))

    out.chart(charts.bars("q15-how-changes-are-merged", "How ordinary pull requests were reviewed and merged, in percent",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("practice")], unit="%", top=100))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
