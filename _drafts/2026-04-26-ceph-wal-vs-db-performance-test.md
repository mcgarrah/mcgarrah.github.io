---
title: "Measuring the WAL vs DB Performance Gap on Ceph USB OSDs"
layout: post
categories: [proxmox, ceph, homelab, storage]
tags: [proxmox, ceph, ssd, wal, db, bluestore, performance, benchmarking, homelab]
excerpt: "Nine of my fifteen Ceph OSDs use WAL-only acceleration while six use DB. Theory says DB should be faster for metadata operations. Here's the test plan to measure the actual difference on identical hardware without destroying the cluster."
published: false
---

My [hybrid Ceph storage article](/ceph-ssd-wal-db-usb-storage/) documented the WAL vs DB inconsistency across the AlteredCarbon cluster — harlan, kovacs, and quell use WAL-only, while edgar and poe use DB. I recommended standardizing on DB but admitted I hadn't measured the actual performance difference.

This article is that measurement.

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

## Test Plan

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

**Risk**: osd.6 will be empty after recreation, so Ceph backfills ~4.5TB to it. During backfill, performance numbers aren't representative. Need to wait for HEALTH_OK before measuring.

**Time estimate**: 4-8 hours for backfill on USB 3.0, plus measurement time.

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
5. Wait for backfill (~4-8 hours per OSD)

**Total conversion time for 9 WAL OSDs**: 9 × 4-8 hours = 36-72 hours of backfill, spread across multiple maintenance windows.

## What to Measure

| Metric | Command | WAL Expected | DB Expected |
|--------|---------|-------------|-------------|
| Apply latency | `ceph osd perf` | Higher | Lower |
| Read latency | `ceph daemon osd.X perf dump` | Higher (HDD seeks) | Lower (SSD reads) |
| Write latency | `ceph daemon osd.X perf dump` | Similar (both WAL to SSD) | Similar |
| Scrub duration | `ceph -w \| grep scrub` | Longer | Shorter |
| Peering time | Time from restart to "up" | Longer | Shorter |
| CephFS ls time | `time ls -la /mnt/...` | Longer | Shorter |

Write latency should be similar because both configurations journal writes to the SSD. The difference is entirely in read-path metadata operations.

## Safety Checklist

- [ ] `ceph osd set noout` before any OSD destruction
- [ ] Verify HEALTH_OK before starting
- [ ] Only destroy one OSD at a time
- [ ] Wait for full backfill before measuring
- [ ] `ceph osd unset noout` when done
- [ ] Don't forget to unset noout (learned this the hard way — see [overlapping failures post](/zfs-ceph-overlapping-failures/))

## References

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

# Custom: 512MB with 4KB blocks (metadata-like small I/O)
ceph tell osd.0 bench 536870912 4096   # WAL
ceph tell osd.6 bench 536870912 4096   # DB

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

# Small I/O: 512MB with 4KB blocks (stresses metadata path)
ceph tell osd.0 bench 536870912 4096

# Tiny I/O: 256MB with 512-byte blocks (extreme metadata stress)
ceph tell osd.0 bench 268435456 512
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

## References

- [Hybrid Ceph Storage: SSD WAL/DB Acceleration](/ceph-ssd-wal-db-usb-storage/) — The architecture article this test supports
- [When ZFS and Ceph Problems Collide](/zfs-ceph-overlapping-failures/) — Where the WAL vs DB inconsistency was discovered
- [Ceph OSD SSD Acceleration Reference](https://github.com/mcgarrah/k8s-proxmox/blob/main/docs/CEPH-OSD-SSD-ACCELERATION.md) — Full OSD-to-device mapping
- [Ceph BlueStore Configuration Reference](https://docs.ceph.com/en/reef/rados/configuration/bluestore-config-ref/)
