#!/usr/bin/env python3
"""Work out, per sampled fix with a named cause, what ClawSweeper had said on the causing PR when it merged.

Reads cases.jsonl and clawsweeper/raw/<pr>.json (from clawsweeper_fetch.py). Writes:
  clawsweeper/table.jsonl     one mechanical row per case (no model judgment)
  clawsweeper/bundles/<rank>.md   the text a reader needs to judge the case

Usage (from research/fix-origins): python3 scripts/clawsweeper_table.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "clawsweeper", "raw")
BUNDLES = os.path.join(HERE, "clawsweeper", "bundles")

BOT = "clawsweeper"
HEAD_RE = re.compile(r"Reviewed head:\*\*\s*`([0-9a-f]{7,40})`")
STATE_RE = re.compile(r"clawsweeper-review-state:([a-z_-]+)[^>]*?sha=([0-9a-f]{7,40})")


def is_bot(node):
    return bool(node.get("author")) and BOT in node["author"]["login"].lower()


def is_review(comment):
    body = comment["body"]
    if "clawsweeper-review item=" in body or "Reviewed head" in body:
        return True
    return any(
        edit["diff"] and ("clawsweeper-review item=" in edit["diff"] or "Reviewed head" in edit["diff"])
        for edit in comment["userContentEdits"]["nodes"]
    )


def versions(comment):
    """Every stored body of a comment, oldest first, as (time, text)."""
    edits = [(e["editedAt"], e["diff"]) for e in comment["userContentEdits"]["nodes"] if e["diff"]]
    if not edits:
        return [(comment["createdAt"], comment["body"])]
    return sorted(edits)


def parse(text):
    head = HEAD_RE.search(text)
    state = STATE_RE.search(text)
    first = next((line.strip() for line in text.splitlines() if line.strip() and not line.startswith("<!--")), "")
    return {
        "reviewed_head": (head.group(1) if head else (state.group(2) if state else None)),
        "state": state.group(1) if state else None,
        "headline": first[:200],
    }


def review_for(pr):
    """Mechanical facts about the ClawSweeper review of one PR at the moment it merged."""
    merged = pr["mergedAt"]
    reviews = [c for c in pr["comments"]["nodes"] if is_bot(c) and is_review(c)]
    out = {
        "merged_at": merged,
        "merged_by": (pr.get("mergedBy") or {}).get("login"),
        "pr_author": (pr.get("author") or {}).get("login"),
        "changed_files": pr["changedFiles"],
        "final_head": pr["headRefOid"],
        "bot_comments": sum(1 for c in pr["comments"]["nodes"] if is_bot(c)),
        "comments_truncated": pr["comments"]["totalCount"] > len(pr["comments"]["nodes"]),
    }
    all_versions = sorted(v for c in reviews for v in versions(c) if HEAD_RE.search(v[1]) or STATE_RE.search(v[1]))
    before = [v for v in all_versions if merged and v[0] <= merged]
    out["review_versions_before_merge"] = len(before)
    out["review_versions_after_merge"] = len(all_versions) - len(before)
    if not before:
        out["status"] = "no-review-before-merge"
        return out, None, []
    at_time, at_text = before[-1]
    facts = parse(at_text)
    out.update(facts)
    out["verdict"] = verdict(facts)
    out["review_time"] = at_time
    commits = [c["commit"]["oid"] for c in pr["commits"]["nodes"]]
    head = facts["reviewed_head"]
    if head and pr["headRefOid"].startswith(head[:7]) or (head and head.startswith(pr["headRefOid"][:7])):
        out["status"] = "reviewed-merged-head"
        out["commits_after_review"] = 0
    else:
        out["status"] = "reviewed-earlier-revision"
        index = next((i for i, oid in enumerate(commits) if head and oid.startswith(head[:7])), None)
        out["commits_after_review"] = (len(commits) - 1 - index) if index is not None else None
    return out, (at_time, at_text), before[:-1]


def section(text, names):
    """The named `## ` sections of a review, in order."""
    parts = re.split(r"(?m)^## ", text)
    kept = []
    for part in parts[1:]:
        title = part.splitlines()[0].strip().lower()
        if any(title.startswith(name) for name in names):
            kept.append("## " + part.rstrip())
    return "\n\n".join(kept)


# Sections that never describe a defect in the change: scoring legends, labels, workflow links, size statistics.
BOILERPLATE = (
    "review scores", "rating scale", "labels", "workflow", "history", "rank-up moves", "pr surface",
    "review metrics", "how this fits together", "product", "what this changes",
)


def without_boilerplate(text):
    """A review with its boilerplate `##`/`###` sections and HTML comments removed."""
    chunks = re.split(r"(?m)^(?=#{2,3} )", text)
    kept = [chunks[0]]
    for chunk in chunks[1:]:
        title = chunk.splitlines()[0].lstrip("# ").strip().lower()
        if not any(title.startswith(name) for name in BOILERPLATE):
            kept.append(chunk)
    return re.sub(r"<!--.*?-->", "", "".join(kept), flags=re.S).strip()


def findings_only(text):
    """The open items of a review version: its Before merge and Findings sections, without nested details."""
    body = section(text, ("before merge", "findings"))
    return re.split(r"<details>", body)[0].strip()[:5000]


def verdict(facts):
    """ClawSweeper's overall call at merge, from the state marker or, for older reviews, the headline."""
    if facts.get("state"):
        return facts["state"]
    headline = (facts.get("headline") or "").lower()
    for needle, name in (
        ("found issues", "needs-changes"), ("blocked", "blocked"), ("needs real behavior proof", "blocked"),
        ("needs maintainer review", "needs-maintainer"), ("ready", "ready"), ("looks good", "ready"),
    ):
        if needle in headline:
            return name
    return "unknown"


def humans_between(pr, start, end):
    rows = []
    for c in pr["comments"]["nodes"]:
        login = (c.get("author") or {}).get("login") or "?"
        if BOT in login.lower() or login in ("github-actions",):
            continue
        if start <= c["createdAt"] <= end:
            rows.append(f"- {c['createdAt']} {login}: {c['body'][:1500]}")
    for r in pr["reviews"]["nodes"]:
        login = (r.get("author") or {}).get("login") or "?"
        if r["submittedAt"] and start <= r["submittedAt"] <= end and r["body"]:
            rows.append(f"- {r['submittedAt']} {login} ({r['state']} review): {r['body'][:1500]}")
    return rows


def main():
    os.makedirs(BUNDLES, exist_ok=True)
    cases = [json.loads(line) for line in open(os.path.join(HERE, "cases.jsonl"))]
    rows = []
    for case in sorted(cases, key=lambda c: c["rank"]):
        if not case.get("cause_sha"):
            continue
        row = {
            "rank": case["rank"],
            "origin": case["origin"],
            "confidence": case["confidence"],
            "fix_pr": case["fix_pr"],
            "cause_pr": case["cause_pr"],
            "cause_sha": case["cause_sha"],
            "cause_date": (case.get("cause") or {}).get("date"),
            "days_to_fix": (case.get("cause") or {}).get("days_to_fix"),
            "fix_names_cause": case["fix_names_cause"],
        }
        path = os.path.join(RAW, f"{case['cause_pr']}.json") if case["cause_pr"] else None
        if not path or not os.path.exists(path):
            row["status"] = "no-pr"
            rows.append(row)
            continue
        pr = json.load(open(path))
        facts, at_merge, earlier = review_for(pr)
        row.update(facts)
        rows.append(row)
        if not at_merge:
            continue
        at_time, at_text = at_merge
        full_path = os.path.join(BUNDLES, f"{case['rank']:04d}.full.md")
        with open(full_path, "w") as handle:
            handle.write(at_text)
        lines = [
            f"# Rank {case['rank']}: fix #{case['fix_pr']} <- cause #{case['cause_pr']}",
            "",
            "## The bug (from the fix-origins reader)",
            f"- Origin: {case['origin']} (confidence {case['confidence']})",
            f"- Fix: {case['fix_subject']}",
            f"- What the user saw: {case['user_saw']}",
            f"- What the fix does: {case['summary']}",
            f"- What in the causing PR was wrong: {case['cause_quote']}",
            f"- Reasoning: {case['reasoning']}",
            "",
            "## The causing PR",
            f"- #{pr['number']}: {pr['title']}",
            f"- Author {facts['pr_author']}, merged by {facts['merged_by']} at {facts['merged_at']}, "
            f"{facts['changed_files']} files",
            f"- ClawSweeper review in force at merge: written {at_time}, state `{facts.get('state')}`, "
            f"reviewed head `{facts.get('reviewed_head')}`, final head `{facts['final_head']}` "
            f"({facts['status']}, commits after review: {facts.get('commits_after_review')})",
            f"- Headline: {facts.get('headline')}",
            f"- Full text of this review version: {full_path}",
            "",
            "## ClawSweeper review in force at merge (boilerplate sections removed)",
            without_boilerplate(at_text)[:24000],
            "",
        ]
        if earlier:
            lines.append(
                f"## Earlier versions of the ClawSweeper review ({len(earlier)} in all; open items of up to the "
                "last 3 distinct ones, oldest first)"
            )
            seen = {findings_only(at_text)}
            shown = []
            for when, text in reversed(earlier):
                items = findings_only(text)
                if items and items not in seen:
                    seen.add(items)
                    shown.append((when, text, items))
                if len(shown) == 3:
                    break
            for when, text, items in reversed(shown):
                lines.append(f"### Version of {when} (reviewed head `{parse(text)['reviewed_head']}`)")
                lines.append(items)
                lines.append("")
        humans = humans_between(pr, earlier[0][0] if earlier else at_time, facts["merged_at"])
        lines.append("## Human comments and reviews between the first ClawSweeper review and the merge")
        lines.extend(humans or ["(none)"])
        with open(os.path.join(BUNDLES, f"{case['rank']:04d}.md"), "w") as handle:
            handle.write("\n".join(lines) + "\n")
    with open(os.path.join(HERE, "clawsweeper", "table.jsonl"), "w") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print(f"{len(rows)} cases")


if __name__ == "__main__":
    main()
