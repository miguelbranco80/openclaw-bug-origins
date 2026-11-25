#!/usr/bin/env python3
"""Read-only lookups for model readers: a fixed set of git and GitHub reads, and nothing else.

Readers work from text written by strangers (commit messages, pull request descriptions), so a reader is never
handed `git` or `gh` themselves: either could be talked into writing somewhere. This tool can only read.

  python3 pipeline/look.py git <log|show|blame|diff|rev-parse|rev-list|cat-file|ls-tree|merge-base> [args]
        the same git subcommand, run in the study's clone, never downloading missing objects
  python3 pipeline/look.py history log [args]
        `git log` in the full-history directory (commit and file listings older than the clone's first commit)
  python3 pipeline/look.py commit <sha>            GitHub: the files and patches of one commit
  python3 pipeline/look.py pull <number>           GitHub: one pull request's title, description, author and dates
  python3 pipeline/look.py blame <sha> <path>      GitHub: who last changed each line range of a file at a commit
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import gh  # noqa: E402
from pipeline.settings import Paused, clone, git_env, history_dir, settings  # noqa: E402

GIT_READS = {"log", "show", "blame", "diff", "rev-parse", "rev-list", "cat-file", "ls-tree", "merge-base"}
REFUSED = ("--output", "--ext-diff", "--textconv", "--no-index", "--exec", "--upload-pack", "--receive-pack",
           "--git-dir", "--work-tree", "--open-files-in-pager", "--contents")
BLAME = """query($owner: String!, $name: String!, $sha: String!, $path: String!) {
  repository(owner: $owner, name: $name) { object(expression: $sha) { ... on Commit { blame(path: $path) {
    ranges { startingLine endingLine commit { oid committedDate messageHeadline } } } } } } }"""


def refuse(message):
    print("refused: " + message, file=sys.stderr)
    sys.exit(2)


def git(base, args):
    if not args or args[0] not in GIT_READS:
        refuse("only these git subcommands are available: " + ", ".join(sorted(GIT_READS)))
    for arg in args[1:]:
        if arg.startswith(REFUSED) or arg == "-O" or arg.startswith("-O"):
            refuse(f"the option {arg.split('=')[0]} is not available")
    done = subprocess.run(["git", *base, "--no-pager", *args], env=git_env(), timeout=300)
    sys.exit(done.returncode)


def main():
    args = sys.argv[1:]
    if not args:
        refuse(__doc__)
    kind, rest = args[0], args[1:]
    owner, name = settings()["repository"].split("/")
    if kind == "git":
        git(["-C", clone()], rest)
    elif kind == "history":
        if not rest or rest[0] != "log":
            refuse("only `history log ...` is available")
        git(["--git-dir=" + history_dir()], rest)
    elif kind == "commit" and len(rest) == 1 and re.fullmatch(r"[0-9a-f]{7,40}", rest[0]):
        data = gh.rest(f"repos/{owner}/{name}/commits/{rest[0]}")
        print(json.dumps({"sha": data.get("sha"), "message": (data.get("commit") or {}).get("message"),
                          "files": [{"filename": f.get("filename"), "status": f.get("status"), "patch": f.get("patch")}
                                    for f in data.get("files") or []]}, indent=1))
    elif kind == "pull" and len(rest) == 1 and rest[0].isdigit():
        data = gh.rest(f"repos/{owner}/{name}/pulls/{rest[0]}")
        print(json.dumps({key: data.get(key) for key in ("number", "title", "body", "created_at", "merged_at",
                                                         "merge_commit_sha")}
                         | {"author": (data.get("user") or {}).get("login")}, indent=1))
    elif kind == "blame" and len(rest) == 2 and re.fullmatch(r"[0-9a-f]{7,40}", rest[0]):
        data = gh.graphql(BLAME, owner=owner, name=name, sha=rest[0], path=rest[1])
        print(json.dumps(data["data"]["repository"]["object"], indent=1))
    else:
        refuse(__doc__)


if __name__ == "__main__":
    try:
        main()
    except Paused as pause:
        print(f"lookup unavailable: {pause}", file=sys.stderr)
        sys.exit(75)
