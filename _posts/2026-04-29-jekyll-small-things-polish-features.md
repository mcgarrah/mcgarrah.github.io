---
title: "The Small Things: Polish Features That Make a Jekyll Blog Feel Professional"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, dark-mode, print-stylesheet, 404-page, favicon, archive, author-bio, ux, github-pages, e-e-a-t]
excerpt: "Dark mode, print stylesheets, haiku error pages, author bios, and the archive page — none of these are glamorous features. Each one took less than a day. Together they're the difference between a blog that looks like a default template and one that feels like someone cares about it."
description: "Six small polish features for a Jekyll blog: automatic dark/light theme via prefers-color-scheme, print stylesheet for clean article printing, custom 404/500 error pages with haiku, author bio with E-E-A-T signals, archive page, and favicon. Each feature explained with code, git history, and design rationale."
date: 2026-04-29
last_modified_at: 2026-04-29
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-29
  date_modified: 2026-04-29
---

Nobody visits a blog because it has a print stylesheet. Nobody subscribes because the 404 page has a haiku. But these small touches signal that the site is maintained, that someone thought about the details, and that the content is worth the reader's time.

Here are six features that each took less than a day to implement but collectively transformed this blog from a default Jekyll template into something that feels intentional.

<!-- excerpt-end -->

## Dark/Light Theme

The blog automatically matches the reader's operating system preference — dark mode on dark systems, light mode on light systems. No toggle button, no JavaScript, no cookie to remember the choice.

### Implementation

The entire dark mode is a single CSS media query in `_sass/basic.sass`:

```sass
@media (prefers-color-scheme: dark)
  body
    background: $dark
    color: $light
```

The `$dark` and `$light` variables come from the Contrast theme's SASS variable system. The theme was designed with dark mode support from the beginning (the original author, Niklas Buschmann, added it in December 2019), but it needed maintenance as I added features.

### The Mermaid Dark Mode Fix

When I added Mermaid diagram support in September 2025, the diagrams rendered with a white background in dark mode — a blinding white rectangle in an otherwise dark page. The fix was detecting the color scheme in JavaScript and passing it to Mermaid's initialization:

```javascript
const isDarkMode = window.matchMedia &&
  window.matchMedia('(prefers-color-scheme: dark)').matches;
mermaid.initialize({
  startOnLoad: true,
  theme: isDarkMode ? 'dark' : 'default'
});
```

The Google Custom Search widget also needed dark mode styling (`_sass/google-search.sass`), and the Giscus comment widget gets it for free via the `preferred_color_scheme` theme setting.

### Why No Toggle?

Some blogs add a manual dark/light toggle button. I chose not to because:

- **OS preference is the right default** — If someone set their system to dark mode, they want dark mode everywhere
- **No JavaScript dependency** — The CSS media query works without JavaScript, in RSS readers, and in print
- **No state to manage** — No cookie, no localStorage, no flash of wrong theme on page load

The Contrast theme originally had a `dark_theme: true/false` config option for a site-wide override. I removed that in favor of the automatic approach.

## Print Stylesheet

Technical blog posts get printed. People print Proxmox walkthroughs to have next to the server, or save Ceph commands as PDF references. The default Jekyll output looks terrible when printed — navigation bars, comment widgets, and copy buttons all show up on paper.

### Implementation

The print stylesheet (`_sass/print.sass`, added September 11, 2025) is 134 lines that handle three things:

**1. Hide non-content elements:**

```sass
@media print
  nav, aside, footer, .giscus, .page__comments,
  .btn-copy, .gcse-search, header nav,
  .taxonomies-list, .more
    display: none !important
```

**2. Reset to print-friendly typography:**

```sass
  body
    background: white !important
    color: black !important
    font-family: "Times New Roman", serif !important
    font-size: 12pt !important
    line-height: 1.4 !important
```

**3. Make links useful on paper:**

Printed pages can't be clicked, so links need to show their URLs. The stylesheet appends the URL after each link text so the reader can type it in.

### The SASS Circular Dependency

Adding the print stylesheet triggered a SASS circular dependency nightmare — the same day I added it, I had to restructure the entire SASS architecture to eliminate circular imports. That story is told in [SASS Circular Dependency Nightmare](/sass-circular-dependency-nightmare/).

## Custom Error Pages with Haiku

GitHub Pages serves a generic error page by default. Custom error pages are a small touch that shows the site is maintained and gives lost visitors a way back.

### 404: Page Not Found

```html
---
permalink: /404.html
title: "404: Page not found"
layout: default
sitemap: false
---

<article>
  <header><h1><a href="https://www.rfc-editor.org/rfc/rfc9110.html#name-404-not-found"
    target="_blank">404 Not Found</a></h1></header>
  <p>
    <i>You step in the stream,</i><br>
    <i>but the water has moved on.</i><br>
    <i>This page is not here.</i><br>
  </p>
</article>
```

### 500: Internal Server Error

```html
<p>
  <i>Server, dark within,</i><br>
  <i>Unexpected fault appears,</i><br>
  <i>Try again, please wait.</i><br>
</p>
```

### Design Decisions

- **Haiku format** — A 5-7-5 syllable poem is memorable and human. It signals that a person built this site, not a template generator
- **RFC links** — The error code in the heading links to the actual HTTP specification. A small nod to the technically curious reader
- **`sitemap: false`** — Error pages should never appear in the sitemap
- **Uses the default layout** — The error page has the same navigation as the rest of the site, so the reader can find their way back

The 404 page went through four commits between 2020 and 2024, mostly simplifying it from the original theme's version down to the haiku format.

## Author Bio

Every post ends with an author bio section — a short paragraph with credentials and links to professional profiles. This was added on April 2, 2026 as part of [E-E-A-T improvements for AdSense approval](/improving-eeat-jekyll-adsense/).

### Implementation

The bio lives in `_includes/author-bio.html`:

```html
<div class="author-bio">
  <strong>About the Author:</strong>
  <a href="/about/">Michael McGarrah</a> is a Cloud Architect with 25+ years
  in enterprise infrastructure, machine learning, and system administration.
  He holds an M.S. in Computer Science (AI/ML) from Georgia Tech and a B.S.
  in Computer Science from NC State University, and is currently pursuing an
  Executive MBA at UNC Wilmington.
  <span class="author-links">
    <a href="https://www.linkedin.com/in/michaelmcgarrah/" rel="me">LinkedIn</a> ·
    <a href="https://github.com/mcgarrah" rel="me">GitHub</a> ·
    <a href="https://orcid.org/0000-0001-8935-1293" rel="me">ORCID</a> ·
    <a href="https://scholar.google.com/citations?user=Lt7T2SwAAAAJ" rel="me">Google Scholar</a> ·
    <a href="/resume/">Resume</a>
  </span>
</div>
```

### Why It Matters

- **E-E-A-T signals** — Google's Experience, Expertise, Authoritativeness, and Trustworthiness framework rewards content with clear author attribution. The bio provides credentials, the `rel="me"` links establish identity across platforms
- **Reader trust** — A reader deciding whether to follow a Ceph walkthrough wants to know the author has relevant experience
- **Professional visibility** — Every post becomes a touchpoint to LinkedIn, GitHub, ORCID, and the resume

The bio includes dark mode support via SASS theme variables and is automatically included in every post via the `post.html` layout.

## Archive Page

The archive page at `/archive/` provides a chronological listing of every post. It's the simplest navigation feature on the site — just titles and dates, sorted newest first.

### History

The archive page has the longest history of any feature on this blog:

- **January 2020** — Original archive include added to the Contrast theme by Niklas Buschmann
- **August 2023** — I created `archive.html` as a standalone page
- **December 2025** — Moved from a temporary `_jmm` debug directory to `_layouts/archive.html` (a cleanup of my own mess)

It works alongside the tag pages (`/tags/`), category pages (`/categories/`), and the paginated homepage to give readers multiple ways to find content. The archive is the "just show me everything" option.

## Favicon

The blog has a basic `favicon.ico` file at the site root. It's the minimum viable favicon — a single `.ico` file that browsers pick up automatically without any `<link>` tags in the HTML.

This is one of the items still on the TODO list for improvement — a proper favicon set would include multiple sizes (16x16, 32x32, 180x180 for Apple Touch), PNG format, and a `site.webmanifest` file. But the basic `.ico` works and prevents the 404 that browsers generate when they request `/favicon.ico` and find nothing.

**Update:** This has since been addressed — you will see an upcoming favicon post shortly.

## The Compound Effect

None of these features would justify a blog post on their own. But together they create a compound effect:

- A reader arrives from a Substack link → the site matches their dark mode preference
- They read a Ceph walkthrough → the author bio establishes credibility
- They print the article for reference → the print stylesheet gives them clean output
- They mistype a URL → the haiku 404 page makes them smile instead of bounce
- They want to browse more → the archive page shows everything chronologically

Each feature took less than a day. The total investment was maybe a week across two years. The return is a site that feels maintained and intentional — which matters more than any individual feature.

## Related Posts

- [Improving E-E-A-T for Jekyll and AdSense](/improving-eeat-jekyll-adsense/) — The author bio and credibility signals
- [SASS Circular Dependency Nightmare](/sass-circular-dependency-nightmare/) — Triggered by adding the print stylesheet
- [Jekyll Website Optimization Part 1](/jekyll-website-optimization-part-1/) — Dark mode and theme improvements
- [Jekyll Website Optimization Part 2](/jekyll-website-optimization-part-2/) — Error pages and UX polish
- [How the Sausage Is Made](/jekyll-markdown-feature-reference/) — Full feature inventory
