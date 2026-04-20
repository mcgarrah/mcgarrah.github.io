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

> **Implementation status (in progress):** The system is live but still being tuned. The notes below include concrete issues encountered during first-run deployments so the final version of this post captures real behavior, not just design intent.

## Creating the Drafts Repo

<!-- TODO: Document repo creation, Pages setup, Discussions enablement -->

> **Implementation note:** GitHub Pages setup fails on a truly empty repo because there is no `main` branch to select yet. The repo needs an initial commit first, so initialize with a `README.md` or create any file before enabling Pages.

## DNS Configuration

<!-- TODO: Document Porkbun CNAME setup, GitHub Pages custom domain verification, HTTPS enforcement -->

## The Final Config Overlay

<!-- TODO: Final _config_drafts.yml with real Giscus repo_id and category_id -->

## The Final GitHub Actions Workflow

<!-- TODO: Final deploy-drafts.yml with any changes from testing -->

## Staticrypt Testing Results

<!-- TODO: Document testing of:
  - Password prompt appearance
  - --remember navigation between pages
  - localStorage behavior across browsers
  - Giscus loading after decryption
  - Mobile experience
-->

## Giscus Feedback in Practice

<!-- TODO: Document Giscus setup on drafts repo, testing with reviewers -->

## The Draft Preview Banner

<!-- TODO: Final banner implementation, screenshot -->

## What Worked

<!-- TODO: Successes and things that went smoothly -->

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

<!-- TODO: Retrospective on the whole process -->

---

*This is Part 3 of a three-part series on building a Jekyll draft preview site:*
- **Part 1**: [Exploring every option I considered](/jekyll-draft-preview-site-part-1/)
- **Part 2**: [Refining the design — config, workflow, feedback, and gaps](/jekyll-draft-preview-site-part-2/)
- **Part 3** (this post): The complete implementation
