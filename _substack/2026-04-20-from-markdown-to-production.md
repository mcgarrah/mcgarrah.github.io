# From Markdown to Production: Building a Technical Blog That Actually Works

**Subtitle:** Jekyll, GitHub Pages, and the Engineering Behind Writing About Engineering

**Author:** McGarrah

**Planned:** April 20, 2026

**URL:** TBD

**Tags:** Software Engineering, Technical Writing, Web Development, Open Source, Blogging

---

I've been writing about technology since 2004. The platforms changed — WordPress, Blogger, hand-rolled HTML — but the habit stuck. In 2023 I moved everything to Jekyll on GitHub Pages, and what started as "just a blog" turned into a software engineering project with CI/CD pipelines, SEO automation, GDPR compliance, PDF generation, and custom Ruby plugins.

If you've ever wondered why a technical blog needs infrastructure, the answer is the same as why a homelab needs monitoring: because anything worth running is worth running well.

This is a companion to my earlier piece, [From Homelabs to Machine Learning](https://mcgarrah.substack.com/p/from-homelabs-to-machine-learning), which covered the infrastructure side. This one covers the other half — the writing platform, the development workflow, and why treating a blog like a software project teaches you skills that transfer directly to professional engineering.

*Thanks for reading! Subscribe for free to receive new posts and support my work.*

## Why Build a Blog Like Software?

A technical blog is a software product. It has users (readers), requirements (accessibility, SEO, performance), a deployment pipeline (GitHub Actions), dependencies (Ruby gems, npm packages), and bugs (broken links, rendering issues, sitemap bloat).

Treating it that way teaches you:

- **CI/CD pipelines** that validate every commit before deployment
- **Static site generation** — the same build-once-serve-everywhere pattern behind CDNs and JAMstack
- **Plugin architecture** — extending a framework without forking it
- **SEO as a system** — structured data, canonical URLs, and automated health checks
- **Privacy engineering** — GDPR compliance that actually works without breaking functionality
- **Documentation as code** — every article is a Markdown file in Git with full version history

These aren't blog skills. They're software engineering skills practiced on a project you control completely.

## The Platform: Jekyll on GitHub Pages

Jekyll is a Ruby-based static site generator. You write Markdown, Jekyll compiles it to HTML, and GitHub Pages serves it for free. No database, no server, no WordPress security patches at 2 AM.

- [How the Sausage Is Made: Every Feature Powering This Jekyll Blog](https://mcgarrah.org/jekyll-markdown-feature-reference/) — The complete feature reference for everything the blog can do: Mermaid diagrams, KaTeX math, collapsible sections, code highlighting with copy buttons, YouTube embeds, and more.
- [Building This Blog: Jekyll on GitHub Pages from Zero to 130+ Posts](https://mcgarrah.org/setting-up-jekyll-blog-github-pages/) — The setup guide: repository creation, custom domains, theme selection, GitHub Actions CI/CD, and what I'd do differently if I started over.
- [Jekyll Upgrade: Two Years of Cascading Breakage](https://mcgarrah.org/jekyll-upgrade-two-years-cascading-breakage/) — What happens when you skip two years of dependency updates. Ruby, Bundler, and Jekyll all moved on without me.
- [Running GitHub Pages Jekyll Locally](https://mcgarrah.org/github-pages-jekyll-locally/) — Local development setup. You need this before you can iterate quickly.

## Writing Features That Required Engineering

Every feature I added to the blog was driven by a specific need in a specific article. The features accumulated into something much larger than I planned.

### Diagrams for Infrastructure Posts

My [Ceph architecture posts](https://mcgarrah.org/proxmox-ceph-homelab-settings/) needed network topology diagrams. Rather than screenshot Visio drawings, I integrated Mermaid.js for diagrams rendered from text at build time.

- [Mermaid Diagram Rendering Challenges in Jekyll](https://mcgarrah.org/jekyll-mermaid-diagram-rendering-challenges/) — Getting Mermaid to work reliably in Jekyll required solving Liquid template conflicts, script loading order, and dark mode compatibility.

- [Jekyll Small Things: The Polish Features That Add Up](https://mcgarrah.org/jekyll-small-things-polish-features/) — Copy buttons on code blocks, reading time estimates, and the small touches that make a technical blog feel professional.
- [Jekyll Liquid Code Fence Rendering Trap](https://mcgarrah.org/jekyll-liquid-code-fence-rendering-trap/) — When your blog post about Liquid templates gets processed *by* Liquid templates. The meta-debugging story.

### PDF Exports for the Resume

My [online resume](https://mcgarrah.org/resume/) needed downloadable PDF and DOCX versions. Rather than maintaining separate files, I built a Jekyll plugin that generates them at build time using Pandoc.

- [Jekyll Pandoc Exports Plugin](https://mcgarrah.org/jekyll-pandoc-exports-plugin/) — The plugin architecture: hooking into Jekyll's build lifecycle to run Pandoc on rendered HTML.
- [Pandoc Exports Resume Integration](https://mcgarrah.org/jekyll-pandoc-exports-resume-integration/) — Integrating the plugin with the resume site's specific layout and styling requirements.

### SEO as a System

SEO isn't a checkbox — it's a system that needs monitoring. I learned this after months of Google AdSense rejections that turned out to be structural issues with canonical URLs, sitemap bloat, and missing structured data.

The debugging started with a completely opaque rejection message — "your site isn't ready to show ads" — and no actionable feedback. Seven hours of systematic investigation later, I'd found sitemap 404 errors, a missing contact page, and navigation bugs that Google never explicitly identified.

- [Google AdSense Approval Failure: Debugging the 'Site Isn't Ready' Rejection](https://mcgarrah.org/adsense-approval-failure-remediation/) — The full debugging story: 20 unpublished posts leaking into the sitemap, the `published: false` gotcha in jekyll-sitemap, and why migrating from WordPress cost me my existing AdSense approval.
- [Jekyll SEO Sitemap and Canonical URL Fixes](https://mcgarrah.org/jekyll-seo-sitemap-canonical-url-fixes/) — Fixing the plumbing: canonical URLs that pointed to the wrong domain, sitemaps with duplicate entries.
- [Jekyll SEO Health Checks](https://mcgarrah.org/jekyll-seo-health-checks/) — Automated validation in CI: every push checks canonical URLs, sitemap XML, meta tags, structured data, and broken links.
- [Jekyll Sitemap Bloat: Tags, Categories, and Pagination](https://mcgarrah.org/jekyll-sitemap-bloat-tags-categories-pagination/) — Tag and category pages were inflating the sitemap with hundreds of low-value URLs. Fixing it required understanding what search engines actually want.
- [Improving E-E-A-T for Jekyll and AdSense](https://mcgarrah.org/improving-eeat-jekyll-adsense/) — Google's Experience, Expertise, Authoritativeness, and Trustworthiness signals, and how to implement them in a static site.

### GDPR Compliance

Google AdSense requires GDPR cookie consent for EU visitors. Building it correctly meant detecting user regions, conditionally loading scripts, and not breaking Google's own verification crawler in the process.

- [Implementing GDPR Compliance for Jekyll and AdSense](https://mcgarrah.org/implementing-gdpr-compliance-jekyll-adsense/) — The full implementation: EU detection via timezone and IP geolocation, consent storage, conditional script loading.
- [Fixing AdSense Verification Without Breaking GDPR](https://mcgarrah.org/adsense-verification-gdpr-script-loading-fix/) — My GDPR implementation was too aggressive — it hid the AdSense script from Google's verification bot. The architectural fix that separated verification from ad serving.

## Site Optimization

Performance matters for both user experience and SEO. A static site should be fast, but "static" doesn't mean "automatically optimized."

- [Jekyll Website Optimization Part 1](https://mcgarrah.org/jekyll-website-optimization-part-1/) — Structure, performance, and the first round of improvements.
- [Jekyll Website Optimization Part 2](https://mcgarrah.org/jekyll-website-optimization-part-2/) — Further refinements after measuring real-world performance.
- [SASS Circular Dependency Nightmare](https://mcgarrah.org/sass-circular-dependency-nightmare/) — What started as adding a print stylesheet turned into a multi-hour debugging session that exposed fundamental architecture problems in the SASS module hierarchy. The fix — extracting variables into a standalone module — is the same separation-of-concerns pattern you'd apply to any software dependency graph.
- [Adding Google Custom Search to Jekyll](https://mcgarrah.org/adding-google-custom-search-jekyll/) — Site search without a backend. Google Custom Search handles the indexing; Jekyll provides the search page.

## Managing Multiple Sites

The blog and resume are separate Jekyll sites in separate repositories, served under the same domain. This creates interesting challenges around sitemaps, themes, and whether to merge them.

- [Managing Multiple Jekyll Sites: Sitemap Challenges](https://mcgarrah.org/managing-multiple-jekyll-sites-sitemap-challenges/) — Two Jekyll sites, one domain, two sitemaps. How to make search engines understand the relationship.
- [Merging Two Jekyll Websites: Architectural Analysis](https://mcgarrah.org/merging-two-jekyll-websites-architectural-analysis/) — I evaluated merging the blog and resume into one site. The analysis of why I didn't is more useful than the merge would have been.

## The Ruby Plugin Side

Jekyll's plugin system lets you extend the build process with Ruby. I've written custom generators for tag pages, category pages, and Pandoc exports.

- [Jekyll Tag and Category Generator Plugin](https://mcgarrah.org/jekyll-tag-category-generator-plugin/) — A custom Ruby generator that creates individual pages for every tag and category. The kind of build-time code generation that's invisible to readers but essential for navigation.
- [Ruby Gem Release Automation](https://mcgarrah.org/ruby-gem-release-automation/) — Automating the release pipeline for the Pandoc exports gem. CI/CD for a Ruby gem is its own education.
- [Jekyll Theme Missing Head and Body Tags](https://mcgarrah.org/jekyll-theme-missing-head-body-tags/) — Debugging a theme issue where the HTML structure was technically invalid but browsers rendered it anyway. The kind of bug that only shows up when you add structured data validation.

## The Development Workflow

The blog itself has a development workflow that mirrors professional software projects — CI/CD, comments, content pipelines, and local development tooling.

- [Jekyll GitHub Actions CI/CD Pipeline](https://mcgarrah.org/jekyll-github-actions-cicd-pipeline/) — Automated builds, SEO validation, and deployment on every push. The same pipeline patterns used in production software.
- [Jekyll Giscus Comments Implementation](https://mcgarrah.org/jekyll-giscus-comments-implementation/) — Adding GitHub Discussions-backed comments to a static site. No database, no hosted service — just GitHub's API.
- [Jekyll Content Distribution Pipeline](https://mcgarrah.org/jekyll-content-distribution-pipeline/) — How content flows from draft to published to syndicated across platforms.
- [Jekyll Content Plumbing: Permalinks and Reading Time](https://mcgarrah.org/jekyll-content-plumbing-permalinks-reading-time/) — The invisible infrastructure: URL structure, reading time estimates, and excerpt handling.
- [Jekyll Run Plugin: Local Development Settings That Actually Work](https://mcgarrah.org/jekyll-run-vscode-plugin-local-development/) — VS Code integration for local Jekyll development. This led to discovering and fixing bugs in an abandoned extension — which became its own open-source project.

## The Connection to Professional Engineering

If this looks like a lot of engineering for "just a blog," that's the point. Every skill here transfers directly:

- **Jekyll plugins** teach you framework extension patterns — the same approach used in Django middleware, Express.js middleware, and Kubernetes operators
- **GitHub Actions CI/CD** is the same pipeline technology running production deployments at every company using GitHub
- **SEO structured data** is JSON-LD — the same linked data format used in knowledge graphs and ML training data annotation
- **GDPR compliance** is privacy engineering — increasingly required in ML systems that handle personal data
- **Static site generation** is the build-once-deploy-everywhere pattern behind every CDN, every serverless function, and every ML model serving endpoint
- **Open-source contribution** — finding a bug in a VS Code extension, diagnosing it, writing the fix, and publishing a maintained fork is the same workflow used in enterprise open-source

The blog is where I practice these skills on my own terms. The enterprise is where I apply them at scale.

## What's Next

The blog continues to evolve. Here's what's in the pipeline:

- **VS Code extension fork** — I found three bugs in the Jekyll Run VS Code extension, and the maintainer hasn't committed in five years. I'm forking it as "Run Jekyll" with bug fixes, new features (Clean and Doctor commands), and a real test suite. The debugging story alone spans seven articles.
- **Draft preview site** — Building a password-protected preview at `drafts.mcgarrah.org` so reviewers can see unpublished content and leave feedback via Giscus before articles go live. Staticrypt encryption on GitHub Pages, automated via GitHub Actions.
- **Jekyll deep dives** — More articles on the internal plumbing: Liquid template gotchas, Jekyll enhancements without plugins, and the formatting conventions that keep 140+ posts consistent.
- **Infrastructure crossover** — The [Proxmox cluster](https://mcgarrah.org/proxmox-ceph-guide/) is getting Caddy reverse proxies, ZFS boot mirror procedures, and eventually Kubernetes. The blog may move from GitHub Pages to self-hosted when the K8s cluster is production-ready.

If you're interested in the infrastructure side, my earlier piece [From Homelabs to Machine Learning](https://mcgarrah.substack.com/p/from-homelabs-to-machine-learning) covers the Proxmox, Ceph, and networking foundation. The next Substack installment covers what happens when that storage infrastructure fails — and how Ceph's self-healing saved my data.

## About Me

I'm Michael McGarrah — a cloud architect and data scientist with 25+ years in enterprise infrastructure. I hold an M.S. in Computer Science (AI/ML) from Georgia Tech, a B.S. in Computer Science from NC State, and I'm currently pursuing an Executive MBA at UNC Wilmington.

You can find more of my writing at [mcgarrah.org](https://mcgarrah.org), my detailed resume at [mcgarrah.org/resume](https://mcgarrah.org/resume), and my profiles on [LinkedIn](https://www.linkedin.com/in/michaelmcgarrah/), [GitHub](https://github.com/mcgarrah), and [Google Scholar](https://scholar.google.com/citations?user=Lt7T2SwAAAAJ).
