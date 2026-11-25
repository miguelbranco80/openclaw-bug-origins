#!/usr/bin/env python3
"""Question 16. Do pull requests that attach a screenshot or video cause fewer bugs?

Reads: changes.jsonl. `visual_proof` is true when the pull request's description, as it read at merge, embedded at
least one picture or video. `interface_files` counts files changed under `ui/` or `apps/`.
Visual proof is mostly attached to interface changes, and interface changes cause more bugs than others, so the fair
comparison is among interface changes only. Method as in question 12.
Answer in short: no. Among interface changes, those with a screenshot or video caused more bugs, not fewer.

Usage: python3 questions/q16_do_changes_with_visual_proof_cause_fewer_bugs.py
"""
import charts
from common import Result, compare, load

LEVELS = [("no", "No screenshot or video in the description"), ("yes", "A screenshot or video in the description")]


def main(quiet=False):
    changes = load("changes.jsonl")
    out = Result("q16")
    proof = lambda c: "yes" if c["visual_proof"] else "no"
    compare(out, "any", changes, proof, LEVELS, "no")
    compare(out, "interface", changes, lambda c: proof(c) if c["interface_files"] > 0 else None, LEVELS, "no")
    compare(out, "kind", changes, lambda c: "ui" if c["interface_files"] > 0 else "other",
            [("other", "Does not touch the interface"), ("ui", "Touches the interface")], "other")
    out.chart(charts.bars(
        "q16-bugs-by-visual-proof", "Among interface changes: bugs per 100 changes, with and without a screenshot or video",
        [{"label": label, "value": out.value("interface_rate_" + key),
          "note": f"{out.value('interface_bugs_' + key)} sampled bugs; {out.value('interface_share_' + key)}% of all changes"}
         for key, label in LEVELS]),
        "Only pull requests that change files under ui/ or apps/. Each bar is a rate: bugs fixed in the period studied "
        "that trace back to such pull requests, per 100 of them.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
