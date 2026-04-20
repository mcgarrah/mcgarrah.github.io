# From Bug Fix to VS Code Marketplace: Reviving an Abandoned Extension

**Subtitle:** How a TypeError in a multi-root workspace led to forking, fixing, testing, and publishing a VS Code extension

**Author:** McGarrah

**Planned:** June 15, 2026 (Monday)

**URL:** TBD

**Tags:** Open Source, VS Code, Software Engineering, TypeScript, CI/CD, Developer Tools

---

My third newsletter covered [when storage breaks](https://mcgarrah.substack.com/p/when-storage-breaks). This one covers a different kind of recovery — taking an abandoned open-source project, diagnosing its failures, and shipping a fixed version to the world.

It started with a crash. The Jekyll Run VS Code extension — the only plugin that lets you build and serve a Jekyll site from inside VS Code — threw a `TypeError: Cannot read properties of null` every time I opened my multi-root workspace. The original author hadn't committed since 2020. No one was coming to fix this.

So I fixed it myself. Then I fixed 17 more bugs. Then I modernized the CI/CD. Then I published it.

*Thanks for reading! Subscribe for free to receive new posts and support my work.*

## The Crash That Started Everything

The error message was misleading. "Cannot read properties of null (reading 'toString')" pointed at the error handler, not the actual bug. The real problem was buried two layers deep: VS Code's `getConfiguration()` API returns `null` in multi-root workspaces when called without a scope parameter. The extension's config reader had never been tested in that context.

- [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](https://mcgarrah.org/jekyll-run-plugin-multiroot-workspace-bug/) — The full debugging story. Blind alleys through VS Code settings, the misleading TypeError, and the real root cause: macOS GUI apps don't inherit shell PATH, so the plugin was running system Ruby 2.6 instead of rbenv Ruby 3.3.

But fixing one bug revealed the codebase was full of them. The `lsof` parser broke on macOS because it split on single spaces instead of whitespace. The stderr handler could reject a promise with `null`. The `stopServerOnExit` setting was declared as a string `"false"` instead of boolean `false` — meaning it was always truthy and the setting had never worked for any user since v1.7.0.

## The Fork Decision

The original repo (Kanna727/jekyll-run) has 30K+ installs on the VS Code Marketplace. The author is gone. Do you submit a PR to a dead repo and hope? Or do you fork, fix, and ship?

I did both. Bug fixes go to an `upstream-pr` branch that's PR-compatible with the original. Everything else — the rename, the tests, the new features — goes to `main` and will be published as "Run Jekyll" on the Marketplace.

- [Forking Jekyll Run to Run Jekyll](https://mcgarrah.org/forking-jekyll-run-to-run-jekyll/) — The fork rationale, CI/CD modernization (Node 12→20, Actions v4, cross-platform testing), and the branch strategy that lets me give back upstream while diverging with my own vision.

- [Run Jekyll: VS Code Marketplace Publisher Setup](https://mcgarrah.org/run-jekyll-vscode-marketplace-publisher-setup/) — The surprisingly bureaucratic process of creating a VS Code Marketplace publisher account. Azure DevOps PATs, publisher verification, and the workflow that publishes automatically on GitHub Release.

## The Deep Code Review

With the fork established, I did a systematic code review of the entire extension. 18 issues total — 3 already fixed in v1.7.1, 15 remaining. Crashes, silent failures, dead code, and a runtime dependency that exists solely for a VS Code version check that hasn't been relevant since 2019.

- [Run Jekyll: Bug Fixes and Code Review](https://mcgarrah.org/run-jekyll-bug-fixes-and-code-review/) — All 18 issues documented with root cause analysis, severity, and fix approach. The double-rejection bug in the stderr handler. The Buffer-to-string conversion that produces `[object Object]`. The `deactivate()` function with no error handling during workspace teardown.

## Testing What Was Never Tested

The original extension had exactly one test: `assert.equal([1,2,3].indexOf(5), -1)`. A placeholder that tests nothing about the extension. The test harness worked — Mocha, VS Code Extension Development Host, the whole infrastructure was there — but no one had written real tests.

- [Run Jekyll: Testing and Test Harness](https://mcgarrah.org/run-jekyll-testing-and-test-harness/) — Setting up regression tests for the three bugs fixed in v1.7.1. The lsof parser with variable-width columns. The null rejection on non-Errno errors. The getConfiguration scoping in multi-root workspaces. Plus the test infrastructure decisions: what needs the Extension Development Host vs what can run as pure unit tests.

## New Features

With the bugs fixed and tests in place, I added two new commands that Jekyll developers actually need: `jekyll clean` (clear the cache when things get weird) and `jekyll doctor` (run diagnostics without changing anything).

- [Run Jekyll: New Features — Clean, Doctor, and Tests](https://mcgarrah.org/run-jekyll-new-features-clean-doctor-tests/) — Feature specs, implementation, keybindings, and the state machine logic for Clean (stop → clean → restart if was running).

## The Open Source Pattern

This whole project follows a pattern I've seen repeatedly in open source:

1. **Find broken software** that solves a real problem
2. **Fix it for yourself** (the minimum viable contribution)
3. **Give back upstream** (PR with just the fixes)
4. **Diverge when needed** (fork for larger vision)
5. **Ship it** (Marketplace, documentation, tests)

The extension went from "crashes on launch" to "18 bugs documented, 3 fixed, CI/CD modernized, cross-platform tested, VSIX published" in about two weeks of evening work. That's the power of focused open-source contribution — you don't need to rewrite everything, just fix what's broken and ship.

## What's Next

- Publishing "Run Jekyll" to the VS Code Marketplace as a separate extension
- Fixing the remaining 15 bugs from the code review
- Submitting the upstream PR to the original repo (goodwill gesture)
- Potentially: LSP integration for Jekyll-specific Liquid template support

## About Me

I'm Michael McGarrah — a cloud architect and data scientist with 25+ years in enterprise infrastructure. I hold an M.S. in Computer Science (AI/ML) from Georgia Tech, a B.S. in Computer Science from NC State, and I'm currently pursuing an Executive MBA at UNC Wilmington.

You can find more of my writing at [mcgarrah.org](https://mcgarrah.org), my detailed resume at [mcgarrah.org/resume](https://mcgarrah.org/resume), and my profiles on [LinkedIn](https://www.linkedin.com/in/michaelmcgarrah/), [GitHub](https://github.com/mcgarrah), and [Google Scholar](https://scholar.google.com/citations?user=Lt7T2SwAAAAJ).
