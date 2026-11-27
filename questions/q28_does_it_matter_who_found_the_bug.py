#!/usr/bin/env python3
"""Question 28. Most fixes close no reported issue. Do the findings hold on the bugs that a person from outside the
project reported?

Reads: sampled_fixes.jsonl, commits.tsv, pull_requests.tsv, pull_request_links.tsv.
A fix counts as "reported from outside" when GitHub records its pull request as closing an issue, and the issue was
filed by a person who merged none of the fetched pull requests. Everything else is "no outside report": the fix
closes no issue, or one filed by a maintainer or an automation account, or it has no pull request.
Method: split the traced bugs by that, and set the main properties of the causing change side by side.
Answer in short: about one traced bug in ten was reported from outside. Their causing changes look the same as the
rest. They took longer to fix.

Usage: python3 questions/q28_does_it_matter_who_found_the_bug.py
"""
import csv
import os
import statistics

from common import DATASET, Result, load, load_commits, load_pull_requests, pct, traced, wilson

GROUPS = [("outside", "Reported from outside the project"), ("rest", "No outside report")]


def load_links():
    with open(os.path.join(DATASET, "pull_request_links.tsv")) as handle:
        return {row["number"]: row for row in csv.DictReader(handle, delimiter="\t")}


def main(quiet=False):
    commits, pulls, links = load_commits(), load_pull_requests(), load_links()
    fixes = load("sampled_fixes.jsonl")
    maintainers = {pull["merged_by"] for pull in pulls.values() if pull["merged_by"]}

    def group(fix):
        link = links.get(str(fix.get("fix_pr") or ""))
        if link and link["closes_issue"] and link["issue_author_kind"] == "person" and link["issue_author"] not in maintainers:
            return "outside"
        return "rest"

    def closes(fix):
        link = links.get(str(fix.get("fix_pr") or ""))
        return bool(link and link["closes_issue"])

    def by_most_active_or_automation(fix):
        pull = pulls.get(str(fix.get("fix_pr") or ""))
        return commits[fix["sha"]]["author_rank"] <= 2 or bool(pull and pull["author_kind"] == "automation")

    out = Result("q28")
    out.add("fixes", "fixes", "Sampled fixes", len(fixes))
    out.add("fixes", "fixes_close_issue", "Fixes whose pull request closes an issue", sum(closes(f) for f in fixes))
    out.add("fixes", "fixes_close_issue_pct", "Share of sampled fixes that close an issue", pct(sum(closes(f) for f in fixes), len(fixes)))
    out.add("fixes", "fixes_outside", "Fixes that close an issue reported from outside", sum(group(f) == "outside" for f in fixes))
    busy = [f for f in fixes if by_most_active_or_automation(f)]
    out.add("fixes", "fixes_busy", "Fixes landed by the two most active accounts or opened by automation", len(busy))
    out.add("fixes", "fixes_busy_pct", "Their share of sampled fixes", pct(len(busy), len(fixes)))
    out.add("fixes", "fixes_busy_outside_pct", "Share of those that close an issue reported from outside",
            pct(sum(group(f) == "outside" for f in busy), len(busy)))
    others = [f for f in fixes if not by_most_active_or_automation(f)]
    out.add("fixes", "fixes_others_outside_pct", "Share of everyone else's fixes that close an issue reported from outside",
            pct(sum(group(f) == "outside" for f in others), len(others)))

    bugs = traced(fixes)
    out.add("traced", "traced", "Traced bugs", len(bugs))
    for key, label in GROUPS:
        mine = [f for f in bugs if group(f) == key]
        recent = [f for f in mine if f["cause_sha"] in commits]
        cause = lambda f: commits[f["cause_sha"]]
        out.add("bugs", "bugs_" + key, label, len(mine))
        out.add("bugs_pct", "bugs_pct_" + key, label, pct(len(mine), len(bugs)))
        out.add("recent", "recent_" + key, label, len(recent))
        for name, count, of in (("feat_pct", sum(cause(f)["title_prefix"] == "feat" for f in recent), len(recent)),
                                ("new_pct", sum(cause(f)["new_code_files"] > 0 for f in recent), len(recent)),
                                ("large_pct", sum(cause(f)["files_changed"] > 30 for f in recent), len(recent)),
                                ("never_pct", sum(f["origin"] == "never-worked" for f in mine), len(mine))):
            out.add(name, f"{name}_{key}", label, pct(count, of), *wilson(count, of))
        out.add("days", "days_" + key, label, round(statistics.median(f["cause"]["days_to_fix"] for f in mine), 1))
        out.add("days_recent", "days_recent_" + key, label, round(statistics.median(f["cause"]["days_to_fix"] for f in recent), 1))
    everything = list(commits.values())
    out.add("feat_pct", "feat_pct_all", "All commits, for comparison", round(100 * sum(c["title_prefix"] == "feat" for c in everything) / len(everything), 1))
    out.add("new_pct", "new_pct_all", "All commits, for comparison", round(100 * sum(c["new_code_files"] > 0 for c in everything) / len(everything), 1))
    out.add("large_pct", "large_pct_all", "All commits, for comparison", round(100 * sum(c["files_changed"] > 30 for c in everything) / len(everything), 1))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
