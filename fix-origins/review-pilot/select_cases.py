#!/usr/bin/env python3
"""Choose the pilot cases by a fixed rule and write data/pilot_ranks.json.

Rule: bugs whose causing change the review bot reviewed, made on or after 2026-09-10, of at most 30 files, with a
medium- or high-confidence cause and a user-visible failure. Take the first 15 broken-later ("regression") and the
first 15 never-worked cases in the sample's random order (rank order).

Three otherwise eligible cases were skipped in the original run because their causing commit could not be read in
the local partial clone (`git show` needed objects that were not stored). Pass them with --skip to reproduce the
published list; with a full clone, omit --skip and the list will differ by those cases.

Usage: python3 fix-origins/review-pilot/select_cases.py --skip 53,113,176
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip", default="")
    parser.add_argument("--per-kind", type=int, default=15)
    args = parser.parse_args()
    skip = {int(x) for x in args.skip.split(",") if x}
    cases = {c["rank"]: c for c in (json.loads(line) for line in open(os.path.join(ROOT, "cases.jsonl")))}
    reviews = {r["rank"]: r for r in (json.loads(line) for line in open(os.path.join(ROOT, "clawsweeper", "results.jsonl")))}
    picked = {"regression": [], "never-worked": []}
    for rank in sorted(reviews):
        review, case = reviews[rank], cases[rank]
        if not review["status"].startswith("reviewed") or (review["cause_date"] or "") < "2026-09-10":
            continue
        if case["confidence"] not in ("high", "medium") or case["user_visible"] != "yes":
            continue
        if case["cause"]["files_changed"] > 30 or rank in skip:
            continue
        if len(picked[case["origin"]]) < args.per_kind:
            picked[case["origin"]].append(rank)
    ranks = sorted(picked["regression"] + picked["never-worked"])
    with open(os.path.join(HERE, "data", "pilot_ranks.json"), "w") as handle:
        json.dump(ranks, handle)
    print(len(ranks), ranks)


if __name__ == "__main__":
    main()
