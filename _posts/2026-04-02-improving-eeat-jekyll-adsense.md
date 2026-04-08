---
title: "Improving E-E-A-T Signals for Google AdSense Approval on Jekyll"
layout: post
categories: [web-development, technical]
tags: [google, adsense, jekyll, github-pages, seo, eeat, structured-data, wikidata]
excerpt: "After another AdSense rejection, I shifted focus from technical fixes to E-E-A-T — Experience, Expertise, Authoritativeness, and Trustworthiness. Here's what I changed and why."
description: "Practical E-E-A-T improvements for a Jekyll blog targeting Google AdSense approval, including structured author data, Wikidata entries, content clustering, and dateModified signals."
last_modified_at: 2026-04-02
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-02
  date_modified: 2026-04-02
---

In my [previous post on AdSense rejection debugging](/adsense-approval-failure-remediation/), I focused on technical issues — sitemap 404 errors, missing contact pages, and thin content analysis. Those were real problems worth fixing, but they weren't the whole story.

After more research, I realized I was ignoring something Google cares deeply about: **E-E-A-T** — Experience, Expertise, Authoritativeness, and Trustworthiness. These are the signals Google's quality raters use to evaluate whether a site deserves to surface in search results and, by extension, whether it's worthy of showing ads.

The frustrating part? I *have* strong E-E-A-T credentials. 25+ years in the industry, an M.S. in Computer Science from Georgia Tech focused on AI/ML, published research, and a career spanning cloud architecture, data science, and enterprise infrastructure. But none of that was visible to Google's crawlers.

<!-- excerpt-end -->

## What Is E-E-A-T and Why Does It Matter for AdSense?

Google's [Search Quality Rater Guidelines](https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf) define E-E-A-T as:

- **Experience** — Does the author have first-hand experience with the topic?
- **Expertise** — Does the author have the knowledge or skill for the topic?
- **Authoritativeness** — Is the author or site a recognized authority?
- **Trustworthiness** — Is the site accurate, honest, and safe?

For AdSense, Google wants to place ads on sites that won't embarrass their advertisers. A site with strong E-E-A-T signals looks like a legitimate publication. A site without them — even with great content — looks like an anonymous blog that could disappear tomorrow.

## The Problem: Hidden Credentials

My site had all the raw ingredients but none of the presentation:

- **No author byline on posts** — 125 articles with no visible attribution
- **No author bio** — Nothing connecting content to a real, credentialed person
- **Flat `author` config** — Just a string `"Michael McGarrah"` with no structured data
- **No `rel="me"` links** — External profiles existed in the sidebar but weren't machine-readable
- **No `dateModified`** — Only 4 of 125 posts had `last_modified_at` in front matter
- **No content clustering** — Proxmox/Ceph posts existed in isolation with no hub page
- **No Wikidata entry** — No authoritative external source linking my identity to my work

Google's crawlers saw a site with good content but no verifiable author. That's a red flag.

## Fix 1: Structured Author Data in Jekyll Config

The `jekyll-seo-tag` plugin generates structured data from `_config.yml`. My author field was a plain string:

```yaml
# Before
author: "Michael McGarrah"
```

Changed to a hash with contact details so the plugin emits richer `Person` schema:

```yaml
# After
author:
  name: "Michael McGarrah"
  email: "mcgarrah@gmail.com"
  uri: "https://mcgarrah.org/about/"
```

## Fix 2: Author Byline on Every Post

Every post now shows who wrote it. I added a byline to the `_includes/meta.html` template with a `rel="author"` link:

```html
<span class="post-byline">By <a href="/about/" rel="author">Michael McGarrah</a></span>
```

This is what Google's quality raters are explicitly trained to look for — visible author attribution on content pages.

## Fix 3: Author Bio on Every Post

Created `_includes/author-bio.html` — a compact bio box that appears at the bottom of every post with credentials and `rel="me"` links to authoritative profiles:

- LinkedIn, GitHub, ORCID, Google Scholar, and my [resume](/resume/)
- Education credentials (Georgia Tech M.S., NC State B.S.)
- Professional summary (25+ years, cloud architecture, ML)

This gives Google multiple verifiable signals connecting the content to a real person with real credentials. The `rel="me"` attribute is specifically how search engines verify cross-platform identity.

## Fix 4: `rel="me"` on Navigation Links

The footer/sidebar already linked to my external profiles, but without `rel="me"`. Updated `_includes/menu.html` to add the attribute to LinkedIn, GitHub, GitLab, ORCID, Stack Overflow, Google Scholar, and ResearchGate links.

## Fix 5: About Page Restructured for E-E-A-T

The [About page](/about/) was rewritten to front-load verifiable credentials:

- Professional background with years of experience
- Education with links to university programs
- Blog topic expertise areas
- External profile links with descriptions
- Link to the [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) as proof of topical depth

## Fix 6: `dateModified` on 63 Posts

The `jekyll-seo-tag` plugin uses the `last_modified_at` front matter field to emit `dateModified` in structured data. Only 4 of my 125 posts had this field.

I wrote a script to pull the last git commit date for every post from 2023 onward and added `last_modified_at` to 59 additional posts. The `jekyll-seo-tag` plugin now emits proper `dateModified` for 63 posts, telling Google the content is actively maintained.

```bash
# Example: git log gives the real last-edit date
git log -1 --format='%ai' -- _posts/2025-10-26-usb-drive-smart.md
# 2026-02-04 (content was updated, not just the original post date)
```

## Fix 7: Wikidata Entry

This was the most unexpected change. [Wikidata](https://www.wikidata.org/) is the structured data backend for Wikipedia, and Google uses it heavily for Knowledge Panels. I created [Q138858864](https://www.wikidata.org/wiki/Q138858864) with:

- All external identifiers (ORCID, Google Scholar, GitHub, GitLab, LinkedIn, Stack Exchange, ResearchGate)
- Education history with qualifiers (degrees, majors, institutions)
- Occupation and field of work
- Official website link
- References on every statement

This is the most reliable path to getting a Google Knowledge Panel, which is the ultimate E-E-A-T signal — Google itself vouching for your identity.

## Fix 8: Content Cluster Hub Page

My Proxmox and Ceph posts are my strongest content — deep technical articles based on hands-on homelab experience. But several had **zero internal links** to related posts. Google uses internal link structure to identify topical authority.

Created the [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) as a pillar page that organizes 20+ related articles into logical sections:

- Getting Started with Proxmox
- Ceph Storage
- Dell Wyse 3040 Cluster
- Monitoring & Maintenance
- Supporting Infrastructure

Then added "Related Articles" sections to the 5 orphaned posts that had no internal links, connecting them back into the cluster.

## Summary of All E-E-A-T Changes

| Change | E-E-A-T Signal | Files Modified |
|--------|---------------|----------------|
| Structured author config | Expertise, Trustworthiness | `_config.yml` |
| Author byline on posts | Authoritativeness | `_includes/meta.html` |
| Author bio with credentials | Experience, Expertise | `_includes/author-bio.html`, `_layouts/post.html` |
| `rel="me"` on profile links | Authoritativeness | `_includes/menu.html` |
| About page restructured | All four pillars | `README.md` |
| `dateModified` on 63 posts | Trustworthiness | 59 post files |
| Wikidata entry (Q138858864) | Authoritativeness | External |
| Hub page + cross-links | Expertise, Experience | 6 files + new page |
| Google Search Console DNS verification | Trustworthiness | External |

## What's Left

The one thing I can't automate: **external citations**. Getting other sites to link to my content is the strongest E-E-A-T signal but requires manual effort. My plan:

- Share the [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) on r/homelab and r/Proxmox
- Answer Proxmox/Ceph questions on Stack Overflow with references to appropriate posts
- Engage on the Proxmox community forums

I do all of these already when I see something I can contribute too quickly but I'll just press on the gas a bit and do a few extra.

## The Bigger Picture

None of these changes altered my actual content. The articles are the same. The expertise is the same. What changed is how that expertise is *presented* to machines.

That's the frustrating reality of modern SEO and AdSense approval — having credentials isn't enough. You have to make them machine-readable, cross-referenced, and independently verifiable. A 25-year career means nothing to a crawler if it can't find structured data confirming it.

I'll update this post and the [original AdSense debugging post](/adsense-approval-failure-remediation/) when I resubmit and get a response.

## Related Articles

- [Google AdSense Approval Failure: Debugging the 'Site Isn't Ready' Rejection](/adsense-approval-failure-remediation/) — The technical fixes that preceded this work
- [Implementing GDPR Compliance for Jekyll Sites](/implementing-gdpr-compliance-jekyll-adsense/) — Cookie consent for AdSense
- [Adding Google Custom Search to Jekyll Website](/adding-google-custom-search-jekyll/) — Search integration
- [Jekyll SEO, Sitemap, and Canonical URL Fixes](/jekyll-seo-sitemap-canonical-url-fixes/) — Earlier SEO work
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — The content cluster hub page
