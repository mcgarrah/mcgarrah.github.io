---
title: "Claude Code on a $79 Chromebook"
layout: post
categories: [technical]
tags: [chromeos, claude, ai, development]
excerpt: "A discontinued Lenovo Chromebook with 8GB RAM and a Celeron N-series CPU makes a surprisingly capable portable terminal for AI-assisted development with Claude Code — if you understand the constraints."
description: "Setting up Claude Code CLI on ChromeOS via Crostini Linux, evaluating the resource constraints of running an AI coding agent on budget hardware, and connecting it to VS Code for a lightweight portable development workflow."
---

I picked up two Lenovo Chromebooks in 2022 — N-series Celeron, 8GB RAM, 64GB eMMC, around $79 each after rebates. Lenovo was discontinuing the model and clearing inventory. The machines still have ChromeOS update support for several more years, and at that price point I bought two without hesitation.

<!-- excerpt-end -->

These machines still boot in under ten seconds, run a full Linux container via Crostini, and have enough RAM to do real work — provided you're deliberate about what "real work" means on 8GB shared between ChromeOS and a Linux VM. The question I wanted to answer: can a budget Chromebook serve as a portable AI-assisted development terminal running Claude Code?

The short answer is yes, with caveats worth understanding.

## Why Bother

The strategic case for a disposable dev terminal is straightforward:

- **Travel machine** — If it gets lost, stolen, or broken, you're out $79 and zero sensitive data (everything lives in Git and the cloud)
- **Secure-by-default posture** — ChromeOS's verified boot and sandboxed architecture mean the base OS is hardened by design, and Crostini runs inside a VM boundary
- **Instant-on terminal** — Open the lid, open the Linux terminal, you're working. No Windows Update surprises, no macOS upgrade prompts
- **Budget hardware, real capability** — At $79 per unit, these are effectively disposable. Buying two means one lives at home and one travels and I let my five year old grandson play with either without worrying about it.

The pattern here is similar to how I think about homelab infrastructure — purpose-built, disposable where appropriate, and designed so that losing any single node costs you nothing but time.

## The Resource Reality

Claude Code's memory footprint is the primary constraint. Based on reported usage and GitHub issues, a single Claude Code session typically consumes 1.5–2GB RAM. On a system with 8GB total, ChromeOS itself takes 2–3GB, and the Crostini VM overhead adds another 500MB–1GB. That leaves roughly 3–4GB for your Linux userspace, which is tight but workable for a single Claude Code session with a small project context.

What this means in practice:

- **Close Chrome tabs** before starting Claude Code. Each tab is its own process and ChromeOS will OOM-kill your Linux container before it touches browser processes.
- **Don't run parallel sessions**. One Claude Code instance at a time.
- **Small-to-medium repos only**. Large monorepos with deep file trees will push context window usage (and memory) beyond what's comfortable here.
- **The 64GB eMMC is fine** — Claude Code itself is small, and you're not storing build artifacts locally. Git repos and Node.js/tooling fit easily.

The Celeron N-series CPU is not the bottleneck. Claude Code is I/O and network-bound — the heavy computation happens on Anthropic's servers. Your local CPU mostly handles terminal rendering and file operations.

## Setting Up the Environment

### Enable Linux (Crostini)

If you haven't already:

1. Open **Settings → Advanced → Developers**
2. Turn on **Linux development environment**
3. Accept the defaults (or increase disk allocation if you have room on your 64GB)

Once the container is running, update it:

```bash
sudo apt update && sudo apt upgrade -y
```

### Install Claude Code

The recommended path as of 2026 is the native installer, which bundles its own runtime and requires zero dependencies:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

This puts `claude` on your PATH and sets up background auto-updates. No Node.js required.

Alternatively, if you prefer version pinning or already have Node.js in your environment:

```bash
# Requires Node.js 18+ and npm
npm install -g @anthropic-ai/claude-code
```

### Authenticate

```bash
claude
```

On first run, Claude Code walks you through authentication. You need a paid Claude account — Pro ($20/month), Max, Team, or Enterprise. The free tier does not include CLI access.

### VS Code Integration

Since I already have VS Code running in Crostini, the natural integration point is the Claude Code VS Code extension rather than trying to wire things through the Chrome browser. Install it from the Extensions marketplace inside VS Code:

1. Open VS Code (the Linux `.deb` version running in Crostini)
2. Install the **Claude Code** extension from the marketplace
3. The extension runs a local MCP server that connects the CLI to VS Code's diff viewer

This gives you inline diff review, file navigation, and the ability to accept or reject changes from within the editor — while Claude Code's agent logic still runs in the terminal.

## Crostini Constraints Worth Knowing

A few ChromeOS-specific behaviors that will bite you if you're not aware:

- **Lid close kills processes** — By default, closing the Chromebook lid suspends the Crostini VM. Long-running Claude Code sessions will die. You can change this in ChromeOS settings under "Power" (keep awake when lid is closed), or use `crosh` to adjust VM behavior.
- **No GPU passthrough** — Irrelevant for Claude Code specifically, but worth noting if you're considering other ML workloads in the same container.
- **Shared filesystem performance** — The Crostini container accesses ChromeOS files through a 9P filesystem bridge. It's not fast. Keep your working repos inside the Linux container's native filesystem (`/home/username/`) rather than in shared folders.
- **Network is straightforward** — Crostini shares the host network. No port forwarding or bridge configuration needed. Claude Code's API calls just work.

## What This Actually Looks Like

My workflow on this machine:

1. Open the lid, open Terminal
2. `cd` into the project directory
3. Run `claude` and start working — quick bug fixes, code review, drafting implementations
4. Push to GitHub when done
5. Close the lid and walk away

For anything requiring sustained multi-file refactoring on a large codebase, I use my primary workstation. But for the kind of focused, single-context work that Claude Code excels at — answering architectural questions against a repo, drafting a new module, fixing a bug with full context — this $79 Chromebook is genuinely useful.

The machine doesn't need to be powerful. It needs to be present, fast to wake, and capable of running a terminal with network access. Everything else is Anthropic's problem.

## Security Posture

ChromeOS is a reasonable choice for a portable dev terminal precisely because of its security model:

- **Verified boot** ensures the OS integrity chain on every startup
- **Crostini's VM boundary** isolates your Linux environment from the ChromeOS host
- **No sensitive data at rest** — credentials live in Claude's auth token (refreshable), code lives in Git, nothing irreplaceable is stored locally
- **Minimal attack surface** — this device initiates outbound HTTPS connections to GitHub and Anthropic's API. It doesn't run services or accept inbound connections.
- **Active updates** — unlike a Windows machine you'd have to patch yourself, ChromeOS updates are automatic and the AUE date is still years out

The machine is purpose-built for one job: be a portable terminal that talks to remote services. ChromeOS is arguably better suited to that role than a full desktop OS.

## Final Thoughts

The combination of a sub-$100 Chromebook, Crostini Linux, and Claude Code creates a surprisingly capable portable development setup. The constraints are real — 8GB RAM means you're disciplined about resource usage — but the constraints also enforce good habits. You focus on one thing at a time, you keep your repos lean, and you let the AI agent handle the heavy cognitive lifting while your local machine just provides the interface.

If you spot a Chromebook clearance deal with 8GB RAM, it's worth grabbing one for this purpose alone. The hardware doesn't need to be impressive — it just needs to run a terminal, authenticate to an API, and stay out of your way.

---

https://psref.lenovo.com/Detail/IdeaPad/IdeaPad_3_CB_11IGL05?M=82BA001FUS

IdeaPad 3 CB 11IGL05
Part Number : 82BA001FUS


PERFORMANCE
Processor
Intel Celeron N4020 (2C / 2T, 1.1 / 2.8GHz, 4MB)
Graphics
Integrated Intel UHD Graphics 600
Chipset
Intel SoC Platform
Memory
4GB Soldered LPDDR4-2400
Memory Slots
Memory soldered to systemboard, no slots
Max Memory
4GB soldered memory, not upgradable
Storage
64GB eMMC 5.1
Storage Support
64GB eMMC 5.1 on systemboard
Card Reader
MicroSD Card Reader
Optical
None
Audio Chip
High Definition (HD) Audio
Speakers
Stereo speakers, 2W x2
Camera
HD 720p
Microphone
Mono
Battery
Integrated 42Wh
Max Battery Life
Google power load test: 10 hr
Power Adapter
45W USB-C (3-pin)
DESIGN
Display
11.6" HD (1366x768) TN 250nits Anti-glare
Touchscreen
None
Keyboard
Non-backlit, English
Case Color
Onyx Black
Surface Treatment
IMR (In-Mold Decoration by Roller)
Case Material
PC + ABS (Top), PC + ABS (Bottom)
Dimensions (WxDxH)
286.7 x 205.5 x 18.05 mm (11.29 x 8.09 x 0.71 inches)
Weight
Starting at 1.12 kg (2.46 lbs)
SOFTWARE
Operating System
Chrome OS
Bundled Software
None
CONNECTIVITY
Onboard Ethernet
None
WLAN + Bluetooth
Intel 9560 11ac, 2x2 + BT4.2
Standard Ports
2x USB 3.2 Gen 1
2x USB-C 3.2 Gen 1 (support data transfer, Power Delivery, and DisplayPort)
1x Card reader
1x Headphone / microphone combo jack (3.5mm)
SECURITY & PRIVACY
Security Chip
Google Security Chip H1
Fingerprint Reader
None
Physical Locks
Kensington Security Slot, 3 x 7 mm
SERVICE
Base Warranty
1-year, Mail-in
Included Upgrade
None
CERTIFICATIONS
Green Certifications
ENERGY STAR 8.0
ErP Lot 3
RoHS compliant

---

Lenovo Chromebook 3 11.6" HD Laptop Celeron N4020 4GB 64GB Black $79

Best Buy had it for $79 and brought it down to $70 with discounts.
$139 -> $79 (+rebates)

---


