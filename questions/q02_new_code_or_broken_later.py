#!/usr/bin/env python3
"""Question 2. Among real bugs, how many were new code that never worked, and how many were working things broken
by a later change?

Reads: sampled_fixes.jsonl, fix_rereads_claude.jsonl, fix_rereads_gpt.jsonl, commits.tsv.
Answer in short: never-worked bugs are at least as common, from about even to about double, depending on how
strictly the cases are filtered and on who reads them.

Usage: python3 questions/q02_new_code_or_broken_later.py
"""
import charts
from common import Result, load, load_commits, traced

PAIR = {"regression", "never-worked"}


def main(quiet=False):
    fixes = load("sampled_fixes.jsonl")
    commits = load_commits()
    bugs = traced(fixes)
    never = [f for f in bugs if f["origin"] == "never-worked"]
    broke = [f for f in bugs if f["origin"] == "regression"]
    out = Result("q02")
    out.add("size", "traced", "Bugs traced to the change that introduced them", len(bugs))
    cuts = [
        ("all", "Every traced bug", lambda f: True),
        ("hm", "Reader was confident or fairly confident of the cause", lambda f: f["confidence"] in ("high", "medium")),
        ("high", "Reader was confident of the cause", lambda f: f["confidence"] == "high"),
        ("recent", "Cause is a commit since 10 Sep 2026, readable in full", lambda f: f["cause_sha"] in commits),
    ]
    ratios = []
    for key, label, keep in cuts:
        a, b = sum(keep(f) for f in never), sum(keep(f) for f in broke)
        out.add("sens_never", "sens_never_" + key, label, a)
        out.add("sens_broke", "sens_broke_" + key, label, b)
        ratios.append(a / b)

    gpt = load("fix_rereads_gpt.jsonl")
    first = [r["first_origin"] for r in gpt]
    second = [r["second_origin"] for r in gpt]
    out.add("sens_never", "sens_never_first60", "First readers, on the fixes that were re-read", first.count("never-worked"))
    out.add("sens_broke", "sens_broke_first60", "First readers, on the fixes that were re-read", first.count("regression"))
    out.add("sens_never", "sens_never_gpt60", "Second model, on the same fixes", second.count("never-worked"))
    out.add("sens_broke", "sens_broke_gpt60", "Second model, on the same fixes", second.count("regression"))
    out.add("size", "ratio_low", "Lowest never-worked to broken-later ratio among the first readers' cuts",
            round(min(ratios), 2))
    out.add("size", "ratio_high", "Highest never-worked to broken-later ratio", round(max(ratios), 2))
    out.add("size", "gpt_ratio", "Never-worked to broken-later, by the second model",
            round(second.count("never-worked") / max(1, second.count("regression")), 2))

    for name, rows in (("second", load("fix_rereads_claude.jsonl")), ("gpt", gpt)):
        pair = [r for r in rows if {r["first_origin"], r["second_origin"]} <= PAIR]
        out.add("size", name + "_pair_n", "Both readers said never-worked or broken-later", len(pair))
        out.add("size", name + "_pair_same", "Of those, same choice", sum(r["first_origin"] == r["second_origin"] for r in pair))
    both = [r for r in gpt if r["first_cause"] and r["second_cause"]]
    out.add("size", "gpt_cause_n", "Fixes where both readers named a causing change", len(both))
    out.add("size", "gpt_cause_same", "Of those, the same change",
            sum(r["first_cause"][:10] == r["second_cause"][:10] for r in both))

    labels = [r["label"] for r in out.group("sens_never")]
    out.chart(charts.grouped(
        "q02-never-worked-or-broken-later", "Never-worked against broken-later bugs, under stricter readings", labels,
        [("Never worked", [r["value"] for r in out.group("sens_never")]),
         ("Broken later", [r["value"] for r in out.group("sens_broke")])]))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
