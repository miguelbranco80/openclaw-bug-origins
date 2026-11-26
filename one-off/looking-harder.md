# Does looking harder find the bug? Tests done by hand

*This is not part of the study. It was done by hand on 25 and 26 November 2026, from scratch scripts and an
interactive session, and cannot be rerun from this repository. The counts quoted in the README's opinion section are
recorded in `looking-harder.json` next to this file.*

## Summary

Pooling many AI reviews of a risky change wrote down about half of the bugs it was known to cause. No single review
technique came close to that alone, building and running the change found none, and the pooled output is too long
to use as it stands. Mostly a negative result.

## The question

The study shows that a small, recognisable group of changes carries about half the bugs. Would a much heavier
review of those changes, before merge, have caught the bug?

## The test set

- **30 changes with the warning signs and a known bug.** Each had two or more of the signs, was traced with high
  confidence as the cause of a later fix that users could see, and touched 150 files or fewer.
- **A reviewer saw each change as it was just before it merged:** the code, the diff and the author's description,
  with no git history and no hint about the bug.
- **A bug counts as found** when a reviewer wrote it down and two separate grading passes by a model both agreed.
  The two passes agreed on more than 97 in 100 calls.

All reviews ran on gpt-6.2 through Codex unless marked. The stronger model is Claude Fable 5.2.

## Techniques that read the code

| # | Technique | Reviews run | Known bug found, of 30 | Problems reported |
|---|---|---:|---:|---:|
| 1 | Plain review | 30 | 2 | 162 |
| 2 | "Assume there is a defect and hunt for it" | 30 | 3 | 166 |
| 3 | Focus on new code | 30 | 3 | 172 |
| 4 | Focus on callers of changed code | 30 | 4 | 143 |
| 5 | Focus on what the tests do not cover | 30 | 2 | 163 |
| 6 | Plain review with more thinking time | 30 | 1 | 184 |
| 7 | Start from the project review bot's own review | 29 | 3 | 171 |
| 8 | Hunt, stronger model | 30 | 7 | 145 |
| 9 | Second review on the 20 changes where #8 missed, stronger model | 20 | 3 | 75 |
| 10 | The same second review, gpt-6.2 | 20 | 1 | 108 |
| 11 | Eight narrow reviews per change, one question each from a fixed checklist | 240 | 6 | 807 |
| 12 | Eight narrow reviews per change, one question each learned from past bugs | 240 | 7 | 1,003 |

Notes on the rows:

- **Second review (9 and 10).** The second reviewer was given the first reviewer's list with the instruction not to
  repeat it and to use a different method. Neither reviewer was told that a bug existed or what it was.
- **Fixed checklist (11).** Restart in the middle; done twice; empty or very large input; odd paths and names;
  something it depends on drops out; two at once; state left by the previous release; a narrow screen.
- **Learned questions (12).** A model read 606 traced bugs fixed between 9 September and 1 November and named the
  eight situations that exposed the most of them. The 20 bugs belonging to a test change were left out. On the 16
  test changes fixed after that period, the learned list found 4 and the fixed checklist found 4.

The eight learned situations, with the model's own counts:

| Bugs | Situation |
|---:|---|
| 136 | Another action can start, finish, or change shared state while this is still in progress. |
| 94 | This is used through another supported client, platform, or way of running the product. |
| 67 | A step this depends on fails, is refused, or returns an uncertain result. |
| 61 | This runs with more data, more requests, or more repetitions than usual, or on a slow machine. |
| 48 | This receives input or displays content in a form the usual examples leave out. |
| 38 | This runs during an upgrade or rollback, or against data from another version. |
| 36 | The product or one of its components is stopped, restarted, or reopened in the middle of this. |
| 35 | A later action reuses a value, view, or decision from an earlier one that has since changed. |

The first of these was the best single question: it alone found 5 of the 30.

## Pooling the reviews

For each change, every review above was run and everything they reported was put in one pile. The bug counts as
found if it is anywhere in the pile.

| Adding | Reviews so far | Known bug found, of 30 |
|---|---:|---:|
| One plain review | 30 | 2 |
| Six more gpt-6.2 styles | 209 | 6 |
| The stronger model's review | 239 | 8 |
| The second reviews | 279 | 10 |
| The fixed-checklist questions | 519 | 12 |
| The learned questions | 759 | 14 |

That is about 25 reviews and about 110 reported problems per change, repeats included.

## Techniques that build and run the change

Twelve of the 30 changes were built and exercised on one developer machine. Many of the others need a real
service manager, containers, real model replies or an update of the installed product. Each was checked out as it merged,
built, and given its own state folder and port, with a gpt-6.2 agent in a sandbox.

| Technique | Changes with a report | Known bug found |
|---|---:|---:|
| An agent writes down what the change promises, tries each promise, then goes down the fixed checklist | 6 | 0 |
| A second agent looks only at the screenshots the first one saved | 6 | 0 |
| An agent runs the same steps on the version before the change and after it, and reports the differences | 7 | 0 |

Seven runs in all were stopped part-way by the model provider's safety filter, mostly on changes that touch
credentials or process control.

## Are the reported problems real?

On eight built changes, an agent took 47 problems that a reader had reported and tried to make each one happen.

| Outcome | Count |
|---|---:|
| Happened as reported | 43 |
| Did not happen | 4 |

All three reports that named a known bug were among the 43. Of the 43, 5 were later fixed on main and 4 partly.
So the reviewers are not raising false alarms. They report real problems, most of which the project never fixed in
the following weeks.

## Which bugs were found

Sorted by hand from each bug's description, so rough:

| Kind of bug | In the 30 | Found by the pooled reviews |
|---|---:|---:|
| The new code meets an existing feature or situation its author did not have in mind | 15 | 9 |
| An unusual environment: a long path, a missing tool, a very large file | 6 | 4 |
| Presentation later judged wrong: a layout, a label, a message | 7 | 1 |
| Only shows over time: a slow start, many restarts | 2 | 0 |

Several of the presentation cases are not bugs in the traditional sense. The change did what its author said, and
the maintainers later decided it should look or behave differently.

## What this shows

- **More reviews find more of the known bugs.** The count rose steadily from 2 to 14 and had not levelled off.
- **No technique stands out.** Prompt style made little difference. Questions learned from past bugs did no better
  than a fixed checklist. The stronger model was the best single step.
- **Running the change added nothing** on these bugs, in any of three forms.
- **The pooled output is not usable as it stands.** The known bug is one item among about 110 mostly real problems
  per change, and nothing marks it as the one that will matter.

## What it does not show

- Whether the pile can be cut to a short list that still holds the bug. That was not tested.
- Anything about changes without the warning signs.
- A firm rate. These are 30 chosen changes, the graders were models, and the hand-sorted kinds are one person's
  reading. The stronger model was not run with the narrow questions.

## How this compares with the project's review bot

The project's own review bot is also a model that reads a change without running it. The reviews here differ in
being asked only for wrong behavior, and in being repeated many times with different questions.
