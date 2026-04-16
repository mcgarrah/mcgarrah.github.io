---
title: "Measuring the WAL vs DB Performance Gap on Ceph USB OSDs"
layout: post
categories: [proxmox, ceph, homelab, storage]
tags: [proxmox, ceph, ssd, wal, db, bluestore, performance, benchmarking, homelab]
excerpt: "Nine of my fifteen Ceph OSDs use WAL-only acceleration while six use DB. I set out to measure the performance gap and discovered the real story isn't WAL vs DB — it's the USB 3.0 hardware ceiling that dominates everything. The matched-hardware comparison shows DB is 5-15% faster on reads, not the 32% that naive cross-node testing suggested."
published: true
---

My [hybrid Ceph storage article](/ceph-ssd-wal-db-usb-storage/) documented the WAL vs DB inconsistency across the AlteredCarbon cluster — harlan, kovacs, and quell use WAL-only, while edgar and poe use DB. I recommended standardizing on DB but admitted I hadn't measured the actual performance difference.

This article is that measurement. What started as a simple A/B test turned into a deep dive on USB storage performance, Ceph recovery tuning, and the importance of controlling variables in benchmarks. The headline result: **DB is ~5-15% faster than WAL on matched hardware** — real but modest, and dwarfed by the 13× gap between the USB spinning disks and the SATA SSD that both configurations share.

*Note: This testing was conducted while osd.6 was backfilling after a drive replacement. Edgar (DB node) was under elevated load as a backfill source, which affected some measurements. A follow-up retest under clean conditions is planned.*

<!-- excerpt-end -->

## The Question

On identical hardware (Dell OptiPlex 990, i7-2600, Crucial MX500 SSD, 5TB Seagate USB), how much faster is a DB-accelerated OSD compared to a WAL-only OSD for:

1. Random metadata reads (RocksDB lookups)
2. Small write latency (WAL journal commits)
3. Scrub completion time
4. OSD peering time after restart
5. CephFS directory listing performance

## Why This Is Hard to Test

The naive approach — compare `ceph osd perf` latency between WAL and DB OSDs — doesn't work because:

- **Different PGs**: each OSD serves different placement groups with different access patterns
- **Different data volumes**: OSDs aren't equally full
- **Different USB drives**: even same-model Seagates have variance in seek performance
- **Different nodes**: network path, CPU load, and memory pressure vary per host

A valid comparison needs **matched OSDs on the same node** with the same data.

## Test Plan: Future Same-Node Comparison

The cross-node matched comparison above is the best we can do without rebuilding an OSD. If a future drive failure or capacity upgrade requires rebuilding an OSD on harlan, kovacs, or quell, that's the opportunity to do a true same-node WAL vs DB comparison. The test plan and scripts below are preserved for that eventuality.

### Prerequisites

- [ ] Cluster at HEALTH_OK with no degraded PGs
- [ ] Recent full backup via PBS or ZFS snapshots
- [ ] Maintenance window (2-4 hours)
- [ ] `ceph osd set noout` during the test

### Phase 1: Baseline Measurements (Non-Destructive)

Collect current performance data without changing anything:

```bash
# Cluster-wide OSD latency comparison
ceph osd perf

# Per-OSD detailed latency (run on each node)
ceph daemon osd.X perf dump | jq '.osd | {op_latency: .op_latency, op_r_latency: .op_r_latency, op_w_latency: .op_w_latency}'

# Scrub timing — trigger scrub on one WAL and one DB OSD, compare duration
ceph osd scrub osd.0   # WAL (harlan)
ceph osd scrub osd.1   # DB (edgar)
# Monitor with: ceph -w | grep scrub

# CephFS metadata benchmark
# Create a test directory with 10,000 small files, time the listing
time ls -la /mnt/pve/cephfs/test-dir/ | wc -l
# Run from a client that routes through different OSDs
```

### Phase 2: Matched OSD Test (Requires OSD Rebuild)

**Target node: harlan** (has WAL-only OSDs, we recently replaced osd.6)

The idea: rebuild osd.6 as DB instead of WAL, then compare osd.6 (DB) against osd.0 and osd.3 (WAL) on the same node, same SSD, same USB bus.

```bash
# Step 1: Record current osd.6 performance baseline
ceph daemon osd.6 perf dump > /tmp/osd6-wal-baseline.json

# Step 2: Wait for osd.6 to be fully backfilled and stable (check PG distribution)
ceph osd df tree | grep osd.6

# Step 3: Destroy osd.6 (Proxmox UI or CLI)
ceph osd set noout
# Proxmox UI: harlan → Ceph → OSD → osd.6 → Out → Destroy

# Step 4: Recreate osd.6 as DB instead of WAL
lvcreate -L 100G -n osd-db-osd6 ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c
ceph-volume lvm create --osd-id 6 --data /dev/sdd \
  --block.db ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c/osd-db-osd6

# Step 5: Wait for backfill to complete
ceph -w  # watch until osd.6 is fully populated

# Step 6: Record osd.6 DB performance
ceph daemon osd.6 perf dump > /tmp/osd6-db-results.json

# Step 7: Compare
diff <(jq '.osd | {op_latency, op_r_latency, op_w_latency}' /tmp/osd6-wal-baseline.json) \
     <(jq '.osd | {op_latency, op_r_latency, op_w_latency}' /tmp/osd6-db-results.json)
```

**Risk**: osd.6 will be empty after recreation, so Ceph backfills ~2.2 TiB to it (the cluster average per OSD). During backfill, performance numbers aren't representative. Need to wait for HEALTH_OK before measuring.

**Time estimate**: 4-5 days for backfill. The article originally estimated 4-8 hours, but real-world recovery on this hardware averages ~6 MiB/s sustained — see [Hardware Bottlenecks](#hardware-bottlenecks-usb-30-and-1-gbe) below for why. Increasing Ceph recovery tuning parameters (`osd_max_backfills`, `osd_recovery_max_active`, `osd_recovery_op_priority`) and pausing scrubs did not improve the rate — the bottleneck is the shared USB controller on harlan, not Ceph scheduling.

### Phase 3: Targeted Benchmarks

After osd.6 is rebuilt as DB and fully backfilled:

```bash
# Compare apply latency: osd.0 (WAL) vs osd.6 (DB) on same node
for osd in 0 3 6; do
  echo "=== osd.$osd ==="
  ceph daemon osd.$osd perf dump | jq '{
    apply_latency: .osd.op_latency.avgcount,
    read_latency: .osd.op_r_latency.sum,
    write_latency: .osd.op_w_latency.sum,
    subop_latency: .osd.subop_latency.sum
  }'
done

# Scrub comparison on same node
ceph osd scrub osd.0  # WAL
ceph osd scrub osd.6  # DB
# Time both, compare duration

# OSD restart peering time
systemctl restart ceph-osd@0  # WAL
# Time until osd.0 shows "up" in ceph osd tree
systemctl restart ceph-osd@6  # DB
# Time until osd.6 shows "up" in ceph osd tree
```

### Phase 4: Decide Whether to Convert Remaining WAL OSDs

If DB shows meaningful improvement, convert osd.0 and osd.3 on harlan to DB as well. Then repeat on kovacs and quell during future maintenance windows.

Each conversion requires:

1. Destroy the OSD
2. Remove the WAL LV
3. Create a DB LV (same 100GB size)
4. Recreate the OSD with `--block.db`
5. Wait for backfill (~4-5 days per OSD on USB 3.0)

**Total conversion time for 9 WAL OSDs**: 9 × 4-5 days ≈ 36-45 days of backfill, spread across multiple maintenance windows. Only one OSD can backfill per node at a time without saturating the USB bus.

## Hardware Bottlenecks: USB 3.0 and 1 GbE

Before looking at the results, it's worth understanding the two hardware constraints that dominate performance in this cluster — and that made the original "4-8 hour backfill" estimate wildly optimistic.

**USB 3.0 throughput ceiling.** The Seagate 5TB USB drives connect via USB 3.0 (5 Gbps theoretical, ~400 MB/s practical for sequential). But these are spinning 2.5" drives doing random I/O during backfill and normal operations. Real-world sustained write throughput during Ceph recovery is **~13 MiB/s per OSD** — roughly 3% of the USB bus theoretical maximum. The bottleneck isn't USB itself; it's the spinning disk behind the USB-SATA bridge.

We can prove this. On harlan, the Crucial MX500 SSD connects via direct SATA to the motherboard, while the three Seagate ST5000LM000 drives connect via USB 3.0. Benchmarking both paths on the same node:

```
=== Sequential read (hdparm -t) ===
SSD  /dev/sdc (SATA):  241.9 MB/s
HDD  /dev/sdd (USB):   125.9 MB/s
HDD  /dev/sde (USB):   103.2 MB/s
HDD  /dev/sdf (USB):   127.1 MB/s

=== Direct 4K sequential read (dd iflag=direct, 10000 blocks) ===
SSD  /dev/sdc (SATA):   88.4 MB/s
HDD  /dev/sdd (USB):    20.4 MB/s
HDD  /dev/sde (USB):    17.2 MB/s

=== Random 4K read IOPS (dd with random offsets, iflag=direct) ===
SSD  /dev/sdc (SATA):   979 IOPS
HDD  /dev/sdd (USB):     77 IOPS
HDD  /dev/sde (USB):     76 IOPS
HDD  /dev/sdf (USB):     71 IOPS
```

The sequential read gap is only 2×, but the random 4K IOPS gap is **13×**. Ceph backfill and normal OSD operations are dominated by random I/O — metadata lookups, PG peering, object reads scattered across the disk. At 75 IOPS × 4 KB = ~300 KB/s of random read throughput, it's clear why recovery crawls at 13 MiB/s: the OSD is mixing random metadata reads with sequential data writes, and the spinning platters can't seek fast enough.

The USB-SATA bridge adds some overhead (command queuing is limited compared to native SATA), but the fundamental constraint is the ~8ms average seek time of a 5400 RPM 2.5" drive. That's physics, not protocol.

To confirm this, the cluster also has two larger USB drives used for ZFS replication — a 20 TB 7200 RPM 3.5" (quell) and a 28 TB 7200 RPM 3.5" (edgar). Same USB 3.0 bus, different drive mechanics:

```
=== Random 4K read IOPS (same USB 3.0 bus) ===
SSD  CT500MX500SSD1 (SATA direct):     979 IOPS
HDD  ST28000DM000   (USB, 7200 RPM):   138 IOPS
HDD  OOS20000G      (USB, 7200 RPM):   120 IOPS
HDD  ST5000LM000    (USB, 5400 RPM):    77 IOPS avg

=== Sequential read ===
SSD  CT500MX500SSD1 (SATA direct):   241.9 MB/s
HDD  ST28000DM000   (USB, 7200 RPM): 187.0 MB/s
HDD  OOS20000G      (USB, 7200 RPM): 174.1 MB/s
HDD  ST5000LM000    (USB, 5400 RPM): 123.0 MB/s avg
```

The 7200 RPM 3.5" drives get **70% more random IOPS** than the 5400 RPM 2.5" Ceph drives on the same USB bus — that's the seek time difference (~5.5ms vs ~8ms), not USB overhead. But even the fastest spinning drive is still **7× slower than the SSD**. DB acceleration matters regardless of which HDD is underneath; it just matters *more* when the HDD is slower.

There's one more factor: all cluster nodes have [UAS disabled via GRUB boot parameters](/usb-drive-smart/) to enable SMART health monitoring on the Seagate USB drives. Disabling UAS drops USB throughput by 10-30% compared to native UAS mode. The benchmark numbers in this article — 13 MiB/s recovery, 75 random IOPS — reflect this trade-off. It's the right call (catching a failing drive before data loss beats a 20% throughput gain), but it means these numbers are a floor, not a ceiling.

**Dual 1 GbE networks.** Each node has two physical NICs on separate switches and bridges:

- **vmbr0 (LAN)** — 192.168.86.0/23 via enp0s25 — management, client access, Ceph public (monitors, client-to-OSD reads/writes)
- **vmbr1 (SAN)** — 10.10.10.0/23 via enp6s4 — dedicated Ceph cluster network (OSD-to-OSD replication, heartbeats, recovery, backfill)

This is Ceph's recommended dual-network architecture: client I/O and replication traffic don't compete for the same link. Backfill traffic (the 13 MiB/s recovery we're waiting on) flows over the SAN, leaving the LAN free for client operations.

Both links are 1 GbE today. The SAN currently runs through an unmanaged Netgear 8-port switch (which replaced an earlier 5-port model that hung every 4-6 months). An HP ProCurve 2810 is on hand for a planned upgrade that will also enable LACP bonding (2× 1 GbE = 2 Gbps aggregate) on the SAN. Even without bonding, the 1 GbE SAN link (~120 MB/s) is not the backfill bottleneck — the USB HDDs at 13 MiB/s are well below the network ceiling. The SAN upgrade will matter more for client I/O under load, where multiple OSDs serving concurrent reads can saturate a single 1 GbE link.

**What this means for backfill timing:**

| Scenario | Optimistic estimate | Actual measured |
|----------|-------------------:|----------------:|
| Single OSD backfill (~2.2 TiB) | 4-8 hours | **4-5 days** |
| Full 9-OSD WAL→DB conversion | 36-72 hours | **36-45 days** |
| Recovery rate (instantaneous) | 50-100 MiB/s | **11-14 MiB/s** |
| Recovery rate (sustained avg) | 50-100 MiB/s | **~6 MiB/s** |
| Random 4K IOPS (SSD vs HDD) | — | **979 vs 75 (13×)** |

The optimistic estimates assumed SSD-like or direct-attached SATA throughput. USB 3.0 with spinning disks is a different world. Plan maintenance windows accordingly — each OSD conversion is a multi-day commitment, not a quick afternoon task.

The gap between instantaneous (11-14 MiB/s) and sustained (6 MiB/s) recovery rates deserves explanation. `ceph status` reports the rate when Ceph is actively moving data, but backfill isn't continuous — it pauses between PGs, yields to client I/O, and on harlan specifically, three USB drives share one USB host controller. During backfill, the source OSDs (osd.0 and osd.3) read from their drives while osd.6 writes to its drive, all competing for the same USB bus. Tuning Ceph's recovery parameters (`osd_max_backfills=3`, `osd_recovery_max_active=5`, `osd_recovery_op_priority=30`) and pausing scrubs (`noscrub`, `nodeep-scrub`) did not improve the sustained rate — the USB controller is the wall, not Ceph scheduling.

A/B testing three concurrency levels (default, moderate, aggressive) confirmed this — all produced the same ~6-7 MiB/s sustained average within noise. Higher concurrency doesn't hurt on this hardware, but it doesn't help either. The concurrency settings were reverted to defaults; only the scrub pause and elevated recovery priority were kept to reduce unnecessary cluster-wide disk pressure.

This also affects the benchmark results themselves. The WAL vs DB performance gap we're measuring sits on top of these hardware constraints. A 32% read latency improvement sounds significant, but both WAL and DB latencies are already inflated by the 75 IOPS ceiling of the USB HDDs. On a cluster with direct-attached SSDs or NVMe, the absolute numbers would be much smaller and the relative gap might differ. The DB advantage is real, but it's amplified by the slow underlying storage — DB moves more metadata operations off the slow disk and onto the fast SSD, and that matters more when the slow disk is *really* slow.

## Phase 1 Results: Cross-Node Baseline

Collected 2026-04-14 from Thomas (dev workstation) via SSH to all cluster nodes. Cluster was at HEALTH_WARN — osd.6 was still backfilling after a recent replacement (729 GiB / 36 PGs vs ~2 TiB / ~120 PGs for peers). osd.6 is excluded from all averages.

### OSD Configuration Map

| OSD | Node | Acceleration | Data Used | PGs |
|-----|------|-------------|-----------|-----|
| osd.0 | harlan | WAL-only | 2.1 TiB | 115 |
| osd.3 | harlan | WAL-only | 2.3 TiB | 136 |
| osd.6 | harlan | WAL-only | 729 GiB | 36 |
| osd.2 | kovacs | WAL-only | 2.4 TiB | 133 |
| osd.5 | kovacs | WAL-only | 2.2 TiB | 122 |
| osd.8 | kovacs | WAL-only | 2.1 TiB | 118 |
| osd.9 | quell | WAL-only | 2.3 TiB | 134 |
| osd.10 | quell | WAL-only | 2.0 TiB | 115 |
| osd.11 | quell | WAL-only | 2.2 TiB | 128 |
| osd.1 | edgar | DB | 2.3 TiB | 130 |
| osd.4 | edgar | DB | 2.4 TiB | 128 |
| osd.7 | edgar | DB | 2.3 TiB | 122 |
| osd.12 | poe | DB | 1.7 TiB | 88 |
| osd.13 | poe | DB | 1.8 TiB | 96 |
| osd.14 | poe | DB | 1.6 TiB | 87 |

### Daemon Latency Averages (perf dump since last OSD restart)

#### WAL-only OSDs

| OSD | Node | op_latency | op_r_latency | op_w_latency | subop_latency | op_count |
|-----|------|----------:|-------------:|-------------:|--------------:|---------:|
| osd.0 | harlan | 63.4ms | 3.7ms | 481.7ms | 337.5ms | 56,315 |
| osd.3 | harlan | 776.9ms | 40.4ms | 832.0ms | 85.2ms | 1,078 |
| osd.2 | kovacs | 321.5ms | 26.3ms | 344.9ms | 111.0ms | 120,847 |
| osd.5 | kovacs | 33.8ms | 0.5ms | 527.0ms | 250.6ms | 534,711 |
| osd.8 | kovacs | 194.8ms | 29.0ms | 200.6ms | 92.0ms | 190,489 |
| osd.9 | quell | 377.6ms | 31.1ms | 388.4ms | 167.8ms | 418,237 |
| osd.10 | quell | 612.8ms | 18.8ms | 715.4ms | 157.5ms | 77,762 |
| osd.11 | quell | 267.1ms | 7.0ms | 350.0ms | 73.2ms | 114,500 |

#### DB OSDs

| OSD | Node | op_latency | op_r_latency | op_w_latency | subop_latency | op_count |
|-----|------|----------:|-------------:|-------------:|--------------:|---------:|
| osd.1 | edgar | 440.3ms | 16.7ms | 539.8ms | 138.2ms | 59,725 |
| osd.4 | edgar | 502.3ms | 17.8ms | 507.1ms | 157.5ms | 1,246,200 |
| osd.7 | edgar | 250.3ms | 16.5ms | 253.1ms | 169.8ms | 655,294 |
| osd.12 | poe | 403.8ms | 22.0ms | 440.6ms | 216.6ms | 63,940 |
| osd.13 | poe | 41.3ms | 0.3ms | 233.2ms | 167.2ms | 1,127,684 |
| osd.14 | poe | 343.1ms | 6.6ms | 492.7ms | 27.0ms | 44,904 |

#### Cross-Node Averages (osd.6 excluded — backfilling)

| Metric | WAL avg (8 OSDs) | DB avg (6 OSDs) | DB advantage |
|--------|------------------:|----------------:|-------------:|
| op_r_latency | 19.6ms | 13.3ms | **32% faster** |
| op_w_latency | 480.0ms | 411.1ms | 14% faster |
| subop_latency | 159.2ms | 146.1ms | 9% faster |

### OSD Bench: Large I/O (1 GB, 4 MB blocks)

| OSD | Type | Node | Time | MB/s | IOPS |
|-----|------|------|-----:|-----:|-----:|
| osd.0 | WAL | harlan | 28.9s | 35.4 | 8.84 |
| osd.1 | DB | edgar | 35.0s | 29.3 | 7.32 |
| osd.5 | WAL | kovacs | 37.2s | 27.5 | 6.88 |
| osd.12 | DB | poe | 36.5s | 28.1 | 7.01 |

No meaningful WAL vs DB difference on large I/O — expected, since large writes bypass the metadata path.

### OSD Bench: Small I/O (12 MB, 4 KB blocks)

Ceph Reef limits `ceph tell osd.X bench` to 12,288,000 bytes at 4 KB block size by default (the `osd_bench_small_size_max_iops` safety cap assumes 100 IOPS over 30 seconds). This is enough to show the trend.

| OSD | Type | Node | Time | MB/s | IOPS |
|-----|------|------|-----:|-----:|-----:|
| osd.0 | WAL | harlan | 1.17s | 10.0 | 2,556 |
| osd.3 | WAL | harlan | 1.59s | 7.4 | 1,886 |
| osd.1 | DB | edgar | 0.78s | 15.0 | **3,834** |
| osd.4 | DB | edgar | 1.10s | 10.6 | 2,720 |
| osd.5 | WAL | kovacs | 1.31s | 8.9 | 2,287 |
| osd.12 | DB | poe | 1.67s | 7.0 | 1,801 |

| Group | Avg IOPS | Notes |
|-------|--------:|---------|
| WAL (3 OSDs) | 2,243 | harlan × 2, kovacs × 1 |
| DB (3 OSDs) | 2,785 | edgar × 2, poe × 1 |
| **DB advantage** | **~24%** | |

The cleanest comparison — harlan (WAL) vs edgar (DB), same-generation Dell OptiPlex 990 hardware — shows an even larger gap: 2,221 vs 3,277 avg IOPS, a **48% advantage for DB**.

osd.12 on poe underperformed relative to other DB OSDs, possibly due to a different SSD model or higher background load. This is exactly why Phase 2's same-node comparison matters.

### Phase 1 Observations

1. **Read latency confirms theory**: DB OSDs average 13.3ms vs 19.6ms for WAL on reads. DB stores RocksDB metadata on SSD, reducing HDD seeks for lookups.
2. **Write latency difference is smaller**: 411ms vs 480ms. Both configurations journal writes to SSD via WAL, so the write path is similar. The DB advantage likely comes from faster metadata updates during write completion.
3. **Small I/O is where DB shines**: 24% higher IOPS on 4 KB writes across all nodes, 48% on matched hardware generations.
4. **Large I/O shows no difference**: WAL osd.0 was actually faster than DB osd.1 on 4 MB blocks. The difference is entirely in the metadata path.
5. **Variance is high**: op_count ranges from 1,078 to 1.2M across OSDs. Perf dump counters reset on OSD restart, so harlan (1 day uptime) has far fewer ops than kovacs (29 days). This makes cross-node averages noisy.
6. **osd.6 is unreliable**: Still backfilling at 15.6% capacity. Excluded from all comparisons.

### Phase 1 Limitations

These results compare OSDs on **different nodes**. Even though the hardware is the same generation, there are confounding variables: different USB drives, different network paths, different CPU/memory pressure, different PG distributions. The numbers are directionally useful but not definitive.

Phase 2 eliminates these variables by comparing WAL and DB OSDs on the **same node, same SSD, same USB bus**.

## Matched Cross-Node Comparison: quell (WAL) vs edgar (DB)

Rather than wait 4-5 days for an OSD rebuild, we can get a much better comparison than Phase 1 by carefully matching hardware. An inventory of all USB drives and controllers across the cluster revealed that **quell** (WAL) and **edgar** (DB) are the cleanest match:

- Same drive model: Seagate ST5000LM000-**2U8170** (5400 RPM, 2.5")
- Same USB 3.0 controller: Renesas uPD720201 (rev 03)
- Same CPU: Intel i7-2600 @ 3.40GHz
- Same chassis: Dell OptiPlex 990 Tower
- Similar fill levels: 43-51% on both nodes

| OSD | Node | Accel | Drive Model | RPM | Power-On Hours | Fill |
|-----|------|-------|-------------|-----|---------------:|------|
| osd.9 | quell | WAL | ST5000LM000-2U8170 | 5400 | 16,019h | 2.3 TiB (51%) |
| osd.10 | quell | WAL | ST5000LM000-2U8170 | 5400 | 16,022h | 2.0 TiB (43%) |
| osd.11 | quell | WAL | ST5000LM000-2U8170 | 5400 | 16,022h | 2.2 TiB (49%) |
| osd.1 | edgar | DB | ST5000LM000-2U8170 | 5400 | 2,138h | 2.3 TiB (49%) |
| osd.4 | edgar | DB | ST5000LM000-2U8170 | 5400 | 2,137h | 2.4 TiB (51%) |
| osd.7 | edgar | DB | ST5000LM000-2U8170 | 5400 | 2,137h | 2.3 TiB (49%) |

Same drive model, same RPM, same USB controller, same CPU. The quell drives are older (16K hours vs 2K hours) but all healthy with zero reallocated sectors. Fill levels are well matched across all six OSDs.

The earlier Phase 1 comparison used harlan (WAL) vs edgar (DB), but harlan has the older ST5000LM000-**2AN170** variant which runs at 5526 RPM vs 5400 RPM — a confounding variable that inflated the apparent DB advantage.

### Matched OSD Bench: Large I/O (1 GB, 4 MB blocks)

| OSD | Type | Node | Time | MB/s | IOPS |
|-----|------|------|-----:|-----:|-----:|
| osd.9 | WAL | quell | 31.0s | 33.1 | 8.27 |
| osd.11 | WAL | quell | 33.7s | 30.4 | 7.60 |
| osd.4 | DB | edgar | 39.0s | 26.2 | 6.56 |
| osd.7 | DB | edgar | 34.2s | 30.0 | 7.50 |

No meaningful difference on large I/O — consistent with Phase 1 and with theory.

### Matched OSD Bench: Small I/O (12 MB, 4 KB blocks)

| OSD | Type | Node | Time | IOPS |
|-----|------|------|-----:|-----:|
| osd.9 | WAL | quell | 0.80s | 3,759 |
| osd.10 | WAL | quell | 0.84s | 3,569 |
| osd.11 | WAL | quell | 0.93s | 3,231 |
| osd.1 | DB | edgar | 0.80s | 3,760 |
| osd.4 | DB | edgar | 2.48s | 1,207 |
| osd.7 | DB | edgar | 1.16s | 2,582 |

osd.4 was a clear outlier (1,207 IOPS) — edgar was under elevated load during this test with mon.edgar out of quorum and all three OSDs serving as backfill sources for osd.6 on harlan. Excluding osd.4, DB averaged 3,171 IOPS vs WAL's 3,520 — within noise.

### Matched Daemon Latency (perf dump averages)

| Metric | WAL avg (quell) | DB avg (edgar) | Difference |
|--------|----------------:|---------------:|------------:|
| op_r_latency | 19.0ms | 16.9ms | DB 11% faster |
| op_w_latency | 485.8ms | 435.9ms | DB 10% faster |
| subop_latency | 133.2ms | 155.7ms | WAL 14% faster |
| op_latency | 420.2ms | 399.8ms | DB 5% faster |

### Revised Assessment

With properly matched hardware, the DB advantage shrinks considerably from the Phase 1 numbers:

| Metric | Phase 1 (mismatched drives) | Matched (same model) |
|--------|----------------------------:|---------------------:|
| Read latency | DB 32% faster | DB **11%** faster |
| Small I/O IOPS | DB 24% faster | **Inconclusive** (noise) |
| Write latency | DB 14% faster | DB **10%** faster |

The Phase 1 "DB is 32% faster on reads" was inflated by comparing different drive variants (2AN170 at 5526 RPM vs 2U8170 at 5400 RPM). The real-world difference on matched hardware is likely **5-15%** — still meaningful over time, but not dramatic enough to justify the 4-5 day backfill cost per OSD conversion as a standalone project. The recommendation changes from "standardize on DB proactively" to **"use DB when rebuilding OSDs for other reasons"** — which was already the approach in the [hybrid storage article](/ceph-ssd-wal-db-usb-storage/).

A cleaner retest after osd.6 backfill completes (removing edgar's elevated load) would give more definitive numbers.

## What to Measure

| Metric | Command | Predicted | Phase 1 | Matched |
|--------|---------|-----------|---------|--------:|
| Read latency | `ceph daemon osd.X perf dump` | DB lower | DB 32% faster | **DB 11% faster** |
| Write latency | `ceph daemon osd.X perf dump` | Similar | DB 14% faster | **DB 10% faster** |
| Small I/O IOPS | `ceph tell osd.X bench 12288000 4096` | DB higher | DB 24% faster | **Inconclusive** |
| Large I/O throughput | `ceph tell osd.X bench` | Similar | No difference | **No difference** |
| Scrub duration | `ceph -w \| grep scrub` | DB shorter | Deferred | Deferred |
| Peering time | Time from restart to "up" | DB shorter | Deferred | Deferred |

The matched comparison tells a very different story than Phase 1. Controlling for drive model, USB controller, and CPU eliminated most of the apparent DB advantage. The remaining 5-15% read/write latency improvement is real but modest — and on this hardware, it's a rounding error compared to the 13× gap between the USB HDDs and the SATA SSD.

## Conclusions

**DB is better than WAL, but not by much on USB storage.** The 5-15% read latency improvement is real — DB keeps RocksDB metadata on the SSD, saving HDD seeks for lookups. But both WAL and DB are bottlenecked by the same 75-IOPS USB spinning disks. The SSD acceleration (whether WAL or DB) is already doing the heavy lifting; the difference between the two modes is incremental.

**Don't rebuild OSDs just to convert WAL to DB.** At 4-5 days per OSD backfill on USB 3.0, proactively converting 9 WAL OSDs would take 36-45 days of maintenance windows for a 5-15% metadata improvement. Instead, **use DB when rebuilding OSDs for other reasons** (drive failures, capacity upgrades) — which was already the recommendation in the [hybrid storage article](/ceph-ssd-wal-db-usb-storage/).

**The real discovery was the hardware analysis.** The USB drive benchmarks (SSD vs 7200 RPM vs 5400 RPM), the backfill tuning A/B test, and the USB controller saturation finding are more valuable than the WAL vs DB comparison itself. They explain *why* this cluster behaves the way it does and set realistic expectations for any future storage changes.

**Follow-up planned.** Once osd.6 finishes backfilling and edgar returns to normal load, a clean retest of the matched quell vs edgar comparison will give more definitive numbers. The scrub timing and peering time comparisons are also deferred until the 577-PG scrub backlog clears.

## Safety Checklist

- [ ] `ceph osd set noout` before any OSD destruction
- [ ] Verify HEALTH_OK before starting
- [ ] Only destroy one OSD at a time
- [ ] Wait for full backfill before measuring
- [ ] `ceph osd unset noout` when done
- [ ] Don't forget to unset noout (learned this the hard way — see [overlapping failures post](/zfs-ceph-overlapping-failures/))
- [ ] Verify SAN network connectivity — `ping 10.10.10.12` from harlan before starting. The current Netgear 8-port switch has been solid (it replaced a 5-port model that hung every 4-6 months), but always confirm the SAN is healthy before a maintenance window.

## Ready-to-Run Benchmark Scripts

These scripts can be run without modifying the cluster. Save them to `/mnt/pve/cephfs/bin/` for cluster-wide access.

### Script 1: OSD Latency Comparison (Safe — Read Only)

```bash
#!/bin/bash
# ceph-wal-db-latency.sh — Compare WAL vs DB OSD latency
# Safe to run anytime, no cluster modifications

echo "=== Ceph WAL vs DB OSD Latency Comparison ==="
echo "Date: $(date)"
echo ""

printf "%-8s %-10s %-6s %12s %12s %12s\n" \
  "OSD" "Host" "Type" "Apply(ms)" "Commit(ms)" "Read(ms)"
printf "%-8s %-10s %-6s %12s %12s %12s\n" \
  "---" "----" "----" "---------" "---------" "--------"

for osd in $(ceph osd ls 2>/dev/null | sort -n); do
  HOST=$(ceph osd metadata $osd 2>/dev/null | grep '"hostname"' | awk -F'"' '{print $4}')
  TYPE="WAL"
  ceph osd metadata $osd 2>/dev/null | grep -q bluefs_db && TYPE="DB"

  # Get latency from ceph osd perf
  PERF=$(ceph osd perf 2>/dev/null | grep "^\s*$osd ")
  APPLY=$(echo "$PERF" | awk '{print $2}')
  COMMIT=$(echo "$PERF" | awk '{print $3}')

  # Get read latency from daemon perf dump (only works on local node)
  RLAT="n/a"
  if ceph daemon osd.$osd perf dump 2>/dev/null | grep -q op_r_latency; then
    RLAT=$(ceph daemon osd.$osd perf dump 2>/dev/null | \
      python3 -c "import sys,json; d=json.load(sys.stdin); \
      avg=d['osd']['op_r_latency']['sum']/max(d['osd']['op_r_latency']['avgcount'],1); \
      print(f'{avg*1000:.3f}')" 2>/dev/null || echo "n/a")
  fi

  printf "%-8s %-10s %-6s %12s %12s %12s\n" \
    "osd.$osd" "$HOST" "$TYPE" "$APPLY" "$COMMIT" "$RLAT"
done

echo ""
echo "Note: Read latency only available for OSDs on the local node."
echo "Run this script on each OSD host for complete read latency data."
```

### Script 2: Scrub Timing Comparison (Safe — Triggers Scrub)

```bash
#!/bin/bash
# ceph-wal-db-scrub-timing.sh — Compare scrub duration between WAL and DB OSDs
# Triggers scrubs but does not modify data. Run during low-usage period.

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <wal-osd-id> <db-osd-id>"
  echo "Example: $0 0 1    (compares osd.0 WAL vs osd.1 DB)"
  exit 1
fi

WAL_OSD=$1
DB_OSD=$2

echo "=== Ceph Scrub Timing: WAL (osd.$WAL_OSD) vs DB (osd.$DB_OSD) ==="
echo "Date: $(date)"
echo ""

# Trigger scrub on WAL OSD
echo "Starting scrub on osd.$WAL_OSD (WAL)..."
WAL_START=$(date +%s)
ceph osd scrub osd.$WAL_OSD

# Trigger scrub on DB OSD
echo "Starting scrub on osd.$DB_OSD (DB)..."
DB_START=$(date +%s)
ceph osd scrub osd.$DB_OSD

echo ""
echo "Monitoring scrub progress (Ctrl+C to stop watching)..."
echo "Both scrubs running in parallel. Watch for completion:"
echo ""

# Poll until both complete
WAL_DONE=0
DB_DONE=0
while [ $WAL_DONE -eq 0 ] || [ $DB_DONE -eq 0 ]; do
  sleep 10

  if [ $WAL_DONE -eq 0 ]; then
    SCRUB_STATE=$(ceph pg ls-by-osd osd.$WAL_OSD 2>/dev/null | grep -c scrubbing)
    if [ "$SCRUB_STATE" -eq 0 ]; then
      WAL_END=$(date +%s)
      WAL_ELAPSED=$((WAL_END - WAL_START))
      WAL_DONE=1
      echo "osd.$WAL_OSD (WAL) scrub complete: ${WAL_ELAPSED}s"
    fi
  fi

  if [ $DB_DONE -eq 0 ]; then
    SCRUB_STATE=$(ceph pg ls-by-osd osd.$DB_OSD 2>/dev/null | grep -c scrubbing)
    if [ "$SCRUB_STATE" -eq 0 ]; then
      DB_END=$(date +%s)
      DB_ELAPSED=$((DB_END - DB_START))
      DB_DONE=1
      echo "osd.$DB_OSD (DB) scrub complete: ${DB_ELAPSED}s"
    fi
  fi
done

echo ""
echo "=== Results ==="
echo "osd.$WAL_OSD (WAL): ${WAL_ELAPSED}s"
echo "osd.$DB_OSD  (DB):  ${DB_ELAPSED}s"
if [ $WAL_ELAPSED -gt 0 ] && [ $DB_ELAPSED -gt 0 ]; then
  DIFF=$((WAL_ELAPSED - DB_ELAPSED))
  PCT=$(python3 -c "print(f'{($DIFF/$WAL_ELAPSED)*100:.1f}')" 2>/dev/null)
  echo "Difference: ${DIFF}s (DB is ${PCT}% faster)"
fi
```

### Script 3: OSD Restart Peering Time (Requires OSD Restart)

```bash
#!/bin/bash
# ceph-wal-db-peering-time.sh — Measure OSD peering time after restart
# WARNING: Restarts an OSD. Run one at a time. Set noout first.

if [ -z "$1" ]; then
  echo "Usage: $0 <osd-id>"
  echo "Example: $0 6"
  echo ""
  echo "WARNING: This restarts the OSD. Set 'ceph osd set noout' first."
  exit 1
fi

OSD_ID=$1
HOST=$(ceph osd metadata $OSD_ID 2>/dev/null | grep '"hostname"' | awk -F'"' '{print $4}')
TYPE="WAL"
ceph osd metadata $OSD_ID 2>/dev/null | grep -q bluefs_db && TYPE="DB"

# Check noout is set
if ! ceph osd dump 2>/dev/null | grep -q noout; then
  echo "ERROR: noout flag is not set. Run 'ceph osd set noout' first."
  exit 1
fi

echo "=== OSD Peering Time: osd.$OSD_ID ($TYPE) on $HOST ==="
echo "Date: $(date)"
echo ""

# Restart the OSD
echo "Stopping osd.$OSD_ID..."
systemctl stop ceph-osd@$OSD_ID
sleep 2

echo "Starting osd.$OSD_ID..."
START=$(date +%s.%N)
systemctl start ceph-osd@$OSD_ID

# Wait for OSD to show as "up"
while true; do
  STATUS=$(ceph osd tree 2>/dev/null | grep "osd\.$OSD_ID " | awk '{print $4}')
  if [ "$STATUS" = "up" ]; then
    END=$(date +%s.%N)
    ELAPSED=$(python3 -c "print(f'{$END - $START:.2f}')")
    echo ""
    echo "osd.$OSD_ID ($TYPE) peering time: ${ELAPSED}s"
    break
  fi
  sleep 1
done
```

### Running the Full Comparison

```bash
# Step 0: Built-in OSD bench (safe, runs directly on OSD daemon)
# Default: 1GB write test with 4MB blocks
ceph tell osd.0 bench    # WAL (harlan)
ceph tell osd.6 bench    # DB (harlan, after conversion)

# Small I/O: 12MB with 4KB blocks (metadata-like small I/O)
# Note: Reef caps at 12,288,000 bytes for 4KB blocks by default
ceph tell osd.0 bench 12288000 4096   # WAL
ceph tell osd.6 bench 12288000 4096   # DB

# Step 1: Safe latency snapshot (run on each OSD host)
ssh root@192.168.86.11 'bash /mnt/pve/cephfs/bin/ceph-wal-db-latency.sh'  # harlan
ssh root@192.168.86.14 'bash /mnt/pve/cephfs/bin/ceph-wal-db-latency.sh'  # edgar

# Step 2: Client-side pool benchmark with rados bench
# 30-second random read (most relevant for metadata comparison)
rados bench -p cephrbd 30 write --no-cleanup
rados bench -p cephrbd 30 rand
rados -p cephrbd cleanup

# Step 3: Scrub timing (pick one WAL and one DB OSD with similar data volume)
# Check data volume first:
ceph osd df | grep -E 'osd\.(0|1) '
# Then run:
bash /mnt/pve/cephfs/bin/ceph-wal-db-scrub-timing.sh 0 1

# Step 4: Peering time (set noout first!)
ceph osd set noout
bash /mnt/pve/cephfs/bin/ceph-wal-db-peering-time.sh 0   # WAL
bash /mnt/pve/cephfs/bin/ceph-wal-db-peering-time.sh 1   # DB
ceph osd unset noout
```

### Built-in Ceph Benchmarking Tools

Ceph has several built-in benchmarking tools that don't require external software:

**`ceph tell osd.X bench`** — Runs a write benchmark directly on the OSD daemon. Bypasses the network entirely, so it isolates storage performance. The most useful tool for comparing WAL vs DB on the same node.

```bash
# Default: 1GB sequential write with 4MB blocks
ceph tell osd.0 bench

# Small I/O: 12MB with 4KB blocks (stresses metadata path)
# Reef default osd_bench_small_size_max_iops limits this to 12,288,000 bytes
ceph tell osd.0 bench 12288000 4096

# To run larger small-I/O tests, temporarily raise the limit:
# ceph tell osd.0 injectargs '--osd_bench_small_size_max_iops=1000'
# ceph tell osd.0 bench 536870912 4096
```

**`rados bench`** — Client-side benchmark through a Ceph pool. Tests the full path including network. Useful for measuring what applications actually experience.

```bash
# Write test (creates objects in the pool)
rados bench -p cephrbd 30 write --no-cleanup

# Sequential read
rados bench -p cephrbd 30 seq

# Random read (most relevant for metadata-heavy workloads)
rados bench -p cephrbd 30 rand

# Cleanup test objects
rados -p cephrbd cleanup
```

**`ceph tell osd.X perf dump`** — Dumps live performance counters without generating any load. Use this for before/after snapshots around other tests.

```bash
# Full perf dump
ceph tell osd.0 perf dump

# Just the interesting bits
ceph tell osd.0 perf dump | python3 -c "
import sys, json
d = json.load(sys.stdin)
osd = d.get('osd', {})
for key in ['op_latency', 'op_r_latency', 'op_w_latency', 'op_rw_latency']:
    v = osd.get(key, {})
    avg = v.get('sum', 0) / max(v.get('avgcount', 1), 1) * 1000
    print(f'{key}: {avg:.3f}ms avg ({v.get("avgcount", 0)} ops)')
"
```

## Monitoring Backfill Progress

Phase 2 requires waiting for a full OSD backfill — roughly 30-40 hours for ~2 TiB over USB 3.0 at ~13 MiB/s. `ceph progress` should show an active recovery event with an ETA, but in practice it sometimes only lists completed events. This one-liner gives you a quick status check from your dev workstation:

```bash
ssh harlan 'DATA=$(ceph osd df 2>/dev/null | grep "^ *6 " | awk "{print \$7,\$8}"); \
  PCT=$(ceph osd df 2>/dev/null | grep "^ *6 " | awk "{print \$17}"); \
  RATE=$(ceph status 2>/dev/null | grep recovery | awk "{print \$2,\$3}"); \
  PGW=$(ceph pg dump 2>/dev/null | grep -c backfill_wait); \
  PGA=$(ceph pg dump 2>/dev/null | grep -c "backfilling[^_]"); \
  echo "osd.6: ${DATA} (${PCT}%) / ~2.2 TiB target | recovery: ${RATE} | PGs: ${PGA} active, ${PGW} waiting"'
```

Example output during the Phase 1 baseline collection, while osd.6 was still backfilling after a drive replacement:

```
osd.6: 739 GiB (15.88%) / ~2.2 TiB target | recovery: 14 MiB/s, | PGs: 4 active, 138 waiting
```

Wrap it in `watch` for auto-refresh:

```bash
watch -n 60 'ssh harlan "DATA=\$(ceph osd df 2>/dev/null | grep \"^ *6 \" | awk \"{print \\\$7,\\\$8}\"); PCT=\$(ceph osd df 2>/dev/null | grep \"^ *6 \" | awk \"{print \\\$17}\"); RATE=\$(ceph status 2>/dev/null | grep recovery | awk \"{print \\\$2,\\\$3}\"); PGW=\$(ceph pg dump 2>/dev/null | grep -c backfill_wait); PGA=\$(ceph pg dump 2>/dev/null | grep -c \"backfilling[^_]\"); echo \"osd.6: \${DATA} (\${PCT}%) / ~2.2 TiB target | recovery: \${RATE} | PGs: \${PGA} active, \${PGW} waiting\""'
```

When PGs waiting hits 0 and the fill percentage reaches ~45% (matching peers osd.0 and osd.3), the backfill is complete and you're ready to start benchmarking.

To generalize this for any OSD, replace `6` with the OSD ID and adjust the target percentage based on `ceph osd df` for the peer OSDs on the same node.

## References

- [Hybrid Ceph Storage: SSD WAL/DB Acceleration](/ceph-ssd-wal-db-usb-storage/) — The architecture article this test supports
- [When ZFS and Ceph Problems Collide](/zfs-ceph-overlapping-failures/) — Where the WAL vs DB inconsistency was discovered
- [Ceph OSD SSD Acceleration Reference](https://github.com/mcgarrah/k8s-proxmox/blob/main/docs/CEPH-OSD-SSD-ACCELERATION.md) — Full OSD-to-device mapping
- [Ceph BlueStore Configuration Reference](https://docs.ceph.com/en/reef/rados/configuration/bluestore-config-ref/)
- [SSH Key-Based Access to a Proxmox Cluster](/ssh-key-access-proxmox-cluster/) — How the remote benchmarking was set up
- [Phase 1 raw data](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/assets/data/ceph-wal-db/phase1-baseline-2026-04-14.md) — Full baseline measurements
- [Matched comparison data](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/assets/data/ceph-wal-db/matched-wal-db-comparison-2026-04-15.md) — quell vs edgar detailed results
- [USB drive benchmarks](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/assets/data/ceph-wal-db/usb-sata-baseline-2026-04-15.md) — SSD vs HDD raw performance data
- [Backfill tuning log](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/assets/data/ceph-wal-db/osd6-backfill-tuning-2026-04-15.md) — Recovery parameter A/B test and revert commands
