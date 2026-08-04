---
title: "ZFS Boot Mirrors on Proxmox 8 for the Homelab - Part 5"
image: /assets/images/og/proxmox-zfs-boot-mirrors-part-5.png
layout: post
categories: [proxmox, zfs, storage, homelab, ceph]
tags: [proxmox, zfs, storage, homelab, hardware, boot, mirror, ceph, ssd, uefi]
excerpt: "Part 4 found four gaps the hard way, live, under pressure. This is the same migration run against tanaka the very next day with all four fixed proactively — plus a real hardware detour before any of the software even mattered, and one genuinely new finding Part 4 never hit."
description: "The tanaka boot-mirror migration (2x HDD to 2x 128GB SSD), run one day after Part 4's edgar migration with every lesson from that article applied up front: SSH trust, Ceph repos, ceph.conf/monmap cleanup, the SAN bridge, and the USB SMART quirks file. Covers a real hardware troubleshooting detour before the OS even mattered, a new pvecm add finding, and where the cluster's remaining spinning-rust nodes stand."
date: 2026-08-08
last_modified_at: 2026-08-08
seo:
  type: BlogPosting
  date_published: 2026-08-08
  date_modified: 2026-08-08
---

[Part 3](/proxmox-zfs-boot-mirrors-part-3/) laid out the planned migration procedure. [Part 4](/proxmox-zfs-boot-mirrors-part-4/) ran it against edgar and found four gaps the hard way — live, mid-migration, under pressure. This is the same migration run against tanaka the very next day, with all four of those gaps fixed proactively instead of discovered on the fly. It went almost boringly well, which is exactly the point — except for one problem that had nothing to do with Proxmox at all.

<!-- excerpt-end -->

## The Trigger

Live SMART checks across the whole cluster on Aug 3, 2026 (the same pass that flagged edgar) turned up a second node worth watching: tanaka's `sdb` (Apple HDD HTS547550A9E384) had jumped from 1 reallocated sector to **25** since the last check. `sda` (Seagate ST3500418AS) stayed clean. Not yet the acute failure edgar was living through, but a real trend — the same reallocated-sector escalation pattern, one node behind.

Replacement hardware: 2x 128GB SSDs, matching the cluster's standard size (harlan, quell, and now edgar are all 128GB). Same topology as edgar too — 128GB is smaller than tanaka's existing 465.8GB mirror members, so ZFS won't allow an in-place `zpool replace` (`device is too small`, confirmed rather than assumed). A fresh install was the only option, same as edgar.

## A Real Hardware Detour, Before Any of the Software Mattered

Tanaka is a Dell OptiPlex 990 **Desktop** chassis rather than the Tower variant the other five nodes use — same BIOS generation, different case. After swapping the drives and powering back on: nothing. Green power light, no fan spin-up signal on the display, no keyboard LED response across three different monitor connections (VGA, HDMI off the motherboard, DisplayPort/DVI off the Quadro K600).

Two separate problems, both mechanical, neither one a drive issue:

1. **A loose VGA cable** at the monitor end — looked identical to "the board is dead" from the chair, and only showed itself once a DVI-to-HDMI adapter was tried on a different port and actually produced a picture.
2. **A SATA power connector with a 90° bend** right at the connector body, causing an intermittent power fault to one of the new SSDs. Swapped for a flat, straight extender cable and the drive appeared immediately.

Neither of these would show up in any runbook. They're exactly the kind of thing the [***trash can*** **crash cart** (TC<sup>3</sup>)](/proxmox-upgrade-issues/) earns its keep on — a spare monitor, keyboard, and a pile of VGA/DVI/DisplayPort/HDMI adapters kept on hand specifically so "is it actually dead or is it a cable" takes five minutes to answer instead of becoming its own outage. That cart was built for a much worse night (a power-outage recovery with four overlapping hardware failures at once); tonight it just made quick work of two small mechanical problems. Worth having on hand for any hands-on hardware work, not just migrations.

## Pre-Flight

Nothing new to do here — the Golden Backup Checklist (plus the two additions from Part 4: full apt inventory with versions, and a full `/etc` tarball excluding the shared `/etc/pve` mount) had already been run against all six nodes back when edgar's migration started, tanaka included. No last-minute scramble; the backup was just sitting there waiting.

## Fresh Install

ZFS RAID1 on the two new SSDs, Legacy BIOS/GRUB from the start — no time spent testing UEFI first. This is the fourth confirmed case on this hardware family (harlan, quell, edgar, now tanaka), and the third was already conclusive. Same hostname and IP as before (`tanaka`, `192.168.86.15/23`).

## Post-Install: Applying Every Gap Proactively

This is where Part 4's lessons actually paid off. Everything below was done *before* it could cause a failure, in the order that avoids re-hitting edgar's snags:

| Gap (found live on edgar) | Handled on tanaka |
|---|---|
| SSH key trust chicken-and-egg | Cleared stale host keys cluster-wide, swapped tanaka's new keypair into the shared `authorized_keys`, seeded tanaka's own local file with the cluster's keys — all *before* attempting to join |
| Wrong default Ceph repo (Quincy enterprise vs. Reef no-subscription) | Fixed repos first, then installed Ceph packages — `apt-get update` came back clean on the first try |
| `/etc/ceph/ceph.conf` missing after `apt install ceph` | Symlinked to `/etc/pve/ceph.conf` immediately, no failed `ceph-volume` command needed to discover it |
| Missing SAN bridge (`vmbr1`, 10.10.10.0/23) | Diffed `/etc/network/interfaces` against the backup, restored the block, confirmed reachable to all 5 peers before moving on |
| Missing USB SMART quirks file | Restored from the CephFS master copy (`/mnt/pve/cephfs/configs/usb-quirks.cfg` — created for real during edgar's fix) even though tanaka has no USB drives attached today, for cluster-wide consistency |
| Stale monmap / `ceph.conf` entries blocking `pveceph mon create` | Cleaned `ceph mon remove tanaka` and the `[mon.tanaka]` section in `/etc/pve/ceph.conf` *before* ever attempting mon create |

Two smaller things confirmed rather than assumed, per Part 4's own advice not to skip the diff just because it "should" match: the GRUB kernel command line matched the old node's exactly (nothing lost), and `/etc/subuid`/`/etc/subgid` were missing the same `root:501:2`/`root:501:1` lines edgar's fresh install had dropped — restored the same way.

One thing came up that edgar's article didn't need to cover: `intel-microcode` isn't installable from this cluster's normal repos (none of the nodes have `non-free-firmware` enabled in `/etc/apt/sources.list`, confirmed by checking a healthy node). Rather than permanently enable that repo by hand, the fix is to let the Proxmox community **microcode** helper script handle it — it enables what it needs temporarily and installs cleanly. Left `intel-microcode`/`iucode-tool` out of the manual package batch for exactly that reason.

## Rejoining the Cluster: One Genuinely New Finding

With SSH trust fixed proactively, `pvecm add <healthy-node-ip>` was expected to just work this time. It didn't — same `EOF while reading password` error Part 4 hit, despite direct key-based SSH between the nodes working perfectly in both directions.

The actual fix: `pvecm add <ip> --use_ssh 1`, forcing the join process to use the SSH path explicitly rather than whatever it tries by default. That one flag took it from a hard failure to a clean success:

```
forcing overwrite of configured node 'tanaka'
copy corosync auth key
stopping pve-cluster service
waiting for quorum...OK
merge authorized SSH keys
successfully added node 'tanaka' to cluster.
```

This is a real, new addition to the checklist — not something carried over from edgar, since edgar's own join (eventually) went through without needing it explicitly.

## Mon/Mgr Recreation: First Try, Both Times

```bash
pveceph mon create   # succeeded immediately — no "address already in use"
pveceph mgr create   # succeeded immediately
```

No repeat of edgar's stale-`ceph.conf` port conflict, because that cleanup happened *before* either command ran, not after the first one failed.

## Final Verification

```bash
ceph -s
# HEALTH_OK
# mon: 6 daemons, quorum poe,kovacs,quell,harlan,edgar,tanaka
# mgr: poe(active), standbys: harlan, quell, kovacs, tanaka, edgar
# osd: 15 osds: 15 up, 15 in   -- untouched throughout; tanaka has no OSDs

zpool status -v rpool
# ONLINE, mirror-0 on the two new SSDs, 0 errors

zpool scrub rpool
# scrub repaired 0B in 00:00:10 with 0 errors

proxmox-boot-tool status
# both ESPs configured with grub, both kernel versions present

pvecm status
# AlteredCarbon, 6 nodes, quorate
```

The community post-install and microcode scripts were run interactively afterward (same repo-fix choices as Part 4: disable enterprise, enable no-subscription, correct Ceph repos, disable the nag, leave HA and corosync enabled since this is a real 6-node cluster). One deliberate reboot followed, bringing in a newer kernel (`6.8.12-39-pve`) along with the microcode package. The only thing that came back momentarily off was a `HEALTH_WARN` clock-skew warning on the fresh mon — normal for a few seconds while NTP catches up right after a cold boot, and it cleared on its own well under a minute later. Worth knowing so it doesn't read as a real problem the next time a freshly-rejoined mon shows it.

## What This Confirms

Part 4 closed with a list of five things to change for next time. Running tanaka the next day is the actual test of whether that list held up, and it did — every one of the five gaps Part 4 found live was either a non-issue here or fixed before it could become one:

- **No UEFI time wasted.** Fourth confirmed wall on this hardware family; went straight to Legacy/GRUB.
- **Mon+mgr recreation worked first try**, both commands, because the stale `ceph.conf`/monmap cleanup happened before rather than after a failure.
- **The hostid mistake wasn't repeated** — `zgenhostid` was never run against tanaka's fresh pool, since it's a new pool under a new install, not a re-import.
- **The apt/etc diff caught real gaps again** (subuid/subgid, the vGPU helper, the same Ceph repo mismatch) — worth keeping as a standard step, not a one-off for edgar.
- **The USB quirks file was restored even though tanaka has no USB drives today** — cluster-wide consistency, no live incident to force the issue this time.

The one thing that wasn't on that list — `pvecm add` needing `--use_ssh 1` explicitly — is the actual new data point from this run, and now it's part of the checklist for poe and kovacs too.

The hardware detour is the other real takeaway, and it has nothing to do with any of the above: a loose monitor cable and a bent SATA power connector cost more real troubleshooting time than the entire software side of this migration combined. No amount of proactive checklist work prevents that kind of thing — only a crash cart with spare cables on hand shortens it.

With tanaka done, the cluster has two nodes left on spinning rust: **poe** (the oldest drives in the cluster, 6+ years, still SMART-clean and stable) and **kovacs** (5+ years, also stable). Neither is showing the kind of reallocated-sector escalation that made edgar and tanaka urgent — both are aging, not degrading. That takes real pressure off the schedule: poe and kovacs can move at a normal cadence rather than an emergency one, with a fully proactive checklist and, now, four other successful migrations' worth of lessons already banked before either of them needs a single command run against it.

## Related Articles

- [ZFS Boot Mirrors on Proxmox 8 - Part 1](/proxmox-zfs-boot-mirrors-part-1/) — Same-size drive replacement
- [ZFS Boot Mirrors on Proxmox 8 - Part 2](/proxmox-zfs-boot-mirrors-part-2/) — Emergency recovery from catastrophic dual-drive failure
- [ZFS Boot Mirrors on Proxmox 8 - Part 3](/proxmox-zfs-boot-mirrors-part-3/) — The planned-migration procedure this article executes
- [ZFS Boot Mirrors on Proxmox 8 - Part 4](/proxmox-zfs-boot-mirrors-part-4/) — edgar's migration, and the four gaps found live that this article fixes proactively
- [Proxmox Upgrade Issues: A Crash Cart Recovery Story](/proxmox-upgrade-issues/) — Where the trash-can crash cart (TC³) comes from
- [Enabling SMART Monitoring on Seagate USB Drives](/usb-drive-smart/) — The original UAS quirks fix behind the USB gap
- [USB Drive SMART Updates](/usb-drive-smart-updates/) — Production experience and the GRUB parameter approach
- [Monitoring ZFS Boot Mirror Health in Proxmox 8 Clusters](/proxmox-zfs-boot-mirror-smart-analysis/) — SMART monitoring and alerting
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — All my Proxmox and Ceph articles in one place
