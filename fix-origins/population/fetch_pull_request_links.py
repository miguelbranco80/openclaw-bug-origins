#!/usr/bin/env python3
"""Fetch the branch name of every pull request in dataset/commits.tsv, and the issue it closes if it closes one:
dataset/pull_request_links.tsv.

One row per pull request number that appears in commits.tsv. Read-only GitHub GraphQL through `gh`, 50 pull
requests per query, three queries at a time; each answer is kept under population/raw-links/ so a rerun fetches
only the pull requests it does not have yet.

Columns:
  number
  head_branch          the name of the branch the pull request was merged from
  closes_issue         number of the first issue GitHub records this pull request as closing, empty when none
  issue_author         who filed that issue
  issue_author_kind    person or automation

Usage: python3 fix-origins/population/fetch_pull_request_links.py
"""
import csv
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from pipeline import gh  # noqa: E402
from pipeline.settings import Paused, stop_paused  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(HERE, "raw-links")
OUT = os.path.join(ROOT, "dataset", "pull_request_links.tsv")
FIELDS = "number headRefName closingIssuesReferences(first: 1) { nodes { number author { login __typename } } }"
BATCH = 50


def numbers():
    with open(os.path.join(ROOT, "dataset", "commits.tsv")) as handle:
        return sorted({int(row["pr_number"]) for row in csv.DictReader(handle, delimiter="\t") if row["pr_number"]})


def automation(who):
    return not who or who["__typename"] != "User" or who["login"].lower().endswith(("bot", "[bot]"))


def load_raw():
    rows = {}
    for name in os.listdir(RAW):
        if name.endswith(".json"):
            for pr in json.load(open(os.path.join(RAW, name))):
                rows[pr["number"]] = pr
    return rows


def fetch_batch(batch):
    parts = " ".join(f"p{n}: pullRequest(number: {n}) {{ {FIELDS} }}" for n in batch)
    query = f'{{ repository(owner: "openclaw", name: "openclaw") {{ {parts} }} }}'
    found = [pr for pr in gh.graphql(query, tolerate_errors=True)["data"]["repository"].values() if pr]
    path = os.path.join(RAW, f"{batch[0]}-{batch[-1]}.json")
    with open(path + ".part", "w") as handle:
        json.dump(found, handle)
    os.replace(path + ".part", path)
    return len(found)


def main():
    os.makedirs(RAW, exist_ok=True)
    wanted = numbers()
    have = load_raw()
    missing = [number for number in wanted if number not in have]
    batches = [missing[i:i + BATCH] for i in range(0, len(missing), BATCH)]
    with ThreadPoolExecutor(3) as pool:
        for done, count in enumerate(pool.map(fetch_batch, batches), 1):
            if done % 100 == 0:
                print(f"  {done} of {len(batches)} queries", flush=True)
    keep = set(wanted)
    rows = sorted((pr for pr in load_raw().values() if pr["number"] in keep), key=lambda pr: pr["number"])
    with open(OUT, "w") as handle:
        handle.write("number\thead_branch\tcloses_issue\tissue_author\tissue_author_kind\n")
        for pr in rows:
            issue = (pr["closingIssuesReferences"]["nodes"] or [None])[0]
            handle.write("\t".join([
                str(pr["number"]), pr["headRefName"] or "",
                str(issue["number"]) if issue else "",
                (issue["author"] or {}).get("login", "") if issue else "",
                ("automation" if automation(issue["author"]) else "person") if issue else "",
            ]) + "\n")
    print(len(rows), "pull requests of", len(wanted), "wanted")


if __name__ == "__main__":
    try:
        main()
    except Paused as pause:
        stop_paused(pause)
