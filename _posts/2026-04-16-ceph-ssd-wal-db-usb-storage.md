---
title: "Hybrid Ceph Storage: SSD WAL/DB Acceleration with USB Drive Data"
layout: post
categories: [proxmox, ceph, homelab, storage]
tags: [proxmox, ceph, ssd, usb, storage, performance, homelab, wal, db, bluestore, dell-optiplex-990, seagate]
excerpt: "Running Ceph on USB drives sounds crazy until you put the WAL and DB on an SSD. Here's how separating metadata onto a Crucial MX500 transformed my 15-OSD homelab cluster from sluggish to surprisingly capable — at a fraction of all-SSD costs."
description: "Architecture and implementation guide for hybrid Ceph BlueStore storage with SSD WAL/DB acceleration and USB HDD data drives. Covers WAL vs DB differences, sizing, ceph-volume creation, Proxmox UI setup, performance results, cost analysis, and operational lessons from a 15-OSD Proxmox homelab cluster."
date: 2026-04-16
last_modified_at: 2026-04-16
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-16
  date_modified: 2026-04-16
---

Running Ceph in a homelab means making tradeoffs — the same cost-performance-resilience triangle that drives every storage architecture decision. You want distributed storage — high availability, scalability, data protection — but enterprise hardware costs spiral fast. My answer: put the brains on SSD and the bulk on cheap USB drives.

After building a [15-OSD Ceph cluster](/proxmox-ceph-homelab-settings/) with 69 TiB of raw storage across five Dell OptiPlex 990 nodes, I've learned that separating the WAL (Write-Ahead Log) and DB (RocksDB metadata) onto fast SSDs while keeping bulk data on 5TB USB drives delivers excellent performance at a fraction of all-SSD costs.

If you read my recent post about [discovering WAL vs DB inconsistencies](/zfs-ceph-overlapping-failures/) across the cluster, this is the deeper explanation of what those terms mean, why the separation matters, and how to set it up.

<!-- excerpt-end -->

## The Theory: Why Separate WAL and DB?

Ceph's BlueStore backend has three types of data with very different I/O patterns:

- **Data** — the actual objects you store. Large sequential writes and reads. Tolerates slow storage.
- **WAL (Write-Ahead Log)** — a journal of pending writes. Small, constant, latency-sensitive. Every write hits the WAL first.
- **DB (RocksDB metadata)** — the index that maps object names to locations. Small random reads on every operation. Heavily accessed during scrubs, recovery, and listing operations.

By default, all three live on the same device. On a USB HDD, that means every metadata lookup and every write journal entry competes with bulk data I/O on a drive that's already slow (USB 3.0 caps at ~125 MB/s, and HDDs add seek latency on top).

Separating WAL and DB onto an SSD means:

- **Writes complete faster** — the WAL acknowledges writes at SSD speed, then data flushes to the HDD in the background
- **Metadata lookups are instant** — directory listings, object lookups, and scrub operations hit the SSD instead of waiting for HDD seeks
- **Recovery is faster** — when an OSD comes back after a failure, the metadata operations that drive peering and backfill run at SSD speed

## WAL vs DB: Which Should You Use?

This is the question I didn't ask carefully enough when building the cluster, which led to the [inconsistency I discovered](/zfs-ceph-overlapping-failures/) across nodes.

### WAL Only (`--block.wal`)

- SSD stores **only the Write-Ahead Log**
- RocksDB metadata lives on the HDD with the data
- Accelerates writes but metadata reads still hit the HDD
- Created via CLI: `ceph-volume lvm create --block.wal /dev/ssd-partition`

### DB (`--block.db`)

- SSD stores **both the RocksDB metadata and the WAL**
- Accelerates writes (WAL) **and** metadata lookups (DB)
- Strictly better than WAL-only if you have the SSD space
- Created via Proxmox UI (default) or CLI: `ceph-volume lvm create --block.db /dev/ssd-partition`

### The Recommendation

**Use DB.** It's what the Proxmox Web UI creates by default, it provides more acceleration for the same SSD space, and there's no downside. The only reason to use WAL-only is if you're extremely constrained on SSD capacity and want to dedicate every byte to write journaling.

In my cluster, the nodes created via the Proxmox UI (edgar, poe) got DB, while the nodes created via CLI (harlan, kovacs, quell) got WAL-only. Both work fine, but future rebuilds will standardize on DB.

### What Are WAL-Only Nodes Actually Losing?

With 9 of 15 OSDs running WAL-only, the performance gap is worth understanding. The difference comes down to where RocksDB metadata reads happen:

- **DB nodes (edgar, poe)**: metadata reads hit the MX500 SSD — sub-millisecond latency
- **WAL-only nodes (harlan, kovacs, quell)**: metadata reads hit the USB HDD — 5-15ms seek latency per operation

For a cluster with 2.94M objects, that's a lot of RocksDB lookups. The impact shows up in:

- **Scrub operations** — each object's checksum requires a metadata lookup. WAL-only OSDs scrub slower because every lookup waits for an HDD seek.
- **Recovery and backfill** — peering decisions require reading metadata for every PG. DB nodes peer faster after a restart.
- **CephFS directory listings** — listing a directory with thousands of files triggers metadata reads for each entry. DB nodes respond noticeably faster.
- **OSD startup time** — the OSD replays its RocksDB on startup. DB nodes boot faster because the replay reads from SSD.

You can compare OSD latency between WAL-only and DB nodes with:

```bash
# Compare apply latency across OSDs (lower is better)
for osd in 0 3 6 1 4 7; do
  LAT=$(ceph osd perf 2>/dev/null | grep "^\s*$osd" | awk '{print $3}')
  HOST=$(ceph osd metadata $osd 2>/dev/null | grep '"hostname"' | awk -F'"' '{print $4}')
  TYPE="WAL"
  ceph osd metadata $osd 2>/dev/null | grep -q bluefs_db && TYPE="DB"
  echo "osd.$osd  $HOST  $TYPE  apply_latency: ${LAT}ms"
done
```

I haven't run a formal A/B comparison yet — designing a test that isolates the WAL vs DB variable without disrupting a live cluster with 10 TiB of data is tricky. The OSDs serve different PGs with different access patterns, so raw latency numbers aren't directly comparable. A proper test would require creating matched OSDs on the same node with identical data, which means temporarily destroying and recreating an OSD. That's a project for a maintenance window, not a Tuesday afternoon. If I get to it, I'll publish the results as a follow-up.

## My Hardware Setup

### The AlteredCarbon Cluster

| Node | Role | CPU | RAM | Boot | Ceph SSD | Ceph Data |
|------|------|-----|-----|------|----------|-----------|
| harlan | OSD host | i7-2600 | 31 GB | 2x 128GB SSD (ZFS mirror) | CT500MX500SSD1 (500GB) | 3x 5TB Seagate USB |
| kovacs | OSD host | i7-2600 | 31 GB | 2x 149GB HDD (ZFS mirror) | CT500MX500SSD1 (500GB) | 3x 5TB Seagate USB |
| poe | OSD host | i7-2600 | 31 GB | 2x 149GB HDD (ZFS mirror) | CT500MX500SSD1 (500GB) | 3x 5TB Seagate USB |
| edgar | OSD host | i7-2600 | 31 GB | 2x 931GB HDD (ZFS mirror) | CT500MX500SSD1 (500GB) | 3x 5TB Seagate USB |
| quell | OSD host | i7-2600 | 31 GB | 2x 128GB SSD (ZFS mirror) | CT500MX500SSD1 (500GB) | 3x 5TB Seagate USB |
| tanaka | Monitor only | i5-2400 | 16 GB | 2x 465GB HDD (ZFS mirror) | — | — |

**15 OSDs** across 5 hosts. **69 TiB raw**, **39 TiB available** with 3x replication. Each OSD host has one Crucial MX500 500GB SATA SSD partitioned into three 100GB LVs for WAL/DB acceleration.

The cluster hasn't always been this size. Kovacs lost two USB drives during a [power failure in September 2025](/ceph-osd-recovery-power-failure/) and ran with a single OSD for months before replacement drives restored it to three. Poe was added as the fifth OSD host during the same period. The hardware table above reflects the current state.

### SSD Selection: Crucial MX500

The MX500 was chosen for:

- **Endurance** — 180 TBW for the 500GB model, adequate for WAL/DB workloads
- **Price** — ~$50-60, shared across 3 OSDs = ~$17-20 per OSD
- **SATA interface** — fits the Dell OptiPlex 990's available SATA ports (one remaining after boot mirror and DVD removal)
- **Reliability** — well-established consumer SSD with consistent performance

Each 500GB MX500 is partitioned into three 100GB LVM logical volumes, one per OSD. The remaining ~165GB is unallocated — available for wear leveling overhead or a future fourth OSD if I ever find a way to squeeze another USB drive onto a node.

### USB Drive Selection: Seagate 5TB Portables

The Ceph data drives are a mix of Seagate models:

- **Seagate One Touch HDD** (0bc2:ac41) — 5TB, USB 3.0
- **Seagate BUP Portable** (0bc2:ab9a) — 5TB, USB 3.0
- **Seagate Expansion** (0bc2:2344) — 5TB, USB 3.0

All require [USB storage quirks for SMART monitoring](/usb-drive-smart/) and stable operation:

```bash
echo 'options usb-storage quirks=0bc2:ac2b:,0bc2:ac41:,0bc2:2344:,0bc2:ab9a:' > /etc/modprobe.d/usbstorage-quirks.conf
update-initramfs -u
```

## Sizing WAL and DB Partitions

The Ceph documentation recommends:

- **WAL**: 1-2% of OSD data size (but minimum useful size is ~1GB)
- **DB**: 4% of OSD data size for optimal RocksDB performance

For a 5TB OSD:

- **WAL only**: ~50-100GB
- **DB (includes WAL)**: ~200GB ideal, 100GB workable

My cluster uses **100GB per OSD** for both WAL-only and DB configurations. This is slightly undersized for the DB recommendation but works well in practice because the actual data stored per OSD (~2-2.5 TiB with 3x replication) generates less metadata than the raw capacity would suggest.

### What Happens If DB Is Too Small?

If the RocksDB metadata outgrows the DB device, Ceph spills the overflow onto the data device (the USB HDD). Performance degrades gracefully — you don't lose data, you just lose the acceleration for the spilled portion. Monitor with:

```bash
ceph daemon osd.X perf dump | grep -i bluefs
```

## Creating Hybrid OSDs

### Method 1: Proxmox Web UI (Recommended)

**Proxmox → Node → Ceph → OSD → Create: OSD**

- **Disk**: select the USB drive (e.g., /dev/sdd)
- **DB Disk**: select the MX500 (e.g., /dev/sdc)
- **DB Disk Size**: 100 GiB
- **WAL Disk**: leave empty (DB includes WAL)

The UI creates the LVM logical volume on the SSD automatically. This creates a **DB** configuration (recommended).

### Method 2: CLI with Pre-Sized LV

For more control, or to force a specific OSD ID:

```bash
# Create a 100GB LV on the MX500's VG
lvcreate -L 100G -n osd-db-osd6 ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c

# Create the OSD with DB on the pre-sized LV
ceph-volume lvm create --osd-id 6 --data /dev/sdd \
  --block.db ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c/osd-db-osd6
```

The `--osd-id` flag is useful when replacing a failed drive and you want to keep the same OSD number for physical labeling. I used this approach when [replacing osd.6 on harlan](/zfs-ceph-overlapping-failures/) after a USB drive failure.

### Method 3: CLI with WAL Only (Legacy)

```bash
lvcreate -L 100G -n osd-wal-osd6 ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c

ceph-volume lvm create --osd-id 6 --data /dev/sdd \
  --block.wal ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c/osd-wal-osd6
```

This is how the original harlan, kovacs, and quell OSDs were created. It works but provides less acceleration than DB.

### Verifying the Configuration

After creation, verify the OSD has the SSD device attached:

```bash
ceph osd metadata osd.6 | grep -E '"id"|"hostname"|bluefs_wal|bluefs_db|bluestore_bdev'
```

For a cluster-wide view:

```bash
for osd in $(ceph osd ls | sort -n); do
  HOST=$(ceph osd metadata $osd 2>/dev/null | grep '"hostname"' | awk -F'"' '{print $4}')
  TYPE="WAL"
  ceph osd metadata $osd 2>/dev/null | grep -q bluefs_db && TYPE="DB"
  echo "osd.$osd  $HOST  $TYPE"
done
```

## Performance Results

### What the SSD Acceleration Changes

I don't have formal before/after benchmarks — I added the MX500 SSDs when building the OSDs, not as a retrofit. But the improvement is obvious in daily use, and the theory explains why: the SSD eliminates HDD seek latency for the operations that happen most frequently (metadata lookups and write journaling), while the USB 3.0 bus (~125 MB/s) remains the bottleneck for bulk data.

**Observed improvements with SSD WAL/DB:**

- **Small write latency**: Writes acknowledge at SSD speed before flushing to HDD in the background
- **Directory listings on CephFS**: Responsive even for directories with thousands of files (our media library has ~2.94M objects)
- **OSD peering after restart**: Minutes instead of tens of minutes — I saw this directly during the [April 2026 osd.6 replacement](/zfs-ceph-overlapping-failures/) when the new OSD peered quickly despite backfilling 4.5TB of data
- **Scrub operations**: Faster completion with less impact on client I/O

### Where It Doesn't Help

- **Large sequential reads** (streaming media from Jellyfin) — bottlenecked by USB 3.0, not metadata
- **Large sequential writes** (bulk file copies to CephFS) — same USB bottleneck
- **Network-limited operations** — 1GbE is often the bottleneck before USB is

### Current Cluster Performance

```console
root@harlan:~# ceph -s
  data:
    pools:   4 pools, 577 pgs
    objects: 2.94M objects, 10 TiB
    usage:   30 TiB used, 39 TiB / 69 TiB avail
```

The cluster handles 10 TiB of stored data (30 TiB with 3x replication) across CephFS for media storage and RBD for VM block devices. The hybrid configuration keeps metadata operations responsive even during Ceph recovery and rebalancing events.

## Cost Analysis

### Per-OSD Cost Comparison

| Configuration | Drive Cost | SSD Cost | Total per OSD |
|--------------|-----------|----------|---------------|
| **Hybrid (USB + SSD WAL/DB)** | $100-129 (5TB USB) | ~$17-20 (1/3 of MX500) | **$117-149** |
| **All-SSD** | $400-600 (5TB enterprise SSD) | included | **$400-600** |
| **USB only (no SSD)** | $100-129 (5TB USB) | $0 | **$100-129** |

### Full Cluster Cost

For the 15-OSD AlteredCarbon cluster:

| Configuration | Total Cost | Performance |
|--------------|-----------|-------------|
| **Hybrid (actual)** | ~$1,800-2,200 | Excellent for homelab |
| **All-SSD equivalent** | ~$6,000-9,000 | Overkill for USB bandwidth |
| **USB only** | ~$1,500-1,900 | Sluggish metadata |

The hybrid approach adds ~$300 (5x MX500 SSDs) to the USB-only cost and delivers the majority of the SSD performance benefit. The all-SSD option would be wasted on USB 3.0 bandwidth — you'd pay 4x more and still be bottlenecked by the bus.

### When the Math Changes

The hybrid approach stops making sense when:

- You upgrade to **10GbE networking** — the USB drives become the clear bottleneck, and all-SSD or NVMe becomes worth the cost
- You switch to **SATA-connected HDDs** — internal SATA is fast enough that WAL/DB separation provides less relative improvement
- You need **consistent low latency** — databases and high-IOPS workloads need all-SSD regardless of cost

## Operational Considerations

### SSD Wear Monitoring

The MX500 SSDs handle constant WAL/DB writes. Monitor wear with:

```bash
smartctl -A /dev/sdc | grep -E "Wear_Leveling|Media_Wearout|Available_Reservd"
```

At 100GB per OSD with 3 OSDs per SSD, the write amplification is modest. My MX500s show minimal wear after months of operation. Budget for replacement every 3-5 years depending on write volume.

### USB Drive Health

USB Ceph drives fail in [annoying ways](/zfs-ceph-overlapping-failures/) — hung USB bridges that block every command, drives that disappear from the bus entirely, and enclosures that enumerate for half a second then disconnect.

Essential monitoring:

```bash
smartctl -H /dev/sdd -d sat,12
```

See [Enabling SMART Monitoring on Seagate USB Drives](/usb-drive-smart/) and [USB Drive SMART Updates](/usb-drive-smart-updates/) for the full setup including USB quirks and GRUB configuration.

**Label your drives.** When a drive fails, knowing which physical USB cable corresponds to which OSD saves significant debugging time.

### The Single SSD Risk

The biggest risk of this architecture: **one SSD failure takes out three OSDs simultaneously.** Every OSD on that node loses its WAL/DB device and goes down at once. On a node with three 5TB OSDs, that's ~13.6 TiB of raw capacity disappearing in an instant.

We mitigate this with cluster design. The AlteredCarbon cluster has 5 OSD hosts with 3 OSDs each. Ceph's CRUSH map distributes replicas across hosts, so losing an entire node (all 3 OSDs) still leaves 2 copies of every object on the remaining 4 hosts. The cluster continues serving data in a degraded state while you replace the SSD.

This is the same failure domain as losing the node itself — a power supply failure, motherboard death, or even accidentally unplugging the wrong power cable would have the same effect. The SSD doesn't make the failure *worse*, it just adds another component that can trigger it.

**If you only have 3 OSD hosts**, this risk is more serious. Losing one node's SSD means losing one-third of your OSDs, and with `min_size=2` you'd be one more failure away from data unavailability. Four or more OSD hosts is the minimum I'd recommend for this architecture.

### SSD Failure Recovery

If the WAL/DB SSD fails, the affected OSDs will go down. Recovery depends on the failure mode:

**SSD dies, data drives intact:**

```bash
# The OSD data is still on the USB drive
# Replace the SSD, create new LVs, and recreate the OSDs
# Ceph will rebuild WAL/DB from the data on the USB drive
systemctl stop ceph-osd@0 ceph-osd@3 ceph-osd@6
# Replace SSD, partition, create LVs
# Recreate OSDs pointing to existing data drives with new WAL/DB LVs
```

**USB drive dies, SSD intact:**

The WAL/DB on the SSD is useless without the data drive. Remove the dead OSD, clean up the orphaned LV on the SSD, and add a replacement drive. This is exactly what I did when [osd.6's Seagate BUP Portable died](/zfs-ceph-overlapping-failures/).

### Rebalancing with Hybrid OSDs

During [Ceph rebalancing](/ceph-rebalance/), the SSD acceleration helps significantly. Metadata operations that drive the rebalancing process (peering, PG migration decisions) run at SSD speed, even though the actual data movement is limited by USB bandwidth. This means rebalancing *starts* faster and *tracks progress* more efficiently, even if the bulk data transfer rate is the same.

## Lessons Learned

1. **Use DB, not WAL-only.** The Proxmox UI defaults to DB for good reason. It accelerates both writes and metadata reads for the same SSD space.

2. **100GB per OSD is a good starting point.** For 5TB data drives with typical homelab workloads (media, backups, VMs), 100GB DB partitions haven't spilled to the HDD.

3. **One SSD per node, partitioned for all OSDs.** A single 500GB MX500 handles three OSDs comfortably. No need for one SSD per OSD.

4. **The SSD doesn't fix the USB bottleneck.** Large sequential I/O is still limited by USB 3.0. The SSD fixes the *metadata* bottleneck, which is what makes the cluster feel responsive.

5. **Label everything.** Physical drive labels with OSD numbers save hours during failures. I learned this the hard way during the [April 2026 osd.6 replacement](/zfs-ceph-overlapping-failures/).

6. **Monitor SSD wear and USB health separately.** They fail in different ways — SSDs wear out gradually (SMART attributes), USB drives fail suddenly (bus disconnects, bridge hangs).

7. **Document your creation method.** Whether you used the Proxmox UI (DB) or CLI (WAL), knowing which method created each OSD explains configuration differences when you're debugging at 2 AM.

## Related Posts

- [When ZFS and Ceph Problems Collide](/zfs-ceph-overlapping-failures/) — Discovering the WAL vs DB inconsistency across the cluster
- [Ceph OSD Recovery After Power Failure](/ceph-osd-recovery-power-failure/) — Recovering from cascading OSD failures on the same hardware
- [Proxmox Ceph Settings for the Homelab](/proxmox-ceph-homelab-settings/) — Tuning scrub intervals and pool settings for homelab hardware
- [Optimizing Ceph Performance in Proxmox](/proxmox-ceph-performance/) — mClock tuning and IOPS optimization
- [Enabling SMART Monitoring on Seagate USB Drives](/usb-drive-smart/) — Getting health data from USB Ceph drives
- [USB Drive SMART Updates](/usb-drive-smart-updates/) — Updated SMART configuration for new drive models
- [Homelab Storage Economics: Ceph vs Single Drive](/homelab-storage-economics/) — Cost analysis of distributed storage
- [Managing Ceph Nearfull Warnings](/proxmox-ceph-nearfull/) — Capacity management for the cluster
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — All Proxmox and Ceph articles

## References

- [Ceph BlueStore Configuration Reference](https://docs.ceph.com/en/reef/rados/configuration/bluestore-config-ref/) — Official WAL/DB documentation
- [Florian's Ceph Calculator](https://florian.ca/ceph-calculator/) — Planning OSD layouts and capacity
- [Proxmox Ceph Documentation](https://pve.proxmox.com/pve-docs/chapter-pveceph.html) — Proxmox-specific Ceph guidance
- [Ceph OSD SSD Acceleration Reference](https://github.com/mcgarrah/k8s-proxmox/blob/main/docs/CEPH-OSD-SSD-ACCELERATION.md) — Full OSD-to-device mapping for the AlteredCarbon cluster
