---
title:  "Jekyll Enhancements Without Plugins"
layout: post
published: false
categories: [technical, jekyll]
tags: [jekyll, plugins, github-pages, enhancements, search, comments, gdpr, seo]
---

A collection of Jekyll enhancements that can be implemented without plugins — useful for GitHub Pages compatibility and reducing dependency complexity. Many of these were evaluated during the build-out of this blog, with some adopted and others deferred.

<!-- excerpt-end -->

## Jekyll Without Plugins Reference

The [Jekyll Codex](https://jekyllcodex.org/without-plugins/) maintains an excellent collection of plugin-free implementations. Here are the ones most relevant to this blog:

### Search

- [Google Custom Search integration](https://jekyllcodex.org/without-plugin/search-google/#) — Implemented on this blog via the [Adding Google Custom Search](/adding-google-custom-search-jekyll/) post.

### Comments

Several approaches were evaluated before settling on Giscus:

- [Jekyll Codex comments overview](https://jekyllcodex.org/without-plugin/comments/)
- [GDPR-compliant comments](https://jekyllcodex.org/blog/gdpr-compliant-comment/) — Relevant to our GDPR implementation
- [GitHub Issues-based comments](https://www.aleksandrhovhannisyan.com/blog/jekyll-comment-system-github-issues/) — Evaluated but Giscus (GitHub Discussions) was preferred
- [Giscus self-hosting](https://github.com/giscus/giscus/blob/main/SELF-HOSTING.md) — Reference for future consideration
  - [Bartosz Gorka's Giscus setup guide](https://bartoszgorka.com/github-discussion-comments-for-jekyll-blog) — Used as reference during implementation
- [Utterances](https://github.com/utterance/utterances) — Predecessor to Giscus, uses GitHub Issues instead of Discussions
- [GitHub Issues API approach](https://aristath.github.io/blog/static-site-comments-using-github-issues-api) — Lower-level alternative

### UX Enhancements

- [Reading time indicator](https://jekyllcodex.org/without-plugin/reading-time-indicator/) — Implemented on this blog
- [Cookie consent](https://jekyllcodex.org/without-plugin/cookie-consent/) — Evaluated; custom GDPR implementation was built instead
- [Breadcrumbs](https://jekyllcodex.org/without-plugin/breadcrumbs/) — Not yet implemented
- [SEO without plugin](https://jekyllcodex.org/without-plugin/seo/#) — Using jekyll-seo-tag plugin instead
- [Share buttons](https://jekyllcodex.org/without-plugin/share-buttons/#) — Not yet implemented
- [Text expand/collapse](https://jekyllcodex.org/without-plugin/text-expand/#) — Not yet implemented

## Jekyll Plugin Development

For cases where plugins are needed:

- [Your First Plugin guide](https://jekyllrb.com/docs/plugins/your-first-plugin/) — Official Jekyll docs
- [reading_time plugin](https://github.com/bdesham/reading_time) — Alternative to without-plugin approach
- [jekyll-analytics](https://github.com/hendrikschneider/jekyll-analytics) — Multi-provider analytics
- [jekyll-seo-tag](https://github.com/jekyll/jekyll-seo-tag) — In use on this blog
- [jekyll-seo-gem](https://github.com/pmarsceill/jekyll-seo-gem) — Alternative SEO approach
- [jekyll-admin](https://github.com/jekyll/jekyll-admin) — Web-based admin interface
- [jekyll-google_search_console_verification_file](https://github.com/erikw/jekyll-google_search_console_verification_file) — GSC verification
- [jemoji](https://github.com/jekyll/jemoji) — GitHub-style emoji support

## Template Branch for Reusable Starter

There is a `clean` branch of this repository that was started as a reusable template for others to use as a starting point with all the blog features (GDPR, SEO, Giscus, Mermaid, etc.) but with personal content removed. The `upstream` branch tracks the original forked theme.

- Compare branches: [upstream...clean](https://github.com/mcgarrah/mcgarrah.github.io/compare/upstream...mcgarrah:mcgarrah.github.io:clean?expand=1)
- The divergence from the original fork has grown significant, making upstream contributions difficult
- The original plan was to break changes into separate merge requests:
  1. Pagination with archives in page counts
  2. Jekyll upgrade to 4.3+
  3. New GitHub Action Workflow
  4. Embedded features for sizing images
  5. Conditional Google Analytics and Google AdSense
  6. RSS Sitemaps

TODO: Evaluate whether the `clean` branch is still viable as a template or if a fresh starter repo would be more practical given the divergence.

## Jekyll Reference Links

- [Jekyll Permalinks](https://jekyllrb.com/docs/permalinks/) — Permalink structure options
- [Jekyll Cheat Sheet](https://devhints.io/jekyll) — Quick reference for Jekyll syntax
- [Generating PDF from Jekyll using Pandoc](https://ognjen.io/generating-pdf-from-jekyll-using-pandoc/) — Original inspiration for the Pandoc exports plugin (now published as [jekyll-pandoc-exports](/jekyll-pandoc-exports-plugin/))
