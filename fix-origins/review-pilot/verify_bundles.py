#!/usr/bin/env python3
"""Prepare the check of whether the reviewers' findings are real.

For each pilot case, pools the findings of the chosen arms under shuffled ids (F1, F2, ...), with no model name and
no hint of which finding is the known bug. Writes:
  <out>/key.json                  case -> id -> {arm, index}
  <out>/refute/<rank>.md          findings only: for a reader who traces the exported code (no later history)
  <out>/laterfix/<rank>.md        findings plus the later `fix`/`revert` commits on main that touch each file

Usage (from the repo root):
  GIT_NO_LAZY_FETCH=1 python3 research/fix-origins/review-pilot/verify_bundles.py <out-dir> <arm> [<arm> ...]
"""
import hashlib
import json
import os
import re
import subprocess
import sys

TIP = "e6b42e31bc1522b8596958fbdd85c394b23fca7b"
HERE = os.path.dirname(os.path.abspath(__file__))


def later_fixes(cause, path, env):
    try:
        out = subprocess.run(
            ["git", "log", "--first-parent", "--format=%H%x09%cs%x09%s", f"{cause}..{TIP}", "--", path],
            capture_output=True, text=True, env=env, timeout=90,
        )
    except subprocess.TimeoutExpired:
        return None
    if out.returncode != 0:
        return None
    rows = [line.split("\t", 2) for line in out.stdout.splitlines() if line.count("\t") >= 2]
    rows = [row for row in rows if re.match(r"(fix|revert)", row[2], re.I)]
    return list(reversed(rows))  # oldest first


def main():
    out, arms = sys.argv[1], sys.argv[2:]
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    for sub in ("refute", "laterfix"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    cases = {}
    with open(os.path.join(HERE, "..", "cases.jsonl")) as handle:
        for line in handle:
            case = json.loads(line)
            cases[case["rank"]] = case
    pooled = {}
    with open(os.path.join(HERE, "findings.jsonl")) as handle:
        for line in handle:
            row = json.loads(line)
            if row["arm"] in arms:
                for index, finding in enumerate(row["findings"], 1):
                    pooled.setdefault(row["rank"], []).append((row["arm"], index, finding))
    key = {}
    for rank, items in sorted(pooled.items()):
        items.sort(key=lambda item: hashlib.sha256(f"verify-v1:{rank}:{item[0]}:{item[1]}".encode()).hexdigest())
        key[rank] = {}
        refute = [f"# Case {rank:04d}: findings to check", ""]
        later = [f"# Case {rank:04d}: findings and later fixes", "",
                 f"The reviewed change is commit `{cases[rank]['cause_sha']}` ({cases[rank]['cause']['date'][:10]}).", ""]
        for number, (arm, index, finding) in enumerate(items, 1):
            fid = f"F{number}"
            key[rank][fid] = {"arm": arm, "index": index}
            text = (f"## {fid}: {str(finding.get('title'))[:200]}\n- Where: `{finding.get('file')}`:{finding.get('line')}\n"
                    f"- Claimed failure: {str(finding.get('failure'))[:1800]}\n")
            refute.append(text)
            later.append(text)
            path = str(finding.get("file") or "").strip()
            fixes = later_fixes(cases[rank]["cause_sha"], path, env) if path else None
            if fixes is None:
                later.append("- Later fixes touching this file: (could not list; path may be wrong)\n")
            elif not fixes:
                later.append("- Later fixes touching this file: none\n")
            else:
                later.append(f"- Later `fix`/`revert` commits on main touching this file ({len(fixes)}, oldest first"
                             + (", first 25 shown" if len(fixes) > 25 else "") + "):")
                later.extend(f"  - `{sha[:12]}` {date} {subject[:160]}" for sha, date, subject in fixes[:25])
                later.append("")
        with open(os.path.join(out, "refute", f"{rank:04d}.md"), "w") as handle:
            handle.write("\n".join(refute) + "\n")
        with open(os.path.join(out, "laterfix", f"{rank:04d}.md"), "w") as handle:
            handle.write("\n".join(later) + "\n")
        print(f"case {rank}: {len(items)} reported problems to check", flush=True)
    with open(os.path.join(out, "key.json"), "w") as handle:
        json.dump(key, handle, indent=1)


if __name__ == "__main__":
    main()
