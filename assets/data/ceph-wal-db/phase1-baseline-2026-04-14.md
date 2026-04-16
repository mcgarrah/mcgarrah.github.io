# Ceph WAL vs DB Performance Baseline — Phase 1 Results

Collected: 2026-04-14 ~23:45 EST
Cluster: AlteredCarbon (Ceph 18.2.7 Reef)
Cluster health: HEALTH_WARN (osd.6 backfilling, 577 PGs behind on scrubs)

## OSD Configuration Map

| OSD | Node | Acceleration | Data Used | PGs | Notes |
|-----|------|-------------|-----------|-----|-------|
| osd.0 | harlan | WAL-only | 2.1 TiB | 115 | |
| osd.3 | harlan | WAL-only | 2.3 TiB | 136 | |
| osd.6 | harlan | WAL-only | 729 GiB | 36 | ⚠️ Backfilling — data unreliable |
| osd.2 | kovacs | WAL-only | 2.4 TiB | 133 | |
| osd.5 | kovacs | WAL-only | 2.2 TiB | 122 | |
| osd.8 | kovacs | WAL-only | 2.1 TiB | 118 | |
| osd.9 | quell | WAL-only | 2.3 TiB | 134 | |
| osd.10 | quell | WAL-only | 2.0 TiB | 115 | |
| osd.11 | quell | WAL-only | 2.2 TiB | 128 | |
| osd.1 | edgar | **DB** | 2.3 TiB | 130 | |
| osd.4 | edgar | **DB** | 2.4 TiB | 128 | |
| osd.7 | edgar | **DB** | 2.3 TiB | 122 | |
| osd.12 | poe | **DB** | 1.7 TiB | 88 | |
| osd.13 | poe | **DB** | 1.8 TiB | 96 | |
| osd.14 | poe | **DB** | 1.6 TiB | 87 | |

## ceph osd perf (cluster-wide snapshot)

| OSD | Type | commit_latency(ms) | apply_latency(ms) |
|-----|------|-------------------:|-------------------:|
| osd.0 | WAL | 288 | 288 |
| osd.3 | WAL | 25 | 25 |
| osd.6 | WAL | 116 | 116 |
| osd.2 | WAL | 0 | 0 |
| osd.5 | WAL | 122 | 122 |
| osd.8 | WAL | 0 | 0 |
| osd.9 | WAL | 0 | 0 |
| osd.10 | WAL | 8 | 8 |
| osd.11 | WAL | 0 | 0 |
| osd.1 | DB | 0 | 0 |
| osd.4 | DB | 30 | 30 |
| osd.7 | DB | 161 | 161 |
| osd.12 | DB | 767 | 767 |
| osd.13 | DB | 278 | 278 |
| osd.14 | DB | 108 | 108 |

Note: `ceph osd perf` shows instantaneous latency, not averages. Many OSDs
show 0ms because they had no recent operations at the moment of sampling.
This metric alone is not useful for WAL vs DB comparison.

## Per-OSD Daemon Latency (perf dump averages since last restart)

### WAL-only OSDs

| OSD | Node | op_latency | op_r_latency | op_w_latency | subop_latency | op_count |
|-----|------|----------:|-------------:|-------------:|--------------:|---------:|
| osd.0 | harlan | 63.4ms | 3.7ms | 481.7ms | 337.5ms | 56,315 |
| osd.3 | harlan | 776.9ms | 40.4ms | 832.0ms | 85.2ms | 1,078 |
| osd.6 | harlan | 3322.3ms | 25.5ms | 3761.8ms | 47.2ms | 17 |
| osd.2 | kovacs | 321.5ms | 26.3ms | 344.9ms | 111.0ms | 120,847 |
| osd.5 | kovacs | 33.8ms | 0.5ms | 527.0ms | 250.6ms | 534,711 |
| osd.8 | kovacs | 194.8ms | 29.0ms | 200.6ms | 92.0ms | 190,489 |
| osd.9 | quell | 377.6ms | 31.1ms | 388.4ms | 167.8ms | 418,237 |
| osd.10 | quell | 612.8ms | 18.8ms | 715.4ms | 157.5ms | 77,762 |
| osd.11 | quell | 267.1ms | 7.0ms | 350.0ms | 73.2ms | 114,500 |

### DB OSDs

| OSD | Node | op_latency | op_r_latency | op_w_latency | subop_latency | op_count |
|-----|------|----------:|-------------:|-------------:|--------------:|---------:|
| osd.1 | edgar | 440.3ms | 16.7ms | 539.8ms | 138.2ms | 59,725 |
| osd.4 | edgar | 502.3ms | 17.8ms | 507.1ms | 157.5ms | 1,246,200 |
| osd.7 | edgar | 250.3ms | 16.5ms | 253.1ms | 169.8ms | 655,294 |
| osd.12 | poe | 403.8ms | 22.0ms | 440.6ms | 216.6ms | 63,940 |
| osd.13 | poe | 41.3ms | 0.3ms | 233.2ms | 167.2ms | 1,127,684 |
| osd.14 | poe | 343.1ms | 6.6ms | 492.7ms | 27.0ms | 44,904 |

### Averages (excluding osd.6 backfilling)

| Metric | WAL avg (8 OSDs) | DB avg (6 OSDs) | Difference |
|--------|------------------:|----------------:|-----------:|
| op_r_latency | 19.6ms | 13.3ms | DB 32% faster |
| op_w_latency | 480.0ms | 411.1ms | DB 14% faster |
| subop_latency | 159.2ms | 146.1ms | DB 9% faster |

## OSD Bench Results (ceph tell osd.X bench)

### Large I/O: 1GB with 4MB blocks

| OSD | Type | Node | elapsed_sec | MB/s | IOPS |
|-----|------|------|------------:|-----:|-----:|
| osd.0 | WAL | harlan | 28.95 | 35.4 | 8.84 |
| osd.1 | DB | edgar | 34.96 | 29.3 | 7.32 |
| osd.5 | WAL | kovacs | 37.19 | 27.5 | 6.88 |
| osd.12 | DB | poe | 36.50 | 28.1 | 7.01 |

Large I/O: No meaningful WAL vs DB difference (expected — large writes bypass metadata).

### Small I/O: 12MB with 4KB blocks (metadata-relevant)

| OSD | Type | Node | elapsed_sec | MB/s | IOPS |
|-----|------|------|------------:|-----:|-----:|
| osd.0 | WAL | harlan | 1.17 | 10.0 | 2,556 |
| osd.3 | WAL | harlan | 1.59 | 7.4 | 1,886 |
| osd.1 | DB | edgar | 0.78 | 15.0 | 3,834 |
| osd.4 | DB | edgar | 1.10 | 10.6 | 2,720 |
| osd.5 | WAL | kovacs | 1.31 | 8.9 | 2,287 |
| osd.12 | DB | poe | 1.67 | 7.0 | 1,801 |

Small I/O averages:
- WAL: 2,243 IOPS (3 OSDs)
- DB:  2,785 IOPS (3 OSDs)
- DB is ~24% faster on small I/O

Note: osd.12 (DB, poe) underperformed — possibly different SSD model or
higher background load on poe. The harlan-WAL vs edgar-DB comparison
(same generation hardware) shows a clearer ~50% advantage for DB.

## Observations

1. **Read latency**: DB OSDs show consistently lower read latency (13.3ms vs 19.6ms avg).
   This aligns with theory — DB stores RocksDB metadata on SSD, reducing HDD seeks for lookups.

2. **Write latency**: Smaller difference (411ms vs 480ms). Both configurations journal
   writes to SSD via WAL, so the write path is similar. The DB advantage likely comes from
   faster metadata updates during write completion.

3. **Small I/O bench**: DB shows ~24% higher IOPS on 4KB writes. The harlan(WAL) vs
   edgar(DB) comparison is the cleanest: 2,221 vs 3,277 IOPS — a 48% advantage for DB.

4. **Large I/O bench**: No meaningful difference. WAL osd.0 was actually faster than
   DB osd.1. This confirms the difference is in the metadata path, not bulk data.

5. **osd.6 is unreliable**: Only 729 GiB / 36 PGs — still backfilling. Exclude from
   all comparisons until HEALTH_OK.

6. **Variance is high**: op_count varies wildly across OSDs (17 to 1.2M), meaning
   some averages are based on very few operations. The perf dump counters reset on
   OSD restart, so harlan's OSDs (restarted 1 day ago) have fewer ops than kovacs
   (29 days uptime).

## Next Steps

- [ ] Wait for osd.6 backfill to complete and cluster to reach HEALTH_OK
- [ ] Re-run perf dump after osd.6 is stable for a cleaner harlan baseline
- [ ] Phase 2: Rebuild osd.6 as DB (requires maintenance window)
- [ ] Phase 3: Matched comparison of osd.0(WAL) vs osd.6(DB) on same node
- [ ] Scrub timing comparison (deferred — too many PGs behind on scrubs currently)
- [ ] Peering time comparison (deferred — requires OSD restart with noout)
