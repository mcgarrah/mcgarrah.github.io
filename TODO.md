# Jekyll Website TODO List

## 🚀 Next Sprint (Immediate Focus - URGENT: AdSense Review)

### 🛡️ GDPR Compliance (PRIORITY 1 - Due: Next Day)
- [x] **URGENT**: Implement cookie consent banner (GDPR compliance)
- [x] **URGENT**: Update privacy policy with GDPR language
- [x] **URGENT**: Make AdSense loading conditional on consent
- [x] **URGENT**: Add consent management JavaScript
- [x] **URGENT**: Fixed hardcoded values to use Jekyll config
- [x] **TESTING**: Verify both AdSense and Analytics are blocked before consent ✅
- [x] **TESTING**: Verify scripts load after consent given ✅
- [x] **COMPLETE**: GDPR compliance ready for AdSense review 🎉
- [ ] Verify Mermaid diagrams work on Github and not just local - SASS article has one

### Quick Wins (< 2 hours each)
- [x] Add Google Search Console verification file
- [x] Update meta descriptions for better SEO
- [ ] Add missing alt tags to images
- [ ] Create proper favicon set (multiple sizes)
- [x] Inconsistent tags and categories in articles

### SEO Foundation (High Impact)
- [x] Add jekyll-seo-tag plugin for better meta tags and structured data
- [x] Implement proper Open Graph and Twitter Card meta tags
- [x] Add JSON-LD structured data for articles
- [x] Create comprehensive robots.txt file
- [x] Configure site URL and SEO metadata in _config.yml
- [x] Add Google site verification code
- [x] Create logo image for structured data

## 📈 Performance & UX Improvements

### User Experience Enhancements
- [ ] Create reading progress indicator
- [ ] Add "related posts" section to post layout
- [ ] Implement breadcrumb navigation
- [ ] Add share buttons for social media
- [ ] Add tag cloud visualization

### Performance Optimizations
- [ ] Implement lazy loading for images
- [ ] Add image optimization and responsive images
- [ ] Optimize CSS delivery (inline critical CSS)
- [ ] Add WebP image format support

## 🔧 Content & Site Management

### Content Organization
- [ ] Consolidate and clean up old posts from 2001-2016
- [ ] Create post templates for common topics (technical, personal)
- [ ] Add author bio section to posts
- [ ] Implement post series/collections feature

### Content Creation Tools
- [ ] PDF version of resume auto-generation
- [ ] Create technical cheat sheets section
- [ ] Add code snippet collection
- [ ] Implement photo gallery for projects

## 🛡️ Security & Compliance

### Security Headers
- [ ] Add Content Security Policy (CSP) headers
- [ ] Implement HTTP security headers (HSTS, X-Frame-Options, etc.)
- [ ] Add security headers

### Privacy & Compliance
- [ ] **MOVED TO PRIORITY 1**: Implement cookie consent banner (GDPR compliance)
- [ ] Add privacy-focused analytics (Plausible or similar)
- [ ] Add data processing transparency documentation
- [ ] Implement right to data deletion process

## 📊 Analytics & Monitoring

### Performance Monitoring
- [ ] Implement performance monitoring
- [ ] Add uptime monitoring
- [ ] Create analytics dashboard

## 🌐 Advanced Features (Future)

### Accessibility & Internationalization
- [ ] Add keyboard navigation support
- [ ] Implement skip-to-content links for accessibility
- [ ] Multi-language support (English/Spanish)

### Advanced Functionality
- [ ] Add newsletter signup
- [ ] Implement full-text search with indexing
- [ ] Add comment moderation system
- [ ] Create mobile app manifest (PWA)
- [ ] Implement service worker for offline functionality

### Infrastructure & Scaling
- [ ] Set up CDN for assets
- [ ] Implement caching strategy
- [ ] Set up automated backups
- [ ] Add loading states for dynamic content

## 🔍 SEO & Discoverability (Nice to Have)

- [ ] Add XML sitemap index for better organization
- [ ] Implement canonical URLs for duplicate content
- [ ] Add meta robots tags for better crawling control
- [ ] Create HTML sitemap page for users
- [ ] Create custom 403 and other HTTP error pages

## Completed Items

- [x] Jekyll code copy to clipboard buttons
- [x] GitHub Comments integration (Giscus)
- [x] Tags and Categories system
- [x] RSS feed and sitemap
- [x] Google Analytics and AdSense integration
- [x] Scheduled builds for future posts
- [x] Reading time indicator
- [x] Update Jekyll to latest version (4.4.1)
- [x] Basic favicon implementation (favicon.ico exists)
- [x] Google AdSense ads.txt file
- [x] Add site search functionality (Google Custom Search)
- [x] Add proper error pages (404, 500) with custom styling
- [x] Add dark/light theme toggle (implemented via CSS `prefers-color-scheme` media query)
- [x] Add print stylesheet
- [x] Create archive page with year/month filtering (basic archive page exists at /archive/)
- [x] robots.txt file (comprehensive custom version with proper directives)
- [x] Jekyll SEO Tag plugin for automated meta tags and structured data
- [x] Open Graph and Twitter Card meta tags
- [x] JSON-LD structured data for articles and author information
- [x] Enhanced site configuration with proper URLs and SEO metadata

## Notes

### Technical Stack
- Jekyll version: 4.4.1
- Ruby version: 3.2.0
- Hosted on: GitHub Pages
- Custom domain: www.mcgarrah.org
- SSL/TLS: Enabled via GitHub Pages

### Content Management
- Total posts: 100+ articles (2001-2025)
- Post pagination: 4 posts per page
- Future posts: Disabled (future: false)
- Excerpt separator: `<!-- excerpt-end -->`
- Permalink structure: `/:title/`

### Search & Discovery
- Google Custom Search Engine: 50dc9b6524efa45a0
- XML Sitemap: Auto-generated via jekyll-sitemap
- RSS Feed: Auto-generated via jekyll-feed
- Archive page: Chronological post listing
- Tags system: Automated tag pages
- Categories system: Automated category pages

### User Experience Features
- Automatic dark/light theme switching (prefers-color-scheme)
- Reading time indicators on posts
- Code copy-to-clipboard buttons
- Print-optimized stylesheets
- Custom 404/500 error pages with haiku
- Responsive design with sidebar navigation
- Mobile-friendly layout

### Analytics & Monetization
- Google Analytics: G-F90DVB199P
- Google AdSense: ca-pub-2421538118074948
- AdSense ads.txt file configured

### Comments & Engagement
- Giscus integration (GitHub Discussions)
- Repository: mcgarrah/mcgarrah.github.io
- Category: Announcements (DIC_kwDOKBKId84Cq3DK)
- Theme: Matches site's preferred color scheme

### Build & Deployment
- Automated builds via GitHub Actions
- Scheduled builds for future post releases
- Jekyll plugins: jekyll-feed, jekyll-sitemap, jekyll-paginate
- Custom tag/category generator plugin

### Performance Features
- Font optimization with PT Sans web fonts
- Syntax highlighting with Rouge
- KaTeX support for mathematical expressions
- Optimized CSS with SASS preprocessing

## 📋 Project Management

### Current Sprint Status
- **In Progress**: None
- **Blocked**: None
- **Next Up**: Quick Wins section

### Effort Estimates
- 🟢 Quick (< 2 hours)
- 🟡 Medium (2-8 hours) 
- 🔴 Large (> 8 hours)

### Impact vs Effort Matrix
- **High Impact, Low Effort**: SEO Foundation, Quick Wins
- **High Impact, High Effort**: Performance Optimizations, Content Organization
- **Low Impact, Low Effort**: Nice to have features
- **Low Impact, High Effort**: Advanced Features (future consideration)


Blog Post SEO Front Matter

**Enhanced front matter template:**
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
