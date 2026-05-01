---
title: "Kiro IDE on Windows: WSL2 Support via Open Remote Extension"
layout: post
categories: [technical, devtools, kiro]
tags: [kiro, vscode, wsl2, windows, linux, mcp, remote-development, open-vsx]
excerpt: "Kiro doesn't ship with Microsoft's WSL extension, and the official extension isn't available on Open VSX. The Open Remote - WSL extension by jeanp413 bridges the gap — but it requires an easy-to-miss argv.json configuration step, breaks predictably on Kiro updates, and has terminal routing quirks that will cost you an hour if you don't know about them. Here's the complete setup, the failure modes, and the recovery procedures."
description: "Complete guide to enabling WSL2 support in Kiro IDE on Windows using the Open Remote - WSL community extension. Covers the required argv.json configuration, kiro-server breakage recovery after updates, terminal default profile fix, MCP server execution within Linux, and known limitations."
date: 2026-05-03
last_modified_at: 2026-05-03
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-03
  date_modified: 2026-05-03
---

Kiro is a VS Code fork, but it doesn't include Microsoft's proprietary Remote - WSL extension. That extension isn't published to Open VSX (the extension marketplace Kiro uses), and Microsoft's marketplace terms restrict it to official VS Code builds. If you're running Kiro on Windows with WSL2 as your primary development environment, this is a hard stop — unless you know where to look.

> **Migration context:** On May 1, 2026, AWS published the [Amazon Q Developer end-of-support announcement](https://aws.amazon.com/blogs/devops/amazon-q-developer-end-of-support-announcement/). If you're migrating from Amazon Q Developer to Kiro on Windows, WSL2 support is likely a hard requirement. This article covers exactly that gap.

The [Open Remote - WSL](https://open-vsx.org/extension/jeanp413/open-remote-wsl) extension by jeanp413 fills this gap. It's a community-built, Open VSX-compatible implementation that enables WSL2 support in any VS Code fork, including Kiro. The [Kiro GitHub issue #17](https://github.com/kirodotdev/Kiro/issues/17) tracks the ongoing community experience — 38+ comments of workarounds, breakage reports, and fixes that inform everything in this article.

The extension works. It also breaks predictably on Kiro updates, has an easy-to-miss configuration requirement, and routes terminal commands to the wrong shell if you don't set a default profile. None of these are dealbreakers, but they'll cost you time if you don't know about them going in.

<!-- excerpt-end -->

## The Problem

VS Code's WSL integration is built on Microsoft's proprietary Remote Development extensions. These extensions are:

- Licensed exclusively for use with Microsoft's VS Code builds
- Published only to Microsoft's Visual Studio Marketplace, not Open VSX
- Not available in Kiro's extension marketplace

Without WSL support, Kiro on Windows can only access the Windows filesystem. Your Linux development environments, toolchains, and MCP servers running inside WSL2 are unreachable from the IDE. As multiple users in the tracking issue put it bluntly: Kiro is "completely useless" for Windows developers who do all their work inside WSL2.

Kiro itself acknowledges the gap — if you install the Linux version inside WSL2, it displays a message directing you to install the Windows version instead and use the remote extension approach.

## Installation and the argv.json Requirement

Install the extension from Kiro's extension panel or the command line:

```powershell
kiro --install-extension jeanp413.open-remote-wsl
```

**This is the step most people miss.** The extension requires proposed API access to function. Without it, the extension installs silently but does nothing. Enable it in your `~/.kiro/argv.json` file (or open it via the command palette: `Preferences: Configure Runtime Arguments`):

```json
{
    "enable-proposed-api": [
        "jeanp413.open-remote-wsl"
    ]
}
```

Restart Kiro after making this change. If you have other entries in `argv.json`, add the `enable-proposed-api` array alongside them — don't replace the file contents. If WSL commands don't appear in the command palette after installing the extension, this missing configuration is almost certainly the reason.

After installation, the command palette gains WSL-specific commands:

- `WSL: New Window` — Open a new Kiro window connected to your default WSL distribution
- `WSL: New Window using Distro...` — Choose a specific distribution
- `WSL: Open Folder in WSL...` — Open a Linux folder directly
- `WSL: Reopen Folder in WSL` — Switch the current folder to WSL context

## The Terminal Default Profile Gotcha

With the extension installed and a WSL2 folder open, Kiro's agentic chat will attempt to run terminal commands. By default, it routes them to PowerShell — not the WSL terminal. This means commands that should execute in your Linux environment run in Windows instead, producing confusing failures.

The fix is to set the WSL distribution as your default terminal profile. Add this to your Kiro settings (`%APPDATA%\Kiro\User\settings.json`):

```json
{
    "wsl.defaultDistro": "Ubuntu",
    "terminal.integrated.defaultProfile.windows": "WSL (Ubuntu)",
    "terminal.integrated.profiles.windows": {
        "WSL (Ubuntu)": {
            "path": "C:\\Windows\\System32\\wsl.exe",
            "args": ["-d", "Ubuntu"]
        }
    }
}
```

Replace `Ubuntu` with your distribution name. This ensures both manual terminal sessions and agent-initiated commands execute inside WSL2.

## Opening WSL2 Folders

From PowerShell or the Windows command line:

```powershell
# Open a specific Linux folder
kiro --folder-uri "vscode-remote://wsl+Ubuntu/home/username/projects"

# Open with the --remote flag
kiro --remote wsl+Ubuntu
```

From inside a WSL2 terminal:

```bash
# If the kiro CLI is on PATH (installed by the Windows Kiro installer)
kiro .
```

Note: launching `kiro .` from inside WSL2 doesn't always auto-detect the WSL context correctly. If Kiro opens in Windows mode instead of WSL mode, use the explicit `--folder-uri` or `--remote` flags from PowerShell, or use the command palette (`WSL: Open Folder in WSL...`) from within Kiro.

A community-contributed launcher script addresses this by detecting whether the path is a WSL path and automatically constructing the correct `--folder-uri`:

```bash
#!/bin/bash
# Save as /usr/local/bin/kiro-wsl or replace the Kiro bin/kiro script
KIRO_ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"

ARGS=()
for arg in "$@"; do
    if [[ "$arg" != -* ]] && { [ -d "$arg" ] || [[ "$arg" == "." ]] || [[ "$arg" == ".." ]]; }; then
        FOLDER="$(realpath -m "$arg")"
        ARGS+=("--folder-uri" "vscode-remote://wsl+${WSL_DISTRO_NAME}${FOLDER}")
    elif [[ "$arg" != -* ]] && [ -f "$arg" ]; then
        FILE="$(realpath -m "$arg")"
        ARGS+=("--file-uri" "vscode-remote://wsl+${WSL_DISTRO_NAME}${FILE}")
    else
        ARGS+=("$arg")
    fi
done

"$KIRO_ROOT/Kiro.exe" "${ARGS[@]}" </dev/null &>/dev/null &
disown
```

## The Kiro Update Breakage Cycle

This is the most significant operational issue. When Kiro updates, the kiro-server binary installed inside WSL2 (at `~/.kiro-server/`) becomes incompatible with the new Kiro version. The extension tries to install a new server, and the installation script can fail — sometimes due to stale cached binaries, sometimes due to quoting bugs in the generated bash script.

The symptom is always the same:

```
[Error] Error resolving authority
Error: Couldn't install vscode server on remote server,
       install script returned non-zero exit status
```

### Recovery Procedure

When WSL2 connectivity breaks after a Kiro update:

```bash
# Inside WSL2
rm -rf ~/.kiro-server
```

Then restart Kiro and reconnect to WSL2. The extension will perform a fresh server installation. This has been the reliable fix across multiple Kiro versions (confirmed working through v0.1.25 and beyond in the tracking issue).

### The Server Installation Script Quoting Bug

In some Kiro versions, the server installation script that the extension generates contains improperly escaped single quotes (`'\''`) that fail in bash. If the `rm -rf ~/.kiro-server` approach doesn't resolve the issue:

1. Open Kiro's Output panel and select the WSL extension output channel
2. Copy the full bash script content from the output
3. Save it to a file inside WSL2 (e.g., `~/kiro-server-install.sh`)
4. Fix the three quoting errors (look for `'\''` patterns that break bash parsing)
5. Run the fixed script manually: `bash ~/kiro-server-install.sh`

This is a known issue in the community extension's server bootstrapping code. The manual fix is tedious but reliable.

## WSL2 Path Escaping Issues

Kiro's agent sometimes generates Windows-style UNC paths when it should be using Linux paths inside WSL2. Commands like:

```
cd "\\wsl.localhost\Ubuntu\home\username\project"
```

...fail because the agent is constructing a Windows UNC path instead of the native Linux path `/home/username/project`. This is a known limitation of how the remote extension bridges the two filesystems. The agent doesn't always correctly detect that it's operating in a Linux context.

There's no configuration fix for this — it's a behavioral issue in how Kiro's agent interacts with the remote extension's filesystem abstraction. When it happens, the workaround is to manually correct the path in the terminal or re-prompt the agent with explicit Linux path context.

## Chat Window Disabled: "Unsafe Environment"

Some users report that after connecting to WSL2, the Kiro chat sidebar shows "Drag a view here to display" or displays an "unsafe environment" warning that disables the chat window entirely. This appears to be related to workspace trust settings.

If you encounter this:

1. Open the command palette and run `Workspaces: Manage Workspace Trust`
2. Trust the WSL2 workspace folder
3. If the chat window still doesn't appear, close the WSL2 window and reopen it via `WSL: New Window`

The alternative approach — running the Linux version of Kiro natively inside WSL2 via WSLg — avoids this issue entirely but introduces its own problems (GUI scaling issues on multi-monitor setups, occasional terminal hangs, and general WSLg instability).

## MCP Servers in WSL2

This is where WSL2 support becomes particularly relevant for Kiro's agentic workflows. MCP servers that depend on Linux toolchains — Python `uvx` packages, Node.js tools, Docker containers — run natively inside WSL2 rather than through Windows compatibility layers.

When Kiro connects to WSL2 via the Open Remote extension, the kiro-agent's MCP server processes spawn inside the Linux environment. This means:

- `uvx`-based MCP servers use the Linux Python installation
- Docker-based MCP servers connect to the WSL2 Docker daemon
- File paths in MCP server configs use Linux paths (`/home/...`), not Windows paths
- Environment variables resolve from the Linux shell, not PowerShell

### WSL2-Side Configuration

The `~/.kiro` directory inside WSL2 is independent from `%USERPROFILE%\.kiro` on the Windows side. When connected to WSL2, Kiro reads:

```
/home/username/.kiro/
├── settings/mcp.json    # MCP servers configured for Linux execution
├── powers/              # Powers available in Linux context
├── hooks/               # Hooks that run in Linux shell
├── steering/            # Steering rules
└── secrets/             # Linux-side credentials
```

This natural separation means your Windows-side Kiro configuration (with Windows-native MCP servers) and your WSL2-side configuration (with Linux-native MCP servers) are already isolated by the filesystem boundary. You don't need the [persona isolation techniques](/kiro-ide-parallel-personas-director-developer/) to separate Windows and Linux configs — the remote extension handles that by virtue of running in a different filesystem.

## The Alternative: Running Kiro Natively in WSL2

Several users in the tracking issue have tried running the Linux `.deb` version of Kiro directly inside WSL2 using WSLg (Windows Subsystem for Linux GUI). This bypasses the remote extension entirely — Kiro runs as a native Linux application with direct filesystem access.

It works, with caveats:

- **Multi-monitor scaling**: WSLg doesn't respect Windows display scaling. On multi-monitor setups (especially mixed DPI), the mouse cursor may be oversized and click targets may be offset.
- **Terminal stability**: The integrated terminal can hang after extended use in some configurations.
- **GTK dependencies**: Requires up-to-date GTK packages in the WSL2 distribution. Missing or outdated libraries cause rendering issues.
- **Performance**: Noticeably slower than the remote extension approach for UI rendering.

Kiro itself discourages this approach — the Linux installer displays a message suggesting you use the Windows version with the remote extension instead. But for developers who find the remote extension's breakage cycle unacceptable, it's a viable if rough alternative.

## Relationship to Persona Isolation

If you're running [parallel Kiro personas](/kiro-ide-parallel-personas-director-developer/) on Windows, WSL2 adds a third dimension to the isolation story. The Windows-side personas (director and developer) each have their own `%USERPROFILE%\.kiro-*` directories. When either persona connects to WSL2, it sees the single `/home/username/.kiro/` inside Linux.

For most workflows this is fine — the WSL2 config is developer-focused by nature. The more common pattern is: director persona runs on Windows (Atlassian, GitLab, observability MCPs), developer persona connects to WSL2 (code toolchains, Docker, Linux-native MCP servers).

## Setup Checklist

1. Install WSL2 with your preferred distribution (`wsl --install -d Ubuntu`)
2. Install the Open Remote - WSL extension in Kiro (`jeanp413.open-remote-wsl`)
3. **Enable proposed API** in `~/.kiro/argv.json` — this is the step most people miss
4. Restart Kiro
5. Set WSL as the default terminal profile in Kiro settings
6. Open a WSL2 folder (command palette → `WSL: New Window`)
7. On first connection, allow the kiro-server installation inside WSL2
8. Configure `~/.kiro/settings/mcp.json` inside WSL2 for Linux-native MCP servers
9. Verify MCP servers start correctly from the Kiro terminal (should show Linux paths)

### After Every Kiro Update

1. If WSL2 connectivity breaks: `rm -rf ~/.kiro-server` inside WSL2, then restart Kiro
2. If that doesn't work: extract the server install script from Kiro's Output panel, fix quoting, run manually
3. Verify `argv.json` still contains the `enable-proposed-api` entry (updates occasionally reset it)

## The State of Things

WSL2 support in Kiro is functional but fragile. The community extension works, the configuration is straightforward once you know about `argv.json`, and the recovery procedure after updates is reliable. But it's a community-maintained bridge over a gap that arguably shouldn't exist in a product targeting Windows developers.

The [tracking issue](https://github.com/kirodotdev/Kiro/issues/17) remains open with the `pending-maintainer-response` label. Multiple users have requested either native WSL support or at minimum official documentation for the community extension setup. Until one of those happens, this article and that issue thread are the primary references.

## References

- [Kiro GitHub Issue #17: WSL Support](https://github.com/kirodotdev/Kiro/issues/17) — The canonical community thread
- [Open Remote - WSL on Open VSX](https://open-vsx.org/extension/jeanp413/open-remote-wsl)
- [jeanp413/open-remote-wsl on GitHub](https://github.com/jeanp413/open-remote-wsl)
- [WSL2 Documentation](https://learn.microsoft.com/en-us/windows/wsl/)
- [Kiro IDE: Running Parallel Personas](/kiro-ide-parallel-personas-director-developer/) — Companion article on persona isolation
