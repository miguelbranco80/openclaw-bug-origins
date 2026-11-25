> **Superseded where it differs.** This is the working report of one study. The top-level `README.md` is the current statement of the findings, and `CORRECTIONS.md` lists what changed after a second-model check.

# Why regressions reached main: missing rules, missed rules, or ignored findings

I looked at 41 bugs that reached `openclaw/openclaw` main between 2026-11-01 and 2026-11-22. For each one, a later
fix or revert names the PR that caused it. For each causing PR I asked three questions. Did a written rule already
forbid what it did? Did ClawSweeper, the project's review bot, warn about it? Did anyone answer that warning?
Twelve of the 41 pairs are set aside, because either the link between the two PRs is weak or no user could have hit
the failure. The headline numbers below use the other 29: confirmed regressions that a user could have hit.
Details: [cases.md](cases.md). Full candidate list: [candidates.md](candidates.md).

## The split (29 confirmed regressions)

| What was true when the causing PR merged | Cases |
|---|---|
| No written rule covered the behavior | **24** |
| A rule in a guide ClawSweeper loads covered it, and review missed it | **3** |
| A rule covered it, but only in a guide ClawSweeper does not load | **1** |
| No rule then; one was added afterwards | **1** |
| ClawSweeper flagged the exact failure on the merged revision and it merged with no public answer | **1** (also counted above as "no rule") |

The rows answer two separate questions, so the last row overlaps the first. That case, #177227, had no rule, yet
ClawSweeper caught the bug anyway.

ClawSweeper's side, for the same 29: it flagged the exact failure in 2 cases (one went unanswered, one got a partial
answer), reviewed without flagging in 24, and never reviewed 3. Across all 41 pairs the picture is the same: 34 with
no rule, 4 with a rule in a loaded guide, 2 with a rule only in an unloaded guide, 1 rule added later, and 1 flag
merged unanswered.

**Only one regression came from ignoring a review.** Most escapes had no rule to break. Where a rule did exist,
review usually missed it. A warning that was given and then ignored happened once.

## Could the existing rules be checked from the diff?

Four rules existed when the 29 core PRs were written (cases 4, 18, 33, 40). **None could be decided from the
changed lines alone.** Three needed code outside the diff to see the break. One needed a runtime measurement. No
`scripts/check-*` guard targeted any of these rules. The diff alone was enough in three cases, but none of them is
in the core group: the later rule in case 21, and set-aside cases 13 and 38.

## Cases that show each bucket

**No rule (24).**
- [#196065](https://github.com/openclaw/openclaw/pull/196065) → revert
  [#200159](https://github.com/openclaw/openclaw/pull/200159): "Skills used" re-read the whole conversation on every
  chat open, freezing large sessions for about a minute. No guide limits history-page reads. ClawSweeper saw the
  cost and judged it acceptable ("older pages and cursor deltas avoid full inventory reconstruction"). It never
  reviewed the head that merged.
- [#170534](https://github.com/openclaw/openclaw/pull/170534) → [#203174](https://github.com/openclaw/openclaw/pull/203174):
  Gemini's "stay silent" replies started showing up. Nothing written covers provider signature parts.
- [#164304](https://github.com/openclaw/openclaw/pull/164304) → [#192037](https://github.com/openclaw/openclaw/pull/192037):
  every channel request to start a session was refused.
- [#185730](https://github.com/openclaw/openclaw/pull/185730) (1,452 files, no ClawSweeper review) caused two
  separate escapes, cases 7 and 19.

**A loaded rule, missed (3).**
- [#203487](https://github.com/openclaw/openclaw/pull/203487) → [#203551](https://github.com/openclaw/openclaw/pull/203551):
  Stop no longer cancelled a running MCP tool call. The loaded guide says "abort stops it through its signal"
  ([src/agents/AGENTS.md:29](https://github.com/openclaw/openclaw/blob/75886fc2a70db6bf068f6c5b26c6e1f88f96fc78/src/agents/AGENTS.md#L29)).
  Seeing the break needs `src/gateway/mcp-http.ts`, which the PR did not touch.
- [#196550](https://github.com/openclaw/openclaw/pull/196550) → revert [#199561](https://github.com/openclaw/openclaw/pull/199561):
  moving compaction into workers made cold compaction slower and use more total CPU. The root guide makes the
  performance skill binding, and the skill says "A worker move or a deferral relocates cost; count main-thread and
  total work both"
  ([SKILL.md:57](https://github.com/openclaw/openclaw/blob/d81a57daf65aa1e36226803e0019d0478c338657/.agents/skills/openclaw-performance/SKILL.md#L57)).
- [#188978](https://github.com/openclaw/openclaw/pull/188978) → [#190857](https://github.com/openclaw/openclaw/pull/190857):
  updates from 2026.6 failed. The update contract that root `AGENTS.md:78` makes binding says the installed updater
  "can't be patched". This is the closest near miss: ClawSweeper flagged the same guard for the 2026.9.3 updater on
  an older head, the author fixed that path, and the 2026.6 path still broke.

**Rule only in an unloaded guide (1).** [#202608](https://github.com/openclaw/openclaw/pull/202608) →
[#202765](https://github.com/openclaw/openclaw/pull/202765) added a disk re-check of database ownership to every
Gateway state read. `src/gateway/AGENTS.md:10` says "Hot request paths never re-read, stat, or realpath them"
([link](https://github.com/openclaw/openclaw/blob/b9aa2b7e6cd264f1572506042944a7c335403295/src/gateway/AGENTS.md#L10)).
The PR changed files under `src/state/`, so ClawSweeper loaded only the root and docs guides. Set-aside case 13
has the same shape: the rule was in `src/plugins/AGENTS.md:47`, and the change was in `extensions/openai`.

**Flag merged unanswered (1).** [#177227](https://github.com/openclaw/openclaw/pull/177227) →
[#196641](https://github.com/openclaw/openclaw/pull/196641): on the merged head, ClawSweeper blocked the PR with "this
unconditionally adds a supplied temperature even though that model rejects it with HTTP 400", naming Activity
recaps ([comment](https://github.com/openclaw/openclaw/pull/177227#issuecomment-6265071757), version of
2026-11-06T06:33Z). It merged 8 minutes later with no reply, and recaps failed exactly that way. In
[#198288](https://github.com/openclaw/openclaw/pull/198288) (case 21) ClawSweeper flagged the class of bug, and the
author fixed only the three providers it named. LiteLLM then broke the same way.

**The pair handed in as an established example does not hold up.** For #200967 → #201563, the fix never names
#200967. It traces its failure to a file #200967 did not touch. Its "Talk attachment" note refers to reviews of the
fix's own earlier revision. The fix does remove the two mechanisms ClawSweeper flagged, unanswered, on #200967's
merged head, so the case is recorded as unclear, not as follow-through.

## Other patterns

- For 13 of the 29 causing PRs, ClawSweeper reviewed only an earlier revision. Three got no review at all; #203466,
  for example, merged 14 minutes after it opened. I did not measure how much the merged revision differed.
- 26 of 29 fix PRs say their regression test fails without the fix. Almost all say it fails on the fix's base or on
  main, not on the causing revision itself.
- Channel plugins appear only once, in a set-aside case. Channel fixes rarely name the PR that caused the bug, so
  this method under-samples them.

## How the sample was built

From `git log --first-parent --since=2026-11-01 e6b42e31bc1` (7,601 commits):

1. Pass 1, four `git log` searches, each with `-i`:
   - `--grep='^revert'`: 9 commits.
   - `-E --grep='reverts? (#[0-9]+|commit [0-9a-f]{7,})'`: 15.
   - `-E --grep='(regress(ion|ed)? (from|in|introduced by|since)|introduced (by|in)|caused by|broken (by|in|since)|broke in|after) (#[0-9]+|[0-9a-f]{9,40}|https://github.com/openclaw/openclaw/pull/[0-9]+)'`: 98.
   - `-E --grep='root.?cause.*(#[0-9]+|[0-9a-f]{9,40})'`: 25.

   The union is 143 commits.
2. Pass 2 kept commits whose subject starts with `fix`, `revert` or `undo` or contains "regress", leaving out
   `fix(ci|test|tests|docs|release|deps)`. Each kept commit has a body line that contains one of regress, introduc,
   since, broke, revert, root cause, caused by, started, first shipped or "landed in", together with a reference to
   another PR or commit. That gave 284. The union of both passes is 355.
3. Automatic drops: 32 by subject prefix (`test`, `chore`, `docs`, `ci`, `feat`, …) and 20 by CI, test, docs or
   release scope.
4. I read by hand the 93 commits whose body matches a stricter attribution pattern ("since #N", "introduced by",
   "regressed in", "reverts", "caused by", "#N made/added/removed …"), plus 5 worded differently. 41 were kept.
   They were kept when the fix names an earlier merged PR or commit as the cause of a product defect, however the
   defect was found. Drops cover CI and test fixes, in-branch reverts, bugs that predate the named PR, and design
   history. Every decision and reason is in [candidates.md](candidates.md).
5. #200967 → #201563 was added by hand because no search finds it. #196065 → #200159 was also requested, and the
   search found it anyway.

Agents make up 9 of the 41 pairs (22%), under the quarter cap. The 12 set-aside pairs are 7 with a weak link
(cases 2, 10, 13, 14, 22, 38, 41) and 5 with no user-visible failure (3: a style preference reversal; 15:
Windows-only test simulation; 25: unreachable code; 37: main CI only, rolled back before release; 39: test-only
effect).

## Limits

- The sample covers only regressions that someone later blamed on a specific PR. Regressions nobody attributed, and
  bugs still on main, are not in it.
- Classification is hindsight reading by model readers. Six parallel readers shared one strict rubric. I re-checked
  every "rule existed", "rule added later" and "flagged" verdict against the source, overrode one (case 33, from
  flagged to near miss), and spot-checked the "no rule" verdicts. A different reader might count rules that live in
  linked docs differently. Cases 18 and 33 depend on such links.
- Nothing was executed: no tests, builds or historical code. Fix PRs' test claims are their own word.
- Only the public record was used. ClawSweeper's private maintainer notes, any private reviews, and its prompt as it
  stood at each review are not visible. The loading rule comes from its current prompt
  ([review-item.md:11](https://github.com/openclaw/clawsweeper/blob/9b770415a1f46d903992c7a0303391b9d1901f72/prompts/review-item.md#L11)).
  Review versions were rebuilt from GitHub comment edit history.
