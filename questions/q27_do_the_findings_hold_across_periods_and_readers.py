#!/usr/bin/env python3
"""Question 27. Do the central findings hold in an earlier period, and under a different reader?

Reads: sampled_fixes.jsonl (the main reader's answer for every sampled fix of every period), bot_reviews.jsonl,
frames.json, readers.json, and commits.tsv, and published_2026_11.json (the numbers of the study as first published, when a
different model read the November fixes; tag `published-2026-11`).

Three columns:
  the November fixes, read by the other maker's model (its answers are in published_2026_11.json);
  the same November fixes, read by the current main reader;
  the fixes of the other period, read by the current main reader.
Comparing the first two shows what the reader changes. Comparing the last two shows what the period changes.

Usage: python3 questions/q27_do_the_findings_hold_across_periods_and_readers.py
"""
import collections
import statistics

import charts
from common import FRAMES, READERS, SCALE, Result, load, load_commits, pct, recent_causes, utc_day, wilson

REAL = ("regression", "never-worked", "latent")


def frame_of(rank):
    return (rank - 1) // 100000 + 1


def column(out, key, label, fixes, reviews):
    n = len(fixes)
    count = lambda origin: sum(f["origin"] == origin for f in fixes)
    never, broke = count("never-worked"), count("regression")
    traced = [f for f in fixes if f["origin"] in ("never-worked", "regression") and f.get("cause")]
    later = [f["cause"]["days_to_fix"] for f in traced if f["origin"] == "regression" and f["cause"].get("days_to_fix") is not None]
    reviewed = [r for r in reviews if r["status"].startswith("reviewed")]
    out.add("fixes", "fixes_" + key, label, n)
    out.add("not_bug_pct", "not_bug_pct_" + key, label, pct(count("not-a-defect"), n), *wilson(count("not-a-defect"), n))
    out.add("unclear_pct", "unclear_pct_" + key, label, pct(count("unclear"), n), *wilson(count("unclear"), n))
    out.add("never", "never_" + key, label, never)
    out.add("broke", "broke_" + key, label, broke)
    out.add("never_share", "never_share_" + key, label, pct(never, never + broke), *wilson(never, never + broke))
    out.add("feat_pct", "feat_pct_" + key, label, pct(sum(f["cause"]["prefix"] == "feat" for f in traced), len(traced)))
    out.add("cause_files", "cause_files_" + key, label,
            statistics.median(f["cause"]["files_changed"] for f in traced) if traced else 0)
    out.add("days", "days_" + key, label, round(statistics.median(later), 1) if later else 0)
    out.add("reviewed", "reviewed_" + key, label, len(reviewed))
    out.add("named", "named_" + key, label, sum(r["flagged"] == "exact" for r in reviewed))


def main(quiet=False):
    fixes, reviews = load("sampled_fixes.jsonl"), load("bot_reviews.jsonl")
    before = load("published_2026_11.json")
    was = lambda question, metric: before[question][metric]["value"]
    out = Result("q27")
    first = f"November fixes, read by {READERS['fixes_other_maker']}"
    n = was("q01", "sample")
    never, broke = was("q01", "origin_never-worked"), was("q01", "origin_regression")
    out.add("fixes", "fixes_published", first, n)
    out.add("not_bug_pct", "not_bug_pct_published", first, pct(was("q01", "origin_not-a-defect"), n), *wilson(was("q01", "origin_not-a-defect"), n))
    out.add("unclear_pct", "unclear_pct_published", first, pct(was("q01", "origin_unclear"), n), *wilson(was("q01", "origin_unclear"), n))
    out.add("never", "never_published", first, never)
    out.add("broke", "broke_published", first, broke)
    out.add("never_share", "never_share_published", first, pct(never, never + broke), *wilson(never, never + broke))
    out.add("feat_pct", "feat_pct_published", first, was("q03", "cmp_cause_feat"))
    out.add("cause_files", "cause_files_published", first, was("q03", "cause_median_files"))
    out.add("days", "days_published", first, was("q05", "median_broke"))
    out.add("reviewed", "reviewed_published", first, was("q06", "reviewed"))
    out.add("named", "named_published", first, was("q06", "flag_exact"))
    columns = [("published", first)]
    for frame in FRAMES:
        key = f"frame{frame['frame']}"
        until = frame["until"][:10] if frame["until"] else max(utc_day(c["committed_at"]) for c in load_commits().values()).isoformat()
        label = f"Fixes from {frame['since'][:10]} to {until}, read by {READERS['fixes']}"
        column(out, key, label, [f for f in fixes if frame_of(f["rank"]) == frame["frame"]],
               [r for r in reviews if frame_of(r["rank"]) == frame["frame"]])
        columns.append((key, label))
    commits = load_commits()
    causes = collections.Counter(commits[sha]["committed_at"][:7] for sha in recent_causes(commits))
    landed = collections.Counter(commit["committed_at"][:7] for commit in commits.values())
    for month, key in (("2026-09", "sep"), ("2026-10", "oct"), ("2026-11", "nov")):
        if landed[month]:
            out.add("rate_by_month", "rate_" + key, f"Bugs per 100 commits landed in {month}",
                    round(100 * causes[month] * SCALE / landed[month], 1))
    traced_bugs = [f for f in fixes if f["origin"] in ("never-worked", "regression") and f.get("cause_sha")]
    out.add("size", "left_out", "Traced bugs whose causing commit is not in the commit list",
            sum(f["cause_sha"] not in commits for f in traced_bugs))
    out.chart(charts.bars(
        "q27-not-a-bug-by-reader-and-period", "Share of changes titled fix that repaired no bug, by who read them and when they merged",
        [{"label": label, "value": out.value("not_bug_pct_" + key), "note": f"of {out.value('fixes_' + key)} fixes"}
         for key, label in columns], unit="%", top=100),
        "Each bar is the percentage of sampled fixes that the reader said repaired no bug. The first two bars are the "
        "same fixes read by two different models: their gap is the reader. The last two bars are one model reading "
        "two periods: their gap is the period.")
    out.chart(charts.bars(
        "q27-never-worked-by-reader-and-period", "Share of traced bugs that were new code that never worked, by who read them and when",
        [{"label": label, "value": out.value("never_share_" + key),
          "note": f"{out.value('never_' + key)} never worked, {out.value('broke_' + key)} broken later"}
         for key, label in columns], unit="%", top=100, reference=(50, "half")),
        "Take only bugs that were new code that never worked, or a working thing broken later. Each bar is the "
        "percentage that were the first kind. Past the dashed line means the first kind is the more common.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
