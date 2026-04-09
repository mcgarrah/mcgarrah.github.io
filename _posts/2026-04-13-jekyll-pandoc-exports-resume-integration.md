---
layout: post
title: "Integrating Jekyll-Pandoc-Exports Into a Real Project - Part 3: Bugs, Fixes, and HTML Cleanup"
categories: [jekyll, ruby, pandoc, automation]
tags: [jekyll-plugin, pandoc, pdf-generation, docx, ruby-gem, resume, github-pages, debugging]
excerpt: "What happens when you integrate your own Jekyll plugin into a real project: three patch releases, a Ruby language gotcha, and the surprising difficulty of converting themed HTML into clean documents."
description: "Real-world integration of the jekyll-pandoc-exports plugin into a resume site, covering Jekyll 3.x compatibility bugs, nil safety issues, Pandoc's CSS limitations, regex-based HTML cleanup for document exports, and the value of eating your own dog food."
date: 2026-04-13
last_modified_at: 2026-04-13
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-13
  date_modified: 2026-04-13
---

What happens when you integrate your own plugin into a real project? Three patch releases in one session, a Ruby language subtlety that only manifests in Jekyll 3.x, and the discovery that Pandoc completely ignores your CSS.

<!-- excerpt-end -->

In [Part 1](/ruby-gem-release-automation/) I covered building the release automation pipeline, and in [Part 2](/jekyll-pandoc-exports-plugin/) I covered the plugin's technical architecture. This is the part where theory meets reality.

My [resume site](https://github.com/mcgarrah/resume) was the original motivation for building [jekyll-pandoc-exports](https://github.com/mcgarrah/jekyll-pandoc-exports) — I wanted PDF and DOCX versions of my resume generated automatically on every build instead of manually exporting and committing static files. The integration seemed straightforward. It wasn't.

## The Integration

The basic setup required changes to six files in the resume repository:

1. **Gemfile** — added `jekyll-pandoc-exports` to the plugins group
2. **_config.yml** — plugin configuration with a `downloads` output directory, pages-only collection processing, and disabled auto-injected download links (the resume theme already has sidebar links)
3. **print.html** — added `pdf: true` and `docx: true` to the front matter
4. **_data/data.yml** — updated the sidebar PDF link from a static file path to the generated `/resume/downloads/print.pdf`, and added a new DOCX link
5. **_includes/contact.html** — added a Word Resume download link to the sidebar
6. **GitHub Actions workflow** — added a step to install Pandoc and LaTeX in CI

The configuration:

```yaml
pandoc_exports:
  enabled: true
  output_dir: 'downloads'
  collections: ['pages']
  incremental: true
  unicode_cleanup: true
  inject_downloads: false
  pdf_options:
    variable: 'geometry:margin=0.75in'
```

Simple enough. Then I ran `bundle exec jekyll build`.

## Bug 1: LocalJumpError in Jekyll 3.x (v0.1.12)

```
jekyll 3.10.0 | Error:  unexpected return
generator.rb:14:in `block in <module:PandocExports>': unexpected return (LocalJumpError)
```

The resume site uses the `github-pages` gem, which pins Jekyll to 3.10.0. My plugin was developed and tested against Jekyll 4.x. The problem was in the hook registration:

```ruby
Jekyll::Hooks.register :site, :post_write do |site|
  config = setup_configuration(site)
  return unless config['enabled']  # 💥 LocalJumpError in Jekyll 3.x
end
```

In Ruby, `return` inside a `do...end` block tries to return from the enclosing method. In Jekyll 4.x, hooks are invoked in a context where this works. In Jekyll 3.x, there's no enclosing method — the block is called directly via `each`, so `return` has nowhere to go.

The fix: replace `return` with `next`, which is the correct way to exit early from a block:

```ruby
Jekyll::Hooks.register :site, :post_write do |site|
  config = setup_configuration(site)
  next unless config['enabled']  # ✅ Works in both Jekyll 3.x and 4.x
end
```

This is the kind of bug that's invisible in development and testing but surfaces immediately in production. The plugin's test suite ran against Jekyll 4.x, and all 87 tests passed. The `github-pages` gem is the only common path to Jekyll 3.x, and I hadn't tested against it.

**Lesson:** If your gem declares `jekyll >= 3.0` as a dependency, test against Jekyll 3.x.

## Bug 2: Nil Safety in Template Configuration (v0.1.13)

With the `return`/`next` fix deployed, the build got further — but crashed again:

```text
undefined method `empty?' for nil:NilClass
generator.rb:187:in `apply_template'
```

The plugin's default configuration defines the `template` hash with all three keys:

```ruby
'template' => { 'header' => '', 'footer' => '', 'css' => '' }
```

But Ruby's `Hash#merge` does a shallow merge. When the user provides only `template.css` in their `_config.yml`, the entire `template` hash is replaced — `header` and `footer` become nil instead of empty strings. Then `.empty?` on nil raises `NoMethodError`.

The fix: coerce nil to empty string with `.to_s` before checking:

```ruby
def self.apply_template(html_content, config)
  template = config['template'] || {}
  header = template['header'].to_s
  footer = template['footer'].to_s
  css = template['css'].to_s
  return html_content if header.empty? && footer.empty? && css.empty?
  # ...
end
```

**Lesson:** If your defaults use nested hashes, shallow merge will bite you. Either deep-merge or nil-guard every access.

## Bug 3: title_cleanup Only Applied to PDF (v0.1.14)

The `title_cleanup` configuration accepts regex patterns that strip HTML elements before Pandoc converts them. But the cleanup code was inside `generate_pdf` only — DOCX exports got the raw, unprocessed HTML.

Additionally, the regex used `Regexp.new(pattern)` without the `MULTILINE` flag. The resume theme's `<li>` elements span three lines:

```html
<li class="website"><i class="fas fa-globe-americas"></i>
  <a href="http://www.mcgarrah.org" target="_blank">www.mcgarrah.org</a>
</li>
```

A pattern like `<li class="website"[^>]*>.*?</li>` won't match because `.` doesn't cross newlines by default.

The fix: move cleanup to `process_html_content` (applies to both formats) and enable `Regexp::MULTILINE`:

```ruby
(config['title_cleanup'] || []).each do |pattern|
  processed.gsub!(Regexp.new(pattern, Regexp::MULTILINE), '')
end
```

**Lesson:** If a processing step should apply to all output formats, put it in the shared pipeline, not in a format-specific method.

## The Release Automation Payoff

These three bugs resulted in three patch releases (v0.1.12, v0.1.13, v0.1.14) in a single session. Each followed the same cycle: fix the code, run the 87-test suite, commit to dev, create PR, merge, tag, create GitHub release, wait for the RubyGems publish workflow, update the consumer project.

The release automation from [Part 1](/ruby-gem-release-automation/) made this sustainable. Without it, three releases in one session would have been a nightmare of manual steps. With it, each release was a few commands.

The one gotcha: the v0.1.12 publish workflow failed because I forgot to run `bundle install` after bumping the version, so the `Gemfile.lock` still referenced 0.1.11. The CI workflow's `bundler-cache: true` sets frozen mode, which refuses to install when the lockfile doesn't match the gemspec. I had to delete the tag, update the lockfile, re-tag, and manually trigger the publish workflow. This is now documented in Part 1's "Frozen Lockfiles" section.

## The HTML Cleanup Challenge

With the plugin running, the generated PDF and DOCX files contained everything from the resume's HTML — including the full sidebar with a headshot photo, social media links, download links, and a languages section. The initial output was 1.2 MB for the PDF and 659 KB for the DOCX, mostly due to the embedded headshot image.

### Why CSS Doesn't Work

My first instinct was to use the plugin's `template.css` injection to hide unwanted elements:

```yaml
template:
  css: >
    .avatar { display: none !important; }
    .languages-container { display: none !important; }
```

This doesn't work. Pandoc parses HTML structure, not rendered output. It doesn't execute CSS — `display: none` elements are still in the DOM, so Pandoc still converts them. The image data still gets embedded in the PDF, and the sidebar text still appears in the DOCX.

### Regex Stripping with title_cleanup

The solution is to remove unwanted elements from the HTML before Pandoc sees them, using the `title_cleanup` regex patterns:

```yaml
title_cleanup:
  - '<img class="avatar"[^>]*/?>                          '
  - '<li class="phone"><i class="fas fa-passport">.*?</li>'
  - '<li class="timezone"[^>]*>.*?</li>'
  - '<li class="website"[^>]*>.*?</li>'
  - '<li class="linkedin"[^>]*>.*?</li>'
  - '<li class="github"[^>]*>.*?</li>'
  - '<li class="gitlab"[^>]*>.*?</li>'
  - '<li class="discord"[^>]*>.*?</li>'
  - '<li class="stack-overflow"[^>]*>.*?</li>'
  - '<li class="pdf"[^>]*>.*?</li>'
  - '<li class="docx"[^>]*>.*?</li>'
  - '<li class="print"[^>]*>.*?</li>'
  - '<div class="languages-container[^"]*"[^>]*>.*?</div>'
  - '<span class="fa-stack[^"]*">.*?</span>'
```

### The Shared CSS Class Trap

One pattern deserves special attention. The resume theme reuses `class="phone"` for both the actual phone number and the citizenship field:

```html
<li class="phone"><i class="fas fa-phone"></i>
  <a href="tel:919 807-1057">919 807-1057</a>
</li>

<li class="phone"><i class="fas fa-passport"></i>
  <a href="">US</a>
</li>
```

A naive pattern like `<li class="phone"[^>]*>.*?</li>` would strip both. The fix was to target the citizenship entry by its icon class instead:

```yaml
- '<li class="phone"><i class="fas fa-passport">.*?</li>'
```

This matches only the passport-icon variant, preserving the actual phone number.

### Font Awesome Icon Cleanup

The section headings in the resume theme include Font Awesome icon stacks:

```html
<h2 class="section-title">
  <span class="fa-stack fa-xs">
    <i class="fas fa-circle fa-stack-2x"></i>
    <i class="fas fa-user fa-stack-1x fa-inverse"></i>
  </span>
  Career Profile
</h2>
```

Pandoc converts these icon spans into LaTeX as `{ \emph{} \emph{} }`, which renders as whitespace before the heading text — creating the appearance of indentation. Stripping the spans produces clean headings:

```yaml
- '<span class="fa-stack[^"]*">.*?</span>'
```

### Layout Flattening with Template CSS

While CSS `display: none` doesn't work for hiding elements, Pandoc does respect some CSS for layout purposes when converting to DOCX. The resume theme uses CSS Grid with `padding: 60px` on the main content wrapper. Adding template CSS to flatten the layout helps produce cleaner output:

```yaml
template:
  css: >
    .wrapper { display: block; padding: 0; margin: 0; }
    .sidebar-wrapper { display: block; padding: 0; }
    .main-wrapper { display: block; padding: 0; }
    .section { margin-bottom: 10px; }
    .section-title { font-size: 24px; font-weight: bold;
      text-transform: uppercase; border-bottom: 2px solid #333;
      padding-bottom: 4px; margin-bottom: 10px; }
```

## Results

After all the cleanup, the output files dropped significantly:

| Metric | Before Cleanup | After Cleanup |
|--------|---------------|---------------|
| PDF size | 1.2 MB | 273 KB |
| DOCX size | 659 KB | 79 KB |
| Build time | ~4 seconds | ~3.5 seconds |

The generated documents now contain:

- Name and tagline
- Email and phone number (only)
- Clean section headings without icon artifacts
- All resume content without sidebar noise

Both files are served from `/resume/downloads/` and linked directly from the resume sidebar, staying current with every deploy.

## What I'd Do Differently

**Test against Jekyll 3.x from the start.** The `github-pages` gem is one of the most common Jekyll deployment paths, and it pins to Jekyll 3.x. If your gemspec says `jekyll >= 3.0`, your CI matrix should include Jekyll 3.x.

**Deep-merge nested configuration hashes.** Ruby's `Hash#merge` is shallow. Any nested hash in your defaults will be completely replaced if the user provides a partial override. Either deep-merge or nil-guard every nested access.

**Apply processing steps in the shared pipeline.** If cleanup, transformation, or validation should apply to all output formats, don't put it in a format-specific method. It's easy to add a feature to PDF generation and forget that DOCX needs it too.

**Don't assume CSS works with Pandoc.** Pandoc's HTML parser reads structure, not rendered output. CSS `display: none` is invisible to it. If you need to remove content from Pandoc's input, strip it from the HTML before conversion.

**Eat your own dog food early.** Every bug in this article was invisible during development and testing. They only surfaced when I integrated the plugin into a real project with a different Jekyll version, a different theme structure, and real content. The sooner you use your own tool in production, the sooner you find the real bugs.

---

**Series Resources:**

- [Part 1: Release Automation](/ruby-gem-release-automation/)
- [Part 2: Plugin Architecture](/jekyll-pandoc-exports-plugin/)
- [GitHub Repository](https://github.com/mcgarrah/jekyll-pandoc-exports)
- [Documentation Site](https://jekyll-pandoc-exports.readthedocs.io)
- [RubyGems Package](https://rubygems.org/gems/jekyll-pandoc-exports)
- [Resume Site Integration](https://github.com/mcgarrah/resume)
