---
title: "Setting Up a VS Code Marketplace Publisher Account"
layout: post
categories: [web-development, technical]
tags: [vscode, vscode-extension, marketplace, azure-devops, open-source, publishing]
excerpt: "If you need to fork and publish a VS Code extension — because the original maintainer disappeared five years ago — you first need a Marketplace publisher account. Here's the setup process: Microsoft account, Azure DevOps PAT, publisher profile, and the vsce CLI."
description: "Step-by-step guide to creating a VS Code Marketplace publisher account for publishing extensions. Covers Microsoft account setup, Azure DevOps Personal Access Token generation, publisher profile creation, vsce CLI authentication, and package.json requirements. Written in the context of forking an abandoned extension."
date: 2026-05-28
last_modified_at: 2026-05-28
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-28
  date_modified: 2026-05-28
---

The [Jekyll Run VS Code extension](https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run) hasn't been updated in five years. I [diagnosed three bugs](/jekyll-run-plugin-multiroot-workspace-bug/) and [wrote the fixes](/jekyll-run-plugin-pr-and-fork/), but the upstream repository appears abandoned. If the PR sits without response, the next step is forking and publishing a maintained version.

To publish a VS Code extension, you need a Marketplace publisher account. The process routes through Microsoft's Azure DevOps infrastructure — not obvious, not well-documented in one place, and easy to get wrong on the authentication step.

<!-- excerpt-end -->

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
    "name": "jekyll-run-fixed",
    "displayName": "Jekyll Run (Fixed)",
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

- **Change the `name`** to avoid confusion (e.g., `jekyll-run-fixed` instead of `jekyll-run`)
- **Credit the original author** in the README and description
- **Link to the original repository** and your PR (if submitted)
- **Explain why the fork exists** — "maintained fork with multi-root workspace fix"
- **Keep the same license** — the original MIT license requires this

## Step 6: Package and Publish

```bash
# Package into a .vsix file (for testing)
vsce package

# Install locally to verify
code --install-extension jekyll-run-fixed-1.8.0.vsix

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

## My Situation: Jekyll Run Fork

For context, here's my publishing plan for the Jekyll Run extension:

1. **PR submitted** to [Kanna727/jekyll-run](https://github.com/Kanna727/jekyll-run) with the three-file fix
2. **Wait 60 days** for a response
3. **If no response**: fork, rename to `jekyll-run-fixed`, publish under my publisher ID
4. **If merged**: no fork needed, everyone benefits from the upstream fix

The fixes are documented in [Jekyll Run Plugin: Patching the Source and Submitting a PR](/jekyll-run-plugin-pr-and-fork/).

## Related Posts

- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/) — Configuration guide
- [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/) — macOS debugging story
- [Jekyll Run Plugin: Patching the Source and Submitting a PR](/jekyll-run-plugin-pr-and-fork/) — Code fixes and fork strategy

## References

- [VS Code Extension Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension) — Official guide
- [vsce CLI](https://github.com/microsoft/vscode-vsce) — VS Code Extension Manager
- [Marketplace Publisher Management](https://marketplace.visualstudio.com/manage) — Create and manage publishers
- [Azure DevOps PAT Documentation](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate) — Token creation guide
