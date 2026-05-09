#!/usr/bin/env python3
"""Update post front matter to reference generated OG images.

Adds 'image: /assets/images/og/<slug>.png' to posts that don't
already have a custom image set.

Usage:
    python3 bin/update-og-frontmatter.py              # All posts since 2023
    python3 bin/update-og-frontmatter.py --since 2025 # Posts since 2025
    python3 bin/update-og-frontmatter.py --dry-run    # Preview changes
"""

import os
import re
import argparse
import yaml


def main():
    parser = argparse.ArgumentParser(description="Update post front matter with OG images")
    parser.add_argument("--since", type=int, default=2023, help="Update posts since this year")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing image fields")
    args = parser.parse_args()

    posts_dir = "_posts"
    og_dir = "assets/images/og"
    updated = 0
    skipped = 0

    for f in sorted(os.listdir(posts_dir)):
        if not f.endswith((".md", ".markdown")):
            continue
        match = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.(md|markdown)", f)
        if not match:
            continue
        year = int(match.group(1))
        if year < args.since:
            continue

        slug = match.group(4)
        png_path = os.path.join(og_dir, f"{slug}.png")

        if not os.path.exists(png_path):
            continue

        filepath = os.path.join(posts_dir, f)
        with open(filepath, "r") as fh:
            content = fh.read()

        # Parse front matter
        fm_match = re.match(r"^(---\s*\n)(.*?)\n(---)", content, re.DOTALL)
        if not fm_match:
            continue

        front_matter = fm_match.group(2)

        # Check if image already set
        if not args.force and re.search(r"^image:", front_matter, re.MULTILINE):
            skipped += 1
            continue

        # Remove existing image line if forcing
        if args.force:
            front_matter = re.sub(r"^image:.*\n?", "", front_matter, flags=re.MULTILINE)

        # Add image field after title (or at end of front matter)
        image_line = f"image: /assets/images/og/{slug}.png"

        # Insert after title line if it exists
        title_match = re.search(r"^(title:.*)\n", front_matter, re.MULTILINE)
        if title_match:
            insert_pos = title_match.end()
            front_matter = front_matter[:insert_pos] + image_line + "\n" + front_matter[insert_pos:]
        else:
            front_matter = front_matter.rstrip() + "\n" + image_line + "\n"

        # Reconstruct file
        new_content = fm_match.group(1) + front_matter + "\n" + fm_match.group(3) + content[fm_match.end():]

        if args.dry_run:
            print(f"  [DRY RUN] {slug} → {image_line}")
        else:
            with open(filepath, "w") as fh:
                fh.write(new_content)
            print(f"  [UPDATED] {slug}")

        updated += 1

    print(f"\nDone: {updated} {'would be ' if args.dry_run else ''}updated, {skipped} skipped (already have image)")


if __name__ == "__main__":
    main()
