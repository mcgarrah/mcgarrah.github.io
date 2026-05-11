# Blog Refactor — Lessons from the Resume Rebuild

## Context

The resume site (`mcgarrah/resume`) went through a complete ground-up refactor in 2026: dropping Bootstrap, jQuery, CDN Font Awesome, the `github-pages` gem, and a fragile Pandoc regex pipeline — replacing everything with minimal CSS Grid, CSS custom properties for light/dark mode, an SVG sprite, and structured HTML that exports cleanly without post-processing hacks.

That refactor surfaced patterns, CI improvements, and architectural decisions that apply directly to the blog. This document captures what we learned and how to apply it here.

---

## 1. Weekly apt Cache Rotation (CI Reliability)

### What the resume learned

The resume CI uses `awalsh128/cache-apt-pkgs-action` to cache TeX Live and Pandoc packages (~500MB). The action takes a `version` key — same key means "use the cached `.deb` files." The problem: when Ubuntu's package repos push new point releases (which happens silently, mid-week, with no notification), the cached `.deb` files become stale. `dpkg` fails because the cached package versions no longer match what the repo metadata expects. The build breaks, and the fix is manually bumping the version key — which means you don't know it's broken until you push and watch it fail.

The fix was replacing the static version key with a date-derived weekly rotation:

```yaml
- name: Get cache week
  id: cache-week
  run: echo "week=$(date +%Y-%U)" >> "$GITHUB_OUTPUT"
- name: Install Pandoc and LaTeX
  uses: awalsh128/cache-apt-pkgs-action@latest
  with:
    packages: pandoc texlive-latex-base texlive-fonts-recommended ...
    version: ${{ steps.cache-week.outputs.week }}
```

`%Y-%U` gives the week number counting from Sunday. The cache refreshes every Sunday automatically. Within the week, builds hit the cache (fast). When Ubuntu pushes updates, the next Sunday rotation picks them up without manual intervention.

### Blog applicability

The blog's `seo-health-check.yml` workflow currently does a bare `sudo apt-get install -y libxml2-utils` with no caching. That's fine for one small package. But if we add html-proofer, Lighthouse CI, or other apt dependencies (which this document proposes), we should apply the weekly rotation pattern from day one rather than learning the same lesson twice.

The main `jekyll.yml` workflow doesn't install any apt packages today — it's pure Ruby. But if that changes (e.g., adding image optimization tools, or a link checker that needs system libraries), the pattern is ready.

### Implementation

Only needed when apt dependencies are added to the blog's CI. When that happens, use the resume's pattern verbatim. No action needed today unless we implement html-proofer (item #2 below).

---

## 2. html-proofer in CI

### What the resume has

The resume runs `htmlproofer` after every build:

```yaml
- name: HTML Proofer
  run: |
    bundle exec htmlproofer _site \
      --ignore-urls "/fonts.googleapis.com/,/fonts.gstatic.com/" \
      --ignore-status-codes "999,403" \
      --no-enforce-https \
      --ignore-missing-alt \
      --allow-missing-href \
      --disable-external || true
```

This catches:
- Broken internal links (typos in `href`, renamed pages without redirects)
- Missing images referenced in HTML
- Malformed HTML that browsers silently fix but may confuse search engines
- Anchor links (`#section-name`) pointing to non-existent IDs

The `--disable-external` flag skips checking external URLs (which are slow and flaky in CI). The `|| true` makes it non-blocking initially — warnings appear in the build log but don't fail the deploy. Once the existing issues are cleaned up, remove `|| true` to enforce.

### Why the blog needs this

With 170+ posts spanning 2001–2026, broken internal links accumulate silently:
- Posts get renamed and `redirect_from` covers the old URL, but other posts linking to the old URL still have stale `href` values
- The tag/category generator creates pages at specific paths — if the generator logic changes, links break
- Image paths change when assets are reorganized
- Anchor links (`#heading-name`) break when headings are reworded

Currently, the only way to discover these is manually clicking through the site or waiting for a reader to report it. html-proofer automates this check on every push.

### Implementation plan

1. Add `gem "html-proofer", "~> 5.0"` to the Gemfile
2. Add a step to `.github/workflows/jekyll.yml` after the build step
3. Start with `--disable-external` and `|| true` (non-blocking)
4. Fix the reported issues in a cleanup pass
5. Remove `|| true` to make it a hard gate
6. Later: enable external link checking on a weekly schedule (not every push — too slow and flaky)

### Considerations

- The blog has `redirect_from` on many posts. html-proofer should follow redirects for internal links — verify this works with the Jekyll redirect plugin's HTML meta-refresh approach.
- The blog uses `<!-- excerpt-end -->` separators and Liquid includes — ensure html-proofer doesn't flag Liquid template syntax in the built HTML.
- Google Custom Search page uses an external script that injects HTML — may need to be excluded from proofer.

---

## 3. Enhanced JSON-LD Structured Data

### What the resume has

The resume's machine view (`/resume/machine/`) outputs comprehensive Schema.org JSON-LD:
- `@type: Person` with `name`, `jobTitle`, `description`, `url`
- `sameAs` array linking to LinkedIn, GitHub, GitLab, ORCID, Google Scholar, ResearchGate
- `alumniOf` with `EducationalOrganization` entries for each degree
- `knowsAbout` array for topic authority signals
- `hasCredential` for certifications
- `worksFor` with current employer

This makes the resume trivially parseable by AI agents, ATS systems, and Google's knowledge graph.

### What the blog has today

The blog uses `jekyll-seo-tag` which generates basic JSON-LD automatically:
- Article type for posts (title, datePublished, author)
- WebSite type for the homepage
- Basic `author` with `name` and `url`

What's missing:
- No `sameAs` links to professional profiles (LinkedIn, GitHub, ORCID, etc.)
- No `knowsAbout` for topic authority (tells Google "this person is authoritative on Proxmox, Ceph, Kubernetes, ML")
- No `Person` entity on the About page connecting the blog to the resume
- No `BlogPosting` → `author` → `Person` chain with full professional identity

### Why this matters

Google's knowledge panel, AI overview snippets, and "People also ask" features all consume structured data. When an AI agent (Claude, GPT, Perplexity) is asked "Who is Michael McGarrah?" or "What does Michael McGarrah know about Ceph?", the structured data on the blog and resume is what feeds those answers. Without explicit `sameAs` and `knowsAbout` markup, the AI has to infer connections from unstructured text — which it does poorly for people who aren't famous.

The resume already declares the professional identity. The blog should reinforce it by linking back to the same Person entity with the same `sameAs` URLs.

### Implementation plan

1. Create `_includes/structured-data-person.html` with a comprehensive Person JSON-LD block
2. Include it on the About page (`about/index.md` or equivalent)
3. Extend the default post layout to include `sameAs` in the author block
4. Add `knowsAbout` based on the post's tags (map tags to Schema.org concepts)
5. Validate with Google's Rich Results Test
6. Validate with Schema.org validator

### Considerations

- `jekyll-seo-tag` already outputs JSON-LD. Adding a second `<script type="application/ld+json">` block is valid — Google merges multiple JSON-LD blocks on the same page. But they shouldn't conflict (e.g., two different `@type: Person` with different `name` values).
- The `sameAs` URLs must match exactly across the blog and resume. Maintain a single list in `_config.yml` and reference it from both the SEO tag config and the custom structured data include.
- `knowsAbout` should be a curated list of 10–15 high-level topics, not a dump of every tag. Tags like "proxmox", "ceph", "kubernetes", "machine-learning", "aws", "jekyll" map to authority signals. Tags like "homelab" or "hardware" are too generic to signal expertise.

---

## 4. Pagefind Replacing Google Custom Search

### What the resume is adding (Phase 5)

The resume's TODO.md includes Pagefind as the next major feature — a static search index generated at build time, served as a client-side JavaScript bundle. No external service, no API keys, no ads, works offline.

### What the blog has today

Google Custom Search (`cx: 50dc9b6524efa45a0`) embedded via an external script. Issues:
- Requires an external network request to Google's servers
- Shows Google branding and occasionally ads
- Doesn't work offline or on localhost during development
- Results are limited to what Google has indexed (new posts may not appear for days)
- Google can deprecate or change the Custom Search API at any time
- The search page is a separate HTML page that loads Google's JavaScript — it's not integrated into the site's design

### Why Pagefind is better for this site

Pagefind generates a search index at build time from the rendered `_site/` HTML. The index is a set of small static files served alongside the site. The JavaScript bundle is ~15KB gzipped. Search is instant (no network round-trip), works on localhost, indexes every post the moment it's published, and respects the site's styling.

For a technical blog with 170+ posts, the search index would be roughly 200–400KB — well within acceptable page weight for a feature that replaces an external dependency.

### Implementation plan

1. Add Pagefind indexing to the GitHub Actions build (after `jekyll build`, before `upload-pages-artifact`)
2. Add the Pagefind UI component to a search page (or inline in the header/nav)
3. Style the search UI to match light/dark mode CSS custom properties
4. Remove the Google Custom Search `cx` configuration and external script
5. Update the search page URL (or keep `/search/` and replace the content)
6. Test search relevance across the full post archive

### Considerations

- Pagefind indexes rendered HTML, not markdown source. This means code blocks, front matter values, and Liquid output are all searchable — which is good for a technical blog.
- The daily cron build (for future-dated posts) would regenerate the search index automatically. New posts become searchable the moment they publish.
- Pagefind supports filtering by metadata (tags, categories, dates). This could replace or complement the existing tag/category pages.
- The blog's `_drafts/` content is excluded from production builds, so drafts won't appear in the search index. Local development with `--drafts` would include them — which is actually useful for finding your own draft content.
- Pagefind is MIT-licensed and actively maintained by CloudCannon. It's used by major documentation sites (Astro docs, 11ty docs). Low risk of abandonment.

### Migration path

Keep Google Custom Search functional during the transition:
1. Build Pagefind search on a new page (`/search-new/` or behind a feature flag)
2. Validate search quality against the existing Google results
3. Swap the nav link from `/search/` (Google) to the Pagefind version
4. Remove Google Custom Search configuration after confirming no regressions

---

## 5. Jekyll Doctor in CI

### What the resume has

A single line in the build workflow:

```yaml
- name: Jekyll Doctor
  run: bundle exec jekyll doctor
```

This runs Jekyll's built-in diagnostic that checks for:
- Deprecated configuration keys
- Conflicting plugin settings
- URL/permalink configuration issues
- Missing or misconfigured dependencies

It runs in ~1 second and catches problems that would otherwise manifest as silent build weirdness (posts not appearing, wrong URLs, missing feeds).

### Why the blog should have it

The blog's `_config.yml` has accumulated settings over years. Some may be deprecated in Jekyll 4.4.x but still silently accepted. `jekyll doctor` would surface these. It's also useful as a canary — if a Gemfile update introduces a plugin conflict, `doctor` catches it before the build produces subtly wrong output.

### Implementation

Add one step to `.github/workflows/jekyll.yml` before the build step:

```yaml
- name: Jekyll Doctor
  run: bundle exec jekyll doctor
```

No Gemfile changes needed — `jekyll doctor` is built into Jekyll core.

### Considerations

- If `doctor` reports warnings (not errors), it exits 0 and the build continues. Only hard configuration errors cause a non-zero exit.
- Run it locally first (`bundle exec jekyll doctor`) to see if there are existing warnings to address before adding it to CI.

---

## 6. Sitemap Entry Count Validation

### What the resume taught us

The resume's "Verify exports" step explicitly checks that expected output files exist after the build. This caught a regression where a config change silently excluded content from the build — the site deployed successfully but was missing pages.

### Blog equivalent

The blog already validates that the sitemap doesn't contain `localhost` URLs. But it doesn't check that the sitemap has a reasonable number of entries. If a config change or plugin update accidentally excludes posts (e.g., a `future: false` default kicking in, or a category filter misconfigured), the sitemap would shrink dramatically — and the current CI wouldn't notice.

### Implementation

Add a step that counts sitemap entries and fails if the count drops below a threshold:

```yaml
- name: Validate sitemap entry count
  run: |
    count=$(grep -c '<url>' ./_site/sitemap.xml)
    echo "Sitemap contains $count URLs"
    if [ "$count" -lt 150 ]; then
      echo "::error::Sitemap has only $count entries (expected 150+). Posts may be excluded."
      exit 1
    fi
```

The threshold (150) should be set to ~80% of the current post count. Update it periodically as the archive grows.

### Considerations

- This is a blunt instrument — it catches catastrophic exclusions but not the loss of a single post. html-proofer (item #2) is better for individual link integrity.
- The threshold needs occasional updating. An alternative: store the previous count as a CI artifact and fail if the delta exceeds 10% in a single push.

---

## 7. Action Version Pinning Strategy

### What the resume does

The resume pins action versions explicitly:
- `actions/checkout@v6`
- `ruby/setup-ruby@v1.306.0` (exact patch version)
- `actions/configure-pages@v6`
- `actions/upload-pages-artifact@v5`

### What the blog does

Similar, but `ruby/setup-ruby@v1.300.0` — slightly behind. The blog also has version reference comments at the bottom of the workflow file, which is a good practice for tracking what's current.

### Recommendation

Both repos should use the same pinning strategy:
- Major version tags (`@v6`) for GitHub's own actions (they maintain backward compat within major versions)
- Exact version for `ruby/setup-ruby` (Ruby setup is sensitive to version changes — a minor bump can change gem resolution behavior)
- `@latest` only for actions where you explicitly want auto-updates (like the apt cache action, where "latest" means "latest bug fixes to the caching logic")

The blog's version comments at the bottom of the workflow are worth adopting in the resume too — they make it obvious when versions are stale.

---

## 8. Build Verification Patterns

### What the resume does well

The resume has explicit verification steps:
- `jekyll doctor` before build (config sanity)
- `htmlproofer` after build (link integrity)
- `Verify exports` after PDF generation (output existence)

Each step catches a different class of failure:
- Doctor: "Is the configuration valid?"
- Build: "Does it compile?"
- Proofer: "Is the output internally consistent?"
- Verify: "Did the expected artifacts actually get created?"

### Blog's current verification

- Sitemap localhost check (catches one specific misconfiguration)
- OG image existence check (catches missing assets)

### Gap

No link integrity check (html-proofer), no config sanity check (doctor), no post count regression check. The blog is more complex than the resume (170+ posts, multiple layouts, tag/category generators, pagination) — it has more surface area for silent regressions.

### Recommended verification stack for the blog

```
1. jekyll doctor          → config sanity
2. jekyll build           → compilation
3. sitemap URL check      → no localhost (existing)
4. sitemap count check    → no mass exclusion (new)
5. OG image check         → asset integrity (existing)
6. html-proofer           → link integrity (new)
```

---

## Priority and Sequencing

| Priority | Item | Effort | Risk if skipped | Dependencies | Status |
|----------|------|--------|-----------------|--------------|--------|
| 1 | Jekyll Doctor in CI | 1 line | Low — but free insurance | None | ✅ Done |
| 2 | html-proofer in CI | Gemfile + workflow + cleanup pass | Medium — broken links accumulate | None | Pending |
| 3 | Sitemap count validation | 5 lines in workflow | Low — catches catastrophic exclusions | None | ✅ Done |
| 4 | Enhanced JSON-LD | 1 include file + config | Medium — AI discoverability gap | None | Pending |
| 5 | Pagefind search | Build step + page rewrite | Low — Google CSE works fine today | Items 1–3 done first (clean foundation) | Pending |
| 6 | Weekly apt cache rotation | Pattern ready, apply when needed | N/A until apt deps are added | Adding html-proofer or other apt deps | Pending |

Items 1–3 are quick wins that improve CI reliability. Item 4 improves discoverability. Item 5 is a larger project that removes an external dependency. Item 6 is a pattern to apply when the time comes.

---

## Completed

- [x] **Jekyll Doctor in CI** (2026-05-05) — Added before build step. Zero config, catches deprecated settings and plugin conflicts.
- [x] **Sitemap count validation** (2026-05-05) — Fails build if sitemap has <150 URLs. Catches accidental mass exclusion.
- [x] **Action version pinning** (2026-05-05) — `ruby/setup-ruby` v1.300.0 → v1.306.0, `upload-pages-artifact` v4 → v5. Matches resume repo.

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-05 | Document resume refactor lessons for blog | Avoid re-learning the same patterns |
| | Jekyll Doctor is free insurance | 1 second, zero config, catches silent issues |
| | html-proofer starts non-blocking | Fix existing issues before enforcing |
| | Pagefind over Google Custom Search | Self-hosted, no ads, works offline, instant |
| | JSON-LD extends jekyll-seo-tag (doesn't replace) | Multiple JSON-LD blocks are valid; avoid conflicts |
| | Sitemap count is a blunt but useful check | Catches "accidentally excluded all posts" scenarios |
| | Weekly apt rotation applied when apt deps are added | Don't add complexity before it's needed |
