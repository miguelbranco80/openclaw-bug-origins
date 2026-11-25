# Where OpenClaw's bugs come from

An independent study of the public [openclaw/openclaw](https://github.com/openclaw/openclaw) repository. It is not
affiliated with or endorsed by the OpenClaw project. It judges changes, not people.

We traced a random sample of 300 fixes from three weeks back to what each one repaired. By the first
readers' count, 105 were new code that never worked and 51
were working things broken by a later change; a second model put the two kinds closer to even. The project's review
bot had named the bug in 2 of the 113 bug-causing changes it reviewed. Two
current models, shown 30 of those changes with no hint, each named 7.

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
| 2 | Supported | New code that never worked accounts for at least as many bugs as working things broken later: from about even (0.94 to one, by a second model) to about double (2.06 to one, by the first readers). When both models trace a bug to a cause, they name the same change. |
| 3 | Well supported | Changes titled as new features cause far more than their share of bugs. The title "fix" tells you little. |
| 4 | Well supported | Large changes cause far more bugs per change, but about the same per file changed. |
| 5 | Well supported | A broken thing typically stayed broken for about three weeks, unless someone traced the cause at once. |
| 6 | Well supported | The review bot had rarely named the bug before the change merged. |
| 7 | Supported | Two current models together named more of the known bugs than the bot had. For either model alone, the gap could still be chance. |
| 8 | Supported | Most of the other problems those models reported hold up when checked, and about a third of them are minor. |
| 9 | Tentative | About a third of the bugs could not be seen by reading code at all. This rests on nine cases. |
| 10 | Tentative | Most bugs broke no written rule. |
| 11 | Tentative | Changes committed straight to main, without a pull request, show no sign of causing more bugs. |
| 12 | Supported | Changes merged while the bot objected carried 2.58 times the bugs of changes it called ready, at equal size. Its objection marks risk even when its words do not name the bug. |
| 13 | Tentative | Merging minutes after the bot's review, or after it saw only an earlier revision, shows no clear extra risk once size is held equal. |
| 14 | Supported | Who opened a change, and whether its author merged it, made no detectable difference. Pull requests open a day or more carried far more bugs than those merged within the hour. |
| 15 | Measured | 88.8% of pull requests were merged by their own author and 95.5% had no review by a person. |

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

We drew 300 fixes by lottery from the 3,996 merged in the period and asked of
each: what was broken, and how did it get that way? By the first readers' strict rule, nothing had been broken in
100 of them: they were redesign steps, speed-ups, wording changes or tooling work that
carried the title "fix". A model from a different maker, given the same written rule, called only
8% of the fixes it re-read "not a bug". The cases they dispute are improvements that can
also be described as a flaw present from the start: a slow path made faster, a log message made more precise, a
report that never fitted a phone screen.

**What each of the 300 sampled fixes repaired, by the first readers' rule**

![What each of the 300 sampled fixes repaired, by the first readers' rule](charts/q01-what-fixes-repaired-light.svg#gh-light-mode-only)
![What each of the 300 sampled fixes repaired, by the first readers' rule](charts/q01-what-fixes-repaired-dark.svg#gh-dark-mode-only)

<details><summary>The numbers behind this chart</summary>

| | Count | Plausible range |
|---|---:|---:|
| New code that never worked | 105 | 30–41% |
| Not a bug: redesign, speed-up, wording or tooling | 100 | 28–39% |
| A working thing that a later change broke | 51 | 13–22% |
| Old code that broke because something outside changed | 29 | 7–14% |
| Could not tell | 15 | 3–8% |

</details>

**How two makers' models sorted the same 60 fixes**

![How two makers' models sorted the same 60 fixes](charts/q01-two-readers-light.svg#gh-light-mode-only)
![How two makers' models sorted the same 60 fixes](charts/q01-two-readers-dark.svg#gh-dark-mode-only)

<details><summary>The numbers behind this chart</summary>

| | First reader (Claude) | Second reader (GPT) |
|---|---:|---:|
| New code that never worked | 17 | 16 |
| Not a bug: redesign, speed-up, wording or tooling | 22 | 5 |
| A working thing that a later change broke | 15 | 17 |
| Old code that broke because something outside changed | 5 | 6 |
| Could not tell | 1 | 16 |

</details>

- **How we know.** One model reader per fix worked from the fix's diff, its PR text and the history of the changed
  lines, with a written rubric that told it to answer "could not tell" when the evidence was thin.
- **How it was checked.** A second reader, blind to the first answer, re-read 47 fixes and agreed
  on bug or not a bug for 41. A reader from a different model maker re-read
  60 and agreed for only 42. It answered "could not tell" for
  16, partly because it could not look up changes older than September 2026.
- **What it does not show.** A single right number. Treat the first readers' third as the upper end and the second
  model's share as the lower end. It also cannot show bugs nobody has fixed yet, or bugs fixed under another title.

Recompute: `python3 questions/q01_how_many_fixes_repair_a_real_bug.py`

## 2. New code that never worked accounts for at least as many bugs as working things broken later

*Supported. About double by the first readers' full count; closer to even under stricter cuts and under a second
model. Neither reading puts never-worked bugs clearly below.*

Of the 156 bugs we could trace to the change that introduced them, 105 were
new code that was wrong from the start and 51 were working things that a later change
broke. The two kinds need different defenses. A test of the old behavior can catch a broken-later bug. A
never-worked bug has no old behavior to test against, so the only chance to catch it is when the new code is
reviewed or first run.

**Never-worked against broken-later bugs, under stricter readings**

![Never-worked against broken-later bugs, under stricter readings](charts/q02-never-worked-or-broken-later-light.svg#gh-light-mode-only)
![Never-worked against broken-later bugs, under stricter readings](charts/q02-never-worked-or-broken-later-dark.svg#gh-dark-mode-only)

<details><summary>The numbers behind this chart</summary>

| | Never worked | Broken later |
|---|---:|---:|
| Every traced bug | 105 | 51 |
| Reader was confident or fairly confident of the cause | 92 | 48 |
| Reader was confident of the cause | 30 | 24 |
| Cause is a commit since 10 Sep 2026, readable in full | 65 | 43 |
| First readers, on the fixes that were re-read | 17 | 15 |
| Second model, on the same fixes | 16 | 17 |

</details>

Older causes are harder to trace, and a reader who cannot find an earlier working version may lean toward "never
worked". That is one reason the gap narrows when only confident or recent cases are kept. The last two rows are the
60 fixes a second model re-read; on that smaller set both readers put the two kinds about even.

- **How we know.** The reader had to point at the lines in the causing change that were wrong, and to say whether the
  behavior had worked before that change.
- **How it was checked.** Where two readers both chose one of these two kinds, they made the same choice in
  25 of 27 cases. The reader from a different maker made the
  same choice in 19 of 20, and named the same causing change in
  18 of 20.
- **What it does not show.** A firm ratio, or that features are the problem. New code arrives in changes of every
  title, as the next finding shows.

Recompute: `python3 questions/q02_new_code_or_broken_later.py`

## 3. Changes titled as new features cause far more than their share of bugs

*Well supported. Measured against every commit on main in the same period, not against an estimate.*

For each traced bug we looked at the change that introduced it. Its title tells you little:
84 of the 156 were themselves titled "fix", but so is about half of everything
merged, and some of those are large additions. One, titled as a fix, changed 138 files and added a whole rollback
mechanism. Changes titled "feat" are a small share of all commits and a large share of causes.

**Bug-causing changes against all commits, in percent**

![Bug-causing changes against all commits, in percent](charts/q03-causing-changes-against-all-light.svg#gh-light-mode-only)
![Bug-causing changes against all commits, in percent](charts/q03-causing-changes-against-all-dark.svg#gh-dark-mode-only)

<details><summary>The numbers behind this chart</summary>

| | Bug-causing changes, % | All commits, % |
|---|---:|---:|
| Titled feat | 26 | 3.4 |
| Titled fix | 55 | 50.9 |
| Changed more than 30 files | 48 | 10.7 |
| Changed more than 100 files | 25 | 1.5 |

</details>

**Title of the causing change, by kind of bug**

![Title of the causing change, by kind of bug](charts/q03-title-of-causing-change-light.svg#gh-light-mode-only)
![Title of the causing change, by kind of bug](charts/q03-title-of-causing-change-dark.svg#gh-dark-mode-only)

<details><summary>The numbers behind this chart</summary>

| | Never worked | Broken later |
|---|---:|---:|
| Titled fix | 53 | 31 |
| Titled feat (a new feature) | 42 | 6 |
| Another title | 10 | 14 |

</details>

- **How we know.** The comparison uses the 108 sampled bugs whose causing change was made
  since 10 September 2026 and all 39,210 commits on main since that date, counted from git.
- **How it was checked.** Titles and file counts are read mechanically from git, not judged. Which change caused
  each bug is the reader's judgment from finding 2.
- **What it does not show.** What the change was really for. A title is a label, and "fix" covers everything from a
  one-line repair to a 138-file addition.

Recompute: `python3 questions/q03_what_kind_of_change_introduces_bugs.py`

## 4. Large changes cause far more bugs per change, but about the same per file changed

*Well supported for the direction. The per-file figures rest on 10 to 45 bugs per size group.*

A causing change touched a median of 28.5 files; an ordinary commit touches
4. Per change, a commit of over 100 files carried about
104 times the bugs of a commit of 1 to 5 files.

**Bugs per 100 commits, by size of the change**

![Bugs per 100 commits, by size of the change](charts/q04-bugs-per-100-commits-light.svg#gh-light-mode-only)
![Bugs per 100 commits, by size of the change](charts/q04-bugs-per-100-commits-dark.svg#gh-dark-mode-only)

Per file changed, the picture is different: between 1.76 and 3.8 bugs
per 1,000 files changed in every size group, with no trend. On this evidence large changes hold more bugs because
they hold more change, not because each part of them is worse.

**Bugs per 1,000 files changed, by size of the change**

![Bugs per 1,000 files changed, by size of the change](charts/q04-bugs-per-1000-files-light.svg#gh-light-mode-only)
![Bugs per 1,000 files changed, by size of the change](charts/q04-bugs-per-1000-files-dark.svg#gh-dark-mode-only)

<details><summary>The numbers behind this chart</summary>

| | Commits | Sampled bugs | Bugs per 100 commits | Bugs per 1,000 files changed |
|---|---:|---:|---:|---:|
| 1 to 5 files | 22130 | 10 | 0.6 | 2.34 |
| 6 to 30 files | 12883 | 46 | 4.76 | 3.8 |
| 31 to 100 files | 3623 | 25 | 9.19 | 1.76 |
| Over 100 files | 574 | 27 | 62.66 | 3.1 |

</details>

- **How we know.** Every commit on main since 10 September 2026 is placed in a size group by files changed. A bug is
  one sampled fix traced to a causing commit in that list (108 cases), scaled from the sample of 300 to
  all fixes in the period. So a rate reads as "bugs fixed in the three weeks, per 100 commits made since 10
  September".
- **How it was checked.** Sizes come from git. The causing commit is the reader's judgment; two makers' models named
  the same one in 18 of 20 cases.
- **What it does not show.** Risk per line, or whether splitting a large change would lower the total. It also
  counts only bugs fixed in the three weeks, so slow-to-surface bugs from recent changes are missing.

Recompute: `python3 questions/q04_do_large_changes_cause_more_bugs.py`

## 5. A broken thing typically stayed broken for about three weeks

*Well supported. Dates come from git. The split depends on the reader naming the right causing change.*

**Broken-later bugs, by time from cause to fix**

![Broken-later bugs, by time from cause to fix](charts/q05-age-of-broken-later-bugs-light.svg#gh-light-mode-only)
![Broken-later bugs, by time from cause to fix](charts/q05-age-of-broken-later-bugs-dark.svg#gh-dark-mode-only)

**Median days from the causing change to the fix**

![Median days from the causing change to the fix](charts/q05-median-days-to-fix-light.svg#gh-light-mode-only)
![Median days from the causing change to the fix](charts/q05-median-days-to-fix-dark.svg#gh-dark-mode-only)

<details><summary>The numbers behind this chart</summary>

| | Count |
|---|---:|
| Under a day | 12 |
| 1 to 7 days | 5 |
| 7 to 30 days | 17 |
| Over 30 days | 17 |

</details>

Only 18 of the 51 broken-later fixes say which change caused the bug,
and those were fixed within a day. The rest took weeks. Scaled from the sample, about 680
broken-later bugs were fixed in the three weeks (plausibly 520 to 880).

- **How we know.** Days are the commit time of the fix minus the commit time of the causing change, both on main.
- **How it was checked.** An earlier study that could only find fixes naming their cause had put the typical time at
  1.7 days. The random sample shows that figure described the quick cases only.
- **What it does not show.** How long users were affected, or how many noticed. A bug counts only once it is fixed,
  so long-lived bugs still open are missing and the true typical time is longer.

Recompute: `python3 questions/q05_how_long_do_bugs_live.py`

## 6. The review bot had rarely named the bug before the change merged

*Well supported. Every case read twice, by models from two makers, with close agreement.*

For each of the 156 traced bugs we read what the bot had written on the causing change at the moment
it merged, rebuilt from the comment's edit history. It had reviewed 113 of them and named the bug
in 2. Both readers agree on those. They differ on how often it raised a related concern:
11 by the first reader, 17 by the second.

**What the bot's review said about the bug, by two readers**

![What the bot's review said about the bug, by two readers](charts/q06-what-the-review-said-light.svg#gh-light-mode-only)
![What the bot's review said about the bug, by two readers](charts/q06-what-the-review-said-dark.svg#gh-dark-mode-only)

<details><summary>The numbers behind this chart</summary>

| | First reader (Claude) | Second reader (GPT) |
|---|---:|---:|
| Said nothing about this bug | 100 | 94 |
| Raised a related concern, not this failure | 11 | 17 |
| Named this bug | 2 | 2 |

</details>

**Whether the bot had reviewed the causing change**

![Whether the bot had reviewed the causing change](charts/q06-was-there-a-review-light.svg#gh-light-mode-only)
![Whether the bot had reviewed the causing change](charts/q06-was-there-a-review-dark.svg#gh-dark-mode-only)

**The bot's overall verdict when the change merged**

![The bot's overall verdict when the change merged](charts/q06-verdict-at-merge-light.svg#gh-light-mode-only)
![The bot's overall verdict when the change merged](charts/q06-verdict-at-merge-dark.svg#gh-dark-mode-only)

Warnings were not being ignored. 69 changes merged while the bot said "blocked" or "needs
changes", but in 59 of them its open items were about something other than the
bug, such as missing proof. Only 7 items that touched the bug were open and unanswered at
merge. The bot also said "ready" on changes that carried a bug. Finding 12 adds the other half: although its words
rarely named the bug, the changes it objected to were the riskier ones.

- **How we know.** A reader compared each bug with the review text under a strict rule: it counts as named only if
  fixing what the review described would have prevented the bug.
- **How it was checked.** A reader from a different maker re-read all 113 and gave the same answer
  for 103. On whether the bug was named, they agreed for 113. Both
  "named" cases were also read by hand.
- **What it does not show.** How many bugs the bot stopped. A bug it caught and the author fixed before merge never
  appears in a sample of later fixes. This is a measure of what got past it, not of its worth.

Recompute: `python3 questions/q06_did_the_review_bot_name_the_bug.py`

## 7. Two current models together named more of the known bugs than the bot had

*Supported. Thirty smaller changes, one run each. Clear for the two models combined, not for either alone.*

We took 30 bug-causing changes and gave each reviewer the repository exactly as it stood at merge,
with no later history, and one plain instruction: find the defects this change introduces. Graders who did not know
which reviewer wrote what then checked whether any reported problem was the known bug.

**Known bugs named by each reviewer, out of 30**

![Known bugs named by each reviewer, out of 30](charts/q07-known-bugs-named-light.svg#gh-light-mode-only)
![Known bugs named by each reviewer, out of 30](charts/q07-known-bugs-named-dark.svg#gh-dark-mode-only)

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

## 8. Most of the other problems those models reported hold up when checked

*Supported. A fifth are proven by later fixes. The rest rest on code reading by two models, with a control but no
executed test.*

A reviewer that reports a lot will name the known bug more often by volume alone, so the other reports matter.
gpt-6.2 and Opus 5.5 reported 148 problems on the 30 changes; 14 were the known
bug. We checked each one two ways: was it later fixed on main, and do two checkers who trace the code agree the
failure happens?

**Where the 148 reported problems stand**

![Where the 148 reported problems stand](charts/q08-where-the-reports-stand-light.svg#gh-light-mode-only)
![Where the 148 reported problems stand](charts/q08-where-the-reports-stand-dark.svg#gh-dark-mode-only)

**The checkers tested on 14 known-real problems**

![The checkers tested on 14 known-real problems](charts/q08-can-the-checkers-say-no-light.svg#gh-light-mode-only)
![The checkers tested on 14 known-real problems](charts/q08-can-the-checkers-say-no-dark.svg#gh-dark-mode-only)

17 of the other reports were later fixed on main by someone else, which is proof they were
real. That count is a floor: the same search found the fix for only 8 of the
14 problems we already knew were fixed.

- **How we know.** The reports were pooled under anonymous labels with nothing marking the known bugs. One reader
  searched later fix commits; two checkers each traced every report in the exported code.
- **How it was checked.** The checkers were tested on the known-real problems, first on the original code and then on
  the code after the fix. After the fix, both still confirmed 3; two of those belong
  to a fix that was only partial.
- **What it does not show.** That the unfixed reports matter enough to block a merge. The two checkers are the same
  two models that wrote the reports, so they could share a convincing mistake. A failing test would settle it; none
  was written.

Recompute: `python3 questions/q08_are_the_other_reported_problems_real.py`

## 9. About a third of the bugs could not be seen by reading code

*Tentative. One reader's judgment on 30 cases; the key group is nine.*

**What a reviewer needed to see the bug, and how many were named**

![What a reviewer needed to see the bug, and how many were named](charts/q09-what-each-bug-needed-light.svg#gh-light-mode-only)
![What a reviewer needed to see the bug, and how many were named](charts/q09-what-each-bug-needed-dark.svg#gh-dark-mode-only)

No reviewer named a bug that depended on how a browser lays out a page, what a database accepts or how a filesystem
behaves under load. Size mattered too: reviewers named 6 of 12 bugs in
changes of 7 files or fewer, and 4 of 18 in larger ones.

- **How we know.** A reader given the bug and the causing change chose the least demanding thing a reviewer would
  have needed: the changed lines, other repository code, or outside knowledge.
- **How it was checked.** It was not checked by a second reader. The reader flagged several close calls between the
  first two groups.
- **What it does not show.** A firm share. Nine cases cannot fix a proportion; they show that such bugs exist in
  number and that none was caught by reading.

Recompute: `python3 questions/q09_could_the_bug_be_seen_by_reading.py`

## 10. Most bugs broke no written rule

*Tentative. A sample found by commit wording, which later proved to favor quickly fixed bugs.*

The project keeps written rules for contributors and for the bot. In the first study, of 29 bugs
whose fix names the causing change, a rule existed for 4 when the change was written, and
0 of those could have been checked from the changed lines alone.

**Whether a written rule covered what went wrong, of 29 bugs**

![Whether a written rule covered what went wrong, of 29 bugs](charts/q10-did-a-rule-cover-it-light.svg#gh-light-mode-only)
![Whether a written rule covered what went wrong, of 29 bugs](charts/q10-did-a-rule-cover-it-dark.svg#gh-dark-mode-only)

Recompute: `python3 questions/q10_did_a_written_rule_cover_it.py`

## 11. Changes committed straight to main show no sign of causing more bugs

*Tentative. The direct-commit side rests on 5 sampled bugs.*

8.6% of commits since 10 September reached main with no pull request number in the title.
Per commit they carried fewer bugs than changes that went through a pull request, not more.

**Bugs per 100 commits, by how the change reached main**

![Bugs per 100 commits, by how the change reached main](charts/q11-bugs-per-100-commits-by-route-light.svg#gh-light-mode-only)
![Bugs per 100 commits, by how the change reached main](charts/q11-bugs-per-100-commits-by-route-dark.svg#gh-dark-mode-only)

They are also smaller (a median of 2 files against 5),
so size alone could explain the gap. Within changes of 6 files or more, the rate was
10.36 for direct commits against 7.54 through a pull request.

<details><summary>The numbers behind this chart</summary>

| | Commits | Sampled bugs | Bugs per 100 commits |
|---|---:|---:|---:|
| Through a pull request | 35836 | 103 | 3.83 |
| Straight to main | 3374 | 5 | 1.97 |

</details>

- **How we know.** Same method as finding 4, split by whether the commit title carries a pull request number.
- **How it was checked.** It was not checked further. The ratio of the two rates is 0.52, with
  a plausible range of 0.21 to 1.26, which includes no difference.
- **What it does not show.** Who made the direct commits or why. Finding 12 takes up changes merged against the
  review bot's verdict.

Recompute: `python3 questions/q11_does_skipping_a_pull_request_matter.py`

## 12. Changes merged while the bot objected carried more bugs

*Supported. A comparison with ordinary changes, with size held equal. It shows a link, not a cause.*

Findings 1 to 11 start from bugs. To ask whether a kind of change causes more bugs, we also need to know how common
that kind is among ordinary changes. So we drew 400 merged pull requests at random and
recorded, for each, what the bot's review said at the moment it merged. The bot had called
64% of them ready and objected to 20.8%, which merged
anyway.

**Bugs per 100 changes, by what the bot said when the change merged**

![Bugs per 100 changes, by what the bot said when the change merged](charts/q12-bugs-by-bot-verdict-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by what the bot said when the change merged](charts/q12-bugs-by-bot-verdict-dark.svg#gh-dark-mode-only)

Changes merged over the bot's objection caused sampled bugs 4.8 times as often as
changes it called ready (plausibly 2.95 to 7.8). The bot objects more to large changes,
and large changes carry more bugs, so part of that is size. Comparing only changes of similar size, the ratio is
2.58 (plausibly 1.5 to 4.44). Changes the bot never
reviewed were no different from ones it called ready.

<details><summary>The numbers behind this chart</summary>

| | Ordinary changes in the sample | Sampled bugs | Bugs per 100 changes |
|---|---:|---:|---:|
| Bot said ready | 256 | 36 | 2.09 |
| Bot said blocked or needs changes | 83 | 56 | 10.03 |
| Bot said needs maintainer review | 1 | 0 | 0.0 |
| No bot review before merge | 60 | 11 | 2.73 |

</details>

- **How we know.** The comparison sample says how common each verdict is; the bug-causing changes say how many
  sampled bugs came from each. The ratio of those two is the relative bug rate. "Similar size" means within three
  groups: 1 to 5 files, 6 to 30, and over 30.
- **How it was checked.** The verdict is read mechanically from the marker the bot writes into its own comment, for
  the last version written before the merge. The causing change is the readers' judgment (finding 2).
- **What it does not show.** That merging against the verdict causes bugs. The bot objects to changes that are
  harder for other reasons too. And finding 6 still holds: in most of these cases its open items were about something
  other than the bug.

Recompute: `python3 questions/q12_does_merging_against_the_bot_matter.py`

## 13. Merging soon after the bot's review shows no clear extra risk

*Tentative. The intervals are wide and include no difference.*

**Bugs per 100 changes, by which revision the bot reviewed**

![Bugs per 100 changes, by which revision the bot reviewed](charts/q13-bugs-by-review-coverage-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by which revision the bot reviewed](charts/q13-bugs-by-review-coverage-dark.svg#gh-dark-mode-only)

Changes where the bot had seen only an earlier revision carried more bugs (2.24 times,
plausibly 1.33 to 3.78), but those are larger changes with more rounds of revision. At
equal size the ratio falls to 1.39 (plausibly
0.78 to 2.49), which includes no difference.

**Bugs per 100 changes, by time from the bot's review to merge**

![Bugs per 100 changes, by time from the bot's review to merge](charts/q13-bugs-by-time-to-merge-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by time from the bot's review to merge](charts/q13-bugs-by-time-to-merge-dark.svg#gh-dark-mode-only)

Changes merged within ten minutes of the bot's review did not carry more bugs: 0.66
times the rate of those merged an hour or more later, at equal size (plausibly
0.33 to 1.32), which includes no difference.

- **How we know.** Same method as finding 12, using which revision the bot reviewed and the minutes from its review
  to the merge.
- **What it does not show.** That speed is safe. Quick merges are mostly small, simple changes; the comparison cannot
  say what would happen if the hard ones were merged as fast.

Recompute: `python3 questions/q13_does_review_timing_matter.py`

## 14. Who opened or merged a change made no detectable difference; how long it stayed open did

*Supported for time open. The other comparisons are too thin to show a difference either way.*

**Bugs per 100 changes, by how long the pull request was open**

![Bugs per 100 changes, by how long the pull request was open](charts/q14-bugs-by-time-open-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by how long the pull request was open](charts/q14-bugs-by-time-open-dark.svg#gh-dark-mode-only)

Pull requests merged within an hour of being opened carried 0.19 times the bugs of those
open a day or more, at equal size (plausibly 0.09 to 0.39). A change that stays open is
usually one that needed work, and those are the ones that later needed fixing.

**Bugs per 100 changes, by who opened the change**

![Bugs per 100 changes, by who opened the change](charts/q14-bugs-by-author-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by who opened the change](charts/q14-bugs-by-author-dark.svg#gh-dark-mode-only)

**Bugs per 100 changes, by who merged it**

![Bugs per 100 changes, by who merged it](charts/q14-bugs-by-merger-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by who merged it](charts/q14-bugs-by-merger-dark.svg#gh-dark-mode-only)

**Bugs per 100 changes, by whether a person reviewed it**

![Bugs per 100 changes, by whether a person reviewed it](charts/q14-bugs-by-human-review-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by whether a person reviewed it](charts/q14-bugs-by-human-review-dark.svg#gh-dark-mode-only)

None of these three differences is distinguishable from none once size is held equal: maintainers against outside
contributors 0.58 (plausibly 0.19 to 1.75),
self-merged against merged by someone else 0.56 (plausibly
0.24 to 1.33), no person's review against a person's review
0.75 (plausibly 0.29 to 1.9).

- **How we know.** Same method as finding 12. A maintainer here is a person who merged at least one of the fetched
  pull requests; GitHub's own member label misses people whose membership is private.
- **What it does not show.** That review by a person does not help. Only 4.5% of changes
  had one, and people chose to review the risky ones, so the two groups are not alike.

Recompute: `python3 questions/q14_does_who_lands_the_change_matter.py`

## 15. How this project reviews and merges, in numbers

*Measured. Counted from git and GitHub; nothing is judged.*

**How ordinary pull requests were reviewed and merged, in percent**

![How ordinary pull requests were reviewed and merged, in percent](charts/q15-how-changes-are-merged-light.svg#gh-light-mode-only)
![How ordinary pull requests were reviewed and merged, in percent](charts/q15-how-changes-are-merged-dark.svg#gh-dark-mode-only)

| | |
|---|---:|
| Commits on main per day, 10 Sep to 22 Nov 2026 | 531 |
| People who merged at least one fetched pull request | 20 |
| Share of sampled pull requests opened by the most active account | 55.5% |
| Median time from opening a pull request to merging it | 70 minutes |
| Median time from the bot's review to the merge | 19 minutes |
| Share of commits titled "fix" | 50.9% |
| Share of commits changing fewer than 10 files | 70.8% |
| Mean files changed per commit | 13.4 |

Recompute: `python3 questions/q15_how_does_the_project_review_and_merge.py`

## How this compares with published research

Only studies whose figures we could check against the paper or its abstract are quoted. None of them studied this
project, and none measured exactly what we measured, so read each row as "same direction or not", not as a ranking.

| What | This project | Published research | Reading |
|---|---|---|---|
| Bug-causing changes are larger | Median 28.5 files against 4 for any commit | In Eclipse and Mozilla, changes that later needed a fix were about three times larger than others: 7.49 against 2.61 files, and 5.19 against 1.97 [1] | Same direction, and stronger here |
| Risk per change against risk per file | Per change, 104 times higher for the largest; per file changed, flat | A model of change risk at Bell Labs found how widely a change spreads across the code essential to predicting failure [2] | Consistent: a bigger change is more exposure |
| Share of changes that are fixes | 50.9% titled "fix" | 20.8% in Eclipse, 48.5% in Mozilla [1] | At the high end of what has been reported |
| Do fixes cause more bugs than other changes | No: "fix" is 55% of causes and 50.9% of commits | Three times more in Eclipse, no difference in Mozilla [1]. 14.8% to 24.4% of operating-system bug fixes were themselves wrong [3]; nearly 40% of fault fixes led to further faults in one telecom system [4] | Unremarkable. Fixes that break things are normal everywhere |
| "Fixes" that fix no bug | 8% to 33%, depending on the reader | 33.8% of bug reports in five open-source projects were not bugs [5] | In line |
| What review catches | The bot named 2 of 113 bugs that got through | About 75% of what code review finds concerns maintainability, not function [6]; reviews find fewer defects than teams expect [7] | Same in kind. Not like for like: those studies count what review found, ours counts what it missed |
| Review by a second person | 4.5% of changes; 88.8% merged by their own author | At Google a change typically needs approval from at least one reviewer; the median is one reviewer [8]. Other studied projects had a median of two [8] | The clearest departure from studied practice |
| Does review coverage matter | No detectable difference here (finding 14) | In Qt, VTK and ITK, components with low review coverage and participation had up to two and five more post-release defects [9]; a later study at Sony Mobile did not find the link [10] | Open. The research is mixed and our sample cannot tell |
| Size of an ordinary change | 70.8% of commits change fewer than 10 files; mean 13.4 | About 90% at Google, with a median of 24 lines [8]; mean 3.5 files in Eclipse and Mozilla [1] | Larger batches here |
| Speed of review | Median 70 minutes from opening to merge | Under 4 hours at Google; 15 to 24 hours at AMD, Chrome OS and Microsoft [8] | Much faster here |

### What stands out, and what does not

Three things in these numbers depart from what the studies describe:

- **Almost no change is reviewed by a second person.** Authors merge their own changes, and the reviewer is a bot.
- **Changes are large.** 1.5% of commits change more than 100 files, and those carry
  25% of the traced bugs.
- **A fifth of changes merge while the bot objects**, and those carry more bugs at equal size (finding 12).

Several things that might look alarming are ordinary by the same studies: half of all changes being fixes, fixes
that introduce new bugs, changes titled "fix" that fix nothing, and a reviewer that misses functional bugs.

### What this study can and cannot say about coding agents

It cannot attribute any change to an agent or a person. Git records who landed a change, and this project's rules ask
for no agent attribution on commits. So nothing here measures agent-written code against human-written code.

What the numbers do show is the working pattern: 531 commits a day through
20 people who merge, one account opening 55.5% of pull requests, and a
median of 70 minutes from opening to merge.

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

References 1 and 8 were read in full for the figures quoted. The others are quoted from their abstracts.

## How each study was done

| Study | Cases | How cases were chosen | Who judged | Independent check |
|---|---:|---|---|---|
| What fixes repaired | 300 | Lottery over every fix in the period, in a fixed pseudo-random order | One Claude Opus 5.5 reader per fix | Second Claude reader on 47; GPT reader on 60 |
| What the bot had said | 113 | Every traced bug whose causing change the bot reviewed | One Claude Opus 5.5 reader per case | GPT reader on all; both "named" cases read by hand |
| Blind review | 30 | First 15 of each kind in random order, among smaller recent changes the bot reviewed | Claude Opus 5.5 graders, blind to the reviewer | GPT grader on all pairs; run logs audited for leaks |
| Are the reports real | 148 | Every report from the two strongest reviewers | One later-fix reader; two code-tracing checkers | Known-real reports as a control, before and after the fix |
| Kinds of change compared | 400 | Lottery over every merged pull request since 10 September, plus every bug-causing one | Nobody: read from git and GitHub | The bot's verdict is read from its own marker |
| Written rules | 29 | Fixes whose wording blames an earlier change | Claude readers, verdicts re-read | Three cases checked against source by hand |

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
