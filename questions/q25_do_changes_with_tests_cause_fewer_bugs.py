#!/usr/bin/env python3
"""Question 25. Do code changes that also change tests cause fewer bugs?

Reads: commits.tsv (`code_files`: changed non-test files under src/, ui/, extensions/, packages/ or apps/;
`test_files`: changed files whose path marks them as tests), sampled_fixes.jsonl. Only commits that change code are
compared.
Method: `compare_commits` in common.py.

Usage: python3 questions/q25_do_changes_with_tests_cause_fewer_bugs.py
"""
from common import Result, compare_commits, load_commits, recent_causes

TESTS = [("with", "Changes code and tests together"), ("without", "Changes code and no test file")]


def level(commit):
    if commit["code_files"] == 0:
        return None
    return "with" if commit["test_files"] > 0 else "without"


def main(quiet=False):
    commits = load_commits()
    causes = recent_causes(commits)
    out = Result("q25")
    compare_commits(out, "tests", commits, causes, level, TESTS, "with")
    out.add("size", "bugs", "Sampled bugs whose causing commit is in the list", len(causes))
    out.save(quiet)
    return out


if __name__ == "__main__":
    main()
