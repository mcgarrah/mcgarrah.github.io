---
layout: post
title: "Jellyfin Media Integrity Scanner: Deployment & Operations"
image: /assets/images/og/jellyfin-media-integrity-deployment-operations.png
categories: [homelab, media-server]
tags: [jellyfin, media-integrity, proxmox, ceph, deployment, ci-cd, monitoring, github-actions]
excerpt: "Getting the Media Integrity Scanner into production — installing in Proxmox LXC containers, configuring for CephFS storage, setting up monitoring and alerting, and building the CI/CD pipeline for automated plugin releases."
description: "Deploying and operating the Jellyfin Media Integrity Scanner plugin in a production homelab. Covers Proxmox LXC installation, CephFS/NFS storage configuration, monitoring with Prometheus/Grafana, alerting on failures, and GitHub Actions CI/CD for automated builds and releases. Part 5 of a 5-part development series."
date: 2026-07-29
last_modified_at: 2026-07-29
seo:
  type: BlogPosting
  date_published: 2026-07-29
  date_modified: 2026-07-29
---

The plugin is built — scanner core, SQLite persistence, REST API, admin dashboard. Now it needs to run reliably in production without causing problems. This article covers the deployment story: installing the plugin, configuring it for shared storage, monitoring its operation, and automating the release pipeline.

<!-- excerpt-end -->

> **Implementation status:** The deployment procedures, CI/CD workflows, and monitoring configurations in this article are partially operational. The GitHub Actions build and release pipelines are live and working. The Proxmox LXC provisioning, CephFS tuning, and monitoring scripts are planned for the milestone following core scanner implementation.

This is Part 5 of the [Jellyfin Media Integrity Scanner](/jellyfin-media-integrity-scanner-introduction/) development series.

## Installation Methods

### Method 1: Plugin Repository (Recommended)

Add the custom repository to Jellyfin:

1. **Dashboard → Plugins → Repositories → Add**
2. **Name:** `mcgarrah-plugins`
3. **URL:** `https://raw.githubusercontent.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/main/manifest.json`
4. **Save** → Go to **Catalog** → Install **Media Integrity Scanner**
5. **Restart Jellyfin**

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

> **Build environment note:** A dedicated Proxmox LXC container is being provisioned as the .NET 9 build and integration test environment. It will include `jellyfin-ffmpeg`, a test Jellyfin instance, and sample media files for end-to-end validation. Until operational, CI uses GitHub-hosted Ubuntu runners.

### GitHub Actions: Build & Test

```yaml
# .github/workflows/build.yml
name: Build Plugin

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET 9
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --configuration Release --no-restore

      - name: Test
        run: dotnet test --no-restore --verbosity normal

      - name: Publish
        run: dotnet publish --configuration Release --output ./artifacts

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: media-integrity-scanner
          path: ./artifacts/
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
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET 9
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'

      - name: Build Release
        run: dotnet publish --configuration Release --output ./publish

      - name: Package
        run: |
          cd publish
          zip -r ../media-integrity-scanner.zip .

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: media-integrity-scanner.zip
          generate_release_notes: true

      - name: Update manifest.json
        run: |
          # Update version and download URL in manifest
          python3 scripts/update-manifest.py ${{ github.ref_name }}
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add manifest.json
          git commit -m "Release ${{ github.ref_name }}"
          git push origin HEAD:main
```

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

## Project Roadmap

Future enhancements under consideration:

- **Prometheus metrics endpoint** — Native `/metrics` export for Grafana dashboards
- **Webhook notifications** — POST to Discord/Slack/ntfy on failures
- **Repair automation** — Attempt `ffmpeg -c copy` repair on fixable failures
- **Library-specific settings** — Different throttle profiles per library
- **Scan priority queue** — Recently added files scan first
- **CLI companion tool** — Standalone scanner using the same core logic

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
