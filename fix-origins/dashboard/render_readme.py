#!/usr/bin/env python3
"""Render the top-level README.md (the report) from the data files, so its numbers cannot drift from the data.

Usage: python3 fix-origins/dashboard/render_readme.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FILES = {"fix": "fix-origins-sample.json", "bot": "clawsweeper-reviews.json", "pilot": "blind-review-pilot.json",
         "checks": "finding-checks.json", "named": "named-cause-study.json"}
DATA = {key: json.load(open(os.path.join(HERE, name))) for key, name in FILES.items()}
EXTRA = json.load(open(os.path.join(ROOT, "audit", "size-and-route.json")))


def v(source, metric):
    row = next(r for r in DATA[source] if r["metric"] == metric)
    value = row["value"]
    return f"{value:,}" if isinstance(value, int) else str(value)


def rng(source, metric):
    row = next(r for r in DATA[source] if r["metric"] == metric)
    return f"{row['low']}–{row['high']}%"


def table(source, group, header, with_range=False, unit=""):
    rows = [r for r in DATA[source] if r["group"] == group]
    lines = [f"| {header} | Count |" + (" Plausible share |" if with_range else ""), "|---|---:|" + ("---:|" if with_range else "")]
    for r in rows:
        lines.append(f"| {r['label']} | {r['value']}{unit} |" + (f" {r['low']}–{r['high']}% |" if with_range else ""))
    return "\n".join(lines)


def duo(source, group_a, group_b, header, name_a, name_b, unit=""):
    first = [r for r in DATA[source] if r["group"] == group_a]
    second = {r["label"]: r for r in DATA[source] if r["group"] == group_b}
    lines = [f"| {header} | {name_a} | {name_b} |", "|---|---:|---:|"]
    for r in first:
        other = second.get(r["label"])
        lines.append(f"| {r['label']} | {r['value']}{unit} | {other['value'] if other else '–'}{unit if other else ''} |")
    return "\n".join(lines)


def pilot_table():
    named = [r for r in DATA["pilot"] if r["group"] == "named"]
    second = {r["label"]: r["value"] for r in DATA["pilot"] if r["group"] == "named_second"}
    found = {r["label"]: r["value"] for r in DATA["pilot"] if r["group"] == "findings"}
    lines = ["| Reviewer | Known bugs named, of 30 | Plausible rate | Same count, second grader | Problems reported |",
             "|---|---:|---:|---:|---:|"]
    for r in named:
        lines.append(f"| {r['label']} | {r['value']} | {r['low']}–{r['high']}% | {second.get(r['label'], '–')} | "
                     f"{found.get(r['label'], '–')} |")
    return "\n".join(lines)


def extra_table(rows, first, columns):
    lines = ["| " + " | ".join([first] + [title for _, title in columns]) + " |", "|---|" + "---:|" * len(columns)]
    for row in rows:
        lines.append("| " + " | ".join([str(row[first.lower()])] + [f"{row[key]:,}" if isinstance(row[key], int) else str(row[key]) for key, _ in columns]) + " |")
    return "\n".join(lines)


REPORT = f"""# Where OpenClaw's bugs come from

An independent study of the public [openclaw/openclaw](https://github.com/openclaw/openclaw) repository. It is not
affiliated with or endorsed by the OpenClaw project. It judges changes, not people.

We traced a random sample of {v('fix', 'sample')} fixes from three weeks back to what each one repaired. By the first
readers' count, {v('fix', 'origin_never-worked')} were new code that never worked and {v('fix', 'origin_regression')}
were working things broken by a later change; a second model put the two kinds closer to even. The project's review
bot had named the bug in {v('bot', 'flag_exact')} of the {v('bot', 'reviewed')} bug-causing changes it reviewed. Two
current models, shown {v('pilot', 'cases')} of those changes with no hint, each named {v('pilot', 'named_gpt62')}.

**Scope.** Changes merged to `main` from 1 to 22 November 2026. Model readers did the classifying; a second model
from a different maker re-read the three central judgments. No project code was run and no test was written.
Written 25 November 2026.

## What the evidence supports, and how strongly

| Strength | Finding |
|---|---|
| Depends on definition | Between about a tenth and a third of changes titled "fix" repair no bug. Two models drew the line differently. |
| Supported | New code that never worked accounts for at least as many bugs as working things broken later: from about even ({v('fix', 'gpt_ratio')} to one, by a second model) to about double ({v('fix', 'ratio_high')} to one, by the first readers). |
| Well supported | When two makers' models both trace a bug to a cause, they name the same causing change. |
| Well supported | Bug-causing changes are much larger than ordinary ones, and new-feature changes cause far more than their share. |
| Well supported | A broken thing typically stayed broken for about three weeks, unless someone traced the cause at once. |
| Well supported | The review bot had rarely named the bug before the change merged. Ignored warnings were rare. |
| Supported | Two current models together named more of the known bugs than the bot had. For either model alone, the gap could still be chance. |
| Supported | Most of the other problems those models reported hold up when checked, and about a third of them are minor. |
| Tentative | About a third of the bugs could not be seen by reading code at all. This rests on nine cases. |

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

## Finding 1. How many "fix" changes repair no bug depends on what you call a bug

*Depends on definition. The sample is random and the first readers were consistent with each other, but a second
model drew the line elsewhere.*

We drew {v('fix', 'sample')} fixes by lottery from the {v('fix', 'population')} merged in the period and asked of
each: what was broken, and how did it get that way? By the first readers' strict rule, nothing had been broken in
{v('fix', 'origin_not-a-defect')} of them: they were redesign steps, speed-ups, wording changes or tooling work that
carried the title "fix". A model from a different maker, given the same written rule, called only
{v('fix', 'gpt_notbug_pct')}% of the fixes it re-read "not a bug". The cases they dispute are improvements that can
also be described as a flaw present from the start: a slow path made faster, a log message made more precise, a
report that never fitted a phone screen.

{table('fix', 'origin', "What each sampled fix repaired, by the first readers' rule", with_range=True)}

"Plausible share" is where the true share of all fixes in the period plausibly lies, given a sample of 300 (a 95%
interval).

- **How we know.** One model reader per fix worked from the fix's diff, its PR text and the history of the changed
  lines, with a written rubric that told it to answer "could not tell" when the evidence was thin.
- **How it was checked.** A second reader, blind to the first answer, re-read {v('fix', 'second_n')} fixes and agreed
  on bug or not a bug for {v('fix', 'second_real_same')}. A reader from a different model maker re-read
  {v('fix', 'gpt_n')} and agreed for only {v('fix', 'gpt_real_same')}.
- **What it does not show.** A single right number. Treat the first readers' third as the upper end and the second
  model's share as the lower end. It also cannot show bugs nobody has fixed yet, or bugs fixed under another title.

## Finding 2. New code that never worked accounts for at least as many bugs as working things broken later

*Supported. About double by the first readers' full count; closer to even under stricter cuts and under a second
model. Neither reading puts never-worked bugs clearly below.*

Of the {v('fix', 'traced')} bugs we could trace to the change that introduced them, {v('fix', 'sens_never_all')} were
new code that was wrong from the start and {v('fix', 'sens_broke_all')} were working things that a later change
broke. The two kinds need different defenses. A test of the old behavior can catch a broken-later bug. A
never-worked bug has no old behavior to test against, so the only chance to catch it is when the new code is
reviewed or first run.

{duo('fix', 'sens_never', 'sens_broke', 'The same comparison under stricter readings', 'Never worked', 'Broken later')}

Older causes are harder to trace, and a reader who cannot find an earlier working version may lean toward "never
worked". That is one reason the gap narrows when only confident or recent cases are kept. The last two rows are the
60 fixes a second model re-read; on that smaller set both readers put the two kinds about even.

- **How we know.** The reader had to point at the lines in the causing change that were wrong, and to say whether the
  behavior had worked before that change.
- **How it was checked.** Where two readers both chose one of these two kinds, they made the same choice in
  {v('fix', 'second_pair_same')} of {v('fix', 'second_pair_n')} cases. The reader from a different maker made the
  same choice in {v('fix', 'gpt_pair_same')} of {v('fix', 'gpt_pair_n')}, and named the same causing change in
  {v('fix', 'gpt_cause_same')} of {v('fix', 'gpt_cause_n')}.
- **What it does not show.** A firm ratio, or that features are the problem. New code arrives in changes of every
  title, as finding 3 shows.

### Check: a model from a different maker agrees on causes, and disagrees on what counts as a bug

All first readings were done by Claude models. A GPT model re-read {v('fix', 'gpt_n')} of the sampled fixes from the
same evidence, without the first answer. It chose the same category for only {v('fix', 'gpt_same')}. The difference
is in two places: it called far fewer fixes "not a bug", and it answered "could not tell" for
{v('fix', 'gpt_unclear')}; where neither reader said that, they agreed on {v('fix', 'gpt_decided_same')} of
{v('fix', 'gpt_decided_n')}.

{duo('fix', 'gpt_first', 'gpt_second', 'How each reader sorted the re-read fixes', 'First reader (Claude)', 'Second reader (GPT)')}

The second reader had the evidence bundle and local history only. It could not look up changes older than September
2026 on GitHub, which the first reader could.

## Finding 3. Bug-causing changes are large, and new-feature changes cause far more than their share

*Well supported. Measured against every commit on main in the same period, not against an estimate.*

For each traced bug we looked at the change that introduced it. Its title tells you little: {v('fix', 'title_fix')}
of the {v('fix', 'traced')} were themselves titled "fix", but so is about half of everything merged, and some of
those are large additions. One, titled as a fix, changed 138 files and added a whole rollback mechanism. Size and
newness tell you more.

{duo('fix', 'cmp_cause', 'cmp_base', 'Share of changes that are...', 'Bug-causing changes', 'All commits', unit='%')}

{duo('fix', 'title_never', 'title_broke', 'Title of the causing change', 'Never worked', 'Broken later')}

A causing change touched a median of {v('fix', 'cause_median_files')} files; an ordinary commit touches
{v('fix', 'base_median_files')}.

- **How we know.** The comparison uses the {v('fix', 'recent_causes')} causing changes made since 10 September 2026
  and all {v('fix', 'base_commits')} commits on main since that date, counted from git.
- **How it was checked.** File counts and titles are read mechanically from git, not judged. Which change caused each
  bug is the reader's judgment from finding 2.
- **What it does not show.** That large changes are worse per file. The first look below suggests they are not.

### First look: is a large change riskier per file, and does skipping a pull request matter?

These two tables come from data already collected and have not had a second check. A "bug" is one sampled fix traced
to a causing commit made since 10 September ({EXTRA['traced_bugs']} cases), scaled from the sample to the whole period.

{extra_table(EXTRA['by_size'], 'Size', [('commits', 'Commits'), ('sampled_bugs', 'Sampled bugs'), ('bugs_per_100_commits', 'Bugs per 100 commits'), ('bugs_per_1000_files_changed', 'Bugs per 1,000 files changed')])}

Per commit, a change of over 100 files carried about a hundred times the bugs of a small one. Per file changed, the
rate is roughly flat. On this evidence large changes hold more bugs because they hold more change, not because each
part of them is worse.

{extra_table(EXTRA['by_route'], 'Route', [('commits', 'Commits'), ('sampled_bugs', 'Sampled bugs'), ('bugs_per_100_commits', 'Bugs per 100 commits')])}

Commits made straight to main, with no pull request number in the title, did not carry more bugs per commit. They
are also smaller, and the count rests on five cases. Whether changes merged against the review bot's verdict carry
more bugs cannot be answered yet: that needs the verdicts on a comparison sample of changes that caused no bug.

## Finding 4. A broken thing typically stayed broken for about three weeks

*Well supported. Dates come from git. The split depends on the reader naming the right causing change.*

{table('fix', 'age', 'Broken-later bugs, by time from cause to fix')}

{table('fix', 'lifetime', 'Median days from the causing change to the fix')}

Only {v('fix', 'named_count')} of the {v('fix', 'broke_count')} broken-later fixes say which change caused the bug,
and those were fixed within a day. The rest took weeks. Scaled from the sample, about {v('fix', 'broke_scaled')}
broken-later bugs were fixed in the three weeks.

- **How we know.** Days are the commit time of the fix minus the commit time of the causing change, both on main.
- **How it was checked.** An earlier study that could only find fixes naming their cause had put the typical time at
  {v('named', 'median_days')} days. The random sample shows that figure described the quick cases only.
- **What it does not show.** How long users were affected, or how many noticed. A bug counts only once it is fixed,
  so long-lived bugs still open are missing and the true typical time is longer.

## Finding 5. The review bot had rarely named the bug before the change merged

*Well supported. Every case read twice, by models from two makers, with close agreement.*

For each of the {v('bot', 'traced')} traced bugs we read what the bot had written on the causing change at the moment
it merged, rebuilt from the comment's edit history. It had reviewed {v('bot', 'reviewed')} of them and named the bug
in {v('bot', 'flag_exact')}. Both readers agree on those. They differ on how often it raised a related concern:
{v('bot', 'flag_related')} by the first reader, {v('bot', 'gpt_flag_related')} by the second.

{duo('bot', 'flag', 'gpt_flag', 'What its review said about the bug', 'First reader (Claude)', 'Second reader (GPT)')}

{table('bot', 'status', 'Whether there was a review at all')}

{table('bot', 'verdict', 'Its overall verdict when the change merged')}

Warnings were not being ignored. {v('bot', 'merged_against')} changes merged while the bot said "blocked" or "needs
changes", but in {v('bot', 'merged_against_unrelated')} of them its open items were about something other than the
bug, such as missing proof. Only {v('bot', 'open_unanswered')} items that touched the bug were open and unanswered at
merge. The bot also said "ready" on changes that carried a bug.

- **How we know.** A reader compared each bug with the review text under a strict rule: it counts as named only if
  fixing what the review described would have prevented the bug.
- **How it was checked.** A reader from a different maker re-read all {v('bot', 'gpt_n')} and gave the same answer
  for {v('bot', 'gpt_same')}. On whether the bug was named, they agreed for {v('bot', 'gpt_exact_same')}. Both
  "named" cases were also read by hand.
- **What it does not show.** How many bugs the bot stopped. A bug it caught and the author fixed before merge never
  appears in a sample of later fixes. This is a measure of what got past it, not of its worth.

## Finding 6. Two current models together named more of the known bugs than the bot had

*Supported. Thirty smaller changes, one run each. Clear for the two models combined, not for either alone.*

We took {v('pilot', 'cases')} bug-causing changes and gave each reviewer the repository exactly as it stood at merge,
with no later history, and one plain instruction: find the defects this change introduces. Graders who did not know
which reviewer wrote what then checked whether any reported problem was the known bug.

{pilot_table()}

gpt-6.2 and Opus 5.5 together named {v('pilot', 'named_either_top')} bugs and overlapped on
{v('pilot', 'named_both_top')}, so they catch different things. How likely is a gap this large by luck alone?

| Comparison | Chance of a gap this large by luck |
|---|---:|
| The two top models together, against the bot | {v('pilot', 'p_two_vs_bot')} |
| One top model, against the bot | {v('pilot', 'p_one_vs_bot')} |
| One top model, against gpt-6.1 on the same instruction | {v('pilot', 'p_top_vs_gpt61')} |
| Three files at a time, against the whole change | {v('pilot', 'p_perfile')} |

The count is not a steady climb across model versions, and it follows how much each model reports. Of the
{v('pilot', 'named_any')} bugs that at least one reviewer named, {v('pilot', 'named_any_old')} had been live for more
than ten days.

- **How we know.** Cases were the first 15 broken-later and first 15 never-worked bugs, in the sample's random order,
  among those the bot had reviewed, with a causing change of at most 30 files made since 10 September.
- **How it was checked.** A grader from a different maker regraded all {v('pilot', 'grade_cells')} reviewer and case
  pairs and agreed on named or not for {v('pilot', 'grade_same')}. Logs show no reviewer read later history, the fix,
  or another case. Two PR descriptions that had been edited after merge to mention the fix were replaced with their
  merge-time text.
- **What it does not show.** A like-for-like contest with the bot. The bot reviewed at the time, sometimes an earlier
  revision, with its own long instructions. It also does not cover changes of more than 30 files, which are where
  most bugs come from.

## Finding 7. Most of the other problems those models reported hold up when checked

*Supported. A fifth are proven by later fixes. The rest rest on code reading by two models, with a control but no
executed test.*

A reviewer that reports a lot will name the known bug more often by volume alone, so the other reports matter.
gpt-6.2 and Opus 5.5 reported {v('checks', 'findings')} problems on the 30 changes; {v('checks', 'known')} were the
known bug. We checked each one two ways: was it later fixed on main, and do two checkers who trace the code agree the
failure happens?

{table('checks', 'quality', 'Where the reported problems stand')}

{duo('checks', 'control_original', 'control_fixed', 'Can the checkers say no? A test on the known-real problems', 'Wrongly dismissed, on the original code', 'Stopped confirming, once the bug was fixed')}

{v('checks', 'later_other')} of the other reports were later fixed on main by someone else, which is proof they were
real. That count is a floor: the same search found the fix for only {v('checks', 'later_found_known')} of the
{v('checks', 'control_cases')} problems we already knew were fixed.

- **How we know.** The reports were pooled under anonymous labels with nothing marking the known bugs. One reader
  searched later fix commits; two checkers each traced every report in the exported code.
- **How it was checked.** The checkers were tested on the known-real problems, first on the original code and then on
  the code after the fix. After the fix, both still confirmed {v('checks', 'control_both_still')}; two of those
  belong to a fix that was only partial.
- **What it does not show.** That the unfixed reports matter enough to block a merge. The two checkers are the same
  two models that wrote the reports, so they could share a convincing mistake. A failing test would settle it; none
  was written.

## Finding 8. About a third of the bugs could not be seen by reading code

*Tentative. One reader's judgment on 30 cases; the key group is nine.*

{duo('pilot', 'needs_cases', 'needs_named', 'What a reviewer had to have in front of them to see the bug', 'Cases', 'Named by at least one reviewer')}

No reviewer named a bug that depended on how a browser lays out a page, what a database accepts or how a filesystem
behaves under load. Size mattered too: reviewers named {v('pilot', 'small_named')} of {v('pilot', 'small_cases')}
bugs in changes of 7 files or fewer, and {v('pilot', 'large_named')} of {v('pilot', 'large_cases')} in larger ones.

- **How we know.** A reader given the bug and the causing change chose the least demanding thing a reviewer would
  have needed: the changed lines, other repository code, or outside knowledge.
- **How it was checked.** It was not checked by a second reader. The reader flagged several close calls between the
  first two groups.
- **What it does not show.** A firm share. Nine cases cannot fix a proportion; they show that such bugs exist in
  number and that none was caught by reading.

## Side finding. Most of these bugs broke no written rule

*Tentative. A sample found by commit wording, which later proved to favor quickly fixed bugs.*

The project keeps written rules for contributors and for the bot. In the first study, of {v('named', 'confirmed')}
bugs whose fix names the causing change, a rule existed for {v('named', 'rules_existing')} when the change was
written, and {v('named', 'rules_checkable')} of those could have been checked from the changed lines alone.

{table('named', 'rules', 'Did a written rule cover what went wrong?')}

## What this supports doing

1. **Add a plain "find the defects" pass by a current top model to the bot's review, and compare it on this benchmark
   first.** Rests on finding 6. The 30 cases and scripts can score any reviewer, so the claim can be re-tested before
   anything changes.
2. **Use two different models for that pass.** Rests on finding 6: the two overlapped on only
   {v('pilot', 'named_both_top')} of {v('pilot', 'named_either_top')}.
3. **Have a second model check each reported problem before a person sees it.** Rests on finding 7: the checkers
   could say no, and a third of confirmed reports were minor.
4. **Review large changes in parts, and mark any change the bot never reviewed.** Rests on findings 3 and 5.
   {v('bot', 'unreviewed_large')} traced bugs came from changes of 500 files or more that the bot acknowledged and
   did not review.
5. **Cover what reading cannot: run it.** Rests on finding 8, which is tentative. Browser checks for interface style
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
| What fixes repaired | {v('fix', 'sample')} | Lottery over every fix in the period, in a fixed pseudo-random order | One Claude Opus 5.5 reader per fix | Second Claude reader on {v('fix', 'second_n')}; GPT reader on {v('fix', 'gpt_n')} |
| What the bot had said | {v('bot', 'reviewed')} | Every traced bug whose causing change the bot reviewed | One Claude Opus 5.5 reader per case | GPT reader on all; both "named" cases read by hand |
| Blind review | {v('pilot', 'cases')} | First 15 of each kind in random order, among smaller recent changes the bot reviewed | Claude Opus 5.5 graders, blind to the reviewer | GPT grader on all pairs; run logs audited for leaks |
| Are the reports real | {v('checks', 'findings')} | Every report from the two strongest reviewers | One later-fix reader; two code-tracing checkers | Known-real reports as a control, before and after the fix |
| Written rules | {v('named', 'confirmed')} | Fixes whose wording blames an earlier change | Claude readers, verdicts re-read | Three cases checked against source by hand |

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

## Reproducing and extending this

Every number above is rebuilt from the data files in this repository by `./rebuild.sh`, with Python 3 and nothing
else. Re-fetching the public data and re-running the model readers are described in [REPRODUCE.md](REPRODUCE.md),
along with what cannot be reproduced exactly. Corrections made after a second-model check are listed in
[fix-origins/dashboard/README.md](fix-origins/dashboard/README.md).

| Folder | What it holds |
|---|---|
| `fix-origins/` | The random sample of 300 fixes: sampling frame, evidence bundles, readers' answers, scripts |
| `fix-origins/clawsweeper/` | The review bot's comments on the causing changes, as fetched, and the readers' verdicts |
| `fix-origins/review-pilot/` | The blind review: prompts, runner scripts, every reviewer's raw output, grades, and the checks on the reported problems |
| `fix-origins/audit/` | The second-model re-reads, the commit base rates, and the first look at size and route |
| `fix-origins/dashboard/` | The data files behind this report, the script that builds them, and this report's renderer |
| `detection-check/` | The first, wording-based study |
"""


def main():
    with open(os.path.join(os.path.dirname(ROOT), "README.md"), "w") as handle:
        handle.write(REPORT)
    print(len(REPORT), "characters")


if __name__ == "__main__":
    main()
