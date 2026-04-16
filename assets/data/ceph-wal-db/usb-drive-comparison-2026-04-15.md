# USB Drive Comparison: 5400 RPM 2.5" vs 7200 RPM 3.5" vs SSD

Collected: 2026-04-15 from Thomas via SSH to quell and edgar
Purpose: Compare Ceph OSD drives against ZFS replica drives on the same USB bus

## Drive Inventory

| Drive | Model | Size | RPM | Form | Interface | Node | Role |
|-------|-------|------|-----|------|-----------|------|------|
| ST5000LM000-2AN170 | Seagate | 5 TB | 5400 | 2.5" | USB 3.0 | harlan | Ceph OSD (×3) |
| ST5000LM000-2U8170 | Seagate | 5 TB | 5400 | 2.5" | USB 3.0 | quell, edgar, poe | Ceph OSD (×3 per node) |
| OOS20000G | ? | 20 TB | 7200 | 3.5" | USB 3.0 | quell/sdd | ZFS replica pool |
| ST28000DM000-3Y9103 | Seagate | 28 TB | 7200 | 3.5" | USB 3.0 | edgar/sdg | ZFS replica28 pool |
| CT500MX500SSD1 | Crucial MX500 | 500 GB | — | 2.5" | SATA direct | all nodes/sdc | Ceph WAL/DB LVs |

Note: UAS disabled cluster-wide via GRUB for SMART monitoring (10-30% throughput reduction).

## Sequential Read (hdparm -t)

| Drive | RPM | Form | Node | MB/s |
|-------|-----|------|------|-----:|
| MX500 SSD | — | 2.5" | harlan | 241.9 |
| ST28000DM000 | 7200 | 3.5" | edgar | 187.0 |
| OOS20000G | 7200 | 3.5" | quell | 174.1 |
| ST5000LM000 | 5400 | 2.5" | quell | 140.3 |
| ST5000LM000 | 5400 | 2.5" | harlan (sdd) | 125.9 |
| ST5000LM000 | 5400 | 2.5" | edgar | 120.9 |
| ST5000LM000 | 5400 | 2.5" | harlan (sde) | 103.2 |
| ST5000LM000 | 5400 | 2.5" | harlan (sdf) | 127.1 |

## Random 4K Read IOPS (dd with random offsets, iflag=direct, 200 iterations)

| Drive | RPM | Form | Node | IOPS |
|-------|-----|------|------|-----:|
| MX500 SSD | — | 2.5" | harlan | 979 |
| ST28000DM000 | 7200 | 3.5" | edgar | 138 |
| OOS20000G | 7200 | 3.5" | quell | 120 |
| ST5000LM000 | 5400 | 2.5" | quell | 85 |
| ST5000LM000 | 5400 | 2.5" | harlan (sdd) | 77 |
| ST5000LM000 | 5400 | 2.5" | harlan (sde) | 76 |
| ST5000LM000 | 5400 | 2.5" | harlan (sdf) | 71 |
| ST5000LM000 | 5400 | 2.5" | edgar | 72 |

## Analysis

### Grouped Averages

| Drive Class | Seq Read | Random 4K IOPS |
|-------------|--------:|---------------:|
| SSD (SATA direct) | 242 MB/s | 979 IOPS |
| 7200 RPM 3.5" (USB) | 181 MB/s | 129 IOPS |
| 5400 RPM 2.5" (USB) | 123 MB/s | 77 IOPS |

### Relative Performance (vs 5400 RPM 2.5" Ceph drives)

| Comparison | Sequential | Random IOPS |
|------------|----------:|------------:|
| 7200 RPM 3.5" vs 5400 RPM 2.5" | 1.5× faster | **1.7× faster** |
| SSD vs 5400 RPM 2.5" | 2.0× faster | **12.7× faster** |
| SSD vs 7200 RPM 3.5" | 1.3× faster | **7.6× faster** |

### Key Takeaways

1. The 7200 RPM 3.5" drives get 60-90% more random IOPS than the 5400 RPM 2.5"
   Ceph drives on the same USB 3.0 bus. This is pure seek time physics — 3.5"
   platters at 7200 RPM have ~5.5ms average seek vs ~8ms for 2.5" at 5400 RPM.

2. Even the fastest spinning USB drive (138 IOPS) is still 7× slower than the
   SSD (979 IOPS). DB acceleration moves metadata reads from any of these HDDs
   to the SSD — the benefit is significant regardless of which HDD is underneath.

3. If the Ceph OSDs used 7200 RPM 3.5" drives instead of 5400 RPM 2.5":
   - Backfill would be ~60% faster (~10 MiB/s sustained vs ~6 MiB/s)
   - The WAL vs DB gap would be somewhat smaller but still significant
   - The Dell OptiPlex 990 can't physically fit 3.5" drives in USB enclosures
     alongside the tower chassis, so this is academic for this cluster

4. The USB 3.0 bus is not the bottleneck for any of these drives. All three
   classes (SSD, 7200 RPM, 5400 RPM) are well below USB 3.0's ~400 MB/s
   practical ceiling. The bottleneck is always the drive's own mechanical
   or flash performance.
