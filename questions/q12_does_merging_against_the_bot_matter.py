#!/usr/bin/env python3
"""Question 12. Do changes merged while the review bot said "blocked" or "needs changes" cause more bugs than
changes it called "ready"?

Reads: changes.jsonl (a random comparison sample of ordinary pull requests, plus the bug-causing ones, each with the
bot's verdict in force when it merged), commits.tsv, sampled_fixes.jsonl.
Method: questions/common.py `compare`. The ratio is how many times more often a change of one kind caused a sampled
bug than a change the bot called ready; "adjusted" holds the size of the change fixed.

Usage: python3 questions/q12_does_merging_against_the_bot_matter.py
"""
import charts
from common import Result, compare, load

LEVELS = [("ready", "Bot said ready"), ("objected", "Bot said blocked or needs changes"),
          ("maintainer", "Bot said needs maintainer review"), ("none", "No bot review before merge")]


def level(change):
    verdict = change["bot_verdict_at_merge"]
    if verdict is None:
        return "none"
    return {"ready": "ready", "blocked": "objected", "needs-changes": "objected", "needs-maintainer": "maintainer"}.get(verdict)


def main(quiet=False):
    changes = load("changes.jsonl")
    out = Result("q12")
    compare(out, "verdict", changes, level, LEVELS, "ready")
    keep = [key for key, _ in LEVELS if out.value("verdict_seen_" + key) >= 20]
    out.chart(charts.bars(
        "q12-bugs-by-bot-verdict", "Bugs per 100 changes, by what the bot said when the change merged",
        [{"label": label, "value": out.value("verdict_rate_" + key),
          "note": f"{out.value('verdict_bugs_' + key)} bugs, from {out.value('verdict_share_' + key)}% of changes"}
         for key, label in LEVELS if key in keep]),
        "Each bar is a rate: bugs fixed in the period studied that trace back to changes merged under that verdict, per "
        "100 such changes. Verdicts seen on fewer than 20 sampled changes are left out.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
