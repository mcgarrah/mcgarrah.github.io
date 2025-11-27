---
layout: post
title: "Building a Jekyll Plugin for Automated Document Exports - Part 2: Technical Implementation"
categories: [jekyll, ruby, pandoc, automation]
tags: [jekyll-plugin, pandoc, pdf-generation, docx, ruby-gem, documentation]
excerpt: "Technical deep-dive into Jekyll plugin development: hooks system, Pandoc integration, and document generation features. Part 2 of building a professional Ruby gem."
---

<!-- excerpt-end -->

In [Part 1](/ruby-gem-release-automation/), I covered the infrastructure challenges of building a professional Ruby gem with automated releases, documentation, and CI/CD. Now let's dive into the technical implementation of the Jekyll plugin itself.

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
  collections: ['pages', 'posts']
  incremental: true
  pdf_options:
    variable: 'geometry:margin=0.75in'
  unicode_cleanup: true
  inject_downloads: true
```

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

The plugin is actively used in my resume site, automatically generating:

- PDF versions for easy downloading and printing
- DOCX versions for recruiters who prefer Word format
- Multiple layout variants (short/long versions)

## Future Enhancements

### Additional Document Formats

Pandoc supports numerous output formats that would expand the plugin's utility:

**ODT (OpenDocument Text)**: LibreOffice/OpenOffice compatibility for users preferring open-source office suites:

```yaml
---
title: My Document
odt: true  # Generate .odt file
---
```

**RTF (Rich Text Format)**: Universal format readable by virtually any word processor, ideal for maximum compatibility:

```yaml
rtf: true  # Generate .rtf file
```

### Site-Wide EPUB Generation

A compelling enhancement would be generating complete EPUB books from entire Jekyll sites. This would be particularly valuable for:

- **Blog Archives**: Convert your entire blog into a readable e-book format
- **Documentation Sites**: Package complete documentation as downloadable EPUB
- **Article Collections**: Combine related posts into themed e-books

Implementation would involve:

```yaml
pandoc_exports:
  epub_collections:
    blog_archive:
      title: "McGarrah Technical Blog - Complete Archive"
      collections: ['posts']
      sort_by: 'date'
      cover_image: '/assets/images/blog-cover.png'
    documentation:
      title: "Complete Documentation"
      collections: ['docs']
      sort_by: 'weight'
```

The plugin would:

1. Aggregate all posts/pages in specified collections
2. Generate a proper EPUB table of contents
3. Handle cross-references and internal links
4. Include metadata (author, publication date, description)
5. Embed images and assets properly

### Technical Considerations

- **Memory Management**: Large site exports would require streaming processing
- **Link Resolution**: Convert internal Jekyll links to EPUB navigation
- **Asset Bundling**: Embed images, CSS, and other assets into EPUB package
- **Metadata Extraction**: Use Jekyll front matter for EPUB metadata

These enhancements would transform the plugin from individual page exports to comprehensive site archival and distribution tool.

### Mermaid Diagram Support

Technical documentation often includes Mermaid diagrams that need proper handling in exported formats:

```yaml
pandoc_exports:
  mermaid:
    enabled: true
    render_method: 'svg'  # or 'png' for better compatibility
    theme: 'default'
```

Challenges to address:

- **SVG Rendering**: Convert Mermaid JavaScript to static SVG/PNG images
- **PDF Compatibility**: Ensure diagrams render properly in LaTeX/PDF output
- **Fallback Handling**: Graceful degradation when Mermaid CLI unavailable

### Other Planned Improvements

- Enhanced template system with Liquid support
- Integration with Jekyll's asset pipeline
- Batch processing optimizations
- Custom CSS injection per format
- Automated table of contents generation

## Getting Started

Install the plugin:

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

The plugin handles the rest automatically during your Jekyll build process.

## Conclusion

Building this plugin was a two-part challenge: creating robust infrastructure (Part 1) and implementing the core functionality (Part 2). The Jekyll plugin architecture proved flexible and powerful, while Pandoc's conversion capabilities enabled professional document generation.

Key technical achievements:

- **Zero-configuration** document exports with sensible defaults
- **Extensible hooks system** for custom processing workflows
- **Performance optimization** with incremental builds and statistics
- **Professional error handling** with dependency validation

The automated export functionality has streamlined my content workflow, and the release automation (from Part 1) enables sustainable open-source development.

The plugin demonstrates how proper infrastructure investment enables rapid feature development and professional software delivery.

---

**Series Resources:**

- [Part 1: Release Automation](/ruby-gem-release-automation/)
- [GitHub Repository](https://github.com/mcgarrah/jekyll-pandoc-exports)
- [Documentation Site](https://jekyll-pandoc-exports.readthedocs.io)
- [RubyGems Package](https://rubygems.org/gems/jekyll-pandoc-exports)
- [Example Implementation](https://github.com/mcgarrah/resume)