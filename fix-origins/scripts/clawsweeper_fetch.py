#!/usr/bin/env python3
"""Fetch, for every causing PR in cases.jsonl, the PR's comments (with edit history), reviews and commits.

Read-only GitHub GraphQL through `gh`. One query per PR, cached in clawsweeper/raw/<pr>.json.
Usage (from research/fix-origins): python3 scripts/clawsweeper_fetch.py
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "clawsweeper", "raw")

QUERY = """
query($n: Int!) {
  rateLimit { remaining resetAt }
  repository(owner: "openclaw", name: "openclaw") {
    pullRequest(number: $n) {
      number title createdAt mergedAt isDraft
      mergedBy { login } author { login }
      changedFiles additions deletions headRefOid
      mergeCommit { oid }
      commits(last: 100) { totalCount nodes { commit { oid committedDate messageHeadline } } }
      comments(first: 100) {
        totalCount
        nodes {
          databaseId author { login } createdAt lastEditedAt body
          userContentEdits(first: 100) { totalCount nodes { editedAt diff } }
        }
      }
      reviews(first: 100) { totalCount nodes { author { login } state submittedAt body } }
    }
  }
}
"""


def main():
    os.makedirs(RAW, exist_ok=True)
    prs = set()
    with open(os.path.join(HERE, "cases.jsonl")) as handle:
        for line in handle:
            case = json.loads(line)
            if case.get("cause_sha") and case.get("cause_pr"):
                prs.add(case["cause_pr"])
    for number in sorted(prs):
        out = os.path.join(RAW, f"{number}.json")
        if os.path.exists(out):
            continue
        result = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"n={number}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"{number}: FAILED {result.stderr.strip()[:200]}", file=sys.stderr)
            continue
        data = json.loads(result.stdout)
        with open(out, "w") as handle:
            json.dump(data["data"]["repository"]["pullRequest"], handle)
        remaining = data["data"]["rateLimit"]["remaining"]
        if remaining < 200:
            print(f"rate limit low ({remaining}); stopping", file=sys.stderr)
            break
        time.sleep(0.2)
    print(f"cached {len(os.listdir(RAW))} of {len(prs)}")


if __name__ == "__main__":
    main()
