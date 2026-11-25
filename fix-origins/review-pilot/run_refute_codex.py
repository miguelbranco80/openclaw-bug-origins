#!/usr/bin/env python3
"""Have a GPT model check each pooled finding against the exported code (same isolation as run_codex.py).

Usage: python3 run_refute_codex.py --exports <dir> --verify <dir> --model gpt-6.2-sol [--jobs 5]
Reads <verify>/refute/<rank>.md; writes <verify>/refute-gpt/<rank>/{last.txt,events.jsonl,stderr.txt}.
"""
import argparse
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))


def run(job):
    rank, export, prompt, model, target = job
    last = os.path.join(target, "last.txt")
    if os.path.exists(last) and os.path.getsize(last) > 0:
        return rank, "cached", 0
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
            code = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=events, stderr=err, timeout=2400).returncode
        except subprocess.TimeoutExpired:
            code = "timeout"
    return rank, code, round(time.time() - started)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exports", required=True)
    parser.add_argument("--verify", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--jobs", type=int, default=5)
    parser.add_argument("--tree", default="cases", help="export subfolder: cases, or fixed-cases for the control")
    parser.add_argument("--ranks", help="comma-separated case numbers; default all")
    args = parser.parse_args()
    wanted = {f"{int(r):04d}" for r in args.ranks.split(",")} if args.ranks else None
    out_name = "refute-gpt" if args.tree == "cases" else "refute-gpt-" + args.tree
    brief = open(os.path.join(HERE, "refute-prompt.md")).read()
    brief = brief.replace("to the output path you were given", "as your final message")
    jobs = []
    for name in sorted(os.listdir(os.path.join(args.verify, "refute"))):
        rank = name[:4]
        if wanted and rank not in wanted:
            continue
        findings = open(os.path.join(args.verify, "refute", name)).read()
        prompt = (brief + "\n\nThe repository directory is the current directory. Stay inside it: do not read "
                  "files anywhere else on this machine.\n\n" + findings)
        jobs.append((rank, os.path.join(args.exports, args.tree, rank), prompt, args.model,
                     os.path.join(args.verify, out_name, rank)))
    with ThreadPoolExecutor(args.jobs) as pool:
        for rank, code, seconds in pool.map(run, jobs):
            print(f"{rank}: exit {code} in {seconds}s", flush=True)


if __name__ == "__main__":
    main()
