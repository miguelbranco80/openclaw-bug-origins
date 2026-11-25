"""Shared helpers for the question scripts: loading the dataset, small statistics, saving results.

Every question script reads only files under dataset/ and writes results/<id>.json (one row per number, with a
group, a unique metric name, a plain label and a value) plus its charts under charts/.
"""
import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(ROOT, "dataset")
RESULTS = os.path.join(ROOT, "results")
POPULATION = 3996  # changes titled "fix" that touch product code, merged 1 to 22 November 2026
SAMPLE = 300
SCALE = POPULATION / SAMPLE


def load(name):
    """Rows of a dataset file: .jsonl gives dicts, .json gives its content."""
    path = os.path.join(DATASET, name)
    if name.endswith(".jsonl"):
        with open(path) as handle:
            return [json.loads(line) for line in handle]
    with open(path) as handle:
        return json.load(handle)


def load_commits():
    """Every commit on main since 2026-09-10 (UTC), keyed by sha."""
    commits = {}
    with open(os.path.join(DATASET, "commits.tsv")) as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            row["files_changed"] = int(row["files_changed"])
            commits[row["sha"]] = row
    return commits


def traced(fixes):
    """Sampled fixes that a reader traced to the change that introduced the bug."""
    return [fix for fix in fixes if fix.get("cause_sha")]


def wilson(k, n, z=1.96):
    """95% interval for a proportion k of n, as whole percentages."""
    if n == 0:
        return 0, 0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5
    return round(100 * (c - h) / d), round(100 * (c + h) / d)


def sign_test(first_only, second_only):
    """Chance of a split at least this uneven if both sides were equally good (exact, two-sided)."""
    n = first_only + second_only
    if n == 0:
        return 1.0
    k = min(first_only, second_only)
    return round(min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n), 3)


def pct(k, n):
    return round(100 * k / n) if n else 0


def ratio_interval(a, n1, b, n2, z=1.96):
    """Ratio of two rates a/n1 over b/n2 with a 95% interval (log method). None when a count is zero."""
    if min(a, b) == 0:
        return None
    ratio = (a / n1) / (b / n2)
    spread = math.sqrt(1 / a - 1 / n1 + 1 / b - 1 / n2)
    return round(ratio, 2), round(ratio * math.exp(-z * spread), 2), round(ratio * math.exp(z * spread), 2)


class Result:
    """Collects the rows of one question and saves them."""

    def __init__(self, question):
        self.question = question
        self.rows = []
        self.charts = []

    def chart(self, drawn):
        """Record a chart drawn by questions/charts.py so the report can place it."""
        self.charts.append(drawn)

    def add(self, group, metric, label, value, low=None, high=None):
        assert all(row["metric"] != metric for row in self.rows), metric
        if isinstance(value, float) and value == int(value) and abs(value) >= 10:
            value = int(value)
        self.rows.append({"group": group, "metric": metric, "label": label, "value": value, "low": low, "high": high})

    def group(self, name):
        return [row for row in self.rows if row["group"] == name]

    def value(self, metric):
        return next(row["value"] for row in self.rows if row["metric"] == metric)

    def save(self, quiet=False):
        os.makedirs(RESULTS, exist_ok=True)
        with open(os.path.join(RESULTS, self.question + ".json"), "w") as handle:
            handle.write("[\n" + ",\n".join(json.dumps(row) for row in self.rows) + "\n]\n")
        with open(os.path.join(RESULTS, self.question + ".charts.json"), "w") as handle:
            json.dump(self.charts, handle, indent=1)
        if not quiet:
            for row in self.rows:
                spread = f"  ({row['low']} to {row['high']})" if row["low"] is not None else ""
                print(f"{row['label']}: {row['value']}{spread}")
