---
title: "ZFS Boot Mirrors on Proxmox 8 for the Homelab - Part 4"
image: /assets/images/og/proxmox-zfs-boot-mirrors-part-4.png
layout: post
categories: [proxmox, zfs, storage, homelab, ceph]
tags: [proxmox, zfs, storage, homelab, hardware, boot, mirror, ceph, ssd, uefi]
excerpt: "Part 3 laid out the plan for migrating to smaller SSDs. Here's what happened running it against a real node with both mirror drives failing at once — a UEFI dead end (the third one), four gaps the plan never anticipated, a mistake I made and had to recover from live, and a real hardware failure that surfaced while fixing the last gap."
description: "A real execution of the Part 3 planned-migration procedure against a live node with both ZFS boot mirror drives degraded. Covers the SMART trigger, a confirmed UEFI dead end on this hardware, gaps in the original checklist (SAN network, Ceph mon/mgr recreation, USB SMART quirks), a hostid mistake that broke the next boot, a live OSD failure caused by the USB gap, and full verification."
date: 2026-08-07
last_modified_at: 2026-08-07
seo:
  type: BlogPosting
  date_published: 2026-08-07
  date_modified: 2026-08-07
---

[Part 1](/proxmox-zfs-boot-mirrors-part-1/) covered replacing a failed drive with one of the same size. [Part 2](/proxmox-zfs-boot-mirrors-part-2/) covered emergency recovery when both drives fail at once. [Part 3](/proxmox-zfs-boot-mirrors-part-3/) laid out the planned migration path — downsizing to smaller SSDs with a fresh install — and even named edgar as one of the cases that shaped it. This is what happened when I actually ran that plan against edgar for real.

<!-- excerpt-end -->

## The Trigger

A smartd alert on Aug 3, 2026, for edgar's `/dev/sda`:

```
Device: /dev/sda [SAT], 67 Currently unreadable (pending) sectors
ST31000524AS, S/N: 5VPD6EX2, FW: JC45, 1.00 TB
```

Checked live rather than assumed: `sda` (Seagate ST31000524AS) had 67 pending sectors and 31 reported uncorrectable errors — previously clean. `sdb` (Toshiba MQ01ABD100) had grown from 384 reallocated sectors (the figure that flagged edgar as priority #1 in this cluster's boot-drive tracking doc) to **664**. Both sides of the mirror were now degraded. `zpool status` still showed `ONLINE` with no errors — ZFS mirrors are forgiving right up until they aren't — but this was worth treating as urgent rather than waiting for an actual fault to force the issue.

Replacement hardware: 2x Patriot P210 128GB SSDs, matching the 128GB standard already used on harlan and quell.

## Pre-Flight: The Golden Backup Checklist, Plus Two Additions

Part 3's checklist — hostid, a migration bundle of identity files, the Ceph OSD-to-disk mapping, `apt-mark showmanual` — ran without surprises. This time I added two things beyond what Part 3 originally captured:

```bash
# Full package inventory with versions, not just manually-installed names
dpkg --get-selections > apt-packages-old.txt
apt list --installed > apt-packages-versioned-old.txt

# Full /etc, excluding the cluster-shared pmxcfs mount
tar --exclude=/etc/pve -czf etc-full-old.tar.gz /etc
```

The point of both: a fresh install doesn't carry anything over silently, and "what exactly did I lose" is a much better question to answer with a real diff than with memory. That paid off later.

While I was at it, I ran the same checklist against all six cluster nodes, not just edgar — cheap insurance, and it means poe and kovacs (next in line) already have a backup on file whenever their turn comes.

One aside worth recording: the cluster's mon quorum had a separate, unrelated warning going in (`1/6 mons down, out of quorum: edgar`, with mon.edgar logging "laggy" lease warnings). edgar's own clock was confirmed synced via `timedatectl` — not the cause. A hard power cycle of the SAN switch (a Netgear GS108) fixed it before the migration even started. Filed under: when Ceph mons get flaky, check the switch before you go looking at the nodes.

That switch is a known weak point, not a one-off. It's an unmanaged consumer switch that hangs every few months, and it's the reason an HP ProCurve 2810 — managed, LACP-capable — has been sitting on a shelf waiting for a maintenance window rather than actually deployed. This incident is one more real data point for a future article: getting that SAN network onto real, LACP-bonded, managed switching instead of hoping the Netgear stays up between reboots.

## Pause Ceph, Pull the Drives

```bash
ceph osd set noout
ceph osd set nobackfill
```

Then the physical part: power down, pull the Seagate and Toshiba, install the two new SSDs. Left the other four drives (a Samsung SSD hosting the OSD DB volumes, three 4.5TB OSD block devices) alone.

## The UEFI Wall — Confirmed a Third Time

Part 3's stated plan included a UEFI upgrade alongside the SSD downsize. In the BIOS, the installer USB only showed up as a generic legacy INT13 device even with Boot Mode set to UEFI, and the blank new SSDs didn't appear in the UEFI boot list at all.

Before spending real time debugging BIOS firmware on hardware from 2011, I checked something first: **harlan and quell — the cluster's only two prior SSD migrations — are both still Legacy BIOS + GRUB today**, despite Part 3 stating UEFI as the goal for both. This was the third attempt to get UEFI working on a Dell OptiPlex 990, and the third wall. Decision: stay on Legacy BIOS/CSM + GRUB, matching the two nodes that actually work. Not a failure — a confirmed, load-bearing fact about this specific hardware that Part 3 didn't have going in.

## Fresh Install

Straightforward: ZFS RAID1 on the two new SSDs only, same hostname and IP (`edgar`, `192.168.86.14/23`) as before, Legacy BIOS path. The one thing worth flagging for anyone following along: the installer's email field is for the local `root@pam` user and isn't part of cluster identity — check `/etc/pve/user.cfg` on a healthy node for what the rest of the cluster uses, rather than guessing.

## Post-Install: The Diff Told the Real Story

With the fresh install up, I pulled the old node's backup down (CephFS isn't mounted yet — the node hasn't rejoined — so I proxied the file through an already-joined node instead) and restored identity: `zgenhostid`, subuid/subgid.

The subuid/subgid restore mattered for real, not hypothetically — the fresh install was missing `root:501:2`/`root:501:1` that old edgar had. Part 2 documented this exact class of gap breaking a Jellyfin LXC during the Harlan recovery; here it was silent until diffed, but the diff caught it before it became a mystery later.

Then the new package/config snapshots, diffed against the old ones:

**Missing from the fresh install (93 packages)** — most importantly, *all of Ceph* (expected, fixed below), plus `pve-nvidia-vgpu-helper` (edgar has a Quadro K600), and ordinary tools: `sudo`, `tmux`, `jq`, `parted`, `nvme-cli`, `lsscsi`, `cryptsetup-bin`, `uuid-runtime`, `needrestart`.

**New on the fresh install, not on old edgar**: `frr`/`frr-pythontools` — the FRR routing daemon, apparently bundled by default in the current PVE 8.4 ISO, never installed on old edgar.

Before reinstalling Ceph, I ran the Proxmox community post-install helper's repo fixes rather than trust the ISO defaults. Good thing — the fresh ISO's `ceph.list` pointed at **`ceph-quincy` enterprise**, but this cluster runs **Ceph Reef** (confirmed live: `ceph version` → `18.2.8 reef`) on the no-subscription repo. Checked against a healthy node and matched exactly:

| Prompt | Answer for this cluster | Why |
|---|---|---|
| Correct Proxmox VE sources? | Yes | Correct repo set for the release |
| Disable `pve-enterprise`? | Yes | No subscription |
| Enable `pve-no-subscription`? | Yes | Required for `apt update` to work at all |
| Correct Ceph package repos? | Yes — to **Reef**, not the ISO's default Quincy | Must match the cluster's actual Ceph version |
| Add (disabled) `pvetest`? | No | Not wanted here |
| Disable subscription nag? | Yes | Cosmetic |
| Disable High Availability services? | Check `ha-manager status` first | Don't diverge one node from the other five without checking |

With the repos fixed, `apt-get install ceph ceph-mon ceph-osd ceph-mgr ceph-mds ceph-mgr-dashboard ceph-volume sudo tmux jq parted nvme-cli lsscsi cryptsetup-bin uuid-runtime needrestart pve-nvidia-vgpu-helper` pulled in exactly `18.2.8 reef` — matching the rest of the cluster precisely.

## Rejoining the Cluster: A Key-Trust Chicken-and-Egg

`pvecm add <healthy-node-ip>` failed with `EOF while reading password` — no TTY for an interactive password prompt over a scripted SSH session. The actual fix wasn't a password at all: the cluster's shared `authorized_keys` (which lives in `/etc/pve`, itself cluster-shared) still had the *old* edgar's key, and the *new* edgar's key wasn't anywhere yet — classic chicken-and-egg for a freshly-wiped node.

Fixed by hand: replaced the stale key entry with the new one via an already-joined node, then hit a second, related snag — the other nodes' `known_hosts` still had edgar's *old* SSH host key, so reverse-direction SSH failed strict host-key checking. Cleared with `ssh-keygen -R 192.168.86.14` on every node, re-seeded edgar's local `authorized_keys` with the cluster's existing keys so trust worked in both directions, and `pvecm add --use_ssh 1` went through cleanly on the next attempt — including the `/etc/pve` busy-mount case Part 3 warns about, which didn't come up this time.

## OSD Reactivation Was Three Gaps, Not One

Part 3's checklist covers OSD reactivation. It turned out a node running mon+mgr+osd together — which is every node in this cluster except tanaka — loses more than that.

**1. `ceph-volume lvm activate --all` failed immediately** — `/etc/ceph/ceph.conf` (a symlink to the real config in `/etc/pve`) doesn't exist on a fresh `apt install ceph`. One `ln -sf` and activation succeeded for all three of edgar's OSDs (`osd.1`, `osd.4`, `osd.7`).

**2. The OSDs "activated successfully" but stayed `down`.** The real error, in the systemd journal: `bind unable to bind to v2:10.10.10.14:7568 ... Cannot assign requested address`. The **second NIC/bridge for the Ceph SAN network (`vmbr1`, 10.10.10.0/23) was never configured** — the Proxmox installer only sets up one interface, and Part 3's checklist backs up `/etc/network/interfaces` but never says to actually restore the non-management bridges from it. Diffed old against new, found the missing block, added it back, `ifreload -a`. The OSDs still wouldn't start on the next attempt — systemd's restart-rate-limiter had latched onto the earlier repeated failures and was silently refusing new start requests. `systemctl reset-failed` cleared it, and all three OSDs came up.

**3. mon.edgar and mgr.edgar didn't exist at all.** Their local state lives under `/var/lib/ceph/{mon,mgr}/` — also on the wiped boot drive, also never mentioned in Part 3's checklist. `pveceph mon create` refused with "address already in use," because `/etc/pve/ceph.conf` — a separate, static file from the live monmap — still had a stale `mon_host` entry and a `[mon.edgar]` section from before the wipe. The live monmap itself needed the same cleanup (`ceph mon remove edgar`, confirmed with a second pair of eyes before running it, since it's a shared-infrastructure change). With both cleaned, `pveceph mon create` and `pveceph mgr create` each succeeded on the first try.

## The Mistake

Here's the one I made and had to recover from live, kept in rather than smoothed over.

Part 3's hostid-restore step (`zgenhostid <old-value>`) exists for *re-importing an existing pool* during an emergency recovery, where the pool's on-disk metadata already expects the old system's identity. I ran it anyway, out of habit, on a pool the fresh installer had just *created* under its own new hostid — which doesn't need that step at all, and actively creates a mismatch when you force it.

Nothing broke immediately. It broke on the *next* reboot: running the community post-install script's kernel/microcode updates triggered an `initramfs` rebuild, which baked the now-mismatched hostid into the boot image. The following reboot dropped straight to an `initramfs` prompt: `rpool` cannot be imported.

Not data loss — a safety check refusing an import it thought looked suspicious. Recovered with:

```
zpool import          # confirm what it sees and why, before forcing anything
zpool import -f -N rpool
exit
```

That force-import re-stamps the pool's recorded hostid to match, so it didn't recur on the reboot after that — confirmed by actually rebooting again rather than assuming it was fixed.

**The actual lesson for Part 3**: the hostid-restore step should be conditional. Only run it when reimporting a pool that predates the current install. Never run it against a pool the current install just created.

## Final Verification

```bash
ceph -s
# HEALTH_OK
# mon: 6 daemons, quorum poe,kovacs,quell,tanaka,harlan,edgar
# mgr: tanaka(active), standbys: poe, harlan, quell, kovacs, edgar
# osd: 15 osds: 15 up, 15 in

zpool status -v rpool
# ONLINE, mirror-0 on the two new SSDs, 0 errors

zpool scrub rpool
# scrub repaired 0B in 00:00:07 with 0 errors

proxmox-boot-tool status
# both ESPs configured with grub, both kernel versions present

pvecm status
# AlteredCarbon, 6 nodes, quorate
```

Back to the exact pre-migration baseline, on new 128GB SSDs, with PVE and the kernel updated (8.4.19, `6.8.12-39-pve`) along the way.

## A Fourth Gap, Found the Next Day

This cluster's Seagate USB drives (three OSD block devices and one backup drive, all on edgar) need a `usb_storage.quirks=` GRUB parameter to report SMART data at all — covered in an [earlier article](/usb-drive-smart/) and its [production update](/usb-drive-smart-updates/), and living in its own drop-in file, `/etc/default/grub.d/usb-quirks.cfg`.

That file was never part of the Golden Backup Checklist. It's a separate concern from `/etc/default/grub` itself (which the checklist does capture), so it silently didn't survive the fresh install. Confirmed the next day: every other node in the cluster had the identical file; edgar didn't.

This wasn't a theoretical gap for long. While confirming it was actually missing, `osd.7` — backed by one of edgar's Seagate USB drives — threw a real hardware I/O error and the drive dropped off the USB bus entirely, reappearing under a new kernel device name a few minutes later (`sdf` → `sdh`). The data was fine — `pvscan` found the LVM volume intact under the new name — but the block device itself kept refusing reads until something forced a clean USB re-enumeration. Exactly the class of instability those two earlier articles exist to reduce, showing up live in the middle of confirming the gap that let it happen.

Fixed by restoring the quirks file (and, while at it, actually creating the CephFS master copy the original USB-SMART article described but that had never really been done), refreshing the boot config, pausing Ceph, and rebooting. The reboot did double duty: it loaded the quirks parameter *and* forced the stuck drive to re-enumerate cleanly. Both problems gone in the same action — `smartctl -d sat -H` now reports real Seagate model numbers and PASSED on all four USB drives instead of generic "Portable"/"Expansion HDD" labels, and all three OSDs came back up on their own.

## What This Changes for Next Time

- **Stop planning for UEFI on this hardware.** Three attempts, three walls (harlan, quell, edgar). poe and kovacs — the two remaining HDD nodes — should budget zero time on it and go straight to Legacy BIOS/GRUB.
- **A mon+mgr+osd node needs more than OSD reactivation.** `pveceph mon create` and `pveceph mgr create`, plus checking `/etc/network/interfaces` for a second bridge, are now part of the real checklist — not just `ceph-volume lvm activate --all`.
- **The hostid-restore step is conditional**, not a reflex. Only for a pool that predates the current install.
- **The apt/etc diff is worth keeping.** It's what actually caught the missing Ceph packages, the vGPU helper, and the stale enterprise Ceph repo — all things that would otherwise have surfaced one at a time, later, as separate confusing failures instead of one upfront list.
- **A node with USB-attached drives needs its `usb_storage.quirks` GRUB drop-in restored explicitly.** It's not covered by the ZFS boot-mirror checklist at all — a separate concern that needs its own line item.

tanaka (an Apple HDD with reallocated sectors climbing fast) was next in line, and by the time this posts it's already done — see [Part 5](/proxmox-zfs-boot-mirrors-part-5/) for how a migration goes when all four of these gaps are fixed proactively instead of found live. Two nodes left on spinning rust after that: poe (oldest drives in the cluster, 6+ years) and kovacs (5 years, stable but aging). Same procedure, same hardware family, same UEFI answer already settled going in.

## Related Articles

- [ZFS Boot Mirrors on Proxmox 8 - Part 1](/proxmox-zfs-boot-mirrors-part-1/) — Same-size drive replacement
- [ZFS Boot Mirrors on Proxmox 8 - Part 2](/proxmox-zfs-boot-mirrors-part-2/) — Emergency recovery from catastrophic dual-drive failure
- [ZFS Boot Mirrors on Proxmox 8 - Part 3](/proxmox-zfs-boot-mirrors-part-3/) — The planned-migration procedure this article executes
- [Enabling SMART Monitoring on Seagate USB Drives](/usb-drive-smart/) — The original UAS quirks fix this article's fourth gap is about
- [USB Drive SMART Updates](/usb-drive-smart-updates/) — Production experience and the GRUB parameter approach
- [Monitoring ZFS Boot Mirror Health in Proxmox 8 Clusters](/proxmox-zfs-boot-mirror-smart-analysis/) — SMART monitoring and alerting
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — All my Proxmox and Ceph articles in one place
