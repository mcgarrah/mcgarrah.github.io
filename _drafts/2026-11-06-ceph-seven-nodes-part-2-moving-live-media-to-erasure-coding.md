---
layout: post
title: "Seven Ceph Nodes, Part 2: Moving a Live Media Library to Erasure Coding"
categories: [homelab, ceph, proxmox]
tags: [ceph, cephfs, erasure-coding, proxmox, usb-storage, migration, jellyfin, observability, runbooks, dell-optiplex-990]
excerpt: "Part 2 of 2. The copy-and-rename plan from Part 1 worked for thirteen small directories and failed for the libraries people are watching. I replaced it with a per-file rewrite that keeps Jellyfin up, wrapped it in a seven-node watchdog, and then spent two days finding out what USB-attached OSDs do under sustained load."
description: "Migrating a live CephFS media library to a k=4,m=2 erasure-coded pool without taking the media server down: why directory swaps fail with bind mounts and active writers, a rate-limited in-place file rewrite with checksum verification, a watchdog across seven nodes, and the recovery steps for a USB OSD the kernel marked offline. Measured numbers and the mistakes along the way."
date: 2026-11-06
last_modified_at: 2026-11-06
seo:
  type: BlogPosting
  date_published: 2026-11-06
  date_modified: 2026-11-06
series: "Seven Ceph Nodes"
series_part: 2
---

In [Part 1](/ceph-seven-nodes-fewer-daemons-and-erasure-coding/) I trimmed the daemons and wrote a plan for erasure coding: create a `k=4, m=2` pool, copy each top-level directory across, verify, delete the original, rename. One directory at a time, smallest first. It was a good plan for a data set nobody was using. The media library is not that data set, and the cluster underneath it is built from desktop PCs with USB drives, which turned out to matter more than any Ceph setting.

<!-- excerpt-end -->

I did this work with an AI agent doing the hands-on typing under my direction, and I made the calls. This post is the account: what worked, what I had to replace, and the numbers.

## Where the cluster stands three weeks later

The raw capacity table from Part 1 is out of date. Jaeger's drives were weighted in and more USB drives were promoted to OSDs after I wrote it, which took the cluster from 28 OSDs and 98 TiB raw to 32 OSDs and 117 TiB.

| | November 6 |
|---|---|
| Raw capacity | 117 TiB (115 TiB HDD, 1.9 TiB SSD) |
| Raw used | 57 TiB, 48.4% |
| OSDs | 32 up and in, Ceph 19.2.5 |
| `cephfs_data` (replicated, 3 copies) | 18 TiB logical, 54 TiB raw |
| `cephfs_data_ec` (4+2) | 260 GiB logical, 390 GiB raw |

The daemon layout from Part 1 held, with one change. Monitors are still on harlan, kovacs, poe, edgar and tanaka, and managers on tanaka, edgar and harlan. The metadata servers are now tanaka active, harlan as the hot standby and edgar as the spare. On October 14 it was edgar as the hot standby and harlan as the spare, and I did not track when that swapped. The quorum has been unbroken for ten days, and neither of the two monitors I checked (harlan and poe) logged an election since October 27. I am not crediting the trim for that. The cause of the election storm was rocksdb compaction, and the fix for that went in on October 5. What I can say is that the smaller daemon set did not make anything worse: the single active MDS carried the whole migration without a failover or a warning.

## The pool setup was the easy part

```bash
ceph osd erasure-code-profile set ec-4-2 k=4 m=2 crush-failure-domain=host crush-device-class=hdd
ceph osd pool create cephfs_data_ec 32 32 erasure ec-4-2 --bulk
ceph osd pool set cephfs_data_ec allow_ec_overwrites true
ceph osd pool application enable cephfs_data_ec cephfs
ceph fs add_data_pool cephfs cephfs_data_ec
```

The pool came up with `size 6` and `min_size 5`, as the arithmetic in Part 1 predicts: one host down leaves every placement group at five chunks and still serving. With `--bulk`, the autoscaler took it from 32 placement groups to 256 on its own. Before trusting any of it with real data, I made a scratch directory, pointed its layout at the new pool, and wrote a 64 MiB random file. It landed as sixteen 4 MiB objects in `cephfs_data_ec`, and the checksum matched after dropping the page cache. That ten-minute test is the one I would not skip.

## Thirteen directories went fine, and two things went wrong

I wrote a small script for the swap: copy to `NAME.ec` with the layout set, compare entry counts and byte totals, run a checksum dry run, remove the original, rename. It moved configs, bin, backups, github, drivers, the pillbox, godot and nutrition workspaces, discover, template, staging and recycle-bin, and then the shared agent workspace, about 65 GB in all.

The first failure was mine. On the 2,680-entry `github` directory the script stopped without printing anything. A `find ... | head -1` under `set -o pipefail` gets a SIGPIPE when `head` exits early, and `pipefail` turned that into a silent exit. The original was untouched, because the delete step comes after the verification, which is the only reason I did not care much. I fixed the line and reran it.

The second was Proxmox. Moving `template`, the script's `rm -rf` of the original failed with "Directory not empty" after deleting all fifteen files. The Proxmox CephFS storage had re-created empty `iso` and `cache` directories inside it mid-delete. The copy had already passed verification, so I removed the empty leftovers by hand, renamed the copy into place, and confirmed `pvesm list` still saw the ISOs. No data lost, one more reason the verification has to come before the delete and not after.

The shared agent workspace needed more care, because it is the `/opt` mount of the containers where the agents run, including the one I was working in. I wrote an unattended script on a different node that stopped both containers, copied and swapped 2 GB (33,394 entries, 15 minutes), and always restarted them, even on failure. Starting it ended my own session. Everything came back 16 minutes later with the data on the EC pool.

## Why the swap fails for a live library

The two directories that matter are 4.8 TB of movies and 14.3 TB of TV, and three things broke the plan for them.

Bind mounts. Jellyfin mounts `movies`, `tvshows` and the other libraries as subdirectory bind mounts, read-only. A swap replaces the directory, and a container that mounted the old one keeps a handle to a directory that no longer has a name. Every directory swap would have needed Jellyfin restarted, and I had already done that dance once for a small directory.

Writers. Radarr, Sonarr and Bazarr write into those directories all day. Anything they write to the original during a copy that takes weeks is gone when the original is deleted.

Time and space. Copy-then-delete holds roughly 1.5 times the directory's size in extra raw space until the last step, and for the TV library that is about 21 TB.

I wanted a way to move data that never replaces a directory. Ceph supports one, and I had been underusing it: a directory layout only affects files created after it is set, but it can be set at any time, and a file's pool is fixed when the file is created. So set the layout first, and every new import lands on the EC pool. Then rewrite each existing file in place: copy it, verify it, and rename the copy over the original. The path never changes. Jellyfin, Tunarr and ErsatzTV never notice.

## The rewrite, and the test that decided it

The one thing I had to be sure of before running it on media was what happens to a stream that is playing when its file is replaced. On CephFS an open file keeps its inode, so in theory the player keeps reading the old data. I tested it instead of relying on theory. I created a 120 MB file, started a slow reader on poe, and while it was reading I replaced the file from harlan with `mv -T`. The reader finished all 125,829,120 bytes of the original, and its SHA-256 matched the original. The next open would get the new file.

The script (`ec-rewrite.py`, about 390 lines) does this for each file:

1. Skip it if it has more than one hard link, is empty, or was modified in the last 15 minutes.
2. Copy it into a hidden holding directory on the same filesystem, with the EC layout, at a capped rate, hashing the stream as it goes. A temporary file outside every library cannot be picked up by a library scanner.
3. Fsync, restore owner, mode and times, drop the cached pages, read the copy back at a capped rate, and compare the hash.
4. Check the source's inode, size and mtime have not changed since step 1.
5. Rename over the original, then confirm the file reports the EC pool.

The hard-link count mattered. Radarr and Sonarr import by hard link from the download directories, and rewriting one name of a linked file breaks the link and leaves a second copy on the old pool. I counted before choosing: 27 files in `movies`, 204 in `tvshows`, 231 in `downloads`. Few enough to skip in the first pass and handle at the end. There is also one honest race: if Sonarr replaces a file in the few milliseconds between step 4 and step 5, my rename puts the old content over its new file. The 15-minute rule covers fresh imports and upgrades are rare, so I accepted it and said so in the runbook.

I tested the script on a scratch directory before the real ones. It skipped a hard-linked pair, a fresh file and an empty file, skipped a file I replaced while it was copying and left my new content in place, and preserved owner, mode and mtime on the rest.

## A watchdog that could see all seven nodes, eventually

A run measured in days needs something that stops it on its own. The script checks every minute: the USB and I/O error counters in `dmesg` on every node, whether any OSD is down or restarted, inactive placement groups, a corosync link-down, and how many OSDs report slow BlueStore operations. Any change stops the run with a distinct exit code and no automatic restart.

The first version could only see five of the seven nodes, because harlan could not ssh to kovacs or jaeger: `Host key verification failed`. The cluster's shared host-key file was dated June 2024. It held RSA keys for the five original nodes, nothing for quell, jaeger or kadmin, and three of the five entries no longer matched the nodes (harlan, edgar and tanaka have all been rebuilt or replaced since). On this Proxmox version `pvecm updatecerts` changes nothing. I did not loosen host-key checking. I read each node's own public host keys over a channel I already trusted, wrote all 24 entries (three key types for each of eight nodes) into the cluster file, and linked it into `/etc/ssh` on every node. All 56 ordered pairs of nodes now connect by name with strict checking still on. Until that was fixed, the script's first run could not read two of the seven nodes at all, which is a bad property for something that claims to watch all of them. The repair is a story of its own.

## What the USB drives did

Everything above is the part I designed. This is the part I had not planned for.

Tanaka's USB drives started resetting. A reset shows up as a burst of `uas_eh_abort_handler` messages and then one `reset SuperSpeed USB device`. Between the afternoon of November 4 and the morning of November 6 the counter rose by 28, which is 14 resets in about 45 hours, across three different drives. One of them happened with the rewrite stopped, so it is not just my load. The first two stopped the run, and I could see the pattern was going to stop it every hour or two forever while doing nothing to the cluster, since no OSD ever went down.

So I made a decision with an explicit cost. A lone tanaka reset, with no real I/O error and no OSD affected, is logged, the copy pauses for five minutes, the cluster is re-checked and the run resumes. Three tanaka resets inside an hour, any `I/O error` line, or anything at all on another node still stops it. I tested those cases in a simulation before restarting. The rule is temporary and documented as temporary. It exists because the hardware is suspect and I am not in Raleigh until Saturday.

The more serious event was on jaeger. At 16:48 on November 5, osd.29 went down: two USB resets on its port, then every read on the drive failed. systemd gave up restarting the OSD after four tries. This was the first time I saw the state in full. The kernel had marked the SCSI device `offline`, and the device node returned "No such device or address". Software recovery worked, and I did it step by step and only after I was told to:

1. Delete the dead SCSI device and toggle USB authorization on that one port. The drive re-enumerated in five seconds under a new name, `sdh`, same serial.
2. Reactivate the LVM volume group, then `ceph-volume lvm activate --no-systemd` for the OSD.
3. `ceph-bluestore-tool fsck`, which printed "fsck success".
4. Start the OSD. It was up at 20:17, three and a half hours after it dropped.

While it was down, 3.9% of objects (645,762 of 16.5 million) were degraded across 158 undersized placement groups. None were inactive, `noout` kept Ceph from starting a rebalance, and playback never noticed. Once the OSD was back, degraded objects fell to 0.05% in about a minute and the cluster was clean a minute or two after that. Rebooting jaeger was the other option, and it had cleared a similar hang two days earlier. I took the targeted fix first, because a reboot takes all four of jaeger's OSDs down and the fix needed only one.

## What it cost, in numbers

| Directory | Size | Time | Method |
|---|---:|---:|---|
| 13 small directories | 65 GB | about 3 hours of copying | swap, 20 then 8 MB/s |
| `pixar` | 99.7 GB | about 7.5 hours of running time over several restarts | in place, 8 MB/s each way |
| `disney-tvshows` | 59.3 GB | 4.6 hours | in place, 8 MB/s each way |

The one number I got wrong in the plan was time. I estimated from the write cap alone: 59 GB at 8 MB/s is 2.1 hours. It took 4.6, because I also read every byte back at the same cap to verify it. The read-back is the part that makes me comfortable, and it doubles the time. At these settings the 4.8 TB movie library is about two weeks and the 14.3 TB TV library about six weeks. Raising the cap is the lever, and I am not going to raise it until tanaka's drives are checked.

Models and `disney-movies` are running as I write this, 390 GB in total, with Jellyfin healthy throughout.

## What I'd do differently, and what's next

- **Test the failure before the scale.** I knew the USB drives were fragile and I still discovered how they fail in the middle of a migration. A scheduled drill, killing a USB port on a weekday afternoon and recovering it, would have given me the recovery steps before I needed them at 4 PM on a Thursday.
- **Let the data layout, not the tool, drive the method.** I picked rsync-and-rename because it is familiar. The directory layout feature was in the runbook all along and fit the problem better.
- **Make the safety net first, then the work.** The watchdog was an afterthought and I retrofitted it twice. Next time it goes in before the first byte moves.
- **Deep scrub stays off for now.** I turned it off weeks ago for recovery and it is still off, with 587 placement groups overdue. That is a debt, not a decision. I will turn it back on when tanaka's hardware is sorted, in stages.

Saturday I will be in front of the machines. I plan to look at tanaka's USB card and ports and at jaeger's drive enclosures, and after that decide the rate for the movie and TV libraries. The software side of this migration behaved. The weak link is a USB3 bridge on a 2011 desktop, and no amount of careful scripting changes that. The scripting only decides how gracefully the cluster fails.
