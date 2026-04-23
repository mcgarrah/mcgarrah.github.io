---
layout: post
title: "Fixing the Missing Markdown Preview Icon in VS Code Across Platforms"
categories: [development-tools, wsl]
tags: [vscode, wsl2, markdown, linux, macos, windows, troubleshooting]
excerpt: "The Markdown 'Open Preview' icon disappears in VS Code on WSL2 and sometimes Windows. Here's how to fix it — and why Markdown Preview Enhanced might be the better long-term answer."
description: "How to restore the default Markdown preview icon and keyboard shortcuts in VS Code on WSL2, Windows, and Linux — plus a look at Markdown Preview Enhanced as a cross-platform fix."
date: 2026-04-23
last_modified_at: 2026-04-23
seo:
  type: BlogPosting
  date_published: 2026-04-23
  date_modified: 2026-04-23
---

<!-- TODO: Screenshots needed for all three platforms showing the behavior difference.
  - macOS: Screenshot of the editor title bar with the "Open Preview" split-pane icon visible (top-right)
  - Windows: Screenshot of the editor title bar with the icon missing
  - WSL2/Linux: Screenshot of the editor title bar with the icon missing
  - macOS: Screenshot of the right-click context menu showing "Open Preview" option
  - Windows/WSL2: Screenshot of the right-click context menu showing "Open With..." submenu instead
  - "Open With..." dialog: Screenshot showing the "Configure default editor for '*.md'" option at the bottom
  - MPE: Screenshot of the Markdown Preview Enhanced icon in the editor title bar after installation
  - MPE: Screenshot of the side-by-side preview rendering a Mermaid diagram or KaTeX formula
-->

<!-- excerpt-end -->

If you use VS Code across macOS, Windows, and WSL2, you have probably noticed that the Markdown preview experience is not consistent. On macOS, the "Open Preview" icon — a split-pane with a magnifying glass — sits in the top-right corner of the editor title bar. Click it and you get a rendered preview immediately.

On Windows or VS Code connected to WSL2/Linux, that icon often disappears. Instead you are forced to right-click the file, navigate through an "Open With..." submenu, and pick from a list. The keyboard shortcut `Ctrl+Shift+V` still works, but losing the one-click icon is a paper cut that adds up when you edit Markdown all day.

This article covers two fixes: restoring the built-in icon, and switching to Markdown Preview Enhanced for a more consistent cross-platform experience.

## Why Does the Icon Disappear on WSL2?

VS Code treats WSL as a "Remote" environment. Extensions, settings, and default file associations do not always sync between the local host (macOS or Windows) and the remote WSL instance. The built-in Markdown Language Features extension can end up disabled or overridden in the remote context, which removes the preview icon from the title bar.

The same issue occasionally appears on native Windows or Linux installs when another extension claims the `.md` file type.

## Fix 1: Restore the Built-In Preview Icon

If the icon is missing, the built-in Markdown Language Features extension is likely disabled in your current environment.

1. Open the Extensions view (`Ctrl+Shift+X`).
2. Search for `@builtin markdown`.
3. Verify that "Markdown Language Features" is enabled. If it shows as disabled for your WSL connection, click **Enable (Workspace)** or **Enable**.

## Fix 2: Set the Default Editor for Markdown

To stop the "Open With..." prompt and make preview the default when double-clicking a `.md` file in the sidebar:

1. Right-click any `.md` file in the Explorer.
2. Select **Open With...**
3. At the bottom of the list, select **Configure default editor for '*.md'**.
4. Choose **Markdown Preview**.

## Markdown Shortcut Cheat Sheet

These three shortcuts work on all platforms regardless of icon visibility:

| Shortcut | Action | Notes |
|:---|:---|:---|
| `Ctrl+Shift+V` | Open Preview | Replaces the current tab with a full preview |
| `Ctrl+K` then `V` | Open Preview to the Side | Split pane — edit and preview simultaneously |
| `Ctrl+Shift+P` → "Markdown" | Command Palette | Lists all Markdown commands including export |

On macOS, substitute `Cmd` for `Ctrl`.

## The Better Fix: Markdown Preview Enhanced

The built-in preview is functional but minimal. [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced) (MPE) is the power-user alternative — and it fixes the missing icon problem as a side effect, because it registers its own dedicated command and title bar icon that works consistently across all platforms.

### Why MPE Is an Upgrade

- **Math and diagrams**: Native KaTeX/MathJax support for formulas, plus Mermaid, PlantUML, and Flowchart.js for diagrams — no extra extensions needed.
- **Image path handling**: Resolves local image paths in WSL more gracefully than the built-in preview, which sometimes struggles with `\\wsl$` file resolution.
- **Export options**: Direct export to PDF, PNG, HTML, ePub, and Marp/Pandoc presentations.
- **Code chunk execution**: Can run code blocks in your Markdown (if the compiler is installed in your environment) and render the output inline in the preview.

### Auto-Open Preview

To make MPE open the preview automatically whenever you open a Markdown file:

1. Open Settings (`Ctrl+,`).
2. Search for `markdown-preview-enhanced.previewConfig.automaticallyShowPreviewOfMarkdownBeingEdited`.
3. Toggle it on.

### WSL2 Performance Note

MPE uses a heavier rendering engine than the built-in preview. On very large files (10k+ lines) inside a WSL container, you may notice scroll lag. If that happens, check the Puppeteer settings in the MPE extension options to tune rendering performance.

## Summary

The missing Markdown preview icon is a VS Code quirk caused by remote environment extension sync issues. You can fix it by re-enabling the built-in Markdown Language Features extension and setting the default editor — or skip the workaround entirely by installing Markdown Preview Enhanced, which provides a consistent, feature-rich preview across macOS, Windows, and WSL2.
