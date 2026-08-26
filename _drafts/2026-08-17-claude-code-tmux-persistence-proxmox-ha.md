---
layout: post
title: "Persisting Claude Code Agent Sessions Through Proxmox HA Migrations"
image: /assets/images/og/claude-code-tmux-persistence-proxmox-ha.png
categories: [homelab, proxmox, ai]
tags: [claude-code, tmux, proxmox, lxc, high-availability, ceph, cephfs, systemd, ai-coding-agent, homelab]
excerpt: "A dedicated LXC runs several long-lived Claude Code agents in tmux against this cluster's real infrastructure. The problem: LXCs can't live-migrate, so every HA failover or manual relocation needed for cluster maintenance killed tmux and every session with it — including, more than once, the very session doing the maintenance. Here's the two-layer fix, the dead ends it took to get a reliable session-ID mapping, and what the real migration test broke that the design review didn't catch."
description: "Building automatic Claude Code session restoration for an HA-managed Proxmox LXC (ct:603, agent-dev): a Proxmox-layer configuration that was already correct (onboot, HA group, a shared CephFS bind mount), an in-container systemd unit and restore script that recreates tmux sessions and resumes each Claude Code conversation by ID, the investigation into reliably mapping a live tmux window to its Claude Code session ID, and three real bugs — a skip-logic gap, a missing CLI flag, and a tmux auto-rename trap — that a live HA migration test surfaced and a code review alone would not have."
date: 2026-08-17
last_modified_at: 2026-08-26
seo:
  type: BlogPosting
  date_published: 2026-08-17
  date_modified: 2026-08-26
---

There's a small irony in an AI agent losing its own memory because of the infrastructure work it's doing. That happened often enough on this cluster to be worth fixing properly, not just working around each time.

<!-- excerpt-end -->

## The setup

`ct:603` — hostname `agent-dev`, on `edgar` — is a dedicated LXC for running Claude Code against this cluster's real infrastructure: the six-node "AlteredCarbon" Proxmox/Ceph cluster this blog has been [documenting the upgrade of](/proxmox-8-to-9-cluster-upgrade-part-1/). It's not a sandbox with fake data — it has SSH reach to every cluster node and does real work there, which is exactly why it's its own container rather than something running on a workstation: one dedicated, auditable place with its own HA policy, not credentials scattered across laptops.

Day to day, that means several Claude Code sessions running concurrently in `tmux` — separate windows, separate long-running conversations, each one accumulating hours of context on a different piece of work. Killing one and starting fresh isn't free: re-establishing the same depth of context takes real time, and mid-task state (a paused investigation, a half-finished plan) doesn't come back on its own.

## The problem

LXC containers can't live-migrate. Every HA failover, every manual `pct migrate` for cluster maintenance, every node reboot — the container stops and restarts, somewhere. `tmux` dies with it, and every session it was holding goes with it.

On a cluster where nodes get rebooted for kernel updates, Ceph maintenance, and an active PVE 8→9 upgrade project, that's not a rare event. Each time, the routine was the same: reattach, notice everything's gone, dig up which Claude Code session ID belonged to which piece of work, and manually retype `claude -r <uuid>` into a fresh `tmux` window for each one. Tedious on a good day — and directly caused by the same cluster maintenance the agents in those windows were often the ones doing.

## Two independent layers

The fix splits cleanly into two problems that don't depend on each other:

1. **Does the container end up running somewhere, with its data intact?** — a Proxmox-side question.
2. **Once it's up, do the sessions come back?** — an in-container question.

Checking `pct config 603` first turned up good news: the Proxmox layer was already correct.

```
mp0: /mnt/pve/cephfs/agent-shared-workspace,mp=/opt,shared=1
onboot: 1
rootfs: cephrbd:vm-603-disk-0,mountoptions=noatime,size=30G
```

```
service ct:603 (edgar, started)
group CEPH-CORE
nodes poe,harlan,edgar,quell,kovacs
```

`onboot: 1` and an HA group with `state started` were both already set. The shared workspace at `/opt` is a proper host-side CephFS bind (`shared=1` — mandatory for HA, since it tells Proxmox this mount is cluster-wide and safe to migrate onto). And because the container's rootfs is Ceph RBD rather than local storage, `~/.claude/` — where Claude Code keeps its session transcripts — already lives on cluster storage too. It moves with the container definition regardless of which of the five `CEPH-CORE` nodes it lands on. Nothing to change here; just worth confirming rather than assuming.

That left the actual gap: nothing inside the container brought the sessions back once it booted.

## The restore mechanism

A `systemd` unit inside the container is the right place for this, specifically because it lives *inside* the LXC — it inherently follows the container across migration, failover, or reboot, with no node-detection logic needed anywhere:

```ini
# /etc/systemd/system/claude-tmux.service
[Unit]
Description=Restore Claude Code tmux sessions
After=network-online.target
Wants=network-online.target

[Service]
Type=forking
User=mcgarrah
WorkingDirectory=/opt
ExecStart=/home/mcgarrah/bin/claude-restore.sh
RemainAfterExit=yes
TimeoutStartSec=180
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

The script it calls waits for the things a fresh boot can't guarantee are ready yet — network reachability to `api.anthropic.com`, and the CephFS bind mount actually being populated (checked against a sentinel file written once, `/opt/.cephfs-ok`, rather than trusting that a mount point existing means it's not just an empty stub). Only then does it recreate each `tmux` session and resume its Claude Code conversation by ID:

```bash
CONFIG=(
  "0|w0|/opt|51dab089-7947-4c42-86a7-6a40e4bc7ed7"
  "0|w1|/opt|87ed2f30-fdb4-4272-936f-1afcd7e41aba"
  "0|w2|/opt|8c527e4e-26c7-46ae-b3b6-4fbb7752e1e4"
  "snapshield-45drive|w0|/opt/snapshield-45drive|d084489a-d972-4841-9a3e-2e90078384af"
)

for row in "${CONFIG[@]}"; do
  IFS='|' read -r sess win cwd sid <<<"$row"
  tmux has-session -t "$sess" 2>/dev/null && continue   # idempotent
  tmux new-session -d -s "$sess" -n "$win" -c "$cwd" "claude -r $sid; exec bash"
done
```

Idempotent by design — checked with `tmux has-session` before touching anything, so a `Restart=on-failure` retry, or running the script by hand to sanity-check it, never risks clobbering sessions that are already up.

This is the design as first built and reasoned through. It held up under review. It did not hold up under the real test — see below.

## The actual hard part: knowing which session ID goes where

The design above only works if `CONFIG` is accurate, and that turned out to be the real problem. Claude Code session IDs are UUIDs with no obvious link back to "the tmux window doing the ARR-suite work" unless something records that mapping — and building that mapping without disturbing four already-running agent conversations (one of which was *this one*, writing the very automation being described) ruled out most of the obvious approaches:

**Open file descriptors — dead end.** The instinct was to check what transcript file each `claude` process had open (`ls -la /proc/<pid>/fd | grep jsonl`) and read the mapping straight off the kernel. It came back empty for every process. Claude Code doesn't hold the transcript file open continuously — it opens, writes, and closes per message — so there's no persistent fd to inspect at an arbitrary point in time.

**Environment variables — closer, but not usable.** Claude Code does export a `CLAUDE_CODE_SESSION_ID` variable, readable via `/proc/<pid>/environ` for any process owned by the same user. That looked like exactly the deterministic answer needed — until checking it against the other three windows' top-level `claude` processes came back empty for all of them, while it was clearly present in this session's own environment. The variable turned out to be scoped to *tool-invocation subprocesses* — the transient shells a running agent spawns while it's actively executing a command — not the long-lived parent process. It's only observable in the narrow window while that specific agent is mid-tool-call, which makes it useless as something to poll on demand.

**What actually worked: read-only pane content, matched against transcript content.** `tmux capture-pane -p` reads a pane's visible screen buffer without sending any input — genuinely non-invasive, unlike attaching or sending keystrokes. Capturing a distinctive snippet from each window (a commit hash, a specific technical term the conversation had just used) and grepping for that exact string across the `.jsonl` transcript files in the relevant project directory picked out the right file every time, with the match verified against real message content rather than assumed from a timestamp. One window's process even confirmed independently: the user, watching a different tmux pane, could read off its actual `claude.ai` bridge session URL and match it directly against this session's own bridge ID — an outside confirmation that the content-matching approach had gotten every window right.

## Testing without breaking anything — the safe test first

The one test that actually proves any of this works — reboot the container, or `pct migrate` it, and watch the sessions come back — wasn't one to run casually. Three other agent conversations were mid-task in the other windows at the time; restarting the container to validate the happy path would have interrupted all of them without warning.

What *was* safe to verify immediately: the idempotent skip path. With every tracked session already running, invoking the restore script should detect each one via `tmux has-session` and do nothing else. Running it and diffing the pane PIDs before and after confirmed exactly that — same window count, same process IDs, nothing spawned. Real evidence the "don't touch a live session" guarantee held — but only for the narrow case of a script running against a clean, fully-up state. It said nothing about what would happen against a real, partially-recovered mess. That gap mattered more than it looked like it would.

## The real test

Two days later, all four windows sat idle at the same moment — nobody mid-task, nothing running. Good a moment as any. Picked `harlan` as the migration target (most free memory of the `CEPH-CORE` nodes) and triggered it the way HA actually does it in production, not a shortcut:

```bash
ssh edgar "ha-manager migrate ct:603 harlan"
```

`ha-manager migrate` just registers the request — the actual stop/start happens asynchronously on the resource manager's normal cycle, which is worth knowing before assuming a quiet return means nothing happened. It wasn't quiet for long. The container migrated, rebooted on `harlan`, and the report back was blunt: **the sessions did not come back, and Remote Control didn't either.** The design that looked solid on paper — verified idempotent, reasoned through carefully — failed its first real test.

### What actually happened

`claude-restore.sh` takes roughly a minute to run — its network and CephFS polling loops see to that. In that window, faster than the automation, the session running this very investigation got started back up by hand, directly in a fresh `tmux` window. By the time the systemd unit's script finally got around to checking, `journalctl` told the real story:

```
Aug 17 02:12:54 agent-dev claude-restore.sh[154]: tmux session '0' already running — skipping
Aug 17 02:12:54 agent-dev claude-restore.sh[154]: claude-restore: done
```

One log line, then done. The script's skip check — `tmux has-session -t "$sess"` — operated at the *session* level, not the window level. The moment it saw session `0` existing at all (one manually-restarted window in it, out of three that belonged there), it treated the entire session as fully handled and walked away, never attempting the other two windows. The fourth window, in its own separate tmux session (`snapshield-45drive`), had no such collision and came back exactly as designed — real, useful confirmation that the mechanism *could* work, and a clean control group for isolating what had actually gone wrong with the other one.

Second bug, sitting right next to the first: even that one correctly-restored window never got Remote Control back. The original restore command was just `claude -r $sid` — no `--remote-control` flag, which turns out to be required explicitly (`claude --help` confirms it: `--remote-control [name]`, off by default). A design that had been "verified" against its own idempotency check had never actually been checked against the thing it was supposedly protecting.

### The fix, and a third bug hiding underneath it

The obvious fix — check per-*window*, not per-session — ran straight into something that hadn't mattered until now: this container has `automatic-rename on` in tmux. Any window name assigned at creation time gets silently overwritten to match whatever's running in the foreground (`claude`, in every case) within seconds. The original design's `-n "$win"` naming, and any future check built on matching that name back, was never going to survive a second script run — it just hadn't been exercised enough yet to show it.

The real fix keys window identity on **index**, not name — confirmed stable first (`base-index 0`, `renumber-windows off`), not assumed:

```bash
for row in "${CONFIG[@]}"; do
  IFS='|' read -r sess idx cwd sid <<<"$row"
  rc_name="${sess}-w${idx}"
  sleep 3   # stagger — see below

  if ! tmux has-session -t "$sess" 2>/dev/null; then
    tmux new-session -d -s "$sess" -c "$cwd" \
      "claude -r $sid --remote-control $rc_name; exec bash"
    continue
  fi

  if tmux list-windows -t "$sess" -F '#{window_index}' 2>/dev/null | grep -qx "$idx"; then
    continue   # this specific window already present
  fi

  tmux new-window -t "$sess:$idx" -c "$cwd" \
    "claude -r $sid --remote-control $rc_name; exec bash"
done
```

Run live against the actual broken state — not a clean slate, the real mess that was still sitting there — it did exactly the right thing: left the two good windows alone, rebuilt the two missing ones. Except one of them didn't come up either, on the first attempt.

That fourth bug was a genuine race: two `claude -r` processes launched back-to-back with no delay between them, and one exited silently — no error text, just a fallback shell where a Claude Code session should have been. A manual retry of the identical command, seconds later, worked instantly. Nothing about the command itself was wrong; something about *two of them starting at once* — most likely contention over shared state in `~/.claude.json` — was. Not fully root-caused, but a 3-second stagger between window launches (visible in the loop above) made it stop reproducing, which was enough to ship.

Re-running the fixed script against the fully-restored state afterward confirmed the idempotency check actually holds this time — all four windows correctly reported "already present," nothing re-spawned.

## Keeping it current

A static, hand-built mapping is only correct at the moment it's built, and the window-index lesson from above changes what a tracking helper needs to know: it can't just take a name typed by hand, because tmux will rename it out from under the mapping within seconds anyway. The more robust move is to have the helper ask tmux directly, from inside the window being registered, rather than trust anything handed to it:

```bash
# claude-track.sh [session-id] — run from inside the window being registered
TMUX_SESS=$(tmux display-message -t "$TMUX_PANE" -p '#{session_name}')
IDX=$(tmux display-message -t "$TMUX_PANE" -p '#{window_index}')
CWD=$(tmux display-message -t "$TMUX_PANE" -p '#{pane_current_path}')
```

That `-t "$TMUX_PANE"` isn't decorative. The first version left it off, on the assumption that `tmux display-message` run from inside a pane would naturally describe that pane. It doesn't — with no explicit target, it resolves against whichever window the *attached client* currently has focused, which is a different thing entirely once more than one window exists. Tested directly: invoking it from window `0:0` while the terminal happened to be focused on window `0:2` returned index `2` — silently wrong, and exactly the kind of bug that only shows up with more than one live window to get confused between, which a single-window test would never catch.

With that fixed, the script infers a session ID (newest `.jsonl` under the matching `~/.claude/projects/` directory, when none is passed explicitly) and edits `claude-restore.sh`'s `CONFIG` array in place — updating an existing row if that session-and-index pair is already tracked, appending a new one otherwise — syntax-checking the result before finishing.

## Pulling the list out of the script

That `CONFIG` array living inside `claude-restore.sh` was fine for four windows and a single afternoon of debugging. It stopped being fine the moment the list needed editing more than once — every change meant opening a script to edit what was really just data, and every entry's only human-readable label was a raw `sess-wN` string next to a UUID. Moved it out to its own file, `claude-sessions.conf`, with one addition: a fifth field for a friendly per-window name (`primus`, `secundus`, `tertius`), passed straight through to `--remote-control` so the claude.ai bridge URL shows something meaningful instead of the auto-generated hostname-based default.

```
# tmux_session|window_index|cwd|claude_session_id|remote_control_name
multi-agent|0|/opt|51dab089-7947-4c42-86a7-6a40e4bc7ed7|primus
multi-agent|1|/opt|87ed2f30-fdb4-4272-936f-1afcd7e41aba|secundus
multi-agent|2|/opt|8c527e4e-26c7-46ae-b3b6-4fbb7752e1e4|tertius
```

`claude-restore.sh` now just loads it with `mapfile -t CONFIG < <(grep -vE '^\s*(#|$)' "$CONFIG_FILE")` — comments and blank lines skipped, everything else identical. `claude-track.sh` writes to the file directly instead of `sed`-patching a bash array embedded in a script, which is both simpler and safer: a malformed edit to a data file can't accidentally corrupt the logic that reads it.

**One field deserves its own warning, learned the hard way a few days after the real test above:** `tmux_session` isn't a cosmetic label — it has to match `tmux ls` exactly. Renaming a session in the config file without renaming the live tmux session to match (`tmux rename-session -t <old> <new>`) leaves the restore script unable to recognize the live session as already covering those windows. On the next restart it would try to create a second, duplicate session under the new name instead — the exact per-session-identity assumption this whole design already depends on, just violated from the config side instead of the tmux side this time. Caught by inspection before it ever hit a real restart, not the hard way — but worth stating plainly rather than leaving as an implicit assumption, since it's precisely the kind of thing that looks like a safe rename and isn't.

## Key takeaways

1. **Split cross-cutting problems at their natural boundary.** "Does the container come back" and "do the sessions come back" don't depend on each other and shouldn't be solved by the same mechanism. Checking the Proxmox-layer prerequisites first — and finding them already correct — meant the actual work was scoped tightly to the one layer that needed it.
2. **A systemd unit inside the container is migration-proof by construction.** No node-detection logic was needed anywhere in this design, because the unit travels with the container by definition — it just runs, wherever the container happens to be.
3. **An idempotency check is only as good as the granularity it operates at.** "Session already exists" and "every window that belongs in this session already exists" are different claims, and the design conflated them. The bug wasn't in the check being wrong — the check did exactly what it said. It was in the check answering a coarser question than the one that actually mattered.
4. **When the obvious inspection points are transient, look for something durable instead.** Both `/proc/<pid>/fd` and `/proc/<pid>/environ` looked like they should work and didn't, for the same underlying reason — they only reflect a process's *momentary* state, not its identity over time. tmux window names had the identical failure shape, one layer up: stable enough to look like an identity, not actually one.
5. **A design that passes its own test can still fail the real one.** The idempotency check was real evidence, correctly interpreted, of a narrower claim than "this works." It proved the mechanism was safe to re-run against a clean state. It said nothing about a partially-recovered, human-touched state — which is exactly the state a real HA migration produces, because a human notices something's missing and starts fixing it before the automation finishes its own polling loop.
6. **The genuine end-to-end test is worth running, even at real cost.** It found four distinct bugs a careful design review and a safe negative test both missed. Timing it for a moment when nothing was mid-task kept the cost of finding them low — but finding them at all required actually doing the thing that could break, not reasoning about whether it might.
7. **A field that looks cosmetic can be load-bearing.** Renaming a tracked tmux session in the config file without renaming the live session to match isn't a labeling change — it breaks the exact identity check the whole mechanism depends on, just from a different direction than the bugs above. The lesson from the real test wasn't "fixed forever, don't think about it again" — it was "know which parts of this are still assumptions," and that list keeps growing a little every time the system actually gets used.
