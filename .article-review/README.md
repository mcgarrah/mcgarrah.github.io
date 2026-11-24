# `.article-review/`

Working directory for the article review and release-schedule project described in
[`../KIRO-CLAUDE-OPUS5-MAX-ARTICLE-REVIEW.md`](../KIRO-CLAUDE-OPUS5-MAX-ARTICLE-REVIEW.md).

Dot-prefixed so Jekyll excludes it from builds — nothing here is published.

## Start here

| File | Purpose |
|------|---------|
| `STATE.yaml` | **Read this first when resuming.** Per-phase status, last completed step, count snapshot. |
| `BASELINE.md` | Frozen measurements from 2026-09-02. What the plan's claims are based on. |
| `audit.py` | Re-measures everything. Run it before trusting any number in the plan. |
| `audit.json` | Raw audit output, including per-file rows. |

## Usage

```bash
python3 .article-review/audit.py              # summary + refresh audit.json
python3 .article-review/audit.py --inventory  # markdown table of all drafts
python3 .article-review/audit.py --buffer     # buffer count only (for scripts)
python3 .article-review/audit.py --json       # machine-readable summary
```

## Why this directory exists

The plan's core diagnosis is that the publication trackers drifted away from what's actually on
disk — `DRAFTS.md` undercounting drafts by 12, `SCHEDULED.md` frozen three months back,
`TODO.md` describing an already-solved problem.

A plan to fix tracker drift is itself a tracker. `audit.py` is the mitigation: every number in
the plan is reproducible from the filesystem in one command, so disagreement is detectable
rather than invisible.

If `STATE.yaml` and `audit.py` disagree, **the filesystem wins.**

## Artifacts added as phases complete

- Phase 1 → `INVENTORY.md`, `PHASE1-CHANGES.md`
- Phase 2 → `TRIAGE-BATCHES.md`, `triage/BATCH-01..07.md`, `QUEUE.md`
- Phase 3 → `PHASE3-DISPOSITIONS.md`
- Phase 4 → `VERIFICATION-LOG.md`, `G-GATE-RESULTS.md`
- Phase 5 → `PHASE5-PROMOTIONS.md`
- Phase 6 → `PHASE6-TOOLING.md`
- Phase 7 → `INTAKE.md`
- Phase 8 → `PHASE8-LEGACY.md`, `PHASE8-SVP.md`

Append to these; don't rewrite them. Corrections go in a dated amendment section.
