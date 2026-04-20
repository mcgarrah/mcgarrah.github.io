---
layout: post
title: "Repository Cleanup Part 2: Audit Methodology & What I Will Evaluate Next"
categories: [git, github, jekyll, infrastructure]
tags: [git-history, repository-size, git-audit, performance, maintenance]
excerpt: "Part 2 of a repository cleanup series. Before applying the same history-rewrite approach elsewhere, I audited my other major repositories to decide what is worth fixing next. Here is the audit method, the current findings, and why mcgarrah.github.io is the only likely follow-on candidate if drafts.mcgarrah.org goes well."
date: 2026-07-09
last_modified_at: 2026-07-09
series: "Repository Cleanup"
series_part: 2
---

**Part 2**: Systematic audit methodology and findings across `mcgarrah.github.io`, `resume`, `k8s-proxmox`, and `jekyll-run`. [Part 1]({{ site.baseurl }}{% post_url 2026-07-08-git-history-bloat-drafts-repo-cleanup %}) covers the drafts repository problem and the cleanup plan I intend to validate first.

I am not treating this as a blanket campaign to rewrite history across every repository I own. The point of this pass was to measure first, then narrow the next likely candidate if the `drafts.mcgarrah.org` cleanup goes smoothly. This post documents the screening approach, the current findings, and why `mcgarrah.github.io` is the only repository that currently looks worth evaluating for the same treatment.

<!-- excerpt-end -->

## Audit Methodology

The goal: Quickly screen all repositories for signs of bloat, identify root causes, and decide which ones need cleanup.

## Command Compatibility (macOS vs WSL2/Linux)

The examples in this article are shell-oriented and work on both macOS and Linux/WSL2, but there are a few portability gotchas worth calling out.

### Baseline Requirements

Install these first:

- `git`
- `awk`
- `sort`
- `xargs`
- `du`

On Ubuntu/WSL2, these are typically available in core packages. On macOS, they are present by default, with BSD variants for some tools.

### Quick Compatibility Notes

- `du -sh` works on both macOS and Linux.
- `du -k` works on both and is used here for consistent KB output.
- Avoid `du -b` on macOS (GNU-only).
- `sort -rn` works on both.
- `xargs -0` works on both (used with `git ls-files -z`).
- `head -20` works on both.

### Step 1: Size Overview (Portable)

macOS and WSL2/Linux:

```bash
for repo in mcgarrah.github.io resume k8s-proxmox jekyll-run; do
  cd "$repo"
  total_size=$(du -sh . | awk '{print $1}')
  git_size=$(du -sh .git | awk '{print $1}')
  echo "$repo: Total=$total_size, .git=$git_size"
  cd - >/dev/null
done
```

### Step 3: Largest Files in HEAD (Portable)

macOS and WSL2/Linux:

```bash
git ls-files -z \
| xargs -0 du -k \
| sort -rn \
| head -20
```

### Step 4: Largest Historical Blobs (Portable)

macOS and WSL2/Linux:

```bash
git rev-list --all --objects \
| git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
| awk '$1=="blob"{print $3"\t"$4}' \
| sort -nr \
| head -20
```

### If You Need Strict Byte Counts

For Linux/WSL2 (GNU coreutils), `du -b` is available. On macOS, use `stat` instead.

Linux/WSL2:

```bash
du -b path/to/file
```

macOS:

```bash
stat -f%z path/to/file
```

If you keep your article examples at the KB/MB level (`du -k`, `du -sh`), you can avoid most GNU vs BSD differences entirely.

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

### 1. `drafts.mcgarrah.org` — 🛠️ Cleanup Candidate Being Validated

**Metrics:**
```
Total:       479 MB
.git:        384 MB (80%)
Objects:     506 loose + 5,894 packed
```

**Root Cause:** 231 MB of old executable files in history.

**Planned Action:** History rewrite if the execution and verification steps in Part 1 behave as expected.

**Target Outcome:**
```
Total:       152 MB (68% reduction)
.git:        151 MB
Objects:     5,368 packed
```

---

### 2. `mcgarrah.github.io` — ⚠️ Next Repository To Evaluate If Part 1 Goes Well

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

**Recommendation:** If the `drafts.mcgarrah.org` cleanup goes well, this is the next repository worth evaluating. First decide whether `assets/exes/` still serves a purpose or is just legacy from older hosting.

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

**Verdict:** Healthy repository. All large files are legitimate (resume PDF, Font Awesome assets). No cleanup work planned here.

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

**Recommendation:** No cleanup work planned here.

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

**Recommendation:** No cleanup work planned here. If I automate checks later, this repo can be part of periodic reporting, but it is not a candidate for intervention.

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
| `drafts.mcgarrah.org` | 🛠️ Validate cleanup plan | 1–2 hrs | First |
| `mcgarrah.github.io` | ⚠️ Candidate | 1–2 hrs | Second, only if Part 1 goes well |
| `resume` | ✅ Healthy | — | No action planned |
| `k8s-proxmox` | ℹ️ Monitored | — | No action planned |
| `jekyll-run` | ✅ Healthy | — | No action planned |

## What I Am Actually Doing Next

1. **Validate Part 1 on `drafts.mcgarrah.org` first.** If the rewrite, push, and re-clone all behave cleanly, then I have a proven process instead of a theoretical one.
2. **Re-evaluate `mcgarrah.github.io` after that.** It is the only repository from this audit that looks like a realistic follow-on candidate.
3. **Leave periodic checks for later.** A GitHub Action that reports `.git` size, object counts, and oversized tracked files is a good future improvement, but it is not the immediate next step. That can live in a later follow-up article or a Part 3.

---

## Future Follow-Up

If this turns into an ongoing maintenance habit, the next useful increment is automation rather than more one-off archaeology.

A future Part 3 could cover:

- A GitHub Action that records `git count-objects -v`, largest tracked files, and repository size trends
- Threshold-based alerts when large binaries get committed
- A lightweight reporting job that helps catch drift before clone performance becomes annoying again

For now, that is future work. The immediate decision tree is much smaller: validate the cleanup once on `drafts.mcgarrah.org`, then decide whether `mcgarrah.github.io` deserves the same treatment.

## Key Lessons

1. **`.git` ratio is your first indicator**: If `.git` > 50% of total, history cleanup is likely worth considering.
2. **Not all bloat is in history**: `jekyll-run`'s 887 MB looks scary, but only 3.4 MB is git history. The rest is dev tooling (expected and fine).
3. **Repository cleanup has a scale threshold**: Cleaning a 3.8 MB repo is never worth the effort, even if the ratio is high.
4. **Current content matters**: If large files are legitimately in `HEAD`, history rewrite won't help unless you also remove them from current commits.
5. **Well-packed objects are efficient**: `drafts.mcgarrah.org` was already aggressively repacked (305 MB pack), so only content removal could reduce size further.
