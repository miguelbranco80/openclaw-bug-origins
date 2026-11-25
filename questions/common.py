"""Shared helpers for the question scripts: loading the dataset, small statistics, saving results.

Every question script reads only files under dataset/ and writes results/<id>.json (one row per number, with a
group, a unique metric name, a plain label and a value) plus its charts under charts/.
"""
import collections
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

    def chart(self, drawn, reading):
        """Record a chart drawn by questions/charts.py, with one sentence saying what a bar is."""
        self.charts.append(dict(drawn, reading=reading))

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


# --- comparing kinds of change -------------------------------------------------------------------------------
# dataset/changes.jsonl holds a random comparison sample of ordinary pull requests and every bug-causing pull
# request found in the fix sample. For a property with a few levels (say, what the review bot said at merge), the
# comparison sample says how common each level is among all changes, and the bug-causing changes say how many
# sampled bugs came from each level. Their ratio is how much more often one kind of change causes a bug than another.

SIZE_GROUPS = (("1 to 5 files", 0, 5), ("6 to 30 files", 6, 30), ("Over 30 files", 31, 10 ** 9))


def size_group(change):
    return next(name for name, low, high in SIZE_GROUPS if low <= change["files_changed"] <= high)


def pull_request_commits():
    return sum(1 for commit in load_commits().values() if commit["pr_number"])


def odds_ratio(a, b, c, d, z=1.96):
    """(a/b) / (c/d) with a 95% interval; a, b are bug counts, c, d comparison counts. None if any count is 0."""
    if min(a, b, c, d) == 0:
        return None
    ratio = (a / b) / (c / d)
    spread = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return round(ratio, 2), round(ratio * math.exp(-z * spread), 2), round(ratio * math.exp(z * spread), 2)


def stratified_ratio(tables, z=1.96):
    """Mantel-Haenszel ratio over strata of (a, b, c, d), with the Robins-Greenland-Breslow interval."""
    tables = [t for t in tables if sum(t) > 0]
    r = sum(a * d / (a + b + c + d) for a, b, c, d in tables)
    s = sum(b * c / (a + b + c + d) for a, b, c, d in tables)
    if r == 0 or s == 0:
        return None
    pr = sum((a + d) / (a + b + c + d) * (a * d / (a + b + c + d)) for a, b, c, d in tables)
    ps_qr = sum((a + d) / (a + b + c + d) * (b * c / (a + b + c + d)) + (b + c) / (a + b + c + d) * (a * d / (a + b + c + d))
                for a, b, c, d in tables)
    qs = sum((b + c) / (a + b + c + d) * (b * c / (a + b + c + d)) for a, b, c, d in tables)
    spread = math.sqrt(pr / (2 * r * r) + ps_qr / (2 * r * s) + qs / (2 * s * s))
    ratio = r / s
    return round(ratio, 2), round(ratio * math.exp(-z * spread), 2), round(ratio * math.exp(z * spread), 2)


def compare(out, prefix, changes, level_of, levels, reference):
    """Add, for each level of a property: how common it is, how many sampled bugs it produced, the bug rate, and
    the rate relative to the reference level, crude and adjusted for the size of the change.

    levels: list of (key, label). level_of(change) returns a key or None to leave the change out.
    """
    sample = [c for c in changes if c["in_comparison_sample"] and level_of(c) is not None]
    causing = [c for c in changes if c["sampled_bugs"] and level_of(c) is not None]
    total = pull_request_commits()
    seen = collections.Counter(level_of(c) for c in sample)
    bugs = collections.Counter()
    for c in causing:
        bugs[level_of(c)] += c["sampled_bugs"]
    for key, label in levels:
        share = seen[key] / len(sample) if sample else 0
        out.add(prefix + "_seen", f"{prefix}_seen_{key}", label, seen[key])
        out.add(prefix + "_share", f"{prefix}_share_{key}", label, round(100 * share, 1))
        out.add(prefix + "_bugs", f"{prefix}_bugs_{key}", label, bugs[key])
        rate = 100 * bugs[key] * SCALE / (share * total) if share else 0
        out.add(prefix + "_rate", f"{prefix}_rate_{key}", label, round(rate, 2))
        if key == reference:
            continue
        crude = odds_ratio(bugs[key], bugs[reference], seen[key], seen[reference])
        if crude:
            out.add(prefix + "_ratio", f"{prefix}_ratio_{key}", label, *crude)
        tables = []
        for name, _, _ in SIZE_GROUPS:
            in_group = lambda c: size_group(c) == name
            tables.append((
                sum(c["sampled_bugs"] for c in causing if in_group(c) and level_of(c) == key),
                sum(c["sampled_bugs"] for c in causing if in_group(c) and level_of(c) == reference),
                sum(1 for c in sample if in_group(c) and level_of(c) == key),
                sum(1 for c in sample if in_group(c) and level_of(c) == reference),
            ))
        adjusted = stratified_ratio(tables)
        if adjusted:
            out.add(prefix + "_adjusted", f"{prefix}_adjusted_{key}", label, *adjusted)
    out.add("size", prefix + "_sample", "Ordinary changes in the comparison sample with this property known", len(sample))
    out.add("size", prefix + "_causing_bugs", "Sampled bugs from changes with this property known",
            sum(c["sampled_bugs"] for c in causing))
