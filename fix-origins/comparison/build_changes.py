#!/usr/bin/env python3
"""Build dataset/changes.jsonl: one row per fetched pull request, ordinary or bug-causing, with the facts the
"does X cause more bugs" questions need.

Reads comparison/raw/<number>.json (from fetch.py), comparison/proof.json (from fetch_proof.py), comparison/areas.json
(from paths.py), dataset/commits.tsv and dataset/sampled_fixes.jsonl.
Everything here is mechanical: dates, sizes, who opened and merged, and the review bot's verdict in force when the
pull request merged (the last version of its review written at or before the merge time).

Usage: python3 fix-origins/comparison/build_changes.py [--count 400]
"""
import argparse
import collections
import csv
import hashlib
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def stamp(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def minutes(later, earlier):
    return round((stamp(later) - stamp(earlier)).total_seconds() / 60, 1)


def automation(login, kind):
    return kind == "Bot" or (login or "").lower().endswith(("bot", "[bot]"))


def who(login, kind, mergers):
    """maintainer, outside contributor or automation.

    GitHub's own label for an author (member, collaborator, contributor) depends on whether their organization
    membership is public, and it marks the project's lead as a plain contributor. So a maintainer here is simply a
    person who merged at least one of the fetched pull requests: someone who can merge.
    """
    if automation(login, kind):
        return "automation"
    return "maintainer" if login in mergers else "outside contributor"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=400)
    args = parser.parse_args()
    commits = []
    with open(os.path.join(ROOT, "dataset", "commits.tsv")) as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["pr_number"]:
                commits.append(row)
    by_number = {}
    for row in commits:
        by_number.setdefault(int(row["pr_number"]), row)
    ordered = sorted(commits, key=lambda row: hashlib.sha256(("comparison-v1:" + row["sha"]).encode()).hexdigest())
    sample = {row["sha"] for row in ordered[:args.count]}
    bugs = collections.Counter()
    origins = collections.defaultdict(list)
    with open(os.path.join(ROOT, "dataset", "sampled_fixes.jsonl")) as handle:
        for line in handle:
            fix = json.loads(line)
            if fix.get("cause_sha"):
                bugs[fix["cause_sha"]] += 1
                origins[fix["cause_sha"]].append(fix["origin"])
    proof = json.load(open(os.path.join(HERE, "proof.json")))
    areas = json.load(open(os.path.join(HERE, "areas.json")))
    rows = []
    raw = os.path.join(HERE, "raw")
    fetched = [json.load(open(os.path.join(raw, name))) for name in sorted(os.listdir(raw), key=lambda n: int(n[:-5]))]
    mergers = {pr["merged_by"] for pr in fetched if pr["merged_by"] and not automation(pr["merged_by"], pr["merged_by_type"])}
    for pr in fetched:
        commit = by_number.get(pr["number"])
        if not commit or not pr["merged_at"]:
            continue
        before = [v for v in pr["bot_review_versions"] if v["at"] <= pr["merged_at"]]
        row = {
            "sha": commit["sha"], "pr_number": pr["number"], "committed_at": commit["committed_at"],
            "files_changed": int(commit["files_changed"]), "title_prefix": commit["title_prefix"],
            "in_comparison_sample": commit["sha"] in sample,
            "sampled_bugs": bugs[commit["sha"]], "bug_kinds": origins[commit["sha"]],
            "author": pr["author"], "author_group": who(pr["author"], pr["author_type"], mergers),
            "author_association": pr["author_association"], "from_fork": pr["from_fork"],
            "merged_by": pr["merged_by"],
            "merged_by_group": "automation" if automation(pr["merged_by"], pr["merged_by_type"]) else "maintainer",
            "self_merged": bool(pr["author"]) and pr["author"] == pr["merged_by"],
            "minutes_open": minutes(pr["merged_at"], pr["created_at"]),
            "human_review_before_merge": any(r["at"] and r["at"] <= pr["merged_at"] for r in pr["human_reviews"]),
            "screenshots": proof[str(pr["number"])]["images"], "videos": proof[str(pr["number"])]["videos"],
            "visual_proof": proof[str(pr["number"])]["images"] + proof[str(pr["number"])]["videos"] > 0,
            "interface_files": areas.get(commit["sha"], {}).get("ui", 0) + areas.get(commit["sha"], {}).get("apps", 0),
            "bot_review_versions_before_merge": len(before),
        }
        if before:
            last = before[-1]
            head = last["reviewed_head"] or ""
            same = bool(head) and (pr["final_head"].startswith(head[:7]) or head.startswith(pr["final_head"][:7]))
            row.update({
                "bot_review": "reviewed the merged revision" if same else "reviewed an earlier revision",
                "bot_verdict_at_merge": last["verdict"],
                "minutes_bot_review_to_merge": minutes(pr["merged_at"], last["at"]),
            })
        else:
            row.update({"bot_review": "no review before merge", "bot_verdict_at_merge": None,
                        "minutes_bot_review_to_merge": None})
        rows.append(row)
    with open(os.path.join(ROOT, "dataset", "changes.jsonl"), "w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print(len(rows), "changes;", sum(r["in_comparison_sample"] for r in rows), "in the comparison sample;",
          sum(r["sampled_bugs"] > 0 for r in rows), "bug-causing, carrying", sum(r["sampled_bugs"] for r in rows), "sampled bugs")


if __name__ == "__main__":
    main()
