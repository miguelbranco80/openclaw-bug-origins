# Where OpenClaw's bugs come from

An informal, independent look at the public [openclaw/openclaw](https://github.com/openclaw/openclaw) repository.
It is not affiliated with the project. It judges changes, not people.

We took a random sample of 1,202 changes titled "fix", merged between 10 September and 22 November
2026, and traced each back to what it repaired and which earlier change had caused the problem. Then we set those
bugs against every commit and pull request of the period, to see which kinds of change carry them.

## Main results

Some of this is what any engineer would guess, and the value is in having a number for it. The rest we did not
expect.

**As you would expect, now with numbers**

- **New code is where the bugs are.** Changes that add a new code file are 13.7% of commits
  and the source of 69% of the traced bugs (346 of
  505). *Finding 1.*
- **Features cause more than their share.** Changes titled "feat" caused 123.7 bugs per 100
  commits, against 18 for changes titled "fix". *Finding 3.*
- **Bigger changes carry more bugs.** A commit of over 100 files carried about 131 times
  the bugs of one of 1 to 5 files. The less obvious part: per file changed, the rate is about the same. A big change
  is more exposure, not worse work. *Finding 4.*
- **Files that several people are editing at once carry more bugs:** 1.67 times, for
  files two or more other people had changed in the previous two weeks. *Finding 20.*

**What we did not expect**

- **Tests came with nearly every bug.** 494 of the 505 traced bugs came
  from a change that also changed tests. Shipping tests with a change is not a sign it is safe. *Finding 21.*
- **About half the bugs were never regressions.** 443 were new code that never worked,
  against 389 working things broken later. A test of the old behavior cannot catch the
  first kind. *Finding 2.*
- **The review bot rarely named the bug, yet its objection marks risk.** It had named the bug in
  21 of the 645 bug-causing changes it reviewed. Changes merged over its
  objection still carried 3.42 times the bugs of changes it called ready, even
  though its complaint was usually about something else. *Findings 6 and 12.*
- **You can point at the risky changes before they merge.** 6.8% of changes show at least
  two of three warning signs (the bot objected, the pull request was open a day or more, it touched more than 30
  files), and those changes carry 48% of the traced bugs. *Finding 17.*
- **A screenshot or video goes with more bugs, not fewer.** Among interface changes, those with one carried
  3.72 times the bugs. *Finding 16.*
- **Fast merges are the safe ones.** Pull requests merged within the hour carried far fewer bugs than those open a
  day or more: 0.28 times as many. *Finding 14.*
- **Nobody looks overloaded.** An author's heavy days are no worse than their light ones, although one account
  merges 54.3% of all pull requests. *Finding 18.*
- **Outsiders' changes are the safer ones.** Changes from people with 20 commits or fewer carried fewer bugs than
  the most active author's: 0.47 times as many. *Finding 19.*
- **Reading alone has a ceiling.** Two strong models, shown 30 bug-causing changes from November
  with no hint, together named 10 of the bugs. 9 could not be
  seen by reading code at all, and nobody named those. *Findings 7 and 9.*

**And it repeats.** We checked two ways. The fixes from September and October give the same picture as those from
November. And a second model, reading the same November fixes, pointed at the same causing change in
108 of 130 cases. Where the two models differ is on what counts as
a bug at all: one said 11% of those fixes repaired nothing, the other
33%. *Findings 22 and 23.*

**Share of the traced bugs that came from changes with each warning sign**

![Share of the traced bugs that came from changes with each warning sign](charts/q17-share-of-bugs-by-warning-sign-light.svg#gh-light-mode-only)
![Share of the traced bugs that came from changes with each warning sign](charts/q17-share-of-bugs-by-warning-sign-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the percentage of traced bugs whose causing change had that sign. The gray note says how common such changes are. A bar much longer than its note's percentage means bugs are concentrated there. The first three rows overlap; the last three are combinations of them.*

## What the numbers point to

These are ideas, not advice to the project. Each rests on a count in this report. None was tried here, and the
last column says which step from the count to the idea is untested.

| Idea | The count behind it | What was not tested |
|---|---|---|
| Decide where to look hard using signs visible before a change merges | 6.8% of changes carry 48% of the bugs. The signs were picked on November's bugs and marked the same share with four times as many | Whether looking hard at those changes would catch the bug |
| Treat the bot's objection as a flag, whatever its words say | Changes merged over its objection carried 3.42 times the bugs, although in 346 of 418 such cases its open items were about something else | Why those changes are riskier |
| Do not take the author's tests as a sign of safety; give new code a check its author did not write | 69% of bugs came from changes adding a code file; 494 of 505 traced bugs came from changes that shipped with tests | Whether an independent check would have caught them |
| For some bugs, run the thing; reading will not find them | 9 of 30 bugs needed knowledge that is not in the code, and no reviewer named any of them | Whether running it would. Thirty cases, November only |

Three things the numbers do not support as ideas. More reviewers: a second person reviews
1.0% of pull requests, too few to tell whether it helps (finding 19). Slowing people
down: an individual's workload shows no effect (finding 18). Asking for a screenshot: changes with one carried more
bugs, not fewer (finding 16).

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
  caused the problem. The main model, gpt-6.2-sol, read every fix. The second model, Claude Opus 5.5, comes from a different
  company and read the November fixes, so that one model's habits can be told apart from facts.
- **Review bot.** ClawSweeper, the automated reviewer that comments on the project's pull requests before they merge.
- **Plausible range.** Where the true figure plausibly lies given the sample size (a 95% interval).

## Where the bugs come from

Findings 1 to 5: what kind of change had introduced each problem, and how long it lasted.

### 1. Changes that add new code files caused two thirds of the bugs

**As expected.** *Well supported. Whether a change adds a file is counted from git, not judged. Findings 2 and 3 reach the same
place by other routes.*

**Bugs per 100 changes, by whether the change adds new code files**

![Bugs per 100 changes, by whether the change adds new code files](charts/q24-bugs-by-whether-the-change-adds-files-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by whether the change adds new code files](charts/q24-bugs-by-whether-the-change-adds-files-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the number of bugs per 100 changes of that kind. The gray note gives how many of the sampled bugs came from such changes and how common such changes are.*

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size, kind and time |
|---|---:|---:|---:|---|
| Only edits existing code files | 59.3% | 159 | 9.11 | (the baseline) |
| Adds at least one new code file | 13.7% | 346 | 86.01 | **3.18 times (plausibly 2.51 to 4.02)** |

A change that adds at least one new code file is 13.7% of commits and the source of
346 of the 505 traced bugs (69%). Such changes are
also larger than others, so we compared like with like: among changes of similar size, with the same kind of title,
landed in the same weeks, one that adds a file caused 3.18 times the bugs of one that
only edits existing files (plausibly 2.51 to 4.02).

- **How we know.** For each sampled fix, a model traced the problem back to the earlier change that caused it. We
  then looked up that change among all 39,210 commits on main since 10 September. Git records which
  files a commit adds. A code file is a non-test file under `src/`, `ui/`, `extensions/`, `packages/` or `apps/`.
  The 505 bugs here are the traced ones whose causing change falls in that list.
- **Why it matters.** Finding 3 uses the word "feat" in a change's title, which only 1,325
  commits carry. Adding a file is a fact, not a label, and it marks the same thing: new code is where the bugs are.
- **What it does not show.** That the bug sits in the new file. It says the change that carried the bug also added
  one.

Recompute: `python3 questions/q24_do_changes_that_add_new_files_cause_more_bugs.py`

### 2. New code that never worked accounts for about as many bugs as working things broken later

**Surprising.** *Supported. About even by the main model in both periods; about double by the second model on the November
fixes. Neither puts never-worked bugs clearly below.*

Of the 832 bugs we could trace to the change that introduced them, 443 were
new code that was wrong from the start and 389 were working things that a later change
broke. The two kinds need different defenses. A test of the old behavior can catch a broken-later bug. A
never-worked bug has no old behavior to test against, so the only chance to catch it is when the new code is
reviewed or first run.

**How much of the time the bug was new code that never worked, by three ways of counting**

![How much of the time the bug was new code that never worked, by three ways of counting](charts/q02-share-never-worked-light.svg#gh-light-mode-only)
![How much of the time the bug was new code that never worked, by three ways of counting](charts/q02-share-never-worked-dark.svg#gh-dark-mode-only)

*How to read it: Take only bugs that were one of two kinds: new code that never worked, or a working thing broken later. Each bar is the percentage that were the first kind. Past the dashed line means the first kind is the more common.*

<details><summary>The numbers behind this chart</summary>

| | Never worked | Broken later | Never worked, % |
|---|---:|---:|---:|
| Every traced bug | 443 | 389 | 53 |
| Model was confident or fairly confident of the cause | 443 | 389 | 53 |
| Model was confident of the cause | 399 | 336 | 54 |
| Cause is a commit since 10 Sep 2026, readable in full | 234 | 271 | 46 |
| Main model, on the fixes the second model also read | 115 | 91 | 56 |
| The second model, on the same fixes | 105 | 51 | 67 |

</details>

Across the main model's ways of counting, the ratio of never-worked to broken-later runs from
0.86 to 1.19. The second model, on the November fixes, put it at
2.06. The two models split a bug between these two kinds differently more often than they
disagree on which change caused it.

- **How we know.** The model had to point at the lines in the causing change that were wrong, and to say whether the
  behavior had worked before that change.
- **How it was checked.** Where two runs of the main model both chose one of these two kinds, they made the same
  choice in 121 of 127 cases. The two models made the
  same choice in 115 of 130, and named the same causing change in
  108 of 130.
- **What it does not show.** A firm ratio, or that features are the problem. New code arrives in changes of every
  title, as the next finding shows.

Recompute: `python3 questions/q02_new_code_or_broken_later.py`

### 3. Changes titled as new features cause far more than their share of bugs

**As expected.** *Well supported. Measured against every commit on main in the same period, not against an estimate.*

For each traced bug we looked at the title of the change that introduced it, and divided by how many commits carry
that title. Changes titled "feat" caused 123.7 bugs per 100 commits, against 18
for changes titled "fix" and 8.3 for everything else.

**Bugs per 100 commits, by how the change was titled**

![Bugs per 100 commits, by how the change was titled](charts/q03-bugs-per-100-commits-by-title-light.svg#gh-light-mode-only)
![Bugs per 100 commits, by how the change was titled](charts/q03-bugs-per-100-commits-by-title-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a rate: bugs fixed in the period studied that trace back to commits with that title, per 100 such commits made since 10 September. The three titles cover every commit.*

<details><summary>The numbers behind this chart</summary>

| | Commits since 10 Sep | Sampled bugs | Bugs per 100 commits | Median files changed |
|---|---:|---:|---:|---:|
| Titled feat (a new feature) | 1325 | 123 | 123.7 | 19 |
| Titled fix | 19951 | 270 | 18 | 4 |
| Any other title (refactor, perf, test, chore, ...) | 17934 | 112 | 8.3 | 4 |

</details>

In absolute numbers most bugs still come from changes titled "fix" (428 of the
832 traced), because half of everything merged carries that title. And a title is a loose label:
one change titled as a fix touched 138 files and added a whole rollback mechanism. Feature changes are also larger
than others, so part of their higher rate is size, which is the next finding.

- **How we know.** The comparison uses the 505 sampled bugs whose causing change was made
  since 10 September 2026 and all 39,210 commits on main since that date, counted from git.
- **How it was checked.** Titles and file counts are read mechanically from git, not judged. Which change caused
  each bug is the model's judgment from finding 2.
- **What it does not show.** What the change was really for, or how much of the gap is size. The rates are not
  adjusted for the size of the change. A rate counts the bugs fixed between 10 September and 22 November, so it grows
  with the length of the period watched: compare these rates with each other, not with another study's.

Recompute: `python3 questions/q03_what_kind_of_change_introduces_bugs.py`

### 4. Large changes cause far more bugs per change, but about the same per file changed

**As expected.** *Well supported. The per-file figures vary by less than a factor of two across size groups.*

A causing change touched a median of 36 files; an ordinary commit touches
4. Per change, a commit of over 100 files carried about
131 times the bugs of a commit of 1 to 5 files.

**Bugs per 100 commits, by size of the change**

![Bugs per 100 commits, by size of the change](charts/q04-bugs-per-100-commits-light.svg#gh-light-mode-only)
![Bugs per 100 commits, by size of the change](charts/q04-bugs-per-100-commits-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a rate: bugs fixed in the period studied that trace back to commits of that size, per 100 such commits made since 10 September. The four sizes cover every commit.*

Per file changed, the picture is different: between 8.9 and 15.3 bugs
per 1,000 files changed in every size group, with no trend. On this evidence large changes hold more bugs because
they hold more change, not because each part of them is worse.

**Bugs per 1,000 files changed, by size of the change**

![Bugs per 1,000 files changed, by size of the change](charts/q04-bugs-per-1000-files-light.svg#gh-light-mode-only)
![Bugs per 1,000 files changed, by size of the change](charts/q04-bugs-per-1000-files-dark.svg#gh-dark-mode-only)

*How to read it: The same bugs, divided by the total number of files those commits changed instead of by the number of commits.*

<details><summary>The numbers behind this chart</summary>

| | Commits | Sampled bugs | Bugs per 100 commits | Bugs per 1,000 files changed |
|---|---:|---:|---:|---:|
| 1 to 5 files | 22130 | 38 | 2.29 | 8.9 |
| 6 to 30 files | 12883 | 185 | 19.13 | 15.3 |
| 31 to 100 files | 3623 | 153 | 56.27 | 10.77 |
| Over 100 files | 574 | 129 | 299.45 | 14.8 |

</details>

- **How we know.** Every commit on main since 10 September 2026 is placed in a size group by files changed. A bug is
  one sampled fix traced to a causing commit in that list (505 cases), scaled from the sample to all
  fixes in the period. So a rate reads as "bugs fixed between 10 September and 22 November, per 100 commits made in
  that time".
- **How it was checked.** Sizes come from git. The causing commit is the model's judgment; the two models named
  the same one in 108 of 130 cases.
- **What it does not show.** Risk per line, or whether splitting a large change would lower the total. It also
  counts only bugs fixed within the period, so slow-to-surface bugs from recent changes are missing.

Recompute: `python3 questions/q04_do_large_changes_cause_more_bugs.py`

### 5. A broken thing typically stayed broken for one to four weeks

*Supported. Dates come from git. The split depends on the model naming the right causing change, and the figure for
the earlier weeks is cut short by how far back a cause could be traced.*

**Broken-later bugs, by time from cause to fix**

![Broken-later bugs, by time from cause to fix](charts/q05-age-of-broken-later-bugs-light.svg#gh-light-mode-only)
![Broken-later bugs, by time from cause to fix](charts/q05-age-of-broken-later-bugs-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a number of broken-later bugs. The four bars add up to 389.*

**Median days from the causing change to the fix, for three kinds of bug**

![Median days from the causing change to the fix, for three kinds of bug](charts/q05-median-days-to-fix-light.svg#gh-light-mode-only)
![Median days from the causing change to the fix, for three kinds of bug](charts/q05-median-days-to-fix-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the middle value of days on main before the fix, for one group of bugs. The three groups do not overlap.*

<details><summary>The numbers behind this chart</summary>

| | Count |
|---|---:|
| Under a day | 97 |
| 1 to 7 days | 67 |
| 7 to 30 days | 105 |
| Over 30 days | 120 |

</details>

Half of the broken-later bugs were fixed within 11.8 days of the change that broke them. For
fixes merged in November the figure is 28.8 days; for fixes merged from 10 September to
1 November it is 8.6. Only 88 of the 389
broken-later fixes say which change caused the bug, and those were fixed within a day. Scaled from the sample, about
5,180 broken-later bugs were fixed in the period (plausibly 4800 to 5610).

- **How we know.** Days are the commit time of the fix minus the commit time of the causing change, both on main.
- **How it was checked.** An earlier study that could only find fixes naming their cause had put the typical time at
  1.7 days. The random sample shows that figure described the quick cases only.
- **What it does not show.** How long users were affected, or how many noticed. A bug counts only once it is fixed,
  so long-lived bugs still open are missing. The model could trace causes back to 1 July 2026 and no further, so a
  fix from September cannot show a bug older than about ten weeks, where one from November can show one of twenty.
  That alone makes the earlier weeks look quicker.

Recompute: `python3 questions/q05_how_long_do_bugs_live.py`

## What review caught, and what it could have

Findings 6 to 10: what the project's review bot had said before each bug-causing change merged, and what other
models find when shown the same changes with no hint. Findings 7 to 10 cover November only.

### 6. The review bot had rarely named the bug before the change merged

**Surprising.** *Well supported. The November cases were read by both models, with close agreement.*

For each of the 832 traced bugs we read what the bot had written on the causing change at the moment
it merged, rebuilt from the comment's edit history. It had reviewed 645 of them and named the bug
in 21. It raised a related concern, without stating the failure, in
82.

**What the bot's review said about the bug, by two models**

![What the bot's review said about the bug, by two models](charts/q06-what-the-review-said-light.svg#gh-light-mode-only)
![What the bot's review said about the bug, by two models](charts/q06-what-the-review-said-dark.svg#gh-dark-mode-only)

*How to read it: The same 88 reviews, read twice. Each bar is a number of bug-causing changes; each color adds up to 88.*

<details><summary>The numbers behind this chart</summary>

| | Main model (gpt-6.2-sol) | Second model (Claude Opus 5.5) |
|---|---:|---:|
| Said nothing about this bug | 72 | 79 |
| Raised a related concern, not this failure | 14 | 7 |
| Named this bug | 2 | 2 |

</details>

**Whether the bot had reviewed the causing change**

![Whether the bot had reviewed the causing change](charts/q06-was-there-a-review-light.svg#gh-light-mode-only)
![Whether the bot had reviewed the causing change](charts/q06-was-there-a-review-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a number of bug-causing changes. The four bars add up to 832.*

**The bot's overall verdict when the bug-causing change merged**

![The bot's overall verdict when the bug-causing change merged](charts/q06-verdict-at-merge-light.svg#gh-light-mode-only)
![The bot's overall verdict when the bug-causing change merged](charts/q06-verdict-at-merge-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a number of bug-causing changes the bot had reviewed. The four bars add up to 645.*

Warnings were not being ignored. 418 changes merged while the bot said "blocked" or "needs
changes", but in 346 of them its open items were about something other than the
bug, such as missing proof. Only 44 items that touched the bug were open and unanswered at
merge. The bot also said "ready" on changes that carried a bug. Finding 12 adds the other half: although its words
rarely named the bug, the changes it objected to were the riskier ones.

- **How we know.** A model compared each bug with the review text under a strict rule: it counts as named only if
  fixing what the review described would have prevented the bug.
- **How it was checked.** For 88 November cases both models read the same review of the
  same causing change. They gave the same answer for 79, and agreed on whether the bug was
  named for 88.
- **What it does not show.** How many bugs the bot stopped. A bug it caught and the author fixed before merge never
  appears in a sample of later fixes. This is a measure of what got past it, not of its worth.

Recompute: `python3 questions/q06_did_the_review_bot_name_the_bug.py`

### 7. Two current models together named more of the known bugs than the bot had

*Supported. Thirty smaller changes, one run each. Clear for the two models combined, not for either alone.*

We took 30 bug-causing changes and gave each reviewer the repository exactly as it stood at merge,
with no later history, and one plain instruction: find the defects this change introduces. Graders who did not know
which reviewer wrote what then checked whether any reported problem was the known bug.

**Known bugs named by each reviewer, out of 30**

![Known bugs named by each reviewer, out of 30](charts/q07-known-bugs-named-light.svg#gh-light-mode-only)
![Known bugs named by each reviewer, out of 30](charts/q07-known-bugs-named-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is how many of the same 30 known bugs that reviewer named. The gray bar is what the project's bot had said at the time, for comparison.*

<details><summary>The numbers behind this chart</summary>

| | Named, first grader | Named, second grader | Problems reported |
|---|---:|---:|---:|
| gpt-5.6-sol | 3 | 2 | 32 |
| gpt-6-astra | 1 | 1 | 13 |
| gpt-6.1-sol (the model the bot's README names) | 0 | 0 | 15 |
| gpt-6.2-sol | 7 | 8 | 98 |
| Claude Opus 5.5 | 7 | 7 | 50 |
| gpt-6.1-sol, three files at a time | 2 | 2 | 33 |
| The review bot's actual reviews at the time | 2 | – | – |

</details>

gpt-6.2 and Opus 5.5 together named 10 bugs and overlapped on
4, so they catch different things. How likely is a gap this large by luck alone?

| Comparison | Chance of a gap this large by luck |
|---|---:|
| The two top models together, against the bot | 0.021 |
| One top model, against the bot | 0.125 |
| One top model, against gpt-6.1 on the same instruction | 0.016 |
| Three files at a time, against the whole change | 0.5 |

The count is not a steady climb across model versions, and it follows how much each model reports:

**Problems each reviewer reported across the 30 changes**

![Problems each reviewer reported across the 30 changes](charts/q07-problems-reported-light.svg#gh-light-mode-only)
![Problems each reviewer reported across the 30 changes](charts/q07-problems-reported-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the total number of problems that reviewer reported on the 30 changes, right or wrong.*

Of the 10 bugs that at least one reviewer named, 7 had been live for
more than ten days.

- **How we know.** Cases were the first 15 broken-later and first 15 never-worked bugs, in the sample's random order,
  among those the bot had reviewed, with a causing change of at most 30 files made since 10 September.
- **How it was checked.** A grader from a different maker regraded all 180 reviewer and case
  pairs and agreed on named or not for 178. Logs show no reviewer read later history, the fix,
  or another case. Two PR descriptions that had been edited after merge to mention the fix were replaced with their
  merge-time text.
- **What it does not show.** A like-for-like contest with the bot. The bot reviewed at the time, sometimes an earlier
  revision, with its own long instructions. It also does not cover changes of more than 30 files, which are where
  most bugs come from.

Recompute: `python3 questions/q07_can_other_models_name_the_bug.py`

### 8. Most of the other problems those models reported hold up when checked

*Supported. A fifth are proven by later fixes. The rest rest on code reading by two models, with a control but no
executed test.*

A reviewer that reports a lot will name the known bug more often by volume alone, so the other reports matter.
gpt-6.2 and Opus 5.5 reported 148 problems on the 30 changes; 14 were the known
bug. We checked each one two ways: was it later fixed on main, and do two checkers who trace the code agree the
failure happens?

**Where the 148 reported problems stand**

![Where the 148 reported problems stand](charts/q08-where-the-reports-stand-light.svg#gh-light-mode-only)
![Where the 148 reported problems stand](charts/q08-where-the-reports-stand-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a number of reported problems. The four bars add up to 148.*

**Known-real problems each checker confirmed, before and after the bug was fixed**

![Known-real problems each checker confirmed, before and after the bug was fixed](charts/q08-can-the-checkers-say-no-light.svg#gh-light-mode-only)
![Known-real problems each checker confirmed, before and after the bug was fixed](charts/q08-can-the-checkers-say-no-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is how many of the same 14 real problems the checker said were present. A sound checker is high in blue and low in orange.*

17 of the other reports were later fixed on main by someone else, which is proof they were
real. That count is a floor: the same search found the fix for only 8 of the
14 problems we already knew were fixed.

- **How we know.** The reports were pooled under anonymous labels with nothing marking the known bugs. One model
  searched later fix commits; two checkers each traced every report in the exported code.
- **How it was checked.** The checkers were tested on the known-real problems, first on the original code and then on
  the code after the fix. After the fix, both still confirmed 3; two of those belong
  to a fix that was only partial.
- **What it does not show.** That the unfixed reports matter enough to block a merge. The two checkers are the same
  two models that wrote the reports, so they could share a convincing mistake. A failing test would settle it; none
  was written.

Recompute: `python3 questions/q08_are_the_other_reported_problems_real.py`

### 9. About a third of the bugs could not be seen by reading code

**Surprising.** *Tentative. One model's judgment on 30 cases; the key group is nine.*

**What a reviewer needed to see the bug, and how many were named**

![What a reviewer needed to see the bug, and how many were named](charts/q09-what-each-bug-needed-light.svg#gh-light-mode-only)
![What a reviewer needed to see the bug, and how many were named](charts/q09-what-each-bug-needed-dark.svg#gh-dark-mode-only)

*How to read it: The gray bar is the number of bugs of that kind, out of 30. The blue part is how many of them any reviewer named.*

No reviewer named a bug that depended on how a browser lays out a page, what a database accepts or how a filesystem
behaves under load. Size mattered too: reviewers named 6 of 12 bugs in
changes of 7 files or fewer, and 4 of 18 in larger ones.

- **How we know.** A model given the bug and the causing change chose the least demanding thing a reviewer would
  have needed: the changed lines, other repository code, or outside knowledge.
- **How it was checked.** It was not checked by a second model. The model flagged several close calls between the
  first two groups.
- **What it does not show.** A firm share. Nine cases cannot fix a proportion; they show that such bugs exist in
  number and that none was caught by reading.

Recompute: `python3 questions/q09_could_the_bug_be_seen_by_reading.py`

### 10. Most bugs broke no written rule

*Tentative. A sample found by commit wording, which later proved to favor quickly fixed bugs.*

The project keeps written rules for contributors and for the bot. In the first study, of 29 bugs
whose fix names the causing change, a rule existed for 4 when the change was written, and
0 of those could have been checked from the changed lines alone.

**Whether a written rule covered what went wrong, of 29 bugs**

![Whether a written rule covered what went wrong, of 29 bugs](charts/q10-did-a-rule-cover-it-light.svg#gh-light-mode-only)
![Whether a written rule covered what went wrong, of 29 bugs](charts/q10-did-a-rule-cover-it-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a number of bugs. The four bars add up to 29.*

Recompute: `python3 questions/q10_did_a_written_rule_cover_it.py`

## Which changes carry the bugs

Findings 11 to 21: the traced bugs set against every commit and pull request of the period. Nothing here is judged
by a model; it is counted from git and GitHub.

### 11. Changes committed straight to main caused fewer bugs per change, not more

**Surprising.** *Supported per change; much of the gap is size. The direct-commit side rests on 19 sampled
bugs.*

8.6% of commits since 10 September reached main with no pull request number in the title.
Per commit they carried 0.42 times the bugs of changes that went through a pull request
(plausibly 0.26 to 0.66).

<details><summary>The numbers behind this chart</summary>

| | Commits | Sampled bugs | Bugs per 100 commits |
|---|---:|---:|---:|
| Through a pull request | 35836 | 486 | 18.07 |
| Straight to main | 3374 | 19 | 7.5 |

</details>

They are also smaller (a median of 2 files against 5),
so size explains part of the gap. Within changes of 6 files or more, the rate was
26.94 for direct commits against 36.8 through a pull request.

- **How we know.** Same method as finding 4, split by whether the commit title carries a pull request number.
- **How it was checked.** It was not checked further.
- **What it does not show.** Who made the direct commits or why, or that skipping a pull request is safe: the
  changes people commit directly are the ones they judge routine. Finding 12 takes up changes merged against the
  review bot's verdict.

Recompute: `python3 questions/q11_does_skipping_a_pull_request_matter.py`

### 12. Changes merged while the bot objected carried more bugs

**Surprising.** *Supported. A comparison with ordinary changes, with size held equal. It shows a link, not a cause.*

Findings 1 to 11 start from bugs. To ask whether a kind of change causes more bugs, we also need to know how common
that kind is among ordinary changes. So we drew 400 merged pull requests at random and
recorded, for each, what the bot's review said at the moment it merged. The bot had called
64% of them ready and objected to 20.8%, which merged
anyway.

**Bugs per 100 changes, by what the bot said when the change merged**

![Bugs per 100 changes, by what the bot said when the change merged](charts/q12-bugs-by-bot-verdict-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by what the bot said when the change merged](charts/q12-bugs-by-bot-verdict-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a rate: bugs fixed in the period studied that trace back to changes merged under that verdict, per 100 such changes. Verdicts seen on fewer than 20 sampled changes are left out.*

Changes merged over the bot's objection caused sampled bugs 7.01 times as often as
changes it called ready (plausibly 5.09 to 9.66). The bot objects more to large changes,
and large changes carry more bugs, so part of that is size. Comparing only changes of similar size that landed in
the same month, the ratio is
3.42 (plausibly 2.34 to 4.99). Changes the bot never
reviewed were no different from ones it called ready.

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |
|---|---:|---:|---:|---|
| Bot said ready | 64% | 135 | 7.84 | (the baseline) |
| Bot said blocked or needs changes | 20.8% | 307 | 55.01 | 3.42 times (plausibly 2.34 to 4.99) |
| Bot said needs maintainer review | 0.2% | 0 | 0.0 | too few to say |
| No bot review before merge | 15% | 44 | 10.91 | 1.27 times (plausibly 0.74 to 2.17) |

- **How we know.** The comparison sample says how common each verdict is; the bug-causing changes say how many
  sampled bugs came from each. The ratio of those two is the relative bug rate. "Similar size" means within three
  groups: 1 to 5 files, 6 to 30, and over 30. The month is held equal because an older change has had longer for its
  bugs to be found and fixed.
- **How it was checked.** The verdict is read mechanically from the marker the bot writes into its own comment, for
  the last version written before the merge. The causing change is the models' judgment (finding 2).
- **What it does not show.** That merging against the verdict causes bugs. The bot objects to changes that are
  harder for other reasons too. And finding 6 still holds: in most of these cases its open items were about something
  other than the bug.

Recompute: `python3 questions/q12_does_merging_against_the_bot_matter.py`

### 13. Merging soon after the bot's review shows no clear extra risk

*Tentative. The intervals include no difference.*

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |
|---|---:|---:|---:|---|
| Bot reviewed the revision that merged | 70.5% | 349 | 18.41 | (the baseline) |
| Bot reviewed only an earlier revision | 14.5% | 93 | 23.85 | 0.92 times (plausibly 0.58 to 1.47) |
| No bot review before merge | 15% | 44 | 10.91 | 0.71 times (plausibly 0.42 to 1.2) |

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |
|---|---:|---:|---:|---|
| Merged an hour or more after the bot's review | 20% | 110 | 20.45 | (the baseline) |
| Merged 10 to 60 minutes after it | 38.8% | 205 | 19.67 | 0.7 times (plausibly 0.44 to 1.11) |
| Merged within 10 minutes of it | 26.2% | 127 | 17.99 | 0.93 times (plausibly 0.56 to 1.54) |

Changes where the bot had seen only an earlier revision carried 0.92 times the
bugs of those where it had seen the merged one (plausibly 0.58 to 1.47). Changes
merged within ten minutes of the bot's review carried 0.93 times the bugs of those
merged an hour or more later (plausibly 0.56 to 1.54). Both ranges include no difference.

- **How we know.** Same method as finding 12, using which revision the bot reviewed and the minutes from its review
  to the merge.
- **What it does not show.** That speed is safe. Quick merges are mostly small, simple changes; the comparison cannot
  say what would happen if the hard ones were merged as fast.

Recompute: `python3 questions/q13_does_review_timing_matter.py`

### 14. Pull requests merged within the hour carried far fewer bugs than those open a day or more

**Surprising.** *Supported for time open. On who opened or merged a change, this sample of 400 is too thin; finding 19 asks the same
of every pull request.*

**Bugs per 100 changes, by how long the pull request was open**

![Bugs per 100 changes, by how long the pull request was open](charts/q14-bugs-by-time-open-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by how long the pull request was open](charts/q14-bugs-by-time-open-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a rate: bugs fixed in the period studied that trace back to pull requests open that long, per 100 such pull requests. The three groups cover every pull request.*

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |
|---|---:|---:|---:|---|
| Open a day or more | 10.2% | 113 | 40.99 | (the baseline) |
| Open 1 to 24 hours | 43.5% | 313 | 26.75 | 0.7 times (plausibly 0.42 to 1.18) |
| Open under an hour | 46.2% | 60 | 4.82 | 0.28 times (plausibly 0.16 to 0.47) |

Pull requests merged within an hour of being opened carried 0.28 times the bugs of those
open a day or more, at equal size and month (plausibly 0.16 to 0.47). A change that stays open is
usually one that needed work, and those are the ones that later needed fixing.

The other three comparisons show no difference that can be told from none in this sample. They are given as tables,
not charts, because a bar would suggest a difference the numbers do not support.

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |
|---|---:|---:|---:|---|
| Opened by an outside contributor | 9.2% | 15 | 6.03 | (the baseline) |
| Opened by a maintainer | 80.8% | 413 | 19.02 | 1.14 times (plausibly 0.5 to 2.62) |
| Opened by an automation account | 10% | 58 | 21.57 | 2.05 times (plausibly 0.8 to 5.21) |

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |
|---|---:|---:|---:|---|
| Merged by someone else | 11.2% | 29 | 9.58 | (the baseline) |
| Merged by its own author | 88.8% | 457 | 19.15 | 0.75 times (plausibly 0.4 to 1.38) |

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |
|---|---:|---:|---:|---|
| A person reviewed it before merge | 2.0% | 5 | 9.3 | (the baseline) |
| No person's review before merge | 98% | 481 | 18.25 | 3.57 times (plausibly 0.44 to 28.95) |

- **How we know.** Same method as finding 12. A maintainer here is a person who merged at least one of the fetched
  pull requests; GitHub's own member label misses people whose membership is private.
- **What it does not show.** That review by another person does not help. Only 2.0% of
  the sampled changes had one, and people chose to review the risky ones, so the two groups are not alike. Finding
  19 repeats the comparisons on every pull request.

Recompute: `python3 questions/q14_does_who_lands_the_change_matter.py`

### 15. How this project reviews and merges, in numbers

*Measured. Counted from git and GitHub; nothing is judged.*

**Share of ordinary pull requests for which each statement is true**

![Share of ordinary pull requests for which each statement is true](charts/q15-how-changes-are-merged-light.svg#gh-light-mode-only)
![Share of ordinary pull requests for which each statement is true](charts/q15-how-changes-are-merged-dark.svg#gh-dark-mode-only)

*How to read it: Five separate yes-or-no facts about the same 400 randomly drawn pull requests. The bars are not parts of a whole and do not add up.*

| | |
|---|---:|
| Commits on main per day, 10 Sep to 22 Nov 2026 | 531 |
| Merged pull requests, 10 Sep to 22 Nov 2026 | 35,826 |
| Accounts that merged at least one of them | 40 |
| Share of all pull requests merged by the most active account | 54.3% |
| Share of all pull requests opened by the most active account | 52.1% |
| Share of all pull requests opened by an automation account | 11% |
| Share of all pull requests another person reviewed before the merge | 1.0% (344) |
| Median time from opening a pull request to merging it | 70 minutes |
| Median time from the bot's review to the merge | 19 minutes |
| Share of commits titled "fix" | 50.9% |
| Share of commits changing fewer than 10 files | 70.8% |
| Mean files changed per commit | 13.4 |

Recompute: `python3 questions/q15_how_does_the_project_review_and_merge.py`

### 16. A screenshot or video in the pull request did not go with fewer bugs

**Surprising.** *Supported. It shows what such pull requests are like, not what the screenshot did.*

The project asks for visual proof on visible changes, so we checked whether pull requests that carry it do better.
Screenshots and videos are attached almost only to interface changes, and interface changes cause more bugs than
others, so the fair comparison is among interface changes alone.

**Among interface changes: bugs per 100 changes, with and without a screenshot or video**

![Among interface changes: bugs per 100 changes, with and without a screenshot or video](charts/q16-bugs-by-visual-proof-light.svg#gh-light-mode-only)
![Among interface changes: bugs per 100 changes, with and without a screenshot or video](charts/q16-bugs-by-visual-proof-dark.svg#gh-dark-mode-only)

*How to read it: Only pull requests that change files under ui/ or apps/. Each bar is a rate: bugs fixed in the period studied that trace back to such pull requests, per 100 of them.*

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size and month |
|---|---:|---:|---:|---|
| No screenshot or video in the description | 15.2% | 74 | 18.04 | (the baseline) |
| A screenshot or video in the description | 10.5% | 141 | 49.93 | 3.72 times (plausibly 2.0 to 6.93) |

Interface changes with a screenshot or video caused 3.72 times the bugs of interface
changes without one, at equal size and month (plausibly 2.0 to 6.93).

- **How we know.** For each of the 400 sampled pull requests and each bug-causing one, we read the
  description as it stood at merge and counted embedded pictures and videos. An interface change is one that touches
  files under `ui/` or `apps/`.
- **How it was checked.** Counts are mechanical. Nearly every description has an "Evidence" heading, so the heading
  alone says nothing; only an embedded picture or video counts here.
- **What it does not show.** That proof makes things worse. People attach screenshots to the changes a user will
  see, and a visible bug is the kind that gets noticed and fixed within weeks. What it does show is that a
  screenshot of the change working once is not a sign the change is safe.

Recompute: `python3 questions/q16_do_changes_with_visual_proof_cause_fewer_bugs.py`

### 17. The bugs are concentrated in changes that could be pointed at beforehand

**Surprising.** *Supported. The three signs were picked after seeing the November fixes alone. On the full period, with four times
the bugs, they mark the same share.*

Three things visible at or before merge each mark a small share of changes and a large share of bugs: the bot
objected, the pull request had been open a day or more, or the change touched more than 30 files.

**Share of the traced bugs that came from changes with each warning sign**

![Share of the traced bugs that came from changes with each warning sign](charts/q17-share-of-bugs-by-warning-sign-light.svg#gh-light-mode-only)
![Share of the traced bugs that came from changes with each warning sign](charts/q17-share-of-bugs-by-warning-sign-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the percentage of traced bugs whose causing change had that sign. The gray note says how common such changes are. A bar much longer than its note's percentage means bugs are concentrated there. The first three rows overlap; the last three are combinations of them.*

<details><summary>The numbers behind this chart</summary>

| | Share of all changes, % | Share of traced bugs, % | Sampled bugs |
|---|---:|---:|---:|
| The bot objected | 20.8 | 63 | 307 |
| Open a day or more | 10.2 | 23 | 113 |
| More than 30 files | 12.8 | 57 | 279 |
| At least one of the three signs | 37 | 81 | 395 |
| At least two of the three signs | 6.8 | 48 | 234 |
| None of the three signs | 63 | 19 | 91 |

</details>

Changes with at least two of the three signs are 6.8% of all changes and the source of
48% of the traced bugs. Changes with none are 63% of changes and
the source of 19%.

- **How we know.** The share of changes comes from the random comparison sample; the share of bugs from the
  486 sampled bugs whose causing change is a fetched pull request.
- **How it was checked.** All three signs are read from git and GitHub. No model judged them.
- **What it does not show.** That looking harder at those changes would have caught the bugs. Finding 7 bears on
  that. The earlier weeks are a partial test of the signs, not a clean one: both periods share one comparison
  sample of ordinary changes.

Recompute: `python3 questions/q17_how_concentrated_are_the_bugs.py`

### 18. An individual's workload shows no effect; the project's busiest days carried more bugs

**Surprising.** *Supported for individual workload. Tentative for busy days: it is one clear result among about thirty comparisons.*

The worry is simple: one person lands hundreds of changes a day, the project lands a thousand, and care must be
slipping. If that were so, changes landed under heavy load would cause more bugs than changes landed under light
load. We looked for that six ways.

For the median commit, its author landed 175 changes that same day, and the previous
one 4.7 minutes earlier. On a typical day 14 accounts merge; one
account merges 54.3% of all pull requests and three accounts merge 73.6%.

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size, kind and time |
|---|---:|---:|---:|---|
| ***By how many changes the author landed that day*** | | | | |
| Author landed 1 to 5 changes that day | 10.6% | 41 | 13.21 | (the baseline) |
| 6 to 20 that day | 10.3% | 91 | 30.1 | **1.85 times (plausibly 1.24 to 2.77)** |
| 21 to 50 that day | 10% | 55 | 18.73 | 1.45 times (plausibly 0.92 to 2.28): no clear difference |
| 51 to 150 that day | 16.5% | 61 | 12.56 | **1.59 times (plausibly 1.01 to 2.48)** |
| Over 150 that day | 52.7% | 257 | 16.57 | 1.18 times (plausibly 0.82 to 1.69): no clear difference |
| ***By how soon after the author's previous change*** | | | | |
| An hour or more after the author's previous change | 15% | 98 | 22.22 | (the baseline) |
| 10 to 60 minutes after it | 19.8% | 91 | 15.61 | 0.85 times (plausibly 0.63 to 1.15): no clear difference |
| Under 10 minutes after it | 63.3% | 311 | 16.69 | 0.9 times (plausibly 0.7 to 1.15): no clear difference |
| ***By the author's own usual pace*** | | | | |
| A light day for that author (under three quarters of their usual) | 11% | 70 | 21.62 | (the baseline) |
| A usual day for that author | 37% | 223 | 20.48 | 0.9 times (plausibly 0.66 to 1.21): no clear difference |
| A heavy day (over one and a half times their usual) | 47.4% | 201 | 14.42 | 0.77 times (plausibly 0.57 to 1.03): no clear difference |
| ***By how many pull requests the person merging merged that day*** | | | | |
| The merger merged 1 to 5 pull requests that day | 2.4% | 24 | 33.66 | (the baseline) |
| 6 to 20 that day | 8.7% | 71 | 27.79 | 1.06 times (plausibly 0.63 to 1.76): no clear difference |
| 21 to 50 that day | 13% | 68 | 17.84 | 0.86 times (plausibly 0.51 to 1.45): no clear difference |
| 51 to 150 that day | 20.6% | 69 | 11.38 | 0.75 times (plausibly 0.45 to 1.27): no clear difference |
| Over 150 that day | 46.7% | 254 | 18.48 | 0.77 times (plausibly 0.48 to 1.24): no clear difference |
| ***By how busy the whole project was that day*** | | | | |
| Quiet days for the project (under 410 commits) | 19.8% | 57 | 9.77 | (the baseline) |
| Middle days (410 to 591) | 32% | 190 | 20.17 | 1.34 times (plausibly 0.88 to 2.05): no clear difference |
| Busy days (592 or more) | 48.2% | 258 | 18.2 | **1.73 times (plausibly 1.11 to 2.71)** |
| ***By day of the week*** | | | | |
| Landed Monday to Friday | 71.1% | 351 | 16.78 | (the baseline) |
| Landed Saturday or Sunday | 28.9% | 154 | 18.1 | 0.98 times (plausibly 0.8 to 1.2): no clear difference |

Read each block against its first row.

- **The person.** Landing minutes after the previous change, having a heavier day than one's own usual, and merging
  many pull requests in a day show no clear difference. In the first block every level sits above the baseline, but
  the baseline is authors landing 1 to 5 changes a day, who are mostly occasional contributors and do better than
  everyone else (finding 19). Above that level the rate does not rise with load.
- **The project.** Changes landed on the busiest third of days carried 1.73 times the bugs
  of changes landed on the quietest third (plausibly 1.11 to 2.71), with the middle third in
  between. The range starts close to no difference. Weekends are no different from weekdays.

- **How we know.** For each of the 39,210 commits we counted how many the same author landed that
  day and how long since their previous one, and for each pull request how many the same person merged that day.
  The bugs are the 505 sampled bugs whose causing commit is among those commits. "At equal size, kind
  and time" compares changes of similar file count, the same title type (feat, fix, other), landed in the same
  half-month. Time has to be held equal because an older commit has had longer for its bugs to be found and fixed:
  September commits show 23.1 bugs per 100, November commits 8.1.
- **What it does not show.** That the pace is harmless. A count per commit favors whoever cuts work into the most
  pieces, and a tired author's mistakes need not land on the same day. Busy days may also differ in what gets
  landed, in ways that size and title do not capture.

Recompute: `python3 questions/q18_does_author_workload_matter.py`; `python3 questions/q19_does_the_day_matter.py`; `python3 questions/q20_does_load_on_the_person_merging_matter.py`

### 19. Changes from occasional contributors, and changes someone else merged, carried about half the bugs

**Surprising.** *Supported. The two overlap: an outside contributor cannot merge their own change.*

Would more contributors mean more bugs? One way to ask is whether changes from people who contribute rarely cause
more bugs than changes from the regulars. They cause fewer.

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size, kind and time |
|---|---:|---:|---:|---|
| ***By how much the author contributes*** | | | | |
| The single most active author | 54% | 270 | 17 | (the baseline) |
| Other authors with over 500 commits | 31.2% | 148 | 16.12 | 1.06 times (plausibly 0.84 to 1.32): no clear difference |
| Authors with 21 to 500 commits | 10.1% | 77 | 25.87 | 1.3 times (plausibly 0.96 to 1.75): no clear difference |
| Authors with 20 commits or fewer | 4.7% | 10 | 7.21 | **0.47 times (plausibly 0.25 to 0.9)** |
| ***By who merged it*** | | | | |
| Merged by the person who opened it | 71.1% | 409 | 19.54 | (the baseline) |
| Merged by someone else | 10.2% | 19 | 6.32 | **0.42 times (plausibly 0.26 to 0.68)** |
| ***The same, only for authors who can merge*** | | | | |
| Author can merge, and merged it themselves | 71.1% | 409 | 19.54 | (the baseline) |
| Author can merge, but someone else merged it | 1.0% | 4 | 13.06 | **0.37 times (plausibly 0.14 to 0.96)** |
| ***By whether another person reviewed it*** | | | | |
| No other person reviewed it before the merge | 80.8% | 423 | 17.79 | (the baseline) |
| Another person reviewed it before the merge | 0.6% | 5 | 30.01 | 0.95 times (plausibly 0.37 to 2.45): no clear difference |

- The 676 authors with 20 commits or fewer wrote 4.7% of
  commits and caused 0.47 times the bugs per change of the most active author
  (plausibly 0.25 to 0.9).
- Among everyone else, how much an author contributes makes no clear difference.
- Changes merged by someone other than their author carried 0.42 times the bugs
  (plausibly 0.26 to 0.68). Most of these are outside contributors' changes. Among authors
  who could have merged it themselves the ratio is 0.37 (plausibly
  0.14 to 0.96), on only 4 bugs.
- Only 222 commits came from a pull request another person had reviewed, which is
  too few to say anything.

- **How we know.** Authors are grouped by how many commits they landed since 10 September. Who merged and who
  reviewed comes from GitHub, for all 35,826 merged pull requests.
- **What it does not show.** That a second person's merge prevents bugs. A change an outsider sends and a maintainer
  accepts is usually a small, targeted repair, and title and file count do not fully capture that. Whether review by
  a second person would help stays open: it is hardly practised here. Authors are told apart by commit email, so one
  person with two addresses counts twice.

Recompute: `python3 questions/q22_do_occasional_contributors_cause_more_bugs.py`; `python3 questions/q21_does_a_second_person_help.py`

### 20. Changes to files that several other people were also editing caused more bugs

**As expected.** *Supported for the most-shared files. It cannot separate "too many hands" from "the busiest, most central code".*

**Bugs per 100 changes, by how many other people were editing the same files**

![Bugs per 100 changes, by how many other people were editing the same files](charts/q23-bugs-by-how-many-people-edit-the-files-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by how many other people were editing the same files](charts/q23-bugs-by-how-many-people-edit-the-files-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the number of bugs per 100 changes of that kind. The first row is changes to files that mostly only their author had been editing; the rows below are changes to files that other people had also changed in the previous two weeks. Longer bars mean more bugs per change.*

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size, kind and time |
|---|---:|---:|---:|---|
| ***By how many other people changed the same files in the previous 14 days*** | | | | |
| Fewer than 1 other person per file in the last 14 days | 22.9% | 113 | 16.78 | (the baseline) |
| 1 to 2 other people per file | 20.5% | 136 | 22.59 | 1.23 times (plausibly 0.94 to 1.61): no clear difference |
| 2 or more other people per file | 14.5% | 101 | 23.68 | **1.67 times (plausibly 1.22 to 2.28)** |
| ***By whether the author had changed those files before*** | | | | |
| The author had changed every edited file before | 28.8% | 109 | 12.86 | (the baseline) |
| Some of them | 11% | 169 | 52.37 | **1.67 times (plausibly 1.27 to 2.19)** |
| None of them | 11.9% | 20 | 5.73 | **0.52 times (plausibly 0.31 to 0.86)** |

When two or more other people per file had changed the files a change edits in the previous two weeks, the change
caused 1.67 times the bugs (plausibly 1.22 to 2.28) of a
change to files that only its author had been editing. With one to two other people the difference is not clear.

Being new to the files did not hurt. Authors editing only files they had never changed before caused
0.52 times the bugs of authors who had changed all of them (plausibly
0.31 to 0.86): fewer, not more. The middle row, changes that reach beyond the author's own
files into others, is the higher one.

- **How we know.** For every code file a commit edits, we counted the other authors who had changed that file in
  the 14 days before, and averaged over the commit's files. Only commits that edit existing code are compared.
- **What it does not show.** That several people editing a file is what causes the bugs. Files many people edit are
  also the central ones where most things connect, and this data cannot tell those two apart.

Recompute: `python3 questions/q23_do_files_many_people_edit_cause_more_bugs.py`

### 21. Nearly every bug-causing change came with tests; no part of the code stands out

**Surprising.** *Measured.*

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size, kind and time |
|---|---:|---:|---:|---|
| ***Among commits that change code: with or without tests*** | | | | |
| Changes code and tests together | 63.3% | 494 | 26.51 | (the baseline) |
| Changes code and no test file | 9.6% | 11 | 3.88 | **0.32 times (plausibly 0.18 to 0.57)** |
| ***By the part of the code the commit touches*** | | | | |
| Core code (src/, packages/), no interface or plugins | 45.5% | 185 | 13.81 | (the baseline) |
| Plugins (extensions/), no interface | 15.7% | 94 | 20.41 | 0.9 times (plausibly 0.69 to 1.18): no clear difference |
| Interface (ui/ or apps/) | 26% | 226 | 29.58 | 1.2 times (plausibly 0.96 to 1.5): no clear difference |
| Only docs, scripts, tests or config | 12.8% | 0 | 0.0 | too few to say |

- 494 of the 505 sampled bugs came from a change that also changed test files.
  The tests that came with a change did not catch the bug it carried.
- Code changes with no test file are few and small (refactors, chores, small fixes) and caused
  11 of the sampled bugs, 0.32 times the rate of
  changes with tests. This is not evidence that skipping tests is safe: the two groups are different kinds of change.
- Interface changes cause more bugs per commit than core changes, but they are also larger. At equal size, kind and
  time, interface, plugin and core changes are alike.

- **How we know.** A test file is one whose path marks it as a test (`.test.`, `.spec.`, `.e2e.`, a `test` or
  `fixtures` folder). Each commit is put in one part of the code by the folders it touches.
- **What it does not show.** Whether the tests were good, or whether they ran. No test was run for this study.

Recompute: `python3 questions/q25_do_changes_with_tests_cause_fewer_bugs.py`; `python3 questions/q26_which_parts_of_the_code_cause_bugs.py`

## Does it hold up

Findings 22 and 23: the same questions asked of a second period and of a second model, and the one answer that
depends on which model is asked.

### 22. The earlier weeks look like November; what differs is the model

*Supported. This is the check on everything above: a second period, and a second model.*

Every fix was read by gpt-6.2-sol. The 300 November fixes were also read by a model from a different
maker, Claude Opus 5.5. That gives three sets to put side by side. The first two are the same November fixes read by two
models, so their difference is the model. The last two are one model reading two periods, so their difference is
the period.

**Share of changes titled fix that repaired no bug, by which model judged them and when they merged**

![Share of changes titled fix that repaired no bug, by which model judged them and when they merged](charts/q27-not-a-bug-by-reader-and-period-light.svg#gh-light-mode-only)
![Share of changes titled fix that repaired no bug, by which model judged them and when they merged](charts/q27-not-a-bug-by-reader-and-period-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the percentage of sampled fixes that the model said repaired no bug. The first two bars are the same fixes read by two different models: their gap is the model. The last two bars are one model reading two periods: their gap is the period.*

**Share of traced bugs that were new code that never worked, by which model judged them and when**

![Share of traced bugs that were new code that never worked, by which model judged them and when](charts/q27-never-worked-by-reader-and-period-light.svg#gh-light-mode-only)
![Share of traced bugs that were new code that never worked, by which model judged them and when](charts/q27-never-worked-by-reader-and-period-dark.svg#gh-dark-mode-only)

*How to read it: Take only bugs that were new code that never worked, or a working thing broken later. Each bar is the percentage that were the first kind. Past the dashed line means the first kind is the more common.*

<details><summary>The numbers behind this chart</summary>

| | Fixes | Fixed no bug, % | Could not tell, % | Never worked | Broken later | Never worked, % of the two | Causes titled feat, % | Median files in a causing change | Median days broken, broken-later | Causing changes the bot reviewed | Bot named the bug |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| November fixes, read by Claude Opus 5.5 | 300 | 33 | 5 | 105 | 51 | 67 | 26 | 28.5 | 20.4 | 113 | 2 |
| Fixes from 2026-11-01 to 2026-11-22, read by gpt-6.2-sol | 300 | 11 | 13 | 115 | 91 | 56 | 30 | 34.5 | 28.8 | 170 | 2 |
| Fixes from 2026-09-10 to 2026-11-01, read by gpt-6.2-sol | 902 | 7 | 18 | 328 | 298 | 52 | 29 | 34 | 8.6 | 475 | 19 |

</details>

**The period changes little.** Under one model, November and the earlier weeks are close on how many fixes repaired
no bug (11% and 7%), on the split between never-worked and
broken-later (56% and 52% never-worked), on how large a
causing change is, and on how rarely the bot named the bug. The one clear gap is how long a broken thing stayed
broken, and finding 5 explains why that one cannot be trusted across periods.

**The model changes one thing a lot.** On the same November fixes, Claude Opus 5.5 said 33%
repaired no bug and gpt-6.2-sol said 11%. They also split never-worked from broken-later
differently. But where both named a causing change, they named the same one in 108 of
130 cases, and every finding that counts bugs by kind of change depends on the causing change, not on the label.

- **How we know.** The same brief was given to both models. Claude Opus 5.5 read the November fixes first, with GitHub
  lookups; gpt-6.2-sol read every fix later, without them.
- **What it does not show.** That another project, or another season of this one, would look the same. And the two
  periods share one commit list and one sample of ordinary changes, so they are not fully separate tests of
  findings 11 to 21.

Recompute: `python3 questions/q27_do_the_findings_hold_across_periods_and_readers.py`

### 23. How many "fix" changes repair no bug depends on which model you ask

*Depends on the model. We gave two models the same written rule for what counts as a bug. They drew the line in
different places, and each gave nearly the same answers when asked a second time.*

We drew 1,202 fixes by lottery from the 16,016 merged in the period and asked of
each: what was broken, and how did it get that way? The main model found that nothing had been broken in
95 of them (8%): they were redesign steps, speed-ups, wording
changes or tooling work that carried the title "fix". The second model, reading the
300 November fixes under the same rule, said so of 33%. The cases they
dispute are improvements that can also be described as a flaw present from the start: a slow path made faster, a log
message made more precise, a report that never fitted a phone screen.

**What each of the 1,202 sampled fixes repaired, by the main model**

![What each of the 1,202 sampled fixes repaired, by the main model](charts/q01-what-fixes-repaired-light.svg#gh-light-mode-only)
![What each of the 1,202 sampled fixes repaired, by the main model](charts/q01-what-fixes-repaired-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a number of sampled fixes. The five bars add up to 1,202.*

<details><summary>The numbers behind this chart</summary>

| | Count | Plausible range |
|---|---:|---:|
| New code that never worked | 443 | 34–40% |
| Not a bug: redesign, speed-up, wording or tooling | 95 | 7–10% |
| A working thing that a later change broke | 389 | 30–35% |
| Old code that broke because something outside changed | 74 | 5–8% |
| Could not tell | 201 | 15–19% |

</details>

**How the two models sorted the same 300 fixes**

![How the two models sorted the same 300 fixes](charts/q01-two-readers-light.svg#gh-light-mode-only)
![How the two models sorted the same 300 fixes](charts/q01-two-readers-dark.svg#gh-dark-mode-only)

*How to read it: The same 300 fixes, sorted twice. Blue is where the main model put them, orange where the second model did; each color adds up to 300.*

<details><summary>The numbers behind this chart</summary>

| | Main model (gpt-6.2-sol) | Second model (Claude Opus 5.5) |
|---|---:|---:|
| New code that never worked | 115 | 105 |
| Not a bug: redesign, speed-up, wording or tooling | 34 | 100 |
| A working thing that a later change broke | 91 | 51 |
| Old code that broke because something outside changed | 20 | 29 |
| Could not tell | 40 | 15 |

</details>

- **How we know.** One model read each fix, working from the fix's diff, its PR text and the history of the changed
  lines, with a written rubric that told it to answer "could not tell" when the evidence was thin.
- **How it was checked.** A second run of the main model, blind to the first answer, re-read
  191 fixes and agreed on bug or not a bug for 184. The second model's
  model had read 300 of the same fixes and agreed for 209. So each
  model is steady, and the two differ.
- **What it does not show.** A single right number. Treat the main model's share as the lower end and the second
  model's third as the upper end. The main model also answered "could not tell" for 201
  fixes: it worked without GitHub lookups, so it could not trace anything older than 1 July 2026. It cannot show
  bugs nobody has fixed yet, or bugs fixed under another title.

Recompute: `python3 questions/q01_how_many_fixes_repair_a_real_bug.py`

## How this compares with published research

Only studies whose figures we could check against the paper or its abstract are quoted. None of them studied this
project, and none measured exactly what we measured, so read each row as "same direction or not", not as a ranking.

| What | This project | Published research | Reading |
|---|---|---|---|
| Bug-causing changes are larger | Median 36 files against 4 for any commit | In Eclipse and Mozilla, changes that later needed a fix were about three times larger than others: 7.49 against 2.61 files, and 5.19 against 1.97 [1] | Same direction, and stronger here |
| Risk per change against risk per file | Per change, 131 times higher for the largest; per file changed, flat | A model of change risk at Bell Labs found how widely a change spreads across the code essential to predicting failure [2] | Consistent: a bigger change is more exposure |
| Share of changes that are fixes | 50.9% titled "fix" | 20.8% in Eclipse, 48.5% in Mozilla [1] | At the high end of what has been reported |
| Do fixes cause more bugs than other changes | No: "fix" is 53% of causes and 50.9% of commits | Three times more in Eclipse, no difference in Mozilla [1]. 14.8% to 24.4% of operating-system bug fixes were themselves wrong [3]; nearly 40% of fault fixes led to further faults in one telecom system [4] | Unremarkable. Fixes that break things are normal everywhere |
| "Fixes" that fix no bug | 8% to 33%, depending on the model | 33.8% of bug reports in five open-source projects were not bugs [5] | In line |
| What review catches | The bot named 21 of 645 bugs that got through | About 75% of what code review finds concerns maintainability, not function [6]; reviews find fewer defects than teams expect [7] | Same in kind. Not like for like: those studies count what review found, ours counts what it missed |
| Review by a second person | 1.0% of pull requests; 88.8% merged by their own author | At Google a change typically needs approval from at least one reviewer; the median is one reviewer [8]. Other studied projects had a median of two [8] | The clearest departure from studied practice |
| Does review coverage matter | No detectable difference here (finding 14) | In Qt, VTK and ITK, components with low review coverage and participation had up to two and five more post-release defects [9]; a later study at Sony Mobile did not find the link [10] | Open. The research is mixed and our sample cannot tell |
| Size of an ordinary change | 70.8% of commits change fewer than 10 files; mean 13.4 | About 90% at Google, with a median of 24 lines [8]; mean 3.5 files in Eclipse and Mozilla [1] | Larger batches here |
| Speed of review | Median 70 minutes from opening to merge | Under 4 hours at Google; 15 to 24 hours at AMD, Chrome OS and Microsoft [8] | Much faster here |
| Many people changing the same code | Changes to files others had also been editing caused 1.23 times the bugs (finding 20). Authors new to a file did no worse | In Windows Vista and Windows 7, how many low-expertise developers changed a component, and how much of it its top owner wrote, were related to its faults before release and its failures after [14] | Same direction for shared code. The "unfamiliar author" part does not show here |

### What stands out, and what does not

Three things in these numbers depart from what the studies describe:

- **Almost no change is reviewed by a second person.** Authors merge their own changes, and the reviewer is a bot.
- **Changes are large.** 1.5% of commits change more than 100 files, and those carry
  26% of the traced bugs.
- **A fifth of changes merge while the bot objects**, and those carry more bugs at equal size (finding 12).

One more thing follows from these: the bugs are not spread evenly. A small, recognisable share of changes carries
about half of them (finding 17).

On whether more people would help, the numbers say four things and leave one open. The work runs through few hands:
one account merges 54.3% of pull requests and three merge 73.6%. Nothing
shows an individual is overloaded: a person's heavy days are no worse than their light ones, though the project's
busiest days are (finding 18). Changes from occasional contributors carry fewer bugs than the core's (finding 19).
Bugs are more common where several people edit the same files (finding 20). What stays open is whether a second pair of eyes helps, because only
1.0% of pull requests get one.

Several things that might look alarming are ordinary by the same studies: half of all changes being fixes, fixes
that introduce new bugs, changes titled "fix" that fix nothing, and a reviewer that misses functional bugs.

### What this study can and cannot say about coding agents

It cannot attribute any change to an agent or a person. Git records who landed a change, and this project's rules ask
for no agent attribution on commits. So nothing here measures agent-written code against human-written code.

What the numbers do show is the working pattern: 531 commits a day through
40 accounts that merge, one account opening 52.1% of pull requests,
11% opened by automation accounts, and a median of 70
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

**Scope.** Changes merged to `main` from 10 September to 22 November 2026. One model (gpt-6.2-sol) read every fix.
A model from a different maker (Claude Opus 5.5) had earlier read the 300 November fixes, and its
answers serve as the check. No project code was run and no test was written. Findings 7 to 10 cover
November only. Findings 1, 3, 4 and 11 to 21 set the traced bugs against every commit and pull
request of the period. Findings 22 and 23 put the two periods and the two models side by side.

**An earlier version.** A first version of this report covered only the 300 November fixes, with Claude Opus 5.5 as the
main model. It is kept as the tag `published-2026-11`, and [CORRECTIONS.md](CORRECTIONS.md) lists what changed.

**How this repository is organised.** `dataset/` holds the facts. `questions/` holds one script per question; each
reads only the dataset and writes the numbers and charts used on this page. `python3 study.py rebuild` runs them all and
re-renders this page. [PROTOCOL.md](PROTOCOL.md) is the experimental setup: every step of the study, and how to
regenerate it from nothing or extend it to other dates with one command and one settings file.
Claims that an earlier draft made and a later check weakened are listed in [CORRECTIONS.md](CORRECTIONS.md).

## How each study was done

| Study | Cases | How cases were chosen | Who judged | Independent check |
|---|---:|---|---|---|
| What fixes repaired | 1,202 | Lottery over every fix in the period, in a fixed pseudo-random order | One gpt-6.2-sol model per fix | Second run of the same model on 191; Claude Opus 5.5 on the 300 November fixes |
| What the bot had said | 645 | Every traced bug whose causing change the bot reviewed | One gpt-6.2-sol model per case | Claude Opus 5.5 on 88 November cases with the same causing change |
| Blind review (November) | 30 | First 15 of each kind in random order, among smaller recent changes the bot reviewed | Claude Opus 5.5 graders, blind to the reviewer | GPT grader on all pairs; run logs audited for leaks |
| Are the reports real | 148 | Every report from the two strongest reviewers | One later-fix model; two code-tracing checkers | Known-real reports as a control, before and after the fix |
| Kinds of change compared | 400 | Lottery over every merged pull request since 10 September, plus every bug-causing one | Nobody: read from git and GitHub | The bot's verdict is read from its own marker |
| Workload, people and files (findings 1 and 18 to 21) | 39,210 | Every commit on main since 10 September; the bugs are the 505 sampled bugs whose causing commit is among them | Nobody: read from git and GitHub | Size and kind of change held equal; heavy-day result repeated without the most active author |
| Written rules (November, first study) | 29 | Fixes whose wording blames an earlier change | Claude models, verdicts re-read | Three cases checked against source by hand |

## Limits that apply throughout

- Every classification is a model's judgment made in hindsight from code changes and PR text. Two models from different companies
  agreeing reduces the risk of one model's habit; it does not make the judgment a measurement.
- Nothing was executed. No bug was reproduced and no reported problem was confirmed by a failing test.
- The period is ten and a half weeks of one project. Finding 22 shows the earlier weeks agree with November; it
  does not show another project would.
- The main model worked without GitHub lookups and could trace a cause back to 1 July 2026 and no further. It
  answered "could not tell" more often than the second model, which had lookups.
- 327 of the 832 traced bugs are left out of findings 1, 3, 4 and 11 to 21, because
  their causing change is older than 10 September, where the commit list starts, or was not a pull request.
- Findings 7 to 10 cover 30 November cases, chosen when Claude Opus 5.5 was the main model, and were not repeated for the
  earlier weeks.
- A sample of fixes cannot see bugs that were never fixed, or bugs the bot stopped before merge.
- The model comparison covers changes of at most 30 files and one run per reviewer. The reviewers did not get
  identical guidance: some GPT runs read a personal review guide on the test machine, and the Claude runs had the
  repository's current contributor guide in context. Neither contains the answers.
- Findings 1 and 18 to 21 make about thirty comparisons on the same 505 bugs. By chance alone, one or two
  of thirty would look like a clear difference. The two we call supported (findings 1 and 20) are far from the
  line; the others that cross it are labelled tentative.
- The data files record the public author and merger of each change, as GitHub shows them. The report draws no
  conclusion about any person.

## All findings at a glance

Each finding carries a label for how far it can be trusted. **Measured** means counted from git or GitHub, with
nothing judged. **Well supported** means a large effect that held when checked a second way. **Supported** means a
clear effect resting on one method. **Tentative** means a small number of cases, or a range that barely clears "no
difference". **Depends on the model** means two models gave different answers.

**As expected** and **Surprising** are our own reading of whether an engineer would have guessed the result. They
say nothing about how well supported it is.

| # | | Strength | Finding |
|---|---|---|---|
| 1 | As expected | Well supported | Changes that add new code files are 13.7% of commits and the source of 69% of the traced bugs. |
| 2 | Surprising | Supported | New code that never worked accounts for about as many bugs as working things broken later: 443 against 389 by the main model. The second model, on the November fixes, found twice as many never-worked. When both name a cause, they usually name the same change. |
| 3 | As expected | Well supported | Changes titled as new features cause far more than their share of bugs. The title "fix" tells you little. |
| 4 | As expected | Well supported | Large changes cause far more bugs per change, but about the same per file changed. |
| 5 |  | Supported | A broken thing typically stayed broken for one to four weeks, unless someone traced the cause at once. |
| 6 | Surprising | Well supported | The review bot had rarely named the bug before the change merged: 21 of 645. |
| 7 |  | Supported, November only | Two current models together named more of the known bugs than the bot had. For either model alone, the gap could still be chance. |
| 8 |  | Supported, November only | Most of the other problems those models reported hold up when checked, and about a third of them are minor. |
| 9 | Surprising | Tentative, November only | About a third of the bugs could not be seen by reading code at all. This rests on nine cases. |
| 10 |  | Tentative, November only | Most bugs broke no written rule. |
| 11 | Surprising | Supported | Changes committed straight to main, without a pull request, caused fewer bugs per change, not more. |
| 12 | Surprising | Well supported | Changes merged while the bot objected carried 3.42 times the bugs of changes it called ready, at equal size and month. Its objection marks risk even when its words do not name the bug. |
| 13 |  | Tentative | Merging minutes after the bot's review, or after it saw only an earlier revision, shows no clear extra risk. |
| 14 | Surprising | Supported | Pull requests merged within the hour carried far fewer bugs than those open a day or more. |
| 15 |  | Measured | 88.8% of pull requests were merged by their own author. Another person reviewed 1.0% of them before the merge. |
| 16 | Surprising | Supported | Attaching a screenshot or video did not go with fewer bugs. Among interface changes, those with one caused 3.72 times as many, at equal size and month. |
| 17 | Surprising | Supported | Bugs are concentrated. Changes with at least two of three warning signs are 6.8% of changes and the source of 48% of traced bugs. |
| 18 | Surprising | Supported, and one tentative result | An individual's workload shows no effect. Changes landed on the project's busiest days carried 1.73 times the bugs of changes landed on its quietest. |
| 19 | Surprising | Supported | Changes from occasional contributors, and changes merged by someone other than their author, carried about half the bugs. Review by a second person is too rare to measure. |
| 20 | As expected | Supported | Changes to files that two or more other people were also editing caused 1.67 times the bugs of changes to files only their author was editing. |
| 21 | Surprising | Measured | 494 of the 505 traced bugs came from a change that also changed tests. No part of the code stands out. |
| 22 |  | Supported | The earlier weeks look like November when the same model reads both. What differs is the model: the two models disagree on what counts as a bug, and agree on what caused one. |
| 23 |  | Depends on the model | Between about a tenth and a third of changes titled "fix" repair no bug. Two models drew the line differently, and each was consistent with itself. |

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
