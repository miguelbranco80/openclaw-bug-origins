#!/usr/bin/env python3
"""Tabulate the checkers' control: verdicts on the same findings against the code after the known bug was fixed.

Reads verify-results.jsonl (verdicts on the original code) and the checkers' answers on the fixed code under
data/verify/refute-gpt-fixed-cases/ and data/verify/refute-opus-fixed-cases/. Writes verify-control.jsonl.

Usage: python3 fix-origins/review-pilot/verify_control.py
"""
import json
import os

from verify_tabulate import load_json_text

HERE = os.path.dirname(os.path.abspath(__file__))
VERIFY = os.path.join(HERE, "data", "verify")


def answers(kind, rank):
    if kind == "gpt":
        path = os.path.join(VERIFY, "refute-gpt-fixed-cases", f"{rank:04d}", "last.txt")
    else:
        path = os.path.join(VERIFY, "refute-opus-fixed-cases", f"{rank:04d}.json")
    if not os.path.exists(path):
        return None
    return (load_json_text(open(path, errors="replace").read()) or {}).get("findings")


def main():
    control = json.load(open(os.path.join(HERE, "data", "pilot_control_ranks.json")))
    rows = [json.loads(line) for line in open(os.path.join(HERE, "verify-results.jsonl"))]
    out = []
    for row in rows:
        if row["rank"] not in control:
            continue
        item = {"rank": row["rank"], "id": row["id"], "known_bug": row["known_bug"], "later": row["later"]}
        for kind in ("gpt", "opus"):
            entry = (answers(kind, row["rank"]) or {}).get(row["id"]) or {}
            item[kind + "_at_cause"] = row[kind]
            item[kind + "_at_fix"] = entry.get("verdict")
            item[kind + "_at_fix_evidence"] = entry.get("evidence")
        out.append(item)
    with open(os.path.join(HERE, "verify-control.jsonl"), "w") as handle:
        for item in out:
            handle.write(json.dumps(item) + "\n")
    print(len(out), "findings in the control")


if __name__ == "__main__":
    main()
