#!/usr/bin/env python3
"""Collect every arm's findings per case and write one grading bundle per case, with the arms anonymised.

Reads <runs>/<arm>/<rank>/last.txt (Codex), <runs>/<arm>/<rank>.<chunk>/last.txt (per-file arm, chunks merged) and
<runs>/<arm>/<rank>.json (Claude subagents). Writes:
  <out>/findings.jsonl      one row per arm x case: parsed findings, run count, parse status
  <out>/bundles/<rank>.md   the bug plus each reviewer's findings under a letter
  <out>/key.json            letter -> arm, per case (not shown to graders)

Usage: python3 fix-origins/review-pilot/grade_bundles.py <runs-dir> <out-dir>
"""
import hashlib
import json
import os
import re
import sys


def parse(text):
    """The last JSON object with a `findings` list in a reviewer's final message, or None."""
    text = text.strip()
    candidates = [text] + re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    start = text.rfind('{"findings"')
    if start >= 0:
        candidates.append(text[start:])
    start = text.find("{")
    if start >= 0:
        candidates.append(text[start:text.rfind("}") + 1])
    for candidate in reversed(candidates):
        try:
            data = json.loads(candidate)
        except (ValueError, TypeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("findings"), list):
            return data["findings"]
    return None


def main():
    runs, out = sys.argv[1:3]
    os.makedirs(os.path.join(out, "bundles"), exist_ok=True)
    cases = {}
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases.jsonl")) as handle:
        for line in handle:
            case = json.loads(line)
            cases[case["rank"]] = case
    per_case = {}
    rows = []
    for arm in sorted(os.listdir(runs)):
        arm_dir = os.path.join(runs, arm)
        grouped = {}
        for name in sorted(os.listdir(arm_dir)):
            path = os.path.join(arm_dir, name)
            if os.path.isdir(path):
                path = os.path.join(path, "last.txt")
            if not os.path.exists(path):
                grouped.setdefault(int(name[:4]), []).append(None)
                continue
            grouped.setdefault(int(name[:4]), []).append(parse(open(path, errors="replace").read()))
        for rank, parts in sorted(grouped.items()):
            findings = [f for part in parts if part for f in part if isinstance(f, dict)]
            row = {"arm": arm, "rank": rank, "runs": len(parts), "unparsed": sum(p is None for p in parts),
                   "findings": findings}
            rows.append(row)
            per_case.setdefault(rank, {})[arm] = row
    with open(os.path.join(out, "findings.jsonl"), "w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    key = {}
    for rank, arms in sorted(per_case.items()):
        case = cases[rank]
        order = sorted(arms, key=lambda arm: hashlib.sha256(f"grade-v1:{rank}:{arm}".encode()).hexdigest())
        key[rank] = {chr(65 + i): arm for i, arm in enumerate(order)}
        lines = [
            f"# Case {rank}",
            "",
            "## The bug that later had to be fixed",
            f"- What the user saw: {case['user_saw']}",
            f"- What the later fix did: {case['summary']}",
            f"- What in the reviewed change was wrong: {case['cause_quote']}",
            f"- Why: {case['reasoning']}",
            "",
            "## Reviewers' findings",
        ]
        for letter, arm in key[rank].items():
            findings = arms[arm]["findings"]
            lines.append(f"### Reviewer {letter} ({len(findings)} findings)")
            if not findings:
                lines.append("(no findings)")
            for index, finding in enumerate(findings, 1):
                lines.append(
                    f"{index}. **{str(finding.get('title'))[:200]}** — `{finding.get('file')}`:{finding.get('line')} "
                    f"(confidence {finding.get('confidence')})\n   {str(finding.get('failure'))[:1500]}"
                )
            lines.append("")
        with open(os.path.join(out, "bundles", f"{rank:04d}.md"), "w") as handle:
            handle.write("\n".join(lines) + "\n")
    with open(os.path.join(out, "key.json"), "w") as handle:
        json.dump(key, handle, indent=1)
    print(f"{len(rows)} arm x case rows, {len(per_case)} bundles")


if __name__ == "__main__":
    main()
