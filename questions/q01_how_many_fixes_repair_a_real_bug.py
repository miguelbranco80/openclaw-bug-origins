#!/usr/bin/env python3
"""Question 1. How many changes titled "fix" repair a real bug?

Reads: sampled_fixes.jsonl (first model), fix_rereads_same_model.jsonl (second Claude model on 47),
fix_rereads_other_maker.jsonl (GPT model on 60).
Answer in short: it depends on the model: about a tenth by one model, a third by another. The line
between an improvement and a bug is a judgment.

Usage: python3 questions/q01_how_many_fixes_repair_a_real_bug.py
"""
import collections

import charts
from common import POPULATION, READERS, SAMPLE, Result, load, pct, wilson

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
    out.add("size", "population", "Changes titled fix that touch product code, in the period studied", POPULATION)
    for origin in ORDER:
        out.add("origin", "origin_" + origin, LABELS[origin], count[origin], *wilson(count[origin], n))
    out.add("size", "real_bugs", "Sampled fixes that repaired a real bug", sum(count[o] for o in REAL))
    out.add("size", "not_bug_pct", "Share of sampled fixes that fixed no bug", pct(count["not-a-defect"], n),
            *wilson(count["not-a-defect"], n))
    out.add("size", "adds_test", "Sampled fixes that add or change a test", sum(bool(f["fix_adds_test"]) for f in fixes))

    second = [(r["first_origin"], r["second_origin"]) for r in load("fix_rereads_same_model.jsonl")]
    out.add("size", "second_n", "Fixes read a second time by the main model", len(second))
    out.add("size", "second_same", "The second run chose the same category", sum(a == b for a, b in second))
    out.add("size", "second_real_same", "The second run agreed on bug or not a bug",
            sum((a in REAL) == (b in REAL) for a, b in second))

    gpt = [(r["first_origin"], r["second_origin"]) for r in load("fix_rereads_other_maker.jsonl")]
    decided = [(a, b) for a, b in gpt if "unclear" not in (a, b)]
    not_bug = sum(b == "not-a-defect" for a, b in gpt)
    out.add("size", "other_n", "Fixes also read by the second model", len(gpt))
    out.add("size", "other_same", "The two models chose the same category", sum(a == b for a, b in gpt))
    out.add("size", "other_real_same", "The two models agreed on bug or not a bug",
            sum((a in REAL) == (b in REAL) for a, b in gpt))
    out.add("size", "other_unclear", "The second model could not tell", sum(b == "unclear" for a, b in gpt))
    out.add("size", "other_decided_n", "Fixes where neither model said unclear", len(decided))
    out.add("size", "other_decided_same", "Of those, same category", sum(a == b for a, b in decided))
    out.add("size", "other_notbug_pct", "Share the second model called not a bug", pct(not_bug, len(gpt)),
            *wilson(not_bug, len(gpt)))
    for origin in ORDER:
        out.add("other_first", "other_first_" + origin, LABELS[origin], sum(a == origin for a, b in gpt))
        out.add("other_second", "other_second_" + origin, LABELS[origin], sum(b == origin for a, b in gpt))

    out.chart(charts.bars(
        "q01-what-fixes-repaired", f"What each of the {SAMPLE:,} sampled fixes repaired, by the main model",
        [{"label": r["label"], "value": r["value"], "note": f"plausibly {r['low']}–{r['high']}% of all fixes"}
         for r in out.group("origin")]),
        f"Each bar is a number of sampled fixes. The five bars add up to {SAMPLE:,}.")
    labels = [r["label"] for r in out.group("other_first")]
    out.chart(charts.grouped(
        "q01-two-readers", f"How the two models sorted the same {len(gpt)} fixes", labels,
        [(f"Main model ({READERS['fixes']})", [r["value"] for r in out.group("other_first")]),
         (f"Second model ({READERS['fixes_other_maker']})", [r["value"] for r in out.group("other_second")])]),
        f"The same {len(gpt)} fixes, sorted twice. Blue is where the main model put them, orange where the second "
        f"model did; each color adds up to {len(gpt)}.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
