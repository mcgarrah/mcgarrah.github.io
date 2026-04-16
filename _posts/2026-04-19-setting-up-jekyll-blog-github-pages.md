---
title: "Building This Blog: Jekyll on GitHub Pages from Zero to 130+ Posts"
layout: post
categories: [web-development, jekyll]
tags: [jekyll, github-pages, tutorial, getting-started, seo, gdpr, giscus, pandoc, github-actions]
excerpt: "I've been writing about technology since 2004. This blog has lived on WordPress, Blogger, and now Jekyll on GitHub Pages. Here's how I set it up, what I added along the way, and what I'd do differently if I started over."
description: "How to set up a Jekyll blog on GitHub Pages with custom domain, GitHub Actions CI/CD, SEO optimization, GDPR compliance, Giscus comments, Pandoc PDF exports, and the lessons learned from building mcgarrah.org over 130+ posts."
date: 2026-04-19
last_modified_at: 2026-04-19
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-19
  date_modified: 2026-04-19
---

I've been writing about technology since 2004 — first on WordPress, then Blogger, and now Jekyll on GitHub Pages. The migration to Jekyll happened in 2023 when I wanted full control over the site without paying for hosting or fighting with WordPress plugin conflicts.

Two years and 130+ posts later, the blog has grown from a basic theme into a heavily customized platform with [Mermaid diagrams](/jekyll-mermaid-diagram-rendering-challenges/), [GDPR compliance](/implementing-gdpr-compliance-jekyll-adsense/), [Pandoc PDF exports](/jekyll-pandoc-exports-plugin/), and an [automated SEO pipeline](/jekyll-seo-health-checks/). This post covers how I set it all up — the order of operations, the decisions I made, and what I'd do differently.

For the day-to-day writing reference (markdown syntax, code blocks, diagrams, embeds), see the companion post: [How the Sausage Is Made: Every Feature Powering This Jekyll Blog](/jekyll-markdown-feature-reference/).

<!-- excerpt-end -->

## Why Jekyll?

After years on WordPress, I wanted:

- **No hosting costs** — GitHub Pages is free
- **Version control** — every post is a Git commit with full history
- **Markdown** — write in a text editor, not a web form
- **Speed** — static HTML is fast, no database queries
- **Control** — no plugin conflicts, no PHP updates, no security patches

The tradeoff is that Jekyll requires comfort with the command line, Git, and Ruby. If you're reading this blog, you probably have that.

## Create the GitHub Pages Repository

GitHub Pages serves a static site from any repository named `<username>.github.io`. Create the repo, clone it, and you have a working site:

```bash
git clone git@github.com:<username>/<username>.github.io.git
cd <username>.github.io
```

GitHub automatically builds and serves anything pushed to the default branch at `https://<username>.github.io`.

## Pick a Theme

Rather than starting from a blank `index.html`, pick a Jekyll theme. This blog uses the [Contrast](https://github.com/niklasbuschmann/contrast) theme by Niklas Buschmann — minimal, responsive, and easy to extend. I've since modified it heavily, but the bones are still Contrast.

The fastest way to start:

1. Fork or copy the theme repository into your `<username>.github.io` repo
2. Run `bundle install` to pull dependencies
3. Run `bundle exec jekyll serve` to preview locally at `http://localhost:4000`

```bash
gem install bundler jekyll
bundle install
bundle exec jekyll serve
```

See [Running GitHub Pages Jekyll Locally](/github-pages-jekyll-locally/) for the full local development setup including Ruby version management.

## Initial Configuration

The `_config.yml` file controls everything. The essential settings to change immediately:

```yaml
title: "Your Site Title"
description: "A brief description for SEO and social sharing"
url: "https://www.yourdomain.com"
author:
  name: "Your Name"
  email: "you@example.com"

plugins:
  - jekyll-feed          # RSS feed
  - jekyll-sitemap       # XML sitemap for search engines
  - jekyll-paginate      # Post pagination
  - jekyll-seo-tag       # SEO meta tags and structured data
  - jekyll-redirect-from # Redirect support for moved pages
```

Changes to `_config.yml` require restarting `jekyll serve` — it's not hot-reloaded like post content.

### File Structure

After theme setup, the key files:

```
├── _config.yml          # Site configuration
├── _layouts/            # Page templates (default, post, page)
├── _includes/           # Reusable HTML components
├── _sass/               # SCSS stylesheets
├── _posts/              # Published articles (YYYY-MM-DD-title.md)
├── _drafts/             # Work-in-progress (no date prefix)
├── _plugins/            # Custom Ruby plugins
├── assets/              # CSS, JS, images, fonts
├── Gemfile              # Ruby dependencies
├── CNAME                # Custom domain mapping
└── index.html           # Homepage
```

## Custom Domain

To serve the site from a custom domain instead of `<username>.github.io`:

1. Create a `CNAME` file in the repository root with your apex domain (no `www`):

    ```text
    mcgarrah.org
    ```

2. Configure DNS with your registrar:
   - **A records** for the apex domain (`@`) pointing to GitHub Pages IPs:
     - `185.199.108.153`
     - `185.199.109.153`
     - `185.199.110.153`
     - `185.199.111.153`
   - **CNAME record** for `www` pointing to `<username>.github.io`

3. In the GitHub repository settings under Pages, set the custom domain to the apex domain (e.g., `mcgarrah.org`) and enable **Enforce HTTPS**

GitHub handles the Let's Encrypt certificate automatically. With this configuration, GitHub Pages serves the site from the apex domain and automatically 301-redirects `www` to the apex.

The [GitHub Pages custom domain docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site) cover the full DNS setup.

I'm currently [migrating my domains from Squarespace to Porkbun](/name-service-registrars/) for better API access and lower costs — relevant if you're choosing a registrar for a new blog.

### The www vs Apex Domain Trap

I ran into a subtle but damaging SEO issue that's worth documenting. My original CNAME file was set to `www.mcgarrah.org`, but my `_config.yml` had:

```yaml
url: "https://mcgarrah.org"
```

This created a mismatch across the entire site:

| Component | Domain Used |
|-----------|------------|
| CNAME (GitHub Pages primary) | `www.mcgarrah.org` |
| `_config.yml` url | `mcgarrah.org` |
| jekyll-seo-tag canonical URLs | `mcgarrah.org` |
| jekyll-sitemap URLs | `mcgarrah.org` |
| robots.txt sitemap reference | `mcgarrah.org` |

GitHub Pages treated `www.mcgarrah.org` as the primary domain and 301-redirected the apex `mcgarrah.org` → `www.mcgarrah.org`. But every canonical tag and sitemap entry pointed to `mcgarrah.org` (no www). Google Search Console saw the site served from one domain with canonical tags pointing to another — splitting crawl data and confusing search rankings.

The fix was straightforward: change the CNAME file from `www.mcgarrah.org` to `mcgarrah.org` and update the GitHub Pages custom domain setting to match. My existing DNS records already supported this:

```text
A    @    185.199.108.153  (GitHub Pages)
A    @    185.199.109.153  (GitHub Pages)
A    @    185.199.110.153  (GitHub Pages)
A    @    185.199.111.153  (GitHub Pages)
CNAME www mcgarrah.github.io
```

After the change, the redirect flipped correctly:

- `https://mcgarrah.org` → **200 OK** (primary)
- `https://www.mcgarrah.org` → **301 redirect** to `https://mcgarrah.org/`

The lesson: **your CNAME file, `_config.yml` url, and GitHub Pages custom domain setting must all agree on the same domain.** If you use the apex domain in `_config.yml`, use it everywhere. The `www` CNAME DNS record still exists so GitHub Pages can handle the redirect — it just shouldn't be the primary domain in the CNAME file.

## GitHub Actions CI/CD

GitHub Pages can build Jekyll sites automatically, but a custom GitHub Actions workflow gives you more control — pinned Ruby versions, additional plugins not in the GitHub Pages whitelist, and build validation:

```yaml
# .github/workflows/jekyll.yml
name: Build and Deploy Jekyll
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true
      - run: bundle exec jekyll build
      - uses: actions/upload-pages-artifact@v3
  deploy:
    needs: build
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
```

This is essential once you add custom plugins (like the [tag/category generator](/jekyll-markdown-feature-reference/#blog-specific-features) or [Pandoc exports](/jekyll-pandoc-exports-plugin/)) that aren't supported by GitHub's default Jekyll build.

I also run an [SEO health check workflow](/jekyll-seo-health-checks/) on every push that validates canonical URLs, sitemap XML, meta tags, structured data, and broken links.

## SEO Setup

SEO was an afterthought when I started. It shouldn't have been. Here's what I added over time:

### jekyll-seo-tag Plugin

This plugin generates Open Graph tags, Twitter cards, JSON-LD structured data, and canonical URLs automatically from your `_config.yml` and post front matter:

```yaml
# _config.yml
seo:
  type: Person
  name: "Michael McGarrah"
  links:
    - "https://www.linkedin.com/in/michaelmcgarrah/"
    - "https://github.com/mcgarrah"
```

### Per-Post SEO

Every post should include a `description` and `seo` block in front matter:

```yaml
---
title: "Post Title"
description: "A longer description for search engines, separate from excerpt."
seo:
  type: BlogPosting
  date_published: 2026-04-19
  date_modified: 2026-04-19
---
```

I learned this the hard way — see [Jekyll SEO Sitemap and Canonical URL Fixes](/jekyll-seo-sitemap-canonical-url-fixes/) and [Improving E-E-A-T for Jekyll and AdSense](/improving-eeat-jekyll-adsense/) for the full story.

### Sitemap and Robots.txt

The `jekyll-sitemap` plugin generates `sitemap.xml` automatically. I had to [fix sitemap bloat](/jekyll-sitemap-bloat-tags-categories-pagination/) from tag and category pages inflating the sitemap with low-value URLs.

## Comments with Giscus

I chose [Giscus](https://giscus.app/) for comments — it uses GitHub Discussions as the backend, so there's no separate service to maintain. Readers need a GitHub account to comment, which is fine for a technical blog.

Configuration in `_config.yml`:

```yaml
giscus:
  repo: mcgarrah/mcgarrah.github.io
  repo_id: R_kgDOKBKIdw
  category: Announcements
  category_id: DIC_kwDOKBKId84Cq3DK
  mapping: pathname
  theme: preferred_color_scheme
  loading: lazy
```

The `_includes/` template renders the Giscus widget at the bottom of each post. Comments are stored as GitHub Discussions and are fully searchable.

## GDPR Cookie Consent

Required for Google AdSense and Analytics in the EU. I built a [custom GDPR implementation](/implementing-gdpr-compliance-jekyll-adsense/) that:

- Detects EU users via timezone and IP geolocation (with fallback)
- Shows a consent banner only to EU visitors
- Blocks Analytics and AdSense scripts until consent is given
- Stores consent in localStorage with secure cookie attributes

This was more complex than expected — the [AdSense verification fix](/adsense-verification-gdpr-script-loading-fix/) documents how my initial implementation was *too* aggressive and blocked Google's own verification crawler.

## Resume as a Separate Repository

My [online resume](https://www.mcgarrah.org/resume/) lives in a separate `resume` repository. GitHub Pages serves project repositories at `<username>.github.io/<repo-name>/`, so with the custom domain it appears at `www.mcgarrah.org/resume/`.

This keeps the resume's Jekyll theme, dependencies, and build independent from the blog. The [Pandoc exports integration](/jekyll-pandoc-exports-resume-integration/) generates downloadable PDF and DOCX versions at build time.

I explored [merging the two sites](/merging-two-jekyll-websites-architectural-analysis/) but decided the separation is worth the minor complexity.

## Favicon

Drop a `favicon.ico` in the repository root. For broader browser support, generate multiple sizes using [RealFaviconGenerator](https://realfavicongenerator.net/) and add the `<link>` tags to your `_includes/head.html` or `_layouts/default.html`.

## What I'd Do Differently

If I started over today:

1. **Set up SEO from day one.** Adding `description`, structured data, and canonical URLs retroactively across 130+ posts was painful.

2. **Use `jekyll-redirect-from` immediately.** I renamed several posts early on and broke links. The redirect plugin would have prevented that.

3. **Pick a theme with dark mode support.** Contrast supports it but I haven't exposed the toggle yet. Starting with it enabled would have been easier.

4. **Automate image optimization.** I still manually compress images. A build-time optimization step would save time and improve performance.

5. **Write the feature reference post first.** Having a single place to check syntax for every feature would have saved hours of Googling the same Mermaid or KaTeX syntax repeatedly.

## Related Posts

- [How the Sausage Is Made: Every Feature Powering This Jekyll Blog](/jekyll-markdown-feature-reference/) — The companion reference for all formatting and features
- [Jekyll Pandoc Exports Plugin](/jekyll-pandoc-exports-plugin/) — PDF and DOCX generation from posts
- [Pandoc Exports Resume Integration](/jekyll-pandoc-exports-resume-integration/) — Using Pandoc for the downloadable resume
- [Jekyll Website Optimization Part 1](/jekyll-website-optimization-part-1/) — Performance and structure improvements
- [Jekyll Website Optimization Part 2](/jekyll-website-optimization-part-2/) — Further refinements
- [Implementing GDPR Compliance for Jekyll and AdSense](/implementing-gdpr-compliance-jekyll-adsense/) — Cookie consent implementation
- [Jekyll SEO Health Checks](/jekyll-seo-health-checks/) — Automated SEO validation in CI
- [Jekyll Sitemap Bloat](/jekyll-sitemap-bloat-tags-categories-pagination/) — Fixing inflated sitemaps
- [Merging Two Jekyll Websites](/merging-two-jekyll-websites-architectural-analysis/) — Why I kept the blog and resume separate
- [Running GitHub Pages Jekyll Locally](/github-pages-jekyll-locally/) — Local development setup

## References

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Jekyll Step-by-Step Tutorial](https://jekyllrb.com/docs/step-by-step/01-setup/)
- [Contrast Theme](https://github.com/niklasbuschmann/contrast)
- [GitHub Pages Custom Domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [Giscus](https://giscus.app/)
- [RealFaviconGenerator](https://realfavicongenerator.net/)
