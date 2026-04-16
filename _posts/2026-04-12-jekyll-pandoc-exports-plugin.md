---
layout: post
title: "Building a Jekyll Plugin for Automated Document Exports - Part 2: Technical Implementation"
categories: [jekyll, ruby, pandoc, automation]
tags: [jekyll-plugin, pandoc, pdf-generation, docx, ruby-gem, documentation]
excerpt: "Technical deep-dive into Jekyll plugin development: hooks system, Pandoc integration, and document generation features. Part 2 of building a professional Ruby gem."
description: "Technical deep-dive into building a Jekyll plugin for automated PDF and DOCX exports using Pandoc, covering the hooks system, incremental builds, Unicode cleanup, CLI tools, and extensible architecture."
date: 2026-04-12
last_modified_at: 2026-04-12
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-12
  date_modified: 2026-04-12
---

<!-- excerpt-end -->

In [Part 1](/ruby-gem-release-automation/), I covered the infrastructure challenges of building a professional Ruby gem with automated releases, documentation, and CI/CD. Now let's dive into the technical implementation of the Jekyll plugin itself. In [Part 3](/jekyll-pandoc-exports-resume-integration/), I'll cover integrating the plugin into a real project and the bugs that surfaced.

The [jekyll-pandoc-exports](https://github.com/mcgarrah/jekyll-pandoc-exports) plugin solves a common problem: automatically generating downloadable PDF and Word document versions of your Jekyll pages using Pandoc.

Jekyll, as a static content website, requires all content to be processed in advance. Often other solutions for PDF and DOCX generation require a server and runtime environment. This is my solution to get those documents types handled with a simple easy to use interface.

## The Problem

While working on my [resume site](https://github.com/mcgarrah/resume), I needed a way to automatically generate PDF and DOCX versions of my resume whenever I updated the markdown content. Manually converting files was tedious and error-prone, especially when making frequent updates.

I also wanted to refresh my Ruby programming skills as I had let them languish for several years. The Jekyll backend that I depend on being based on Ruby was also a factor. I hate not having skills ready for tools I use extensively.

## The Solution

The plugin hooks into Jekyll's build process and automatically generates exports for any page with `docx: true` or `pdf: true` in its front matter:

```yaml
---
title: My Resume
docx: true
pdf: true
---
```

## Key Features

### Automatic Generation

The plugin runs during Jekyll's `post_write` phase, processing all configured collections (pages, posts, custom collections) and generating exports for marked content.

### Configurable Output

Full configuration control through `_config.yml`:

```yaml
pandoc_exports:
  enabled: true
  output_dir: 'downloads'
  collections: ['pages']
  incremental: true
  pdf_options:
    variable: 'geometry:margin=0.75in'
  unicode_cleanup: true
  inject_downloads: false
  image_path_fixes:
    - pattern: 'src="/resume/assets/'
      replacement: 'src="{% raw %}{{site.dest}}{% endraw %}/assets/'
```

The `inject_downloads: false` setting is useful when your theme already has its own download links — as was the case with my resume site's sidebar. The `image_path_fixes` array handles the path rewriting needed when a site uses a `baseurl` like `/resume`.

### Incremental Builds

The plugin only regenerates files when the source content changes, significantly improving build performance:

```ruby
def self.skip_unchanged_file?(site, item, config)
  return false unless config['incremental']
  
  source_mtime = File.mtime(source_file)
  return false if File.mtime(output_file) < source_mtime
  
  true
end
```

### Download Link Injection

Automatically injects styled download links into pages that generate exports, with configurable CSS classes for print-friendly hiding.

## Advanced Features

### Hooks System

Extensible architecture with pre and post-conversion hooks:

```ruby
# Register custom processing
Jekyll::PandocExports::Hooks.register_pre_conversion do |html_content, config, context|
  # Modify HTML before conversion
  html_content.gsub('old-pattern', 'new-pattern')
end
```

### CLI Tools

Standalone command-line interface for batch processing:

```bash
# Convert single file
jekyll-pandoc-exports --file page.html --format pdf

# Process entire site
jekyll-pandoc-exports --source . --destination _site
```

### Performance Monitoring

Built-in statistics tracking with detailed timing and success metrics:

```ruby
@stats.record_processing_start
# ... conversion logic ...
@stats.record_conversion_success(:pdf)
@stats.print_summary(config)
```

## Technical Implementation

### Dependency Validation

The plugin validates required dependencies (Pandoc, LaTeX) at runtime:

```ruby
def self.validate_dependencies
  pandoc_available = system('pandoc --version > /dev/null 2>&1')
  latex_available = system('pdflatex --version > /dev/null 2>&1')
  
  unless pandoc_available
    Jekyll.logger.warn "Pandoc not found. Install with: brew install pandoc"
  end
  
  pandoc_available
end
```

### Unicode Cleanup

Automatic cleanup of problematic Unicode characters that cause LaTeX compilation errors:

```ruby
def self.clean_unicode_characters(html)
  # Remove emoji and symbol ranges that cause LaTeX issues
  html.gsub(/[\u{1F000}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/, '')
end
```

### Template System

Flexible template customization with header, footer, and CSS injection:

```ruby
def self.apply_template(html_content, config)
  template = config['template']
  
  # Add custom CSS
  if !template['css'].empty?
    css_tag = "<style>#{template['css']}</style>"
    html_content = html_content.sub(/<\/head>/, "#{css_tag}\n</head>")
  end
  
  html_content
end
```

## Development Journey

### From Simple Script to Full Plugin

The plugin evolved from a simple script in my resume repository to a full-featured Ruby gem. As covered in [Part 1](/ruby-gem-release-automation/), the infrastructure and release automation consumed significant development time, but enabled rapid iteration on the plugin functionality.

### Testing Infrastructure

Implemented comprehensive test suite with 87 test runs and 176 assertions, covering:

- Configuration validation
- File processing logic
- Hook system functionality
- CLI tool operations
- Error handling scenarios

The automated testing pipeline (detailed in Part 1) runs across multiple Ruby versions and operating systems.

### Professional Documentation

The Read the Docs integration (covered in Part 1) provides professional documentation with:

- Installation guides for multiple platforms
- Configuration reference with examples
- API documentation for hooks system
- CLI usage guide
- Development workflow documentation

## Real-World Usage

The plugin is integrated into my [resume site](https://github.com/mcgarrah/resume), replacing the previous workflow of manually exporting PDFs and committing static files. The integration uncovered several compatibility bugs and required HTML cleanup work to produce clean document output — that full story is covered in [Part 3](/jekyll-pandoc-exports-resume-integration/).

## Future Enhancements

Pandoc's format support opens several directions for the plugin:

- **Additional formats** — ODT for LibreOffice users, RTF for maximum compatibility
- **Site-wide EPUB generation** — aggregate posts or collections into downloadable e-books with proper table of contents and metadata
- **Mermaid diagram support** — render Mermaid JavaScript diagrams to static SVG/PNG for PDF compatibility
- **Enhanced templates** — Liquid support in export templates, per-format CSS injection
- **Batch optimizations** — parallel processing and Jekyll asset pipeline integration

## Getting Started

Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended texlive-latex-extra

# macOS
brew install pandoc
brew install --cask mactex
```

Install the plugin (v0.1.12+ required for Jekyll 3.x / `github-pages` compatibility):

```bash
gem install jekyll-pandoc-exports
```

Add to your `_config.yml`:

```yaml
plugins:
  - jekyll-pandoc-exports
```

Mark pages for export:

```yaml
---
title: My Document
docx: true
pdf: true
---
```

For GitHub Actions CI builds, add a step to install Pandoc and LaTeX before the Jekyll build:

```yaml
- name: Install Pandoc and LaTeX
  run: |
    sudo apt-get update
    sudo apt-get install -y pandoc texlive-latex-base texlive-fonts-recommended texlive-latex-extra
```

The plugin handles the rest automatically during your Jekyll build process.

## Conclusion

Building this plugin was a three-part challenge: creating robust infrastructure ([Part 1](/ruby-gem-release-automation/)), implementing the core functionality (this article), and integrating it into a real project ([Part 3](/jekyll-pandoc-exports-resume-integration/)). The Jekyll plugin architecture proved flexible and powerful, while Pandoc's conversion capabilities enabled professional document generation.

Key technical achievements:

- **Zero-configuration** document exports with sensible defaults
- **Jekyll 3.x and 4.x** compatibility for broad ecosystem support
- **Extensible hooks system** for custom processing workflows
- **Performance optimization** with incremental builds and statistics
- **Professional error handling** with dependency validation
- **CI/CD ready** with GitHub Actions workflow integration

The automated export functionality has streamlined my content workflow, and the release automation (from Part 1) enables sustainable open-source development.

The plugin demonstrates how proper infrastructure investment enables rapid feature development and professional software delivery. In [Part 3](/jekyll-pandoc-exports-resume-integration/), I cover the real-world integration into my resume site — where eating my own dog food uncovered Jekyll 3.x compatibility bugs, nil safety issues, and the surprising challenges of converting themed HTML into clean PDF and Word documents.

---

**Series Resources:**

- [Part 1: Release Automation](/ruby-gem-release-automation/)
- [Part 3: Resume Integration](/jekyll-pandoc-exports-resume-integration/)
- [GitHub Repository](https://github.com/mcgarrah/jekyll-pandoc-exports)
- [Documentation Site](https://jekyll-pandoc-exports.readthedocs.io)
- [RubyGems Package](https://rubygems.org/gems/jekyll-pandoc-exports)
- [Example Implementation](https://github.com/mcgarrah/resume)

## Related Posts

- [Ruby Gem Release Automation](/ruby-gem-release-automation/) — Part 1: The CI/CD pipeline for this plugin
- [Pandoc Exports Resume Integration](/jekyll-pandoc-exports-resume-integration/) — Part 3: Real-world integration and bug fixes
- [Jekyll Mermaid Diagram Rendering Challenges](/jekyll-mermaid-diagram-rendering-challenges/) — Another Jekyll plugin integration challenge
- [How the Sausage Is Made](/jekyll-markdown-feature-reference/) — Complete feature reference including Pandoc exports