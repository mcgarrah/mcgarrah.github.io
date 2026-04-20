---
title: "Taming Tag Sprawl: Consolidating 138 Singleton Tags in Jekyll"
layout: post
categories: [web-development, jekyll]
tags: [jekyll, tags, seo, content-organization, maintenance]
date: 2026-07-10
last_modified_at: 2026-07-10
excerpt: "My Jekyll blog has 237 tags — 138 of which are used on exactly one post. Each generates a tag page with a single entry. Time to audit, merge, and clean up the tag system so it actually helps readers find related content."
description: "Auditing and consolidating singleton tags in a Jekyll blog. How to identify tag sprawl, merge related tags, and make the tag system useful for navigation and SEO."
seo:
  type: BlogPosting
  date_published: 2026-07-10
  date_modified: 2026-07-10
---

My tag system has gotten out of control. 237 tags across 139 posts — and 138 of those tags appear on exactly one post. Each singleton generates a tag page with a single entry, marked `noindex` by the tag generator plugin. They dilute navigation and provide zero value to readers.

Time to fix it.

<!-- excerpt-end -->

## The Problem

<!-- TODO: Show the data — how many tags, how many singletons, examples of redundant tags -->
<!-- TODO: grep/script to identify all singleton tags -->
<!-- TODO: Examples of obvious merges: dart-sass → sass, serial-console → configuration -->

## The Audit Process

<!-- TODO: Script to generate tag usage report -->
<!-- TODO: Decision framework: when to merge vs when to keep a singleton -->
<!-- TODO: Categories vs tags — what belongs where -->

## The Consolidation

<!-- TODO: Document the actual merges performed -->
<!-- TODO: Before/after tag count -->
<!-- TODO: Impact on generated pages -->

## Results

<!-- TODO: Tag count reduction -->
<!-- TODO: Generated page reduction -->
<!-- TODO: Does the /tags/ page look better now? -->

## Related Articles

- [Jekyll Tag and Category Generator Plugin](/jekyll-tag-category-generator-plugin/) — The plugin that generates tag pages
- [Jekyll Sitemap Bloat: Tags, Categories, and Pagination](/jekyll-sitemap-bloat-tags-categories-pagination/) — Previous cleanup of generated pages
