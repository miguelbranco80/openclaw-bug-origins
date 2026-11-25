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

## What the evidence supports, and how strongly

| Strength | Finding |
|---|---|
| Depends on definition | Between about a tenth and a third of changes titled "fix" repair no bug. Two models drew the line differently. |
| Supported | New code that never worked accounts for at least as many bugs as working things broken later: from about even (0.94 to one, by a second model) to about double (2.06 to one, by the first readers). |
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

We drew 300 fixes by lottery from the 3,996 merged in the period and asked of
each: what was broken, and how did it get that way? By the first readers' strict rule, nothing had been broken in
100 of them: they were redesign steps, speed-ups, wording changes or tooling work that
carried the title "fix". A model from a different maker, given the same written rule, called only
8% of the fixes it re-read "not a bug". The cases they dispute are improvements that can
also be described as a flaw present from the start: a slow path made faster, a log message made more precise, a
report that never fitted a phone screen.

| What each sampled fix repaired, by the first readers' rule | Count | Plausible share |
|---|---:|---:|
| New code that never worked | 105 | 30–41% |
| Not a bug: redesign, speed-up, wording or tooling | 100 | 28–39% |
| A working thing that a later change broke | 51 | 13–22% |
| Old code that broke because something outside changed | 29 | 7–14% |
| Could not tell | 15 | 3–8% |

"Plausible share" is where the true share of all fixes in the period plausibly lies, given a sample of 300 (a 95%
interval).

- **How we know.** One model reader per fix worked from the fix's diff, its PR text and the history of the changed
  lines, with a written rubric that told it to answer "could not tell" when the evidence was thin.
- **How it was checked.** A second reader, blind to the first answer, re-read 47 fixes and agreed
  on bug or not a bug for 41. A reader from a different model maker re-read
  60 and agreed for only 42.
- **What it does not show.** A single right number. Treat the first readers' third as the upper end and the second
  model's share as the lower end. It also cannot show bugs nobody has fixed yet, or bugs fixed under another title.

## Finding 2. New code that never worked accounts for at least as many bugs as working things broken later

*Supported. About double by the first readers' full count; closer to even under stricter cuts and under a second
model. Neither reading puts never-worked bugs clearly below.*

Of the 156 bugs we could trace to the change that introduced them, 105 were
new code that was wrong from the start and 51 were working things that a later change
broke. The two kinds need different defenses. A test of the old behavior can catch a broken-later bug. A
never-worked bug has no old behavior to test against, so the only chance to catch it is when the new code is
reviewed or first run.

| The same comparison under stricter readings | Never worked | Broken later |
|---|---:|---:|
| Every traced bug | 105 | 51 |
| Reader was confident or fairly confident of the cause | 92 | 48 |
| Reader was confident of the cause | 30 | 24 |
| Cause recent enough to read in full | 64 | 42 |
| First readers, on the fixes that were re-read | 17 | 15 |
| Second model, on the same fixes | 16 | 17 |

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
  title, as finding 3 shows.

### Check: a model from a different maker agrees on causes, and disagrees on what counts as a bug

All first readings were done by Claude models. A GPT model re-read 60 of the sampled fixes from the
same evidence, without the first answer. It chose the same category for only 26. The difference
is in two places: it called far fewer fixes "not a bug", and it answered "could not tell" for
16; where neither reader said that, they agreed on 26 of
43.

| How each reader sorted the re-read fixes | First reader (Claude) | Second reader (GPT) |
|---|---:|---:|
| New code that never worked | 17 | 16 |
| A working thing that a later change broke | 15 | 17 |
| Not a bug: redesign, speed-up, wording or tooling | 22 | 5 |
| Old code that broke because something outside changed | 5 | 6 |
| Could not tell | 1 | 16 |

The second reader had the evidence bundle and local history only. It could not look up changes older than September
2026 on GitHub, which the first reader could.

## Finding 3. Bug-causing changes are large, and new-feature changes cause far more than their share

*Well supported. Measured against every commit on main in the same period, not against an estimate.*

For each traced bug we looked at the change that introduced it. Its title tells you little: 84
of the 156 were themselves titled "fix", but so is about half of everything merged, and some of
those are large additions. One, titled as a fix, changed 138 files and added a whole rollback mechanism. Size and
newness tell you more.

| Share of changes that are... | Bug-causing changes | All commits |
|---|---:|---:|
| Titled feat | 25% | 3.3% |
| Titled fix | 56% | 50.9% |
| Changed more than 30 files | 48% | 10.7% |
| Changed more than 100 files | 25% | 1.5% |

| Title of the causing change | Never worked | Broken later |
|---|---:|---:|
| Titled fix | 53 | 31 |
| Titled feat (a new feature) | 42 | 6 |
| Another title | 10 | 14 |

A causing change touched a median of 28.5 files; an ordinary commit touches
4.

- **How we know.** The comparison uses the 106 causing changes made since 10 September 2026
  and all 38,812 commits on main since that date, counted from git.
- **How it was checked.** File counts and titles are read mechanically from git, not judged. Which change caused each
  bug is the reader's judgment from finding 2.
- **What it does not show.** That large changes are worse per file. The first look below suggests they are not.

### First look: is a large change riskier per file, and does skipping a pull request matter?

These two tables come from data already collected and have not had a second check. A "bug" is one sampled fix traced
to a causing commit made since 10 September (106 cases), scaled from the sample to the whole period.

| Size | Commits | Sampled bugs | Bugs per 100 commits | Bugs per 1,000 files changed |
|---|---:|---:|---:|---:|
| 1 to 5 files | 21,893 | 10 | 0.61 | 2.36 |
| 6 to 30 files | 12,746 | 45 | 4.7 | 3.76 |
| 31 to 100 files | 3,591 | 25 | 9.27 | 1.77 |
| Over 100 files | 571 | 26 | 60.65 | 3.0 |

Per commit, a change of over 100 files carried about a hundred times the bugs of a small one. Per file changed, the
rate is roughly flat. On this evidence large changes hold more bugs because they hold more change, not because each
part of them is worse.

| Route | Commits | Sampled bugs | Bugs per 100 commits |
|---|---:|---:|---:|
| Through a pull request | 35,427 | 101 | 3.8 |
| Straight to main | 3,374 | 5 | 1.97 |

Commits made straight to main, with no pull request number in the title, did not carry more bugs per commit. They
are also smaller, and the count rests on five cases. Whether changes merged against the review bot's verdict carry
more bugs cannot be answered yet: that needs the verdicts on a comparison sample of changes that caused no bug.

## Finding 4. A broken thing typically stayed broken for about three weeks

*Well supported. Dates come from git. The split depends on the reader naming the right causing change.*

| Broken-later bugs, by time from cause to fix | Count |
|---|---:|
| Under a day | 12 |
| 1 to 7 days | 5 |
| 7 to 30 days | 17 |
| Over 30 days | 17 |

| Median days from the causing change to the fix | Count |
|---|---:|
| Working things broken later, all | 20.4 |
| Broken later, fix says what caused it | 0.5 |
| Broken later, fix does not say | 24.2 |
| New code that never worked | 45.6 |

Only 18 of the 51 broken-later fixes say which change caused the bug,
and those were fixed within a day. The rest took weeks. Scaled from the sample, about 680
broken-later bugs were fixed in the three weeks.

- **How we know.** Days are the commit time of the fix minus the commit time of the causing change, both on main.
- **How it was checked.** An earlier study that could only find fixes naming their cause had put the typical time at
  1.7 days. The random sample shows that figure described the quick cases only.
- **What it does not show.** How long users were affected, or how many noticed. A bug counts only once it is fixed,
  so long-lived bugs still open are missing and the true typical time is longer.

## Finding 5. The review bot had rarely named the bug before the change merged

*Well supported. Every case read twice, by models from two makers, with close agreement.*

For each of the 156 traced bugs we read what the bot had written on the causing change at the moment
it merged, rebuilt from the comment's edit history. It had reviewed 113 of them and named the bug
in 2. Both readers agree on those. They differ on how often it raised a related concern:
11 by the first reader, 17 by the second.

| What its review said about the bug | First reader (Claude) | Second reader (GPT) |
|---|---:|---:|
| Said nothing about this bug | 100 | 94 |
| Raised a related concern, not this failure | 11 | 17 |
| Named this bug | 2 | 2 |

| Whether there was a review at all | Count |
|---|---:|
| Reviewed the revision that merged | 80 |
| Reviewed only an earlier revision | 33 |
| A PR, but no review before merge | 27 |
| No PR: committed straight to main | 16 |

| Its overall verdict when the change merged | Count |
|---|---:|
| Blocked | 51 |
| Needs changes | 18 |
| Needs maintainer review | 8 |
| Ready | 36 |

Warnings were not being ignored. 69 changes merged while the bot said "blocked" or "needs
changes", but in 59 of them its open items were about something other than the
bug, such as missing proof. Only 7 items that touched the bug were open and unanswered at
merge. The bot also said "ready" on changes that carried a bug.

- **How we know.** A reader compared each bug with the review text under a strict rule: it counts as named only if
  fixing what the review described would have prevented the bug.
- **How it was checked.** A reader from a different maker re-read all 113 and gave the same answer
  for 103. On whether the bug was named, they agreed for 113. Both
  "named" cases were also read by hand.
- **What it does not show.** How many bugs the bot stopped. A bug it caught and the author fixed before merge never
  appears in a sample of later fixes. This is a measure of what got past it, not of its worth.

## Finding 6. Two current models together named more of the known bugs than the bot had

*Supported. Thirty smaller changes, one run each. Clear for the two models combined, not for either alone.*

We took 30 bug-causing changes and gave each reviewer the repository exactly as it stood at merge,
with no later history, and one plain instruction: find the defects this change introduces. Graders who did not know
which reviewer wrote what then checked whether any reported problem was the known bug.

| Reviewer | Known bugs named, of 30 | Plausible rate | Same count, second grader | Problems reported |
|---|---:|---:|---:|---:|
| gpt-5.6-sol | 3 | 3–26% | 2 | 32 |
| gpt-6-astra | 1 | 1–17% | 1 | 13 |
| gpt-6.1-sol (the model the bot's README names) | 0 | 0–11% | 0 | 15 |
| gpt-6.2-sol | 7 | 12–41% | 8 | 98 |
| Claude Opus 5.5 | 7 | 12–41% | 7 | 50 |
| gpt-6.1-sol, three files at a time | 2 | 2–21% | 2 | 33 |
| The review bot's actual reviews at the time | 2 | 2–21% | – | – |

gpt-6.2 and Opus 5.5 together named 10 bugs and overlapped on
4, so they catch different things. How likely is a gap this large by luck alone?

| Comparison | Chance of a gap this large by luck |
|---|---:|
| The two top models together, against the bot | 0.021 |
| One top model, against the bot | 0.125 |
| One top model, against gpt-6.1 on the same instruction | 0.016 |
| Three files at a time, against the whole change | 0.5 |

The count is not a steady climb across model versions, and it follows how much each model reports. Of the
10 bugs that at least one reviewer named, 7 had been live for more
than ten days.

- **How we know.** Cases were the first 15 broken-later and first 15 never-worked bugs, in the sample's random order,
  among those the bot had reviewed, with a causing change of at most 30 files made since 10 September.
- **How it was checked.** A grader from a different maker regraded all 180 reviewer and case
  pairs and agreed on named or not for 178. Logs show no reviewer read later history, the fix,
  or another case. Two PR descriptions that had been edited after merge to mention the fix were replaced with their
  merge-time text.
- **What it does not show.** A like-for-like contest with the bot. The bot reviewed at the time, sometimes an earlier
  revision, with its own long instructions. It also does not cover changes of more than 30 files, which are where
  most bugs come from.

## Finding 7. Most of the other problems those models reported hold up when checked

*Supported. A fifth are proven by later fixes. The rest rest on code reading by two models, with a control but no
executed test.*

A reviewer that reports a lot will name the known bug more often by volume alone, so the other reports matter.
gpt-6.2 and Opus 5.5 reported 148 problems on the 30 changes; 14 were the
known bug. We checked each one two ways: was it later fixed on main, and do two checkers who trace the code agree the
failure happens?

| Where the reported problems stand | Count |
|---|---:|
| Proven: the known bug, or fixed later on main | 31 |
| Both checkers: real, and a user would notice | 64 |
| Both checkers: real, but minor | 40 |
| Refuted or unclear to at least one checker | 13 |

| Can the checkers say no? A test on the known-real problems | Wrongly dismissed, on the original code | Stopped confirming, once the bug was fixed |
|---|---:|---:|
| gpt-6.2 checker | 0 | 9 |
| Opus 5.5 checker | 0 | 11 |

17 of the other reports were later fixed on main by someone else, which is proof they were
real. That count is a floor: the same search found the fix for only 8 of the
14 problems we already knew were fixed.

- **How we know.** The reports were pooled under anonymous labels with nothing marking the known bugs. One reader
  searched later fix commits; two checkers each traced every report in the exported code.
- **How it was checked.** The checkers were tested on the known-real problems, first on the original code and then on
  the code after the fix. After the fix, both still confirmed 3; two of those
  belong to a fix that was only partial.
- **What it does not show.** That the unfixed reports matter enough to block a merge. The two checkers are the same
  two models that wrote the reports, so they could share a convincing mistake. A failing test would settle it; none
  was written.

## Finding 8. About a third of the bugs could not be seen by reading code

*Tentative. One reader's judgment on 30 cases; the key group is nine.*

| What a reviewer had to have in front of them to see the bug | Cases | Named by at least one reviewer |
|---|---:|---:|
| The changed lines alone | 4 | 2 |
| Other code in the repository | 17 | 8 |
| Knowledge from outside the repository | 9 | 0 |

No reviewer named a bug that depended on how a browser lays out a page, what a database accepts or how a filesystem
behaves under load. Size mattered too: reviewers named 6 of 12
bugs in changes of 7 files or fewer, and 4 of 18 in larger ones.

- **How we know.** A reader given the bug and the causing change chose the least demanding thing a reviewer would
  have needed: the changed lines, other repository code, or outside knowledge.
- **How it was checked.** It was not checked by a second reader. The reader flagged several close calls between the
  first two groups.
- **What it does not show.** A firm share. Nine cases cannot fix a proportion; they show that such bugs exist in
  number and that none was caught by reading.

## Side finding. Most of these bugs broke no written rule

*Tentative. A sample found by commit wording, which later proved to favor quickly fixed bugs.*

The project keeps written rules for contributors and for the bot. In the first study, of 29
bugs whose fix names the causing change, a rule existed for 4 when the change was
written, and 0 of those could have been checked from the changed lines alone.

| Did a written rule cover what went wrong? | Count |
|---|---:|
| No written rule covered it | 24 |
| A rule the bot loads covered it, and review missed it | 3 |
| A rule covered it, in a guide the bot does not load | 1 |
| No rule then; one was added afterwards | 1 |

## What this supports doing

1. **Add a plain "find the defects" pass by a current top model to the bot's review, and compare it on this benchmark
   first.** Rests on finding 6. The 30 cases and scripts can score any reviewer, so the claim can be re-tested before
   anything changes.
2. **Use two different models for that pass.** Rests on finding 6: the two overlapped on only
   4 of 10.
3. **Have a second model check each reported problem before a person sees it.** Rests on finding 7: the checkers
   could say no, and a third of confirmed reports were minor.
4. **Review large changes in parts, and mark any change the bot never reviewed.** Rests on findings 3 and 5.
   4 traced bugs came from changes of 500 files or more that the bot acknowledged and
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
| What fixes repaired | 300 | Lottery over every fix in the period, in a fixed pseudo-random order | One Claude Opus 5.5 reader per fix | Second Claude reader on 47; GPT reader on 60 |
| What the bot had said | 113 | Every traced bug whose causing change the bot reviewed | One Claude Opus 5.5 reader per case | GPT reader on all; both "named" cases read by hand |
| Blind review | 30 | First 15 of each kind in random order, among smaller recent changes the bot reviewed | Claude Opus 5.5 graders, blind to the reviewer | GPT grader on all pairs; run logs audited for leaks |
| Are the reports real | 148 | Every report from the two strongest reviewers | One later-fix reader; two code-tracing checkers | Known-real reports as a control, before and after the fix |
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
