# Severity of the 29 confirmed regressions

Companion to [report.md](report.md). It adds three measurements for the 29 "core" cases in [cases.md](cases.md):
what kind of failure each was, how long it sat on `main` before its fix, and whether a versioned release carried
the bug without the fix commit. Written 2026-11-25.

## Summary

| Kind of failure | Cases | Median days live | Reached a versioned release |
|---|---|---|---|
| Failed every time for some setup | 9 | 4.2 | 4 |
| Wrong behavior in a sequence or timing | 9 | 17.5 | 5 |
| Slower or heavier | 6 | 0.8 | 0 |
| Presentation | 3 | 0.2 | 0 |
| Wrong permissions | 2 | 1.0 | 0 or 1 (case 16 is doubtful, see Limits) |

- Days live, all 29: median 1.7; 12 under a day, 6 within a week, 7 within a month, 4 longer.
- 10 of 29 appear in at least one versioned release without the fix commit; 2 of those are in the `v2026.10.x` line.
- Performance and presentation regressions were fixed within about a day and did not reach a versioned release.
  The cases that stayed for weeks and shipped are failures tied to one provider, channel or runtime.

## Per case

| # | Cause -> fix | Kind | Days live | Versioned releases with the bug | What went wrong |
|---|---|---|---|---|---|
| 12 | #126542 -> #201638 | Wrong behavior in a sequence or timing | 90.9 | v2026.10.3 to v2026.11.10 (13) | A scheduled automation whose model first called a tool that does not exist, then recovered with the right tool and finished, was still recorded as failed with a "blocked" warning and triggered a repea |
| 20 | #162763 -> #198859 | Wrong behavior in a sequence or timing | 44.0 | v2026.10.3 to v2026.11.9 (12) | Opening a chat whose run was busily producing messages left it stuck on the loading placeholder forever; only a page reload opened it. |
| 8 | #170534 -> #203174 | Wrong behavior in a sequence or timing | 36.6 | v2026.11.5 to v2026.11.10 (6) | With Gemini 3, a reply meant to stay silent (exactly "NO_REPLY") was posted into the chat as the literal text "NO_REPLY", in direct chats and announced automations. |
| 9 | #174797 -> #202436 | Failed every time for some setup | 34.1 | v2026.11.5 to v2026.11.10 (6) | On OpenAI-compatible chat-completions providers (e.g. LiteLLM in front of Anthropic) with Tool Search directory mode, every turn that used web search failed because the follow-up request was rejected  |
| 7 | #185730 -> #203185 | Wrong behavior in a sequence or timing | 23.8 | v2026.11.5 to v2026.11.10 (6) | after updating OpenClaw while the Gateway kept running, the next Gateway stop failed to record which conversations were busy, so they were not resumed after restart. |
| 24 | #178764 -> #180603 | Failed every time for some setup | 22.1 | v2026.11.5 to v2026.11.9 (5) | Scheduled jobs and heartbeats on the main conversation could not send messages when that conversation was being used from a Telegram or WhatsApp direct message: on Telegram the run failed before the m |
| 35 | #164304 -> #192037 | Failed every time for some setup | 20.2 | v2026.11.5 to v2026.11.9 (5) | When someone in Discord or Slack asked the agent to start a new session, the agent was refused with a "requires current session write authority" error instead of creating it. |
| 19 | #185730 -> #199529 | Wrong behavior in a sequence or timing | 17.5 | v2026.11.5 to v2026.11.9 (5) | scheduled jobs that generated images were marked failed after a long stall and then retried delivering each image every 1-2 seconds until the Gateway restarted. |
| 34 | #172026 -> #191722 | Failed every time for some setup | 13.8 | v2026.11.5 to v2026.11.9 (5) | On Claude CLI turns, MCP servers that sign in per user (per-user OAuth or plugin resolvers) silently disappeared from the agent's tools, even for users who had connected their account. Nothing told th |
| 28 | #189847 -> #193930 | Slower or heavier | 8.3 | none | in Safari and other WebKit browsers, each visible spinner (for example running sessions in the sidebar) made the Control UI use noticeably more CPU/GPU on every frame, including while the page was oth |
| 30 | #189469 -> #194704 | Wrong behavior in a sequence or timing | 7.1 | none | an automation set to re-run when a command exits silently skipped its next run if the next exit arrived while the previous run was still finishing. |
| 27 | #177227 -> #196641 | Failed every time for some setup | 4.2 | none | Activity recaps (and other utility completions) failed every time with an HTTP 400 "temperature is not supported" error when the utility model rejects temperature and runs on the native Codex runtime. |
| 11 | #199706 -> #201917 | Failed every time for some setup | 2.3 | none | On a managed Git (dev-channel) install, agent turns that needed the OpenClaw MCP server failed before replying because Node refused to load bundled plugin TypeScript sources from a path under node_mod |
| 16 | #199512 -> #200396 | Wrong permissions | 1.8 | v2026.11.10 | After the change, automatic "repair" turns for a broken automation created from a chat quietly ran without the chat owner's permissions (and, in the same area, watchers created from a chat were switch |
| 33 | #188978 -> #190857 | Failed every time for some setup | 1.7 | none | Users updating from a 2026.6.x release to a build containing #188978 had the update fail at the plugin step with "Plugin cohort convergence requires its live outer update executor." |
| 18 | #196550 -> #199561 | Slower or heavier | 1.2 | none | Compacting a conversation that had not been loaded recently got slower (about 2.5 s vs 1.8 s) and used more total CPU after compaction moved into background worker tasks. |
| 36 | #197382 -> #197936 | Slower or heavier | 1.0 | none | Running `openclaw --help` started loading network encryption (TLS) code that it never uses, which made the lightweight help path heavier. No user report exists; an existing help import-guard test caug |
| 6 | #203118 -> #203455 | Wrong behavior in a sequence or timing | 0.7 | none | after approving a browser sign-in (e.g. OpenCode Go), the dialog went back to "Enter this code in your browser" for about 5 seconds, so it looked like sign-in failed. |
| 26 | #196468 -> #196751 | Presentation | 0.7 | none | a change meant to shrink one small "source update" row also changed text sizes and scaling across most of the Control UI and plugin views, so the interface's typography shifted far beyond what was ask |
| 29 | #197251 -> #197593 | Failed every time for some setup | 0.7 | none | preparing a workspace or PR worktree from a large shared Git clone with thousands of Git config entries failed with "spawn E2BIG" (process launch limit exceeded), so missing file contents could not be |
| 23 | #197445 -> #197833 | Slower or heavier | 0.6 | none | On Linux and Windows, every update left the previous ~640 MiB updater copy on disk, and `openclaw doctor --fix` could not clean them up while the Gateway was running, so disk use grew with each update |
| 17 | #197510 -> #199907 | Wrong behavior in a sequence or timing | 0.5 | none | Looking up a session could fail with "SQLite database path identity changed" when the agent's first database happened to be created while the lookup was running. |
| 21 | #198288 -> #198582 | Failed every time for some setup | 0.4 | none | With a LiteLLM proxy, the proxy's chat models disappeared from model lists and chatting with one was refused with "This model doesn't support chat; pick another model." |
| 32 | #190367 -> #191157 | Presentation | 0.2 | none | In the native app windows at phone width, the Sessions page lost its only visible title, because the page hid its big title on the assumption that a web-only floating header would show it instead. |
| 40 | #202608 -> #202765 | Slower or heavier | 0.2 | none | After the change, every live state read in the Gateway re-checked database ownership on disk (path resolution plus reading the owner file) synchronously, adding avoidable filesystem work to request pa |
| 1 | #196065 -> #200159 | Slower or heavier | 0.1 | none | Opening a chat made the Gateway re-read the whole conversation history each time, so on large conversations new messages and restarts froze for about a minute at a time. |
| 4 | #203487 -> #203551 | Wrong behavior in a sequence or timing | 0.1 | none | pressing Stop on a Claude CLI (or other CLI-backed) turn no longer cancelled a message action already in progress, so it still posted. |
| 5 | #203466 -> #203479 | Wrong permissions | 0.1 | none | after a Gateway restart, a parent chat woken to receive a helper agent's result could run with less access than the person who started it (losing admin). |
| 31 | #194234 -> #194497 | Presentation | 0.1 | none | backing up a corrupt database showed a low-level worker error instead of the clear "database is corrupt" diagnostic, and skipped the usual cleanup. |

## How this was measured

- **Kind of failure:** one reader's grouping of the "What went wrong" line in `cases.md`. Not verified against
  the code. Cases 18, 31 and 36 are marginal and a stricter reader could set them aside.
- **Days live:** commit time of the fix minus commit time of the causing change, both on `upstream/main`, using
  the pinned commits in `cases.md`.
- **Versioned releases:** stable tags `v2026.10.3`, `v2026.10.33`, `v2026.10.34` and `v2026.11.1` to `v2026.11.10`
  (beta and rc tags left out). A release is listed when the causing commit is an ancestor of the tag and the fix
  commit is not. Tag dates: `v2026.10.33` 2026-11-17, `v2026.10.34` 2026-11-25, `v2026.11.1` 2026-11-04,
  `v2026.11.5` 2026-11-17, `v2026.11.10` 2026-11-24.

## Limits

- If a fix was copied onto a release branch as a separate commit, the ancestor check misses it, so the release
  lists can be too long. Case 16 is the clearest suspect: only `v2026.11.10` lists it, eight days after its fix.
- Releases before `v2026.10.33` other than `v2026.10.3` were not checked, so older exposure of cases 12 and 20 is
  not counted.
- "Reached a release" does not show that any user hit the bug.
- The 29 are regressions that a fix explicitly blamed on an earlier change. They are not all bugs from the period.
