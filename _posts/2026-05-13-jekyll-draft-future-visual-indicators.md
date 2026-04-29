---
title: "Visual Indicators for Draft and Future Posts in Jekyll"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, drafts, future-posts, font-awesome, local-development, github-pages, ux]
excerpt: "When previewing a Jekyll site locally with --drafts and --future, it's hard to tell which posts are live and which are still unpublished. I added Font Awesome icons and italic styling to the archive and home pages so drafts get a pencil and future posts get a robot — visible only during local development."
description: "How to add visual indicators for draft and future-dated posts in Jekyll templates. Uses Font Awesome SVG icons (pencil for drafts, robot for future), italic styling, and Liquid conditionals that only activate during local development with --drafts and --future flags. Covers archive pages, paginated home pages, and excerpt views."
date: 2026-05-13
last_modified_at: 2026-05-13
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-13
  date_modified: 2026-05-13
---

My previous article on [Jekyll Run plugin configuration](/jekyll-run-vscode-plugin-local-development/) documented a frustrating problem: when you run `jekyll serve --drafts --future`, draft and future-dated posts appear in your listings but look identical to published posts. You can't tell at a glance which articles are live on production and which are still waiting.

After scrolling past 130+ posts trying to spot my drafts one too many times, I added visual indicators — a pencil icon for drafts, a robot icon for future-dated posts (because robots are cool and futuristic), and italic text for both. The indicators only appear during local development because drafts and future posts don't exist in production builds.

| Drafts | Future |
| :---: | :---: |
| <svg aria-label="Draft" class="icon icon-status" style="height:1.7em;width:1.7em" title="Draft"><use xlink:href="/assets/fontawesome/icons.svg#pencil-alt"></use></svg> (PENCIL) | <svg aria-label="Future" class="icon icon-status" style="height:1.7em;width:1.7em" title="Scheduled"><use xlink:href="/assets/fontawesome/icons.svg#robot"></use></svg> (ROBOT) |

<!-- excerpt-end -->

## The Problem

Running `jekyll serve --drafts --future --unpublished` renders everything into `site.posts`. The archive page, home page, and paginated listings all show drafts and future posts mixed in with published content. There's no visual distinction.

This matters when you have 50 drafts and 5 future-dated posts queued up. You want to:

- Quickly identify what's live vs what's scheduled
- Spot drafts that accidentally have `published: true` (they'll deploy if moved to `_posts/`)
- Verify that future-dated posts have the correct dates before they go live

## What Jekyll Exposes

Before building anything, I needed to confirm what data Jekyll makes available in templates.

**Future posts** are straightforward. Every post has a `post.date`, and Jekyll provides `site.time` (the build timestamp). Compare them:

```liquid
{% raw %}{% if post.date > site.time %}
  <!-- this post is future-dated -->
{% endif %}{% endraw %}
```

**Drafts** are trickier. Jekyll doesn't set a `post.draft` flag or expose the source collection. But drafts come from the `_drafts/` directory, and that path is available:

```liquid
{% raw %}{% if post.path contains '_drafts/' %}
  <!-- this post is a draft -->
{% endif %}{% endraw %}
```

This works because `post.path` contains the relative path from the site root, including the directory name.

**In production**, neither check matters — drafts and future posts aren't in `site.posts` at all when building without `--drafts` and `--future`. The conditionals are inert. No performance cost, no risk of leaking unpublished content.

## The Implementation

### Adding Icons to the SVG Sprite

This blog uses a Font Awesome SVG sprite that's built at compile time from icons referenced in `_config.yml`. Only icons listed under `navigation` and `external` get included. To add the draft and future icons without polluting those lists, I added a new config key:

```yaml
# _config.yml
post_status_icons:
  - {icon: pencil-alt}     # draft posts
  - {icon: robot}          # future-dated posts
```

And extended the sprite template to include them:

```liquid
{% raw %}<!-- assets/fontawesome/icons.svg -->
{% assign keys = 'navigation,external,post_status_icons' | split: ',' %}
{% for key in keys %}
{% for link in site[key] %}
  {% assign icon = link.icon %}
  {% assign svg = site.data.font-awesome.icons[icon].svg | first %}
  <symbol id="{{ icon }}" viewBox="0 0 {{ svg[1].width }} {{ svg[1].height }}">
    <path d="{{ svg[1].path }}" />
  </symbol>
{% endfor %}
{% endfor %}{% endraw %}
```

This adds exactly two SVG symbols to the sprite — no CDN load, no external requests.

### Archive Page

The `_includes/archive.html` gets the detection logic and conditional rendering:

```liquid
{% raw %}{% for post in site.posts %}
{%- assign is_draft = false -%}
{%- assign is_future = false -%}
{%- if post.path contains '_drafts/' -%}{%- assign is_draft = true -%}{%- endif -%}
{%- if post.date > site.time -%}{%- assign is_future = true -%}{%- endif -%}
<li>
  <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%Y-%m-%d" }}</time>
  {%- if is_draft %}
  <svg aria-label="Draft" class="icon icon-status" title="Draft">
    <use xlink:href="{{ "/assets/fontawesome/icons.svg" | relative_url }}#pencil-alt"></use>
  </svg>
  {%- elsif is_future %}
  <svg aria-label="Future" class="icon icon-status" title="Scheduled">
    <use xlink:href="{{ "/assets/fontawesome/icons.svg" | relative_url }}#robot"></use>
  </svg>
  {%- endif %}
  {%- if is_draft or is_future %}
  <em><a href="{{ post.url | relative_url }}">{{ post.title }}</a></em>
  {%- else %}
  <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
  {%- endif %}
</li>
{% endfor %}{% endraw %}
```

Draft entries get a <svg aria-label="Draft" class="icon icon-status" style="height:1em;width:1em" title="Draft"><use xlink:href="/assets/fontawesome/icons.svg#pencil-alt"></use></svg> pencil icon. Future entries get a <svg aria-label="Future" class="icon icon-status" style="height:1em;width:1em" title="Scheduled"><use xlink:href="/assets/fontawesome/icons.svg#robot"></use></svg> robot icon. Both get italic text. Published posts render normally with no extra markup.

Here's what future-dated posts look like in the archive with the robot icon and italic styling:

[![Future post indicators in the archive view](/assets/images/jekyll-visual-indicator-future-robot.png){:width="75%" height="75%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/jekyll-visual-indicator-future-robot.png){:target="_blank"}

And drafts with the pencil icon:

[![Draft post indicators in the archive view](/assets/images/jekyll-visual-indicator-drafts-pencil.png){:width="75%" height="75%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/jekyll-visual-indicator-drafts-pencil.png){:target="_blank"}

### Home Page Excerpt Views

The `_includes/meta.html` header component passes the detection through as include parameters:

```liquid
{% raw %}{% include meta.html post=post preview=true is_draft=is_draft is_future=is_future %}{% endraw %}
```

Inside `meta.html`, the icon renders next to the post title:

```liquid
{% raw %}<h1>
  <a href="{{ include.post.url | relative_url }}">{{ include.post.title }}</a>
  {%- if include.is_draft %}
  <svg aria-label="Draft" class="icon icon-status" title="Draft">
    <use xlink:href="{{ "/assets/fontawesome/icons.svg" | relative_url }}#pencil-alt"></use>
  </svg>
  {%- elsif include.is_future %}
  <svg aria-label="Future" class="icon icon-status" title="Scheduled">
    <use xlink:href="{{ "/assets/fontawesome/icons.svg" | relative_url }}#robot"></use>
  </svg>
  {%- endif %}
</h1>{% endraw %}
```

The excerpt `<article>` wrapper also gets a class for italic styling:

```liquid
{% raw %}<article{% if is_draft or is_future %} class="post-preview-unpublished"{% endif %}>{% endraw %}
```

### CSS

Two additions to `_sass/classes.sass`:

```sass
.icon-status
  height: .85em
  width: .85em
  opacity: .6
  margin: 0 .2em

.post-preview-unpublished
  font-style: italic
```

The status icons are slightly smaller and more transparent than navigation icons — they're informational, not interactive. The italic class applies to the entire excerpt card for draft and future posts.

## Files Changed

| File | Change |
|------|--------|
| `_config.yml` | Added `post_status_icons` with `pencil-alt` and `robot` |
| `assets/fontawesome/icons.svg` | Extended sprite loop to include `post_status_icons` |
| `_includes/archive.html` | Draft/future detection with icons and italics |
| `_includes/home.html` | Same treatment for paginated excerpt view |
| `_includes/meta.html` | Icon badge next to post title in headers |
| `_layouts/home.html` | Same treatment for list-style home layout |
| `_layouts/paginate.html` | Same treatment for paginate layout |
| `_layouts/archive.html` | Same treatment for archive layout |
| `_sass/classes.sass` | Added `.icon-status` and `.post-preview-unpublished` |

## Why These Icons

**Pencil (pencil-alt)** for drafts — universally understood as "editing" or "work in progress." It's already in Font Awesome Free and visually distinct at small sizes.

**Robot** for future posts — a nod to the automated scheduled publishing via GitHub Actions cron. The daily build at 00:05 UTC is the "robot" that publishes future-dated posts when their date arrives. It's also visually distinctive and unlikely to be confused with any other status.

I considered `clock` and `hourglass` for future posts but they're too generic — they could mean "reading time" or "loading." The robot is unambiguous in context.

## Production Safety

This feature is inherently safe for production:

- **No `--drafts` flag** → no drafts in `site.posts` → no pencil icons rendered
- **No `--future` flag** → no future posts in `site.posts` → no robot icons rendered
- The Liquid conditionals evaluate to false and produce zero HTML output
- The SVG sprite includes the two extra icon symbols (~2KB), but they're never referenced in production HTML

The only "cost" in production is two unused `<symbol>` elements in the SVG sprite file. They add negligible bytes and are never rendered by the browser.

## Related Posts

- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/) — The predecessor article on configuring `--drafts` and `--future` flags
- [How the Sausage Is Made: Every Feature Powering This Jekyll Blog](/jekyll-markdown-feature-reference/) — Complete feature reference
- [Building This Blog: Jekyll on GitHub Pages from Zero to 130+ Posts](/setting-up-jekyll-blog-github-pages/) — Blog setup guide
- [The CI/CD Pipeline Behind This Jekyll Blog](/jekyll-github-actions-cicd-pipeline/) — How scheduled builds publish future-dated posts

## References

- [Jekyll Drafts Documentation](https://jekyllrb.com/docs/posts/#drafts) — Official docs on the `_drafts` folder
- [Jekyll Configuration: Show Drafts](https://jekyllrb.com/docs/configuration/options/#build-command-options) — CLI flags for draft and future rendering
- [Font Awesome Free Icons](https://fontawesome.com/icons?d=gallery&m=free) — Icon browser
