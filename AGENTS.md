# Instructions for an agent working in this repository

This repository is a study of where the bugs in `openclaw/openclaw` come from. `README.md` is the report.
**`PROTOCOL.md` is the experimental setup: read it in full before running or changing anything.** It tells you how
to rebuild the report, regenerate the study from nothing, or extend it, using `python3 study.py`.

## Rules

- **Start with `python3 study.py doctor`, and use `python3 study.py status` to see where a run stands.** Do not
  guess what is done from memory or from file listings. In `doctor`, `STOP` blocks the stages that need that thing
  and `NOTE` is information; run it again after changing `study.json`.
- **Run stages through `study.py`.** Do not call the collection scripts by hand, and do not write a second way to
  do something `study.py` already does.
- **Never write, edit or "fix" a model's answer.** Answers under `fix-origins/` are data. If an answer is invalid,
  delete it and rerun the step. If a model step cannot run, say so; do not fill the gap yourself.
- **Never judge a case yourself in place of the configured model.** With `--backend agent`, each work order goes to
  a fresh subagent whose whole task is the order's text, with nothing added. See PROTOCOL.md, "Model steps without
  a command line tool".
- **A model that answers a step is part of the result.** If you switch backend or model because a tool is signed
  out or out of quota, say so in your report to the user; `fix-origins/judging-log.jsonl` records it per answer.
- **`PAUSED` (exit code 75) is not a failure.** It means a sign-in or a quota is in the way. Tell the user exactly
  what it printed, and rerun the same command when it is cleared. Do not work around it.
- **The project clone is read-only.** Never check out, fetch into, build, test or run code in it. Every git command
  against it carries `GIT_NO_LAZY_FETCH=1` (the scripts set it); a search without it once downloaded 12 GB.
- **GitHub access is read-only.** No comments, reviews, issues or pushes to the studied project.
- **`work/` is scratch and is never committed.** Do not commit model run logs: they contain machine paths.
- **The report states findings.** Its one section of ideas, "What the numbers point to", ties each idea to a count
  in the report and names the step that was not tested. Keep it that way: no advice to the project, and no idea
  without its count. Every number in `README.md` comes from `results/` through `report/render.py`; never type a
  number into the report. After numbers change, read the sentences around them and
  edit the ones that no longer fit.
- **Changing a brief changes the instrument.** Edit a brief under `fix-origins/` only on request, bump its version
  line, and note the change in `CORRECTIONS.md`.

## Where things are

| Path | What |
|---|---|
| `study.json` | Settings: pinned commit, periods, sample sizes, model per step |
| `study.py`, `pipeline/` | The command and its parts |
| `fix-origins/` | Collection scripts, briefs, stored answers |
| `dataset/`, `questions/`, `results/`, `charts/`, `report/` | Facts, one script per question, their output, the report renderer |
| `CORRECTIONS.md` | Claims an earlier draft made that a later check weakened |
