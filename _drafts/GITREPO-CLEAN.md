---
layout: none
date: 1999-12-31
sitemap: false
---

# Git Repository Cleanup & Performance Audit — Project Tracker

Systematic audit and cleanup of personal repository bloat. Series documents methodology for identifying historical binary blobs, safe execution of git history rewrites, and findings across mcgarrah.github.io and related projects.

Last updated: 2026-04-20

---

## Repositories Under Review

| Repo | Total Size | .git | Ratio | Status |
|------|-----------|------|-------|--------|
| `drafts.mcgarrah.org` | 479 MB | 384 MB | 80% | ✅ Part 1: Cleanup complete |
| `mcgarrah.github.io` | 934 MB | 301 MB | 32% | ⚠️ Candidate for cleanup |
| `resume` | 27 MB | 7.3 MB | 27% | ✅ Healthy (no action) |
| `k8s-proxmox` | 3.8 MB | 2.6 MB | 68% | ℹ️ False alarm (too small) |
| `jekyll-run` | 887 MB | 3.4 MB | 0.4% | ✅ Excellent (dev artifacts, not history) |

---

## Article Sequence

### Part 1: Git History Bloat — Drafts Repository Cleanup (2026-07-08)

**Status:** Draft  
**Focus:** Concrete walkthrough of drafts.mcgarrah.org cleanup  
**Includes:**
- Symptoms and root cause (231 MB of historical exe files)
- Options evaluated (do nothing, shallow clone, history rewrite)
- Safe execution plan with step-by-step commands
- Console output from actual execution
- Metrics: before/after clone and pack sizes
- Rollback strategy and team communication

**Key Outputs:**
```
Before cleanup:
- Total: 479 MB
- .git: 384 MB (80% of clone)
- Largest blobs: FirefoxPortable (95.7 MB + 95.6 MB), jPortable (40.1 MB)

After cleanup:
- Total: ~220 MB (estimated)
- .git: ~150 MB (estimated)
- Clone time: ~50% reduction
```

---

### Part 2: Repository Audit Methodology & Multi-Repo Findings (2026-07-09)

**Status:** Draft  
**Focus:** Methodology for discovering which repos need cleanup, findings across all 5 repos  
**Includes:**
- Audit commands (git count-objects, du -sh, git ls-files)
- Quick screening (total size, .git ratio, object count)
- Deep inspection for root cause (executable files, large blobs, history)
- Findings for each repo:
  - `mcgarrah.github.io`: NEEDS CLEANUP (220 MB from active exe files)
  - `resume`: Healthy (legitimate assets, no bloat)
  - `k8s-proxmox`: False alarm (68% ratio, but only 3.8 MB total)
  - `jekyll-run`: Excellent (dev artifacts in working tree, not history)
- Decision matrix: when to cleanup vs when to ignore
- Console output from all audits

**Key Recommendations:**
- ✅ `mcgarrah.github.io`: Apply Part 1 approach (remove exe files or rewrite history)
- ✅ `drafts.mcgarrah.org`: Execute Part 1 plan
- ℹ️ Others: No action needed (already healthy or too small to matter)

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

- [ ] Document safe execution steps with real commands
- [ ] Test git filter-repo commands in mirror (drafts.mcgarrah.org)
- [ ] Execute rewrite and force-push
- [ ] Verify new clone size and metrics
- [ ] Document actual before/after numbers in article
- [ ] Publish Part 1

### Phase 3: Part 2 Article & Decision

- [ ] Document audit methodology with command explanations
- [ ] Publish Part 2 with recommendations for each repo
- [ ] Decide: Cleanup mcgarrah.github.io or leave exe files as-is?

### Phase 4: Optional Cleanup of mcgarrah.github.io (if decided)

- [ ] Determine if exe files are still needed
- [ ] If removing: apply same git filter-repo approach from Part 1
- [ ] If keeping: document why and dismiss this cleanup task

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
| Should `mcgarrah.github.io` exe files stay? | TBD | If no: saves 220 MB; if yes: skip cleanup |
| Should `drafts.mcgarrah.org` cleanup be public or quiet? | TBD | Affects communication + PR metadata |
| Should `k8s-proxmox` get a `git gc` cleanup (purely aesthetic)? | No | Repo too small to justify |
| Should `resume` and `jekyll-run` be monitored? | Yes (monitor) | Baseline set for future audits |

---

## Status Summary

- **Part 1 draft:** Ready for execution and console output documentation
- **Part 2 draft:** Findings complete, awaiting write-up
- **mcgarrah.github.io decision:** Pending (exe files: needed or removable?)
- **Overall:** Audit complete; cleanup ready to execute; articles awaiting completion
