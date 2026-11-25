#!/usr/bin/env python3
"""Build the five data files behind the results page from the studies' own output files.

Every file is a JSON array of rows: group, metric (unique), label, value, low, high. One row per number on the page.
Nothing is typed in by hand except the figures of the first, wording-based study, which exist only in its written
report (research/detection-check/report.md); every other value is computed here from the per-case files.

Usage (from the repo root): python3 research/fix-origins/dashboard/build_data.py
"""
import collections
import json
import math
import os
import statistics
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RECENT = "2026-09-10"  # causes from here on can be read in full in the local clone
POPULATION = 3996


def rows_of(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    with open(full) as handle:
        return [json.loads(line) for line in handle]


def wilson(k, n, z=1.96):
    """95% interval for a proportion, as whole percentages."""
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) + z * z / (4 * n)) / n) ** 0.5
    return round(100 * (c - h) / d), round(100 * (c + h) / d)


def sign_test(first_only, second_only):
    """Two-sided exact test on paired yes/no results (McNemar's exact test)."""
    n = first_only + second_only
    if n == 0:
        return 1.0
    k = min(first_only, second_only)
    return round(min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n), 3)


def pct(k, n):
    return round(100 * k / n) if n else 0


def write(name, rows):
    seen = set()
    records = []
    for group, metric, label, value, *rest in rows:
        assert metric not in seen, metric
        seen.add(metric)
        low, high = (rest + [None, None])[:2]
        records.append({"group": group, "metric": metric, "label": label, "value": value, "low": low, "high": high})
    with open(os.path.join(HERE, name), "w") as handle:
        handle.write("[\n" + ",\n".join(json.dumps(record) for record in records) + "\n]\n")
    print(name, len(rows))


def fix_origins():
    cases = rows_of("cases.jsonl")
    base = json.load(open(os.path.join(ROOT, "audit", "base-rates.json")))
    n = len(cases)
    count = collections.Counter(case["origin"] for case in cases)
    labels = {
        "never-worked": "New code that never worked",
        "not-a-defect": "Not a bug: redesign, speed-up, wording or tooling",
        "regression": "A working thing that a later change broke",
        "latent": "Old code that broke because something outside changed",
        "unclear": "Could not tell",
    }
    rows = [["size", "sample", "Fixes sampled at random", n],
            ["size", "population", "Changes titled fix that touch product code, 1 to 22 Nov 2026", POPULATION]]
    for origin in ("never-worked", "not-a-defect", "regression", "latent", "unclear"):
        low, high = wilson(count[origin], n)
        rows.append(["origin", "origin_" + origin, labels[origin], count[origin], low, high])
    real = count["never-worked"] + count["regression"] + count["latent"]
    traced = [c for c in cases if c.get("cause_sha")]
    never = [c for c in traced if c["origin"] == "never-worked"]
    broke = [c for c in traced if c["origin"] == "regression"]
    rows += [["size", "real_bugs", "Sampled fixes that repaired a real bug", real],
             ["size", "traced", "Bugs traced to the change that introduced them", len(traced)],
             ["size", "not_bug_pct", "Share of sampled fixes that fixed no bug", pct(count["not-a-defect"], n),
              *wilson(count["not-a-defect"], n)]]

    # How the never-worked / broken-later balance moves under stricter readings.
    cuts = [
        ("all", "Every traced bug", lambda c: True),
        ("hm", "Reader was confident or fairly confident of the cause", lambda c: c["confidence"] in ("high", "medium")),
        ("high", "Reader was confident of the cause", lambda c: c["confidence"] == "high"),
        ("recent", "Cause recent enough to read in full", lambda c: c["cause"]["date"] >= RECENT),
    ]
    ratios = []
    for key, label, keep in cuts:
        a, b = sum(keep(c) for c in never), sum(keep(c) for c in broke)
        rows.append(["sens_never", "sens_never_" + key, label, a])
        rows.append(["sens_broke", "sens_broke_" + key, label, b])
        ratios.append(a / b)
    rows += [["size", "ratio_low", "Lowest ratio of never-worked to broken-later", round(min(ratios), 2)],
             ["size", "ratio_high", "Highest ratio of never-worked to broken-later", round(max(ratios), 2)]]

    # What the change that introduced the bug was titled.
    def title(case):
        prefix = case["cause"]["prefix"]
        return prefix if prefix in ("fix", "feat") else "other"
    names = {"fix": "Titled fix", "feat": "Titled feat (a new feature)", "other": "Another title"}
    for key in ("fix", "feat", "other"):
        rows.append(["title", "title_" + key, names[key], sum(title(c) == key for c in traced)])
        rows.append(["title_never", "title_never_" + key, names[key], sum(title(c) == key for c in never)])
        rows.append(["title_broke", "title_broke_" + key, names[key], sum(title(c) == key for c in broke)])

    # Causing changes against ordinary commits, both taken from the same period.
    recent = [c for c in traced if c["cause"]["date"] >= RECENT]
    size = [c["cause"]["files_changed"] for c in recent]
    compare = [
        ("feat", "Titled feat", pct(sum(title(c) == "feat" for c in recent), len(recent)), base["pct_feat"]),
        ("fix", "Titled fix", pct(sum(title(c) == "fix" for c in recent), len(recent)), base["pct_fix"]),
        ("over30", "Changed more than 30 files", pct(sum(s > 30 for s in size), len(size)), base["pct_over_30_files"]),
        ("over100", "Changed more than 100 files", pct(sum(s > 100 for s in size), len(size)), base["pct_over_100_files"]),
    ]
    for key, label, cause_value, base_value in compare:
        rows.append(["cmp_cause", "cmp_cause_" + key, label, cause_value])
        rows.append(["cmp_base", "cmp_base_" + key, label, base_value])
    rows += [["size", "recent_causes", "Causing changes since 10 Sep 2026", len(recent)],
             ["size", "base_commits", "All commits on main since 10 Sep 2026", base["commits"]],
             ["size", "cause_median_files", "Median files changed by a causing change", statistics.median(size)],
             ["size", "base_median_files", "Median files changed by any commit", int(base["median_files"])]]

    # How long the bugs lived.
    days = [c["cause"]["days_to_fix"] for c in broke]
    for metric, label, test in (
        ("age_day", "Under a day", lambda d: d < 1), ("age_week", "1 to 7 days", lambda d: 1 <= d < 7),
        ("age_month", "7 to 30 days", lambda d: 7 <= d < 30), ("age_more", "Over 30 days", lambda d: d >= 30),
    ):
        rows.append(["age", metric, label, sum(test(d) for d in days)])
    named = [c["cause"]["days_to_fix"] for c in broke if c["fix_names_cause"]]
    unnamed = [c["cause"]["days_to_fix"] for c in broke if not c["fix_names_cause"]]
    low, high = wilson(len(broke), n)
    rows += [
        ["lifetime", "median_broke", "Working things broken later, all", round(statistics.median(days), 1)],
        ["lifetime", "median_named", "Broken later, fix says what caused it", round(statistics.median(named), 1)],
        ["lifetime", "median_unnamed", "Broken later, fix does not say", round(statistics.median(unnamed), 1)],
        ["lifetime", "median_never", "New code that never worked",
         round(statistics.median(c["cause"]["days_to_fix"] for c in never), 1)],
        ["size", "named_count", "Broken-later fixes that say what caused the bug", len(named)],
        ["size", "broke_count", "Broken-later bugs in the sample", len(broke)],
        ["size", "broke_scaled", "Broken-later bugs fixed in the three weeks, scaled from the sample",
         int(round(len(broke) / n * POPULATION, -1)), int(round(low / 100 * POPULATION, -1)),
         int(round(high / 100 * POPULATION, -1))],
        ["size", "adds_test", "Sampled fixes that add or change a test", sum(bool(c["fix_adds_test"]) for c in cases)],
    ]

    # Agreement: a second Claude reader on 47, and a GPT reader on 60.
    by_sha = {c["sha"]: c for c in cases}
    second = [(by_sha[s["sha"]]["origin"], s["origin"]) for s in rows_of("second_reads.jsonl")]
    real_set = {"regression", "never-worked", "latent"}
    pair = [(a, b) for a, b in second if {a, b} <= {"regression", "never-worked"}]
    rows += [
        ["size", "second_n", "Fixes read by a second reader", len(second)],
        ["size", "second_same", "Second reader chose the same category", sum(a == b for a, b in second)],
        ["size", "second_real_same", "Second reader agreed on bug or not a bug",
         sum((a in real_set) == (b in real_set) for a, b in second)],
        ["size", "second_pair_n", "Both readers said never-worked or broken-later", len(pair)],
        ["size", "second_pair_same", "Of those, same choice", sum(a == b for a, b in pair)],
    ]
    reread = rows_of("audit/origin-second-reads.jsonl")
    gpt = [(r["first_origin"], r["second_origin"]) for r in reread]
    if gpt:
        both_cause = [r for r in reread if r["first_cause"] and r["second_cause"]]
        k = sum(b == "not-a-defect" for a, b in gpt)
        rows += [
            ["size", "gpt_cause_n", "Fixes where both readers named a causing change", len(both_cause)],
            ["size", "gpt_cause_same", "Of those, the same change",
             sum(r["first_cause"][:10] == r["second_cause"][:10] for r in both_cause)],
            ["size", "gpt_notbug_pct", "Share the GPT reader called not a bug", pct(k, len(gpt)), *wilson(k, len(gpt))],
        ]
        # The same balance on the re-read fixes, by each reader.
        rows += [
            ["sens_never", "sens_never_first60", "First readers, on the fixes that were re-read",
             sum(a == "never-worked" for a, b in gpt)],
            ["sens_broke", "sens_broke_first60", "First readers, on the fixes that were re-read",
             sum(a == "regression" for a, b in gpt)],
            ["sens_never", "sens_never_gpt60", "Second model, on the same fixes", sum(b == "never-worked" for a, b in gpt)],
            ["sens_broke", "sens_broke_gpt60", "Second model, on the same fixes", sum(b == "regression" for a, b in gpt)],
            ["size", "gpt_ratio", "Never-worked to broken-later, by the second model",
             round(sum(b == "never-worked" for a, b in gpt) / max(1, sum(b == "regression" for a, b in gpt)), 2)],
        ]
        pair = [(a, b) for a, b in gpt if {a, b} <= {"regression", "never-worked"}]
        decided = [(a, b) for a, b in gpt if "unclear" not in (a, b)]
        rows += [
            ["size", "gpt_n", "Fixes re-read by a GPT reader", len(gpt)],
            ["size", "gpt_same", "GPT reader chose the same category", sum(a == b for a, b in gpt)],
            ["size", "gpt_real_same", "GPT reader agreed on bug or not a bug",
             sum((a in real_set) == (b in real_set) for a, b in gpt)],
            ["size", "gpt_unclear", "GPT reader could not tell", sum(b == "unclear" for a, b in gpt)],
            ["size", "gpt_decided_n", "Fixes where neither reader said unclear", len(decided)],
            ["size", "gpt_decided_same", "Of those, same category", sum(a == b for a, b in decided)],
            ["size", "gpt_pair_n", "Both readers said never-worked or broken-later", len(pair)],
            ["size", "gpt_pair_same", "Of those, same choice", sum(a == b for a, b in pair)],
        ]
        for origin in ("never-worked", "regression", "not-a-defect", "latent", "unclear"):
            rows.append(["gpt_first", "gpt_first_" + origin, labels[origin], sum(a == origin for a, b in gpt)])
            rows.append(["gpt_second", "gpt_second_" + origin, labels[origin], sum(b == origin for a, b in gpt)])
    write("fix-origins-sample.json", rows)


def reviews():
    data = rows_of("clawsweeper/results.jsonl")
    status = collections.Counter(r["status"] for r in data)
    reviewed = [r for r in data if r["flagged"]]
    flags = collections.Counter(r["flagged"] for r in reviewed)
    stamp = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    gaps = [(stamp(r["merged_at"]) - stamp(r["review_time"])).total_seconds() / 60 for r in reviewed]
    against = [r for r in reviewed if r["verdict"] in ("blocked", "needs-changes")]
    rows = [
        ["size", "traced", "Bugs traced to the change that introduced them", len(data)],
        ["size", "reviewed", "Causing changes the bot reviewed before merge", len(reviewed)],
        ["status", "status_head", "Reviewed the revision that merged", status["reviewed-merged-head"]],
        ["status", "status_earlier", "Reviewed only an earlier revision", status["reviewed-earlier-revision"]],
        ["status", "status_none", "A PR, but no review before merge", status["no-review-before-merge"]],
        ["status", "status_nopr", "No PR: committed straight to main", status["no-pr"]],
        ["flag", "flag_none", "Said nothing about this bug", flags["none"]],
        ["flag", "flag_related", "Raised a related concern, not this failure", flags["related"]],
        ["flag", "flag_exact", "Named this bug", flags["exact"]],
        ["size", "exact_pct", "Share where the bot named the bug", pct(flags["exact"], len(reviewed)),
         *wilson(flags["exact"], len(reviewed))],
        ["size", "any_pct", "Share where the bot named it or raised a related concern",
         pct(flags["exact"] + flags["related"], len(reviewed)),
         *wilson(flags["exact"] + flags["related"], len(reviewed))],
        ["size", "merged_against", "Merged while the bot said blocked or needs changes", len(against)],
        ["size", "merged_against_unrelated", "Of those, the open items were about something else",
         sum(r["flagged"] == "none" for r in against)],
        ["size", "open_unanswered", "Flags touching the bug that were open and unanswered at merge",
         sum(r["outcome"] == "open-at-merge" for r in reviewed)],
        ["size", "median_minutes", "Median minutes from the review in force to the merge", round(statistics.median(gaps))],
        ["size", "unreviewed_large", "Unreviewed cases from PRs of 500 files or more",
         sum(r["status"] == "no-review-before-merge" and (r.get("changed_files") or 0) >= 500 for r in data)],
    ]
    names = {"blocked": "Blocked", "needs-changes": "Needs changes", "needs-maintainer": "Needs maintainer review",
             "ready": "Ready"}
    for verdict, label in names.items():
        rows.append(["verdict", "verdict_" + verdict, label, sum(r["verdict"] == verdict for r in reviewed)])
    gpt = rows_of("audit/flag-second-reads.jsonl")
    if gpt:
        rows += [
            ["size", "gpt_n", "Reviews re-read by a GPT reader", len(gpt)],
            ["size", "gpt_same", "Same answer from the GPT reader", sum(r["first"] == r["second"] for r in gpt)],
            ["size", "gpt_exact_same", "Same answer on whether the bot named the bug",
             sum((r["first"] == "exact") == (r["second"] == "exact") for r in gpt)],
        ]
        for level, label in (("none", "Said nothing about this bug"),
                             ("related", "Raised a related concern, not this failure"), ("exact", "Named this bug")):
            rows.append(["gpt_flag", "gpt_flag_" + level, label, sum(r["second"] == level for r in gpt)])
    write("clawsweeper-reviews.json", rows)


def pilot():
    data = rows_of("review-pilot/results.jsonl")
    n = len(data)
    arms = [
        ("gpt-5.6-sol__whole", "gpt-5.6-sol", "gpt56"), ("gpt-6-astra__whole", "gpt-6-astra", "gpt6"),
        ("gpt-6.1-sol__whole", "gpt-6.1-sol (the model the bot's README names)", "gpt61"),
        ("gpt-6.2-sol__whole", "gpt-6.2-sol", "gpt62"), ("claude-opus-5-5__whole", "Claude Opus 5.5", "opus"),
        ("gpt-6.1-sol__per-file", "gpt-6.1-sol, three files at a time", "gpt61pf"),
    ]
    hit = lambda r, arm: r["arms"][arm]["flagged"] == "exact"
    bot = lambda r: r["clawsweeper_actual"] == "exact"
    rows = [["size", "cases", "Bug-causing changes reviewed blind", n]]
    second = collections.defaultdict(int)
    for r in rows_of("audit/grade-second-reads.jsonl"):
        second[r["arm"]] += r["second"] == "exact"
    grade = rows_of("audit/grade-second-reads.jsonl")
    for arm, label, slug in arms:
        k = sum(hit(r, arm) for r in data)
        rows.append(["named", "named_" + slug, label, k, *wilson(k, n)])
        rows.append(["findings", "findings_" + slug, label, sum(r["arms"][arm]["findings"] for r in data)])
        if grade:
            rows.append(["named_second", "named_second_" + slug, label, second[arm]])
    k = sum(bot(r) for r in data)
    rows.append(["named", "named_bot", "The review bot's actual reviews at the time", k, *wilson(k, n)])
    top = ("gpt-6.2-sol__whole", "claude-opus-5-5__whole")
    either = lambda r: any(hit(r, a) for a in top)
    k = sum(either(r) for r in data)
    rows += [["size", "named_either_top", "Named by gpt-6.2 or Opus 5.5", k, *wilson(k, n)],
             ["size", "named_both_top", "Named by both", sum(all(hit(r, a) for a in top) for r in data)]]

    def paired(first, second_fn):
        return sign_test(sum(first(r) and not second_fn(r) for r in data), sum(second_fn(r) and not first(r) for r in data))
    rows += [
        ["size", "p_one_vs_bot", "Chance of a gap this large by luck: one top model against the bot",
         paired(lambda r: hit(r, top[0]), bot)],
        ["size", "p_two_vs_bot", "Chance by luck: the two top models together against the bot", paired(either, bot)],
        ["size", "p_top_vs_gpt61", "Chance by luck: a top model against gpt-6.1 on the same prompt",
         paired(lambda r: hit(r, top[0]), lambda r: hit(r, "gpt-6.1-sol__whole"))],
        ["size", "p_perfile", "Chance by luck: three files at a time against the whole change",
         paired(lambda r: hit(r, "gpt-6.1-sol__per-file"), lambda r: hit(r, "gpt-6.1-sol__whole"))],
    ]
    caught = lambda r: any(v["flagged"] == "exact" for v in r["arms"].values())
    for needs, label in (("diff", "The changed lines alone"), ("repo", "Other code in the repository"),
                         ("outside", "Knowledge from outside the repository")):
        mine = [r for r in data if r["needs"] == needs]
        rows.append(["needs_cases", "needs_" + needs, label, len(mine)])
        rows.append(["needs_named", "needs_named_" + needs, label, sum(caught(r) for r in mine)])
    small = [r for r in data if r["files_changed"] <= 7]
    large = [r for r in data if r["files_changed"] > 7]
    hits = [r for r in data if caught(r)]
    rows += [
        ["size", "small_cases", "Changes of 7 files or fewer", len(small)],
        ["size", "small_named", "Of those, bug named by a reviewer", sum(caught(r) for r in small)],
        ["size", "large_cases", "Changes of more than 7 files", len(large)],
        ["size", "large_named", "Of those, bug named by a reviewer", sum(caught(r) for r in large)],
        ["size", "named_any", "Bugs named by at least one reviewer", len(hits)],
        ["size", "named_any_old", "Of those, live more than 10 days before the fix",
         sum(r["days_to_fix"] > 10 for r in hits)],
    ]
    if grade:
        rows += [
            ["size", "grade_cells", "Reviewer and case pairs graded twice", len(grade)],
            ["size", "grade_same", "Second grader agreed on named or not",
             sum((r["first"] == "exact") == (r["second"] == "exact") for r in grade)],
        ]
    write("blind-review-pilot.json", rows)


def checks():
    data = rows_of("review-pilot/verify-results.jsonl")
    control = rows_of("review-pilot/verify-control.jsonl")
    known = lambda r: r["known_bug"] == "exact"
    both = lambda r: r["opus"] == "confirmed" and r["gpt"] == "confirmed"
    visible = lambda r: r["opus_impact"] == "user-visible" and r["gpt_impact"] == "user-visible"
    proven = lambda r: known(r) or r["later"] == "yes"
    rest = [r for r in data if not proven(r)]
    rows = [
        ["size", "findings", "Findings from gpt-6.2 and Opus 5.5", len(data)],
        ["size", "known", "Findings that are the known bug", sum(known(r) for r in data)],
        ["later", "later_yes", "Later fixed on main", sum(r["later"] == "yes" for r in data)],
        ["later", "later_partly", "Partly fixed later", sum(r["later"] == "partly" for r in data)],
        ["later", "later_no", "No later fix found", sum(r["later"] == "no" for r in data)],
        ["size", "later_other", "Later-fixed findings that are not the known bug",
         sum(r["later"] == "yes" and not known(r) for r in data)],
        ["quality", "q_proven", "Proven: the known bug, or fixed later on main", sum(proven(r) for r in data)],
        ["quality", "q_visible", "Both checkers: real, and a user would notice", sum(both(r) and visible(r) for r in rest)],
        ["quality", "q_minor", "Both checkers: real, but minor", sum(both(r) and not visible(r) for r in rest)],
        ["quality", "q_unconfirmed", "Refuted or unclear to at least one checker", sum(not both(r) for r in rest)],
        ["size", "both_confirmed", "Confirmed by both checkers", sum(both(r) for r in data)],
        ["size", "refuted_any", "Refuted by at least one checker",
         sum(r["opus"] == "refuted" or r["gpt"] == "refuted" for r in data)],
        ["size", "later_found_known", "Known-real findings for which the later-fix check found the fix",
         sum(known(r) and r["later"] == "yes" for r in data)],
    ]
    mine = [r for r in control if known(r)]
    for kind, label in (("gpt", "gpt-6.2 checker"), ("opus", "Opus 5.5 checker")):
        rows.append(["control_original", "dismissed_" + kind, label,
                     sum(r[kind + "_at_cause"] != "confirmed" for r in mine)])
        rows.append(["control_fixed", "flipped_" + kind, label, sum(r[kind + "_at_fix"] != "confirmed" for r in mine)])
    rows += [
        ["size", "control_cases", "Known-real findings used as the control", len(mine)],
        ["size", "control_both_still", "Still confirmed by both checkers after the fix",
         sum(r["gpt_at_fix"] == "confirmed" and r["opus_at_fix"] == "confirmed" for r in mine)],
    ]
    write("finding-checks.json", rows)


def named_cause():
    # From research/detection-check/report.md and severity.md; counts re-read against cases.md.
    write("named-cause-study.json", [
        ["size", "candidates", "Fix commits whose wording blames an earlier change", 355],
        ["size", "pairs", "Cause and fix pairs kept after reading", 41],
        ["size", "confirmed", "Confirmed bugs a user could hit", 29],
        ["size", "median_days", "Median days from cause to fix", 1.7],
        ["rules", "no_rule", "No written rule covered it", 24],
        ["rules", "rule_missed", "A rule the bot loads covered it, and review missed it", 3],
        ["rules", "rule_unloaded", "A rule covered it, in a guide the bot does not load", 1],
        ["rules", "rule_later", "No rule then; one was added afterwards", 1],
        ["size", "rules_checkable", "Existing rules that could be checked from the changed lines alone", 0],
        ["size", "rules_existing", "Cases where a rule existed when the change was written", 4],
    ])


if __name__ == "__main__":
    fix_origins()
    reviews()
    pilot()
    checks()
    named_cause()
