---
title: "Building a Draft Preview Site for Jekyll — Part 3: The Implementation"
layout: post
categories: [jekyll, github-pages, devops]
tags: [jekyll, github-pages, staticrypt, drafts, preview, ci-cd, github-actions, giscus]
excerpt: "The design is done. Time to build it. This post covers the complete implementation — repo creation, DNS configuration, the final GitHub Actions workflow, Staticrypt testing results, and every edge case I hit along the way."
description: "Complete implementation guide for a Jekyll draft preview site using GitHub Pages, Staticrypt, and GitHub Actions. Includes repo setup, DNS configuration, final workflow, testing results, and lessons learned. Part 3 of a three-part series."
date: 2026-06-17
last_modified_at: 2026-06-17
seo:
  type: BlogPosting
  date_published: 2026-06-17
  date_modified: 2026-06-17
---

In [Part 1](/jekyll-draft-preview-site-part-1/), I explored the options. In [Part 2](/jekyll-draft-preview-site-part-2/), I refined the design. Now it's time to build it.

<!-- excerpt-end -->

This is Part 3 of a three-part series:
- **Part 1**: [Exploring every option I considered](/jekyll-draft-preview-site-part-1/)
- **Part 2**: [Refining the design — config, workflow, feedback, and gaps](/jekyll-draft-preview-site-part-2/)
- **Part 3** (this post): The complete implementation

> **Status:** The system is live at `drafts.mcgarrah.org` and deploying reliably on every push to `main`. What follows captures the real issues and fixes from first-run deployments — not just the design intent, but what actually happened.

## Creating the Drafts Repo

The deployment target is `mcgarrah/drafts.mcgarrah.org` — a public repo that contains only built HTML output. I chose public because:

- GitHub Pages on free accounts requires public repos
- The source markdown is already public in `mcgarrah.github.io`
- The HTML is Staticrypt-encrypted, so the rendered content isn't casually browsable
- The repo has no source code of value — it's a deployment target, not a project

Setup steps:
1. Created the repo initialized with a `README.md` (critical — see below)
2. Enabled GitHub Pages: Settings → Pages → Deploy from branch → `main` → `/ (root)`
3. Enabled GitHub Discussions with a dedicated "Draft Reviews" category for Giscus feedback
4. Generated a fine-grained GitHub PAT scoped to only the `drafts.mcgarrah.org` repo with `repo` permissions
5. Added `DRAFTS_DEPLOY_TOKEN` and `DRAFTS_PASSWORD` as secrets on the `mcgarrah.github.io` repo

**The empty-repo trap:** GitHub Pages cannot be configured on a truly empty repo because there's no `main` branch to select. The Pages settings page just shows an error. The repo needs at least one commit before `main` exists and Pages can be enabled. Initializing with a `README.md` avoids this entirely.

## DNS Configuration

One-time setup in Porkbun:

```text
drafts.mcgarrah.org  CNAME  mcgarrah.github.io.
```

Propagation took under five minutes. After the first successful deployment, I enabled "Enforce HTTPS" in the drafts repo's Pages settings — GitHub provisions a Let's Encrypt certificate automatically.

## The Config Overlay

The real `_config_drafts.yml` that's deployed:

```yaml
url: "https://drafts.mcgarrah.org"
canonical_url: "https://drafts.mcgarrah.org"
baseurl: ""
draft_preview_site: true
main_site_url: "https://mcgarrah.org"

# Disable production tracking and ads on the drafts preview site.
google_analytics: ""
google_adsense: ""
google_cse_id: ""

# Enable Giscus comments for the drafts preview site.
giscus:
  repo: mcgarrah/drafts.mcgarrah.org
  repo_id: R_kgDOSG6Quw
  category: Draft Reviews
  category_id: DIC_kwDOSG6Qu84C7PMZ
  mapping: pathname
  strict: 0
  reactions_enabled: 1
  emit_metadata: 0
  input_position: top
  theme: preferred_color_scheme
  lang: en
  loading: lazy

# Mark every rendered page as noindex on the drafts site.
defaults:
  - scope:
      path: ""
    values:
      noindex: true
```

Key decisions baked into this config:

- `draft_preview_site: true` and `main_site_url` power the orange preview banner in the layout
- The `defaults:` block sets `noindex: true` on every page site-wide. The layout picks this up as `<meta name="robots" content="noindex, follow">` — the primary defense against search engine indexing
- Giscus points to the drafts repo's Discussions, keeping preview feedback completely separate from production comments
- Analytics, AdSense, and custom search are all blanked — no tracking on the preview site

## The Final Workflow

The workflow evolved significantly from the sketch in Part 2. The biggest change: **selective encryption**. Instead of encrypting every HTML file on the site, the workflow identifies only draft and future-dated post pages and encrypts those. Already-published content stays unencrypted — it's public anyway, and encrypting it just adds build time and makes navigation annoying.

Here's the structure of `.github/workflows/deploy-drafts.yml`:

```yaml
name: Deploy Draft Preview Site

on:
  push:
    branches: ["main"]
  workflow_dispatch:

concurrency:
  group: drafts-pages
  cancel-in-progress: true
```

The concurrency group ensures only one drafts deployment runs at a time — if I push twice in quick succession, the second run cancels the first rather than racing.

### Build Step

Standard Jekyll build with the config overlay:

```yaml
- name: Build with Jekyll (drafts + future)
  run: bundle exec jekyll build --drafts --future --config _config.yml,_config_drafts.yml
  env:
    JEKYLL_ENV: production
```

### Selective Encryption

This is the most complex step. The workflow:

1. Scans `_drafts/` for files matching the `YYYY-MM-DD-*.md` pattern (skipping convenience files like `DRAFTS.md`)
2. Scans `_posts/` for future-dated files (post date > today)
3. Maps each source file to its rendered HTML in `_site/` using Jekyll's permalink slug
4. Encrypts each file individually in an isolated temp directory to avoid Staticrypt's basename collision problem

```bash
# Only encrypt if it starts with YYYY-MM-DD pattern (actual post format).
if [[ "$base" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
  add_target_for_slug "$(slug_from_source_file "$source_file")"
fi
```

Each file is encrypted one at a time with hash-based verification:

```bash
before_hash="$(sha256sum "$file" | awk '{print $1}')"
cp "$encrypted_src" "$file"
after_hash="$(sha256sum "$file" | awk '{print $1}')"

if [[ "$before_hash" == "$after_hash" ]]; then
  echo "::error::Encryption did not modify $file (hashes match)"
  exit 1
fi
```

Staticrypt flags used:
- `--short` — compact password prompt page
- `--remember 30` — stores the decryption key in `localStorage` for 30 days so reviewers don't re-enter the password on every page click
- `--template-title "Draft Preview - mcgarrah.org"` — custom title on the password prompt
- `-c false` — disables Staticrypt's config file creation (not needed in CI)
- `-d <temp_dir>` — output to a temp directory, then copy back to preserve the original path structure

### Crawler Protections

```yaml
- name: Apply crawler protections
  run: |
    printf "User-agent: *\nDisallow: /\n" > _site/robots.txt
    rm -f _site/feed.xml _site/sitemap.xml _site/sitemapindex.xml

    # Remove feed discovery hints from generated pages
    find _site -type f -name '*.html' \
      -exec sed -i.bak '/type="application\/atom+xml"/d' {} +
    find _site -type f -name '*.bak' -delete
```

Three layers of protection:
1. `robots.txt` with `Disallow: /` — tells well-behaved crawlers to stay away
2. `noindex` meta tags on every page (via the config overlay defaults)
3. Feed and sitemap removal — prevents content leakage through structured formats. The `sed` step also strips `<link rel="alternate" type="application/atom+xml">` tags from the HTML so there's no discoverable feed URL even in the page source.

### Binary Artifact Filtering

```yaml
- name: Remove oversized binaries from deploy output
  run: |
    rm -rf _site/assets/exes
    find _site -type f \( -iname '*.exe' -o -iname '*.msi' \) -print -delete
    find _site -type f -size +45M -print -delete
```

The production site has some downloadable executables under `assets/exes/`. These triggered GitHub large-file warnings during deployment and aren't needed for draft review. The 45MB guard catches anything else that shouldn't be in a static site deployment.

### Cross-Repo Deploy

```yaml
- name: Deploy to drafts.mcgarrah.org repo
  run: |
    deploy_dir="$(mktemp -d)"
    git clone --depth 1 --branch main \
      "https://x-access-token:${DRAFTS_DEPLOY_TOKEN}@github.com/${TARGET_REPO}.git" \
      "$deploy_dir"

    find "$deploy_dir" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
    cp -a _site/. "$deploy_dir"/

    echo "drafts.mcgarrah.org" > "$deploy_dir/CNAME"
    touch "$deploy_dir/.nojekyll"

    cd "$deploy_dir"
    git add -A
    if git diff --cached --quiet; then
      echo "No drafts-site changes to deploy"
      exit 0
    fi

    git commit -m "Deploy drafts site from ${GITHUB_SHA}"
    git push origin HEAD:main --force-with-lease
```

A few details worth noting:
- The `.nojekyll` file prevents GitHub Pages from re-processing the already-built HTML through Jekyll again
- `--force-with-lease` is safer than `--force` — it fails if someone else pushed to the drafts repo since the clone, rather than silently overwriting
- The `git diff --cached --quiet` check skips the push entirely if nothing changed, avoiding empty commits
- The shallow clone (`--depth 1`) keeps the operation fast since we don't need history

## Staticrypt Testing Results

What works:
- Draft and future post pages present the Staticrypt password prompt as expected
- The `--remember 30` flag stores the decryption key in `localStorage` — after entering the password once, subsequent pages decrypt automatically without re-prompting
- The encrypted HTML contains the Staticrypt wrapper, verified by both hash comparison and string detection in CI
- The custom template title ("Draft Preview - mcgarrah.org") makes it clear which site you're on even at the password prompt

What needs more testing before broad reviewer rollout:
- Cross-browser `--remember` behavior over longer sessions (does it survive browser updates?)
- Mobile UX around the password prompt and navigation flow
- Private/incognito windows (should always prompt — `localStorage` is session-scoped in incognito)

## Giscus Feedback

Giscus is configured to point at the `drafts.mcgarrah.org` repo's Discussions with a dedicated "Draft Reviews" category. This keeps preview feedback completely separate from production comments.

The Giscus `<script>` tag lives inside the encrypted HTML. After Staticrypt decrypts the page in-browser, the browser parses the decrypted DOM and the Giscus script loads normally. This works because Staticrypt replaces the entire page content with the decrypted HTML, which the browser then processes as if it were freshly loaded.

Reviewers need a GitHub account to leave comments. For reviewers without GitHub accounts, the preview banner includes a link back to the main site where they can use the contact page.

## The Preview Banner

The banner is implemented in `_layouts/default.html` behind the `draft_preview_site` flag:

```html
{% raw %}{% if site.draft_preview_site %}
<div style="background:#e67e00;color:#fff;text-align:center;padding:0.5em 1em;font-size:0.9em;font-weight:bold;">
  ⚠ DRAFT PREVIEW SITE — unpublished content, may change.
  <a href="{{ site.main_site_url }}" style="color:#fff;text-decoration:underline;margin-left:0.5em;">Go to the main site →</a>
</div>
{% endif %}{% endraw %}
```

This turned out to be one of the highest-value additions. It's immediately obvious to reviewers that they're on the preview site, and the link back to production makes context-switching effortless.

## What Worked

- **Config overlay approach** cleanly separated production and drafts behavior without touching `_config.yml`
- **Cross-repo deploy pipeline** is stable and repeatable — push to `main` updates both sites automatically
- **Selective encryption** reduced runtime and removed unnecessary friction on already-public pages
- **The preview banner** had outsized impact on reviewer clarity for minimal implementation effort
- **Giscus on a separate repo** keeps draft feedback isolated — when a post graduates to `_posts/`, the draft comments stay behind, having served their purpose
- **Archive ordering** is now deterministic after adding front matter to convenience files

## What Didn't Work

Early runs surfaced several workflow-level issues:

1. **GitHub Pages setup on empty repo failed**: the repo needed an initial commit before `main` could be selected in Pages settings.
2. **Encryption step appeared hung**: processing hundreds of pages made the `Encrypt HTML with Staticrypt` step look stuck even when still running. The logs were hard to interpret.
3. **Password prompt did not appear after first success**: pages were deployed unencrypted. Root cause: Staticrypt v3.5.4+ doesn't support the `-o` flag and silently ignores it. Switched to `-d <directory>`, but that flattens directory structures — all output goes to `<dir>/basename.html` regardless of input nesting. Fixed by processing each file individually in isolated temp directories.
4. **Deployment included large executable files**: binaries in deploy output triggered GitHub large-file warnings and highlighted the need for artifact filtering.
5. **Full-site encryption created unnecessary overhead**: encrypting already-public content increased runtime and complexity without adding value. Switched to selective encryption of draft and future posts only.
6. **Initial verification check was too brittle**: string matching on encrypted output caused false failures. Replaced with SHA-256 hash comparison to detect whether files were actually transformed.
7. **Special-case files broke encryption targeting**: utility documents like `DRAFTS.md` and `SUBDOMAIN-DRAFTS.md` (without standard front matter) were included in the encryption scope. Fixed by filtering to only files matching the `YYYY-MM-DD-*.md` pattern.
8. **Convenience files broke archive sort order**: The uppercase convenience files (`DRAFTS.md`, `SUBDOMAIN-DRAFTS.md`, `DRAFTS-TODO.md`) had no front matter, so Jekyll used the file's filesystem mtime as their date. This caused them to appear at random positions in the archive depending on when they were last edited. Fixed by adding minimal front matter (`layout: none`, `date: 2038-01-18`, `sitemap: false`). The pinned date of 2038-01-18 (day before the Unix Y2K38 epoch overflow) sorts them to the very top of the archive. `layout: none` preserves raw markdown rendering without site chrome. `sitemap: false` keeps them out of the sitemap.

## What NOT to Do

A few guardrails I wish I'd written down before starting:

- **Don't add `--drafts --future` to the production build** — defeats the entire purpose
- **Don't use `published: false` as a gating mechanism** — the `_drafts/` directory is the correct approach
- **Don't rely solely on `robots.txt`** — it's advisory, not enforced. Layer it with `noindex` meta tags
- **Don't put passwords in the repo** — use GitHub Secrets
- **Don't modify `_config.yml` for the drafts site** — use a config overlay file
- **Don't encrypt the entire site** — only draft and future posts need protection. Encrypting published content adds friction without adding value
- **Don't use Staticrypt's `-o` flag** — it doesn't exist in v3.5.4+. Use `-d <directory>` and handle the path flattening yourself

## Quick Reference: What Goes Where

For anyone implementing this pattern, here's where everything lives:

| File | Repo | Purpose |
|------|------|---------|
| `_config_drafts.yml` | `mcgarrah.github.io` | Jekyll config overlay for drafts build |
| `.github/workflows/deploy-drafts.yml` | `mcgarrah.github.io` | GitHub Actions workflow |
| `CNAME` | `drafts.mcgarrah.org` (auto-created) | GitHub Pages custom domain routing |
| `.nojekyll` | `drafts.mcgarrah.org` (auto-created) | Prevents GitHub Pages re-processing |
| `DRAFTS_PASSWORD` secret | `mcgarrah.github.io` | Staticrypt shared password |
| `DRAFTS_DEPLOY_TOKEN` secret | `mcgarrah.github.io` | GitHub PAT for cross-repo push |
| Draft preview banner | `_layouts/default.html` | Visual indicator for reviewers |
| Giscus config | `_config_drafts.yml` | Points comments to drafts repo Discussions |

## Lessons Learned

1. **Static-site security controls are mostly UX signals** unless source content is private. The password prompt says "this is a preview" — it doesn't prevent a determined reader from viewing the public source on GitHub.
2. **Build verification should check file transformation**, not just string signatures. SHA-256 hash comparison catches real changes; string matching produces false negatives.
3. **Tooling behavior under batch mode matters.** Staticrypt's output flattening was the key hidden trap — it works fine on a single file but silently breaks when processing multiple files with the same basename (like dozens of `index.html` files).
4. **Selective encryption is better than full-site encryption.** It reduces build time, avoids encrypting already-public content, and makes the password prompt meaningful rather than annoying.
5. **A tiny UI affordance has outsized impact.** The orange preview banner took five minutes to implement and is the single most useful feature for reviewer clarity.
6. **Convenience files should get explicit front matter** when they participate in Jekyll collections. Without a pinned date, Jekyll uses filesystem mtime, which causes random archive placement every time the file is edited.
7. **The concurrency group matters.** Without `cancel-in-progress: true`, rapid pushes can queue up multiple deployments that step on each other.

---

*This is Part 3 of a three-part series on building a Jekyll draft preview site:*
- **Part 1**: [Exploring every option I considered](/jekyll-draft-preview-site-part-1/)
- **Part 2**: [Refining the design — config, workflow, feedback, and gaps](/jekyll-draft-preview-site-part-2/)
- **Part 3** (this post): The complete implementation
