---
title: "Merging Two Jekyll Websites: Architectural Analysis and Integration Strategies"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, github-pages, architecture, website-migration, multi-site, integration]
excerpt: "Analyzing the feasibility of merging a technical blog and resume site into a unified Jekyll website, exploring architectural challenges and integration strategies."
published: false
---

Following my previous article on [managing multiple Jekyll sites under one domain]({% post_url 2025-12-30-managing-multiple-jekyll-sites-sitemap-challenges %}), I've been exploring whether it's feasible to merge my two Jekyll websites into a single unified site. This analysis examines the architectural differences between my main blog (`mcgarrah.github.io`) and resume site (`resume`) to determine integration strategies.

<!-- excerpt-end -->

## Current Architecture Overview

### Main Blog Site (`mcgarrah.github.io`)
- **Purpose**: Technical blog with 100+ articles spanning 2001-2026
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
  - PDF generation capabilities

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
```

**Resume Configuration** (`_config.yml`):
```yaml
title: McGarrah Resume
baseurl: "/resume"
theme_skin: ceramic
compress-site: yes
# No pagination or blog-specific plugins
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
- PDF generation assets
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
  - {file: "README.md", icon: user}
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

## Implementation Complexity Assessment

### Low Complexity Options

1. **Keep Separate Sites**: Maintain current architecture with improved sitemap coordination
2. **Simple Subdirectory**: Move resume as static subdirectory with minimal integration

### Medium Complexity Options

1. **Collection-Based Integration**: Convert resume to Jekyll collection with custom layouts
2. **Shared Navigation**: Integrate navigation while maintaining separate themes

### High Complexity Options

1. **Full Theme Merger**: Create unified theme supporting both content types
2. **Dynamic Layout Switching**: Context-aware layouts based on content type

## Recommended Approach

Based on this analysis, I recommend a **phased integration approach**:

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

## Alternative: Maintain Separation

Given the significant architectural differences, maintaining separate sites may be the most pragmatic approach:

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

While technically feasible, merging these two Jekyll sites would require substantial architectural work due to their fundamentally different approaches:

- **Blog site**: Content-focused with file-based management
- **Resume site**: Data-driven with specialized layouts

The **collection-based integration** offers the best balance of functionality and maintainability, but requires significant development effort. For most use cases, **maintaining separate sites with improved coordination** may be the more practical solution.

The decision ultimately depends on:
- Available development time
- Maintenance preferences
- SEO requirements
- Content management workflow preferences

## Next Steps

If proceeding with integration:

1. **Prototype Phase**: Create a branch testing collection-based integration
2. **Asset Audit**: Catalog all dependencies and potential conflicts
3. **Layout Development**: Design unified layouts supporting both content types
4. **Migration Planning**: Develop step-by-step migration process
5. **Testing Strategy**: Comprehensive testing across devices and use cases

---

*This analysis provides the foundation for making an informed decision about Jekyll site architecture. The complexity assessment suggests that while integration is possible, the effort required may not justify the benefits for most use cases.*