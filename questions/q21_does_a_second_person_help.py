#!/usr/bin/env python3
"""Question 21. Do pull requests that a second person merged or reviewed cause fewer bugs?

Reads: commits.tsv, pull_requests.tsv, sampled_fixes.jsonl. Pull requests opened by automation are left out.
  merged by another: the person who merged is not the person who opened it.
  reviewed by another: someone other than the author, and not automation, submitted a review before the merge.
  author can merge: the author merged at least one pull request in the period. Comparing only their pull requests
  separates "a second person merged it" from "an outside contributor wrote it", since outsiders cannot merge.
This repeats two rows of question 14 on every pull request since 10 Sep 2026 instead of a sample of 400.
Method: `compare_commits` in common.py.

Usage: python3 questions/q21_does_a_second_person_help.py
"""
from common import Result, compare_commits, load_commits, load_pull_requests, recent_causes

MERGE = [("self", "Merged by the person who opened it"), ("other", "Merged by someone else")]
REVIEW = [("none", "No other person reviewed it before the merge"), ("reviewed", "Another person reviewed it before the merge")]
PAIR = [("self", "Author can merge, and merged it themselves"), ("other", "Author can merge, but someone else merged it")]
SECOND = [("none", "No second person: self-merged and unreviewed"), ("second", "A second person merged or reviewed it")]


def main(quiet=False):
    commits = load_commits()
    pulls = {number: pull for number, pull in load_pull_requests().items()
             if pull["author_kind"] == "person" and pull["merged_by"]}

    def merge(commit):
        pull = pulls.get(commit["pr_number"])
        return pull and ("self" if pull["merged_by"] == pull["author"] else "other")

    def review(commit):
        pull = pulls.get(commit["pr_number"])
        return pull and ("reviewed" if pull["reviewers_before_merge"] else "none")

    def second(commit):
        pull = pulls.get(commit["pr_number"])
        return pull and ("second" if pull["reviewers_before_merge"] or pull["merged_by"] != pull["author"] else "none")
    mergers = {pull["merged_by"] for pull in pulls.values()}

    def pair(commit):
        pull = pulls.get(commit["pr_number"])
        if not pull or pull["author"] not in mergers:
            return None
        return "self" if pull["merged_by"] == pull["author"] else "other"
    causes = recent_causes(commits)
    out = Result("q21")
    compare_commits(out, "merge", commits, causes, merge, MERGE, "self")
    compare_commits(out, "review", commits, causes, review, REVIEW, "none")
    compare_commits(out, "second", commits, causes, second, SECOND, "none")
    compare_commits(out, "pair", commits, causes, pair, PAIR, "self")
    out.add("size", "pulls", "Merged pull requests opened by a person", len(pulls))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
