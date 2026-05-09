---
layout: post
title: "Rebuilding My Resume Site From the Ground Up"
image: /assets/images/og/resume-site-ground-up-rebuild.png
categories: [web-development, technical, jekyll]
tags: [jekyll, resume, css, pandoc, pdf, xelatex, structured-data, json-ld, github-pages, seo]
excerpt: "I gutted a 2017 Bootstrap template and rebuilt my resume site with modern CSS, four purpose-built views, a Jinja2/XeLaTeX PDF pipeline, company logos, and machine-readable structured data. Here is what I kept, what I dropped, and why."
description: "A walkthrough of rebuilding a Jekyll resume site from a legacy Bootstrap 3 template to a modern single-column layout with light/dark mode, semantic HTML, JSON-LD structured data, company logos in PDF exports, and a dual Ruby/Python pipeline producing professional PDFs via XeLaTeX."
date: 2026-05-14
last_modified_at: 2026-05-14
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-14
  date_modified: 2026-05-14
---

My [resume site](https://mcgarrah.org/resume/) started life in 2017 as a fork of the [orbit-theme](https://github.com/sharu725/developer-theme) — a Bootstrap 3 sidebar layout with jQuery skill bar animations, Font Awesome via CDN, and IE8 conditional comments. It served its purpose for years, but the technical debt had compounded to the point where every change required understanding decisions made for a different era.

The trigger was a content rewrite. I sat down to update five years of work at Envestnet — a role that had evolved from platform engineer to cross-enterprise operator to compliance leader to AI/ML initiator — and realized the template was fighting me at every turn. Condensing that arc into clear, quantified impact statements was hard enough without also wrestling with a sidebar layout that wasted half the viewport and a Pandoc pipeline that needed 16 regex patterns to produce a clean PDF. The content challenge made the architectural debt impossible to ignore. To be fair, I built some of this complexity myself in the rush to get resume content out quickly — so the debt was partly my own making.

Over the past two weeks I executed a ground-up rebuild — 80 commits across 9 days. New architecture, new content voice, new export pipeline, and a few improvements to the blog along the way.

<!-- excerpt-end -->

## What Was Wrong

The short version: the site loaded Bootstrap 3.4.1, jQuery, and the full Font Awesome library to render what is fundamentally a text document. The only JavaScript usage was animating skill progress bars — a feature I was removing anyway. IE8 shims were still in the `<head>`. A Liquid-based HTML minifier (`compress.html`) added complexity for negligible benefit. Nine SCSS color skins existed for a site that used exactly one.

The deeper problem was structural. The sidebar layout wasted horizontal space on a content-dense resume, and it made Pandoc exports painful. My [jekyll-pandoc-exports](/jekyll-pandoc-exports-plugin/) plugin needed 16 regex patterns to strip sidebar markup, icon stacks, and CDN references before Pandoc could produce a clean PDF. That is not a sustainable architecture.

## The Sunk Cost Problem

I had invested significantly in the old template. Over 107 commits across nine years, I had:

- Upgraded jQuery from 1.11.3 to 3.7.1 (addressing security vulnerabilities)
- Upgraded Bootstrap from 3.3.6 to 3.4.1 (the last 3.x release)
- Upgraded Font Awesome from the original 4.x local copy to 5.1.1, then to 6.6.0, then to 6.7.2 via CDN
- Converted all static dependencies from local copies to CDN with SRI integrity hashes (saving ~2MB of repo bloat)
- Added Dependabot monitoring, then immediately had to pin Bootstrap to `~3.4.x` and Font Awesome to `^6.x` to prevent Dependabot from proposing breaking major version upgrades
- Added a print view, certifications section, publications section, OSS contributions
- Created dark mode SCSS skins (that I never shipped)
- Built the `details`/`summary` collapsible pattern for the brief view
- Added GitHub Actions deployment, replacing the old `github-pages` gem approach

Each of those upgrades was defensible in isolation. jQuery 1.11.3 had known CVEs — upgrading to 3.7.1 was the responsible thing to do. Font Awesome 4.x was end-of-life — moving to 6.x was correct. Converting to CDN with SRI hashes was a security best practice.

But stepping back, the pattern was clear: I was spending effort maintaining dependencies the site did not actually need. Bootstrap provided a CSS reset and some utility classes — my layout was already CSS Grid. jQuery animated skill bars — a feature I wanted to remove. Font Awesome provided icons — I used fifteen of them. Every upgrade was polishing a dependency that should have been deleted.

This is the same pattern I see in enterprise architecture. Teams invest years upgrading Oracle 11g to 12c to 19c, carefully managing breaking changes and compatibility matrices, when the real question is whether they should be on PostgreSQL. The sunk cost of previous upgrades makes the "just upgrade again" path feel safer than the "start fresh" path — even when starting fresh is objectively less total effort and produces a better result.

The moment I realized I was writing commit messages like "Pin Bootstrap to 3.4.x to prevent major version upgrades" — actively fighting my own dependency management tooling to keep a library I barely used — was the moment the refactor became inevitable. The decision framework is simple: if you are spending more effort managing a dependency than the value it provides, the correct action is removal, not another upgrade cycle.

## The Rebuild: Four Views, One Data Source

Everything renders from `_data/data.yml`. No content duplication across views.

| View | URL | Purpose |
|------|-----|---------|
| **Brief** | [`/resume/`](https://mcgarrah.org/resume/) | Scannable, collapsible sections for recruiters |
| **Print** | [`/resume/print/`](https://mcgarrah.org/resume/print/) | Fully expanded, comprehensive — the canonical reference |
| **Ultra-Brief** | [`/resume/ultra-brief/`](https://mcgarrah.org/resume/ultra-brief/) | Two-page elevator pitch for job boards and quick reads |
| **Machine** | [`/resume/machine/`](https://mcgarrah.org/resume/machine/) | JSON-LD + semantic HTML for AI agents and ATS systems |

The brief view uses native `<details>`/`<summary>` elements for progressive disclosure — no JavaScript required. The print view is linear HTML that Pandoc converts cleanly and serves as the comprehensive version that the shorter views link back to. The ultra-brief is a self-contained two-page resume — the kind you hand someone in an elevator — with every job title linking to its full entry in the print view via stable anchors. The machine view provides Schema.org structured data that makes the resume trivially parseable by recruiting tools.

## What Got Dropped

- Bootstrap 3.4.1 (replaced by ~200 lines of hand-rolled CSS with CSS Grid)
- jQuery (zero JavaScript for presentation)
- Font Awesome CDN (replaced by an inline SVG sprite with ~12 icons)
- IE8/IE9 conditional comments and shims
- `compress.html` Liquid minifier
- Nine unused SCSS color skins
- `github-pages` gem (80+ transitive dependencies, conflicts with Jekyll 4.x)
- Sidebar layout entirely
- Skill bar animations
- Legacy static PDF snapshots in `assets/pdf/`
- Obsolete template files from the original orbit-theme

## What Got Built

### Content Overhaul First

Before touching the architecture, I rewrote the content. Five years at Envestnet meant five years of scope expansion — from a single platform to 20+ AWS accounts, from isolated evidence requests to leading eight simultaneous SOC audits, from supporting a data science team to delivering the first AI/ML production workload on the billing platform. Capturing that progression in concise, impact-focused language was the hardest part of the entire project. Every position got a fresh voice — clearer impact statements, better quantification, leadership framing where appropriate. I added consulting roles that had been missing (some dating back to the early 2000s), added recently published Python packages to the projects section, and restructured experience entries from flat markdown blobs into a structured `subsections` array with explicit titles. That last change solved a Pandoc rendering problem where job titles and subsection headings rendered at identical visual weight in PDF output.

### Modern CSS with Light/Dark Mode

The entire stylesheet is CSS custom properties with a `prefers-color-scheme` media query. The site respects the user's OS setting automatically — no JavaScript toggle, no cookie, no flash of wrong theme.

```css
:root {
  --bg: #ffffff;
  --text: #3F4650;
  --accent: #4B6A78;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a2e;
    --text: #e0e0e0;
    --accent: #7fb3c8;
  }
}
```

### Jinja2/XeLaTeX PDF Pipeline

The Pandoc-based export still works for quick DOCX generation, but for PDF I built a separate Python pipeline. A Jinja2 template reads the same `_data/data.yml` and produces LaTeX source that XeLaTeX compiles with full typographic control — proper font selection, precise spacing, and a visual hierarchy that CSS-to-PDF converters cannot match.

I evaluated WeasyPrint first (CSS-to-PDF via Python) and rejected it after a day. The rendering was acceptable for simple documents but lacked the fine-grained typographic control required for a professional resume — page break placement, precise header spacing, proper LaTeX ligatures, and conditional content based on template variant. XeLaTeX gives full control over every aspect of the output. The trade-off is build complexity (LaTeX toolchain installation), but that cost is paid once in CI and amortized across every subsequent build.

Three template variants exist:

- **Long** — Full detail, multi-page with company logos (34 pages with everything)
- **Brief** — Curated highlights, 5 pages
- **Ultra-brief** — Aggressive two-page format for job boards that penalize length

The pipeline lives in `bin/generate-latex.py` and runs independently of Jekyll. Same YAML data, different rendering engine, purpose-built output.

### Company and University Logos

Both the HTML views and the LaTeX PDFs now include company and university logos alongside experience and education entries. I wanted the visual appeal that LinkedIn profiles have — a recognizable logo next to each role grounds the reader and adds credibility at a glance.

The implementation was more work than expected. The challenges fell into three categories:

**Finding logos for defunct companies.** Q+E Software was acquired by Intersolv in 1994, which became Merant, then Serena, then Micro Focus. No digital logo assets survive online — the only path would be scanning physical materials from the 1990s. Hosted Solutions (a Raleigh ISP from 2004) required the Wayback Machine. NC LIVE's original purple logo from 2000 was similarly archived. For companies truly lost to history, I created custom SVG icons — a generic tooth for a dental practice, a database cylinder for a database consulting firm.

**SVG clipping and viewBox manipulation.** Many SVGs include both an icon mark and a wordmark. At 48px display size, the wordmark is unreadable — you want just the icon. The technique is adjusting the `viewBox` to "zoom in" on the icon portion: find the coordinate boundaries of the mark by examining path data, then set a cropped viewBox that frames just that area. This worked for USPS (eagle only), Measurement Incorporated (M+I+caliper only), and the AKC shield.

Except when it did not work. The AKC SVG uses a transform matrix (`matrix(9.37,0,0,9.37,-2975,-5501)`) with `overflow:visible` — the content renders at absolute positions regardless of viewBox. The fallback was rendering the full SVG to a high-resolution PNG with `cairosvg`, then cropping the raster image with Pillow. Sometimes the pragmatic solution wins.

**Converting for LaTeX.** XeLaTeX cannot embed SVG files directly. A Python script (`bin/convert_logos_to_png.py`) converts all SVGs to 400px-wide PNGs with transparent backgrounds using `cairosvg`, then the LaTeX template includes them with `\includegraphics`. Getting `\IfFileExists` paths correct so missing logos degrade gracefully (rather than crashing the build) took more iterations than I would like to admit.

The result is a `preview.html` page that shows all logos at resume scale in both light and dark mode — essential for catching dark-fill logos that disappear on dark backgrounds. The full inventory, sources, and lessons learned live in the [logo README](https://github.com/mcgarrah/resume/blob/main/assets/images/company-logos/README.md).

### Ultra-Brief View

Beyond the three original planned views, I added an ultra-brief HTML page at `/resume/ultra-brief/` — a self-contained, two-page resume with inline styles. It is designed for the "paste your resume" fields on job boards where you need maximum density. The corresponding XeLaTeX template produces a matching PDF.

### Stable Anchor IDs — Linking Views Together

A problem I did not anticipate: how do the brief and ultra-brief views link back to the comprehensive view? When a recruiter reads the two-page ultra-brief PDF and wants more detail on a specific role, they need a reliable URL that takes them directly to that entry in the full `/resume/print/` view.

The solution was adding an `anchor` field to every experience and education entry in `_data/data.yml` — a stable, human-readable ID following the convention `{company-slug}-{start-year}` (e.g., `envestnet-2021`, `edu-gatech-2014`). These anchors are rendered as HTML `id` attributes in the print view, and the ultra-brief PDF links each job title to `mcgarrah.org/resume/print/#envestnet-2021`.

The critical constraint: **these anchors must never change.** They are embedded in PDFs I hand to recruiters, linked from LinkedIn posts, and referenced in external documents. A broken anchor link in a resume PDF reflects poorly in exactly the way you cannot afford when job hunting. I added a stability warning comment at the top of `data.yml` and wrote the anchor generation as a one-time script (`bin/add_anchors.py`) so the IDs are deterministic and reproducible — not generated dynamically from content that might shift.

This turned out to be one of the more important architectural decisions. The different views are not isolated documents — they are a connected system where the brief versions serve as entry points that funnel interested readers toward the comprehensive version.

### Machine-Readable Structured Data

The `/resume/machine/` view embeds two JSON-LD blocks — a `WebPage` descriptor and a full `Person` entity with 17 credentials, 27 occupations, and semantic markup on every content element. The HTML uses `<article>`, `<section>`, `<time datetime="...">`, and Schema.org microdata attributes throughout.

After deploying to production, I ran Google's Rich Results Test and fixed the Schema.org validation warnings it flagged — mostly `ScholarlyArticle` type issues in the publications section. The structured data now validates cleanly.

### SEO and Social Sharing — The Cascade to the Blog

Adding an Open Graph image (`og:image`) to the resume site was straightforward — one branded SVG rendered to PNG, referenced in the config defaults. But validating the resume's `/resume/machine/` view with Google's Rich Results Test revealed a broader gap: Google's Article rich results require an `image` property on every page. My blog had 117 published posts, none with OG images.

This became the single biggest change to the blog during this sprint. I wrote a Python script (`bin/generate-og-images.py`) that generates branded social preview cards — SVG templates with the post title rendered in, converted to PNG via `cairosvg`. A companion script (`bin/update-og-frontmatter.py`) added the `image:` front matter field to all 117 posts. One commit, 350 files.

The blog also gained `BlogPosting` structured data support in `_config.yml`, enabling Article rich results across all posts. Both changes — the OG images and the structured data — trace directly back to the resume's machine view work. Building the resume's JSON-LD made me realize the blog was missing the same SEO fundamentals that I had just implemented for the resume.

This is the kind of cross-pollination that happens when you maintain related sites on the same domain. Improving one surfaces gaps in the other.

### CI Pipeline Improvements

The GitHub Actions workflow now handles the full build pipeline:

- Jekyll build (HTML views)
- XeLaTeX compilation (long, brief, and ultra-brief PDFs)
- `html-proofer` for link integrity
- Apt package caching to cut 6+ minutes off deploy time

The apt caching was a nice win — XeLaTeX and its dependencies are large packages, and caching them between runs makes the CI feedback loop much tighter.

### Developer Experience

Small things that made the iteration faster:

- `jekyll-start.sh` with automatic port detection and a `--clean` flag
- `jekyll-clean.sh` with soft/hard clean modes
- Sass modernization (`@import` → `@use`) to eliminate deprecation warnings
- Added Substack profile link across all views

## The Dual-Language Architecture

The site now runs two rendering stacks deliberately:

- **Ruby (Jekyll)** — HTML views for the web (brief, print, machine, ultra-brief)
- **Python (Jinja2 + XeLaTeX)** — PDF generation with full typographic control

Both read from `_data/data.yml`. This is not accidental complexity — it is a deliberate architectural decision. Each tool does what it is best at. Jekyll excels at templating HTML for the web. XeLaTeX excels at typesetting documents for print. Trying to make one tool do both jobs is how you end up with 16 regex cleanup patterns — the same kind of impedance mismatch you see when teams force a single CI/CD tool to handle both container builds and infrastructure provisioning.

The shared data layer (`data.yml`) is the integration point. Content changes propagate to all outputs automatically. The rendering engines are independent and replaceable — if a better LaTeX alternative emerges, or if Jekyll is eventually replaced, the data layer remains stable.

## Blog Improvements (Along the Way)

Beyond the OG image and structured data work described above, the blog picked up one housekeeping item:

- **OG image publishing workflow** — Documented the generation and front matter update process so future posts get OG images as part of the standard publishing workflow rather than as a bulk backfill.

## What is Next

The structural rebuild is done — the foundation is solid. What remains is building on top of it:

- **In-browser search** — not Google Custom Search (which I actively dislike on the blog but needed something quick). For the resume, I want purpose-built semantic search that lets recruiters query by skill, role, or technology and get linked results across experiences. Pagefind is the pragmatic first step — static indexing at build time, swappable later for something smarter.
- **Per-entry skills taxonomy** — explicit skill-to-experience mapping for ATS keyword matching
- **AI agent integration** — conversational interface backed by the machine view's structured data

The skills taxonomy is the one I am most interested in. Right now, skills live in a flat list at the bottom of the resume — disconnected from the experiences that developed them. I want to build a semantic map: which skills were used at which jobs, for how long, and how they cluster. The stable anchor IDs already give each experience entry a permanent address. Adding per-entry skill annotations creates the edges in a graph — connecting "Kubernetes" not just to a skills list but to specific roles, specific years, specific outcomes.

That kind of structured relationship data opens up interesting possibilities — semantic search across the resume ("show me everything involving Kubernetes in production"), automatic keyword optimization for specific job descriptions, and eventually feeding richer context to an AI agent that can answer recruiter questions with grounded, specific evidence rather than generic summaries. When someone asks "how long have you worked with EKS?" the answer should not be a number — it should be a linked trail through five years of specific clusters, upgrades, and incidents.

The machine view's JSON-LD already provides the foundation. The next step is enriching it with per-entry skill annotations and seeing what becomes possible when the resume is not just a document but a queryable knowledge graph.

The broader implication: a resume should not be a static document you update twice a year. It should be a living system — structured data that multiple consumers can query, render, and reason about in ways appropriate to their needs. The rebuild gives me that foundation.

The site is live at [mcgarrah.org/resume/](https://mcgarrah.org/resume/) and the source is on [GitHub](https://github.com/mcgarrah/resume).

## Lessons Learned

**Legacy templates accumulate invisible debt.** The orbit-theme worked fine in 2017. By 2026 it was carrying 500KB of unused dependencies and architectural decisions that actively fought every change. This is true of any system that grows by accretion — the cost is not in any single dependency but in the aggregate maintenance burden and the cognitive overhead of understanding why each piece exists.

**Separate concerns by output format.** One rendering engine for web, another for print. The shared data layer (`data.yml`) is the integration point — not shared templates trying to serve both masters. This is the same principle behind separating API contracts from implementation: define the interface once, let each consumer render it appropriately.

**Evaluate quickly, decide quickly.** I tried WeasyPrint, found it lacking for my requirements, and removed it the same day. The git history shows the full arc: add WeasyPrint → evaluate → remove → build XeLaTeX pipeline. Rapid prototyping with a willingness to discard is faster than extended analysis paralysis. The key is having clear acceptance criteria before you start evaluating.

**Structured data pays compound interest.** The machine view took a day to build but serves three purposes: SEO, ATS compatibility, and future AI agent grounding context. Investments that serve multiple stakeholders from a single implementation are the highest-leverage work you can do.

**Treat your views as a linked system, not isolated documents.** The brief versions are entry points that funnel readers toward the comprehensive version. Stable anchor IDs in the data layer make that linking reliable — and once those IDs are in external PDFs, they are a contract you cannot break. This is the same principle as API versioning: once you publish an interface, backward compatibility becomes a constraint.

**CSS has caught up.** CSS Grid, custom properties, `clamp()`, `:has()`, `prefers-color-scheme` — you genuinely do not need a framework for a content site in 2026. The entire stylesheet is under 200 lines. Know when your dependencies have been superseded by the platform itself.

**Cache your CI dependencies.** Six minutes of apt downloads on every push adds up fast when you are iterating on LaTeX templates. One caching step fixed it. Build pipeline optimization is not glamorous work, but it directly multiplies developer velocity.
