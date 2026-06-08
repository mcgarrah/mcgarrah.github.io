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

This idea isn't new. Veronica Explains has an excellent video on building a ["Writerdeck" — a tty-only laptop for maximum focus](https://www.youtube.com/watch?v=E7vFdy4BEAY). She repurposed a System76 Galago Pro with Debian Trixie, stripped down to nothing but a text console. No desktop environment, no display manager — just a TTY and the tools needed for writing.

The writerdeck approach solves many of the same technical problems we need to sort out here:

- **Console font sizing** — On a bare TTY, the default font is tiny on modern screens. The writerdeck video covers using `kmscon` (a userspace terminal emulator that replaces the kernel's built-in virtual terminals) for scalable fonts, or configuring `/etc/default/console-setup` with larger bitmap fonts like Terminus.
- **TUI-based configuration** — Without a GUI, you need terminal interfaces for system management. NetworkManager's `nm-tui` provides a curses-based interface for WiFi configuration that works perfectly in a pure console environment.
- **Single-purpose philosophy** — The writerdeck is designed for writing. Mine is designed for AI-assisted development. Same principle: remove everything that isn't the core task.

The [writerdeckOS project](https://github.com/tinkersec/tinkerwriterdeck) takes this further with a turn-key OS image that explicitly supports Chromebooks with 64-bit Intel/AMD processors — which is exactly our hardware.

My use case differs from a writerdeck in one important way: I need network access (for Claude Code's API calls and git operations). A pure writerdeck intentionally removes networking. But the underlying TTY configuration — font scaling, console setup, and the philosophy of radical minimalism — translates directly.

## TTY Configuration Details

Running a TTY-only system on an 11.6" 1366×768 display requires deliberate configuration. The default Linux console font is roughly 8×16 pixels — workable on this resolution but could be more comfortable.

### Console Font Sizing

**Option A: `console-setup` (simple, built-in)**

```bash
sudo dpkg-reconfigure console-setup
```

Select UTF-8 encoding, then choose a font like **Terminus** at a size that works for your screen. For 1366×768, `Terminus 16×32` or `TerminusBold 14×28` are good starting points. The config lives in `/etc/default/console-setup`:

```
CODESET="guess"
FONTFACE="Terminus"
FONTSIZE="16x32"
```

**Option B: `kmscon` (advanced, scalable)**

`kmscon` is a userspace terminal emulator that replaces the kernel VTs. It supports TrueType fonts, Unicode, and hardware-accelerated rendering — all without X11 or Wayland.

```bash
sudo apt install kmscon
```

Kmscon gives you proper font scaling, scrollback, and multiple terminal sessions managed outside the kernel. It's what the writerdeck video uses for a polished TTY experience.

### Network Management (TUI)

Without a desktop environment, WiFi management needs a terminal interface:

```bash
sudo apt install network-manager
```

Then use `nm-tui` for an interactive curses interface, or `nmcli` for scripted/command-line operations:

```bash
# Interactive TUI for WiFi
nm-tui

# Command-line WiFi connection
nmcli device wifi list
nmcli device wifi connect "SSID" password "password"

# Check connection status
nmcli general status
```

### Local Help File

On a console-only system with no browser, you need documentation available locally. I plan to create a `/usr/local/share/doc/system-help.txt` with essential commands and configuration notes — a cheat sheet accessible via `less /usr/local/share/doc/system-help.txt` or aliased to a short command.

The help file should cover:

- WiFi connection (`nm-tui` and `nmcli` usage)
- Font size adjustment (`setfont`, `console-setup` reconfiguration)
- tmux basics (session management, splits, detach/reattach)
- Claude Code quick-reference (auth, common flags)
- System maintenance (apt update, disk usage, battery status)
- Power management (suspend, lid behavior, shutdown)

Having this on-device matters. When you're sitting in a coffee shop with nothing but a TTY and no browser, the answer to "how do I do X" needs to be local.

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
