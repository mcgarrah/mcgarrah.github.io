# McGarrah Technical Blog - Technology Stack

## Core Technologies

### Static Site Generator
- **Jekyll 4.4.1** - Ruby-based static site generator
- **Ruby 3.0+** - Programming language runtime
- **Bundler** - Ruby dependency management
- **Liquid** - Template engine for dynamic content

### Frontend Technologies
- **HTML5** - Semantic markup structure
- **SASS/SCSS** - CSS preprocessing with variables and mixins
- **JavaScript ES6+** - Modern client-side functionality
- **Responsive CSS** - Mobile-first design approach

### Build System
- **GitHub Actions** - CI/CD pipeline automation
- **GitHub Pages** - Static site hosting and deployment
- **Bundler** - Ruby gem dependency resolution
- **npm** - JavaScript package management for security scanning

## Dependencies

### Jekyll Plugins (Gemfile)
```ruby
gem "jekyll", "~> 4.4.1"
gem "jekyll-feed", "~> 0.17.0"        # RSS/Atom feed generation
gem "jekyll-sitemap", "~> 1.4.0"      # XML sitemap creation
gem "jekyll-paginate", "~> 1.1.0"     # Post pagination
gem "jekyll-seo-tag", "~> 2.8.0"      # SEO meta tags
gem "webrick", "~> 1.9.1"             # Local development server
```

### JavaScript Dependencies (package.json)
```json
{
  "mermaid": "^11.0.0",      # Diagram rendering
  "katex": "^0.16.9",        # Mathematical notation
  "clipboard": "^2.0.11"     # Copy-to-clipboard functionality
}
```

### Custom Plugins
- **tag_category_generator.rb** - Automatic page generation for taxonomies

## Development Commands

### Local Development
```bash
# Install dependencies
bundle install
npm install

# Start development server
bundle exec jekyll serve
# or
./start-jekyll.sh

# Build for production
bundle exec jekyll build

# Update dependencies
bundle update
npm update
```

### Content Management
```bash
# Create new post
touch _posts/$(date +%Y-%m-%d)-post-title.md

# Move draft to published
mv _drafts/draft-title.md _posts/$(date +%Y-%m-%d)-draft-title.md

# Preview with drafts
bundle exec jekyll serve --drafts
```

### Maintenance
```bash
# Security audit
npm audit
bundle audit

# Dependency updates
bundle update
npm update

# Clean build artifacts
bundle exec jekyll clean
```

## Configuration Files

### Jekyll Configuration (_config.yml)
- **Site metadata** - Title, description, author information
- **SEO settings** - Canonical URLs, social profiles, structured data
- **Plugin configuration** - Feed, sitemap, pagination settings
- **Navigation structure** - Menu items and external links
- **Analytics integration** - Google Analytics and AdSense
- **Comment system** - Giscus configuration

### Build Configuration
- **.github/workflows/** - CI/CD pipeline definitions
- **Gemfile** - Ruby dependency specifications
- **package.json** - JavaScript dependency tracking
- **.gitignore** - Version control exclusions
- **CNAME** - Custom domain configuration

## External Integrations

### Analytics and SEO
- **Google Analytics (G-F90DVB199P)** - Traffic analysis
- **Google Custom Search (50dc9b6524efa45a0)** - Site search
- **Google AdSense (ca-pub-2421538118074948)** - Optional monetization
- **Structured Data** - Schema.org markup for search engines

### Social and Professional
- **GitHub** - Source code hosting and issue tracking
- **LinkedIn** - Professional networking integration
- **ORCID (0000-0001-8935-1293)** - Academic identifier
- **Google Scholar** - Research publication tracking
- **ResearchGate** - Academic networking

### Content Features
- **Giscus Comments** - GitHub Discussions-based commenting
- **Mermaid Diagrams** - Technical diagram rendering
- **KaTeX** - Mathematical notation support
- **Font Awesome** - Icon library for UI elements

## Performance Considerations

### Optimization Strategies
- **Static generation** - Pre-built HTML for fast delivery
- **Image compression** - Optimized assets for web delivery
- **CSS minification** - Reduced stylesheet sizes
- **CDN delivery** - GitHub Pages global distribution

### Monitoring
- **Lighthouse CI** - Performance and accessibility testing
- **SEO health checks** - Automated validation
- **Security scanning** - CodeQL analysis for vulnerabilities
- **Dependency monitoring** - Dependabot automated updates

## Development Environment

### Requirements
- **Ruby 3.0+** - Language runtime
- **Node.js 16+** - JavaScript runtime for tooling
- **Git** - Version control system
- **Text editor** - VS Code, Vim, or similar

### Recommended Setup
```bash
# Ruby version management
rbenv install 3.2.0
rbenv local 3.2.0

# Install Jekyll and dependencies
gem install bundler jekyll
bundle install

# Node.js dependencies
npm install

# Start development
./start-jekyll.sh
```