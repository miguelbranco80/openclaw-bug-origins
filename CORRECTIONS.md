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

## Not done

- No project code was run and no test was written.
- The "what each bug needed" tags (finding 9) were not re-read by a second model.
- The GPT reader could not look up history older than September 2026 on GitHub, so it answered "could not tell" for
  16 of 60 fixes.
