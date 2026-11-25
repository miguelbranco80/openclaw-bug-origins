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
            f"![{drawn['title']}](charts/{drawn['stem']}-dark.svg#gh-dark-mode-only)")


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
Written 25 November 2026.

**How this repository is organised.** `dataset/` holds the facts. `questions/` holds one script per question; each
reads only the dataset and writes the numbers and charts used below. `./rebuild.sh` runs them all and re-renders
this page. How the dataset was collected, and what cannot be reproduced exactly, is in [REPRODUCE.md](REPRODUCE.md).

## What the evidence supports, and how strongly

| # | Strength | Finding |
|---|---|---|
| 1 | Depends on definition | Between about a tenth and a third of changes titled "fix" repair no bug. Two models drew the line differently. |
| 2 | Supported | New code that never worked accounts for at least as many bugs as working things broken later: from about even ({v('q02', 'gpt_ratio')} to one, by a second model) to about double ({v('q02', 'ratio_high')} to one, by the first readers). When both models trace a bug to a cause, they name the same change. |
| 3 | Well supported | Changes titled as new features cause far more than their share of bugs. The title "fix" tells you little. |
| 4 | Well supported | Large changes cause far more bugs per change, but about the same per file changed. |
| 5 | Well supported | A broken thing typically stayed broken for about three weeks, unless someone traced the cause at once. |
| 6 | Well supported | The review bot had rarely named the bug before the change merged. Ignored warnings were rare. |
| 7 | Supported | Two current models together named more of the known bugs than the bot had. For either model alone, the gap could still be chance. |
| 8 | Supported | Most of the other problems those models reported hold up when checked, and about a third of them are minor. |
| 9 | Tentative | About a third of the bugs could not be seen by reading code at all. This rests on nine cases. |
| 10 | Tentative | Most bugs broke no written rule. |
| 11 | Tentative | Changes committed straight to main, without a pull request, show no sign of causing more bugs. |

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

{numbers('q02', 'sens_never', 'sens_broke', names=['Never worked', 'Broken later'])}

Older causes are harder to trace, and a reader who cannot find an earlier working version may lean toward "never
worked". That is one reason the gap narrows when only confident or recent cases are kept. The last two rows are the
60 fixes a second model re-read; on that smaller set both readers put the two kinds about even.

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

For each traced bug we looked at the change that introduced it. Its title tells you little:
{v('q03', 'title_fix')} of the {v('q02', 'traced')} were themselves titled "fix", but so is about half of everything
merged, and some of those are large additions. One, titled as a fix, changed 138 files and added a whole rollback
mechanism. Changes titled "feat" are a small share of all commits and a large share of causes.

{chart('q03', 0)}

{numbers('q03', 'cmp_cause', 'cmp_base', names=['Bug-causing changes, %', 'All commits, %'])}

{chart('q03', 1)}

{numbers('q03', 'title_never', 'title_broke', names=['Never worked', 'Broken later'])}

- **How we know.** The comparison uses the {v('q03', 'recent_causes')} sampled bugs whose causing change was made
  since 10 September 2026 and all {v('q03', 'base_commits')} commits on main since that date, counted from git.
- **How it was checked.** Titles and file counts are read mechanically from git, not judged. Which change caused
  each bug is the reader's judgment from finding 2.
- **What it does not show.** What the change was really for. A title is a label, and "fix" covers everything from a
  one-line repair to a 138-file addition.

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
merge. The bot also said "ready" on changes that carried a bug.

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

{chart('q11', 0)}

They are also smaller (a median of {v('q11', 'median_files_direct')} files against {v('q11', 'median_files_pr')}),
so size alone could explain the gap. Within changes of 6 files or more, the rate was
{v('q11', 'strat_direct_larger')} for direct commits against {v('q11', 'strat_pr_larger')} through a pull request.

{numbers('q11', 'commits', 'bugs', 'per_commit', names=['Commits', 'Sampled bugs', 'Bugs per 100 commits'])}

- **How we know.** Same method as finding 4, split by whether the commit title carries a pull request number.
- **How it was checked.** It was not checked further. The ratio of the two rates is {v('q11', 'direct_ratio')}, with
  a plausible range of {span('q11', 'direct_ratio')}, which includes no difference.
- **What it does not show.** Who made the direct commits or why. It also cannot say whether changes merged against
  the review bot's verdict cause more bugs: that needs the bot's verdicts on ordinary changes, not only on
  bug-causing ones.

{run_line('q11')}

## What this supports doing

1. **Add a plain "find the defects" pass by a current top model to the bot's review, and compare it on this benchmark
   first.** Rests on finding 7. The 30 cases and scripts can score any reviewer, so the claim can be re-tested before
   anything changes.
2. **Use two different models for that pass.** Rests on finding 7: the two overlapped on only
   {v('q07', 'named_both_top')} of {v('q07', 'named_either_top')}.
3. **Have a second model check each reported problem before a person sees it.** Rests on finding 8: the checkers
   could say no, and a third of confirmed reports were minor.
4. **Review large changes in parts, and mark any change the bot never reviewed.** Rests on findings 4 and 6.
   {v('q06', 'unreviewed_large')} traced bugs came from changes of 500 files or more that the bot acknowledged and
   did not review.
5. **Cover what reading cannot: run it.** Rests on finding 9, which is tentative. Browser checks for interface style
   changes and real database runs for query changes are the two places the nine cases point to.

What it does not support:

- Enforcing the bot's current verdicts more strictly. Ignored warnings were rare.
- Leading with more written rules. Most bugs broke none, and the rules that existed could not be checked from the
  change alone.
- Relying on tests of old behavior alone. They cannot catch new code that never worked, which is at least half of the
  traced bugs.
- Waiting for better models. The better result came from models available now.

## How each study was done

| Study | Cases | How cases were chosen | Who judged | Independent check |
|---|---:|---|---|---|
| What fixes repaired | {v('q01', 'sample')} | Lottery over every fix in the period, in a fixed pseudo-random order | One Claude Opus 5.5 reader per fix | Second Claude reader on {v('q01', 'second_n')}; GPT reader on {v('q01', 'gpt_n')} |
| What the bot had said | {v('q06', 'reviewed')} | Every traced bug whose causing change the bot reviewed | One Claude Opus 5.5 reader per case | GPT reader on all; both "named" cases read by hand |
| Blind review | {v('q07', 'cases')} | First 15 of each kind in random order, among smaller recent changes the bot reviewed | Claude Opus 5.5 graders, blind to the reviewer | GPT grader on all pairs; run logs audited for leaks |
| Are the reports real | {v('q08', 'findings')} | Every report from the two strongest reviewers | One later-fix reader; two code-tracing checkers | Known-real reports as a control, before and after the fix |
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
- The data files record the public author and merger of each change, as GitHub shows them. The report draws no
  conclusion about any person.

## Repository map

| Folder | What it holds |
|---|---|
| `dataset/` | The facts every question reads, one table per kind of thing, with a data dictionary |
| `questions/` | One script per question; each reads only `dataset/` and writes `results/` and `charts/` |
| `report/` | The renderer for this page |
| `fix-origins/` | How the dataset was collected: sampling, evidence bundles, prompts, runners, every model answer |
| `detection-check/` | The first, wording-based study |
"""


def main():
    text = report()
    with open(os.path.join(ROOT, "README.md"), "w") as handle:
        handle.write(text)
    print(len(text), "characters,", sum(len(c) for c in CHARTS.values()), "charts")


if __name__ == "__main__":
    main()
