# Drafts Site: Analysis & Options

## Goal

Expose a preview site that builds with `--drafts --future` flags, allowing vetted reviewers to see unpublished content, give feedback, and not pollute the production site or get indexed by search engines.

## Constraints

1. **GitHub Pages only serves one site per repo** — one branch, one CNAME, one domain
2. **GitHub Pages has no native authentication** — static files are public or nothing
3. **Google must not index the drafts site** — `robots.txt` + `noindex` meta tags required
4. **Production site must not be affected** — no config changes, no build flag changes
5. **No new external services** — stay within GitHub + Porkbun (tools already in use)
6. **Minimal ongoing maintenance** — this is a hobby site, not a SaaS product

## Security Reality Check

The `mcgarrah.github.io` repo is **public**. Anyone can already read `_drafts/` and future-dated posts in `_posts/` by browsing the repo on GitHub. The raw markdown is fully visible.

This means:
- **The drafts site is not hiding secrets** — it's providing a *rendered preview* of content that's already public in source form
- **Password protection is a UX signal**, not real access control — it says "this isn't ready, don't share it" rather than "you can't see this"
- **Staticrypt is optional** — it adds a speed bump but doesn't protect content that's already in a public repo
- **The real protection is `noindex`** — keeping Google from indexing unfinished content is the primary goal

This simplifies the options significantly.

---

## GitHub Pages Naming: How It Works

### `*.github.io` Domains

`*.github.io` domains are tied to GitHub usernames/orgs. `mcgarrah.github.io` is yours because your username is `mcgarrah`. You cannot use `drafts.github.io` — that belongs to whoever owns the `drafts` GitHub username. There's no way to get a second `*.github.io` domain.

### Project Pages (Sub-Path)

Any repo under your account can be a GitHub Pages project site:
- Repo named `drafts` → serves at `mcgarrah.github.io/drafts/` → with custom domain: `mcgarrah.org/drafts/`
- This is exactly how your `resume` repo works: `mcgarrah.org/resume/`
- Uses `baseurl: "/drafts"` in Jekyll config
- **No DNS changes needed** — it's a path under your existing domain
- **No CNAME file needed** in the drafts repo

### Custom Subdomain

Any repo can also use a custom subdomain:
- Repo named `drafts.mcgarrah.org` (or any name) with a `CNAME` file containing `drafts.mcgarrah.org`
- Requires a DNS CNAME record in Porkbun: `drafts.mcgarrah.org` → `mcgarrah.github.io.`
- GitHub routes by `Host` header — it finds the repo whose `CNAME` matches the request
- Uses `url: "https://drafts.mcgarrah.org"` and `baseurl: ""` in Jekyll config

### Comparison

| Aspect | Project Page (`/drafts/`) | Subdomain (`drafts.mcgarrah.org`) |
|--------|--------------------------|----------------------------------|
| DNS changes | None | CNAME record in Porkbun |
| Repo name | `drafts` (any name works) | Any name (convention: `drafts.mcgarrah.org`) |
| URL | `mcgarrah.org/drafts/` | `drafts.mcgarrah.org` |
| Jekyll config | `baseurl: "/drafts"` | `url: "https://drafts.mcgarrah.org"` |
| CNAME file | Not needed | Required |
| HTTPS | Automatic (under main domain) | Automatic (GitHub provisions cert) |
| Isolation feel | Looks like part of main site | Looks like a separate site |
| robots.txt | Shared with main site — **problem** | Separate — clean `Disallow: /` |
| Cookie/localStorage | Shared with main domain | Separate domain |

### The robots.txt Problem with Project Pages

This is the key issue with `mcgarrah.org/drafts/`:
- `robots.txt` lives at the domain root (`mcgarrah.org/robots.txt`) and is served by the **main site**
- You can add `Disallow: /drafts/` to the main site's `robots.txt`, but that means **modifying the production site** to support the drafts site
- The `noindex` meta tag on each page still works, but `robots.txt` is the first line of defense
- This violates constraint #4 (production site must not be affected)

**Verdict:** The subdomain approach (`drafts.mcgarrah.org`) is cleaner because it gets its own `robots.txt`, its own cookie scope, and feels like a separate site. The DNS setup is a one-time cost.

---

## Option 1: Subdomain + Staticrypt (Recommended)

### How It Works

1. Create a new repo: `mcgarrah/drafts.mcgarrah.org`
2. GitHub Actions workflow in `mcgarrah.github.io` (the main repo):
   - Triggers on push to `main` (or on-demand via `workflow_dispatch`)
   - Builds Jekyll with `--drafts --future --config _config.yml,_config_drafts.yml`
   - Runs [Staticrypt](https://github.com/robinmoisson/staticrypt) on every HTML file in `_site/`
   - Replaces `robots.txt` with `Disallow: /`, removes feeds and sitemaps
   - Pushes the built `_site/` contents to the `drafts.mcgarrah.org` repo's `main` branch
3. The `drafts.mcgarrah.org` repo has GitHub Pages enabled, serving the static files
4. `CNAME: drafts.mcgarrah.org` in the drafts repo, DNS configured in Porkbun
5. Reviewers visit `drafts.mcgarrah.org`, enter the shared password, browse the rendered site

### Why Staticrypt (Even Though the Repo Is Public)

The source markdown is public, but:
- Most reviewers aren't developers — they want a rendered website, not raw markdown on GitHub
- The password prompt signals "this is a private preview" — sets expectations
- Prevents casual link-sharing from exposing rendered drafts to the world
- Blocks web scrapers that ignore `robots.txt`
- It's a single line in the build pipeline — minimal complexity cost

If you later decide the password is unnecessary friction, remove the Staticrypt step and everything else still works (Option 2).

### Automation Flow

```
mcgarrah.github.io (push to main)
  └─ GitHub Actions workflow
       ├─ bundle exec jekyll build --drafts --future --config _config.yml,_config_drafts.yml
       ├─ staticrypt _site/**/*.html -p ${{ secrets.DRAFTS_PASSWORD }} --short --remember 30
       ├─ Replace robots.txt, remove feed.xml and sitemap.xml
       └─ Push _site/ → mcgarrah/drafts.mcgarrah.org (main branch)
            └─ GitHub Pages auto-deploys → drafts.mcgarrah.org
```

### Cross-Repo Push

GitHub Actions can push to another repo using a Personal Access Token (PAT) or a deploy key:

- **PAT approach**: Store a GitHub PAT with `repo` scope as `secrets.DRAFTS_DEPLOY_TOKEN` in the main repo. The workflow clones the drafts repo, copies `_site/` contents, commits, and pushes.
- **Deploy key approach**: Generate an SSH key pair, add the public key as a deploy key (with write access) on the drafts repo, and store the private key as a secret in the main repo. More secure (scoped to one repo) but slightly more setup.

### Staticrypt Details

[Staticrypt](https://github.com/robinmoisson/staticrypt) (v3+) uses AES-256-GCM with a password-derived key (Web Crypto API). Each HTML page is replaced with a password prompt that decrypts the original content in-browser.

```bash
# Install
npm install -g staticrypt

# Encrypt all HTML files in _site/ with a shared password
staticrypt _site/**/*.html -p "reviewer-password" --short --template-title "Draft Preview"

# Or use --remember to allow "remember me" checkbox (stores key in localStorage)
staticrypt _site/**/*.html -p "reviewer-password" --short --remember 30
```

Key behaviors:
- `--short` uses a compact password prompt page
- `--remember 30` lets reviewers skip the password for 30 days (localStorage)
- Password is NOT stored in the HTML — only a salted hash for verification
- Encrypted content is AES-256-GCM — not trivially reversible
- Password change requires a rebuild (which happens automatically on push)

### Pros

- **Zero external services** — only GitHub (already used) and Porkbun (already used)
- Complete isolation from production site (separate domain, robots.txt, cookies)
- Automated via GitHub Actions — push to `main` updates both sites
- Password prompt signals "private preview" to reviewers
- `robots.txt` with `Disallow: /` blocks crawlers
- Free — no paid tiers, no bandwidth limits beyond GitHub Pages
- Staticrypt is removable — drop it anytime to simplify (becomes Option 2)

### Cons

- Shared password (not per-user) — anyone with the password can access
- Staticrypt encrypts HTML only — images, CSS, JS are unencrypted (acceptable given public repo)
- Two repos to maintain (but the drafts repo is fully automated — no manual commits)
- Staticrypt adds ~30KB per page for the decryption wrapper
- Requires one-time DNS setup in Porkbun

### DNS Setup (Porkbun)

One-time setup. Add a CNAME record in Porkbun:

```
drafts.mcgarrah.org  CNAME  mcgarrah.github.io.
```

GitHub routes by `Host` header:
1. Browser requests `drafts.mcgarrah.org` → DNS resolves to GitHub's IPs
2. GitHub sees `Host: drafts.mcgarrah.org`
3. GitHub finds `mcgarrah/drafts.mcgarrah.org` repo with matching `CNAME` file
4. Serves that repo's GitHub Pages content

The `CNAME` file in the drafts repo is created automatically by the GitHub Actions workflow.

### Verdict: **Best fit — uses only GitHub and Porkbun, fully automated, clean separation, password optional but recommended.**

---

## Option 2: Subdomain WITHOUT Staticrypt (Simplest)

### How It Works

Identical to Option 1 but skip the Staticrypt step. The drafts site is publicly accessible but:
- `robots.txt` blocks crawlers with `Disallow: /`
- `<meta name="robots" content="noindex, nofollow">` on every page
- No links from the production site
- No Google Analytics, no AdSense, no sitemap

### Pros

- Simplest possible implementation — just Jekyll build + push
- No password to share or manage
- No Staticrypt dependency or build step
- Still automated via GitHub Actions
- Reviewers just click the link and see the site

### Cons

- **No access gate** — anyone who discovers the URL can read drafts
- But: the source markdown is already public in the GitHub repo, so this is consistent
- Relies on `noindex` meta tags to prevent search engine indexing

### When to Choose This

- If your reviewers are non-technical and a password prompt would confuse them
- If you decide the "private preview" signal isn't worth the friction
- If you want to start simple and add Staticrypt later if needed

### Verdict: Perfectly defensible given the public repo. Start here if you want minimal complexity, upgrade to Option 1 if you want the speed bump.

---

## Option 3: Project Page at `/drafts/` (No DNS Changes)

### How It Works

- Create a repo named `drafts` under your account
- GitHub Pages serves it at `mcgarrah.github.io/drafts/` → `mcgarrah.org/drafts/`
- Same pattern as your `resume` repo at `mcgarrah.org/resume/`
- Jekyll config uses `baseurl: "/drafts"`

### Pros

- No DNS changes — works immediately
- Familiar pattern (same as resume)
- Simpler mental model — everything under one domain

### Cons

- **robots.txt is shared with the main site** — you'd need to add `Disallow: /drafts/` to the production `robots.txt`, which modifies the production site
- **Cookies and localStorage shared** with main domain — Staticrypt's `--remember` key would be visible to the main site's JavaScript (low risk but not clean)
- **Feels like part of the main site** — reviewers might not realize they're on a preview
- The `/drafts/` path is easily guessable from the main site

### Verdict: Works but less clean than the subdomain approach. The shared `robots.txt` problem is the main issue. Use this only if you want to avoid DNS changes entirely.

---

## Build Pipeline Considerations (All Options)

### Jekyll Build Differences

| Setting | Production (`mcgarrah.org`) | Drafts (`drafts.mcgarrah.org`) |
|---------|---------------------------|-------------------------------|
| `--drafts` | No | Yes |
| `--future` | No | Yes |
| `url` | `https://mcgarrah.org` | `https://drafts.mcgarrah.org` |
| `baseurl` | `""` | `""` (subdomain) or `"/drafts"` (project page) |
| `robots.txt` | `Allow: /` | `Disallow: /` |
| `meta robots` | (none) | `noindex, nofollow` |
| `google_analytics` | `G-F90DVB199P` | (disabled) |
| `giscus` | production repo | drafts repo (separate feedback) |
| `sitemap` | generated | removed |
| `feed.xml` | generated | removed |

### Config Override File

Create a `_config_drafts.yml` overlay in the main repo:

```yaml
url: "https://drafts.mcgarrah.org"
google_analytics: ""
google_adsense: ""

# Override Giscus to point to drafts repo (keeps feedback separate from production)
giscus:
  repo: mcgarrah/drafts.mcgarrah.org
  repo_id: "<drafts-repo-id>"         # Get from https://giscus.app after creating repo
  category: "Draft Reviews"
  category_id: "<category-id>"         # Get from https://giscus.app after creating category
  mapping: pathname
  strict: 0
  reactions_enabled: 1
  emit_metadata: 0
  input_position: bottom
  theme: preferred_color_scheme
  lang: en
  loading: lazy
```

Build command:

```bash
bundle exec jekyll build --drafts --future --config _config.yml,_config_drafts.yml
```

Jekyll merges configs left-to-right, so `_config_drafts.yml` overrides the production values.

### Visual Indicator for Reviewers

Add a banner to the drafts site so reviewers know they're on the preview:

```html
{% if site.url contains 'drafts' %}
<div style="background: #ff6600; color: white; text-align: center; padding: 8px; position: fixed; top: 0; width: 100%; z-index: 9999;">
  ⚠️ DRAFT PREVIEW — Not for public distribution
</div>
{% endif %}
```

This goes in `_layouts/default.html` (or a new include). It renders only when the site URL contains "drafts" — invisible on production.

### Sketch of GitHub Actions Workflow

This would live in the main repo as `.github/workflows/deploy-drafts.yml`:

```yaml
name: Deploy Drafts Site

on:
  push:
    branches: ["main"]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout main repo
        uses: actions/checkout@v6

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2.6'
          bundler-cache: true

      - name: Setup Node (for Staticrypt)
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Staticrypt
        run: npm install -g staticrypt

      - name: Build Jekyll with drafts and future
        run: bundle exec jekyll build --drafts --future --config _config.yml,_config_drafts.yml
        env:
          JEKYLL_ENV: production

      - name: Encrypt HTML with Staticrypt
        run: |
          find _site -name '*.html' -exec staticrypt {} -p "${{ secrets.DRAFTS_PASSWORD }}" --short --remember 30 \;

      - name: Replace robots.txt and remove feeds/sitemaps
        run: |
          printf "User-agent: *\nDisallow: /\n" > _site/robots.txt
          rm -f _site/feed.xml _site/sitemap.xml _site/sitemapindex.xml

      - name: Deploy to drafts repo
        run: |
          cd _site
          git init
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          echo "drafts.mcgarrah.org" > CNAME
          git add -A
          git commit -m "Deploy drafts site from ${{ github.sha }}"
          git push --force https://x-access-token:${{ secrets.DRAFTS_DEPLOY_TOKEN }}@github.com/mcgarrah/drafts.mcgarrah.org.git HEAD:main
```

**Secrets required:**
- `DRAFTS_PASSWORD` — the shared password for Staticrypt (remove this and the Staticrypt steps for Option 2)
- `DRAFTS_DEPLOY_TOKEN` — GitHub PAT with `repo` scope (or use deploy key)

---

## Reviewer Feedback Mechanism

The whole point is getting feedback. Options:

### Giscus on Drafts Repo (Recommended)

Enable GitHub Discussions on the `drafts.mcgarrah.org` repo with a "Draft Reviews" category. Configure Giscus to point to that repo (via `_config_drafts.yml` above). This gives:
- Per-post threaded comments (same UX as production)
- Feedback stays in the drafts repo — completely separate from production comments
- When a post is promoted to `_posts/`, draft comments stay behind (they served their purpose)
- Reviewers need a GitHub account (likely fine for your audience)

**Giscus + Staticrypt compatibility:** Staticrypt decrypts the page in-browser, then the Giscus script loads normally. This should work but needs testing — the script tag is inside the encrypted HTML, so it only executes after decryption.

### Alternatives

| Method | Pros | Cons |
|--------|------|------|
| **GitHub Issues on drafts repo** | Simple, no Discussions setup | Not tied to specific posts |
| **Email link in draft banner** | Works for anyone, zero setup | Unstructured, hard to track |
| **Google Form** | Structured, no GitHub account | Another external service |

### Recommendation

Start with Giscus on the drafts repo. If reviewers don't have GitHub accounts, add a mailto link in the draft banner as a fallback.

---

## Gaps and Things to Think Through

### 1. Staticrypt + Internal Navigation

Staticrypt encrypts each HTML file individually. When a reviewer decrypts one page and clicks a link to another page, they hit **another password prompt** unless `--remember` is working.

- `--remember 30` stores the decryption key in `localStorage` — subsequent pages decrypt automatically
- If `localStorage` is blocked or cleared, every page click is a password prompt
- **Test this thoroughly** — the reviewer experience lives or dies on this

### 2. Non-HTML Assets Are Not Encrypted

Staticrypt only encrypts `.html` files. These are accessible without a password:
- Images (`/assets/images/`)
- PDFs (`/assets/pdfs/`)
- CSS, JS, fonts

This is fine given the public repo — the source is already visible. The workflow already removes `feed.xml` and `sitemap.xml` to prevent content leakage in structured formats.

### 3. GitHub Pages Deployment Method

The drafts repo needs Pages configured to "Deploy from a branch" → `main` → `/ (root)`. This is different from the production site which uses `actions/deploy-pages`. The force-push approach in the workflow is simpler.

### 4. Public vs Private Drafts Repo

- **Public**: GitHub Pages works on free tier. Content is Staticrypt-encrypted (if using Option 1). The repo is just a deployment target with no source code.
- **Private**: Requires GitHub Pro ($4/mo) for private repo Pages.

**Recommendation:** Public repo. The source markdown is already public in `mcgarrah.github.io`. Encrypting the rendered HTML in a private repo adds no real security.

### 5. Full Site Mirror vs Draft-Only

The build includes the **entire site** (139+ published posts plus drafts/future). This is probably what you want — reviewers see context for where a draft fits. Building only draft posts would require a custom Jekyll plugin and isn't worth the complexity.

### 6. Broken Absolute Links

Draft posts that hardcode `https://mcgarrah.org/some-post/` will link to production, not the drafts site. The `url` override in `_config_drafts.yml` handles `{{ site.url }}` Liquid references, but hardcoded URLs in markdown content won't be rewritten. Use relative links (`/some-post/`) in drafts.

### 7. Resume Sub-Site

The resume lives in a separate repo (`mcgarrah/resume`) and builds independently. It won't be included in the drafts build. Links to `/resume/` from the drafts site will 404 or redirect to production. This is fine — reviewers don't need the resume.

### 8. Build Frequency

Two Jekyll builds per push to `main` (production + drafts). Both run in a public repo → unlimited GitHub Actions minutes. Build time ≈ 2-4 minutes for drafts (Jekyll + Staticrypt on ~140 posts). Not a concern.

---

## Eliminated Options

### Cloudflare Access

> **Status: Eliminated.** Requires Cloudflare as a new external dependency.

### Netlify with Password Protection

> **Status: Eliminated.** Requires a Netlify account as a new external dependency.

### Vercel with Password Protection

> **Status: Eliminated.** Requires Vercel Pro ($20/mo). Overkill.

### Self-Hosted on Proxmox / Kubernetes

> **Status: Not viable at this time.** Proxmox homelab not ready for external-facing services. K8s cluster (AlteredCarbon) still in build-out. Revisit after K8s has ingress-nginx + cert-manager serving external sites.

### Separate Branch in Same Repo

> **Status: Not viable.** GitHub Pages deploys one branch to one domain per repo.

---

## Open Questions

1. **Subdomain vs project page** — Subdomain (`drafts.mcgarrah.org`) recommended for clean `robots.txt` separation. Project page (`mcgarrah.org/drafts/`) avoids DNS changes but shares `robots.txt` with production.
2. **Staticrypt yes/no** — Recommended as a low-cost speed bump. Can be removed anytime. Given the public repo, it's a UX signal not real security.
3. **Update frequency** — Rebuild on every push to `main`, or only on-demand (`workflow_dispatch`)? Both supported.
4. **Feedback mechanism** — Giscus on drafts repo recommended. See Feedback section above.
5. **Drafts repo visibility** — Public (free) recommended. See Gap #4.
6. **Multiple reviewers** — Shared password works for 2-10 trusted people.

---

## What NOT to Do

- **Don't add `--drafts --future` to the production build** — defeats the entire purpose
- **Don't use `published: false` as a gating mechanism** — `_drafts/` is the correct approach
- **Don't rely solely on `robots.txt`** — it's advisory, not enforced
- **Don't put passwords in the repo** — use GitHub Secrets
- **Don't modify the main site's `_config.yml`** — use a config overlay file
- **Don't create a subdirectory on the main site** (e.g., `/drafts/` path in the main repo) — no way to password-protect a path on GitHub Pages, and it pollutes the production build

---

## Decisions Made

- **Subdomain** (`drafts.mcgarrah.org`) — chosen over project page for clean `robots.txt` separation
- **Staticrypt** — yes, as a low-cost UX speed bump; removable anytime
- **Giscus on drafts repo** — keeps feedback separate from production comments
- **Public drafts repo** — free GitHub Pages, no real security benefit from private given public source
- **Build on every push** — both triggers (push to `main` + `workflow_dispatch`) enabled

## Challenges Encountered During Implementation

- **Empty-repo Pages trap**: GitHub Pages could not be enabled until the drafts repo had a real `main` branch with an initial commit.
- **Giscus setup friction**: repository/category readiness and app criteria caused setup delays before IDs could be captured.
- **Staticrypt runtime looked stalled**: encrypting hundreds of generated HTML pages made the workflow appear hung for long stretches.
- **No-password deploy after first successful run**: workflow success did not guarantee in-place encrypted output was being deployed.
- **Large binary artifacts in output**: deployment surfaced GitHub warnings for oversized executables and reinforced pruning/LFS boundaries.
- **Selective encryption became necessary**: only draft and future article pages needed protection; encrypting the full site added avoidable churn.
- **Verification false negatives**: content-string checks failed even when files were transformed, requiring a more reliable verification method.
- **Staticrypt `-o` flag doesn't exist**: version 3.5.4+ uses `-d <directory>` for output; the invalid `-o` flag caused silent failures with no error message, making encrypted output appear but silently fail to write.

## Implementation Checklist

Organized by where the work happens. Each step is independent enough to do in a spare 5-15 minutes.

### Phase 1: GitHub Setup (browser, ~15 minutes total)

- [x] **1.1** Create `mcgarrah/drafts.mcgarrah.org` repo on GitHub (public, initialized so `main` exists)
- [x] **1.2** Enable GitHub Pages on the drafts repo (Settings → Pages → Deploy from branch → `main` → `/ (root)`)
- [x] **1.3** Enable GitHub Discussions on the drafts repo (Settings → General → Features → Discussions)
- [ ] **1.4** Create a "Draft Reviews" category in Discussions (Discussions tab → Categories → New category)
- [ ] **1.5** Generate a GitHub PAT with `repo` scope for cross-repo push (Settings → Developer settings → Personal access tokens → Fine-grained tokens, scope to `drafts.mcgarrah.org` repo only)
- [x] **1.6** Add `DRAFTS_DEPLOY_TOKEN` secret to `mcgarrah.github.io` repo (Settings → Secrets and variables → Actions → New repository secret)
- [x] **1.7** Pick a Staticrypt password and add `DRAFTS_PASSWORD` secret to `mcgarrah.github.io` repo

**Important gotcha:** GitHub Pages cannot be configured for `main` until the repo has an initial commit and the `main` branch actually exists. Creating the repo as truly empty blocks Pages setup with an error. Initializing with a `README.md` (or creating any file and committing it) avoids that.

### Phase 2: DNS (Porkbun, ~2 minutes)

- [ ] **2.1** Add CNAME record in Porkbun: `drafts` → `mcgarrah.github.io.`
- [ ] **2.2** Wait for DNS propagation (usually < 5 minutes, can verify with `dig drafts.mcgarrah.org`)
- [ ] **2.3** After first deployment, enable "Enforce HTTPS" in the drafts repo's Pages settings

### Phase 3: Giscus Configuration (browser, ~5 minutes)

- [ ] **3.1** Go to https://giscus.app
- [ ] **3.2** Enter `mcgarrah/drafts.mcgarrah.org` as the repo
- [ ] **3.3** Select "Draft Reviews" as the Discussion category
- [ ] **3.4** Copy the `data-repo-id` and `data-category-id` values
- [ ] **3.5** Save these values — needed for `_config_drafts.yml` in Phase 4

### Phase 4: Main Repo Files (IDE, ~20 minutes total)

- [x] **4.1** Create `_config_drafts.yml` in the main repo root with drafts URL, disabled analytics/ads, and Giscus config pointing to drafts repo (use IDs from Phase 3)
- [x] **4.2** Create `.github/workflows/deploy-drafts.yml` in the main repo (workflow sketch is in this document and Part 2)
- [ ] **4.3** Add the draft preview banner to `_layouts/default.html` (Liquid conditional on `site.url contains 'drafts'`)
- [ ] **4.4** Commit and push to `main`

### Phase 5: Testing (~30 minutes)

- [ ] **5.1** Verify the `deploy-drafts.yml` workflow runs successfully in GitHub Actions
- [ ] **5.2** Verify `drafts.mcgarrah.org` loads and shows the Staticrypt password prompt
- [ ] **5.3** Enter the password — verify the site renders correctly with drafts and future posts visible
- [ ] **5.4** Click through 3-4 internal links — verify `--remember` works (no re-prompting)
- [ ] **5.5** Verify the orange "DRAFT PREVIEW" banner appears at the top
- [ ] **5.6** Verify `robots.txt` at `drafts.mcgarrah.org/robots.txt` shows `Disallow: /`
- [ ] **5.7** Verify `feed.xml` and `sitemap.xml` return 404
- [ ] **5.8** Verify Google Analytics is NOT loading (check browser DevTools → Network)
- [ ] **5.9** Scroll to bottom of a post — verify Giscus loads and points to the drafts repo Discussions
- [ ] **5.10** Leave a test comment via Giscus — verify it appears in the drafts repo's Discussions
- [ ] **5.11** Test on mobile (Staticrypt prompt, navigation, banner)
- [ ] **5.12** Test in a private/incognito window (should prompt for password again)

### Phase 6: Write Part 3 Article

- [ ] **6.1** Fill in Part 3 (`_drafts/2026-06-19-jekyll-draft-preview-site-part-3.md`) with real results from testing
- [ ] **6.2** Document anything that didn't work as expected and workarounds applied
- [ ] **6.3** Add screenshots of the password prompt, draft banner, and Giscus comments
- [ ] **6.4** Update `SUBDOMAIN-DRAFTS.md` with any changes discovered during implementation

### Phase 7: Share with Reviewers

- [ ] **7.1** Send the URL (`drafts.mcgarrah.org`) and password to reviewers
- [ ] **7.2** Explain that Giscus comments require a GitHub account
- [ ] **7.3** Provide a fallback contact method (email) for reviewers without GitHub accounts
- [ ] **7.4** Promote the three-part blog series to `_posts/` when ready

## Quick Reference: What Goes Where

| File | Repo | Purpose |
|------|------|---------|
| `_config_drafts.yml` | `mcgarrah.github.io` | Jekyll config overlay for drafts build |
| `.github/workflows/deploy-drafts.yml` | `mcgarrah.github.io` | GitHub Actions workflow |
| `CNAME` | `drafts.mcgarrah.org` (auto-created by workflow) | GitHub Pages custom domain routing |
| `DRAFTS_PASSWORD` secret | `mcgarrah.github.io` | Staticrypt shared password |
| `DRAFTS_DEPLOY_TOKEN` secret | `mcgarrah.github.io` | GitHub PAT for cross-repo push |
| Draft preview banner | `mcgarrah.github.io` `_layouts/default.html` | Visual indicator for reviewers |
| Giscus config | `_config_drafts.yml` | Points comments to drafts repo Discussions |
