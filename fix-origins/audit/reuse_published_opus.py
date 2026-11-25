#!/usr/bin/env python3
"""Keep the published Claude Opus 5.5 answers for the November fixes as the second-maker check.

The study as published (tag `published-2026-11`) had Opus read all 300 November fixes and a GPT model re-read a
slice. From 25 November 2026 the roles are swapped: a GPT model reads every fix of every period, and the Opus
answers already made become the check. This script moves those answers into the folders the "re-read" steps use,
so nothing has to be read twice.

  python3 fix-origins/audit/reuse_published_opus.py origins
      Before the new main reading: each Opus answer in fix-origins/reads/<rank>.json becomes
      audit/raw/origin/<rank>/last.txt, and what Opus said about each bot review is saved, with the causing pull
      request it was about, in audit/published-opus-flags.jsonl.
  python3 fix-origins/audit/reuse_published_opus.py flags
      After the new bot-review bundles exist: where the new main reader named the same causing pull request as
      Opus had, the Opus verdict on the bot's review still applies and becomes audit/raw/flag/<rank>/last.txt.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.dirname(HERE)
SAVED = os.path.join(HERE, "published-opus-flags.jsonl")


def origins():
    target = os.path.join(HERE, "raw", "origin")
    shutil.rmtree(target, ignore_errors=True)
    moved = 0
    for name in os.listdir(os.path.join(FIX, "reads")):
        answer = json.load(open(os.path.join(FIX, "reads", name)))
        folder = os.path.join(target, f"{int(answer['rank']):04d}")
        os.makedirs(folder)
        with open(os.path.join(folder, "last.txt"), "w") as handle:
            handle.write(json.dumps(answer, indent=2) + "\n")
        moved += 1
    with open(os.path.join(FIX, "clawsweeper", "results.jsonl")) as source, open(SAVED, "w") as out:
        kept = 0
        for line in source:
            row = json.loads(line)
            if row.get("flagged"):
                out.write(json.dumps({key: row.get(key) for key in ("rank", "cause_pr", "flagged", "where", "quote",
                                                                    "outcome", "note")}) + "\n")
                kept += 1
    print(f"Opus answers kept as the check: {moved} fixes, {kept} bot reviews")


def flags():
    target = os.path.join(HERE, "raw", "flag")
    shutil.rmtree(target, ignore_errors=True)
    now = {}
    with open(os.path.join(FIX, "clawsweeper", "table.jsonl")) as handle:
        for line in handle:
            row = json.loads(line)
            now[row["rank"]] = row.get("cause_pr")
    reused = 0
    for line in open(SAVED):
        row = json.loads(line)
        bundle = os.path.join(FIX, "clawsweeper", "bundles", f"{row['rank']:04d}.md")
        if now.get(row["rank"]) != row["cause_pr"] or not os.path.exists(bundle):
            continue
        folder = os.path.join(target, f"{row['rank']:04d}")
        os.makedirs(folder)
        with open(os.path.join(folder, "last.txt"), "w") as handle:
            handle.write(json.dumps({key: row[key] for key in ("flagged", "where", "quote", "outcome", "note")}, indent=2) + "\n")
        reused += 1
    print(f"Opus verdicts on bot reviews that still apply (same causing pull request): {reused} of {sum(1 for _ in open(SAVED))}")


if __name__ == "__main__":
    {"origins": origins, "flags": flags}[sys.argv[1]]()
