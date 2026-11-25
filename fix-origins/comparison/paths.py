#!/usr/bin/env python3
"""For every fetched pull request's commit on main, count the files it changed under each top-level folder.

Run from the root of an openclaw/openclaw clone, with this repository checked out as `research/`. Writes
comparison/areas.json: sha -> {folder: files changed}. Used to tell interface changes from the rest.

Usage: python3 research/fix-origins/comparison/paths.py
"""
import collections
import csv
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    numbers = {int(name[:-5]) for name in os.listdir(os.path.join(HERE, "raw"))}
    shas = []
    seen = set()
    with open(os.path.join(ROOT, "dataset", "commits.tsv")) as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["pr_number"] and int(row["pr_number"]) in numbers and row["pr_number"] not in seen:
                seen.add(row["pr_number"])
                shas.append(row["sha"])
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    areas = {}
    for sha in shas:
        out = subprocess.run(["git", "show", "--no-renames", "--name-only", "--format=", sha],
                             capture_output=True, text=True, env=env, timeout=120)
        counts = collections.Counter(path.split("/")[0] for path in out.stdout.splitlines() if path)
        areas[sha] = dict(counts)
    with open(os.path.join(HERE, "areas.json"), "w") as handle:
        json.dump(areas, handle, sort_keys=True)
    print(len(areas), "commits")


if __name__ == "__main__":
    main()
