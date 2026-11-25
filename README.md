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
| 15 | Measured | 88.8% of pull requests were merged by their own author. Another person reviewed 1.0% of them before the merge. |
| 16 | Supported | Attaching a screenshot or video did not go with fewer bugs. Among interface changes, those with one caused 5.3 times as many, at equal size. |
| 17 | Supported, not yet tested on new data | Bugs are concentrated. Changes with at least two of three warning signs are 6.8% of changes and the source of 47% of traced bugs. |
| 18 | Supported as "no sign found" | No sign that anyone is overloaded. Changes landed on an author's heavy days, on a merger's heavy days, on the project's busiest days, at weekends, or minutes after the previous one caused no more bugs than the rest. |
| 19 | Tentative | Changes from people who contribute rarely caused no more bugs than the most active author's. Too few changes get a second person to tell whether one helps. |
| 20 | Supported | Changes to files that other people were also editing caused 2.48 times the bugs of changes to files only their author was editing, at equal size and kind. |
| 21 | Well supported | Changes that add new code files are 13.7% of commits and the source of 66% of the traced bugs. |
| 22 | Measured | 106 of the 108 traced bugs came from a change that also changed tests. No part of the code stands out once size is held equal. |

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

*How to read it: Each bar is a number of sampled fixes. The five bars add up to 300.*

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

*How to read it: The same 60 fixes, sorted twice. Blue is where the first reader put them, orange where the second did; each color adds up to 60.*

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

**How much of the time the bug was new code that never worked, by three ways of counting**

![How much of the time the bug was new code that never worked, by three ways of counting](charts/q02-share-never-worked-light.svg#gh-light-mode-only)
![How much of the time the bug was new code that never worked, by three ways of counting](charts/q02-share-never-worked-dark.svg#gh-dark-mode-only)

*How to read it: Take only bugs that were one of two kinds: new code that never worked, or a working thing broken later. Each bar is the percentage that were the first kind. Past the dashed line means the first kind is the more common.*

<details><summary>The numbers behind this chart</summary>

| | Never worked | Broken later | Never worked, % |
|---|---:|---:|---:|
| Every traced bug | 105 | 51 | 67 |
| Reader was confident or fairly confident of the cause | 92 | 48 | 66 |
| Reader was confident of the cause | 30 | 24 | 56 |
| Cause is a commit since 10 Sep 2026, readable in full | 65 | 43 | 60 |
| First readers, on the fixes that were re-read | 17 | 15 | 53 |
| Second model, on the same fixes | 16 | 17 | 48 |

</details>

The first readers found twice as many never-worked bugs as broken-later ones. Counting only the bugs where they were
sure of the cause, the two kinds are closer. A second model, re-reading 60 of the fixes, found them about even. So
the safe statement is "at least as many", not "twice as many".

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

For each traced bug we looked at the title of the change that introduced it, and divided by how many commits carry
that title. Changes titled "feat" caused 28.1 bugs per 100 commits, against 3.9
for changes titled "fix" and 1.6 for everything else.

**Bugs per 100 commits, by how the change was titled**

![Bugs per 100 commits, by how the change was titled](charts/q03-bugs-per-100-commits-by-title-light.svg#gh-light-mode-only)
![Bugs per 100 commits, by how the change was titled](charts/q03-bugs-per-100-commits-by-title-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a rate: bugs fixed in the three weeks that trace back to commits with that title, per 100 such commits made since 10 September. The three titles cover every commit.*

<details><summary>The numbers behind this chart</summary>

| | Commits since 10 Sep | Sampled bugs | Bugs per 100 commits | Median files changed |
|---|---:|---:|---:|---:|
| Titled feat (a new feature) | 1325 | 28 | 28.1 | 19 |
| Titled fix | 19951 | 59 | 3.9 | 4 |
| Any other title (refactor, perf, test, chore, ...) | 17934 | 21 | 1.6 | 4 |

</details>

In absolute numbers most bugs still come from changes titled "fix" (84 of the
156 traced), because half of everything merged carries that title. And a title is a loose label:
one change titled as a fix touched 138 files and added a whole rollback mechanism. Feature changes are also larger
than others, so part of their higher rate is size, which is the next finding.

- **How we know.** The comparison uses the 108 sampled bugs whose causing change was made
  since 10 September 2026 and all 39,210 commits on main since that date, counted from git.
- **How it was checked.** Titles and file counts are read mechanically from git, not judged. Which change caused
  each bug is the reader's judgment from finding 2.
- **What it does not show.** What the change was really for, or how much of the gap is size. The rates are not
  adjusted for the size of the change.

Recompute: `python3 questions/q03_what_kind_of_change_introduces_bugs.py`

## 4. Large changes cause far more bugs per change, but about the same per file changed

*Well supported for the direction. The per-file figures rest on 10 to 45 bugs per size group.*

A causing change touched a median of 28.5 files; an ordinary commit touches
4. Per change, a commit of over 100 files carried about
104 times the bugs of a commit of 1 to 5 files.

**Bugs per 100 commits, by size of the change**

![Bugs per 100 commits, by size of the change](charts/q04-bugs-per-100-commits-light.svg#gh-light-mode-only)
![Bugs per 100 commits, by size of the change](charts/q04-bugs-per-100-commits-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a rate: bugs fixed in the three weeks that trace back to commits of that size, per 100 such commits made since 10 September. The four sizes cover every commit.*

Per file changed, the picture is different: between 1.76 and 3.8 bugs
per 1,000 files changed in every size group, with no trend. On this evidence large changes hold more bugs because
they hold more change, not because each part of them is worse.

**Bugs per 1,000 files changed, by size of the change**

![Bugs per 1,000 files changed, by size of the change](charts/q04-bugs-per-1000-files-light.svg#gh-light-mode-only)
![Bugs per 1,000 files changed, by size of the change](charts/q04-bugs-per-1000-files-dark.svg#gh-dark-mode-only)

*How to read it: The same bugs, divided by the total number of files those commits changed instead of by the number of commits.*

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

*How to read it: Each bar is a number of broken-later bugs. The four bars add up to 51.*

**Median days from the causing change to the fix, for three kinds of bug**

![Median days from the causing change to the fix, for three kinds of bug](charts/q05-median-days-to-fix-light.svg#gh-light-mode-only)
![Median days from the causing change to the fix, for three kinds of bug](charts/q05-median-days-to-fix-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the middle value of days on main before the fix, for one group of bugs. The three groups do not overlap.*

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

*How to read it: The same 113 reviews, read twice. Each bar is a number of bug-causing changes; each color adds up to 113.*

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

*How to read it: Each bar is a number of bug-causing changes. The four bars add up to 156.*

**The bot's overall verdict when the bug-causing change merged**

![The bot's overall verdict when the bug-causing change merged](charts/q06-verdict-at-merge-light.svg#gh-light-mode-only)
![The bot's overall verdict when the bug-causing change merged](charts/q06-verdict-at-merge-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is a number of bug-causing changes the bot had reviewed. The four bars add up to 113.*

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

*How to read it: Each bar is a number of reported problems. The four bars add up to 148.*

**Known-real problems each checker confirmed, before and after the bug was fixed**

![Known-real problems each checker confirmed, before and after the bug was fixed](charts/q08-can-the-checkers-say-no-light.svg#gh-light-mode-only)
![Known-real problems each checker confirmed, before and after the bug was fixed](charts/q08-can-the-checkers-say-no-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is how many of the same 14 real problems the checker said were present. A sound checker is high in blue and low in orange.*

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

*How to read it: The gray bar is the number of bugs of that kind, out of 30. The blue part is how many of them any reviewer named.*

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

*How to read it: Each bar is a number of bugs. The four bars add up to 29.*

Recompute: `python3 questions/q10_did_a_written_rule_cover_it.py`

## 11. Changes committed straight to main show no sign of causing more bugs

*Tentative. The direct-commit side rests on 5 sampled bugs.*

8.6% of commits since 10 September reached main with no pull request number in the title.
Per commit they carried fewer bugs than changes that went through a pull request, not more.

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

*How to read it: Each bar is a rate: bugs fixed in the three weeks that trace back to changes merged under that verdict, per 100 such changes. Verdicts seen on fewer than 20 sampled changes are left out.*

Changes merged over the bot's objection caused sampled bugs 4.8 times as often as
changes it called ready (plausibly 2.95 to 7.8). The bot objects more to large changes,
and large changes carry more bugs, so part of that is size. Comparing only changes of similar size, the ratio is
2.58 (plausibly 1.5 to 4.44). Changes the bot never
reviewed were no different from ones it called ready.

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |
|---|---:|---:|---:|---|
| Bot said ready | 64% | 36 | 2.09 | (the baseline) |
| Bot said blocked or needs changes | 20.8% | 56 | 10.03 | 2.58 times (plausibly 1.5 to 4.44) |
| Bot said needs maintainer review | 0.2% | 0 | 0.0 | too few to say |
| No bot review before merge | 15% | 11 | 2.73 | 1.18 times (plausibly 0.54 to 2.6) |

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

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |
|---|---:|---:|---:|---|
| Bot reviewed the revision that merged | 70.5% | 63 | 3.32 | (the baseline) |
| Bot reviewed only an earlier revision | 14.5% | 29 | 7.43 | 1.39 times (plausibly 0.78 to 2.49) |
| No bot review before merge | 15% | 11 | 2.73 | 0.75 times (plausibly 0.35 to 1.6) |

Changes where the bot had seen only an earlier revision carried more bugs (2.24 times,
plausibly 1.33 to 3.78), but those are larger changes with more rounds of revision. At
equal size the ratio falls to 1.39 (plausibly
0.78 to 2.49), which includes no difference.

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |
|---|---:|---:|---:|---|
| Merged an hour or more after the bot's review | 20% | 29 | 5.39 | (the baseline) |
| Merged 10 to 60 minutes after it | 38.8% | 43 | 4.12 | 0.61 times (plausibly 0.32 to 1.14) |
| Merged within 10 minutes of it | 26.2% | 20 | 2.83 | 0.66 times (plausibly 0.33 to 1.32) |

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

*How to read it: Each bar is a rate: bugs fixed in the three weeks that trace back to pull requests open that long, per 100 such pull requests. The three groups cover every pull request.*

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |
|---|---:|---:|---:|---|
| Open a day or more | 10.2% | 30 | 10.88 | (the baseline) |
| Open 1 to 24 hours | 43.5% | 58 | 4.96 | 0.44 times (plausibly 0.23 to 0.84) |
| Open under an hour | 46.2% | 15 | 1.21 | 0.19 times (plausibly 0.09 to 0.39) |

Pull requests merged within an hour of being opened carried 0.19 times the bugs of those
open a day or more, at equal size (plausibly 0.09 to 0.39). A change that stays open is
usually one that needed work, and those are the ones that later needed fixing.

The other three comparisons show no difference that can be told from none once size is held equal. They are given
as tables, not charts, because a bar would suggest a difference the numbers do not support.

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |
|---|---:|---:|---:|---|
| Opened by an outside contributor | 9.2% | 6 | 2.41 | (the baseline) |
| Opened by a maintainer | 80.8% | 82 | 3.77 | 0.58 times (plausibly 0.19 to 1.75) |
| Opened by an automation account | 10% | 15 | 5.58 | 1.18 times (plausibly 0.36 to 3.82) |

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |
|---|---:|---:|---:|---|
| Merged by someone else | 11.2% | 10 | 3.3 | (the baseline) |
| Merged by its own author | 88.8% | 93 | 3.89 | 0.56 times (plausibly 0.24 to 1.33) |

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |
|---|---:|---:|---:|---|
| A person reviewed it before merge | 2.0% | 2 | 3.72 | (the baseline) |
| No person's review before merge | 98% | 101 | 3.83 | 0.78 times (plausibly 0.1 to 6.26) |

- **How we know.** Same method as finding 12. A maintainer here is a person who merged at least one of the fetched
  pull requests; GitHub's own member label misses people whose membership is private.
- **What it does not show.** That review by another person does not help. Only 2.0% of
  the sampled changes had one, and people chose to review the risky ones, so the two groups are not alike. Finding
  19 repeats this on every pull request, with the same answer.

Recompute: `python3 questions/q14_does_who_lands_the_change_matter.py`

## 15. How this project reviews and merges, in numbers

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

## 16. A screenshot or video in the pull request did not go with fewer bugs

*Supported. It shows what such pull requests are like, not what the screenshot did.*

The project asks for visual proof on visible changes, so we checked whether pull requests that carry it do better.
Screenshots and videos are attached almost only to interface changes, and interface changes cause more bugs than
others, so the fair comparison is among interface changes alone.

**Among interface changes: bugs per 100 changes, with and without a screenshot or video**

![Among interface changes: bugs per 100 changes, with and without a screenshot or video](charts/q16-bugs-by-visual-proof-light.svg#gh-light-mode-only)
![Among interface changes: bugs per 100 changes, with and without a screenshot or video](charts/q16-bugs-by-visual-proof-dark.svg#gh-dark-mode-only)

*How to read it: Only pull requests that change files under ui/ or apps/. Each bar is a rate: bugs fixed in the three weeks that trace back to such pull requests, per 100 of them.*

| Kind of change | Share of ordinary changes | Sampled bugs | Bugs per 100 changes | Against the first row, at equal size |
|---|---:|---:|---:|---|
| No screenshot or video in the description | 15.2% | 11 | 2.68 | (the baseline) |
| A screenshot or video in the description | 10.5% | 35 | 12.39 | 5.3 times (plausibly 2.17 to 12.94) |

Interface changes with a screenshot or video caused 5.3 times the bugs of interface
changes without one, at equal size (plausibly 2.17 to 12.94).

- **How we know.** For each of the 400 sampled pull requests and each bug-causing one, we read the
  description as it stood at merge and counted embedded pictures and videos. An interface change is one that touches
  files under `ui/` or `apps/`.
- **How it was checked.** Counts are mechanical. Nearly every description has an "Evidence" heading, so the heading
  alone says nothing; only an embedded picture or video counts here.
- **What it does not show.** That proof makes things worse. People attach screenshots to the changes a user will
  see, and a visible bug is the kind that gets noticed and fixed within three weeks. What it does show is that a
  screenshot of the change working once is not a sign the change is safe.

Recompute: `python3 questions/q16_do_changes_with_visual_proof_cause_fewer_bugs.py`

## 17. The bugs are concentrated in changes that could be pointed at beforehand

*Supported for this period. The three signs were picked after seeing the earlier findings, so this is a description,
not a tested prediction.*

Three things visible at or before merge each mark a small share of changes and a large share of bugs: the bot
objected, the pull request had been open a day or more, or the change touched more than 30 files.

**Share of the traced bugs that came from changes with each warning sign**

![Share of the traced bugs that came from changes with each warning sign](charts/q17-share-of-bugs-by-warning-sign-light.svg#gh-light-mode-only)
![Share of the traced bugs that came from changes with each warning sign](charts/q17-share-of-bugs-by-warning-sign-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the percentage of traced bugs whose causing change had that sign. The gray note says how common such changes are. A bar much longer than its note's percentage means bugs are concentrated there. The first three rows overlap; the last three are combinations of them.*

<details><summary>The numbers behind this chart</summary>

| | Share of all changes, % | Share of traced bugs, % | Sampled bugs |
|---|---:|---:|---:|
| The bot objected | 20.8 | 54 | 56 |
| Open a day or more | 10.2 | 29 | 30 |
| More than 30 files | 12.8 | 49 | 50 |
| At least one of the three signs | 37 | 70 | 72 |
| At least two of the three signs | 6.8 | 47 | 48 |
| None of the three signs | 63 | 30 | 31 |

</details>

Changes with at least two of the three signs are 6.8% of all changes and the source of
47% of the traced bugs. Changes with none are 63% of changes and
the source of 30%.

- **How we know.** The share of changes comes from the random comparison sample; the share of bugs from the
  103 sampled bugs whose causing change is a fetched pull request.
- **How it was checked.** All three signs are read from git and GitHub. No model judged them.
- **What it does not show.** That the same signs will mark the bugs of another period, or that looking harder at
  those changes would have caught the bugs. Finding 7 bears on the second point; nothing here tests the first.

Recompute: `python3 questions/q17_how_concentrated_are_the_bugs.py`

## 18. No sign that anyone is overloaded

*Supported as "no sign found". These are comparisons across every commit since 10 September, with no model
judging anything.*

The worry is simple: one person lands hundreds of changes a day, the project lands a thousand, and care must be
slipping. If that were so, changes landed under heavy load would cause more bugs than changes landed under light
load. We looked for that six ways and did not find it.

For the median commit, its author landed 175 changes that same day, and the previous
one 4.7 minutes earlier. On a typical day 14 accounts merge; one
account merges 54.3% of all pull requests and three accounts merge 73.6%.

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size and kind |
|---|---:|---:|---:|---|
| ***By how many changes the author landed that day*** | | | | |
| Author landed 1 to 5 changes that day | 10.6% | 13 | 4.19 | (the baseline) |
| 6 to 20 that day | 10.3% | 23 | 7.61 | 1.5 times (plausibly 0.74 to 3.04): no clear difference |
| 21 to 50 that day | 10% | 15 | 5.11 | 1.11 times (plausibly 0.52 to 2.37): no clear difference |
| 51 to 150 that day | 16.5% | 21 | 4.32 | 1.47 times (plausibly 0.72 to 3.01): no clear difference |
| Over 150 that day | 52.7% | 36 | 2.32 | 0.72 times (plausibly 0.37 to 1.39): no clear difference |
| ***By how soon after the author's previous change*** | | | | |
| An hour or more after the author's previous change | 15% | 26 | 5.89 | (the baseline) |
| 10 to 60 minutes after it | 19.8% | 26 | 4.46 | 0.88 times (plausibly 0.51 to 1.53): no clear difference |
| Under 10 minutes after it | 63.3% | 55 | 2.95 | 0.71 times (plausibly 0.44 to 1.15): no clear difference |
| ***By the author's own usual pace, leaving out the most active author*** | | | | |
| A light day for that author (under three quarters of their usual) | 4.7% | 7 | 5.09 | (the baseline) |
| A usual day for that author | 13.6% | 20 | 5.01 | 1.25 times (plausibly 0.52 to 3.04): no clear difference |
| A heavy day (over one and a half times their usual) | 23.1% | 36 | 5.29 | 1.38 times (plausibly 0.6 to 3.18): no clear difference |
| ***By how many pull requests the person merging merged that day*** | | | | |
| The merger merged 1 to 5 pull requests that day | 2.4% | 8 | 11.22 | (the baseline) |
| 6 to 20 that day | 8.7% | 17 | 6.65 | 0.85 times (plausibly 0.36 to 1.98): no clear difference |
| 21 to 50 that day | 13% | 19 | 4.98 | 0.67 times (plausibly 0.29 to 1.56): no clear difference |
| 51 to 150 that day | 20.6% | 25 | 4.12 | 0.74 times (plausibly 0.32 to 1.71): no clear difference |
| Over 150 that day | 46.7% | 34 | 2.47 | 0.46 times (plausibly 0.21 to 1.03): no clear difference |
| ***By how busy the whole project was that day*** | | | | |
| Quiet days for the project (under 410 commits) | 19.8% | 27 | 4.63 | (the baseline) |
| Middle days (410 to 591) | 32% | 31 | 3.29 | 0.69 times (plausibly 0.41 to 1.17): no clear difference |
| Busy days (592 or more) | 48.2% | 50 | 3.53 | 0.83 times (plausibly 0.52 to 1.34): no clear difference |
| ***By day of the week*** | | | | |
| Landed Monday to Friday | 71.1% | 79 | 3.77 | (the baseline) |
| Landed Saturday or Sunday | 28.9% | 29 | 3.41 | 0.86 times (plausibly 0.56 to 1.32): no clear difference |

Read each block against its first row. No row differs clearly from its baseline, and where the numbers lean, they
lean toward fewer bugs under heavier load, not more.

- **How we know.** For each of the 39,210 commits we counted how many the same author landed that
  day and how long since their previous one, and for each pull request how many the same person merged that day.
  The bugs are the 108 sampled bugs whose causing commit is among those commits. "At equal size and
  kind" compares changes of similar file count and the same title type (feat, fix, other).
- **One exception, and what it is.** Taking all authors together, an author's light days carried more bugs per
  change than their usual days (0.46 times on usual days, plausibly
  0.26 to 0.79). That comes from the single most active author, who lands over half of all
  commits. Without that author the three kinds of day are alike, as the third block shows.
- **What it does not show.** That the pace is harmless. A count per commit favors whoever cuts work into the most
  pieces, and a tired author's mistakes need not land on the same day. It shows only that heavier days are not
  where the traced bugs came from.

Recompute: `python3 questions/q18_does_author_workload_matter.py`; `python3 questions/q19_does_the_day_matter.py`; `python3 questions/q20_does_load_on_the_person_merging_matter.py`

## 19. Occasional contributors did no worse; a second person is too rare to measure

*Tentative. The groups are small.*

Would more contributors mean more bugs? One way to ask is whether changes from people who contribute rarely cause
more bugs than changes from the regulars.

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size and kind |
|---|---:|---:|---:|---|
| ***By how much the author contributes*** | | | | |
| The single most active author | 54% | 42 | 2.64 | (the baseline) |
| Other authors with over 500 commits | 31.2% | 39 | 4.25 | 1.49 times (plausibly 0.96 to 2.34): no clear difference |
| Authors with 21 to 500 commits | 10.1% | 24 | 8.06 | **1.91 times (plausibly 1.1 to 3.33)** |
| Authors with 20 commits or fewer | 4.7% | 3 | 2.16 | 0.78 times (plausibly 0.23 to 2.6): no clear difference |
| ***By whether a second person was involved*** | | | | |
| No second person: self-merged and unreviewed | 71% | 80 | 3.83 | (the baseline) |
| A second person merged or reviewed it | 10.4% | 8 | 2.62 | 0.75 times (plausibly 0.36 to 1.58): no clear difference |
| ***By whether another person reviewed it*** | | | | |
| No other person reviewed it before the merge | 80.8% | 86 | 3.62 | (the baseline) |
| Another person reviewed it before the merge | 0.6% | 2 | 12 | 1.91 times (plausibly 0.45 to 8.18): no clear difference |

- The 676 authors with 20 commits or fewer wrote 4.7% of
  commits and caused 3 of the sampled bugs: no more per change than the most active
  author.
- The 53 authors in the middle, with 21 to 500 commits, caused
  1.91 times as many per change (plausibly 1.1 to 3.33).
  The range only just excludes "no difference", and finding 14 saw none on a smaller sample.
- A second person merged or reviewed 10.4% of commits. Those caused no clearly
  different number of bugs. Only 222 commits came from a pull request another
  person had reviewed, which is too few to say anything.

- **How we know.** Authors are grouped by how many commits they landed since 10 September. Who merged and who
  reviewed comes from GitHub, for all 35,826 merged pull requests.
- **What it does not show.** Whether review by a second person would help. It is hardly practised here, so this
  data cannot answer it. Authors are told apart by commit email, so one person with two addresses counts twice.

Recompute: `python3 questions/q22_do_occasional_contributors_cause_more_bugs.py`; `python3 questions/q21_does_a_second_person_help.py`

## 20. Changes to files that other people were also editing caused more bugs

*Supported. It cannot separate "too many hands" from "the busiest, most central code".*

**Bugs per 100 changes, by how many other people were editing the same files**

![Bugs per 100 changes, by how many other people were editing the same files](charts/q23-bugs-by-how-many-people-edit-the-files-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by how many other people were editing the same files](charts/q23-bugs-by-how-many-people-edit-the-files-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the number of bugs per 100 changes of that kind. The first row is changes to files that mostly only their author had been editing; the rows below are changes to files that other people had also changed in the previous two weeks. Longer bars mean more bugs per change.*

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size and kind |
|---|---:|---:|---:|---|
| ***By how many other people changed the same files in the previous 14 days*** | | | | |
| Fewer than 1 other person per file in the last 14 days | 22.9% | 17 | 2.52 | (the baseline) |
| 1 to 2 other people per file | 20.5% | 43 | 7.14 | **2.48 times (plausibly 1.41 to 4.36)** |
| 2 or more other people per file | 14.5% | 32 | 7.5 | **2.69 times (plausibly 1.44 to 5.03)** |
| ***By whether the author had changed those files before*** | | | | |
| The author had changed every edited file before | 28.8% | 25 | 2.95 | (the baseline) |
| Some of them | 11% | 51 | 15.8 | **2.3 times (plausibly 1.33 to 3.98)** |
| None of them | 11.9% | 10 | 2.86 | 0.99 times (plausibly 0.47 to 2.07): no clear difference |

When the files a change edits had also been changed by other people in the previous two weeks, the change caused
about 2.48 times the bugs (plausibly 1.41 to 4.36) of a change
to files that only its author had been editing. Two or more other people per file was no worse than one.

Whether the author knew the files made no steady difference: authors editing files they had never changed before
did the same as authors who had changed all of them. The middle row, "some of them", is higher; those are changes
that reach beyond the author's own files into others.

- **How we know.** For every code file a commit edits, we counted the other authors who had changed that file in
  the 14 days before, and averaged over the commit's files. Only commits that edit existing code are compared.
- **What it does not show.** That several people editing a file is what causes the bugs. Files many people edit are
  also the central ones where most things connect, and this data cannot tell those two apart.

Recompute: `python3 questions/q23_do_files_many_people_edit_cause_more_bugs.py`

## 21. Changes that add new code files caused two thirds of the bugs

*Well supported. Counted from git; it agrees with findings 2 and 3 by a different route.*

**Bugs per 100 changes, by whether the change adds new code files**

![Bugs per 100 changes, by whether the change adds new code files](charts/q24-bugs-by-whether-the-change-adds-files-light.svg#gh-light-mode-only)
![Bugs per 100 changes, by whether the change adds new code files](charts/q24-bugs-by-whether-the-change-adds-files-dark.svg#gh-dark-mode-only)

*How to read it: Each bar is the number of bugs per 100 changes of that kind. The gray note gives how many of the sampled bugs came from such changes and how common such changes are.*

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size and kind |
|---|---:|---:|---:|---|
| Only edits existing code files | 59.3% | 37 | 2.12 | (the baseline) |
| Adds at least one new code file | 13.7% | 71 | 17.64 | **3.27 times (plausibly 1.98 to 5.39)** |

A change that adds at least one new code file is 13.7% of commits and the source of
71 of the 108 sampled bugs (66%). At equal size
and kind it caused 3.27 times the bugs of a change that only edits existing files
(plausibly 1.98 to 5.39).

- **How we know.** Git records which files a commit adds. A code file is a non-test file under `src/`, `ui/`,
  `extensions/`, `packages/` or `apps/`.
- **Why it matters here.** Finding 3 relied on the word "feat" in the title, which only 1,325
  commits carry. Adding a file is a fact, not a label, and it marks the same thing: new code is where the bugs are.
- **What it does not show.** That the bug sits in the new file. It says the change that carried the bug also added
  one.

Recompute: `python3 questions/q24_do_changes_that_add_new_files_cause_more_bugs.py`

## 22. Nearly every bug-causing change came with tests; no part of the code stands out

*Measured.*

| Kind of change | Share of all commits | Sampled bugs | Bugs per 100 commits | Against the baseline, at equal size and kind |
|---|---:|---:|---:|---|
| ***Among commits that change code: with or without tests*** | | | | |
| Changes code and tests together | 63.3% | 106 | 5.69 | (the baseline) |
| Changes code and no test file | 9.6% | 2 | 0.7 | 0.29 times (plausibly 0.07 to 1.13): no clear difference |
| ***By the part of the code the commit touches*** | | | | |
| Core code (src/, packages/), no interface or plugins | 45.5% | 43 | 3.21 | (the baseline) |
| Plugins (extensions/), no interface | 15.7% | 15 | 3.26 | 0.72 times (plausibly 0.4 to 1.3): no clear difference |
| Interface (ui/ or apps/) | 26% | 50 | 6.54 | 1.18 times (plausibly 0.75 to 1.84): no clear difference |
| Only docs, scripts, tests or config | 12.8% | 0 | 0.0 | too few to say |

- 106 of the 108 sampled bugs came from a change that also changed test files.
  The tests that came with a change did not catch the bug it carried.
- Code changes with no test file are few and small (refactors, chores, small fixes) and caused
  2 of the sampled bugs. This is not evidence that skipping tests is safe: the two
  groups are different kinds of change.
- Interface changes cause about twice the bugs per commit of core changes, but they are also larger. At equal size
  and kind, interface, plugin and core changes are alike.

- **How we know.** A test file is one whose path marks it as a test (`.test.`, `.spec.`, `.e2e.`, a `test` or
  `fixtures` folder). Each commit is put in one part of the code by the folders it touches.
- **What it does not show.** Whether the tests were good, or whether they ran. No test was run for this study.

Recompute: `python3 questions/q25_do_changes_with_tests_cause_fewer_bugs.py`; `python3 questions/q26_which_parts_of_the_code_cause_bugs.py`

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
| Review by a second person | 1.0% of pull requests; 88.8% merged by their own author | At Google a change typically needs approval from at least one reviewer; the median is one reviewer [8]. Other studied projects had a median of two [8] | The clearest departure from studied practice |
| Does review coverage matter | No detectable difference here (finding 14) | In Qt, VTK and ITK, components with low review coverage and participation had up to two and five more post-release defects [9]; a later study at Sony Mobile did not find the link [10] | Open. The research is mixed and our sample cannot tell |
| Size of an ordinary change | 70.8% of commits change fewer than 10 files; mean 13.4 | About 90% at Google, with a median of 24 lines [8]; mean 3.5 files in Eclipse and Mozilla [1] | Larger batches here |
| Speed of review | Median 70 minutes from opening to merge | Under 4 hours at Google; 15 to 24 hours at AMD, Chrome OS and Microsoft [8] | Much faster here |
| Many people changing the same code | Changes to files others had also been editing caused 2.48 times the bugs (finding 20). Authors new to a file did no worse | In Windows Vista and Windows 7, how many low-expertise developers changed a component, and how much of it its top owner wrote, were related to its faults before release and its failures after [14] | Same direction for shared code. The "unfamiliar author" part does not show here |

### What stands out, and what does not

Three things in these numbers depart from what the studies describe:

- **Almost no change is reviewed by a second person.** Authors merge their own changes, and the reviewer is a bot.
- **Changes are large.** 1.5% of commits change more than 100 files, and those carry
  25% of the traced bugs.
- **A fifth of changes merge while the bot objects**, and those carry more bugs at equal size (finding 12).

One more thing follows from these: the bugs are not spread evenly. A small, recognisable share of changes carries
about half of them (finding 17).

On whether more people would help, the numbers say four things and leave one open. The work runs through few hands:
one account merges 54.3% of pull requests and three merge 73.6%. Yet nothing
shows those hands are overloaded: heavy days are no worse than light ones (finding 18). Changes from occasional
contributors are no worse than the core's (finding 19). Bugs are more common where several people edit the same
files (finding 20). What stays open is whether a second pair of eyes helps, because only
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

## How each study was done

| Study | Cases | How cases were chosen | Who judged | Independent check |
|---|---:|---|---|---|
| What fixes repaired | 300 | Lottery over every fix in the period, in a fixed pseudo-random order | One Claude Opus 5.5 reader per fix | Second Claude reader on 47; GPT reader on 60 |
| What the bot had said | 113 | Every traced bug whose causing change the bot reviewed | One Claude Opus 5.5 reader per case | GPT reader on all; both "named" cases read by hand |
| Blind review | 30 | First 15 of each kind in random order, among smaller recent changes the bot reviewed | Claude Opus 5.5 graders, blind to the reviewer | GPT grader on all pairs; run logs audited for leaks |
| Are the reports real | 148 | Every report from the two strongest reviewers | One later-fix reader; two code-tracing checkers | Known-real reports as a control, before and after the fix |
| Kinds of change compared | 400 | Lottery over every merged pull request since 10 September, plus every bug-causing one | Nobody: read from git and GitHub | The bot's verdict is read from its own marker |
| Workload, people and files (findings 18 to 22) | 39,210 | Every commit on main since 10 September; the bugs are the 108 sampled bugs whose causing commit is among them | Nobody: read from git and GitHub | Size and kind of change held equal; heavy-day result repeated without the most active author |
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
- Findings 18 to 22 make about thirty comparisons on the same 108 bugs. By chance alone, one or two
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
