#!/usr/bin/env python3
"""Fetch each pilot case's PR title and description as they read when the PR merged.

PR descriptions are sometimes edited after merge, and two of the pilot's had been edited to mention the later fix.
This reads the description's edit history through GitHub GraphQL and keeps the last version written at or before the
merge time. Read-only; needs `gh` with a token. Writes data/pilot_pr_bodies.json.

Usage: python3 fix-origins/review-pilot/fetch_descriptions.py
"""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    ranks = json.load(open(os.path.join(HERE, "data", "pilot_ranks.json")))
    cases = {c["rank"]: c for c in (json.loads(line) for line in open(os.path.join(ROOT, "cases.jsonl")))}
    numbers = sorted({cases[rank]["cause_pr"] for rank in ranks})
    found = {}
    for start in range(0, len(numbers), 10):
        chunk = numbers[start:start + 10]
        fields = " ".join(
            f"p{n}: pullRequest(number:{n}) {{ title body mergedAt userContentEdits(first:100) {{ nodes {{ editedAt diff }} }} }}"
            for n in chunk
        )
        query = 'query { repository(owner:"openclaw", name:"openclaw") { ' + fields + " } }"
        out = subprocess.run(["gh", "api", "graphql", "-f", "query=" + query], capture_output=True, text=True, check=True)
        for key, value in json.loads(out.stdout)["data"]["repository"].items():
            found[key[1:]] = value
    bodies = {}
    for number, pr in found.items():
        edits = sorted((e["editedAt"], e["diff"]) for e in pr["userContentEdits"]["nodes"] if e["diff"] is not None)
        before = [edit for edit in edits if edit[0] <= pr["mergedAt"]]
        if not edits:
            body = pr["body"]
        elif before:
            body = before[-1][1]
        else:
            body = "(description unavailable as of merge)"
        bodies[number] = {"title": pr["title"], "body": body}
    with open(os.path.join(HERE, "data", "pilot_pr_bodies.json"), "w") as handle:
        json.dump(bodies, handle)
    print(len(bodies), "descriptions")


if __name__ == "__main__":
    main()
