---
layout: post
title: "Restoring the Markdown Preview Icon in VS Code on WSL2"
categories: [development-tools, wsl]
tags: [vscode, wsl2, markdown, linux, macos, troubleshooting]
excerpt: "Fixing the missing 'Open Preview' option for Markdown files in VS Code when using WSL2 compared to macOS."
description: "A quick guide on how to restore the default Markdown preview functionality and keyboard shortcuts in VS Code when working in a WSL2 Remote Linux environment."
date: 2026-04-23
last_modified_at: 2026-04-23
seo:
  type: BlogPosting
  date_published: 2026-04-23
  date_modified: 2026-04-23
---

<!-- TODO: Add a screenshot of the missing 'Open Preview' icon and the 'Open With...' menu for context. -->

If you regularly use VS Code across different operating systems, you might notice subtle differences in how certain features behave. One such quirk involves previewing Markdown (`.md`) files. 

On macOS, the "Open Preview" option (an icon that looks like a split pane with a magnifying glass) is usually readily available in the top-right corner of the editor. However, when switching to a Windows environment using VS Code connected to WSL2/Linux, you might find this icon missing, forcing you to right-click the file and navigate through an "Open With..." menu and picking from a list of items.

While `Ctrl+Shift+V` is a reliable "secret handshake" to bypass the menus and open the preview, it can be frustrating to lose the dedicated icon in your editor tab bar. It essentially feels like your VS Code environment on WSL2/Linux has lost its default file association for Markdown.

Here is how to fix the UI and a couple of other shortcuts to keep you moving fast.

## Why is it different on WSL?

VS Code treats your WSL environment as a "Remote" instance. Sometimes settings or default extensions don't sync perfectly between the local (e.g., macOS or Windows host) and remote (WSL Linux) environments. Setting the Default Editor or ensuring the right extensions are active in the remote environment usually anchors the "Open Preview" button back to the top-right header for good.

## 1. Restoring the "Open Preview" Icon

If the icon is missing from the top-right corner of your editor, it’s usually because the Built-in Markdown Language Features extension is disabled or overridden in your WSL instance.

1. **Check Extensions:** Open the Extensions view (`Ctrl+Shift+X`).
2. **Search:** Type `@builtin markdown`.
3. **Verify:** Ensure "Markdown Language Features" is enabled. If it's disabled specifically for your WSL connection, click **Enable (Workspace)** or **Enable**.

## 2. Setting the Default Editor

To stop the "Open With..." prompt when double-clicking a file in the sidebar and make the preview option the default behavior:

1. Right-click a `.md` file in the file explorer.
2. Select **Open With...**
3. Select **Configure default editor for '*.md'** (usually at the bottom of the list).
4. Choose **Markdown Preview**.

## Markdown Shortcut Cheat Sheet

Since you're already using the keyboard, these three shortcuts are the primary ways to handle previews in VS Code:

| Shortcut | Action | Use Case |
| :--- | :--- | :--- |
| `Ctrl + Shift + V` | Open Preview | Replaces the current editor tab with the full preview. |
| `Ctrl + K` then `V` | Open Preview to the Side | Opens the preview in a split pane so you can see code and results simultaneously. |
| `Ctrl + Shift + P` | Command Palette | Type "Markdown" to see all options, including exporting to HTML or PDF. |

## Notes for AI AGENT

The reason this came about as an issue is that on MacOS VSCode, the "Open Preview" shows up in the context menu at the top and is an easy to use option to get too.  In VSCode on Windows or Linux, this option does not show up for me and was annoying to have to press the split preview in the upper right corner.

I wanted a consistent solution across platforms. And an easy to use interface.

```text
The plugin "Markdown Preview Enhanced" seems to fix this issue and adds some improvements to the preview itself.

That is a solid pivot. Markdown Preview Enhanced (MPE) is widely considered the "power user" version of the built-in preview. It often forces its way back into the UI because it registers its own dedicated command and icon, effectively steamrolling whatever configuration glitch was hiding the default one.

Beyond just fixing the "missing button" issue, here is why you might actually prefer keeping it on your WSL/Windows setup:

Why MPE is an upgrade over the default:
Math & Diagrams: It has native support for KaTeX and MathJax for formulas, plus Mermaid, PlantUML, and Flowchart.js for diagrams without needing extra plugins.

Image Helper: It handles local image paths in WSL much more gracefully than the built-in preview, which sometimes struggles with the \\wsl$ file resolution.

Export Options: You can export directly to PDF, PNG, and HTML, or even create eBooks (ePub) and Marp/Pandoc presentations.

Code Chunk Execution: It can actually "run" code blocks in your markdown (if you have the respective compilers installed in your WSL Linux distro) and show the output in the preview.

One quick tip for MPE:
If you want it to feel even more seamless, you can set it to open automatically whenever you open a Markdown file.

Open your Settings (Ctrl + ,).

Search for markdown-preview-enhanced.previewConfig.automaticallyShowPreviewOfMarkdownBeingEdited.

Toggle that on, and you’ll never have to hunt for the button again.

A heads-up on WSL performance: Since MPE uses a slightly heavier rendering engine than the built-in VSCode preview, you might notice a tiny bit of "scroll lag" if you're working on a massive (10k+ line) file inside a WSL container. If that happens, you can toggle the Puppeteer settings in the plugin options to speed things up.

Are you using it mostly for documentation, or are you doing more technical writing with math/diagrams?
```