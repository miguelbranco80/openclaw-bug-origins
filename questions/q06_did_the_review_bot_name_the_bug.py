#!/usr/bin/env python3
"""Question 6. Before a bug-causing change merged, had the project's review bot named the bug?

Reads: bot_reviews.jsonl (one row per traced bug, with the bot's review as it stood at merge and a Claude reader's
verdict), bot_review_rereads_gpt.jsonl (a GPT reader's verdict on the same reviews).
Answer in short: almost never. Two readers agree on the two cases where it did.

Usage: python3 questions/q06_did_the_review_bot_name_the_bug.py
"""
import collections
import statistics
from datetime import datetime

import charts
from common import Result, load, pct, wilson

LEVELS = (("none", "Said nothing about this bug"), ("related", "Raised a related concern, not this failure"),
          ("exact", "Named this bug"))


def stamp(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def main(quiet=False):
    data = load("bot_reviews.jsonl")
    status = collections.Counter(r["status"] for r in data)
    reviewed = [r for r in data if r["flagged"]]
    flags = collections.Counter(r["flagged"] for r in reviewed)
    out = Result("q06")
    out.add("size", "traced", "Bugs traced to the change that introduced them", len(data))
    out.add("size", "reviewed", "Causing changes the bot reviewed before merge", len(reviewed))
    out.add("status", "status_head", "Reviewed the revision that merged", status["reviewed-merged-head"])
    out.add("status", "status_earlier", "Reviewed only an earlier revision", status["reviewed-earlier-revision"])
    out.add("status", "status_none", "A pull request, but no review before merge", status["no-review-before-merge"])
    out.add("status", "status_nopr", "No pull request: committed straight to main", status["no-pr"])
    for level, label in LEVELS:
        out.add("flag", "flag_" + level, label, flags[level])
    out.add("size", "exact_pct", "Share where the bot named the bug", pct(flags["exact"], len(reviewed)),
            *wilson(flags["exact"], len(reviewed)))
    against = [r for r in reviewed if r["verdict"] in ("blocked", "needs-changes")]
    out.add("size", "merged_against", "Merged while the bot said blocked or needs changes", len(against))
    out.add("size", "merged_against_unrelated", "Of those, the open items were about something else",
            sum(r["flagged"] == "none" for r in against))
    out.add("size", "open_unanswered", "Flags touching the bug that were open and unanswered at merge",
            sum(r["outcome"] == "open-at-merge" for r in reviewed))
    gaps = [(stamp(r["merged_at"]) - stamp(r["review_time"])).total_seconds() / 60 for r in reviewed]
    out.add("size", "median_minutes", "Median minutes from the review in force to the merge", round(statistics.median(gaps)))
    out.add("size", "unreviewed_large", "Unreviewed cases from pull requests of 500 files or more",
            sum(r["status"] == "no-review-before-merge" and (r.get("changed_files") or 0) >= 500 for r in data))
    for verdict, label in (("blocked", "Blocked"), ("needs-changes", "Needs changes"),
                           ("needs-maintainer", "Needs maintainer review"), ("ready", "Ready")):
        out.add("verdict", "verdict_" + verdict, label, sum(r["verdict"] == verdict for r in reviewed))

    gpt = load("bot_review_rereads_gpt.jsonl")
    out.add("size", "gpt_n", "Reviews re-read by a GPT reader", len(gpt))
    out.add("size", "gpt_same", "Same answer from the GPT reader", sum(r["first"] == r["second"] for r in gpt))
    out.add("size", "gpt_exact_same", "Same answer on whether the bot named the bug",
            sum((r["first"] == "exact") == (r["second"] == "exact") for r in gpt))
    for level, label in LEVELS:
        out.add("gpt_flag", "gpt_flag_" + level, label, sum(r["second"] == level for r in gpt))

    labels = [label for _, label in LEVELS]
    out.chart(charts.grouped(
        "q06-what-the-review-said", "What the bot's review said about the bug, by two readers", labels,
        [("First reader (Claude)", [r["value"] for r in out.group("flag")]),
         ("Second reader (GPT)", [r["value"] for r in out.group("gpt_flag")])]),
        f"The same {len(reviewed)} reviews, read twice. Each bar is a number of bug-causing changes; each color adds "
        f"up to {len(reviewed)}.")
    out.chart(charts.bars("q06-was-there-a-review", "Whether the bot had reviewed the causing change",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("status")]),
              f"Each bar is a number of bug-causing changes. The four bars add up to {len(data)}.")
    out.chart(charts.bars("q06-verdict-at-merge", "The bot's overall verdict when the bug-causing change merged",
                          [{"label": r["label"], "value": r["value"]} for r in out.group("verdict")]),
              f"Each bar is a number of bug-causing changes the bot had reviewed. The four bars add up to {len(reviewed)}.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
