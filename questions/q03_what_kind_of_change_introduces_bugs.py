#!/usr/bin/env python3
"""Question 3. What kind of change introduces the bugs: what was it titled, and how does it compare with an
ordinary commit?

Reads: sampled_fixes.jsonl, commits.tsv.
Answer in short: the title says little (half of everything is titled "fix"), but bug-causing changes are far
larger than ordinary commits, and changes titled "feat" cause many times their share.

Usage: python3 questions/q03_what_kind_of_change_introduces_bugs.py
"""
import statistics

import charts
from common import SCALE, Result, load, load_commits, pct, traced

NAMES = {"fix": "Titled fix", "feat": "Titled feat (a new feature)", "other": "Another title"}


def title(fix):
    prefix = fix["cause"]["prefix"]
    return prefix if prefix in ("fix", "feat") else "other"


def main(quiet=False):
    bugs = traced(load("sampled_fixes.jsonl"))
    commits = load_commits()
    never = [f for f in bugs if f["origin"] == "never-worked"]
    broke = [f for f in bugs if f["origin"] == "regression"]
    out = Result("q03")
    for key in ("fix", "feat", "other"):
        out.add("title", "title_" + key, NAMES[key], sum(title(f) == key for f in bugs))
        out.add("title_never", "title_never_" + key, NAMES[key], sum(title(f) == key for f in never))
        out.add("title_broke", "title_broke_" + key, NAMES[key], sum(title(f) == key for f in broke))

    recent = [f for f in bugs if f["cause_sha"] in commits]
    cause_sizes = [commits[f["cause_sha"]]["files_changed"] for f in recent]
    all_sizes = [c["files_changed"] for c in commits.values()]
    total = len(commits)
    compare = [
        ("feat", "Titled feat", pct(sum(title(f) == "feat" for f in recent), len(recent)),
         round(100 * sum(c["title_prefix"] == "feat" for c in commits.values()) / total, 1)),
        ("fix", "Titled fix", pct(sum(title(f) == "fix" for f in recent), len(recent)),
         round(100 * sum(c["title_prefix"] == "fix" for c in commits.values()) / total, 1)),
        ("over30", "Changed more than 30 files", pct(sum(s > 30 for s in cause_sizes), len(recent)),
         round(100 * sum(s > 30 for s in all_sizes) / total, 1)),
        ("over100", "Changed more than 100 files", pct(sum(s > 100 for s in cause_sizes), len(recent)),
         round(100 * sum(s > 100 for s in all_sizes) / total, 1)),
    ]
    for key, label, cause_value, base_value in compare:
        out.add("cmp_cause", "cmp_cause_" + key, label, cause_value)
        out.add("cmp_base", "cmp_base_" + key, label, base_value)
    out.add("size", "recent_causes", "Sampled bugs whose causing change is a commit since 10 Sep 2026", len(recent))
    out.add("size", "base_commits", "All commits on main since 10 Sep 2026", total)
    out.add("size", "cause_median_files", "Median files changed by a causing change", statistics.median(cause_sizes))
    out.add("size", "base_median_files", "Median files changed by any commit", int(statistics.median(all_sizes)))

    # Bugs per 100 commits, by the title of the commit. Titles come from the commit list for both sides.
    def kind(prefix):
        return prefix if prefix in ("fix", "feat") else "other"
    rate_names = {"feat": "Titled feat (a new feature)", "fix": "Titled fix",
                  "other": "Any other title (refactor, perf, test, chore, ...)"}
    rows = []
    for key in ("feat", "fix", "other"):
        made = [c for c in commits.values() if kind(c["title_prefix"]) == key]
        bugs_here = sum(kind(commits[f["cause_sha"]]["title_prefix"]) == key for f in recent)
        out.add("rate_commits", "rate_commits_" + key, rate_names[key], len(made))
        out.add("rate_bugs", "rate_bugs_" + key, rate_names[key], bugs_here)
        out.add("rate", "rate_" + key, rate_names[key], round(100 * bugs_here * SCALE / len(made), 1))
        out.add("rate_median_files", "rate_median_files_" + key, rate_names[key],
                int(statistics.median(c["files_changed"] for c in made)))
        rows.append({"label": rate_names[key], "value": out.value("rate_" + key),
                     "note": f"{bugs_here} sampled bugs from {len(made):,} commits"})
    out.chart(charts.bars("q03-bugs-per-100-commits-by-title", "Bugs per 100 commits, by how the change was titled", rows),
              "Each bar is a rate: bugs fixed in the period studied that trace back to commits with that title, per 100 "
              "such commits made since 10 September. The three titles cover every commit.")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
