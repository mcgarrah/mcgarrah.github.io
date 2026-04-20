---
layout: none
date: 1999-12-31
sitemap: false
---

# Git Repository Cleanup & Performance Audit — Project Tracker

Systematic audit and cleanup of personal repository bloat. Series documents methodology for identifying historical binary blobs, safe execution of git history rewrites, findings across related repositories, and a future automation path for git-health monitoring.

Last updated: 2026-04-20

---

## Repositories Under Review

| Repo | Total Size | .git | Ratio | Status |
|------|-----------|------|-------|--------|
| `drafts.mcgarrah.org` | 479 MB | 384 MB | 80% | 🛠️ Part 1 validation in progress |
| `mcgarrah.github.io` | 934 MB | 301 MB | 32% | ⚠️ Evaluate after Part 1 |
| `resume` | 27 MB | 7.3 MB | 27% | ✅ Healthy (no action) |
| `k8s-proxmox` | 3.8 MB | 2.6 MB | 68% | ℹ️ False alarm (too small) |
| `jekyll-run` | 887 MB | 3.4 MB | 0.4% | ✅ Excellent (dev artifacts, not history) |

---

## Article Sequence

### Part 1: Git History Bloat — Drafts Repository Cleanup (2026-07-08)

**Status:** Draft  
**Focus:** Concrete walkthrough of the drafts.mcgarrah.org problem and cleanup plan  
**Includes:**
- Symptoms and root cause (231 MB of historical exe files)
- Options evaluated (do nothing, shallow clone, history rewrite)
- Safe execution plan with step-by-step commands
- Console output from actual execution
- Metrics: before/after clone and pack sizes
- Rollback strategy and team communication
- Personal motivation: why a brand new drafts repo feeling chunky was enough to investigate

**Key Outputs:**
```
Before cleanup:
- Total: 479 MB
- .git: 384 MB (80% of clone)
- Largest blobs: FirefoxPortable (95.7 MB + 95.6 MB), jPortable (40.1 MB)

Target after cleanup:
- Total: ~220 MB (estimated)
- .git: ~150 MB (estimated)
- Clone time: ~50% reduction
```

---

### Part 2: Repository Audit Methodology & Multi-Repo Findings (2026-07-09)

**Status:** Draft  
**Focus:** Methodology for deciding what to evaluate next after validating Part 1  
**Includes:**
- Audit commands (git count-objects, du -sh, git ls-files)
- Quick screening (total size, .git ratio, object count)
- Deep inspection for root cause (executable files, large blobs, history)
- Findings for each repo:
  - `mcgarrah.github.io`: likely next candidate if Part 1 goes well
  - `resume`: healthy, no action planned
  - `k8s-proxmox`: false alarm (68% ratio, but only 3.8 MB total)
  - `jekyll-run`: excellent (dev artifacts in working tree, not history)
- Decision matrix: when to cleanup vs when to ignore
- Console output from all audits
- Future idea: GitHub Action for periodic git-health reporting, likely better as a Part 3

**Key Recommendations:**
- 🛠️ `drafts.mcgarrah.org`: validate Part 1 plan first
- ⚠️ `mcgarrah.github.io`: evaluate next only if Part 1 goes well
- ℹ️ Others: no action needed right now

---

### Part 3: Git Health Monitoring with GitHub Actions (Outline) (2026-07-24)

**Status:** Outline only  
**Focus:** Future automation after Parts 1 and 2 are validated with real results  
**Includes:**
- Why automation belongs after manual cleanup, not before it
- Candidate git-health metrics and thresholds
- Scheduled, push, PR, and manual workflow options
- Reporting options for GitHub Actions summaries and warnings
- Repo-specific policy differences
- A phased rollout approach that starts with reporting before enforcement

**Current Decision:**
- Not immediate work
- Keep as a future follow-up after Part 2 is finalized or revised
- Good candidate for a later article once the manual process is proven

---

## Execution Phases

### Phase 1: Baseline & Audit (Complete)

- [x] `drafts.mcgarrah.org`: Size audit complete (479 MB → 384 MB .git)
- [x] `mcgarrah.github.io`: Size audit complete (934 MB → 301 MB .git)
- [x] `resume`: Size audit complete (27 MB → 7.3 MB .git)
- [x] `k8s-proxmox`: Size audit complete (3.8 MB → 2.6 MB .git)
- [x] `jekyll-run`: Size audit complete (887 MB → 3.4 MB .git)
- [x] Root cause identified for each repo

### Phase 2: Part 1 Article & Execution

- [x] Document safe execution steps with real commands
- [ ] Test git filter-repo commands in mirror (drafts.mcgarrah.org)
- [ ] Execute rewrite and force-push
- [ ] Verify new clone size and metrics
- [ ] Replace target metrics with actual post-cleanup numbers in article
- [ ] Publish Part 1

### Phase 3: Part 2 Article & Decision

- [x] Document audit methodology with command explanations
- [ ] Publish Part 2 with staged recommendations
- [ ] Decide: if Part 1 goes well, should `mcgarrah.github.io` get the same treatment?

### Phase 4: Optional Cleanup of mcgarrah.github.io (if decided)

- [ ] Determine if exe files are still needed
- [ ] If removing: apply same git filter-repo approach from Part 1
- [ ] If keeping: document why and dismiss this cleanup task

### Phase 5: Future Automation (Part 3)

- [x] Create Part 3 outline draft
- [ ] Revisit after Part 2 is finalized with real cleanup outcomes
- [ ] Decide whether GitHub Actions reporting is worth the maintenance cost
- [ ] If yes: implement a lightweight git-health workflow and document it

---

## Commands Reference

### Audit Commands (Part 2)

```bash
# Size overview
du -sh . && du -sh .git

# Object count
git count-objects -v

# Largest current files in HEAD
git ls-files -z | xargs -0 du -k | sort -rn | head -20

# Find large historical objects (expensive)
git rev-list --all --objects | sed 's/ /\t/' | sort -t$'\t' -k2 -rn | head -20
```

### Cleanup Commands (Part 1)

```bash
# Create backup and mirror
git clone --mirror <url> <repo>.mirror
cd <repo>.mirror

# Rewrite history (remove large blobs and paths)
git filter-repo --invert-paths --paths-from-deletions <file-list>

# Or remove specific paths
git filter-repo --invert-paths --path assets/exes/

# Force-push rewritten history
git push origin +main  # or +master

# Re-clone to verify
git clone <url> <repo>-fresh
```

---

## Decision Points

| Question | Answer | Impact |
|----------|--------|--------|
| Should `mcgarrah.github.io` exe files stay? | TBD after Part 1 | If no: saves 220 MB; if yes: skip cleanup |
| Should `drafts.mcgarrah.org` cleanup be public or quiet? | TBD | Affects communication + PR metadata |
| Should `k8s-proxmox` get a `git gc` cleanup (purely aesthetic)? | No | Repo too small to justify |
| Should `resume` and `jekyll-run` be monitored? | Later, periodically | Baseline set for future audits |
| Should git-health automation be added? | Maybe, future Part 3 | Good candidate for a GitHub Action once manual cleanup path is proven |
| Should Part 3 stay report-only at first? | Probably | Safer way to learn signal quality before enforcing thresholds |

---

## Status Summary

- **Part 1 draft:** Ready for validation run and replacement of target metrics with actual results
- **Part 2 draft:** Reframed around staged evaluation and future follow-up
- **mcgarrah.github.io decision:** Deferred until Part 1 proves out cleanly
- **Part 3 outline:** Created and parked for later implementation
- **Overall:** Audit complete; immediate focus is one successful cleanup, not a broad rewrite campaign or early automation push
