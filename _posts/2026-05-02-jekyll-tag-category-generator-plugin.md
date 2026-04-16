---
title: "Building a Custom Tag and Category Generator Plugin for Jekyll"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, ruby, plugins, tags, categories, github-pages, seo, github-actions]
excerpt: "GitHub Pages doesn't support tag or category pages out of the box. Here's how I built a custom Jekyll generator plugin that creates them automatically — and the SEO lessons learned along the way."
description: "How to build a custom Jekyll Ruby plugin that automatically generates tag and category pages, with SEO controls for sitemap exclusion and noindex on thin content. Includes the full plugin, layouts, and index pages."
date: 2026-05-02
last_modified_at: 2026-05-02
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-02
  date_modified: 2026-05-02
---

GitHub Pages with Jekyll gives you tags and categories in front matter, but no pages for them. You can tag a post `proxmox` all day long — there's no `/tags/proxmox/` page unless you build one. Manually creating a page for each tag doesn't scale. At 139 posts with 237 unique tags and 53 categories, that's not an option.

This plugin solves it: a single Ruby file that generates a page for every tag and every category at build time.

<!-- excerpt-end -->

## The Problem

Jekyll's built-in `site.tags` and `site.categories` hashes collect posts by taxonomy, but they don't generate browsable pages. Most Jekyll themes include a `tags.html` that lists all tags on one page, but clicking a tag doesn't go anywhere useful.

The common solutions are:

1. **Manual pages** — Create a markdown file per tag. Doesn't scale.
2. **Third-party plugins** — [jekyll-tagging](https://github.com/pattex/jekyll-tagging), [jekyll-archives](https://github.com/jekyll/jekyll-archives). Not whitelisted on GitHub Pages (if using the default build).
3. **Custom generator plugin** — Write your own. Works with GitHub Actions builds.

Useful references I consulted during the decision:

- [Long Qian's Jekyll tag page guide](https://longqian.me/2017/02/09/github-jekyll-tag/) — The approach I adapted
- [Untangled.dev tag management](https://www.untangled.dev/2020/06/02/tag-management-jekyll/) — Alternative approach
- [Jekyll docs on tags](https://jekyllrb.com/docs/posts/#tags) — Official reference

I went with option 3 because I was already using GitHub Actions for the build (required for other custom plugins), and I wanted full control over URL structure and SEO behavior.

## Evolution of the Plugin

The plugin went through three distinct versions, each driven by a real problem. The git history tells the story.

### Version 1: Basic Generator (July 2025)

The initial version was straightforward — two Generator classes and two Page classes. It iterated `site.tags` and `site.categories`, created a page for each, and was done:

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

  # ... CategoryPageGenerator identical pattern ...

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
    end
  end
end
```

This worked fine for months. Then AdSense review forced a closer look at the sitemap.

### Version 2: Sitemap Exclusion and Noindex (April 6, 2026 — morning)

During AdSense review preparation, I audited the sitemap and found it had **434 URLs, 262 of which (60%) were auto-generated tag, category, and pagination pages** with little unique content. This dilutes content quality signals.

The fix added two lines to each Page class and a `Jekyll::Hooks` callback for pagination:

```ruby
# Added to TagPage and CategoryPage:
self.data['sitemap'] = false
self.data['noindex'] = true if posts.size < 3

# Added for pagination pages:
Jekyll::Hooks.register :pages, :post_init do |page|
  if page.url =~ %r{^/page\d+/}
    page.data['sitemap'] = false
  end
end
```

Result: sitemap dropped from 434 to 172 URLs. 195 thin tag/category pages got `noindex`.

### Version 3: Hook-to-Generator Refactor (April 6, 2026 — afternoon)

The `Jekyll::Hooks :pages :post_init` approach broke pagination within hours. The hook fired during page initialization — *before* `jekyll-paginate` had created its pagination pages. This caused the homepage to display as **page 32 of 32** (oldest posts first) and prevented pagination directories from being created.

The fix replaced the hook with a lowest-priority Generator that runs *after* `jekyll-paginate` has finished:

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

The key insight: `priority :lowest` ensures this generator runs after all other generators (including `jekyll-paginate`), so the pagination pages exist by the time we iterate them. The hook approach was too early in the lifecycle.

Result: homepage showed newest posts again (page 1 of 32), all 31 pagination directories restored, pagination pages still excluded from sitemap.

## The Final Plugin

The current version lives in `_plugins/tag_category_generator.rb`:

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

### Design Decisions

**`safe true`** — Marks the generator as safe for GitHub Pages compatibility. Even though we're building with GitHub Actions, this is good practice.

**URL structure** — Tags go to `/tags/tag-name/` and categories to `/categories/category-name/`. The `downcase.gsub(' ', '-')` normalizes spaces to hyphens. Categories also convert underscores to hyphens for consistency.

**`sitemap: false`** — This was added after discovering that the generated pages were bloating the sitemap. With 237 tags, that's 237 extra URLs in `sitemap.xml` — most pointing to pages with only one or two posts. See [Your Jekyll Sitemap Is 60% Garbage](/jekyll-sitemap-bloat-tags-categories-pagination/) for the full story.

**`noindex` for thin content** — Tags with fewer than 3 posts get `noindex` to avoid search engines indexing low-value pages. This is a soft SEO signal — the page still exists for users, but search engines are asked to skip it.

**`PaginationSitemapExcluder`** — A bonus generator that excludes `/page2/`, `/page3/`, etc. from the sitemap. These pagination pages add no SEO value and were another source of sitemap bloat. This was originally a `Jekyll::Hooks :pages :post_init` callback, but that broke `jekyll-paginate` because the hook fired before pagination pages existed. The `priority :lowest` Generator approach runs after all other generators have finished.

## The Layouts

Both layouts are nearly identical. Here's `_layouts/tag_page.html`:

```html
---
layout: default
---

<article class="page">
  <h1 class="page-title">{% raw %}{{ page.title }}{% endraw %}</h1>
  <div class="page-content">
    <div class="posts-list">
      {% raw %}{% for post in page.posts %}{% endraw %}
        <article class="post-item">
          <h2><a href="{% raw %}{{ post.url | relative_url }}{% endraw %}">{% raw %}{{ post.title }}{% endraw %}</a></h2>
          <time datetime="{% raw %}{{ post.date | date_to_xmlschema }}{% endraw %}">{% raw %}{{ post.date | date: site.date_format }}{% endraw %}</time>
          {% raw %}{% if post.excerpt %}{% endraw %}
            <div class="post-excerpt">{% raw %}{{ post.excerpt }}{% endraw %}</div>
          {% raw %}{% endif %}{% endraw %}
        </article>
      {% raw %}{% endfor %}{% endraw %}
    </div>
  </div>
</article>
```

The `category_page.html` layout is identical. You could DRY this up with an include, but for two files it's not worth the indirection.

## The Index Pages

Users need a way to browse all tags and categories. These are simple Liquid pages:

`tags.html`:

```html
---
layout: list_page
title: All Tags
---
<div class="taxonomies-list">
  {% raw %}{% for tag_hash in site.tags %}
    {% assign tag_name = tag_hash[0] %}
    {% assign num_posts = tag_hash[1].size %}
    <a href="{{ site.baseurl }}/tags/{{ tag_name | slugify }}/" class="taxonomy-item">
      {{ tag_name }} ({{ num_posts }})
    </a>
  {% endfor %}{% endraw %}
</div>
```

`categories.html` follows the same pattern with `site.categories`.

## GitHub Actions Requirement

This plugin won't work with the default GitHub Pages Jekyll build — only [whitelisted plugins](https://pages.github.com/versions/) run there. You need a GitHub Actions workflow that runs `jekyll build` yourself and deploys the output.

If you're already using GitHub Actions for your Jekyll build (which you'll need for any custom plugin), this just works — drop the `.rb` file in `_plugins/` and it's picked up automatically.

## Lessons Learned

**Tag proliferation is real.** At 237 tags across 139 posts, many tags have only 1-2 posts. This creates thin content pages that dilute SEO. The `noindex` threshold helps, but the real fix is disciplined tagging — reuse existing tags rather than inventing new ones for every post.

**Sitemap exclusion matters.** The original version of this plugin didn't set `sitemap: false`. The result was a sitemap with 434 URLs where 262 were auto-generated junk. Google Search Console flagged many as "Discovered – currently not indexed." Adding `sitemap: false` cut the sitemap to meaningful content only.

**Jekyll hook ordering is treacherous.** The `:post_init` hook seemed like the right place to tag pagination pages for sitemap exclusion — it fires when a page is initialized. But `jekyll-paginate` creates pages *during* generation, not initialization. The hook fired too early, interfered with pagination's template detection, and the homepage showed the oldest posts instead of the newest. The fix was moving to a `priority :lowest` Generator. Lesson: when modifying pages created by other plugins, use a Generator with lowest priority, not a hook.

**Categories vs tags** — In practice, categories on this blog are broad buckets (`technical`, `homelab`, `web-development`) while tags are specific topics (`proxmox`, `ceph`, `jekyll`). The plugin treats them identically but they serve different navigation purposes.

## Current Stats

As of this writing:

- **139** published posts
- **237** unique tags → 237 generated tag pages
- **53** unique categories → 53 generated category pages
- Top tags: homelab (32), proxmox (23), jekyll (23), ceph (19), storage (18)
- Top categories: technical (63), homelab (22), web-development (21), hardware (20)

## Related Posts

- [Your Jekyll Sitemap Is 60% Garbage](/jekyll-sitemap-bloat-tags-categories-pagination/) — The sitemap bloat problem this plugin caused and how it was fixed
- [Building This Blog: Jekyll on GitHub Pages from Zero to 130+ Posts](/setting-up-jekyll-blog-github-pages/) — Broader setup guide that mentions this plugin
- [How the Sausage Is Made: Every Feature Powering This Jekyll Blog](/jekyll-markdown-feature-reference/) — Feature inventory including tag/category pages
