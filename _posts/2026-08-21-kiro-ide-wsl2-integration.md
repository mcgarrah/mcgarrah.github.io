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

After getting shell execution working, you may notice another oddity: Kiro's Source Control panel shows files as "modified" even when `git status` from the terminal reports a clean working tree. The phantom diffs almost always affect shell scripts (`.sh` files), though other text files can be hit too.

**Root cause:** Kiro's SCM panel accesses the WSL2 filesystem through the `\\wsl$\` UNC path. When the Windows-side git provider (or the SCM extension itself) reads these files through the 9P filesystem bridge, it may interpret line endings or file permissions differently than the Linux-native git. Shell scripts are the most common trigger because they have the executable bit set — and Windows/9P doesn't perfectly translate Unix permissions.

You can confirm this is a phantom diff by running:
```bash
git ls-files -m  # Should show nothing
git diff         # Should show nothing
```

If both are empty but the SCM panel still shows changes, the fix is to add a `.gitattributes` file that explicitly declares line endings:

```
# .gitattributes — prevents phantom diffs via \\wsl$\ UNC path access
*.sh text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
*.json text eol=lf
*.py text eol=lf
*.html text eol=lf
*.svg text eol=lf
*.png binary
*.jpg binary
*.webp binary
*.pdf binary
```

**Global vs per-repo:** You can set this globally so it applies to all repositories without adding a file to each one. Git reads global attributes from `~/.config/git/attributes` (the XDG default location on Linux). Create the file with the same content above — no `core.attributesFile` config entry needed, git finds it automatically.

```bash
mkdir -p ~/.config/git
cat > ~/.config/git/attributes << 'EOF'
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
EOF
```

Adding a per-repo `.gitattributes` is still worthwhile for portability — collaborators and CI will benefit from the explicit declarations — but the global file covers your local Kiro experience across all repositories immediately.

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
| Phantom SCM diffs | `~/.config/git/attributes` (global) or `.gitattributes` (per-repo) | Explicit `eol=lf` for text files |

Once configured, Kiro's agent can reliably execute shell commands in your WSL2 environment — making the agentic coding experience actually functional for Linux-first developers on Windows hardware.

## Related

- [Kiro IDE on Windows: WSL2 Support via Open Remote Extension](/kiro-ide-wsl2-support-open-remote-extension/) — The prerequisite setup: installing `jeanp413.open-remote-wsl`, the `argv.json` requirement, the update breakage cycle, and recovery procedures.
- [Open Remote - WSL on Open VSX](https://open-vsx.org/extension/jeanp413/open-remote-wsl)
- [jeanp413/open-remote-wsl on GitHub](https://github.com/jeanp413/open-remote-wsl)
- [Kiro GitHub Issue #17](https://github.com/kirodotdev/kiro/issues/17) — WSL support tracking issue
- [Kiro IDE Documentation](https://kiro.dev/docs/)
