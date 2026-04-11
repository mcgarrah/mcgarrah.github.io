---
title: "Setting Up a Jekyll Blog on GitHub Pages"
layout: post
categories: [web-development, jekyll]
tags: [jekyll, github-pages, tutorial, getting-started]
excerpt: "A walkthrough of setting up a Jekyll blog on GitHub Pages from scratch — covering repository creation, custom domains, themes, favicons, and the initial customizations that turn a default site into something personal."
published: false
---

This post covers the initial setup steps I went through when building this blog. If you're starting a Jekyll site on GitHub Pages from zero, this is the order of operations that worked for me.

For the day-to-day writing reference (markdown syntax, code blocks, diagrams, embeds), see the companion post: [Jekyll and Markdown Feature Reference for This Blog]({% post_url 2026-04-01-jekyll-markdown-feature-reference %}).

<!-- excerpt-end -->

## Create the GitHub Pages Repository

GitHub Pages serves a static site from any repository named `<username>.github.io`. Create the repo, clone it, and you have a working site:

```bash
# Create the repo on GitHub, then clone it
git clone git@github.com:<username>/<username>.github.io.git
cd <username>.github.io
```

GitHub will automatically build and serve anything pushed to the default branch at `https://<username>.github.io`.

### Add a Jekyll Theme

Rather than starting from a blank `index.html`, pick a Jekyll theme. This blog uses the [Contrast](https://github.com/niklasbuschmann/contrast) theme. The fastest way to start:

1. Fork or copy the theme repository into your `<username>.github.io` repo
2. Run `bundle install` to pull dependencies
3. Run `bundle exec jekyll serve` to preview locally at `http://localhost:4000`

```bash
gem install bundler jekyll
bundle install
bundle exec jekyll serve
```

### Initial File Structure

After theme setup, the key files to customize first:

```
├── _config.yml          # Site title, description, URL, author
├── index.html           # Homepage (usually provided by theme)
├── about.md             # Your About page
├── Gemfile              # Ruby dependencies
└── _posts/              # Your blog articles
```

## Custom Domain with CNAME

To serve the site from a custom domain instead of `<username>.github.io`:

1. Create a `CNAME` file in the repository root containing your domain:

    ```text
    www.mcgarrah.org
    ```

2. Configure DNS with your registrar — add a CNAME record pointing `www` to `<username>.github.io`

3. In the GitHub repository settings under Pages, verify the custom domain and enable HTTPS

GitHub's documentation on [custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site) covers the DNS details.

## Add a Favicon

Drop a `favicon.ico` file in the repository root. Most themes will pick it up automatically. For broader browser support, generate multiple sizes using a tool like [favicon.io](https://favicon.io/) or [RealFaviconGenerator](https://realfavicongenerator.net/) and add the appropriate `<link>` tags to your `_includes/head.html` or `_layouts/default.html`.

## Customize the About Page

The About page is typically `about.md` or `README.md` mapped to `/about/`. Edit it with your background, links, and professional information. This blog's About page uses the `page` layout:

```yaml
---
title: "About"
permalink: "/about/"
layout: page
---
```

## Update _config.yml

The `_config.yml` file controls everything about your site. The essential settings to change immediately:

```yaml
title: "Your Site Title"
description: "A brief description for SEO and social sharing"
url: "https://www.yourdomain.com"
author:
  name: "Your Name"
  email: "you@example.com"
```

This file is also where you configure navigation, external links, plugins, analytics, and comment systems. Changes to `_config.yml` require restarting `jekyll serve` — it's not hot-reloaded.

## Resume as a Separate Repository

If you have a resume site (like my [online resume](https://www.mcgarrah.org/resume/)), it can live in a separate repository and be served as a subpath of your main site using GitHub Pages project sites.

The resume repository is named `resume` and GitHub Pages serves it at `<username>.github.io/resume/`. With a custom domain configured on the main site, it automatically appears at `www.mcgarrah.org/resume/`.

This keeps the resume's Jekyll theme, dependencies, and build independent from the blog.

## GitHub Actions for CI/CD

GitHub Pages can build Jekyll sites automatically, but a custom GitHub Actions workflow gives you more control — pinned Ruby versions, additional plugins, and build validation:

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

## What's Next

Once the basic site is running, the [Jekyll and Markdown Feature Reference]({% post_url 2026-04-01-jekyll-markdown-feature-reference %}) covers everything you need for writing content — markdown formatting, code highlighting, images, YouTube embeds, Mermaid diagrams, KaTeX math, Font Awesome icons, and more.

## References

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Jekyll Step-by-Step Tutorial](https://jekyllrb.com/docs/step-by-step/01-setup/)
- [Contrast Theme](https://github.com/niklasbuschmann/contrast)
- [GitHub Pages Custom Domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
