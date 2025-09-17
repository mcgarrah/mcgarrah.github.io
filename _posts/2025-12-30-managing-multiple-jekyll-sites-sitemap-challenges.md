---
title: "Managing Multiple Jekyll Sites Under One Domain: Sitemap Challenges"
layout: post
categories: [web-development, technical]
tags: [jekyll, github-pages, sitemap, multi-site, domain-management]
excerpt: "How to handle sitemap.xml generation when running multiple Jekyll sites under a single custom domain on GitHub Pages."
date: 2025-12-30
published: true
---

Running multiple Jekyll sites under a single custom domain creates unique challenges for SEO and sitemap management. This post explores the complexities of managing **mcgarrah.org** (main blog) and **mcgarrah.org/resume** (separate Jekyll site) as distinct GitHub repositories while maintaining proper search engine indexing.

<!-- excerpt-end -->

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
---
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
</urlset>
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
---
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
</urlset>
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
<!-- In custom sitemap.xml -->
{% for manual_url in site.sitemap_urls %}
  <url>
    <loc>{{ site.url }}{{ manual_url.url }}</loc>
    <lastmod>{{ manual_url.lastmod }}T00:00:00+00:00</lastmod>
  </url>
{% endfor %}
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

---

*This article explores the complexities of managing multiple Jekyll sites under one domain. The implementation details and final solution will be documented in a future update.*