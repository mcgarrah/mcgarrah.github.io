---
title: "Your Jekyll Sitemap Is 60% Garbage"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, sitemap, seo, tags, categories, pagination, github-pages, ruby, plugins]
excerpt: "I audited my Jekyll sitemap and found that 262 of 434 URLs were auto-generated tag pages, category pages, and pagination — most with a single post. Here's how to clean it up without losing anything."
description: "How to audit and fix Jekyll sitemap bloat from auto-generated tag pages, category pages, and pagination. Includes Ruby plugin fixes, noindex patterns, and a CI/CD gotcha with static file timestamps."
date: 2026-04-07
last_modified_at: 2026-04-07
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-07
  date_modified: 2026-04-07
---

My Jekyll blog had 434 URLs in its sitemap. Sounds like a well-established site with lots of content, right? Here's the breakdown:

| URL Type | Count | % of Sitemap |
|----------|-------|-------------|
| Blog posts | 125 | 29% |
| Static pages (about, contact, etc.) | 8 | 2% |
| Tag pages | 209 | 48% |
| Category pages | 56 | 13% |
| Pagination pages | 31 | 7% |
| Static files (PDFs) | 7 | 2% |

**60% of my sitemap was auto-generated taxonomy and pagination pages.** Most tag pages had a single post. Some category pages had one or two. Every pagination page was just a different slice of the same post list. And the PDFs were switch manuals from 2007 that didn't need indexing.

Google was seeing a site that was mostly machine-generated index pages with little unique content. Not a great signal when you're trying to get AdSense approved.

<!-- excerpt-end -->

## The Audit

If you're running Jekyll with `jekyll-sitemap`, a tag/category generator plugin, and `jekyll-paginate`, you probably have the same problem. Here's how to check:

```bash
# Build your site
bundle exec jekyll build

# Total URLs
grep -c "<loc>" _site/sitemap.xml

# Breakdown
echo "Tags:       $(grep -c '/tags/' _site/sitemap.xml)"
echo "Categories: $(grep -c '/categories/' _site/sitemap.xml)"
echo "Pagination: $(grep '/page[0-9]' _site/sitemap.xml | wc -l)"
echo "PDFs:       $(grep -c 'assets/pdfs' _site/sitemap.xml)"

# Check for duplicates while you're at it
grep -oP '(?<=<loc>)[^<]+' _site/sitemap.xml | sort | uniq -c | sort -rn | awk '$1 > 1'
```

If your tag and category counts are higher than your post count, you have a problem.

## Why This Matters

Google's crawl budget is finite. When Googlebot visits your site, it decides how many pages to crawl based on signals about your site's quality and size. If 60% of the URLs in your sitemap lead to pages with a single post listing, Google learns that most of your site isn't worth crawling deeply.

For AdSense specifically, reviewers (human or automated) look at the ratio of substantive content to thin/auto-generated pages. A sitemap dominated by taxonomy pages looks like a site that's padding its page count.

## Fix 1: Exclude Tag and Category Pages from Sitemap

If you're using a custom tag/category generator plugin (most Jekyll sites with tag pages are), add `sitemap: false` in the page initialization:

```ruby
class TagPage < Page
  def initialize(site, base, tag, posts)
    @site = site
    @base = base
    @dir = File.join('tags', tag.downcase.gsub(' ', '-'))
    @name = 'index.html'

    self.process(@name)
    self.read_yaml(File.join(base, '_layouts'), 'tag_page.html')
    self.data['tag'] = tag
    self.data['posts'] = posts
    self.data['title'] = "Posts tagged with \"#{tag}\""
    self.data['sitemap'] = false  # <-- add this
  end
end
```

Do the same for your `CategoryPage` class. The `jekyll-sitemap` plugin checks `page.sitemap != false` when building the sitemap, so this cleanly excludes them.

The pages still render and are accessible via your `/tags/` and `/categories/` index pages. They're just not advertised to crawlers individually.

## Fix 2: noindex on Thin Taxonomy Pages

Excluding pages from the sitemap tells Google "don't prioritize crawling this." But if Google discovers the page through internal links (which it will — your tag cloud links to every tag page), it may still index it.

For tag and category pages with fewer than 3 posts, add a `noindex` flag:

```ruby
self.data['sitemap'] = false
self.data['noindex'] = true if posts.size < 3
```

Then in your `_layouts/default.html`, inside `<head>`:

```html
{% raw %}{% if page.noindex %}
<meta name="robots" content="noindex, follow">
{% endif %}{% endraw %}
```

The `follow` part is important — it tells Google "don't index this page, but do follow the links on it." This way Google still discovers your actual posts through tag pages, it just doesn't waste an index slot on a page that lists a single post.

**My results:** 161 tag pages and 34 category pages got `noindex`. The remaining 48 tag pages and 21 category pages with 3+ posts stay indexable — those are genuinely useful navigation pages.

## Fix 3: Exclude Pagination Pages

Pagination pages (`/page2/`, `/page3/`, etc.) are the same content in different slices. They don't need to be in the sitemap.

This one is trickier because `jekyll-paginate` creates pagination pages internally — you don't control their initialization. My first attempt used a Jekyll hook:

```ruby
# DON'T DO THIS — it breaks pagination
Jekyll::Hooks.register :pages, :post_init do |page|
  if page.url =~ %r{^/page\d+/}
    page.data['sitemap'] = false
  end
end
```

**This broke my entire site.** The `:post_init` hook fires during page initialization, before `jekyll-paginate` has created the pagination pages. It interfered with the paginator's template detection, causing the homepage to display as page 32 of 32 (oldest posts first) and preventing pagination directories from being created at all.

The fix is to use a Generator with `priority :lowest`, which runs *after* `jekyll-paginate` has finished:

```ruby
class PaginationSitemapExcluder < Generator
  safe true
  priority :lowest

  def generate(site)
    site.pages.each do |page|
      if page.dir =~ %r{^/page\d+}
        page.data['sitemap'] = false
      end
    end
  end
end
```

This iterates the final page list after all generators (including the paginator) have run, and sets `sitemap: false` on any page in a `/page\d+/` directory.

## Fix 4: Exclude Static Files with Stale Timestamps

If you have PDFs or other static files in your site, `jekyll-sitemap` includes them with their filesystem `modified_time` as the `lastmod`. The problem: when GitHub Actions checks out your repo, `git checkout` sets every file's modification time to the checkout timestamp — not the original commit date.

This means every deploy, your 2007 PDF manuals show up in the sitemap as "modified today." Google sees constant churn on files that haven't actually changed.

Fix this with `_config.yml` defaults:

```yaml
defaults:
  - scope:
      path: "assets/pdfs"
    values:
      sitemap: false
```

The files are still served normally — they're just not in the sitemap.

## The Complete Plugin

Here's the full generator plugin with all fixes in one file:

```ruby
module Jekyll
  class TagPageGenerator < Generator
    safe true

    def generate(site)
      site.tags.each do |tag, posts|
        site.pages << TagPage.new(site, site.source, tag, posts)
      end
    end
  end

  class CategoryPageGenerator < Generator
    safe true

    def generate(site)
      site.categories.each do |category, posts|
        site.pages << CategoryPage.new(site, site.source, category, posts)
      end
    end
  end

  class TagPage < Page
    def initialize(site, base, tag, posts)
      @site = site
      @base = base
      @dir = File.join('tags', tag.downcase.gsub(' ', '-'))
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'tag_page.html')
      self.data['tag'] = tag
      self.data['posts'] = posts
      self.data['title'] = "Posts tagged with \"#{tag}\""
      self.data['sitemap'] = false
      self.data['noindex'] = true if posts.size < 3
    end
  end

  class CategoryPage < Page
    def initialize(site, base, category, posts)
      @site = site
      @base = base
      @dir = File.join('categories', category.downcase.gsub(' ', '-').gsub('_', '-'))
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'category_page.html')
      self.data['category'] = category
      self.data['posts'] = posts
      self.data['title'] = "Posts in category \"#{category}\""
      self.data['sitemap'] = false
      self.data['noindex'] = true if posts.size < 3
    end
  end

  # Must run AFTER jekyll-paginate creates pagination pages
  class PaginationSitemapExcluder < Generator
    safe true
    priority :lowest

    def generate(site)
      site.pages.each do |page|
        if page.dir =~ %r{^/page\d+}
          page.data['sitemap'] = false
        end
      end
    end
  end
end
```

## Bonus: CI Check for Sitemap Health

I added a step to my GitHub Actions workflow that fails the build if `localhost` URLs leak into the sitemap (which happens if you accidentally deploy from a local build):

```yaml
- name: Validate sitemap URLs
  run: |
    if grep -q 'localhost' ./_site/sitemap.xml; then
      echo "::error::sitemap.xml contains localhost URLs"
      grep 'localhost' ./_site/sitemap.xml | head -5
      exit 1
    fi
    echo "Sitemap OK: all URLs use production domain"
```

You could extend this to check for duplicates too:

```yaml
- name: Validate sitemap URLs
  run: |
    if grep -q 'localhost' ./_site/sitemap.xml; then
      echo "::error::sitemap.xml contains localhost URLs"
      exit 1
    fi
    DUPES=$(grep -oP '(?<=<loc>)[^<]+' ./_site/sitemap.xml | sort | uniq -d)
    if [ -n "$DUPES" ]; then
      echo "::error::sitemap.xml contains duplicate URLs:"
      echo "$DUPES"
      exit 1
    fi
    echo "Sitemap OK"
```

## Results

| Metric | Before | After |
|--------|--------|-------|
| Total sitemap URLs | 434 | 133 |
| Tag pages in sitemap | 209 | 0 |
| Category pages in sitemap | 56 | 0 |
| Pagination pages in sitemap | 31 | 0 |
| Static files in sitemap | 7 | 0 |
| Actual content URLs | 131 | 133 |
| `noindex` tag pages | 0 | 161 |
| `noindex` category pages | 0 | 34 |

The sitemap went from 434 URLs to 133 — a 69% reduction — while the actual content count stayed the same. Every URL in the sitemap now points to a page with substantive, unique content.

The tag and category pages still exist, still render, and still provide navigation for readers. They're just not cluttering the sitemap or competing for index slots with real content.

## The Lesson

`jekyll-sitemap` does exactly what it says — it generates a sitemap of every page on your site. The problem is that "every page" includes a lot of pages that shouldn't be in a sitemap. The plugin has no opinion about content quality; that's your job.

If you're running a Jekyll blog with tags, categories, and pagination, audit your sitemap. You might be surprised how much of it is garbage.

## Related Articles

- [Your Jekyll Theme Is Probably Missing head and body Tags](/jekyll-theme-missing-head-body-tags/) — The companion article on HTML structure
- [Google AdSense Approval Failure: Debugging the 'Site Isn't Ready' Rejection](/adsense-approval-failure-remediation/) — Where I discovered the sitemap bloat
- [Jekyll SEO, Sitemap, and Canonical URL Fixes](/jekyll-seo-sitemap-canonical-url-fixes/) — Earlier SEO work
- [Jekyll SEO Health Checks](/jekyll-seo-health-checks/) — Automated SEO validation
