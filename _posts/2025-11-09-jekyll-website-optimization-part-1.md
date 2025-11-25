---
title: "Jekyll Website Optimization for GitHub Pages - Part 1"
layout: post
categories: [web-development, technical]
tags: [jekyll, github-pages, optimization, seo, performance, website]
published: true
---

After running this Jekyll-based website for a couple years (since July of 2023), I've learned valuable lessons about optimizing Jekyll sites for GitHub Pages. This blog initially started as a consolidation of several blog websites I'd published over the years. This is Part 1 of a two-part series covering the foundational optimizations that have made the biggest difference for my homelab blog.

<!-- excerpt-end -->

## The Journey So Far

This website started as a fork of the excellent [Contrast theme](https://github.com/niklasbuschmann/contrast) by Niklas Buschmann. While the theme provided a solid foundation, running a technical blog with 100+ posts revealed areas for improvement in performance, SEO, and user experience.

## Current Website Statistics

- **Jekyll Version**: 4.4.1
- **Posts**: 100+ technical articles
- **Comments**: GitHub Discussions via Giscus
- **Analytics**: Google Analytics (G-F90DVB199P)
- **Monetization**: Google AdSense (ca-pub-2421538118074948)
- **Pagination**: 4 posts per page

## Performance Optimizations Implemented

### 1. Code Copy Buttons

One of the most requested features for technical blogs is the ability to copy code snippets easily. I implemented JavaScript-based copy buttons for all code blocks:

```javascript
// Add copy buttons to all code blocks
document.querySelectorAll('pre code').forEach((block) => {
  const button = document.createElement('button');
  button.className = 'copy-button';
  button.textContent = 'Copy';
  button.addEventListener('click', () => {
    navigator.clipboard.writeText(block.textContent);
    button.textContent = 'Copied!';
    setTimeout(() => button.textContent = 'Copy', 2000);
  });
  block.parentNode.appendChild(button);
});
```

### 2. Reading Time Indicator

Readers appreciate knowing how long an article will take to read. I added a reading time calculator:

```liquid
{% raw %}{% assign words = content | number_of_words %}
{% assign reading_time = words | divided_by: 200 %}
{% if reading_time < 1 %}
  Less than 1 minute read
{% else %}
  {{ reading_time }} minute read
{% endif %}{% endraw %}
```

### 3. Optimized Image Loading

For technical posts with many screenshots, image optimization is crucial:

```markdown
[![Image Description](/assets/images/image.png){:width="50%" height="50%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/image.png){:target="_blank"}
```

This approach:

- Provides responsive sizing
- Centers images automatically
- Opens full-size images in new tabs
- Maintains aspect ratios

## SEO Enhancements

### 1. Structured Data and Meta Tags

Proper meta tags significantly improve search engine visibility:

```html
<meta name="description" content="{{ page.excerpt | strip_html | truncate: 160 }}">
<meta property="og:title" content="{{ page.title }}">
<meta property="og:description" content="{{ page.excerpt | strip_html | truncate: 160 }}">
<meta property="og:type" content="article">
<meta property="og:url" content="{{ site.url }}{{ page.url }}">
```

### 2. Sitemap Generation

GitHub Pages automatically generates sitemaps, but custom optimization helps:

```yaml
# _config.yml
plugins:
  - jekyll-sitemap
  - jekyll-feed
  - jekyll-seo-tag

url: "https://www.mcgarrah.org"
baseurl: ""
```

### 3. RSS Feed Optimization

The jekyll-feed plugin generates RSS feeds automatically, but customization improves subscriber experience:

```liquid
{% raw %}---
layout: null
---
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{{ site.title }}</title>
    <description>{{ site.description }}</description>
    <link>{{ site.url }}</link>
    {% for post in site.posts limit:20 %}
      <item>
        <title>{{ post.title }}</title>
        <description>{{ post.excerpt | strip_html }}</description>
        <link>{{ site.url }}{{ post.url }}</link>
        <pubDate>{{ post.date | date_to_rfc822 }}</pubDate>
      </item>
    {% endfor %}
  </channel>
</rss>{% endraw %}
```

## Content Management Improvements

### 1. Tags and Categories System

Organizing technical content requires a robust tagging system:

```yaml
# Front matter example
---
title: "Article Title"
layout: post
categories: [technical, homelab]
tags: [proxmox, ceph, networking, hardware]
published: true
---
```

### 2. Archive Pages

Created dynamic archive pages for better content discovery:

```liquid
{% raw %}{% for post in site.posts %}
  {% assign year = post.date | date: "%Y" %}
  {% assign month = post.date | date: "%B" %}
  {% if year != previous_year %}
    <h2>{{ year }}</h2>
  {% endif %}
  {% if month != previous_month %}
    <h3>{{ month }}</h3>
  {% endif %}
  <article>
    <a href="{{ post.url }}">{{ post.title }}</a>
    <time>{{ post.date | date: "%B %d, %Y" }}</time>
  </article>
  {% assign previous_year = year %}
  {% assign previous_month = month %}
{% endfor %}{% endraw %}
```

### 3. Related Posts Section

Implemented related posts based on tags and categories:

```liquid
{% raw %}{% assign related_posts = site.related_posts | where_exp: "post", "post.url != page.url" | slice: 0, 3 %}
{% if related_posts.size > 0 %}
  <section class="related-posts">
    <h3>Related Articles</h3>
    {% for post in related_posts %}
      <article>
        <a href="{{ post.url }}">{{ post.title }}</a>
        <p>{{ post.excerpt | strip_html | truncate: 100 }}</p>
      </article>
    {% endfor %}
  </section>
{% endif %}{% endraw %}
```

## GitHub Actions Workflow

Automated builds ensure consistent deployment:

```yaml
name: Deploy Jekyll site to Pages

on:
  # Runs on pushes targeting the default branch
  push:
    branches: ["main"]
  # Runs at 05:00 UTC (01:00 AM EST) every day
  schedule:
    - cron: '5 0 * * *'  
  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  build-and-deploy:
  ...
```

Details for this build can be found in my repository under [.github\workflows\jekyll.yml](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/.github/workflows/jekyll.yml) for expanded details.

This above Github Actions automation facilitates future dated articles being published since I also setup my `_config.yml` to not post future articles.

```yaml
# _config.yml

# Future posts disabled for scheduled releases via GHA scheduled job
future: false
```

This combination of settings allows me to bank up several articles to post at future dates once checked into the repository.

## Comment System Integration

Replaced traditional comment systems with GitHub Discussions via Giscus:

```html
<script src="https://giscus.app/client.js"
        data-repo="mcgarrah/mcgarrah.github.io"
        data-repo-id="{{ site.giscus.repo_id }}"
        data-category="General"
        data-category-id="{{ site.giscus.category_id }}"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="preferred_color_scheme"
        data-lang="en"
        crossorigin="anonymous"
        async>
</script>
```

Benefits:

- No database required
- Spam protection via GitHub
- Familiar interface for developers
- Markdown support in comments

## What's Next

This covers the foundational optimizations that every Jekyll site should implement. In [Part 2 of this series](/jekyll-website-optimization-part-2/), I'll dive into:

- Advanced analytics and monitoring setup
- Remaining optimization priorities
- Performance measurement and results
- Lessons learned from running a technical blog
- Future enhancement roadmap

## Conclusion

These foundational optimizations provide immediate value to readers and establish a solid base for further improvements. The combination of performance enhancements, SEO basics, and content organization creates a much better user experience.

Key takeaways from Part 1:

- **Code copy buttons** are essential for technical content
- **Proper meta tags** significantly improve search visibility
- **Content organization** helps readers find related information
- **GitHub Actions** automate deployment and reduce errors
- **Giscus comments** provide engagement without database overhead

Stay tuned for Part 2, where we'll explore advanced optimizations and dive deeper into performance metrics and future enhancements.

## References

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Contrast Theme](https://github.com/niklasbuschmann/contrast) - Original theme
- [Giscus](https://giscus.app/) - GitHub Discussions comment system
