#!/usr/bin/env python3
"""Question 30. Three comparisons could be the kind of work in disguise: quick merges, commits straight to main, and
busy days are all dominated by small routine changes. Do they hold when the kind of work is held equal?

Reads: changes.jsonl, commits.tsv, pull_requests.tsv, pull_request_links.tsv, sampled_fixes.jsonl.
Method: the same stratified ratio as questions 11, 14 and 19, with finer groups. The kind of change is one of six
titles (feat, fix, refactor, perf, test, other) instead of three; for pull requests, a further split says whether
the change belongs to a line of work of 100 pull requests or more (see question 29).
Answer in short: see the three ratios; each is printed beside the figure the report gave before.

Usage: python3 questions/q30_do_three_findings_hold_at_equal_kind_of_work.py
"""
import collections

from common import (Result, landed, load, load_commits, load_pull_requests, recent_causes, size_group,
                    stratified_ratio, utc_day)
from q29_how_is_the_code_produced import LINE_OF_WORK, kind, line_of_work, load_links


def ratio(units, weight, level_of, stratum, key, reference):
    """Stratified ratio of bugs per unit, `key` against `reference`. weight(unit) is its count of sampled bugs."""
    cells = collections.Counter()
    for unit in units:
        level = level_of(unit)
        if level in (key, reference):
            cells[(stratum(unit), "bugs", level)] += weight(unit)
            cells[(stratum(unit), "seen", level)] += unit.get("seen", 1)
    tables = [(cells[(name, "bugs", key)], cells[(name, "bugs", reference)],
               cells[(name, "seen", key)], cells[(name, "seen", reference)]) for name in {name for name, _, _ in cells}]
    return stratified_ratio(tables)


def main(quiet=False):
    commits, pulls, links = load_commits(), load_pull_requests(), load_links()
    out = Result("q30")

    # 1. Time open (finding 14), over the comparison sample and the bug-causing pull requests.
    changes = load("changes.jsonl")
    label_of = {}
    for number, link in links.items():
        if number in pulls:
            label_of[number] = line_of_work(link["head_branch"], pulls[number]["author"])
    sizes = collections.Counter(label for label in label_of.values() if label)
    in_line = lambda c: sizes[label_of.get(str(c["pr_number"]))] >= LINE_OF_WORK if label_of.get(str(c["pr_number"])) else False
    units = []
    for c in changes:
        if c["in_comparison_sample"]:
            units.append(dict(c, seen=1, bugs=0))
        if c["sampled_bugs"]:
            units.append(dict(c, seen=0, bugs=c["sampled_bugs"]))
    open_level = lambda c: "hour" if c["minutes_open"] < 60 else "hours" if c["minutes_open"] < 1440 else "day"
    month = lambda c: c["committed_at"][:7]
    designs = [("as_reported", "Size and month held equal, as in finding 14", lambda c: (size_group(c), month(c))),
               ("three", "Size, month and three kinds of change (feat, fix, other) held equal",
                lambda c: (size_group(c), month(c), c["title_prefix"] if c["title_prefix"] in ("feat", "fix") else "other")),
               ("kind", "Size, month and six kinds of change held equal", lambda c: (size_group(c), month(c), kind(c))),
               ("kind_line", "Size, month, six kinds of change and line of work held equal",
                lambda c: (size_group(c), month(c), kind(c), in_line(c)))]
    for key, label, stratum in designs:
        got = ratio(units, lambda c: c["bugs"], open_level, stratum, "hour", "day")
        if got:
            out.add("open", "open_" + key, label, *got)
    sample = [c for c in changes if c["in_comparison_sample"]]
    quick = [c for c in sample if c["minutes_open"] < 60]
    out.add("size", "quick_in_line_pct", "Share of pull requests merged within the hour that belong to a line of work",
            round(100 * sum(in_line(c) for c in quick) / len(quick)))
    out.add("size", "slow_in_line_pct", "Share of pull requests open a day or more that belong to a line of work",
            round(100 * sum(in_line(c) for c in sample if c["minutes_open"] >= 1440) / max(1, sum(c["minutes_open"] >= 1440 for c in sample))))

    # 2. Straight to main (finding 11) and 3. busy days (finding 18), over every commit.
    causes = collections.Counter(recent_causes(commits))
    everything = [dict(c, bugs=causes[sha]) for sha, c in commits.items()]
    route = lambda c: "pr" if c["pr_number"] else "direct"
    per_day = collections.Counter(utc_day(c["committed_at"]) for c in commits.values())
    ordered = sorted(per_day.values())
    low, high = ordered[len(ordered) // 3], ordered[2 * len(ordered) // 3]
    busy = lambda c: (lambda n: "quiet" if n < low else "middle" if n < high else "busy")(per_day[utc_day(c["committed_at"])])
    three = lambda c: c["title_prefix"] if c["title_prefix"] in ("feat", "fix") else "other"
    for name, level_of, key, reference in (("direct", route, "direct", "pr"), ("busy", busy, "busy", "quiet")):
        for design, label, stratum in (
                ("as_reported", "Size, three kinds of change and half-month held equal",
                 lambda c: (size_group(c), three(c), landed(c))),
                ("kind", "Size, six kinds of change and half-month held equal",
                 lambda c: (size_group(c), kind(c), landed(c)))):
            got = ratio(everything, lambda c: c["bugs"], level_of, stratum, key, reference)
            if got:
                out.add(name, f"{name}_{design}", label, *got)
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
