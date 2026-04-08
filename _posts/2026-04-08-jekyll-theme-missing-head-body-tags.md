---
title: "Your Jekyll Theme Is Probably Missing head and body Tags"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, html, seo, adsense, github-pages, debugging, themes]
excerpt: "Many Jekyll themes — especially minimal forks — ship without proper head and body tags. Browsers don't care. Bots do. Here's how to check and fix it in five minutes."
description: "How to detect and fix missing head and body HTML tags in Jekyll themes, why browsers render them fine but bots and verification scripts fail, and the SEO problems this causes."
date: 2026-04-08
last_modified_at: 2026-04-08
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-08
  date_modified: 2026-04-08
---

I spent months debugging why Google AdSense kept rejecting my site. The content was good. The SEO was solid. The privacy policy was in place. Then I looked at the actual HTML my Jekyll theme was generating and found this:

```html
<!DOCTYPE html>
<html lang="en">
<!-- SEO tags here -->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="/assets/css/index.css">
<script async src="https://pagead2.googlesyndication.com/..."></script>
<!-- sidebar HTML here -->
<header>...</header>
<article>...</article>
<footer>...</footer>
</html>
```

No `<head>`. No `</head>`. No `<body>`. No `</body>`. Everything — meta tags, stylesheets, scripts, navigation, content, footer — dumped directly under `<html>` with no structural separation.

And it worked perfectly in every browser I tested.

<!-- excerpt-end -->

## Why Browsers Don't Care

The [HTML5 parsing specification](https://html.spec.whatwg.org/multipage/parsing.html) is extraordinarily forgiving. When a browser encounters a `<meta>` tag without a preceding `<head>`, it implicitly creates one. When it hits a `<header>` or `<div>` without a `<body>`, it creates that too. The browser's parser reconstructs the DOM tree you *meant* to write, even if you didn't write it.

This is by design. The web is full of broken HTML, and browsers evolved to handle it gracefully. You can view-source on a page with no `<head>` tag, then inspect the DOM in DevTools, and you'll see `<head>` and `<body>` right where they should be. The browser added them for you.

## Why Bots Do Care

Bots and verification systems don't always use a full HTML5 parser. Many of them:

- Parse HTML structurally, looking for elements in specific locations
- Expect scripts in `<head>` to actually be inside a `<head>` tag
- Don't execute JavaScript (so they can't see dynamically injected elements)
- Use simpler parsers that don't do implicit element creation

Google's AdSense verification bot is one of these. It crawls your page looking for the AdSense script tag inside `<head>`. If there's no `<head>` tag in the raw HTML, the bot can't confirm the script is installed — even if a browser would render it correctly.

## How to Check Your Theme

Open any page on your Jekyll site and view the source (not the DOM inspector — the actual source):

```bash
curl -s https://yoursite.com | head -20
```

You should see something like:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<!-- meta tags, stylesheets, scripts -->
</head>
<body>
<!-- visible content -->
</body>
</html>
```

If you see meta tags and stylesheets immediately after `<html>` with no `<head>` tag, your theme has this problem.

For a quick check of your default layout:

```bash
grep -c '<head>' _layouts/default.html
grep -c '<body>' _layouts/default.html
```

Both should return `1`. If either returns `0`, keep reading.

## The Problems This Causes

### 1. Bot Verification Failures

Any service that needs to verify a script tag in your `<head>` will fail:

- **Google AdSense** — Can't verify the publisher script
- **Google Search Console** — HTML tag verification method may fail
- **Social media crawlers** — May miss Open Graph tags
- **SEO audit tools** — Will flag invalid HTML structure

### 2. Duplicate Canonical Tags

This often comes bundled with the missing `<head>` problem. If your theme uses `jekyll-seo-tag` (which emits a canonical link) *and* has a manual canonical link, you get two:

```html
<!-- From jekyll-seo-tag -->
<link rel="canonical" href="https://yoursite.com/page/" />
<!-- From default.html -->
<link rel="canonical" href="https://yoursite.com/page/" />
```

Google [explicitly warns](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) against duplicate canonical tags. Without a `<head>` boundary, it's easy to miss that both are present.

### 3. Stylesheets in the Body

Some themes include components that mix `<link>` stylesheet tags with HTML content. In my case, the sidebar include had:

```html
<link rel="stylesheet" href="/assets/css/sidebar.css">
<aside>
  <nav>...</nav>
</aside>
```

Without `<head>`/`<body>` separation, that `<link>` tag ends up in the body. Browsers handle it, but it's invalid HTML and can cause a flash of unstyled content.

## The Five-Minute Fix

Here's the pattern. Your `_layouts/default.html` should look like this:

```html
{% raw %}<!DOCTYPE html>
<html lang="{{ page.lang | default: site.lang | default: 'en' }}">
<head>
{% seo %}
<meta charset="{{ site.encoding }}">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!-- stylesheets, scripts, feeds -->
</head>

<body>
<!-- sidebar, navigation, content, footer -->
{{ content }}
</body>
</html>{% endraw %}
```

The rules are simple:

- **In `<head>`**: meta tags, `{% seo %}`, stylesheets, scripts, feed links, analytics, verification scripts
- **In `<body>`**: everything visible — navigation, sidebar, content, footer, cookie banners

### What to Move

If your theme has includes that mix head and body content, split them. My sidebar include had a `<link>` tag that needed to move to `<head>`:

```html
<!-- Before: sidebar.html mixed <link> with <aside> -->
<link rel="stylesheet" href="/assets/css/sidebar.css">
<aside>...</aside>

<!-- After: <link> moved to default.html <head>, sidebar.html is just: -->
<aside>...</aside>
```

And in `default.html`:

```html
{% raw %}<head>
<!-- other head content -->
{% if site.show_sidebar %}<link rel="stylesheet" href="/assets/css/sidebar.css">{% endif %}
</head>

<body>
{% if site.show_sidebar %}{% include sidebar.html %}{% endif %}
<!-- rest of body -->
</body>{% endraw %}
```

### Verify After Fixing

```bash
# Build and check
bundle exec jekyll build

# Count tags (should all be 1)
grep -c '<head>'  _site/index.html
grep -c '</head>' _site/index.html
grep -c '<body>'  _site/index.html
grep -c '</body>' _site/index.html

# Check for duplicate canonicals (should be 1)
grep -c 'rel="canonical"' _site/index.html
```

## Which Themes Have This Problem?

I can't name every theme, but the pattern is common in:

- **Minimal themes** that prioritize simplicity over correctness
- **Forks of forks** where the original had proper structure but it got lost
- **Themes that evolved from single-file layouts** where everything was inline
- **Themes that predate `jekyll-seo-tag`** and added it later without restructuring

If your theme's `default.html` is under 50 lines and doesn't contain `<head>` or `<body>`, it almost certainly has this problem.

## My Specific Case

My blog uses a minimal Jekyll theme that I've customized extensively over the years. The original theme never had `<head>` or `<body>` tags — it relied on browser forgiveness. This worked fine for years until I tried to get AdSense approval and Google's bot couldn't find the verification script.

The fix took five minutes. The debugging took months. I wrote about the full AdSense journey in:

- [Google AdSense Approval Failure: Debugging the 'Site Isn't Ready' Rejection](/adsense-approval-failure-remediation/)
- [Fixing AdSense Verification Without Breaking GDPR](/adsense-verification-gdpr-script-loading-fix/)

But the HTML structure fix was the foundation that made everything else work.

## The Takeaway

If you're running a Jekyll site and anything involving bot verification isn't working — AdSense, Search Console HTML verification, social media previews — check your `<head>` and `<body>` tags before debugging anything else. Browsers will forgive you. Bots won't.

## Related Articles

- [Fixing AdSense Verification Without Breaking GDPR: The Script Loading Mistake](/adsense-verification-gdpr-script-loading-fix/)
- [Your Jekyll Sitemap Is 60% Garbage](/jekyll-sitemap-bloat-tags-categories-pagination/) — The companion article on sitemap cleanup
- [Jekyll SEO, Sitemap, and Canonical URL Fixes](/jekyll-seo-sitemap-canonical-url-fixes/)
- [Implementing GDPR Compliance for Jekyll Sites](/implementing-gdpr-compliance-jekyll-adsense/)
