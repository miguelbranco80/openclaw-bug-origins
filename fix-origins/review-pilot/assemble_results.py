#!/usr/bin/env python3
"""Unblind the grades and write the pilot's per-case results.

Reads data/grade/reads/<rank>.json (graders' verdicts by reviewer letter), data/grade/key.json (letter -> reviewer),
data/grade/tags/<rank>.json (what each bug needed), findings.jsonl, and the pinned case facts data/pilot_cases.jsonl and data/pilot_bot.jsonl.
Writes data/grade/grid.json and results.jsonl.

Usage: python3 fix-origins/review-pilot/assemble_results.py
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GRADE = os.path.join(HERE, "data", "grade")
sys.path.insert(0, os.path.dirname(ROOT))
from pipeline.settings import settings  # noqa: E402

ORDER = [f"{arm['model']}__{arm['mode']}" for arm in settings()["judging"]["review"]]  # the reviewers, in study.json


def main():
    key = {int(k): v for k, v in json.load(open(os.path.join(GRADE, "key.json"))).items()}
    findings = {(r["arm"], r["rank"]): r for r in (json.loads(line) for line in open(os.path.join(HERE, "findings.jsonl")))}
    cases = {c["rank"]: c for c in (json.loads(line) for line in open(os.path.join(HERE, "data", "pilot_cases.jsonl")))}
    bot = {r["rank"]: r for r in (json.loads(line) for line in open(os.path.join(HERE, "data", "pilot_bot.jsonl")))}
    grid = {}
    for path in sorted(glob.glob(os.path.join(GRADE, "reads", "*.json"))):
        data = json.load(open(path))
        rank = int(data["rank"])
        assert set(data["reviewers"]) == set(key[rank]), rank
        for letter, verdict in data["reviewers"].items():
            arm = key[rank][letter]
            if verdict["flagged"] != "none":
                assert 1 <= verdict["finding"] <= len(findings[(arm, rank)]["findings"]), (rank, letter)
            grid[(arm, rank)] = verdict
    with open(os.path.join(GRADE, "grid.json"), "w") as handle:
        json.dump({f"{arm}|{rank}": verdict for (arm, rank), verdict in grid.items()}, handle)
    tags = {}
    for path in glob.glob(os.path.join(GRADE, "tags", "*.json")):
        data = json.load(open(path))
        tags[int(data["rank"])] = data
    with open(os.path.join(HERE, "results.jsonl"), "w") as handle:
        for rank in sorted(tags):
            case = cases[rank]
            row = {"rank": rank, "origin": case["origin"], "cause_pr": case["cause_pr"], "fix_pr": case["fix_pr"],
                   "files_changed": case["cause"]["files_changed"], "days_to_fix": case["cause"]["days_to_fix"],
                   "needs": tags[rank]["needs"], "needs_where": tags[rank].get("where"),
                   "needs_note": tags[rank].get("note"), "clawsweeper_actual": bot[rank]["flagged"], "arms": {}}
            for arm in ORDER:
                verdict = grid[(arm, rank)]
                found = findings[(arm, rank)]["findings"]
                row["arms"][arm] = {"flagged": verdict["flagged"], "findings": len(found),
                                    "runs": findings[(arm, rank)]["runs"],
                                    "matching_finding": found[verdict["finding"] - 1] if verdict["finding"] else None,
                                    "grader_note": verdict["note"]}
            handle.write(json.dumps(row) + "\n")
    print(f"blind review assembled: {len(tags)} cases, {len(grid)} reviewer-and-case grades")


if __name__ == "__main__":
    main()
