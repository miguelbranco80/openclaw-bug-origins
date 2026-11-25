# Candidate ledger for the detection check

Every commit the searches returned, with the keep/drop decision and its reason. Commit links point to
`openclaw/openclaw`. The search commands and inclusion rule are in [report.md](report.md#how-the-sample-was-built).

Counts: pass 1 (four `git log --grep` searches) returned 143 commits; pass 2 (body-line scan) returned 284;
the union is 355 (72 in both). One pair was added by hand because no search finds it (#200967 -> #201563).

- 52 dropped automatically: 32 by subject prefix (not a fix or revert), 20 by CI/test/docs/release scope.
- 205 dropped because no body line matches the attribution pattern (see report.md). Their PR or commit references
  are credit, ordering, evidence SHAs, CI runs, or design context. I skimmed their matching lines; the 5 kept
  commits listed below as "worded differently" came from that skim. Listed at the end.
- 98 read by hand (93 that match the attribution pattern, plus 5 whose attribution is worded differently and was
  found while reading the pass 1 and pass 2 output), plus 1 forced pair: 41 kept, 58 dropped with the reason shown.

## Read by hand

| Commit | Date | Subject | Decision | Reason |
|---|---|---|---|---|
| [8ef2c737ce](https://github.com/openclaw/openclaw/commit/8ef2c737ce) | 2026-11-01 | fix(models): keep v3 catalog rows when newer publishers add fields (#190187) | **drop** | latent hazard in #189678 (reader would reject future fields); no failure observed |
| [88177be90a](https://github.com/openclaw/openclaw/commit/88177be90a) | 2026-11-01 | fix(update): let run-less 2026.6 updaters finish plugin convergence (#190857) | **keep** | #188978 made post-core convergence require a fence and broke 2026.6 updaters |
| [dc66ed00e3](https://github.com/openclaw/openclaw/commit/dc66ed00e3) | 2026-11-01 | fix(agents): avoid empty tool schema settlement (#190664) | **keep** | product cleanup-contract defect from #190627 (seen first as a main CI failure) |
| [161f76d795](https://github.com/openclaw/openclaw/commit/161f76d795) | 2026-11-02 | fix: reduce filesystem stalls during chat turn preparation (#191075) | **drop** | test fixture repair |
| [428b02da8f](https://github.com/openclaw/openclaw/commit/428b02da8f) | 2026-11-02 | fix(ui): restore phone session-filter browser checks (#191279) | **drop** | browser test selector repair |
| [13be296758](https://github.com/openclaw/openclaw/commit/13be296758) | 2026-11-02 | fix(ui): keep the Sessions heading visible in native phone layouts (#191157) | **keep** | phone clipping rule introduced in #190367 hid the Sessions title |
| [c8518acbb2](https://github.com/openclaw/openclaw/commit/c8518acbb2) | 2026-11-03 | fix(talk): voice-only relay Talk sessions stay untitled after the user speaks (#191532) | **drop** | relay path never had the feature #190613 added; not a regression |
| [9a0a5e6bb2](https://github.com/openclaw/openclaw/commit/9a0a5e6bb2) | 2026-11-03 | fix(sqlite): report reader work and bound workspace sweep allocation (#191779) | **drop** | reference is test-budget context, no attribution |
| [31ad71a8ad](https://github.com/openclaw/openclaw/commit/31ad71a8ad) | 2026-11-03 | fix(claude-cli): per-requester MCP servers missing from Claude CLI turns (#191722) | **keep** | since #172026 per-requester MCP servers missing from Claude CLI turns |
| [3475ab3edf](https://github.com/openclaw/openclaw/commit/3475ab3edf) | 2026-11-03 | fix(worktrees): avoid slow snapshots of installed dependencies (#192452) | **drop** | dead-export CI noise from #191589 |
| [1835c9cad1](https://github.com/openclaw/openclaw/commit/1835c9cad1) | 2026-11-04 | fix(ui): restore static checks after copy updates (#192824) | **drop** | static-check (lint/dead copy) repair |
| [4a43644e7a](https://github.com/openclaw/openclaw/commit/4a43644e7a) | 2026-11-04 | fix: stop line-limit checks from blocking release branches (#192806) | **drop** | release line-limit tooling; quoted line is static-check repair |
| [17b6ad4114](https://github.com/openclaw/openclaw/commit/17b6ad4114) | 2026-11-04 | fix(codex): forward-port 2026.10.10 thread ownership and cleanup fixes (#191830) | **drop** | forward-port of release-branch fixes; no single introducing PR |
| [1db1416320](https://github.com/openclaw/openclaw/commit/1db1416320) | 2026-11-04 | fix: bound memory retained by conversation and workspace diagnostics (#192944) | **drop** | reference is test-budget context, no attribution |
| [ae420c5040](https://github.com/openclaw/openclaw/commit/ae420c5040) | 2026-11-04 | fix(matrix): forward-port 2026.10.10 startup and shutdown fixes (#192385) | **drop** | forward-port of release-branch fixes; "since #N" is design context |
| [dbf42da14e](https://github.com/openclaw/openclaw/commit/dbf42da14e) | 2026-11-04 | fix(agents): let channels create sessions with spawn authority (#192037) | **keep** | every channel request to start a session was refused after #164304 |
| [ba33925801](https://github.com/openclaw/openclaw/commit/ba33925801) | 2026-11-06 | fix(update): update and Doctor still copy the state database for most reads (#194267) | **drop** | reverts a commit inside its own PR branch |
| [d041ef81ab](https://github.com/openclaw/openclaw/commit/d041ef81ab) | 2026-11-06 | fix(gateway): break Control UI static/root import cycle (#194496) | **drop** | import cycle caught by static check; no product effect stated |
| [cba7c0ec2e](https://github.com/openclaw/openclaw/commit/cba7c0ec2e) | 2026-11-06 | fix(backup): preserve SQLite corruption diagnostics (#194497) | **keep** | "Regressed in 691bc8dbe001 (#194234)" |
| [83e68fa72b](https://github.com/openclaw/openclaw/commit/83e68fa72b) | 2026-11-07 | fix(ui): wait for quota metrics in account identity e2e (#194258) | **drop** | e2e test wait repair |
| [32f14c9b8d](https://github.com/openclaw/openclaw/commit/32f14c9b8d) | 2026-11-07 | fix(cron): align lifecycle tests with controller retirement (#195026) | **drop** | test alignment |
| [fc9749fb1e](https://github.com/openclaw/openclaw/commit/fc9749fb1e) | 2026-11-07 | fix: restore main dead-export checks (#194800) | **drop** | Knip dead-export CI repair |
| [75694cca18](https://github.com/openclaw/openclaw/commit/75694cca18) | 2026-11-07 | fix(deps): roll back fs-safe 0.28 integration regressions (#194589) | **keep** | "#194560 introduced failures" (dependency bump rollback; user impact checked in case) |
| [450d4af755](https://github.com/openclaw/openclaw/commit/450d4af755) | 2026-11-07 | fix(cron): wait for prior receipts before admitting rearmed exits (#194704) | **keep** | "Regression introduced by 7caee827c5be (#189469)" |
| [6da6f5cb44](https://github.com/openclaw/openclaw/commit/6da6f5cb44) | 2026-11-08 | fix(skills): package sources with normalized timestamps (#194700) | **drop** | "broke" refers to branch history, not product |
| [2e0e3c5ed2](https://github.com/openclaw/openclaw/commit/2e0e3c5ed2) | 2026-11-08 | fix(cli): cancel interrupted tts gateway RPCs (#195206) | **drop** | no introducing PR named |
| [b9a2a9b5b7](https://github.com/openclaw/openclaw/commit/b9a2a9b5b7) | 2026-11-08 | fix(ui): align composer menu focus check with attachment order (#195262) | **drop** | test expectation alignment |
| [3001551e27](https://github.com/openclaw/openclaw/commit/3001551e27) | 2026-11-09 | fix(active-memory): expire recall circuit breaker on elapsed time (#195472) | **drop** | no introducing PR named |
| [585ba3815e](https://github.com/openclaw/openclaw/commit/585ba3815e) | 2026-11-09 | fix(gateway): serve startup reads while sessions resume (#195987) | **drop** | test fixture repair |
| [aedc6d29da](https://github.com/openclaw/openclaw/commit/aedc6d29da) | 2026-11-09 | fix(ui): stop spinners from keeping WebKit busy every frame (#193930) | **keep** | since #189847 spinners keep WebKit busy |
| [6c1c19fe32](https://github.com/openclaw/openclaw/commit/6c1c19fe32) | 2026-11-09 | fix(sessions): preserve retained history through provider replay hooks (#196023) | **drop** | no introducing PR named |
| [f001243c25](https://github.com/openclaw/openclaw/commit/f001243c25) | 2026-11-09 | fix(skills): send Whisper model and language fields literally (#196049) | **drop** | no introducing PR named |
| [5fd794e2b7](https://github.com/openclaw/openclaw/commit/5fd794e2b7) | 2026-11-09 | fix: accepted preparing turns disappear across Gateway restarts (#195773) | **drop** | named introduction (#194364) is a release CI attribution gate failure |
| [8fe570151a](https://github.com/openclaw/openclaw/commit/8fe570151a) | 2026-11-10 | fix(agents): omit temperature on native isolated completions for models that reject it (#1 | **keep** | since #177227 isolated completions send temperature that models reject |
| [4ec97ef5e7](https://github.com/openclaw/openclaw/commit/4ec97ef5e7) | 2026-11-10 | fix(gateway): automatic Activity recaps fail after Codex runs with a closed plugin scope ( | **drop** | no introducing PR named |
| [3ef64ea5c8](https://github.com/openclaw/openclaw/commit/3ef64ea5c8) | 2026-11-11 | Revert "fix(agents): keep session forks on the parent's cached prompt prefix (#197074)" (# | **keep** | plain revert of #197074 (reason checked in case) |
| [e212edede2](https://github.com/openclaw/openclaw/commit/e212edede2) | 2026-11-11 | fix(gateway): restore missing-admission refusal and update 3 gateway tests broken on main  | **keep** | #196337 dropped the missing-admission refusal |
| [6d71e65086](https://github.com/openclaw/openclaw/commit/6d71e65086) | 2026-11-11 | fix(sessions): keep transcript workers outside Doctor repair imports (#197153) | **drop** | import-graph boundary repair; no product effect stated |
| [6f6bf91812](https://github.com/openclaw/openclaw/commit/6f6bf91812) | 2026-11-11 | fix(worktrees): avoid E2BIG during isolated Git hydration (#197593) | **keep** | #197251 routed hydration through the env transport -> E2BIG |
| [c37e3897be](https://github.com/openclaw/openclaw/commit/c37e3897be) | 2026-11-11 | fix(ui): restore prior typography and keep source updates compact (#196751) | **keep** | reverts typography changes from #196468 |
| [0ac0df32c1](https://github.com/openclaw/openclaw/commit/0ac0df32c1) | 2026-11-12 | fix: keep usage pricing from blocking the Gateway on filesystem lookups (#197599) | **drop** | references are test/benchmark fixtures |
| [d30e45c3f4](https://github.com/openclaw/openclaw/commit/d30e45c3f4) | 2026-11-12 | fix(cli): restore lightweight help and cleanup test startup (#197936) | **keep** | TLS initialization introduced by #197382 in the help path |
| [d6e445fa8c](https://github.com/openclaw/openclaw/commit/d6e445fa8c) | 2026-11-12 | fix(knowledge): page prose and claims render too light on macOS (#197479) | **drop** | "since #196767" is test-fixture context |
| [fb83d658cf](https://github.com/openclaw/openclaw/commit/fb83d658cf) | 2026-11-12 | fix: reduce transcript allocation when preparing native context seeds | **drop** | references are design context |
| [4f96534013](https://github.com/openclaw/openclaw/commit/4f96534013) | 2026-11-12 | fix: main-session automations fail before the model call when the main session is used fro | **keep** | since #178764 main-session automations fail before the model call |
| [b6468ddec2](https://github.com/openclaw/openclaw/commit/b6468ddec2) | 2026-11-12 | fix(update): reclaim retained runtimes while the Gateway watches directories (#197833) | **keep** | since #197445 retained runtimes not reclaimed |
| [3e7fb1bfca](https://github.com/openclaw/openclaw/commit/3e7fb1bfca) | 2026-11-12 | fix(memory): rebuild never finishes on large indexes after updating (#196378) | **drop** | no introducing PR named |
| [5d2c85196f](https://github.com/openclaw/openclaw/commit/5d2c85196f) | 2026-11-12 | fix(gateway): surface refused service management on preserved-definition restart (#197420) | **drop** | no introducing PR named |
| [50798df4c6](https://github.com/openclaw/openclaw/commit/50798df4c6) | 2026-11-13 | fix(compaction): /compact fails for sandboxed Claude CLI sessions with a selected skill (# | **drop** | no introducing PR named |
| [9ffa0502cc](https://github.com/openclaw/openclaw/commit/9ffa0502cc) | 2026-11-13 | fix(browser): Browser panel lags behind typing and the live view stutters (#197927) | **drop** | reverts an in-branch commit; says the bug also exists on main |
| [6dbf7e37b6](https://github.com/openclaw/openclaw/commit/6dbf7e37b6) | 2026-11-13 | fix(telegram): large media sends time out after 30 seconds (#151923) | **keep** | timeout default since 783a5d21cfc (#111382) |
| [a02a1e02f5](https://github.com/openclaw/openclaw/commit/a02a1e02f5) | 2026-11-14 | fix(cli): surface message option-guard remedies in --json failures (#198861) | **drop** | no introducing PR named |
| [007bf728bb](https://github.com/openclaw/openclaw/commit/007bf728bb) | 2026-11-14 | fix(ui): busy chats never finish loading when opened during an active run (#198859) | **keep** | since #162763 busy chats never finish loading |
| [07e049f8d4](https://github.com/openclaw/openclaw/commit/07e049f8d4) | 2026-11-14 | fix(auto-reply): keep emoji whole in group thread caps (#193562) | **drop** | no introducing PR named |
| [48cdab36dd](https://github.com/openclaw/openclaw/commit/48cdab36dd) | 2026-11-14 | fix(litellm): LiteLLM proxy chat models are hidden from model lists and refused as not cha | **keep** | since #198288 LiteLLM chat models hidden |
| [4f20ee5c39](https://github.com/openclaw/openclaw/commit/4f20ee5c39) | 2026-11-14 | fix(cli): surface the capability inspect remedy in --json failures (#198662) | **drop** | no introducing PR named |
| [ad09e3821a](https://github.com/openclaw/openclaw/commit/ad09e3821a) | 2026-11-15 | fix: load earlier chat messages when upward input interrupts Latest (#199890) | **drop** | PR says relation to #171009 is unreproduced |
| [e6265d6f2a](https://github.com/openclaw/openclaw/commit/e6265d6f2a) | 2026-11-15 | fix(cron): cron runs that generate images stall and retry their completion forever (#19952 | **keep** | #185730 removed the only caller of the admission flag |
| [adf70ab2ec](https://github.com/openclaw/openclaw/commit/adf70ab2ec) | 2026-11-15 | fix(a2a): inbound correlation test fails intermittently on unrelated PRs (#199882) | **drop** | flaky test |
| [a4cc2adb5d](https://github.com/openclaw/openclaw/commit/a4cc2adb5d) | 2026-11-15 | fix: undo cold-session compaction CPU and latency regressions (#199561) | **keep** | reverts #196550 for CPU/latency regressions |
| [237111eabf](https://github.com/openclaw/openclaw/commit/237111eabf) | 2026-11-15 | fix(exec): keep processes the agent detaches, tracked and bounded (#199079) | **drop** | "#150750 made the killing deliberate" is design history |
| [52fd3d8029](https://github.com/openclaw/openclaw/commit/52fd3d8029) | 2026-11-15 | fix(nodes): cancel interrupted camera list and location reads (#199388) | **drop** | no introducing PR named |
| [af43a14a49](https://github.com/openclaw/openclaw/commit/af43a14a49) | 2026-11-15 | fix: session lookup rejects a database created during discovery (#199907) | **keep** | "fails with the worker conversion from #197510" |
| [4bce7604f0](https://github.com/openclaw/openclaw/commit/4bce7604f0) | 2026-11-16 | revert: skills-used full-transcript scan on every chat history page (#200159) | **keep** | reverts #196065 (forced inclusion; also found by search) |
| [df78722789](https://github.com/openclaw/openclaw/commit/df78722789) | 2026-11-16 | fix(gateway): prevent readiness probes from freezing the main thread (#200370) | **drop** | CI wrapper-closure repair |
| [24385a2042](https://github.com/openclaw/openclaw/commit/24385a2042) | 2026-11-16 | fix(ui): continue self-woken work in the turn that started it (#200056) | **drop** | no introducing PR named |
| [4940240568](https://github.com/openclaw/openclaw/commit/4940240568) | 2026-11-16 | fix(cli): nodes push test still expects silent JSON-mode failures (#200199) | **drop** | test expectation repair |
| [30e9d3ee29](https://github.com/openclaw/openclaw/commit/30e9d3ee29) | 2026-11-16 | fix(agents): explain when a listed model rejects a chat request (#200073) | **keep** | #199998 made listed models runnable; non-chat ones now fail with a misleading message |
| [5962eee2fc](https://github.com/openclaw/openclaw/commit/5962eee2fc) | 2026-11-16 | fix: recover saved Responses state and completion delivery after restart (#200020) | **drop** | reference is CI dead-export context |
| [f360b837c2](https://github.com/openclaw/openclaw/commit/f360b837c2) | 2026-11-16 | fix(models): guessed non-chat models leave the default picker instead of being refused (#2 | **drop** | #199998 kept a pre-existing refusal rule; not introduced by it |
| [22d5c8735a](https://github.com/openclaw/openclaw/commit/22d5c8735a) | 2026-11-17 | fix: resource broker startup fails when parent and child disagree on the socket directory  | **keep** | since #200216 broker startup fails |
| [346d231275](https://github.com/openclaw/openclaw/commit/346d231275) | 2026-11-17 | fix(cron): keep automations running when their chat's id changes (#200396) | **keep** | since #199512 repair turns silently downgraded |
| [7cb238ad89](https://github.com/openclaw/openclaw/commit/7cb238ad89) | 2026-11-17 | fix(ai): keep provider checkpoints across model switches (#200208) | **drop** | "after #200063" is ordering; dropped checkpoints pre-existed |
| [e9e1bd0ea0](https://github.com/openclaw/openclaw/commit/e9e1bd0ea0) | 2026-11-17 | fix: shorten sandbox pauses when retrying PR refreshes (#200902) | **drop** | test observer repair |
| [52e80792e0](https://github.com/openclaw/openclaw/commit/52e80792e0) | 2026-11-18 | fix(codex): attach a request over the turn cap instead of losing its middle (#200735) | **keep** | since #200690 oversized requests lose their middle |
| [00d105d9fa](https://github.com/openclaw/openclaw/commit/00d105d9fa) | 2026-11-18 | Revert "fix(openai): show newer subscription models in the picker" (#200870) | **keep** | reverts #200811 |
| [b15c658270](https://github.com/openclaw/openclaw/commit/b15c658270) | 2026-11-18 | fix: finish A2A tasks for messages sent while the agent is still answering (#200846) | **drop** | #183803 named as related behavior, not as the cause |
| [f5958f4049](https://github.com/openclaw/openclaw/commit/f5958f4049) | 2026-11-19 | fix(agents): scheduled runs that recover from calling a missing tool are recorded failed ( | **keep** | since #126542 slot clears only on the same tool name |
| [724de78fa4](https://github.com/openclaw/openclaw/commit/724de78fa4) | 2026-11-19 | revert: remove temporary beta publication exception and repair after closeout (#201805) | **drop** | release tooling |
| [2ef6f7bade](https://github.com/openclaw/openclaw/commit/2ef6f7bade) | 2026-11-19 | fix(update): build and serve Git releases outside node_modules (#201917) | **keep** | dev-channel installs since #199706 (layout regression) |
| [97d10e0bb9](https://github.com/openclaw/openclaw/commit/97d10e0bb9) | 2026-11-19 | fix: show the right agent and live activity when adding a template | **drop** | reverts a commit inside its own PR branch |
| [5724f95182](https://github.com/openclaw/openclaw/commit/5724f95182) | 2026-11-19 | fix: keep one child completion failure from dropping sibling results (#201563) | **keep** | forced inclusion (#200967 -> #201563); not found by any search |
| [4332e9aa16](https://github.com/openclaw/openclaw/commit/4332e9aa16) | 2026-11-20 | fix(models): apply a changed catalog source at once without breaking turns (#202583) | **drop** | reverted part of an earlier attempt inside the same work; no merged introducing PR |
| [b3afb5b589](https://github.com/openclaw/openclaw/commit/b3afb5b589) | 2026-11-20 | fix(agents): drop the deleted revalidateOnCompletion option from users.setRole (#202449) | **drop** | typecheck failure on main (CI) |
| [e44a7e3681](https://github.com/openclaw/openclaw/commit/e44a7e3681) | 2026-11-20 | fix(ui): retain the reader position through history measurements (#200482) | **drop** | test regression port |
| [2d7934abf9](https://github.com/openclaw/openclaw/commit/2d7934abf9) | 2026-11-20 | fix: keep web_search via Tool Search working on chat-completions providers that reject ass | **keep** | #174797 replays missing tools as text; breaks strict providers |
| [9175df9c3f](https://github.com/openclaw/openclaw/commit/9175df9c3f) | 2026-11-20 | fix: reuse admitted live owner custody for state reads (#202765) | **keep** | "fixes the host identity-read regression from #202608" |
| [e4c17c5dd4](https://github.com/openclaw/openclaw/commit/e4c17c5dd4) | 2026-11-20 | fix(openai): send the numeric OpenClaw release as the ChatGPT version header (#202427) | **keep** | since #202380 listing/turn version mismatch |
| [fcfb114087](https://github.com/openclaw/openclaw/commit/fcfb114087) | 2026-11-21 | fix: keep Gemini NO_REPLY replies silent when the signature arrives on its own part (#2031 | **keep** | since #170534 empty signed blocks picked as the answer |
| [d31a94354b](https://github.com/openclaw/openclaw/commit/d31a94354b) | 2026-11-21 | revert(agents): drop the bounded-mode branch for CLIs with native tools (#202957) | **drop** | design reversal of #202945; no user-visible failure |
| [061fd34ccc](https://github.com/openclaw/openclaw/commit/061fd34ccc) | 2026-11-21 | fix: interrupted sessions still resume after a running Gateway's package is replaced in pl | **keep** | since #185730 restart markers lost after in-place package replacement |
| [c8a643b625](https://github.com/openclaw/openclaw/commit/c8a643b625) | 2026-11-22 | fix(models): stop showing the device code after browser sign-in is approved (#203455) | **keep** | #203118 added steps that keep showing the device code |
| [75886fc2a7](https://github.com/openclaw/openclaw/commit/75886fc2a7) | 2026-11-22 | fix: keep a provider sign-in when you leave the Control UI tab (#203478) | **drop** | fix says the bug predates the suspected PR; two older PRs named |
| [38ea444a46](https://github.com/openclaw/openclaw/commit/38ea444a46) | 2026-11-22 | fix: restore the previous macOS Dashboard spacing (#203651) | **keep** | reverts #203284 |
| [1a0a24dcd2](https://github.com/openclaw/openclaw/commit/1a0a24dcd2) | 2026-11-22 | fix: restore Stop for MCP loopback tool calls after turn abort (#203551) | **keep** | since #203487 Stop does not cancel MCP loopback calls |
| [450441b904](https://github.com/openclaw/openclaw/commit/450441b904) | 2026-11-22 | fix: give a subagent result's restart wake the requester's original access (#203479) | **keep** | since #203466 restart wake gets wrong access |
| [b949a1cb4d](https://github.com/openclaw/openclaw/commit/b949a1cb4d) | 2026-11-22 | fix(cli): validate the loaded agent roster in fast config checks (#203520) | **drop** | "since #112678" is supported-shape context |
| [ae8155cf5f](https://github.com/openclaw/openclaw/commit/ae8155cf5f) | 2026-11-22 | fix: stop refusing chat reads before the main session exists (#203126) | **drop** | "since #175041" is feature context, not attributed as cause |
| [20964c92c3](https://github.com/openclaw/openclaw/commit/20964c92c3) | 2026-11-23 | fix: keep a steered document's text in later runs (#203627) | **drop** | no introducing PR named |

## Dropped automatically

### not a fix/revert commit (subject prefix) (32)

- [72ba78c0b9](https://github.com/openclaw/openclaw/commit/72ba78c0b9) 2026-11-01 test: advance startup fixtures to their scheduled retry (#190193)
- [2426aa9288](https://github.com/openclaw/openclaw/commit/2426aa9288) 2026-11-02 test(cli): assert typed numeric input failures
- [f6efdcb8ea](https://github.com/openclaw/openclaw/commit/f6efdcb8ea) 2026-11-02 test(gateway): establish trajectory fixture eviction target
- [67ebdd19ff](https://github.com/openclaw/openclaw/commit/67ebdd19ff) 2026-11-04 test(ui): align native embed settings coverage
- [d595644b4c](https://github.com/openclaw/openclaw/commit/d595644b4c) 2026-11-04 refactor(workboard): keep run settlement helper private
- [b7ae6dd4f1](https://github.com/openclaw/openclaw/commit/b7ae6dd4f1) 2026-11-05 test(macos): align new-session assertions with chat inheritance
- [3f4ce86421](https://github.com/openclaw/openclaw/commit/3f4ce86421) 2026-11-05 test(ollama): align MiniMax cloud output cap expectations
- [a956ef1714](https://github.com/openclaw/openclaw/commit/a956ef1714) 2026-11-05 feat(chat): send pending steers now without stopping the run (#193665)
- [34e607682b](https://github.com/openclaw/openclaw/commit/34e607682b) 2026-11-05 improve(ui): open large completed chat runs faster (#183800)
- [80cee51a04](https://github.com/openclaw/openclaw/commit/80cee51a04) 2026-11-05 test(update): expect empty-reader receipt reuse
- [b7ce1c3fde](https://github.com/openclaw/openclaw/commit/b7ce1c3fde) 2026-11-05 test(windows): keep ordinary CLI coverage in one partition
- [94ba8aef40](https://github.com/openclaw/openclaw/commit/94ba8aef40) 2026-11-06 feat(codex): use OpenClaw's base prompt for ordinary threads (#191344)
- [f8b1a6ba3d](https://github.com/openclaw/openclaw/commit/f8b1a6ba3d) 2026-11-07 test(ui): track current composer alert in corner fixture
- [3fa60aed34](https://github.com/openclaw/openclaw/commit/3fa60aed34) 2026-11-08 test: call run failure notice reader with one argument
- [9348ceac34](https://github.com/openclaw/openclaw/commit/9348ceac34) 2026-11-10 test(ui): restore Agent Tools loading skeleton coverage (#197063)
- [0182580ebf](https://github.com/openclaw/openclaw/commit/0182580ebf) 2026-11-12 feat(google): support Gemini Decision models (#197501)
- [b703089e00](https://github.com/openclaw/openclaw/commit/b703089e00) 2026-11-13 improve: frame public shared conversations like chat (#197942)
- [2946c67bae](https://github.com/openclaw/openclaw/commit/2946c67bae) 2026-11-14 test(worktrees): recreate the retention symlink parent
- [d13336516b](https://github.com/openclaw/openclaw/commit/d13336516b) 2026-11-14 test(update): create source roots for dry-run previews
- [9bbc89ccdb](https://github.com/openclaw/openclaw/commit/9bbc89ccdb) 2026-11-14 chore(workboard): stop exporting MAX_COMPLETION_CLAIMS (#198672)
- [e712102a15](https://github.com/openclaw/openclaw/commit/e712102a15) 2026-11-14 test(agents): assert typed unsupported-chat rejections
- [a519dcfe9f](https://github.com/openclaw/openclaw/commit/a519dcfe9f) 2026-11-15 feat(ui): show what an idle chat is waiting on (#198891)
- [e345d2240d](https://github.com/openclaw/openclaw/commit/e345d2240d) 2026-11-15 test(sessions): align storage failure footer with app naming (#199408)
- [32abe7e815](https://github.com/openclaw/openclaw/commit/32abe7e815) 2026-11-15 chore(ci): cover the compaction subprocess entry in deadcode tests (#199062)
- [bdbf30094e](https://github.com/openclaw/openclaw/commit/bdbf30094e) 2026-11-16 test(memory): track shadow descriptors opened by async admission
- [d275ff6cc8](https://github.com/openclaw/openclaw/commit/d275ff6cc8) 2026-11-16 improve(talk): live transcription uses a saved Deepgram, ElevenLabs or Mistral API key (#199858)
- [6747b1ec5a](https://github.com/openclaw/openclaw/commit/6747b1ec5a) 2026-11-17 feat(update): run Git checkout installs from releases behind the release link (#199706)
- [17e19bf0bd](https://github.com/openclaw/openclaw/commit/17e19bf0bd) 2026-11-18 test(gateway): assert the restart marker production writes after #200533 (#201590)
- [e62a1a37a6](https://github.com/openclaw/openclaw/commit/e62a1a37a6) 2026-11-19 docs(releases): repair 11.5 heading structure (#202249)
- [eb56951a4c](https://github.com/openclaw/openclaw/commit/eb56951a4c) 2026-11-20 feat: only link file paths that open in chat (#202534)
- [112ba9e931](https://github.com/openclaw/openclaw/commit/112ba9e931) 2026-11-21 test: expose native scheduler recovery progress on failure (#203104)
- [ef7ed49555](https://github.com/openclaw/openclaw/commit/ef7ed49555) 2026-11-22 refactor: drop tool-caller re-checks from Gateway-side callers (#203503)

### CI/test/docs/release-tooling scope (20)

- [bf35e054b0](https://github.com/openclaw/openclaw/commit/bf35e054b0) 2026-11-03 fix(test): align Ollama transport guards with provider trust
- [a4d7594944](https://github.com/openclaw/openclaw/commit/a4d7594944) 2026-11-03 fix(ci): reconcile exact test budget and restore browser fixtures (#192026)
- [12f0ae45a5](https://github.com/openclaw/openclaw/commit/12f0ae45a5) 2026-11-03 fix(ci): recognize embedding creation type bridges
- [642693ad3a](https://github.com/openclaw/openclaw/commit/642693ad3a) 2026-11-05 fix(test): align scheduled child tools with retained admin authority (#193683)
- [d02defd90c](https://github.com/openclaw/openclaw/commit/d02defd90c) 2026-11-07 fix(ci): clear inherited test budget and unused export failures (#194509)
- [837f871caf](https://github.com/openclaw/openclaw/commit/837f871caf) 2026-11-07 fix(ci): keep event load progress type private (#195081)
- [6e5d5f518d](https://github.com/openclaw/openclaw/commit/6e5d5f518d) 2026-11-07 fix(ci): restore Control UI export analysis (#194917)
- [3264f92caf](https://github.com/openclaw/openclaw/commit/3264f92caf) 2026-11-07 fix(test): expect interrupted update canary progress (#194743)
- [3ea9d63c30](https://github.com/openclaw/openclaw/commit/3ea9d63c30) 2026-11-11 fix(test): worker containment checks expect retired recovery guidance (#197082)
- [16ab400340](https://github.com/openclaw/openclaw/commit/16ab400340) 2026-11-11 fix(test): Telegram loopback rejects compact answered results (#197068)
- [477e17a77c](https://github.com/openclaw/openclaw/commit/477e17a77c) 2026-11-12 fix(test): supply renamed startup diagnostics to standalone metadata fixture (#197756)
- [0a442391ee](https://github.com/openclaw/openclaw/commit/0a442391ee) 2026-11-13 fix(test): agent artifact fixture uses the retired worker creation API (#197985)
- [10da34f98d](https://github.com/openclaw/openclaw/commit/10da34f98d) 2026-11-13 fix(ci): include PostgreSQL Gateway ownership conformance (#198325)
- [9161e20e2c](https://github.com/openclaw/openclaw/commit/9161e20e2c) 2026-11-14 fix(ci): keep test-only member role presets out of production exports (#198863)
- [8978cbba03](https://github.com/openclaw/openclaw/commit/8978cbba03) 2026-11-14 fix(ci): unused exports fail the dependency check (#198510)
- [5c1a6f06de](https://github.com/openclaw/openclaw/commit/5c1a6f06de) 2026-11-14 fix(ci): retain worker delivery reporter in wrapper closure (#199053)
- [d9a6928692](https://github.com/openclaw/openclaw/commit/d9a6928692) 2026-11-14 fix(ci): remove unused exec helper exports (#199511)
- [ba92f3086c](https://github.com/openclaw/openclaw/commit/ba92f3086c) 2026-11-16 fix(ci): restore live audit consumers and readiness fixtures (#200133)
- [ae6b903359](https://github.com/openclaw/openclaw/commit/ae6b903359) 2026-11-17 fix(e2e): run update repair before the next update in the installed-recovery lane (#200776)
- [703cd16725](https://github.com/openclaw/openclaw/commit/703cd16725) 2026-11-19 fix(test): retain admitted GitHub receipts after membership changes (#201749)

### No attributing line (205)

- [33e7baf17c](https://github.com/openclaw/openclaw/commit/33e7baf17c) 2026-11-01 fix(sessions): bound active accounting without blocking writers (#190182)
- [0596cfc982](https://github.com/openclaw/openclaw/commit/0596cfc982) 2026-11-01 fix(agents): explain local model fallback stops (#190377)
- [29526f1319](https://github.com/openclaw/openclaw/commit/29526f1319) 2026-11-01 fix(infra): round relative ages from elapsed milliseconds (#190200)
- [b9aa487b3a](https://github.com/openclaw/openclaw/commit/b9aa487b3a) 2026-11-01 fix(ui): keep failed-run detail truncation surrogate-safe (#190288)
- [ed052ccb06](https://github.com/openclaw/openclaw/commit/ed052ccb06) 2026-11-01 fix(update-repair): preserve repair budgets across wall-clock changes (#190298)
- [e33046421b](https://github.com/openclaw/openclaw/commit/e33046421b) 2026-11-01 fix(workers): keep retention schemas private (#190506)
- [8c292ddb1b](https://github.com/openclaw/openclaw/commit/8c292ddb1b) 2026-11-02 fix: bound transcript lists when meetings are inaccessible (#190667)
- [2dd3ffec00](https://github.com/openclaw/openclaw/commit/2dd3ffec00) 2026-11-02 fix(agents): reject FIFO native-hook credentials without blocking (#191423)
- [6434b62cbd](https://github.com/openclaw/openclaw/commit/6434b62cbd) 2026-11-02 fix: await Doctor session and shared-auth inspection (#190870)
- [a9c6e2b077](https://github.com/openclaw/openclaw/commit/a9c6e2b077) 2026-11-02 fix(doctor): explain workspace imports blocked by earlier refusals (#191442)
- [79d7e8f4f7](https://github.com/openclaw/openclaw/commit/79d7e8f4f7) 2026-11-02 fix(update): a damaged npm plugin no longer rolls back core updates (#191348)
- [3a0bb2a358](https://github.com/openclaw/openclaw/commit/3a0bb2a358) 2026-11-02 fix(mcp): stop repeated warnings for unknown schema formats (#190793)
- [8eb11ec171](https://github.com/openclaw/openclaw/commit/8eb11ec171) 2026-11-03 fix(sessions): find CJK text inside transcript words (#191466)
- [901ca49c61](https://github.com/openclaw/openclaw/commit/901ca49c61) 2026-11-03 fix(msteams): update approval cards after decisions in personal chats (#191302)
- [91a636fc0c](https://github.com/openclaw/openclaw/commit/91a636fc0c) 2026-11-03 fix(worktrees): bound registration waiting on repository operations (#192275)
- [a90f3e24c2](https://github.com/openclaw/openclaw/commit/a90f3e24c2) 2026-11-03 fix(database): refuse non-regular recovery manifests before reading (#191347)
- [7b0cfe3594](https://github.com/openclaw/openclaw/commit/7b0cfe3594) 2026-11-03 fix(google): restore tool calls with Python keyword parameters (#191561)
- [3e3935a6b4](https://github.com/openclaw/openclaw/commit/3e3935a6b4) 2026-11-03 fix(web-search): honor sandbox provider trust during search (#191748)
- [e66883ebeb](https://github.com/openclaw/openclaw/commit/e66883ebeb) 2026-11-03 fix: recover utility tasks when automatic models are unavailable (#191199)
- [20a6e458df](https://github.com/openclaw/openclaw/commit/20a6e458df) 2026-11-03 fix(agents): stop retaining completed tool calls (#192362)
- [f593ed11af](https://github.com/openclaw/openclaw/commit/f593ed11af) 2026-11-04 fix(cron): Discord announce jobs without an account deliver to a nonexistent "default" account (#187
- [341f69b93d](https://github.com/openclaw/openclaw/commit/341f69b93d) 2026-11-04 fix(ios): chat screen ignores every tap while reconnecting to an unreachable gateway (#191560)
- [f594cf68af](https://github.com/openclaw/openclaw/commit/f594cf68af) 2026-11-04 fix(cron): show a run's next run time as a fixed time in run history (#186725)
- [58293c5bbe](https://github.com/openclaw/openclaw/commit/58293c5bbe) 2026-11-04 fix(discord): release voice recordings when speaking-end events are lost (#192932)
- [649dbeb9f5](https://github.com/openclaw/openclaw/commit/649dbeb9f5) 2026-11-04 fix(codex): avoid Gateway freezes during app-server launch (#192543)
- [6f8893c6d0](https://github.com/openclaw/openclaw/commit/6f8893c6d0) 2026-11-04 fix: updater recovers when memory inspection storage is full (#192699)
- [3d76fcf775](https://github.com/openclaw/openclaw/commit/3d76fcf775) 2026-11-04 fix(memory): match standing intents in unspaced CJK prompts (#191603)
- [e747944b47](https://github.com/openclaw/openclaw/commit/e747944b47) 2026-11-04 fix(memory): honor Memory Core dreaming opt-out under foreign slot (#188950)
- [b6287c8675](https://github.com/openclaw/openclaw/commit/b6287c8675) 2026-11-04 fix(anthropic): one failed Claude CLI launch breaks every later turn in the conversation (#187117)
- [eb5d0cb5ea](https://github.com/openclaw/openclaw/commit/eb5d0cb5ea) 2026-11-04 fix(install): keep the installed runtime private under umask 0002 (#186782)
- [b99ed97b8f](https://github.com/openclaw/openclaw/commit/b99ed97b8f) 2026-11-04 fix(memory): record the selected memory plugin in forget --json (#190721)
- [87b5a34d6a](https://github.com/openclaw/openclaw/commit/87b5a34d6a) 2026-11-04 fix(android): name chat metadata failures instead of models (#185623)
- [c1be284382](https://github.com/openclaw/openclaw/commit/c1be284382) 2026-11-04 fix(telegram): message effects are silently dropped when effectId is set (#191646)
- [b079019773](https://github.com/openclaw/openclaw/commit/b079019773) 2026-11-04 fix(daemon): Gateway repair stops the Gateway and fails when macOS denies the Trash (#189321)
- [07fce674fd](https://github.com/openclaw/openclaw/commit/07fce674fd) 2026-11-05 fix(skills): republish a discovery read retired by a config refresh (#189754)
- [6f69195cd6](https://github.com/openclaw/openclaw/commit/6f69195cd6) 2026-11-05 fix(clawrouter): fall back immediately on exhausted upstream credit (#193250)
- [69ea417aef](https://github.com/openclaw/openclaw/commit/69ea417aef) 2026-11-05 fix(state): reduce lease heartbeat write contention (#193219)
- [b31b521214](https://github.com/openclaw/openclaw/commit/b31b521214) 2026-11-05 fix(active-memory): recall memories by Chinese, Japanese, and Korean triggers in unspaced messages (
- [91f796d79f](https://github.com/openclaw/openclaw/commit/91f796d79f) 2026-11-05 fix(macos): Stop leaves browser tabs loading during navigation startup (#193307)
- [9435188c9f](https://github.com/openclaw/openclaw/commit/9435188c9f) 2026-11-05 fix: stop replaying messages discarded by queue caps (#193313)
- [f2ddf6bf13](https://github.com/openclaw/openclaw/commit/f2ddf6bf13) 2026-11-05 fix(status): empty --agent silently reports the default agent's usage (#193336)
- [06b7e2405b](https://github.com/openclaw/openclaw/commit/06b7e2405b) 2026-11-06 fix(ui): catalog dashboard e2e stalls in reconnect on loaded runners (#193197)
- [31a65d5def](https://github.com/openclaw/openclaw/commit/31a65d5def) 2026-11-07 fix(update): skip --no-lazy-fetch on Git versions without it (#194198)
- [4af0013a2c](https://github.com/openclaw/openclaw/commit/4af0013a2c) 2026-11-07 fix: skip unchanged disclosure and shell state writes during resize (#194936)
- [b2f3f9ed42](https://github.com/openclaw/openclaw/commit/b2f3f9ed42) 2026-11-07 fix(ui): Logs empty filter results lack status semantics (#183817)
- [d90ede24eb](https://github.com/openclaw/openclaw/commit/d90ede24eb) 2026-11-07 fix: diagram notices identify the wrong Pele version (#194582)
- [17e15e2e1f](https://github.com/openclaw/openclaw/commit/17e15e2e1f) 2026-11-07 fix(model-usage): reject mismatched provider in imported costs (#194564)
- [065b8f7eb6](https://github.com/openclaw/openclaw/commit/065b8f7eb6) 2026-11-08 fix: avoid slow follow-ups from native rollout size rotation (#194902)
- [c9e6370bb1](https://github.com/openclaw/openclaw/commit/c9e6370bb1) 2026-11-08 fix: reduce repeated npm publication evidence requests (#195099)
- [f498e99e29](https://github.com/openclaw/openclaw/commit/f498e99e29) 2026-11-08 fix(agents): process log claims no output for negative limit (#195065)
- [d43ff5a7e4](https://github.com/openclaw/openclaw/commit/d43ff5a7e4) 2026-11-08 fix(media): canonicalize missing media paths like their roots (#195009)
- [a3691574f4](https://github.com/openclaw/openclaw/commit/a3691574f4) 2026-11-08 fix(control-ui): reveal cached Details with the first chat frame (#194639)
- [3dea9cbb2b](https://github.com/openclaw/openclaw/commit/3dea9cbb2b) 2026-11-08 fix(ios): Claude CLI tool rows show no result despite returned output (#191878)
- [3d6914aaad](https://github.com/openclaw/openclaw/commit/3d6914aaad) 2026-11-08 fix(agents): Gateway-method turns compact large-window sessions at the 200k default (#195307)
- [f89dacd923](https://github.com/openclaw/openclaw/commit/f89dacd923) 2026-11-08 fix(android): clear folder errors after pagination recovers (#193783)
- [24f5183313](https://github.com/openclaw/openclaw/commit/24f5183313) 2026-11-09 fix(workers): mount workspace paths that contain a comma (#195304)
- [35523ba3e4](https://github.com/openclaw/openclaw/commit/35523ba3e4) 2026-11-09 fix(browser): measure managed-launch cooldown on elapsed time (#195858)
- [35db0a3464](https://github.com/openclaw/openclaw/commit/35db0a3464) 2026-11-09 fix(ui): keep backslashes in plain-text Windows paths in chat (#195504)
- [35afce96bf](https://github.com/openclaw/openclaw/commit/35afce96bf) 2026-11-09 fix(sessions): sessions_history reads transcripts for configured ACP owners (#164993)
- [af7fd744c0](https://github.com/openclaw/openclaw/commit/af7fd744c0) 2026-11-09 fix(worktrees): avoid minute-long ignored-file provisioning (#196298)
- [30ef0f155b](https://github.com/openclaw/openclaw/commit/30ef0f155b) 2026-11-09 fix(ui): keep bounded update and plugin failure text surrogate-safe (#194954)
- [e138bd4bc2](https://github.com/openclaw/openclaw/commit/e138bd4bc2) 2026-11-10 fix(matrix): a long reply with a code block arrives split into broken blocks (#196167)
- [3686da563c](https://github.com/openclaw/openclaw/commit/3686da563c) 2026-11-10 fix(ui): name plugin pages by their own label in the phone header and tab title (#196680)
- [32257d4c5f](https://github.com/openclaw/openclaw/commit/32257d4c5f) 2026-11-10 fix(talk): stop voice claiming cancelled consult work finished (#191950)
- [2f58b4f11f](https://github.com/openclaw/openclaw/commit/2f58b4f11f) 2026-11-11 fix: prevent memory cleanup errors after temporary agent exec (#196458)
- [7ad1606316](https://github.com/openclaw/openclaw/commit/7ad1606316) 2026-11-11 fix(agents): preserve custom bootstrap onboarding (#196411)
- [3031a32908](https://github.com/openclaw/openclaw/commit/3031a32908) 2026-11-11 fix(cli): gateway usage-cost and stability print nothing after Ctrl+C (#197019)
- [eb595136c6](https://github.com/openclaw/openclaw/commit/eb595136c6) 2026-11-11 fix(telegram): name DM topics from the first real message, not commands (#184821)
- [afa73f35c9](https://github.com/openclaw/openclaw/commit/afa73f35c9) 2026-11-11 fix(subagents): subagent results sent straight to the chat fail with "Plugin invocation scope is clo
- [a9c961f777](https://github.com/openclaw/openclaw/commit/a9c961f777) 2026-11-11 fix(android): disclose target device identity in pairing confirmation dialogs (#195997)
- [24f686dd05](https://github.com/openclaw/openclaw/commit/24f686dd05) 2026-11-11 fix(nodes): cancel interrupted inventory reads (#197185)
- [a0aa49cf4b](https://github.com/openclaw/openclaw/commit/a0aa49cf4b) 2026-11-11 fix(memory): disk space from finished reindexes is not returned until the Gateway restarts (#197230)
- [de2e1fec9f](https://github.com/openclaw/openclaw/commit/de2e1fec9f) 2026-11-11 fix(telegram): deliver final text when the draft stream stops before final send (#181508)
- [c686c16f21](https://github.com/openclaw/openclaw/commit/c686c16f21) 2026-11-11 fix: identify exhausted budgets in worker capacity warnings (#194894)
- [5a2b6e131c](https://github.com/openclaw/openclaw/commit/5a2b6e131c) 2026-11-11 fix(usage): chat and session costs show $0 for new Claude models and Claude CLI turns (#197246)
- [548b8346e5](https://github.com/openclaw/openclaw/commit/548b8346e5) 2026-11-12 fix(cli): let interrupted session listings exit promptly (#197758)
- [bb78f2bdab](https://github.com/openclaw/openclaw/commit/bb78f2bdab) 2026-11-12 fix(cli): restore missing Bash completions after output redirection (#196225)
- [ac849beea7](https://github.com/openclaw/openclaw/commit/ac849beea7) 2026-11-12 fix(tlon): inbound messages lose their list contents (#197057)
- [ac8b592095](https://github.com/openclaw/openclaw/commit/ac8b592095) 2026-11-12 fix(users): stop interrupted profile list requests (#197322)
- [5203424051](https://github.com/openclaw/openclaw/commit/5203424051) 2026-11-12 fix(android): discard unsaved wake-word drafts when switching gateways (#195777)
- [2c2bfd9804](https://github.com/openclaw/openclaw/commit/2c2bfd9804) 2026-11-12 fix(sessions): stop bulk imports after Ctrl-C (#197508)
- [c6667b166c](https://github.com/openclaw/openclaw/commit/c6667b166c) 2026-11-12 fix(android): close command suggestions when typing arguments (#195784)
- [0001c18108](https://github.com/openclaw/openclaw/commit/0001c18108) 2026-11-12 fix: make failed workspace preparation diagnosable
- [74fe09926a](https://github.com/openclaw/openclaw/commit/74fe09926a) 2026-11-12 fix(gateway): avoid redundant GitHub action authority work (#198008)
- [dbef1538a2](https://github.com/openclaw/openclaw/commit/dbef1538a2) 2026-11-12 fix(skills): stop library list/read replies that land after Ctrl+C (#197281)
- [ba6147a8f3](https://github.com/openclaw/openclaw/commit/ba6147a8f3) 2026-11-12 fix(android): session catalog stays disabled after cancelling continuation (#195782)
- [f471c34c1e](https://github.com/openclaw/openclaw/commit/f471c34c1e) 2026-11-12 fix(codex): stop interrupted session catalog reads (#197750)
- [c7784484fa](https://github.com/openclaw/openclaw/commit/c7784484fa) 2026-11-12 fix(usage): custom proxies record $0 for vendor models instead of the vendor's API rate (#197275)
- [407537bc41](https://github.com/openclaw/openclaw/commit/407537bc41) 2026-11-12 fix(devices): stop join-code reply that lands after Ctrl+C (#197284)
- [46c5638ff2](https://github.com/openclaw/openclaw/commit/46c5638ff2) 2026-11-12 fix(talk): voice requests stall before the backing agent starts (#183586)
- [e0dd020641](https://github.com/openclaw/openclaw/commit/e0dd020641) 2026-11-12 fix(agents): collect process results at suspended-run capacity
- [89b4a45ace](https://github.com/openclaw/openclaw/commit/89b4a45ace) 2026-11-12 fix(android): preserve pre-ack steer ownership across idle recovery snapshots (#195402)
- [ba052b7ed7](https://github.com/openclaw/openclaw/commit/ba052b7ed7) 2026-11-12 fix(android): keep 48dp composer touch targets in compact height (#195622)
- [c7a4976767](https://github.com/openclaw/openclaw/commit/c7a4976767) 2026-11-12 fix(channels): cancel pending status read in channels list on Ctrl+C (#197815)
- [43a973d0cd](https://github.com/openclaw/openclaw/commit/43a973d0cd) 2026-11-12 fix(cron): silent cron runs fail after starting fire-and-forget subagents (#197618)
- [ea4879279a](https://github.com/openclaw/openclaw/commit/ea4879279a) 2026-11-12 fix(cron): cancel interrupted status and history reads (#197315)
- [898893e85e](https://github.com/openclaw/openclaw/commit/898893e85e) 2026-11-13 fix(ui): keep the Default model under its configured runtime group while a session pins another runt
- [35949a1cea](https://github.com/openclaw/openclaw/commit/35949a1cea) 2026-11-13 fix: compaction fails for sandboxed sessions with selected skills (#198029)
- [69b3f27bf3](https://github.com/openclaw/openclaw/commit/69b3f27bf3) 2026-11-13 fix(cron): scheduled session failures lose their cause (#195901)
- [3111745395](https://github.com/openclaw/openclaw/commit/3111745395) 2026-11-13 fix(status): cancel pending Gateway reads in status on Ctrl+C (#197909)
- [da0be61a81](https://github.com/openclaw/openclaw/commit/da0be61a81) 2026-11-13 fix(ui): Browser panel blanks its live view after every agent action on the same tab (#198082)
- [d66ba010ee](https://github.com/openclaw/openclaw/commit/d66ba010ee) 2026-11-13 fix(text): streaming Markdown checkpoint must settle after a closed legacy bracket block (#193871)
- [928c118f64](https://github.com/openclaw/openclaw/commit/928c118f64) 2026-11-13 fix(telegram): agent inline button taps expire instead of reaching the agent (#196217)
- [45e2704c84](https://github.com/openclaw/openclaw/commit/45e2704c84) 2026-11-14 fix(plugins): JSON5 manifests fail Control UI builds (#198808)
- [0640d3995c](https://github.com/openclaw/openclaw/commit/0640d3995c) 2026-11-14 fix(status): cancel deep gateway reads on Ctrl+C (#198651)
- [746135b7e7](https://github.com/openclaw/openclaw/commit/746135b7e7) 2026-11-14 fix(plugins): plugins update --all keeps installing plugins and hook packs after Ctrl+C (#198379)
- [fc0d986e61](https://github.com/openclaw/openclaw/commit/fc0d986e61) 2026-11-14 fix(file-transfer): recognize UTF-8 across the text sniff boundary (#198931)
- [559f68a57d](https://github.com/openclaw/openclaw/commit/559f68a57d) 2026-11-14 fix(cli): report friendly error for unreadable exact-state JSON (#198840)
- [77f79c00df](https://github.com/openclaw/openclaw/commit/77f79c00df) 2026-11-14 fix(templates): oversized automation name or heartbeat passes validate and fails Add (#198800)
- [5328b2754d](https://github.com/openclaw/openclaw/commit/5328b2754d) 2026-11-14 fix(ui): restore upload and channel setup e2e checks (#199224)
- [aa4bc216ff](https://github.com/openclaw/openclaw/commit/aa4bc216ff) 2026-11-14 fix(workers): declare delivery diagnostic tooling dependencies
- [1ac07b3335](https://github.com/openclaw/openclaw/commit/1ac07b3335) 2026-11-14 fix(geolocation): load gzip URLs with query parameters (#198954)
- [939d04f450](https://github.com/openclaw/openclaw/commit/939d04f450) 2026-11-14 fix(imap): prevent mail skips after unsolicited FETCH updates (#198820)
- [7f22598f78](https://github.com/openclaw/openclaw/commit/7f22598f78) 2026-11-14 fix(agents): do not count host sleep toward the catalog stall watchdog (#198709)
- [897846bbe0](https://github.com/openclaw/openclaw/commit/897846bbe0) 2026-11-14 fix(knowledge): report discrawl export errors without a traceback (#198650)
- [ec46689460](https://github.com/openclaw/openclaw/commit/ec46689460) 2026-11-14 fix(telegram): pass the runtime session key to message_sending hooks (#197519)
- [57e6473fc7](https://github.com/openclaw/openclaw/commit/57e6473fc7) 2026-11-14 fix(knowledge): Replace with new asks the scribe twice when retried after the connection drops (#198
- [1b947c9a9f](https://github.com/openclaw/openclaw/commit/1b947c9a9f) 2026-11-14 fix(plugins): show why a stale registry refresh was refused (#198839)
- [06bfea7a57](https://github.com/openclaw/openclaw/commit/06bfea7a57) 2026-11-14 fix(telegram): treat forwarded rich messages as debounceable text (#187711)
- [a6750f2a01](https://github.com/openclaw/openclaw/commit/a6750f2a01) 2026-11-14 fix(cli): malformed --url crashes with TypeError instead of a security error (#198728)
- [78d3696be4](https://github.com/openclaw/openclaw/commit/78d3696be4) 2026-11-15 fix: templates build rejects BOOTSTRAP.md that passes validation (#198586)
- [c24badbee4](https://github.com/openclaw/openclaw/commit/c24badbee4) 2026-11-15 fix(templates): allow retrying creation after a partial write (#199447)
- [b483fc08d1](https://github.com/openclaw/openclaw/commit/b483fc08d1) 2026-11-15 fix(irc): tab-separated words are joined together in sent messages (#199108)
- [d5f5529cc3](https://github.com/openclaw/openclaw/commit/d5f5529cc3) 2026-11-15 fix(plugins): build browser bundles with long expressions (#199539)
- [3f7d2a1c77](https://github.com/openclaw/openclaw/commit/3f7d2a1c77) 2026-11-15 fix(gateway): stop legacy Claude CLI gap notes from duplicating user messages (#198606) (#199016)
- [648924a9b3](https://github.com/openclaw/openclaw/commit/648924a9b3) 2026-11-15 revert(ui): drop the composer waiting card; Details lists processes (#199456)
- [3d4bd2a708](https://github.com/openclaw/openclaw/commit/3d4bd2a708) 2026-11-15 fix: reuse compacted tool catalogs between agent runs (#199804)
- [6ee07a446e](https://github.com/openclaw/openclaw/commit/6ee07a446e) 2026-11-15 fix: cancel response bodies after headers with foreign signals (#199186)
- [1a8307c88c](https://github.com/openclaw/openclaw/commit/1a8307c88c) 2026-11-15 fix(sessions): keep the canonical abort outcome when compaction is interrupted (#199050)
- [ee41e9e188](https://github.com/openclaw/openclaw/commit/ee41e9e188) 2026-11-15 fix(templates): invalid MCP declarations report only "Invalid input" (#198598)
- [918847e588](https://github.com/openclaw/openclaw/commit/918847e588) 2026-11-15 fix(cli): surface onboard recommendations blank --agent remedy in --json failures (#199523)
- [6c57f5a9cf](https://github.com/openclaw/openclaw/commit/6c57f5a9cf) 2026-11-15 fix(logging): close log descriptors when workers terminate (#199554)
- [940e76922e](https://github.com/openclaw/openclaw/commit/940e76922e) 2026-11-15 fix(cli): cancel interrupted state-store guard reads (#199353)
- [e7341744df](https://github.com/openclaw/openclaw/commit/e7341744df) 2026-11-15 fix(cli): surface backup path guard remedies in --json failures (#199562)
- [d0733c6e0e](https://github.com/openclaw/openclaw/commit/d0733c6e0e) 2026-11-15 fix(cron): ended cron runs admit late turns from background work (#199585)
- [005850723d](https://github.com/openclaw/openclaw/commit/005850723d) 2026-11-15 fix(cli): cancel gateway call reads that land after Ctrl+C (#199307)
- [d89c4b55db](https://github.com/openclaw/openclaw/commit/d89c4b55db) 2026-11-15 fix(cron): cron session reports "Context overflow" when recovery compaction fails (#199473)
- [2928381894](https://github.com/openclaw/openclaw/commit/2928381894) 2026-11-15 fix(feishu): escape Markdown link destinations in incoming posts (#199339)
- [669576890a](https://github.com/openclaw/openclaw/commit/669576890a) 2026-11-15 fix(cli): surface sandbox explain blank --agent remedy in --json failures (#199369)
- [3d5d853a95](https://github.com/openclaw/openclaw/commit/3d5d853a95) 2026-11-15 fix(plugins): allow retrying pack after a failed artifact write (#199426)
- [6341f93c9c](https://github.com/openclaw/openclaw/commit/6341f93c9c) 2026-11-16 fix(knowledge): match canonically equivalent NFC/NFD keywords (#195092)
- [84a378cfe2](https://github.com/openclaw/openclaw/commit/84a378cfe2) 2026-11-16 fix(models): read provider model kinds at one owner; unknown is not chat:false
- [47b4b5e4e8](https://github.com/openclaw/openclaw/commit/47b4b5e4e8) 2026-11-16 fix(ui): Usage filters change when Enter confirms IME input (#199872)
- [317f0656ac](https://github.com/openclaw/openclaw/commit/317f0656ac) 2026-11-16 fix(agents): keep a yielded subagent's command wakes on its task after a follow-up run (#200046)
- [fa11cdd995](https://github.com/openclaw/openclaw/commit/fa11cdd995) 2026-11-16 fix(worktrees): avoid waiting on debt-free reservations
- [6e38d6dc71](https://github.com/openclaw/openclaw/commit/6e38d6dc71) 2026-11-17 fix: change saved MCP servers from the CLI without stopping the Gateway (#200582)
- [f31a0b106a](https://github.com/openclaw/openclaw/commit/f31a0b106a) 2026-11-17 fix(gateway): leave a replaced installation to the update run that holds it (#200389)
- [cacbd460cc](https://github.com/openclaw/openclaw/commit/cacbd460cc) 2026-11-17 fix: use hosted catalog limits and input for live-listed models (#200403)
- [f5d74a5df9](https://github.com/openclaw/openclaw/commit/f5d74a5df9) 2026-11-17 fix(gateway): preserve clean exit while releasing retained state leases (#200330)
- [a3dd700bb8](https://github.com/openclaw/openclaw/commit/a3dd700bb8) 2026-11-17 fix(codex): settled-turn recovery rejects sessions containing a media-only user turn (#185186)
- [eea1d5a7ff](https://github.com/openclaw/openclaw/commit/eea1d5a7ff) 2026-11-17 fix: settle yielded child notices after sibling resumes (#200581)
- [0881152c24](https://github.com/openclaw/openclaw/commit/0881152c24) 2026-11-17 fix: deliver the final answer after a Gateway restart interrupts sending it (#200553)
- [949ac11963](https://github.com/openclaw/openclaw/commit/949ac11963) 2026-11-17 fix(agents): an empty tools.allow stays unrestricted when controls are added (#197590)
- [82a38fb2fe](https://github.com/openclaw/openclaw/commit/82a38fb2fe) 2026-11-17 fix: update bundled Codex for newer ChatGPT models (#200784)
- [8610cd6562](https://github.com/openclaw/openclaw/commit/8610cd6562) 2026-11-17 fix: reduce completion churn and preserve first-chat authorization (#200966)
- [ea94eb3bd3](https://github.com/openclaw/openclaw/commit/ea94eb3bd3) 2026-11-18 fix(acp): keep a configured binding online when the adapter rejects an inherited thinking level (#19
- [c7254cc418](https://github.com/openclaw/openclaw/commit/c7254cc418) 2026-11-18 fix(codex): Codex turns fail when a plugin MCP server shares a configured server's name (#194831)
- [5ef0e2fb98](https://github.com/openclaw/openclaw/commit/5ef0e2fb98) 2026-11-18 fix: deliver a finished Codex subagent's result while a sibling is still running (#190999)
- [1b1d483d6b](https://github.com/openclaw/openclaw/commit/1b1d483d6b) 2026-11-18 fix: stop listing chat attachments the Files panel can't open (#151100)
- [2272edc69e](https://github.com/openclaw/openclaw/commit/2272edc69e) 2026-11-18 fix(gateway): config changes no longer exhaust session discovery with GitHub publication refreshes (
- [1680f54504](https://github.com/openclaw/openclaw/commit/1680f54504) 2026-11-18 fix(openai): new ChatGPT subscription models missing until an OpenClaw release (#201130)
- [fc41113560](https://github.com/openclaw/openclaw/commit/fc41113560) 2026-11-18 fix(talk): load conversation history when starting a fresh call (#201352)
- [2f658fce25](https://github.com/openclaw/openclaw/commit/2f658fce25) 2026-11-18 fix(models): relist provider model lists older than 15 minutes on picker reads (#200988)
- [7e267d814e](https://github.com/openclaw/openclaw/commit/7e267d814e) 2026-11-18 fix(ui): restore long-paste cards, sent as message text (#201137)
- [703c82d20c](https://github.com/openclaw/openclaw/commit/703c82d20c) 2026-11-18 fix(sessions): record queued input end causes and recover them across crashes (#200533)
- [b42a8ff2a2](https://github.com/openclaw/openclaw/commit/b42a8ff2a2) 2026-11-18 fix(auto-reply): a message sent after /stop is not answered when the Stop reply is delivered late (#
- [fea4a9d28f](https://github.com/openclaw/openclaw/commit/fea4a9d28f) 2026-11-18 fix: stop a long Claude CLI turn from redoing its tool work on the fallback model (#200801)
- [5bb6f35cb6](https://github.com/openclaw/openclaw/commit/5bb6f35cb6) 2026-11-18 fix(whatsapp): reconnects fill the agent session queue with connection notices (#191037)
- [2fe1f8c116](https://github.com/openclaw/openclaw/commit/2fe1f8c116) 2026-11-18 fix: stop showing a running Linux Gateway service as last exit 0 (#200778)
- [dd854aa92e](https://github.com/openclaw/openclaw/commit/dd854aa92e) 2026-11-18 fix: Telegram accounts keep receiving messages after Telegram restarts update ids (#201167)
- [cd2ae19272](https://github.com/openclaw/openclaw/commit/cd2ae19272) 2026-11-19 fix: agent-authored message buttons reach the agent on every channel (#201764)
- [cf5cf7a8c6](https://github.com/openclaw/openclaw/commit/cf5cf7a8c6) 2026-11-19 fix(discord): reconnect every account after a network outage (#201415)
- [999e873a91](https://github.com/openclaw/openclaw/commit/999e873a91) 2026-11-19 fix: let Codex subagents start when an agent folder name uses capital letters (#201520)
- [0d4eacf5b9](https://github.com/openclaw/openclaw/commit/0d4eacf5b9) 2026-11-19 fix: let the hosted model catalog publish again with the 2026.10.33 extended-stable release (#201737
- [36def6e7a0](https://github.com/openclaw/openclaw/commit/36def6e7a0) 2026-11-19 fix: let models listing none reasoning run on native Codex (#198387)
- [140e6bf92c](https://github.com/openclaw/openclaw/commit/140e6bf92c) 2026-11-19 fix(browser): stop page text reads from returning another page's text after a navigation (#196659)
- [0ff5c3354c](https://github.com/openclaw/openclaw/commit/0ff5c3354c) 2026-11-19 fix(feishu): finish long replies in the same streaming card after ten minutes (#161777)
- [c6f10e80c4](https://github.com/openclaw/openclaw/commit/c6f10e80c4) 2026-11-19 fix(matrix): replies that quote a bot mention no longer start bot turns (#197091)
- [ee1140e2bb](https://github.com/openclaw/openclaw/commit/ee1140e2bb) 2026-11-20 fix(agents): keep the prompt series when the bounded window drops an old compaction (#201655)
- [03a1c37534](https://github.com/openclaw/openclaw/commit/03a1c37534) 2026-11-20 fix: show a plugin page that opens directly or after a reload (#201542)
- [df406637f3](https://github.com/openclaw/openclaw/commit/df406637f3) 2026-11-20 fix: give parents the sub-agent's answer, not its model-switch notice (#202540)
- [150edeea6e](https://github.com/openclaw/openclaw/commit/150edeea6e) 2026-11-20 fix(ui): restore Plugins first-visit asset budget (#202795)
- [a757a08f5f](https://github.com/openclaw/openclaw/commit/a757a08f5f) 2026-11-20 fix(discord): agent presentation controls stop expiring (#201965)
- [6e56a2a42b](https://github.com/openclaw/openclaw/commit/6e56a2a42b) 2026-11-20 fix: open the recorded run from an automation's Inspect run link (#201899)
- [0ced5150aa](https://github.com/openclaw/openclaw/commit/0ced5150aa) 2026-11-20 fix: keep ACP replies alive while tools are still returning results (#202276)
- [514880429c](https://github.com/openclaw/openclaw/commit/514880429c) 2026-11-20 fix(discord): check a queued message's access again when its turn starts (#202330)
- [b24f06fa8e](https://github.com/openclaw/openclaw/commit/b24f06fa8e) 2026-11-20 fix(msteams): deliver the rest of a reply when Teams rejects the stream end (#202368)
- [e9b112d050](https://github.com/openclaw/openclaw/commit/e9b112d050) 2026-11-20 fix(ui): remove stale Workshop and template test exports (#202685)
- [ea63462201](https://github.com/openclaw/openclaw/commit/ea63462201) 2026-11-20 fix: let slow auto-compaction run to its configured timeout instead of stopping at 6 minutes (#20192
- [4639df3864](https://github.com/openclaw/openclaw/commit/4639df3864) 2026-11-20 fix(agents): freeze a prompt series' tool set at its first request (#201710)
- [ccc83c79db](https://github.com/openclaw/openclaw/commit/ccc83c79db) 2026-11-20 fix: stop empty automation checklists from recording failed runs and "did not start" notices (#20239
- [b9aa2b7e6c](https://github.com/openclaw/openclaw/commit/b9aa2b7e6c) 2026-11-20 fix(models): never list a model the provider's listing omits, including on the Gateway's first read 
- [39c3099189](https://github.com/openclaw/openclaw/commit/39c3099189) 2026-11-20 fix(doctor): diagnose immutable state without pending writes (#199509)
- [b4ddf4b30f](https://github.com/openclaw/openclaw/commit/b4ddf4b30f) 2026-11-20 fix(cron): a session cron's reply reaches the model once (#201838)
- [08a26231f4](https://github.com/openclaw/openclaw/commit/08a26231f4) 2026-11-21 fix(models): select a first model when a browser sign-in finds none (#203118)
- [39a215a36c](https://github.com/openclaw/openclaw/commit/39a215a36c) 2026-11-21 fix: let GPT-6 Luna chat again on the ChatGPT/Codex subscription route (#201746)
- [d541d8c9ea](https://github.com/openclaw/openclaw/commit/d541d8c9ea) 2026-11-21 fix(plugins): tell hooks which turn started the command a completion run reports (#201503)
- [7e5cad36da](https://github.com/openclaw/openclaw/commit/7e5cad36da) 2026-11-21 fix: keep screenshots working for background tabs in headed Chrome (#202878)
- [8fdae415ed](https://github.com/openclaw/openclaw/commit/8fdae415ed) 2026-11-21 fix(agents): keep a bounded session mode on CLIs with native tools (#202945)
- [1ac1fa353a](https://github.com/openclaw/openclaw/commit/1ac1fa353a) 2026-11-21 fix: ACP clients get the whole reply when a prompt waits behind other work (#202658)
- [3c2009fa3e](https://github.com/openclaw/openclaw/commit/3c2009fa3e) 2026-11-22 fix: show device-code sign-in steps on separate lines when the Gateway runs the login (#200884)
- [45b96ba60b](https://github.com/openclaw/openclaw/commit/45b96ba60b) 2026-11-22 fix(agents): harness history moves only at compaction (#203559)
- [3cd3a31186](https://github.com/openclaw/openclaw/commit/3cd3a31186) 2026-11-22 fix(gateway): every saved-requester start needs the grant that created it (#203521)
- [d1589dccd7](https://github.com/openclaw/openclaw/commit/d1589dccd7) 2026-11-23 fix: show HEIC photos in Control UI chat previews (#203585)
- [a63a4297f3](https://github.com/openclaw/openclaw/commit/a63a4297f3) 2026-11-23 fix: let background reviews reuse their session's cached prompt (#203601)
