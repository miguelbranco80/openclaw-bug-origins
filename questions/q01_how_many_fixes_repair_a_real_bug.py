#!/usr/bin/env python3
"""Question 1. How many changes titled "fix" repair a real bug?

Reads: sampled_fixes.jsonl (first reader), fix_rereads_claude.jsonl (second Claude reader on 47),
fix_rereads_gpt.jsonl (GPT reader on 60).
Answer in short: a third fix no bug by the first readers' rule; a second maker's model says far fewer. The line
between an improvement and a bug is a judgment.

Usage: python3 questions/q01_how_many_fixes_repair_a_real_bug.py
"""
import collections

import charts
from common import POPULATION, Result, load, pct, wilson

LABELS = {
    "never-worked": "New code that never worked",
    "not-a-defect": "Not a bug: redesign, speed-up, wording or tooling",
    "regression": "A working thing that a later change broke",
    "latent": "Old code that broke because something outside changed",
    "unclear": "Could not tell",
}
ORDER = ("never-worked", "not-a-defect", "regression", "latent", "unclear")
REAL = {"regression", "never-worked", "latent"}


def main(quiet=False):
    fixes = load("sampled_fixes.jsonl")
    n = len(fixes)
    count = collections.Counter(fix["origin"] for fix in fixes)
    out = Result("q01")
    out.add("size", "sample", "Fixes sampled at random", n)
    out.add("size", "population", "Changes titled fix that touch product code, 1 to 22 Nov 2026", POPULATION)
    for origin in ORDER:
        out.add("origin", "origin_" + origin, LABELS[origin], count[origin], *wilson(count[origin], n))
    out.add("size", "real_bugs", "Sampled fixes that repaired a real bug", sum(count[o] for o in REAL))
    out.add("size", "not_bug_pct", "Share of sampled fixes that fixed no bug", pct(count["not-a-defect"], n),
            *wilson(count["not-a-defect"], n))
    out.add("size", "adds_test", "Sampled fixes that add or change a test", sum(bool(f["fix_adds_test"]) for f in fixes))

    second = [(r["first_origin"], r["second_origin"]) for r in load("fix_rereads_claude.jsonl")]
    out.add("size", "second_n", "Fixes read by a second reader", len(second))
    out.add("size", "second_same", "Second reader chose the same category", sum(a == b for a, b in second))
    out.add("size", "second_real_same", "Second reader agreed on bug or not a bug",
            sum((a in REAL) == (b in REAL) for a, b in second))

    gpt = [(r["first_origin"], r["second_origin"]) for r in load("fix_rereads_gpt.jsonl")]
    decided = [(a, b) for a, b in gpt if "unclear" not in (a, b)]
    not_bug = sum(b == "not-a-defect" for a, b in gpt)
    out.add("size", "gpt_n", "Fixes re-read by a GPT reader", len(gpt))
    out.add("size", "gpt_same", "GPT reader chose the same category", sum(a == b for a, b in gpt))
    out.add("size", "gpt_real_same", "GPT reader agreed on bug or not a bug",
            sum((a in REAL) == (b in REAL) for a, b in gpt))
    out.add("size", "gpt_unclear", "GPT reader could not tell", sum(b == "unclear" for a, b in gpt))
    out.add("size", "gpt_decided_n", "Fixes where neither reader said unclear", len(decided))
    out.add("size", "gpt_decided_same", "Of those, same category", sum(a == b for a, b in decided))
    out.add("size", "gpt_notbug_pct", "Share the GPT reader called not a bug", pct(not_bug, len(gpt)),
            *wilson(not_bug, len(gpt)))
    for origin in ORDER:
        out.add("gpt_first", "gpt_first_" + origin, LABELS[origin], sum(a == origin for a, b in gpt))
        out.add("gpt_second", "gpt_second_" + origin, LABELS[origin], sum(b == origin for a, b in gpt))

    out.chart(charts.bars(
        "q01-what-fixes-repaired", "What each of the 300 sampled fixes repaired, by the first readers' rule",
        [{"label": r["label"], "value": r["value"], "note": f"plausibly {r['low']}–{r['high']}% of all fixes"}
         for r in out.group("origin")]))
    labels = [r["label"] for r in out.group("gpt_first")]
    out.chart(charts.grouped(
        "q01-two-readers", "How two makers' models sorted the same 60 fixes", labels,
        [("First reader (Claude)", [r["value"] for r in out.group("gpt_first")]),
         ("Second reader (GPT)", [r["value"] for r in out.group("gpt_second")])]))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
