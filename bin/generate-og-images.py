#!/usr/bin/env python3
"""Generate OG images (SVG + PNG) for blog posts.

Reads post front matter, generates branded SVG images at 1200x630,
and converts them to PNG using cairosvg. Images are named by post slug
and stored in assets/images/og/.

Usage:
    python3 bin/generate-og-images.py              # All posts since 2023
    python3 bin/generate-og-images.py --since 2025 # Posts since 2025
    python3 bin/generate-og-images.py --slug quicksight-vanity-urls  # Single post
    python3 bin/generate-og-images.py --force      # Regenerate existing
"""

import os
import re
import sys
import math
import argparse
import textwrap
import yaml

# Color themes mapped to primary tags
TAG_THEMES = {
    # Infrastructure / DevOps
    "proxmox": {"bg": "#2C3E50", "accent": "#E67E22", "icon": "gear"},
    "ceph": {"bg": "#1A237E", "accent": "#7C4DFF", "icon": "disk"},
    "zfs": {"bg": "#263238", "accent": "#00BCD4", "icon": "layers"},
    "networking": {"bg": "#1B5E20", "accent": "#69F0AE", "icon": "globe"},
    "dell-wyse-3040": {"bg": "#37474F", "accent": "#80CBC4", "icon": "monitor"},
    "homelab": {"bg": "#2C3E50", "accent": "#F39C12", "icon": "home"},
    "storage": {"bg": "#1A237E", "accent": "#448AFF", "icon": "disk"},
    # Cloud / AWS
    "aws": {"bg": "#232F3E", "accent": "#FF9900", "icon": "cloud"},
    "terraform": {"bg": "#1A1A2E", "accent": "#7B42BC", "icon": "blocks"},
    "quicksight": {"bg": "#232F3E", "accent": "#FF9900", "icon": "chart"},
    "cloudfront": {"bg": "#232F3E", "accent": "#FF9900", "icon": "bolt"},
    # Development
    "jekyll": {"bg": "#CC0000", "accent": "#FFFFFF", "icon": "gem"},
    "ruby-gem": {"bg": "#CC342D", "accent": "#FFFFFF", "icon": "gem"},
    "python": {"bg": "#1A3A5C", "accent": "#FFD43B", "icon": "code"},
    "github-actions": {"bg": "#0D1117", "accent": "#58A6FF", "icon": "cycle"},
    "github-pages": {"bg": "#0D1117", "accent": "#58A6FF", "icon": "page"},
    "vscode": {"bg": "#1E1E1E", "accent": "#007ACC", "icon": "code"},
    "vscode-extension": {"bg": "#1E1E1E", "accent": "#007ACC", "icon": "code"},
    "kiro": {"bg": "#1A1A2E", "accent": "#00D4AA", "icon": "bot"},
    # AI / ML
    "ai": {"bg": "#0F0F23", "accent": "#00D4AA", "icon": "bot"},
    "pytorch": {"bg": "#1C1C1C", "accent": "#EE4C2C", "icon": "flame"},
    "machine-learning": {"bg": "#0F0F23", "accent": "#00D4AA", "icon": "bot"},
    # Security
    "security": {"bg": "#1A1A2E", "accent": "#FF4444", "icon": "shield"},
    "isc2": {"bg": "#003366", "accent": "#00CC66", "icon": "shield"},
    "cybersecurity": {"bg": "#1A1A2E", "accent": "#FF4444", "icon": "shield"},
    "gdpr": {"bg": "#003366", "accent": "#4FC3F7", "icon": "lock"},
    # SEO / Web
    "seo": {"bg": "#1B5E20", "accent": "#76FF03", "icon": "chart"},
    "google": {"bg": "#FFFFFF", "accent": "#4285F4", "icon": "search"},
    "adsense": {"bg": "#FFFFFF", "accent": "#4285F4", "icon": "dollar"},
    # Hardware
    "thinkpad": {"bg": "#333333", "accent": "#E2231A", "icon": "monitor"},
    "hardware": {"bg": "#37474F", "accent": "#B0BEC5", "icon": "wrench"},
    "gpu": {"bg": "#1A1A2E", "accent": "#76B900", "icon": "chip"},
    # General
    "planning": {"bg": "#2C3E50", "accent": "#3498DB", "icon": "list"},
    "writing": {"bg": "#3E2723", "accent": "#FFAB91", "icon": "pen"},
    "personal": {"bg": "#2C3E50", "accent": "#9B59B6", "icon": "user"},
}

DEFAULT_THEME = {"bg": "#2C3E50", "accent": "#3498DB", "icon": "page"}

# SVG icon paths (simple geometric shapes that render in cairosvg)
SVG_ICONS = {
    "gear": '<circle cx="24" cy="24" r="18" fill="none" stroke="{color}" stroke-width="3"/><circle cx="24" cy="24" r="7" fill="{color}"/><g stroke="{color}" stroke-width="3">{teeth}</g>',
    "disk": '<circle cx="24" cy="24" r="20" fill="none" stroke="{color}" stroke-width="2.5"/><circle cx="24" cy="24" r="6" fill="none" stroke="{color}" stroke-width="2.5"/><line x1="24" y1="4" x2="24" y2="18" stroke="{color}" stroke-width="2"/>',
    "layers": '<polygon points="24,4 44,16 24,28 4,16" fill="none" stroke="{color}" stroke-width="2.5"/><polyline points="4,22 24,34 44,22" fill="none" stroke="{color}" stroke-width="2.5"/><polyline points="4,28 24,40 44,28" fill="none" stroke="{color}" stroke-width="2.5"/>',
    "globe": '<circle cx="24" cy="24" r="20" fill="none" stroke="{color}" stroke-width="2.5"/><ellipse cx="24" cy="24" rx="10" ry="20" fill="none" stroke="{color}" stroke-width="2"/><line x1="4" y1="24" x2="44" y2="24" stroke="{color}" stroke-width="2"/><line x1="24" y1="4" x2="24" y2="44" stroke="{color}" stroke-width="2"/>',
    "monitor": '<rect x="6" y="6" width="36" height="26" rx="3" fill="none" stroke="{color}" stroke-width="2.5"/><line x1="24" y1="32" x2="24" y2="40" stroke="{color}" stroke-width="2.5"/><line x1="16" y1="40" x2="32" y2="40" stroke="{color}" stroke-width="2.5"/>',
    "home": '<path d="M24 6 L4 24 L10 24 L10 42 L20 42 L20 30 L28 30 L28 42 L38 42 L38 24 L44 24 Z" fill="none" stroke="{color}" stroke-width="2.5"/>',
    "cloud": '<path d="M12 34 C6 34 2 30 2 25 C2 20 6 16 11 16 C12 10 18 6 25 6 C32 6 38 11 38 18 C43 18 46 22 46 26 C46 31 42 34 38 34 Z" fill="none" stroke="{color}" stroke-width="2.5"/>',
    "blocks": '<rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="{color}" stroke-width="2.5"/><rect x="28" y="4" width="16" height="16" rx="2" fill="none" stroke="{color}" stroke-width="2.5"/><rect x="4" y="28" width="16" height="16" rx="2" fill="none" stroke="{color}" stroke-width="2.5"/><rect x="28" y="28" width="16" height="16" rx="2" fill="none" stroke="{color}" stroke-width="2.5"/>',
    "chart": '<polyline points="4,40 16,24 28,32 44,8" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/><line x1="4" y1="44" x2="44" y2="44" stroke="{color}" stroke-width="2.5"/><line x1="4" y1="4" x2="4" y2="44" stroke="{color}" stroke-width="2.5"/>',
    "bolt": '<polygon points="26,2 10,26 22,26 18,46 38,20 26,20" fill="{color}"/>',
    "gem": '<polygon points="24,4 40,16 24,44 8,16" fill="none" stroke="{color}" stroke-width="2.5"/><line x1="8" y1="16" x2="40" y2="16" stroke="{color}" stroke-width="2.5"/>',
    "code": '<polyline points="14,12 4,24 14,36" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/><polyline points="34,12 44,24 34,36" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/><line x1="28" y1="6" x2="20" y2="42" stroke="{color}" stroke-width="2.5"/>',
    "cycle": '<path d="M24 4 A20 20 0 1 1 4 24" fill="none" stroke="{color}" stroke-width="3"/><polygon points="24,4 18,12 30,12" fill="{color}"/>',
    "page": '<rect x="8" y="4" width="28" height="40" rx="2" fill="none" stroke="{color}" stroke-width="2.5"/><line x1="14" y1="14" x2="30" y2="14" stroke="{color}" stroke-width="2"/><line x1="14" y1="22" x2="30" y2="22" stroke="{color}" stroke-width="2"/><line x1="14" y1="30" x2="24" y2="30" stroke="{color}" stroke-width="2"/>',
    "bot": '<rect x="8" y="12" width="32" height="28" rx="4" fill="none" stroke="{color}" stroke-width="2.5"/><circle cx="18" cy="26" r="4" fill="{color}"/><circle cx="30" cy="26" r="4" fill="{color}"/><line x1="24" y1="4" x2="24" y2="12" stroke="{color}" stroke-width="2.5"/><circle cx="24" cy="4" r="3" fill="{color}"/>',
    "flame": '<path d="M24 4 C24 4 36 16 36 28 C36 36 30 42 24 42 C18 42 12 36 12 28 C12 16 24 4 24 4 Z" fill="none" stroke="{color}" stroke-width="2.5"/><path d="M24 22 C24 22 30 26 30 32 C30 36 27 38 24 38 C21 38 18 36 18 32 C18 26 24 22 24 22 Z" fill="{color}" opacity="0.5"/>',
    "shield": '<path d="M24 4 L40 12 L40 24 C40 34 32 42 24 44 C16 42 8 34 8 24 L8 12 Z" fill="none" stroke="{color}" stroke-width="2.5"/><polyline points="16,24 22,30 34,18" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>',
    "lock": '<rect x="12" y="22" width="24" height="20" rx="3" fill="none" stroke="{color}" stroke-width="2.5"/><path d="M16 22 L16 14 C16 8 20 4 24 4 C28 4 32 8 32 14 L32 22" fill="none" stroke="{color}" stroke-width="2.5"/><circle cx="24" cy="32" r="3" fill="{color}"/>',
    "search": '<circle cx="20" cy="20" r="14" fill="none" stroke="{color}" stroke-width="3"/><line x1="30" y1="30" x2="42" y2="42" stroke="{color}" stroke-width="3" stroke-linecap="round"/>',
    "dollar": '<circle cx="24" cy="24" r="20" fill="none" stroke="{color}" stroke-width="2.5"/><text x="24" y="32" font-family="sans-serif" font-size="24" font-weight="700" fill="{color}" text-anchor="middle">$</text>',
    "wrench": '<path d="M36 8 C32 4 26 4 22 8 C18 12 18 18 22 22 L10 34 C8 36 8 40 10 42 C12 44 16 44 18 42 L30 30 C34 34 40 34 44 30 C48 26 48 20 44 16 L36 24 Z" fill="none" stroke="{color}" stroke-width="2.5"/>',
    "chip": '<rect x="10" y="10" width="28" height="28" rx="3" fill="none" stroke="{color}" stroke-width="2.5"/><rect x="16" y="16" width="16" height="16" rx="1" fill="none" stroke="{color}" stroke-width="2"/><g stroke="{color}" stroke-width="2"><line x1="18" y1="10" x2="18" y2="4"/><line x1="24" y1="10" x2="24" y2="4"/><line x1="30" y1="10" x2="30" y2="4"/><line x1="18" y1="38" x2="18" y2="44"/><line x1="24" y1="38" x2="24" y2="44"/><line x1="30" y1="38" x2="30" y2="44"/></g>',
    "list": '<line x1="12" y1="10" x2="40" y2="10" stroke="{color}" stroke-width="3" stroke-linecap="round"/><line x1="12" y1="20" x2="40" y2="20" stroke="{color}" stroke-width="3" stroke-linecap="round"/><line x1="12" y1="30" x2="40" y2="30" stroke="{color}" stroke-width="3" stroke-linecap="round"/><line x1="12" y1="40" x2="32" y2="40" stroke="{color}" stroke-width="3" stroke-linecap="round"/><circle cx="5" cy="10" r="3" fill="{color}"/><circle cx="5" cy="20" r="3" fill="{color}"/><circle cx="5" cy="30" r="3" fill="{color}"/><circle cx="5" cy="40" r="3" fill="{color}"/>',
    "pen": '<path d="M36 4 L44 12 L16 40 L4 44 L8 32 Z" fill="none" stroke="{color}" stroke-width="2.5"/><line x1="30" y1="10" x2="38" y2="18" stroke="{color}" stroke-width="2.5"/>',
    "user": '<circle cx="24" cy="16" r="10" fill="none" stroke="{color}" stroke-width="2.5"/><path d="M8 44 C8 34 16 28 24 28 C32 28 40 34 40 44" fill="none" stroke="{color}" stroke-width="2.5"/>',
}


def render_icon(icon_name, color):
    """Render an SVG icon at the header position."""
    icon_template = SVG_ICONS.get(icon_name, SVG_ICONS["page"])
    # Handle the gear teeth specially
    if icon_name == "gear":
        teeth = ""
        for i in range(8):
            angle = i * 45 * math.pi / 180
            x1 = 24 + 16 * math.cos(angle)
            y1 = 24 + 16 * math.sin(angle)
            x2 = 24 + 20 * math.cos(angle)
            y2 = 24 + 20 * math.sin(angle)
            teeth += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>'
        icon_template = icon_template.replace("{teeth}", teeth)
    icon_svg = icon_template.replace("{color}", color)
    return f'  <g transform="translate(68, 55) scale(1.2)">\n    {icon_svg}\n  </g>'


def get_theme(tags):
    """Pick the best color theme based on post tags."""
    for tag in tags:
        if tag in TAG_THEMES:
            return TAG_THEMES[tag]
    return DEFAULT_THEME


def wrap_title(title, max_chars=38):
    """Wrap title text for SVG rendering."""
    # Remove special characters that break SVG
    title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    lines = textwrap.wrap(title, width=max_chars)
    return lines[:4]  # Max 4 lines


def generate_svg(title, tags, date, slug):
    """Generate an OG image SVG for a blog post."""
    theme = get_theme(tags)
    bg = theme["bg"]
    accent = theme["accent"]
    icon = theme["icon"]

    title_lines = wrap_title(title)

    # Calculate title positioning
    title_start_y = 200 if len(title_lines) <= 2 else 160
    line_height = 58 if len(title_lines) <= 2 else 52

    # Build title text elements
    title_elements = ""
    for i, line in enumerate(title_lines):
        y = title_start_y + (i * line_height)
        font_size = 48 if len(title_lines) <= 2 else 42
        title_elements += f'    <text x="80" y="{y}" font-family="system-ui, -apple-system, Segoe UI, sans-serif" font-size="{font_size}" font-weight="700" fill="white">{line}</text>\n'

    # Tag pills (show up to 3)
    tag_elements = ""
    tag_x = 80
    for i, tag in enumerate(tags[:3]):
        tag_text = tag.replace("&", "&amp;")
        # Estimate width: ~9px per char + 24px padding
        tag_width = len(tag) * 9 + 24
        tag_elements += f'''    <rect x="{tag_x}" y="420" width="{tag_width}" height="30" rx="15" fill="{accent}" opacity="0.3"/>
    <text x="{tag_x + 12}" y="440" font-family="system-ui, sans-serif" font-size="14" font-weight="500" fill="{accent}">{tag_text}</text>
'''
        tag_x += tag_width + 12

    # Determine if we need light or dark text for the accent
    is_light_bg = bg.upper() in ("#FFFFFF", "#FFF")
    text_color = "#333333" if is_light_bg else "white"
    muted_color = "#666666" if is_light_bg else "rgba(255,255,255,0.7)"

    # Render SVG icon
    icon_element = render_icon(icon, accent)

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="630" viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="1200" height="630" fill="{bg}"/>

  <!-- Accent stripe -->
  <rect x="0" y="0" width="8" height="630" fill="{accent}"/>

  <!-- Decorative corner element -->
  <circle cx="1100" cy="100" r="200" fill="{accent}" opacity="0.08"/>
  <circle cx="1150" cy="580" r="120" fill="{accent}" opacity="0.05"/>

  <!-- Icon -->
{icon_element}

  <!-- Title -->
{title_elements}
  <!-- Tags -->
{tag_elements}
  <!-- Footer: site + date -->
  <line x1="80" y1="520" x2="1120" y2="520" stroke="{accent}" stroke-opacity="0.3" stroke-width="1"/>
  <text x="80" y="570" font-family="system-ui, sans-serif" font-size="20" fill="{muted_color}">mcgarrah.org</text>
  <text x="1120" y="570" font-family="system-ui, sans-serif" font-size="20" fill="{muted_color}" text-anchor="end">{date}</text>

  <!-- Author -->
  <text x="80" y="600" font-family="system-ui, sans-serif" font-size="16" fill="{muted_color}">Michael McGarrah</text>
</svg>
'''
    return svg


def get_posts(posts_dir="_posts", since=2023, slug_filter=None):
    """Read posts from _posts directory."""
    posts = []
    for f in sorted(os.listdir(posts_dir)):
        if not f.endswith((".md", ".markdown")):
            continue
        match = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.(md|markdown)", f)
        if not match:
            continue
        year = int(match.group(1))
        if year < since:
            continue
        slug = match.group(4)
        if slug_filter and slug_filter not in slug:
            continue

        with open(os.path.join(posts_dir, f), "r") as fh:
            content = fh.read()
        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue
        try:
            fm = yaml.safe_load(fm_match.group(1))
        except Exception:
            continue

        title = fm.get("title", slug.replace("-", " ").title())
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

        posts.append({
            "file": f,
            "slug": slug,
            "title": title,
            "date": date_str,
            "tags": tags or [],
        })
    return posts


def main():
    parser = argparse.ArgumentParser(description="Generate OG images for blog posts")
    parser.add_argument("--since", type=int, default=2023, help="Generate for posts since this year")
    parser.add_argument("--slug", type=str, help="Filter to posts matching this slug substring")
    parser.add_argument("--force", action="store_true", help="Regenerate existing images")
    parser.add_argument("--svg-only", action="store_true", help="Generate SVG only, skip PNG conversion")
    args = parser.parse_args()

    output_dir = "assets/images/og"
    os.makedirs(output_dir, exist_ok=True)

    posts = get_posts(since=args.since, slug_filter=args.slug)
    print(f"Found {len(posts)} posts to process\n")

    # Check for cairosvg
    has_cairosvg = False
    if not args.svg_only:
        try:
            import cairosvg
            has_cairosvg = True
        except ImportError:
            print("WARNING: cairosvg not installed. Generating SVG only.")
            print("  Install with: pip install cairosvg\n")

    generated = 0
    skipped = 0

    for post in posts:
        svg_path = os.path.join(output_dir, f"{post['slug']}.svg")
        png_path = os.path.join(output_dir, f"{post['slug']}.png")

        if not args.force and os.path.exists(png_path if has_cairosvg else svg_path):
            skipped += 1
            continue

        svg_content = generate_svg(
            title=post["title"],
            tags=post["tags"],
            date=post["date"],
            slug=post["slug"],
        )

        with open(svg_path, "w") as f:
            f.write(svg_content)

        if has_cairosvg and not args.svg_only:
            import cairosvg
            cairosvg.svg2png(
                bytestring=svg_content.encode("utf-8"),
                write_to=png_path,
                output_width=1200,
                output_height=630,
            )

        generated += 1
        status = "SVG+PNG" if (has_cairosvg and not args.svg_only) else "SVG"
        print(f"  [{status}] {post['slug']}")

    print(f"\nDone: {generated} generated, {skipped} skipped (already exist)")


if __name__ == "__main__":
    main()
