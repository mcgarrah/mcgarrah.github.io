---
layout: post
title: "Proxmox VE 8 to 9 Cluster Upgrade, Part 4: A Media Automation Stack, Built Ahead of the OS Jump — and Two Incidents That Found the Cluster's Real Limits"
image: /assets/images/og/proxmox-8-to-9-cluster-upgrade-part-4.png
categories: [homelab, proxmox, infrastructure]
tags: [proxmox, ceph, cephfs, homelab, upgrade, cluster, radarr, sonarr, prowlarr, qbittorrent, sabnzbd, bazarr, jellyseerr, wireguard, vpn, jellyfin, troubleshooting, performance]
excerpt: "The point of upgrading a six-node cluster was never the upgrade itself — it was to run more on it with confidence. With Ceph already on Squid and GPU passthrough already working, Part 4 covers standing up a full *arr media automation stack ahead of the still-pending OS jump, reusing an existing WireGuard pattern for the download client's kill switch, a handful of real coordination bugs a growing service mesh surfaces on its own, and two incidents — one memory, one disk I/O — that the new stack's first real burst of activity exposed within an hour of each other."
description: "Part 4 of a five-part series upgrading a 6-node Proxmox VE 8 cluster to Proxmox VE 9. Covers deploying a nine-container *arr media automation stack (Prowlarr, Radarr, Sonarr, qBittorrent, SABnzbd, Bazarr, Seerr, Recyclarr, caddy-ui) deliberately ahead of the OS upgrade itself, reusing an existing native WireGuard kill-switch pattern for qBittorrent instead of Docker/gluetun, several real coordination bugs surfaced by wiring independent services together (Seerr and Bazarr each caching their own copy of Radarr/Sonarr's root-folder paths, a config-drift bug that silently reverted a password fix three times, a Recyclarr crash that turned out to be an unrelated stale cache), and two incidents diagnosed back to back: Jellyfin's ffmpeg transcodes getting OOM-killed inside an undersized 2GB container, and a CephFS-wide disk I/O saturation event traced to a mass concurrent download burst overwhelming BlueStore's write pipeline on HDD-backed OSDs."
date: 2026-08-15
last_modified_at: 2026-08-16
seo:
  type: BlogPosting
  date_published: 2026-08-15
  date_modified: 2026-08-16
---

**[Part 1](/proxmox-8-to-9-cluster-upgrade-part-1/)** covered pre-flight hardening and a real backup safety net. **[Part 2](/proxmox-8-to-9-cluster-upgrade-part-2/)** covered the Ceph Reef → Squid migration required before the OS jump can even start. **[Part 3](/proxmox-8-to-9-cluster-upgrade-part-3/)** covered the NVIDIA GPU driver work, also done deliberately ahead of the jump so hardware-accelerated Jellyfin transcoding would actually work once there was a real library to transcode. The OS upgrade itself — Trixie, the new kernel, all six nodes — is still ahead; that's **Part 5**, once it's actually run.

This post is the reason the GPU work in Part 3 mattered in the first place: a real Jellyfin library, fed by a real media automation pipeline, running on the *current*, already-proven PVE 8.4 kernel rather than waiting on the OS jump — one fewer unknown to introduce at the same time as everything else. It covers standing that pipeline up — nine new containers, a download client riding an existing WireGuard pattern instead of reaching for Docker, and a handful of coordination bugs that only show up once independent services start talking to each other for real. It closes with the two incidents that mattered most: within about an hour of each other, the first real burst of activity through the new stack found a memory ceiling on Jellyfin and a disk I/O ceiling on Ceph that neither had been tested against before — found now, deliberately, before that same load has to compete with an OS upgrade too.

## The Stack: Nine Containers, One Convention

The build followed the same one-app-per-LXC convention already established across this cluster (`ct:500` Caddy, `ct:501` Homepage, `ct:502` Jellyfin) rather than a combined Docker Compose stack — consistent with a broader preference this infrastructure has for native installs over containerized ones wherever that's reasonably achievable.

| VMID | App | Role |
|---|---|---|
| 503 | Prowlarr | Indexer aggregator — the one place indexers get configured, synced out to Radarr/Sonarr |
| 504 | qBittorrent | Torrent client, VPN-gated (see below) |
| 505 | Radarr | Movie library automation |
| 506 | Sonarr | TV library automation |
| 507 | Bazarr | Subtitle automation for both libraries |
| 508 | Seerr | Request/discovery front end (the user-facing "add this to my library" UI) |
| 509 | Recyclarr | Headless — no persistent process, just a daily cron syncing TRaSH Guides quality profiles into Radarr/Sonarr |
| 510 | FlareSolverr | Cloudflare-challenge solver for Prowlarr indexers — see the dead end below |
| 511 | SABnzbd | Usenet download client |

Reverse proxy exposure matches the pattern already established for Homepage and UrBackup: `https://<cluster-ip>:<port>` blocks differentiated by port on the shared Caddy instance (`ct:500`), not per-app hostnames. Nine new `bind` blocks, nine new ports, zero new DNS records.

**One dead end worth naming plainly:** FlareSolverr was added specifically to unblock Cloudflare-protected public torrent indexers (1337x, eztv). It doesn't. Both sites gate their actual *search* pages — not their homepages, which is what a naive standalone test hits — behind Cloudflare Turnstile, a materially harder interactive challenge than FlareSolverr's headless-Chrome JS-challenge solver was ever built to pass. This was confirmed two ways: directly against FlareSolverr, and against a second, heavier tool ([Byparr](https://github.com/ThePhaseless/Byparr), a Firefox-based drop-in replacement) installed specifically to test whether a stronger anti-bot stack would fare better. It didn't — both genuinely attempted the challenge and both failed after 130–200 seconds, most likely because Turnstile also scores IP reputation, not just browser fingerprint, and a home IP with no history on either site has none to offer. FlareSolverr stays deployed for indexers with a lighter challenge, but 1337x and eztv are a closed question until a real Turnstile solver exists, not a configuration gap.

## Reusing an Existing WireGuard Pattern for the Download Client

qBittorrent needed a kill switch — torrent traffic should stop dead if the VPN tunnel isn't up, not silently fail over to the LAN IP. The [site-to-site VPN work](/networking-site-2-site-vpn/) already running elsewhere in this infrastructure meant WireGuard wasn't a new technology to introduce here, just a new application of it: a per-device tunnel config from PrivadoVPN (bundled with an existing Easynews Usenet subscription, confirmed to have an official P2P-allowed policy before committing to it), deployed as `/etc/wireguard/wg0.conf` inside `ct:504`, with `wg-quick` and `iptables` doing the enforcement — no Docker, no `gluetun` sidecar.

The kill switch itself is a fwmark-based default-reject:

```bash
# Everything qBittorrent sends gets marked by wg-quick's own routing table.
# Default REJECT on OUTPUT for anything that isn't going out the tunnel...
iptables -A OUTPUT -m mark --mark $(wg show wg0 fwmark) -j ACCEPT
iptables -A OUTPUT -o wg0 -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
# ...with an explicit LAN exception inserted ahead of the reject, so
# management access (SSH, the WebUI) survives even with the tunnel down.
iptables -I OUTPUT -d 192.168.86.0/24 -j ACCEPT
iptables -A OUTPUT -j REJECT
```

Verified the only way that actually means something: force-killing the `wg0` interface (not a graceful `wg-quick down`, which runs cleanup hooks that could mask a real failure) and confirming both DNS resolution and direct-IP traffic failed while LAN access kept working.

One real gotcha from this build, worth remembering for anyone maintaining a kill switch like this rather than just standing one up once: **never edit the live iptables rules while the app is still running against them.** `iptables -I` inserts at position 1, so a routine mid-session tweak briefly reordered the LAN-`ACCEPT` exception behind the default `REJECT` — caught quickly by checking `iptables -L OUTPUT -n -v --line-numbers` rather than trusting the edit blindly, but the brief window was enough for real ICMP-reject responses to reach qBittorrent's *already-open* UDP tracker sockets. Those sockets latched into a bad state — `Operation not permitted` on every UDP tracker — that persisted even after the ruleset itself was fixed. Only a full `systemctl restart qbittorrent-nox`, forcing fresh sockets, actually cleared it. The rule fix and the service restart are two separate remediations; doing only the first looks fixed and isn't.

## What a Growing Service Mesh Actually Costs You

Nine services that need to agree with each other about where files live, what a "good enough" release looks like, and who owns the credentials for what turned up a consistent failure shape: **independent services love caching a copy of state that belongs to a different service, and nothing tells you when that copy goes stale.**

**Seerr caches its own root-folder path per Radarr/Sonarr connection, and doesn't track the live value.** A later, unrelated fix — consolidating Radarr's and Sonarr's CephFS mounts from three separate bind-mounts down to one so hardlinked imports would actually work instead of silently falling back to copies — changed both apps' root folder paths. Seerr's *own* stored copy of those paths, set once at initial connection time, didn't follow. Every new request through the default Radarr/Sonarr connections would have failed outright until this was caught and fixed by hand. Bazarr has the identical failure shape for its own reason — it maintains its own `path_mappings` translating Radarr's/Sonarr's reported paths back to its own separate CephFS mount — and needed the same manual fix for the same underlying change. **Any service that stores a filesystem path belonging to a *different* service needs that path re-checked every time the owning service's layout changes, full stop; there's no dynamic-discovery shortcut here.**

**A live-patched config and its local source-of-truth drifting apart caused the same bug to resurface three times.** qBittorrent's WebUI password got fixed once, directly, via `sed` against the live `services.yaml` inside the Homepage container — without touching the *local* copy of that same file that every subsequent Homepage deploy actually pushes *from*. Every unrelated Homepage edit after that (adding a new widget, fixing an unrelated tile) silently reverted the password back to the stale value, because it was overwriting the live file from a local copy that had never been told about the fix. The lesson generalizes past this one file: **never patch a config live on a remote host without updating whatever local copy is the actual source of truth for the next push** — a `diff` against live before pushing again would have caught this on the first recurrence instead of the third.

**An opaque crash pointed at the most recent change, and wasn't caused by it.** Adding a second, differently-scoped quality profile to Recyclarr's config produced an immediate `.NET` `Offset and length were out of bounds for the array` exception on sync — reproduced even after fully reverting the edit, which ruled out the config change and pointed at something environmental instead: a corrupted local cache of the downloaded TRaSH Guides data. Deleting `~/.config/recyclarr/resources/` and letting it re-download fixed it outright, edit and all. Worth remembering for any tool that caches a remote definitions repo locally: an opaque crash with no config-level explanation is worth ruling the cache out before assuming the most recent edit is the culprit.

**Quality profiles assign at add-time, not continuously.** Three movies and one TV series had been added via Seerr *before* Recyclarr's curated quality profiles existed, back when Seerr's Radarr/Sonarr connections still pointed at the generic default profile with no format restrictions. Radarr and Sonarr both assign a title's quality profile once, at the moment it's added — changing the app's default profile later doesn't retroactively touch anything already in the library. The practical result: two of those movies had silently grabbed 37–40GB Remux releases, and one TV show had multiple non-compliant HDTV/Bluray-remux season packs sitting in the download queue, all invisible until checked directly against each title's actual `qualityProfileId`. Fixed with a bulk reassignment to the correct profile, a blocklist-and-remove on the non-compliant queue items, and a fresh search — but the fact that it took a direct API check to even notice is the real point. **A profile change in one of these apps is not retroactive, and nothing surfaces that on its own.**

## Incident 1: Jellyfin's Transcodes Getting Silently Killed

With the pipeline live and Jellyfin actually serving real playback again, a report came in fast: a title hanging mid-playback, looking for all the world like the server had gone offline.

It hadn't, quite. `curl` against `/System/Info/Public` returned a clean `200` — a lightweight, likely in-memory-served endpoint. `curl` against `/health` hung completely, no response at all inside a ten-second window. That split is the tell: a genuinely offline or network-partitioned server fails both identically; a server up but internally starved for threads or memory answers the cheap requests and stalls on anything that has to actually do work. Jellyfin's own log confirmed it directly:

```
[20:09:42] WRN  the heartbeat has been running for "00:00:05.9278910" which is
           longer than "00:00:01". This could be caused by thread pool starvation.
[20:10:23] ERR  FFmpeg exited with code 137
[20:11:59] ERR  Error processing request: A task was canceled.
           URL GET /videos/.../hls1/main/0.ts
[20:19:17] ERR  FFmpeg exited with code 137
```

Exit code 137 is `128 + SIGKILL` — the kernel's OOM killer, not a crash or a codec failure. The HLS segment request failing two minutes later is the exact mechanism behind "playback hung": the transcoder feeding the stream had already been killed, so the player just stopped receiving new segments. The container itself explained why: capped at 2048MB with effectively no usable swap, and Jellyfin's own base process — before any transcode even starts — was already sitting at roughly 1.9GB RSS. There was never real headroom for a transcode's `ffmpeg` child process to exist inside that limit; it was a matter of when, not if.

```bash
systemctl restart jellyfin       # clears the current hung state
pct set 502 -memory 6144         # 2048 -> 6144MB; host had 19GB free to spare
```

Both `/health` and `/System/Info/Public` returned clean `200`s immediately after the restart, with the process back to a healthy ~264MB baseline. Two things are still open rather than fully closed: `pct config` reports 512MB of swap allocated to this container, but `free -h` run *inside* it shows zero — a real discrepancy that would have meant a graceful degradation path was actually a hard cliff, worth a closer look next time this comes up. And it's still unconfirmed whether the failed transcode was actually using the hardware acceleration Part 3 spent an entire post getting working, or silently fell back to a far heavier software encode — worth checking Jellyfin's own transcode dashboard the next time a session is active.

## Incident 2: A Disk I/O Storm From the Stack's Own First Real Workload

The same viewing session also produced actual, cluster-wide `ceph -s` warnings — not adjacent to the Jellyfin incident, a second, independent finding surfaced by checking storage health directly rather than assuming the memory fix was the whole story:

```
health: HEALTH_WARN
        Slow OSD heartbeats on back (longest 2123.010ms)
        Slow OSD heartbeats on front (longest 1430.318ms)
        0 slow ops, oldest one blocked for 32 sec, daemons [osd.13,osd.4] have slow ops.
```

Multi-second heartbeat delays and ops blocked for over half a minute are not cosmetic — any read landing on an affected OSD stalls for exactly that long, which is more than enough to visibly pause video playback. `ceph osd tree` narrowed it to a specific host: `osd.4` and `osd.7`, both on `edgar`, showed slow heartbeats to nearly every other OSD in the cluster — a node-level pattern, not one failing disk. `top` on `edgar` pointed at the actual mechanism: `50% wa` (I/O wait), not CPU — a classic symptom on this cluster's HDD-backed OSDs (`ceph osd tree` confirms all fifteen are `hdd` class) when write demand outpaces what spinning disks can absorb.

The trigger was self-inflicted and easy to name: adding a paid Usenet indexer (NZBgeek) and three new public torrent indexers to Prowlarr in the same session had just triggered hundreds of near-simultaneous grabs across two shows' entire back catalogs. `/proc/diskstats`, sampled before and after a 3-second window, confirmed real queuing rather than just a busy-but-fine disk — one of `edgar`'s three data drives showed roughly 57% instantaneous utilization *and* an average queue depth of about 9 concurrent I/Os, computed from the ratio of the weighted-time field to the raw busy-time field:

```bash
# %util  = Δ(field 13, io_ticks)   / window_ms * 100
# avg qd = Δ(field 14, weighted_ms) / Δ(field 13, io_ticks)
```

A queue depth of 9 on a rotational disk means real requests waiting a real amount of time before being serviced — enough, on its own, to explain the observed multi-hundred-millisecond OSD commit latencies.

**What actually fixed it took three attempts, and the middle two only partially worked:**

1. **Throttling new download traffic** (qBittorrent capped to 8Mbps and one concurrent download, SABnzbd capped to a fraction of its prior speed) — heartbeat times improved briefly, then got worse again.
2. **Pausing Ceph's own background scrub** (`ceph osd set noscrub` / `nodeep-scrub` — standard, safe, fully reversible; the cluster had 10 scrubbing plus 5 deep-scrubbing PGs running concurrently with everything else) — cleared the `SLOW_OPS` and `MDS_SLOW_METADATA_IO` warnings from the health summary.
3. **Fully stopping all download traffic**, not just throttling it — SABnzbd's queue paused outright, every qBittorrent torrent explicitly stopped rather than speed-capped, plus `start_paused_enabled` flipped on so Radarr/Sonarr's still-running background searches couldn't quietly re-add active downloads. This is what actually mattered: I/O wait on `edgar` dropped from 69% to 10% within about a minute.

The gap between steps 1 and 3 is the real finding here. **Throttling new traffic and clearing an existing backlog are not the same fix.** BlueStore's internal write pipeline (RocksDB compaction, in this case) had already accepted far more work than the disks could keep up with in real time; slowing new arrivals down didn't undo what was already queued internally. Only actually stopping new arrivals gave the backlog room to drain. SMART health on every disk checked came back clean — this was a self-inflicted traffic jam from how much got requested at once, not failing hardware.

## Why These Two Landed Together

Neither incident was really about a bug. Jellyfin's 2GB memory cap had been fine for however long the container had been idling with nothing serious asking it to transcode. Ceph's HDD-backed OSDs had been fine under whatever background load the cluster carried before this stack existed. Both limits were real the entire time; nothing had generated enough concurrent, realistic demand to actually find them until the automation pipeline's first real burst of activity did — in the same viewing session, about ten minutes apart. That's not a coincidence so much as the expected outcome of finally pointing real, continuous, self-generated load at infrastructure that had only ever been smoke-tested.

## Key Takeaways

1. **A service that stores another service's filesystem path is a liability the moment that path changes.** Seerr and Bazarr both did this independently, and both broke the same way for the same reason — check every dependent service's cached copy, not just the app whose config you actually changed.
2. **A config fix applied directly to a live host, without updating whatever local copy the next deploy pushes from, isn't fixed — it's postponed.** Diff before you push, especially after any out-of-band edit.
3. **Quality/format policies in Radarr and Sonarr are not retroactive.** Anything added before a profile change stays on the old profile forever unless it's explicitly re-checked and reassigned.
4. **Throttling new load and draining an existing backlog are different problems with different fixes.** If slowing new traffic down doesn't relieve pressure within a reasonable window, the bottleneck is very possibly already-queued work, not the current arrival rate — stop the traffic instead of just capping it.
5. **A container's memory limit that "has always been fine" has usually just never been tested against real concurrent load.** Idle headroom and working headroom are not the same measurement.
6. **Reuse existing infrastructure patterns before reaching for new tooling.** The qBittorrent kill switch needed nothing this cluster didn't already have proven elsewhere — native WireGuard, `iptables`, and TUN passthrough on an unprivileged LXC — which is a real argument for standardizing on a small set of patterns across a growing homelab instead of picking new tools per project.

With the media pipeline live, both incidents diagnosed and fixed, and the download backlog intentionally paused until it can resume without contending with active playback, the cluster is in a genuinely better-understood state than it was before this stack existed — not because nothing broke, but because what broke was real, found fast, and fixed for reasons that generalize past this one stack.

**Part 5** picks up next: the actual Proxmox OS upgrade to Trixie, now with a real, actively-used workload on the cluster to verify against instead of an idle one.
