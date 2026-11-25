> **Superseded where it differs.** This is the working report of one study. The top-level `README.md` is the current statement of the findings, and `fix-origins/dashboard/README.md` lists what changed after a second-model check.

# Where OpenClaw's bug fixes come from: a random sample of 300

Between 2026-11-01 and 2026-11-22, `openclaw/openclaw` main received 3,996 commits titled "fix" that changed product
code. I drew 300 at random and traced each back with `git blame`, the PR text and earlier diffs, one model reader
per fix. Figures come from [cases.jsonl](cases.jsonl) via [stats.md](stats.md); method in [README.md](README.md).

## The split

| What the fix repaired | Fixes (of 300) | Plausible range for all 3,996 |
|---|---|---|
| **Never worked**: the bug shipped with the change that added the code | 105 | 30 to 41 in 100 |
| **Not a defect**: a design change, speed-up, copy or style change, hardening or CI repair titled "fix" | 100 | 28 to 39 in 100 |
| **Regression**: a specific later change broke something that worked | 51 | 13 to 22 in 100 |
| **Latent**: old code that became wrong when something outside changed (a provider, a tool, a new caller) | 29 | 7 to 14 in 100 |
| **Unclear** | 15 | 3 to 8 in 100 |

Of the 185 fixes that repaired a real defect, more than half (50 to 64 in 100) fixed code that was wrong from the
day it shipped. About a quarter (22 to 34 in 100) undid a regression. Only about one product fix in six repairs
something that used to work. A stricter count, using only regressions whose cause the reader rated high-confidence,
gives 24 of 300, about 8 in 100.

## How long regressions lived

The median regression sat on main for **20 days** before its fix. Of the 51, 12 were fixed within a day, 5 within a
week, 17 within a month, and 17 lasted longer. The bugs that never worked lived longer still: median 46 days from the change
that introduced them.

This overturns the earlier wording-based study's figure of 1.7 days. That study could only see fixes that name
their cause, and those are a fast subset. Here, the 18 regressions whose fix mentions the causing change were fixed
in a median of **half a day**. The 33 whose fix does not mention it lived a median of **24 days**.

## What kinds of change cause them

These comparisons use the 115 causing commits newer than 2026-09-03, measured against all 43,187 commits on main
from that date to the tip.

- **Size.** Causing commits changed a median of 30 files; a typical commit changes 4. A quarter of causes changed
  more than 100 files, against 1.4% of all commits. Part of this is mechanical: a change that touches more code has
  more chances to break something. The data does not show whether large changes are riskier per line.
- **Type.** "feat" commits are 26% of causes but 3% of all commits. Refactor and perf commits are
  under-represented, at 7% and 3% of causes against 15% and 10% of commits.
- **Fixes of fixes.** 54% of causes are titled "fix" (61% for regressions). But 51% of all commits are titled
  "fix", so fixes are not more dangerous than other commits. They simply are most commits.
- **One change, several fixes.** Six causing commits appear more than once in this sample of 300.
  [#188978](https://github.com/openclaw/openclaw/pull/188978) (138 files, update and plugin rollback) is the cause of
  three sampled fixes, and also of one regression in the earlier study. With a sample of about 1 fix in 13, a commit
  seen three times probably needed a few dozen follow-up fixes.
- **Author.** The git author with most commits is the author of 42% of causes and 55% of all commits. The RoboClaw
  account, which lands contributors' PRs, is 15% of causes and 8% of commits. Git records who landed a change, not
  who or what wrote it, so these figures say little about people.
- **Area.** The Control UI is the largest area in every group: 27% of all fixes and 26% of fixes with a named cause.
  Update code stands out for defects that never worked: 11 of its 17 fixes.

## How far the existing signals can be trusted

- **Fixes rarely say what caused them.** Only 19% of fixes with a named cause mention it in their message or PR
  description: 35% for regressions, 10% for never-worked. Scaled up, about 680 regressions were fixed in the window
  (between 520 and 880). The earlier study found 41 pairs, so wording-based search saw about 5 to 8 in 100.
- **Blame alone was right 29% of the time.** The top blame candidate was the cause for 46 of 156. Allowing the top
  five, the cause was there for 47%. Blame mostly lands on a later refactor, a move, or an earlier fix of the same
  lines. When the cause is recent enough for local history to see (after 2026-09-03), blame's top pick was right 40%
  of the time.
- **Fixes come with tests.** 93% of sampled fixes add or change a test.

## Do the readers agree?

A second reader classified 47 fixes (16%) without seeing the first answer. They chose the same origin for **39 of
47** (70 to 91 in 100). Where both named a cause, they named the same commit **27 of 27** times. Both read the same
evidence bundle and blame list, so that figure is not fully independent. Every disagreement sat on a boundary:
regression against never-worked (2), latent against not-a-defect (3), unclear against latent (2), never-worked
against not-a-defect (1). I re-checked the four high-confidence regressions in the first 50 against the causing
diff (ranks 19, 22, 37, 40). All four hold.

## Six cases

- **Regression, fixed fast and named.** [#203487](https://github.com/openclaw/openclaw/pull/203487) stopped Stop
  from cancelling a running MCP tool call on CLI-backed turns. The fix,
  [#203551](https://github.com/openclaw/openclaw/pull/203551), names it and landed 0.1 days later.
- **Regression, slow and unnamed.** [#97235](https://github.com/openclaw/openclaw/pull/97235) put a 16 MiB cap on the
  whole proxied model stream. Healthy long responses failed with "Proxy SSE stream exceeded" for 137 days.
  [#197842](https://github.com/openclaw/openclaw/pull/197842) fixed it without naming the cause.
- **Never worked.** [#128447](https://github.com/openclaw/openclaw/pull/128447) built Docker `--mount` values by
  plain string joining. Container-isolated workers failed to start whenever a path held a comma, until
  [#195304](https://github.com/openclaw/openclaw/pull/195304) 77 days later.
- **Latent.** pnpm changed the format of its launcher shims. After `openclaw update` on a pnpm global install, every
  `openclaw` command then failed ([#201735](https://github.com/openclaw/openclaw/pull/201735)); no OpenClaw change
  broke it.
- **Not a defect.** [#199831](https://github.com/openclaw/openclaw/pull/199831), titled "fix", is part 10 of a
  16-PR sidebar redesign that landed the same day.
- **One change, three fixes.** Within six days of #188978, three PRs fixed separate failures it caused: updates
  that rolled back when one plugin lacked a `package.json`, a repair that refused every time, and a dozen extra
  whole-database copies per update.

## Limits

- **Three weeks of fixes.** Causes reach back to 2025-12, but a bug only counts if it was fixed in the window.
  Bugs still on main, and bugs nobody fixed, are invisible.
- **Hindsight by model readers.** The line between never-worked, latent and not-a-defect is a judgment, and two
  readers disagree about 1 time in 6. 37 of the 300 answers came from the first version of the reader brief, which
  differs only in its git instructions.
- **Nothing was executed.** Mechanisms come from reading diffs and PR text. Tests a fix PR says it ran are taken on
  its word.
- **The local clone is shallow and partial.** 41 of the 156 causes predate its 2026-09-03 graft. Readers traced
  those through GitHub's history. Local blame points at the graft for older code, which lowers its hit rate here.
- **"Names its cause" is mechanical.** Any mention of the causing PR number or commit counts.
