# Results page: source and corrections

This folder holds the data files behind the report, the script that builds them, the renderer for the top-level
`README.md`, and the source of an interactive version of the same report (`index.html`, which needs a host page to
draw its charts). The top-level `README.md` is the current statement of what the studies support. Where it differs from the earlier per-study reports
(`../report.md`, `../clawsweeper/report.md`, `../review-pilot/report.md`, `../../detection-check/report.md`),
the top-level report is right and those reports are superseded.

## Files

| File | What it is |
|---|---|
| `index.html` | The page: words in the HTML, every number drawn from a data file. |
| `build_data.py` | Builds the five data files from the studies' per-case outputs. Run from the repo root. |
| `*.json` | The five data files: one row per number on the page. |
| `../audit/second_read_codex.py` | Re-reads the three central judgments with a GPT model through the Codex CLI. |
| `../audit/collect.py` | Collects those re-reads into `../audit/*-second-reads.jsonl` and prints agreement. |
| `../audit/base_rates.py` | Measures ordinary commits on main, for comparison with bug-causing changes. |

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

- The median size of a causing change is 28.5 files for causes since 10 September 2026 (106 cases), measured against
  38,812 ordinary commits with a median of 4. Earlier text said 30, from a slightly different subset.
- Shares of bug-causing changes over 100 files (25%) and titled `feat` (25%) are compared with shares among all
  commits (1.5% and 3.3%) recomputed from git by `../audit/base_rates.py`.
- The population of 3,996 fixes uses a UTC cutoff. An earlier count of 3,884 used the local time zone.

## Not done

- No project code was run and no test was written.
- The "what each bug needed" tags (finding 8) were not re-read by a second model.
- The GPT reader could not look up history older than September 2026 on GitHub, so it answered "could not tell" for
  16 of 60 fixes.
