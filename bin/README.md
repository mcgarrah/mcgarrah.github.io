# bin/ — Build & Utility Scripts

Scripts for generating OG images, converting assets, and validating the blog site.

## Active Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `generate-og-images.py` | Generates branded OG images (SVG + PNG at 1200x630) from post front matter. Outputs to `assets/images/og/`. | When adding new posts or regenerating social preview images |
| `update-og-frontmatter.py` | Adds `image: /assets/images/og/<slug>.png` to posts that don't already have a custom image set. | After generating new OG images |
| `convert_logos_to_png.py` | Converts SVG logos to 400px PNG with transparent backgrounds for use in contexts that don't support SVG (email, certain social platforms). | When logos are added or modified |
| `validate_seo.py` | Validates SEO tags (title, canonical, og:image, JSON-LD, robots, sitemap) across the built `_site/`. | After builds, before deploy |

## Usage

All scripts should be run from the project root with the `.venv` activated:

```bash
cd ~/github/mcgarrah.github.io
source .venv/bin/activate

# Generate OG images for all posts since 2025
python3 bin/generate-og-images.py --since 2025

# Generate OG image for a specific post
python3 bin/generate-og-images.py --slug kiro-ide-wsl2-integration

# Update front matter to reference OG images
python3 bin/update-og-frontmatter.py --since 2025

# Convert SVG logos to PNG
python3 bin/convert_logos_to_png.py

# Validate SEO (requires _site/ to be built first)
python3 bin/validate_seo.py
```

## Dependencies

- **Python 3.10+** with `.venv` (see `requirements.txt`)
- **cairosvg** — SVG to PNG conversion
- **Pillow** — image manipulation (used by OG image generation)
- **PyYAML** — reading post front matter
