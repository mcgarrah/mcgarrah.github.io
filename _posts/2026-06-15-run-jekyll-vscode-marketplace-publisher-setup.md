---
title: "Run Jekyll: VS Code Marketplace Publisher Account Setup"
layout: post
categories: [web-development, technical]
tags: [vscode, vscode-extension, marketplace, azure-devops, open-source, publishing, jekyll]
excerpt: "If you need to fork and publish a VS Code extension — because the original maintainer disappeared five years ago — you first need a Marketplace publisher account. Here's the setup process: Microsoft account, Azure DevOps PAT, publisher profile, and the vsce CLI."
description: "Step-by-step guide to creating a VS Code Marketplace publisher account for publishing extensions. Covers Microsoft account setup, Azure DevOps Personal Access Token generation, publisher profile creation, vsce CLI authentication, and package.json requirements. Written in the context of forking an abandoned extension."
date: 2026-06-15
last_modified_at: 2026-06-15
seo:
  type: BlogPosting
  date_published: 2026-06-15
  date_modified: 2026-06-15
---

The [Jekyll Run VS Code extension](https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run) hasn't been updated in five years. I [diagnosed three bugs](/jekyll-run-plugin-multiroot-workspace-bug/) and [wrote the fixes](/forking-jekyll-run-to-run-jekyll/), but the upstream repository appears abandoned. If the PR sits without response, the next step is forking and publishing a maintained version.

To publish a VS Code extension, you need a Marketplace publisher account. The process routes through Microsoft's Azure DevOps infrastructure — not obvious, not well-documented in one place, and easy to get wrong on the authentication step.

<!-- excerpt-end -->

This is part of an ongoing series on the Run Jekyll VS Code extension:
- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/)
- [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/)
- [Forking Jekyll Run: From Abandoned Plugin to Run Jekyll](/forking-jekyll-run-to-run-jekyll/)
- **Run Jekyll: VS Code Marketplace Publisher Account Setup** (this post)
- [Run Jekyll: Bug Fixes and Code Review](/run-jekyll-bug-fixes-and-code-review/)
- [Run Jekyll: Testing and Test Harness](/run-jekyll-testing-and-test-harness/)
- [Run Jekyll: New Features — Clean, Doctor, and Real Tests](/run-jekyll-new-features-clean-doctor-tests/)

## Why You'd Need This

Most VS Code extension users never think about publishing. You need a publisher account when:

- You're forking an abandoned extension to ship a bug fix (my situation)
- You've built a custom extension for your team or workflow
- You want to contribute to the VS Code ecosystem

The account is free. The process takes about 15 minutes if you know the steps.

## Step 1: Microsoft Account and Azure DevOps Organization

The VS Code Marketplace uses Azure DevOps for authentication and management. Everything starts with a Microsoft account.

1. Go to [Azure DevOps](https://dev.azure.com/) and sign in with a Microsoft account
2. If you don't have an Azure DevOps organization, create one when prompted

The organization name doesn't matter for publishing — it's for internal management. Your public identity comes from the publisher profile (Step 3).

## Step 2: Generate a Personal Access Token (PAT)

The PAT authenticates your `vsce` CLI commands. This is the step most people get wrong.

1. In Azure DevOps, click your **User Settings** icon (gear icon next to your profile image)
2. Select **Personal access tokens**
3. Click **New Token**
4. Configure these settings carefully:

| Setting | Value |
|---------|-------|
| **Name** | Something descriptive (e.g., "vsce-marketplace") |
| **Organization** | **All accessible organizations** |
| **Expiration** | Set a reasonable duration (90 days, 1 year, or custom) |
| **Scopes** | Custom defined → Show all scopes → **Marketplace** → check **Manage** |

5. Click **Create**
6. **Copy the token immediately** — you cannot view it again after closing the dialog

Store the token securely. You'll need it for the `vsce login` step.

### Common Mistakes

- **Wrong organization scope**: If you select a specific organization instead of "All accessible organizations," publishing will fail with a 401 error
- **Wrong scopes**: The Marketplace scope is hidden under "Show all scopes" at the bottom of the dialog. If you only select the default scopes, authentication succeeds but publishing fails
- **Not copying the token**: Azure DevOps shows the token exactly once. If you close the dialog without copying it, you have to create a new one

## Step 3: Create Your Publisher Profile

The publisher profile is your public identity on the Marketplace — the name that appears next to your extension.

1. Go to the [Marketplace Publisher Management Page](https://marketplace.visualstudio.com/manage)
2. Sign in with the same Microsoft account
3. Click **Create publisher** in the left pane
4. Fill in:

| Field | Notes |
|-------|-------|
| **ID** | URL-safe identifier (e.g., `mcgarrah`). **Cannot be changed later.** |
| **Name** | Display name shown to users (e.g., "Michael McGarrah") |

The publisher ID is what goes in your extension's `package.json` under the `publisher` field. Choose carefully — it's permanent.

## Step 4: Install and Authenticate the CLI

The `vsce` (Visual Studio Code Extensions) CLI handles packaging and publishing.

```bash
npm install -g @vscode/vsce
```

Authenticate with your publisher ID and PAT:

```bash
vsce login <your-publisher-id>
```

It will prompt for the Personal Access Token from Step 2. Paste it in.

Verify the login:

```bash
vsce ls-publishers
```

## Step 5: Prepare package.json

Before publishing, your extension's `package.json` must include these fields:

```json
{
    "name": "run-jekyll",
    "displayName": "Run Jekyll",
    "description": "Build and Run your Jekyll static website (maintained fork)",
    "version": "1.8.0",
    "publisher": "mcgarrah",
    "engines": {
        "vscode": "^1.18.0"
    },
    "repository": {
        "type": "git",
        "url": "https://github.com/mcgarrah/jekyll-run"
    },
    "license": "MIT"
}
```

| Field | Purpose |
|-------|---------|
| `name` | Unique identifier (must not conflict with existing extensions) |
| `displayName` | User-friendly name shown in the Marketplace |
| `publisher` | Must match your exact Marketplace Publisher ID from Step 3 |
| `version` | SemVer format (e.g., `1.8.0`) — bump from the original |
| `engines.vscode` | Minimum VS Code version required |
| `repository` | Link to your fork's source code |
| `license` | The original extension's license (MIT in this case) |

### Forking Etiquette

When publishing a fork of someone else's extension:

- **Change the `name`** to avoid confusion (e.g., `run-jekyll` instead of `jekyll-run`)
- **Credit the original author** in the README and description
- **Link to the original repository** and your PR (if submitted)
- **Explain why the fork exists** — "maintained fork with multi-root workspace fix"
- **Keep the same license** — the original MIT license requires this

## Step 6: Package and Publish

```bash
# Package into a .vsix file (for testing)
vsce package

# Install locally to verify
code --install-extension run-jekyll-1.8.0.vsix

# Publish to the Marketplace
vsce publish
```

After publishing, the extension appears on the Marketplace within a few minutes. Users can find it by searching the extension name in VS Code.

### Version Bumping

For subsequent releases:

```bash
# Bump patch version (1.8.0 → 1.8.1) and publish
vsce publish patch

# Bump minor version (1.8.0 → 1.9.0) and publish
vsce publish minor
```

## Automated Publishing with GitHub Actions

The Jekyll Run fork already has a CI pipeline that automates both testing and publishing. Instead of running `vsce publish` manually, you can publish by creating a GitHub Release.

### How It Works

The fork includes two workflows:

- `ci-release.yml` — Runs tests on macOS, Ubuntu, and Windows on every push and PR
- `ci-publish.yml` — Publishes to the Marketplace when you create a GitHub Release

The publish workflow uses your Marketplace PAT (the same token from Step 2) as a GitHub secret:

```yaml
# .github/workflows/ci-publish.yml
on:
  release:
    types: [published]
jobs:
  publish:
    steps:
      - run: npm install
      - uses: JCofman/vscodeaction@master
        env:
          PUBLISHER_TOKEN: ${{ secrets.PUBLISHER_TOKEN }}
        with:
          args: publish -p $PUBLISHER_TOKEN
```

### Setting Up the Secret

1. Go to your fork on GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `PUBLISHER_TOKEN`
4. Value: The Personal Access Token from Step 2 (the Azure DevOps PAT with Marketplace Manage scope)

### Publishing a Release

Once the secret is configured:

1. Push your fixes and bump the version in `package.json`
2. Go to your fork on GitHub → **Releases** → **Create a new release**
3. Tag with the version (e.g., `v1.8.0`), write release notes
4. Click **Publish release**
5. The `ci-publish.yml` workflow triggers automatically and publishes to the Marketplace

This means the full workflow is: push code → CI tests on three platforms → create release → auto-publish. No manual `vsce` commands needed after initial setup.

### GitHub Release with VSIX Download

In addition to Marketplace publishing, the fork has a `build-vsix.yml` workflow that builds the `.vsix` extension package and attaches it to GitHub Releases. This lets users install the extension directly from GitHub without the Marketplace.

`code --install-extension` only accepts local files or Marketplace extension IDs — it can't download from a URL. You need to download the `.vsix` first, then install it.

### Installing from a GitHub Release

Using the `gh` CLI (one command):

```bash
# Download the latest release and install
gh release download v1.7.0 --repo mcgarrah/jekyll-run --pattern '*.vsix'
code --install-extension jekyll-run.vsix
```

Using `curl`:

```bash
# Download from the release assets URL
curl -L -o jekyll-run.vsix \
  https://github.com/mcgarrah/jekyll-run/releases/download/v1.7.0/jekyll-run.vsix
code --install-extension jekyll-run.vsix
```

Or just download manually from the [Releases page](https://github.com/mcgarrah/jekyll-run/releases) and run:

```bash
code --install-extension ~/Downloads/jekyll-run.vsix
```

The workflow triggers in two ways:

- **On GitHub Release**: builds and attaches `jekyll-run.vsix` to the release as a downloadable asset
- **Manual trigger** (`workflow_dispatch`): builds and uploads as a GitHub Actions artifact for testing before a release

To test the build without creating a release:

1. Go to the fork on GitHub → **Actions** tab
2. Select **Build VSIX** workflow
3. Click **Run workflow** → select `main` branch → **Run workflow**
4. When complete, download the artifact from the workflow run

To create a release with the VSIX attached:

1. Tag the release: `git tag -a v1.8.0 -m "v1.8.0 - description"`
2. Push the tag: `git push origin v1.8.0`
3. Create the release: `gh release create v1.8.0 --title "v1.8.0 - Title" --notes "Release notes"`
4. Both `ci-publish.yml` (Marketplace) and `build-vsix.yml` (GitHub artifact) trigger automatically
5. The `.vsix` file appears as a downloadable asset on the release page

Or create the release through the GitHub web UI: **Releases** → **Create a new release** → select the tag → **Publish release**.

The VSIX download is useful for:
- Testing before publishing to the Marketplace
- Sharing with others who want to try the fix before it's officially published
- Installing on machines without Marketplace access

For details on the test infrastructure and CI workflows, see [Testing a VS Code Extension: Building a Test Harness for Jekyll Run](/vscode-extension-testing-jekyll-run/).

## My Situation: Jekyll Run Fork

For context, here's my publishing plan for the Jekyll Run extension:

1. **PR submitted** to [Kanna727/jekyll-run](https://github.com/Kanna727/jekyll-run) with the three-file fix
2. **Wait 60 days** for a response
3. **If no response**: fork, rename to `run-jekyll`, publish under my publisher ID
4. **If merged**: no fork needed, everyone benefits from the upstream fix

The fixes are documented in [Forking Jekyll Run: From Abandoned Plugin to Run Jekyll](/forking-jekyll-run-to-run-jekyll/).

---

*This is part of an ongoing series on forking and improving the Jekyll Run VS Code extension. The extension source is at [github.com/mcgarrah/jekyll-run](https://github.com/mcgarrah/jekyll-run).*

## References

- [VS Code Extension Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension) — Official guide
- [vsce CLI](https://github.com/microsoft/vscode-vsce) — VS Code Extension Manager
- [Marketplace Publisher Management](https://marketplace.visualstudio.com/manage) — Create and manage publishers
- [Azure DevOps PAT Documentation](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate) — Token creation guide
