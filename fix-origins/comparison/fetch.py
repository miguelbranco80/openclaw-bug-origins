#!/usr/bin/env python3
"""Fetch pull request facts for a comparison sample of ordinary changes and for the bug-causing changes.

The sample: commits in dataset/commits.tsv that carry a pull request number, in ascending order of
sha256("comparison-v1:" + sha); the first 400 are the comparison sample. Every sampled bug's causing commit that is in
commits.tsv and has a pull request is fetched too.

For each pull request this stores a small record under comparison/raw/<number>.json: who opened and merged it, when,
its size, and every version of the review bot's review comment reduced to its time, verdict and reviewed revision
(the comment text itself is not kept). Read-only GitHub GraphQL through `gh`; one query per pull request.

Usage: python3 fix-origins/comparison/fetch.py [--count 400]
"""
import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pipeline import gh  # noqa: E402
from pipeline.settings import Paused, settings, stop_paused  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from clawsweeper_table import is_bot, is_review, parse, verdict, versions, HEAD_RE, STATE_RE  # noqa: E402

QUERY = """
query($n: Int!) {
  rateLimit { remaining }
  repository(owner: "openclaw", name: "openclaw") {
    pullRequest(number: $n) {
      number title createdAt mergedAt isCrossRepository authorAssociation
      author { login __typename } mergedBy { login __typename }
      changedFiles additions deletions headRefOid
      commits(last: 100) { totalCount nodes { commit { oid } } }
      comments(first: 100) {
        totalCount
        nodes { author { login } createdAt body userContentEdits(first: 100) { nodes { editedAt diff } } }
      }
      reviews(first: 100) { nodes { author { login __typename } state submittedAt } }
    }
  }
}
"""


def wanted(count):
    commits = []
    with open(os.path.join(ROOT, "dataset", "commits.tsv")) as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["pr_number"]:
                commits.append(row)
    by_sha = {row["sha"]: row for row in commits}
    commits.sort(key=lambda row: hashlib.sha256(("comparison-v1:" + row["sha"]).encode()).hexdigest())
    numbers = {int(row["pr_number"]) for row in commits[:count]}
    with open(os.path.join(ROOT, "fix-origins", "cases.jsonl")) as handle:
        for line in handle:
            fix = json.loads(line)
            if fix.get("cause_sha") in by_sha:
                numbers.add(int(by_sha[fix["cause_sha"]]["pr_number"]))
    return sorted(numbers)


def slim(pr):
    reviews = []
    for comment in pr["comments"]["nodes"]:
        if not (is_bot(comment) and is_review(comment)):
            continue
        for at, text in versions(comment):
            if HEAD_RE.search(text) or STATE_RE.search(text):
                facts = parse(text)
                reviews.append({"at": at, "verdict": verdict(facts), "reviewed_head": facts["reviewed_head"]})
    humans = [r for r in pr["reviews"]["nodes"] if r["author"] and r["author"]["__typename"] == "User"]
    return {
        "number": pr["number"], "title": pr["title"], "created_at": pr["createdAt"], "merged_at": pr["mergedAt"],
        "author": (pr["author"] or {}).get("login"), "author_type": (pr["author"] or {}).get("__typename"),
        "author_association": pr["authorAssociation"], "from_fork": pr["isCrossRepository"],
        "merged_by": (pr["mergedBy"] or {}).get("login"), "merged_by_type": (pr["mergedBy"] or {}).get("__typename"),
        "changed_files": pr["changedFiles"], "additions": pr["additions"], "deletions": pr["deletions"],
        "final_head": pr["headRefOid"], "commits": [c["commit"]["oid"] for c in pr["commits"]["nodes"]],
        "comment_count": pr["comments"]["totalCount"],
        "bot_commented": any(is_bot(c) for c in pr["comments"]["nodes"]),
        "bot_review_versions": sorted(reviews, key=lambda r: r["at"]),
        "human_reviews": [{"by": r["author"]["login"], "state": r["state"], "at": r["submittedAt"]} for r in humans],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=settings()["comparison_sample"])
    parser.add_argument("--shard", default="0/1", help="i/n: fetch every n-th pull request starting at i, to run workers side by side")
    args = parser.parse_args()
    raw = os.path.join(HERE, "raw")
    os.makedirs(raw, exist_ok=True)
    numbers = wanted(args.count)
    start, step = (int(x) for x in args.shard.split("/"))
    for number in numbers[start::step]:
        out = os.path.join(raw, f"{number}.json")
        if os.path.exists(out):
            continue
        data = gh.graphql(QUERY, n=number)["data"]
        with open(out, "w") as handle:
            json.dump(slim(data["repository"]["pullRequest"]), handle)
    print(f"comparison and causing pull requests fetched: {len(os.listdir(raw))} of {len(numbers)}", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Paused as pause:
        stop_paused(pause)
