---
layout: post
title: "Jellyfin Media Integrity Scanner: Why Your Media Library Needs a Health Check"
image: /assets/images/og/jellyfin-media-integrity-scanner-introduction.png
categories: [homelab, media-server]
tags: [jellyfin, media-integrity, ffmpeg, proxmox, ceph, plugin-development, dotnet]
excerpt: "Media files rot silently. Bit-flip corruption, incomplete transfers, and storage failures leave your Jellyfin library with files that look fine in the UI but fail during playback. This is the first in a series on building a production-safe media integrity scanner for Jellyfin."
description: "Introducing the Jellyfin Media Integrity Scanner plugin project — a production-safe tool for detecting corrupt, truncated, and damaged media files in your Jellyfin library without impacting playback performance. Part 1 of a 5-part development series."
date: 2026-07-29
last_modified_at: 2026-07-29
seo:
  type: BlogPosting
  date_published: 2026-07-29
  date_modified: 2026-07-29
---

Your Jellyfin library looks healthy. Every thumbnail loads. Every title appears in the right collection. But somewhere in those terabytes of media, files are silently broken — and you won't know until someone hits play and gets a black screen, audio glitch, or a crash halfway through a movie.

<!-- excerpt-end -->

This is the first article in a series documenting the development of **jellyfin-plugin-media-integrity-scanner** — a Jellyfin plugin that performs production-safe integrity scanning of your media library. The plugin detects corrupt, truncated, and damaged media files without impacting playback performance or overwhelming your storage infrastructure.

## The Problem: Silent Media Corruption

Media files degrade for reasons that have nothing to do with Jellyfin itself:

- **Bit-flip corruption** — Storage hardware degrades over time. A single flipped bit in a video stream can cause playback artifacts, crashes, or complete failure to decode.
- **Incomplete transfers** — Interrupted rsync jobs, failed SMB copies, or network hiccups during NFS writes leave files that appear complete (correct filename, reasonable size) but are truncated or contain null sections.
- **Storage subsystem failures** — RAID rebuilds, CephFS rebalancing, ZFS scrub-detected errors with no redundancy available, or LVM thin provisioning running out of space mid-write.
- **Filesystem corruption** — Power loss, kernel panics, or hardware failures that corrupt the filesystem metadata or file contents.
- **Encoding errors** — Incomplete transcoding jobs, ffmpeg crashes during processing, or malformed container headers from buggy ripping software.

The common thread: Jellyfin's library scan only checks that files exist and have parseable metadata. It does not validate that the actual media streams are playable from start to finish.

## Why Existing Solutions Fall Short

The Jellyfin ecosystem has a few tools that touch this space:

- **[jellyfin-plugin-media-analyzer](https://github.com/endrl/jellyfin-plugin-media-analyzer)** — Analyzes media for intro/credit detection. Not focused on integrity.
- **[jellyfin-helper](https://github.com/JellyPlugins/jellyfin-helper)** — An all-in-one dashboard plugin with some health features, but no deep byte-level scanning.
- **Manual ffmpeg scripts** — The most accurate approach, but requires manual scheduling, has no Jellyfin integration, and offers no dashboard visibility.

What's missing is a purpose-built tool that:

1. Validates media streams at the byte level using ffmpeg
2. Runs safely alongside a production Jellyfin instance
3. Throttles I/O to avoid impacting concurrent playback
4. Tracks scan results persistently (SQLite)
5. Provides admin dashboard visibility into library health
6. Responds to library changes (new files, deletions) automatically

## The Project: jellyfin-plugin-media-integrity-scanner

**Plugin name:** Media Integrity Scanner  
**Repository:** [github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner)  
**Namespace:** `Jellyfin.Plugin.MediaIntegrityScanner`  
**Target:** Jellyfin 10.11+ / .NET 9

The naming follows the established Jellyfin plugin convention (`jellyfin-plugin-{purpose}`) and the C# namespace convention (`Jellyfin.Plugin.{PascalCaseName}`).

### Why .NET 9 and Jellyfin 10.11+

Jellyfin 10.11 (released February 2025) moved the server runtime to .NET 9. Official plugins like [jellyfin-plugin-trakt](https://github.com/jellyfin/jellyfin-plugin-trakt) have already followed. The plugin template README still references .NET 8, but it lags behind the server — the Jellyfin server itself, community packaging (Synology, Docker), and first-party plugins have all moved to .NET 9.

Targeting 10.11+ means we get access to the latest APIs (including the EF Core database refactor that shipped in 10.11) and align with where the ecosystem is heading. The next major release (Jellyfin 12.0) will continue on .NET 9. Users on 10.9 or 10.10 are a shrinking group and will need to upgrade for 12.0 regardless.

### License: GPL-2.0-or-later

The plugin is licensed **GPL-2.0-or-later** to match [Jellyfin server's own license](https://github.com/jellyfin/jellyfin). The community uses a mix (MIT, GPL-2.0, GPL-3.0), but matching the server keeps the door open for potential inclusion as a core Jellyfin plugin down the road. GPL-3.0 would have been a compatibility gray area since Jellyfin inherited GPL-2.0 from the Emby fork without explicit "or later" language.

> **Build environment note:** The initial v0.1.0 scaffold builds and passes CI via GitHub Actions (Ubuntu runner, .NET 9 SDK, Jellyfin 10.11.11 NuGet packages). A dedicated Proxmox LXC container is being provisioned for local development and integration testing with `jellyfin-ffmpeg` and a live Jellyfin instance.

### Design Principles

1. **Production-safe by default** — Scans are throttled, pausable, and never hold locks on media files during playback.
2. **Two-phase scanning** — Fast metadata/header checks first, then opt-in deep byte-stream validation for flagged or all files.
3. **Storage-aware throttling** — Configurable I/O limits that respect shared storage (CephFS, NFS, SMB) where other services depend on the same bandwidth.
4. **Persistent state** — SQLite database tracks what's been scanned, when, and the result — so rescans are incremental, not full-library.
5. **Event-driven updates** — Hooks into Jellyfin library events to scan new files on add and clean up records on delete.

## Article Series Outline

This is a five-part series covering the full development lifecycle:

| # | Article | Focus |
|---|---------|-------|
| 1 | **Introduction** (this post) | Problem statement, project scope, architecture overview |
| 2 | [Architecture & Design Decisions](/jellyfin-media-integrity-architecture-design/) | Plugin vs. script, scanning strategy, throttling model, SQLite schema |
| 3 | [Building the Scanner Core](/jellyfin-media-integrity-scanner-core/) | FFmpeg integration, cross-platform paths, .NET 9 plugin structure |
| 4 | [The Dashboard & API](/jellyfin-media-integrity-dashboard-api/) | Admin UI, REST API controller, real-time scan status |
| 5 | [Deployment & Operations](/jellyfin-media-integrity-deployment-operations/) | Proxmox/CephFS deployment, scheduling, monitoring, CI/CD |

## Architecture at a Glance

```
┌─────────────────────────────────────────────────┐
│                 Jellyfin Server                 │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │       Media Integrity Scanner Plugin      │  │
│  ├───────────────────────────────────────────┤  │
│  │  Library Event Monitor                    │  │
│  │    ├── OnItemAdded → Queue for scan       │  │
│  │    ├── OnItemUpdated → Re-queue if needed │  │
│  │    └── OnItemRemoved → Purge from cache   │  │
│  ├───────────────────────────────────────────┤  │
│  │  Scan Engine (Bounded, Thread-Safe)       │  │
│  │    ├── Phase 1: Header/metadata check     │  │
│  │    ├── Phase 2: Full stream decode        │  │
│  │    └── I/O Throttle (configurable)        │  │
│  ├───────────────────────────────────────────┤  │
│  │  SQLite Cache                             │  │
│  │    └── Scan results, timestamps, status   │  │
│  ├───────────────────────────────────────────┤  │
│  │  REST API Controller                      │  │
│  │    ├── GET /MediaIntegrity/Status         │  │
│  │    ├── GET /MediaIntegrity/Results        │  │
│  │    └── POST /MediaIntegrity/Scan          │  │
│  ├───────────────────────────────────────────┤  │
│  │  Admin Dashboard (HTML/JS)                │  │
│  │    └── Library health overview + details  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
           │                           │
           ▼                           ▼
    ┌─────────────┐            ┌──────────────┐
    │   FFmpeg    │            │  Media Files │
    │  (decode)   │            │  (read-only) │
    └─────────────┘            └──────────────┘
```

## My Infrastructure Context

This plugin is being developed against my homelab setup:

- **Jellyfin** running in a Proxmox LXC container
- **Media storage** on CephFS (distributed, shared across nodes)
- **Multiple concurrent users** — playback must never be degraded by scanning
- **Mixed media** — Movies, TV series, music videos, concerts (tens of thousands of files)

CephFS adds a specific constraint: aggressive sequential reads from a scan can saturate OSD throughput and impact other clients. The throttling design accounts for this.

## Current Status (v0.1.0)

The project scaffold is complete and [published on GitHub](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/releases/tag/v0.1.0):

- ✅ Plugin loads in Jellyfin 10.11+ (verified via CI build against real NuGet packages)
- ✅ GitHub Actions CI/CD pipeline builds on every push and creates releases on tags
- ✅ Dependabot tracks NuGet and GitHub Actions updates
- ✅ GPL-2.0-or-later licensed to match Jellyfin server
- ⬜ Scanner engine implementation (next milestone)
- ⬜ SQLite persistence layer
- ⬜ REST API controller
- ⬜ Admin dashboard with live data
- ⬜ Library event hooks
- ⬜ Integration testing with real media files

The v0.1.0 release is installable in Jellyfin but not yet functional — it establishes the plugin structure, interfaces, and build pipeline. Implementation begins with the scan engine in the next development cycle.

## What's Next

The [next article](/jellyfin-media-integrity-architecture-design/) dives into architecture decisions: why a plugin instead of a standalone script, how the two-phase scanning strategy works, the SQLite schema design, and the throttling model that keeps production playback smooth.

## Resources

- **Repository:** [github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner)
- **Latest Release:** [v0.1.0](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/releases/tag/v0.1.0)
- **Installation Guide:** [INSTALL.md](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/blob/main/INSTALL.md)
- **Jellyfin Plugin Template:** [github.com/jellyfin/jellyfin-plugin-template](https://github.com/jellyfin/jellyfin-plugin-template)
- **Jellyfin Plugin Development Docs:** [jellyfin.org/docs/general/server/plugins/](https://jellyfin.org/docs/general/server/plugins/)
- **FFmpeg Documentation:** [ffmpeg.org/documentation.html](https://ffmpeg.org/documentation.html)
