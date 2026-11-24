#!/usr/bin/env python3
"""
audit.py — Article review audit for mcgarrah.github.io

Measures the state of _posts/ and _drafts/ so the review plan
(KIRO-CLAUDE-OPUS5-MAX-ARTICLE-REVIEW.md) can detect drift between what the
trackers claim and what the filesystem actually contains.

This exists because the diagnosis in that plan was "the trackers decoupled from
reality." A plan that can't be re-measured becomes the next stale tracker.

Usage:
    python3 .article-review/audit.py               # summary to stdout + audit.json
    python3 .article-review/audit.py --inventory   # per-draft inventory table (markdown)
    python3 .article-review/audit.py --buffer      # just the buffer count, for scripts
    python3 .article-review/audit.py --json        # machine-readable only

Exit codes:
    0  audit ran
    1  repo layout not as expected
"""

import argparse
import collections
import datetime
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(REPO, "_posts")
DRAFTS = os.path.join(REPO, "_drafts")
OUT_JSON = os.path.join(REPO, ".article-review", "audit.json")

# Non-article markdown living in _drafts/. These are planning/tracker documents,
# not posts, and must be excluded from every article count.
TRACKERS = {
    "DRAFTS.md", "SCHEDULED.md", "SCHEDULE.md",
    "PERSONA.md", "PERSONA-NOTES.md", "PERSONA-SVP.md",
    "PERSONA-LINKEDIN.md", "PERSONA-RESUME.md", "ENVESTNET-RESUME.md",
    "RUNJEKYLL-EXTENSION.md", "JEKYLLGDPR-PLUGIN.md", "GITREPO-CLEAN.md",
    "AASR-PROJECT.md", "AME-GPT-EXPLORATION.md",
    "FASTAPI-NUTRITION-API.md", "FASTAPI-DATASRCS.md", "FASTAPI-FOOD-API.md",
    "PROJECT-NEXUS.md",
}

# 2023-01-01 is the schema boundary used by scripts/lint-frontmatter.py:
# earlier posts are warn-only legacy, later posts must satisfy the full schema.
MODERN_CUTOFF = "2023"

FM_FIELDS = [
    "title", "date", "last_modified_at", "description", "excerpt",
    "categories", "tags", "image", "published", "layout", "readiness",
]

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")


def parse_file(path):
    """Return (front_matter_dict, body, word_count)."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    fm, body = {}, text
    if text.startswith("---"):
        match = FRONT_MATTER_RE.match(text)
        if match:
            raw, body = match.group(1), match.group(2)
            for line in raw.split("\n"):
                keyed = KEY_RE.match(line)
                if keyed:
                    fm[keyed.group(1)] = keyed.group(2).strip()
    return fm, body, len(re.findall(r"\S+", body))


def scan(folder, kind):
    """Audit every article-bearing markdown file in a folder."""
    rows = []
    if not os.path.isdir(folder):
        return rows
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name in TRACKERS:
            continue
        fm, body, words = parse_file(os.path.join(folder, name))
        rows.append({
            "file": name,
            "kind": kind,
            "words": words,
            "sections": len(re.findall(r"^## ", body, re.M)),
            "code_blocks": len(re.findall(r"^```", body, re.M)) // 2,
            "images": len(re.findall(r"!\[", body)),
            "ext_links": len(re.findall(r"\]\(https?://", body)),
            # Unresolved-work markers. High counts mean the draft is a worklist,
            # not prose -- a useful proxy for the rubric's W (writing state) axis.
            "todo_markers": len(re.findall(r"\bTODO\b|\bTBD\b|\bFIXME\b|\[ \]", body)),
            "placeholders": len(re.findall(
                r"placeholder|screenshot needed|coming soon|to be written|\bWIP\b", body, re.I)),
            "has_excerpt_sep": ("excerpt-end" in body) or ("excerpt_separator" in fm),
            **{f: fm.get(f, "") for f in FM_FIELDS},
        })
    return rows


def post_date(row):
    """Filename date as a date object, or None."""
    match = DATE_RE.match(row["file"])
    if not match:
        return None
    try:
        return datetime.date(*map(int, match.groups()))
    except ValueError:
        return None


def missing(rows, field):
    return [r["file"] for r in rows if not r.get(field)]


def percentiles(values):
    values = sorted(values)
    if not values:
        return {}
    n = len(values)
    return {
        "min": values[0],
        "p25": values[n // 4],
        "median": values[n // 2],
        "p75": values[(3 * n) // 4],
        "max": values[-1],
    }


def build(today):
    drafts = scan(DRAFTS, "draft")
    posts = scan(POSTS, "post")

    tracker_count = len([
        f for f in os.listdir(DRAFTS)
        if f.endswith(".md") and f in TRACKERS
    ]) if os.path.isdir(DRAFTS) else 0

    modern = [r for r in posts if r["file"] >= MODERN_CUTOFF]
    legacy = [r for r in posts if r["file"] < MODERN_CUTOFF]

    # The buffer: future-dated posts already in _posts/. Production builds run
    # without --future, so these stay hidden until the daily cron passes their
    # date. This number IS the release schedule's health metric.
    dated = [(post_date(r), r) for r in posts]
    future = [r["file"] for d, r in dated if d and d > today]
    published = [(d, r) for d, r in dated if d and d <= today]
    published.sort(key=lambda pair: pair[0])
    last_pub = published[-1][0] if published else None

    by_month = collections.Counter()
    by_dow = collections.Counter()
    for d, _ in published:
        if d.year == today.year:
            by_month[f"{d.year}-{d.month:02d}"] += 1
            by_dow[d.strftime("%a")] += 1

    def fm_gaps(rows):
        return {
            f: len(missing(rows, f))
            for f in ("description", "tags", "categories", "last_modified_at", "image")
        }

    return {
        "generated": today.isoformat(),
        "counts": {
            "posts": len(posts),
            "drafts": len(drafts),
            "trackers": tracker_count,
            "buffer": len(future),
            "draft_words": sum(r["words"] for r in drafts),
            "post_words": sum(r["words"] for r in posts),
        },
        "buffer": {
            "count": len(future),
            "files": sorted(future),
            "health": "green" if len(future) >= 4 else ("yellow" if len(future) >= 2 else "red"),
            "last_published": last_pub.isoformat() if last_pub else None,
            "days_since_last": (today - last_pub).days if last_pub else None,
        },
        "front_matter": {
            "modern_posts": {"n": len(modern), "missing": fm_gaps(modern)},
            "legacy_posts": {"n": len(legacy), "missing": fm_gaps(legacy)},
            "drafts": {
                "n": len(drafts),
                "missing": fm_gaps(drafts),
                "missing_excerpt_sep": len([r for r in drafts if not r["has_excerpt_sep"]]),
            },
        },
        "readiness": dict(collections.Counter(
            r.get("readiness") or "unset" for r in drafts)),
        "size": {
            "drafts": percentiles([r["words"] for r in drafts]),
            "posts": percentiles([r["words"] for r in posts]),
            "stubs_under_600": sorted(
                (r["words"], r["file"]) for r in drafts if r["words"] < 600),
            "over_4000": sorted(
                ((r["words"], r["file"]) for r in drafts if r["words"] > 4000),
                reverse=True),
        },
        "cadence": {
            "by_month": dict(sorted(by_month.items())),
            "by_dow": dict(by_dow),
        },
        "rows": {"drafts": drafts, "posts": posts},
    }


def tracker_mentions(rows):
    """Which drafts are invisible to the control-plane trackers."""
    corpus = ""
    for name in ("DRAFTS.md", "SCHEDULED.md", "SCHEDULE.md"):
        path = os.path.join(DRAFTS, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                corpus += fh.read()
    orphans = []
    for r in rows:
        stem = r["file"][:-3]
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
        if stem not in corpus and slug not in corpus:
            orphans.append(r["file"])
    return orphans


def print_inventory(data):
    rows = data["rows"]["drafts"]
    orphans = set(tracker_mentions(rows))
    print("| Draft | Words | §  | Code | Img | TODO | Ready | Tracked |")
    print("|-------|------:|---:|-----:|----:|-----:|-------|---------|")
    for r in rows:
        print("| `{}` | {} | {} | {} | {} | {} | {} | {} |".format(
            r["file"], r["words"], r["sections"], r["code_blocks"], r["images"],
            r["todo_markers"], r.get("readiness") or "—",
            "no" if r["file"] in orphans else "yes"))
    print()
    print(f"**Orphaned (absent from DRAFTS.md / SCHEDULE.md): {len(orphans)}**")
    for o in sorted(orphans):
        print(f"- `{o}`")


def print_summary(data):
    c, b = data["counts"], data["buffer"]
    print("=" * 72)
    print(f"ARTICLE AUDIT — {data['generated']}")
    print("=" * 72)
    print(f"  posts {c['posts']}   drafts {c['drafts']}   trackers {c['trackers']}")
    print(f"  words: {c['post_words']:,} published / {c['draft_words']:,} draft")
    print()
    icon = {"green": "OK", "yellow": "LOW", "red": "EMPTY"}[b["health"]]
    print(f"  BUFFER: {b['count']} future-dated post(s)  [{icon}]")
    print(f"  last published: {b['last_published']} ({b['days_since_last']} days ago)")
    if b["files"]:
        for f in b["files"]:
            print(f"    - {f}")
    print()
    fm = data["front_matter"]
    for label in ("modern_posts", "legacy_posts", "drafts"):
        blk = fm[label]
        gaps = ", ".join(f"{k}={v}" for k, v in blk["missing"].items() if v) or "none"
        print(f"  {label:<14} n={blk['n']:<4} missing: {gaps}")
    print()
    print(f"  readiness: {data['readiness']}")
    s = data["size"]
    print(f"  draft words: {s['drafts']}")
    print(f"  stubs <600w: {len(s['stubs_under_600'])}   over 4000w: {len(s['over_4000'])}")
    print()
    print(f"  cadence {data['generated'][:4]}: {data['cadence']['by_month']}")
    print(f"  day-of-week: {data['cadence']['by_dow']}")
    orphans = tracker_mentions(data["rows"]["drafts"])
    print()
    print(f"  DRIFT: {len(orphans)} draft(s) absent from DRAFTS.md / SCHEDULE.md")


def main():
    ap = argparse.ArgumentParser(description="Audit article inventory and release buffer.")
    ap.add_argument("--inventory", action="store_true", help="markdown per-draft table")
    ap.add_argument("--buffer", action="store_true", help="print buffer count only")
    ap.add_argument("--json", action="store_true", help="machine-readable output only")
    args = ap.parse_args()

    if not os.path.isdir(POSTS) or not os.path.isdir(DRAFTS):
        print(f"error: expected _posts/ and _drafts/ under {REPO}", file=sys.stderr)
        return 1

    data = build(datetime.date.today())

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)

    if args.buffer:
        print(data["buffer"]["count"])
    elif args.json:
        print(json.dumps({k: v for k, v in data.items() if k != "rows"}, indent=2))
    elif args.inventory:
        print_inventory(data)
    else:
        print_summary(data)
        print(f"\n  wrote {os.path.relpath(OUT_JSON, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
