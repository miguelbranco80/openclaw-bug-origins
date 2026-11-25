# Corrections

The top-level `README.md` is the current statement of what the studies support. The earlier per-study reports
(`fix-origins/report.md`, `fix-origins/clawsweeper/report.md`, `fix-origins/review-pilot/report.md`,
`detection-check/report.md`) are kept as working records. Where they differ from the README, the README is right.
This file lists what changed and why.

## What the second-model check changed

The first pass used Claude readers throughout. A GPT reader (gpt-6.2-sol) then re-read 60 of the 300 fix
classifications, all 113 review-bot verdicts and all 180 gradings of the blind review.

| Claim in the earlier reports | What the check found | What the page now says |
|---|---|---|
| A third of changes titled "fix" fix no bug | The GPT reader called 5 of 60 "not a bug" where the first reader had 22 | Between about a tenth and a third, depending on how a bug is defined |
| New code that never worked outnumbers broken-later bugs two to one | 105 against 51 by the first readers; 30 against 24 at high confidence; 16 against 17 by the GPT reader on 60 | At least as many; from about even to about double |
| The causing change is identified correctly | Both readers named the same change in 18 of 20 | Stated as well supported |
| The review bot named the bug in 2 of 113 | Both readers agree on both cases; related concerns 11 against 17 | Unchanged for "named"; a range for "related" |
| gpt-6.2 and Opus 5.5 each named 7 of 30 | A second grader agrees on 178 of 180 named-or-not calls; 8 and 7 by its count | Unchanged |
| A stronger model names several times more than the bot | One model against the bot: p = 0.125. Both together against the bot: p = 0.021 | Supported for the two together; not established for either alone |
| Reviewing three files at a time helped a little | 2 against 0, p = 0.5 | No reliable gain |

## Other corrections

- Sizes and titles of bug-causing changes are compared with every commit on main since 10 September 2026 (UTC),
  listed in `dataset/commits.tsv` (39,210 commits). Earlier text used slightly different subsets and cutoffs.
- The population of 3,996 fixes uses a UTC cutoff. An earlier count of 3,884 used the local time zone.

- The bug rates in the comparisons of findings 12 to 14 are now computed against all ordinary changes. An earlier
  version divided by only the changes where the property was known, which understated the rates in the
  review-timing table by about a sixth. The ratios were not affected.
- "Review by a person" now means review by a person other than the author. The first count, 4.5% of sampled pull
  requests, included authors' own review comments on their own pull requests; 11 of the 18 were that. The corrected
  figure is 2% of the sample and 1.0% of all 35,826 merged pull requests since 10 September.
- Finding 15 said 20 people merge. That was the number seen in the 496 fetched pull requests. Across all pull
  requests it is 40 accounts. The most active account opens 52.1% of all pull requests (55.5% in the sample).
- The briefs given to models were reworded on 25 November 2026 so that a program can run them with nothing filled
  in by hand: one case per run, the answer given as the final message, and the clone's details inserted by the
  runner. The rubrics, the categories and their definitions are unchanged. Every stored answer was made with the
  earlier wording. `PROTOCOL.md`, "What differs from how the published answers were made", lists the differences.

## The extension of 25 November 2026

The study was first published with 300 November fixes read by Claude Opus 5.5 (tag `published-2026-11`). It was then
extended to 1,202 fixes from 10 September to 22 November, all read by gpt-6.2-sol, with the Opus answers for the
November fixes kept as the check. Finding 23 in the README compares the two readers and the two periods. What
changed between the versions is recorded here, not in the README:

| Claim in the first version | What the extension found | What the report now says |
|---|---|---|
| A third of fixes repair no bug by the first readers; a tenth by a second model | With the readers' roles swapped the same gap appears: 8% by the main reader on 1,202, 33% by the other on the 300 | It depends on the reader; each reader is consistent with itself |
| Never-worked bugs outnumber broken-later ones by about two to one | 443 against 389 by the main reader, in both periods | About as many; the other reader says double |
| A broken thing stayed broken about three weeks | 11.8 days overall; 28.8 for November fixes and 8.6 for the earlier weeks, where causes could not be traced as far back | One to four weeks; the periods cannot be compared on this |
| Straight-to-main commits show no sign of more bugs (5 cases) | 19 cases: 0.42 times the rate per commit (0.26 to 0.66) | Fewer per change; much of it is size |
| No sign that anyone is overloaded | Individual workload: still nothing. Busiest third of days: 1.73 times the quietest (1.11 to 2.71) | Individual workload shows no effect; busy days are a tentative exception |
| Occasional contributors did no worse; the middle group about double | Occasional contributors: 0.47 times (0.25 to 0.9). The middle group: no clear difference | Occasional contributors' changes carry about half the bugs |
| A second person merging or reviewing: no clear difference | Merged by someone else: 0.42 times (0.26 to 0.68) | About half the bugs; mostly outside contributors' changes |
| Files other people were editing: about two and a half times the bugs | 1.67 times, and only where two or more others were editing | Supported, weaker |
| Code changes without tests: no clear difference | 0.32 times (0.18 to 0.57) | Fewer; they are a different, smaller kind of change |

The same comparisons in numbers, as each version reported them. Where both give a range and the ranges overlap,
the finding held. The first version's ratios did not hold landing time equal.

| | First version: 300 November fixes | Now: 1,202 fixes, 10 Sep to 22 Nov |
|---|---:|---:|
| Fixes that repaired no bug, % (the readers differ: finding 1) | 33 (28 to 39) | 8 (7 to 10) |
| Bugs traced to the change that introduced them | 156 | 832 |
| Causing changes titled feat, % | 26 | 24 |
| Median files changed by a causing change | 28.5 | 36 |
| Bugs per commit, over 100 files against 1 to 5 files | 104 | 131 |
| Causing changes the bot reviewed | 113 | 645 |
| Of those, the bot named the bug | 2 | 21 |
| Straight to main against through a pull request | 0.52 (0.21 to 1.26) | 0.42 (0.26 to 0.66) |
| Merged over the bot's objection against called ready | 2.58 (1.5 to 4.44) | 3.42 (2.34 to 4.99) |
| Open under an hour against open a day or more | 0.19 (0.09 to 0.39) | 0.28 (0.16 to 0.47) |
| Interface change with a screenshot or video against without | 5.3 (2.17 to 12.94) | 3.72 (2.0 to 6.93) |
| Share of bugs from changes with two or more warning signs, % | 47 | 48 |
| Busiest third of days against quietest third | 0.83 (0.52 to 1.34) | 1.73 (1.11 to 2.71) |
| Merged by someone else against by the author | 0.56 (0.24 to 1.32) | 0.42 (0.26 to 0.68) |
| Occasional contributors against the most active author | 0.78 (0.23 to 2.6) | 0.47 (0.25 to 0.9) |
| Files two or more others were editing against files only the author was | 2.69 (1.44 to 5.03) | 1.67 (1.22 to 2.28) |
| Adds a new code file against only edits | 3.27 (1.98 to 5.39) | 3.18 (2.51 to 4.02) |
| Share of bugs from changes that add a code file, % | 66 | 69 |
| Code change with no test file against with tests | 0.29 (0.07 to 1.13) | 0.32 (0.18 to 0.57) |

Read across: four held and tightened (the bot's objection, new code files, time open, screenshots). Two were unclear
and are now clear in the same direction (straight-to-main commits, code changes with no test file). Three that showed
nothing now show something (busy days, changes merged by someone else, occasional contributors). One weakened (shared
files). None reversed. The two versions are not independent tests: the comparison sample of ordinary changes, the
commit list and the pull request data are the same in both; what grew is the number of traced bugs, from 156 to 832.
The first version's numbers are also kept in `dataset/published_2026_11.json`.

Method changes made with the extension:

- Every comparison of bug rates now also holds equal when the change landed (the month for pull request
  comparisons, the half-month for commit comparisons). An older change has had longer for its bugs to be found and
  fixed: commits from September show about three times the rate of commits from November. Over three weeks of fixes
  this mattered little; over ten it would have produced false differences, such as a much larger busy-day effect.
- Bug rates per 100 commits are four to five times higher than in the first version, because fixes are now counted
  over ten and a half weeks instead of three. The rates are for comparing kinds of change with each other.
- The main reader ran without GitHub lookups, against a clone with history back to 1 July 2026.
- The blind review (findings 7 to 9) and the first study (finding 10) were not repeated; they describe November.

## Not done

- No project code was run and no test was written.
- The "what each bug needed" tags (finding 9) were not re-read by a second model.
- The GPT reader could not look up history older than September 2026 on GitHub, so it answered "could not tell" for
  16 of 60 fixes.
