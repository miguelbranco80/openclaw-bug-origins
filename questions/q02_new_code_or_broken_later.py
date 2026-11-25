#!/usr/bin/env python3
"""Question 2. Among real bugs, how many were new code that never worked, and how many were working things broken
by a later change?

Reads: sampled_fixes.jsonl, fix_rereads_same_model.jsonl, fix_rereads_other_maker.jsonl, commits.tsv.
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

    gpt = load("fix_rereads_other_maker.jsonl")
    first = [r["first_origin"] for r in gpt]
    second = [r["second_origin"] for r in gpt]
    out.add("sens_never", "sens_never_first_same", "Main reader, on the fixes the other maker's reader also read", first.count("never-worked"))
    out.add("sens_broke", "sens_broke_first_same", "Main reader, on the fixes the other maker's reader also read", first.count("regression"))
    out.add("sens_never", "sens_never_other", "The other maker's reader, on the same fixes", second.count("never-worked"))
    out.add("sens_broke", "sens_broke_other", "The other maker's reader, on the same fixes", second.count("regression"))
    out.add("size", "ratio_low", "Lowest never-worked to broken-later ratio among the main reader's cuts",
            round(min(ratios), 2))
    out.add("size", "ratio_high", "Highest never-worked to broken-later ratio", round(max(ratios), 2))
    out.add("size", "other_ratio", "Never-worked to broken-later, by the other maker's reader",
            round(second.count("never-worked") / max(1, second.count("regression")), 2))

    for name, rows in (("second", load("fix_rereads_same_model.jsonl")), ("other", gpt)):
        pair = [r for r in rows if {r["first_origin"], r["second_origin"]} <= PAIR]
        out.add("size", name + "_pair_n", "Both readers said never-worked or broken-later", len(pair))
        out.add("size", name + "_pair_same", "Of those, same choice", sum(r["first_origin"] == r["second_origin"] for r in pair))
    both = [r for r in gpt if r["first_cause"] and r["second_cause"]]
    out.add("size", "other_cause_n", "Fixes where both readers named a causing change", len(both))
    out.add("size", "other_cause_same", "Of those, the same change",
            sum(r["first_cause"][:10] == r["second_cause"][:10] for r in both))

    for a, b in zip(out.group("sens_never"), out.group("sens_broke")):
        key = a["metric"].replace("sens_never_", "")
        out.add("never_share", "never_share_" + key, a["label"], round(100 * a["value"] / (a["value"] + b["value"])))
    # Three counts are enough to show the spread; all six are in the table under the chart.
    shown = [("all", "Main reader, counting every bug it traced"),
             ("high", "Main reader, counting only bugs where it was sure of the cause"),
             ("other", f"The other maker's reader, on the {len(gpt)} fixes it also read")]
    rows = [{"label": label, "value": out.value("never_share_" + key),
             "note": f"{out.value('sens_never_' + key)} never worked, {out.value('sens_broke_' + key)} broken later"}
            for key, label in shown]
    out.chart(charts.bars(
        "q02-share-never-worked", "How much of the time the bug was new code that never worked, by three ways of counting",
        rows, unit="%", top=100, reference=(50, "half")),
        "Take only bugs that were one of two kinds: new code that never worked, or a working thing broken later. Each "
        "bar is the percentage that were the first kind. Past the dashed line means the first kind is the more common.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
