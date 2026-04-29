---
title: "Run Jekyll: New Features — Clean, Doctor, and Real Tests"
layout: post
categories: [web-development, technical]
tags: [vscode, vscode-extension, typescript, jekyll, open-source, testing]
excerpt: "The Run Jekyll VS Code extension has five commands: Run, Build, Stop, Restart, and Open. After living with it daily, I know exactly what's missing — a Clean command for when stale caches hide new drafts, a Doctor command for quick diagnostics, and actual tests so I can ship these features without breaking what already works."
description: "Proposed new features for the Run Jekyll VS Code extension: Jekyll Clean command with two-mode behavior (standalone and clean-restart), Jekyll Doctor diagnostic command, and an automated test suite replacing the placeholder test. Includes implementation plans, keybindings, and testing strategy."
date: 2026-06-29
last_modified_at: 2026-06-29
seo:
  type: BlogPosting
  date_published: 2026-06-29
  date_modified: 2026-06-29
---

In the previous posts in this series, I've been [fixing bugs](/run-jekyll-bug-fixes-and-code-review/), [modernizing CI/CD](/forking-jekyll-run-to-run-jekyll/), and [building a test harness](/run-jekyll-testing-and-test-harness/) for the Run Jekyll VS Code extension. Now it's time to add features.

The extension currently has five commands: Run, Build, Stop, Restart, and Open in Browser. After using it daily on my [Jekyll blog](https://mcgarrah.org), I've hit the same friction points enough times to know exactly what's missing. The prioritization follows the same framework I'd apply to any product backlog: Clean and Doctor address the most common daily friction points, and tests are the prerequisite for shipping anything safely.

<!-- excerpt-end -->

This is part of an ongoing series on the Run Jekyll VS Code extension:
- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/)
- [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/)
- [Forking Jekyll Run to Run Jekyll](/forking-jekyll-run-to-run-jekyll/)
- [VS Code Marketplace Publisher Account Setup](/run-jekyll-vscode-marketplace-publisher-setup/)
- [Run Jekyll: Bug Fixes and Code Review](/run-jekyll-bug-fixes-and-code-review/)
- [Run Jekyll: Testing and Test Harness](/run-jekyll-testing-and-test-harness/)
- **Run Jekyll: New Features — Clean, Doctor, and Real Tests** (this post)

## The Problem That Started This

I added three new draft posts to my `_drafts/` folder, restarted Jekyll via the extension (Cmd+F7), and... nothing. The new drafts didn't appear. The site looked exactly the same as before.

The culprit: `--incremental`. Jekyll's incremental build flag is great for speed — it only rebuilds changed pages. But it tracks what it knows about in `.jekyll-metadata`, and new files added after the server started aren't in that index. Even without `--incremental`, stale data in `.jekyll-cache/` can cause similar issues.

The fix is `bundle exec jekyll clean`, which removes `_site/`, `.jekyll-cache/`, and `.jekyll-metadata`. But that means stopping the server, opening a terminal, running the command, and restarting. That should be one button click.

## Feature 1: Jekyll Clean

### Two Modes, One Command

The Clean command needs to work in two contexts:

**When the server is stopped:** Run `bundle exec jekyll clean` standalone, just like Build works today. Clear the caches and you're done.

**When the server is running:** Stop the server, clean the caches, and restart — a "clean restart" that feels like a single operation. This is the common case: you're serving locally, add new files, and need a fresh build.

| Context | Keybinding | What Happens |
|---------|-----------|-------------|
| Server stopped | `Cmd+F10` | Cleans cache |
| Server running | `Cmd+F10` | Stops → cleans → restarts |

The `when` clause in `package.json` is `jekyll-run&&!isBuilding` — no `!isRunning` check because the command handles both states internally.

### Implementation

<!-- TODO: Implement clean.ts, register in extension.ts, add to package.json -->
<!-- TODO: Test the stop → clean → restart sequence — verify status bar updates correctly -->
<!-- TODO: Test that new drafts appear after clean restart -->

The implementation follows the same pattern as `build.ts` — spawn `bundle exec jekyll clean` with a progress notification. The running-state handler chains Stop → Clean → Run as sequential async operations.

The full implementation plan with code is in [FEATURE.md](https://github.com/mcgarrah/jekyll-run/blob/main/FEATURE.md) in the repository.

## Feature 2: Jekyll Doctor

Jekyll has a built-in diagnostic command: `bundle exec jekyll doctor` (aliased as `hyde`). It checks for deprecation warnings, config issues, and URL conflicts. On my site it flags all the future-dated posts — useful confirmation that Jekyll sees them correctly.

### Safe to Run Anytime

Unlike Clean, Doctor is read-only. It doesn't modify the site, doesn't interfere with a running server, and doesn't touch the cache. So it's available in all states — running, stopped, building, whatever.

| Context | Keybinding | What Happens |
|---------|-----------|-------------|
| Any state | `Cmd+F11` | Runs diagnostics, shows output |

### The stderr Quirk

One implementation detail worth noting: `jekyll doctor` outputs its warnings to stderr, even when everything is fine. The existing pattern in the extension (from `build.ts`) treats stderr as an error and rejects the promise. Doctor's handler needs to display stderr in the output channel instead of rejecting — those warnings *are* the output.

<!-- TODO: Implement doctor.ts with stderr-as-output handling -->
<!-- TODO: Register in extension.ts, add to package.json -->
<!-- TODO: Test that Doctor runs without interfering with a running server -->
<!-- TODO: Test stderr warning display in output channel -->

The full implementation plan is in [FEATURE.md](https://github.com/mcgarrah/jekyll-run/blob/main/FEATURE.md).

## Feature 3: Real Tests

This isn't a user-facing feature, but it's the prerequisite for shipping the other two safely.

### The Current State

The extension has one test file with one test:

```typescript
test('Sample test', () => {
    assert.equal(-1, [1, 2, 3].indexOf(5));
    assert.equal(-1, [1, 2, 3].indexOf(0));
});
```

The test harness works — Mocha, @vscode/test-electron, Extension Development Host, cross-platform CI on macOS/Ubuntu/Windows. But it's exercising nothing. Every bug fix and feature is manually verified.

### The Plan

Seven test files, organized from easiest to hardest:

| File | Tests | Type |
|------|-------|------|
| `get-numbers-in-string.test.ts` | Number extraction edge cases | Unit |
| `process-on-port.test.ts` | lsof parsing (the bug I already fixed) | Unit |
| `pid-on-port.test.ts` | Windows netstat PID extraction | Unit |
| `error-handling.test.ts` | stderr rejection behavior | Unit (mocked spawn) |
| `clean.test.ts` | Clean command spawn and error handling | Unit (mocked spawn) |
| `doctor.test.ts` | Doctor stderr-as-output behavior | Unit (mocked spawn) |
| `config.test.ts` | getConfiguration scoping | Integration |

The first three are pure functions — input in, output out, no VS Code API needed. They cover the bugs already fixed in v1.7.1 and prevent regressions. The mocked-spawn tests verify command behavior without needing a real Jekyll installation. The integration test comes last because it needs the Extension Development Host and is inherently slower.

<!-- TODO: Implement unit tests for utility functions (process-on-port, get-numbers-in-string, pid-on-port) -->
<!-- TODO: Implement mocked-spawn tests for error handling, clean, doctor -->
<!-- TODO: Implement integration test for getConfiguration scoping -->
<!-- TODO: Verify CI passes on all three platforms -->

### Success Criteria

- All 3 fixed bugs (v1.7.1) have regression tests
- All utility functions have edge-case coverage
- New features (Clean, Doctor) have tests before merge
- CI runs tests on all 3 platforms
- No test depends on a real Jekyll installation

The detailed test plan with code examples is in [FEATURE.md](https://github.com/mcgarrah/jekyll-run/blob/main/FEATURE.md) and the [testing article](/run-jekyll-testing-and-test-harness/) covers the harness setup.

## Command Summary After These Features

| Command | Keybinding | When Available | Status |
|---------|-----------|---------------|--------|
| Jekyll Run | `Cmd+F5` | Server stopped | Existing |
| Jekyll Stop | `Cmd+F6` | Server running | Existing |
| Jekyll Restart | `Cmd+F7` | Server running | Existing |
| Jekyll Build | `Cmd+F8` | Server stopped | Existing |
| Jekyll Open in Browser | `Cmd+F9` | Server running | Existing |
| **Jekyll Clean** | **`Cmd+F10`** | **Any (not building)** | **Planned** |
| **Jekyll Doctor** | **`Cmd+F11`** | **Any** | **Planned** |

The keybindings follow the existing F5-F9 pattern, extending to F10 and F11.

## What's Next

<!-- TODO: Implement the features, write tests, update this article with results -->
<!-- TODO: Add screenshots of the Clean and Doctor commands in action -->
<!-- TODO: Document any implementation surprises or design changes -->

The implementation order is: tests first (so I can verify the new features work), then Clean (highest user impact), then Doctor (nice to have). Each feature gets committed with its tests in the same PR.

All three features are `main`-branch-only — they're new functionality for the Run Jekyll fork, not bug fixes that should go upstream to the abandoned original repo.

---

*This is part of an ongoing series on forking and improving the Jekyll Run VS Code extension. The extension source is at [github.com/mcgarrah/jekyll-run](https://github.com/mcgarrah/jekyll-run).*
