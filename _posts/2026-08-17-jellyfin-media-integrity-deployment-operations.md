---
layout: post
title: "Jellyfin Media Integrity Scanner: Deployment & Operations"
image: /assets/images/og/jellyfin-media-integrity-deployment-operations.png
categories: [homelab, media-server]
tags: [jellyfin, media-integrity, proxmox, ceph, deployment, ci-cd, monitoring, github-actions]
excerpt: "Getting the Media Integrity Scanner into production — installing in Proxmox LXC containers, configuring for CephFS storage, setting up monitoring and alerting, and building the CI/CD pipeline for automated plugin releases."
description: "Deploying and operating the Jellyfin Media Integrity Scanner plugin in a production homelab. Covers Proxmox LXC installation, CephFS/NFS storage configuration, monitoring with Prometheus/Grafana, alerting on failures, and GitHub Actions CI/CD for automated builds and releases. Part 5 of a 6-part development series."
date: 2026-08-17
last_modified_at: 2026-08-17
seo:
  type: BlogPosting
  date_published: 2026-08-17
  date_modified: 2026-08-17
---

The plugin is built — scanner core, SQLite persistence, REST API, admin dashboard. Now it needs to run reliably in production without causing problems. This article covers the deployment story: installing the plugin, configuring it for shared storage, monitoring its operation, and automating the release pipeline.

<!-- excerpt-end -->

This is Part 5 of the [Jellyfin Media Integrity Scanner](/jellyfin-media-integrity-scanner-introduction/) development series. The build pipeline, release pipeline, and Proxmox LXC provisioning described below are all live and operational, and `MaxReadRateMbPerSec` and the quiet-hours settings in the CephFS/NFS tuning tables are genuinely enforced (see [CephFS-Specific Configuration](#cephfs-specific-configuration) for the mechanism). The CI/CD section reflects the real, current workflows — automated `manifest.json` version bumps on tagged releases, plus a unit test suite and a Docker-based integration suite gating every build (see [CI/CD Pipeline](#cicd-pipeline) for what that testing found). There's also a real in-app settings page now (see the [dashboard article](/jellyfin-media-integrity-dashboard-api/#update-a-real-settings-page)), so the "Configure throttling settings" step in the [Operational Runbook](#operational-runbook) no longer means hand-editing an XML file. CephFS OSD-level tuning and Prometheus/Grafana monitoring remain aspirational — see the [final article's Future Work section](/jellyfin-media-integrity-release-and-updates/#future-work) for where those stand.

## Installation Methods

### Method 1: Plugin Repository (Recommended)

Add the custom repository to Jellyfin:

1. **Dashboard → Plugins → Repositories → Add**
2. **Name:** `mcgarrah-plugins`
3. **URL:** `https://raw.githubusercontent.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/main/manifest.json`
4. **Save** → Go to **Catalog** → Install **Media Integrity Scanner**
5. **Restart Jellyfin**

**If the plugin doesn't appear in the Catalog after adding the repository, this is almost always the web client, not the server.** Hit exactly this standing up a second test instance: the repository saved correctly, the manifest was reachable (confirmed both from a browser and with `curl` from inside the container), and querying the server's own `/Packages` API directly with an authenticated request showed the plugin present in the catalog data all along — correct GUID, correctly tagged with the repository name. The web UI was just holding a stale, cached view of the catalog fetched before the repository was added. A hard refresh of the Catalog page (Ctrl+Shift+R / Cmd+Shift+R, not a normal reload) resolved it immediately. If that doesn't do it, a full logout/login or a private-browsing window rules out cached session state, and it's worth checking the Catalog page's category filter dropdown hasn't been left on something other than "General" from a previous session.

### Method 2: Manual DLL Installation

For development or airgapped environments:

```bash
# Download the latest release
wget https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/releases/latest/download/media-integrity-scanner.zip

# Extract to plugin directory
unzip media-integrity-scanner.zip -d \
  /var/lib/jellyfin/plugins/MediaIntegrityScanner

# Restart Jellyfin
systemctl restart jellyfin
```

### Method 3: Build from Source

```bash
git clone https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner.git
cd jellyfin-plugin-media-integrity-scanner

dotnet build --configuration Release
dotnet publish --configuration Release --output ./publish

# Copy to plugins directory
cp -r ./publish /var/lib/jellyfin/plugins/MediaIntegrityScanner

systemctl restart jellyfin
```

## Proxmox LXC Configuration

My Jellyfin runs in an unprivileged Proxmox LXC container. Key considerations:

### FFmpeg Availability

The `jellyfin-ffmpeg` package bundles a compatible ffmpeg build:

```bash
# Inside the LXC container
apt install jellyfin-ffmpeg6

# Verify
/usr/lib/jellyfin-ffmpeg/ffmpeg -version
```

The plugin auto-detects this path. No configuration needed.

### Resource Limits

The LXC container should have adequate resources for background scanning:

```ini
# /etc/pve/lxc/XXX.conf additions for scan workload
lxc.cgroup2.cpu.max: 200000 100000  # 2 cores max
lxc.cgroup2.memory.max: 4G
lxc.cgroup2.io.max: /dev/sdX rbps=10485760  # 10MB/s read limit
```

The `io.max` cgroup limit provides a hard ceiling on disk I/O at the container level, complementing the plugin's application-level throttling.

### Storage Mount

CephFS media storage mounted into the container:

```ini
# /etc/pve/lxc/XXX.conf
mp0: /mnt/cephfs/media,mp=/media,ro=0
```

For integrity scanning, read-only access is sufficient. Consider mounting as read-only to prevent any accidental writes:

```ini
mp0: /mnt/cephfs/media,mp=/media,ro=1
```

## CephFS-Specific Configuration

CephFS distributed storage requires careful throttling to avoid impacting other clients:

### Recommended Plugin Settings for CephFS

```json
{
  "MaxConcurrentScans": 1,
  "DelayBetweenFilesMs": 10000,
  "MaxReadRateMbPerSec": 5,
  "PauseDuringPlayback": true,
  "UseQuietHoursOnly": true,
  "QuietHoursStart": "01:00",
  "QuietHoursEnd": "07:00"
}
```

### Why These Values

- **10-second inter-file delay** — Allows CephFS OSD recovery between reads
- **5 MB/s read cap** — Well below typical OSD throughput, leaves headroom for playback
- **Quiet hours only** — Scanning happens when nobody is watching
- **Single file at a time** — Prevents MDS metadata load spikes

> **Update (July 31, 2026) — how the read-rate cap and quiet hours actually work:** For a while, `MaxReadRateMbPerSec` and the quiet-hours settings were config fields that did nothing — a gap found during a later review. They're enforced now, but worth understanding the mechanism:
>
> - **`MaxReadRateMbPerSec` is an average-rate pacer, not a literal in-flight byte cap.** After each file scan, the plugin computes how long the file *should* have taken at the configured rate (`fileSizeMB ÷ maxReadRateMbPerSec`) and pads the wall-clock gap before the next file if the scan finished faster than that. This was a deliberate choice over piping the file through ffmpeg's stdin for precise byte-level control: stdin piping breaks seekability, and many MP4/MOV files store the `moov` atom at the end of the file — probing them over a non-seekable pipe produces a false `"moov atom not found"` failure, which is exactly the corruption signature this plugin exists to catch. The padding approach has zero risk to decode correctness and still bounds the long-run average throughput pulled from CephFS.
> - **`UseQuietHoursOnly` gates every scan through `ScanEngine`**, the same choke point all scan paths (manual, event-driven, and scheduled) already go through — mirroring the existing playback-pause mechanism. If the toggle is on and the current time falls outside the window, the scan waits (polling every 5 minutes) rather than skipping outright, so a manual "scan now" from the dashboard still eventually runs instead of silently no-op'ing.
>
> The OS-level `lxc.cgroup2.io.max` limit from the [Resource Limits](#resource-limits) section above is still the harder guarantee — the plugin's pacing is a cooperative, application-level complement to it, not a replacement.

### Monitoring CephFS Impact

Watch OSD utilization during scanning:

```bash
# On Proxmox host
ceph osd perf

# Per-OSD bandwidth
ceph daemon osd.X perf dump | jq '.osd.op_r_out_bytes'

# Client I/O from the Jellyfin container
ceph daemon mds.X session ls | jq '.[].inst'
```

## NFS Storage Configuration

For NFS-backed media libraries:

```json
{
  "MaxConcurrentScans": 1,
  "DelayBetweenFilesMs": 5000,
  "MaxReadRateMbPerSec": 20,
  "PauseDuringPlayback": true
}
```

NFS is more tolerant of sequential reads than CephFS, so the rate limit can be higher. Monitor with `nfsstat` on the server side.

## Monitoring & Alerting

### Prometheus Metrics (Future Enhancement)

The API endpoint provides data suitable for Prometheus scraping:

```yaml
# prometheus.yml scrape config
- job_name: 'jellyfin-media-integrity'
  metrics_path: '/MediaIntegrity/Status'
  static_configs:
    - targets: ['jellyfin-host:8096']
  # Custom relabeling to extract metrics from JSON response
```

### Simple Health Check Script

Until native Prometheus support is added:

```bash
#!/bin/bash
# /usr/local/bin/check-media-integrity.sh

API_KEY="your-api-key"
JELLYFIN_URL="http://localhost:8096"

STATUS=$(curl -s "${JELLYFIN_URL}/MediaIntegrity/Status" \
  -H "X-Emby-Token: ${API_KEY}")

FAILED=$(echo "$STATUS" | jq '.failedFiles')
HEALTH=$(echo "$STATUS" | jq '.healthPercentage')

if [ "$FAILED" -gt 0 ]; then
    echo "WARNING: $FAILED media files failed integrity check"
    echo "Library health: ${HEALTH}%"
    # Send notification (adapt to your alerting system)
    # curl -d "Media integrity: $FAILED failed files" ntfy.sh/your-topic
    exit 1
fi

echo "OK: Library health ${HEALTH}%"
exit 0
```

### Systemd Timer for Health Checks

```ini
# /etc/systemd/system/media-integrity-check.timer
[Unit]
Description=Check media integrity scan results

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

## CI/CD Pipeline

> **Build environment note (updated July 31, 2026):** The Proxmox LXC build/integration-test container is operational (.NET 9 SDK, `jellyfin-ffmpeg`, test Jellyfin instance, sample media). GitHub-hosted Ubuntu runners remain the primary CI path; the LXC is used for local/manual verification.
>
> **Update:** The workflows below are the real, current ones — including two things that were missing for a while: a wired-up unit test suite (`tests/Jellyfin.Plugin.MediaIntegrityScanner.Tests`, covering the quiet-hours/read-rate pacing logic from the [scanner core article](/jellyfin-media-integrity-scanner-core/#update-quiet-hours-and-read-rate-throttling)), and a real `scripts/update-manifest.py` wired into the release workflow (the script existed only as an unimplemented reference in this article before). Note that `dotnet build`/`dotnet publish` target the plugin's `.csproj` explicitly rather than the solution file — once the test project joined the `.sln`, publishing the whole solution would have bundled test binaries into the release artifact.
>
> **Update (August 1, 2026) — the test suite grew a lot, and it found real bugs:** The unit test project grew from 20 tests to 113 across 8 files, covering the database layer, the ffmpeg process wrapper, the API controller, and `ScanEngine` itself with mocked dependencies. Separately, the Docker-based integration suite (`tests/run-integration-tests.sh` and `integration-test.yml`, kept in sync with each other) grew from a basic "plugin loads, config endpoint responds" smoke check into something that actually exercises the scanning pipeline: a settings-page configuration round-trip, both web pages being served, a full scan-and-verify flow (trigger → poll → assert results), item-detail lookups, an item-scoped deep scan, and the cancel endpoint.
>
> Two things surfaced along the way that are worth knowing about if you're troubleshooting a similar setup:
> - **The "Verify FFmpeg is available in container" CI step was silently passing without checking anything**, for a long time. It ran `docker exec jellyfin-test ffmpeg -version | head -5` — since `jellyfin-ffmpeg` isn't symlinked onto `PATH` in the `jellyfin/jellyfin` image (it only lives at `/usr/lib/jellyfin-ffmpeg/ffmpeg`), that command actually fails, but piping into `head` without `pipefail` means the pipeline's reported exit code is `head`'s, not `ffmpeg`'s — so the step went green anyway. Fixed by checking the real path and adding `set -euo pipefail`, a good reminder that any `cmd | head`/`| tail` in CI is worth a second look for whether it's masking the thing you actually meant to check.
> - **Writing that integration suite found two real, previously-undetected bugs in the plugin itself** — the dashboard was reading JSON field names in the wrong casing (see the [dashboard article](/jellyfin-media-integrity-dashboard-api/#update-the-dashboard-was-reading-the-wrong-json-casing)), and the deep-scan "skip if already scanned" check never looked at scan phase (see the [scanner core article](/jellyfin-media-integrity-scanner-core/#update-the-skip-check-didnt-know-about-scan-phase)). Both had shipped silently for a while; both were only caught because the integration tests started actually asserting on real response data instead of just HTTP status codes.
>
> **Update (August 2, 2026) — a real corruption matrix, and a real-browser test suite:** The integration suite's test media was, until now, a single always-valid clip — every scan test proved the scanner *ran*, but none proved it actually *detected* anything. `tests/generate-test-media.sh` now generates seven files: two valid (different container/codec pairs) and five corrupted in distinct, verified-for-real ways — an empty file, random bytes with a video extension, a zeroed header, a truncated copy, and a file with a few KB zeroed out mid-stream. The last two are the interesting pair: both pass a header-only `ffprobe` scan (the corruption doesn't touch `moov`/`ftyp`) but fail a full `ffmpeg` decode — the first automated proof that this plugin's two-phase scanning design actually does what it claims, rather than just running twice for show.
>
> Building on top of that, a [Playwright](https://playwright.dev/) suite now drives the dashboard and settings pages through a real Chromium session — logging in via the actual web form, triggering a real scan, and asserting the UI reflects it — instead of the integration suite's curl+grep, which never executes a page's own JavaScript or its real `ApiClient`-backed session. That gap is exactly what caught the dashboard-was-never-reachable bug described in the [dashboard article's update](/jellyfin-media-integrity-dashboard-api/#update-the-dashboard-was-never-actually-reachable-in-a-real-browser). It runs in its own `playwright-e2e.yml` workflow, deliberately kept separate from `build.yml`/`integration-test.yml` — a real-browser suite is slower and more prone to environmental flakiness than a curl-based check, so its result is independent rather than blocking those other checks.
>
> One operational gotcha worth keeping in mind for any script that starts a Jellyfin container and installs a plugin into it in the same breath: **the plugin DLL has to land in the bind-mounted config directory *before* the container's first boot, not after.** Jellyfin loads plugins once, early in its own startup; copying a DLL in after that point is a no-op until the container is restarted. This is a genuine race, not a hypothetical — reproduced locally by starting the container and copying the DLL in immediately after, which intermittently lost the race and left every `/MediaIntegrity/*` route 404ing until an explicit restart. Both CI workflows now copy the plugin in before `docker run`/`docker compose up`, not after.

## Update: Automated Development Releases

Adding an [in-plugin update checker](/jellyfin-media-integrity-dashboard-api/#update-an-in-plugin-update-checker) that can offer a Development channel meant that channel needed something real to point at — a plugin repository manifest that actually gets newer entries as work lands on `main`, not just at tagged milestones.

A second workflow, `release-dev.yml`, now runs on every push to `main` and cuts a real GitHub **pre-release** plus a new `manifest-unstable.json`, parallel to the existing tagged-release path but never touching the stable `manifest.json`. The tricky part was version numbering: Jellyfin manifest versions have to be a clean 4-part numeric `System.Version` — no semver `-dev`/`-rc` suffix survives round-tripping through it — so the dev workflow keeps Major.Minor.Build from the current stable base and bumps only the fourth (Revision) component using the run's own unique, ever-increasing run number (`0.1.0.147`, say). The human-friendly `v0.1.0-dev.147` form still shows up in the GitHub release title and changelog text, just not in the version Jellyfin actually compares against.

One thing deliberately *not* done: bumping `Directory.Build.props` on every single dev push and committing it back. That's fine for a build artifact (the compiled DLL needs the real version baked in to compare correctly against what's installed), but committing it every push would spam the repo and collide with the stable release workflow's own version-bump commits to the same file — so the dev workflow bumps it locally within the CI run only, discards that change, and commits just the manifest update.

Also fixed while wiring this up: the existing stable `release.yml` updated `manifest.json`'s version on every tag but never actually bumped `Directory.Build.props` — meaning the *built assembly's own* version number never moved past `0.1.0.0`, tag after tag. Harmless before there was any code that cared about the plugin's own version, but a real problem for an update checker: it would report "update available" forever, even seconds after actually installing one, since the thing it's comparing against never changes. Both workflows now agree on the version story.

No safe way to dry-run a workflow whose only trigger is "push to main" without literally pushing to main first, so the real test was the first real merge. It worked cleanly on the first attempt: a genuine `v0.1.0-dev.1` pre-release appeared with the built zip attached, and `manifest-unstable.json` picked up a matching `0.1.0.1` entry with the right checksum and source URL, no fix-forward required.

### GitHub Actions: Build & Test

```yaml
# .github/workflows/build.yml
name: Build Plugin

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Setup .NET 9
        uses: actions/setup-dotnet@v6
        with:
          dotnet-version: '9.0.x'

      - name: Restore dependencies
        run: dotnet restore --verbosity normal

      - name: Build
        run: dotnet build --configuration Release --no-restore --verbosity normal

      - name: Test
        run: dotnet test --configuration Release --no-restore --no-build --verbosity normal

      - name: Publish
        run: dotnet publish Jellyfin.Plugin.MediaIntegrityScanner/Jellyfin.Plugin.MediaIntegrityScanner.csproj --configuration Release --output ./artifacts --no-build

      - name: List artifacts
        run: ls -la ./artifacts/

      - name: Upload build artifact
        uses: actions/upload-artifact@v7
        with:
          name: media-integrity-scanner
          path: ./artifacts/
          retention-days: 30
```

### GitHub Actions: Release

```yaml
# .github/workflows/release.yml
name: Release Plugin

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Setup .NET 9
        uses: actions/setup-dotnet@v6
        with:
          dotnet-version: '9.0.x'

      - name: Restore dependencies
        run: dotnet restore Jellyfin.Plugin.MediaIntegrityScanner/Jellyfin.Plugin.MediaIntegrityScanner.csproj

      - name: Build Release
        run: dotnet publish Jellyfin.Plugin.MediaIntegrityScanner/Jellyfin.Plugin.MediaIntegrityScanner.csproj --configuration Release --output ./publish

      - name: Package
        run: |
          cd publish
          zip -r ../media-integrity-scanner-${{ github.ref_name }}.zip .

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v3
        with:
          files: media-integrity-scanner-${{ github.ref_name }}.zip
          generate_release_notes: true

      - name: Update manifest.json
        run: |
          python3 scripts/update-manifest.py "${{ github.ref_name }}" "media-integrity-scanner-${{ github.ref_name }}.zip"
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add manifest.json
          git commit -m "chore: update manifest.json for ${{ github.ref_name }}"
          # Assumes the tag was created from the current tip of main.
          git push origin HEAD:main
```

`scripts/update-manifest.py` normalizes the git tag (`v0.2.0` → `0.2.0.0`), computes the MD5 checksum of the release zip (the convention Jellyfin plugin manifests use), derives `targetAbi` from the `Jellyfin.Controller` package reference in the `.csproj`, and prepends a new version entry to `manifest.json` — replacing any existing entry for the same version, so re-running for the same tag is idempotent.

## Operational Runbook

### First-Time Setup

1. Install plugin via repository or manual DLL
2. Restart Jellyfin
3. Navigate to **Dashboard → Plugins → Media Integrity Scanner**
4. Configure throttling settings for your storage backend
5. Optionally enable "Scan on Item Added" for new file validation
6. Run initial header scan from the dashboard (this may take hours for large libraries)

### Handling Failed Files

When files are flagged as failed:

1. Check the error output in the dashboard detail view
2. Common failures:
   - `"Invalid data found when processing input"` → Corrupt container
   - `"moov atom not found"` → Truncated MP4/MOV
   - `"Error while decoding stream"` → Corrupt video frames
3. Attempt repair: `ffmpeg -i broken.mkv -c copy repaired.mkv`
4. If repair fails: re-download or re-rip the source
5. After fix: trigger a rescan from the dashboard

### Database Maintenance

The SQLite database grows slowly. Occasional maintenance:

```bash
# Location
ls /var/lib/jellyfin/plugins/MediaIntegrityScanner/data/

# Vacuum to reclaim space (while Jellyfin is stopped)
sqlite3 media-integrity.db "VACUUM;"

# Check database integrity
sqlite3 media-integrity.db "PRAGMA integrity_check;"
```

### Upgrading the Plugin

1. Check the repository for new releases
2. Jellyfin's plugin auto-update handles it if installed via repository
3. For manual installs: replace the DLL files and restart

## What's Next

The plugin is deployed, monitored, and releasing on a real CI/CD pipeline — but v0.1.0 wasn't the end of the story. The [final article](/jellyfin-media-integrity-release-and-updates/) covers what production use and real testing turned up afterward: an update checker, session-aware auto-restart, a packaging bug that broke non-Linux installs, and a full future-work list of what's still being evaluated.

## Resources

- **Repository:** [github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner)
- **Issues & Feature Requests:** [GitHub Issues](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/issues)
- **Jellyfin Plugin Template:** [github.com/jellyfin/jellyfin-plugin-template](https://github.com/jellyfin/jellyfin-plugin-template)
- **CephFS Performance Tuning:** [docs.ceph.com/en/latest/cephfs/](https://docs.ceph.com/en/latest/cephfs/)
- **Jellyfin API Docs:** [api.jellyfin.org](https://api.jellyfin.org/)

## Series Navigation

1. [Introduction & Problem Statement](/jellyfin-media-integrity-scanner-introduction/)
2. [Architecture & Design Decisions](/jellyfin-media-integrity-architecture-design/)
3. [Building the Scanner Core](/jellyfin-media-integrity-scanner-core/)
4. [The Dashboard & API](/jellyfin-media-integrity-dashboard-api/)
5. **Deployment & Operations** (this post)
6. [v0.1.1 Release: Update Checker & Auto-Update](/jellyfin-media-integrity-release-and-updates/)
