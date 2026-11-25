#!/usr/bin/env python3
"""Question 11. Do changes committed straight to main, without a pull request, cause more bugs?

Reads: sampled_fixes.jsonl, commits.tsv. A commit counts as "straight to main" when its title carries no pull
request number.
Method: as in question 4, bugs fixed in the three weeks per 100 commits made since 10 Sep 2026, also within size
groups so that size does not masquerade as route.
Answer in short: no sign of it. Direct commits carried fewer bugs per commit, and they are smaller. Few cases.

Usage: python3 questions/q11_does_skipping_a_pull_request_matter.py
"""
import statistics

from common import SCALE, Result, load, load_commits, ratio_interval, traced


def main(quiet=False):
    commits = load_commits()
    causes = [f["cause_sha"] for f in traced(load("sampled_fixes.jsonl")) if f["cause_sha"] in commits]
    direct = {sha for sha, c in commits.items() if not c["pr_number"]}
    with_pr = len(commits) - len(direct)
    bugs_direct = sum(sha in direct for sha in causes)
    bugs_pr = len(causes) - bugs_direct
    out = Result("q11")
    out.add("commits", "commits_pr", "Through a pull request", with_pr)
    out.add("commits", "commits_direct", "Straight to main", len(direct))
    out.add("bugs", "bugs_pr", "Through a pull request", bugs_pr)
    out.add("bugs", "bugs_direct", "Straight to main", bugs_direct)
    out.add("per_commit", "per_commit_pr", "Through a pull request", round(100 * bugs_pr * SCALE / with_pr, 2))
    out.add("per_commit", "per_commit_direct", "Straight to main", round(100 * bugs_direct * SCALE / len(direct), 2))
    ratio = ratio_interval(bugs_direct, len(direct), bugs_pr, with_pr)
    if ratio:
        out.add("size", "direct_ratio", "Bugs per commit, straight to main against through a pull request", *ratio)
    out.add("size", "direct_share_pct", "Share of commits made straight to main", round(100 * len(direct) / len(commits), 1))
    out.add("size", "median_files_direct", "Median files changed, straight to main",
            int(statistics.median(commits[sha]["files_changed"] for sha in direct)))
    out.add("size", "median_files_pr", "Median files changed, through a pull request",
            int(statistics.median(c["files_changed"] for sha, c in commits.items() if sha not in direct)))
    small = lambda sha: commits[sha]["files_changed"] <= 5
    for key, label, keep in (("small", "Changes of 1 to 5 files", small), ("larger", "Changes of 6 files or more", lambda sha: not small(sha))):
        n_direct = sum(keep(sha) for sha in direct)
        n_pr = sum(keep(sha) for sha in commits if sha not in direct)
        b_direct = sum(keep(sha) and sha in direct for sha in causes)
        b_pr = sum(keep(sha) and sha not in direct for sha in causes)
        out.add("strat_pr", "strat_pr_" + key, label, round(100 * b_pr * SCALE / n_pr, 2))
        out.add("strat_direct", "strat_direct_" + key, label, round(100 * b_direct * SCALE / n_direct, 2))
        out.add("strat_bugs", "strat_bugs_direct_" + key, label + ": sampled bugs from direct commits", b_direct)

    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
