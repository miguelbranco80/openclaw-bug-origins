#!/usr/bin/env python3
"""Render README.md, the report, from the question scripts' results and charts.

Every number in the text is looked up in results/<question>.json, so the words cannot drift from the data.
Run the question scripts first (python3 questions/run_all.py).

Usage: python3 report/render.py
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = {}
CHARTS = {}
for path in sorted(glob.glob(os.path.join(ROOT, "results", "q*.json"))):
    name = os.path.basename(path)
    if name.endswith(".charts.json"):
        CHARTS[name[:3]] = json.load(open(path))
    else:
        RESULTS[name[:3]] = json.load(open(path))
SCRIPTS = {os.path.basename(p)[:3]: "questions/" + os.path.basename(p)
           for p in glob.glob(os.path.join(ROOT, "questions", "q*.py"))}


def v(question, metric):
    value = next(r for r in RESULTS[question] if r["metric"] == metric)["value"]
    return f"{value:,}" if isinstance(value, int) else str(value)


def span(question, metric):
    row = next(r for r in RESULTS[question] if r["metric"] == metric)
    return f"{row['low']} to {row['high']}"


def chart(question, number=0):
    drawn = CHARTS[question][number]
    return (f"**{drawn['title']}**\n\n"
            f"![{drawn['title']}](charts/{drawn['stem']}-light.svg#gh-light-mode-only)\n"
            f"![{drawn['title']}](charts/{drawn['stem']}-dark.svg#gh-dark-mode-only)\n\n"
            f"*How to read it: {drawn['reading']}*")


def ratio_table(question, prefix):
    """One row per kind of change: how common it is, the bugs it produced, its bug rate, and the rate relative to
    the first row with the size of the change held equal."""
    rows = {r["metric"]: r for r in RESULTS[question]}
    keys = [m[len(prefix) + 7:] for m in rows if m.startswith(prefix + "_share_")]
    lines = ["| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |",
             "|---|---:|---:|---:|---|"]
    for i, key in enumerate(keys):
        adjusted = rows.get(f"{prefix}_adjusted_{key}")
        if i == 0:
            versus = "(the baseline)"
        elif adjusted:
            versus = f"{adjusted['value']} times (plausibly {adjusted['low']} to {adjusted['high']})"
        else:
            versus = "too few to say"
        lines.append(f"| {rows[f'{prefix}_share_{key}']['label']} | {rows[f'{prefix}_share_{key}']['value']}% | "
                     f"{rows[f'{prefix}_bugs_{key}']['value']} | {rows[f'{prefix}_rate_{key}']['value']} | {versus} |")
    return "\n".join(lines)


def commit_table(*parts):
    """Like ratio_table, for comparisons made over every commit on main. Each part is (question, prefix); a part's
    first row is its baseline. A part may carry a third item, a caption printed above its rows."""
    lines = ["| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size and kind |",
             "|---|---:|---:|---:|---|"]
    for question, prefix, *caption in parts:
        rows = {r["metric"]: r for r in RESULTS[question]}
        keys = [m[len(prefix) + 7:] for m in rows if m.startswith(prefix + "_share_")]
        if caption:
            lines.append(f"| ***{caption[0]}*** | | | | |")
        for i, key in enumerate(keys):
            adjusted = rows.get(f"{prefix}_adjusted_{key}")
            if i == 0:
                versus = "(the baseline)"
            elif adjusted:
                clear = adjusted["low"] > 1 or adjusted["high"] < 1
                versus = f"{adjusted['value']} times (plausibly {adjusted['low']} to {adjusted['high']})"
                versus = f"**{versus}**" if clear else versus + ": no clear difference"
            else:
                versus = "too few to say"
            lines.append(f"| {rows[f'{prefix}_share_{key}']['label']} | {rows[f'{prefix}_share_{key}']['value']}% | "
                         f"{rows[f'{prefix}_bugs_{key}']['value']} | {rows[f'{prefix}_rate_{key}']['value']} | {versus} |")
    return "\n".join(lines)


def numbers(question, *groups, names=None):
    """A folded table of the numbers behind a chart: one row per label, one column per group."""
    rows = {}
    for group in groups:
        for r in RESULTS[question]:
            if r["group"] == group:
                rows.setdefault(r["label"], {})[group] = r
    heads = names or ["Count"] * len(groups)
    with_range = any(r.get(groups[0]) and r[groups[0]]["low"] is not None for r in rows.values()) and len(groups) == 1
    lines = ["<details><summary>The numbers behind this chart</summary>", "",
             "| | " + " | ".join(heads) + (" | Plausible range |" if with_range else " |"),
             "|---|" + "---:|" * (len(heads) + (1 if with_range else 0))]
    for label, cells in rows.items():
        line = f"| {label} | " + " | ".join(str(cells[g]["value"]) if g in cells else "–" for g in groups) + " |"
        if with_range:
            r = cells[groups[0]]
            line += f" {r['low']}–{r['high']}% |"
        lines.append(line)
    lines += ["", "</details>"]
    return "\n".join(lines)


def run_line(question):
    return f"Recompute: `python3 {SCRIPTS[question]}`"


def report():
    return f"""# Where OpenClaw's bugs come from

An independent study of the public [openclaw/openclaw](https://github.com/openclaw/openclaw) repository. It is not
affiliated with or endorsed by the OpenClaw project. It judges changes, not people.

We traced a random sample of {v('q01', 'sample')} fixes from three weeks back to what each one repaired. By the first
readers' count, {v('q01', 'origin_never-worked')} were new code that never worked and {v('q01', 'origin_regression')}
were working things broken by a later change; a second model put the two kinds closer to even. The project's review
bot had named the bug in {v('q06', 'flag_exact')} of the {v('q06', 'reviewed')} bug-causing changes it reviewed. Two
current models, shown {v('q07', 'cases')} of those changes with no hint, each named {v('q07', 'named_gpt62')}.

**Scope.** Changes merged to `main` from 1 to 22 November 2026. Model readers did the classifying; a second model
from a different maker re-read the three central judgments. No project code was run and no test was written.
Findings 18 to 22 set the traced bugs against every commit on `main` since 10 September 2026 and judge nothing.
Written 25 November 2026.

**How this repository is organised.** `dataset/` holds the facts. `questions/` holds one script per question; each
reads only the dataset and writes the numbers and charts used below. `python3 study.py rebuild` runs them all and
re-renders this page. [PROTOCOL.md](PROTOCOL.md) is the experimental setup: every step of the study, and how to
regenerate it from nothing or extend it to other dates with one command and one settings file.
Claims that an earlier draft made and a later check weakened are listed in [CORRECTIONS.md](CORRECTIONS.md).

## What the evidence supports, and how strongly

| # | Strength | Finding |
|---|---|---|
| 1 | Depends on definition | Between about a tenth and a third of changes titled "fix" repair no bug. Two models drew the line differently. |
| 2 | Supported | New code that never worked accounts for at least as many bugs as working things broken later: from about even ({v('q02', 'gpt_ratio')} to one, by a second model) to about double ({v('q02', 'ratio_high')} to one, by the first readers). When both models trace a bug to a cause, they name the same change. |
| 3 | Well supported | Changes titled as new features cause far more than their share of bugs. The title "fix" tells you little. |
| 4 | Well supported | Large changes cause far more bugs per change, but about the same per file changed. |
| 5 | Well supported | A broken thing typically stayed broken for about three weeks, unless someone traced the cause at once. |
| 6 | Well supported | The review bot had rarely named the bug before the change merged. |
| 7 | Supported | Two current models together named more of the known bugs than the bot had. For either model alone, the gap could still be chance. |
| 8 | Supported | Most of the other problems those models reported hold up when checked, and about a third of them are minor. |
| 9 | Tentative | About a third of the bugs could not be seen by reading code at all. This rests on nine cases. |
| 10 | Tentative | Most bugs broke no written rule. |
| 11 | Tentative | Changes committed straight to main, without a pull request, show no sign of causing more bugs. |
| 12 | Supported | Changes merged while the bot objected carried {v('q12', 'verdict_adjusted_objected')} times the bugs of changes it called ready, at equal size. Its objection marks risk even when its words do not name the bug. |
| 13 | Tentative | Merging minutes after the bot's review, or after it saw only an earlier revision, shows no clear extra risk once size is held equal. |
| 14 | Supported | Who opened a change, and whether its author merged it, made no detectable difference. Pull requests open a day or more carried far more bugs than those merged within the hour. |
| 15 | Measured | {v('q15', 'self_merged_pct')}% of pull requests were merged by their own author. Another person reviewed {v('q15', 'all_second_review_pct')}% of them before the merge. |
| 16 | Supported | Attaching a screenshot or video did not go with fewer bugs. Among interface changes, those with one caused {v('q16', 'interface_adjusted_yes')} times as many, at equal size. |
| 17 | Supported, not yet tested on new data | Bugs are concentrated. Changes with at least two of three warning signs are {v('q17', 'changes_pct_two')}% of changes and the source of {v('q17', 'bugs_pct_two')}% of traced bugs. |
| 18 | Supported as "no sign found" | No sign that anyone is overloaded. Changes landed on an author's heavy days, on a merger's heavy days, on the project's busiest days, at weekends, or minutes after the previous one caused no more bugs than the rest. |
| 19 | Tentative | Changes from people who contribute rarely caused no more bugs than the most active author's. Too few changes get a second person to tell whether one helps. |
| 20 | Supported | Changes to files that other people were also editing caused {v('q23', 'shared_adjusted_mid')} times the bugs of changes to files only their author was editing, at equal size and kind. |
| 21 | Well supported | Changes that add new code files are {v('q24', 'new_share_adds')}% of commits and the source of {v('q24', 'bugs_pct_adds')}% of the traced bugs. |
| 22 | Measured | {v('q25', 'tests_bugs_with')} of the {v('q25', 'bugs')} traced bugs came from a change that also changed tests. No part of the code stands out once size is held equal. |

## Words used in this report

- **Fix.** A change whose title starts with "fix" and that touches product code. The title is the author's label,
  not a judgment that something was broken.
- **Causing change.** The earlier change that introduced the bug a fix later repaired. Every bug here has two
  changes: the one that introduced it and the one that fixed it.
- **Never worked.** The faulty code was new, and it was wrong on the day it merged. Example: a new feature built a
  Docker command by joining strings, so it failed for any folder with a comma in its name.
- **Broken later.** Something worked, and a later change broke it. Engineers call this a regression. Example: a
  change capped a data stream at 16 MiB, and long replies that used to work began to fail.
- **Broken from outside.** Old code that was fine until something outside the project changed. Example: a package
  manager changed the format of its launcher files, and every command failed after an update.
- **Review bot.** ClawSweeper, the automated reviewer that comments on the project's pull requests before they merge.
- **Plausible range.** Where the true figure plausibly lies given the sample size (a 95% interval).

## 1. How many "fix" changes repair no bug depends on what you call a bug

*Depends on definition. The sample is random and the first readers were consistent with each other, but a second
model drew the line elsewhere.*

We drew {v('q01', 'sample')} fixes by lottery from the {v('q01', 'population')} merged in the period and asked of
each: what was broken, and how did it get that way? By the first readers' strict rule, nothing had been broken in
{v('q01', 'origin_not-a-defect')} of them: they were redesign steps, speed-ups, wording changes or tooling work that
carried the title "fix". A model from a different maker, given the same written rule, called only
{v('q01', 'gpt_notbug_pct')}% of the fixes it re-read "not a bug". The cases they dispute are improvements that can
also be described as a flaw present from the start: a slow path made faster, a log message made more precise, a
report that never fitted a phone screen.

{chart('q01', 0)}

{numbers('q01', 'origin')}

{chart('q01', 1)}

{numbers('q01', 'gpt_first', 'gpt_second', names=['First reader (Claude)', 'Second reader (GPT)'])}

- **How we know.** One model reader per fix worked from the fix's diff, its PR text and the history of the changed
  lines, with a written rubric that told it to answer "could not tell" when the evidence was thin.
- **How it was checked.** A second reader, blind to the first answer, re-read {v('q01', 'second_n')} fixes and agreed
  on bug or not a bug for {v('q01', 'second_real_same')}. A reader from a different model maker re-read
  {v('q01', 'gpt_n')} and agreed for only {v('q01', 'gpt_real_same')}. It answered "could not tell" for
  {v('q01', 'gpt_unclear')}, partly because it could not look up changes older than September 2026.
- **What it does not show.** A single right number. Treat the first readers' third as the upper end and the second
  model's share as the lower end. It also cannot show bugs nobody has fixed yet, or bugs fixed under another title.

{run_line('q01')}

## 2. New code that never worked accounts for at least as many bugs as working things broken later

*Supported. About double by the first readers' full count; closer to even under stricter cuts and under a second
model. Neither reading puts never-worked bugs clearly below.*

Of the {v('q02', 'traced')} bugs we could trace to the change that introduced them, {v('q02', 'sens_never_all')} were
new code that was wrong from the start and {v('q02', 'sens_broke_all')} were working things that a later change
broke. The two kinds need different defenses. A test of the old behavior can catch a broken-later bug. A
never-worked bug has no old behavior to test against, so the only chance to catch it is when the new code is
reviewed or first run.

{chart('q02', 0)}

{numbers('q02', 'sens_never', 'sens_broke', 'never_share', names=['Never worked', 'Broken later', 'Never worked, %'])}

The first readers found twice as many never-worked bugs as broken-later ones. Counting only the bugs where they were
sure of the cause, the two kinds are closer. A second model, re-reading 60 of the fixes, found them about even. So
the safe statement is "at least as many", not "twice as many".

- **How we know.** The reader had to point at the lines in the causing change that were wrong, and to say whether the
  behavior had worked before that change.
- **How it was checked.** Where two readers both chose one of these two kinds, they made the same choice in
  {v('q02', 'second_pair_same')} of {v('q02', 'second_pair_n')} cases. The reader from a different maker made the
  same choice in {v('q02', 'gpt_pair_same')} of {v('q02', 'gpt_pair_n')}, and named the same causing change in
  {v('q02', 'gpt_cause_same')} of {v('q02', 'gpt_cause_n')}.
- **What it does not show.** A firm ratio, or that features are the problem. New code arrives in changes of every
  title, as the next finding shows.

{run_line('q02')}

## 3. Changes titled as new features cause far more than their share of bugs

*Well supported. Measured against every commit on main in the same period, not against an estimate.*

For each traced bug we looked at the title of the change that introduced it, and divided by how many commits carry
that title. Changes titled "feat" caused {v('q03', 'rate_feat')} bugs per 100 commits, against {v('q03', 'rate_fix')}
for changes titled "fix" and {v('q03', 'rate_other')} for everything else.

{chart('q03', 0)}

{numbers('q03', 'rate_commits', 'rate_bugs', 'rate', 'rate_median_files', names=['Commits since 10 Sep', 'Sampled bugs', 'Bugs per 100 commits', 'Median files changed'])}

In absolute numbers most bugs still come from changes titled "fix" ({v('q03', 'title_fix')} of the
{v('q02', 'traced')} traced), because half of everything merged carries that title. And a title is a loose label:
one change titled as a fix touched 138 files and added a whole rollback mechanism. Feature changes are also larger
than others, so part of their higher rate is size, which is the next finding.

- **How we know.** The comparison uses the {v('q03', 'recent_causes')} sampled bugs whose causing change was made
  since 10 September 2026 and all {v('q03', 'base_commits')} commits on main since that date, counted from git.
- **How it was checked.** Titles and file counts are read mechanically from git, not judged. Which change caused
  each bug is the reader's judgment from finding 2.
- **What it does not show.** What the change was really for, or how much of the gap is size. The rates are not
  adjusted for the size of the change.

{run_line('q03')}

## 4. Large changes cause far more bugs per change, but about the same per file changed

*Well supported for the direction. The per-file figures rest on 10 to 45 bugs per size group.*

A causing change touched a median of {v('q03', 'cause_median_files')} files; an ordinary commit touches
{v('q03', 'base_median_files')}. Per change, a commit of over 100 files carried about
{v('q04', 'per_commit_ratio')} times the bugs of a commit of 1 to 5 files.

{chart('q04', 0)}

Per file changed, the picture is different: between {v('q04', 'per_file_low')} and {v('q04', 'per_file_high')} bugs
per 1,000 files changed in every size group, with no trend. On this evidence large changes hold more bugs because
they hold more change, not because each part of them is worse.

{chart('q04', 1)}

{numbers('q04', 'commits', 'bugs', 'per_commit', 'per_file', names=['Commits', 'Sampled bugs', 'Bugs per 100 commits', 'Bugs per 1,000 files changed'])}

- **How we know.** Every commit on main since 10 September 2026 is placed in a size group by files changed. A bug is
  one sampled fix traced to a causing commit in that list ({v('q04', 'bugs')} cases), scaled from the sample of 300 to
  all fixes in the period. So a rate reads as "bugs fixed in the three weeks, per 100 commits made since 10
  September".
- **How it was checked.** Sizes come from git. The causing commit is the reader's judgment; two makers' models named
  the same one in {v('q02', 'gpt_cause_same')} of {v('q02', 'gpt_cause_n')} cases.
- **What it does not show.** Risk per line, or whether splitting a large change would lower the total. It also
  counts only bugs fixed in the three weeks, so slow-to-surface bugs from recent changes are missing.

{run_line('q04')}

## 5. A broken thing typically stayed broken for about three weeks

*Well supported. Dates come from git. The split depends on the reader naming the right causing change.*

{chart('q05', 0)}

{chart('q05', 1)}

{numbers('q05', 'age')}

Only {v('q05', 'named_count')} of the {v('q05', 'broke_count')} broken-later fixes say which change caused the bug,
and those were fixed within a day. The rest took weeks. Scaled from the sample, about {v('q05', 'broke_scaled')}
broken-later bugs were fixed in the three weeks (plausibly {span('q05', 'broke_scaled')}).

- **How we know.** Days are the commit time of the fix minus the commit time of the causing change, both on main.
- **How it was checked.** An earlier study that could only find fixes naming their cause had put the typical time at
  {v('q05', 'first_study_median_days')} days. The random sample shows that figure described the quick cases only.
- **What it does not show.** How long users were affected, or how many noticed. A bug counts only once it is fixed,
  so long-lived bugs still open are missing and the true typical time is longer.

{run_line('q05')}

## 6. The review bot had rarely named the bug before the change merged

*Well supported. Every case read twice, by models from two makers, with close agreement.*

For each of the {v('q06', 'traced')} traced bugs we read what the bot had written on the causing change at the moment
it merged, rebuilt from the comment's edit history. It had reviewed {v('q06', 'reviewed')} of them and named the bug
in {v('q06', 'flag_exact')}. Both readers agree on those. They differ on how often it raised a related concern:
{v('q06', 'flag_related')} by the first reader, {v('q06', 'gpt_flag_related')} by the second.

{chart('q06', 0)}

{numbers('q06', 'flag', 'gpt_flag', names=['First reader (Claude)', 'Second reader (GPT)'])}

{chart('q06', 1)}

{chart('q06', 2)}

Warnings were not being ignored. {v('q06', 'merged_against')} changes merged while the bot said "blocked" or "needs
changes", but in {v('q06', 'merged_against_unrelated')} of them its open items were about something other than the
bug, such as missing proof. Only {v('q06', 'open_unanswered')} items that touched the bug were open and unanswered at
merge. The bot also said "ready" on changes that carried a bug. Finding 12 adds the other half: although its words
rarely named the bug, the changes it objected to were the riskier ones.

- **How we know.** A reader compared each bug with the review text under a strict rule: it counts as named only if
  fixing what the review described would have prevented the bug.
- **How it was checked.** A reader from a different maker re-read all {v('q06', 'gpt_n')} and gave the same answer
  for {v('q06', 'gpt_same')}. On whether the bug was named, they agreed for {v('q06', 'gpt_exact_same')}. Both
  "named" cases were also read by hand.
- **What it does not show.** How many bugs the bot stopped. A bug it caught and the author fixed before merge never
  appears in a sample of later fixes. This is a measure of what got past it, not of its worth.

{run_line('q06')}

## 7. Two current models together named more of the known bugs than the bot had

*Supported. Thirty smaller changes, one run each. Clear for the two models combined, not for either alone.*

We took {v('q07', 'cases')} bug-causing changes and gave each reviewer the repository exactly as it stood at merge,
with no later history, and one plain instruction: find the defects this change introduces. Graders who did not know
which reviewer wrote what then checked whether any reported problem was the known bug.

{chart('q07', 0)}

{numbers('q07', 'named', 'named_second', 'findings', names=['Named, first grader', 'Named, second grader', 'Problems reported'])}

gpt-6.2 and Opus 5.5 together named {v('q07', 'named_either_top')} bugs and overlapped on
{v('q07', 'named_both_top')}, so they catch different things. How likely is a gap this large by luck alone?

| Comparison | Chance of a gap this large by luck |
|---|---:|
| The two top models together, against the bot | {v('q07', 'p_two_vs_bot')} |
| One top model, against the bot | {v('q07', 'p_one_vs_bot')} |
| One top model, against gpt-6.1 on the same instruction | {v('q07', 'p_top_vs_gpt61')} |
| Three files at a time, against the whole change | {v('q07', 'p_perfile')} |

The count is not a steady climb across model versions, and it follows how much each model reports:

{chart('q07', 1)}

Of the {v('q07', 'named_any')} bugs that at least one reviewer named, {v('q07', 'named_any_old')} had been live for
more than ten days.

- **How we know.** Cases were the first 15 broken-later and first 15 never-worked bugs, in the sample's random order,
  among those the bot had reviewed, with a causing change of at most 30 files made since 10 September.
- **How it was checked.** A grader from a different maker regraded all {v('q07', 'grade_cells')} reviewer and case
  pairs and agreed on named or not for {v('q07', 'grade_same')}. Logs show no reviewer read later history, the fix,
  or another case. Two PR descriptions that had been edited after merge to mention the fix were replaced with their
  merge-time text.
- **What it does not show.** A like-for-like contest with the bot. The bot reviewed at the time, sometimes an earlier
  revision, with its own long instructions. It also does not cover changes of more than 30 files, which are where
  most bugs come from.

{run_line('q07')}

## 8. Most of the other problems those models reported hold up when checked

*Supported. A fifth are proven by later fixes. The rest rest on code reading by two models, with a control but no
executed test.*

A reviewer that reports a lot will name the known bug more often by volume alone, so the other reports matter.
gpt-6.2 and Opus 5.5 reported {v('q08', 'findings')} problems on the 30 changes; {v('q08', 'known')} were the known
bug. We checked each one two ways: was it later fixed on main, and do two checkers who trace the code agree the
failure happens?

{chart('q08', 0)}

{chart('q08', 1)}

{v('q08', 'later_other')} of the other reports were later fixed on main by someone else, which is proof they were
real. That count is a floor: the same search found the fix for only {v('q08', 'later_found_known')} of the
{v('q08', 'control_cases')} problems we already knew were fixed.

- **How we know.** The reports were pooled under anonymous labels with nothing marking the known bugs. One reader
  searched later fix commits; two checkers each traced every report in the exported code.
- **How it was checked.** The checkers were tested on the known-real problems, first on the original code and then on
  the code after the fix. After the fix, both still confirmed {v('q08', 'control_both_still')}; two of those belong
  to a fix that was only partial.
- **What it does not show.** That the unfixed reports matter enough to block a merge. The two checkers are the same
  two models that wrote the reports, so they could share a convincing mistake. A failing test would settle it; none
  was written.

{run_line('q08')}

## 9. About a third of the bugs could not be seen by reading code

*Tentative. One reader's judgment on 30 cases; the key group is nine.*

{chart('q09', 0)}

No reviewer named a bug that depended on how a browser lays out a page, what a database accepts or how a filesystem
behaves under load. Size mattered too: reviewers named {v('q09', 'small_named')} of {v('q09', 'small_cases')} bugs in
changes of 7 files or fewer, and {v('q09', 'large_named')} of {v('q09', 'large_cases')} in larger ones.

- **How we know.** A reader given the bug and the causing change chose the least demanding thing a reviewer would
  have needed: the changed lines, other repository code, or outside knowledge.
- **How it was checked.** It was not checked by a second reader. The reader flagged several close calls between the
  first two groups.
- **What it does not show.** A firm share. Nine cases cannot fix a proportion; they show that such bugs exist in
  number and that none was caught by reading.

{run_line('q09')}

## 10. Most bugs broke no written rule

*Tentative. A sample found by commit wording, which later proved to favor quickly fixed bugs.*

The project keeps written rules for contributors and for the bot. In the first study, of {v('q10', 'confirmed')} bugs
whose fix names the causing change, a rule existed for {v('q10', 'rules_existing')} when the change was written, and
{v('q10', 'rules_checkable')} of those could have been checked from the changed lines alone.

{chart('q10', 0)}

{run_line('q10')}

## 11. Changes committed straight to main show no sign of causing more bugs

*Tentative. The direct-commit side rests on {v('q11', 'bugs_direct')} sampled bugs.*

{v('q11', 'direct_share_pct')}% of commits since 10 September reached main with no pull request number in the title.
Per commit they carried fewer bugs than changes that went through a pull request, not more.

They are also smaller (a median of {v('q11', 'median_files_direct')} files against {v('q11', 'median_files_pr')}),
so size alone could explain the gap. Within changes of 6 files or more, the rate was
{v('q11', 'strat_direct_larger')} for direct commits against {v('q11', 'strat_pr_larger')} through a pull request.

{numbers('q11', 'commits', 'bugs', 'per_commit', names=['Commits', 'Sampled bugs', 'Bugs per 100 commits'])}

- **How we know.** Same method as finding 4, split by whether the commit title carries a pull request number.
- **How it was checked.** It was not checked further. The ratio of the two rates is {v('q11', 'direct_ratio')}, with
  a plausible range of {span('q11', 'direct_ratio')}, which includes no difference.
- **What it does not show.** Who made the direct commits or why. Finding 12 takes up changes merged against the
  review bot's verdict.

{run_line('q11')}

## 12. Changes merged while the bot objected carried more bugs

*Supported. A comparison with ordinary changes, with size held equal. It shows a link, not a cause.*

Findings 1 to 11 start from bugs. To ask whether a kind of change causes more bugs, we also need to know how common
that kind is among ordinary changes. So we drew {v('q12', 'verdict_sample')} merged pull requests at random and
recorded, for each, what the bot's review said at the moment it merged. The bot had called
{v('q12', 'verdict_share_ready')}% of them ready and objected to {v('q12', 'verdict_share_objected')}%, which merged
anyway.

{chart('q12', 0)}

Changes merged over the bot's objection caused sampled bugs {v('q12', 'verdict_ratio_objected')} times as often as
changes it called ready (plausibly {span('q12', 'verdict_ratio_objected')}). The bot objects more to large changes,
and large changes carry more bugs, so part of that is size. Comparing only changes of similar size, the ratio is
{v('q12', 'verdict_adjusted_objected')} (plausibly {span('q12', 'verdict_adjusted_objected')}). Changes the bot never
reviewed were no different from ones it called ready.

{ratio_table('q12', 'verdict')}

- **How we know.** The comparison sample says how common each verdict is; the bug-causing changes say how many
  sampled bugs came from each. The ratio of those two is the relative bug rate. "Similar size" means within three
  groups: 1 to 5 files, 6 to 30, and over 30.
- **How it was checked.** The verdict is read mechanically from the marker the bot writes into its own comment, for
  the last version written before the merge. The causing change is the readers' judgment (finding 2).
- **What it does not show.** That merging against the verdict causes bugs. The bot objects to changes that are
  harder for other reasons too. And finding 6 still holds: in most of these cases its open items were about something
  other than the bug.

{run_line('q12')}

## 13. Merging soon after the bot's review shows no clear extra risk

*Tentative. The intervals are wide and include no difference.*

{ratio_table('q13', 'coverage')}

Changes where the bot had seen only an earlier revision carried more bugs ({v('q13', 'coverage_ratio_earlier')} times,
plausibly {span('q13', 'coverage_ratio_earlier')}), but those are larger changes with more rounds of revision. At
equal size the ratio falls to {v('q13', 'coverage_adjusted_earlier')} (plausibly
{span('q13', 'coverage_adjusted_earlier')}), which includes no difference.

{ratio_table('q13', 'speed')}

Changes merged within ten minutes of the bot's review did not carry more bugs: {v('q13', 'speed_adjusted_fast')}
times the rate of those merged an hour or more later, at equal size (plausibly
{span('q13', 'speed_adjusted_fast')}), which includes no difference.

- **How we know.** Same method as finding 12, using which revision the bot reviewed and the minutes from its review
  to the merge.
- **What it does not show.** That speed is safe. Quick merges are mostly small, simple changes; the comparison cannot
  say what would happen if the hard ones were merged as fast.

{run_line('q13')}

## 14. Who opened or merged a change made no detectable difference; how long it stayed open did

*Supported for time open. The other comparisons are too thin to show a difference either way.*

{chart('q14', 0)}

{ratio_table('q14', 'open')}

Pull requests merged within an hour of being opened carried {v('q14', 'open_adjusted_hour')} times the bugs of those
open a day or more, at equal size (plausibly {span('q14', 'open_adjusted_hour')}). A change that stays open is
usually one that needed work, and those are the ones that later needed fixing.

The other three comparisons show no difference that can be told from none once size is held equal. They are given
as tables, not charts, because a bar would suggest a difference the numbers do not support.

{ratio_table('q14', 'author')}

{ratio_table('q14', 'merge')}

{ratio_table('q14', 'human')}

- **How we know.** Same method as finding 12. A maintainer here is a person who merged at least one of the fetched
  pull requests; GitHub's own member label misses people whose membership is private.
- **What it does not show.** That review by another person does not help. Only {v('q15', 'human_review_pct')}% of
  the sampled changes had one, and people chose to review the risky ones, so the two groups are not alike. Finding
  19 repeats this on every pull request, with the same answer.

{run_line('q14')}

## 15. How this project reviews and merges, in numbers

*Measured. Counted from git and GitHub; nothing is judged.*

{chart('q15', 0)}

| | |
|---|---:|
| Commits on main per day, 10 Sep to 22 Nov 2026 | {v('q15', 'commits_per_day')} |
| Merged pull requests, 10 Sep to 22 Nov 2026 | {v('q15', 'pulls')} |
| Accounts that merged at least one of them | {v('q15', 'mergers')} |
| Share of all pull requests merged by the most active account | {v('q15', 'top_merger_pct')}% |
| Share of all pull requests opened by the most active account | {v('q15', 'top_author_pct')}% |
| Share of all pull requests opened by an automation account | {v('q15', 'automation_pct')}% |
| Share of all pull requests another person reviewed before the merge | {v('q15', 'all_second_review_pct')}% ({v('q15', 'all_second_review')}) |
| Median time from opening a pull request to merging it | {v('q15', 'median_minutes_open')} minutes |
| Median time from the bot's review to the merge | {v('q15', 'median_minutes_after_bot')} minutes |
| Share of commits titled "fix" | {v('q15', 'fix_title_pct')}% |
| Share of commits changing fewer than 10 files | {v('q15', 'under_10_files_pct')}% |
| Mean files changed per commit | {v('q15', 'mean_files')} |

{run_line('q15')}

## 16. A screenshot or video in the pull request did not go with fewer bugs

*Supported. It shows what such pull requests are like, not what the screenshot did.*

The project asks for visual proof on visible changes, so we checked whether pull requests that carry it do better.
Screenshots and videos are attached almost only to interface changes, and interface changes cause more bugs than
others, so the fair comparison is among interface changes alone.

{chart('q16', 0)}

{ratio_table('q16', 'interface')}

Interface changes with a screenshot or video caused {v('q16', 'interface_adjusted_yes')} times the bugs of interface
changes without one, at equal size (plausibly {span('q16', 'interface_adjusted_yes')}).

- **How we know.** For each of the {v('q17', 'sample')} sampled pull requests and each bug-causing one, we read the
  description as it stood at merge and counted embedded pictures and videos. An interface change is one that touches
  files under `ui/` or `apps/`.
- **How it was checked.** Counts are mechanical. Nearly every description has an "Evidence" heading, so the heading
  alone says nothing; only an embedded picture or video counts here.
- **What it does not show.** That proof makes things worse. People attach screenshots to the changes a user will
  see, and a visible bug is the kind that gets noticed and fixed within three weeks. What it does show is that a
  screenshot of the change working once is not a sign the change is safe.

{run_line('q16')}

## 17. The bugs are concentrated in changes that could be pointed at beforehand

*Supported for this period. The three signs were picked after seeing the earlier findings, so this is a description,
not a tested prediction.*

Three things visible at or before merge each mark a small share of changes and a large share of bugs: the bot
objected, the pull request had been open a day or more, or the change touched more than 30 files.

{chart('q17', 0)}

{numbers('q17', 'changes_pct', 'bugs_pct', 'bugs', names=['Share of all changes, %', 'Share of traced bugs, %', 'Sampled bugs'])}

Changes with at least two of the three signs are {v('q17', 'changes_pct_two')}% of all changes and the source of
{v('q17', 'bugs_pct_two')}% of the traced bugs. Changes with none are {v('q17', 'changes_pct_none')}% of changes and
the source of {v('q17', 'bugs_pct_none')}%.

- **How we know.** The share of changes comes from the random comparison sample; the share of bugs from the
  {v('q17', 'bugs')} sampled bugs whose causing change is a fetched pull request.
- **How it was checked.** All three signs are read from git and GitHub. No model judged them.
- **What it does not show.** That the same signs will mark the bugs of another period, or that looking harder at
  those changes would have caught the bugs. Finding 7 bears on the second point; nothing here tests the first.

{run_line('q17')}

## 18. No sign that anyone is overloaded

*Supported as "no sign found". These are comparisons across every commit since 10 September, with no model
judging anything.*

The worry is simple: one person lands hundreds of changes a day, the project lands a thousand, and care must be
slipping. If that were so, changes landed under heavy load would cause more bugs than changes landed under light
load. We looked for that six ways and did not find it.

For the median commit, its author landed {v('q18', 'median_author_load')} changes that same day, and the previous
one {v('q18', 'median_gap')} minutes earlier. On a typical day {v('q20', 'people_per_day')} accounts merge; one
account merges {v('q20', 'top_pct')}% of all pull requests and three accounts merge {v('q20', 'top3_pct')}%.

{commit_table(('q18', 'load', 'By how many changes the author landed that day'),
              ('q18', 'gap', "By how soon after the author's previous change"),
              ('q18', 'ownrest', "By the author's own usual pace, leaving out the most active author"),
              ('q20', 'load', 'By how many pull requests the person merging merged that day'),
              ('q19', 'busy', 'By how busy the whole project was that day'),
              ('q19', 'week', 'By day of the week'))}

Read each block against its first row. No row differs clearly from its baseline, and where the numbers lean, they
lean toward fewer bugs under heavier load, not more.

- **How we know.** For each of the {v('q18', 'commits')} commits we counted how many the same author landed that
  day and how long since their previous one, and for each pull request how many the same person merged that day.
  The bugs are the {v('q18', 'bugs')} sampled bugs whose causing commit is among those commits. "At equal size and
  kind" compares changes of similar file count and the same title type (feat, fix, other).
- **One exception, and what it is.** Taking all authors together, an author's light days carried more bugs per
  change than their usual days ({v('q18', 'own_adjusted_usual')} times on usual days, plausibly
  {span('q18', 'own_adjusted_usual')}). That comes from the single most active author, who lands over half of all
  commits. Without that author the three kinds of day are alike, as the third block shows.
- **What it does not show.** That the pace is harmless. A count per commit favors whoever cuts work into the most
  pieces, and a tired author's mistakes need not land on the same day. It shows only that heavier days are not
  where the traced bugs came from.

{run_line('q18')}; `python3 {SCRIPTS['q19']}`; `python3 {SCRIPTS['q20']}`

## 19. Occasional contributors did no worse; a second person is too rare to measure

*Tentative. The groups are small.*

Would more contributors mean more bugs? One way to ask is whether changes from people who contribute rarely cause
more bugs than changes from the regulars.

{commit_table(('q22', 'who', 'By how much the author contributes'),
              ('q21', 'second', 'By whether a second person was involved'),
              ('q21', 'review', 'By whether another person reviewed it'))}

- The {v('q22', 'authors_occasional')} authors with 20 commits or fewer wrote {v('q22', 'who_share_occasional')}% of
  commits and caused {v('q22', 'who_bugs_occasional')} of the sampled bugs: no more per change than the most active
  author.
- The {v('q22', 'authors_regular')} authors in the middle, with 21 to 500 commits, caused
  {v('q22', 'who_adjusted_regular')} times as many per change (plausibly {span('q22', 'who_adjusted_regular')}).
  The range only just excludes "no difference", and finding 14 saw none on a smaller sample.
- A second person merged or reviewed {v('q21', 'second_share_second')}% of commits. Those caused no clearly
  different number of bugs. Only {v('q21', 'review_commits_reviewed')} commits came from a pull request another
  person had reviewed, which is too few to say anything.

- **How we know.** Authors are grouped by how many commits they landed since 10 September. Who merged and who
  reviewed comes from GitHub, for all {v('q15', 'pulls')} merged pull requests.
- **What it does not show.** Whether review by a second person would help. It is hardly practised here, so this
  data cannot answer it. Authors are told apart by commit email, so one person with two addresses counts twice.

{run_line('q22')}; `python3 {SCRIPTS['q21']}`

## 20. Changes to files that other people were also editing caused more bugs

*Supported. It cannot separate "too many hands" from "the busiest, most central code".*

{chart('q23', 0)}

{commit_table(('q23', 'shared', 'By how many other people changed the same files in the previous 14 days'),
              ('q23', 'familiar', 'By whether the author had changed those files before'))}

When the files a change edits had also been changed by other people in the previous two weeks, the change caused
about {v('q23', 'shared_adjusted_mid')} times the bugs (plausibly {span('q23', 'shared_adjusted_mid')}) of a change
to files that only its author had been editing. Two or more other people per file was no worse than one.

Whether the author knew the files made no steady difference: authors editing files they had never changed before
did the same as authors who had changed all of them. The middle row, "some of them", is higher; those are changes
that reach beyond the author's own files into others.

- **How we know.** For every code file a commit edits, we counted the other authors who had changed that file in
  the 14 days before, and averaged over the commit's files. Only commits that edit existing code are compared.
- **What it does not show.** That several people editing a file is what causes the bugs. Files many people edit are
  also the central ones where most things connect, and this data cannot tell those two apart.

{run_line('q23')}

## 21. Changes that add new code files caused two thirds of the bugs

*Well supported. Counted from git; it agrees with findings 2 and 3 by a different route.*

{chart('q24', 0)}

{commit_table(('q24', 'new'))}

A change that adds at least one new code file is {v('q24', 'new_share_adds')}% of commits and the source of
{v('q24', 'new_bugs_adds')} of the {v('q25', 'bugs')} sampled bugs ({v('q24', 'bugs_pct_adds')}%). At equal size
and kind it caused {v('q24', 'new_adjusted_adds')} times the bugs of a change that only edits existing files
(plausibly {span('q24', 'new_adjusted_adds')}).

- **How we know.** Git records which files a commit adds. A code file is a non-test file under `src/`, `ui/`,
  `extensions/`, `packages/` or `apps/`.
- **Why it matters here.** Finding 3 relied on the word "feat" in the title, which only {v('q03', 'rate_commits_feat')}
  commits carry. Adding a file is a fact, not a label, and it marks the same thing: new code is where the bugs are.
- **What it does not show.** That the bug sits in the new file. It says the change that carried the bug also added
  one.

{run_line('q24')}

## 22. Nearly every bug-causing change came with tests; no part of the code stands out

*Measured.*

{commit_table(('q25', 'tests', 'Among commits that change code: with or without tests'),
              ('q26', 'part', 'By the part of the code the commit touches'))}

- {v('q25', 'tests_bugs_with')} of the {v('q25', 'bugs')} sampled bugs came from a change that also changed test files.
  The tests that came with a change did not catch the bug it carried.
- Code changes with no test file are few and small (refactors, chores, small fixes) and caused
  {v('q25', 'tests_bugs_without')} of the sampled bugs. This is not evidence that skipping tests is safe: the two
  groups are different kinds of change.
- Interface changes cause about twice the bugs per commit of core changes, but they are also larger. At equal size
  and kind, interface, plugin and core changes are alike.

- **How we know.** A test file is one whose path marks it as a test (`.test.`, `.spec.`, `.e2e.`, a `test` or
  `fixtures` folder). Each commit is put in one part of the code by the folders it touches.
- **What it does not show.** Whether the tests were good, or whether they ran. No test was run for this study.

{run_line('q25')}; `python3 {SCRIPTS['q26']}`

## How this compares with published research

Only studies whose figures we could check against the paper or its abstract are quoted. None of them studied this
project, and none measured exactly what we measured, so read each row as "same direction or not", not as a ranking.

| What | This project | Published research | Reading |
|---|---|---|---|
| Bug-causing changes are larger | Median {v('q03', 'cause_median_files')} files against {v('q03', 'base_median_files')} for any commit | In Eclipse and Mozilla, changes that later needed a fix were about three times larger than others: 7.49 against 2.61 files, and 5.19 against 1.97 [1] | Same direction, and stronger here |
| Risk per change against risk per file | Per change, {v('q04', 'per_commit_ratio')} times higher for the largest; per file changed, flat | A model of change risk at Bell Labs found how widely a change spreads across the code essential to predicting failure [2] | Consistent: a bigger change is more exposure |
| Share of changes that are fixes | {v('q15', 'fix_title_pct')}% titled "fix" | 20.8% in Eclipse, 48.5% in Mozilla [1] | At the high end of what has been reported |
| Do fixes cause more bugs than other changes | No: "fix" is {v('q03', 'cmp_cause_fix')}% of causes and {v('q03', 'cmp_base_fix')}% of commits | Three times more in Eclipse, no difference in Mozilla [1]. 14.8% to 24.4% of operating-system bug fixes were themselves wrong [3]; nearly 40% of fault fixes led to further faults in one telecom system [4] | Unremarkable. Fixes that break things are normal everywhere |
| "Fixes" that fix no bug | {v('q01', 'gpt_notbug_pct')}% to {v('q01', 'not_bug_pct')}%, depending on the reader | 33.8% of bug reports in five open-source projects were not bugs [5] | In line |
| What review catches | The bot named {v('q06', 'flag_exact')} of {v('q06', 'reviewed')} bugs that got through | About 75% of what code review finds concerns maintainability, not function [6]; reviews find fewer defects than teams expect [7] | Same in kind. Not like for like: those studies count what review found, ours counts what it missed |
| Review by a second person | {v('q15', 'all_second_review_pct')}% of pull requests; {v('q15', 'self_merged_pct')}% merged by their own author | At Google a change typically needs approval from at least one reviewer; the median is one reviewer [8]. Other studied projects had a median of two [8] | The clearest departure from studied practice |
| Does review coverage matter | No detectable difference here (finding 14) | In Qt, VTK and ITK, components with low review coverage and participation had up to two and five more post-release defects [9]; a later study at Sony Mobile did not find the link [10] | Open. The research is mixed and our sample cannot tell |
| Size of an ordinary change | {v('q15', 'under_10_files_pct')}% of commits change fewer than 10 files; mean {v('q15', 'mean_files')} | About 90% at Google, with a median of 24 lines [8]; mean 3.5 files in Eclipse and Mozilla [1] | Larger batches here |
| Speed of review | Median {v('q15', 'median_minutes_open')} minutes from opening to merge | Under 4 hours at Google; 15 to 24 hours at AMD, Chrome OS and Microsoft [8] | Much faster here |
| Many people changing the same code | Changes to files others had also been editing caused {v('q23', 'shared_adjusted_mid')} times the bugs (finding 20). Authors new to a file did no worse | In Windows Vista and Windows 7, how many low-expertise developers changed a component, and how much of it its top owner wrote, were related to its faults before release and its failures after [14] | Same direction for shared code. The "unfamiliar author" part does not show here |

### What stands out, and what does not

Three things in these numbers depart from what the studies describe:

- **Almost no change is reviewed by a second person.** Authors merge their own changes, and the reviewer is a bot.
- **Changes are large.** {v('q15', 'over_100_files_pct')}% of commits change more than 100 files, and those carry
  {v('q03', 'cmp_cause_over100')}% of the traced bugs.
- **A fifth of changes merge while the bot objects**, and those carry more bugs at equal size (finding 12).

One more thing follows from these: the bugs are not spread evenly. A small, recognisable share of changes carries
about half of them (finding 17).

On whether more people would help, the numbers say four things and leave one open. The work runs through few hands:
one account merges {v('q20', 'top_pct')}% of pull requests and three merge {v('q20', 'top3_pct')}%. Yet nothing
shows those hands are overloaded: heavy days are no worse than light ones (finding 18). Changes from occasional
contributors are no worse than the core's (finding 19). Bugs are more common where several people edit the same
files (finding 20). What stays open is whether a second pair of eyes helps, because only
{v('q15', 'all_second_review_pct')}% of pull requests get one.

Several things that might look alarming are ordinary by the same studies: half of all changes being fixes, fixes
that introduce new bugs, changes titled "fix" that fix nothing, and a reviewer that misses functional bugs.

### What this study can and cannot say about coding agents

It cannot attribute any change to an agent or a person. Git records who landed a change, and this project's rules ask
for no agent attribution on commits. So nothing here measures agent-written code against human-written code.

What the numbers do show is the working pattern: {v('q15', 'commits_per_day')} commits a day through
{v('q15', 'mergers')} accounts that merge, one account opening {v('q15', 'top_author_pct')}% of pull requests,
{v('q15', 'automation_pct')}% opened by automation accounts, and a median of {v('q15', 'median_minutes_open')}
minutes from opening to merge.

Recent studies of AI-assisted development, which are newer and less settled than the work above, point at the same
two pressures this data shows, volume and batch size:

- A large practitioner survey estimated lower delivery stability as AI adoption rose, and suggested larger changes
  as a reason [11].
- A study of open-source projects that adopted an AI editor found a short-lived rise in output and a lasting rise in
  static-analysis warnings and code complexity [12].
- A study of pull requests written by coding agents found they are accepted less often than people's [13].

On this evidence the thing to watch is not who or what writes a change. It is how much change arrives at once
(finding 4) and whether anything other than its author looks at it before it merges (finding 15).

### References

1. J. Śliwerski, T. Zimmermann, A. Zeller. [When do changes induce fixes?](https://www.st.cs.uni-saarland.de/papers/msr2005/msr2005.pdf) MSR 2005. Tables 3 to 6.
2. A. Mockus, D. Weiss. [Predicting risk of software changes](https://dblp1.uni-trier.de/rec/journals/bell/MockusW00.html). Bell Labs Technical Journal, 2000.
3. Z. Yin, D. Yuan, Y. Zhou, S. Pasupathy, L. Bairavasundaram. [How do fixes become bugs?](https://bibtex.github.io/ESEC-FSE-2011-YinYZPB.html) ESEC/FSE 2011.
4. R. Purushothaman, D. Perry. [Toward understanding the rhetoric of small source code changes](https://users.ece.utexas.edu/~perry/work/papers/DP-03-small.pdf). IEEE Transactions on Software Engineering, 2005.
5. K. Herzig, S. Just, A. Zeller. [It's not a bug, it's a feature: how misclassification impacts bug prediction](https://www.st.cs.uni-saarland.de/publications/files/herzig-icse-2013.pdf). ICSE 2013.
6. M. Mäntylä, C. Lassenius. [What types of defects are really discovered in code reviews?](https://mmantyla.github.io/wiki/What+Types+of+Defects+Are+Really+Discovered+in+Code+Reviews%253F.html) IEEE Transactions on Software Engineering, 2009.
7. A. Bacchelli, C. Bird. [Expectations, outcomes, and challenges of modern code review](https://www.microsoft.com/en-us/research/?p=164195). ICSE 2013.
8. C. Sadowski, E. Söderberg, L. Church, M. Sipko, A. Bacchelli. [Modern code review: a case study at Google](https://research.google/pubs/pub47025/). ICSE-SEIP 2018. The figures for other projects are those it quotes from Rigby and Bird, FSE 2013.
9. S. McIntosh, Y. Kamei, B. Adams, A. Hassan. [The impact of code review coverage and code review participation on software quality](https://rebels.cs.uwaterloo.ca/papers/msr2014_mcintosh.pdf). MSR 2014.
10. J. Shimagaki, Y. Kamei, S. McIntosh, A. Hassan, N. Ubayashi. [A study of the quality-impacting practices of modern code review at Sony Mobile](https://rebels.cs.uwaterloo.ca/papers/icse2016_shimagaki.pdf). ICSE 2016 companion.
11. DORA. [Accelerate State of DevOps Report 2024](https://dora.dev/report/2024). A survey; the estimate is a correlation.
12. H. He, B. Vasilescu and others. [Does AI-assisted coding deliver? A difference-in-differences study of Cursor's impact on software projects](https://arxiv.org/abs/2511.04427). Preprint, 2025.
13. H. Li, H. Zhang, A. Hassan. [The rise of AI teammates in software engineering (SE) 3.0: how autonomous coding agents are reshaping software engineering](https://arxiv.org/abs/2507.15003). Preprint, 2025.
14. C. Bird, N. Nagappan, B. Murphy, H. Gall, P. Devanbu. [Don't touch my code! Examining the effects of ownership on software quality](https://www.microsoft.com/en-us/research/publication/dont-touch-my-code-examining-the-effects-of-ownership-on-software-quality/). ESEC/FSE 2011.

References 1 and 8 were read in full for the figures quoted. The others are quoted from their abstracts.

## How each study was done

| Study | Cases | How cases were chosen | Who judged | Independent check |
|---|---:|---|---|---|
| What fixes repaired | {v('q01', 'sample')} | Lottery over every fix in the period, in a fixed pseudo-random order | One Claude Opus 5.5 reader per fix | Second Claude reader on {v('q01', 'second_n')}; GPT reader on {v('q01', 'gpt_n')} |
| What the bot had said | {v('q06', 'reviewed')} | Every traced bug whose causing change the bot reviewed | One Claude Opus 5.5 reader per case | GPT reader on all; both "named" cases read by hand |
| Blind review | {v('q07', 'cases')} | First 15 of each kind in random order, among smaller recent changes the bot reviewed | Claude Opus 5.5 graders, blind to the reviewer | GPT grader on all pairs; run logs audited for leaks |
| Are the reports real | {v('q08', 'findings')} | Every report from the two strongest reviewers | One later-fix reader; two code-tracing checkers | Known-real reports as a control, before and after the fix |
| Kinds of change compared | {v('q15', 'sample')} | Lottery over every merged pull request since 10 September, plus every bug-causing one | Nobody: read from git and GitHub | The bot's verdict is read from its own marker |
| Workload, people and files (findings 18 to 22) | {v('q18', 'commits')} | Every commit on main since 10 September; the bugs are the {v('q18', 'bugs')} sampled bugs whose causing commit is among them | Nobody: read from git and GitHub | Size and kind of change held equal; heavy-day result repeated without the most active author |
| Written rules | {v('q10', 'confirmed')} | Fixes whose wording blames an earlier change | Claude readers, verdicts re-read | Three cases checked against source by hand |

## Limits that apply throughout

- Every classification is a model's judgment made in hindsight from code changes and PR text. Two makers' models
  agreeing reduces the risk of one model's habit; it does not make the judgment a measurement.
- Nothing was executed. No bug was reproduced and no reported problem was confirmed by a failing test.
- The period is three weeks of one project. The figures describe that period and may not hold for another.
- A sample of fixes cannot see bugs that were never fixed, or bugs the bot stopped before merge.
- The model comparison covers changes of at most 30 files and one run per reviewer. The reviewers did not get
  identical guidance: some GPT runs read a personal review guide on the test machine, and the Claude runs had the
  repository's current contributor guide in context. Neither contains the answers.
- Findings 18 to 22 make about thirty comparisons on the same {v('q18', 'bugs')} bugs. By chance alone, one or two
  of thirty would look like a clear difference. The two we call supported (findings 20 and 21) are far from the
  line; the others that cross it are labelled tentative.
- The data files record the public author and merger of each change, as GitHub shows them. The report draws no
  conclusion about any person.

## Repository map

| Folder | What it holds |
|---|---|
| `PROTOCOL.md` | The experimental setup: every step, what it needs, what it makes, how to check it |
| `study.json`, `study.py`, `pipeline/` | The settings, the one command that runs every stage, and its parts |
| `dataset/` | The facts every question reads, one table per kind of thing, with a data dictionary |
| `questions/` | One script per question; each reads only `dataset/` and writes `results/` and `charts/` |
| `report/` | The renderer for this page |
| `fix-origins/` | How the dataset was collected: sampling, evidence bundles, the briefs given to models, every model answer |
| `detection-check/` | The first, wording-based study |
"""


def main():
    text = report()
    with open(os.path.join(ROOT, "README.md"), "w") as handle:
        handle.write(text)
    print(len(text), "characters,", sum(len(c) for c in CHARTS.values()), "charts")


if __name__ == "__main__":
    main()
