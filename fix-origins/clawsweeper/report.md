> **Superseded where it differs.** This is the working report of one study. The top-level `README.md` is the current statement of the findings, and `fix-origins/dashboard/README.md` lists what changed after a second-model check.

# What ClawSweeper had said when the bug-causing changes merged

Follow-up to [../report.md](../report.md). That study traced 156 of 300 sampled fixes to the change that caused the
bug: 51 regressions and 105 bugs that never worked. This one asks what ClawSweeper, the project's review bot, had
written on each causing PR at the moment it merged. Written 2026-11-25. Data: [results.jsonl](results.jsonl).

## Was there a review?

| When the causing change merged | Cases (of 156) |
|---|---|
| ClawSweeper had reviewed the revision that merged | 80 |
| ClawSweeper had reviewed only an earlier revision | 33 |
| The PR had no ClawSweeper review yet | 27 |
| No PR: the change was committed straight to main | 16 |

Of the 27 with no review, 16 are from before August 2026, when the bot did not yet review regularly. The other 11
include four cases from three very large PRs (550, 1,452 and 1,897 files) that the bot acknowledged and never
reviewed. The 113 reviewed cases cover 107 distinct PRs.

## Did the review flag the bug?

One model reader per case compared the bug with the review text, using a strict rubric
([reader-prompt.md](reader-prompt.md)).

| What the review said about this bug | Cases (of 113 reviewed) | Plausible range |
|---|---|---|
| Nothing | 100 | 81 to 93 in 100 |
| Related: a concern about the same mechanism, but not this failure | 11 | |
| Exact: it named this failure | 2 | 0.5 to 6 in 100 |

The two exact flags:

- [#200758](https://github.com/openclaw/openclaw/pull/200758): on the merged revision the bot wrote that the new CSS
  selector "also owns `::after` and supplies `opacity: 0`, so the dictation border disappears". The PR merged two
  minutes later with no reply. [#200770](https://github.com/openclaw/openclaw/pull/200770) fixed it the same day.
- [#186041](https://github.com/openclaw/openclaw/pull/186041): an earlier review said a new grid lets long tool
  summaries overflow. The author pushed a change, the next review treated the item as addressed, and the overflow
  still shipped in Safari and Firefox. It was fixed 20 days later
  ([#200337](https://github.com/openclaw/openclaw/pull/200337)).

Of the 11 related flags, 6 were still open on the review in force at merge with no human answer, 4 had been answered
by the author before merge, and 1 had been dropped by a later review version.

Regressions and never-worked bugs look the same: 35 of 41 reviewed regressions and 65 of 72 reviewed never-worked
bugs got no flag.

## What the bot's overall verdict was

| ClawSweeper's verdict at merge | Cases | Of those, bug flagged (exact or related) |
|---|---|---|
| Blocked | 51 | 5 |
| Needs changes | 18 | 5 |
| Needs maintainer review | 8 | 1 |
| Ready | 36 | 2 |

- **69 of 113 merged while the bot said "blocked" or "needs changes".** In 59 of those the open items were about
  something other than the bug: missing proof, config compatibility, a different defect. Merging against the verdict
  is routine here, and it is not what let these bugs in.
- **The bot said "ready" on 36 changes that carried a bug.**
- **Merges follow reviews closely.** The median gap between the review in force and the merge is 28 minutes; 27 of
  113 merged within 10 minutes of it.

## What this shows and does not show

- For bugs that reached main, the bot had almost never named the problem. Ignored warnings are rare: 1 exact flag
  and 6 related ones were open and unanswered at merge, out of 113.
- This says nothing about how many bugs the bot stopped. Bugs it caught and authors fixed before merge never appear
  in a sample of fixes.
- It does not show whether a better reviewer could have caught these from the diff. That needs a separate test:
  give a reviewer the causing diff without the answer and see whether it names the bug.

## How this was built

1. `scripts/clawsweeper_fetch.py` fetched each of the 133 distinct causing PRs once through GitHub GraphQL: comments
   with their full edit history, reviews, commits. Cached in `raw/`.
2. `scripts/clawsweeper_table.py` picked, per case, the last version of the ClawSweeper review comment written at or
   before the merge time, read its "Reviewed head" and state marker, and compared the head with the PR's final head.
   For reviews older than the state marker the verdict comes from the headline. Output: `table.jsonl` and one
   reader bundle per reviewed case in `bundles/`.
3. Ten model readers (Claude Opus 5.5) each judged about 11 bundles and wrote `reads/<rank>.json`. They saw the
   review in force at merge, the open items of up to three distinct earlier versions, and human comments in between.
4. `results.jsonl` joins the table and the reads.

## Checks

- All 113 reads are present and well-formed. Every quote on the 13 flagged cases appears verbatim in its bundle.
- I read both exact cases in the review text. Both hold.
- I compared 7 randomly chosen "nothing" verdicts with the review's item titles. All 7 hold.
- Three cases also appear in the earlier wording-based study (`../../detection-check/`). Both studies say the bot
  reviewed them without flagging the bug.

## Limits

- One reader per case, no second reader. The rubric says to pick the lower level when unsure, so "related" and
  "exact" are conservative. Readers reported about 20 close calls that they scored "nothing".
- The bug descriptions come from the fix-origins readers, who were themselves model readers working from diffs.
- Readers saw at most three earlier review versions. Some PRs have dozens, so "flagged earlier, then dropped" may be
  under-counted.
- Only ClawSweeper's review comment was judged. Other bots (the Codex connector left 105 reviews on these PRs) and
  human inline review comments were not.
- GitHub returns at most 100 comments and 100 edits per comment in one query. One PR (#122425) has more than 100
  comments; its review comment was among the first 100.
- Nothing was executed, and no code diff was read for this step.
