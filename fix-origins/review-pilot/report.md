> **Superseded where it differs.** This is the working report of one study. The top-level `README.md` is the current statement of the findings, and `CORRECTIONS.md` lists what changed after a second-model check.

# Pilot: can a reviewer that sees only the causing change name the bug?

Follow-up to [../clawsweeper/report.md](../clawsweeper/report.md). I took 30 changes that each introduced a bug
later fixed on main, gave six reviewer setups the change as it stood at merge, with no later history, and had
graders check whether any finding named the bug. Written 2026-11-25. Data: [results.jsonl](results.jsonl).

## Result

| Reviewer (same plain prompt, medium effort) | Named the bug (of 30) | Related concern | Findings reported |
|---|---|---|---|
| gpt-5.6-sol | 3 | 2 | 32 |
| gpt-6-astra | 1 | 0 | 13 |
| gpt-6.1-sol (the model ClawSweeper's README names) | 0 | 0 | 15 |
| gpt-6.2-sol | 7 | 7 | 98 |
| Claude Opus 5.5 | 7 | 3 | 50 |
| gpt-6.1-sol, reviewing 3 files at a time | 2 | 0 | 33 |
| ClawSweeper's actual review of these 30 | 2 | 1 | not counted |

- **The two newest models each named 7 of 30. Together they named 10**, with 4 in common.
- **It is not a steady climb.** The GPT line goes 3, 1, 0, 7. With 30 cases, 0 against 3 is within noise; 0 against 7
  is not.
- **Hits follow how much a model reports.** gpt-6 and gpt-6.1 returned no findings at all for 19 of 30 changes.
  gpt-6.2 never returned none and averaged 3.3 findings per change.
- **Narrower review helped a little.** Giving gpt-6.1 three files at a time took it from 0 to 2 hits and doubled its
  findings. On this sample the choice of model mattered more than the technique.
- **The caught bugs were not trivial ones.** Seven of the ten had been live for more than 10 days before their fix;
  two for more than 60.

## What each bug needed

A separate reader tagged each bug by what a reviewer had to have in front of them to see it.

| What was needed to see the bug | Cases | Named by at least one reviewer |
|---|---|---|
| The diff alone | 4 | 2 |
| Other code in the repository (a caller, a consumer, an existing rule) | 17 | 8 |
| Knowledge outside the repository (a browser, PostgreSQL, Btrfs, GitHub, measured speed) | 9 | 0 |

No blind reviewer named any of the nine bugs that needed outside knowledge. Those are the cases for running the
code, a browser check or a recorded expectation, not for a better reader. Size also mattered: reviewers named 6 of
the 12 bugs in changes of 7 files or fewer, and 4 of the 18 in larger ones.

## What this does not show

- **Whether the other findings are real.** gpt-6.2 reported 98 findings and 7 were the known bug. The other 91 may
  be real bugs nobody has traced, or false alarms. Nothing here measures that, and it decides whether such a
  reviewer is usable.
- **Run-to-run variation.** Each setup reviewed each change once.
- **A fair match against ClawSweeper.** ClawSweeper reviewed at the time, sometimes an earlier revision, with its
  own long prompt. The plain prompt on its model found less than ClawSweeper did, so its prompt is not the weak
  point on that model.

## How it was run

1. **Cases.** From the 156 traced bugs, those with a ClawSweeper review, a cause after 2026-09-10, a causing change
   of at most 30 files, medium or high confidence and a user-visible failure: 38. The first 15 regressions and
   first 15 never-worked bugs in the sample's fixed random order, skipping 3 whose objects are not stored locally.
2. **Exports.** `export.py` wrote each repository as it stood at the causing commit into a plain directory with no
   git history, plus the change's diff and the PR description as it read at merge time. Two descriptions had been
   edited after merge to mention the later fix; the merge-time version removes that.
3. **Reviews.** `run_codex.py` (since replaced by `pipeline/judge.py`) ran each GPT model through `codex exec` in the export directory: read-only sandbox,
   user config ignored, project instructions off, medium effort, prompt in [prompt-whole.md](prompt-whole.md). The
   per-file setup split the changed code files into groups of three ([prompt-per-file.md](prompt-per-file.md)),
   86 runs. Opus 5.5 ran as one subagent per case with the same prompt.
4. **Grading.** `grade_bundles.py` put every setup's findings for a case under shuffled letters. Five graders
   (Opus 5.5) scored each letter as exact, related or none with [grader-prompt.md](grader-prompt.md), the same
   rubric as the ClawSweeper lookup. Five more tagged what each bug needed ([tag-prompt.md](tag-prompt.md)).

## Checks

- All 236 review runs produced parseable findings. All 180 grades are present, and every hit points at an existing
  finding.
- I read 6 of the 20 hits against the bug description. All 6 describe the same failure.
- No GPT run and no Opus run read the live checkout, the research folder, another case or the grading files, and
  none ran git, `gh` or a network command.

## Limits

- **Reviewers were not equally isolated.** Codex's sandbox allowed reads anywhere on disk. 23 of 30 gpt-5.6 runs
  read a personal review skill from the home directory, and 24 of 86 per-file runs read a personal engineering
  skill. The Opus subagents had this repository's current `AGENTS.md` in their context. None of these contain the
  answers, but the setups did not get identical guidance.
- **The graders are Opus.** They did not know which setup wrote which findings, but writing style may be
  recognisable.
- **Selection.** Small and medium changes only, and only bugs that were later found and traced by a model reader.
- **One grader per case**, with the rule to pick the lower level when unsure.
- The exports (4.7 GB, hard-linked) and raw run logs are in the session scratch directory, not in this folder.

---

# Follow-up: are the other findings real?

gpt-6.2 and Opus 5.5 reported 148 findings on the 30 changes; 14 of them are the known bug. This follow-up checks
the rest. Data: [verify-results.jsonl](verify-results.jsonl), [verify-control.jsonl](verify-control.jsonl).

## Three checks

| Check | Result on the 148 findings |
|---|---|
| Was it later fixed on main? | 25 yes, 12 partly, 111 no |
| gpt-6.2 traces the code: does the failure happen? | 140 confirmed, 5 refuted, 3 unclear |
| Opus 5.5 traces the code: does the failure happen? | 136 confirmed, 5 refuted, 7 unclear |

- **Proven by history: 31 of 148.** The 14 known-bug findings, plus 17 others that a later commit on main fixed.
  Those 17 map to 11 distinct fix commits in 8 of the 30 changes. Five of them are the known fix seen from another
  angle; the rest are separate bugs in the same change that someone had to fix later.
- **Both checkers confirmed 134 of 148.** They rated 84 of those as something a user or operator would notice, and
  50 as minor (cosmetic, log-only, or needing an unusual setup).
- **By reviewer:** gpt-6.2 has 53 findings that both checkers call real and user-visible out of 98, about 1.8 per
  change. Opus has 31 of 50, about 1.0 per change.
- **About 23 findings repeat another finding** on the same change, mostly the two models reporting the same defect.

## Can the checkers be trusted?

Two controls, both using the 14 findings already known to be real.

| Control | gpt-6.2 checker | Opus checker |
|---|---|---|
| On the original code: wrongly dismissed | 0 of 14 | 0 of 14 |
| On the code after the bug was fixed: stopped confirming | 9 of 14 | 11 of 14 |

The checkers do not confirm everything: when the bug was gone, most verdicts flipped. Both still confirmed three
findings on the fixed code. Two belong to a fix the later-fix reader had already called partial (#190446), and one
was fixed by a different commit than the one the tree was taken at. So the measured rate of wrongly confirming is at
most 3 in 14 for the pair, and 5 in 14 for the weaker checker alone.

The later-fix check undercounts. It found a fix for only 8 of the 14 known-real findings (4 more as "partly"),
because it only looks at fix commits touching the file the finding names and applies a strict match.

## What this supports

- These reviewers' extra findings are mostly not false alarms. At least a fifth are proven by a later fix, and
  about nine in ten survive two independent code traces that demonstrably can say no.
- A real defect is not the same as one worth blocking a merge for. More than a third of the confirmed findings
  were rated minor, and 111 of 148 were never fixed on main in the weeks that followed.
- Nothing was executed. A code trace by a model is weaker evidence than a failing test.

## Limits

- The two checkers are the same two models that wrote the findings. They would share a convincing misreading.
- The controls cover 14 findings in 10 changes.
- "Later fixed" was judged by one reader per case. One reader ran two git commands outside the allowed forms
  (read-only), and two diffs could not be read because objects are not stored locally.
- Impact ratings are the checkers' opinion, not measured.
