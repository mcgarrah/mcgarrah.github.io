---
layout: post
title: "Not Every Persistent tmux Window Needs Claude Code"
image: /assets/images/og/claude-code-persistent-plain-shell-windows.png
categories: [homelab, proxmox, ai]
tags: [claude-code, tmux, proxmox, lxc, nvim, lazygit, homelab]
excerpt: "The same systemd mechanism that resumes Claude Code conversations after ct:603 restarts was already being asked to do a second job informally — hold a plain shell open for nvim, lazygit, or ad-hoc commands. It just wasn't doing that job on purpose, which meant it wasn't doing it reliably. A one-line sentinel value fixed that."
description: "Extending the ct:603 (agent-dev) session-persistence mechanism, previously built to resume Claude Code conversations by ID after an HA migration, to also cover plain tmux windows with no Claude Code process at all — for ad-hoc shell commands, nvim/LazyVim, or lazygit. Covers the design (a 'shell' sentinel value in the existing config format), the real untracked windows that motivated it, the live test that confirmed both the idempotent-skip and creation paths work correctly, and a follow-up fix for tmux's status bar showing the wrong window label once automatic-rename and a real config disagree about what each window actually is."
date: 2026-08-26
last_modified_at: 2026-08-27
seo:
  type: BlogPosting
  date_published: 2026-08-26
  date_modified: 2026-08-27
---

The [session-persistence mechanism covered previously](/claude-code-tmux-persistence-proxmox-ha/) resumes Claude Code conversations by ID after `ct:603` restarts. It was never asked to do anything else — but a look at what was actually running in `tmux` showed it was already being used for something else anyway, informally, and badly.

<!-- excerpt-end -->

## The windows that weren't Claude Code at all

Checking the live state of the container turned up three tmux windows with no Claude Code process in them whatsoever: a bare shell sitting in `/opt`, and an `nvim` session plus a second bare shell in a project subdirectory. None of these were tracked in the restore config. None of them would have survived the next HA migration — the exact failure this whole mechanism exists to prevent, just for a category of window the original design never considered.

That's a real, already-happening use case: not every persistent tmux window is a multi-hour agent conversation. Some are just a shell kept open in a specific directory for running commands, or for `nvim .` and LazyVim, or `lazygit` — things worth keeping around across a restart for the same reason a Claude Code session is, without needing an actual Claude Code process attached to them at all.

## Extending the format instead of building a second one

The config file already had everything needed except a way to say "don't resume a Claude Code session here — just give me a shell":

```
# tmux_session|window_index|cwd|claude_session_id|remote_control_name
claude-ma|3|/opt|shell|scratch shell
```

The fourth field — normally a UUID passed to `claude -r` — becomes the literal string `shell` for one of these windows instead. The restore script branches on that single value:

```bash
if [[ "$sid" == "shell" ]]; then
  cmd="exec bash"
  label="plain shell"
else
  cmd="claude -r $sid --remote-control $rc_name; exec bash"
  label="remote-control: $rc_name"
fi
```

Everything downstream — the per-window idempotency check, the session/window creation logic, the launch stagger — stays identical, because window identity was already keyed on tmux index rather than anything Claude-specific. Adding a second *kind* of window didn't require a second mechanism, just a fork in the one line that decides what gets launched inside it.

The tracking helper got the matching registration path — `--shell [label]`, run from inside the window being registered, the same way a Claude Code window gets tracked:

```bash
if [[ "$1" == "--shell" ]]; then
  SID="shell"
  RC_NAME="${2:-plain shell}"
  # ...writes the row, same as the Claude Code path
fi
```

No `--remote-control` for these — the flag is specific to Claude Code sessions and doesn't apply to a bare shell — so the name field becomes purely a human-readable label in the config file, not something passed to any command.

## Testing both paths for real, not just the happy one

Registered the actual untracked `/opt` shell window this way — `--shell 'scratch shell'` — and confirmed the row landed correctly. Then two things needed checking, matching the same discipline as the original mechanism: does it correctly *skip* an already-restored plain-shell window, and does it correctly *create* one from scratch.

The skip path: running the restore script against the now-fully-populated live state reported all four windows — three Claude Code sessions and the one new plain shell — as "already present," nothing re-spawned. The creation path needed a throwaway test, since the real window was already running: a temporary config row in a disposable tmux session confirmed a plain `bash` actually launches, in the right directory, with no Claude Code process anywhere near it.

## The status bar still couldn't tell windows apart

Even with the plain-shell window correctly tracked and restorable, actually living with several windows day to day surfaced a different, smaller gap: tmux's bottom status bar showed `claude`/`bash`/`bash`/`bash` for four windows doing completely different things. `automatic-rename` (on by default in this container) drives that label from the raw foreground process name, and it's unreliable by nature — Claude Code, a plain shell, or any other agent CLI sharing this mechanism all just show up as whatever binary happens to be running at that instant, or a generic name once they return to a bash prompt between actions.

`Ctrl-b w`'s window-tree view was more useful — it also surfaces `pane_title`, a separate piece of tmux state Claude Code sets explicitly via a terminal-title escape sequence, independent of `automatic-rename`. Checked directly against the live session: `pane_title` stayed accurate and stable per window the whole time. The bottom status bar just never displays it by default.

The fix wasn't to chase `pane_title` into the status bar — `window-status-format` can reference `#{pane_title}`, but every window's title happened to differ only in a suffix that gets truncated at typical status-bar width, so all of them rendered identically anyway; that would have made the problem worse, not better. The actual fix: set `window_name` explicitly to the value the restore config already knows — the tool (`claude`, `codex`, `kiro`, `agy`, or `shell`) — at creation time, then immediately turn `automatic-rename` off for that one window so it can't be silently overwritten later:

```bash
tmux new-session -d -s "$sess" -n "$tool" -c "$cwd" "$cmd"
tmux set-window-option -t "$sess:$idx" automatic-rename off
```

Same pattern the rest of this design already leans on: don't fight tmux's automatic behavior, disable it precisely where it conflicts with something the config already has better information about. Applied retroactively to the already-running windows too, not just future ones — a rename and an option flip, no process disruption, the same "fix it live, don't wait for the next restart" instinct used throughout this project.

## What this doesn't cover yet

Two more untracked windows exist — an `nvim` session and a second bare shell, both in a different project directory — that this same mechanism could now track but don't yet. Registering them is a one-line command each, whenever that's worth doing; nothing about the design requires it to happen all at once. Worth naming as the obvious next use of this, not because it's blocking anything.

## Key takeaways

1. **Look at what's actually running, not just what the system was designed for.** The three untracked windows weren't a hypothetical future need — they already existed, informally solving the same problem this mechanism was built to solve, just without the reliability of actually being tracked.
2. **A one-value fork beats a parallel mechanism.** The temptation with "also support plain shells" is a second script, a second config file, a second set of tests. Since window identity, idempotency, and launch sequencing were already generic, the entire addition was a three-line conditional and one new config field value.
3. **Test the branch you added, not just the one you didn't touch.** The idempotent-skip path was trivially likely to still work — it doesn't care what's inside a window. The creation path was the actually-new code, and it got its own real test rather than an assumption that "it's just `exec bash`, what could go wrong."
4. **A label only helps if something keeps it accurate.** `automatic-rename` and a manually-set window name are fighting over the same field — leaving both enabled just means whichever wrote most recently wins, unpredictably. Turning the automatic behavior off, precisely where the config already has better information than tmux's own heuristic, beat trying to make the automatic behavior smarter.
