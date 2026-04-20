---
layout: post
title: "Why My Drafts Repository Was Slow to Clone (And How I Fixed It)"
categories: [git, github, jekyll, infrastructure]
tags: [git-history, repository-size, git-filter-repo, performance, maintenance]
excerpt: "My drafts repository felt huge and slow to clone. The culprit was old binary blobs in Git history, not current site content. Here is the exact audit, options, and the rewrite-history + reclone path I am taking."
date: 2026-07-08
last_modified_at: 2026-07-08
seo:
  type: BlogPosting
  date_published: 2026-07-08
  date_modified: 2026-07-08
---

My `drafts.mcgarrah.org` repository started feeling heavy. Fresh clones were slow, and local operations felt more expensive than they should for a static content repo.

This post documents the exact issue, what I found, and the options I evaluated. I am leaning toward a history rewrite + clean reclone as the long-term fix.

<!-- excerpt-end -->

## The Symptom

A normal clone pulled far more data than expected for a drafts site.

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

## The Path I Am Taking

I am choosing **Option 3**: rewrite history and then re-clone cleanly.

Given the size profile, this is the only option that fixes root cause instead of hiding it locally.

## Safe Execution Plan

### 1) Freeze Writes Briefly

- Pause merges/pushes while rewrite is in progress
- Announce a short maintenance window

### 2) Create a Mirror Backup

```bash
git clone --mirror https://github.com/mcgarrah/drafts.mcgarrah.org.git drafts-mirror-backup.git
```

Keep this untouched until the migration is complete.

### 3) Rewrite in a Fresh Mirror Clone

```bash
git clone --mirror https://github.com/mcgarrah/drafts.mcgarrah.org.git drafts-rewrite.git
cd drafts-rewrite.git
```

Example removal strategy:

```bash
git filter-repo \
  --path assets/exes/FirefoxPortable_51.0.1_English.paf.exe --invert-paths \
  --path assets/exes/FirefoxPortable_51.0_English.paf.exe --invert-paths \
  --path assets/exes/jPortable_8_Update_121.paf.exe --invert-paths
```

If I decide to remove an entire obsolete directory from all history:

```bash
git filter-repo --path assets/exes --invert-paths
```

### 4) Verify Size Improvement

```bash
git count-objects -vH
```

Optional deeper check:

```bash
git rev-list --objects --all \
| git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
| awk '$1=="blob"{print $3"\t"$4}' \
| sort -nr | head -n 20
```

### 5) Force Push Rewritten History

```bash
git push --force --all origin
git push --force --tags origin
```

### 6) Re-clone Working Copy

```bash
git clone https://github.com/mcgarrah/drafts.mcgarrah.org.git
```

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

For my `drafts.mcgarrah.org` repo, rewrite-history + clean reclone is the right long-term move.
