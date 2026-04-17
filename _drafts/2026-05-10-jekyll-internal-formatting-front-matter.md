---
title:  "Jekyll Internal Formatting: Front Matter, Parsing Engines, and Content Syntax"
layout: post
categories: [technical, jekyll]
tags: [jekyll, markdown, front-matter, kramdown, liquid, formatting, abbreviations]
---

A deep dive into the internal formatting and syntax conventions used in this Jekyll blog — front matter structure, parsing engine behavior, abbreviation definitions, and content conventions that have evolved over 139+ posts.

<!-- excerpt-end -->

## Abbreviation Definitions in Markdown

Jekyll's kramdown parser supports [abbreviation definitions](https://kramdown.gettalong.org/syntax.html#abbreviations) that automatically wrap matching text in `<abbr>` tags with tooltips. I use these across posts for technical acronyms.

Here's a useful grep command to extract all abbreviation definitions from published posts:

```shell
grep "^\*\[" _posts/*.md | cut -d":" -f 2- | sort | uniq
```

Current abbreviations in use across the blog:

```text
*[BIOS]: Basic Input/Output System, is a type of firmware that is embedded in a computer motherboard and is responsible for starting up the system.
*[CLI]: command line interface
*[CMOS]: Complementary Metal-Oxide-Semiconductor - A CMOS chip stores the settings like date & time, fan speed, booting sequence.
*[CT]: Container
*[DVI]: Digital Visual Interface
*[Gbps]: Gigabits per second is a unit of measurement for data transfer rate. Typically used to describe internet speed or the capacity of network connections.
*[HA]: High Availability
*[IOMMU]: Input-Output Memory Management Unit
*[ISP]: Internet Service Provider which is a company that provides customers access to the internet.
*[JNLP]: Java Network Launch Protocol
*[NIC]: Network Interface Card is a component of a computer that connects it to the network.
*[NPAPI]: Netscape Plugin Application Programming Interface
*[PVE]: Proxmox Virtual Environment
*[SDN]: Software Defined Networking
*[VM]: Virtual Machine
*[WSLv2]: Windows Subsystem for Linux
*[eMMC]: embedded MultiMediaCard (embedded flash memory)
*[lede]: introductory section in journalism
```

These should be standardized and potentially moved to an `_includes/` partial or `_data/` file for consistency across posts.

## Front Matter Conventions

The full SEO-optimized front matter template used for new posts:

```yaml
---
title: "Your Post Title"
layout: post
categories: [category1, category2]
tags: [tag1, tag2, tag3]
excerpt: "Brief description for listings"
description: "Detailed meta description for SEO (150-160 chars)"
image: /assets/images/post-image.png
author: Michael McGarrah
date: YYYY-MM-DD
last_modified_at: YYYY-MM-DD
published: true
seo:
  type: BlogPosting
  date_published: YYYY-MM-DD
  date_modified: YYYY-MM-DD
---
```

TODO: Document the evolution of front matter fields used across the blog — from minimal early posts to the full SEO-optimized template.

## Kramdown vs Other Parsing Engines

TODO: Document kramdown-specific features used (abbreviations, footnotes, attribute lists) and gotchas encountered.

## Liquid Template Syntax in Posts

TODO: Document Liquid usage patterns within post content — when to use includes, when to use inline Liquid, and edge cases with code blocks.

## Content Formatting Standards

TODO: Document excerpt separators, image sizing conventions, link formatting patterns, and code block usage.
