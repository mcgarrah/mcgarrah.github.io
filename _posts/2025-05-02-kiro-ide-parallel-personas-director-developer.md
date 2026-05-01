---
title: "Kiro IDE: Running Parallel Personas for Director and Developer Workflows"
layout: post
categories: [technical, devtools, kiro]
tags: [kiro, vscode, ide, personas, macos, windows, mcp, powers, configuration, productivity]
excerpt: "Kiro's ~/.kiro directory stores powers, hooks, agents, and MCP server configs globally — but there's no built-in way to switch between profiles. If you need a Senior Director persona loaded with Atlassian, GitLab, and observability MCPs running alongside a stripped-down developer persona focused on code, you have to get creative. Here's how the path resolution actually works and three approaches to running both simultaneously on macOS and Windows."
description: "Deep technical analysis of Kiro IDE's configuration path resolution and practical approaches to running parallel Kiro instances with isolated powers, hooks, agents, and MCP server configurations on macOS and Windows 11 Pro."
date: 2025-05-02
last_modified_at: 2025-05-02
published: true
seo:
  type: BlogPosting
  date_published: 2025-05-02
  date_modified: 2025-05-02
---

Kiro is a compelling IDE — particularly for agentic workflows where powers, hooks, and MCP servers turn it into something closer to a command center than a text editor. The problem surfaces when you need that command center configured two fundamentally different ways at the same time.

My use case: a Senior Director persona loaded with Atlassian (Jira, Confluence), GitLab, NewRelic, Wiz, and AWS pricing MCPs for ticket management, architecture reviews, and operational oversight — running alongside a developer persona stripped down to Terraform, AWS docs, and code-focused tooling. These configurations don't overlap well. The director's MCP servers add latency, consume resources, and clutter the tool list when I'm writing code. The developer's minimal setup lacks the integrations I need when triaging incidents or managing a sprint.

VS Code solved this years ago with profiles. Kiro inherited the `--profile` flag, but it doesn't do what you'd expect.

<!-- excerpt-end -->

## The Problem: What `--profile` Actually Isolates

Kiro has two separate configuration stores:

| Store | Location (macOS) | Location (Windows) | `--profile` isolates? |
|-------|-------------------|---------------------|----------------------|
| VS Code state | `~/Library/Application Support/Kiro/` | `%APPDATA%\Kiro\` | Yes |
| Kiro agent config | `~/.kiro/` | `%USERPROFILE%\.kiro\` | No |

The `--profile` flag creates named profiles under the VS Code state directory — separate editor settings, extensions, keybindings, and UI state. That's the inherited VS Code profile system working as designed.

But everything that makes Kiro *Kiro* lives in `~/.kiro/`:

```
~/.kiro/
├── agents/          # Agent persona definitions
├── hooks/           # Automation hooks (AWS guard rails, VPN checks)
├── powers/          # MCP power integrations (Atlassian, GitLab, etc.)
├── settings/
│   └── mcp.json     # MCP server configurations
├── steering/        # Steering rules
├── skills/          # Custom skills
└── secrets/         # Encrypted credentials
```

All profiles share this single `~/.kiro/` directory. There's no flag, environment variable, or configuration option to redirect it.

## How Kiro Resolves the `~/.kiro` Path

I traced the path resolution through Kiro's source to understand the full chain. There are two independent code paths that both land on `~/.kiro`:

### Main Process (Electron Layer)

The main Electron process resolves user data through a priority chain:

```
1. VSCODE_PORTABLE env var  → join(PORTABLE, "user-data")
2. VSCODE_APPDATA env var   → join(VSCODE_APPDATA, nameShort)
3. --user-data-dir flag     → direct path
4. Platform default         → macOS: ~/Library/Application Support/Kiro
                              Windows: %APPDATA%\Kiro
```

For `~/.kiro` specifically (argv.json, extensions, policy), it uses:

```javascript
// product.json: dataFolderName = ".kiro"
get argvResource() {
    const portable = process.env.VSCODE_PORTABLE;
    return portable
        ? URI.file(join(portable, "argv.json"))
        : joinPath(this.userHome, this.product.dataFolderName, "argv.json");
}
```

`this.userHome` comes from `os.homedir()`, which on both macOS and Windows reads the `HOME` / `USERPROFILE` environment variable.

### Kiro Agent Extension (Powers, Hooks, Agents)

The kiro-agent extension — the code that actually loads powers, hooks, agents, and steering — has its own `getHomeDir` function:

```javascript
var getHomeDir = () => {
    const { HOME, USERPROFILE, HOMEPATH, HOMEDRIVE = `C:${path.sep}` } = process.env;
    if (HOME) return HOME;
    if (USERPROFILE) return USERPROFILE;
    if (HOMEPATH) return `${HOMEDRIVE}${HOMEPATH}`;
    // ... fallback to os.homedir()
};
```

Then it hardcodes the `.kiro` string:

```javascript
const powersPath = path.join(this.homeDir, ".kiro", "powers", "installed", name);
const mcpSettingsPath = path.join(this.homeDir, ".kiro", "settings", "mcp.json");
const steeringDir = path.join(this.homeDir, ".kiro", "steering");
```

The string `".kiro"` is not read from `product.json` — it's a literal in the extension bundle. This is the key constraint that shapes every solution.

## What Doesn't Work

Before covering what does work, here's what I evaluated and rejected:

**`--profile` flag**: Only isolates VS Code state, not `~/.kiro/`. Useless for this problem.

**`VSCODE_PORTABLE` env var**: Redirects the VS Code data path chain (user-data, extensions, argv), but the kiro-agent extension ignores it entirely and still reads `~/.kiro/` from `HOME`/`USERPROFILE`. Partial solution at best.

**`--user-data-dir` flag**: Same limitation — redirects VS Code state but not the kiro-agent's `~/.kiro/` resolution.

**Symlink swapping**: Works for sequential use but not parallel. Two simultaneous Kiro instances would race on the symlink target.

## Approach 1: HOME/USERPROFILE Override

The kiro-agent checks `HOME` (macOS/Linux) or `USERPROFILE` (Windows) before falling back to `os.homedir()`. Override it per instance, and each Kiro resolves a different `~/.kiro`.

### macOS

Create a fake home directory per persona that symlinks everything back to the real home except `.kiro`:

```bash
# One-time setup
REAL_HOME="$HOME"
PERSONA_HOME="$HOME/kiro-homes/engineer"
mkdir -p "$PERSONA_HOME"

# Symlink .kiro to persona-specific config
cp -R ~/.kiro ~/.kiro-engineer
ln -sfn ~/.kiro-engineer "$PERSONA_HOME/.kiro"

# Symlink everything else Kiro or shells might need
for item in .zshrc .zshenv .ssh .gnupg .gitconfig .config Library; do
    ln -sfn "$REAL_HOME/$item" "$PERSONA_HOME/$item" 2>/dev/null
done

# Launch
env HOME="$PERSONA_HOME" \
    kiro --user-data-dir "$REAL_HOME/Library/Application Support/Kiro-Engineer"
```

### Windows (PowerShell)

```powershell
$realProfile = $env:USERPROFILE
$personaHome = "$realProfile\kiro-homes\engineer"
New-Item -ItemType Directory -Force -Path $personaHome

# Copy .kiro config
Copy-Item -Recurse "$realProfile\.kiro" "$realProfile\.kiro-engineer"

# Symlink .kiro in fake home (requires Developer Mode or admin)
New-Item -ItemType SymbolicLink -Path "$personaHome\.kiro" -Target "$realProfile\.kiro-engineer"

# Symlink essentials back to real profile
foreach ($item in @('.ssh', '.gitconfig', 'AppData', 'Documents', 'Downloads')) {
    if (Test-Path "$realProfile\$item") {
        New-Item -ItemType SymbolicLink -Path "$personaHome\$item" -Target "$realProfile\$item" -ErrorAction SilentlyContinue
    }
}

# Launch
$env:USERPROFILE = $personaHome
& "$env:LOCALAPPDATA\Programs\Kiro\Kiro.exe" --user-data-dir "$realProfile\AppData\Roaming\Kiro-Engineer"
$env:USERPROFILE = $realProfile
```

**Trade-offs**: Works on both platforms. The fake home directory is the main annoyance — any tool that resolves paths relative to `HOME`/`USERPROFILE` sees the fake home. The symlinks cover common cases, but you'll occasionally discover something missing and need to add another symlink. On Windows, creating symlinks requires either Developer Mode enabled or an elevated prompt.

## Approach 2: Duplicate App with Patched product.json

Copy the Kiro installation, modify `product.json` to change the `dataFolderName`, and patch the kiro-agent extension to match. Each copy is a fully independent Kiro instance.

### macOS

```bash
# Copy the app bundle
cp -R /Applications/Kiro.app /Applications/Kiro-Engineer.app

# Patch product.json
python3 -c "
import json
p = '/Applications/Kiro-Engineer.app/Contents/Resources/app/product.json'
with open(p) as f: d = json.load(f)
d['dataFolderName'] = '.kiro-engineer'
d['darwinBundleIdentifier'] = 'dev.kiro.desktop.engineer'
with open(p, 'w') as f: json.dump(d, f, indent=2)
"

# Patch the kiro-agent extension (hardcoded ".kiro" string)
sed -i '' 's/".kiro"/".kiro-engineer"/g' \
    /Applications/Kiro-Engineer.app/Contents/Resources/app/extensions/kiro.kiro-agent/dist/extension.js

# Re-sign (macOS requires valid signature)
codesign --remove-signature /Applications/Kiro-Engineer.app
codesign --force --deep --sign - /Applications/Kiro-Engineer.app

# Create the engineer's config directory
cp -R ~/.kiro ~/.kiro-engineer
```

The `darwinBundleIdentifier` change is critical — macOS uses it to distinguish app instances. With different bundle IDs, both apps appear separately in the Dock and can run truly in parallel.

### Windows

No code signing needed. The parallel-instance constraint on Windows is a named mutex:

```powershell
# Copy the installation
$source = "$env:LOCALAPPDATA\Programs\Kiro"
$dest = "$env:LOCALAPPDATA\Programs\Kiro-Engineer"
Copy-Item -Recurse -Path $source -Destination $dest

# Patch product.json
$productJson = "$dest\resources\app\product.json"
$product = Get-Content $productJson | ConvertFrom-Json
$product.dataFolderName = ".kiro-engineer"
$product.win32MutexName = "kiro-engineer"
$product.win32AppUserModelId = "Kiro-Engineer"
$product | ConvertTo-Json -Depth 10 | Set-Content $productJson

# Patch kiro-agent extension
$extJs = "$dest\resources\app\extensions\kiro.kiro-agent\dist\extension.js"
(Get-Content $extJs -Raw) -replace '".kiro"', '".kiro-engineer"' | Set-Content $extJs

# Create the engineer's config directory
Copy-Item -Recurse "$env:USERPROFILE\.kiro" "$env:USERPROFILE\.kiro-engineer"

# Optional: create Start Menu shortcut
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Kiro Engineer.lnk")
$shortcut.TargetPath = "$dest\Kiro.exe"
$shortcut.Save()
```

The `win32MutexName` change is the Windows equivalent of `darwinBundleIdentifier` — without it, the second instance would detect the mutex and hand off to the first instance instead of launching independently.

**Trade-offs**: Cleanest runtime behavior — no fake home directories, no symlink gymnastics, both instances use your real home directory for git, SSH, and everything else. The cost is maintenance: you re-apply the patch after every Kiro update. A 10-line script handles it.

## Approach 3: Portable Mode (Partial Solution)

Kiro inherits VS Code's portable mode. If a specific directory exists, Kiro auto-sets `VSCODE_PORTABLE` and redirects all VS Code state into it:

| Platform | Portable directory |
|----------|-------------------|
| macOS | `/Applications/Kiro.app/Contents/Resources/kiro-portable-data/` |
| Windows | `%LOCALAPPDATA%\Programs\Kiro\data\` |

```bash
# macOS: enable portable mode
mkdir -p "/Applications/Kiro.app/Contents/Resources/kiro-portable-data/tmp"

# Windows (PowerShell): enable portable mode
New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\Programs\Kiro\data\tmp"
```

This redirects user-data, extensions, argv.json, and policy — but **not** the kiro-agent's `~/.kiro/` resolution. Powers, hooks, agents, and steering still come from the home directory. Portable mode is useful for carrying a self-contained Kiro on a USB drive, but it doesn't solve the persona isolation problem on its own.

## Recommended Setup

For parallel personas, I recommend Approach 2 (duplicate app + patch) because:

- Both instances run simultaneously with full isolation
- No fake home directories or symlink maintenance
- Each instance appears as a separate app in the Dock / Taskbar
- Git, SSH, and shell tools work normally from both instances
- The only maintenance is re-running the patch script after Kiro updates

### Post-Setup: Stripping the Developer Persona

After creating `~/.kiro-engineer`, remove the director-specific integrations:

```bash
# Remove director powers
rm -rf ~/.kiro-engineer/powers/atlassian
rm -rf ~/.kiro-engineer/powers/gitlab
rm -rf ~/.kiro-engineer/powers/github

# Remove director agents
rm ~/.kiro-engineer/agents/app-expert-*.md
rm ~/.kiro-engineer/agents/iac-expert-*.md

# Remove director hooks
rm ~/.kiro-engineer/hooks/aws-*.kiro.hook
rm ~/.kiro-engineer/hooks/vpn-check-gitlab.kiro.hook
```

Then edit `~/.kiro-engineer/settings/mcp.json` to keep only coding-relevant MCP servers (Terraform, AWS docs) and remove Atlassian, GitLab, NewRelic, and Wiz.

### Update Automation

#### macOS (`update-kiro-engineer.sh`)

```bash
#!/bin/bash
set -euo pipefail

APP="/Applications/Kiro-Engineer.app"
SRC="/Applications/Kiro.app"
PRODUCT="$APP/Contents/Resources/app/product.json"
EXTENSION="$APP/Contents/Resources/app/extensions/kiro.kiro-agent/dist/extension.js"

echo "Updating Kiro-Engineer from Kiro..."
rm -rf "$APP"
cp -R "$SRC" "$APP"

python3 -c "
import json
with open('$PRODUCT') as f: d = json.load(f)
d['dataFolderName'] = '.kiro-engineer'
d['darwinBundleIdentifier'] = 'dev.kiro.desktop.engineer'
with open('$PRODUCT', 'w') as f: json.dump(d, f, indent=2)
"

sed -i '' 's/\".kiro\"/\".kiro-engineer\"/g' "$EXTENSION"

codesign --remove-signature "$APP"
codesign --force --deep --sign - "$APP"

echo "Done. ~/.kiro-engineer/ config is preserved."
```

#### Windows (`Update-KiroEngineer.ps1`)

```powershell
$source = "$env:LOCALAPPDATA\Programs\Kiro"
$dest = "$env:LOCALAPPDATA\Programs\Kiro-Engineer"

Write-Host "Updating Kiro-Engineer from Kiro..."
Remove-Item -Recurse -Force $dest -ErrorAction SilentlyContinue
Copy-Item -Recurse -Path $source -Destination $dest

$productJson = "$dest\resources\app\product.json"
$product = Get-Content $productJson | ConvertFrom-Json
$product.dataFolderName = ".kiro-engineer"
$product.win32MutexName = "kiro-engineer"
$product.win32AppUserModelId = "Kiro-Engineer"
$product | ConvertTo-Json -Depth 10 | Set-Content $productJson

$extJs = "$dest\resources\app\extensions\kiro.kiro-agent\dist\extension.js"
(Get-Content $extJs -Raw) -replace '".kiro"', '".kiro-engineer"' | Set-Content $extJs

Write-Host "Done. $env:USERPROFILE\.kiro-engineer\ config is preserved."
```

## Platform-Specific Notes

### macOS

- Ad-hoc code signing (`codesign --force --deep --sign -`) is required after modifying any file inside the `.app` bundle. macOS Gatekeeper will block unsigned modified apps.
- The `darwinBundleIdentifier` must differ between copies for macOS to treat them as separate applications. Without this, the second instance may not launch or may share window state with the first.
- Kiro auto-updates only affect the original `/Applications/Kiro.app`. The engineer copy must be manually updated via the script above.

### Windows 11 Pro

- No code signing is required for locally installed applications.
- The `win32MutexName` must differ between copies. Windows uses a named kernel mutex for single-instance enforcement — identical mutex names cause the second launch to hand off to the existing instance.
- If Kiro was installed via the system installer (to `C:\Program Files\Kiro\`), copying and patching requires administrator privileges. The user installer (`%LOCALAPPDATA%\Programs\Kiro\`) does not have this limitation.
- Creating symbolic links on Windows requires either Developer Mode enabled in Settings or an elevated PowerShell prompt. This only matters for Approach 1 (HOME override). Approach 2 doesn't need symlinks.
- Kiro auto-updates only affect the original installation. The engineer copy must be manually updated.

## What Kiro Could Do Natively

The underlying issue is that the kiro-agent extension hardcodes `".kiro"` as a string literal rather than reading `dataFolderName` from `product.json` or exposing a configuration option. If the agent resolved its config directory through the same `dataFolderName` mechanism the main process uses, the `--profile` flag or `--user-data-dir` could potentially isolate everything.

Even simpler: a `KIRO_HOME` environment variable that overrides the `~/.kiro` path would eliminate the need for any of these workarounds. VS Code's `VSCODE_PORTABLE` demonstrates the pattern — Kiro just needs to extend it to the agent layer.

Until then, the duplicate-and-patch approach works reliably on both platforms. The friction is real, but the workaround is a one-time setup plus a 10-second script after updates.
