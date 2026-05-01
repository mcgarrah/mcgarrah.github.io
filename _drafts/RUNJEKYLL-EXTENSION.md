---
layout: none
date: 1999-12-31
sitemap: false
---

# Run Jekyll VS Code Extension — Project Tracker

Fork and overhaul of the abandoned [Jekyll Run](https://github.com/Kanna727/jekyll-run) VS Code extension.

Last updated: 2026-06-29

---

## Repositories

| Repo | Purpose |
|------|---------|
| [mcgarrah/jekyll-run](https://github.com/mcgarrah/jekyll-run) | Fork (origin) |
| [Kanna727/jekyll-run](https://github.com/Kanna727/jekyll-run) | Original (upstream) |

## Branch Strategy

| Branch | Purpose | Extension name | PR-able to upstream? |
|--------|---------|---------------|---------------------|
| `upstream-pr` | Bug fixes only, compatible with original repo | Jekyll Run | Yes |
| `main` | Full overhaul — rename, tests, all fixes, Marketplace publish | Run Jekyll | No |

- Bug fixes that should go upstream: commit on `upstream-pr` first, cherry-pick to `main`
- Everything else (rename, tests, new features): commit directly on `main`
- **Never merge `main` into `upstream-pr`** — the rename makes it un-PR-able

### Execution Model (Deep Review Update)

- **Track A: `upstream-pr` (critical-only stabilization)**
  - Goal: small, low-risk bug fixes that are easy to review and accept upstream
  - Include: crash/silent-failure fixes, deterministic error handling, and minimal CI/workflow modernization needed to validate fixes
  - Exclude: rename/rebrand, large refactors, new commands/features, behavior changes beyond bug scope
- **Track B: `main` (major improvements)**
  - Goal: full overhaul (new features, deeper refactors, tests, Marketplace/publisher work)
  - Can include dependency upgrades and broader CI/CD enhancements not appropriate for upstream PR scope

---

## Deep Review Findings (2026-04-20)

Additional findings from deep code review and local build/test validation in `mcgarrah/jekyll-run`.

### Critical (upstream-pr candidates)

- [ ] **Dependency detection can misreport tools as installed**
  - `!(await lookpath(...))?.startsWith(...)` can pass when value is undefined, allowing run/build flow to proceed with missing dependencies
  - Files: `src/extension.ts` (run/build command checks)
- [ ] **Restart race condition (stop not awaited before run)**
  - Restart path calls stop and immediately starts new server, causing flaky port conflicts
  - File: `src/extension.ts`
- [ ] **Promise multi-settle and inconsistent rejection payloads in run/build/install**
  - `stderr` can reject while `close` still resolves, and rejection types vary (Buffer/string/regex array/undefined)
  - Files: `src/cmds/run.ts`, `src/cmds/build.ts`, `src/cmds/install.ts`
- [ ] **Existing-server open flow can use stale/undefined URL**
  - `openUrl(address)` may run before address is reliably initialized in already-running-server path
  - File: `src/extension.ts`
- [ ] **Unprotected `_config.yml` parse path can crash flow**
  - sync YAML parse has no guard for malformed config
  - File: `src/extension.ts`

### High/Medium (main branch first unless kept very small)

- [ ] Open command registration not added to disposables (`open` not pushed to `context.subscriptions`)
- [ ] `stopServerOnExit` default type mismatch (`"false"` string vs boolean)
- [ ] Unix kill path not awaited (`kill -9` fire-and-forget)
- [ ] lsof parser still assumes a data line exists (header-only output crash risk)
- [ ] whitespace parsing helpers are brittle (`split(' ')`, undefined-first-element assumptions)

### Testing Reality Check

- [ ] Build/compile passes and extension test harness runs, but test coverage is still effectively placeholder-level (`extension.test.ts` sample test only)
- [ ] Critical paths above are not protected by focused unit tests yet (error handling, process parsing, restart flow)

---

## Open Questions (from Deep Review)

- [ ] Should command-line argument parsing support quoted/escaped arguments, or keep current simple split behavior with documented limitations?
- [ ] In already-running-server detection, should URL always be derived from configured port/baseurl instead of reused runtime address state?
- [ ] For upstream PR acceptance, should CI/workflow updates be bundled with bug fixes in one PR or split into two small PRs?

## Current State

- **v1.7.1 released** — 3 critical bugs fixed, CI/CD modernized, VSIX on GitHub Release
- **`upstream-pr` branch created** — ready for PR to upstream, not yet submitted
- **`.amazonq/rules/` added** — full project context for future sessions
- **6 blog drafts written** — all marked complete, not yet promoted

## What's Done

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

## Phase 1 — Submit Upstream PR

- [ ] Open PR from `mcgarrah/jekyll-run:upstream-pr` → `Kanna727/jekyll-run:master`
  - Include only critical stabilization fixes and minimal CI/workflow updates needed to validate those fixes
  - Keep PR narrowly scoped and easy to review/merge
  - This is the goodwill gesture before diverging with rename/new features on `main`

### Phase 1 Candidate Scope (Critical Only)

- [ ] Fix dependency detection guard logic in run/build command prechecks
- [ ] Await stop in restart flow before launching new run
- [ ] Normalize run/build/install promise behavior to settle once with consistent `Error` objects
- [ ] Guard config parse path and report actionable errors
- [ ] Fix existing-server open URL derivation/initialization path

## Phase 2 — Fix Remaining 15 Bugs (on `main`)

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

## Phase 3 — Add Real Tests (on `main`)

Test code is written in the testing blog draft but not yet added to the repo.

- [ ] Add `src/test/suite/process-on-port.test.ts` — lsof parsing with variable-width columns
- [ ] Add `src/test/suite/error-handling.test.ts` — null rejection on non-Errno errors
- [ ] Add `src/test/suite/config.test.ts` — getConfiguration scoping (integration test)
- [ ] Add `src/test/suite/utils.test.ts` — getNumbersInString edge cases
- [ ] Remove or replace placeholder `extension.test.ts`

## Phase 4 — New Features (on `main`)

Documented in `FEATURE.md` in the jekyll-run repo and the new features blog draft.

- [ ] Jekyll Clean command (`jekyll-run.Clean` / `ctrl+f10`) — cleans cache, restarts if running
- [ ] Jekyll Doctor command (`jekyll-run.Doctor` / `ctrl+f11`) — read-only diagnostic
- [ ] Multi-workspace Jekyll site selection (see below)
- [ ] Tests for new commands

### Multi-Workspace Jekyll Site Selection

**Problem:** In a multi-root workspace with multiple Jekyll repos (e.g., `mcgarrah.github.io`
and `resume`), the extension always serves the first workspace folder. There is no way to
choose which Jekyll site to run.

The root cause is in `isStaticWebsiteWorkspace()` (`src/extension.ts:79-96`). When no editor
is active, it falls back to `workspace.workspaceFolders[0]`. When an editor *is* active, it
uses that file's workspace folder — but this is implicit and not obvious to the user.

**Desired behavior (evaluate these options):**

1. **Active workspace folder** — If a file from a Jekyll repo is open and focused in the
   editor, serve that repo. This partially works today but is not communicated to the user
   (no indicator of which site will be served).

2. **Quick pick prompt** — When multiple workspace folders contain `_config.yml`, show a
   VS Code QuickPick letting the user choose which site to serve. Could fire on Run if
   multiple Jekyll sites are detected.

3. **Configuration setting** — Add a `jekyll-run.workspaceFolder` setting that lets the
   user pin a specific workspace folder by name. Falls back to current behavior if unset.

4. **Status bar indicator** — Show which Jekyll site is currently targeted in the status
   bar (e.g., "Jekyll: mcgarrah.github.io"). Clicking it could open the QuickPick.

Option 2 + 4 combined is probably the best UX — prompt on ambiguity, show current selection.

**Branch:** `main` only (new feature, not upstream-compatible)

## Phase 5 — Rename to "Run Jekyll" (on `main`)

- [ ] `package.json` — `name`, `displayName`, `description`, `publisher`, `repository`, `bugs`
- [ ] `README.md` — title, description, credit original author, link upstream
- [ ] `CHANGELOG.md` — add v1.8.0 section documenting the fork
- [ ] `LICENSE` — add fork copyright line (keep original)
- [ ] `src/extension.ts` — output channel name, status bar text
- [ ] `.github/workflows/build-vsix.yml` — VSIX filename
- [ ] Decide on command IDs: keep `jekyll-run.*` for backward compat or rename to `run-jekyll.*`

## Phase 6 — Marketplace Publishing

- [ ] Create Microsoft account (or use existing)
- [ ] Create Azure DevOps Personal Access Token with "Marketplace: Manage" scope
- [ ] Create publisher at https://marketplace.visualstudio.com/manage
- [ ] Add PAT as `PUBLISHER_TOKEN` secret in GitHub repo settings
- [ ] Tag v1.8.0 release — CI publishes to Marketplace automatically

## Blog Articles

| # | Status | Date | File | Topic |
|---|--------|------|------|-------|
| 1 | ✅ Published | 2026-05-11 | `_posts/2026-05-11-jekyll-run-vscode-plugin-local-development.md` | Configuration guide |
| 2 | ✅ Published | 2026-06-05 | `_posts/2026-06-05-jekyll-run-plugin-multiroot-workspace-bug.md` | macOS debugging story |
| 3 | ✅ Published | 2026-06-10 | `_posts/2026-06-10-forking-jekyll-run-to-run-jekyll.md` | Fork rationale and CI/CD |
| 4 | ✅ Published | 2026-06-15 | `_posts/2026-06-15-run-jekyll-vscode-marketplace-publisher-setup.md` | Marketplace publisher setup |
| 5 | ✅ Published | 2026-06-19 | `_posts/2026-06-19-run-jekyll-bug-fixes-and-code-review.md` | 18 issues documented |
| 6 | ✅ Published | 2026-06-24 | `_posts/2026-06-24-run-jekyll-testing-and-test-harness.md` | Test harness and regression tests |
| 7 | ✅ Published | 2026-06-29 | `_posts/2026-06-29-run-jekyll-new-features-clean-doctor-tests.md` | New features: Clean, Doctor, tests |

All 7 articles published. Articles 2–7 promoted 2026-06-20, interleaved with Draft Preview Site series on MWF cadence, with one open insertion slot on June 22 for a non-Run-Jekyll subject (June 26 filled by Caddy/Ceph).

## Notes

- The 3 remaining npm vulnerabilities are transitive (in npm and mocha internals) — unfixable from our side
- `compare-versions` runtime dep can be removed entirely when the dead VS Code <1.31 check is removed (Phase 2, issue #10)
- `read-yaml` is the only real runtime dep — reads `_config.yml` for port/baseurl
- The `stopServerOnExit` bug (Phase 2, issue #12) has been silently broken since v1.7.0 — every user who set it to `false` has been ignored because `"false"` is a truthy string in JavaScript
