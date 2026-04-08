# McGarrah Technical Blog - Project Structure

## Directory Organization

### Core Jekyll Structure
```
mcgarrah.github.io/
├── _config.yml              # Main Jekyll configuration
├── _layouts/                 # Page templates (default, post, page, etc.)
├── _includes/               # Reusable HTML components
├── _sass/                   # SCSS stylesheets and variables
├── _posts/                  # Blog articles (100+ markdown files)
├── _drafts/                 # Unpublished content in development
├── _plugins/                # Custom Ruby plugins
├── _data/                   # YAML data files (Font Awesome icons)
└── _site/                   # Generated static site (build output)
```

### Content Management
- **_posts/** - Published articles with date-based naming (YYYY-MM-DD-title.md)
- **_drafts/** - Work-in-progress articles without publication dates
- **_data/font-awesome/** - Icon definitions for UI components
- **categories.html** - Category listing page
- **tags.html** - Tag cloud and organization
- **archive.html** - Chronological post listing

### Asset Organization
```
assets/
├── css/                     # Additional stylesheets
├── js/                      # JavaScript functionality
├── images/                  # Blog post images and screenshots
├── fonts/                   # Custom web fonts (PT Sans)
├── pdfs/                    # Technical documentation
├── binaries/                # Software downloads
└── exes/                    # Portable applications
```

### Development Infrastructure
```
.github/
├── workflows/               # GitHub Actions CI/CD
│   ├── jekyll.yml          # Site build and deployment
│   ├── codeql.yml          # Security scanning
│   └── seo-health-check.yml # SEO validation
└── dependabot.yml          # Dependency updates
```

## Core Components

### Layout System
- **default.html** - Base template with navigation and footer
- **post.html** - Blog article layout with metadata and comments
- **page.html** - Static page template
- **home.html** - Homepage with post excerpts and pagination
- **category_page.html** - Category-specific post listings
- **tag_page.html** - Tag-specific post listings

### Include Components
- **menu.html** - Navigation bar with responsive design
- **sidebar.html** - Social links and external profiles
- **analytics.html** - Google Analytics integration
- **cookie-consent.html** - GDPR compliance banner
- **meta.html** - SEO meta tags and structured data

### Plugin Architecture
- **tag_category_generator.rb** - Automatic page generation for tags/categories
- **jekyll-feed** - RSS/Atom feed generation
- **jekyll-sitemap** - XML sitemap creation
- **jekyll-paginate** - Post pagination
- **jekyll-seo-tag** - Comprehensive SEO optimization

## Architectural Patterns

### Static Site Generation
- **Build-time processing** - Content compiled to static HTML
- **GitHub Pages hosting** - Automatic deployment on push
- **CDN distribution** - Fast global content delivery
- **Version control** - Full site history in Git

### Content Organization
- **Chronological structure** - Posts organized by publication date
- **Taxonomic classification** - Categories and tags for content discovery
- **Excerpt system** - Automatic content previews with custom separators
- **Future post scheduling** - Controlled publication timing

### Responsive Design
- **Mobile-first approach** - Optimized for all screen sizes
- **Progressive enhancement** - Core functionality without JavaScript
- **Semantic HTML** - Accessible markup structure
- **CSS Grid/Flexbox** - Modern layout techniques

### Performance Optimization
- **Minimal dependencies** - Lightweight JavaScript libraries
- **Image optimization** - Compressed assets for fast loading
- **CSS preprocessing** - SASS compilation for maintainable styles
- **Caching strategies** - Browser and CDN caching headers

## Integration Points

### External Services
- **Google Analytics** - Traffic and user behavior tracking
- **Google Custom Search** - Site-wide search functionality
- **Giscus Comments** - GitHub Discussions-based commenting
- **Font Awesome** - Icon library for UI elements

### Development Workflow
- **Local development** - Jekyll serve for testing
- **Continuous integration** - Automated builds and testing
- **Security scanning** - CodeQL analysis for vulnerabilities
- **SEO monitoring** - Automated health checks and validation