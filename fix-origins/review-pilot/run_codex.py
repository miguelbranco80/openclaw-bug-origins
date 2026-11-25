#!/usr/bin/env python3
"""Run blind reviews of the exported causing changes through the Codex CLI.

One run = one model reviewing one export (whole change) or one group of its files (per-file arm). Each run starts in
the export directory with a read-only sandbox, the user's Codex config ignored, no project instructions loaded, and
medium reasoning effort. Output per run, under <out>/<arm>/<rank>[.<chunk>]/: last.txt (final message), events.jsonl
(tool calls and usage), stderr.txt.

Usage:
  python3 run_codex.py --exports <dir> --out <dir> --model gpt-6.1-sol [--per-file] [--ranks 264,37] [--jobs 4]
"""
import argparse
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TEST_RE = re.compile(r"(\.test\.|\.spec\.|\.e2e\.|/__tests__/|/test/|/tests/|^test/|/fixtures/|\.snap$)")
CODE_EXT = (".ts", ".tsx", ".js", ".mjs", ".cjs", ".css", ".swift", ".kt", ".py", ".sh", ".sql", ".json", ".yml", ".yaml")
GROUP = 3


def changed_code_files(export):
    files = []
    with open(os.path.join(export, ".review", "change.diff"), errors="replace") as handle:
        for line in handle:
            if line.startswith("+++ b/"):
                path = line[6:].strip()
                if path.endswith(CODE_EXT) and not TEST_RE.search(path) and not path.startswith("docs/"):
                    files.append(path)
    return files


def run(job):
    arm, key, export, prompt, model, out = job
    target = os.path.join(out, arm, key)
    last = os.path.join(target, "last.txt")
    if os.path.exists(last) and os.path.getsize(last) > 0:
        return key, "cached", 0
    os.makedirs(target, exist_ok=True)
    command = [
        "codex", "exec", "-m", model, "-s", "read-only", "--skip-git-repo-check", "--ephemeral",
        "--ignore-user-config", "--ignore-rules", "--json",
        "-c", "model_reasoning_effort=medium", "-c", "project_doc_max_bytes=0", "-c", 'web_search="disabled"',
        "-C", export, "-o", last, prompt,
    ]
    started = time.time()
    with open(os.path.join(target, "events.jsonl"), "w") as events, open(os.path.join(target, "stderr.txt"), "w") as err:
        try:
            code = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=events, stderr=err, timeout=1800).returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
    return key, code, round(time.time() - started)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exports", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--per-file", action="store_true")
    parser.add_argument("--ranks")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    cases_dir = os.path.join(args.exports, "cases")
    ranks = [f"{int(r):04d}" for r in args.ranks.split(",")] if args.ranks else sorted(os.listdir(cases_dir))
    arm = args.model + ("__per-file" if args.per_file else "__whole")
    jobs = []
    for rank in ranks:
        export = os.path.join(cases_dir, rank)
        if not args.per_file:
            jobs.append((arm, rank, export, open(os.path.join(HERE, "prompt-whole.md")).read(), args.model, args.out))
            continue
        files = changed_code_files(export)
        template = open(os.path.join(HERE, "prompt-per-file.md")).read()
        for index in range(0, len(files), GROUP):
            chunk = files[index:index + GROUP]
            prompt = template.replace("{FILES}", "\n".join(f"- `{path}`" for path in chunk))
            jobs.append((arm, f"{rank}.{index // GROUP:02d}", export, prompt, args.model, args.out))
    print(f"{arm}: {len(jobs)} runs", flush=True)
    with ThreadPoolExecutor(args.jobs) as pool:
        for key, code, seconds in pool.map(run, jobs):
            print(f"{arm} {key}: exit {code} in {seconds}s", flush=True)


if __name__ == "__main__":
    main()
