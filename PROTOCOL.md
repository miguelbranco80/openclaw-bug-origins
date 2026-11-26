# Protocol: how this study is run

This file is the experimental setup. It is written so that a person or an agent who has never seen how the study
was made can run it again from nothing, for the same dates or for other dates, using only what is in this
repository.

There are three things you may want to do. Each has one section below.

| You want to | What it needs | Result |
|---|---|---|
| [Rebuild](#rebuild-from-the-stored-answers) the report from the stored answers | Python 3 | Identical, to the last digit |
| [Regenerate](#regenerate-from-nothing) the whole study from nothing | A clone of the project, GitHub read access, model access | The same procedure; numbers close to the published ones, not identical, because models answer afresh |
| [Extend](#extend-to-more-fixes-or-a-longer-period) it to more fixes or a longer period | The same | Old cases keep their answers; only new cases are worked on |

Everything is driven by one command, `python3 study.py`, and one settings file, `study.json`.

## The idea in one paragraph

Take every change titled "fix" in a period. Put them in a fixed random order and take the first N: that is the
sample. For each sampled fix, collect the evidence (what it changed, and which earlier commits last touched those
lines) and have a model read it and say what the fix repaired and which earlier change caused the problem. For each
causing change, fetch what the project's review bot had said before it merged and have a model say whether the bot
had named the bug. Count everything against all commits and pull requests of the period. Separately, show a few
causing changes to several models with no hint, and check what they report. A second model from a different maker
re-reads a slice of every judgment.

## The parts

| Part | What it is |
|---|---|
| `study.json` | The settings: the pinned commit, the periods, the sample sizes, which model answers which question |
| `study.py` | The one command: `doctor`, `status`, `run <stage>`, `judge <step>`, `rebuild`, `compare`, `reset` |
| `pipeline/` | What `study.py` is made of: settings, the model runner, GitHub access |
| `fix-origins/` | The collection scripts, the briefs given to models, and every stored answer |
| `dataset/` | The facts the questions read, assembled from `fix-origins/` |
| `questions/` | One script per question; each reads only `dataset/` |
| `report/render.py` | Writes `README.md`, the report, from the questions' results |
| `work/` | Scratch space made while running: logs, code exports, work orders. Never committed |

## Settings: `study.json`

| Setting | Meaning |
|---|---|
| `repository` | The GitHub repository studied |
| `tip` | The pinned commit. All history is read as of this commit, so reruns see the same history |
| `commits_since` | Start of the list of all commits (the denominator for "bugs per 100 commits") |
| `frames` | The periods of fixes. Each has an `id`, a `since` date, an optional `until` date, a `sample` size, `reread`: how many of its sampled fixes the other maker's model also reads, and `reread_bot`: whether the other maker's model also reads this period's bot reviews (default yes) |
| `comparison_sample` | How many ordinary pull requests to fetch as a comparison group |
| `pilot.per_kind` | Blind review experiment: how many broken-later and how many never-worked cases to take |
| `pilot.skip` | Cases left out of the blind review because their causing commit could not be read in the original clone. Empty for a new study |
| `pilot.verify_arms` | Which reviewers' reports are checked for being real |
| `judging` | For every model step: the tool that runs it (`backend`) and the `model` |
| `limits.effort` | The reasoning effort every model run uses |
| `limits.jobs` | How many model runs at once |
| `limits.max_wait_minutes` | How long to wait out a rate limit before pausing |
| `limits.github_reserve` | Stop using GitHub when fewer than this many calls are left in the hour, and wait for the reset |

One thing is not in the settings because it differs per machine: where the clone of the project is. Set the
environment variable `OPENCLAW_CLONE` to its path once per shell (`export OPENCLAW_CLONE=/path/to/clone`); every
`study.py` command except `rebuild`, `status` and `compare` needs it. Without it, `work/openclaw` is used.

**Ranks.** A fix's rank is its place in its period's random order. Frame 1 has ranks 1, 2, 3, and so on; frame 2
has ranks 100001, 100002, and so on. A rank never changes once given, so every stored answer stays valid when a
frame is added or a sample is enlarged.

## What you need

- Python 3.9 or later. No packages.
- `git`.
- The GitHub command line tool `gh`, signed in. Every GitHub call is read-only.
- For the model steps: the Codex command line tool (`codex`), the Claude Code command line tool (`claude`), or an
  agent session that can start subagents. See [Model steps](#model-steps).
- About 20 GB of free disk: 12 GB for a clone of the project and 5 GB for the blind review's code exports.

Before anything else, and whenever something stops:

```bash
python3 study.py doctor
```

It checks the settings, the clone, GitHub's remaining quota and whether each model tool is signed in, and says
what to fix. A line marked `STOP` blocks the stages that need that thing; `NOTE` is information. A signed-out model
tool is a `STOP` only when the settings give it cases that are not answered yet, so on the published study, where
everything is answered, it is a `NOTE`. To see how far a run has got:

```bash
python3 study.py status
```

## Try it small first

Before a full regeneration, run a ten-fix study in a second copy of this repository. It exercises every stage and
every model step in about twenty minutes, and shows whether your clone, sign-ins and quotas are in order.

```bash
git clone . ../study-trial && cd ../study-trial
```

```bash
python3 study.py reset --yes && cp examples/small-study.json study.json
```

```bash
export OPENCLAW_CLONE=/path/to/your/openclaw/clone
```

```bash
python3 study.py doctor && python3 study.py run all
```

- `reset` deletes the published study's data in that copy; that is what starting from nothing means. `git status`
  will show those files as deleted.
- `examples/small-study.json` uses Codex for every model step and two reviewers. It does not exercise the `claude`
  backend, the `agent` backend or the three-files-at-a-time reviewer. Edit its `judging` section to try others.
- With ten fixes the report's numbers mean nothing, and its closing note will list several comparisons as "(not
  available)" because there were too few cases to make them. The trial only shows that every step runs.
- To try an extension afterwards, commit the finished trial first (`git add -A && git commit -m trial`), then
  follow [Extend](#extend-to-more-fixes-or-a-longer-period).

## Rebuild from the stored answers

```bash
python3 study.py rebuild
```

This recomputes every derived file, number and chart, and rewrites `README.md`. It needs no network, no clone and
no model. If nothing was changed, `git status --short` afterwards prints nothing.

## Regenerate from nothing

### Step 0. Get a clone of the project

The scripts read history with `git`; they never check files out, build or run the project.

```bash
git clone --no-checkout --single-branch --branch main --shallow-since=2026-09-03 --filter=blob:limit=10m https://github.com/openclaw/openclaw.git work/openclaw
```

- This takes about ten minutes and 12 GB. It was tested on 25 November 2026: the stages give the same sampling
  frame and commit list from this clone as from the clone the published study used.
- `--shallow-since` must be on or before the earliest date in `study.json`, and earlier is better: a reader can
  only trace a cause as far back as the clone goes. The first version used 2026-09-03; the current one was deepened
  to 2026-07-01 with `git -C work/openclaw fetch --shallow-since=2026-07-01 origin main` (two more minutes, 2 GB).
- `--filter=blob:limit=10m` leaves out files over 10 MB. The scripts set `GIT_NO_LAZY_FETCH=1` on every git command
  so that git never downloads a missing file on its own. During the original study, searches without that setting
  pulled in 12 GB.
- A clone you already have works too: set `OPENCLAW_CLONE` to it. `doctor` checks that it contains the pinned commit
  and reaches back far enough.
- Causes older than the clone's first commit cannot be traced by git. Readers are told this and answer "unclear" or
  use GitHub lookups where they have them.

### Step 1. Start clean

Only when starting a new study in a copy of this repository. This deletes every stored answer and generated file:

```bash
python3 study.py reset --yes
```

Then edit `study.json`: the pinned commit, the dates, the sample sizes. For a new study, set `pilot.skip` to `[]`.

### Step 2. Run the stages

```bash
python3 study.py run all
```

or one stage at a time, in this order. Each stage skips what is already done, so it can be stopped and run again.

| # | Stage | What it does | Needs | Makes | How to check |
|---|---|---|---|---|---|
| 1 | `frame` | Lists every fix of each period in its random order, and every commit on main | clone | `fix-origins/population.tsv`, `dataset/commits.tsv` | It prints the population of each frame. The published frame 1 is 3,996 |
| 2 | `evidence` | For each sampled fix, finds which earlier commits last touched the lines it changed, and writes one evidence file | clone, GitHub | `fix-origins/blame.jsonl`, `fix-origins/evidence/` | `status` shows as many evidence files as sampled fixes |
| 3 | `origin` | A model reads each fix and says what it repaired and which change caused it. A second reader takes about 15% of fixes, chosen by a fixed rule | clone, model | `fix-origins/reads/`, `reads-second/`, `cases.jsonl`, `second_reads.jsonl` | No `PROBLEM` lines. `status` shows as many accepted answers as sampled fixes |
| 4 | `bot` | Fetches what the review bot wrote on each causing pull request, as it stood at merge. A model says whether the bot named the bug | GitHub, model | `fix-origins/clawsweeper/` | `status`: `flag` answered equals its cases |
| 5 | `facts` | Fetches who opened, merged and reviewed every pull request, its branch name and the issue it closes, and a random comparison sample of ordinary pull requests | clone, GitHub | `dataset/pull_requests.tsv`, `dataset/pull_request_links.tsv`, `fix-origins/comparison/`, `dataset/changes.jsonl` | It prints how many pull requests it has of how many wanted |
| 6 | `rereads` | A model from a different maker re-reads a slice of the fixes and every bot review | clone, model | `fix-origins/audit/raw/` | `status`: both re-read steps answered |
| 7 | `pilot` | The blind review experiment: chooses cases, exports the code as it stood at each causing change (into `work/exports/`, about 5 GB for the published 40 exports, never committed), runs the reviewers, has graders say who named the known bug, and has checkers test the other reports | clone, GitHub, model, disk | `fix-origins/review-pilot/` | `status`: every `review`, `grade`, `tags`, `refute` and `laterfix` line answered |
| 8 | `report` | Assembles the dataset, runs every question, draws the charts, writes the report | nothing | `dataset/`, `results/`, `charts/`, `README.md` | It ends with "Rebuilt." Read the report's claims against its numbers (see [What a rerun cannot do](#what-a-rerun-cannot-do-for-you)) |

Stage 7 is separate from the rest: it gives findings 7 to 9. Every other finding comes from stages 1 to 6 and 8,
except finding 10, which rests on the first study (see below).

## Model steps

A model step gives a model a brief (a Markdown file in this repository), one case, and a rule for what it may
read, and takes back one JSON object. `pipeline/judge.py` defines every step in one place: its cases, its brief,
where its answers are stored and what a valid answer looks like.

| Step | Stage | Brief | One case is | The model may read | Answers stored in |
|---|---|---|---|---|---|
| `origin` | 3 | `fix-origins/reader-prompt.md` | a sampled fix | its evidence file; the clone, with read-only git; GitHub lookups where the tool allows | `fix-origins/reads/` |
| `origin_second` | 3 | the same | about 15% of them | the same | `fix-origins/reads-second/` |
| `origin_reread` | 6 | the same | the first `reread` per frame, in a fixed order | the same | `fix-origins/audit/raw/origin/` |
| `flag` | 4 | `fix-origins/clawsweeper/reader-prompt.md` | a causing change the bot reviewed | one bundle of the bot's text | `fix-origins/clawsweeper/reads/` |
| `flag_reread` | 6 | the same | the same | the same | `fix-origins/audit/raw/flag/` |
| `review` | 7 | `review-pilot/prompt-whole.md`, `prompt-per-file.md` | a pilot case, once per reviewer | the code as it stood at the causing change, no history | `review-pilot/data/runs/` |
| `grade` | 7 | `review-pilot/grader-prompt.md` | a pilot case | the bug and every reviewer's findings, reviewers shown as letters | `review-pilot/data/grade/reads/` |
| `grade_reread` | 7 | the same | the same | the same | `fix-origins/audit/raw/grade/` |
| `tags` | 7 | `review-pilot/tag-prompt.md` | a pilot case | the bug's description and the exported code | `review-pilot/data/grade/tags/` |
| `refute_gpt`, `refute_opus` | 7 | `review-pilot/refute-prompt.md` | a pilot case; control cases again on the fixed code | the reports, with no model names, and the exported code | `review-pilot/data/verify/refute-*/` |
| `laterfix` | 7 | `review-pilot/laterfix-prompt.md` | a pilot case | the reports and later fix commits touching the same files | `review-pilot/data/verify/laterfix-reads/` |

Run one step by itself, on every case without an answer or on named cases:

```bash
python3 study.py judge origin
```

```bash
python3 study.py judge flag --cases 4,5,12
```

**How one run goes.** The runner copies the case's files into an empty folder (or uses the code export), sends
the brief plus a "Your task" section naming the case, and asks for one JSON object as the final message. It checks
the answer has the right fields and values, stores it, and adds a line to `fix-origins/judging-log.jsonl` saying
which tool, model and brief produced it. An answer that fails the check is asked for once more, then recorded as a
failure under `work/failures/`. Models never write files.

**Three ways to run a prompt.** The `backend` of each step in `study.json`, or `--backend` on the command line:

| Backend | What runs | Isolation |
|---|---|---|
| `codex` | The Codex command line tool, headless | Read-only sandbox, no network, the user's Codex settings and project instructions ignored |
| `claude` | The Claude Code command line tool, headless | Reading tools only. Where a step needs git or GitHub, the model gets `pipeline/look.py` and nothing else: it can run a fixed set of read-only lookups and cannot write, push or post |
| `agent` | No tool. See below | Whatever the subagent's session enforces; the work order states the limits |

Readers work from text written by strangers: commit messages and pull request descriptions. That text can contain
instructions. This is why no backend gives a model the `git` or `gh` commands with network access, and why answers
are checked for shape before they are stored. Two limits to know:

- The `claude` backend holds the model to `pipeline/look.py` through Claude Code's own permission rules. That path
  could not be exercised while this protocol was written, because the tool was signed out; its sign-out detection
  was. Try one case first (`python3 study.py judge flag --cases <n>`) and read its log under `work/logs/`.
- The `agent` backend cannot enforce anything: a subagent has whatever its session allows. The work order states
  the limits, and that is all.

To run a step with a different tool or model than the settings say, for one run:

```bash
python3 study.py judge origin --backend codex --model gpt-6.2-sol
```

Record such a change: the model that answered is part of the result. `judging-log.jsonl` keeps it per answer.

### Model steps without a command line tool

When the tool a step needs is signed out or not installed, an agent session can do the step by starting
subagents. This is how the published study's Claude answers were made.

```bash
python3 study.py judge origin --backend agent
```

1. This writes one work order per unanswered case under `work/orders/<step>/`: a `.md` file holding the complete
   brief, the task, what may be read and where to write the answer.
2. For each `.md` file, start one fresh subagent whose whole task is that file's text. Use the model the settings
   name for the step. Do not add context, hints or other cases' answers. Run about ten at a time.
3. Each subagent writes its JSON answer to the `.answer.txt` file its order names.
4. Run the same command again. It checks each answer, stores the valid ones, and keeps the orders whose answers
   were missing or invalid. Repeat until it reports none waiting.

## When something stops

Long runs meet sign-outs, rate limits and used-up quotas. The rule is the same for all of them: **nothing is lost,
and the fix is to clear the cause and run the same command again.** A command that stops for one of these reasons
prints `PAUSED:` with the reason and exits with code 75.

| What happened | What the run does | What you do |
|---|---|---|
| A model tool is signed out | Pauses at once | `codex login`, or `claude auth login`. Or run the step with another backend |
| A model tool reports a usage or rate limit | Waits 1, then 3, then 9 minutes and so on, up to `limits.max_wait_minutes`; then pauses | Wait for the quota to return, then rerun. Or switch backend or model for that step, and record it |
| A model gives no answer, or an invalid one | Asks once more, then records a failure and goes on to the next case | Read `work/failures/<step>/<case>.txt`, then rerun the step; failed cases are tried again |
| GitHub's hourly limit is nearly used | Waits for the reset when it is within `limits.max_wait_minutes`; otherwise pauses | Rerun after the reset time it prints |
| `gh` is signed out | Pauses at once | `gh auth login` |
| GitHub or the network fails briefly | Retries with growing pauses, then pauses | Rerun |
| A stage's script fails | Stops with `FAILED:` and the script's name | Read the error above it; it is a bug or a missing input, not a quota |

What makes this safe: every answer and every fetched record is its own file, written only when complete. A rerun
looks at which files exist and does only the rest. Two runs of the same step at once are harmless but wasteful.

Budget to expect, from the published study: about one model run per sampled fix for `origin` (several minutes
each), one GitHub query per causing pull request, about 360 queries for all pull requests, about 720 more for their branch names and linked issues, and about 400 for the
comparison sample.

## Extend to more fixes or a longer period

**More fixes from the same period.** Raise that frame's `sample` in `study.json`, then:

```bash
python3 study.py run all
```

Only the new ranks are blamed, read and judged.

**A longer or different period.** Add a frame to `study.json` with the next `id`, for example:

```json
{"id": 2, "since": "2026-10-01T00:00:00Z", "until": "2026-11-01T00:00:00Z", "sample": 300, "reread": 60}
```

Then run all stages. Keep these in mind:

- Give frames the same sampling share (sample divided by population; `frame` prints both), so that every fix counts
  equally in the rates. Run stage `frame` first to see the new frame's population, then set its `sample`; `doctor`
  warns when the shares differ and says what sample would match frame 1.
- `commits_since` and the clone's history must reach back at least as far as the earliest causes you expect.
  `doctor` checks the clone. Stage `facts` prints a `NOTE` with how many traced bugs were left out of the
  comparisons because their causing change is older than `commits_since`.
- To study fixes after the pinned commit, fetch in the clone, set `tip` to the newer commit, and give the old frame
  an `until` equal to the old tip's date, so its population stays what it was.
- The blind review's cases are chosen once and pinned: the facts it uses about each case are kept in
  `fix-origins/review-pilot/data/pilot_cases.jsonl` and `pilot_bot.jsonl`. Adding frames, or changing the main
  reader, does not change the experiment. Delete `review-pilot/data/` to choose and run it again.

**Compare with the study before the change.** Commit before extending. After extending, and before committing
again:

```bash
python3 study.py compare HEAD
```

`compare <commit>` sets the numbers now in `results/` against the same numbers at that commit, and lists each one
that left its earlier plausible range, or changed by more than a tenth where it has no range. Once the extension
is committed too, the commit before it is `HEAD~1`. The earlier report itself is in git history.

## What a rerun cannot do for you

- **Identical model answers.** Models are not deterministic and versions change. Expect agreement of the kind the
  report measures between readers, not the same digits.
- **The report's sentences.** Every number in `README.md` is looked up from the results, but the sentences around
  them ("no clear difference", "about three weeks") were written for the published numbers. After a regeneration,
  read the main results, the ideas table and each finding's first paragraph against its numbers and edit `report/render.py` where
  a sentence no longer fits. `study.py compare` shows where to look first.
- **Other reviewers in the blind review.** `questions/q07` compares named reviewers (the two strongest against the
  bot, three files at a time against the whole change). With a different `judging.review` list every reviewer still
  gets its row, but those named comparisons are skipped and the report prints "(not available)" where its text
  expected them. Edit `report/render.py` to match the new design.
- **Comparisons a small study cannot make.** A comparison with no cases on one side has no ratio, and the report
  prints "(not available)" there too. `study.py rebuild` ends with a note listing every such gap.
- **The first study.** `detection-check/` is a one-off done by hand in November 2026: 29 bugs whose fix named the
  change that caused them, each checked against the project's written rules. Its figures are typed into
  `dataset/named_cause_study.json`. It is not regenerated. Finding 10 and one comparison in finding 5 rest on it and
  describe November 2026 only.
- **The same GitHub.** Pull request descriptions and bot comments can be edited later. The fetch steps read them as
  they stood at merge, from GitHub's edit history, which keeps this stable.

## The two versions of this study

| | Published first (tag `published-2026-11`) | Current |
|---|---|---|
| Fixes | 300, from 1 to 22 November 2026 | 1,202: those 300, and 902 from 10 September to 1 November |
| Main reader of fixes and bot reviews | Claude Opus 5.5 | gpt-6.2-sol, for every fix of both periods |
| Other maker's check | gpt-6.2-sol on 60 fixes and all 113 bot reviews | The Claude Opus 5.5 answers already made: all 300 November fixes, and its verdicts on bot reviews where both readers named the same causing pull request |
| Clone history | from 3 September 2026 | from 1 July 2026, so that September fixes can be traced about as far back as November's were |
| Blind review experiment | 30 cases from the November fixes as Opus read them | The same experiment, unchanged and pinned |

One reader for both periods means a difference between the periods is a difference in the fixes, not in who read
them. With the longer period, every comparison of bug rates also holds equal when the change landed, because an
older change has had longer for its bugs to be found and fixed. `fix-origins/audit/reuse_published_opus.py` moved the Opus answers into the check's folders. To see the first
version: `git checkout published-2026-11`. To list what changed: `python3 study.py compare published-2026-11`.

## What differs from how the published answers were made

The published answers were made before this protocol existed. The differences are small and are recorded here so
that a regeneration is not mistaken for an exact replay.

- The first readers (Claude Opus 5.5) were subagents of an interactive session, five fixes per reader, and wrote
  their answers to files. Under this protocol a reader gets one fix and gives its answer as its final message. The
  rubric is the same; the brief's version went from v1.1 to v1.2 for this.
- Those subagents had the session's context of the project's contributor guide. A headless run does not.
- The second-maker re-reads of fixes used a shortened brief (the rubric section only). They now use the full brief.
- Stored answers made before this protocol have no line in `fix-origins/judging-log.jsonl`.
- Some Codex runs read a personal review guide on the original machine. `--ignore-user-config` and the read-only
  sandbox are set, but the sandbox does not stop reads outside the working folder.
