# Reader dispatch text (batches 3 onward)

Each reader is a fresh model agent with shell access to the checkout. It receives this text with `<FULLHIST>`,
`<S>` (a scratch directory holding `evidence/` and `reads/`) and the ranks filled in. A second reader gets the same
text plus the independence paragraph, and writes to `<S>/reads2/` instead.

---

You are a model reader for a research study of where bug fixes' defects came from in openclaw/openclaw. First read
<openclaw>/research/fix-origins/reader-prompt.md in full: it is your complete brief, rubric and
output format (rubric v1.1). Work in <openclaw>, read-only.

Hard rules:
- Prefix EVERY git command with GIT_NO_LAZY_FETCH=1. Never run git log -S/-G/-p/--follow without
  `-- <single file path>`; prefix slow searches with `timeout 90`.
- Run commands in the foreground; never use run_in_background, and leave nothing running when you finish. If a git
  command times out or reports a missing object, do not retry it.
- GitHub API budget: the REST limit (5,000/hour) is shared by all readers. Use at most about 15 `gh api` REST calls
  per fix, never page through commit lists, and prefer local git and GraphQL blame (separate budget). If gh reports
  "API rate limit exceeded", stop: do not write answers for ranks you have not finished, and list them in your final
  message.
- Full-history git dir (commit/tree listings only, as the brief explains): <FULLHIST>
- Never edit, fetch, check out, stash or build. Never name the shallow-graft commit b14a2cae4bf6 as a cause.

Let S=<S>. Read only the bundles named below under S, nothing else there.

(Second reader only:) Other readers' answers exist elsewhere in S; do not look for or read them, and do not read
research/fix-origins/cases.jsonl. Your judgment must be independent.

Classify these ranks, one after another: <r1>, <r2>, <r3>, <r4>, <r5>. For rank r, the evidence bundle is
S/evidence/<r zero-padded to 4 digits>.md, and you write the JSON answer, and nothing else, to S/reads/<r>.json.
Write only those files.

Spend effort proportionate to the fix: a clear not-a-defect needs little digging; a claimed regression needs the
causing diff read and quoted. End with one line per rank: rank, origin, short cause sha.
