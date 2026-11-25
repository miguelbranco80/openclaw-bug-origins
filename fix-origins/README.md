# Fix origins dataset

Where do the bugs fixed on `openclaw/openclaw` main come from? This folder holds a random sample of product fixes
merged between 2026-11-01 and `e6b42e31bc1` (2026-11-22), each traced back to its origin with `git blame` plus a
model reader. Findings are in [report.md](report.md). Everything here can be extended by another batch without
redoing earlier work.

## Files

| File | What it is |
|---|---|
| `population.tsv` | The sampling frame: every fix in the population, ranked. Columns: `rank`, `sha`, `date`, `subject`. |
| `blame.jsonl` | One line per blamed fix: the top five blame candidates (append-only). |
| `cases.jsonl` | One line per classified fix: the primary reader's answer plus mechanical fields (append-only). |
| `second_reads.jsonl` | Independent second-reader answers for about 15% of fixes, same schema (append-only). |
| `rechecks.jsonl` | My own re-check of every high-confidence `regression` verdict in the first batch (ranks 1–50). |
| `pr-cache/` | The fix PRs' descriptions as fetched from GitHub (`gh api`, public read), used by readers and by `fix_names_cause`. |
| `reader-prompt.md` | The full brief each reader gets. |
| `scripts/` | `sample.py`, `blame.py`, `evidence.py`, `second.py`, `assemble.py`, `stats.py`, `fullhist.sh`. |
| `stats.md` | Every figure in the report, computed by `scripts/stats.py`. |
| `dispatch-template.md` | The exact task text given to each reader alongside `reader-prompt.md`. |

## Population and sampling

- Population: first-parent commits reachable from `e6b42e31bc1522b8596958fbdd85c394b23fca7b` with commit date on or
  after `2026-11-01T00:00:00Z` (7,820 commits), whose subject starts with `fix` in any case (5,108), and that change at
  least one non-test file under `src/`, `ui/`, `extensions/`, `packages/` or `apps/` (**3,996**). A path is a test
  file when it contains `.test.`, `/test/`, `test-support` or `fixtures`.
- The cutoff is pinned in UTC so the frame does not depend on the machine's time zone. (Plain `--since=2026-11-01`
  follows the local time zone and gives 7,578 commits / 3,880 fixes here, which is why the earlier study's counts
  differ slightly.)
- Order: ascending `sha256("fix-origins-v1:" + full sha)`. Ranks 1–N are a simple random sample of size N. The next
  batch is the next ranks.
- Second reader: a fix gets one when `sha256("fix-origins-second-v1:" + sha)` (first 8 hex digits as a fraction of
  2³²) is below 0.15. This depends only on the sha, so it carries over to new batches.

## Before you run anything: this checkout is shallow and partial

- It is **shallow**, grafted at `b14a2cae4bf6` (2026-09-03). Locally that commit looks like a 37,000-file import,
  and `git blame` credits every older line to it. `blame.py` marks those candidates `"graft": true`, and readers are
  told it is never a cause.
- It is **partial**: about 37,000 objects reachable from `e6b42e31bc1` are not stored locally (check with
  `GIT_NO_LAZY_FETCH=1 git rev-list --objects --missing=print e6b42e31bc1 | grep -c '^?'`). Older commits and trees
  are present (from the `origin` fork fetch), but most file contents before the graft are not.
- Git silently downloads any missing object it needs ("lazy fetch"). On 2026-11-25, unscoped `git log -S` searches
  by readers pulled in ~12 GB of large blobs this way. **Every script sets `GIT_NO_LAZY_FETCH=1`, and readers must
  prefix every git command with it** and limit `-S`/`-G`/`-p` searches to a single file. A missing object then
  fails fast (or after a timeout) instead of touching the network.
- To list commits older than the graft by path, use a scratch git dir that borrows this checkout's objects without
  the shallow file (trees only; no file contents):

```bash
export FIX_ORIGINS_FULL_GIT_DIR=$(sh research/fix-origins/scripts/fullhist.sh <scratch>/fullhist.git)
```

  `assemble.py` uses it for the `is_ancestor_of_fix` check. Readers use it for `git log -- <path>`, and read older
  diffs through `gh api repos/openclaw/openclaw/commits/<sha>` and GraphQL `blame(path:)`.
- The GitHub REST limit is 5,000 calls an hour, shared by all readers. Fifteen parallel readers exhausted it once.
  Run about ten readers at a time (one batch of 50) and cap each at about 15 REST calls per fix.

## Extending the sample by one batch (ranks A to B)

Run from the repo root. Nothing here needs network except `evidence.py` fetching fix PR descriptions with `gh`.

```bash
python3 research/fix-origins/scripts/blame.py --from A --to B
```

```bash
python3 research/fix-origins/scripts/evidence.py --from A --to B --out <scratch>/evidence
```

Then give each model reader the full text of [reader-prompt.md](reader-prompt.md), the hard rules above (no lazy
fetch, path-limited searches, foreground commands only, the REST budget), the full-history git dir path, five ranks,
the paths of their bundles `<scratch>/evidence/<rank as 4 digits>.md`, and an output path `<scratch>/reads/<rank>.json`
per rank. The dispatch text used for batches 3 to 6 is in [dispatch-template.md](dispatch-template.md). Then:

```bash
python3 research/fix-origins/scripts/assemble.py --reads <scratch>/reads --from A --to B
```

(with `FIX_ORIGINS_FULL_GIT_DIR` exported as above, so causes older than the graft get a correct `is_ancestor_of_fix`)

For the second reader, list the ranks with `scripts/second.py --from A --to B`, give a different reader the same
prompt and bundles for those ranks (never the first answer), with outputs in a separate directory, and run:

```bash
python3 research/fix-origins/scripts/assemble.py --reads <scratch>/reads2 --from A --to B --second
```

`assemble.py` prints `PROBLEM` lines for missing or invalid answers and does not write them; re-run the reader for
those ranks and assemble again (ranks already written are skipped). Finally recompute the figures:

```bash
python3 research/fix-origins/scripts/stats.py > research/fix-origins/stats.md
```

Keep the same `TIP`, cutoff and salt. Changing any of them starts a new frame (call it v2) rather than extending this
one.

## How the first 300 were produced (history worth knowing)

- Ranks 1–50 were first read under brief v1, before the graft problem was understood. Thirteen primary and three
  second-reader answers either named the graft commit as the cause or gave up at it. Those were discarded unread by
  the assembly step and re-read under v1.1 (ranks 5, 6, 9, 10, 17, 18, 19, 20, 31, 32, 35, 47, 49; second reader 5,
  10, 32). The other 37 batch-1 answers are v1 and stand; v1.1 changed only git instructions, not the rubric.
- A brief attempt at full-history blame (through `fullhist.sh`) was abandoned because most pre-graft file contents
  are missing. All blame in `blame.jsonl` is on the shallow checkout.
- `cases.jsonl` and `second_reads.jsonl` for ranks 1–100 were rebuilt once from the same reader answers after
  switching commit file counts to `--no-renames`, before anything consumed them. From then on both are append-only.

## What a reader is asked to do

Each reader gets an evidence bundle per fix: the fix message, the fix PR description, the list of changed files, the
product diff, and the five commits blame names, with the top three's messages and diffs limited to the files the fix
touched. It may dig further with read-only `git` and `gh api`. It decides the origin (`regression`, `never-worked`,
`latent`, `not-a-defect`, `unclear`), names the causing commit for the first two with a quote from the causing diff and
a confidence, and records user visibility, impact and area. `regression` requires pointing at the breaking line and
checking that the behavior worked before. See [reader-prompt.md](reader-prompt.md) for the exact wording.

## Schema of `cases.jsonl` and `second_reads.jsonl`

Reader fields (from the reader's answer):

| Field | Meaning |
|---|---|
| `rubric` | Reader-prompt version: `v1` (37 batch-1 answers) or `v1.1` (all others; same rubric, safer git instructions). |
| `reader` | `primary` or `second`. |
| `origin` | `regression`, `never-worked`, `latent`, `not-a-defect`, `unclear`. |
| `cause_sha`, `cause_pr` | The causing commit and its PR, for `regression` and `never-worked`; else null. |
| `confidence` | `high`, `medium`, `low` (null without a cause). |
| `cause_quote` | One sentence quoting what in the causing diff did it. |
| `trigger_sha` | For `latent`: an in-repo commit that exposed the old code, if any. |
| `user_visible` | `yes`, `internal`, `unclear`; `user_saw` is one plain sentence. |
| `impact` | `failed-every-time`, `sequence-or-timing`, `permissions`, `slower-or-heavier`, `presentation`, `data-loss-or-duplication`, `other`. |
| `area` | `gateway`, `agents`, `channels`, `ui`, `plugins`, `models/providers`, `cron`, `update`, `storage`, `cli`, `apps`, `other`. |
| `summary`, `reasoning` | What the fix changed; why this origin. |

Mechanical fields (computed by `assemble.py` from git and the PR cache, not by the reader):

| Field | Meaning |
|---|---|
| `rank`, `sha`, `fix_date`, `fix_subject`, `fix_pr`, `fix_author`, `fix_files_changed` | The fix. |
| `fix_adds_test` | The fix changes a file whose path contains `.test.`, `/test/`, `test-support`, `fixtures`, `test-helpers`, `__tests__`, `.e2e.`, `/e2e/` or `.spec.`. |
| `cause` | Causing commit's `date`, `days_to_fix` (commit time of fix minus commit time of cause), `prefix` (`feat`, `fix`, `refactor`, `perf`, `other`, from the subject's first word), `subject`, `pr`, `author` (git author name), `files_changed`, `is_ancestor_of_fix`. Null without a cause. |
| `fix_of_fix` | The causing commit's subject starts with `fix`. |
| `fix_names_cause` | The fix's commit message or PR description contains `#<cause PR>`, `/pull/<cause PR>`, or the cause sha (7+ chars). |
| `blame_agrees` | The top blame candidate is the cause the reader chose. `blame_in_top5`: it is any of the five. |
| `blame` | `product_files`, line counts, `blame_errors`, and the five `candidates` (sha, removed and context line counts, `context_only`, `graft` (the shallow-graft commit, meaning "older than 2026-09-03"), date, author, subject, PR, files changed). |
