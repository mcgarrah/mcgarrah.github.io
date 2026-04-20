---
layout: post
title: "Repository Cleanup Part 2: Audit Methodology & Multi-Repo Findings"
categories: [git, github, jekyll, infrastructure]
tags: [git-history, repository-size, git-audit, performance, maintenance]
excerpt: "Part 2 of a two-part series on repository bloat. After cleaning up drafts.mcgarrah.org, I audited my other major repositories using the same methodology. Not all need cleanup. Here's the audit approach, commands, and decision matrix for determining which repositories are worth fixing."
date: 2026-07-09
last_modified_at: 2026-07-09
series: "Repository Cleanup"
series_part: 2
---

**Part 2 of 2**: Systematic audit methodology and findings across `mcgarrah.github.io`, `resume`, `k8s-proxmox`, and `jekyll-run` repositories. [Part 1]({{ site.baseurl }}{% post_url 2026-07-08-git-history-bloat-drafts-repo-cleanup %}) covered the detailed cleanup of `drafts.mcgarrah.org`.

After successfully cleaning up `drafts.mcgarrah.org`, I applied the same audit methodology to my other major repositories. This post documents the screening approach, audit commands, findings for each repo, and a decision matrix for determining what's worth cleaning up versus what's already healthy.

<!-- excerpt-end -->

## Audit Methodology

The goal: Quickly screen all repositories for signs of bloat, identify root causes, and decide which ones need cleanup.

### Step 1: Size Overview (< 30 seconds)

Start with the highest-level metrics to identify candidates:

```bash
$ for repo in mcgarrah.github.io resume k8s-proxmox jekyll-run; do
  cd $repo
  total_size=$(du -sh . | cut -f1)
  git_size=$(du -sh .git | cut -f1)
  echo "$repo: Total=$total_size, .git=$git_size"
done
```

**What to look for:**
- `.git` size > 30% of total → candidate for cleanup
- `.git` size < 20% → likely healthy (bloat is in working tree, not history)
- Total repo size > 500 MB → investigate further

### Step 2: Object Count Analysis (< 1 second)

Get detailed packing efficiency:

```bash
$ git count-objects -v
```

**What to look for:**
- `in-pack: 0` → Objects are loose, not packed (repack helps)
- `in-pack: >1000` → Well-packed (aggressive repack unlikely to help much)
- `size-pack` vs `size` ratio → If pack is only slightly smaller than loose, history is already optimized

### Step 3: Current Working Tree Inspection (< 1 minute)

Find the largest files in `HEAD`:

```bash
$ git ls-files -z | xargs -0 du -k | sort -rn | head -20
```

**What to look for:**
- Large media files (1–50 MB each) → legitimate content
- Large binaries still in HEAD → May need removal
- Total of all large files < 30 MB → Healthy for a dev project

### Step 4: Deep History Inspection (1–5 minutes, if needed)

Only run if Step 1–3 suggest significant bloat:

```bash
$ git rev-list --all --objects \
| git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
| awk '$1=="blob"{print $3"\t"$4}' \
| sort -nr | head -20
```

**What to look for:**
- Large blobs (> 10 MB) that **aren't** in current HEAD → Historical bloat, cleanup candidate
- Large blobs in HEAD → Legitimate (user must decide to keep or remove)

---

## Results: Five Repositories Audited

### 1. `drafts.mcgarrah.org` — ✅ Cleanup Complete

**Metrics:**
```
Total:       479 MB
.git:        384 MB (80%)
Objects:     506 loose + 5,894 packed
```

**Root Cause:** 231 MB of old executable files in history.

**Action Taken:** History rewrite (Part 1 of this series).

**Outcome:**
```
Total:       152 MB (68% reduction)
.git:        151 MB
Objects:     5,368 packed
```

---

### 2. `mcgarrah.github.io` — ⚠️ CANDIDATE FOR CLEANUP

**Metrics:**
```
Total:       934 MB
.git:        301 MB (32%)
Objects:     506 loose + 5,894 packed
```

**Full Audit Output:**

```bash
$ du -sh .
934M    .

$ du -sh .git
301M    .git

$ git count-objects -v
count: 506
size: 2764
in-pack: 5894
packs: 2
size-pack: 305477
```

**Current Working Tree (Largest Files):**

```bash
91.2 MB  | assets/exes/FirefoxPortable_51.0.1_English.paf.exe
91.2 MB  | assets/exes/FirefoxPortable_51.0_English.paf.exe
38.3 MB  | assets/exes/jPortable_8_Update_121.paf.exe
18.1 MB  | assets/images/proxmox-upgrade-video-003.png
5.9 MB   | assets/pdfs/2810-Install-May2006-59913843.pdf
3.0 MB   | _data/font-awesome/icons.json
(... 16 more files under 2 MB)
```

**Root Cause:** This repository has **THREE portable executables still in HEAD** that total 220.7 MB. The decision on cleanup depends on whether these files are still needed.

**Decision Point:**
- **If removing exe files:** Apply the same history rewrite from Part 1 → **saves ~280 MB** (220 MB current + ~60 MB historical versions)
- **If keeping exe files:** Clone will remain expensive regardless of git cleanup. These files are in HEAD, so every clone must pull them.

**Recommendation:** Decide whether `assets/exes/` directory serves a purpose or is legacy from old hosting.

---

### 3. `resume` — ✅ Healthy (No Action Needed)

**Metrics:**
```
Total:       27 MB
.git:        7.3 MB (27%)
Objects:     0 loose + 2,909 packed
```

**Audit Output:**

```bash
$ du -sh .
27M     .

$ du -sh .git
7.3M    .git

$ git count-objects -v
count: 0
size: 0
in-pack: 2909
packs: 1
size-pack: 7222
```

**Working Tree (Largest Files):**

```bash
2.3 MB   | assets/plugins/font-awesome/metadata/icons.json
1.2 MB   | assets/pdf/michael_mcgarrah_full_resume-2024-07-11.pdf
0.9 MB   | assets/plugins/font-awesome/js/all.js
0.9 MB   | assets/plugins/font-awesome/js/all.min.js
0.6 MB   | assets/plugins/font-awesome/webfonts/fa-brands-400.svg
(... all legitimate assets)
```

**Verdict:** Healthy repository. All large files are legitimate (resume PDF, Font Awesome assets). No cleanup needed. Monitor baseline: 27 MB total.

---

### 4. `k8s-proxmox` — ℹ️ False Alarm (No Action)

**Metrics:**
```
Total:       3.8 MB
.git:        2.6 MB (68% ratio)
Objects:     557 loose + 0 packed
```

**Audit Output:**

```bash
$ du -sh .
3.8M    .

$ du -sh .git
2.6M    .git

$ git count-objects -v
count: 557
size: 2512
in-pack: 0
packs: 0
size-pack: 0
```

**Working Tree (Largest Files):**

```bash
100 KB   | docs/SITE-TO-SITE-VPN.md
<100 KB  | (all other files)
```

**Verdict:** High `.git` ratio (68%), but the entire repository is only 3.8 MB. This is a **false alarm**. The ratio looks bad because objects have never been repacked into a pack file (0 in-pack). Running `git gc` would improve the ratio visually, but it's not worth the effort for a tiny repo with legitimate content.

**Recommendation:** Monitor only. No cleanup needed.

---

### 5. `jekyll-run` — ✅ Excellent (Development Project)

**Metrics:**
```
Total:       887 MB
.git:        3.4 MB (0.4%)
Objects:     231 loose + 493 packed
```

**Audit Output:**

```bash
$ du -sh .
887M    .

$ du -sh .git
3.4M    .git

$ git count-objects -v
count: 231
size: 2644
in-pack: 493
packs: 1
size-pack: 414
```

**Directory Breakdown:**

```bash
638 MB   | .vscode-test/  (test framework artifacts, not tracked)
244 MB   | node_modules/  (dev dependencies)
3.4 MB   | .git/          (clean history)
2 MB     | src/           (actual source code)
```

**Verdict:** Excellent git repository hygiene. The large total size (887 MB) comes from build/test artifacts and node dependencies in the working tree, **not from git history**. The `.git` directory is lean (3.4 MB) and efficiently packed (493 objects). No cleanup needed.

**Recommendation:** This is a model for how development projects should look. Continue monitoring.

---

## Decision Matrix

Use this matrix to quickly decide if a repository needs cleanup:

| Factor | Suggests Cleanup | Verdict |
|--------|------------------|---------|
| `.git` > 50% of total | Yes | Bloat likely in history |
| `.git` > 30% of total AND total > 200 MB | Maybe | Depends on content |
| Largest blob > 50 MB **not in HEAD** | Yes | Historical bloat |
| Largest blob > 50 MB **in HEAD** | Maybe | Only if you want to remove it |
| `.git` well-packed (high in-pack count) | No | History already optimized |
| Repository < 10 MB total | No | Not worth effort |
| All large files are current assets | No | Legitimate content |

---

## Summary & Recommendations

| Repository | Status | Effort | Priority |
|------------|--------|--------|----------|
| `drafts.mcgarrah.org` | ✅ Cleaned | Complete | Done |
| `mcgarrah.github.io` | ⚠️ Candidate | 1–2 hrs | Decide on exe files first |
| `resume` | ✅ Healthy | — | Monitor only |
| `k8s-proxmox` | ℹ️ Monitored | — | No action (too small) |
| `jekyll-run` | ✅ Healthy | — | Monitor only |

### What I'm Doing Next

1. **Decide on `mcgarrah.github.io` exe files:** Are they still serving a purpose? If no → apply Part 1 cleanup approach and save 280 MB.
2. **Monitor remaining repos:** Track baseline sizes to catch bloat early in future.
3. **Implement guardrails** (per Part 1):
   - CI check to fail PRs with files > 20 MB
   - Pre-commit hook for local warnings
   - Document binary asset policy

---

## Key Lessons

1. **`.git` ratio is your first indicator**: If `.git` > 50% of total, history cleanup is likely worth considering.
2. **Not all bloat is in history**: `jekyll-run`'s 887 MB looks scary, but only 3.4 MB is git history. The rest is dev tooling (expected and fine).
3. **Repository cleanup has a scale threshold**: Cleaning a 3.8 MB repo is never worth the effort, even if the ratio is high.
4. **Current content matters**: If large files are legitimately in `HEAD`, history rewrite won't help unless you also remove them from current commits.
5. **Well-packed objects are efficient**: `drafts.mcgarrah.org` was already aggressively repacked (305 MB pack), so only content removal could reduce size further.
