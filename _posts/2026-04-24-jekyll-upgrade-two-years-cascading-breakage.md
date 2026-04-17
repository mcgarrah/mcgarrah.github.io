---
title: "Upgrading Jekyll: Two Years of Cascading Breakage"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, ruby, sass, dart-sass, github-actions, github-pages, upgrade, webrick, node-js]
excerpt: "Every Jekyll upgrade broke something downstream. Ruby 3.0 dropped webrick. Jekyll 4.3 broke SASS imports. Dart Sass 3.0 deprecated color functions. Node.js 24 forced all GitHub Actions to update. Here's the full upgrade timeline and what each one taught me."
description: "A chronicle of upgrading Jekyll from 4.2 to 4.4.1 over two years: webrick dependency, SASS index naming conflicts, Dart Sass 2.0 division syntax, module system migration, circular dependency restructuring, and Node.js 24 GitHub Actions updates. Each upgrade's breakage and fix documented from git history."
date: 2026-04-24
last_modified_at: 2026-04-24
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-24
  date_modified: 2026-04-24
---

I've upgraded Jekyll three times in two years. Each time, the version bump was one line in the Gemfile. Each time, the cascading breakage took hours to fix. The Jekyll upgrade was never the hard part — it was everything that broke downstream.

Here's the full timeline.

<!-- excerpt-end -->

## The Starting Point: Contrast Theme

This blog is built on the [Contrast theme](https://github.com/niklasbuschmann/contrast) by Niklas Buschmann. The theme was last updated March 2021 — over three years before I started customizing it. That gap meant every upgrade had to bridge years of ecosystem changes in Ruby, SASS, and GitHub Actions simultaneously.

I maintain `upstream` and `clean` branches to track divergence from the original theme:

```bash
git diff clean upstream
```

The divergence has grown significant enough that pushing changes back upstream is no longer practical.

## Timeline

### March 2024: webrick — The Missing Server

**Problem:** `bundle exec jekyll serve` stopped working after a Ruby update.

**Root cause:** Ruby 3.0 removed `webrick` from the standard library. Jekyll's development server depends on it, but the Gemfile didn't list it as a dependency because it used to ship with Ruby.

**Fix:** One line in the Gemfile:

```ruby
gem "webrick", "~> 1.9.1"
```

**Lesson:** Ruby's stdlib removals break tools that assumed those libraries would always be there. Always pin your server dependencies explicitly.

### June 2024: Ubuntu 24.04 LTS — Local Development

**Problem:** The local development startup script needed updates for Ubuntu 24.04 LTS.

**Fix:** Updated `start-jekyll.sh` with the correct package installation and gem path setup:

```bash
# Setting up on Ubuntu 24.04 LTS
sudo apt -y install make build-essential ruby ruby-dev

# In ~/.bashrc or ~/.zshrc
export GEM_HOME=$HOME/.gems
export PATH=$HOME/.gems/bin:$PATH
```

The script also documents every useful `jekyll serve` flag — `--drafts`, `--future`, `--unpublished`, `--livereload`, `--incremental` — which I use daily during development.

### August 2024: Jekyll 4.2 → 4.3.3 — SASS Breaks

**Problem:** Jekyll 4.3 shipped with an updated `jekyll-sass-converter` that changed how SASS files are resolved.

**Three things broke at once:**

**1. Duplicate `index.sass` naming conflict**

The Contrast theme had `_sass/index.sass` as the main SASS entry point. The new SASS converter also looked for `index.sass` as a directory index file, creating an ambiguity. Fix: rename `_sass/index.sass` to `_sass/main.sass` and update all imports.

**2. Dart Sass 2.0 division syntax**

Dart Sass 2.0 deprecated the `/` operator for division (because `/` is valid CSS for shorthand properties like `font: 12px/1.5`). Every SASS file using division needed updating:

```sass
// Before (deprecated)
width: $container-width / 2

// After
@use "sass:math"
width: math.div($container-width, 2)
```

**3. Gemfile version bump**

```ruby
# Before
gem "jekyll", "~> 4.2.0"

# After
gem "jekyll", "~> 4.3.3"
```

This was the commit that taught me: a one-line Gemfile change can cascade into five file changes across the SASS architecture.

### May 2025: Dart Sass 3.0 — The Module System

**Problem:** Dart Sass 3.0 deprecated `@import` in favor of `@use` and `@forward`. The deprecation warnings were becoming errors.

**Two commits, two days:**

**Day 1: Color function migration**

Every global color function was deprecated in favor of namespaced versions:

```sass
// Before (deprecated)
color: lighten($base-color, 20%)
color: darken($base-color, 10%)
background: mix($color-a, $color-b, 50%)

// After
@use "sass:color"
color: color.adjust($base-color, $lightness: 20%)
color: color.adjust($base-color, $lightness: -10%)
background: color.mix($color-a, $color-b, 50%)
```

Six files changed. Every color manipulation in the theme needed updating.

**Day 2: Module system migration**

Replaced `@import` chains with `@use`/`@forward`:

```sass
// Before: _sass/main.sass
@import "basic"
@import "layout"
@import "classes"

// After: _sass/index.sass (forwarding file)
@forward "variables"
@forward "basic"
@forward "layout"
@forward "classes"
```

Created a central `_sass/index.sass` forwarding file and a `_sass/variables.sass` for shared values. Nine files changed.

### May 2025: Google Jules PR — More SASS Pain

The Google Jules experiment PR (#13) added four new SASS files (copy-button, comments, tags-categories, reading-time). The AI-generated code used SCSS syntax (curly braces and semicolons) in `.sass` files (which expect indented syntax). Three rounds of fixes were needed:

1. Convert SCSS syntax to indented SASS
2. Update `@import` to `@use` in the new files
3. Fix `@use` rule ordering (must come before variable declarations)

**Lesson:** AI code generators don't always respect the existing project's SASS dialect. Always check whether the project uses `.sass` (indented) or `.scss` (braces).

### September 2025: Jekyll 4.3.3 → 4.4.1 + The Circular Dependency

**The upgrade itself** was clean — just a Gemfile version bump:

```ruby
gem "jekyll", "~> 4.4.1"
```

**The same day**, I added a print stylesheet (`_sass/print.sass`) and a Google Custom Search stylesheet (`_sass/google-search.sass`). Both needed to import the theme's color variables. This created a circular dependency:

```
main.sass → imports print.sass → imports main.sass → ∞
```

**The fix** required restructuring the entire SASS architecture:

- Extract variables and functions to a new `_sass/variables.sass`
- Update all SASS files to import from `variables` instead of `main`
- Reorganize `_sass/index.sass` to properly forward modules
- Nine files changed, 92 insertions, 171 deletions

This is documented in detail in [SASS Circular Dependency Nightmare](/sass-circular-dependency-nightmare/).

### April 2026: Node.js 24 — GitHub Actions Forced Update

**Problem:** GitHub announced that Node.js 20 actions would be forced to Node.js 24 starting June 2, 2026. All three workflows needed updates.

**Changes across all workflows:**

| Action | Before | After |
|--------|--------|-------|
| actions/checkout | v5 | v6 |
| ruby/setup-ruby | v1.198.0 | v1.300.0 |
| actions/configure-pages | v5 | v6 |
| actions/deploy-pages | v4 | v5 |
| actions/upload-artifact | v4 | v7 |
| treosh/lighthouse-ci-action | v10 | v12 |
| lycheeverse/lychee-action | v2.0.2 | v2.4.0 |
| github/codeql-action | v3 | v4 |

Three workflow files, 16 insertions, 16 deletions. This one was mechanical but the blast radius was wide — every workflow in the repository needed changes simultaneously.

## The Current Stack

```ruby
# Gemfile (as of April 2026)
source "https://rubygems.org"

gem "jekyll", "~> 4.4.1"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17.0"
  gem "jekyll-sitemap", "~> 1.4.0"
  gem "jekyll-paginate", "~> 1.1.0"
  gem "jekyll-seo-tag", "~> 2.8.0"
  gem "jekyll-redirect-from", "~> 0.16.0"
end

gem "webrick", "~> 1.9.1"
```

## Lessons Learned

**One-line changes cascade.** A Gemfile version bump is never just a version bump. It's a version bump plus every downstream incompatibility that the new version exposes.

**SASS is the most fragile layer.** Of the six upgrade events, four involved SASS breakage. The Dart Sass team's deprecation-to-removal pipeline is aggressive, and Jekyll themes written in 2019-2021 are full of deprecated patterns.

**Pin everything.** The Gemfile uses `~>` (pessimistic version constraints) for every gem. This prevents surprise major version jumps while allowing patch updates. The GitHub Actions workflows pin specific versions with comments linking to release pages.

**Keep a startup script.** The `start-jekyll.sh` script documents the full local development setup — Ruby gem paths, package dependencies, and every useful `jekyll serve` flag. When Ubuntu 24.04 changed things, the script was the single place to update.

**AI-generated code needs dialect checking.** The Google Jules PR generated valid SCSS that was invalid SASS. The syntax is similar enough that it looks right at first glance but fails at build time.

**Upstream divergence is permanent.** The Contrast theme hasn't been updated since 2021. My fork has diverged through three Jekyll versions, a complete SASS module system migration, and dozens of new features. Contributing back upstream is no longer practical — the codebases have evolved in different directions.

## Related Posts

- [SASS Circular Dependency Nightmare](/sass-circular-dependency-nightmare/) — The September 2025 restructuring in detail
- [The CI/CD Pipeline Behind This Jekyll Blog](/jekyll-github-actions-cicd-pipeline/) — The GitHub Actions workflows that needed Node.js 24 updates
- [Building This Blog: Jekyll on GitHub Pages](/setting-up-jekyll-blog-github-pages/) — Overall setup guide
- [How the Sausage Is Made](/jekyll-markdown-feature-reference/) — Full feature inventory including SASS architecture
