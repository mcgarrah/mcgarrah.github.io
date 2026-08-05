#!/usr/bin/env python3
"""Validate SEO tags and JSON-LD across all resume views."""

import json
import re
import sys
from pathlib import Path

site_dir = Path("_site")

def extract_head(html):
    match = re.search(r'<head[^>]*>(.*?)</head>', html, re.DOTALL)
    return match.group(1) if match else ""

def check_view(name, filepath):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    if not filepath.exists():
        print(f"  ERROR: {filepath} not found!")
        return False

    html = filepath.read_text()
    head = extract_head(html)
    issues = []

    # Title
    title = re.search(r'<title>([^<]+)</title>', head)
    print(f"  title: {title.group(1) if title else 'MISSING'}")

    # Description
    desc = re.search(r'<meta name="description" content="([^"]+)"', head)
    print(f"  description: {desc.group(1)[:80]}..." if desc else "  description: MISSING")

    # Canonical
    canonicals = re.findall(r'<link rel="canonical" href="([^"]+)"', head)
    print(f"  canonical: {len(canonicals)} tag(s)")
    for c in canonicals:
        print(f"    -> {c}")
    if len(canonicals) > 1:
        issues.append("DUPLICATE canonical tags")
    if len(canonicals) == 0:
        issues.append("MISSING canonical tag")

    # OG tags
    og_title = re.search(r'<meta property="og:title" content="([^"]+)"', head)
    og_desc = re.search(r'<meta property="og:description" content="([^"]+)"', head)
    og_url = re.search(r'<meta property="og:url" content="([^"]+)"', head)
    og_type = re.search(r'<meta property="og:type" content="([^"]+)"', head)
    og_image = re.search(r'<meta property="og:image" content="([^"]+)"', head)
    twitter_card = re.search(r'<meta name="twitter:card" content="([^"]+)"', head)

    print(f"  og:title: {og_title.group(1) if og_title else 'MISSING'}")
    print(f"  og:url: {og_url.group(1) if og_url else 'MISSING'}")
    print(f"  og:type: {og_type.group(1) if og_type else 'MISSING'}")
    print(f"  og:image: {og_image.group(1) if og_image else 'NOT SET'}")
    print(f"  twitter:card: {twitter_card.group(1) if twitter_card else 'MISSING'}")

    if not og_image:
        issues.append("No og:image - social shares will have no preview image")

    # Robots
    robots = re.search(r'<meta name="robots" content="([^"]+)"', head)
    print(f"  robots: {robots.group(1) if robots else 'not set (default: index,follow)'}")

    # JSON-LD
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    print(f"  JSON-LD blocks: {len(blocks)}")
    for i, block in enumerate(blocks):
        try:
            data = json.loads(block)
            schema_type = data.get("@type", "unknown")
            print(f"    [{i+1}] @type={schema_type}")
            if schema_type == "Person":
                print(f"        name: {data.get('name')}")
                print(f"        hasCredential: {len(data.get('hasCredential', []))}")
                print(f"        hasOccupation: {len(data.get('hasOccupation', []))}")
                print(f"        alumniOf: {len(data.get('alumniOf', []))}")
                print(f"        sameAs: {len(data.get('sameAs', []))}")
                # Validate telephone format
                phone = data.get("telephone", "")
                if phone and not phone.startswith("+"):
                    issues.append(f"telephone '{phone}' should use E.164 format (+1...)")
        except json.JSONDecodeError as e:
            print(f"    [{i+1}] INVALID JSON: {e}")
            issues.append(f"Invalid JSON-LD in block {i+1}")

    # Report issues
    if issues:
        print(f"\n  ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print(f"\n  No issues found.")

    return len(issues) == 0


def main():
    print("Resume SEO Validation Report")
    print(f"Site directory: {site_dir.resolve()}")

    all_ok = True
    all_ok &= check_view("BRIEF VIEW (/resume/)", site_dir / "index.html")
    all_ok &= check_view("MACHINE VIEW (/resume/machine/)", site_dir / "machine" / "index.html")

    # Print view uses permalink without trailing slash
    print_path = site_dir / "print" / "index.html"
    if not print_path.exists():
        print_path = site_dir / "print.html"
    all_ok &= check_view("PRINT VIEW (/resume/print)", print_path)

    # Sitemap check
    sitemap = site_dir / "sitemap.xml"
    print(f"\n{'='*60}")
    print(f"  SITEMAP")
    print(f"{'='*60}")
    if sitemap.exists():
        content = sitemap.read_text()
        urls = re.findall(r'<loc>([^<]+)</loc>', content)
        print(f"  URLs in sitemap: {len(urls)}")
        for url in urls:
            print(f"    -> {url}")
    else:
        print("  sitemap.xml not found")

    # Summary
    print(f"\n{'='*60}")
    if all_ok:
        print("  ALL CHECKS PASSED")
    else:
        print("  ISSUES FOUND - see above")
    print(f"{'='*60}")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
