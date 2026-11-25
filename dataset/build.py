#!/usr/bin/env python3
"""Assemble the dataset: the facts every question script reads, gathered from the collection folders.

This only copies and renames. All judgment happened earlier, in the collection steps under fix-origins/ and
detection-check/. dataset/README.md says what each file and column means.

Not rebuilt here: commits.tsv (made from a clone by fix-origins/scripts/commit_list.py), named_cause_study.json
(figures of the first study, entered from detection-check/report.md) and changes.jsonl (made by
fix-origins/comparison/build_changes.py from fetched pull request data).

Usage: python3 dataset/build.py
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCE = os.path.join(ROOT, "fix-origins")
COPIES = {
    "sampled_fixes.jsonl": "cases.jsonl",
    "fix_rereads_gpt.jsonl": "audit/origin-second-reads.jsonl",
    "bot_reviews.jsonl": "clawsweeper/results.jsonl",
    "bot_review_rereads_gpt.jsonl": "audit/flag-second-reads.jsonl",
    "blind_review.jsonl": "review-pilot/results.jsonl",
    "blind_review_regrades_gpt.jsonl": "audit/grade-second-reads.jsonl",
    "reported_problems.jsonl": "review-pilot/verify-results.jsonl",
    "checker_control.jsonl": "review-pilot/verify-control.jsonl",
}


def main():
    for target, source in COPIES.items():
        shutil.copyfile(os.path.join(SOURCE, source), os.path.join(HERE, target))
    fixes = fixes_in = {}
    with open(os.path.join(SOURCE, "cases.jsonl")) as handle:
        for line in handle:
            fix = json.loads(line)
            fixes[fix["sha"]] = fix
    with open(os.path.join(SOURCE, "second_reads.jsonl")) as source, \
            open(os.path.join(HERE, "fix_rereads_claude.jsonl"), "w") as out:
        for line in source:
            second = json.loads(line)
            first = fixes[second["sha"]]
            out.write(json.dumps({
                "rank": first["rank"], "first_origin": first["origin"], "first_cause": first.get("cause_sha"),
                "second_origin": second["origin"], "second_cause": second.get("cause_sha"),
                "second_reasoning": second.get("reasoning"),
            }) + "\n")
    sys.path.insert(0, ROOT)
    from pipeline.settings import frame_offset, population, settings
    fixes, frames = population(), []
    for frame in settings()["frames"]:
        ranks = [rank for rank in fixes if frame_offset(frame) < rank <= frame_offset(frame) + 100000 - 1]
        frames.append({"frame": frame["id"], "since": frame["since"], "until": frame.get("until"),
                       "population": len(ranks),
                       "sampled": sum(1 for sha in fixes_in if (fixes_in[sha]["rank"] - 1) // 100000 + 1 == frame["id"])})
    with open(os.path.join(HERE, "frames.json"), "w") as handle:
        json.dump(frames, handle, indent=1)
    print("dataset assembled:", ", ".join(sorted(name for name in os.listdir(HERE) if "." in name and name != "build.py")))


if __name__ == "__main__":
    main()
