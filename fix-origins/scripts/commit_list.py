#!/usr/bin/env python3
"""List every commit on main since 2026-09-10 (UTC) with the facts the questions need: dataset/commits.tsv.

Run from the root of an openclaw/openclaw clone, with this repository checked out as `research/`.

Columns:
  sha, committed_at
  files_changed          files in the commit's diff against its first parent
  pr_number              the number in a trailing "(#123)" in the title; empty when there is none
  title_prefix           leading word of the title, lower case (fix, feat, refactor, ...)
  author_commits_that_day    commits on main by the same author on the same UTC day, this one included
  minutes_since_author_previous   minutes since that author's previous commit on main; empty for their first
  folders                top-level folders the commit touched, comma separated
  test_files             changed files whose path marks them as tests
  code_files             changed non-test files under src/, ui/, extensions/, packages/ or apps/
  author_rank            1 for the author with the most commits in the list, 2 for the next, and so on
  new_code_files         of code_files, how many the commit adds
  edited_code_files      of code_files, how many already existed and the commit edits
  familiar_code_files    of edited_code_files, how many the same author had already added or edited in an earlier
                         commit in the list
  other_recent_authors   how many other authors added or edited any of the edited code files in the 14 days before
  other_recent_authors_per_file   the same count taken for each edited code file on its own, then averaged

Authors are told apart by the commit's author email, which is used only to count and rank and is not written out.

Usage: python3 research/fix-origins/scripts/commit_list.py
"""
import collections
import os
import re
import subprocess
from datetime import datetime, timezone

TIP = "e6b42e31bc1522b8596958fbdd85c394b23fca7b"
SINCE = "2026-09-10T00:00:00Z"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "dataset", "commits.tsv")
TEST = re.compile(r"(\.test\.|\.spec\.|\.e2e\.|/__tests__/|/test/|/tests/|^test/|test-support|/fixtures/)")
CODE = ("src/", "ui/", "extensions/", "packages/", "apps/")


def main():
    log = subprocess.run(
        ["git", "log", "--first-parent", f"--since={SINCE}", "--no-renames", "--format=COMMIT %H %cI %ae %s",
         "--name-status", TIP],
        capture_output=True, text=True, check=True, env=dict(os.environ, GIT_NO_LAZY_FETCH="1"),
    ).stdout
    rows = []
    for line in log.splitlines():
        if line.startswith("COMMIT "):
            _, sha, date, author, subject = (line.split(" ", 4) + [""])[:5]
            prefix = re.match(r"([a-zA-Z]+)", subject)
            number = re.search(r"\(#(\d+)\)\s*$", subject)
            rows.append({"sha": sha, "committed_at": date, "author": author.lower(), "files": 0,
                         "pr": number.group(1) if number else "", "prefix": prefix.group(1).lower() if prefix else "other",
                         "folders": set(), "tests": 0, "code": [], "new": 0, "edited": []})
        elif line:
            status, line = line.split("\t", 1)
            row = rows[-1]
            row["files"] += 1
            row["folders"].add(line.split("/")[0] if "/" in line else "(root)")
            if TEST.search(line):
                row["tests"] += 1
            elif line.startswith(CODE):
                row["code"].append(line)
                if status == "A":
                    row["new"] += 1
                elif status == "M":
                    row["edited"].append(line)
    stamp = lambda row: datetime.fromisoformat(row["committed_at"]).astimezone(timezone.utc)
    per_day = collections.Counter((row["author"], stamp(row).date()) for row in rows)
    totals = collections.Counter(row["author"] for row in rows)
    rank = {author: place for place, (author, _) in enumerate(totals.most_common(), 1)}
    previous = {}
    gaps = {}
    touched = collections.defaultdict(set)
    recent = collections.defaultdict(dict)  # file -> author -> when they last changed it
    for row in reversed(rows):  # git lists newest first; walk main oldest first
        when = stamp(row)
        if row["author"] in previous:
            gaps[row["sha"]] = round((when - previous[row["author"]]).total_seconds() / 60, 1)
        previous[row["author"]] = when
        row["familiar"] = sum(path in touched[row["author"]] for path in row["edited"])
        row["others"] = len({author for path in row["edited"] for author, last in recent[path].items()
                             if author != row["author"] and (when - last).days < 14})
        each = [sum(author != row["author"] and (when - last).days < 14 for author, last in recent[path].items())
                for path in row["edited"]]
        row["others_per_file"] = round(sum(each) / len(each), 1) if each else ""
        touched[row["author"]].update(row["code"])
        for path in row["code"]:
            recent[path][row["author"]] = when
    with open(OUT, "w") as handle:
        handle.write("sha\tcommitted_at\tfiles_changed\tpr_number\ttitle_prefix\tauthor_commits_that_day\t"
                     "minutes_since_author_previous\tfolders\ttest_files\tcode_files\tauthor_rank\tnew_code_files\t"
                     "edited_code_files\tfamiliar_code_files\tother_recent_authors\t"
                     "other_recent_authors_per_file\n")
        for row in rows:
            handle.write("\t".join(map(str, [
                row["sha"], row["committed_at"], row["files"], row["pr"], row["prefix"],
                per_day[(row["author"], stamp(row).date())], gaps.get(row["sha"], ""),
                ",".join(sorted(row["folders"])), row["tests"], len(row["code"]), rank[row["author"]],
                row["new"], len(row["edited"]), row["familiar"], row["others"],
                row["others_per_file"]])) + "\n")
    print(len(rows), "commits,", len({row["author"] for row in rows}), "distinct authors")


if __name__ == "__main__":
    main()
