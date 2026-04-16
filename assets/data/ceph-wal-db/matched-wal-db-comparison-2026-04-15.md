# Matched Cross-Node WAL vs DB Comparison

Collected: 2026-04-15 ~01:45 EDT from Thomas via SSH
Purpose: Best-possible WAL vs DB comparison without rebuilding an OSD

## Hardware Match Verification

All five OSD nodes confirmed identical:
- CPU: Intel Core i7-2600 @ 3.40GHz (Sandy Bridge)
- Chassis: Dell OptiPlex 990 Tower
- USB 3.0 controller: Renesas uPD720201 (rev 03) — same chip, same revision
- USB 2.0 controllers: Intel 6 Series/C200 EHCI #1 and #2

### Drive Model Match: quell (WAL) vs edgar (DB)

| OSD | Node | Accel | Drive Model | RPM | Power-On Hours | Fill |
|-----|------|-------|-------------|-----|---------------:|------|
| osd.9 | quell | WAL | ST5000LM000-2U8170 | 5400 | 16,019h | 2.3 TiB (51%) |
| osd.10 | quell | WAL | ST5000LM000-2U8170 | 5400 | 16,022h | 2.0 TiB (43%) |
| osd.11 | quell | WAL | ST5000LM000-2U8170 | 5400 | 16,022h | 2.2 TiB (49%) |
| osd.1 | edgar | DB | ST5000LM000-2U8170 | 5400 | 2,138h | 2.3 TiB (49%) |
| osd.4 | edgar | DB | ST5000LM000-2U8170 | 5400 | 2,137h | 2.4 TiB (51%) |
| osd.7 | edgar | DB | ST5000LM000-2U8170 | 5400 | 2,137h | 2.3 TiB (49%) |

Same drive model, same RPM, same USB controller, same CPU. quell drives are
older (16K hours vs 2K hours) but all healthy. Fill levels are well matched.

Note: harlan (WAL) uses the older ST5000LM000-2AN170 variant (5526 RPM) and
kovacs has a Samsung SSD on sdd — neither is a clean match for edgar.

## OSD Bench: Large I/O (1 GB, 4 MB blocks)

| OSD | Type | Node | Time | MB/s | IOPS |
|-----|------|------|-----:|-----:|-----:|
| osd.9 | WAL | quell | 31.0s | 33.1 | 8.27 |
| osd.11 | WAL | quell | 33.7s | 30.4 | 7.60 |
| osd.4 | DB | edgar | 39.0s | 26.2 | 6.56 |
| osd.7 | DB | edgar | 34.2s | 30.0 | 7.50 |

| Group | Avg MB/s | Avg IOPS |
|-------|--------:|--------:|
| WAL (quell) | 31.8 | 7.93 |
| DB (edgar) | 28.1 | 7.03 |

Large I/O: WAL slightly faster — likely noise or edgar under more load (3 DB
OSDs + mon + backfill source duties). No meaningful WAL vs DB difference expected
on large sequential writes.

## OSD Bench: Small I/O (12 MB, 4 KB blocks)

| OSD | Type | Node | Time | MB/s | IOPS |
|-----|------|------|-----:|-----:|-----:|
| osd.9 | WAL | quell | 0.80s | 14.7 | 3,759 |
| osd.10 | WAL | quell | 0.84s | 13.9 | 3,569 |
| osd.11 | WAL | quell | 0.93s | 12.6 | 3,231 |
| osd.1 | DB | edgar | 0.80s | 14.7 | 3,760 |
| osd.4 | DB | edgar | 2.48s | 4.7 | 1,207 |
| osd.7 | DB | edgar | 1.16s | 10.1 | 2,582 |

| Group | Avg IOPS | Notes |
|-------|--------:|-------|
| WAL (quell, 3 OSDs) | 3,520 | Consistent: 3,231-3,759 |
| DB (edgar, 3 OSDs) | 2,516 | High variance: 1,207-3,760 |

**Surprise: WAL outperformed DB on small I/O in this matched test.**

osd.4 (DB, edgar) was a clear outlier at 1,207 IOPS — possibly under heavy
background load from backfill source duties or mon.edgar issues (mon was out
of quorum during this test). osd.1 (DB) matched WAL performance exactly.

This contradicts the Phase 1 cross-node results where DB appeared faster.
The earlier test compared harlan (WAL, 2AN170 drives at 5526 RPM) against
edgar (DB, 2U8170 at 5400 RPM) — the harlan drives are a slightly faster
variant, which may have masked the true comparison.

## Daemon Perf Dump Latency (since last OSD restart)

### quell — WAL

| OSD | op_latency | op_r_latency | op_w_latency | subop_latency | op_count |
|-----|----------:|-------------:|-------------:|--------------:|---------:|
| osd.9 | 378.3ms | 31.1ms | 389.2ms | 168.1ms | 418,592 |
| osd.10 | 613.9ms | 18.9ms | 716.6ms | 158.3ms | 77,877 |
| osd.11 | 268.4ms | 7.1ms | 351.7ms | 73.4ms | 114,592 |
| **avg** | **420.2ms** | **19.0ms** | **485.8ms** | **133.2ms** | |

### edgar — DB

| OSD | op_latency | op_r_latency | op_w_latency | subop_latency | op_count |
|-----|----------:|-------------:|-------------:|--------------:|---------:|
| osd.1 | 445.8ms | 16.8ms | 546.5ms | 138.9ms | 59,848 |
| osd.4 | 502.2ms | 17.9ms | 506.9ms | 158.0ms | 1,251,321 |
| osd.7 | 251.5ms | 16.1ms | 254.4ms | 170.3ms | 658,137 |
| **avg** | **399.8ms** | **16.9ms** | **435.9ms** | **155.7ms** | |

### Comparison

| Metric | WAL avg (quell) | DB avg (edgar) | Difference |
|--------|----------------:|---------------:|-----------:|
| op_r_latency | 19.0ms | 16.9ms | DB 11% faster |
| op_w_latency | 485.8ms | 435.9ms | DB 10% faster |
| subop_latency | 133.2ms | 155.7ms | WAL 14% faster |
| op_latency | 420.2ms | 399.8ms | DB 5% faster |

DB shows a modest read latency advantage (11%) but the gap is much smaller
than the Phase 1 cross-node comparison suggested (32%). subop_latency actually
favors WAL, possibly because edgar's OSDs handle more subops from being
backfill sources.

## Key Findings

1. **The Phase 1 "DB is 32% faster on reads" was overstated.** With properly
   matched hardware (same drive model, same USB controller), the read latency
   gap shrinks to ~11%. The earlier comparison was confounded by different
   drive variants (2AN170 vs 2U8170) and different node load profiles.

2. **Small I/O bench results are inconclusive.** WAL averaged 3,520 IOPS vs
   DB at 2,516 IOPS, but osd.4 was a clear outlier (1,207 IOPS) likely due
   to edgar's elevated load (mon out of quorum, backfill source duties).
   Excluding osd.4, DB averaged 3,171 IOPS — within noise of WAL's 3,520.

3. **Large I/O shows no WAL vs DB difference** — consistent with theory.

4. **The real-world difference between WAL and DB on this hardware is likely
   5-15%, not the 24-48% suggested by Phase 1.** Still meaningful over time,
   but not dramatic enough to justify the 4-5 day backfill cost per OSD
   conversion.

5. **edgar was under more stress during this test** (mon out of quorum, 3 OSDs
   serving as backfill sources for osd.6 on harlan). A cleaner test after
   osd.6 backfill completes would give more reliable numbers.
