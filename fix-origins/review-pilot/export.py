#!/usr/bin/env python3
"""Export, for each pilot case, the repository as it stood at the causing commit, with no git history.

Each export is a plain directory: every text-sized file of the commit's tree (hard-linked from a shared blob store,
read-only), plus `.review/change.diff` (the causing commit's diff) and `.review/description.md` (PR title and body).
A reviewer working inside it cannot see later commits, the fix, or GitHub.

Usage (from the repo root):
  GIT_NO_LAZY_FETCH=1 python3 research/fix-origins/review-pilot/export.py <out-dir> <ranks.json> <pr-bodies.json> [fix]

With the optional fourth argument `fix`, the tree is taken at the later fix commit instead (written under
<out-dir>/fixed-cases/), while `.review/` still holds the causing change. Those exports are the control for the
finding checkers: a finding that names the known bug should no longer hold there.
"""
import json
import os
import subprocess
import sys

MAX_BYTES = 512 * 1024
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".icns", ".mp4", ".mov", ".woff", ".woff2", ".ttf",
            ".pdf", ".zip", ".gz", ".wasm", ".bin")


def main():
    out, ranks_path, bodies_path = sys.argv[1:4]
    at_fix = len(sys.argv) > 4 and sys.argv[4] == "fix"
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    ranks = json.load(open(ranks_path))
    bodies = json.load(open(bodies_path))
    cases = {}
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases.jsonl")) as handle:
        for line in handle:
            case = json.loads(line)
            cases[case["rank"]] = case
    store = os.path.join(out, "store")
    batch = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)

    def blob(sha):
        path = os.path.join(store, sha[:2], sha)
        if os.path.exists(path):
            return path
        batch.stdin.write((sha + "\n").encode())
        batch.stdin.flush()
        header = batch.stdout.readline().decode().split()
        if len(header) < 3 or header[1] != "blob":
            if len(header) >= 3:
                batch.stdout.read(int(header[2]) + 1)
            return None
        data = batch.stdout.read(int(header[2]))
        batch.stdout.read(1)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
        os.chmod(path, 0o444)
        return path

    for rank in ranks:
        case = cases[rank]
        sha = case["sha"] if at_fix else case["cause_sha"]
        root = os.path.join(out, "fixed-cases" if at_fix else "cases", f"{rank:04d}")
        if os.path.exists(os.path.join(root, ".review", "change.diff")):
            continue
        listing = subprocess.run(["git", "ls-tree", "-r", "-l", sha], capture_output=True, text=True, env=env, check=True)
        written = skipped = missing = 0
        for line in listing.stdout.splitlines():
            meta, path = line.split("\t", 1)
            mode, kind, blob_sha, size = meta.split()
            if kind != "blob" or mode == "120000" or size == "-" or int(size) > MAX_BYTES or path.lower().endswith(SKIP_EXT):
                skipped += 1
                continue
            source = blob(blob_sha)
            if source is None:
                missing += 1
                continue
            target = os.path.join(root, path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if not os.path.exists(target):
                os.link(source, target)
            written += 1
        review = os.path.join(root, ".review")
        os.makedirs(review, exist_ok=True)
        diff = subprocess.run(["git", "show", "--format=", case["cause_sha"]], capture_output=True, env=env,
                              timeout=120, check=True)
        with open(os.path.join(review, "change.diff"), "wb") as handle:
            handle.write(diff.stdout)
        pr = bodies.get(str(case["cause_pr"]), {})
        with open(os.path.join(review, "description.md"), "w") as handle:
            handle.write(f"# {pr.get('title') or case['cause']['subject']}\n\n{pr.get('body') or '(no description)'}\n")
        print(f"{rank}: {written} files, {skipped} skipped, {missing} missing, diff {len(diff.stdout)} bytes", flush=True)


if __name__ == "__main__":
    main()
