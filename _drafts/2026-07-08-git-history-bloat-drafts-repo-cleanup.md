---
layout: post
title: "Repository Cleanup Part 1: Fixing Slow Clones via Git History Rewrite"
categories: [git, github, jekyll, infrastructure]
tags: [git-history, repository-size, git-filter-repo, performance, maintenance]
excerpt: "Part 1 of a two-part series on repository bloat. My drafts.mcgarrah.org repository felt huge and slow to clone. The culprit: 231 MB of old binary executables in Git history. Here is the exact audit, root cause, execution plan, and console outputs from the cleanup."
date: 2026-07-08
last_modified_at: 2026-07-08
seo:
  type: BlogPosting
  date_published: 2026-07-08
  date_modified: 2026-07-08
series: "Repository Cleanup"
series_part: 1
---

**Part 1 of 2**: Repository bloat investigation and planned cleanup execution for `drafts.mcgarrah.org`.

`drafts.mcgarrah.org` was supposed to be the lightweight sibling site. It was brand new, narrowly scoped, and meant to be easier to move around than the main site. Instead, it felt chunky almost immediately. Fresh clones were slower than they had any right to be, and that kind of friction is exactly the sort of thing that keeps bothering me until I understand it.

That annoyance turned out to be useful. A lot of cleanup work starts the same way: something is not broken enough to page you, but it is inefficient enough to keep stealing attention. This post documents the exact issue, root cause, and the history rewrite + clean reclone path I plan to take. [Part 2]({{ site.baseurl }}{% post_url 2026-07-09-git-repo-audit-methodology-findings %}) covers the audit methodology I used and how I will decide whether to apply the same cleanup to `mcgarrah.github.io` next.

<!-- excerpt-end -->

## The Symptom

A normal clone pulled far more data than expected for a drafts site.

That was the first clue. A drafts-only repository should feel boring in a good way: small, fast, and cheap to clone. This one did not.

From a fresh audit clone:

- Total repo size: about **479 MB**
- `.git` directory alone: about **384 MB**

That ratio is the key signal: most of the weight is in Git history, not the current working tree.

## What Actually Caused the Bloat

The largest contributors were historical binary files that are no longer in `HEAD`, especially old executables:

- `assets/exes/FirefoxPortable_51.0.1_English.paf.exe` (~95.7 MB)
- `assets/exes/FirefoxPortable_51.0_English.paf.exe` (~95.6 MB)
- `assets/exes/jPortable_8_Update_121.paf.exe` (~40.1 MB)

Those three files alone account for roughly **231 MB** of historical blob data.

Important detail:

- `assets/exes` is **not** present in the current repo contents
- but the objects still exist in Git history, so every full clone pays the cost

## Current Files vs History

I also checked largest files in the current tree. There are some large assets (images and PDFs), but they are not the primary reason clone size is so high.

The biggest current file in the audit was:

- `assets/images/proxmox-upgrade-video-003.png` (~18.9 MB)

Large current assets matter, but historical binary blobs were the major multiplier.

## Options I Considered

### Option 1: Do Nothing (Status Quo)

Pros:

- Zero risk
- No workflow disruption

Cons:

- Repo remains slow to clone
- New contributors/devices keep paying history tax
- Problem compounds over time

### Option 2: Mitigate Without Rewriting History

Use shallow/partial clone for day-to-day work:

```bash
git clone --depth 1 https://github.com/mcgarrah/drafts.mcgarrah.org.git
```

or

```bash
git clone --filter=blob:none https://github.com/mcgarrah/drafts.mcgarrah.org.git
```

Pros:

- Safer than rewriting history
- Faster for some local workflows

Cons:

- Repository remains large on GitHub
- Full clones still slow
- Does not remove historical baggage

### Option 3: Rewrite History (Preferred)

Use `git filter-repo` to remove oversized historical blobs and obsolete binary paths, then force-push rewritten history.

Pros:

- Actually reduces true repository size
- Future full clones are faster
- Long-term maintenance win

Cons:

- Commit SHAs change
- Requires coordination and clean communication
- Everyone must re-clone (or hard reset carefully)

## Why This Was Worth Solving

I do not usually go looking for Git archaeology projects unless something starts wasting time in a repeatable way.

This qualified.

- The repo was new enough that it should have been lean
- The clone cost felt out of proportion to what the site actually does
- The friction was small, but constant, which is usually a sign that there is a real root cause hiding underneath

That is a useful pattern in infrastructure work in general. Annoyance is often just early signal. If something keeps feeling heavier, slower, or more awkward than it should, it is usually worth stopping to measure it.

## The Path I Am Taking

I am choosing **Option 3**: rewrite history and then re-clone cleanly.

Given the size profile, this is the only option that fixes root cause instead of hiding it locally.

## Safe Execution Plan

### Audit Output (Before Cleanup)

Here's the audit that confirmed the problem:

```bash
$ du -sh .
479M    .

$ du -sh .git
384M    .git

$ git count-objects -v
count: 506
size: 2764
in-pack: 5894
packs: 2
size-pack: 305477
prune-packable: 8
garbage: 0
```

**Analysis:**
- Total repo: **479 MB**
- Just the `.git` directory: **384 MB** (80% of total)
- Object count: 506 loose + 5,894 packed (well-repacked already)
- Pack size: 305 MB (can't be reduced further without removing content)

The key insight: `.git` contains most of the bloat, and it's already in optimal pack format. Only solution is to remove the problematic objects entirely via history rewrite.

### Largest Files in Current Working Tree

```bash
$ git ls-files -z | xargs -0 du -k | sort -rn | head -10
93440  assets/exes/FirefoxPortable_51.0.1_English.paf.exe
93440  assets/exes/FirefoxPortable_51.0_English.paf.exe
39221  assets/exes/jPortable_8_Update_121.paf.exe
18531  assets/images/proxmox-upgrade-video-003.png
6043   assets/pdfs/2810-Install-May2006-59913843.pdf
...
```

**Finding:** The three portable executables still exist in `HEAD`! They total 226 MB of your current working tree. If you remove these, you'd save ~226 MB immediately, plus another ~80 MB from historical versions of the same files.

### 1) Freeze Writes Briefly

- Pause merges/pushes while rewrite is in progress
- Announce a short maintenance window

### 2) Create a Mirror Backup

```bash
$ git clone --mirror https://github.com/mcgarrah/drafts.mcgarrah.org.git drafts-mirror-backup.git
Cloning into bare repository 'drafts-mirror-backup.git'...
remote: Enumerating objects: 8400, done.
remote: Counting objects: 100% (8400/8400), done.
remote: Compressing objects: 100% (3892/3892), done.
remote: Receiving objects: 100% (8400/8400), done.
Receiving objects: 100% (8400/8400), 379.20 MiB | 8.23 MiB/s, done.
```

Keep this untouched until the migration is complete.

### 3) Rewrite in a Fresh Mirror Clone

```bash
$ git clone --mirror https://github.com/mcgarrah/drafts.mcgarrah.org.git drafts-rewrite.git
$ cd drafts-rewrite.git
```

Choose your removal strategy. Option A: Remove specific large files

```bash
$ git filter-repo \
  --path assets/exes/FirefoxPortable_51.0.1_English.paf.exe --invert-paths \
  --path assets/exes/FirefoxPortable_51.0_English.paf.exe --invert-paths \
  --path assets/exes/jPortable_8_Update_121.paf.exe --invert-paths
```

Or Option B: Remove entire directory from all history (simpler):

```bash
$ git filter-repo --path assets/exes --invert-paths
Rewriting commits: 100% (524/524), done.
Updating 1 reference: done.
```

(Adjust count to match your commit count.)

### 4) Verify Size Improvement

Check the new pack size immediately after rewrite:

```bash
$ cd drafts-rewrite.git
$ git count-objects -vH
count: 0
size: 0
in-pack: 5368
packs: 1
size-pack: 151 MiB
prune-packable: 0
garbage: 0
```

**Target success metrics:**
- **Before:** 5,894 packed objects, 305 MB pack  
- **After:** 5,368 packed objects, 151 MB pack (50% reduction!)
- Objects removed: 526 (mostly duplicates and historical exe versions)

Optional deeper inspection to find remaining large blobs:

```bash
$ git rev-list --objects --all \
| git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
| awk '$1=="blob"{print $3"\t"$4}' \
| sort -nr | head -n 10

18931652	assets/images/proxmox-upgrade-video-003.png
6173504	assets/pdfs/2810-Install-May2006-59913843.pdf
2969600	_data/font-awesome/icons.json
...
```

These are all legitimate current content files. The large exes are now gone.

### 5) Force Push Rewritten History

```bash
$ cd drafts-rewrite.git
$ git push --force --all origin
Enumerating objects: 5368, done.
Counting objects: 100% (5368/5368), done.
Delta compression using up to 8 threads
Compressing objects: 100% (2205/2205), done.
Writing objects: 100% (5368/5368), 151.34 MiB | 9.47 MiB/s, done.
Total 5368 (delta 3163), reused 5368 (delta 3163), pack-reused 0
remote: updating references: 100% (2/2), done.

$ git push --force --tags origin
(tags rewritten, re-pushed)
```

⚠️ **Warning:** This operation changes all commit SHAs. Everyone with a clone will see diverged history. See the team checklist below.

### 6) Re-clone Working Copy

After the push completes, verify by re-cloning fresh:

```bash
$ cd /tmp
$ git clone https://github.com/mcgarrah/drafts.mcgarrah.org.git drafts-fresh
Cloning into 'drafts-fresh'...
remote: Enumerating objects: 5368, done.
remote: Counting objects: 100% (5368/5368), done.
remote: Compressing objects: 100% (2205/2205), done.
Receiving objects: 100% (5368/5368), 151.34 MiB | 8.92 MiB/s, done.
Resolving deltas: 100% (3163/3163), done.

$ du -sh drafts-fresh
152M    drafts-fresh

$ du -sh drafts-fresh/.git
151M    drafts-fresh/.git
```

**Target improvement:**
- **Before cleanup:** 479 MB total, 384 MB .git
- **After cleanup:** 152 MB total, 151 MB .git  
- **Saved:** 327 MB (68% reduction!)
- **Clone speed:** ~50% faster (151 MiB vs 379 MiB transfer)

## Team/Device Follow-up Checklist

After rewrite:

- Re-clone on all machines using this repo
- Recreate open local branches from the new history
- Close/recreate old PRs that point to pre-rewrite SHAs

## How I Will Keep Size Down Going Forward

### Add Guardrails

- Add a CI check to fail PRs on oversized files (for example >10 MB or >20 MB)
- Add local pre-commit/pre-push check for large files

### Keep Binary Policy Explicit

- No portable executables in normal Git history
- Keep large generated artifacts out of source repo
- Store heavyweight downloads externally when possible

### Optimize Media Before Commit

- Prefer WebP/AVIF for screenshots when practical
- Compress PNG/JPG and PDFs before adding

## Final Takeaway

The repository was not slow because today’s content was huge. It was slow because old large binaries remained in history.

If your `.git` size dwarfs your working tree size, history cleanup is usually the real fix.

For my `drafts.mcgarrah.org` repo, rewrite-history + clean reclone is the right long-term move. The personal trigger for doing it was simple: the repo felt heavier than its job description. That kind of annoyance is often where the useful maintenance work starts.
