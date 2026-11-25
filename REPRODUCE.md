# Reproducing this study

There are three levels. The first is exact and needs nothing but Python. The other two need access that this
repository cannot give you, and their results will not match to the last digit.

## Level 1: rebuild every number from the included data

```bash
./rebuild.sh
```

```bash
git status --short
```

This re-runs every step that turns the readers' and reviewers' stored answers into the report: joining verdicts,
unblinding grades, tabulating the checks, computing the agreement figures, building the five data files and
rendering `README.md`. It needs Python 3 and no packages. If the second command prints nothing, your rebuild matches
what is published.

To check a single number, find its row in `fix-origins/dashboard/*.json`, then read the function in
`fix-origins/dashboard/build_data.py` that produced it. Each one is a few lines over the per-case files:

| Per-case file | One row per |
|---|---|
| `fix-origins/cases.jsonl` | sampled fix, with the first reader's answer |
| `fix-origins/second_reads.jsonl` | fix re-read by a second Claude reader |
| `fix-origins/audit/origin-second-reads.jsonl` | fix re-read by the GPT reader |
| `fix-origins/clawsweeper/results.jsonl` | traced bug, with what the review bot had said |
| `fix-origins/review-pilot/results.jsonl` | pilot case, with every reviewer's grade |
| `fix-origins/review-pilot/verify-results.jsonl` | reported problem, with the three checks |

## Level 2: re-fetch the public data

You need a clone of `openclaw/openclaw` and the GitHub CLI (`gh`) signed in. The scripts expect to be run from the
root of that clone, with this repository checked out as a folder named `research` inside it:

```bash
git clone https://github.com/openclaw/openclaw.git
```

```bash
cd openclaw && git clone https://github.com/miguelbranco80/openclaw-bug-origins.git research
```

| Step | Command (from the openclaw clone) | Writes |
|---|---|---|
| Sampling frame and sample | `python3 research/fix-origins/scripts/sample.py` | `population.tsv` |
| Blame candidates | `python3 research/fix-origins/scripts/blame.py --from 1 --to 300` | `blame.jsonl` |
| Evidence bundles | `python3 research/fix-origins/scripts/evidence.py --from 1 --to 300 --out <dir>` | one bundle per fix |
| Review bot comments | `python3 research/fix-origins/scripts/clawsweeper_fetch.py` | `clawsweeper/raw/` |
| Review at merge time | `python3 research/fix-origins/scripts/clawsweeper_table.py` | `clawsweeper/table.jsonl`, `bundles/` |
| First readers' answers into one file | `python3 research/fix-origins/scripts/assemble.py --reads <dir> --from 1 --to 300` | `cases.jsonl` |
| Pilot PR descriptions | `python3 research/fix-origins/review-pilot/fetch_descriptions.py` | `data/pilot_pr_bodies.json` |
| Pilot exports | `python3 research/fix-origins/review-pilot/export.py <out> <ranks.json> <bodies.json>` | one directory per case |
| Commit base rates | `python3 research/fix-origins/audit/base_rates.py` | `audit/base-rates.json` |

All history is pinned to commit `e6b42e31bc1522b8596958fbdd85c394b23fca7b`. `fix-origins/README.md` describes the
sampling and the per-fix procedure in detail.

What will differ: the original ran in a shallow, partial clone whose history starts on 2026-09-03, and it read
older changes through the GitHub API. With a full clone, `git blame` reaches further back, so blame candidates for
old code will differ. Three otherwise eligible pilot cases were skipped because their objects were missing locally
(`select_cases.py --skip 53,113,176`).

## Level 3: re-run the model judgments

The prompts and runners are here, and so is every answer the models gave. Re-running needs your own model access.

| Judgment | Prompt | Runner | Stored answers |
|---|---|---|---|
| What each fix repaired | `fix-origins/reader-prompt.md` | Run by hand as Claude Opus 5.5 subagents (`dispatch-template.md`) | `fix-origins/reads/` |
| What the bot's review said | `fix-origins/clawsweeper/reader-prompt.md` | Run by hand as Claude Opus 5.5 subagents | `fix-origins/clawsweeper/reads/` |
| Blind review, GPT models | `review-pilot/prompt-whole.md`, `prompt-per-file.md` | `review-pilot/run_codex.py` (Codex CLI) | `review-pilot/data/runs/` |
| Blind review, Opus 5.5 | `review-pilot/prompt-whole.md` | Run by hand as subagents | `review-pilot/data/runs/claude-opus-5-5__whole/` |
| Grading | `review-pilot/grader-prompt.md` | Run by hand as Claude Opus 5.5 subagents | `review-pilot/data/grade/reads/` |
| What each bug needed | `review-pilot/tag-prompt.md` | Run by hand as subagents | `review-pilot/data/grade/tags/` |
| Checking reported problems | `review-pilot/refute-prompt.md`, `laterfix-prompt.md` | `review-pilot/run_refute_codex.py`, and subagents | `review-pilot/data/verify/` |
| Second-model re-reads | `audit/raw/prompt-*.md` | `audit/second_read_codex.py` (Codex CLI) | `audit/raw/` |

To score a new reviewer on the 30 pilot cases: build the exports (level 2), run it in each export directory with
`prompt-whole.md`, save its final JSON as `data/runs/<name>__whole/<rank>/last.txt`, then run `./rebuild.sh` and
grade the new letter in each bundle under `data/grade/bundles/`.

## What cannot be reproduced exactly

- **Model answers.** Models are not deterministic, and model versions change. Expect agreement of the kind the
  report measures between readers, not identical answers.
- **The Claude readers were run by hand** inside an interactive session, one subagent per batch, not from a script.
  The prompts are exact; the dispatch is described, not automated.
- **Reviewer isolation was not uniform.** The Codex sandbox allowed reads outside the export directory, and some
  runs read a personal review guide from the test machine. The run logs that showed this are not included, because
  they contain machine details.
- **Local paths were removed.** Absolute paths in the data and bundles were replaced with `<openclaw>`, `<scratch>`
  and `<home>`.
- **The first study** (`detection-check/`) has a written report and case list but no scripts; its search commands
  are listed in its report.

## Extending it

The sample is ordered by a fixed hash, so the next batch is the next ranks: fixes 301 onward in
`fix-origins/population.tsv`. Questions of the form "do changes of kind X cause more bugs" need two things: the
attribute for the traced causing changes, and the same attribute for ordinary changes. `audit/size_and_route.py`
shows the pattern for size and for commits made without a pull request. Questions about review, such as whether
changes merged against the bot's verdict cause more bugs, need the bot's verdicts on a comparison sample of changes
that caused no bug; that sample has not been collected.
