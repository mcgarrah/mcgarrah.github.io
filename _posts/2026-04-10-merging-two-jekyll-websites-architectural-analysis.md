---
title: "Merging Two Jekyll Websites: Architectural Analysis and Integration Strategies"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, github-pages, architecture, website-migration, multi-site, integration]
excerpt: "Analyzing the feasibility of merging a technical blog and resume site into a unified Jekyll website, exploring architectural challenges and integration strategies."
description: "Architectural analysis of merging a Jekyll blog and resume site into a single repository, comparing collection-based integration, subdirectory approaches, and hybrid layout strategies with complexity assessments."
date: 2026-04-10
last_modified_at: 2026-04-10
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-10
  date_modified: 2026-04-10
---

Following my previous article on [managing multiple Jekyll sites under one domain](/managing-multiple-jekyll-sites-sitemap-challenges/), I've been exploring whether it makes sense to merge my two Jekyll websites into a single repository. This is the analysis phase — not an implementation article. I'm laying out the architectural differences and weighing the options before committing to a direction. A large part of my day job as a Solutions Architect involves exactly this kind of trade-off analysis, so I figured I'd write it up.

<!-- excerpt-end -->

## Current Architecture Overview

### Main Blog Site (`mcgarrah.github.io`)

- **Purpose**: Technical blog with 130+ articles spanning 2001-2026
- **Theme**: Custom minimal theme with extensive customization
- **Content Structure**: Posts, pages, categories, tags, archives
- **Key Features**: 
  - Blog-focused with chronological content
  - Category and tag organization
  - Search functionality via Google Custom Search
  - Comment system using Giscus
  - GDPR compliance with cookie consent
  - Mermaid diagram support
  - Code syntax highlighting with copy buttons

### Resume Site (`resume`)

- **Purpose**: Professional resume and portfolio
- **Theme**: Specialized resume theme with data-driven content
- **Content Structure**: Single-page resume with modular sections
- **Key Features**:
  - Data-driven content from `_data/data.yml`
  - Print-optimized layouts
  - Professional styling with multiple color themes
  - Modular sections (experience, education, skills, etc.)
  - Automatic PDF and DOCX generation via [jekyll-pandoc-exports](/jekyll-pandoc-exports-plugin/)

## Architectural Differences Analysis

### 1. Content Management Approaches

**Blog Site**: File-based content management

```yaml
# Traditional Jekyll structure
_posts/2025-01-02-article-title.md
_pages/about.md
categories.html
tags.html
```

**Resume Site**: Data-driven content management

```yaml
# Centralized data structure
_data/data.yml  # All content in structured YAML
_includes/      # Modular HTML components
_layouts/       # Specialized resume layouts
```

### 2. Theme Architecture Incompatibility

**Blog Theme Structure**:

- Minimal, content-focused design
- Navigation-heavy with multiple pages
- Responsive blog layout with sidebar
- Custom SASS with variables for theming

**Resume Theme Structure**:

- Professional, print-optimized design
- Single-page application approach
- Sidebar-based layout with sections
- Bootstrap-based responsive framework

### 3. Configuration Conflicts

**Blog Configuration** (`_config.yml`):

```yaml
title: "McGarrah Technical Blog"
permalink: /:title/
paginate: 4
show_excerpts: true
plugins:
  - jekyll-feed
  - jekyll-sitemap
  - jekyll-paginate
  - jekyll-seo-tag
  - jekyll-redirect-from
```

**Resume Configuration** (`_config.yml`):

```yaml
title: McGarrah Resume
baseurl: "/resume"
theme_skin: ceramic
compress-site: yes
plugins:
  - jekyll-sitemap
  - jekyll-seo-tag
  - jekyll-pandoc-exports
```

## Integration Strategies

### Strategy 1: Resume as Jekyll Collection

**Approach**: Convert resume content to a Jekyll collection within the main site.

**Implementation**:

```yaml
# _config.yml additions
collections:
  resume:
    output: true
    permalink: /resume/:name/

# Directory structure
_resume/
  index.md
  print.md
_data/
  resume.yml  # Migrated from resume site
```

**Pros**:

- Maintains existing blog functionality
- Clean URL structure (`/resume/`)
- Unified sitemap and SEO
- Single repository maintenance

**Cons**:

- Requires significant theme integration work
- May lose specialized resume styling
- Print optimization challenges

### Strategy 2: Subdirectory Integration

**Approach**: Move resume content into a subdirectory of the main site.

**Implementation**:

```
mcgarrah.github.io/
├── _posts/           # Blog content
├── _layouts/
│   ├── default.html  # Blog layouts
│   ├── resume.html   # Resume-specific layout
│   └── print.html    # Print layout
├── resume/
│   ├── index.html
│   ├── print.html
│   └── assets/       # Resume-specific assets
└── _data/
    └── resume.yml
```

**Pros**:

- Preserves resume functionality
- Maintains URL structure
- Easier migration path

**Cons**:

- Dual theme maintenance
- Asset management complexity
- Potential styling conflicts

### Strategy 3: Hybrid Layout System

**Approach**: Create a unified theme that supports both blog and resume layouts.

**Implementation**:

```yaml
# Front matter switching
---
layout: blog-post     # For articles
layout: resume-page   # For resume sections
layout: hybrid-home   # Unified homepage
---
```

**Pros**:

- Single theme maintenance
- Consistent branding
- Flexible content types

**Cons**:

- Complex theme development
- Potential performance impact
- Testing complexity across layouts

## Technical Challenges

### 1. Asset Management Conflicts

**Blog Assets**:

- Font Awesome icons via CDN
- Custom fonts (PT Sans)
- Blog-specific JavaScript (cookie consent, copy buttons)
- Extensive image library

**Resume Assets**:

- Bootstrap framework
- jQuery dependencies
- Professional headshot
- PDF/DOCX generation via Pandoc
- Company logos

**Resolution Approach**:

```scss
// Unified SASS structure
_sass/
├── base/           # Shared styles
├── blog/           # Blog-specific styles
├── resume/         # Resume-specific styles
└── components/     # Reusable components
```

### 2. Navigation Integration

**Current Blog Navigation**:

```yaml
navigation:
  - {file: "index.html", icon: blog}
  - {file: "archive.html", icon: list}
  - {file: "tags.html", title: Tags, icon: tags}
  - {file: "categories.html", title: Categories, icon: th-list}
  - {file: "search.html", title: Search, icon: search}
  - {url: "/about/", title: About, icon: user}
  - {url: "/contact/", title: Contact, icon: envelope}
  - {url: "/privacy/", title: Privacy, icon: lock}
```

**Proposed Unified Navigation**:

```yaml
navigation:
  - {file: "index.html", title: "Blog", icon: blog}
  - {file: "resume/index.html", title: "Resume", icon: user}
  - {file: "archive.html", title: "Archive", icon: list}
  - {file: "search.html", title: "Search", icon: search}
```

### 3. Data Structure Harmonization

**Challenge**: Resume site uses extensive YAML data structures that don't align with blog post front matter.

**Current Resume Data Structure**:

```yaml
experiences:
  - role: Lead Principal Engineer
    time: Oct 2021 - Present
    company: Envestnet, Inc.
    details: |
      Building large scale cloud platforms...
```

**Proposed Integration**:

```yaml
# _data/site.yml
blog:
  title: "McGarrah Technical Blog"
  description: "Technical content..."
  
resume:
  personal:
    name: "Michael McGarrah"
    tagline: "Data Scientist / Cloud Architect"
  experiences: [...]
  education: [...]
```

## Complexity Assessment

### Low Complexity Options

1. **Keep Separate Sites**: Maintain current architecture with improved sitemap coordination
2. **Simple Subdirectory**: Move resume as static subdirectory with minimal integration

### Medium Complexity Options

1. **Collection-Based Integration**: Convert resume to Jekyll collection with custom layouts
2. **Shared Navigation**: Integrate navigation while maintaining separate themes

### High Complexity Options

1. **Full Theme Merger**: Create unified theme supporting both content types
2. **Dynamic Layout Switching**: Context-aware layouts based on content type

## What I'd Actually Recommend

If I were going to do this, I'd take a phased approach:

### Phase 1: Collection Integration (Recommended)

- Convert resume to Jekyll collection
- Migrate data from `_data/data.yml` to collection files
- Create resume-specific layouts within main theme
- Maintain print functionality

### Phase 2: Asset Consolidation

- Merge CSS frameworks (minimize Bootstrap conflicts)
- Consolidate JavaScript dependencies
- Optimize image assets

### Phase 3: Navigation Unification

- Integrate resume into main navigation
- Update sitemap generation
- Implement breadcrumb navigation

## The Case for Staying Separate

Honestly, maintaining separate sites may be the most pragmatic answer given the architectural gap:

**Benefits of Separation**:

- Specialized optimization for each use case
- Independent deployment and maintenance
- Clear separation of concerns
- Reduced complexity and testing burden

**Improved Coordination**:

- Shared GitHub Actions for cross-site sitemap generation
- Consistent branding and navigation links
- Coordinated deployment workflows

## Conclusion

Merging these two sites is technically feasible but would require substantial work. The two sites have fundamentally different architectures:

- **Blog**: Content-focused, file-based, minimal theme
- **Resume**: Data-driven, single-page, Bootstrap-based

The collection-based integration (Strategy 1) is the cleanest path, but it's a real project — not a weekend task. For now, I've been improving coordination between the two sites instead: unified sitemaps, consistent SEO plugins, and shared tooling like [jekyll-pandoc-exports](/jekyll-pandoc-exports-plugin/) for document generation.

The SEO benefits of a single repository are real (one sitemap, one `robots.txt`, consistent structured data), but they need to be weighed against the development effort and the risk of breaking a resume site that works well as-is.

## Next Steps

If I decide to proceed:

1. Prototype the collection-based integration on a branch
2. Audit all asset dependencies and potential conflicts
3. Design unified layouts that support both content types
4. Plan the migration step by step
5. Test across devices and use cases before switching over

## Related Articles

- [Managing Multiple Jekyll Sites Under One Domain: Sitemap Challenges](/managing-multiple-jekyll-sites-sitemap-challenges/) — The sitemap and SEO problems that motivated this analysis
- [Building a Jekyll Plugin for Automated Document Exports](/jekyll-pandoc-exports-plugin/) — The PDF/DOCX generation plugin now integrated into the resume site
- [Integrating Jekyll-Pandoc-Exports Into a Real Project](/jekyll-pandoc-exports-resume-integration/) — Real-world integration of the export plugin into the resume site
