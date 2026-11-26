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
READERS = json.load(open(os.path.join(ROOT, "dataset", "readers.json")))
MAIN, OTHER = READERS["fixes"], READERS["fixes_other_maker"]
ONE_OFF = json.load(open(os.path.join(ROOT, "one-off", "looking-harder.json")))  # hand-recorded; see that folder
OPINION = "What I would do with this: an opinion"
RESEARCH = "How this compares with published research"
SCRIPTS = {os.path.basename(p)[:3]: "questions/" + os.path.basename(p)
           for p in glob.glob(os.path.join(ROOT, "questions", "q*.py"))}


MISSING = []  # numbers the text asks for that the results do not hold (a study with other settings, or too few cases)


def lookup(question, metric):
    row = next((r for r in RESULTS.get(question, []) if r["metric"] == metric), None)
    if row is None:
        MISSING.append(f"{question} {metric}")
    return row


def v(question, metric):
    row = lookup(question, metric)
    if row is None:
        return "(not available)"
    return f"{row['value']:,}" if isinstance(row["value"], int) else str(row["value"])


def span(question, metric):
    row = lookup(question, metric)
    return f"{row['low']} to {row['high']}" if row else "(not available)"


def chart(question, number=0):
    if number >= len(CHARTS.get(question, [])):
        MISSING.append(f"{question} chart {number}")
        return "*(chart not available)*"
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
    lines = ["| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |",
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
    lines = ["| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size, kind and time |",
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
    read, ran, conf = ONE_OFF["reading"], ONE_OFF["running"], ONE_OFF["confirm"]
    return f"""# Where OpenClaw's bugs come from

An informal, independent look at the public [openclaw/openclaw](https://github.com/openclaw/openclaw) repository.
It is not affiliated with the project. It judges changes, not people.

We took a random sample of {v('q01', 'sample')} changes titled "fix", merged between 10 September and 22 November
2026, and traced each back to what it repaired and which earlier change had caused the problem. Then we set those
bugs against every commit and pull request of the period, to see which kinds of change carry them.

**In short.** You can tell beforehand where the bugs will be: a small, recognisable share of changes carries about
half of them. Tests did not protect: nearly every change that caused a bug shipped with tests. Can the bug be
caught before it merges? Only by brute force, and only about half the time. We tried by hand on
{read['changes']} risky changes: one AI review caught the bug in {read['one_review']} of them, and
{read['reviews_per_change']} AI reviews of each change, taken together, caught it in {read['pooled']}. That test is
not part of the study and is explained in [{OPINION}]({anchor(OPINION)}).

## Main results

**Expected results**

- **New code is where the bugs are.** Changes that add a new code file are {v('q24', 'new_share_adds')}% of commits
  and the source of {v('q24', 'bugs_pct_adds')}% of the traced bugs ({v('q24', 'new_bugs_adds')} of
  {v('q25', 'bugs')}). *Finding 1.*
- **Features cause more than their share.** Changes titled "feat" caused {v('q03', 'rate_feat')} bugs per 100
  commits, against {v('q03', 'rate_fix')} for changes titled "fix". *Finding 3.*
- **Bigger changes carry more bugs.** A commit of over 100 files carried about {v('q04', 'per_commit_ratio')} times
  the bugs of one of 1 to 5 files. The less obvious part: per file changed, the rate is about the same. A big change
  is more exposure, not worse work. *Finding 4.*
- **Files that several people are editing at once carry more bugs:** {v('q23', 'shared_adjusted_high')} times, for
  files two or more other people had changed in the previous two weeks. *Finding 20.*

**Less expected results...**

- **You can point at the risky changes before they merge.** {v('q17', 'changes_pct_two')}% of changes show at least
  two of three warning signs (the bot objected, the pull request was open a day or more, it touched more than 30
  files), and those changes carry {v('q17', 'bugs_pct_two')}% of the traced bugs. *Finding 17.*
- **The review bot rarely named the bug, yet its verdict marks risk.** Before a change merges, the bot gives a
  verdict: ready, needs changes, or blocked. It had named the actual bug in {v('q06', 'flag_exact')} of the
  {v('q06', 'reviewed')} bug-causing changes it reviewed. But changes merged while it said "needs changes" or
  "blocked" carried {v('q12', 'verdict_adjusted_objected')} times the bugs of changes it called ready. It was not
  hinting at the bug: in {v('q06', 'merged_against_unrelated')} of {v('q06', 'merged_against')} such cases its
  complaints were about something else, such as missing proof. It is as if the reviewer felt something was wrong
  without being able to say what. Or the pull request was simply being rushed past its review.
  *Findings 6 and 12.*
- **A screenshot or video goes with more bugs, not fewer.** (In hindsight makes sense because interface changes are
  hard). Among interface changes, those with one carried {v('q16', 'interface_adjusted_yes')} times the bugs.
  *Finding 16.*
- **Tests came with nearly every bug.** {v('q25', 'tests_bugs_with')} of the {v('q25', 'bugs')} traced bugs came
  from a change that also changed tests. Shipping tests with a change is not a sign it is safe. *Finding 21.*
- **About half the bugs were never regressions.** {v('q02', 'sens_never_all')} were new code that never worked,
  against {v('q02', 'sens_broke_all')} working things broken later. A test of the old behavior cannot catch the
  first kind. *Finding 2.*
- **Fast merges are the safe ones.** Pull requests merged within the hour carried far fewer bugs than those open a
  day or more: {v('q14', 'open_adjusted_hour')} times as many. *Finding 14.*
- **Nobody looks overloaded, not even the busiest account.** One account lands {v('q22', 'who_share_top')}% of all
  commits (guess who?). Its bug rate is the same as everyone else's: {v('q22', 'who_rate_top')} bugs per 100 commits,
  against {v('q22', 'rest_rate')} for all other authors together. So it is the source of
  {v('q22', 'top_bugs_pct')}% of the bugs, which is its share and no more. Among people who contribute regularly, the
  bug rate barely depends on who lands the change, once changes of the same size and kind are compared. That would
  make sense if everyone is working with coding agents, though this study cannot tell who is (although we know it is
  everyone 😄). The exception is people
  who contribute rarely: see the next point. And an author's heavy days are no worse than their light ones.
  *Findings 18 and 19.*
- **Outsiders' changes are the safer ones.** Changes from people with 20 commits or fewer carried fewer bugs than
  the most active author's: {v('q22', 'who_adjusted_occasional')} times as many. *Finding 19.*
- **Some bugs cannot be found by looking at the code.** We gave two strong AI models {v('q07', 'cases')}
  bug-causing changes from November and asked them to review each one, without saying a bug was in there. Between
  them they found the bug in {v('q07', 'named_either_top')}. For {v('q09', 'needs_outside')} of the
  {v('q07', 'cases')}, the bug could not be seen in the code at all: it depended on how a browser, a database or
  some other outside tool behaves. Nobody found any of those.
  *Findings 7 and 9.*

**So what would I do about it?** That is opinion, not part of the study, and it has its own section at the end:
[{OPINION}]({anchor(OPINION)}).

**And the pattern held.** We looked at two separate periods, September to October and then November, and found the
same thing in both. We also had a second AI model judge the November fixes. It mostly agreed on which change caused
each bug. It was stricter about what counts as a bug in the first place, so it counted fewer of them, but the
patterns above showed up either way. *Findings 22 and 23.*

**And compared with published research?** Much of this is ordinary: other projects also see about half of all
changes being fixes, fixes that cause new bugs, and reviews that miss real bugs. Three things stand out here: almost
no change is reviewed by a second person, changes are large, and a fifth of them merge while the bot objects.
*[{RESEARCH}]({anchor(RESEARCH)}).*

One caution on all of it: this shows where the bugs are, not what would have caught them. A test by hand,
outside the study, found that only brute force gets partway (see [the opinion section]({anchor(OPINION)})).

{chart('q17', 0)}

<!-- contents -->

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
- **Main model and second model.** A model read each fix and said what it repaired and which earlier change had
  caused the problem. The main model, {MAIN}, read every fix. The second model, {OTHER}, comes from a different
  company and read the November fixes, so that one model's habits can be told apart from facts.
- **Review bot.** ClawSweeper, the automated reviewer that comments on the project's pull requests before they merge.
- **Plausible range.** Where the true figure plausibly lies given the sample size (a 95% interval).

## Where the bugs come from

Findings 1 to 5: what kind of change had introduced each problem, and how long it lasted.

### 1. Changes that add new code files caused two thirds of the bugs

*Well supported. Whether a change adds a file is counted from git, not judged. Findings 2 and 3 reach the same
place by other routes.*

{chart('q24', 0)}

{commit_table(('q24', 'new'))}

A change that adds at least one new code file is {v('q24', 'new_share_adds')}% of commits and the source of
{v('q24', 'new_bugs_adds')} of the {v('q25', 'bugs')} traced bugs ({v('q24', 'bugs_pct_adds')}%). Such changes are
also larger than others, so we compared like with like: among changes of similar size, with the same kind of title,
landed in the same weeks, one that adds a file caused {v('q24', 'new_adjusted_adds')} times the bugs of one that
only edits existing files (plausibly {span('q24', 'new_adjusted_adds')}).

- **How we know.** For each sampled fix, a model traced the problem back to the earlier change that caused it. We
  then looked up that change among all {v('q18', 'commits')} commits on main since 10 September. Git records which
  files a commit adds. A code file is a non-test file under `src/`, `ui/`, `extensions/`, `packages/` or `apps/`.
  The {v('q25', 'bugs')} bugs here are the traced ones whose causing change falls in that list.
- **Why it matters.** Finding 3 uses the word "feat" in a change's title, which only {v('q03', 'rate_commits_feat')}
  commits carry. Adding a file is a fact, not a label, and it marks the same thing: new code is where the bugs are.
- **What it does not show.** That the bug sits in the new file. It says the change that carried the bug also added
  one.

{run_line('q24')}

### 2. New code that never worked accounts for about as many bugs as working things broken later

*Supported. About even by the main model in both periods; about double by the second model on the November
fixes. Neither puts never-worked bugs clearly below.*

Of the {v('q02', 'traced')} bugs we could trace to the change that introduced them, {v('q02', 'sens_never_all')} were
new code that was wrong from the start and {v('q02', 'sens_broke_all')} were working things that a later change
broke. The two kinds need different defenses. A test of the old behavior can catch a broken-later bug. A
never-worked bug has no old behavior to test against, so the only chance to catch it is when the new code is
reviewed or first run.

{chart('q02', 0)}

{numbers('q02', 'sens_never', 'sens_broke', 'never_share', names=['Never worked', 'Broken later', 'Never worked, %'])}

Across the main model's ways of counting, the ratio of never-worked to broken-later runs from
{v('q02', 'ratio_low')} to {v('q02', 'ratio_high')}. The second model, on the November fixes, put it at
{v('q02', 'other_ratio')}. The two models split a bug between these two kinds differently more often than they
disagree on which change caused it.

- **How we know.** The model had to point at the lines in the causing change that were wrong, and to say whether the
  behavior had worked before that change.
- **How it was checked.** Where two runs of the main model both chose one of these two kinds, they made the same
  choice in {v('q02', 'second_pair_same')} of {v('q02', 'second_pair_n')} cases. The two models made the
  same choice in {v('q02', 'other_pair_same')} of {v('q02', 'other_pair_n')}, and named the same causing change in
  {v('q02', 'other_cause_same')} of {v('q02', 'other_cause_n')}.
- **What it does not show.** A firm ratio, or that features are the problem. New code arrives in changes of every
  title, as the next finding shows.

{run_line('q02')}

### 3. Changes titled as new features cause far more than their share of bugs

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
  each bug is the model's judgment from finding 2.
- **What it does not show.** What the change was really for, or how much of the gap is size. The rates are not
  adjusted for the size of the change. A rate counts the bugs fixed between 10 September and 22 November, so it grows
  with the length of the period watched: compare these rates with each other, not with another study's.

{run_line('q03')}

### 4. Large changes cause far more bugs per change, but about the same per file changed

*Well supported. The per-file figures vary by less than a factor of two across size groups.*

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
  one sampled fix traced to a causing commit in that list ({v('q04', 'bugs')} cases), scaled from the sample to all
  fixes in the period. So a rate reads as "bugs fixed between 10 September and 22 November, per 100 commits made in
  that time".
- **How it was checked.** Sizes come from git. The causing commit is the model's judgment; the two models named
  the same one in {v('q02', 'other_cause_same')} of {v('q02', 'other_cause_n')} cases.
- **What it does not show.** Risk per line, or whether splitting a large change would lower the total. It also
  counts only bugs fixed within the period, so slow-to-surface bugs from recent changes are missing.

{run_line('q04')}

### 5. A broken thing typically stayed broken for one to four weeks

*Supported. Dates come from git. The split depends on the model naming the right causing change, and the figure for
the earlier weeks is cut short by how far back a cause could be traced.*

{chart('q05', 0)}

{chart('q05', 1)}

{numbers('q05', 'age')}

Half of the broken-later bugs were fixed within {v('q05', 'median_broke')} days of the change that broke them. For
fixes merged in November the figure is {v('q27', 'days_frame1')} days; for fixes merged from 10 September to
1 November it is {v('q27', 'days_frame2')}. Only {v('q05', 'named_count')} of the {v('q05', 'broke_count')}
broken-later fixes say which change caused the bug, and those were fixed within a day. Scaled from the sample, about
{v('q05', 'broke_scaled')} broken-later bugs were fixed in the period (plausibly {span('q05', 'broke_scaled')}).

- **How we know.** Days are the commit time of the fix minus the commit time of the causing change, both on main.
- **How it was checked.** An earlier study that could only find fixes naming their cause had put the typical time at
  {v('q05', 'first_study_median_days')} days. The random sample shows that figure described the quick cases only.
- **What it does not show.** How long users were affected, or how many noticed. A bug counts only once it is fixed,
  so long-lived bugs still open are missing. The model could trace causes back to 1 July 2026 and no further, so a
  fix from September cannot show a bug older than about ten weeks, where one from November can show one of twenty.
  That alone makes the earlier weeks look quicker.

{run_line('q05')}

## What review caught, and what it could have

Findings 6 to 10: what the project's review bot had said before each bug-causing change merged, and what other
models find when shown the same changes with no hint. Findings 7 to 10 cover November only.

### 6. The review bot had rarely named the bug before the change merged

*Well supported. The November cases were read by both models, with close agreement.*

For each of the {v('q06', 'traced')} traced bugs we read what the bot had written on the causing change at the moment
it merged, rebuilt from the comment's edit history. It had reviewed {v('q06', 'reviewed')} of them and named the bug
in {v('q06', 'flag_exact')}. It raised a related concern, without stating the failure, in
{v('q06', 'flag_related')}.

{chart('q06', 0)}

{numbers('q06', 'other_first', 'other_flag', names=[f'Main model ({MAIN})', f"Second model ({OTHER})"])}

{chart('q06', 1)}

{chart('q06', 2)}

Warnings were not being ignored. {v('q06', 'merged_against')} changes merged while the bot said "blocked" or "needs
changes", but in {v('q06', 'merged_against_unrelated')} of them its open items were about something other than the
bug, such as missing proof. Only {v('q06', 'open_unanswered')} items that touched the bug were open and unanswered at
merge. The bot also said "ready" on changes that carried a bug. Finding 12 adds the other half: although its words
rarely named the bug, the changes it objected to were the riskier ones.

- **How we know.** A model compared each bug with the review text under a strict rule: it counts as named only if
  fixing what the review described would have prevented the bug.
- **How it was checked.** For {v('q06', 'other_n')} November cases both models read the same review of the
  same causing change. They gave the same answer for {v('q06', 'other_same')}, and agreed on whether the bug was
  named for {v('q06', 'other_exact_same')}.
- **What it does not show.** How many bugs the bot stopped. A bug it caught and the author fixed before merge never
  appears in a sample of later fixes. This is a measure of what got past it, not of its worth.

{run_line('q06')}

### 7. Two current models together named more of the known bugs than the bot had

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

### 8. Most of the other problems those models reported hold up when checked

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

- **How we know.** The reports were pooled under anonymous labels with nothing marking the known bugs. One model
  searched later fix commits; two checkers each traced every report in the exported code.
- **How it was checked.** The checkers were tested on the known-real problems, first on the original code and then on
  the code after the fix. After the fix, both still confirmed {v('q08', 'control_both_still')}; two of those belong
  to a fix that was only partial.
- **What it does not show.** That the unfixed reports matter enough to block a merge. The two checkers are the same
  two models that wrote the reports, so they could share a convincing mistake. A failing test would settle it; none
  was written.

{run_line('q08')}

### 9. About a third of the bugs could not be seen by reading code

*Tentative. One model's judgment on 30 cases; the key group is nine.*

{chart('q09', 0)}

No reviewer named a bug that depended on how a browser lays out a page, what a database accepts or how a filesystem
behaves under load. Size mattered too: reviewers named {v('q09', 'small_named')} of {v('q09', 'small_cases')} bugs in
changes of 7 files or fewer, and {v('q09', 'large_named')} of {v('q09', 'large_cases')} in larger ones.

- **How we know.** A model given the bug and the causing change chose the least demanding thing a reviewer would
  have needed: the changed lines, other repository code, or outside knowledge.
- **How it was checked.** It was not checked by a second model. The model flagged several close calls between the
  first two groups.
- **What it does not show.** A firm share. Nine cases cannot fix a proportion; they show that such bugs exist in
  number and that none was caught by reading.

{run_line('q09')}

### 10. Most bugs broke no written rule

*Tentative. A sample found by commit wording, which later proved to favor quickly fixed bugs.*

The project keeps written rules for contributors and for the bot. In the first study, of {v('q10', 'confirmed')} bugs
whose fix names the causing change, a rule existed for {v('q10', 'rules_existing')} when the change was written, and
{v('q10', 'rules_checkable')} of those could have been checked from the changed lines alone.

{chart('q10', 0)}

{run_line('q10')}

## Which changes carry the bugs

Findings 11 to 21: the traced bugs set against every commit and pull request of the period. Nothing here is judged
by a model; it is counted from git and GitHub.

### 11. Changes committed straight to main caused fewer bugs per change, not more

*Supported per change; much of the gap is size. The direct-commit side rests on {v('q11', 'bugs_direct')} sampled
bugs.*

{v('q11', 'direct_share_pct')}% of commits since 10 September reached main with no pull request number in the title.
Per commit they carried {v('q11', 'direct_ratio')} times the bugs of changes that went through a pull request
(plausibly {span('q11', 'direct_ratio')}).

{numbers('q11', 'commits', 'bugs', 'per_commit', names=['Commits', 'Sampled bugs', 'Bugs per 100 commits'])}

They are also smaller (a median of {v('q11', 'median_files_direct')} files against {v('q11', 'median_files_pr')}),
so size explains part of the gap. Within changes of 6 files or more, the rate was
{v('q11', 'strat_direct_larger')} for direct commits against {v('q11', 'strat_pr_larger')} through a pull request.

- **How we know.** Same method as finding 4, split by whether the commit title carries a pull request number.
- **How it was checked.** It was not checked further.
- **What it does not show.** Who made the direct commits or why, or that skipping a pull request is safe: the
  changes people commit directly are the ones they judge routine. Finding 12 takes up changes merged against the
  review bot's verdict.

{run_line('q11')}

### 12. Changes merged while the bot objected carried more bugs

*Supported. A comparison with ordinary changes, with size held equal. It shows a link, not a cause.*

Findings 1 to 11 start from bugs. To ask whether a kind of change causes more bugs, we also need to know how common
that kind is among ordinary changes. So we drew {v('q12', 'verdict_sample')} merged pull requests at random and
recorded, for each, what the bot's review said at the moment it merged. The bot had called
{v('q12', 'verdict_share_ready')}% of them ready and objected to {v('q12', 'verdict_share_objected')}%, which merged
anyway.

{chart('q12', 0)}

Changes merged over the bot's objection caused sampled bugs {v('q12', 'verdict_ratio_objected')} times as often as
changes it called ready (plausibly {span('q12', 'verdict_ratio_objected')}). The bot objects more to large changes,
and large changes carry more bugs, so part of that is size. Comparing only changes of similar size that landed in
the same month, the ratio is
{v('q12', 'verdict_adjusted_objected')} (plausibly {span('q12', 'verdict_adjusted_objected')}). Changes the bot never
reviewed were no different from ones it called ready.

{ratio_table('q12', 'verdict')}

- **How we know.** The comparison sample says how common each verdict is; the bug-causing changes say how many
  sampled bugs came from each. The ratio of those two is the relative bug rate. "Similar size" means within three
  groups: 1 to 5 files, 6 to 30, and over 30. The month is held equal because an older change has had longer for its
  bugs to be found and fixed.
- **How it was checked.** The verdict is read mechanically from the marker the bot writes into its own comment, for
  the last version written before the merge. The causing change is the models' judgment (finding 2).
- **What it does not show.** That merging against the verdict causes bugs. The bot objects to changes that are
  harder for other reasons too. And finding 6 still holds: in most of these cases its open items were about something
  other than the bug.

{run_line('q12')}

### 13. Merging soon after the bot's review shows no clear extra risk

*Tentative. The intervals include no difference.*

{ratio_table('q13', 'coverage')}

{ratio_table('q13', 'speed')}

Changes where the bot had seen only an earlier revision carried {v('q13', 'coverage_adjusted_earlier')} times the
bugs of those where it had seen the merged one (plausibly {span('q13', 'coverage_adjusted_earlier')}). Changes
merged within ten minutes of the bot's review carried {v('q13', 'speed_adjusted_fast')} times the bugs of those
merged an hour or more later (plausibly {span('q13', 'speed_adjusted_fast')}). Both ranges include no difference.

- **How we know.** Same method as finding 12, using which revision the bot reviewed and the minutes from its review
  to the merge.
- **What it does not show.** That speed is safe. Quick merges are mostly small, simple changes; the comparison cannot
  say what would happen if the hard ones were merged as fast.

{run_line('q13')}

### 14. Pull requests merged within the hour carried far fewer bugs than those open a day or more

*Supported for time open. On who opened or merged a change, this sample of 400 is too thin; finding 19 asks the same
of every pull request.*

{chart('q14', 0)}

{ratio_table('q14', 'open')}

Pull requests merged within an hour of being opened carried {v('q14', 'open_adjusted_hour')} times the bugs of those
open a day or more, at equal size and month (plausibly {span('q14', 'open_adjusted_hour')}). A change that stays open is
usually one that needed work, and those are the ones that later needed fixing.

The other three comparisons show no difference that can be told from none in this sample. They are given as tables,
not charts, because a bar would suggest a difference the numbers do not support.

{ratio_table('q14', 'author')}

{ratio_table('q14', 'merge')}

{ratio_table('q14', 'human')}

- **How we know.** Same method as finding 12. A maintainer here is a person who merged at least one of the fetched
  pull requests; GitHub's own member label misses people whose membership is private.
- **What it does not show.** That review by another person does not help. Only {v('q15', 'human_review_pct')}% of
  the sampled changes had one, and people chose to review the risky ones, so the two groups are not alike. Finding
  19 repeats the comparisons on every pull request.

{run_line('q14')}

### 15. How this project reviews and merges, in numbers

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

### 16. A screenshot or video in the pull request did not go with fewer bugs

*Supported. It shows what such pull requests are like, not what the screenshot did.*

The project asks for visual proof on visible changes, so we checked whether pull requests that carry it do better.
Screenshots and videos are attached almost only to interface changes, and interface changes cause more bugs than
others, so the fair comparison is among interface changes alone.

{chart('q16', 0)}

{ratio_table('q16', 'interface')}

Interface changes with a screenshot or video caused {v('q16', 'interface_adjusted_yes')} times the bugs of interface
changes without one, at equal size and month (plausibly {span('q16', 'interface_adjusted_yes')}).

- **How we know.** For each of the {v('q17', 'sample')} sampled pull requests and each bug-causing one, we read the
  description as it stood at merge and counted embedded pictures and videos. An interface change is one that touches
  files under `ui/` or `apps/`.
- **How it was checked.** Counts are mechanical. Nearly every description has an "Evidence" heading, so the heading
  alone says nothing; only an embedded picture or video counts here.
- **What it does not show.** That proof makes things worse. People attach screenshots to the changes a user will
  see, and a visible bug is the kind that gets noticed and fixed within weeks. What it does show is that a
  screenshot of the change working once is not a sign the change is safe.

{run_line('q16')}

### 17. The bugs are concentrated in changes that could be pointed at beforehand

*Supported. The three signs were picked after seeing the November fixes alone. On the full period, with four times
the bugs, they mark the same share.*

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
- **What it does not show.** That looking harder at those changes would have caught the bugs. Finding 7 bears on
  that. The earlier weeks are a partial test of the signs, not a clean one: both periods share one comparison
  sample of ordinary changes.

{run_line('q17')}

### 18. An individual's workload shows no effect; the project's busiest days carried more bugs

*Supported for individual workload. Tentative for busy days: it is one clear result among about thirty comparisons.*

The worry is simple: one person lands hundreds of changes a day, the project lands a thousand, and care must be
slipping. If that were so, changes landed under heavy load would cause more bugs than changes landed under light
load. We looked for that six ways.

For the median commit, its author landed {v('q18', 'median_author_load')} changes that same day, and the previous
one {v('q18', 'median_gap')} minutes earlier. On a typical day {v('q20', 'people_per_day')} accounts merge; one
account merges {v('q20', 'top_pct')}% of all pull requests and three accounts merge {v('q20', 'top3_pct')}%.

{commit_table(('q18', 'load', 'By how many changes the author landed that day'),
              ('q18', 'gap', "By how soon after the author's previous change"),
              ('q18', 'own', "By the author's own usual pace"),
              ('q20', 'load', 'By how many pull requests the person merging merged that day'),
              ('q19', 'busy', 'By how busy the whole project was that day'),
              ('q19', 'week', 'By day of the week'))}

Read each block against its first row.

- **The person.** Landing minutes after the previous change, having a heavier day than one's own usual, and merging
  many pull requests in a day show no clear difference. In the first block every level sits above the baseline, but
  the baseline is authors landing 1 to 5 changes a day, who are mostly occasional contributors and do better than
  everyone else (finding 19). Above that level the rate does not rise with load.
- **The project.** Changes landed on the busiest third of days carried {v('q19', 'busy_adjusted_busy')} times the bugs
  of changes landed on the quietest third (plausibly {span('q19', 'busy_adjusted_busy')}), with the middle third in
  between. The range starts close to no difference. Weekends are no different from weekdays.

- **How we know.** For each of the {v('q18', 'commits')} commits we counted how many the same author landed that
  day and how long since their previous one, and for each pull request how many the same person merged that day.
  The bugs are the {v('q18', 'bugs')} sampled bugs whose causing commit is among those commits. "At equal size, kind
  and time" compares changes of similar file count, the same title type (feat, fix, other), landed in the same
  half-month. Time has to be held equal because an older commit has had longer for its bugs to be found and fixed:
  September commits show {v('q27', 'rate_sep')} bugs per 100, November commits {v('q27', 'rate_nov')}.
- **What it does not show.** That the pace is harmless. A count per commit favors whoever cuts work into the most
  pieces, and a tired author's mistakes need not land on the same day. Busy days may also differ in what gets
  landed, in ways that size and title do not capture.

{run_line('q18')}; `python3 {SCRIPTS['q19']}`; `python3 {SCRIPTS['q20']}`

### 19. Changes from occasional contributors, and changes someone else merged, carried about half the bugs

*Supported. The two overlap: an outside contributor cannot merge their own change.*

Would more contributors mean more bugs? One way to ask is whether changes from people who contribute rarely cause
more bugs than changes from the regulars. They cause fewer.

{commit_table(('q22', 'who', 'By how much the author contributes'),
              ('q21', 'merge', 'By who merged it'),
              ('q21', 'pair', 'The same, only for authors who can merge'),
              ('q21', 'review', 'By whether another person reviewed it'))}

- The {v('q22', 'authors_occasional')} authors with 20 commits or fewer wrote {v('q22', 'who_share_occasional')}% of
  commits and caused {v('q22', 'who_adjusted_occasional')} times the bugs per change of the most active author
  (plausibly {span('q22', 'who_adjusted_occasional')}).
- Among everyone else, how much an author contributes makes no clear difference.
- Changes merged by someone other than their author carried {v('q21', 'merge_adjusted_other')} times the bugs
  (plausibly {span('q21', 'merge_adjusted_other')}). Most of these are outside contributors' changes. Among authors
  who could have merged it themselves the ratio is {v('q21', 'pair_adjusted_other')} (plausibly
  {span('q21', 'pair_adjusted_other')}), on only {v('q21', 'pair_bugs_other')} bugs.
- Only {v('q21', 'review_commits_reviewed')} commits came from a pull request another person had reviewed, which is
  too few to say anything.

- **How we know.** Authors are grouped by how many commits they landed since 10 September. Who merged and who
  reviewed comes from GitHub, for all {v('q15', 'pulls')} merged pull requests.
- **What it does not show.** That a second person's merge prevents bugs. A change an outsider sends and a maintainer
  accepts is usually a small, targeted repair, and title and file count do not fully capture that. Whether review by
  a second person would help stays open: it is hardly practised here. Authors are told apart by commit email, so one
  person with two addresses counts twice.

{run_line('q22')}; `python3 {SCRIPTS['q21']}`

### 20. Changes to files that several other people were also editing caused more bugs

*Supported for the most-shared files. It cannot separate "too many hands" from "the busiest, most central code".*

{chart('q23', 0)}

{commit_table(('q23', 'shared', 'By how many other people changed the same files in the previous 14 days'),
              ('q23', 'familiar', 'By whether the author had changed those files before'))}

When two or more other people per file had changed the files a change edits in the previous two weeks, the change
caused {v('q23', 'shared_adjusted_high')} times the bugs (plausibly {span('q23', 'shared_adjusted_high')}) of a
change to files that only its author had been editing. With one to two other people the difference is not clear.

Being new to the files did not hurt. Authors editing only files they had never changed before caused
{v('q23', 'familiar_adjusted_none')} times the bugs of authors who had changed all of them (plausibly
{span('q23', 'familiar_adjusted_none')}): fewer, not more. The middle row, changes that reach beyond the author's own
files into others, is the higher one.

- **How we know.** For every code file a commit edits, we counted the other authors who had changed that file in
  the 14 days before, and averaged over the commit's files. Only commits that edit existing code are compared.
- **What it does not show.** That several people editing a file is what causes the bugs. Files many people edit are
  also the central ones where most things connect, and this data cannot tell those two apart.

{run_line('q23')}

### 21. Nearly every bug-causing change came with tests; no part of the code stands out

*Measured.*

{commit_table(('q25', 'tests', 'Among commits that change code: with or without tests'),
              ('q26', 'part', 'By the part of the code the commit touches'))}

- {v('q25', 'tests_bugs_with')} of the {v('q25', 'bugs')} sampled bugs came from a change that also changed test files.
  The tests that came with a change did not catch the bug it carried.
- Code changes with no test file are few and small (refactors, chores, small fixes) and caused
  {v('q25', 'tests_bugs_without')} of the sampled bugs, {v('q25', 'tests_adjusted_without')} times the rate of
  changes with tests. This is not evidence that skipping tests is safe: the two groups are different kinds of change.
- Interface changes cause more bugs per commit than core changes, but they are also larger. At equal size, kind and
  time, interface, plugin and core changes are alike.

- **How we know.** A test file is one whose path marks it as a test (`.test.`, `.spec.`, `.e2e.`, a `test` or
  `fixtures` folder). Each commit is put in one part of the code by the folders it touches.
- **What it does not show.** Whether the tests were good, or whether they ran. No test was run for this study.

{run_line('q25')}; `python3 {SCRIPTS['q26']}`

## Does it hold up

Findings 22 and 23: the same questions asked of a second period and of a second model, and the one answer that
depends on which model is asked.

### 22. The earlier weeks look like November; what differs is the model

*Supported. This is the check on everything above: a second period, and a second model.*

Every fix was read by {MAIN}. The {v('q01', 'other_n')} November fixes were also read by a model from a different
maker, {OTHER}. That gives three sets to put side by side. The first two are the same November fixes read by two
models, so their difference is the model. The last two are one model reading two periods, so their difference is
the period.

{chart('q27', 0)}

{chart('q27', 1)}

{numbers('q27', 'fixes', 'not_bug_pct', 'unclear_pct', 'never', 'broke', 'never_share', 'feat_pct', 'cause_files', 'days', 'reviewed', 'named',
         names=['Fixes', 'Fixed no bug, %', 'Could not tell, %', 'Never worked', 'Broken later', 'Never worked, % of the two', 'Causes titled feat, %', 'Median files in a causing change', 'Median days broken, broken-later', 'Causing changes the bot reviewed', 'Bot named the bug'])}

**The period changes little.** Under one model, November and the earlier weeks are close on how many fixes repaired
no bug ({v('q27', 'not_bug_pct_frame1')}% and {v('q27', 'not_bug_pct_frame2')}%), on the split between never-worked and
broken-later ({v('q27', 'never_share_frame1')}% and {v('q27', 'never_share_frame2')}% never-worked), on how large a
causing change is, and on how rarely the bot named the bug. The one clear gap is how long a broken thing stayed
broken, and finding 5 explains why that one cannot be trusted across periods.

**The model changes one thing a lot.** On the same November fixes, {OTHER} said {v('q27', 'not_bug_pct_published')}%
repaired no bug and {MAIN} said {v('q27', 'not_bug_pct_frame1')}%. They also split never-worked from broken-later
differently. But where both named a causing change, they named the same one in {v('q02', 'other_cause_same')} of
{v('q02', 'other_cause_n')} cases, and every finding that counts bugs by kind of change depends on the causing change, not on the label.

- **How we know.** The same brief was given to both models. {OTHER} read the November fixes first, with GitHub
  lookups; {MAIN} read every fix later, without them.
- **What it does not show.** That another project, or another season of this one, would look the same. And the two
  periods share one commit list and one sample of ordinary changes, so they are not fully separate tests of
  findings 11 to 21.

{run_line('q27')}

### 23. How many "fix" changes repair no bug depends on which model you ask

*Depends on the model. We gave two models the same written rule for what counts as a bug. They drew the line in
different places, and each gave nearly the same answers when asked a second time.*

We drew {v('q01', 'sample')} fixes by lottery from the {v('q01', 'population')} merged in the period and asked of
each: what was broken, and how did it get that way? The main model found that nothing had been broken in
{v('q01', 'origin_not-a-defect')} of them ({v('q01', 'not_bug_pct')}%): they were redesign steps, speed-ups, wording
changes or tooling work that carried the title "fix". The second model, reading the
{v('q01', 'other_n')} November fixes under the same rule, said so of {v('q01', 'other_notbug_pct')}%. The cases they
dispute are improvements that can also be described as a flaw present from the start: a slow path made faster, a log
message made more precise, a report that never fitted a phone screen.

{chart('q01', 0)}

{numbers('q01', 'origin')}

{chart('q01', 1)}

{numbers('q01', 'other_first', 'other_second', names=[f'Main model ({MAIN})', f"Second model ({OTHER})"])}

- **How we know.** One model read each fix, working from the fix's diff, its PR text and the history of the changed
  lines, with a written rubric that told it to answer "could not tell" when the evidence was thin.
- **How it was checked.** A second run of the main model, blind to the first answer, re-read
  {v('q01', 'second_n')} fixes and agreed on bug or not a bug for {v('q01', 'second_real_same')}. The second model's
  model had read {v('q01', 'other_n')} of the same fixes and agreed for {v('q01', 'other_real_same')}. So each
  model is steady, and the two differ.
- **What it does not show.** A single right number. Treat the main model's share as the lower end and the second
  model's third as the upper end. The main model also answered "could not tell" for {v('q01', 'origin_unclear')}
  fixes: it worked without GitHub lookups, so it could not trace anything older than 1 July 2026. It cannot show
  bugs nobody has fixed yet, or bugs fixed under another title.

{run_line('q01')}

## {OPINION}

*This section is my opinion. It is speculative and not part of the study. The study shows where the bugs are; it
does not show that any of the checks below would catch them.*

**The obvious one: stop treating every change the same.** Three signs are visible before a change merges: the bot
objected, the pull request was open a day or more, it touched more than 30 files.

| Changes with | Share of changes | Share of bugs | Later-fixed bugs per change |
|---|---:|---:|---:|
| Two or more signs | {v('q17', 'changes_pct_two')}% | {v('q17', 'bugs_pct_two')}% | {v('q17', 'per_change_two')} |
| No sign | {v('q17', 'changes_pct_none')}% | {v('q17', 'bugs_pct_none')}% | {v('q17', 'per_change_none')} |

- **Look harder at the flagged {v('q17', 'changes_pct_two')}%.** It is a small enough slice to afford a deep
  review. Expect that to turn up real problems, but not necessarily the one that later needs fixing (see the end of
  this section).
- **Let the unflagged {v('q17', 'changes_pct_none')}% flow.** Fast merges were the safe ones, and nothing suggests
  slowing them would help.

**Two that follow from it.**

- **Treat "needs changes" or "blocked" as a stop sign, not a comment.** {v('q17', 'changes_pct_objected')}% of
  changes merge over the bot's objection, and they carry {v('q17', 'bugs_pct_objected')}% of the bugs. The cheapest
  rule is that such a change does not merge on its author's say alone, even when the bot's complaint looks unrelated.
- **For new code, do not take the tests' word for it.** Changes adding a code file carry
  {v('q24', 'bugs_pct_adds')}% of the bugs, and {v('q25', 'tests_bugs_with')} of {v('q25', 'bugs')} traced bugs came
  from changes that shipped with tests. So the author's tests are not the safety net. Even after trying several
  ways, prompts and models, I also do not have a check that is.

**What the data says not to do.** These are just as actionable, because they are the rules a team reaches for
first.

- **Require tests or screenshots as a gate.** Both were present on the changes that broke.
- **Slow people down or cap throughput.** Workload shows no effect, and the bug rate barely depends on who lands the
  change.
- **Add a second reviewer to everything.** It happens on {v('q15', 'all_second_review_pct')}% of pull requests, so
  the data cannot say it helps.
- **Worry about outside contributors.** Their changes were the safer ones.

**I tried it, informally.** I took {read['changes']} flagged changes that later caused a known bug and had AI
reviewers read each one as it was before merge, with no hint. One ordinary review wrote the known bug down in
{read['one_review']} of the {read['changes']}. Then I piled on: different prompts, a stronger model, second passes,
and narrow reviews that each ask one question, such as "what happens after a restart?". About
{read['reviews_per_change']} reviews per change, pooled, wrote it down in {read['pooled']} of the
{read['changes']}. So brute force works, up to a point 🙂. The catch is the pile: about
{read['problems_per_change']} reported problems per change. They are mostly real. An agent tried {conf['tried']} of
them on built changes and {conf['happened']} really happened; the project just never fixed most of them. Building
and running the change found none of the known bugs: {ran['used_named']} of {ran['used_changes']} by using the
product, and {ran['compared_named']} of {ran['compared_changes']} by comparing it with the version before. So the
warning signs say where the bugs are, and enough reviewing writes about half of them down, but I have no way to turn
that pile into a short list a maintainer could act on. Some of the missed bugs were not bugs in the traditional
sense: the change did what it promised, and the maintainers later decided it should behave differently. Others were
judgment calls about how something should look. A generic check has no way to know either. This was done by hand and
is not part of the study; the details are in [one-off/looking-harder.md](one-off/looking-harder.md).

## {RESEARCH}

Only studies whose figures we could check against the paper or its abstract are quoted. None of them studied this
project, and none measured exactly what we measured, so read each row as "same direction or not", not as a ranking.

| What | This project | Published research | Reading |
|---|---|---|---|
| Bug-causing changes are larger | Median {v('q03', 'cause_median_files')} files against {v('q03', 'base_median_files')} for any commit | In Eclipse and Mozilla, changes that later needed a fix were about three times larger than others: 7.49 against 2.61 files, and 5.19 against 1.97 [1] | Same direction, and stronger here |
| Risk per change against risk per file | Per change, {v('q04', 'per_commit_ratio')} times higher for the largest; per file changed, flat | A model of change risk at Bell Labs found how widely a change spreads across the code essential to predicting failure [2] | Consistent: a bigger change is more exposure |
| Share of changes that are fixes | {v('q15', 'fix_title_pct')}% titled "fix" | 20.8% in Eclipse, 48.5% in Mozilla [1] | At the high end of what has been reported |
| Do fixes cause more bugs than other changes | No: "fix" is {v('q03', 'cmp_cause_fix')}% of causes and {v('q03', 'cmp_base_fix')}% of commits | Three times more in Eclipse, no difference in Mozilla [1]. 14.8% to 24.4% of operating-system bug fixes were themselves wrong [3]; nearly 40% of fault fixes led to further faults in one telecom system [4] | Unremarkable. Fixes that break things are normal everywhere |
| "Fixes" that fix no bug | {v('q01', 'not_bug_pct')}% to {v('q01', 'other_notbug_pct')}%, depending on the model | 33.8% of bug reports in five open-source projects were not bugs [5] | In line |
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
one account merges {v('q20', 'top_pct')}% of pull requests and three merge {v('q20', 'top3_pct')}%. Nothing
shows an individual is overloaded: a person's heavy days are no worse than their light ones, though the project's
busiest days are (finding 18). Changes from occasional contributors carry fewer bugs than the core's (finding 19).
Bugs are more common where several people edit the same files (finding 20). What stays open is whether a second pair of eyes helps, because only
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

## About this study

**Scope.** Changes merged to `main` from 10 September to 22 November 2026. One model ({MAIN}) read every fix.
A model from a different maker ({OTHER}) had earlier read the {v('q01', 'other_n')} November fixes, and its
answers serve as the check. No project code was run and no test was written. Findings 7 to 10 cover
November only. Findings 1, 3, 4 and 11 to 21 set the traced bugs against every commit and pull
request of the period. Findings 22 and 23 put the two periods and the two models side by side.

**An earlier version.** A first version of this report covered only the 300 November fixes, with {OTHER} as the
main model. It is kept as the tag `published-2026-11`, and [CORRECTIONS.md](CORRECTIONS.md) lists what changed.

**How this repository is organised.** `dataset/` holds the facts. `questions/` holds one script per question; each
reads only the dataset and writes the numbers and charts used on this page. `python3 study.py rebuild` runs them all and
re-renders this page. [PROTOCOL.md](PROTOCOL.md) is the experimental setup: every step of the study, and how to
regenerate it from nothing or extend it to other dates with one command and one settings file.
Claims that an earlier draft made and a later check weakened are listed in [CORRECTIONS.md](CORRECTIONS.md).

## How each study was done

| Study | Cases | How cases were chosen | Who judged | Independent check |
|---|---:|---|---|---|
| What fixes repaired | {v('q01', 'sample')} | Lottery over every fix in the period, in a fixed pseudo-random order | One {MAIN} model per fix | Second run of the same model on {v('q01', 'second_n')}; {OTHER} on the {v('q01', 'other_n')} November fixes |
| What the bot had said | {v('q06', 'reviewed')} | Every traced bug whose causing change the bot reviewed | One {MAIN} model per case | {OTHER} on {v('q06', 'other_n')} November cases with the same causing change |
| Blind review (November) | {v('q07', 'cases')} | First 15 of each kind in random order, among smaller recent changes the bot reviewed | Claude Opus 5.5 graders, blind to the reviewer | GPT grader on all pairs; run logs audited for leaks |
| Are the reports real | {v('q08', 'findings')} | Every report from the two strongest reviewers | One later-fix model; two code-tracing checkers | Known-real reports as a control, before and after the fix |
| Kinds of change compared | {v('q15', 'sample')} | Lottery over every merged pull request since 10 September, plus every bug-causing one | Nobody: read from git and GitHub | The bot's verdict is read from its own marker |
| Workload, people and files (findings 1 and 18 to 21) | {v('q18', 'commits')} | Every commit on main since 10 September; the bugs are the {v('q18', 'bugs')} sampled bugs whose causing commit is among them | Nobody: read from git and GitHub | Size and kind of change held equal; heavy-day result repeated without the most active author |
| Written rules (November, first study) | {v('q10', 'confirmed')} | Fixes whose wording blames an earlier change | Claude models, verdicts re-read | Three cases checked against source by hand |

## Limits that apply throughout

- Every classification is a model's judgment made in hindsight from code changes and PR text. Two models from different companies
  agreeing reduces the risk of one model's habit; it does not make the judgment a measurement.
- Nothing was executed. No bug was reproduced and no reported problem was confirmed by a failing test.
- The period is ten and a half weeks of one project. Finding 22 shows the earlier weeks agree with November; it
  does not show another project would.
- The main model worked without GitHub lookups and could trace a cause back to 1 July 2026 and no further. It
  answered "could not tell" more often than the second model, which had lookups.
- {v('q27', 'left_out')} of the {v('q02', 'traced')} traced bugs are left out of findings 1, 3, 4 and 11 to 21, because
  their causing change is older than 10 September, where the commit list starts, or was not a pull request.
- Findings 7 to 10 cover 30 November cases, chosen when {OTHER} was the main model, and were not repeated for the
  earlier weeks.
- A sample of fixes cannot see bugs that were never fixed, or bugs the bot stopped before merge.
- The model comparison covers changes of at most 30 files and one run per reviewer. The reviewers did not get
  identical guidance: some GPT runs read a personal review guide on the test machine, and the Claude runs had the
  repository's current contributor guide in context. Neither contains the answers.
- Findings 1 and 18 to 21 make about thirty comparisons on the same {v('q18', 'bugs')} bugs. By chance alone, one or two
  of thirty would look like a clear difference. The two we call supported (findings 1 and 20) are far from the
  line; the others that cross it are labelled tentative.
- The data files record the public author and merger of each change, as GitHub shows them. The report draws no
  conclusion about any person.

## All findings at a glance

Each finding carries a label for how far it can be trusted. **Measured** means counted from git or GitHub, with
nothing judged. **Well supported** means a large effect that held when checked a second way. **Supported** means a
clear effect resting on one method. **Tentative** means a small number of cases, or a range that barely clears "no
difference". **Depends on the model** means two models gave different answers.

| # | Strength | Finding |
|---|---|---|
| 1 | Well supported | Changes that add new code files are {v('q24', 'new_share_adds')}% of commits and the source of {v('q24', 'bugs_pct_adds')}% of the traced bugs. |
| 2 | Supported | New code that never worked accounts for about as many bugs as working things broken later: {v('q02', 'sens_never_all')} against {v('q02', 'sens_broke_all')} by the main model. The second model, on the November fixes, found twice as many never-worked. When both name a cause, they usually name the same change. |
| 3 | Well supported | Changes titled as new features cause far more than their share of bugs. The title "fix" tells you little. |
| 4 | Well supported | Large changes cause far more bugs per change, but about the same per file changed. |
| 5 | Supported | A broken thing typically stayed broken for one to four weeks, unless someone traced the cause at once. |
| 6 | Well supported | The review bot had rarely named the bug before the change merged: {v('q06', 'flag_exact')} of {v('q06', 'reviewed')}. |
| 7 | Supported, November only | Two current models together named more of the known bugs than the bot had. For either model alone, the gap could still be chance. |
| 8 | Supported, November only | Most of the other problems those models reported hold up when checked, and about a third of them are minor. |
| 9 | Tentative, November only | About a third of the bugs could not be seen by reading code at all. This rests on nine cases. |
| 10 | Tentative, November only | Most bugs broke no written rule. |
| 11 | Supported | Changes committed straight to main, without a pull request, caused fewer bugs per change, not more. |
| 12 | Well supported | Changes merged while the bot objected carried {v('q12', 'verdict_adjusted_objected')} times the bugs of changes it called ready, at equal size and month. Its objection marks risk even when its words do not name the bug. |
| 13 | Tentative | Merging minutes after the bot's review, or after it saw only an earlier revision, shows no clear extra risk. |
| 14 | Supported | Pull requests merged within the hour carried far fewer bugs than those open a day or more. |
| 15 | Measured | {v('q15', 'self_merged_pct')}% of pull requests were merged by their own author. Another person reviewed {v('q15', 'all_second_review_pct')}% of them before the merge. |
| 16 | Supported | Attaching a screenshot or video did not go with fewer bugs. Among interface changes, those with one caused {v('q16', 'interface_adjusted_yes')} times as many, at equal size and month. |
| 17 | Supported | Bugs are concentrated. Changes with at least two of three warning signs are {v('q17', 'changes_pct_two')}% of changes and the source of {v('q17', 'bugs_pct_two')}% of traced bugs. |
| 18 | Supported, and one tentative result | An individual's workload shows no effect. Changes landed on the project's busiest days carried {v('q19', 'busy_adjusted_busy')} times the bugs of changes landed on its quietest. |
| 19 | Supported | Changes from occasional contributors, and changes merged by someone other than their author, carried about half the bugs. Review by a second person is too rare to measure. |
| 20 | Supported | Changes to files that two or more other people were also editing caused {v('q23', 'shared_adjusted_high')} times the bugs of changes to files only their author was editing. |
| 21 | Measured | {v('q25', 'tests_bugs_with')} of the {v('q25', 'bugs')} traced bugs came from a change that also changed tests. No part of the code stands out. |
| 22 | Supported | The earlier weeks look like November when the same model reads both. What differs is the model: the two models disagree on what counts as a bug, and agree on what caused one. |
| 23 | Depends on the model | Between about a tenth and a third of changes titled "fix" repair no bug. Two models drew the line differently, and each was consistent with itself. |

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
| `one-off/` | A test done by hand outside the study: does looking harder at a flagged change find the bug? |
"""


def anchor(title):
    """The link GitHub gives a heading: lower case, punctuation dropped, spaces turned into hyphens."""
    kept = "".join(ch for ch in title.lower() if ch.isalnum() or ch in " -_")
    return "#" + kept.replace(" ", "-")


def contents(text):
    """A table of contents from the report's own headings: sections, with each finding under its group."""
    lines = ["## Contents", ""]
    for line in text.split("\n"):
        if line.startswith("## ") and line[3:] not in ("Main results", "Contents"):
            lines.append(f"- [{line[3:]}]({anchor(line[3:])})")
        elif line.startswith("### ") and line[4:5].isdigit():
            lines.append(f"  - [{line[4:]}]({anchor(line[4:])})")
    return "\n".join(lines)


def main():
    text = report()
    text = text.replace("<!-- contents -->", contents(text))
    with open(os.path.join(ROOT, "README.md"), "w") as handle:
        handle.write(text)
    print(len(text), "characters,", sum(len(c) for c in CHARTS.values()), "charts")
    if MISSING:
        print(f"NOTE: the report text asks for {len(set(MISSING))} numbers or charts that this study did not produce; "
              "they read \"(not available)\". The text was written for the published settings: " +
              ", ".join(sorted(set(MISSING))[:12]) + (" ..." if len(set(MISSING)) > 12 else ""))


if __name__ == "__main__":
    main()
