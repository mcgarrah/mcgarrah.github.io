---
title: "Adding Post Series Navigation to Jekyll"
layout: post
categories: [web-development, jekyll]
tags: [jekyll, navigation, series, collections, user-experience]
date: 2026-07-20
last_modified_at: 2026-07-20
excerpt: "My blog has natural multi-part series — ZFS boot mirrors, Caddy reverse proxy, Draft Preview Site — but no automated previous/next navigation between parts. The Proxmox & Ceph Guide page is a manual solution. Time to automate it."
description: "Implementing automated post series navigation in Jekyll with previous/next links, series index pages, and structured data. Covers Liquid-based approaches without plugins for GitHub Pages compatibility."
seo:
  type: BlogPosting
  date_published: 2026-07-20
  date_modified: 2026-07-20
---

I have at least six multi-part series on this blog: ZFS boot mirrors (3 parts), Caddy reverse proxy (2 parts), Draft Preview Site (3 parts), Run Jekyll (7 parts), and more. Each part links to the others manually in the intro and footer. The [Proxmox & Ceph Guide](/proxmox-ceph-guide/) page is a hand-curated index.

This doesn't scale. When I add a new post to a series, I have to update every other post in that series. Time to automate previous/next navigation.

<!-- excerpt-end -->

## Current State

<!-- TODO: List all existing series and their manual cross-references -->
<!-- TODO: How the Proxmox & Ceph Guide page works (manual curation) -->
<!-- TODO: Pain points: adding a new part requires editing all existing parts -->

## Design Goals

<!-- TODO: Automatic previous/next links at bottom of series posts -->
<!-- TODO: Series name and part number in post metadata -->
<!-- TODO: Optional series index page (auto-generated or manual) -->
<!-- TODO: Structured data for series (schema.org) -->
<!-- TODO: No plugins (GitHub Pages compatible) — pure Liquid -->

## Implementation Options

<!-- TODO: Option 1: Front matter series field + Liquid loop -->
<!-- TODO: Option 2: Jekyll collections (separate from posts) -->
<!-- TODO: Option 3: Data file defining series membership -->
<!-- TODO: Comparison and decision -->

## The Implementation

<!-- TODO: Front matter convention (series: "name", series_part: N) -->
<!-- TODO: Liquid include for previous/next navigation -->
<!-- TODO: Styling the navigation component -->
<!-- TODO: Retroactively adding series metadata to existing posts -->

## Results

<!-- TODO: Screenshot of the navigation component -->
<!-- TODO: How many posts got series metadata -->
<!-- TODO: Does it work with the existing guide page? -->

## Related Articles

- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — Manual series index this could automate
- [Jekyll Content Plumbing: Permalinks and Reading Time](/jekyll-content-plumbing-permalinks-reading-time/) — Previous navigation improvements
