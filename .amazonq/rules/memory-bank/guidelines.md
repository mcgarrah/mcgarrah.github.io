# McGarrah Technical Blog - Development Guidelines

## Code Quality Standards

### File Header Documentation
All custom code files must include comprehensive header comments with:
- **Copyright notice** with year and author name
- **License information** (MIT License standard)
- **Purpose description** explaining the file's functionality
- **Author contact** information (email and website)
- **Repository reference** for source code location

Example format:
```javascript
/*!
 * GDPR Cookie Consent Management
 * Copyright (c) 2025 Michael McGarrah
 * Licensed under MIT License
 * 
 * Custom implementation for Jekyll blog GDPR compliance
 * Author: Michael McGarrah (mcgarrah@gmail.com)
 * Website: https://mcgarrah.org
 * Repository: https://github.com/mcgarrah/mcgarrah.github.io
 */
```

### JavaScript Standards

#### Code Structure
- **IIFE Pattern** - Wrap all JavaScript in immediately invoked function expressions
- **Strict Mode** - Always use `'use strict';` at function scope
- **Const/Let Usage** - Prefer `const` for immutable values, `let` for variables
- **Descriptive Constants** - Use UPPER_CASE for configuration constants

#### Error Handling
- **Graceful Degradation** - Provide fallback functionality for failed operations
- **Try-Catch Blocks** - Wrap async operations and external API calls
- **Timeout Handling** - Set reasonable timeouts for network requests
- **Localhost Detection** - Skip external service loading during development

#### Async Patterns
```javascript
async function checkUserRegion() {
    try {
        const response = await fetch('https://ipapi.co/json/', { timeout: 3000 });
        const data = await response.json();
        return EU_COUNTRIES.includes(data.country_code);
    } catch (error) {
        // Fallback to timezone detection
        return isEUUser();
    }
}
```

### Ruby Plugin Development

#### Class Organization
- **Module Namespace** - All plugins within `Jekyll` module
- **Generator Classes** - Inherit from `Jekyll::Generator` for build-time processing
- **Page Classes** - Inherit from `Jekyll::Page` for generated content
- **Safe Flag** - Always mark generators as `safe true` for GitHub Pages compatibility

#### Naming Conventions
- **CamelCase Classes** - `TagPageGenerator`, `CategoryPage`
- **Snake_case Methods** - `generate`, `initialize`
- **Descriptive Variables** - `tag`, `posts`, `category` for clarity
- **File Naming** - Use underscores for multi-word filenames

#### URL Generation
- **Lowercase Paths** - Convert all URLs to lowercase
- **Hyphen Separation** - Replace spaces and underscores with hyphens
- **Directory Structure** - Organize generated pages in logical hierarchies

Example pattern:
```ruby
@dir = File.join('categories', category.downcase.gsub(' ', '-').gsub('_', '-'))
```

### Python Environment
- **Always use `.venv`** — Never install packages globally or with `--user`/`--break-system-packages`
- **Create per-project venvs** — `python3 -m venv .venv` in the repo root
- **Activate before use** — `source .venv/bin/activate && pip install ...`
- **Add `.venv` to `.gitignore`** — Virtual environments must not be committed
- **No system-level pip** — Respect PEP 668 managed environments on macOS

## Architectural Patterns

### Jekyll Integration
- **Liquid Template Variables** - Use Jekyll site variables for configuration
- **Layout Inheritance** - Reference appropriate layout files for generated pages
- **Data Binding** - Set page data for template consumption
- **Title Generation** - Create descriptive, user-friendly page titles

### Configuration Management
- **Site Variables** - Access Jekyll configuration via `site` object
- **Environment Detection** - Check hostname for development vs production
- **Feature Flags** - Use configuration to enable/disable functionality
- **External Service IDs** - Store API keys and service IDs in Jekyll config

### Performance Optimization
- **Lazy Loading** - Load external scripts only when needed
- **Conditional Loading** - Skip unnecessary operations in development
- **Script Deduplication** - Check for existing scripts before adding new ones
- **Async Script Loading** - Use async attributes for non-blocking execution

## Content Standards

### Markdown Formatting
- **Front Matter** - Include YAML front matter for all content files
- **Date Format** - Use YYYY-MM-DD format for post filenames
- **Category/Tag Usage** - Apply consistent taxonomy for content organization
- **Excerpt Separators** - Use `<!-- excerpt-end -->` for custom excerpts
- **Redirect Support** - Use `redirect_from` in front matter when renaming or moving posts

Example redirect front matter:
```yaml
---
title: "New Post Title"
redirect_from:
  - /old-url/
  - /another-old-url/
---
```

### Post Date Consistency
When creating or rescheduling posts, four date values must all agree:
- **Filename date** - `YYYY-MM-DD` prefix in the filename
- **`date:`** - Explicit date in front matter (if present)
- **`seo.date_published`** - Structured data publish date
- **`seo.date_modified`** / **`last_modified_at`** - Must be >= `date_published`

If renaming a file to change its publish date, update all four. A `last_modified_at` or `seo.date_modified` that predates `date_published` looks wrong to search engines.

### Draft and Future Post Detection in Templates
Jekyll does not expose a `post.draft` flag. To detect post status in Liquid templates:
- **Drafts**: `post.path contains '_drafts/'` — works because `post.path` includes the source directory
- **Future posts**: `post.date > site.time` — compares post date against build timestamp

Both checks are inert in production builds (without `--drafts`/`--future` flags) since those posts are excluded from `site.posts` entirely.

### Asset Organization
- **Image Optimization** - Compress images for web delivery
- **Descriptive Filenames** - Use clear, descriptive names for assets
- **Directory Structure** - Organize assets by type and purpose
- **Version Control** - Include all assets in repository for reproducibility

## Security Practices

### Homelab SSH Access
- **Shared credentials file** at `~/.shared-creds` contains SSH credentials for LXC containers and VMs
- **INI-style format** with section headers per host (e.g., `[caddy-lxc]`) and `username:` / `password:` fields
- **File permissions** must be 600 (`chmod 600 ~/.shared-creds`)
- **Usage**: Use `sshpass -p '<password>' ssh <user>@<ip>` to access homelab hosts when SSH key auth is not configured
- **Adding new hosts**: Append a new `[section-name]` block with username and password
- **Never** echo or display credentials in command output — read the file silently

### Privacy Compliance
- **GDPR Implementation** - Implement proper consent management for EU users
- **Cookie Management** - Use secure cookie attributes (SameSite=Lax)
- **Local Storage** - Store consent preferences locally for persistence
- **Regional Detection** - Implement fallback methods for user location

### External Dependencies
- **Dependency Scanning** - Regular security audits with npm audit
- **Version Pinning** - Use specific version ranges in package.json
- **CDN Usage** - Load external libraries from trusted CDNs
- **Fallback Strategies** - Provide alternatives when external services fail

## Testing and Validation

### Development Workflow
- **Local Testing** - Use Jekyll serve for development testing
- **Draft Management** - Use _drafts folder for work-in-progress content
- **Build Validation** - Ensure clean builds before deployment
- **Link Checking** - Validate internal and external links

### Automated Checks
- **CI/CD Pipeline** - GitHub Actions for automated testing
- **Security Scanning** - CodeQL analysis for vulnerability detection
- **SEO Validation** - Automated SEO health checks via seo-health-check.yml
- **Dependency Updates** - Dependabot for security updates

### SEO Health Check Workflow
The `seo-health-check.yml` workflow validates on every push to main:
- **Canonical URL consistency** - Verifies all `<link rel="canonical">` tags use mcgarrah.org domain
- **Sitemap validation** - Checks XML validity and correct domain usage
- **Robots.txt verification** - Ensures correct sitemap reference
- **Meta tag checks** - Validates description and Open Graph tags
- **Structured data** - Checks for JSON-LD presence
- **Link validation** - Lychee link checker for broken links
- **Content quality** - Duplicate titles, generic link text, missing alt text
- **Lighthouse CI** - Performance, accessibility, and SEO scoring

Note: Canonical URL checks must match `<link` tags specifically to avoid false positives from syntax-highlighted code blocks in blog posts.

## Documentation Requirements

### Code Comments
- **Inline Documentation** - Explain complex logic and business rules
- **Function Documentation** - Describe parameters and return values
- **Configuration Notes** - Document configuration options and defaults
- **TODO Comments** - Mark areas for future improvement

### README Updates
- **Installation Instructions** - Keep setup documentation current
- **Feature Documentation** - Document new features and capabilities
- **Troubleshooting** - Include common issues and solutions
- **Contributing Guidelines** - Provide clear contribution instructions

## Maintenance Practices

### Regular Updates
- **Dependency Management** - Monthly dependency updates
- **Security Patches** - Immediate application of security fixes
- **Performance Monitoring** - Regular performance audits
- **Content Review** - Periodic review of outdated content

### Backup and Recovery
- **Version Control** - Full site history in Git repository
- **Asset Backup** - Ensure all assets are version controlled
- **Configuration Backup** - Document all external service configurations
- **Recovery Testing** - Periodic testing of site restoration procedures