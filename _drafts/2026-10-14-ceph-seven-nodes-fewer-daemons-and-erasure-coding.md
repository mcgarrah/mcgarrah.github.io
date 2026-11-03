---
layout: post
title: "Seven Ceph Nodes, Fewer Daemons: Why an Even Monitor Count Buys Nothing and Where Erasure Coding Fits"
categories: [homelab, ceph, proxmox]
tags: [ceph, proxmox, cephfs, monitors, mds, mgr, erasure-coding, quorum, capacity-planning, high-availability, dell-optiplex-990]
excerpt: "My Ceph cluster ran a monitor, a manager and a metadata server on every node but one. Six monitors tolerate exactly the same two failures as five, so I trimmed the cluster to 5 monitors, 3 managers and 3 metadata servers, measured a 5-second CephFS failover, and cleared the way for erasure coding that will cut the raw cost of 18 TiB of media from 55 TiB to 27."
description: "Why a six-monitor Ceph quorum is no more fault tolerant than five, how to trim monitors, managers and metadata servers safely with pveceph, what to fix in the consumers that hard-code daemon addresses, and how a seventh OSD host makes a k=4,m=2 erasure-coded CephFS data pool practical. Measured numbers from a seven-node Proxmox cluster."
date: 2026-10-14
last_modified_at: 2026-10-14
seo:
  type: BlogPosting
  date_published: 2026-10-14
  date_modified: 2026-10-14
---

Most Ceph clusters I see in small deployments share one trait: every node runs every service. Proxmox makes it a few clicks per node, the first three nodes get a monitor, a manager and a metadata server, and nobody revisits the decision as the cluster grows. Mine did exactly that. When the cluster reached seven nodes, with a move to erasure coding on the roadmap, I stopped to ask whether that layout was a design or a default. It was a default, and it was costing me more than it returned.

This is the reasoning, the measured results of the change, and where the cluster is heading.

<!-- excerpt-end -->

## Where the cluster stands

Seven Dell OptiPlex 990 desktops run Proxmox VE and Ceph Squid. Each carries three 5 TB SMR drives on a USB3 card as OSDs, with a SATA SSD in front of them for the BlueStore DB and WAL, plus a small SSD-backed OSD that holds the CephFS metadata. The cluster grew from six OSD hosts to seven when the newest node, jaeger, joined as an OSD-only host.

| | Today |
|---|---|
| Raw capacity | 98 TiB (97 TiB HDD, 1.9 TiB SSD) |
| Raw used | 56 TiB, 57% |
| CephFS data, logical | 18 TiB |
| CephFS data, raw (3 replicas) | 55 TiB |

That last pair is the whole story of the next section: 18 TiB of media costs 55 TiB of disk.

## Quorum arithmetic: why six monitors is a bad number

A Ceph monitor quorum is a strict majority: floor(n/2) + 1. Write the table down once and the sizing decision makes itself.

| Monitors | Quorum needed | Failures tolerated |
|---|---|---|
| 3 | 2 | 1 |
| 4 | 3 | 1 |
| 5 | 3 | 2 |
| 6 | 4 | 2 |
| 7 | 4 | 3 |

Six monitors tolerate the same two failures as five. The sixth buys no additional fault tolerance and adds cost: one more member in every election and every Paxos round, one more database to keep writing to a boot disk, and a failure mode the odd counts don't have. Split six monitors three and three across a network partition and neither side holds a majority, so the cluster stops. Split five two and three and the three keep going. This is the same reasoning behind sizing etcd and ZooKeeper ensembles with odd numbers, and it is easy to forget when the default is "one per node."

I had also been carrying a documentation error that made six look better than it is. My own cluster summary said six monitors "can lose three and maintain quorum." They can lose two. I corrected it as part of this change.

The target was five. Five tolerates two monitor failures, which matches the two host failures a 4+2 erasure-coded pool can survive without losing data. Seven monitors would tolerate three, but I'd be paying for resilience the storage layer underneath doesn't have.

## Managers and metadata servers: one active, the rest are standby

The monitor count is a correctness question. The manager and metadata server counts are a cost question.

**Managers.** Only one is ever active. It serves the dashboard and the Prometheus module; the standbys sit idle at roughly 0.4 GB of resident memory each. Five standbys are not five times the safety. Three (one active, two spares) tolerate two manager failures, which is plenty for a stateless daemon that restarts in seconds.

**Metadata servers.** With `max_mds 1`, exactly one MDS is active. Mine was holding about 508,000 inodes and 1.9 GB of resident memory, while five cold standbys sat at about 40 MB each. A cold standby has to replay the journal and rebuild its cache before it can serve, and that is the part that matters during a failure. Five of them don't shorten it. One **hot standby** does: with `allow_standby_replay` on, a daemon follows the active MDS's journal continuously and keeps a warm cache, so the takeover is a promotion, not a recovery. One hot standby plus one spare is the right shape.

## Where to put them

Placement matters more than count, and it is the part a default layout ignores.

- **Keep the GPU node free.** One node in the cluster (quell) exists to run GPU workloads: an RTX 3060, local models, image generation. Its CPU and RAM are the point. It was running a monitor, a manager and a metadata server, about 0.9 GB of RAM and a steady CPU draw on a machine that had about 7 GB free. It runs none of them now.
- **Keep the newest and most disposable node out of the control plane.** Jaeger is an OSD-only host, and it is the canary for the next Proxmox major upgrade. A node that is expected to reboot often shouldn't carry a monitor.
- **Think about disks.** Monitor stores are small (22 to 36 MB here) but latency-sensitive. Four of my nodes boot from SSD; three boot from spinning disks. I accepted two HDD-backed monitors (kovacs and poe) rather than leave the cluster with three. It is a trade-off, not a free lunch, and it is on the list to fix when those boot drives are replaced.

The result: monitors on harlan, kovacs, poe, edgar and tanaka; managers on tanaka (active), harlan and edgar; metadata servers on tanaka (active), edgar (hot standby) and harlan (spare).

## Doing it without moving a byte

None of this touches data, but the order still matters because the metadata server is on the live path for every CephFS client, including the shared workspaces and the media server's mounts.

```bash
# 1. Managers: standbys only, never the active one (run on each node)
pveceph mgr destroy

# 2. Metadata servers
ceph fs set cephfs allow_standby_replay true
pveceph mds destroy                 # on the nodes being trimmed (cold standbys first)
ceph mds fail poe                   # move the active rank on purpose
pveceph mds destroy                 # then on the old active's node

# 3. Monitors, last, and never the leader first
pveceph mon destroy                 # on the node being trimmed
ceph quorum_status                  # confirm 5 of 5 before anything else
```

Measured results: failing the active MDS off its node and promoting the standby-replay daemon took **5 seconds**. A write and read test to CephFS succeeded immediately afterward, and all seven clients stayed attached. The monitor quorum moved from six to five within seconds. Cluster health was identical before and after (a pre-existing slow-BlueStore-operations warning), which is the result I wanted: no new alarms.

Two behaviors worth knowing. After `pveceph mgr destroy`, the manager map keeps the dead standbys listed for 30 to 60 seconds until their beacons expire; that is normal, not a failed removal. And a metadata server you have just failed comes back as a standby on its own until you destroy it, so fail first, destroy second.

## The part people forget: things that list every node

Removing daemons is the easy half. The harder half is everything that hard-coded the old set. In my case, two consumers listed all six nodes:

- **The Telegraf Ceph collector** scraped the Prometheus module on every node. Only the active manager answers, so most of those scrapes were wasted. It now lists the three manager nodes, so it follows a failover without a config change.
- **The reverse proxy for the Ceph dashboard** listed all six nodes as upstreams. It now lists the three managers.

I tested both before reloading (Telegraf's `--test` mode produced over ten thousand metric lines with no errors; `caddy validate` passed), kept a dated backup next to each file, and confirmed afterward that the dashboard answered through the proxy and fresh metrics kept arriving. The same hygiene applies to anything with a monitor address pinned: `pveceph` rewrites `mon_host` in the cluster's `ceph.conf`, and after the removal I verified that no stale auth entries or config sections were left behind. That check is not paranoia. After an earlier node rebuild I had hit exactly this: a daemon could not be recreated because a stale section and a stale cephx entry survived the rebuild.

## Why this makes things better

- **More correct.** An odd monitor count removes the dead-zone failure mode (an even split with no majority) and keeps the same two-failure tolerance.
- **Faster failure handling where it counts.** A hot standby MDS turns a metadata failover into a 5-second promotion instead of a journal replay.
- **Cheaper.** About 1.7 GB of RAM across the fleet (one monitor and three managers), and 0.9 GB off the node that most needs its memory for GPU work.
- **Quieter.** Fewer monitors means fewer election participants and fewer writers to boot disks I am already watching for wear.
- **Honest documentation.** The layout now encodes a reason for each daemon's placement instead of a default.

I haven't yet measured an effect on election frequency, and I'm not going to claim one. The monitor-election instability I fixed earlier this month had a different root cause (rocksdb compaction), and I'll compare election counts from this point forward against that baseline.

## What comes next: erasure coding on seven hosts

The layout change is partly preparation. The expensive thing in this cluster is replication: `cephfs_data` is `replicated size=3`, so 18 TiB of media occupies 55 TiB of raw disk. A `k=4, m=2` erasure-coded pool stores the same data at (k+m)/k = 1.5x, about 27 TiB. That is roughly 28 TiB of raw capacity back, from a cluster that is 57% full, with the same durability: both layouts survive the loss of any two failure domains without losing data.

Why this workload suits it: the data is a media library, written once, read many times, in large files. Erasure coding's weak spot is small, partial overwrites, which are a poor match for spinning SMR drives and a non-issue for a movie that is copied in and then only read. Metadata stays on replicated SSD-backed OSDs, and the filesystem's first data pool must stay replicated regardless, because it holds the inode backtraces. That pool stays and shrinks to almost nothing.

Why the seventh host matters. With `crush-failure-domain=host` and exactly six hosts, a 4+2 pool places one chunk on every host. Lose one and every placement group is down to five of six chunks with no spare host to rebuild onto, so there is no self-healing until it returns. With seven hosts, each placement group picks six of seven, and when a host fails its missing chunk can be rebuilt onto the seventh. Availability is honest rather than magical: with the default `min_size` of 5, losing two hosts at once leaves placement groups inactive (four chunks) until recovery, though no data is lost. That is the same outcome replication gives me today with `size=3`, `min_size=2`.

The migration itself is deliberately boring, because the cluster can't afford a clever one. Add the erasure-coded pool as an additional data pool, set the directory layout on a new directory so new writes land in it, copy the existing data across with rsync, verify, then remove the old copy. One top-level directory at a time, smallest first, saving the 13 TB TV library for last, so the old and new copies of only one directory ever coexist. The layout attribute survives the rename, so no per-file work is needed afterward. The staging order and the capacity checks (`nearfull` at 85%, backfills refused at 90%, writes refused at 95%) are in the runbook, and I'm not starting until the rebalance has settled and the new host's drives have taken their share.

## What I'd do differently at scale

On a production cluster I'd put monitors on dedicated, SSD-backed hosts and keep them out of the OSD nodes entirely. The seven-node, converged layout is a deliberate compromise for a lab, and it is exactly why placement and boot-disk media earned a paragraph here. I'd also alert on quorum size (not just quorum health), so a slow drift back to an even count is caught by monitoring and not by a partition.

Three lessons transfer from this exercise. Defaults encode a number, not a reason. Redundancy counts follow arithmetic, so write the table before you pick the count. And removing a service is a change-management exercise as much as a technical one: the daemons are the easy part, and the list of everything that knew their addresses is where a clean change can quietly go wrong.
