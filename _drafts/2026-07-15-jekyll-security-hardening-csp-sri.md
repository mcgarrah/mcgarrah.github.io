---
title: "Hardening a Jekyll Blog: CSP, SRI, and Security Headers"
layout: post
categories: [web-development, jekyll, security]
tags: [jekyll, security, csp, sri, headers, cdn, github-pages]
date: 2026-07-15
last_modified_at: 2026-07-15
excerpt: "My Jekyll blog loads Mermaid, KaTeX, and Clipboard.js from CDNs with no integrity verification. There's no Content Security Policy restricting what scripts can execute. Time to add SRI hashes, CSP headers, and evaluate self-hosting critical libraries."
description: "Adding Subresource Integrity (SRI) hashes, Content Security Policy (CSP), and security headers to a Jekyll blog hosted on GitHub Pages. Covers CDN trust, self-hosting trade-offs, and the limitations of static hosting."
seo:
  type: BlogPosting
  date_published: 2026-07-15
  date_modified: 2026-07-15
---

Every page on this blog loads JavaScript from three CDNs: Mermaid for diagrams, KaTeX for math, and Clipboard.js for code copy buttons. If any of those CDNs are compromised, my readers execute malicious code. There's nothing stopping it — no integrity checks, no Content Security Policy, no restrictions on what scripts can run.

For a personal blog, the risk is low. But the fix is straightforward, and it's the kind of defense-in-depth that matters at scale.

<!-- excerpt-end -->

## Current State

<!-- TODO: List all external script/style loads -->
<!-- TODO: Which CDNs are used (jsdelivr, cdnjs, etc.) -->
<!-- TODO: What happens if a CDN is compromised today? -->

## Subresource Integrity (SRI)

<!-- TODO: What SRI is and how it works -->
<!-- TODO: Generate hashes for current CDN resources -->
<!-- TODO: Add integrity="" and crossorigin="" attributes -->
<!-- TODO: What happens when CDN versions change (Dependabot trigger) -->

## Content Security Policy (CSP)

<!-- TODO: What CSP prevents (XSS, unauthorized scripts) -->
<!-- TODO: GitHub Pages limitations (no custom HTTP headers) -->
<!-- TODO: Meta tag CSP as alternative -->
<!-- TODO: Draft a CSP that allows current CDNs + inline scripts -->
<!-- TODO: Report-only mode for testing -->

## Self-Hosting vs CDN

<!-- TODO: Trade-offs: repo size, manual updates, no external dependency -->
<!-- TODO: package.json already tracks versions -->
<!-- TODO: Build step to copy from node_modules to assets/ -->
<!-- TODO: Decision: which libraries to self-host, which to keep on CDN -->

## Additional Security Headers

<!-- TODO: HSTS (GitHub Pages handles at infra level) -->
<!-- TODO: X-Frame-Options / X-Content-Type-Options via meta tags -->
<!-- TODO: Referrer-Policy -->

## Testing

<!-- TODO: Browser DevTools console for CSP violations -->
<!-- TODO: securityheaders.com scan results -->
<!-- TODO: Lighthouse security audit -->

## Related Articles

- [Implementing GDPR Compliance for Jekyll with AdSense](/implementing-gdpr-compliance-jekyll-adsense/) — Privacy and consent framework
- [Jekyll GitHub Actions CI/CD Pipeline](/jekyll-github-actions-cicd-pipeline/) — Where SRI hash updates would be automated
