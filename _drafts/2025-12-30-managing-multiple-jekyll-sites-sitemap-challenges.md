---
title: "Managing Multiple Jekyll Sites Under One Domain: Sitemap Challenges"
layout: post
categories: [web-development, technical]
tags: [jekyll, github-pages, sitemap, multi-site, domain-management, seo, adsense]
excerpt: "How to handle sitemap.xml generation when running multiple Jekyll sites under a single custom domain on GitHub Pages — and why it matters for AdSense approval."
published: false
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

The resume site has no `jekyll-seo-tag` plugin, so its pages lack:
- Structured data (`application/ld+json`)
- Open Graph meta tags
- Canonical URL tags
- Twitter card meta tags

Google sees these pages as part of `mcgarrah.org` but with noticeably worse SEO markup than the blog pages. This inconsistency may contribute to the "site isn't ready" rejections.

### What I've Fixed So Far

| Issue | Status |
|-------|--------|
| Placeholder description | ✅ Fixed — updated to real description |
| Missing `jekyll-seo-tag` | ⏳ Deferred — requires theme integration work |
| Missing `jekyll-sitemap` | ⏳ Deferred — requires cross-repo sitemap strategy |
| `robots.txt` for `/resume/` | ❌ Not possible — `robots.txt` must be at domain root |
| Unified sitemap | ⏳ Deferred — see solutions below |

The rest of this article explores the sitemap problem and potential solutions.

## The Multi-Site Architecture Challenge

My setup involves two separate Jekyll sites:

- **Main blog**: `mcgarrah.github.io` → `https://mcgarrah.org`
- **Resume site**: `resume` repository → `https://mcgarrah.org/resume`

This architecture creates several SEO and sitemap management challenges:

### Problem 1: Fragmented Sitemaps

Each Jekyll site generates its own `sitemap.xml`:
- Main site: `https://mcgarrah.org/sitemap.xml`
- Resume site: `https://mcgarrah.org/resume/sitemap.xml`

Google Search Console expects a unified sitemap for the domain, but gets fragmented coverage.

### Problem 2: Cross-Site URL References

The main blog needs to reference resume pages in its sitemap, but Jekyll's `jekyll-sitemap` plugin only knows about files in its own repository.

### Problem 3: Canonical URL Conflicts

Both sites need consistent canonical URL configuration, but they're managed independently.

## Potential Solutions

### Approach 1: Manual Sitemap Generation

Generate sitemap.xml without plugins using Jekyll's Liquid templating:

```xml
{% raw %}---
layout: null
sitemap: false
---
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {% for post in site.posts %}
    <url>
      <loc>{{ site.url }}{{ post.url }}</loc>
      <lastmod>{{ post.date | date_to_xmlschema }}</lastmod>
    </url>
  {% endfor %}
  
  <!-- Manually add resume site URLs -->
  <url>
    <loc>{{ site.url }}/resume/</loc>
    <lastmod>2025-01-01T00:00:00+00:00</lastmod>
  </url>
</urlset>{% endraw %}
```

### Approach 2: Sitemap Index Files

Use a sitemap index to reference multiple sitemaps:

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

### Approach 3: GitHub Actions Workflow

Use GitHub Actions to generate a unified sitemap across repositories:

```yaml
name: Generate Unified Sitemap
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  generate-sitemap:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout main site
        uses: actions/checkout@v4
        
      - name: Checkout resume site
        uses: actions/checkout@v4
        with:
          repository: mcgarrah/resume
          path: resume-site
          
      - name: Generate unified sitemap
        run: |
          # Combine sitemaps from both sites
          # Implementation details...
```

## Jekyll Sitemap Plugin Limitations

The `jekyll-sitemap` plugin cannot be configured to include additional entries manually. The plugin automatically generates sitemaps based only on files and pages within the current Jekyll site repository.

### Current Plugin Constraints

The `jekyll-sitemap` plugin:

- Only includes pages, posts, and collections from the current repository
- Has no configuration option for manual URL additions
- Cannot reference external sites or other repositories
- Does not support sitemap index files

### Workaround Solutions

#### Solution 1: Custom Sitemap Template (Recommended)

Replace the plugin with a custom `sitemap.xml` template that allows manual entries:

```xml
{% raw %}---
layout: null
sitemap: false
---
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {% for post in site.posts %}
    <url>
      <loc>{{ site.url }}{{ post.url }}</loc>
      <lastmod>{{ post.date | date_to_xmlschema }}</lastmod>
    </url>
  {% endfor %}
  
  {% for page in site.pages %}
    {% unless page.sitemap == false %}
      <url>
        <loc>{{ site.url }}{{ page.url }}</loc>
        {% if page.last_modified_at %}
          <lastmod>{{ page.last_modified_at | date_to_xmlschema }}</lastmod>
        {% endif %}
      </url>
    {% endunless %}
  {% endfor %}
  
  <!-- Manual entries for external sites -->
  <url>
    <loc>{{ site.url }}/resume/</loc>
    <lastmod>2025-01-01T00:00:00+00:00</lastmod>
  </url>
  <url>
    <loc>{{ site.url }}/resume/print/</loc>
    <lastmod>2025-01-01T00:00:00+00:00</lastmod>
  </url>
</urlset>{% endraw %}
```

#### Solution 2: Configuration-Based Manual Entries

Add manual URLs to `_config.yml` for easier maintenance:

```yaml
# _config.yml
sitemap_urls:
  - url: "/resume/"
    lastmod: "2025-01-01"
  - url: "/resume/print/"
    lastmod: "2025-01-01"
  - url: "/resume/pdf/"
    lastmod: "2025-01-01"
```

Then reference in custom sitemap:

```xml
{% raw %}<!-- In custom sitemap.xml -->
{% for manual_url in site.sitemap_urls %}
  <url>
    <loc>{{ site.url }}{{ manual_url.url }}</loc>
    <lastmod>{{ manual_url.lastmod }}T00:00:00+00:00</lastmod>
  </url>
{% endfor %}{% endraw %}
```

#### Solution 3: Hybrid Approach

Keep the plugin for automatic generation, then post-process with GitHub Actions to add manual entries.

## Implementation Challenges

### Plugin Development Status

Current `jekyll-sitemap` plugin issues:

- [Possibility to add pages that are not in the project #295](https://github.com/jekyll/jekyll-sitemap/issues/295)
- [Allow generating sitemap_index files #300](https://github.com/jekyll/jekyll-sitemap/pull/300)

### Cross-Repository Coordination

Changes to either site need to trigger sitemap regeneration, requiring:

- Webhook coordination between repositories
- Shared deployment workflows
- Consistent URL structure maintenance

### SEO Considerations

- Canonical URL consistency across sites
- Proper robots.txt configuration
- Google Search Console property management

## Alternative Architectures

### Single Repository Approach

Move resume content into main repository as a collection:

```yaml
# _config.yml
collections:
  resume:
    output: true
    permalink: /resume/:name/
```

### Subdomain Approach

Separate sites completely:

- Main blog: `https://blog.mcgarrah.org`
- Resume: `https://resume.mcgarrah.org`

## Future Research

- [cicirello/generate-sitemap](https://github.com/cicirello/generate-sitemap) GitHub Action
- Jekyll multi-site management best practices
- Google Search Console multi-property strategies

## References

- [Jekyll Sitemap Generator Plugin](https://github.com/jekyll/jekyll-sitemap)
- [Jekyll - Generating sitemap.xml without a plugin](https://www.independent-software.com/generating-a-sitemap-xml-with-jekyll-without-a-plugin.html)
- [Jekyll-Sitemap: adding URLs not in project](https://talk.jekyllrb.com/t/jekyll-sitemap-adding-url-that-are-not-in-the-project/6920/3)
- [Multi-site sitemap discussions](https://www.reddit.com/r/Jekyll/comments/1egcfsh/how_to_include_urls_from_secondary_project_in/)

## My Recommended Path Forward

After working through the AdSense approval process and hitting these issues firsthand, here's what I'd actually recommend for sites in this situation:

### Short Term: Sitemap Index File

The sitemap index approach (Approach 2 above) is the lowest-effort solution that solves the Google Search Console problem. Create a `sitemapindex.xml` at the domain root that references both sitemaps, and submit that to Search Console instead of the individual sitemaps.

This doesn't require changes to either Jekyll site's build process — just a static file in the main blog repo.

### Medium Term: Add `jekyll-seo-tag` to Resume

The resume site's lack of structured data is a real SEO gap. Adding `jekyll-seo-tag` to the resume's Gemfile and including `{% seo %}` in its `<head>` would bring its pages up to the same standard as the blog. This is independent of the sitemap problem.

### Long Term: Evaluate Merging

I've written a [separate analysis of merging the two sites](/merging-two-jekyll-websites-architectural-analysis/) into a single repository. The collection-based approach is technically sound but requires significant work. The sitemap and SEO problems are the strongest argument for eventually doing this merge.

## Related Articles

- [Google AdSense Approval Failure: Debugging the 'Site Isn't Ready' Rejection](/adsense-approval-failure-remediation/) — Where the multi-site SEO gaps were discovered
- [Improving E-E-A-T Signals for Google AdSense Approval on Jekyll](/improving-eeat-jekyll-adsense/) — Broader SEO improvements
- [Fixing AdSense Verification Without Breaking GDPR](/adsense-verification-gdpr-script-loading-fix/) — The verification script fix
- [Merging Two Jekyll Websites: Architectural Analysis](/merging-two-jekyll-websites-architectural-analysis/) — Full merge feasibility study
- [Jekyll SEO, Sitemap, and Canonical URL Fixes](/jekyll-seo-sitemap-canonical-url-fixes/) — Earlier SEO work on the main blog

---

*This article explores the complexities of managing multiple Jekyll sites under one domain. The implementation details and final solution will be documented in a future update.*
