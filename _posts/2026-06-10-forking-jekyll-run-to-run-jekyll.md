---
title: "Forking Jekyll Run: From Abandoned Plugin to Run Jekyll"
layout: post
categories: [web-development, technical]
tags: [jekyll, vscode, vscode-extension, open-source, github-actions, fork, publishing]
excerpt: "The Jekyll Run VS Code extension hasn't been updated in five years. After fixing three bugs and modernizing the CI/CD pipeline, I'm forking it as 'Run Jekyll' — a maintained version with cross-platform testing, automated releases, and a path to the VS Code Marketplace."
description: "How I forked the abandoned Jekyll Run VS Code extension, modernized its CI/CD infrastructure, and prepared it for independent publication as 'Run Jekyll'. Covers GitHub Actions upgrades, dependency updates, VSIX packaging, Marketplace publishing setup, and the etiquette of forking open source projects."
date: 2026-06-10
last_modified_at: 2026-06-10
seo:
  type: BlogPosting
  date_published: 2026-06-10
  date_modified: 2026-06-10
---

The [Jekyll Run VS Code extension](https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run) hasn't been updated since 2020. I [found three bugs](/jekyll-run-plugin-multiroot-workspace-bug/), [fixed them](/run-jekyll-bug-fixes-and-code-review/), and modernized the build infrastructure. The original author appears to have moved on — the repository has open issues with no responses and the last commit was five years ago.

Rather than wait indefinitely for a PR review, I'm forking the extension as **Run Jekyll** — a maintained version that acknowledges the original work while providing a path forward for bug fixes and improvements.

<!-- excerpt-end -->

## Why Fork Instead of PR

I submitted a PR to the original repository. The respectful first step. But the repository shows no signs of activity:

- Last commit: 2020
- Open issues: unanswered
- Dependencies: 42 known vulnerabilities (before I updated them)

The MIT license explicitly permits forking and republishing. The original author built something useful — thousands of people use it. Forking keeps it alive.

## The Rename: Jekyll Run → Run Jekyll

Publishing a fork under the same name creates confusion. Users searching for "Jekyll Run" would find two extensions with the same name, different publishers, and different versions. That's a bad experience.

**Run Jekyll** is distinct enough to avoid confusion while being immediately recognizable to existing users. The `package.json` changes:

```json
{
    "name": "run-jekyll",
    "displayName": "Run Jekyll",
    "description": "Build and Run your Jekyll static website (maintained fork of Jekyll Run)",
    "publisher": "<your-marketplace-publisher-id>",
    "version": "1.8.0"
}
```

The README credits the original author and links to the upstream repository.

## CI/CD Modernization

The original CI pipeline was from 2020 and couldn't run on current GitHub Actions runners. Here's what was updated:

### GitHub Actions Upgrades

| Component | Before | After |
|-----------|--------|-------|
| `actions/checkout` | v2 | v4 |
| `actions/setup-node` | v1 | v4 |
| `github/codeql-action` | v1 | v4 |
| Node.js | 12 (EOL) | 20 |
| Runner | `ubuntu-18.04` (EOL) | `ubuntu-latest` |
| `GabrielBB/xvfb-action` | v1.2 (all platforms) | v1.7 (Linux only) |
| `vsce` | v1 (deprecated) | `@vscode/vsce` v3 |
| `vscode-test` | v1.3 (broken) | `@vscode/test-electron` v2.4 |
| Stale bot | Probot config | `actions/stale@v9` |
| Action runtime | Node.js 20 | Node.js 24 opt-in |

### Cross-Platform Testing

The `ci-release.yml` workflow tests on macOS, Ubuntu, and Windows. The `xvfb-action` provides a headless display server for VS Code integration tests on Linux — macOS and Windows don't need it:

```yaml
- name: Run headless test (Linux)
  if: runner.os == 'Linux'
  uses: GabrielBB/xvfb-action@v1.7
  with:
    run: npm test
- name: Run test (macOS/Windows)
  if: runner.os != 'Linux'
  run: npm test
```

### VSIX Build and Release

A new `build-vsix.yml` workflow builds the `.vsix` extension package and attaches it to GitHub Releases:

- Triggers on release publish and manual `workflow_dispatch`
- Packages with `@vscode/vsce`
- Uploads as GitHub Actions artifact
- Attaches to the GitHub Release for direct download

Install from a release:

```bash
gh release download v1.7.1 --repo mcgarrah/jekyll-run --pattern '*.vsix'
code --install-extension jekyll-run.vsix
```

### Marketplace Publishing

The `ci-publish.yml` workflow publishes to the VS Code Marketplace when a GitHub Release is created. It checks for the `PUBLISHER_TOKEN` secret and skips gracefully if not configured:

```yaml
- name: Check for Marketplace token
  run: |
    if [ -z "${{ secrets.PUBLISHER_TOKEN }}" ]; then
      echo "::warning::PUBLISHER_TOKEN not configured. Skipping publish."
    fi
```

Setting up the token requires a [VS Code Marketplace publisher account](/run-jekyll-vscode-marketplace-publisher-setup/).

## Dependency Updates

All dependencies were updated from 2020 versions to current:

| Package | Before | After |
|---------|--------|-------|
| TypeScript | 3.8 | 5.7 |
| ESLint | 6.8 | 8.57 |
| `@typescript-eslint/*` | 2.30 | 8.58 |
| Mocha | 7.1 | 11.7 |
| `@types/node` | 13.11 | 20.17 |
| semantic-release | 17.4 | 24.2 |

Vulnerabilities reduced from 42 to 3 (remaining are transitive deps in npm and mocha that can't be fixed from our side).

Source code changes for TypeScript 5 compatibility:
- `child.pid` is `number | undefined` (added non-null assertions)
- `resolve()` requires an argument in `Promise<void>` (pass `undefined`)
- `skipLibCheck: true` in `tsconfig.json` for node_modules type conflicts
- ESLint rule `@typescript-eslint/semi` renamed to core `semi`

## Building from Source

```bash
git clone https://github.com/mcgarrah/jekyll-run.git
cd jekyll-run
npm install
npm run compile    # TypeScript → JavaScript
npm run lint       # ESLint check
npm test           # Run tests in Extension Development Host
vsce package       # Build .vsix
```

## What's Next

1. Apply the [bug fixes and code review improvements](/run-jekyll-bug-fixes-and-code-review/)
2. Rename to "Run Jekyll" in `package.json`
3. Set up a VS Code Marketplace publisher account
4. Add the `PUBLISHER_TOKEN` secret to the repository
5. Create a v1.8.0 release — CI publishes to Marketplace automatically

## Related Posts

- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/) — Configuration guide
- [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/) — macOS debugging story
- [Run Jekyll: Bug Fixes and Code Review](/run-jekyll-bug-fixes-and-code-review/) — The actual code fixes
- [Setting Up a VS Code Marketplace Publisher Account](/run-jekyll-vscode-marketplace-publisher-setup/) — Publishing prerequisites
- [Testing a VS Code Extension](/vscode-extension-testing-jekyll-run/) — Test harness and CI

## References

- [Jekyll Run Source Code](https://github.com/Kanna727/jekyll-run) — Original repository (upstream)
- [Run Jekyll Fork](https://github.com/mcgarrah/jekyll-run) — Maintained fork
- [Jekyll Run Extension](https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run) — Original Marketplace listing
- [VS Code Extension Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension) — Official guide
