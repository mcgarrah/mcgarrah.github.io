---
layout: post
title: "The Config Already Supported Four Tools. Only One Had Ever Been Used."
image: /assets/images/og/claude-code-tmux-persistence-other-three-tools.png
categories: [homelab, proxmox, ai]
tags: [claude-code, tmux, proxmox, lxc, systemd, ai-coding-agent, kiro, antigravity, codex, homelab]
excerpt: "The session-restore mechanism on ct:603 was generalized back in August to cover four AI coding CLIs, not just Claude Code — the config format already had a tool field, the restore script already had a case statement for kiro, agy, and codex. None of the three had ever actually been used. The day they finally were, real usage surfaced four separate bugs a year of running the Claude-only path had never hit: a PATH gap invisible until a cold restart, a dead window that silently stayed broken forever, a standalone daemon that dies at logout unless told otherwise, and a status field that lies about what's actually running in a pane."
description: "Extending ct:603 (agent-dev)'s tmux session-persistence mechanism from a design that had merely been generalized on paper to one that has actually restored real Kiro CLI, Antigravity, and Codex sessions — session-ID discovery per tool via each one's own SQLite store, a PATH bug specific to Codex's separate npm prefix, a near-miss from trusting tmux's pane_current_command, standalone remote-control daemons requiring systemd lingering, and a real gap in the restore script's own idempotency check that let a dead window stay silently broken indefinitely."
date: 2026-09-27
last_modified_at: 2026-09-27
seo:
  type: BlogPosting
  date_published: 2026-09-27
  date_modified: 2026-09-27
---

A config file can say it supports four tools for a month without anyone finding out it doesn't, really — not until someone actually asks it to.

<!-- excerpt-end -->

## What "generalized" actually meant

The [session-persistence mechanism](/claude-code-tmux-persistence-proxmox-ha/) on `ct:603` started Claude-Code-only, then got [generalized on 2026-08-26](/claude-code-persistent-plain-shell-windows/) to also recognize plain shell windows. That same pass widened the config format's `tool` field to accept `claude | codex | kiro | agy | shell`, and `agent-restore.sh` picked up a full `case` statement with a real resume command for each:

```bash
case "$tool" in
  claude) cmd="claude -r $sid --remote-control $name; exec bash" ;;
  codex)  cmd="codex resume $sid; exec bash" ;;
  kiro)   cmd="kiro-cli chat --resume-id $sid; exec bash" ;;
  agy)    cmd="agy --conversation $sid; exec bash" ;;
  shell)  cmd="exec bash" ;;
esac
```

That looked done. It wasn't. A month later, `agent-sessions.conf` still had zero `kiro`, `agy`, or `codex` rows — three of the five branches in that `case` statement had never fired once, against real state, on this container. "Generalized" meant "the code exists to handle it," which is a real, useful, but much weaker claim than "this has been used."

## Finding a real session ID, three different ways

Claude Code's session ID is easy — a `.jsonl` transcript file per project directory, newest-wins. None of the other three work that way, and the restore script's own comments already knew it (`agent-track.sh`: "automatic inference isn't implemented for $TOOL yet"). Getting a real ID for each meant going straight to where each tool actually keeps its state:

**Kiro CLI** keeps a SQLite database, keyed by working directory rather than any kind of session picker:

```sql
SELECT conversation_id, updated_at
FROM conversations_v2 WHERE key='/opt' ORDER BY updated_at DESC;
```

**Antigravity (`agy`)** has a `conversation_summaries` table — but a freshly-opened conversation with no real prompt sent yet doesn't have a row there at all. The first attempt at a real `agy` registration found nothing newer than five weeks old, for exactly this reason; sending one throwaway message ("review mcgarrah.github.io and k8s-proxmox again") was enough to force a checkpoint and produce a findable row, title and workspace path matching what had just happened.

**Codex** turned out to store threads in its own SQLite file, `thread_turns`, with real timestamps to sort by:

```sql
SELECT thread_id, started_at, completed_at, status
FROM thread_turns ORDER BY started_at DESC LIMIT 5;
```

Three tools, three schemas, zero shared convention — exactly why the restore script never tried to guess and just requires the ID up front.

## The bug that only a cold restart would have caught

Registering `codex` surfaced something specific to it: `command not found`, even in a brand-new window. `claude`, `kiro-cli`, and `agy` all live in `~/.local/bin`, which `agent-tmux.service`'s hardcoded `Environment=PATH=` already covered. `codex` installs through `npm install -g` into a deliberately separate per-user prefix, `~/.npm-global/bin` — on purpose, per a comment already sitting in the provisioning script (`# Fixed with user-level npm prefix`) from an earlier, different bug where running that install as root would have put it in *root's* npm prefix instead, unreachable by the dev user entirely. That older bug was already fixed. This was a new one: the systemd unit's `PATH` had simply never been told about the fix.

The reason it hadn't caused a visible problem yet is the more interesting part. The live `tmux` server on `ct:603` had been running for weeks, started at some point by an interactive login shell — which does source `~/.npm-global/bin` into its `PATH` via `.bashrc`. Every `tmux new-window` since then inherited that already-correct environment from the running server, not from the systemd unit that originally started it. The unit's own `PATH` was wrong the entire time; nothing had ever been in a position to notice, because nothing had gone through a cold start since the bug was introduced.

```
Environment=PATH=/home/mcgarrah/.local/bin:/usr/local/bin:/usr/bin:/bin
                                            # ↑ missing entirely
```

Testing the fix hit a second, smaller version of the identical problem: `bash -lc "codex; exec bash"` failed too, despite `.bashrc` genuinely containing the right line. `bash -lc` is a login shell, not an *interactive* one — and this container's `.bashrc` has the standard Debian guard (`case $- in *i*) ;; *) return;; esac`) that bails out before reaching anything useful for non-interactive invocations. The systemd unit's explicit `PATH` was the only thing that was ever going to matter for the real restore path; `.bashrc` was never going to save it, in any shell mode.

## The near-miss: a field that reports the wrong thing with total confidence

Before any of the above, checking whether a given tmux window was safe to send a maintenance command into meant checking `pane_current_command`. It reported `bash` for a window that turned out to be running a live, unrelated Claude Code conversation — mid-response, "Thinking...", a real multi-hour session that wasn't this one. The command went in as a chat message instead of a shell command. Nothing was destroyed — `agent-sessions.conf` was unchanged afterward, confirming the intended shell command never actually ran anywhere — but a stray line landed in someone else's real conversation, and the field that was supposed to make this check safe had reported the opposite of the truth.

The fix going forward: never trust that field for this. `tmux capture-pane -t <target> -p | tail -10` shows what a window actually looks like — an interactive AI tool's own prompt (`❯`, `12% >`, whatever the tool's chosen) doesn't resemble a bare shell once actually looked at. For real certainty, the process tree settles it outright:

```bash
ps --forest -o pid,ppid,cmd -g $(ps -o sid= -p $(tmux list-panes -t <target> -F '#{pane_pid}'))
```

And when a maintenance command genuinely needs to run inside a window without disturbing whatever's in its one pane: split it first, run the command in the new pane, `tmux kill-pane` when done. `agent-track.sh` only needs `$TMUX_PANE` to resolve the right *window* — it works identically from a second pane in the same window, and never touches the first one's content.

## Two remote-control mechanisms, only one of which persists on its own

Both `agy` and `codex` offer a standalone way to make a machine remotely controllable from a web dashboard, independent of any specific resumed conversation — `agy remote-control start` and `codex remote-control start`. They turned out to behave completely differently under the hood. `agy`'s command installs a real `systemd --user` unit on its own, `enabled`, ready to restart itself. `codex`'s command does not install anything persistent at all — just a properly detached process (`PPID=1`, survives the shell that launched it) with no boot-time restart mechanism whatsoever. Confirmed via its actual running command line, then wrapped in a hand-written unit pointed at the tool's own stable `current/bin/codex` symlink, so it doesn't need editing every time `codex update` bumps a version number:

```ini
ExecStart=/home/mcgarrah/.codex/packages/app-server-daemon/current/bin/codex \
  app-server --remote-control --listen unix:// --managed-daemon
```

Neither one was actually going to help without a separate, easy-to-miss step. `agy`'s own `start` command said so directly on first run:

```
Warning: failed to enable linger; the daemon will stop when you log out
and will not start at boot. To fix, run: loginctl enable-linger mcgarrah
```

`systemd --user` units, by design, stop existing entirely once their owning user's last session ends — unless that user has lingering enabled, in which case `systemd` keeps a session alive on their behalf indefinitely. Every previous piece of this whole persistence mechanism has been built to survive a container restart; without `loginctl enable-linger mcgarrah`, both of these new daemons would have quietly failed to survive the very next SSH logout, let alone an HA migration.

## The bug hiding underneath all of the above: a window that "exists" forever

Adding real rows for `kiro`, `agy`, and `codex` meant those windows finally got exercised for real, which surfaced the deepest bug of the day — one that had nothing to do with any of the three specific tools and everything to do with the original design's oldest assumption. A routine review of all seven live windows found `codex`'s sitting at a bare, idle shell prompt. Not broken visibly — the tmux window was still named `codex`, `agent-sessions.conf` still had the correct row and session ID — just quietly not running anything at all. The process had died at some point (an update prompt, most likely, that never got answered) and fallen through to the script's own `; exec bash` fallback, and nothing had put anything back.

`agent-restore.sh`'s idempotency check had only ever asked one question — "does this window index exist" — the exact same coarseness the [original article's third takeaway](/claude-code-tmux-persistence-proxmox-ha/#key-takeaways) already named as the root cause of that project's very first bug, just recurring one level down. A `systemctl restart agent-tmux.service` would never have caught this: the check would see the window, say "already present," and move on. Only a full container reboot — which kills `tmux` itself, forcing every window to be rebuilt from the config from scratch — would ever have noticed.

The fix adds a real second question for every window that already exists: is the tool actually still running inside it? Not via `pane_current_command`, for the reasons covered above — via the same process-tree check, scripted:

```bash
PANE_PID=$(tmux list-panes -t "$sess:$idx" -F '#{pane_pid}' | head -1)
PANE_SID=$(ps -o sid= -p "$PANE_PID" | tr -d ' ')
if [[ -z "$PANE_SID" ]] || ! ps -g "$PANE_SID" -o cmd= | grep -qF "$tool"; then
  tmux respawn-pane -k -t "$sess:$idx" "$cmd"
fi
```

`tmux respawn-pane -k` relaunches a pane's command in place, without touching the window or session it lives in — exactly the primitive this needed, and one the original design never had reason to reach for.

Two of the seven live windows at review time were real Claude Code conversations, one of them the very session doing this review — not something to test a new kill-and-relaunch mechanism against directly. A throwaway session with a fake `sleep`-based "tool" stood in instead: confirmed the check correctly reports healthy while the process is genuinely alive, confirmed it correctly detects the dead state after killing just the child process (an earlier attempt using `exec -a` to fake a process name instead replaced the shell itself via `exec`, meaning nothing was left to fall through to `; exec bash` when the fake process died — closing the whole window instead of leaving it idle, which isn't how any real tool invocation behaves and would have been the wrong test entirely), then confirmed `respawn-pane -k` produces a window indistinguishable from a freshly-created one. Only after all three held up in isolation did the real, actually-dead `codex` window get relaunched by hand.

## Key takeaways

1. **"The code exists" and "this has been used" are different claims, and the gap between them is exactly where the bugs live.** Generalizing the config format and the restore script's `case` statement in August was real work, correctly done — and it still left three of five tool paths completely unexercised against live state for a month. Nothing was wrong with the code sitting there unused; the risk was in mistaking its existence for validation.
2. **A field that's usually right is more dangerous than one that's usually wrong.** `pane_current_command` reporting the correct thing most of the time is exactly what made trusting it once, without checking, land a stray message in someone else's real conversation. A signal that fails rarely gets trusted at the exact moment it happens to be lying.
3. **The same class of bug can hide at a different layer than the first time you fixed it.** The original mechanism's core lesson — an idempotency check answering a coarser question than the one that actually matters — showed up again here, one level down: "does the window exist" instead of "does the session exist," but the identical shape of mistake, invisible for exactly the same reason (nothing had exercised the failure path yet).
4. **A persistence mechanism is only as persistent as its least-obvious dependency.** Two new remote-control daemons were both technically running, both technically enabled — and both would have silently died at the next logout without `loginctl enable-linger`, a single command that has nothing to do with either tool's own configuration and everything to do with how `systemd --user` works.
5. **Test the dangerous change somewhere it can't hurt anything real.** A kill-and-respawn mechanism aimed at production windows — two of which were real, valuable Claude Code conversations — got its full test cycle in a disposable session with a fake tool first. The first attempt at even that isolated test had its own bug (the `exec -a` shell-replacement issue), caught safely because nothing real was ever in the blast radius while working it out.
