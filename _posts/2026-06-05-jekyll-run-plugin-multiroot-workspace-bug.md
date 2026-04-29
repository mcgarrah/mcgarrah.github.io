---
title: "Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, vscode, multi-root-workspace, plugin-bug, github-pages, ruby, rbenv, macos]
excerpt: "The Jekyll Run VS Code extension crashes with 'TypeError: Cannot read properties of null' in multi-root workspaces on macOS. The error is misleading — the real problem is macOS GUI apps don't inherit your shell PATH, so the plugin runs system Ruby 2.6. The fix is rbenv with Ruby 3.3, launching VS Code from a terminal, and understanding why every other approach fails."
description: "Diagnosing and fixing the Jekyll Run VS Code extension crash in multi-root workspaces on macOS. A debugging story covering the misleading null toString TypeError, blind alleys through VS Code settings and plugin source code, the real root cause (macOS GUI PATH inheritance), and the complete solution using rbenv with Ruby 3.3."
date: 2026-06-05
last_modified_at: 2026-06-05
seo:
  type: BlogPosting
  date_published: 2026-06-05
  date_modified: 2026-06-05
---

In my [previous post on the Jekyll Run plugin](/jekyll-run-vscode-plugin-local-development/), I covered how to configure the extension for local development — the flags that matter, settings precedence, and the `_config.yml` trap. That post assumed the plugin actually starts. This one covers what happens when it doesn't.

If you use a multi-root workspace in VS Code on macOS, the Jekyll Run extension crashes before it even tries to run Jekyll. The error is unhelpful:

```
TypeError: Cannot read properties of null (reading 'toString')
```

No stack trace in the UI. No hint about what's null. Just a dead button. I spent hours chasing this through VS Code settings, plugin source code, and compiled JavaScript patches before finding the real cause — and it had nothing to do with any of that. Misleading error messages that point to the wrong layer are the most expensive bugs to diagnose — true in VS Code extensions and equally true in distributed systems.

<!-- excerpt-end -->

## The Symptom

You open a multi-root workspace with your Jekyll blog and other projects. You click the Jekyll Run button in the status bar. Instead of building your site, you get the TypeError. The extension does nothing.

The same workspace, same plugin version, same settings — works fine on WSL2. Only macOS is broken.

## Blind Alley #1: VS Code Settings Precedence

My first theory was settings precedence. The plugin reads its configuration via `getConfiguration().get('jekyll-run')`, and I knew VS Code settings come from multiple sources with complex override rules. In a multi-root workspace, an empty `"settings": {}` in the `.code-workspace` file could shadow per-folder settings.

I added `jekyll-run` settings to every possible location:

| Location | Result |
|----------|--------|
| `.vscode/settings.json` (workspace folder) | Crash |
| `.code-workspace` settings block | Crash |
| VS Code User settings | Crash |
| All three simultaneously | Crash |

None of them fixed it. The settings were correct everywhere, but the plugin still crashed.

## Blind Alley #2: Plugin Source Code

I dug into the plugin's compiled JavaScript. The `Config.get()` method uses an unscoped API call:

```javascript
// out/config/config.js
return vscode.workspace.getConfiguration().get(extension);
```

The VS Code API documentation recommends `getConfiguration('jekyll-run')` (passing the section name directly) instead of `getConfiguration().get('jekyll-run')` (fetching the root and extracting a key). The unscoped form can return `null` in multi-root workspaces.

I patched `config.js` to use the scoped form. The TypeError persisted. The settings were resolving correctly — the crash was happening somewhere else entirely.

## Blind Alley #3: `.zshenv`

I noticed the plugin spawns `bundle exec jekyll serve` with `{ shell: true }`. On macOS, VS Code launched from the Dock doesn't source `~/.zshrc`. I created `~/.zshenv` (which is supposed to be sourced by all zsh instances, including non-interactive ones) with the Homebrew Ruby PATH.

Fully quit VS Code, reopened — still system Ruby 2.6. VS Code's extension host process isn't a zsh instance, so `.zshenv` is never sourced.

## The Breakthrough: Developer Tools

The actual error was hiding in plain sight. Opening VS Code's Developer Tools (`Cmd+Shift+P` → "Toggle Developer Tools" → Console tab) revealed the real error above the TypeError:

```
stderr: /System/Library/Frameworks/Ruby.framework/Versions/2.6/usr/lib/ruby/2.6.0/rubygems.rb:283:
in `find_spec_for_exe': Could not find 'bundler' (4.0.8) required by your Gemfile.lock.
(Gem::GemNotFoundException)
```

The plugin was running **macOS system Ruby 2.6** — not my Homebrew Ruby. System Ruby doesn't have the correct bundler version, so `bundle exec jekyll serve` fails immediately.

The TypeError was a secondary crash in the plugin's error handler. When stderr contains "ruby", the plugin tries to extract an Errno message:

```javascript
reject(error.match(/\B(.+)Errno(.+)/m));
```

The bundler error doesn't contain "Errno", so `match()` returns `null`. The plugin calls `reject(null)`, and the caller does `null.toString()` — crash. The real error (wrong Ruby) is swallowed. The user sees only the misleading TypeError.

## The Root Cause: macOS GUI PATH Inheritance

On macOS, applications launched from the Dock, Spotlight, or Finder inherit their environment from `launchd`, not from your shell. Your `~/.zshrc` PATH modifications — including Homebrew Ruby — are invisible to VS Code when launched this way.

```bash
# Your terminal sees:
which ruby    → /opt/homebrew/opt/ruby/bin/ruby  (Homebrew Ruby 4.0)

# VS Code's spawned processes see:
which ruby    → /usr/bin/ruby                     (macOS system Ruby 2.6)
```

WSL2 works because VS Code Remote Server runs inside a login shell that sources `~/.zshrc`. Same plugin, same workspace, same settings — but different environment inheritance model.

## The Solution: rbenv + Launch from Terminal

The fix has three parts:

### 1. Use rbenv for Ruby Version Management

Homebrew Ruby 4.0 has its own problem — `--livereload` causes a thread exception popup with Jekyll 4.4.1. Rather than fight bleeding-edge compatibility issues, use `rbenv` to pin the project to Ruby 3.3, which works perfectly with all Jekyll features:

```bash
# Install rbenv
brew install rbenv ruby-build

# Install Ruby 3.3
rbenv install 3.3.11

# Set project-local Ruby version
cd mcgarrah.github.io
rbenv local 3.3.11    # creates .ruby-version

# Install gems under Ruby 3.3
gem install bundler
bundle install
```

### 2. Initialize rbenv in Your Shell

Add to `~/.zshrc` (before `source $ZSH/oh-my-zsh.sh`):

```bash
# rbenv Ruby version manager (macOS only)
# Uses .ruby-version in project directories to select the correct Ruby
if [[ "$(uname -s)" == "Darwin" ]]; then
  eval "$(rbenv init - zsh)"
fi
```

And create `~/.zshenv` so non-interactive shells (like those VS Code spawns) can find rbenv's shims:

```bash
# rbenv shims for non-interactive shells (VS Code extensions)
if [[ "$(uname -s)" == "Darwin" && -d "$HOME/.rbenv" ]]; then
  export PATH="$HOME/.rbenv/shims:$HOME/.rbenv/bin:$PATH"
fi
```

### 3. Launch VS Code from a Terminal

macOS GUI apps don't source any shell configuration files. The `~/.zshenv` file helps with some non-interactive shells, but VS Code's extension host may still not pick it up reliably. The bulletproof fix is to launch VS Code from a terminal where your PATH is correct:

```bash
code ~/Personal/Github-mcgarrah/articles-workspace.code-workspace
```

When VS Code is launched this way, it inherits the terminal's environment, including rbenv's shims. The plugin finds the correct `bundle` and `ruby` executables, and Jekyll starts with all features working — including `--livereload`.

## Why Ruby 3.3 Instead of 4.0

Homebrew Ruby 4.0.2 works for Jekyll builds, but `--livereload` triggers a thread exception:

```
#<Thread:0x00000001266bb850 .../live_reload_reactor.rb:39 run> terminated with exception
```

The site still serves, but the popup is disruptive. Ruby 3.3.11 has no such issue — all Jekyll 4.4.1 features work correctly, including livereload.

Using `rbenv` with a `.ruby-version` file means:
- The Jekyll project uses Ruby 3.3 (stable, fully compatible)
- Other projects can use whatever Ruby they need
- The version is committed to the repository so collaborators get the same Ruby
- GitHub Actions can read `.ruby-version` to match the local development environment

## The Plugin Bug (Still Real)

The misleading TypeError is a genuine bug in the plugin's error handling, separate from the PATH issue. The plugin hasn't been updated since 2020 ([GitHub: Kanna727/jekyll-run](https://github.com/Kanna727/jekyll-run)).

Two issues worth a PR:

**1. Null rejection on non-Errno errors** in `src/cmds/run.ts`:

```diff
-            reject(error.match(/\B(.+)Errno(.+)/m));
+            reject(error.match(/\B(.+)Errno(.+)/m) || error);
```

**2. Unscoped getConfiguration call** in `src/config/config.ts`:

```diff
-        return vscode.workspace.getConfiguration().get(extension) as any;
+        return vscode.workspace.getConfiguration(extension);
```

The first fix ensures users see the actual Ruby error instead of a cryptic TypeError. The second fix properly resolves settings in multi-root workspaces. Neither is required if you follow the rbenv + terminal launch approach above, but both would make the plugin more robust.

## Complete Setup Reference

### Shell Configuration (`~/.zshrc`)

```bash
# rbenv Ruby version manager (macOS only)
if [[ "$(uname -s)" == "Darwin" ]]; then
  eval "$(rbenv init - zsh)"
fi
```

### Shell Environment (`~/.zshenv`)

```bash
# rbenv shims for non-interactive shells (VS Code extensions)
if [[ "$(uname -s)" == "Darwin" && -d "$HOME/.rbenv" ]]; then
  export PATH="$HOME/.rbenv/shims:$HOME/.rbenv/bin:$PATH"
fi
```

### Project Ruby Version (`.ruby-version`)

```
3.3.11
```

### VS Code Settings (`.vscode/settings.json`)

```json
{
    "jekyll-run.commandLineArguments": "--trace --drafts --future --unpublished --livereload --incremental",
    "jekyll-run.stopServerOnExit": true
}
```

### Multi-Root Workspace (`.code-workspace`)

```json
{
    "settings": {
        "jekyll-run.commandLineArguments": "--trace --drafts --future --unpublished --livereload --incremental",
        "jekyll-run.stopServerOnExit": true
    }
}
```

### Fallback Script (`start-jekyll.sh`)

```bash
#!/bin/bash
bundle exec jekyll serve --trace --drafts --future --unpublished --livereload --incremental
```

## Known Issue: Port Conflict Shows Thread Exception

If a Jekyll server is already running on port 4000 (from a terminal `./start-jekyll.sh` session, for example), clicking the Jekyll Run button won't show a clean "port in use" error. Instead, you'll see a thread exception popup:

```
#<Thread:0x0000000126cc9a58 .../live_reload_reactor.rb:39 run> terminated with exception
```

This happens because the plugin's port-detection code parses `lsof` output by splitting on single spaces, but macOS `lsof` uses variable-width columns with multiple spaces between fields. The PID is never extracted, so the plugin thinks port 4000 is free, launches Jekyll, and the livereload thread crashes on the port conflict before the main server reports `EADDRINUSE`.

The workaround is to not run both simultaneously — use either `./start-jekyll.sh` or the Jekyll Run button, not both. Kill the terminal server first (`Ctrl+C`) before using the plugin.

This is a separate plugin bug covered in [Jekyll Run Plugin: Patching the Source and Submitting a PR](/jekyll-run-plugin-pr-and-fork/).

## Summary

Three problems, layered on top of each other, each masking the next:

| Problem | Symptom | Fix |
|---------|---------|-----|
| macOS GUI apps don't inherit shell PATH | System Ruby 2.6 runs instead of project Ruby | Launch VS Code from terminal |
| Plugin rejects `null` on non-Errno Ruby errors | TypeError instead of useful error message | Plugin bug (PR needed) |
| Ruby 4.0 livereload incompatibility | Thread exception popup | Use Ruby 3.3 via rbenv |
| Plugin `lsof` parsing broken on macOS | Port conflict shows thread exception instead of clean error | Don't run terminal server and plugin simultaneously; plugin bug (PR needed) |

The first one is the blocker. The second makes debugging harder. The third drove the choice of Ruby 3.3 over 4.0. The fourth is a nuisance if you forget to stop a terminal server before using the plugin.

## Related Posts

- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/) — Complete configuration guide for the extension
- [Running GitHub Pages Jekyll Locally](/github-pages-jekyll-locally/) — Initial local development setup

## References

- [Jekyll Run Extension](https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run) — VS Code Marketplace
- [Jekyll Run Source Code](https://github.com/Kanna727/jekyll-run) — GitHub repository (last updated 2020)
- [rbenv](https://github.com/rbenv/rbenv) — Ruby version manager
- [VS Code getConfiguration API](https://code.visualstudio.com/api/references/vscode-api#workspace.getConfiguration) — Official API documentation
