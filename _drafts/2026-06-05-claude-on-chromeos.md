---
title: "Claude Code on a $79 Chromebook"
layout: post
categories: [technical]
tags: [chromeos, claude, ai, development]
excerpt: "A discontinued Lenovo Chromebook with 4GB RAM and a Celeron N4020 makes a surprisingly capable portable terminal for AI-assisted development with Claude Code — if you understand the constraints."
description: "Setting up Claude Code CLI on ChromeOS via Crostini Linux, evaluating the resource constraints of running an AI coding agent on a sub-$100 Chromebook, and connecting it to VS Code for a lightweight portable development workflow."
---

I picked up two Lenovo IdeaPad 3 Chromebooks (11IGL05) back in 2022 when Best Buy was clearing them out — $79 marked down from $139, and I got one down to $70 with additional discounts. Lenovo was discontinuing the model. The machines still have ChromeOS update support for several more years, and at that price point I bought two without hesitation.

<!-- excerpt-end -->

These machines boot in under ten seconds, run a full Linux container via Crostini, and have enough storage and connectivity to do real work — provided you're deliberate about what "real work" means on 4GB RAM shared between ChromeOS and a Linux VM. The question I wanted to answer: can a budget Chromebook serve as a portable AI-assisted development terminal running Claude Code?

The short answer is yes, with caveats worth understanding.

## The Hardware

The specific model is the [Lenovo IdeaPad 3 CB 11IGL05](https://psref.lenovo.com/Detail/IdeaPad/IdeaPad_3_CB_11IGL05?M=82BA001FUS) (Part Number: 82BA001FUS):

| Component | Spec |
|-----------|------|
| Processor | Intel Celeron N4020 (2C/2T, 1.1GHz base / 2.8GHz burst, 4MB cache) |
| Memory | 4GB LPDDR4-2400 (soldered, not upgradable) |
| Storage | 64GB eMMC 5.1 |
| Display | 11.6" HD (1366×768) TN, 250 nits |
| Graphics | Intel UHD Graphics 600 (integrated) |
| Wireless | Intel 9560 802.11ac 2×2 + Bluetooth 4.2 |
| Ports | 2× USB-A 3.2 Gen 1, 2× USB-C 3.2 Gen 1 (data + PD + DP), MicroSD, 3.5mm combo |
| Battery | 42Wh integrated (~10 hours) |
| Weight | 1.12 kg (2.46 lbs) |
| OS | ChromeOS |
| Security | Google H1 Security Chip, Kensington slot |

At 2.46 lbs with a 10-hour battery and USB-C charging, it's a genuinely portable machine. The dual USB-C ports with Power Delivery and DisplayPort mean you can run it off any USB-C charger and connect an external monitor if needed.

## Why Bother

The strategic case for a disposable dev terminal is straightforward:

- **Travel machine** — If it gets lost, stolen, or broken, you're out $79 and zero sensitive data (everything lives in Git and the cloud)
- **Secure-by-default posture** — ChromeOS's verified boot and sandboxed architecture mean the base OS is hardened by design, and Crostini runs inside a VM boundary
- **Instant-on terminal** — Open the lid, open the Linux terminal, you're working. No Windows Update surprises, no macOS upgrade prompts
- **Budget hardware, real capability** — At $70–79 per unit, these are effectively disposable. Buying two means one lives at home and one travels and I let my five year old grandson play with either without worrying about it.

The pattern here is similar to how I think about homelab infrastructure — purpose-built, disposable where appropriate, and designed so that losing any single node costs you nothing but time.

## The Resource Reality

Claude Code's memory footprint is the primary constraint — and with only 4GB total RAM, this is where things get interesting. Based on reported usage and GitHub issues, a single Claude Code session typically consumes 1.5–2GB RAM. On a system with 4GB total, ChromeOS itself takes 1.5–2GB, and the Crostini VM overhead adds several hundred MB. That leaves very little headroom.

What this means in practice:

- **Close all Chrome tabs** before starting Claude Code. This is non-negotiable at 4GB. Each tab is its own process and ChromeOS will OOM-kill your Linux container before it touches browser processes.
- **Don't run parallel sessions**. One Claude Code instance at a time — and even that may require closing VS Code's GUI in favor of terminal-only workflow.
- **Small repos only**. Large monorepos with deep file trees will push context window usage (and memory) beyond what's feasible here.
- **The 64GB eMMC is shared** — ChromeOS and Crostini carve up the same 64GB. When you enable Crostini, you allocate a portion of that storage to the Linux container. I'm running 10GB for Linux currently and it's sufficient — Git repos and Claude Code tooling don't take much space, and you can resize later if needed.
- **Consider swap** — Configuring swap space inside Crostini can provide a buffer when memory pressure spikes, at the cost of eMMC write wear.

The Celeron N4020 is not the bottleneck. It's a dual-core chip running at 1.1GHz base with burst to 2.8GHz — modest by any measure — but Claude Code is I/O and network-bound. The heavy computation happens on Anthropic's servers. Your local CPU mostly handles terminal rendering and file operations, and two threads at burst clock is adequate for that.

## Setting Up the Environment

### Enable Linux (Crostini)

If you haven't already:

1. Open **Settings → Advanced → Developers**
2. Turn on **Linux development environment**
3. Set the disk size allocation — the default is around 10GB, which is where I'm currently running with room to grow. This comes out of your shared 64GB eMMC, so you'll want to balance it against ChromeOS and any Android apps you keep installed.

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

The combination of a sub-$100 Chromebook, Crostini Linux, and Claude Code creates a surprisingly capable portable development setup. The constraints are real — 4GB RAM means you're extremely disciplined about resource usage — but the constraints also enforce good habits. You focus on one thing at a time, you keep your repos lean, and you let the AI agent handle the heavy cognitive lifting while your local machine just provides the interface.

If you spot a Chromebook clearance deal with at least 4GB RAM (8GB preferred), it's worth grabbing one for this purpose alone. The hardware doesn't need to be impressive — it just needs to run a terminal, authenticate to an API, and stay out of your way.
