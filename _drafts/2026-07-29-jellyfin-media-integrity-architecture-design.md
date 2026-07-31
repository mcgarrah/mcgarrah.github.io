---
layout: post
title: "Jellyfin Media Integrity Scanner: Architecture & Design Decisions"
image: /assets/images/og/jellyfin-media-integrity-architecture-design.png
categories: [homelab, media-server]
tags: [jellyfin, media-integrity, architecture, sqlite, throttling, plugin-development, dotnet]
excerpt: "Plugin or script? How aggressive should scanning be? Where do results live? This article covers the key architecture decisions behind the Jellyfin Media Integrity Scanner — from two-phase scanning strategy to production-safe I/O throttling."
description: "Architecture and design decisions for the Jellyfin Media Integrity Scanner plugin. Covers plugin vs. script tradeoffs, two-phase scanning strategy, SQLite schema design, I/O throttling model, and CephFS/NFS storage considerations. Part 2 of a 5-part development series."
date: 2026-07-29
last_modified_at: 2026-07-29
seo:
  type: BlogPosting
  date_published: 2026-07-29
  date_modified: 2026-07-29
---

The [first article](/jellyfin-media-integrity-scanner-introduction/) introduced the problem: media files rot silently, and Jellyfin doesn't validate stream integrity. This article covers the architectural decisions that shape the plugin's design — the tradeoffs, constraints, and reasoning behind each choice.

<!-- excerpt-end -->

This is Part 2 of the [Jellyfin Media Integrity Scanner](/jellyfin-media-integrity-scanner-introduction/) development series.

## Decision 1: Plugin vs. Standalone Script

The first major decision: should this be a Jellyfin plugin (C#/.NET, runs inside the server process) or an external script (bash/Python, runs independently)?

### Why a Plugin Wins

| Factor | Plugin | Script |
|--------|--------|--------|
| Library awareness | Direct access to Jellyfin's item database | Must query API or parse filesystem |
| Event hooks | Subscribes to ItemAdded/Removed events | Requires polling or webhooks |
| Admin UI | Native dashboard integration | Separate web interface needed |
| Configuration | Jellyfin's plugin config system | Separate config file |
| Scheduling | Jellyfin's scheduled task system | External cron/systemd timer |
| User visibility | Shows in Plugins page | Invisible to Jellyfin admins |
| State management | Plugin lifecycle managed by Jellyfin | Must handle own process lifecycle |

### Why Scripts Still Have a Role

Scripts remain useful for:
- One-off scans before initial library import
- Environments where plugin installation isn't possible
- Debugging and development (faster iteration than plugin reload)

The architecture supports both: the core scanning logic wraps ffmpeg in a way that could be extracted into a standalone CLI tool later.

## Decision 2: Two-Phase Scanning Strategy

Not all integrity checks are equal in cost. A full byte-stream decode of a 4K Blu-ray remux can take 10-15 minutes and read 50+ GB. Running that against every file on every scan is impractical.

### Phase 1: Fast Header & Metadata Check

**Cost:** ~100ms per file  
**What it catches:** Truncated files, corrupt containers, missing streams, invalid codecs

```bash
ffprobe -v error -show_entries format=duration,size,bit_rate \
  -show_entries stream=codec_type,codec_name,width,height \
  -of json "input.mkv"
```

If ffprobe returns errors or can't parse the container, the file is immediately flagged.

### Phase 2: Full Byte-Stream Decode

**Cost:** Minutes per file (proportional to file size)  
**What it catches:** Corrupt frames, audio glitches, mid-file corruption, encoding errors

```bash
ffmpeg -v error -i "input.mkv" -f null - 2>&1
```

This decodes every frame without producing output. Any decode errors are captured from stderr.

### When to Use Each Phase

- **Phase 1** runs on all files during scheduled scans
- **Phase 2** runs on:
  - Files that fail Phase 1 (confirm the failure)
  - Newly added files (validate before marking as "good")
  - User-triggered deep scans from the dashboard
  - Scheduled full-library deep scans (opt-in, runs over days/weeks)

## Decision 3: I/O Throttling Model

The most critical design constraint: scanning must never degrade playback.

### The Problem with Unthrottled Scanning

A naive scan reads files sequentially at maximum disk speed. On shared storage (CephFS, NFS), this:
- Saturates network bandwidth between storage nodes
- Fills OSD/NFS server read caches with scan data, evicting hot playback data
- Creates I/O contention that adds latency to concurrent reads

### The Throttling Approach

```
┌─────────────────────────────────────┐
│        Throttle Configuration       │
├─────────────────────────────────────┤
│  MaxConcurrentScans: 1              │
│  DelayBetweenFiles: 5000ms          │
│  MaxBytesPerSecond: 10MB/s          │
│  PauseDuringPlayback: true          │
│  ActiveHoursOnly: false             │
│  QuietHoursStart: 02:00             │
│  QuietHoursEnd: 06:00               │
└─────────────────────────────────────┘
```

Key throttling mechanisms:

1. **Inter-file delay** — Configurable pause between scanning each file (default: 5 seconds)
2. **Bandwidth cap** — Limit read throughput via ionice or application-level rate limiting
3. **Playback awareness** — Pause scanning when active playback sessions exist
4. **Concurrency limit** — Never scan more than N files simultaneously (default: 1)
5. **Time-of-day scheduling** — Optional restriction to quiet hours

### CephFS-Specific Considerations

CephFS distributes data across OSDs. Sequential reads from scanning spread across the cluster, but:
- MDS (metadata server) load increases with rapid stat() calls during file enumeration
- OSD read-ahead can be wasteful for scanning (we read the whole file regardless)
- Client-side caching of scanned data wastes RAM since we won't re-read

The plugin uses `posix_fadvise(FADV_SEQUENTIAL | FADV_DONTNEED)` semantics (via ffmpeg's I/O behavior) to hint that scanned data shouldn't be cached.

## Decision 4: SQLite for Persistent State

### Why SQLite

- Zero configuration — single file, no server process
- ACID compliant — safe against crashes during scan
- Embedded — ships with .NET, no external dependency
- Concurrent reads — multiple threads can read while one writes
- Small footprint — scan metadata for 100K files fits in <50MB

### Schema Design

```sql
CREATE TABLE scan_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL,           -- Jellyfin item GUID
    file_path TEXT NOT NULL,
    file_size INTEGER,
    last_modified TEXT,              -- File mtime at scan time
    scan_phase INTEGER NOT NULL,     -- 1 = header, 2 = full decode
    scan_status INTEGER NOT NULL,    -- 0 = pending, 1 = pass, 2 = fail, 3 = error
    scan_timestamp TEXT NOT NULL,
    error_output TEXT,               -- ffmpeg/ffprobe stderr on failure
    scan_duration_ms INTEGER,
    UNIQUE(item_id, scan_phase)
);

CREATE TABLE scan_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX idx_scan_results_status ON scan_results(scan_status);
CREATE INDEX idx_scan_results_item ON scan_results(item_id);
CREATE INDEX idx_scan_results_timestamp ON scan_results(scan_timestamp);
```

### Incremental Scanning Logic

On each scheduled scan:
1. Query Jellyfin for all media items
2. For each item, check if `scan_results` has an entry where `last_modified` matches current file mtime
3. If mtime matches and previous scan passed → skip
4. If mtime differs or no entry exists → queue for scan

This means only new or modified files get scanned on subsequent runs.

## Decision 5: Event-Driven Library Monitoring

Rather than relying solely on scheduled scans, the plugin hooks into Jellyfin's library events:

- **ItemAdded** — New file imported → queue Phase 1 scan
- **ItemUpdated** — File replaced/re-encoded → queue Phase 1 scan
- **ItemRemoved** — File deleted → purge scan_results entry

This keeps the database in sync with the actual library state and ensures new imports are validated promptly.

## Decision 6: Cross-Platform FFmpeg Resolution

Jellyfin runs on Linux, Windows, and macOS. FFmpeg's binary location varies:

| Platform | Common Paths |
|----------|-------------|
| Linux (apt) | `/usr/bin/ffmpeg`, `/usr/bin/ffprobe` |
| Linux (Jellyfin bundle) | `/usr/lib/jellyfin-ffmpeg/ffmpeg` |
| Windows | `C:\ProgramData\Jellyfin\Server\ffmpeg.exe` |
| macOS (brew) | `/opt/homebrew/bin/ffmpeg` |
| Docker | `/usr/lib/jellyfin-ffmpeg/ffmpeg` |

The plugin resolves ffmpeg using:
1. Jellyfin's own configured ffmpeg path (from server config)
2. `PATH` environment variable lookup
3. Platform-specific known locations
4. User-configurable override in plugin settings

## What's Next

The [next article](/jellyfin-media-integrity-scanner-core/) implements the scanner core: the .NET 9 plugin structure, ffmpeg process management, the bounded task queue, and cross-platform path resolution.

## Series Navigation

1. [Introduction & Problem Statement](/jellyfin-media-integrity-scanner-introduction/)
2. **Architecture & Design Decisions** (this post)
3. [Building the Scanner Core](/jellyfin-media-integrity-scanner-core/)
4. [The Dashboard & API](/jellyfin-media-integrity-dashboard-api/)
5. [Deployment & Operations](/jellyfin-media-integrity-deployment-operations/)
