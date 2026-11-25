#!/usr/bin/env python3
"""Choose the control cases for the checkers: data/pilot_control_ranks.json.

A control case is a pilot case in which one of the reviewers whose reports get checked (`pilot.verify_arms` in
study.json) named the known bug exactly. On the fixed code that report should no longer hold, so re-checking these
cases on the fixed code shows how far the checkers can be trusted.

Usage: python3 fix-origins/review-pilot/control_cases.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from pipeline.settings import settings  # noqa: E402


def main():
    arms = settings()["pilot"]["verify_arms"]
    grid = json.load(open(os.path.join(HERE, "data", "grade", "grid.json")))
    ranks = sorted({int(key.split("|")[1]) for key, verdict in grid.items()
                    if key.split("|")[0] in arms and verdict["flagged"] == "exact"})
    with open(os.path.join(HERE, "data", "pilot_control_ranks.json"), "w") as handle:
        json.dump(ranks, handle)
    print(len(ranks), "control cases", ranks)


if __name__ == "__main__":
    main()
