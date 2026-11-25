#!/usr/bin/env python3
"""Join the mechanical review table with the readers' verdicts into clawsweeper/results.jsonl.

Usage (from anywhere): python3 fix-origins/clawsweeper/assemble_results.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    reads = {}
    for name in os.listdir(os.path.join(HERE, "reads")):
        data = json.load(open(os.path.join(HERE, "reads", name)))
        reads[data["rank"]] = data
    with open(os.path.join(HERE, "table.jsonl")) as source, open(os.path.join(HERE, "results.jsonl"), "w") as out:
        for line in source:
            row = json.loads(line)
            read = reads.get(row["rank"])
            row.update({key: (read[key] if read else None) for key in ("flagged", "where", "quote", "outcome", "note")})
            out.write(json.dumps(row) + "\n")
    print(f"{len(reads)} verdicts joined")


if __name__ == "__main__":
    main()
