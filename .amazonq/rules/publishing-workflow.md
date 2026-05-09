# Publishing Workflow — New Blog Posts

## OG Image Generation (Required for all new posts)

Every blog post needs a branded OG image for Google Article rich results and social media sharing. The image appears in:
- Google search results (Article rich result with thumbnail)
- Social media link previews (Twitter/X, LinkedIn, Discord, Slack)
- The `og:image` meta tag and JSON-LD `image` field

### Steps for a New Post

1. **Write the post** with front matter including `title:` and `tags:`

2. **Generate the OG image** (requires `cairosvg` and `pyyaml` — available in the resume `.venv`):

   ```bash
   # From the mcgarrah.github.io directory
   source ../resume/.venv/bin/activate  # or any venv with cairosvg + pyyaml
   python3 bin/generate-og-images.py --slug <partial-slug>
   ```

   This creates both `assets/images/og/<slug>.svg` and `assets/images/og/<slug>.png`.

3. **Add the image to front matter**:

   ```bash
   python3 bin/update-og-frontmatter.py --since 2026
   ```

   Or manually add to the post's front matter:
   ```yaml
   image: /assets/images/og/<slug>.png
   ```

4. **Verify** the image looks correct by opening the SVG in a browser.

### Script Reference

| Script | Purpose | Example |
|--------|---------|---------|
| `bin/generate-og-images.py` | Generate SVG + PNG OG images | `--slug quicksight` (partial match) |
| `bin/generate-og-images.py --force` | Regenerate existing images | Use after changing the template |
| `bin/generate-og-images.py --svg-only` | SVG only (no cairosvg needed) | For quick previews |
| `bin/update-og-frontmatter.py` | Add `image:` to posts missing it | `--dry-run` to preview |
| `bin/update-og-frontmatter.py --force` | Overwrite existing image fields | Use with caution |

### How the Theme System Works

Each post gets a color theme based on its first matching tag:
- **Proxmox/Ceph/ZFS** → dark blue/teal tones with infrastructure icons
- **AWS/Terraform/CloudFront** → AWS dark with orange accent
- **Jekyll/Ruby** → Ruby red with white accent
- **Python** → Navy with yellow accent
- **AI/ML** → Dark with green accent
- **Security** → Dark with red accent

The full mapping is in `bin/generate-og-images.py` under `TAG_THEMES`. Add new tags there when introducing new topic areas.

### Dependencies

- `cairosvg` — SVG to PNG conversion (pip package)
- `pyyaml` — Reading post front matter (pip package)
- Both are available in the resume repo's `.venv`

### Posts with Custom Images

Three posts have hand-crafted images that override the generated ones:
- `jekyll-seo-health-checks` → `/assets/images/jekyll-seo-health-checks.png`
- `jekyll-seo-sitemap-canonical-url-fixes` → `/assets/images/jekyll-seo-canonical.png`
- `adding-google-custom-search-jekyll` → `/assets/images/google-search-jekyll.png`

The `update-og-frontmatter.py` script skips posts that already have an `image:` field unless `--force` is used.

## Front Matter Checklist (New Posts)

Every new post should have:
- [ ] `title:` — Post title
- [ ] `tags:` — At least 2-4 relevant tags
- [ ] `description:` — 150-160 char summary for search snippets
- [ ] `image:` — OG image path (generated via script above)
- [ ] `<!-- excerpt-end -->` — Custom excerpt separator after the intro paragraph
