---
layout: post
title: "Kiro IDE + WSL2: Fixing the Agent Shell Execution Layer"
image: /assets/images/og/kiro-ide-wsl2-integration.png
categories: [development, tools]
tags: [kiro, wsl2, ubuntu, ide, ai-coding, zsh, shell-integration, open-remote-wsl]
excerpt: "Kiro's AI agent can execute shell commands in WSL2, but the execution layer misbehaves without explicit Linux terminal profiles and shell integration. Here's how to fix the garbled output, path mangling, and false error codes."
description: "A practical guide to fixing Kiro IDE's agent shell execution in WSL2 — adding Linux terminal profiles, shell integration scripts, and steering context for reliable AI agent interactions on Ubuntu 24.04."
date: 2026-08-21
last_modified_at: 2026-08-21
seo:
  type: BlogPosting
  date_published: 2026-08-21
  date_modified: 2026-08-21
---

Kiro is AWS's AI-native IDE — a Code OSS fork with agentic coding capabilities baked in. Unlike VS Code, it doesn't ship with Microsoft's proprietary Remote - WSL extension. Instead, WSL2 connectivity relies on the community-maintained [Open Remote - WSL](https://open-vsx.org/extension/jeanp413/open-remote-wsl) extension (`jeanp413.open-remote-wsl`), which is available on Open VSX. I covered the full setup — installation, `argv.json` configuration, the update breakage cycle, and recovery — in a [previous article](/kiro-ide-wsl2-support-open-remote-extension/).

This article tackles what happens *after* WSL2 connectivity is working: the agent's shell execution layer still misbehaves. Kiro's AI agent can run terminal commands inside your WSL2 environment, but without explicit Linux terminal profiles and shell integration, the results are garbled, unreliable, and frustrating.

<!-- excerpt-end -->

I hit this after migrating from VS Code to Kiro. Every shell command the agent tried to run came back with double-echoed output, `Exit Code: 1`, and Windows-style path escaping — despite the commands actually executing successfully inside my WSL2 Ubuntu 24.04 environment. This article documents the fixes.

## The Trigger: "I'm Clearly Stuck in a Loop"

The moment that sent me down this rabbit hole was Kiro's agent announcing:

> "I've been trying to use `execute_pwsh` but it's failed 7 times in a row. I'm clearly stuck in a loop. What would you like me to do?"

My immediate reaction: *why is it using PowerShell?* I'm in WSL2 running Ubuntu 24.04 with zsh. There is no PowerShell here. I told the agent — repeatedly across multiple sessions — that it cannot use PowerShell in this environment, and each time it acknowledged the constraint but kept invoking the same `execute_pwsh` tool.

The confusion is understandable. The tool is *named* `execute_pwsh`. If you're a developer who sees "pwsh" in a tool name, you think PowerShell. The agent thinks PowerShell. Everyone assumes the wrong thing.

Here's the reality: `execute_pwsh` is just the name of Kiro's *only* shell execution tool. It's not actually calling PowerShell — it dispatches commands to whatever terminal backend the IDE is configured to use. In a WSL Remote context, that terminal *should* be your Linux shell. The name is a misnomer inherited from the tool's original Windows-first design.

The real problem isn't that PowerShell is being invoked. It's that the terminal backend, despite reaching your Linux shell, is misconfigured — the path escaping, echo handling, and exit code parsing are all broken because Kiro doesn't have explicit Linux terminal profiles telling it how to behave in this context.

Once I understood that distinction — `execute_pwsh` ≠ PowerShell, it's just a badly-named shell dispatch tool — the fix became obvious: tell Kiro what shell to actually use on the Linux side.

**Prerequisites:** You should already have `jeanp413.open-remote-wsl` installed and configured with the `enable-proposed-api` entry in `~/.kiro/argv.json`. If you haven't done that yet, start with [Kiro IDE on Windows: WSL2 Support via Open Remote Extension](/kiro-ide-wsl2-support-open-remote-extension/).

## The Problem

When Kiro's agent executes terminal commands via its `execute_pwsh` tool (yes, the name is hardcoded regardless of your actual shell), it does the following in a WSL Remote context:

1. **Mangles the `cwd` parameter** — Converts Linux paths to Windows UNC notation before passing them, causing `cd` failures.
2. **Double-echoes commands** — Every command appears twice in the output, garbled with character insertions.
3. **Reports false exit codes** — Commands succeed but the tool reports `Exit Code: 1`.
4. **Treats paths as Windows** — Backslash escaping and quoting patterns break Linux commands.

The commands actually execute — `git pull` succeeds, files get modified — but the agent can't reliably parse its own output, leading to confusion, retries, and a frustrating developer experience.

## Why This Worked in VS Code

VS Code extensions like GitHub Copilot, Amazon Q, and Continue dispatch shell commands through the `terminal.integrated.automationProfile` settings. When you're connected to WSL2 via Remote WSL, VS Code correctly uses the Linux automation profile for command execution.

Kiro's agent tool (`execute_pwsh`) appears to bypass or ignore this setting chain in certain configurations. The fix is to explicitly declare Linux terminal profiles so there's no ambiguity.

Note: VS Code uses Microsoft's proprietary Remote - WSL extension, which is not available on Open VSX and cannot be used in Kiro. Kiro uses `jeanp413.open-remote-wsl` — a community-built alternative that provides the same WSL2 filesystem and terminal bridging. The terminal profile fix below applies regardless of which remote extension provides the WSL2 connection.

## The Fix: Three Parts

### 1. Kiro User Settings (settings.json)

Location on the Windows filesystem: `%APPDATA%\Kiro\User\settings.json`

From WSL: `/mnt/c/Users/<username>/AppData/Roaming/Kiro/User/settings.json`

Add these settings:

```json
{
  "terminal.integrated.defaultProfile.linux": "zsh",
  "terminal.integrated.automationProfile.linux": {
    "path": "/bin/zsh"
  },
  "terminal.integrated.profiles.linux": {
    "zsh": { "path": "/bin/zsh" },
    "bash": { "path": "/bin/bash" }
  }
}
```

The key insight: even though `terminal.integrated.defaultProfile.windows` was already set to a WSL profile, the **Linux-side profiles** were never declared. When Kiro's Remote WSL connection needs to execute commands inside the Linux environment, it looks for `*.linux` settings — and without them, falls back to behavior that doesn't match your environment.

You should also have the Windows-side WSL profile configured:

```json
{
  "terminal.integrated.defaultProfile.windows": "Ubuntu-24.04 (WSL)",
  "terminal.integrated.profiles.windows": {
    "Ubuntu-24.04 (WSL)": {
      "path": "C:\\WINDOWS\\System32\\wsl.exe",
      "args": ["-d", "Ubuntu-24.04"]
    }
  }
}
```

### 2. Shell Integration Scripts

Kiro provides shell integration that improves command tracking, exit code detection, and working directory awareness. Without these, the agent has to infer results from raw terminal output — which is where the garbling and false errors come from.

**For zsh** — add to the end of `~/.zshrc`:

```bash
# Kiro shell integration
[[ "$TERM_PROGRAM" == "kiro" ]] && . "$(kiro --locate-shell-integration-path zsh)"
```

**For bash** — add to the end of `~/.bashrc`:

```bash
# Kiro shell integration
[[ "$TERM_PROGRAM" == "kiro" ]] && . "$(kiro --locate-shell-integration-path bash)"
```

The `[[ "$TERM_PROGRAM" == "kiro" ]]` guard ensures these only activate when running inside Kiro — no impact on your regular terminal sessions.

### 3. Reload Kiro

After making these changes:

1. Close and reopen Kiro, **or** use Command Palette → "Developer: Reload Window"
2. Open a new agent session to test

The shell integration loads at terminal startup, so existing sessions won't pick up the changes.

## Bonus: WSL Launcher Function

If you want to launch Kiro from your WSL terminal (like `code .` opens VS Code), add this to `~/.zshrc`:

```bash
kiro() {
    local KIRO_BIN="/mnt/c/Users/<username>/AppData/Local/Programs/Kiro/Kiro.exe"
    env -i /init "$KIRO_BIN" "$(wslpath -w "${1:-.}")" > /dev/null 2>&1 &
}
```

Usage:
- `kiro .` — Open current directory in Kiro
- `kiro ~/github/myproject` — Open a specific project

The `env -i /init` pattern is key — it uses the WSL interop bridge (`/init`) to launch the Windows binary while cleaning the environment so Linux environment variables don't leak into the Windows process. The `&` backgrounds it so your terminal stays usable.

## Kiro Steering Files

If you're using Kiro's steering system (`.kiro/steering/*.md`) to provide project context to the agent, add a note about the shell environment. I keep this at the user level (`~/.kiro/steering/shell-environment.md`) so it applies across all workspaces:

```markdown
---
inclusion: auto
---

# Shell & Platform Environment

- **Execution environment:** WSL2 running Ubuntu 24.04 LTS
- **Shell:** zsh with Oh My Zsh (omz)
- **This is a Linux environment.** Always use Linux commands, paths, and tooling.
- Do NOT use PowerShell, `cmd.exe`, or Windows-style paths in shell commands.
- Native paths use `/home/<username>/...` format, not Windows UNC paths.
```

This gives the agent explicit context about the execution environment, reducing the chance it tries to use Windows-style commands or paths.

## Phantom Diffs in the Source Control Panel

After getting shell execution working, you may notice another oddity: Kiro's Source Control panel shows files as "modified" even when `git status` from the terminal reports a clean working tree. The phantom diffs almost always affect shell scripts (`.sh` files) — specifically those with the executable bit (`chmod +x`) set.

**Root cause:** Kiro's built-in git SCM extension reads file metadata through the `\\wsl$\` UNC path (the 9P filesystem bridge between Windows and WSL2). The 9P bridge does not faithfully translate Unix file permissions — Windows sees all files without the executable bit. Git's index stores these files as `100755` (executable), but when the SCM extension stats them through the UNC path, it sees `100644` (non-executable). That permission mismatch registers as a modification.

You can confirm this is a phantom diff by running:
```bash
git status          # Clean — nothing to commit
git ls-files -m     # Empty — no modifications
git diff            # Empty — no content changes
git ls-tree HEAD jekyll-caddy.sh  # Shows 100755 — executable in index
ls -la jekyll-caddy.sh            # Shows -rwxr-xr-x — executable on disk
```

If all of those are clean but the SCM panel still shows "M", the issue is filemode detection through the 9P bridge.

### What Doesn't Work

I tried several approaches before finding the solution:

- **`.gitattributes` with `eol=lf`** — This fixes line-ending phantom diffs but has no effect on permission/filemode diffs. The problem isn't line endings.
- **`git.path` pointing to a wrapper script** — I created `~/.local/bin/git-kiro` that injected `-c core.fileMode=false` and set `"git.path"` in both the Kiro user settings and workspace `.vscode/settings.json`. The SCM extension ignored it entirely — it appears to use its own git integration that doesn't honor `git.path` when connected via WSL Remote.
- **Global git attributes** (`~/.config/git/attributes`) — Same story. Attributes control line-ending normalization, not filemode comparison.

### The Fix: `core.fileMode=false` Per Repository

The only approach that works is setting `core.fileMode=false` directly in each repository's `.git/config`:

```bash
git config core.fileMode false
```

This tells git to stop comparing the executable bit between the index and the working tree. Files already committed as `100755` remain `100755` in the repository — this setting only affects the working-tree comparison.

Apply to all affected repos:
```bash
git -C ~/github/mcgarrah.github.io config core.fileMode false
git -C ~/github/jellyfin-plugin-media-integrity-scanner config core.fileMode false
git -C ~/github/k8s-proxmox config core.fileMode false
git -C ~/github/resume config core.fileMode false
```

For new clones, add it after cloning:
```bash
git clone <url> && git -C <repo> config core.fileMode false
```

### Why Not Set It Globally?

You could run `git config --global core.fileMode false` to apply it everywhere, but that affects all tools on the system — Claude Code, Antigravity (Gemini), terminal git, CI scripts. The per-repo approach isolates the workaround to just the repositories open in Kiro.

The tradeoff is minor: if you add a new shell script with `chmod +x`, git won't automatically detect the permission change. You'll need to explicitly tell git:
```bash
git update-index --chmod=+x newscript.sh
```

Since this only matters when adding *new* executable files (not editing existing ones), it's rarely an issue in practice.

### Why This Happens

The chain of events:

1. Kiro connects to WSL2 via `jeanp413.open-remote-wsl`
2. The built-in git SCM extension runs on the remote side
3. But it reads file stats through a code path that goes via the 9P bridge (`\\wsl$\`)
4. The 9P bridge strips Unix permission bits — all files appear as `644`
5. Git's index says `755` for shell scripts
6. The SCM extension sees `755 → 644` = modified

The Linux-native git binary doesn't have this problem because it reads permissions directly from the ext4 filesystem. The SCM extension's internal git implementation takes a different code path that hits the 9P translation layer.

### Supplementary: `.gitattributes` for Line Endings

While `.gitattributes` doesn't fix the permission issue, it's still worth adding for line-ending normalization — a separate class of phantom diffs that can occur with other file types:

```
# .gitattributes — normalize line endings for cross-platform sanity
*.sh text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.json text eol=lf
*.py text eol=lf
*.html text eol=lf
*.svg text eol=lf
*.png binary
*.jpg binary
*.pdf binary
```

This handles the case where a file is committed with LF but the 9P bridge serves it with CRLF (less common, but possible depending on mount options).

## Known Remaining Limitations

Even with these fixes, some quirks persist:

- **The tool is still named `execute_pwsh`** — This is cosmetic but confusing in logs. The name doesn't change the actual shell used.
- **File read/write tools use Windows UNC paths** — Kiro's file tools resolve paths as `\\wsl$\Ubuntu-24.04\...`. Shell commands must use native Linux paths. The agent needs to handle both.
- **The `cwd` parameter may still be unreliable** — For git operations, using `git -C /path/to/repo` is more reliable than depending on the `cwd` parameter.
- **Exit code reporting** — Even after fixes, the tool may still report non-zero exit codes for successful commands. This is a Kiro-side issue worth tracking.

## Filing a Bug

If you're still experiencing issues after these changes, file a bug at the [Kiro GitHub repository](https://github.com/kirodotdev/kiro/issues). The [tracking issue #17](https://github.com/kirodotdev/kiro/issues/17) covers WSL2 support broadly. For agent-specific shell execution problems, a separate issue may be warranted. Include:

- Your OS (Windows 11 + WSL2 distribution and version)
- Kiro version (Help → About)
- Open Remote - WSL extension version (`jeanp413.open-remote-wsl`)
- The terminal settings from your `settings.json`
- Example of garbled output from the agent

## Summary

The fix boils down to: **explicitly declare Linux terminal profiles** in Kiro's settings and **enable shell integration** in your RC files. VS Code inferred this correctly; Kiro (as of mid-2026) needs the explicit configuration.

| Component | File | Change |
|-----------|------|--------|
| Terminal profiles | `%APPDATA%\Kiro\User\settings.json` | Add `automationProfile.linux` and `profiles.linux` |
| Shell integration (zsh) | `~/.zshrc` | Source Kiro integration when `TERM_PROGRAM == kiro` |
| Shell integration (bash) | `~/.bashrc` | Source Kiro integration when `TERM_PROGRAM == kiro` |
| Agent context | `~/.kiro/steering/shell-environment.md` | Tell agent it's in Linux/zsh |
| Phantom SCM diffs | Each repo's `.git/config` | `core.fileMode=false` to suppress permission phantom diffs |
| Line-ending normalization | `.gitattributes` (per-repo) or `~/.config/git/attributes` (global) | `eol=lf` declarations for text files |

Once configured, Kiro's agent can reliably execute shell commands in your WSL2 environment — making the agentic coding experience actually functional for Linux-first developers on Windows hardware.

## Related

- [Kiro IDE on Windows: WSL2 Support via Open Remote Extension](/kiro-ide-wsl2-support-open-remote-extension/) — The prerequisite setup: installing `jeanp413.open-remote-wsl`, the `argv.json` requirement, the update breakage cycle, and recovery procedures.
- [Open Remote - WSL on Open VSX](https://open-vsx.org/extension/jeanp413/open-remote-wsl)
- [jeanp413/open-remote-wsl on GitHub](https://github.com/jeanp413/open-remote-wsl)
- [Kiro GitHub Issue #17](https://github.com/kirodotdev/kiro/issues/17) — WSL support tracking issue
- [Kiro IDE Documentation](https://kiro.dev/docs/)
