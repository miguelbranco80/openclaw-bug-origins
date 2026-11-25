#!/usr/bin/env python3
"""Fetch who opened, merged and reviewed every pull request in dataset/commits.tsv: dataset/pull_requests.tsv.

One row per pull request number that appears in commits.tsv. Read-only GitHub GraphQL through `gh`, 100 pull
requests per query; each answer is kept under population/raw/ so a rerun only fetches what is missing.

Columns:
  number, author, merged_by, created_at, merged_at
  author_kind              person or automation
  reviewers_before_merge   people, other than the author and not automation, who submitted a review before the merge,
                           comma separated

Usage: python3 fix-origins/population/fetch_pull_requests.py [--shard i/n]
"""
import argparse
import csv
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
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
    for attempt in range(5):
        run = subprocess.run(["gh", "api", "graphql", "-f", "query=" + query], capture_output=True, text=True)
        try:
            data = json.loads(run.stdout)["data"]["repository"]
            return [pr for pr in data.values() if pr]
        except (ValueError, KeyError, TypeError):
            time.sleep(10 * (attempt + 1))
    raise SystemExit("gave up on batch starting " + str(batch[0]) + ": " + run.stdout[:300] + run.stderr[:300])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", default="0/1")
    index, shards = map(int, parser.parse_args().shard.split("/"))
    wanted = numbers()
    batches = [wanted[i:i + BATCH] for i in range(0, len(wanted), BATCH)]
    for position, batch in enumerate(batches):
        path = os.path.join(RAW, f"{batch[0]}.json")
        if position % shards != index or os.path.exists(path):
            continue
        found = fetch(batch)
        cut = [pr["number"] for pr in found if pr["reviews"]["totalCount"] > len(pr["reviews"]["nodes"])]
        if cut:
            full = {pr["number"]: pr for group in (cut[i:i + 10] for i in range(0, len(cut), 10)) for pr in fetch(group, more=True)}
            found = [full.get(pr["number"], pr) for pr in found]
        with open(path + ".part", "w") as handle:
            json.dump(found, handle)
        os.replace(path + ".part", path)
    if shards > 1:
        return
    rows = []
    for name in os.listdir(RAW):
        if name.endswith(".json"):
            rows.extend(json.load(open(os.path.join(RAW, name))))
    rows.sort(key=lambda pr: pr["number"])
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
    main()
