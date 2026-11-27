#!/usr/bin/env python3
"""Question 29. How is the code produced: at what hours, in what kinds of work, and in how many parallel lines?

Reads: commits.tsv, pull_requests.tsv, pull_request_links.tsv, sampled_fixes.jsonl.
Nothing is judged. Hours and gaps come from commit times. A "line of work" is a group of pull requests whose branch
names start the same way: the part before the first "/", or, when that part is the author's own account name or the
name of a coding tool, the first two words after it. Branch names that only state a type of change ("fix/...",
"feat/...") are not counted as a line of work.
Answer in short: the most active account commits at every hour of the day with almost no breaks, most of what merges
is repair and upkeep, and on its busiest day that account merged several hundred pull requests in a handful of named
lines of work.

Usage: python3 questions/q29_how_is_the_code_produced.py
"""
import collections
import csv
import os
import statistics
from datetime import datetime, timezone

import charts
from common import DATASET, SCALE, Result, load_commits, load_pull_requests, recent_causes, utc_day

KINDS = [("feat", "Titled feat (a new feature)"), ("fix", "Titled fix"), ("refactor", "Titled refactor"),
         ("perf", "Titled perf (speed or memory)"), ("test", "Titled test"), ("other", "Any other title")]
TOOLS = {"codex", "claude", "cursor", "copilot", "amp", "devin", "agent", "agents"}
TYPE_ONLY = {"fix", "fixes", "feat", "feature", "perf", "test", "tests", "refactor", "docs", "chore", "ci", "build",
             "improve", "style", "revert", "hotfix", "bugfix", "bug", "main", "patch", "dependabot", "release"}
LINE_OF_WORK = 100  # pull requests sharing a branch name start, over the period, to count as one line of work


def kind(commit):
    return commit["title_prefix"] if commit["title_prefix"] in ("feat", "fix", "refactor", "perf", "test") else "other"


def load_links():
    with open(os.path.join(DATASET, "pull_request_links.tsv")) as handle:
        return {row["number"]: row for row in csv.DictReader(handle, delimiter="\t")}


def words(text, count):
    kept = [word for word in text.replace("_", "-").split("-") if word and not word.isdigit()]
    return "-".join(kept[:count]).lower()


def line_of_work(branch, author):
    """The start of a branch name that pull requests of one line of work share, or None."""
    head, _, rest = branch.partition("/")
    if rest and (head.lower() == author.lower() or head.lower() in TOOLS):
        label = words(rest, 2)
    else:
        label = words(head, 1) if rest else words(branch, 1)
    return None if not label or label in TYPE_ONLY else label


def main(quiet=False):
    commits, pulls, links = load_commits(), load_pull_requests(), load_links()
    out = Result("q29")

    # The clock: when the most active account commits.
    top = [c for c in commits.values() if c["author_rank"] == 1]
    hour = lambda c: datetime.fromisoformat(c["committed_at"]).astimezone(timezone.utc).hour
    per_hour = collections.Counter(hour(c) for c in top)
    days = {utc_day(c["committed_at"]) for c in top}
    gaps = [c["minutes_since_author_previous"] for c in top if c["minutes_since_author_previous"] is not None]
    out.add("clock", "top_commits", "Commits by the most active account", len(top))
    out.add("clock", "top_days", "Days on which it committed", len(days))
    out.add("clock", "top_per_day", "Its median commits per day", int(statistics.median(collections.Counter(utc_day(c["committed_at"]) for c in top).values())))
    out.add("clock", "top_quiet_hour", "Its commits in its quietest hour of the day (UTC), whole period", min(per_hour[h] for h in range(24)))
    out.add("clock", "top_busy_hour", "Its commits in its busiest hour of the day (UTC), whole period", max(per_hour.values()))
    out.add("clock", "top_quiet_hour_pct", "Quietest hour as a share of the busiest", round(100 * min(per_hour[h] for h in range(24)) / max(per_hour.values())))
    out.add("clock", "top_median_gap", "Its median minutes between one commit and the next", round(statistics.median(gaps), 1))
    out.add("clock", "top_long_breaks", "Breaks of more than six hours between its commits", sum(g > 360 for g in gaps))
    for hour_of_day in range(24):
        out.add("hours", f"hour_{hour_of_day:02d}", f"{hour_of_day:02d}:00", per_hour[hour_of_day])

    # The kind of work, and the bugs each kind carried.
    causes = recent_causes(commits)
    for key, label in KINDS:
        made = [c for c in commits.values() if kind(c) == key]
        bugs = sum(kind(commits[sha]) == key for sha in causes)
        out.add("kind_commits", "kind_commits_" + key, label, len(made))
        out.add("kind_share", "kind_share_" + key, label, round(100 * len(made) / len(commits), 1))
        out.add("kind_bugs", "kind_bugs_" + key, label, bugs)
        out.add("kind_bugs_pct", "kind_bugs_pct_" + key, label, round(100 * bugs / len(causes), 1))
        out.add("kind_rate", "kind_rate_" + key, label, round(100 * bugs * SCALE / len(made), 1))
    out.chart(charts.bars(
        "q29-bugs-per-100-commits-by-kind", "Bugs per 100 commits, by the kind of work in the title",
        [{"label": label, "value": out.value("kind_rate_" + key),
          "note": f"{out.value('kind_bugs_' + key)} sampled bugs, {out.value('kind_share_' + key)}% of commits"}
         for key, label in KINDS]),
        "Each bar is a rate: bugs fixed in the period studied that trace back to commits with that title, per 100 "
        "such commits made since 10 September. The six titles cover every commit.")
    upkeep = sum(kind(c) != "feat" for c in commits.values())
    out.add("size", "not_feature_pct", "Share of commits not titled as a feature", round(100 * upkeep / len(commits), 1))

    # Lines of work: pull requests of the most active account, grouped by how their branch name starts.
    mine = {}
    for commit in top:
        number = commit["pr_number"]
        if number in links and number in pulls:
            mine[number] = (utc_day(commit["committed_at"]), line_of_work(links[number]["head_branch"], pulls[number]["author"]))
    sizes = collections.Counter(label for _, label in mine.values() if label)
    lines = {label for label, count in sizes.items() if count >= LINE_OF_WORK}
    out.add("lines", "top_pulls", "Pull requests of the most active account with a known branch name", len(mine))
    out.add("lines", "lines_of_work", f"Lines of work of {LINE_OF_WORK} pull requests or more", len(lines))
    out.add("lines", "lines_share_pct", "Share of its pull requests that belong to one of them",
            round(100 * sum(label in lines for _, label in mine.values()) / len(mine)))
    active = collections.defaultdict(set)
    for day, label in mine.values():
        if label in lines:
            active[label].add(day)
    for label, count in sizes.most_common(12):
        if label in lines:
            out.add("line_pulls", "line_pulls_" + label, label, count)
            out.add("line_days", "line_days_" + label, label, len(active[label]))
    per_day = collections.Counter(day for day, _ in mine.values())
    busiest, merged = per_day.most_common(1)[0]
    today = collections.Counter(label for day, label in mine.values() if day == busiest and label in lines)
    out.add("day", "busiest_day", "Its busiest day", busiest.strftime("%-d %B %Y"))
    out.add("day", "busiest_day_pulls", "Pull requests it merged that day", merged)
    out.add("day", "busiest_day_lines", "Lines of work with ten or more pull requests that day", sum(n >= 10 for n in today.values()))
    out.add("day", "busiest_day_in_lines_pct", "Share of that day's pull requests in a line of work",
            round(100 * sum(today.values()) / merged))
    for label, count in today.most_common(8):
        if count >= 10:
            out.add("day_line", "day_line_" + label, label, count)
    out.chart(charts.bars(
        "q29-lines-of-work-on-the-busiest-day", "Pull requests the most active account merged on its busiest day, by line of work",
        [{"label": label, "value": count} for label, count in today.most_common(8) if count >= 10]
        + [{"label": "Everything else", "value": merged - sum(count for count in today.values() if count >= 10)}]),
        "Each bar is a count of pull requests merged that day whose branch names start the same way. The label is that "
        "shared start, as the project wrote it.")
    out.add("day", "busiest_day_per_line_days", "Median lines of work active per day (ten or more pull requests)",
            int(statistics.median(
                sum(n >= 10 for n in collections.Counter(l for d, l in mine.values() if d == day and l in lines).values())
                for day in per_day)))

    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
