#!/usr/bin/env python3
"""Print the ranks in a range that get an independent second reader.

A fix gets a second read when sha256("fix-origins-second-v1:" + sha), read as a
fraction of 2**32 from its first 8 hex digits, is below 0.15. The rule depends
only on the sha, so extending the sample keeps earlier choices and adds about
15% of each new batch.

Usage (from the repo root):
    python3 research/fix-origins/scripts/second.py --from 1 --to 300
"""
import argparse
import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ap = argparse.ArgumentParser()
ap.add_argument("--from", dest="lo", type=int, required=True)
ap.add_argument("--to", dest="hi", type=int, required=True)
a = ap.parse_args()
with open(os.path.join(ROOT, "population.tsv")) as f:
    next(f)
    for line in f:
        rank, sha = line.split("\t")[:2]
        h = int(hashlib.sha256(("fix-origins-second-v1:" + sha).encode()).hexdigest()[:8], 16) / 2**32
        if a.lo <= int(rank) <= a.hi and h < 0.15:
            print(rank)
