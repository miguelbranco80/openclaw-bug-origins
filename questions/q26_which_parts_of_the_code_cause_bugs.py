#!/usr/bin/env python3
"""Question 26. Do changes to some parts of the code cause more bugs than changes to others?

Reads: commits.tsv (the top-level folders each commit touched), sampled_fixes.jsonl.
Each commit is put in exactly one group, by the first rule that applies: it touches the interface (ui/ or apps/);
else plugins (extensions/); else the core (src/ or packages/); else only supporting files (docs, scripts, tests,
config).
Method: `compare_commits` in common.py.

Usage: python3 questions/q26_which_parts_of_the_code_cause_bugs.py
"""
from common import Result, compare_commits, load_commits, recent_causes

PARTS = [("core", "Core code (src/, packages/), no interface or plugins"), ("plugins", "Plugins (extensions/), no interface"),
         ("interface", "Interface (ui/ or apps/)"), ("support", "Only docs, scripts, tests or config")]


def part(commit):
    folders = commit["folders"]
    if folders & {"ui", "apps"}:
        return "interface"
    if "extensions" in folders:
        return "plugins"
    if folders & {"src", "packages"}:
        return "core"
    return "support"


def main(quiet=False):
    commits = load_commits()
    out = Result("q26")
    compare_commits(out, "part", commits, recent_causes(commits), part, PARTS, "core")
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
