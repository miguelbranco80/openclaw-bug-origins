#!/usr/bin/env python3
"""Collect the GPT second reads into durable files beside the studies and print agreement with the first pass.

Usage (from the repo root): python3 research/fix-origins/audit/collect.py <audit-out-dir> <grade-key.json> <grid.json>
Writes audit/origin-second-reads.jsonl, audit/flag-second-reads.jsonl, audit/grade-second-reads.jsonl.
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def parse(path):
    if not os.path.exists(path):
        return None
    text = open(path, errors="replace").read().strip()
    candidates = [text, text[text.find("{"):text.rfind("}") + 1]]
    candidates += re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


def outside_reads(folder):
    """Paths a run touched outside its own work directory, other than the allowed bare history."""
    hits = collections.Counter()
    path = os.path.join(folder, "events.jsonl")
    if not os.path.exists(path):
        return hits
    for line in open(path, errors="replace"):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        item = event.get("item") or {}
        if item.get("type") != "command_execution" or event.get("type") != "item.completed":
            continue
        for found in re.findall(r"(/(?:Users|private|tmp)/[^\s'\";|)]+)", item.get("command", "")):
            if "/fullhist.git" in found or "/audit/" in found and "/work" in found:
                continue
            hits[found[:90]] += 1
    return hits


def main():
    out, key_path, grid_path = sys.argv[1:4]
    count = collections.Counter
    leaks = collections.Counter()

    cases = {c["rank"]: c for c in (json.loads(line) for line in open(os.path.join(ROOT, "cases.jsonl")))}
    rows = []
    folder = os.path.join(out, "origin")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        data = parse(os.path.join(folder, name, "last.txt"))
        leaks.update(outside_reads(os.path.join(folder, name)))
        if not data or "origin" not in data:
            continue
        case = cases[int(name)]
        rows.append({"rank": int(name), "first_origin": case["origin"], "first_cause": case.get("cause_sha"),
                     "first_confidence": case.get("confidence"), "second_origin": data["origin"],
                     "second_cause": data.get("cause_sha"), "second_confidence": data.get("confidence"),
                     "second_reasoning": data.get("reasoning")})
    with open(os.path.join(HERE, "origin-second-reads.jsonl"), "w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    real = {"regression", "never-worked", "latent"}
    pair = [r for r in rows if {r["first_origin"], r["second_origin"]} <= {"regression", "never-worked"}]
    same_cause = [r for r in rows if r["first_cause"] and r["second_cause"]]
    print("origin:", len(rows), "same origin", sum(r["first_origin"] == r["second_origin"] for r in rows),
          "| same on real-bug-or-not", sum((r["first_origin"] in real) == (r["second_origin"] in real) for r in rows),
          "| both regression-or-never", len(pair), "agree", sum(r["first_origin"] == r["second_origin"] for r in pair),
          "| both named a cause", len(same_cause),
          "same commit", sum(r["first_cause"][:10] == r["second_cause"][:10] for r in same_cause))
    print("  pairs:", dict(count((r["first_origin"], r["second_origin"]) for r in rows)))
    print("  second reader totals:", dict(count(r["second_origin"] for r in rows)),
          "first reader on same:", dict(count(r["first_origin"] for r in rows)))

    first = {r["rank"]: r for r in (json.loads(line) for line in open(os.path.join(ROOT, "clawsweeper", "results.jsonl")))}
    rows = []
    folder = os.path.join(out, "flag")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        data = parse(os.path.join(folder, name, "last.txt"))
        leaks.update(outside_reads(os.path.join(folder, name)))
        if not data or "flagged" not in data:
            continue
        rows.append({"rank": int(name), "first": first[int(name)]["flagged"], "second": data["flagged"],
                     "second_where": data.get("where"), "second_quote": data.get("quote"),
                     "second_note": data.get("note")})
    with open(os.path.join(HERE, "flag-second-reads.jsonl"), "w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print("flag:", len(rows), "same level", sum(r["first"] == r["second"] for r in rows),
          "| pairs", dict(count((r["first"], r["second"]) for r in rows)))

    key = {int(k): v for k, v in json.load(open(key_path)).items()}
    grid = json.load(open(grid_path))
    rows = []
    folder = os.path.join(out, "grade")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        data = parse(os.path.join(folder, name, "last.txt"))
        leaks.update(outside_reads(os.path.join(folder, name)))
        if not data or "reviewers" not in data:
            continue
        rank = int(name)
        for letter, arm in key[rank].items():
            second = (data["reviewers"].get(letter) or {}).get("flagged")
            rows.append({"rank": rank, "arm": arm, "first": grid[f"{arm}|{rank}"]["flagged"], "second": second})
    with open(os.path.join(HERE, "grade-second-reads.jsonl"), "w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print("grade:", len(rows), "cells; same level", sum(r["first"] == r["second"] for r in rows),
          "| same on named-or-not", sum((r["first"] == "exact") == (r["second"] == "exact") for r in rows))
    print("  pairs:", dict(count((r["first"], r["second"]) for r in rows)))
    for arm in sorted({r["arm"] for r in rows}):
        mine = [r for r in rows if r["arm"] == arm]
        print("  ", arm, "first", sum(r["first"] == "exact" for r in mine), "second", sum(r["second"] == "exact" for r in mine))
    print("reads outside the work folder:", dict(leaks) or "none")


if __name__ == "__main__":
    main()
