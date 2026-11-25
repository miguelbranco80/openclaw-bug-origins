#!/usr/bin/env python3
"""Choose the pilot cases by a fixed rule and write data/pilot_ranks.json.

Rule: bugs whose causing change the review bot reviewed, made on or after `commits_since` in study.json, of at most
30 files, with a medium- or high-confidence cause and a user-visible failure. Take the first `pilot.per_kind`
broken-later ("regression") and the same number of never-worked cases in the sample's random order (rank order).

Three otherwise eligible cases were skipped in the original run because their causing commit could not be read in
the local partial clone (`git show` needed objects that were not stored). They are listed under `pilot.skip` in
study.json, which reproduces the published list; a new study starts with that list empty.

Usage: python3 fix-origins/review-pilot/select_cases.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
import sys
sys.path.insert(0, os.path.dirname(ROOT))
from pipeline.settings import settings  # noqa: E402


def main():
    pinned = os.path.join(HERE, "data", "pilot_cases.jsonl")
    if os.path.exists(pinned):
        print(f"blind review cases are already chosen and pinned: {sum(1 for _ in open(pinned))} "
              "(delete review-pilot/data/ to choose again)")
        return
    pilot = settings()["pilot"]
    skip, per_kind, since = set(pilot.get("skip", [])), pilot["per_kind"], settings()["commits_since"][:10]
    cases = {c["rank"]: c for c in (json.loads(line) for line in open(os.path.join(ROOT, "cases.jsonl")))}
    reviews = {r["rank"]: r for r in (json.loads(line) for line in open(os.path.join(ROOT, "clawsweeper", "results.jsonl")))}
    picked = {"regression": [], "never-worked": []}
    for rank in sorted(reviews):
        review, case = reviews[rank], cases[rank]
        if not review["status"].startswith("reviewed") or (review["cause_date"] or "") < since:
            continue
        if case["confidence"] not in ("high", "medium") or case["user_visible"] != "yes":
            continue
        if case["cause"]["files_changed"] > 30 or rank in skip:
            continue
        if len(picked[case["origin"]]) < per_kind:
            picked[case["origin"]].append(rank)
    ranks = sorted(picked["regression"] + picked["never-worked"])
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    with open(os.path.join(HERE, "data", "pilot_ranks.json"), "w") as handle:
        json.dump(ranks, handle)
    # Pin the facts the experiment uses, so that later changes to the main reading cannot alter it.
    with open(pinned, "w") as handle:
        for rank in ranks:
            handle.write(json.dumps(cases[rank]) + "\n")
    with open(os.path.join(HERE, "data", "pilot_bot.jsonl"), "w") as handle:
        for rank in ranks:
            handle.write(json.dumps(reviews[rank]) + "\n")
    print(f"blind review cases chosen and pinned: {len(ranks)} (ranks {ranks})")


if __name__ == "__main__":
    main()
