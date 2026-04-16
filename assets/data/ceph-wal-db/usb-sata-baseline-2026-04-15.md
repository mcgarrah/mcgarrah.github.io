# USB 3.0 vs Direct SATA Performance Baseline

Collected: 2026-04-15 from Thomas via SSH to harlan
Node: harlan (Dell OptiPlex 990, i7-2600)
Purpose: Prove the backfill bottleneck is spinning disk random I/O, not USB bus bandwidth

## Device Topology (harlan)

| Device | Model | Interface | Type | ROTA | Role |
|--------|-------|-----------|------|------|------|
| sda | SSD (boot) | SATA direct | SSD | 0 | ZFS boot mirror |
| sdb | SSD (boot) | SATA direct | SSD | 0 | ZFS boot mirror |
| sdc | CT500MX500SSD1 | SATA direct | SSD | 0 | Ceph WAL LVs (3x 100GB) |
| sdd | ST5000LM000-2AN170 | USB 3.0 | HDD | 1 | Ceph OSD (osd.0) |
| sde | ST5000LM000-2AN170 | USB 3.0 | HDD | 1 | Ceph OSD (osd.3) |
| sdf | ST5000LM000-2AN170 | USB 3.0 | HDD | 1 | Ceph OSD (osd.6) |

Source: `lsblk -o NAME,SIZE,TYPE,TRAN,MODEL,ROTA` on harlan

Note: UAS is disabled cluster-wide via GRUB boot parameters for SMART monitoring.
This reduces USB throughput by 10-30% vs native UAS mode. All numbers below
reflect this trade-off.

## Sequential Read (hdparm -t)

| Device | Interface | MB/s |
|--------|-----------|-----:|
| sdc (MX500 SSD) | SATA direct | 241.91 |
| sdd (Seagate HDD) | USB 3.0 | 125.86 |
| sde (Seagate HDD) | USB 3.0 | 103.20 |
| sdf (Seagate HDD) | USB 3.0 | 127.14 |

SSD is ~2x faster on sequential reads. USB bus is not the bottleneck here —
the HDDs are delivering 100-127 MB/s, which is reasonable for 5400 RPM 2.5" drives.

## Cached Read — Controller/Bus Speed (hdparm -T)

| Device | Interface | MB/s |
|--------|-----------|-----:|
| sdc (MX500 SSD) | SATA direct | 11,921.10 |
| sdd (Seagate HDD) | USB 3.0 | 11,503.18 |

Nearly identical — confirms the memory/bus path is not a differentiator.

## Direct 4K Sequential Read (dd iflag=direct, 10000 blocks)

| Device | Interface | MB/s |
|--------|-----------|-----:|
| sdc (MX500 SSD) | SATA direct | 88.4 |
| sdd (Seagate HDD) | USB 3.0 | 20.4 |
| sde (Seagate HDD) | USB 3.0 | 17.2 |

SSD is ~4.5x faster at 4K sequential direct reads. The gap widens as block
size shrinks because the HDD's seek time becomes a larger fraction of each I/O.

## Random 4K Read IOPS (dd with random offsets, iflag=direct)

Method: Shell loop doing `dd if=/dev/sdX of=/dev/null bs=4k count=1 skip=$((RANDOM * offset)) iflag=direct`
SSD: 1000 iterations. HDDs: 200 iterations (too slow for 1000).

| Device | Interface | IOPS |
|--------|-----------|-----:|
| sdc (MX500 SSD) | SATA direct | 979 |
| sdd (Seagate HDD) | USB 3.0 | 77 |
| sde (Seagate HDD) | USB 3.0 | 76 |
| sdf (Seagate HDD) | USB 3.0 | 71 |

**SSD is 13x faster on random 4K reads.** This is the smoking gun.

## Analysis

| Metric | SSD (SATA) | HDD (USB) | Ratio |
|--------|----------:|----------:|------:|
| Sequential read | 242 MB/s | 119 MB/s avg | 2.0x |
| 4K sequential read | 88 MB/s | 19 MB/s avg | 4.6x |
| Random 4K IOPS | 979 | 75 avg | **13.0x** |

The gap grows dramatically as I/O becomes more random:
- Sequential: 2x (USB bus + HDD platter speed)
- Small sequential: 4.6x (seek time starts to matter)
- Random: 13x (pure seek-time dominated)

Ceph OSD operations during backfill and normal use are dominated by random I/O —
metadata lookups, PG peering, scattered object reads/writes. At 75 IOPS × 4 KB =
~300 KB/s of random read throughput, the ~13 MiB/s recovery rate makes sense:
the OSD mixes random metadata reads with sequential data writes, and the spinning
platters can't seek fast enough.

The USB-SATA bridge adds some overhead (limited command queuing vs native SATA NCQ),
but the fundamental constraint is the ~8ms average seek time of a 5400 RPM 2.5" drive.

## Why This Matters for WAL vs DB

DB acceleration moves RocksDB metadata reads from the 75-IOPS HDD to the 979-IOPS SSD.
That's a 13x improvement on the metadata path specifically. WAL-only acceleration
already puts writes on the SSD, but metadata reads still hit the slow HDD.

The DB advantage is amplified by slow underlying storage — on a cluster with NVMe
or direct-attached SSDs, the gap between WAL and DB would be much smaller because
the "slow" path wouldn't be nearly as slow.

## Tools Used

- `hdparm -t` — sequential buffered read
- `hdparm -T` — cached read (controller/bus speed)
- `dd iflag=direct bs=4k` — direct I/O bypassing page cache
- Shell loop with `$RANDOM` offsets — poor man's random IOPS test
- No `fio` or `ioping` available on the node (not installed)
