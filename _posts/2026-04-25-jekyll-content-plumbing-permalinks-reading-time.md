---
title: "Jekyll Content Plumbing: Permalinks, Reading Time, Excerpts, and Redirects"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, permalinks, reading-time, excerpts, pagination, redirects, seo, github-pages, configuration]
excerpt: "The invisible infrastructure behind a Jekyll blog — how permalink structure, reading time estimates, custom excerpt separators, pagination, and redirect handling all work together. These aren't glamorous features, but getting them wrong breaks SEO, confuses readers, and creates maintenance headaches."
description: "A deep dive into Jekyll content management configuration: permalink structure with /:title/, reading time calculation via Liquid, custom excerpt separators, jekyll-paginate setup, and jekyll-redirect-from for URL preservation. Includes the git history of how each feature evolved on mcgarrah.org."
date: 2026-04-25
last_modified_at: 2026-04-25
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-25
  date_modified: 2026-04-25
---

These are the features nobody notices until they break. Permalink structure determines every URL on the site. Reading time sets reader expectations. Excerpt separators control what shows on the homepage. Pagination keeps the front page from becoming a mile-long scroll. Redirects prevent 404s when you rename a post.

None of this is exciting. All of it matters.

<!-- excerpt-end -->

## Permalink Structure

The permalink setting is the single most consequential configuration choice in a Jekyll blog. It determines the URL of every post, and changing it after you have inbound links is painful.

```yaml
# _config.yml
permalink: /:title/
```

This produces clean URLs like `mcgarrah.org/proxmox-ceph-nearfull/` instead of the Jekyll default `mcgarrah.org/2025/09/28/proxmox-ceph-nearfull.html`. The `:title` variable comes from the post filename (everything after the date prefix).

### Why `/:title/` and Not Something Else

Jekyll supports [several permalink patterns](https://jekyllrb.com/docs/permalinks/):

| Pattern | Example URL | Pros | Cons |
|---------|-------------|------|------|
| `/:title/` | `/proxmox-ceph-nearfull/` | Clean, short, shareable | No date context in URL |
| `/:year/:month/:day/:title/` | `/2025/09/28/proxmox-ceph-nearfull/` | Date context, avoids title collisions | Long, date becomes part of the permanent URL |
| `/:categories/:title/` | `/homelab/proxmox-ceph-nearfull/` | Category context | Changing categories breaks URLs |
| `pretty` (default) | `/2025/09/28/proxmox-ceph-nearfull/` | Same as date pattern | Same issues |

I chose `/:title/` because:

- **Shorter URLs are more shareable** — They look better in social media previews and are easier to type
- **Dates in URLs become lies** — If I update a post significantly, the URL still shows the original date. The `last_modified_at` front matter handles freshness signaling for SEO without baking it into the URL
- **Category changes don't break links** — I've reorganized categories several times. With `/:categories/:title/`, every reorganization would be a mass redirect event

This setting came from the original [Contrast theme](https://github.com/niklasbuschmann/contrast) — it was set to `/:title/` in the very first commit (January 2019). I kept it because it was the right choice.

### External Links Make Permalinks Permanent

When the blog was just for me and a few readers, permalink stability was nice to have. Now that I'm linking from external sources — Substack newsletters, Reddit posts, LinkedIn shares — it's critical infrastructure.

The two Substack articles alone contain **47 inbound links** to specific blog posts:

- [From Homelabs to Machine Learning](https://mcgarrah.substack.com/p/from-homelabs-to-machine-learning) — 24 links to blog posts
- [From Markdown to Production](https://mcgarrah.substack.com/p/from-markdown-to-production) — 23 links to blog posts

Every one of those links uses the `/:title/` URL pattern: `https://mcgarrah.org/proxmox-ceph-nearfull/`, `https://mcgarrah.org/jekyll-mermaid-diagram-rendering-challenges/`, etc. If I changed the permalink structure tomorrow — say, adding dates — all 47 of those links would break. So would every Reddit thread, every Stack Overflow reference, every bookmark someone saved.

This is why the permalink decision matters more the longer a blog exists. Early on, you can change it with minimal damage. After two years of external linking, it's effectively frozen. Choose well from the start.

### Google Search and Permalink Stability

Permalink structure directly affects how Google indexes and ranks your content:

**URL stability builds authority.** Google associates ranking signals (backlinks, click-through rates, engagement) with specific URLs. When a URL changes, those signals don't automatically transfer — even with a 301 redirect, there's a [temporary ranking dip](https://developers.google.com/search/docs/crawling-indexing/301-redirects) while Google reprocesses. A stable `/:title/` URL accumulates authority over time without interruption.

**Clean URLs get better click-through rates.** In search results, Google displays the URL below the title. `mcgarrah.org/proxmox-ceph-nearfull` is more inviting than `mcgarrah.org/2025/09/28/proxmox-ceph-nearfull`. Users are more likely to click a URL they can read and understand.

**Canonical URLs depend on permalink consistency.** The `jekyll-seo-tag` plugin generates `<link rel="canonical">` tags using the `site.url` + `page.url` pattern. With `/:title/`, the canonical URL is predictable and stable. The [canonical URL fixes](/jekyll-seo-sitemap-canonical-url-fixes/) I did in December 2025 were about domain consistency (`mcgarrah.org` vs `www.mcgarrah.org`), not permalink structure — because the `/:title/` pattern was already correct.

**Dates in URLs can mislead Google.** If a URL contains `/2024/` and you update the content in 2026, Google may perceive the content as stale based on the URL alone, even if `last_modified_at` says otherwise. Dateless URLs avoid this ambiguity entirely.

### The Trailing Slash Matters

The trailing `/` in `/:title/` means Jekyll generates `title/index.html` instead of `title.html`. This produces directory-style URLs that work consistently across web servers and CDNs. Without the trailing slash, some servers serve the file directly while others redirect — and that redirect can cause duplicate content issues in search engines.

## Reading Time Indicator

Every post on this blog shows an estimated reading time (e.g., "5 min read") in the post metadata, next to the author name and date. It's calculated at build time using pure Liquid — no plugin needed.

### Implementation

The calculation lives in `_includes/meta.html`:

```liquid
{% raw %}{%- assign words_per_minute = 200 -%}
{%- assign number_of_words = include.post.content | number_of_words -%}
{%- if number_of_words < words_per_minute -%}
  <span class="reading-time">Less than 1 min read</span>
{%- else -%}
  {%- assign reading_time = number_of_words | divided_by: words_per_minute -%}
  <span class="reading-time">{{ reading_time }} min read</span>
{%- endif -%}{% endraw %}
```

The math is simple: count words, divide by 200 words per minute (average adult reading speed), round down. Posts under 200 words show "Less than 1 min read" instead of "0 min read."

### Design Decisions

**200 WPM, not 250** — Some implementations use 250 WPM. I chose 200 because technical content with code blocks reads slower than prose. A reader doesn't skim a `ceph osd tree` output at the same speed as a paragraph. Slightly overestimating reading time is better than underestimating — nobody's annoyed that a post was faster than expected.

**Build-time, not client-side** — The reading time is calculated by Liquid during the Jekyll build, not by JavaScript in the browser. This means it works without JavaScript, appears in RSS feeds, and doesn't cause layout shift on page load.

**No plugin** — The [reading_time gem](https://github.com/bdesham/reading_time) exists, but the Liquid implementation is 8 lines. Adding a gem dependency for 8 lines of template logic isn't worth it. The [Jekyll Codex without-plugin approach](https://jekyllcodex.org/without-plugin/reading-time-indicator/) was the reference I used.

### Styling

The reading time gets a muted style to avoid competing with the title and date:

```sass
// _sass/reading-time.sass
.reading-time
  font-size: 0.8em
  color: #888
  margin-left: 10px
```

### History

Reading time was added on May 31, 2025 as part of a batch feature enhancement (the same commit that added Giscus comments, copy-to-clipboard buttons, and the tag/category system). It was implemented by Google Jules as part of an experiment with AI-assisted development — one of the few features from that PR that worked correctly on the first try.

## Custom Excerpt Separator

Jekyll uses excerpts to show post previews on the homepage and in RSS feeds. By default, the excerpt is everything before the first blank line (`\n\n\n`). That's a terrible default for technical writing.

### The Problem with the Default

The default triple-newline separator means your excerpt is your first paragraph. For a post that starts with:

```markdown
I've been running Ceph on Proxmox for two years.

Here's what I learned about OSD recovery after a power failure.
```

The excerpt would be just "I've been running Ceph on Proxmox for two years." — one sentence with no useful information about what the post covers.

### The Fix

```yaml
# _config.yml
excerpt_separator: <!-- excerpt-end -->
```

Now I control exactly where the excerpt ends by placing an HTML comment in the post:

```markdown
Setting up my PiKVM v3 has been a journey spanning well over a year.
The goal was a frugal setup that let me manage more than one machine
with both local KVM and remote PiKVM WebUI access.

<!-- excerpt-end -->

## Parts List

So the center piece was the purchase of...
```

The `<!-- excerpt-end -->` comment is invisible in the rendered HTML but tells Jekyll exactly where to cut. I can include multiple paragraphs, a bullet list, or whatever gives the reader enough context to decide if they want to click through.

### Migration Story

This was one of the first changes I made to the blog. On June 22, 2024, I changed the excerpt separator from the default and updated every existing post — a mass migration across all posts from 2001 through 2024. The commit message was simply "Change the excerpt identifier for all posts and config."

A month later (August 12, 2024), while trying to align with the upstream Contrast theme, I accidentally reverted the separator back to the default `\n\n\n`. That broke every excerpt on the site. The fix was straightforward but it's a reminder that config changes can have blast radius across every page.

## Pagination

```yaml
# _config.yml
paginate: 4
```

The homepage shows 4 posts per page, with "Older" and "Newer" navigation links. This is handled by `jekyll-paginate`, one of the original Jekyll plugins.

### Why 4 Posts Per Page

- **Not too few** — 2-3 posts per page means too many clicks to browse
- **Not too many** — With excerpts enabled, each post preview takes significant vertical space. 8+ posts per page creates an overwhelming scroll
- **Matches reading patterns** — A visitor scanning the homepage can evaluate 4 posts in a few seconds and decide whether to click or paginate

### The Sitemap Problem

Pagination generates `/page2/`, `/page3/`, ... `/page32/` directories. With 139 posts at 4 per page, that's 32 pagination pages. These were all ending up in the sitemap, adding 31 low-value URLs.

The fix was the `PaginationSitemapExcluder` generator in the [tag/category generator plugin](/jekyll-tag-category-generator-plugin/) — a `priority :lowest` generator that marks pagination pages with `sitemap: false` after `jekyll-paginate` has created them.

## Redirects with jekyll-redirect-from

When you rename a post file, the URL changes. With `permalink: /:title/`, renaming `2024-04-04-thinkpad-t480-wwan-sdd.md` to `2024-04-04-thinkpad-t480-wwan-ssd.md` (fixing a typo — SDD→SSD) changes the URL from `/thinkpad-t480-wwan-sdd/` to `/thinkpad-t480-wwan-ssd/`. Anyone who bookmarked or linked to the old URL gets a 404.

### The Plugin

```yaml
# Gemfile
gem "jekyll-redirect-from", "~> 0.16.0"
```

```yaml
# _config.yml
plugins:
  - jekyll-redirect-from
```

### Usage

In the renamed post's front matter:

```yaml
---
title: "Thinkpad T480 WWAN SSD"
redirect_from:
  - /thinkpad-t480-wwan-sdd/
---
```

The plugin generates a small HTML file at the old URL path that does a `<meta http-equiv="refresh">` redirect to the new URL. Search engines follow the redirect and update their index.

### When to Use Redirects

- **Filename typo fixes** — The SDD→SSD rename above
- **Title improvements** — When a better title changes the slug
- **Content reorganization** — When splitting or merging posts

I added `jekyll-redirect-from` on April 5, 2026 — relatively late in the blog's life. The trigger was the SSD typo fix, but it's now available for any future renames. In hindsight, I should have added it from day one. The cost of the plugin is near zero (one gem, one config line), and the insurance against broken external links is invaluable now that Substack newsletters and Reddit threads point to specific post URLs.

The redirect mechanism generates a small HTML file at the old path with a `<meta http-equiv="refresh">` redirect. It's not a server-side 301 (GitHub Pages doesn't support those), but Google treats meta refresh redirects as equivalent for indexing purposes. The old URL gets replaced by the new one in search results within a few crawl cycles.

## How These Features Interact

These aren't isolated settings — they form a content management system:

1. **Permalink** (`/:title/`) determines the URL from the filename
2. **Excerpt separator** (`<!-- excerpt-end -->`) controls what appears on the paginated homepage
3. **Pagination** (4 per page) determines how many excerpts show per page
4. **Reading time** (200 WPM) appears in the post metadata alongside the date
5. **Redirects** preserve old URLs when filenames change
6. **Sitemap exclusion** keeps pagination pages out of the sitemap

Change the permalink structure and you need redirects for every existing URL. Change the excerpt separator and every post's homepage preview changes. Change pagination count and the number of sitemap-excluded pages changes. They're coupled.

## Configuration Summary

```yaml
# _config.yml — Content management settings
permalink: /:title/
excerpt_separator: <!-- excerpt-end -->
date_format: "%B %d, %Y"
paginate: 4
show_excerpts: true

plugins:
  - jekyll-paginate
  - jekyll-redirect-from
```

## Related Posts

- [Building This Blog: Jekyll on GitHub Pages](/setting-up-jekyll-blog-github-pages/) — Setup guide covering these features at a high level
- [How the Sausage Is Made](/jekyll-markdown-feature-reference/) — Feature inventory including excerpts and redirects
- [Your Jekyll Sitemap Is 60% Garbage](/jekyll-sitemap-bloat-tags-categories-pagination/) — The pagination sitemap problem
- [Building a Custom Tag and Category Generator Plugin](/jekyll-tag-category-generator-plugin/) — The PaginationSitemapExcluder that cleans up pagination URLs
- [Jekyll SEO, Sitemap, and Canonical URL Fixes](/jekyll-seo-sitemap-canonical-url-fixes/) — SEO implications of permalink choices
