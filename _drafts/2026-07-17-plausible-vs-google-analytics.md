---
title: "Replacing Google Analytics with Plausible: Is It Worth $9/Month?"
layout: post
categories: [web-development, privacy]
tags: [analytics, plausible, google-analytics, privacy, gdpr, jekyll]
date: 2026-07-17
last_modified_at: 2026-07-17
excerpt: "Google Analytics requires GDPR consent banners, loads third-party JavaScript, and feeds data to Google's advertising machine. Plausible is lightweight, cookie-free, and GDPR-compliant by default. But is it worth paying for what Google gives away free?"
description: "Comparing Google Analytics and Plausible Analytics for a Jekyll blog. Covers privacy implications, GDPR consent requirements, implementation complexity, data quality, and whether the $9/month cost is justified."
seo:
  type: BlogPosting
  date_published: 2026-07-17
  date_modified: 2026-07-17
---

My GDPR consent implementation exists primarily because of Google Analytics. The cookie banner, the consent state management, the conditional script loading — all of it is there because GA sets cookies and requires explicit consent under GDPR. What if I just... didn't use GA?

Plausible Analytics is ~1KB of JavaScript, sets no cookies, requires no consent banner, and costs $9/month. Is the simplification worth the price?

<!-- excerpt-end -->

## The Current Setup

<!-- TODO: What GA provides today (traffic, sources, pages, events) -->
<!-- TODO: The GDPR overhead: consent banner, conditional loading, region detection -->
<!-- TODO: How much of GA's data do I actually look at? -->

## What Plausible Offers

<!-- TODO: Feature comparison table -->
<!-- TODO: What you lose (detailed user flows, demographics, custom events) -->
<!-- TODO: What you gain (simplicity, privacy, no consent needed, faster page loads) -->

## The GDPR Simplification

<!-- TODO: If no cookies → no consent needed for analytics -->
<!-- TODO: Could simplify or remove the consent banner entirely? -->
<!-- TODO: What else requires consent? (AdSense still does) -->
<!-- TODO: Net effect on the GDPR implementation -->

## Implementation

<!-- TODO: Plausible script tag (single line) -->
<!-- TODO: Jekyll integration (config variable, conditional include) -->
<!-- TODO: Self-hosted Plausible option (free but requires server) -->
<!-- TODO: Could run on the Proxmox homelab? -->

## The Cost Question

<!-- TODO: $9/month = $108/year for a hobby blog -->
<!-- TODO: What does "free" GA actually cost? (complexity, privacy, consent overhead) -->
<!-- TODO: Self-hosted Plausible as middle ground -->

## Decision

<!-- TODO: What I decided and why -->

## Related Articles

- [The Google Services Tax on a Simple Blog](/google-service-sprawl/) — The frustration that prompted this evaluation
- [Implementing GDPR Compliance for Jekyll with AdSense](/implementing-gdpr-compliance-jekyll-adsense/) — The consent system that might be simplified
