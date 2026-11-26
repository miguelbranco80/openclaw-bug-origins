# Does looking harder find the bug? A one-off test

*This is not part of the study. It was done by hand on 25 and 26 November 2026, from scratch scripts and an
interactive session, and cannot be rerun from this repository. The counts quoted in the README's opinion section are
recorded in `looking-harder.json` next to this file.*

The study shows which changes carry the bugs. It does not show that checking those changes harder would have caught
the bug. This test tried, two ways: by reading the change, and by building it and using it.

## The changes

- **30 flagged changes with a known bug.** Each had two or more of the warning signs, was traced with high
  confidence as the cause of a later fix that users could see, and touched 150 files or fewer. 18 were new code that
  never worked and 12 broke something that had worked.
- **25 flagged changes with no known bug**, from the comparison sample.

Every reviewer saw a change as it was just before it merged: the code, the diff and the author's description, with
no git history and no hint about the bug. A separate model, run twice, decided whether a review named the known
bug. The two passes agreed on found-or-not in 233 of 239 cells; a bug counts as found only when both said so.

## Part 1: reading

Seven review styles ran on gpt-6.2 through Codex: a plain review, a hunt for defects, one focused on new code, one
on callers of changed code, one on what the tests do not cover, a plain review with more thinking time, and one
that started from the review bot's own review. One hunt for defects ran on Claude Fable 5.2. A second pass, told
what had already been found and asked to use a different method, ran on both models for the 20 changes the first
Fable review missed.

| Review | Named the known bug (of 30) |
|---|---:|
| One gpt-6.2 review, any style | 1 to 4 |
| All seven gpt-6.2 styles together | 6 |
| One Fable review | 7 |
| Fable and its second pass | 10 |
| Every review together | 10 |

- Prompt style made little difference, and more thinking time did not help.
- The stronger model made more difference: one Fable review named more than the seven gpt-6.2 styles together.
- The second pass added 3 with Fable and nothing new with gpt-6.2.
- Fable's stated confidence carried information: 5 of its 24 "high confidence" reports were the known bug. gpt-6.2
  marked nearly every report high confidence.

**Other bugs.** For five of the review runs, a model checked whether each other reported problem was fixed on main
afterwards. At least 25 distinct ones were, spread over 18 of the 30 changes. Counting the known bug or another
later-fixed one, the reviews found something real in 24 of the 30. On the 25 changes with no known bug, one gpt-6.2
review reported 53 problems, 4 of them later fixed, in 3 changes.

**Cost.** A review reports about five problems per change. At least one in eight was confirmed by a later fix; the
true share is higher, because the check recognised only part of the fixes known to exist. A gpt-6.2 review took 3
to 5 minutes; a Fable review took 6 to 20.

**What kind of bug was missed.** Sorted by hand from one-line descriptions, so rough:

| Kind of bug | In the 30 | Named by reading |
|---|---:|---:|
| What the user sees: a screen state, a message, a label | 10 | 3 |
| Needs a specific situation: a restart at the wrong moment, a lost connection, an odd machine setup | 12 | 3 |
| Plain logic or permission error | 8 | 4 |

Two of the named bugs depended on facts about the machine (a temporary-folder path that was too long, a missing
package manager). Finding 9 of the study reports that no reviewer named a bug of that kind in its 30 cases; "rarely"
is probably closer than "never".

## Part 2: running

Eight of the 20 missed changes were chosen because their bug can be reached on one developer machine. The other 12
need a real service manager, containers, real model replies or an update of the installed product. Each of the
eight was checked out as it merged, built, and given its own state folder and port.

A gpt-6.2 tester in a sandbox got one generic order: write down what the change promises, try each promise through
the command line, the running server or the web interface in a headless browser, then go down a fixed list of
conditions. The list was written before the test and not adjusted afterwards: restart in the middle, do it twice,
empty and very large input, odd paths and names, something it depends on drops out, two at once, state left by the
previous release, a narrow screen. A second gpt-6.2 then looked only at the screenshots each tester saved.

| | Count |
|---|---:|
| Changes built | 8 |
| Testers stopped part-way by the model provider's safety filter | 2 |
| Testers that reported | 6 |
| Known bug named | 0 |
| Problems the testers reported | 18 |
| Of those, later fixed on main | 4, and 2 partly, in 3 of the 6 changes |
| Problems from the second look at screenshots | 38, none later fixed |

Why the testers missed:

- **One saw the bug and did not think it was one.** Its own screenshot shows the large, nearly empty model picker
  that was later fixed.
- **One change did what it promised, and the promise was later judged wrong.** The description said a mobile
  composer collapses when the user taps outside. The tester saw it collapse with a draft in it and counted that as
  correct. The later fix keeps it open while a draft waits.
- **Two never reached the exact moment** where the bug shows, although both tried disconnects and reconnects.
- **One bug is purely about looks:** a selected filter that is hard to tell from a hovered one.

Building took about 5 minutes per change and testing about 15.

## What this does and does not show

- Neither reading nor running reliably found the particular bug that later needed fixing.
- Both found other problems that were later fixed, so extra scrutiny of flagged changes is not wasted.
- Several of the missed "bugs" are not bugs in the traditional sense. The change did what its author said, and the
  maintainers later decided it should look or behave differently.

Limits: 30 changes for reading and 6 for running; the graders and the later-fix check were models, spot-checked by
hand on five cases; the changes for running were picked for being runnable; two testers first ran without a working
browser and were rerun; Fable was not run on the changes with no known bug, so its false-alarm rate on those is
unknown.
