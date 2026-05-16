#!/usr/bin/env python3
"""
Front matter linter for mcgarrah.github.io blog posts.

Enforces a tiered schema based on post date:
  - Legacy  (before 2023-01-01): title, layout required — warnings only, never fails CI
  - Full    (2023-01-01 and later): title, layout, categories, tags, last_modified_at,
                                    excerpt, description, seo.type, seo.date_published
                                    — errors, fails CI

Usage:
  python3 scripts/lint-frontmatter.py [--strict] [path ...]

  --strict   Exit non-zero on warnings (legacy posts) in addition to errors.
             Default: only errors (standard/full violations) cause non-zero exit.

  path       One or more files or directories to check.
             Defaults to _posts/ and _drafts/ relative to repo root.

Exit codes:
  0  No errors (warnings may be present)
  1  One or more schema errors found
"""

import sys
import os
import re
import argparse
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not available. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Schema tiers
# ---------------------------------------------------------------------------

LEGACY_CUTOFF   = date(2023, 1, 1)
STANDARD_CUTOFF = date(2023, 1, 1)  # full schema enforced from 2023-01-01 onward

LEGACY_REQUIRED   = {"title", "layout"}
STANDARD_REQUIRED = LEGACY_REQUIRED | {"categories", "tags", "last_modified_at"}
FULL_REQUIRED     = STANDARD_REQUIRED | {"excerpt", "description"}

# seo block sub-keys required for full-tier posts
SEO_REQUIRED = {"type", "date_published"}

# Allowed values
ALLOWED_LAYOUTS = {"post", "page", "default", "home", "archive", "list_page",
                   "category_page", "tag_page", "paginate", "none"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Convenience files in _drafts/ are uppercase markdown planning docs, not posts.
# They use layout: none and date: 1999-12-31 intentionally — skip them.
CONVENIENCE_FILE_RE = re.compile(r"^[A-Z][A-Z0-9_-]*\.md$")


def extract_front_matter(path: Path):
    """Return parsed front matter dict or None if not present / unparseable."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"cannot read file: {exc}"

    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, "no front matter block found"

    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        return None, f"YAML parse error: {exc}"

    return data, None


def post_date_from_filename(path: Path):
    """Extract date from YYYY-MM-DD-title.md filename, or None."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-", path.name)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    return None


def tier_for_date(post_date):
    if post_date is None or post_date < LEGACY_CUTOFF:
        return "legacy"
    if post_date < STANDARD_CUTOFF:
        return "standard"
    return "full"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(path: Path):
    """
    Returns (warnings, errors) — both lists of strings.
    warnings: legacy posts missing fields (never fail CI by default)
    errors:   standard/full posts missing required fields
    """
    warnings = []
    errors = []

    # Skip convenience files in _drafts/
    if CONVENIENCE_FILE_RE.match(path.name):
        return warnings, errors

    data, parse_error = extract_front_matter(path)
    if parse_error:
        errors.append(parse_error)
        return warnings, errors

    # Determine post date (filename takes precedence over front matter date:)
    post_date = post_date_from_filename(path)
    if post_date is None and "date" in data:
        raw = data["date"]
        if isinstance(raw, date):
            post_date = raw

    tier = tier_for_date(post_date)

    # --- Required field checks ---
    if tier == "legacy":
        for field in LEGACY_REQUIRED:
            if field not in data:
                warnings.append(f"[legacy] missing '{field}'")
    elif tier == "standard":
        for field in STANDARD_REQUIRED:
            if field not in data:
                errors.append(f"[standard] missing required field '{field}'")
    else:  # full
        for field in FULL_REQUIRED:
            if field not in data:
                errors.append(f"[full] missing required field '{field}'")
        # seo block
        seo = data.get("seo")
        if not isinstance(seo, dict):
            errors.append("[full] missing 'seo' block (must be a mapping)")
        else:
            for key in SEO_REQUIRED:
                if key not in seo:
                    errors.append(f"[full] missing 'seo.{key}'")

    # --- Type / value checks (all tiers) ---
    if "layout" in data and data["layout"] not in ALLOWED_LAYOUTS:
        errors.append(f"unknown layout '{data['layout']}' (allowed: {sorted(ALLOWED_LAYOUTS)})")

    if "categories" in data:
        cats = data["categories"]
        if not isinstance(cats, (str, list)):
            errors.append("'categories' must be a string or list")

    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, (str, list)):
            errors.append("'tags' must be a string or list")

    # published: false is discouraged in _drafts/ (redundant, creates cleanup work)
    if "_drafts" in path.parts and data.get("published") is False:
        warnings.append("'published: false' in _drafts/ is redundant — remove it")

    return warnings, errors


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def collect_files(paths):
    result = []
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix == ".md":
            result.append(p)
        elif p.is_dir():
            result.extend(sorted(p.rglob("*.md")))
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero on warnings as well as errors")
    parser.add_argument("paths", nargs="*",
                        help="files or directories to check (default: _posts/ _drafts/)")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    targets = args.paths if args.paths else [repo_root / "_posts", repo_root / "_drafts"]
    files = collect_files(targets)

    if not files:
        print("No markdown files found.")
        sys.exit(0)

    total_warnings = 0
    total_errors = 0

    for path in files:
        warnings, errors = validate(path)
        total_warnings += len(warnings)
        total_errors += len(errors)

        rel = path.relative_to(repo_root) if path.is_absolute() else path
        for msg in warnings:
            print(f"WARN  {rel}: {msg}")
        for msg in errors:
            print(f"ERROR {rel}: {msg}")

    print(f"\n{len(files)} files checked — {total_errors} error(s), {total_warnings} warning(s)")

    if total_errors > 0:
        sys.exit(1)
    if args.strict and total_warnings > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
