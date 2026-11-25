# The dataset

These files are the facts. Every script in `questions/` reads only this folder. Nothing here is computed from
anything else in `dataset/`; each file is either copied from a collection step or fetched from the public repository.

All files describe `openclaw/openclaw` as of commit `e6b42e31bc1522b8596958fbdd85c394b23fca7b` (22 November 2026).

| File | One row per | Made by |
|---|---|---|
| `commits.tsv` | commit on `main` since 2026-09-10 (UTC), 39,210 rows | `fix-origins/scripts/commit_list.py`, from git |
| `sampled_fixes.jsonl` | sampled fix (300), with the first reader's answer | `fix-origins/scripts/assemble.py`, from the readers' answers in `fix-origins/reads/` |
| `fix_rereads_claude.jsonl` | fix re-read by a second Claude reader (47) | `dataset/build.py`, from `fix-origins/second_reads.jsonl` |
| `fix_rereads_gpt.jsonl` | fix re-read by a GPT reader (60) | `fix-origins/audit/collect.py` |
| `bot_reviews.jsonl` | sampled bug traced to a causing change (156), with the review bot's review at merge | `fix-origins/clawsweeper/assemble_results.py` |
| `bot_review_rereads_gpt.jsonl` | reviewed case re-read by a GPT reader (113) | `fix-origins/audit/collect.py` |
| `blind_review.jsonl` | blind-review case (30), with every reviewer's grade | `fix-origins/review-pilot/assemble_results.py` |
| `blind_review_regrades_gpt.jsonl` | reviewer and case pair regraded by a GPT grader (180) | `fix-origins/audit/collect.py` |
| `reported_problems.jsonl` | problem reported by gpt-6.2 or Opus 5.5 (148), with three checks | `fix-origins/review-pilot/verify_tabulate.py` |
| `checker_control.jsonl` | reported problem in the ten control cases (52), judged on the fixed code | `fix-origins/review-pilot/verify_control.py` |
| `named_cause_study.json` | figure of the first, wording-based study | Entered by hand from `detection-check/report.md` |

Run `python3 dataset/build.py` to refresh the copies after changing a collection step.

## Columns that questions rely on

**`commits.tsv`**: `sha`; `committed_at`; `files_changed` (files in the commit's diff against its first parent);
`pr_number` (the number in a trailing `(#123)` in the title, empty when there is none); `title_prefix` (the leading
word of the title, lower case: `fix`, `feat`, `refactor`, ...).

**`sampled_fixes.jsonl`**: `rank` (position in the fixed pseudo-random order; ranks 1 to 300 are the sample); `sha`,
`fix_pr`, `fix_subject`, `fix_date`, `fix_author`; `origin` (`never-worked`, `regression`, `latent`, `not-a-defect`,
`unclear`; the report calls `regression` "broken later"); `cause_sha`, `cause_pr` (the change that introduced the
bug, for the first two origins); `confidence` in that cause (`high`, `medium`, `low`); `cause` (facts about the
causing commit: `date`, `days_to_fix`, `prefix`, `subject`, `author`, `files_changed`); `fix_names_cause` (the fix's
message or PR text mentions the causing change); `fix_adds_test`; `user_visible`, `user_saw`, `impact`, `area`,
`summary`, `reasoning` (the reader's words); `blame_agrees`, `blame_in_top5`, `blame` (what `git blame` suggested).

**`fix_rereads_*.jsonl`**: `rank`; `first_origin`, `second_origin`; `first_cause`, `second_cause`.

**`bot_reviews.jsonl`**: `rank`, `origin`, `cause_pr`, `cause_sha`, `fix_pr`; `status` (`reviewed-merged-head`,
`reviewed-earlier-revision`, `no-review-before-merge`, `no-pr`); `verdict` (the bot's overall call at merge:
`ready`, `blocked`, `needs-changes`, `needs-maintainer`); `review_time`, `merged_at`, `merged_by`, `pr_author`,
`changed_files`; `flagged` (did the review name the bug: `exact`, `related`, `none`); `where`, `quote`, `outcome`,
`note` (the reader's support for that).

**`blind_review.jsonl`**: `rank`, `origin`, `cause_pr`, `fix_pr`, `files_changed`, `days_to_fix`; `needs` (`diff`,
`repo`, `outside`: what a reviewer needed to see the bug); `clawsweeper_actual` (the bot's `flagged` value for this
case); `arms` (per reviewer: `flagged`, `findings` count, `matching_finding`, `grader_note`).

**`reported_problems.jsonl`**: `rank`, `id`, `arm` (which reviewer), `title`, `file`; `known_bug` (`exact` when this
report is the known bug); `later` (was it later fixed on main: `yes`, `partly`, `no`), `later_commit`; `opus`, `gpt`
(each checker's verdict: `confirmed`, `refuted`, `unclear`), `opus_impact`, `gpt_impact` (`user-visible`, `minor`).

**`checker_control.jsonl`**: `rank`, `id`, `known_bug`; `gpt_at_cause`, `opus_at_cause` (verdict on the original
code); `gpt_at_fix`, `opus_at_fix` (verdict on the code after the known bug was fixed).

## What is judgment and what is not

Facts read from git or GitHub: everything in `commits.tsv`; dates, titles, file counts, authors, mergers; the review
bot's verdict and timing.

Model judgments: `origin`, `cause_sha`, `confidence`, `user_visible`, `impact`; `flagged`; `needs`; every grade;
`later`; every checker verdict. The report says, for each finding, how often two models agreed on the judgment it
rests on.
