"""The study's settings (study.json) and the places things live.

study.json is the only file to edit to change what is studied: the repository commit, the periods ("frames"), the
sample sizes and which model answers which question. Machine-specific things are not in it: the path of the
openclaw clone comes from the environment variable OPENCLAW_CLONE, or work/openclaw when it is not set.

A frame is one period of fixes with its own random order. Frame 1 has ranks 1, 2, 3, ...; frame 2 has ranks 100001,
100002, ...; and so on. A fix's rank never changes once assigned, so adding a frame, or raising a frame's sample
size, adds cases and leaves every stored answer valid.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "fix-origins")
PILOT = os.path.join(FIX, "review-pilot")
WORK = os.path.join(ROOT, "work")  # scratch: exports, logs, the history directory; never committed
FRAME_STEP = 100000
PAUSED = 75  # exit code: stopped for a reason outside the study (signed out, quota); rerun the same command


class Paused(Exception):
    """Work stopped for a reason the operator must clear, or that clears with time. Nothing is lost."""


def settings():
    path = os.environ.get("STUDY_SETTINGS", os.path.join(ROOT, "study.json"))
    with open(path) as handle:
        data = json.load(handle)
    ids = [frame["id"] for frame in data["frames"]]
    if ids != sorted(set(ids)) or ids[0] < 1:
        raise SystemExit("study.json: frame ids must be distinct, ascending and start at 1 or above")
    return data


def clone():
    return os.path.abspath(os.environ.get("OPENCLAW_CLONE", os.path.join(WORK, "openclaw")))


def history_dir():
    """A bare git directory that borrows the clone's objects without its shallow boundary (see fullhist.sh)."""
    return os.path.join(WORK, "history.git")


def frame_offset(frame):
    return (frame["id"] - 1) * FRAME_STEP


def frame_ranges(data=None):
    """(first rank, last rank) of the sampled fixes of each frame."""
    data = data or settings()
    return [(frame_offset(f) + 1, frame_offset(f) + f["sample"]) for f in data["frames"]]


def sampled_ranks(data=None):
    return [rank for low, high in frame_ranges(data) for rank in range(low, high + 1)]


def population():
    """rank -> row of fix-origins/population.tsv."""
    rows = {}
    path = os.path.join(FIX, "population.tsv")
    if not os.path.exists(path):
        return rows
    with open(path) as handle:
        next(handle)
        for line in handle:
            rank, sha, date, subject = line.rstrip("\n").split("\t", 3)
            rows[int(rank)] = {"rank": int(rank), "sha": sha, "date": date, "subject": subject}
    return rows


def git_env():
    """Git must never download a missing object on its own: a search once pulled in 12 GB that way."""
    return dict(os.environ, GIT_NO_LAZY_FETCH="1")


def say(*parts):
    print(*parts, flush=True)


def stop_paused(error):
    say(f"\nPAUSED: {error}\nNothing is lost. When that is cleared, run the same command again; finished work is skipped.")
    sys.exit(PAUSED)
