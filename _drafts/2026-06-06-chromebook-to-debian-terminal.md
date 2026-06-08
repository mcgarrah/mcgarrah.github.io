---
title: "Turning a $79 Chromebook into a Debian Linux Terminal"
layout: post
categories: [technical]
tags: [chromeos, linux, debian, development]
excerpt: "Three paths to running Debian on a Lenovo IdeaPad 3 Chromebook — from the sandboxed container you already have, to a full bare-metal installation that reclaims every byte of RAM for terminal work."
description: "Evaluating three approaches to running Debian Linux on a budget Chromebook: Crostini containers, Developer Mode with legacy boot, and full UEFI firmware replacement via MrChromebox. Optimizing for a text-console-only workflow on 4GB RAM."
---

In my [previous post](/drafts/2026-06-05-claude-on-chromeos), I set up Claude Code on a Lenovo IdeaPad 3 Chromebook (11IGL05) — a $79 clearance machine with a Celeron N4020 and 4GB RAM. It works, but the memory constraints are real. ChromeOS consumes 1.5–2GB just existing, leaving precious little headroom for a Linux container running Claude Code.

That got me thinking: what if I stripped this thing down to bare Debian with nothing but a text console? No desktop environment, no ChromeOS overhead, no Wayland compositor burning RAM. Just a TTY, tmux, and Claude Code.

<!-- excerpt-end -->

I'm a terminal session guy anyway. My actual workflow on this machine is: open terminal, clone repo, run `claude`, push commits. I don't need a browser on this device — I have a phone for that. So the question becomes: what's the most efficient path from "ChromeOS appliance" to "Debian terminal appliance"?

There are three options, each with different trade-offs in reversibility, complexity, and resource efficiency.

## Option 1: Crostini (What I'm Already Running)

This is the default Linux experience on ChromeOS. It runs a Debian container inside a VM (managed by `termina`), sandboxed from the host OS.

**How it works:**
- ChromeOS runs the `crosvm` virtual machine manager
- Inside that VM, a Debian container provides your Linux environment
- You interact with it through the Terminal app or SSH

**Pros:**
- Zero risk — reversible with a single toggle in Settings
- Already set up and working
- ChromeOS handles WiFi, Bluetooth, display, power management
- Secure — the VM boundary isolates Linux from ChromeOS

**Cons:**
- ChromeOS still consumes 1.5–2GB RAM as the host
- The VM layer adds overhead on top of that
- 9P filesystem bridge between ChromeOS and the container is slow
- Processes die when you close the lid (default behavior)
- You're running three layers: ChromeOS → VM → Container

**RAM available for your work:** ~1.5–2GB after ChromeOS and VM overhead on a 4GB system.

For Claude Code, this is tight. It works for small repos and focused sessions, but you're always one background Chrome process away from an OOM kill on your container.

## Option 2: Developer Mode + RW_LEGACY Boot

This keeps ChromeOS intact but adds the ability to boot Linux from external media (USB or SD card) using a legacy BIOS payload.

**How it works:**
1. Enable Developer Mode (Esc + Refresh + Power at boot → Ctrl+D to confirm)
2. From a ChromeOS terminal (Ctrl+Alt+T → `shell`), run MrChromebox's firmware utility script
3. Install the RW_LEGACY payload — this adds a SeaBIOS or alternative bootloader without replacing the stock firmware
4. Boot from USB/SD by pressing Ctrl+L at the Developer Mode boot screen

**Pros:**
- Reversible — disabling Developer Mode restores stock ChromeOS
- No hardware disassembly required
- You can dual-boot: ChromeOS for daily use, Debian from USB for dev sessions
- Full access to all 4GB RAM when booted into Linux

**Cons:**
- Developer Mode disables verified boot — you get a warning screen on every power-on
- 30-second boot delay (or press Ctrl+D/Ctrl+L to skip)
- NVRAM for boot variables is limited with RW_LEGACY — some Linux features won't persist across reboots
- Booting from SD/USB is slower than internal eMMC
- Anyone pressing Space at the warning screen will powerwash the device back to stock

**RAM available for your work:** All 4GB minus kernel and minimal system overhead. A text-only Debian install with no desktop environment would leave ~3.5GB free.

This is the "try before you commit" option. Install Debian onto a USB stick or SD card, boot from it, and see how the hardware behaves with full Linux. If it works, you can graduate to Option 3.

## Option 3: Full UEFI Firmware Replacement (MrChromebox)

This replaces the Chromebook's stock firmware entirely with a standard UEFI implementation, turning the hardware into a generic x86_64 laptop that can boot any OS from internal storage.

**How it works:**
1. Enable Developer Mode
2. Disable firmware write-protect — on Gemini Lake (N4020) boards, this typically requires opening the case and temporarily disconnecting the battery
3. Run MrChromebox's firmware utility script and select "Install/Update UEFI (Full ROM) Firmware"
4. Boot from a Debian USB installer and install to the internal 64GB eMMC
5. You now have a standard Debian laptop

**Prerequisites:**
- Confirm your board name supports UEFI Full ROM in MrChromebox (check the Developer Mode screen or `chrome://version` → last word of "Platform" for your board name)
- A USB-C to USB-A adapter or hub for the installer USB (unless you have a USB-C boot drive)
- Willingness to open the case — this is a $79 machine, so the stakes are low
- Back up the stock firmware when the script offers (save to USB, not internal storage)

**Pros:**
- ChromeOS is gone — all resources go to your Linux install
- Boots from internal eMMC at full speed
- Standard UEFI means standard Linux kernel support, NVRAM, proper boot management (GRUB/systemd-boot)
- No boot warning screens, no Developer Mode quirks
- Full 4GB RAM available to Linux
- The machine behaves like any other laptop

**Cons:**
- Irreversible without the firmware backup (keep that USB safe)
- Hardware disassembly required to disable write-protect
- If the flash fails, you have a brick (low risk with MrChromebox, but non-zero)
- Some Chromebook hardware may have limited Linux driver support (trackpad, audio, suspend/resume)
- You lose ChromeOS entirely — no going back without reflashing

**RAM available for your work:** All 4GB. A minimal Debian text-console install (no X11, no Wayland, no desktop environment) uses roughly 150–300MB at idle. That leaves ~3.7GB for Claude Code, tmux, git, and whatever else you need.

## The Terminal-Only Configuration

Regardless of which option gets Linux onto bare metal (Option 2 or 3), the target configuration is the same: a minimal Debian installation optimized for terminal-only work.

**Base install:**
- Debian 12 (Bookworm) netinstall — deselect all desktop environment tasks during the installer
- Only select "SSH server" and "standard system utilities"

**Post-install packages:**

```bash
sudo apt install -y \
  tmux \
  git \
  curl \
  wget \
  htop \
  vim \
  openssh-client \
  ca-certificates \
  gnupg
```

**Install Claude Code:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Optional but useful:**

```bash
sudo apt install -y \
  fzf \
  ripgrep \
  jq \
  tree \
  unzip
```

**What you don't install:**
- No X11, no Wayland, no display manager
- No desktop environment (GNOME, KDE, XFCE — none of it)
- No GUI text editors
- No browser (you have a phone)

**Expected idle memory footprint:** 150–300MB for the kernel, systemd, and basic services. That's it.

## Inspiration: The Writerdeck Concept

This idea isn't new. Veronica Explains has an excellent [video](https://www.youtube.com/watch?v=E7vFdy4BEAY) and [blog post](https://veronicaexplains.net/my-first-writerdeck/) on building a "Writerdeck" — a tty-only laptop for maximum focus. She took a System76 Galago Pro, installed console-only Debian Trixie (no X11, no Wayland, no desktop), and set up a dedicated writing environment in about 20 minutes. Her [FAQ follow-up](https://veronicaexplains.net/writerdeck-faq/) covers the inevitable questions about why not just use a desktop with no browser, or switch to a TTY on an existing system.

Her setup solves the exact same technical problems we need to address for a "coderdeck":

- **`kmscon`** — A userspace terminal emulator that replaces the kernel's built-in virtual terminals. It provides scalable fonts (`Ctrl-Plus`/`Ctrl-Minus` to resize, like a browser), more than 16 colors, and proper Unicode support. On Debian Trixie it's available from backports. This is the key piece for making a TTY usable on a modern screen without a GUI.
- **`network-manager` + `nm-tui`** — A curses-based TUI for WiFi management. Connect to hotspots, manage saved networks, all without a browser or desktop. Essential for our use case since Claude Code needs network access.
- **`tmux`** — Terminal multiplexing with a status bar showing battery level (via `acpi`) and brightness control (via `light` bound to function keys). This gives you pane tiling, detachable sessions, and system info without any GUI.
- **Autologin via kmscon** — Edit the kmscon systemd service to auto-login on boot, then launch tmux from `.bashrc` on the primary TTY. Open the lid, you're at a prompt in seconds.

The [writerdeckOS project](https://github.com/tinkersec/tinkerdeckos) takes this further with a turn-key OS image that explicitly supports Chromebooks with 64-bit Intel/AMD processors — which is exactly our hardware.

My use case differs from a writerdeck in one important way: I need persistent network access (for Claude Code's API calls and git operations). A pure writerdeck intentionally removes networking to eliminate distraction. But the underlying TTY configuration — kmscon for font scaling, tmux for session management, and the philosophy of radical minimalism — translates directly to a "coderdeck" setup.

## TTY Configuration Details

Running a TTY-only system on an 11.6" 1366×768 display requires deliberate configuration. The default Linux console font is roughly 8×16 pixels — workable on this resolution but not comfortable for long sessions.

### kmscon (Recommended)

Based on Veronica's writerdeck setup, `kmscon` is the clear choice for a usable TTY experience. It replaces the kernel's virtual terminals with a userspace implementation that supports:

- Scalable fonts (resize with `Ctrl-Plus` / `Ctrl-Minus`)
- More than 16 colors
- Proper Unicode rendering
- Hardware-accelerated rendering without X11/Wayland

On Debian Trixie, install from backports:

```bash
# Add backports to sources.list
echo "deb http://deb.debian.org/debian/ trixie-backports main contrib non-free non-free-firmware" | sudo tee -a /etc/apt/sources.list
sudo apt update
sudo apt install -t trixie-backports kmscon
```

After install, kmscon starts automatically on boot. On the 1366×768 display, you'll want to scale up a few notches from the default.

### Autologin with kmscon

To boot straight to a prompt (no login screen delay), edit the kmscon systemd service:

```bash
sudo systemctl edit kmsconvt@tty1.service
```

Add:

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/kmscon --login -- /bin/login -f your_username
```

### Console Font Fallback (Without kmscon)

If kmscon causes issues on Chromebook hardware, the fallback is configuring the standard console font:

```bash
sudo dpkg-reconfigure console-setup
```

Select UTF-8 encoding, then choose **Terminus** at a size appropriate for the display. For 1366×768, `TerminusBold 14×28` or `Terminus 16×32` are reasonable. Config lives in `/etc/default/console-setup`.

### tmux Configuration

Veronica's tmux setup is directly applicable. Install tmux with battery and brightness tools:

```bash
sudo apt install tmux acpi light
```

Create `~/.tmux.conf`:

```bash
# Status bar at top (neovim uses the bottom)
set -g status-position top
set -g status-style bg=green

# Battery readout in status bar
set-window-option -g status-right "#(acpi -b | grep -m1 -o -P '.{0,2}%')"

# Brightness control via function keys
bind -n F8 run-shell 'light -U 10'
bind -n F9 run-shell 'light -A 10'
```

Then auto-launch tmux on login by adding to `~/.bashrc`:

```bash
# Launch tmux on the primary TTY if not already in tmux
if [ -z "${TMUX}" ] && [ $(tty) == "/dev/pts/0" ]; then
    exec tmux new-session
fi
```

### Network Management (TUI)

Without a desktop, WiFi needs a terminal interface:

```bash
sudo apt install network-manager
```

Then use `nm-tui` for interactive WiFi management:

```bash
# Interactive TUI — scan networks, connect, manage saved connections
nm-tui

# Command-line alternative
nmcli device wifi list
nmcli device wifi connect "SSID" password "password"
nmcli general status
```

### Local Help File

On a console-only system with no browser, documentation must be local. I plan to create a help file accessible via a short alias:

```bash
sudo mkdir -p /usr/local/share/doc
sudo tee /usr/local/share/doc/system-help.txt << 'EOF'
=== CODERDECK QUICK REFERENCE ===

NETWORK
  nm-tui              Interactive WiFi manager
  nmcli device wifi list    Show available networks
  nmcli device wifi connect "SSID" password "pass"
  nmcli general status      Connection status

DISPLAY
  Ctrl-Plus / Ctrl-Minus    Resize font (kmscon)
  light -A 10               Increase brightness
  light -U 10               Decrease brightness

TMUX
  Ctrl-B %         Split vertical
  Ctrl-B "         Split horizontal
  Ctrl-B arrow     Move between panes
  Ctrl-B d         Detach session
  tmux attach      Reattach

CLAUDE CODE
  claude           Start Claude Code
  claude --resume  Resume last session
  /help            In-session help

SYSTEM
  acpi -b          Battery status
  df -h            Disk usage
  htop             Process monitor
  sudo apt update && sudo apt upgrade   Update packages
  sudo systemctl poweroff               Shutdown
  sudo systemctl suspend                Suspend
EOF
```

Add an alias in `~/.bashrc`:

```bash
alias help-me='less /usr/local/share/doc/system-help.txt'
```

Having this on-device matters. When you're at a coffee shop with nothing but a TTY and no browser, the answer to "how do I reconnect WiFi" needs to be one command away.

## Google Services from the Terminal

A pure writerdeck intentionally cuts off the internet. My coderdeck can't — Claude Code needs it. And since I'm already online, I want occasional access to Google Drive and Gmail without installing a browser or desktop.

### Google Drive: rclone

[rclone](https://rclone.org/) is rsync for cloud storage. It supports Google Drive (and 70+ other backends) via a single CLI with a consistent interface. Install it:

```bash
sudo apt install rclone
```

Configure a Google Drive remote (one-time setup — this requires a browser for OAuth, so do it before you strip the desktop, or use `rclone authorize` on another machine):

```bash
rclone config
# Follow prompts: name it "gdrive", select Google Drive, complete OAuth
```

Then upload, download, and sync from the terminal:

```bash
# Upload a file to Drive
rclone copy ./my-document.md gdrive:Documents/

# List files in a Drive folder
rclone ls gdrive:Documents/

# Sync a local directory to Drive
rclone sync ./projects gdrive:Backups/projects/

# Download from Drive
rclone copy gdrive:Documents/notes.md ./
```

For headless OAuth (when you no longer have a browser on-device), you can run `rclone authorize "drive"` on a machine that does have a browser, then paste the resulting token into the config on the Chromebook.

### Gmail: neomutt

[NeoMutt](https://neomutt.org/) is a terminal email client that works well with Gmail via IMAP/SMTP. Install:

```bash
sudo apt install neomutt
```

Gmail configuration requires an App Password (since Google deprecated standard password auth for IMAP). Generate one at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords), then configure `~/.config/neomutt/neomuttrc`:

```bash
# Gmail IMAP
set imap_user = "your.email@gmail.com"
set imap_pass = "your-app-password"
set folder = "imaps://imap.gmail.com:993/"
set spoolfile = "+INBOX"
set postponed = "+[Gmail]/Drafts"
set record = "+[Gmail]/Sent Mail"
set trash = "+[Gmail]/Trash"

# Gmail SMTP for sending
set smtp_url = "smtps://your.email@gmail.com@smtp.gmail.com:465/"
set smtp_pass = "your-app-password"
set from = "your.email@gmail.com"
set realname = "Your Name"

# Practical defaults
set sort = reverse-date
set editor = "vim"
set mail_check = 120
```

This gives you read, compose, reply, search, and folder management — all from a TUI. It's not the Gmail web interface, but for occasional email access (checking messages, sending a quick reply, receiving OTP codes), it's more than sufficient.

**Alternative: `aerc`** — If neomutt's configuration feels heavy, [aerc](https://aerc-mail.org/) is a newer terminal email client with a simpler setup and built-in Gmail support. It's not in Debian stable yet but may be available from backports or as a Go binary.

### Adding to the help file

These commands belong in the local reference:

```
GOOGLE DRIVE (rclone)
  rclone copy ./file gdrive:path/     Upload file
  rclone ls gdrive:path/              List remote files
  rclone sync ./dir gdrive:path/      Sync directory to Drive
  rclone copy gdrive:path/file ./     Download file

EMAIL (neomutt)
  neomutt                             Open email client
  m                                   Compose new message
  r                                   Reply
  /                                   Search
  q                                   Quit
```

## The Math

| Configuration | RAM for ChromeOS/VM | RAM for Linux system | RAM available for work |
|--------------|--------------------:|--------------------:|----------------------:|
| Crostini (current) | ~2–2.5GB | ~500MB | ~1–1.5GB |
| Bare Debian + Desktop | 0 | ~800MB–1.2GB | ~2.8–3.2GB |
| Bare Debian + Console only | 0 | ~200–300MB | ~3.5–3.7GB |

Going from Crostini to a console-only Debian install roughly **triples** the available RAM for Claude Code. On a 4GB machine, that's the difference between "barely functional" and "comfortable for single-session work."

## Hardware Compatibility Notes

Before committing to Option 3, there are hardware considerations specific to Chromebooks running native Linux:

- **WiFi (Intel 9560)** — Well-supported in mainline Linux. Should work out of the box with the `iwlwifi` driver.
- **eMMC storage** — Standard block device, fully supported.
- **USB-C ports** — Work for charging and data. DisplayPort alt-mode may or may not function depending on kernel/firmware.
- **Audio** — Chromebook audio is often the weakest point in Linux compatibility. For a terminal-only machine, this is irrelevant — but worth noting if you ever want to add multimedia.
- **Trackpad/Keyboard** — Usually functional, though the ChromeOS-specific key layout (no F-keys, no Delete) requires remapping or adjustment.
- **Suspend/Resume** — Can be hit-or-miss on Chromebooks. Test this early — if suspend doesn't work reliably, you'll want to configure the lid-close behavior to shut down instead.
- **Battery reporting** — Typically works via standard ACPI, but verify after install.

## My Plan

I'm going to approach this incrementally:

1. **Continue with Crostini** for now — it works and I'm productive
2. **Enable Developer Mode** and test RW_LEGACY boot with Debian on a USB stick — verify WiFi, keyboard, and basic functionality
3. **If everything works**, flash full UEFI firmware and install Debian to the internal eMMC as a console-only system
4. **Configure tmux + Claude Code** as the primary interface

The beauty of having two identical machines is that I can experiment on one while keeping the other as a known-good ChromeOS setup. That's exactly why I bought two at $79 each.

## What This Gets Me

A 2.46-pound, 10-hour-battery portable terminal that:

- Boots to a login prompt in seconds
- Runs Claude Code with 3.5GB of available RAM
- Has no GUI overhead to manage or update
- Connects to WiFi and does exactly one thing: be a terminal to remote services and AI coding agents
- Cost less than a nice dinner for two

The ChromeOS version of this machine is a compromise — it works, but you're fighting the OS for resources the entire time. A bare Debian console install aligns the machine's purpose with its resources. Every byte of RAM goes toward the work.

Sometimes the best optimization is removing everything that isn't the thing you actually need.
