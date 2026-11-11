---
layout: post
title: "Building a Fast SSD Tier in Ceph for LXC Root Disks"
categories: [homelab, ceph, proxmox]
tags: [ceph, proxmox, lxc, rbd, ssd, bluestore, storage-latency, influxdb, grafana, capacity-planning, dell-optiplex-990]
excerpt: "My monitoring database was dropping thousands of metrics at a time, and the CPU and RAM were idle. The root disk sat on a Ceph pool of USB hard drives with 730 ms write latency. I built an SSD tier out of leftover space on each node's DB/WAL drive, found two of the six drives could barely write, and cut that latency to 4.5 ms."
description: "How to build a replicated SSD pool for Proxmox LXC root disks from the free space on Ceph DB/WAL SSDs: sizing, a CRUSH rule that keeps HDD pools off the SSDs, why the default OSD bench missed two bad drives, measured latency before and after, move times per GiB, and which containers a root-disk move does not help."
date: 2026-11-06
last_modified_at: 2026-11-06
seo:
  type: BlogPosting
  date_published: 2026-11-06
  date_modified: 2026-11-06
series: "Seven Ceph Nodes"
series_part: 3
---

My InfluxDB container was healthy by every measure I normally check. Two cores, about 4% of one in use, 859 MB of 6 GB of RAM, no swap. And Telegraf was throwing away 7,500 to 9,500 metrics at a time with "Metric buffer overflow" warnings, while the Proxmox status daemon on harlan and poe logged InfluxDB timeouts all day. My first question was whether the container was undersized. The number that answered it was the root disk's write latency: 730 ms.

That disk was an RBD image on a Ceph pool of 5 TB USB hard drives. InfluxDB syncs every write, so at roughly 29 writes a second it spent most of its time waiting for spinning disks. More CPU would have changed nothing. This post is how I built a small SSD tier in the cluster to fix it, what went wrong on the way, and which containers I decided not to move.

<!-- excerpt-end -->

## The SSD space was already there

Every node in the cluster has a SATA SSD in front of its three HDD OSDs, holding their BlueStore DB and WAL. After I right-sized those DB/WAL volumes in September, each SSD had 315 to 339 GB sitting idle. That is not much, and it is the only fast storage the cluster has. I carved one more OSD out of the free space on each node's SSD, keeping at least 50 GB free per drive, and gave the new OSDs the device class `ssd`.

| Node | New SSD OSD |
|---|---|
| harlan, kovacs | 265 GB each |
| quell, edgar, tanaka | 276 GB each |
| poe | 289 GB |
| jaeger (added later) | 276 GB |

Seven OSDs, about 1.9 TiB raw. At three replicas that is roughly 640 GiB usable. For a tier meant for a couple of dozen small root disks and a metadata pool, that is plenty. For anything bulk it is a rounding error next to the 115 TiB of HDD, which is the point: this tier is deliberately small.

I chose replicated size 3 with min_size 2 and ruled out erasure coding for it. The same cluster is moving its media library to a 4+2 erasure-coded pool (that story is [Part 2](/ceph-seven-nodes-part-2-moving-live-media-to-erasure-coding/) of the Ceph series), and the contrast is the lesson. Erasure coding suits large files written once. This tier exists for small random writes, where every write would touch six hosts and pay encoding and network overhead for nothing. One cluster, two pool types, picked by workload.

## The rule that stops the HDD pools landing on the SSDs

Adding SSD OSDs changes where every other pool can place data, and I almost walked past this. My original CRUSH rule used `step take default` with no device class. Before the SSDs existed that was harmless, because everything under `default` was a hard drive. The moment the SSD OSDs joined the same host buckets, that rule became capable of putting `cephfs_data`, 18 TiB at the time, onto 270 GB drives.

So before creating anything, I moved every existing pool onto a new `replicated_hdd_rule` restricted to the `hdd` class, and created `ssd_rule` for the new tier. It was the right call and it was expensive. Rewriting the rule on all ten pools triggered a rebalance that left 65% of objects misplaced and ran for weeks on drives that were already tight. The SSD tier itself was ready in days; the HDD pools finishing their rebalance gated everything after it. If you add a device class to a cluster that already has data, count that shuffle in the plan.

## Two of my six SSDs could not write

The first benchmark looked fine. `ceph tell osd bench` reported 253 to 264 MB/s on five OSDs, and one outlier, edgar's, at 35 MB/s. I assumed the outlier was contention with its three HDD OSDs mid-backfill, and I was wrong. I re-ran it with no backfill touching those OSDs and got the same 37 MB/s. Then I took Ceph out of the picture and ran `dd` with `oflag=direct` straight to a scratch volume on the same drive: 32 MB/s. A read test on that drive gave 241 MB/s. Healthy reads, crippled sustained writes, and SMART said PASSED with 95% life remaining. The drive had 35,570 power-on hours, about four years of continuous use, which is the real tell. Consumer SSDs can degrade this way in the controller long before SMART's thresholds notice.

The more useful finding came a week later. I noticed that the default bench had briefly reported edgar as healthy again, and realized the short 1 GB write fits inside these drives' write cache. So I re-ran all six with a 4 GB direct write:

| Node | Drive | Sustained 4 GB direct write |
|---|---|---:|
| harlan | Crucial MX500 | 243 MB/s |
| kovacs | Crucial MX500 | 233 MB/s |
| tanaka | ORICO | 218 MB/s |
| poe | Crucial MX300 | 192 MB/s |
| edgar | Samsung | 33.7 MB/s |
| quell | Timetec | 35.4 MB/s |

Two of six, not one. Quell's OSD had never been exercised long enough to expose it. Both drives sat on the same SATA 3.0 Gb/s links as the healthy ones, so this was the drives and not the cabling. A drive like that would have been the worst possible member of this tier, since CRUSH puts roughly a seventh of the data on each OSD regardless of how fast it is, and the metadata pool and every database would have inherited its speed.

I replaced both with ORICO 512 GB drives, which also host the DB/WAL for those nodes' HDD OSDs, so the swap helped more than the new OSD. After the swap the 3 GiB bench read 240 and 247 MB/s on the two rebuilt OSDs. One caveat from quell: the replacement ended up on a port that negotiates 3.0 Gb/s, which caps it near 224 MB/s. The same drive measured 419 MB/s on a 6 Gb/s port. Swapping the two ports needs another power-down of that node, so I left it as low priority.

My rule from this: benchmark a new SSD tier with a direct-I/O write of at least 4 GB per drive. The short default bench measures the drive's cache.

## From metadata to guests

With six healthy SSD OSDs, the first move was the safe one. On October 6 I pointed `cephfs_metadata` at the new rule with `ceph osd pool set cephfs_metadata crush_rule ssd_rule`, then force-backfilled its 32 PGs so they would not queue behind the 165 HDD backfills still running. About 1 GiB moved in 15 minutes, every PG ended `active+clean`, and CephFS never went down.

Three weeks later, on October 30, I created the `cephrbd-ssd` pool (replicated 3/2, 32 PGs, `ssd_rule`), added it as Proxmox storage, and moved the InfluxDB container to it:

```bash
ha-manager set ct:111 --state stopped      # HA guests need the HA stop, not pct stop
pct move-volume 111 rootfs cephrbd-ssd
ha-manager set ct:111 --state started
```

| | Before (HDD pool) | After (SSD pool) |
|---|---|---|
| Write latency | 730 ms | 4.5 ms |
| Container I/O pressure | about 20% | about 1% |
| Telegraf drop and timeout warnings | constant | none after startup |
| `pvestatd` InfluxDB errors on the nodes | constant | none in the first 5 minutes |

The cost was 21 minutes of downtime, which left a gap in every InfluxDB bucket and a blank Grafana. `pct move-volume` for a container is a file-level copy: it reads every file from the slow pool and writes it to the fast one, so the move is limited by the slow side. That night I moved Grafana (8.5 minutes) and UrBackup's root disk (9.5 minutes), and the SSD images for those two measured about 11 ms. Across the three moves the downtime worked out to about 1.4 minutes per GiB of data used, which is the number I now use to plan the others.

I kept each old disk as `unused0` for rollback. They are still there, about 25 GiB of HDD, waiting for a few clean days before `pct set <id> --delete unused0` frees them. I also made one operational mistake on the second pair. My move script redirected its log to a path it could not write, so it would never have run. I killed it, but HA had already restarted the container it stopped, which was a 25-second Grafana blip. Check the log path before you stop a service.

## Was the speedup real?

The 730 ms to 4.5 ms comparison is the number I would not trust on its own. I took the "before" reading while a rebalance was running and the cluster was still working through slow-operation warnings, so some of that latency was the cluster's bad day and not the hard drives' normal behavior. A week later I ran a fairer test: a small script that commits 60 single-row transactions to SQLite with `synchronous=FULL`, run against three places. The cluster was busy at the time, because the erasure-coding migration was running, so these are numbers under load, not best case.

| Where the database lives | Journal mode | Mean | p95 | Worst commit |
|---|---|---:|---:|---:|
| RBD, HDD pool | rollback journal | 140.6 ms | 883.2 ms | 2,221.6 ms |
| RBD, HDD pool | WAL | 30.6 ms | 43.5 ms | 984.8 ms |
| CephFS, HDD data pool | WAL | 35.2 ms | 64.7 ms | 1,147.1 ms |
| RBD, SSD pool | rollback journal | 21.9 ms | 30.7 ms | 37.1 ms |
| RBD, SSD pool | WAL | 12.5 ms | 14.2 ms | 15.8 ms |

The average improves by 2.4x in WAL mode and 6.4x in rollback mode. The tail is the real story: the worst commit goes from about a second to 16 ms. An application that holds a lock while it commits turns that one-second commit into a stall for everything waiting behind it, and that is what Telegraf saw. So the first test showed a real improvement, mostly in the tail, with the caveat in the next paragraph.

I then repeated the test after moving eight more containers, and it did not hold up. On the second run the SSD pool was no faster than the hard drives: WAL commits averaged 56 and 71 ms on two SSD containers against 63 and 44 ms on two HDD containers. The first run's 12.5 ms had been a lucky sample. The cause was one SSD OSD, the one on poe, committing in 21 to 33 ms while the other six committed in 2 to 4 ms. The drive is not failing (SMART is clean, 94% of its life left), and it is not slow at writing. It is slow at flushing its cache: 3.5 ms per flush, against 0.26 to 0.69 ms on the other nodes' drives, and BlueStore needs a flush for every commit. That drive is also the oldest SSD in the fleet, at 26,600 hours, and it carries the DB/WAL for four HDD OSDs where the other nodes carry three, so those four hard-drive OSDs commit four to seven times slower than their counterparts elsewhere. The SSD OSD sits in 17 of the pool's 32 placement groups, and a write has to be acknowledged by all three replicas, so more than half of the images inherit its latency. The lesson is the one from the benchmark section again, one level up: a replicated tier is only as fast as its slowest member, so check per-OSD commit latency (`ceph osd perf`) and per-drive flush time (`iostat -x`, the `f_await` column) before you decide the tier is fast, and never judge it from one container.

I got the test wrong twice before it measured anything. From the host, a container's root disk is not under `/var/lib/lxc/<id>/rootfs`; that path is the node's own disk, so my first "RBD" numbers were from a local drive. And `/tmp` inside the containers is memory, which gave me 0.1 ms commits. The script has to run inside the container, writing to `/var/tmp`.

## What a root-disk move cannot fix

This is the part I got wrong first. After the Telegraf result I started listing containers to move, and Jellyfin was at the top of my list, because its database is the slowest thing users touch. I checked before moving it. `jellyfin.db` is 622 MB and lives, with its write-ahead log, on a CephFS bind mount, not on the root disk. `pct move-volume` moves only the root disk. Moving Jellyfin's container would have copied the operating system to SSD and left the database exactly where it was.

I reviewed all 24 containers for where the hot data actually lives.

| Where the hot data is | Containers | Does a root-disk move help? |
|---|---|---|
| On the root disk | Radarr, Sonarr, Bazarr, Prowlarr, Tunarr, ErsatzTV, Dispatcharr | Yes, though several already show 7 to 26 ms |
| On CephFS bind mounts | Jellyfin, qBittorrent, SABnzbd, the GPU container | No |
| Home directory on root, project on CephFS | agent-dev, pillbox-dev, nutrition-api-dev | Only the home directory |
| Node-local ZFS | UrBackup and PBS data | Only the root disk |

The honest consequence is that the SSD tier fixes a specific class of container, the ones with a database on the root disk and sync-heavy writes. For Jellyfin the right tool is a CephFS data pool on the SSD class with a directory layout pointing the database at it. That is a different change with a measurement step first, and it is still on the list, not done.

## What I'd watch

- **Wear.** Seven drives hold three replicas of everything here, and databases write constantly. The MX500s report 9% (harlan) and 18% (kovacs) of life used. The ORICO drives report no wear at all, and they are the newest, with 475 to 755 power-on hours. I have a baseline task and no limit set yet.
- **Shared drives.** Each SSD OSD lives on the same device as the DB/WAL volumes for three or four HDD OSDs. Heavy writes to the SSD tier compete with the commit path for the hard drives behind them.
- **Failure arithmetic.** Losing one SSD means re-replicating its share onto the other six. That works while the class stays under about half full, and it is under 4% now.
- **Backups first.** An SSD failure takes real data with it, so anything on this tier should already be covered by backups before the move, not after.

The next candidates are the containers with a SQLite database on a small root disk: Bazarr, Sonarr, Radarr and JellyGlance. At 1.4 minutes per GiB used, each is a few minutes, and I will do them one at a time and keep the old disk each time. The agent-dev container is the awkward one: moving its 32 GiB root disk would take about 45 minutes and end every session running inside it, so that one waits until I pick a quiet day to lose my own workspace.
