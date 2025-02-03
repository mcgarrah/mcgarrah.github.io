---
title:  "Adding a `sitemap.xml` file to Jekyll for Google Indexing"
layout: post
published: false
---

Adding a `sitemap.xml` for the posts of a Jekyll website is an important part of getting Google Search to index your website appropriately. I have an interest in this working well so I can use the Google Indices for a local search bar to find things on my Jekyll website. It would also be nice to have it indexed so people can find my posts.

The Google Search Console says the automagically generated [sitemaps.xml](https://www.mcgarrah.org/sitemap.xml) is invalid for this website.

``` text
Sitemap can be read, but has errors
Invalid URL 115 instances
This is not a valid URL. Please correct it and resubmit.
Examples
    URL: /devstudio/
```

jekyll-sitemaps is missing `baseurl` or `url` in config

https://talk.jekyllrb.com/t/jekyll-sitemap-not-adding-base-url/6918/3

https://github.com/orgs/community/discussions/23341

<!-- excerpt-end -->

Three approaches are available...

1. Generate a the file myself with code (no plugins).
2. Modify the plugin `jekyll-sitemap` or pickup changes coming for it.
3. Generate the `sitemap.xml` using an external process like Github Workflow

## Static sitemap.xml options

[Jekyll - Generating a sitemap.xml without a plugin](https://www.independent-software.com/generating-a-sitemap-xml-with-jekyll-without-a-plugin.html)

[Jekyll Sitemap Generator Plugin](https://github.com/jekyll/jekyll-sitemap)

I have a problem with multiple Github Websites under one domain

**mcgarrah.github.io** and **resume** are both under root **mcgarrah.org** and **mcgarrah.org/resume** which was challenging to initially setup...

So the https://mcgarrah.org/resume is a different github website and Jekyll instance from https://mcgarrah.org site.

[Jekyll-Sitemap: adding url that are not in the project](https://talk.jekyllrb.com/t/jekyll-sitemap-adding-url-that-are-not-in-the-project/6920/3)

Possible solution in `jekyll-sitemap` plugin not merged yet...

- [Possibility to add pages that are not in the project #295](https://github.com/jekyll/jekyll-sitemap/issues/295)

- [Allow generating sitemap_index files #300](https://github.com/jekyll/jekyll-sitemap/pull/300)

TODO: Need to exclude the "PAGES##" sections as duplicates...

[How to include URLs from Secondary Project in Main Site's sitemap??](https://www.reddit.com/r/Jekyll/comments/1egcfsh/how_to_include_urls_from_secondary_project_in/)

[Github Pages: How to include URLs from Secondary Project in Main Site's sitemap??](https://www.reddit.com/r/github/comments/1eiqxpm/github_pages_how_to_include_urls_from_secondary/)

---

Completely different path to `sitemap.xml` using Github Workflow:

- [github.com/cicirello/generate-sitemap](https://github.com/cicirello/generate-sitemap)

---

For something completely different...

[Jekyll GitHub Pages](https://davemateer.com/2019/07/28/Jekyll-Github-Pages) is worth a quick read for the plugins and configuration setup by Dave Mateer's.

[Peer Review Blog posts](https://davemateer.com/2016/10/17/Blog-with-Jekyll-and-host-for-free#peer-review-your-blog-posts)
