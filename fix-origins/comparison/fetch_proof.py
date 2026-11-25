#!/usr/bin/env python3
"""For every pull request in comparison/raw, record what visual proof its description carried when it merged.

Reads the description's edit history through GitHub GraphQL and keeps the last version written at or before the
merge. Stores only counts and flags, not the text: comparison/proof.json maps pull request number to
  images    embedded pictures (Markdown image syntax or <img>)
  videos    embedded videos (<video>, a bare GitHub attachment link, or a link to an .mp4/.mov/.webm/.gif file)
  evidence_heading   the description has a heading containing "Evidence", "Proof", "Screenshots" or "Demo"
  characters   length of the description

Read-only; needs `gh`. Usage: python3 fix-origins/comparison/fetch_proof.py
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)|<img\b", re.I)
ATTACHMENT = re.compile(r"https://github\.com/(?:user-attachments/assets|[\w.-]+/[\w.-]+/assets)/[\w/-]+")
VIDEO_FILE = re.compile(r"https?://\S+\.(?:mp4|mov|webm|gif)\b", re.I)
HEADING = re.compile(r"(?mi)^#{1,4}\s.*\b(evidence|proof|screenshots?|demo|before\s*/\s*after)\b")


def measure(body):
    images = IMAGE.findall(body)
    stripped = IMAGE.sub(" ", body)
    stripped = re.sub(r"<img\b[^>]*>", " ", stripped, flags=re.I)
    videos = len(re.findall(r"<video\b", body, re.I)) + len(ATTACHMENT.findall(stripped)) + len(VIDEO_FILE.findall(stripped))
    return {"images": len(images), "videos": videos, "evidence_heading": bool(HEADING.search(body)), "characters": len(body)}


def main():
    numbers = sorted(int(name[:-5]) for name in os.listdir(os.path.join(HERE, "raw")))
    out_path = os.path.join(HERE, "proof.json")
    proof = json.load(open(out_path)) if os.path.exists(out_path) else {}
    todo = [n for n in numbers if str(n) not in proof]
    for start in range(0, len(todo), 10):
        chunk = todo[start:start + 10]
        fields = " ".join(
            f"p{n}: pullRequest(number:{n}) {{ body mergedAt userContentEdits(first:100) {{ nodes {{ editedAt diff }} }} }}"
            for n in chunk)
        query = 'query { repository(owner:"openclaw", name:"openclaw") { ' + fields + " } }"
        result = subprocess.run(["gh", "api", "graphql", "-f", "query=" + query], capture_output=True, text=True)
        if result.returncode != 0:
            print("failed:", result.stderr.strip()[:160])
            continue
        for key, pr in json.loads(result.stdout)["data"]["repository"].items():
            edits = sorted((e["editedAt"], e["diff"]) for e in pr["userContentEdits"]["nodes"] if e["diff"] is not None)
            before = [e for e in edits if pr["mergedAt"] and e[0] <= pr["mergedAt"]]
            body = pr["body"] if not edits else (before[-1][1] if before else "")
            entry = measure(body or "")
            entry["edited_after_merge"] = bool(edits) and edits[-1][0] > (pr["mergedAt"] or "")
            proof[key[1:]] = entry
        with open(out_path, "w") as handle:
            json.dump(proof, handle, indent=0, sort_keys=True)
    print(len(proof), "of", len(numbers))


if __name__ == "__main__":
    main()
