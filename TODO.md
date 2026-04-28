# Jekyll Website TODO List

## High Impact

### GDPR Cookie Consent Ruby Plugin

- [ ] Complete the GDPR cookie consent Ruby plugin as a proper Jekyll gem — The GDPR article (`2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md`) and the plugin development draft (`_drafts/2025-12-18-jekyll-gdpr-plugin-development.md`) cover the implementation, but the plugin needs a follow-through article about packaging it as a published Ruby gem. Follow the same pattern as the Pandoc exports plugin (`2026-04-12-jekyll-pandoc-exports-plugin.md`) and the gem release automation article (`2026-04-11-ruby-gem-release-automation.md`). Write the companion article and publish the gem.

### Front Matter Hygiene

The blog has 173 published posts but front matter completeness varies widely. Older posts (2001-2016) have minimal front matter while newer posts have full SEO optimization. Filling these gaps improves search engine visibility across the entire archive.

- [ ] Add `description` to posts missing it (122 of 173 posts) — Google uses this for search result snippets in SERPs. Without it, Google auto-generates a snippet from page content, which is often a poor representation of the article. The `jekyll-seo-tag` plugin renders this as `<meta name="description">`. Target 150-160 characters per post.
- [ ] Add `tags` to posts missing them (51 of 173 posts) — Tags drive the tag page generator and help readers discover related content. Posts without tags are invisible to tag-based navigation. Many of the 50 untagged posts are from 2001-2015 and predate the tag system.
- [ ] Add `<!-- excerpt-end -->` separator to posts missing it (35 of 173, mostly 2004-2015) — Without the custom separator, Jekyll uses the first paragraph as the excerpt. For technical posts that start with context-setting, this produces unhelpful homepage previews. The 34 missing posts are deep in pagination but still appear in RSS feeds and search results.
- [ ] Add `last_modified_at` to posts missing it (62 of 173) — The `jekyll-seo-tag` plugin uses this to generate `<meta property="article:modified_time">`, signaling content freshness to search engines. Posts updated since original publication should reflect the update date. Google may rank recently-modified content higher for competitive queries.
- [ ] Add missing alt tags to images — Required for accessibility (screen readers) and SEO (Google Image Search). The SEO health check workflow already flags these but doesn't block deploys.

### Tag Hygiene

- [ ] Consolidate singleton tags — 189 of 334 tags are used on only one post. Each generates a tag page with a single post, marked `noindex` by the tag generator plugin. These dilute the tag system's usefulness for navigation. Merge singleton tags into existing broader tags where possible (e.g., merge `dart-sass` into `sass`, merge `serial-console` into `configuration`). This would reduce generated pages and make the `/tags/` index more useful.

### Resume Repo Gemfile

The resume site at `mcgarrah.org/resume/` has two Gemfile issues that could cause unexpected breakage:

- [ ] Pin Jekyll version in resume `Gemfile` with `~>` constraint — Currently `gem "jekyll"` with no version. A `bundle update` could jump from Jekyll 3.x to 4.x (or beyond) without warning, breaking the build. The blog pins `gem "jekyll", "~> 4.4.1"` which allows patch updates but prevents major version surprises.
- [ ] Resolve `jekyll` + `github-pages` gem conflict — Both `gem "jekyll"` and `gem 'github-pages'` are present. The `github-pages` gem bundles its own pinned Jekyll version (currently 3.10.x). Having both can cause version resolution conflicts where Bundler picks an unexpected Jekyll version. Choose one: either use `github-pages` (which pins Jekyll for you but limits plugin choices) or use standalone `jekyll` with a pinned version (which gives full control but requires a custom GitHub Actions build).

## Quick Wins

- [x] Create proper favicon set (16x16, 32x32, 180x180 Apple Touch, `site.webmanifest`) — Full set generated and deployed. Blog post: `2026-06-02-jekyll-modern-favicon-set.md`.
- [ ] Upgrade `http://` links to `https://` in old posts (2011-2015 era) — Several old posts link to Wikipedia, blogspot, SourceForge, and other sites using `http://`. These sites all support HTTPS now. Mixed content warnings aside, `https://` links are a minor trust signal and prevent browser security warnings. Simple find-and-replace across the affected posts.

## Resume Repo CI/CD Parity

The blog has three GitHub Actions workflows (build/deploy, CodeQL, SEO health check), Dependabot across three ecosystems, and Lighthouse CI. The resume repo has only the build workflow and Dependabot. Given that the resume is a professional asset — often the first thing a potential employer sees — it deserves the same quality gates.

- [ ] Add SEO health check workflow to resume repo — Validate canonical URLs, meta tags, structured data, and broken links. The blog's `seo-health-check.yml` can be adapted with minimal changes.
- [ ] Add Lighthouse CI config to resume repo — Performance, accessibility, and SEO scoring. The blog's `.lighthouserc.json` is a good starting template. The resume should score ≥0.9 on accessibility since it's a professional document.
- [ ] Add CodeQL workflow to resume repo — Security scanning for the GitHub Actions workflows themselves. Low effort (copy the blog's `codeql.yml`), low maintenance, free on public repos.
- [ ] Pin all gem versions in resume `Gemfile` with `~>` constraints — Match the blog's approach of pessimistic version constraints on every gem. Prevents surprise breakage from major version jumps during `bundle update`.

## User Experience

- [ ] Add share buttons for social media — Reduce friction for readers who want to share posts on LinkedIn, Reddit, or Twitter/X. The `jekyll-codex.org` without-plugin approach avoids adding JavaScript dependencies. Currently readers must manually copy the URL.
- [ ] Create reading progress indicator (scroll-based) — A thin progress bar at the top of the page showing how far through the article the reader is. Different from the existing "X min read" estimate which is static. Useful for long technical posts (some exceed 3,000 words).
- [ ] Implement breadcrumb navigation — Show the path (Home > Category > Post) at the top of each page. Helps readers understand site structure and navigate up. Also generates breadcrumb structured data that Google displays in search results.
- [ ] Add tag cloud visualization — A visual representation of all tags weighted by post count on the `/tags/` page. More engaging than the current flat list. Should be done after tag hygiene cleanup to avoid displaying 138 singleton tags.
- [ ] Add automated "related posts" to post layout — 16 of 139 posts have hand-curated "Related Posts" sections (all from Sep 2025 onward). Manual cross-references are higher quality but don't scale to the 123 older posts. An automated solution via `site.related_posts` or tag-based matching would provide baseline related content for every post. Could coexist with manual sections where they exist.
- [x] Fix "read more" links — The post title is currently used as the link text for "read more" links, making them excessively long. Move the title into a `title=""` tooltip attribute instead and use short link text like "Read more" or "Continue reading". Keeps the links compact while preserving the context on hover.

## Performance

- [ ] Implement lazy loading for images — Add `loading="lazy"` to `<img>` tags so images below the fold don't load until the reader scrolls to them. Improves initial page load time, especially on image-heavy posts like the PiKVM parts list or network diagrams.
- [ ] Add responsive images and WebP format support — Serve appropriately sized images based on viewport width and modern formats where supported. Reduces bandwidth for mobile readers. Would require an image processing step in the build pipeline.
- [ ] Optimize CSS delivery (inline critical CSS) — Extract above-the-fold CSS and inline it in the `<head>` to eliminate the render-blocking stylesheet request. Improves First Contentful Paint in Lighthouse scores.

## Content Organization

- [ ] Consolidate and clean up old posts from 2001-2016 — The oldest posts are short, lack front matter, and some have broken formatting from platform migrations (WordPress → Blogger → Jekyll). Consider adding a "vintage" category, updating front matter, and fixing formatting issues. Some may be candidates for merging into retrospective posts.
- [ ] Audit and fix dead links in old posts (2011-2015 era) — Posts from this era link to blogspot blogs, old Seagate forums, SourceForge projects, and other sites that may no longer exist. The Lychee link checker in the SEO workflow catches new breakage, but a one-time audit of the ~14 unique external URLs in the oldest posts would clean up existing link rot. Replace dead links with Wayback Machine archives where possible.
- [ ] Create post templates for common topics (technical, personal) — Standardize front matter and section structure for recurring post types (homelab walkthrough, Jekyll feature, hardware review, opinion piece). Reduces the friction of starting a new post and ensures consistent SEO metadata.
- [ ] Implement post series/collections feature — Group related posts into named series (e.g., "Proxmox & Ceph Homelab", "Jekyll Blog Infrastructure") with previous/next navigation. Jekyll collections or a custom Liquid include could handle this. The [Proxmox & Ceph Guide](/proxmox-ceph-guide/) page is a manual version of this concept.

## Security

- [ ] Add Subresource Integrity (SRI) hashes for CDN resources — CDN-loaded scripts (Mermaid, KaTeX, Clipboard.js) could be tampered with if the CDN is compromised. SRI hashes ensure the browser only executes scripts that match the expected hash. Requires updating hashes when CDN versions change (Dependabot PRs would be the trigger).
- [ ] Evaluate self-hosting critical libraries (Mermaid, KaTeX, Clipboard.js) — Eliminates CDN dependency entirely. Trade-off: larger repository, manual version updates, but no external runtime dependency. The `package.json` already tracks these versions for security scanning.
- [ ] Add Content Security Policy (CSP) headers — Restrict which domains can serve scripts, styles, and images on the site. Prevents XSS attacks by blocking unauthorized script execution. GitHub Pages has limited header support, but a `<meta>` tag CSP in the HTML head provides baseline protection.
- [ ] Implement HTTP security headers (HSTS, X-Frame-Options) — HSTS forces HTTPS connections. X-Frame-Options prevents clickjacking. GitHub Pages handles HSTS at the infrastructure level, but explicit headers in the HTML provide defense in depth.

## Accessibility

- [ ] Add keyboard navigation support — Ensure all interactive elements (navigation, code copy buttons, tag links) are reachable and operable via keyboard. Test with Tab, Enter, and arrow keys. Important for users who can't use a mouse.
- [ ] Implement skip-to-content links — A hidden link at the top of each page that becomes visible on keyboard focus, allowing screen reader and keyboard users to skip the navigation and jump directly to the main content. Standard accessibility pattern.

## Privacy

- [ ] Evaluate privacy-focused analytics (Plausible or similar) — Google Analytics requires GDPR consent management and loads third-party JavaScript. Plausible is lightweight (~1KB), cookie-free, GDPR-compliant by default, and could replace or supplement GA. Trade-off: paid service ($9/month) vs free GA with consent complexity.

## Future Considerations

- [ ] Multi-language support (English/Spanish) — Would differentiate the blog and reach a broader audience. The [Polyglot plugin](https://github.com/untra/polyglot/) handles Jekyll multi-language sites. Start with ES and EN. Significant ongoing effort to maintain translations. Reference: [Multilingual Jekyll site guide](https://leo3418.github.io/collections/multilingual-jekyll-site/).
- [ ] Full-text search with local indexing (beyond Google Custom Search) — Google Custom Search depends on Google's index and shows ads on the free tier. A local search index (Lunr.js, Pagefind) would provide instant, ad-free search without external dependencies. Trade-off: increases build time and JavaScript bundle size.
- [ ] Progressive Web App (PWA) manifest and service worker — Allow readers to "install" the blog on mobile home screens and read cached content offline. Useful for readers in low-connectivity environments. Requires a `manifest.json` and service worker JavaScript.
- [ ] Custom 403 error page — The blog has custom 404 and 500 pages with haiku but no 403 (Forbidden). Low priority since GitHub Pages rarely serves 403s, but completes the error page set.
- [ ] Performance and uptime monitoring — External monitoring (UptimeRobot, Pingdom free tier) to alert if the site goes down. GitHub Pages is generally reliable but outages happen. Also useful for tracking response time trends.
