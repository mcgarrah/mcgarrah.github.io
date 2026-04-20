---
title: "Building a Draft Preview Site for Jekyll — Part 3: The Implementation"
layout: post
categories: [jekyll, github-pages, devops]
tags: [jekyll, github-pages, staticrypt, drafts, preview, ci-cd, github-actions, giscus]
excerpt: "The design is done. Time to build it. This post covers the complete implementation — repo creation, DNS configuration, the final GitHub Actions workflow, Staticrypt testing results, and what happened when real reviewers used it."
description: "Complete implementation guide for a Jekyll draft preview site using GitHub Pages, Staticrypt, and GitHub Actions. Includes repo setup, DNS configuration, final workflow, testing results, and lessons learned. Part 3 of a three-part series."
date: 2026-06-19
last_modified_at: 2026-06-19
published: true
seo:
  type: BlogPosting
  date_published: 2026-06-19
  date_modified: 2026-06-19
---

In [Part 1](/jekyll-draft-preview-site-part-1/), I explored the options. In [Part 2](/jekyll-draft-preview-site-part-2/), I refined the design. Now it's time to build it.

<!-- excerpt-end -->

This is Part 3 of a three-part series:
- **Part 1**: [Exploring every option I considered](/jekyll-draft-preview-site-part-1/)
- **Part 2**: [Refining the design — config, workflow, feedback, and gaps](/jekyll-draft-preview-site-part-2/)
- **Part 3** (this post): The complete implementation

> **Implementation status:** The system is live on `drafts.mcgarrah.org` and running reliably. The notes below capture the real issues and fixes from first-run deployments.

## Creating the Drafts Repo

The deployment target repo is `mcgarrah/drafts.mcgarrah.org`.

Implementation details:
- Repo initialized so `main` existed before Pages setup
- GitHub Pages enabled (`main` branch, root)
- GitHub Discussions enabled with a dedicated `Draft Reviews` category for feedback

> **Implementation note:** GitHub Pages setup fails on a truly empty repo because there is no `main` branch to select yet. The repo needs an initial commit first, so initialize with a `README.md` or create any file before enabling Pages.

## DNS Configuration

Porkbun is configured with:

```text
drafts.mcgarrah.org  CNAME  mcgarrah.github.io.
```

GitHub Pages routing then maps the host to the repo via the `CNAME` file in deploy output.

## The Final Config Overlay

`_config_drafts.yml` now contains concrete values, including a site-level preview flag for the banner:

```yaml
url: "https://drafts.mcgarrah.org"
canonical_url: "https://drafts.mcgarrah.org"
baseurl: ""
draft_preview_site: true
main_site_url: "https://mcgarrah.org"

google_analytics: ""
google_adsense: ""
google_cse_id: ""

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
```

## The Final GitHub Actions Workflow

The final workflow stabilized around a few key decisions:

- Build with `--drafts --future` and config overlay
- Encrypt only draft and future article pages (not the full site)
- Process encryption targets one-by-one in isolated temp directories to avoid Staticrypt basename collisions
- Use hash checks to validate files were actually transformed
- Remove executable artifacts and oversized binaries from deploy output
- Enforce crawler protections (`robots.txt: Disallow /`, remove feed/sitemap files)
- Force-push generated output to `mcgarrah/drafts.mcgarrah.org`

Latest run status in this implementation cycle: `completed/success`.

## Staticrypt Testing Results

Validated:
- Draft/future post pages present the Staticrypt password prompt
- Encryption is present in deployed draft pages (`staticrypt` wrapper detected in generated HTML)
- Workflow-level verification catches unchanged output via SHA-256 hash comparisons

Still worth repeating before broad reviewer rollout:
- Cross-browser `--remember` behavior over longer sessions
- Mobile UX around password prompt + nav flow

## Giscus Feedback in Practice

Giscus is now pointed to the drafts repo/category via `_config_drafts.yml`, keeping preview feedback separate from production discussions.

Configuration is complete and active in the drafts build. Full end-to-end reviewer comment testing remains a final validation step.

## The Draft Preview Banner

The banner is now implemented in `_layouts/default.html` behind a site-level flag (`draft_preview_site`).

Current banner text:

```text
⚠ DRAFT PREVIEW SITE — unpublished content, may change.
Go to the main site →
```

It appears on drafts pages and links directly to `https://mcgarrah.org`, which makes context-switching between preview and production much clearer for reviewers.

## What Worked

- Config overlay approach cleanly separated production and drafts behavior
- Cross-repo deploy pipeline is now stable and repeatable
- Selective encryption reduced runtime and removed unnecessary churn
- The preview banner made reviewer context immediately clear
- Archive ordering is now deterministic after adding front matter to convenience pages

## What Didn't Work

Early runs surfaced several workflow-level issues:

1. **GitHub Pages setup on empty repo failed**: the repo needed an initial commit before `main` could be selected in Pages settings.
2. **Encryption step appeared hung**: processing many files made `Encrypt HTML with Staticrypt` look stuck even when still running.
3. **Password prompt did not appear after first success**: pages were deployed unencrypted — root cause was Staticrypt API misuse: the `-o` flag doesn't exist in v3.5.4+. Switched to `-d <directory>`, but that flattens directory structures (all output goes to `<dir>/basename.html`). Fixed by processing each file individually to preserve paths.
4. **Deployment included large executable files**: binaries in deploy output triggered GitHub large-file warnings and highlighted the need for artifact filtering.
5. **Full-site encryption created unnecessary overhead**: encrypting already-public content increased runtime and complexity.
6. **Initial verification check was too brittle**: string matching on encrypted output caused false failures; replaced with hash-based verification to detect actual file transformation.
7. **Special-case files broke encryption targeting**: utility documents like `DRAFTS.md` and `SUBDOMAIN-DRAFTS.md` (without front matter) were included in encryption scope. Fixed by filtering to only files matching `YYYY-MM-DD-*.md` pattern (actual posts).
8. **Convenience files broke archive sort order**: The uppercase convenience files (`DRAFTS.md`, `SUBDOMAIN-DRAFTS.md`, `DRAFTS-TODO.md`) had no front matter, so Jekyll used the file's filesystem mtime as their date. This caused them to appear at random positions in the archive depending on when they were last edited — not where they belonged temporally. Fixed by adding minimal front matter (`layout: none`, `date: 2038-01-18`, `sitemap: false`). The pinned date of 2038-01-18 (day before the Unix Y2K38 epoch overflow) sorts them to the very top of the archive where they're easy to find. `layout: none` preserves the raw markdown rendering without any site chrome or CSS formatting. `sitemap: false` keeps them out of the sitemap.

## Lessons Learned

1. Static-site security controls are mostly UX signals unless source content is private.
2. Build verification should check file transformation (hashes), not just string signatures.
3. Tooling behavior under batch mode matters: Staticrypt output flattening was the key hidden trap.
4. A tiny UI affordance (the banner) has outsized impact on reviewer clarity.
5. Convenience/ops files should still get explicit front matter when they participate in Jekyll collections.

---

*This is Part 3 of a three-part series on building a Jekyll draft preview site:*
- **Part 1**: [Exploring every option I considered](/jekyll-draft-preview-site-part-1/)
- **Part 2**: [Refining the design — config, workflow, feedback, and gaps](/jekyll-draft-preview-site-part-2/)
- **Part 3** (this post): The complete implementation
