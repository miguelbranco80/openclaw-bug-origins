#!/usr/bin/env python3
"""Write the five data files used by the interactive version of the report (fix-origins/dashboard/index.html).

They are the question scripts' results regrouped; nothing is computed here.

Usage: python3 report/export_dashboard.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {
    "fix-origins-sample.json": ["q01", "q02", "q03", "q05"],
    "clawsweeper-reviews.json": ["q06"],
    "blind-review-pilot.json": ["q07", "q09"],
    "finding-checks.json": ["q08"],
    "named-cause-study.json": ["q10"],
}


def main():
    for name, questions in FILES.items():
        rows = []
        for question in questions:
            rows += json.load(open(os.path.join(ROOT, "results", question + ".json")))
        assert len({row["metric"] for row in rows}) == len(rows), name
        with open(os.path.join(ROOT, "fix-origins", "dashboard", name), "w") as handle:
            handle.write("[\n" + ",\n".join(json.dumps(row) for row in rows) + "\n]\n")
    print("dashboard data exported")


if __name__ == "__main__":
    main()
