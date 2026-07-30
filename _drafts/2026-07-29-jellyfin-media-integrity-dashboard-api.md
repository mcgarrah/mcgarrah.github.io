---
layout: post
title: "Jellyfin Media Integrity Scanner: The Dashboard & API"
image: /assets/images/og/jellyfin-media-integrity-dashboard-api.png
categories: [homelab, media-server]
tags: [jellyfin, media-integrity, rest-api, dashboard, html, javascript, plugin-development]
excerpt: "A scanner that runs in the background is only useful if you can see its results. This article implements the REST API controller and admin dashboard for the Jellyfin Media Integrity Scanner — turning raw scan data into actionable library health visibility."
description: "Implementing the REST API and admin dashboard for the Jellyfin Media Integrity Scanner plugin. Covers the ASP.NET Core controller, scan result queries, manual scan triggers, and the HTML/JavaScript dashboard with library health overview. Part 4 of a 5-part development series."
date: 2026-07-29
last_modified_at: 2026-07-29
seo:
  type: BlogPosting
  date_published: 2026-07-29
  date_modified: 2026-07-29
---

The [scanner core](/jellyfin-media-integrity-scanner-core/) handles the detection work — finding corrupt files and recording results in SQLite. But a scanner that runs silently in the background is only half the solution. Admins need to see what's broken, when it was scanned, and have the ability to trigger scans on demand.

<!-- excerpt-end -->

> **Implementation status:** The REST API controller and dashboard code in this article represent the target implementation. The [v0.1.0 release](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/releases/tag/v0.1.0) includes a placeholder dashboard HTML but not yet the functional API controller or live data integration shown here.

This is Part 4 of the [Jellyfin Media Integrity Scanner](/jellyfin-media-integrity-scanner-introduction/) development series.

## REST API Controller

The API controller exposes scan results, status, and manual triggers through Jellyfin's built-in HTTP pipeline:

```csharp
using Microsoft.AspNetCore.Mvc;
using MediaBrowser.Controller.Net;

namespace Jellyfin.Plugin.MediaIntegrityScanner.Api;

[ApiController]
[Route("MediaIntegrity")]
public class MediaIntegrityController : ControllerBase
{
    private readonly IDatabaseManager _db;
    private readonly IScanEngine _scanner;
    private readonly ILibraryManager _library;

    public MediaIntegrityController(
        IDatabaseManager db,
        IScanEngine scanner,
        ILibraryManager library)
    {
        _db = db;
        _scanner = scanner;
        _library = library;
    }

    /// <summary>
    /// Get overall scan status and statistics.
    /// </summary>
    [HttpGet("Status")]
    [Authorize(Policy = "RequiresElevation")]
    public async Task<ActionResult<ScanStatusResponse>> GetStatus()
    {
        var stats = await _db.GetStatisticsAsync();
        return Ok(new ScanStatusResponse
        {
            IsScanning = _scanner.IsScanning,
            TotalFiles = stats.TotalFiles,
            ScannedFiles = stats.ScannedFiles,
            PassedFiles = stats.PassedFiles,
            FailedFiles = stats.FailedFiles,
            PendingFiles = stats.PendingFiles,
            LastScanTimestamp = stats.LastScanTimestamp,
            HealthPercentage = stats.ScannedFiles > 0
                ? Math.Round(
                    (double)stats.PassedFiles / stats.ScannedFiles * 100, 1)
                : 0
        });
    }

    /// <summary>
    /// Get scan results with filtering and pagination.
    /// </summary>
    [HttpGet("Results")]
    [Authorize(Policy = "RequiresElevation")]
    public async Task<ActionResult<PagedResultResponse>> GetResults(
        [FromQuery] ScanStatus? status = null,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 50,
        [FromQuery] string? libraryId = null)
    {
        var results = await _db.GetResultsAsync(
            status, page, pageSize, libraryId);

        return Ok(new PagedResultResponse
        {
            Items = results.Items,
            TotalCount = results.TotalCount,
            Page = page,
            PageSize = pageSize
        });
    }

    /// <summary>
    /// Get details for a specific item's scan history.
    /// </summary>
    [HttpGet("Results/{itemId}")]
    [Authorize(Policy = "RequiresElevation")]
    public async Task<ActionResult<ItemScanDetail>> GetItemDetail(
        string itemId)
    {
        var detail = await _db.GetItemDetailAsync(itemId);
        if (detail == null) return NotFound();
        return Ok(detail);
    }

    /// <summary>
    /// Trigger a manual scan for a specific item or library.
    /// </summary>
    [HttpPost("Scan")]
    [Authorize(Policy = "RequiresElevation")]
    public async Task<ActionResult> TriggerScan(
        [FromBody] ScanRequest request)
    {
        if (_scanner.IsScanning)
            return Conflict("A scan is already in progress.");

        // Fire-and-forget with cancellation support
        _ = Task.Run(async () =>
        {
            if (!string.IsNullOrEmpty(request.ItemId))
            {
                var item = _library.GetItemById(
                    Guid.Parse(request.ItemId));
                if (item != null)
                {
                    await _scanner.ScanItemAsync(
                        item,
                        request.DeepScan
                            ? ScanPhase.FullDecode
                            : ScanPhase.Header,
                        CancellationToken.None);
                }
            }
            else
            {
                await _scanner.ScanLibraryAsync(
                    request.LibraryId,
                    request.DeepScan
                        ? ScanPhase.FullDecode
                        : ScanPhase.Header,
                    CancellationToken.None);
            }
        });

        return Accepted();
    }

    /// <summary>
    /// Cancel the currently running scan.
    /// </summary>
    [HttpPost("Cancel")]
    [Authorize(Policy = "RequiresElevation")]
    public ActionResult CancelScan()
    {
        _scanner.Cancel();
        return Ok();
    }
}
```

### Request/Response Models

```csharp
public class ScanStatusResponse
{
    public bool IsScanning { get; set; }
    public int TotalFiles { get; set; }
    public int ScannedFiles { get; set; }
    public int PassedFiles { get; set; }
    public int FailedFiles { get; set; }
    public int PendingFiles { get; set; }
    public string? LastScanTimestamp { get; set; }
    public double HealthPercentage { get; set; }
}

public class ScanRequest
{
    public string? ItemId { get; set; }
    public string? LibraryId { get; set; }
    public bool DeepScan { get; set; } = false;
}
```

## Admin Dashboard

The dashboard is an embedded HTML page served through Jellyfin's plugin web page system:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Media Integrity Scanner</title>
    <style>
        .integrity-dashboard { padding: 1em 2em; font-family: inherit; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1em;
            margin: 1.5em 0;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 1.2em;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin: 0.2em 0;
        }
        .stat-label { opacity: 0.7; font-size: 0.9em; }
        .status-pass { color: #4caf50; }
        .status-fail { color: #f44336; }
        .status-pending { color: #ff9800; }
        .status-scanning { color: #2196f3; }
        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1em;
        }
        .results-table th,
        .results-table td {
            padding: 0.6em 1em;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .results-table th { opacity: 0.7; font-weight: 600; }
        .btn {
            padding: 0.5em 1.2em;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
        }
        .btn-primary { background: #00a4dc; color: white; }
        .btn-danger { background: #f44336; color: white; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .health-bar {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 1em 0;
        }
        .health-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        .filter-row {
            display: flex;
            gap: 1em;
            margin: 1em 0;
            align-items: center;
        }
    </style>
</head>
<body>
    <div class="integrity-dashboard" id="app">
        <h1>Media Integrity Scanner</h1>

        <!-- Status Overview -->
        <div class="stats-grid" id="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Library Health</div>
                <div class="stat-value status-pass" id="health-pct">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Files</div>
                <div class="stat-value" id="total-files">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Passed</div>
                <div class="stat-value status-pass" id="passed-files">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Failed</div>
                <div class="stat-value status-fail" id="failed-files">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Pending</div>
                <div class="stat-value status-pending" id="pending-files">—</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Status</div>
                <div class="stat-value status-scanning" id="scan-status">Idle</div>
            </div>
        </div>

        <div class="health-bar">
            <div class="health-bar-fill" id="health-bar"
                 style="width: 0%; background: #4caf50;"></div>
        </div>

        <!-- Controls -->
        <div class="filter-row">
            <button class="btn btn-primary" id="btn-scan-headers"
                    onclick="triggerScan(false)">
                Run Header Scan
            </button>
            <button class="btn btn-primary" id="btn-scan-deep"
                    onclick="triggerScan(true)">
                Run Deep Scan
            </button>
            <button class="btn btn-danger" id="btn-cancel"
                    onclick="cancelScan()" disabled>
                Cancel Scan
            </button>
            <select id="filter-status" onchange="loadResults()">
                <option value="">All Results</option>
                <option value="2">Failed Only</option>
                <option value="1">Passed Only</option>
                <option value="0">Pending Only</option>
            </select>
        </div>

        <!-- Results Table -->
        <table class="results-table">
            <thead>
                <tr>
                    <th>File</th>
                    <th>Status</th>
                    <th>Phase</th>
                    <th>Last Scanned</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody id="results-body">
                <tr><td colspan="5">Loading...</td></tr>
            </tbody>
        </table>

        <div class="filter-row" id="pagination"></div>
    </div>

    <script>
        const API_BASE = ApiClient.getUrl('MediaIntegrity');
        let currentPage = 1;

        async function loadStatus() {
            try {
                const resp = await ApiClient.fetch({
                    url: API_BASE + '/Status',
                    type: 'GET'
                });
                const data = JSON.parse(resp);

                document.getElementById('health-pct').textContent =
                    data.healthPercentage + '%';
                document.getElementById('total-files').textContent =
                    data.totalFiles;
                document.getElementById('passed-files').textContent =
                    data.passedFiles;
                document.getElementById('failed-files').textContent =
                    data.failedFiles;
                document.getElementById('pending-files').textContent =
                    data.pendingFiles;
                document.getElementById('scan-status').textContent =
                    data.isScanning ? 'Scanning...' : 'Idle';
                document.getElementById('health-bar').style.width =
                    data.healthPercentage + '%';
                document.getElementById('btn-cancel').disabled =
                    !data.isScanning;
            } catch (e) {
                console.error('Failed to load status:', e);
            }
        }

        async function loadResults() {
            const status = document.getElementById('filter-status').value;
            const params = new URLSearchParams({
                page: currentPage,
                pageSize: 50
            });
            if (status) params.set('status', status);

            try {
                const resp = await ApiClient.fetch({
                    url: API_BASE + '/Results?' + params.toString(),
                    type: 'GET'
                });
                const data = JSON.parse(resp);
                renderResults(data);
            } catch (e) {
                console.error('Failed to load results:', e);
            }
        }

        function renderResults(data) {
            const tbody = document.getElementById('results-body');
            if (!data.items || data.items.length === 0) {
                tbody.innerHTML =
                    '<tr><td colspan="5">No results yet. Run a scan to begin.</td></tr>';
                return;
            }

            tbody.innerHTML = data.items.map(item => `
                <tr>
                    <td title="${item.filePath}">
                        ${item.filePath.split('/').pop()}
                    </td>
                    <td class="status-${getStatusClass(item.scanStatus)}">
                        ${getStatusLabel(item.scanStatus)}
                    </td>
                    <td>Phase ${item.scanPhase}</td>
                    <td>${formatDate(item.scanTimestamp)}</td>
                    <td title="${item.errorOutput || ''}">
                        ${item.errorOutput
                            ? item.errorOutput.substring(0, 60) + '...'
                            : '—'}
                    </td>
                </tr>
            `).join('');
        }

        async function triggerScan(deep) {
            await ApiClient.fetch({
                url: API_BASE + '/Scan',
                type: 'POST',
                data: JSON.stringify({ deepScan: deep }),
                contentType: 'application/json'
            });
            setTimeout(loadStatus, 1000);
        }

        async function cancelScan() {
            await ApiClient.fetch({
                url: API_BASE + '/Cancel',
                type: 'POST'
            });
            setTimeout(loadStatus, 1000);
        }

        function getStatusClass(status) {
            return ['pending', 'pass', 'fail', 'fail'][status] || 'pending';
        }

        function getStatusLabel(status) {
            return ['Pending', 'Pass', 'Fail', 'Error'][status] || 'Unknown';
        }

        function formatDate(iso) {
            if (!iso) return '—';
            return new Date(iso).toLocaleString();
        }

        // Initial load and refresh interval
        loadStatus();
        loadResults();
        setInterval(loadStatus, 10000);
    </script>
</body>
</html>
```

## API Usage Examples

### Check library health from the command line

```bash
# Get overall status
curl -s http://localhost:8096/MediaIntegrity/Status \
  -H "X-Emby-Token: YOUR_API_KEY" | jq .

# Get failed files only
curl -s "http://localhost:8096/MediaIntegrity/Results?status=2" \
  -H "X-Emby-Token: YOUR_API_KEY" | jq '.items[].filePath'

# Trigger a header scan
curl -X POST http://localhost:8096/MediaIntegrity/Scan \
  -H "X-Emby-Token: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"deepScan": false}'
```

## What's Next

The [final article](/jellyfin-media-integrity-deployment-operations/) covers deployment and operations: installing the plugin in Proxmox LXC containers, configuring for CephFS storage, setting up monitoring/alerting, and the CI/CD pipeline for plugin releases.

## Series Navigation

1. [Introduction & Problem Statement](/jellyfin-media-integrity-scanner-introduction/)
2. [Architecture & Design Decisions](/jellyfin-media-integrity-architecture-design/)
3. [Building the Scanner Core](/jellyfin-media-integrity-scanner-core/)
4. **The Dashboard & API** (this post)
5. [Deployment & Operations](/jellyfin-media-integrity-deployment-operations/)
