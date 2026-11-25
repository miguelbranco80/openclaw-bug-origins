#!/usr/bin/env python3
"""Question 8. The two strongest reviewers reported 148 problems. Fourteen were the known bug. Are the rest real?

Reads: reported_problems.jsonl (each reported problem with three checks: was it later fixed on main, and what two
code-tracing checkers concluded), checker_control.jsonl (the checkers tested on the known-real problems, before and
after the fix).
Answer in short: a fifth are proven by a later fix; both checkers confirm about nine in ten; about a third of the
confirmed ones are minor. Nothing was executed.

Usage: python3 questions/q08_are_the_other_reported_problems_real.py
"""
import charts
from common import Result, load


def main(quiet=False):
    data = load("reported_problems.jsonl")
    control = [r for r in load("checker_control.jsonl") if r["known_bug"] == "exact"]
    known = lambda r: r["known_bug"] == "exact"
    both = lambda r: r["opus"] == "confirmed" and r["gpt"] == "confirmed"
    visible = lambda r: r["opus_impact"] == "user-visible" and r["gpt_impact"] == "user-visible"
    proven = lambda r: known(r) or r["later"] == "yes"
    rest = [r for r in data if not proven(r)]
    out = Result("q08")
    out.add("size", "findings", "Problems reported by gpt-6.2 and Opus 5.5", len(data))
    out.add("size", "known", "Reports that are the known bug", sum(known(r) for r in data))
    out.add("later", "later_yes", "Later fixed on main", sum(r["later"] == "yes" for r in data))
    out.add("later", "later_partly", "Partly fixed later", sum(r["later"] == "partly" for r in data))
    out.add("later", "later_no", "No later fix found", sum(r["later"] == "no" for r in data))
    out.add("size", "later_other", "Later-fixed reports that are not the known bug",
            sum(r["later"] == "yes" and not known(r) for r in data))
    out.add("quality", "q_proven", "Proven: the known bug, or fixed later on main", sum(proven(r) for r in data))
    out.add("quality", "q_visible", "Both checkers: real, and a user would notice", sum(both(r) and visible(r) for r in rest))
    out.add("quality", "q_minor", "Both checkers: real, but minor", sum(both(r) and not visible(r) for r in rest))
    out.add("quality", "q_unconfirmed", "Refuted or unclear to at least one checker", sum(not both(r) for r in rest))
    out.add("size", "both_confirmed", "Confirmed by both checkers", sum(both(r) for r in data))
    out.add("size", "refuted_any", "Refuted by at least one checker",
            sum(r["opus"] == "refuted" or r["gpt"] == "refuted" for r in data))
    out.add("size", "later_found_known", "Known-real reports for which the later-fix check found the fix",
            sum(known(r) and r["later"] == "yes" for r in data))
    for kind, label in (("gpt", "gpt-6.2 checker"), ("opus", "Opus 5.5 checker")):
        out.add("control_original", "dismissed_" + kind, label, sum(r[kind + "_at_cause"] != "confirmed" for r in control))
        out.add("control_fixed", "flipped_" + kind, label, sum(r[kind + "_at_fix"] != "confirmed" for r in control))
    out.add("size", "control_cases", "Known-real reports used as the control", len(control))
    out.add("size", "control_both_still", "Still confirmed by both checkers after the fix",
            sum(r["gpt_at_fix"] == "confirmed" and r["opus_at_fix"] == "confirmed" for r in control))

    out.chart(charts.bars("q08-where-the-reports-stand", "Where the 148 reported problems stand",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("quality")]))
    labels = [r["label"] for r in out.group("control_original")]
    out.chart(charts.grouped(
        "q08-can-the-checkers-say-no", "The checkers tested on 14 known-real problems", labels,
        [("Wrongly dismissed, on the original code", [r["value"] for r in out.group("control_original")]),
         ("Stopped confirming, once the bug was fixed", [r["value"] for r in out.group("control_fixed")])],
        top=len(control)))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
