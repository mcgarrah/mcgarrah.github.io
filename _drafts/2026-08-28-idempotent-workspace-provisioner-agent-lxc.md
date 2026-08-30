---
layout: post
title: "A Bash Script You're Supposed to Run Again"
image: /assets/images/og/idempotent-workspace-provisioner-agent-lxc.png
categories: [homelab, proxmox, ai]
tags: [claude-code, codex, kiro, antigravity, lxc, proxmox, bash, idempotent, neovim, lazyvim, tmux, homelab]
excerpt: "Most environment-setup scripts are a ritual you run once and then forget — a snapshot of a good state at the moment it was written, decaying from the first apt upgrade onward. The script that builds ct:603 (agent-dev) is built to be run again, indefinitely, converging back to a known-good state every time — and it's already caught a real regression, and survived a near-deletion, because of that design."
description: "A detailed look at provision-agent-dev-lxc.sh — the idempotent bash provisioner behind ct:603 (agent-dev), a Proxmox LXC running four AI coding agent CLIs (Claude Code, Codex, Kiro CLI, Antigravity) side by side alongside a full dev toolchain (Neovim/LazyVim, lazygit, Node/.NET/Ruby/Python, Docker). Covers the guard-check pattern that makes every step safely re-runnable, a real regression the idempotency design caught before it shipped (a locale fix that would have downgraded a working config on a second container), the iterative fixes applied across real deployments, and a near-miss where the script itself was almost lost to an unrelated branch cleanup."
date: 2026-08-28
last_modified_at: 2026-08-28
seo:
  type: BlogPosting
  date_published: 2026-08-28
  date_modified: 2026-08-28
---

Most setup scripts have a lifespan of one run. You execute it, the environment exists, and from that moment on the script is a historical document — an accurate description of how things *used to* get built, quietly diverging from reality as the environment drifts. The script behind `ct:603` (agent-dev) was written to not work that way.

<!-- excerpt-end -->

## What it builds

`provision-agent-dev-lxc.sh` — deployed as `/root/install.sh` on the box itself — turns a bare Debian LXC into a fully-equipped, multi-agent development workspace in one run: four AI coding agent CLIs installed side by side (Claude Code, Codex, Kiro CLI, and Antigravity's `agy` — the same four this container's [session-persistence mechanism](/claude-code-tmux-persistence-proxmox-ha/) now knows how to resume), plus token/cost tracking (Tokscale, `kiro-usage`), a full polyglot toolchain (Node, .NET 9, Ruby/Jekyll, Python via `uv`, Docker CE), Neovim configured with LazyVim and a handful of language-specific overrides, `lazygit`, `fzf`, a tmux config tuned for truecolor pass-through and Claude Code's TUI, an SSH drop-in, a dynamic MOTD, and a generated onboarding `README.md` — all from one root-run bash script, no manual follow-up steps.

That alone isn't unusual — plenty of homelab setups have a big install script. What makes this one worth writing about is the header comment at the top of the file: **"IDEMPOTENT WORKSPACE PROVISIONER."** Not "setup script." Provisioner, in the sense infrastructure-as-code tools use the word — something you point at a target and it converges that target to a known state, regardless of what state it started in, safe to run over and over.

## The pattern: check before you act

Every step in the script follows the same shape — confirm the desired end state doesn't already exist before doing anything to create it:

```bash
# Neovim 0.11+ Installation
if [ ! -f /usr/local/bin/nvim ]; then
    echo " -> Fetching precompiled Neovim Stable binary payload..."
    cd /tmp
    wget -q --connect-timeout=10 --tries=3 https://github.com/neovim/neovim/releases/download/stable/nvim-linux-x86_64.tar.gz
    tar -C /usr/local --strip-components=1 -xzf nvim-linux-x86_64.tar.gz
    rm -f nvim-linux-x86_64.tar.gz
fi
```

```bash
# Antigravity CLI (agy)
if ! su - "$DEV_USER" -c "command -v agy &>/dev/null || [ -f ~/.local/bin/agy ]"; then
    echo "   * Installing Antigravity CLI (agy)..."
    su - "$DEV_USER" -c "curl -fsSL https://antigravity.google/cli/install.sh | bash" || true
fi
```

Same shape, twenty-plus times over — binaries, apt repos, config files, the LazyVim clone, all guarded the same way. Run the whole script on a container that already has everything installed, and it does almost nothing: checks twenty-some conditions, finds them all already true, exits clean. Run it on a half-built container, or one that lost a package in an unrelated apt mishap, and it fills in exactly the gap, nothing more.

## Where this actually mattered: a locale fix that almost broke a second container

The idempotency isn't decorative — it caught a real regression before it shipped. The original UTF-8 locale fix (Claude Code's Ink-based TUI suppresses Nerd Font glyphs without one) was unconditional:

```bash
echo " -> Configuring UTF-8 locale (LANG=C.utf8)..."
update-locale LANG=C.utf8
```

Fine on `ct:603`, which started at the Debian-default `LANG=C`. But when the same script got reused to provision `ct:602` (nutrition-api-dev) — a different container, already running `LANG=en_US.UTF-8` — that unconditional line would have silently downgraded a locale that was already correctly configured, for no reason other than the script not bothering to check first. Caught before it ran, fixed to match the pattern the rest of the script already used:

```bash
if ! grep -qi 'utf-\?8' /etc/default/locale 2>/dev/null; then
    echo " -> No UTF-8 locale configured, falling back to LANG=C.utf8..."
    update-locale LANG=C.utf8
else
    echo " -> UTF-8 locale already configured ($(grep '^LANG=' /etc/default/locale)), leaving as-is."
fi
```

The commit message for that fix says it plainly: *"applying the fix unconditionally would have downgraded a working locale on any re-run."* One extra container with a different starting state was enough to turn a working script into a real regression risk — exactly the kind of thing a script that's only ever run once, against the one environment it was written for, would never surface at all.

## Kept updated, not just kept working

Two more real fixes landed on this script after `ct:603` was already up and running, both illustrating the other half of "idempotent": re-running it should also pick up genuine improvements, not just restore a static baseline.

A tmux truecolor fix — `terminal-overrides` originally only covered `tmux-256color`/`xterm-256color`, which worked fine over the one SSH client this container happened to be accessed from at the time, but wasn't portable to Foot (ChromeOS) or other terminals a more generic template might see. Widened to a proper `terminal-features ",*:RGB"` declaration plus a broader override wildcard. And a LazyVim load-order fix — the `lazyvim.plugins.extras.*` imports had been nested one level too deep, inside the plugin-overrides file instead of the top-level `lazy.lua` spec table where LazyVim's own load order actually requires them.

Both fixes were applied live on the running container first, then backported into the script and committed — the commit message for the tmux/LazyVim fix says so directly: *"Already applied live on ct:603 (agent-dev)... nvim config was already correct."* The script isn't a one-time artifact describing history; it's the thing you keep in sync with whatever you've actually learned, so the *next* container — or this one, after a rebuild — gets the improved version, not the original one.

## The near-miss: the script almost disappeared

Version-controlling this script turned out to matter in a way that had nothing to do with idempotency directly. While reviewing an unrelated, much larger infrastructure branch (a Kubernetes 1.36 upgrade with a CNI swap and an autoscaler rewrite), a sweeping cleanup commit on that branch deleted a batch of scripts it judged unrelated to the K8s work — including this one. Unnoticed, because the branch's own diff was 74 files and 2,600+ lines; a 475-line provisioner quietly disappearing among that is easy to miss.

Caught only because this container's actual `/root/install.sh` got read directly, byte-for-byte, while writing this very post — and compared against what version control actually had on each branch. `main` still had it, correct and current. The feature branch didn't. Restored from `main` onto the feature branch, unchanged, confirmed identical to the live file first rather than assumed.

Worth naming as its own small lesson, separate from the idempotency story: a script this useful is easy to take for granted specifically *because* it works quietly in the background — nobody opens it up to check it's still there until something forces the question.

## What isn't idempotent-safe yet

Worth being honest about the gaps rather than presenting this as a finished, bulletproof pattern:

- **The default password is a literal string in the script** (`DEV_PASS="password"`), applied via `chpasswd` on every run for a newly-created user. Fine for a homelab LXC nobody but the operator can reach, not a pattern to carry anywhere more exposed.
- **Agent authentication isn't provisioned at all** — the script installs all four CLIs, but each one's actual login step is a manual, one-time thing done after the fact. [Kiro CLI's enterprise-auth path is separately known-broken](/ai-agent-context-files-in-practice/#reality-check-kiro-cli-is-broken-for-enterprise-auth) regardless of how it gets installed — a gap the provisioner can't paper over, since it's an upstream bug in the tool itself, not a setup-ordering problem.
- **Nothing in the script verifies the *running* state matches what it just declared** — it checks for a binary's existence or a config file's presence, not that the resulting tool actually works. An idempotent installer and a health check are different guarantees; this script is only the first one.

## Key takeaways

1. **"Idempotent" isn't a description, it's a design constraint that has to be checked, not assumed.** The locale fix looked idempotent-adjacent from the start — it was just one `update-locale` call — right up until a second, differently-configured container proved it wasn't. Every step needs its own guard, not just the ones that feel risky in isolation.
2. **A script that's reused across more than one target finds its own bugs.** The locale regression was invisible on `ct:603` alone, because `ct:603` never had a working locale to accidentally downgrade. Reuse against a second, differently-shaped environment was the actual test that mattered — a single deployment target can hide an entire category of bug.
3. **Backport real fixes from production into the source, in that order.** Both the tmux and LazyVim fixes were proven live before being written back into the script. The running system is allowed to be ahead of the checked-in provisioner briefly, as long as the gap gets closed deliberately — the failure mode to avoid is the reverse, where the script quietly stops matching what's actually been running for months.
4. **Something useful enough to be invisible is exactly the thing worth checking still exists.** The script wasn't lost because anyone decided it didn't matter — it was lost as incidental damage in an unrelated cleanup, on a branch nobody was specifically reviewing this file against. Trust, but verify against the live system occasionally, especially for the pieces quiet enough that nothing forces the question on its own.
