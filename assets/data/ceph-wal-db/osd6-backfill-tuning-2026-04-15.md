# OSD.6 Backfill Acceleration — Temporary Tuning

Applied: 2026-04-15 ~00:40 EDT
Purpose: Speed up osd.6 backfill by pausing scrubs and increasing recovery priority
Revert: After osd.6 reaches ~45% fill and cluster returns to HEALTH_OK

## What Was Changed

| Setting | Before | Tuned | Final | Method |
|---------|--------|-------|-------|--------|
| `noscrub` flag | off | **on** | **on** | `ceph osd set noscrub` |
| `nodeep-scrub` flag | off | **on** | **on** | `ceph osd set nodeep-scrub` |
| `osd_max_backfills` | 1 | 3 | **1 (reverted)** | `ceph tell osd.X injectargs` |
| `osd_recovery_max_active` | 0 (auto=3 HDD) | 5 | **0 (reverted)** | `ceph tell osd.X injectargs` |
| `osd_recovery_op_priority` | 15 | **30** | **30** | `ceph config set osd` (persistent) |

Concurrency settings were reverted after A/B testing showed no benefit — see below.

## Observed Impact

- Scrubs dropped from 20 → 0 immediately
- Instantaneous recovery rate: 11-14 MiB/s (similar, but no longer competing with scrubs)
- **Post-tuning sustained average: still ~6 MiB/s** — same as pre-tuning
- The tuning did not meaningfully improve backfill throughput on harlan

### Why Tuning Didn't Help

The bottleneck is harlan's USB controller, not Ceph scheduling. All three USB
drives (sdd=osd.0, sde=osd.3, sdf=osd.6) share the same USB host controller.
During backfill, osd.0 and osd.3 read source data from their drives while osd.6
writes incoming data to its drive — three drives competing for one USB bus.

Harlan disk I/O snapshot (2026-04-15 01:25 EDT):

| Device | OSD | Role in backfill | Write IOs | IO time (sec) |
|--------|-----|-----------------|----------:|-------------:|
| sdd | osd.0 | Source (reading) | 1,768,175 | 30,846 |
| sde | osd.3 | Source (reading) | 145,334 | 12,701 |
| sdf | osd.6 | Target (writing) | 87,465 | 9,158 |

osd.6 is barely getting writes — it's starved by the other two OSDs consuming
USB bus bandwidth. Increasing `osd_max_backfills` and `osd_recovery_max_active`
just queues more work that the USB controller can't deliver.

The scrub pause was still the right call — 20 concurrent scrubs were adding
unnecessary disk pressure across the whole cluster — but the backfill rate on
harlan is fundamentally limited by the shared USB bus.

**Lesson:** Ceph recovery tuning has diminishing returns when the storage I/O
path is already saturated. On USB-attached spinning disks, the hardware ceiling
is the constraint, not Ceph's scheduling parameters.

## Concurrency A/B Test (2026-04-15 01:35 EDT)

Tested three concurrency levels to check if higher settings hurt or help:

| Setting | backfills | active | Samples | Rate range | Avg |
|---------|-----------|--------|---------|-----------|-----|
| Tuned | 3 | 5 | 3 | 6.8-7.4 MiB/s | ~7.0 |
| Default | 1 | auto(3) | 9 | 4.9-9.1 MiB/s | ~6.5 |
| Moderate | 2 | 3 | 6 | 5.3-8.0 MiB/s | ~6.7 |

All within the same noise band. Higher concurrency doesn't hurt, but doesn't
help either — the USB controller is the ceiling regardless.

**Decision:** Reverted concurrency to defaults (backfills=1, active=auto).
Kept the scrub pause and elevated priority (30) since those reduce unnecessary
cluster-wide disk pressure without adding contention on harlan's USB bus.

## OSD.6 Backfill Timeline

| Timestamp | Event |
|-----------|-------|
| 2026-04-13 12:39:52 | WAL LV created (`osd-wal-osd6`) |
| 2026-04-13 12:40:13 | osd.6 service started, backfill began |
| 2026-04-15 00:40:00 | 744 GiB filled (15.97%), 35.3 hours elapsed, avg 6.0 MiB/s |
| 2026-04-15 00:40:00 | Tuning applied (scrubs paused, backfill priority raised) |
| 2026-04-15 01:25:00 | 756 GiB filled (16.24%), rate still ~6 MiB/s — USB bus saturated |
| TBD (~2026-04-18) | osd.6 reaches ~2.2 TiB (~45%), backfill complete |

## Monitor Progress

```bash
ssh harlan 'DATA=$(ceph osd df 2>/dev/null | grep "^ *6 " | awk "{print \$7,\$8}"); \
  PCT=$(ceph osd df 2>/dev/null | grep "^ *6 " | awk "{print \$17}"); \
  RATE=$(ceph status 2>/dev/null | grep recovery | awk "{print \$2,\$3}"); \
  PGW=$(ceph pg dump 2>/dev/null | grep -c backfill_wait); \
  PGA=$(ceph pg dump 2>/dev/null | grep -c "backfilling[^_]"); \
  echo "osd.6: ${DATA} (${PCT}%) / ~2.2 TiB target | recovery: ${RATE} | PGs: ${PGA} active, ${PGW} waiting"'
```

## Revised ETA

| Metric | Value |
|--------|-------|
| Created | 2026-04-13 12:40 EDT |
| Current (2026-04-15 01:25) | 756 GiB (16.24%) |
| Elapsed | 36.8 hours |
| Sustained avg rate | ~6.0 MiB/s |
| Remaining | ~1,444 GiB |
| Est. remaining | ~68 hours (2.9 days) |
| Est. total | ~105 hours (4.4 days) |

The rate did not improve after tuning. The USB controller sharing is the wall.

## Revert Commands (RUN AFTER BACKFILL COMPLETES)

Concurrency already reverted to defaults. Only scrub flags and priority remain:

```bash
# Step 1: Remove scrub pause flags
ceph osd unset noscrub
ceph osd unset nodeep-scrub

# Step 2: Revert recovery priority (persistent — must explicitly reset)
ceph config set osd osd_recovery_op_priority 15

# Step 3: Verify
ceph config show osd.6 | grep -E "max_backfill|recovery_max_active|recovery_op_priority"
ceph osd dump | grep flags
# Should show: sortbitwise,recovery_deletes,purged_snapdirs,pglog_hardlimit
# Should NOT show: noscrub, nodeep-scrub
```

## Notes

- The `ceph config set osd osd_recovery_op_priority 30` is persistent and MUST
  be explicitly reverted. Concurrency settings were already reverted to defaults.
- After reverting, the 577-PG scrub backlog will start catching up. This will
  temporarily increase disk I/O on all OSDs. Expect HEALTH_WARN for scrub
  backlog to persist for several days as scrubs work through the queue.
- If client I/O becomes noticeably slow before backfill completes, reduce
  priority back: `ceph config set osd osd_recovery_op_priority 15`

## Post-Backfill TODO

- [ ] Revert scrub flags and recovery priority (commands above)
- [ ] Re-run the matched quell (WAL) vs edgar (DB) comparison after edgar's load normalizes — the 2026-04-15 test had edgar under elevated stress (mon out of quorum, backfill source duties) which likely skewed osd.4's small I/O result (1,207 IOPS vs 3,760 for osd.1). A clean retest with edgar at idle will give definitive numbers.
- [ ] Collect a fresh `ceph daemon osd.X perf dump` on all 15 OSDs after counters have accumulated for at least a week of normal operation
- [ ] Consider running the scrub timing comparison (Script 2 in the article) once the 577-PG scrub backlog clears
