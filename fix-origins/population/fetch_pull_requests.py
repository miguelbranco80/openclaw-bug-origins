#!/usr/bin/env python3
"""Fetch who opened, merged and reviewed every pull request in dataset/commits.tsv: dataset/pull_requests.tsv.

One row per pull request number that appears in commits.tsv. Read-only GitHub GraphQL through `gh`, 100 pull
requests per query, three queries at a time; each answer is kept under population/raw/ so a rerun fetches only the
pull requests it does not have yet.

Columns:
  number, author, merged_by, created_at, merged_at
  author_kind              person or automation
  reviewers_before_merge   people, other than the author and not automation, who submitted a review before the merge,
                           comma separated

Usage: python3 fix-origins/population/fetch_pull_requests.py
"""
import csv
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pipeline import gh  # noqa: E402
from pipeline.settings import Paused, settings, stop_paused  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(ROOT, "dataset", "pull_requests.tsv")
FIELDS = """number createdAt mergedAt author { login __typename } mergedBy { login __typename }
      reviews(first: 8) { totalCount nodes { author { login __typename } submittedAt } }"""
BATCH = 100


def numbers():
    with open(os.path.join(ROOT, "dataset", "commits.tsv")) as handle:
        return sorted({int(row["pr_number"]) for row in csv.DictReader(handle, delimiter="\t") if row["pr_number"]})


def automation(who):
    return not who or who["__typename"] != "User" or who["login"].lower().endswith(("bot", "[bot]"))


def fetch(batch, more=False):
    fields = FIELDS.replace("first: 8", "first: 100") if more else FIELDS
    parts = " ".join(f"p{n}: pullRequest(number: {n}) {{ {fields} }}" for n in batch)
    query = f'{{ repository(owner: "openclaw", name: "openclaw") {{ {parts} }} }}'
    data = gh.graphql(query, tolerate_errors=True)["data"]["repository"]
    return [pr for pr in data.values() if pr]


def load_raw():
    rows = {}
    for name in os.listdir(RAW):
        if name.endswith(".json"):
            for pr in json.load(open(os.path.join(RAW, name))):
                rows[pr["number"]] = pr
    return rows


def fetch_batch(batch):
    found = fetch(batch)
    cut = [pr["number"] for pr in found if pr["reviews"]["totalCount"] > len(pr["reviews"]["nodes"])]
    if cut:
        full = {pr["number"]: pr for group in (cut[i:i + 10] for i in range(0, len(cut), 10)) for pr in fetch(group, more=True)}
        found = [full.get(pr["number"], pr) for pr in found]
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
    # Two numbers in the published list are not pull requests; asking again for a few misses is harmless.
    batches = [missing[i:i + BATCH] for i in range(0, len(missing), BATCH)]
    with ThreadPoolExecutor(3) as pool:
        for count in pool.map(fetch_batch, batches):
            pass
    keep = set(wanted)
    rows = sorted((pr for pr in load_raw().values() if pr["number"] in keep), key=lambda pr: pr["number"])
    with open(OUT, "w") as handle:
        handle.write("number\tauthor\tauthor_kind\tmerged_by\tcreated_at\tmerged_at\treviewers_before_merge\n")
        for pr in rows:
            author = (pr["author"] or {}).get("login", "")
            reviewers = sorted({r["author"]["login"] for r in pr["reviews"]["nodes"]
                                if not automation(r["author"]) and r["author"]["login"] != author
                                and r["submittedAt"] and pr["mergedAt"] and r["submittedAt"] <= pr["mergedAt"]})
            handle.write("\t".join([str(pr["number"]), author, "automation" if automation(pr["author"]) else "person",
                                    (pr["mergedBy"] or {}).get("login", ""),
                                    pr["createdAt"], pr["mergedAt"] or "", ",".join(reviewers)]) + "\n")
    print(len(rows), "pull requests of", len(wanted), "wanted")


if __name__ == "__main__":
    try:
        main()
    except Paused as pause:
        stop_paused(pause)
