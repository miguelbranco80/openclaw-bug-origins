#!/usr/bin/env python3
"""Join the three checks on the pooled findings and print the tallies.

Usage (from the repo root): python3 research/fix-origins/review-pilot/verify_tabulate.py <verify-dir> <grid.json>
Writes research/fix-origins/review-pilot/verify-results.jsonl (one row per finding).
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_json_text(text):
    text = text.strip()
    for candidate in (text, text[text.find("{"):text.rfind("}") + 1]):
        try:
            return json.loads(candidate)
        except ValueError:
            continue
    blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    for block in reversed(blocks):
        try:
            return json.loads(block)
        except ValueError:
            continue
    return None


def main():
    verify, grid_path = sys.argv[1:3]
    key = json.load(open(os.path.join(verify, "key.json")))
    grid = json.load(open(grid_path))
    findings = {}
    with open(os.path.join(HERE, "findings.jsonl")) as handle:
        for line in handle:
            row = json.loads(line)
            findings[(row["arm"], row["rank"])] = row["findings"]
    rows = []
    missing = collections.Counter()
    for rank_text, ids in sorted(key.items(), key=lambda item: int(item[0])):
        rank = int(rank_text)
        name = f"{rank:04d}"
        opus = later = gpt = None
        path = os.path.join(verify, "refute-opus", name + ".json")
        if os.path.exists(path):
            opus = load_json_text(open(path).read())
        path = os.path.join(verify, "laterfix-reads", name + ".json")
        if os.path.exists(path):
            later = load_json_text(open(path).read())
        path = os.path.join(verify, "refute-gpt", name, "last.txt")
        if os.path.exists(path):
            gpt = load_json_text(open(path, errors="replace").read())
        for fid, source in ids.items():
            arm, index = source["arm"], source["index"]
            cell = grid[f"{arm}|{rank}"]
            known = cell["flagged"] if cell.get("finding") == index else "none"
            finding = findings[(arm, rank)][index - 1]
            row = {"rank": rank, "id": fid, "arm": arm, "index": index, "known_bug": known,
                   "title": finding.get("title"), "file": finding.get("file"),
                   "self_confidence": finding.get("confidence")}
            for label, data, field in (("opus", opus, "verdict"), ("gpt", gpt, "verdict"), ("later", later, "fixed")):
                entry = ((data or {}).get("findings") or {}).get(fid)
                if entry is None:
                    missing[label] += 1
                    row[label] = None
                    continue
                row[label] = entry.get(field)
                if label == "later":
                    row["later_commit"] = entry.get("commit")
                    row["later_note"] = entry.get("note")
                else:
                    row[label + "_impact"] = entry.get("impact")
                    row[label + "_evidence"] = entry.get("evidence")
                    row[label + "_same_as"] = entry.get("same_as")
            rows.append(row)
    with open(os.path.join(HERE, "verify-results.jsonl"), "w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    count = collections.Counter
    print("findings", len(rows), "missing", dict(missing))
    for label in ("opus", "gpt", "later"):
        print(label, dict(count(row[label] for row in rows)))
    print("opus x gpt", dict(count((row["opus"], row["gpt"]) for row in rows)))
    known = [row for row in rows if row["known_bug"] == "exact"]
    print("known-real controls", len(known), "opus", dict(count(r["opus"] for r in known)),
          "gpt", dict(count(r["gpt"] for r in known)), "later", dict(count(r["later"] for r in known)))
    rest = [row for row in rows if row["known_bug"] != "exact"]
    print("other findings", len(rest), "later", dict(count(r["later"] for r in rest)))
    for arm in sorted({row["arm"] for row in rows}):
        mine = [row for row in rows if row["arm"] == arm]
        cross = "gpt" if arm.startswith("claude") else "opus"
        print(arm, len(mine), "| cross-vendor verdict", dict(count(r[cross] for r in mine)),
              "| own-vendor", dict(count(r["opus" if cross == "gpt" else "gpt"] for r in mine)),
              "| later", dict(count(r["later"] for r in mine)),
              "| cross impact", dict(count(r[cross + "_impact"] for r in mine if r[cross] == "confirmed")))
    both = [r for r in rows if r["opus"] == "confirmed" and r["gpt"] == "confirmed"]
    print("confirmed by both", len(both), "impact both user-visible",
          sum(r["opus_impact"] == "user-visible" and r["gpt_impact"] == "user-visible" for r in both))
    print("later yes by checker verdicts", dict(count((r["opus"], r["gpt"]) for r in rows if r["later"] == "yes")))
    print("refuted by either", sum(r["opus"] == "refuted" or r["gpt"] == "refuted" for r in rows),
          "of which later yes", sum((r["opus"] == "refuted" or r["gpt"] == "refuted") and r["later"] == "yes" for r in rows))
    dup = sum(bool(r.get("opus_same_as")) for r in rows)
    print("marked duplicate of another finding (opus)", dup, "distinct", len(rows) - dup)


if __name__ == "__main__":
    main()
