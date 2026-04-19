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

> **TODO:** This post will be written after the implementation is complete. The sections below are placeholders for the content that will be filled in during implementation.

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

<!-- TODO: Problems encountered, workarounds, things I changed from the design -->

## Lessons Learned

<!-- TODO: Retrospective on the whole process -->

---

*This is Part 3 of a three-part series on building a Jekyll draft preview site:*
- **Part 1**: [Exploring every option I considered](/jekyll-draft-preview-site-part-1/)
- **Part 2**: [Refining the design — config, workflow, feedback, and gaps](/jekyll-draft-preview-site-part-2/)
- **Part 3** (this post): The complete implementation
