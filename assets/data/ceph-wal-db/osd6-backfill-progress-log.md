# OSD.6 Backfill Progress Log

Created: 2026-04-13 12:40 EDT (osd.6 LV created and service started)
Target: ~2.2 TiB (~45% fill to match peers osd.0 and osd.3 on harlan)

## Progress Snapshots

| Timestamp | Fill | % | PGs Active | PGs Waiting | Instant Rate | Sustained Avg | Notes |
|-----------|-----:|--:|----------:|-----------:|----------:|-------------:|-------|
| 2026-04-13 12:40 | 0 GiB | 0.0% | — | — | — | — | OSD created, backfill started |
| 2026-04-15 00:40 | 744 GiB | 15.97% | 3 | 138 | 6.0 MiB/s | 6.0 MiB/s | Pre-tuning baseline (35.3h elapsed) |
| 2026-04-15 00:45 | 744 GiB | 15.97% | 4 | 138 | 14 MiB/s | 6.0 MiB/s | Tuning applied: noscrub, nodeep-scrub, priority=30 |
| 2026-04-15 01:25 | 756 GiB | 16.24% | 3 | 137 | 6.0 MiB/s | 6.0 MiB/s | Concurrency A/B test — no improvement, reverted to defaults |
| 2026-04-15 10:30 | 992 GiB | 21.30% | 3 | 101 | 16 MiB/s | 6.2 MiB/s | Best instantaneous rate seen; 236 GiB in ~10h |
| 2026-04-15 14:00 | 1,126 GiB | 23.18% | 3 | 87 | 15 MiB/s | 6.5 MiB/s | Sustained avg climbing; halfway on data |

## Estimated Completion

Based on 2026-04-15 14:00 snapshot:
- Elapsed: 49.3 hours
- Remaining: ~1,126 GiB (1.1 TiB)
- Sustained avg: 6.5 MiB/s
- Est. remaining: ~49 hours (2.1 days)
- Est. total: ~98 hours (4.1 days)
- Est. completion: ~2026-04-17 15:00 EDT

## Active Tuning

| Setting | Value | Notes |
|---------|-------|-------|
| noscrub | on | Pauses scrubs cluster-wide |
| nodeep-scrub | on | Pauses deep scrubs cluster-wide |
| osd_recovery_op_priority | 30 (persistent) | Elevated from default 15 |
| osd_max_backfills | 1 (default) | Reverted — higher didn't help |
| osd_recovery_max_active | 0/auto (default) | Reverted — higher didn't help |

## How to Update This Log

Run the one-liner and append a row:

```bash
ssh harlan 'DATA=$(ceph osd df 2>/dev/null | grep "^ *6 " | awk "{print \$7,\$8}"); \
  PCT=$(ceph osd df 2>/dev/null | grep "^ *6 " | awk "{print \$17}"); \
  RATE=$(ceph status 2>/dev/null | grep recovery | awk "{print \$2,\$3}"); \
  PGW=$(ceph pg dump 2>/dev/null | grep -c backfill_wait); \
  PGA=$(ceph pg dump 2>/dev/null | grep -c "backfilling[^_]"); \
  echo "osd.6: ${DATA} (${PCT}%) / ~2.2 TiB target | recovery: ${RATE} | PGs: ${PGA} active, ${PGW} waiting"'
```
