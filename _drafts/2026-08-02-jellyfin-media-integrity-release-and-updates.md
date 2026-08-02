---
layout: post
title: "Jellyfin Media Integrity Scanner: v0.1.1 Release — Update Checker and Auto-Update"
image: /assets/images/og/jellyfin-media-integrity-release-and-updates.png
categories: [homelab, media-server]
tags: [jellyfin, media-integrity, release-management, auto-update, testing, plugin-development, dotnet]
excerpt: "From v0.1.0-dev to v0.1.1 stable: building automatic update checking, session-aware restart logic, and testing infrastructure to ship reliable releases. This article documents the post-development improvements that turned a working prototype into production-ready software."
description: "v0.1.1 release article for the Jellyfin Media Integrity Scanner. Covers update checker architecture, session-aware auto-restart, package bloat fixes, Playwright E2E testing, media corruption test matrix, and architectural documentation. Part 6 of a 6-part development series."
date: 2026-08-02
last_modified_at: 2026-08-02
seo:
  type: BlogPosting
  date_published: 2026-08-02
  date_modified: 2026-08-02
---

The first five articles in this series documented the development path from problem statement through operational deployment of the Media Integrity Scanner plugin. By the end of that arc (2026-07-31), the plugin was functionally complete — two-phase scanning, SQLite persistence, REST API, dashboard, and event-driven library monitoring all shipping and tested.

But "functionally complete" and "production-ready" are different things. Between v0.1.0 and the v0.1.1 stable release (2026-08-02), the plugin gained automatic update checking, session-aware restart logic, comprehensive end-to-end testing, and critical packaging fixes. This article covers what changed and why.

<!-- excerpt-end -->

No plan survives contact with real data. The first five articles designed a scanner, a dashboard, and a release pipeline that all looked correct on paper — and every one of them still had a gap that only showed up once something real got involved: a real installed release instead of five hand-copied DLLs, a real dashboard response parsed by real browser JavaScript, a real Jellyfin server that has no idea whether anyone's mid-episode when a restart gets triggered. This article is that reckoning, not a sixth increment of new features.

## The v0.1.0 → v0.1.1 Journey

The path from the initial v0.1.0 release to v0.1.1 stable involved:

1. **Development channel releases** — Three pre-releases (v0.1.0-dev.1 through dev.4) to test fixes before marking them stable
2. **Critical packaging bugs** — Discovered and fixed two issues that broke cross-platform installation
3. **Testing infrastructure** — Added Playwright E2E suite and media corruption matrix to validate real-world behavior
4. **Update mechanism** — Implemented automatic update checking with smart restart logic to prevent scan interruption
5. **Documentation** — Created ARCHITECTURE.md with event-flow diagrams, complementing the blog series

This article is Part 6 of the [Jellyfin Media Integrity Scanner](/jellyfin-media-integrity-scanner-introduction/) development series. Unlike the previous five parts, it's not required reading before deploying v0.1.0 — those articles describe a complete, working plugin. This is a "what came next" article for users interested in how production release engineering shaped the project after initial functionality shipped.

## Feature 1: Update Checker with Stable/Development Channels

Users installing the plugin via manifest.json could see updates in the Jellyfin dashboard, but there was no way for the plugin itself to detect new versions and notify the user — let alone automatically install them. The update checker solves this.

### Architecture

```
┌────────────────────────────────────────────┐
│         Plugin Startup / Scheduled          │
├────────────────────────────────────────────┤
│  Check for updates every 7 days (default)  │
│  Query GitHub releases API                 │
│  Compare versions & filter by channel      │
│  (stable or development)                   │
└────────────┬─────────────────────────────┘
             │
             ▼
      ┌──────────────────┐
      │ Update Available?│
      └──────┬───────┬──┘
             │       │
         Yes│       │No
             │       │
             ▼       ▼
        [Notify   [Reschedule
         User]    Check]
```

The update checker runs asynchronously without blocking plugin startup or scan operations. When it detects a new version, it logs a message and sets a flag that appears in the dashboard status:

```json
{
  "IsScanning": false,
  "UpdateAvailable": {
    "Version": "0.1.2",
    "Channel": "stable",
    "ReleaseUrl": "https://github.com/mcgarrah/...",
    "AllowAutoUpdate": true
  }
}
```

### Channel Selection

The update checker respects a user-configurable preference:

| Setting | Default | Effect |
|---------|---------|--------|
| `CheckForUpdates` | true | Enable automatic checking |
| `PreferredReleaseChannel` | "stable" | "stable" or "development" |
| `AllowAutoUpdate` | false | Automatically download and install updates |

A user can enable `AllowAutoUpdate` to have the plugin download and stage updates automatically, then restart to apply them. The key innovation is the **session-aware restart logic** (covered next).

### Implementation Details

The update checker:

1. **Uses GitHub releases API** — No custom update server to maintain. Release artifacts on GitHub become the authoritative source.
2. **Filters by semantic version** — Parses `manifest.json` version field and compares against GitHub releases. Ignores pre-releases unless the user selected the development channel.
3. **Runs on a 7-day schedule** — Configurable via settings, defaulting to weekly checks to avoid hammering the API.
4. **Handles offline gracefully** — If GitHub is unreachable, the check logs a warning and reschedules for next week. No user-facing errors.

## Feature 2: Session-Aware Auto-Restart

Automatic updates are only useful if they actually apply. But blindly restarting Jellyfin to load a new plugin version creates a terrible user experience: if a scan is running, restarting interrupts it and potentially corrupts the database. If someone is actively watching a movie, restarting kills their playback.

The plugin detects these situations and defers the restart:

```csharp
// Pseudo-code: session-aware restart decision
bool CanRestartNow()
{
    // Check if an integrity scan is running
    if (ScanEngine.IsScanning)
        return false;
    
    // Check if users are actively streaming
    if (SessionManager.ActivePlaybackSessions.Any())
        return false;
    
    // Check quiet hours (if configured)
    if (Config.UseQuietHoursOnly && !IsInQuietHours())
        return false;
    
    return true;
}
```

When the update is staged and ready to apply:

1. **On idle** — If the plugin detects zero active scans and zero playback sessions, it restarts immediately
2. **On schedule** — If the user configured quiet hours, it waits for the quiet window and restarts then
3. **Last resort** — If an update has been staged for more than 7 days, it forces a restart (the update is critical) but logs a warning that scans were interrupted

This prevents the most painful scenario: a user's scan of 50,000 files starts on Monday, and auto-update silently kills it on Wednesday morning.

### What Triggers a Restart

The plugin only restarts when:
- An update is staged and ready to apply (`AllowAutoUpdate: true`)
- OR a manual "Apply Update" button is clicked in the dashboard

Normal operation (scanning, API requests, dashboard access) never triggers a restart.

## Critical Fixes: Packaging and Cross-Platform Support

Two packaging bugs surfaced during testing and needed to be fixed before calling the release stable.

### Issue 1: Shipping Redundant Assemblies

The initial plugin package included:

- Every Jellyfin assembly (even though the host already provides them)
- Platform-specific native SQLite libraries for Windows, Linux, and macOS (all bundled together)

This bloated the plugin zip to ~40MB, most of it unused. Windows installs included Linux binaries and vice versa. Worse, the duplicate Jellyfin assemblies sometimes shadowed the host versions, causing unpredictable binding-redirect behavior.

**Fix (PR #29):** Removed all redundant assemblies and platform-specific natives from the package. The plugin now:

- Declares Jellyfin assemblies as `<FrameworkReference>` (the server provides them)
- Declares `Microsoft.Data.Sqlite` as a NuGet dependency (the runtime installs the right native library for the target platform)
- Publishes only the plugin's own code and essential cross-platform dependencies

**Result:** Package size dropped from ~40MB to ~3MB. Installation is faster, and cross-platform conflicts disappeared.

### Issue 2: Assembly Whitelist for Cross-Platform Loading

Even after removing redundant assemblies, the plugin needed an explicit **whitelist** of which assemblies were allowed to load on each platform. The `.pdb` debug symbol files were platform-independent, but some binaries weren't, and Jellyfin's plugin loader was conservative: if it saw any assembly it couldn't verify, it rejected the entire plugin package.

**Fix (PR #30):** Added an assembly whitelist to `manifest.json`:

```json
{
  "assemblies": [
    "Jellyfin.Plugin.MediaIntegrityScanner.dll",
    "Microsoft.Data.Sqlite.dll"
  ],
  "linuxNativeAssemblies": [
    "runtimes/linux-x64/native/e_sqlite3.so"
  ],
  "windowsNativeAssemblies": [
    "runtimes/win-x64/native/e_sqlite3.dll"
  ],
  "osxNativeAssemblies": [
    "runtimes/osx-x64/native/libe_sqlite3.dylib"
  ]
}
```

This lets Jellyfin know: "This plugin is guaranteed to load correctly on Windows, Linux, and macOS." The plugin now installs successfully on all three platforms.

## Testing Infrastructure: Playwright E2E and Corruption Matrix

Between commits, two major testing initiatives shipped to reduce post-release surprises.

### Playwright End-to-End Testing (PR #24)

The unit test suite (141 tests) covers the core logic: scan engine decisions, database queries, API responses, concurrency safety. But unit tests can't catch everything — particularly UI integration bugs and Jellyfin API version mismatches.

The plugin now includes a **Playwright E2E test suite** that:

1. Launches a real Jellyfin instance in Docker
2. Automates a real web browser (headless Chrome)
3. Logs in as admin
4. Navigates to the plugin dashboard
5. Triggers a scan
6. Verifies results appear in the dashboard
7. Edits settings
8. Confirms the UI reflects the changes

This caught a real bug that slipped past unit tests: the dashboard JSON response was using wrong casing for some fields, causing the UI JavaScript to fail silently. The E2E suite caught it immediately by actually rendering the page.

### Media Corruption Test Matrix (PR #23)

The plugin's core value is detecting corrupt media files. But how do you verify the detection logic works? You need actual corrupt files to scan.

The project now includes a **test fixture generator** that creates good and bad video files:

```bash
# Good files (valid containers, playable streams)
ffmpeg -f lavfi -i testsrc=size=320x240:duration=1 -f lavfi -i sine=f=1000:d=1 good_video.mp4
ffmpeg -f lavfi -i testsrc=size=320x240:duration=1 good_video.mkv

# Bad files (truncated, corrupt headers, invalid codecs)
truncate -s 1M good_video.mp4        # Truncated file
dd if=/dev/zero of=corrupt.mp4 bs=1 count=1024 seek=65536 conv=notrunc  # Corrupt middle
dd if=/dev/urandom of=badheader.mp4 bs=1 count=100  # Corrupt header
```

The matrix validates that:
- **Phase 1 (ffprobe)** catches truncated files, corrupt containers, invalid codecs
- **Phase 2 (ffmpeg decode)** catches mid-file corruption and encoding errors
- **False positives** don't occur on actually valid files

This gives confidence that the plugin's detection logic matches what real ffmpeg does, not what the developer *thinks* ffmpeg does.

## Documentation: ARCHITECTURE.md

The five-part blog series covers the design, but operators and developers need to understand **every single code path** that can trigger a scan — Jellyfin events, scheduled tasks, manual API calls. A single diagram that shows all of these helps immensely.

[ARCHITECTURE.md](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/blob/main/ARCHITECTURE.md) includes:

1. **Event-flow diagram** — Every Jellyfin event that feeds into the scan engine:
   - Library item added/removed
   - Scheduled tasks (header scan, deep scan)
   - REST API calls (manual triggers)
   - Settings changes that affect throttling

2. **Gate pipeline diagram** — Every decision the scan engine makes before actually starting a scan:
   - Is it quiet hours? Stop.
   - Is playback active? Pause.
   - Are we at concurrency limit? Queue.
   - Does Phase 1 pass? Skip Phase 2 (unless configured otherwise).

3. **Two worked scenarios**:
   - Scenario 1: User adds a new file to the library while deep scan is running
   - Scenario 2: User manually triggers a deep scan from the dashboard during active playback

These diagrams live in the repository, not in the blog series, because they update as the code evolves. The blog articles describe *why* the design works; ARCHITECTURE.md documents *how* it works in real code.

## The Release Checklist

Getting from v0.1.0-dev to v0.1.1 stable required a formal checklist:

- ✅ Unit tests passing (141 tests)
- ✅ Integration tests passing (Docker + real Jellyfin instance)
- ✅ E2E tests passing (Playwright browser automation)
- ✅ Media corruption matrix validated
- ✅ Cross-platform packaging verified (Windows, Linux, macOS)
- ✅ Update checker tested and working
- ✅ Session-aware restart logic verified
- ✅ Documentation complete (README.md, ARCHITECTURE.md, INSTALL.md, RELEASE.md)
- ✅ GitHub releases API workflow automated (manifest.json version bumps on tagged release)
- ✅ Both stable and development channel builds working

The development channel (`v0.1.0-dev.1` through `dev.4`) provided a staging ground for the fixes. Each dev release was a stepping stone toward stability.

## For Users: What Changed

If you're running v0.1.0 and upgrading to v0.1.1:

1. **Installation is easier** — Package is 13x smaller (3MB vs 40MB)
2. **Cross-platform works now** — If you're on Windows or macOS, the plugin now works reliably
3. **Auto-update is optional** — Disabled by default. Enable in **Dashboard → Plugins → Media Integrity Scanner → Settings** if you want automatic updates
4. **Scans never interrupted by restarts** — Even if you enable auto-update, restarts wait for idle periods
5. **Everything else is the same** — The scanning logic, throttling, database schema, and API are unchanged

No action required. The upgrade is transparent.

## For Developers: What Matters

If you're using this plugin as a reference for Jellyfin plugin development:

1. **Platform-specific artifacts belong in manifest.json, not the package** — Declare them and let the plugin loader sort out what to install where
2. **Update checking is worth doing** — GitHub releases API is free and reliable. Users expect to see "Update available" notifications
3. **Session awareness prevents disasters** — Check playback sessions and scan state before auto-restarting
4. **E2E testing catches what unit tests miss** — Browser automation finds UI bugs, casing bugs, and integration mismatches
5. **Test fixture generation validates detection logic** — Create the edge cases you're trying to detect
6. **Architectural diagrams live in code, not blog articles** — Blog articles explain *why*; diagrams document *what*

## Series Recap

The six-part series now covers:

| # | Article | Focus |
|---|---------|-------|
| 1 | [Introduction](/jellyfin-media-integrity-scanner-introduction/) | Problem statement, project scope, architecture overview |
| 2 | [Architecture & Design Decisions](/jellyfin-media-integrity-architecture-design/) | Plugin vs. script, two-phase scanning, I/O throttling, SQLite |
| 3 | [Building the Scanner Core](/jellyfin-media-integrity-scanner-core/) | FFmpeg integration, plugin structure, scan engine |
| 4 | [The Dashboard & API](/jellyfin-media-integrity-dashboard-api/) | Admin UI, REST API, real-time status |
| 5 | [Deployment & Operations](/jellyfin-media-integrity-deployment-operations/) | Proxmox/CephFS setup, monitoring, CI/CD pipeline |
| 6 | **v0.1.1 Release** (this post) | Update checker, auto-update, testing, packaging |

Together, these articles document a complete development and release cycle: from identifying a problem, designing a solution, implementing it, shipping it, and then hardening it for production use based on real-world feedback.

## What's Next

The plugin is stable and production-ready, but the roadmap includes:

- Prometheus metrics export (direct scrape, not custom polling scripts)
- Bulk rescan operations (scan all files matching criteria: media type, library, date range)
- Scan result export (CSV for analysis or archival)
- Storage-level integrations (alerts when CephFS/RAID health degrades)

These are future enhancements, not prerequisites for stable operation. v0.1.1 is the end of the development series, but not the end of the plugin's evolution.

---

**Related Articles:**
- [Managing Context and Rules Across Multiple AI Coding Assistants](/managing-cross-ai-agent-context/) — Bonus: how this plugin was built
- [AI Coding Agent Context Files: A Reference Guide](/ai-coding-agent-context-files-reference/) — The methodology behind coordinating multiple AI agents on the project
- [AI Agent Context Files in Practice: One Repo, Five Agents](/ai-agent-context-files-in-practice/) — The same plugin as a case study in cross-agent collaboration

**Project Links:**
- [Repository](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner)
- [ARCHITECTURE.md](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/blob/main/ARCHITECTURE.md) — Event-flow and gate-pipeline diagrams
- [Releases](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/releases) — Stable and development channel
