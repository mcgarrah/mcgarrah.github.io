---
layout: none
date: 2038-01-18
sitemap: false
---

# Drafts TODO — Project Tracker

Tracks projects that span code repositories, blog drafts, and external accounts.
Each project has its own section with status, next steps, and related artifacts.

Last updated: 2026-04-18

---

## 🔌 Run Jekyll VS Code Extension

Fork and overhaul of the abandoned [Jekyll Run](https://github.com/Kanna727/jekyll-run) VS Code extension.

### Repositories

| Repo | Purpose |
|------|---------|
| [mcgarrah/jekyll-run](https://github.com/mcgarrah/jekyll-run) | Fork (origin) |
| [Kanna727/jekyll-run](https://github.com/Kanna727/jekyll-run) | Original (upstream) |

### Branch Strategy

| Branch | Purpose | Extension name | PR-able to upstream? |
|--------|---------|---------------|---------------------|
| `upstream-pr` | Bug fixes only, compatible with original repo | Jekyll Run | Yes |
| `main` | Full overhaul — rename, tests, all fixes, Marketplace publish | Run Jekyll | No |

- Bug fixes that should go upstream: commit on `upstream-pr` first, cherry-pick to `main`
- Everything else (rename, tests, new features): commit directly on `main`
- **Never merge `main` into `upstream-pr`** — the rename makes it un-PR-able

### Current State

- **v1.7.1 released** — 3 critical bugs fixed, CI/CD modernized, VSIX on GitHub Release
- **`upstream-pr` branch created** — ready for PR to upstream, not yet submitted
- **`.amazonq/rules/` added** — full project context for future sessions
- **6 blog drafts written** — all marked complete, not yet promoted

### What's Done

- [x] Fix getConfiguration scoping for multi-root workspaces (`src/config/config.ts`)
- [x] Fix null rejection when Ruby errors don't contain Errno (`src/cmds/run.ts`)
- [x] Fix lsof parsing on macOS variable-width columns (`src/utils/process-on-port.ts`)
- [x] Modernize CI/CD (Actions v4, Node 20, cross-platform testing)
- [x] Update dependencies (42 → 3 vulnerabilities)
- [x] Create VSIX build workflow with GitHub Release artifacts
- [x] Create Marketplace publish workflow (graceful skip without token)
- [x] Tag and release v1.7.1
- [x] Create `upstream-pr` branch for PR-compatible changes
- [x] Add `.amazonq/rules/` project context

### Phase 1 — Submit Upstream PR

- [ ] Open PR from `mcgarrah/jekyll-run:upstream-pr` → `Kanna727/jekyll-run:master`
  - Include the 3 bug fixes and CI modernization
  - This is the goodwill gesture before diverging with the rename

### Phase 2 — Fix Remaining 15 Bugs (on `main`)

High priority (crashes or silent failures):

- [ ] Double rejection in stderr handler (`src/cmds/run.ts:65-74`) — use `else if`
- [ ] Raw Buffer passed to reject (`src/cmds/run.ts:68`, `src/cmds/build.ts:37`) — use `reject(error)`
- [ ] lsof crash on header-only output (`src/utils/process-on-port.ts:22`) — check line exists
- [ ] install.ts rejects with no error (`src/cmds/install.ts:31`) — pass `new Error(data.toString())`
- [ ] runBundleInstall not async-aware (`src/extension.ts:175-188`) — move cleanup to `.finally()`
- [ ] deactivate() has no error handling (`src/extension.ts:290`) — wrap in try-catch

Medium priority (robustness):

- [ ] exec-cmd.ts swallows all errors (`src/utils/exec-cmd.ts:6`) — return actual error message
- [ ] getNumbersInString splits on single space (`src/utils/get-numbers-in-string.ts:3`) — fix to `.split(/\s+/)`
- [ ] kill-process-children doesn't await kill (`src/utils/kill-process-children.ts:22`) — add `await`
- [ ] Dead code: VS Code < 1.31 check (`src/utils/open-in-browser.ts:4`) — remove check and `compare-versions` dep
- [ ] pid-on-port undefined array access (`src/utils/pid-on-port.ts:8`) — add fallback

Low priority (code quality):

- [ ] stopServerOnExit default is wrong type (`package.json`) — `"false"` string → `false` boolean
- [ ] Inline require (`src/extension.ts:62`) — move to top-level import
- [ ] Duplicate error handlers (`src/extension.ts`) — extract to shared function
- [ ] Commented-out code (`src/utils/process-on-port.ts`, `src/utils/open-in-browser.ts`) — remove
- [ ] `.eslintrc.json` has duplicate `semi` rule — remove one

### Phase 3 — Add Real Tests (on `main`)

Test code is written in the testing blog draft but not yet added to the repo.

- [ ] Add `src/test/suite/process-on-port.test.ts` — lsof parsing with variable-width columns
- [ ] Add `src/test/suite/error-handling.test.ts` — null rejection on non-Errno errors
- [ ] Add `src/test/suite/config.test.ts` — getConfiguration scoping (integration test)
- [ ] Add `src/test/suite/utils.test.ts` — getNumbersInString edge cases
- [ ] Remove or replace placeholder `extension.test.ts`

### Phase 4 — New Features (on `main`)

Documented in `FEATURE.md` in the jekyll-run repo and the new features blog draft.

- [ ] Jekyll Clean command (`jekyll-run.Clean` / `ctrl+f10`) — cleans cache, restarts if running
- [ ] Jekyll Doctor command (`jekyll-run.Doctor` / `ctrl+f11`) — read-only diagnostic
- [ ] Tests for new commands

### Phase 5 — Rename to "Run Jekyll" (on `main`)

- [ ] `package.json` — `name`, `displayName`, `description`, `publisher`, `repository`, `bugs`
- [ ] `README.md` — title, description, credit original author, link upstream
- [ ] `CHANGELOG.md` — add v1.8.0 section documenting the fork
- [ ] `LICENSE` — add fork copyright line (keep original)
- [ ] `src/extension.ts` — output channel name, status bar text
- [ ] `.github/workflows/build-vsix.yml` — VSIX filename
- [ ] Decide on command IDs: keep `jekyll-run.*` for backward compat or rename to `run-jekyll.*`

### Phase 6 — Marketplace Publishing

- [ ] Create Microsoft account (or use existing)
- [ ] Create Azure DevOps Personal Access Token with "Marketplace: Manage" scope
- [ ] Create publisher at https://marketplace.visualstudio.com/manage
- [ ] Add PAT as `PUBLISHER_TOKEN` secret in GitHub repo settings
- [ ] Tag v1.8.0 release — CI publishes to Marketplace automatically

### Blog Articles

| # | Status | Date | File | Topic |
|---|--------|------|------|-------|
| 1 | ✅ Published | 2026-05-11 | `_posts/2026-05-11-jekyll-run-vscode-plugin-local-development.md` | Configuration guide |
| 2 | 📝 Draft | 2026-05-22 | `_drafts/2026-05-22-jekyll-run-plugin-multiroot-workspace-bug.md` | macOS debugging story |
| 3 | 📝 Draft | 2026-05-25 | `_drafts/2026-05-25-forking-jekyll-run-to-run-jekyll.md` | Fork rationale and CI/CD |
| 4 | 📝 Draft | 2026-05-28 | `_drafts/2026-05-28-run-jekyll-vscode-marketplace-publisher-setup.md` | Marketplace publisher setup |
| 5 | 📝 Draft | 2026-05-29 | `_drafts/2026-05-29-run-jekyll-bug-fixes-and-code-review.md` | 18 issues documented |
| 6 | 📝 Draft | 2026-06-01 | `_drafts/2026-06-01-run-jekyll-testing-and-test-harness.md` | Test harness and regression tests |
| 7 | 📝 Draft | 2026-06-04 | `_drafts/2026-06-04-run-jekyll-new-features-clean-doctor-tests.md` | New features: Clean, Doctor, tests |

Publish order: 2 → 3 → 4 → 5 → 6 → 7 (follows the narrative arc)

All 6 drafts are marked `published: true` and content-complete — ready to promote to `_posts/` on MWF cadence using `git mv`. Remove `published: true` from front matter during promotion (the `_drafts/` directory is sufficient).

### Notes

- The 3 remaining npm vulnerabilities are transitive (in npm and mocha internals) — unfixable from our side
- `compare-versions` runtime dep can be removed entirely when the dead VS Code <1.31 check is removed (Phase 2, issue #10)
- `read-yaml` is the only real runtime dep — reads `_config.yml` for port/baseurl
- The `stopServerOnExit` bug (Phase 2, issue #12) has been silently broken since v1.7.0 — every user who set it to `false` has been ignored because `"false"` is a truthy string in JavaScript

---

## 🔒 Drafts Preview Site (drafts.mcgarrah.org)

Password-protected preview site that builds with `--drafts --future` flags, allowing vetted reviewers to see unpublished content and provide feedback via Giscus before public release.

### Design Documents

| File | Purpose |
|------|---------|
| `_drafts/SUBDOMAIN-DRAFTS.md` | Full analysis, architecture, implementation checklist |
| `jekyll-run/FEATURE.md` | Jekyll Clean command (triggered by this project's cache issues) |

### Architecture

```
mcgarrah.github.io (push to main)
  ├─ jekyll.yml → builds production → mcgarrah.org
  └─ deploy-drafts.yml → builds with --drafts --future
       ├─ Applies _config_drafts.yml overlay
       ├─ Encrypts HTML with Staticrypt
       ├─ Removes feed.xml, sitemap.xml
       ├─ Replaces robots.txt with Disallow: /
       └─ Pushes _site/ → drafts.mcgarrah.org repo → GitHub Pages
```

### Decisions Made

- **Subdomain** (`drafts.mcgarrah.org`) over project page — clean `robots.txt` separation
- **Staticrypt** — UX speed bump, not real security (source repo is public)
- **Giscus on drafts repo** — feedback separate from production comments
- **Public drafts repo** — free GitHub Pages, no benefit from private
- **Build on every push** to `main` + `workflow_dispatch` for on-demand

### Phase 1: GitHub Setup (~15 minutes, browser)

- [ ] Create `mcgarrah/drafts.mcgarrah.org` repo on GitHub (public, empty, no README)
- [ ] Enable GitHub Pages (Settings → Pages → Deploy from branch → `main` → root)
- [ ] Enable GitHub Discussions (Settings → General → Features → Discussions)
- [ ] Create "Draft Reviews" category in Discussions
- [ ] Generate GitHub PAT with `repo` scope (fine-grained, scoped to `drafts.mcgarrah.org` only)
- [ ] Add `DRAFTS_DEPLOY_TOKEN` secret to `mcgarrah.github.io` repo
- [ ] Pick Staticrypt password, add `DRAFTS_PASSWORD` secret to `mcgarrah.github.io` repo

### Phase 2: DNS (~2 minutes, Porkbun)

- [ ] Add CNAME record: `drafts` → `mcgarrah.github.io.`
- [ ] Verify propagation: `dig drafts.mcgarrah.org`
- [ ] After first deployment, enable "Enforce HTTPS" in drafts repo Pages settings

### Phase 3: Giscus Configuration (~5 minutes, browser)

- [ ] Configure at https://giscus.app with `mcgarrah/drafts.mcgarrah.org` repo
- [ ] Select "Draft Reviews" category
- [ ] Copy `data-repo-id` and `data-category-id` values for `_config_drafts.yml`

### Phase 4: Main Repo Files (~20 minutes, IDE)

- [ ] Create `_config_drafts.yml` (URL override, disable analytics/ads, Giscus config for drafts repo)
- [ ] Create `.github/workflows/deploy-drafts.yml` (build + Staticrypt + push to drafts repo)
- [ ] Add draft preview banner to `_layouts/default.html` (Liquid conditional on `site.url contains 'drafts'`)
- [ ] Commit and push to `main`

### Phase 5: Testing (~30 minutes)

- [ ] Verify `deploy-drafts.yml` workflow runs successfully in GitHub Actions
- [ ] Verify `drafts.mcgarrah.org` shows Staticrypt password prompt
- [ ] Enter password — verify site renders with drafts and future posts
- [ ] Click through 3-4 internal links — verify `--remember` works (no re-prompting)
- [ ] Verify orange "DRAFT PREVIEW" banner appears
- [ ] Verify `robots.txt` shows `Disallow: /`
- [ ] Verify `feed.xml` and `sitemap.xml` return 404
- [ ] Verify Google Analytics is NOT loading (DevTools → Network)
- [ ] Verify Giscus loads and points to drafts repo Discussions
- [ ] Leave a test comment — verify it appears in drafts repo Discussions
- [ ] Test on mobile (Staticrypt prompt, navigation, banner)
- [ ] Test in incognito window (should prompt for password again)

### Phase 6: Write Part 3 Article

- [ ] Fill in `_drafts/2026-06-19-jekyll-draft-preview-site-part-3.md` with real results
- [ ] Document anything that didn't work and workarounds applied
- [ ] Add screenshots of password prompt, draft banner, Giscus comments
- [ ] Update `SUBDOMAIN-DRAFTS.md` with any changes from implementation

### Phase 7: Share with Reviewers

- [ ] Send URL and password to reviewers
- [ ] Explain Giscus requires a GitHub account
- [ ] Provide email fallback for reviewers without GitHub accounts
- [ ] Promote the three-part blog series to `_posts/` when ready

### Blog Articles

| # | Status | Date | File | Topic |
|---|--------|------|------|-------|
| 1 | 📝 Draft | 2026-06-15 | `_drafts/2026-06-15-jekyll-draft-preview-site-part-1.md` | Options exploration |
| 2 | 📝 Draft | 2026-06-17 | `_drafts/2026-06-17-jekyll-draft-preview-site-part-2.md` | Refined design |
| 3 | 📝 Draft | 2026-06-19 | `_drafts/2026-06-19-jekyll-draft-preview-site-part-3.md` | Implementation (TODO — write after building) |

Parts 1 and 2 are content-complete. Part 3 is a placeholder with TODO sections — fill in after implementation.

Publish order: 1 → 2 → 3 on consecutive MWF slots.

### Quick Reference: What Goes Where

| File | Repo | Purpose |
|------|------|---------|
| `_config_drafts.yml` | `mcgarrah.github.io` | Jekyll config overlay |
| `.github/workflows/deploy-drafts.yml` | `mcgarrah.github.io` | GitHub Actions workflow |
| `CNAME` | `drafts.mcgarrah.org` (auto-created) | GitHub Pages routing |
| `DRAFTS_PASSWORD` secret | `mcgarrah.github.io` | Staticrypt password |
| `DRAFTS_DEPLOY_TOKEN` secret | `mcgarrah.github.io` | PAT for cross-repo push |
| Draft preview banner | `_layouts/default.html` | Visual indicator |
| Giscus config | `_config_drafts.yml` | Points to drafts repo Discussions |

---

<!-- Future projects go below this line -->
