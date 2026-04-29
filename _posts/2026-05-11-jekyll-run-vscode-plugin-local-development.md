---
title: "Jekyll Run Plugin: Local Development Settings That Actually Work"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, vscode, local-development, github-pages, future-posts, drafts, configuration]
excerpt: "The Jekyll Run VS Code extension is convenient for local development, but its settings live in four different places and the defaults won't show your future-dated posts. Here's how to configure it properly, where the settings actually come from, and the _config.yml trap that silently overrides your CLI flags."
description: "Complete guide to configuring the Jekyll Run VS Code extension for local Jekyll development. Covers command-line arguments, settings precedence across workspace, machine, and multi-root workspace files, the _config.yml future flag trap, and a fallback bash script for when the extension misbehaves."
date: 2026-05-11
last_modified_at: 2026-05-11
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-11
  date_modified: 2026-05-11
---

The [Jekyll Run](https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run) VS Code extension (Dedsec727.jekyll-run) gives you a one-click button to build and serve your Jekyll site. It works well for basic use, but if you write future-dated posts, use drafts, or run a multi-root workspace, the defaults will bite you.

This post covers the configuration I use, the settings precedence that tripped me up, and a bash script fallback for when the extension gets confused.

<!-- excerpt-end -->

## Why Jekyll Run

Without the extension, local development means opening a terminal and running:

```bash
bundle exec jekyll serve --trace --drafts --future --unpublished --livereload --incremental
```

Jekyll Run wraps this into a button in the VS Code status bar. Click to start, click to stop. It picks up your workspace settings for command-line arguments and handles the process lifecycle.

For a blog with 130+ posts where I'm constantly previewing drafts and future-dated articles, the convenience is worth the occasional quirk.

Developer experience is a platform engineering concern, whether you're standardizing IDE settings across a 50-person engineering organization or configuring a Jekyll plugin for a solo blog. The time lost to tooling friction — a missing CLI flag, a settings precedence conflict, a stale incremental build — compounds. Getting the local development environment right once means every future writing session starts clean.

## The Flags That Matter

Here's what each flag does and why I use all of them:

| Flag | Purpose |
|------|---------|
| `--trace` | Show full Ruby backtraces on errors instead of cryptic one-liners |
| `--drafts` | Render files in `_drafts/` as if they were published |
| `--future` | Include posts with dates in the future |
| `--unpublished` | Render posts with `published: false` in front matter |
| `--livereload` | Auto-refresh the browser when files change |
| `--incremental` | Only rebuild changed pages (faster, but occasionally stale) |

The critical ones are `--future` and `--drafts`. Without them, you can't preview the content you're actively writing.

## Configuring the Extension

The extension reads its command-line arguments from the `jekyll-run.commandLineArguments` setting. Add this to your workspace's `.vscode/settings.json`:

```json
{
    "jekyll-run.commandLineArguments": "--trace --drafts --future --unpublished --livereload --incremental",
    "jekyll-run.stopServerOnExit": true
}
```

The `stopServerOnExit` setting kills the Jekyll process when you close VS Code, preventing orphaned processes that block port 4000 on the next launch.

## Settings Precedence: Where It Gets Tricky

VS Code settings come from multiple sources, and higher-priority settings silently override lower ones. For the Jekyll Run extension, the precedence is:

1. **Multi-root workspace file** (`.code-workspace`) — highest priority
2. **Workspace folder settings** (`.vscode/settings.json`)
3. **User settings** (`~/.vscode-server/data/User/settings.json`)
4. **Machine settings** (`~/.vscode-server/data/Machine/settings.json`)

### The Multi-Root Workspace Trap

If you use a multi-root workspace (multiple folders in one VS Code window), the `.code-workspace` file's settings override per-folder `.vscode/settings.json` files. An empty settings block in the workspace file:

```json
{
    "folders": [
        { "path": "my-blog" },
        { "path": "resume" }
    ],
    "settings": {}
}
```

...means the extension falls through to machine or user settings, which may not have your flags. The fix is to add the settings explicitly:

```json
{
    "folders": [
        { "path": "my-blog" },
        { "path": "resume" }
    ],
    "settings": {
        "jekyll-run.commandLineArguments": "--trace --drafts --future --unpublished --livereload --incremental",
        "jekyll-run.stopServerOnExit": true
    }
}
```

**macOS users:** If you see `TypeError: Cannot read properties of null (reading 'toString')` in a multi-root workspace, the problem is deeper than settings — it's related to macOS GUI PATH inheritance and Ruby version management. See [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/) for the full diagnosis and fix.

### The Machine Settings Trap

On VS Code Remote (SSH, WSL, etc.), machine settings live at `~/.vscode-server/data/Machine/settings.json` on the remote host. If someone — or an extension update — writes a `jekyll-run.commandLineArguments` value there with fewer flags, it can override your workspace settings depending on how the extension resolves precedence.

Check what's actually there:

```bash
cat ~/.vscode-server/data/Machine/settings.json
```

### Diagnosing Which Settings Win

The fastest way to confirm what the extension is actually using:

```bash
ps aux | grep jekyll | grep -v grep
```

This shows the exact command line. If you see `--trace --drafts` but not `--future`, your workspace settings aren't being picked up.

## The _config.yml Trap

Even with `--future` in your CLI flags, Jekyll will ignore it if `_config.yml` explicitly sets:

```yaml
future: false
```

The config file value **overrides** the command-line flag. This is counterintuitive — you'd expect CLI flags to win — but that's how Jekyll works.

The fix is to not set `future` in `_config.yml` at all. The default is `false`, which means:

- **Production builds** (GitHub Actions without `--future`) won't publish future posts
- **Local development** (with `--future` flag) will show them

```yaml
# Don't do this — it overrides the --future CLI flag
# future: false

# Do this — let the CLI flag control it
# (just leave it out entirely, or comment it)
```

This applies to `show_drafts` and `unpublished` as well. If you set them explicitly in `_config.yml`, the CLI flags become useless.

## The Draft and Unpublished Visibility Trap

This one cost me hours. The `--drafts` and `--unpublished` flags make Jekyll **render** draft files and posts with `published: false` — but they don't appear in `site.posts`. That means:

- They won't show in your archive page
- They won't show in tag or category listings
- They won't show on the homepage pagination
- They **are** accessible by direct URL

The files exist in `_site/`. Jekyll built them. But any template that iterates `site.posts` (which is nearly every listing page) silently excludes them.

### How to Confirm They Exist

Check the build output directly:

```bash
ls _site/your-draft-slug/
```

If `index.html` is there, Jekyll rendered it. You can view it at `http://127.0.0.1:4000/your-draft-slug/`. It just won't appear in any listing.

### Draft Sorting: They're at the Bottom, Not the Top

Even when drafts do appear in `site.posts`, they show up **at the end of the archive** — after your oldest post. You'll scroll past 100+ articles looking for your new draft at the top and conclude it's missing.

Jekyll appends drafts after all regular posts in `site.posts` rather than sorting them into chronological position by their assigned date. So a draft dated 2026-05-10 appears after a post from 2001, not at the top of the list where you'd expect it.

Check the bottom of your archive page, not the top.

### The Workaround

Set `published: true` in your draft's front matter. The file is still in `_drafts/` so it won't deploy to production (GitHub Actions doesn't use `--drafts`), but locally it will appear in all listings.

The `published: false` flag is useful for posts in `_posts/` that you want to temporarily hide. For files in `_drafts/`, it's counterproductive — you're already using the drafts folder to prevent publication, and adding `published: false` makes them invisible even in local development.

## The Bash Script Fallback

The Jekyll Run extension occasionally gets into a bad state — it thinks a server is running when nothing is on port 4000. When that happens, I fall back to a bash script:

```bash
#!/bin/bash
bundle exec jekyll serve --trace --drafts --future --unpublished --livereload --incremental
```

Save this as `start-jekyll.sh` in your project root. When the extension misbehaves:

1. Try **Jekyll Run: Stop Server** from the Command Palette (`Ctrl+Shift+P`)
2. If that doesn't work, run **Developer: Reload Window**
3. If that doesn't work, use the script: `bash start-jekyll.sh`

### Clearing Stale State

If you're getting build errors that don't match your current code, incremental builds may be serving cached content. Clear everything:

```bash
rm -rf .jekyll-cache _site && bash start-jekyll.sh
```

This forces a full rebuild from scratch.

## My Complete Setup

For reference, here's every file involved in my local development configuration:

**`.vscode/settings.json`** (per workspace folder):
```json
{
    "jekyll-run.commandLineArguments": "--trace --drafts --future --unpublished --livereload --incremental",
    "jekyll-run.stopServerOnExit": true
}
```

**`blog-workspace.code-workspace`** (multi-root workspace):
```json
{
    "folders": [
        { "path": "mcgarrah.github.io" },
        { "path": "resume" }
    ],
    "settings": {
        "jekyll-run.commandLineArguments": "--trace --drafts --future --unpublished --livereload --incremental",
        "jekyll-run.stopServerOnExit": true
    }
}
```

**`start-jekyll.sh`** (fallback script):
```bash
#!/bin/bash
bundle exec jekyll serve --trace --drafts --future --unpublished --livereload --incremental
```

**`_config.yml`** (no explicit `future` setting):
```yaml
# Future posts controlled by CLI --future flag
# Default is false, so production builds exclude future posts
# Local development uses --future to preview them
```

## Related Posts

- [Running GitHub Pages Jekyll Locally](/github-pages-jekyll-locally/) — Initial local development setup
- [How the Sausage Is Made: Every Feature Powering This Jekyll Blog](/jekyll-markdown-feature-reference/) — Complete feature reference

## References

- [Jekyll Run Extension](https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run) — VS Code Marketplace
- [Jekyll Configuration Options](https://jekyllrb.com/docs/configuration/options/) — Official docs on CLI flags and config precedence
- [VS Code Settings Precedence](https://code.visualstudio.com/docs/getstarted/settings#_settings-precedence) — How VS Code resolves settings from multiple sources
