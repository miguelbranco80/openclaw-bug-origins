#!/usr/bin/env python3
"""Question 7. Given only the bug-causing change, with no hint, can a reviewer model name the bug?

Reads: blind_review.jsonl (30 cases; each reviewer's grade by a Claude grader, and the bot's actual result),
blind_review_regrades_gpt.jsonl (the same grading by a GPT grader).
Answer in short: two current models each named 7 of 30 and together 10, against 2 for the bot's reviews at the
time. With 30 cases, one model against the bot could be chance; the two together could not easily be.

Usage: python3 questions/q07_can_other_models_name_the_bug.py
"""
import collections

import charts
from common import Result, load, sign_test, wilson

ARMS = [
    ("gpt-5.6-sol__whole", "gpt-5.6-sol", "gpt56"), ("gpt-6-astra__whole", "gpt-6-astra", "gpt6"),
    ("gpt-6.1-sol__whole", "gpt-6.1-sol (the model the bot's README names)", "gpt61"),
    ("gpt-6.2-sol__whole", "gpt-6.2-sol", "gpt62"), ("claude-opus-5-5__whole", "Claude Opus 5.5", "opus"),
    ("gpt-6.1-sol__per-file", "gpt-6.1-sol, three files at a time", "gpt61pf"),
]
TOP = ("gpt-6.2-sol__whole", "claude-opus-5-5__whole")
BOT = "The review bot's actual reviews at the time"


def main(quiet=False):
    data = load("blind_review.jsonl")
    regrade = load("blind_review_regrades_gpt.jsonl")
    n = len(data)
    hit = lambda r, arm: r["arms"][arm]["flagged"] == "exact"
    bot = lambda r: r["clawsweeper_actual"] == "exact"
    either = lambda r: any(hit(r, arm) for arm in TOP)
    second = collections.Counter(r["arm"] for r in regrade if r["second"] == "exact")
    out = Result("q07")
    out.add("size", "cases", "Bug-causing changes reviewed blind", n)
    for arm, label, slug in ARMS:
        k = sum(hit(r, arm) for r in data)
        out.add("named", "named_" + slug, label, k, *wilson(k, n))
        out.add("findings", "findings_" + slug, label, sum(r["arms"][arm]["findings"] for r in data))
        out.add("named_second", "named_second_" + slug, label, second[arm])
    k = sum(bot(r) for r in data)
    out.add("named", "named_bot", BOT, k, *wilson(k, n))
    k = sum(either(r) for r in data)
    out.add("size", "named_either_top", "Named by gpt-6.2 or Opus 5.5", k, *wilson(k, n))
    out.add("size", "named_both_top", "Named by both", sum(all(hit(r, arm) for arm in TOP) for r in data))

    def luck(first, other):
        return sign_test(sum(first(r) and not other(r) for r in data), sum(other(r) and not first(r) for r in data))
    out.add("luck", "p_two_vs_bot", "The two top models together, against the bot", luck(either, bot))
    out.add("luck", "p_one_vs_bot", "One top model, against the bot", luck(lambda r: hit(r, TOP[0]), bot))
    out.add("luck", "p_top_vs_gpt61", "One top model, against gpt-6.1 on the same instruction",
            luck(lambda r: hit(r, TOP[0]), lambda r: hit(r, "gpt-6.1-sol__whole")))
    out.add("luck", "p_perfile", "Three files at a time, against the whole change",
            luck(lambda r: hit(r, "gpt-6.1-sol__per-file"), lambda r: hit(r, "gpt-6.1-sol__whole")))
    caught = [r for r in data if any(v["flagged"] == "exact" for v in r["arms"].values())]
    out.add("size", "named_any", "Bugs named by at least one reviewer", len(caught))
    out.add("size", "named_any_old", "Of those, live more than 10 days before the fix",
            sum(r["days_to_fix"] > 10 for r in caught))
    out.add("size", "grade_cells", "Reviewer and case pairs graded twice", len(regrade))
    out.add("size", "grade_same", "Second grader agreed on named or not",
            sum((r["first"] == "exact") == (r["second"] == "exact") for r in regrade))

    out.chart(charts.bars(
        "q07-known-bugs-named", "Known bugs named by each reviewer, out of 30",
        [{"label": r["label"], "value": r["value"], "note": f"true rate plausibly {r['low']}–{r['high']}%"}
         for r in out.group("named")], top=n, context={BOT}),
        "Each bar is how many of the same 30 known bugs that reviewer named. The gray bar is what the project's bot "
        "had said at the time, for comparison.")
    out.chart(charts.bars("q07-problems-reported", "Problems each reviewer reported across the 30 changes",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("findings")]),
              "Each bar is the total number of problems that reviewer reported on the 30 changes, right or wrong.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
