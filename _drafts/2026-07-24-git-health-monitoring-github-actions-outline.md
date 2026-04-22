---
layout: post
title: "Repository Cleanup Part 3 Outline: Git Health Monitoring with GitHub Actions"
categories: [git, github, jekyll, infrastructure]
tags: [git-history, repository-size, github-actions, automation, maintenance]
excerpt: "Outline for a future Part 3 follow-up after the repository cleanup work. Focus: use GitHub Actions to measure git-health metrics over time, flag oversized files before they become clone pain, and turn repository cleanup into a lightweight maintenance habit instead of a reactive archaeology project."
description: "Planning a GitHub Actions workflow for ongoing Git repository health monitoring. Automated size tracking, large file detection, and history bloat prevention."
date: 2026-07-24
last_modified_at: 2026-07-24
seo:
  type: BlogPosting
  date_published: 2026-07-24
  date_modified: 2026-07-24
series: "Repository Cleanup"
series_part: 3
---

**Part 3 outline**: Git-health monitoring after the manual cleanup work proves itself.

This is not the next thing I am doing immediately. It is the follow-up I want ready once Part 1 is executed and Part 2 has been revised with real results.

The idea is straightforward: if repository bloat is annoying enough to investigate manually, it is probably important enough to monitor automatically.

<!-- excerpt-end -->

## Core Premise

Part 1 is about fixing one concrete repository problem.

Part 2 is about deciding whether that same cleanup path should apply anywhere else.

Part 3 would be about preventing this work from turning into another future archaeology project.

The goal is not to build an elaborate compliance system. The goal is to create a lightweight signal loop that answers a few practical questions early:

- Is `.git` growing faster than expected?
- Did someone commit a large binary that will make clones slower?
- Are object counts, pack size, or tracked asset sizes drifting enough to justify attention?
- Can I catch this before it becomes a half-day cleanup task?

## Article Goal

Show how to use GitHub Actions to measure repository health over time and surface the small Git metrics that affect clone and maintenance performance.

This follow-up should stay practical:

- no overengineered observability stack
- no false precision
- no pretending every repository needs the same rules

The angle should be: simple automation for personal repositories that makes future cleanup decisions easier.

## Candidate Structure

### 1. Why Add Automation After Manual Cleanup?

- Manual cleanup is useful because it teaches the real failure mode
- Automation is useful because it catches recurrence earlier
- The right sequence is manual understanding first, automation second

### 2. What Should Be Measured?

Potential metrics:

- `du -sh .git`
- `git count-objects -v`
- largest tracked files in `HEAD`
- largest historical blobs when needed
- total repository size
- count of files above thresholds like 5 MB, 10 MB, 20 MB

Potential derived signals:

- `.git` as percentage of total repo size
- delta from last successful run
- newly introduced large files in a PR or push

### 3. What Should Trigger Attention?

Possible thresholds:

- fail when a newly committed file exceeds a hard size limit
- warn when `.git` exceeds a percentage threshold
- warn when pack size jumps materially between runs
- report when top-N tracked files change significantly

This section should discuss signal quality versus noise. A repository with images or PDFs will have different expectations than a code-only project.

### 4. Workflow Design Options

Possible GitHub Action patterns:

- scheduled weekly health report
- push-based reporting on `main`
- PR-time checks for newly added large files
- manual workflow dispatch for deeper audits

Tradeoffs:

- scheduled jobs are low-friction but can be noisy
- PR checks are more actionable but narrower
- full historical blob scans may be too expensive for every run

### 5. Reporting Options

Possible outputs:

- workflow summary in Actions UI
- markdown artifact upload
- issue comment or periodic issue update
- commit status check with warning/fail behavior

The best version is probably one that keeps output readable and boring.

### 6. Repository-Specific Policy

This section should explain why one threshold does not fit every repo.

Examples:

- `resume` can tolerate a PDF and bundled assets
- `jekyll-run` has large working-tree dev artifacts but a tiny `.git`
- `mcgarrah.github.io` has historically carried large downloadable binaries
- content repositories need different limits than code repositories

### 7. Lightweight Implementation Plan

Proposed rollout:

1. Start with one repository after Part 1 and Part 2 are finalized.
2. Collect metrics and print them in a workflow summary.
3. Add soft warnings before any hard failures.
4. Add file-size gates only after the false-positive rate is understood.

### 8. What Not To Automate Yet

Important boundary conditions:

- do not run full history rewrites automatically
- do not fail every build on broad health heuristics
- do not add expensive scans where a cheap file-size gate is enough
- do not standardize thresholds before comparing repo types

## Commands and Data Points To Reuse

Likely building blocks from Parts 1 and 2:

```bash
du -sh .git
git count-objects -v
git ls-files -z | xargs -0 du -k | sort -rn | head -20
git rev-list --all --objects \
| git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
| awk '$1=="blob"{print $3"\t"$4}' \
| sort -nr | head -20
```

The article should separate cheap metrics from expensive metrics, because that distinction matters in CI.

## Open Questions Before Writing Part 3 Fully

- Should the first version report only, or also enforce thresholds?
- Should reporting live in one reusable workflow or be customized per repo?
- Should large-file checks happen in PRs, on `main`, or both?
- Is a GitHub Action enough, or would a small script repo make this easier to reuse?
- Which metrics are genuinely predictive versus just interesting?

## Likely End State

If this becomes a real article, it should end with a small, boring, reusable GitHub Action and a clear explanation of what it catches well, what it intentionally ignores, and how it fits after the manual cleanup work from Parts 1 and 2.

That is the right level of ambition for a Part 3: not a platform, just a durable guardrail.