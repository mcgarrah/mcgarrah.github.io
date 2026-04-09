---
title: "Managing Multiple Jekyll Sites Under One Domain: Sitemap Challenges"
layout: post
categories: [web-development, technical]
tags: [jekyll, github-pages, sitemap, multi-site, domain-management, seo, adsense]
excerpt: "How to handle sitemap.xml generation when running multiple Jekyll sites under a single custom domain on GitHub Pages — and why it matters for AdSense approval."
description: "Practical guide to managing sitemaps, robots.txt, and SEO consistency when running multiple Jekyll sites under one domain on GitHub Pages, with solutions ranging from sitemap index files to full repository merges."
date: 2026-04-09
last_modified_at: 2026-04-09
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-09
  date_modified: 2026-04-09
---

Running multiple Jekyll sites under a single custom domain creates unique challenges for SEO and sitemap management. This post explores the complexities of managing **mcgarrah.org** (main blog) and **mcgarrah.org/resume** (separate Jekyll site) as distinct GitHub repositories while maintaining proper search engine indexing.

<!-- excerpt-end -->

## Why This Matters: The AdSense Wake-Up Call

This isn't just a theoretical SEO concern. During my [ongoing AdSense approval debugging](/adsense-approval-failure-remediation/), I discovered that the multi-site architecture creates concrete problems that affect how Google evaluates the domain:

### The `robots.txt` Problem

The `robots.txt` specification requires the file to live at the **domain root** — `https://mcgarrah.org/robots.txt`. You cannot place a `robots.txt` at `/resume/robots.txt` and have crawlers respect it. This means the main blog's `robots.txt` governs the entire domain, but it has no awareness of the resume site's structure.

My blog's `robots.txt` allows `/resume/` (good), but the resume site has no way to add its own crawl directives.

### The Placeholder Description Problem

The resume site shipped with the default theme description: `"A beautiful Jekyll theme for creating a Resume"`. Google crawls `mcgarrah.org/resume` as part of the same domain it's evaluating for AdSense. Template placeholder text on any subpath hurts the overall domain quality signal.

This was an easy fix — just updating `_config.yml` in the resume repo — but it illustrates how a separate repository can silently degrade the main site's SEO without anyone noticing.

### The Missing SEO Infrastructure

The resume site originally had no `jekyll-seo-tag` plugin, so its pages lacked:
- Structured data (`application/ld+json`)
- Open Graph meta tags
- Canonical URL tags
- Twitter card meta tags

Google saw these pages as part of `mcgarrah.org` but with noticeably worse SEO markup than the blog pages. This inconsistency may have contributed to the "site isn't ready" rejections.

### What I've Fixed So Far

| Issue | Status |
|-------|--------|
| Placeholder description | ✅ Fixed — updated to real description |
| Missing `jekyll-seo-tag` | ✅ Fixed — added plugin and `{% seo %}` tag to resume head |
| Missing `jekyll-sitemap` | ✅ Fixed — added plugin to resume repo |
| `robots.txt` for `/resume/` | ❌ Not possible — `robots.txt` must be at domain root |
| Unified sitemap | ✅ Fixed — `sitemapindex.xml` at domain root references both sitemaps |

The rest of this article explores the sitemap problem and potential solutions.

## The Multi-Site Architecture

My setup involves two separate Jekyll sites deployed to the same domain:

- **Main blog**: `mcgarrah.github.io` → `https://mcgarrah.org`
- **Resume site**: `resume` repository → `https://mcgarrah.org/resume`

GitHub Pages makes this easy to set up — the main repo gets the custom domain, and project repos deploy to subpaths. But it creates several SEO problems that aren't obvious until you start looking at what Google actually sees.

### Problem 1: Fragmented Sitemaps

Each Jekyll site generates its own `sitemap.xml`:
- Main site: `https://mcgarrah.org/sitemap.xml`
- Resume site: `https://mcgarrah.org/resume/sitemap.xml`

Google Search Console expects a unified sitemap for the domain, but gets fragmented coverage. The main sitemap has no knowledge of the resume pages, and the resume sitemap only covers its own content.

### Problem 2: Cross-Site URL References

The main blog links to `/resume/` in its navigation and footer, but Jekyll's `jekyll-sitemap` plugin only knows about files in its own repository. The resume pages are invisible to the main site's sitemap generation.

### Problem 3: Canonical URL Conflicts

Both sites need consistent canonical URL configuration, but they're managed independently. If one site uses `https://mcgarrah.org` and the other uses `https://www.mcgarrah.org`, Google sees conflicting signals about the authoritative domain.

## Potential Solutions

### Approach 1: Sitemap Index File (Recommended for Quick Wins)

The [sitemaps.org protocol](https://www.sitemaps.org/protocol.html) supports sitemap index files that reference multiple sitemaps. Create a `sitemapindex.xml` at the domain root:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://mcgarrah.org/sitemap.xml</loc>
    <lastmod>2025-01-01T00:00:00+00:00</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://mcgarrah.org/resume/sitemap.xml</loc>
    <lastmod>2025-01-01T00:00:00+00:00</lastmod>
  </sitemap>
</sitemapindex>
```

Submit this to Google Search Console instead of the individual sitemaps. This is the lowest-effort solution — just a static file in the main blog repo, no changes to either site's build process.

The downside: you need to ensure the resume site actually generates a `sitemap.xml` (I've since added `jekyll-sitemap` to the resume repo).

### Approach 2: Custom Sitemap Template

Replace the `jekyll-sitemap` plugin with a custom `sitemap.xml` Liquid template that includes manual entries for the resume site:

```xml
{% raw %}---
layout: null
sitemap: false
---
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {% for post in site.posts %}
    {% unless post.sitemap == false %}
    <url>
      <loc>{{ site.url }}{{ post.url }}</loc>
      <lastmod>{{ post.last_modified_at | default: post.date | date_to_xmlschema }}</lastmod>
    </url>
    {% endunless %}
  {% endfor %}

  {% for page in site.pages %}
    {% unless page.sitemap == false %}
    <url>
      <loc>{{ site.url }}{{ page.url | replace: '/index.html', '/' }}</loc>
      {% if page.last_modified_at %}
        <lastmod>{{ page.last_modified_at | date_to_xmlschema }}</lastmod>
      {% endif %}
    </url>
    {% endunless %}
  {% endfor %}

  <!-- Cross-repo entries for resume site -->
  {% for entry in site.sitemap_urls %}
  <url>
    <loc>{{ site.url }}{{ entry.url }}</loc>
    <lastmod>{{ entry.lastmod }}T00:00:00+00:00</lastmod>
  </url>
  {% endfor %}
</urlset>{% endraw %}
```

With corresponding `_config.yml` entries:

```yaml
sitemap_urls:
  - url: "/resume/"
    lastmod: "2025-01-01"
  - url: "/resume/print/"
    lastmod: "2025-01-01"
```

This gives you full control but means maintaining the sitemap template yourself instead of relying on the plugin. You lose automatic handling of new pages and collections.

### Approach 3: GitHub Actions Post-Processing

Keep the `jekyll-sitemap` plugin for automatic generation, then use a GitHub Actions step to inject additional URLs after the build:

```yaml
- name: Add resume URLs to sitemap
  run: |
    # Insert resume entries before closing </urlset>
    sed -i '/<\/urlset>/i \
    <url><loc>https://mcgarrah.org/resume/</loc></url>\n\
    <url><loc>https://mcgarrah.org/resume/print/</loc></url>' \
    _site/sitemap.xml
```

This is a hack, but it works without changing the Jekyll build process. The `sed` command inserts entries before the closing `</urlset>` tag.

## Jekyll Sitemap Plugin Limitations

The `jekyll-sitemap` plugin is deliberately simple. It:

- Only includes pages, posts, and collections from the current repository
- Has no configuration option for manual URL additions
- Cannot reference external sites or other repositories
- Does not support sitemap index files

These are known limitations. The plugin's issue tracker has open requests for both features:

- [Possibility to add pages that are not in the project #295](https://github.com/jekyll/jekyll-sitemap/issues/295)
- [Allow generating sitemap_index files #300](https://github.com/jekyll/jekyll-sitemap/pull/300)

Neither has been merged as of this writing.

## Alternative Architectures

If the sitemap problem is painful enough, there are more fundamental solutions:

### Single Repository Approach

Move resume content into the main repository as a Jekyll collection:

```yaml
collections:
  resume:
    output: true
    permalink: /resume/:name/
```

This eliminates the multi-site problem entirely — one repo, one build, one sitemap. But it requires significant work to merge two different Jekyll themes and data structures. I've written a [separate analysis of this approach](/merging-two-jekyll-websites-architectural-analysis/).

### Subdomain Approach

Separate the sites completely with subdomains:

- Main blog: `https://mcgarrah.org` (or `https://blog.mcgarrah.org`)
- Resume: `https://resume.mcgarrah.org`

Each subdomain gets its own `robots.txt`, `sitemap.xml`, and Google Search Console property. This is cleaner from an SEO perspective but means the resume is no longer under the main domain's authority.

## My Recommended Path Forward

After working through the AdSense approval process and hitting these issues firsthand, here's what I'd actually recommend for sites in this situation:

### Short Term: Sitemap Index File

The sitemap index approach is the lowest-effort solution that solves the Google Search Console problem. Create a `sitemapindex.xml` at the domain root that references both sitemaps, and submit that to Search Console instead of the individual sitemaps.

This doesn't require changes to either Jekyll site's build process — just a static file in the main blog repo.

### Medium Term: Add `jekyll-seo-tag` to Resume

The resume site's lack of structured data is a real SEO gap. Adding `jekyll-seo-tag` to the resume's Gemfile and including `{% seo %}` in its `<head>` would bring its pages up to the same standard as the blog. This is independent of the sitemap problem.

### Long Term: Evaluate Merging

The [collection-based integration approach](/merging-two-jekyll-websites-architectural-analysis/) is technically sound but requires significant work. The sitemap and SEO problems are the strongest argument for eventually doing this merge — but it's a project, not a quick fix.

## The Bigger Picture

The multi-site architecture on GitHub Pages is a common pattern — many people have a blog and a portfolio or resume as separate repos. It works great for deployment and maintenance. But from Google's perspective, it's one domain with inconsistent SEO infrastructure, fragmented sitemaps, and no unified crawl control.

If you're running this pattern and care about SEO (or AdSense approval), you need to actively manage the gaps. The sitemap index file is the minimum viable fix. Everything else is optimization.

## References

- [Jekyll Sitemap Generator Plugin](https://github.com/jekyll/jekyll-sitemap)
- [Sitemaps.org Protocol — Sitemap Index](https://www.sitemaps.org/protocol.html#index)
- [Jekyll - Generating sitemap.xml without a plugin](https://www.independent-software.com/generating-a-sitemap-xml-with-jekyll-without-a-plugin.html)
- [Jekyll-Sitemap: adding URLs not in project](https://talk.jekyllrb.com/t/jekyll-sitemap-adding-url-that-are-not-in-the-project/6920/3)
- [cicirello/generate-sitemap](https://github.com/cicirello/generate-sitemap) — GitHub Action for sitemap generation

## Related Articles

- [Your Jekyll Sitemap Is 60% Garbage](/jekyll-sitemap-bloat-tags-categories-pagination/) — Cleaning up auto-generated sitemap bloat
- [Your Jekyll Theme Is Probably Missing head and body Tags](/jekyll-theme-missing-head-body-tags/) — HTML structure problems in Jekyll themes
- [Google AdSense Approval Failure: Debugging the 'Site Isn't Ready' Rejection](/adsense-approval-failure-remediation/) — Where the multi-site SEO gaps were discovered
- [Improving E-E-A-T Signals for Google AdSense Approval on Jekyll](/improving-eeat-jekyll-adsense/) — Broader SEO improvements
- [Fixing AdSense Verification Without Breaking GDPR](/adsense-verification-gdpr-script-loading-fix/) — The verification script fix
- [Jekyll SEO, Sitemap, and Canonical URL Fixes](/jekyll-seo-sitemap-canonical-url-fixes/) — Earlier SEO work on the main blog
