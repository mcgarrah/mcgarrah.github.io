# Baseline — Article Review

**Measured:** 2026-09-02 by `.article-review/audit.py`
**Raw data:** `.article-review/audit.json`
**Plan:** `../KIRO-CLAUDE-OPUS5-MAX-ARTICLE-REVIEW.md`

This is the frozen starting point. Everything the plan claims is measured here. Re-run
`python3 .article-review/audit.py` to detect drift; do not trust these numbers if the
current date is more than two weeks past the measurement date above.

---

## Inventory

| Metric | Value |
|--------|-------|
| Published posts | 190 |
| Article drafts | 68 |
| Tracker files in `_drafts/` | 17 |
| Published words | 220,846 |
| Draft words | 92,848 |

## Release buffer — the critical metric

| Metric | Value |
|--------|-------|
| Future-dated posts in `_posts/` | **0** |
| Buffer health | 🔴 **EMPTY** |
| Last published | 2026-08-21 |
| Days since last publish | **12** |

Production builds run without `--future`, so future-dated posts are the publishing queue that
the daily cron (10:05 UTC, `.github/workflows/jekyll.yml`) drains automatically. A buffer of
zero means nothing will publish until someone manually promotes a draft. This is the immediate
cause of the current 12-day gap.

## Front matter

| Cohort | n | Missing |
|--------|---|---------|
| Modern posts (2023+) | 131 | `tags` 1, `categories` 2 |
| Legacy posts (<2023) | 59 | `description` 59, `image` 59, `tags` 50, `last_modified_at` 35, `categories` 7 |
| Drafts | 68 | `image` 49 |

Modern posts are effectively clean. `TODO.md`'s claim of "122 of 173 posts missing description"
refers to a state that no longer exists — the remaining gap is entirely the 59 legacy posts
(2001–2016), which `scripts/lint-frontmatter.py` correctly treats as warn-only.

Drafts have **zero** gaps in `description` / `tags` / `categories` / `last_modified_at`
(filled by commit `3f51c81`). This is why front matter no longer distinguishes a ready draft
from a stub.

## Readiness

| Value | Count |
|-------|-------|
| unset | 68 |

No draft carries a `readiness:` marker. Phase 6 introduces this field; until then, disposition
lives only in `DRAFTS.md` prose.

## Size distribution

| | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| Drafts | 20 | 423 | 1,233 | 1,754 | 8,364 |
| Posts | 19 | 329 | 1,019 | 1,698 | 6,306 |

- **21 drafts under 600 words** — stubs sharing a directory with finished work
- **2 drafts over 4,000 words** — `2026-08-12-proxmox-8-to-9-cluster-upgrade-part-3.md` (8,364)
  and `2026-08-09-proxmox-8-to-9-cluster-upgrade-part-2.md` (4,088)

Published p75 of 1,698 is the practical target band.

## 2026 cadence

| Month | Posts |
|-------|-------|
| Jan | 2 |
| Feb | 3 |
| Mar | 1 |
| Apr | 22 |
| May | 22 |
| Jun | 7 |
| Jul | 4 |
| Aug | 10 |
| Sep | 0 |

Day-of-week: Wed 15, Mon 13, Tue 12, Fri 10, Thu 9, Sat 9, Sun 3.

`SCHEDULED.md` declares "once per week, Monday." July ran entirely on Tuesdays; August ran
Mon/Wed/Fri. The declared cadence has never been the operating cadence.

## Tracker drift

**12 drafts are absent from both `DRAFTS.md` and `SCHEDULED.md`:**

- `2026-06-15-run-jekyll-vscode-marketplace-publisher-setup.md`
- `2026-06-19-run-jekyll-bug-fixes-and-code-review.md`
- `2026-06-24-run-jekyll-testing-and-test-harness.md`
- `2026-06-29-run-jekyll-new-features-clean-doctor-tests.md`
- `2026-08-05-proxmox-8-to-9-cluster-upgrade-part-1.md`
- `2026-08-12-proxmox-8-to-9-cluster-upgrade-part-3.md`
- `2026-08-15-proxmox-8-to-9-cluster-upgrade-part-4.md`
- `2026-08-16-proxmox-8-to-9-cluster-upgrade-part-5.md`
- `2026-08-17-claude-code-tmux-persistence-proxmox-ha.md`
- `2026-08-26-claude-code-persistent-plain-shell-windows.md`
- `2026-08-28-idempotent-workspace-provisioner-agent-lxc.md`
- `2026-08-29-cephfs-gapfill-throttle-tuning.md`

A 13th, `2026-06-10-forking-jekyll-run-to-run-jekyll.md`, is absent from `DRAFTS.md` but does
appear in `SCHEDULED.md` — so **13 drafts are invisible to `DRAFTS.md`**, which is the file
where promotion decisions actually get made.

`DRAFTS.md`'s own summary table says "Drafts in `_drafts/`: 56". Actual: 68.

---

## What the baseline says

Three things, in order of urgency:

1. **The buffer is empty and the cron has nothing to publish.** This is a one-session fix
   (Phase 5) and it stops the bleeding.
2. **The largest and newest body of work — the 5-part Proxmox 8→9 series, the 4-article Run
   Jekyll cluster, and all four August drafts — is invisible to the publication tracker.**
   Roughly 30,000 words of it. Not blocked, not rejected: unlisted.
3. **Front matter passes on everything, so it signals nothing.** Readiness needs its own marker
   (Phase 6) or the triage in Phase 2 will decay the same way `DRAFTS.md` did.

---

## Amendment — 2026-10-30 re-audit

Re-measured with `python3 .article-review/audit.py` after pulling `origin/main`. The 2026-09-02
numbers above are left as the frozen baseline; this section records drift since.

| Metric | 2026-09-02 | 2026-10-30 | Change |
|--------|-----------:|-----------:|-------:|
| Published posts | 190 | 191 | +1 |
| Article drafts | 68 | 71 | +3 |
| Published words | 220,846 | 221,457 | +611 |
| Draft words | 92,848 | 98,041 | +5,193 |
| Future-dated buffer | 0 | 0 | none |
| Last published | 2026-08-21 | 2026-09-14 | |
| Days since last publish | 12 | 46 | +34 |
| Drafts absent from trackers | 12 | 15 | +3 |
| Modern posts (2023+) | 131 | 132 | +1 |
| Drafts missing `image` | 49 | 50 | +1 |
| Drafts missing `last_modified_at` | 0 | 1 | +1 |
| Drafts with `readiness:` set | 0 | 0 | none |

Cadence: September now shows 1 post (the Google Fiber to Google Voice landline article,
2026-09-14); nothing has published since. Monthly counts for Jan-Aug are unchanged.

What changed in the diagnosis:

1. **The buffer is still empty and the gap has grown from 12 to 46 days.** The urgent finding is
   unchanged and worse. Phase 5 is still the fix.
2. **Phases 1-6 and 8 have not started.** Only Phase 0 is done and Phase 7 is partly done
   (`INTAKE.md`). Tracker drift is growing, not shrinking: 3 more drafts are untracked.
3. **New drafts since baseline** include the Ceph SAN network bottleneck / node upgrade article,
   the PVE node diagnostic tooling baseline, the GPU upgrade decision article, and the two
   ct:603 session-persistence posts. None carry a `readiness:` marker.
4. Remaining size, stub (21 under 600 words) and legacy front-matter figures are unchanged.


---

## Amendment — 2026-11-24 re-audit

Full table and analysis are in `Amendment 2` of `../KIRO-CLAUDE-OPUS5-MAX-ARTICLE-REVIEW.md`.

| Metric | 2026-10-30 | 2026-11-24 |
|--------|-----------:|-----------:|
| Published posts | 191 | 191 |
| Article drafts | 71 | 84 |
| Draft words | 98,041 | 131,432 |
| Future-dated buffer | 0 | 0 |
| Days since last publish | 46 | 71 |
| Drafts absent from trackers | 15 | 28 |
| Drafts over 4,000 words | 2 | 3 |
| Drafts missing `image` | 50 | 60 |
