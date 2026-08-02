---
layout: post
title: "Jellyfin Media Integrity Scanner: The Dashboard & API"
image: /assets/images/og/jellyfin-media-integrity-dashboard-api.png
categories: [homelab, media-server]
tags: [jellyfin, media-integrity, rest-api, dashboard, html, javascript, plugin-development]
excerpt: "A scanner that runs in the background is only useful if you can see its results. This article implements the REST API controller and admin dashboard for the Jellyfin Media Integrity Scanner — turning raw scan data into actionable library health visibility."
description: "Implementing the REST API and admin dashboard for the Jellyfin Media Integrity Scanner plugin. Covers the ASP.NET Core controller, scan result queries, manual scan triggers, and the HTML/JavaScript dashboard with library health overview. Part 4 of a 6-part development series."
date: 2026-07-29
last_modified_at: 2026-08-02
seo:
  type: BlogPosting
  date_published: 2026-07-29
  date_modified: 2026-08-02
---

The [scanner core](/jellyfin-media-integrity-scanner-core/) handles the detection work — finding corrupt files and recording results in SQLite. But a scanner that runs silently in the background is only half the solution. Admins need to see what's broken, when it was scanned, and have the ability to trigger scans on demand.

<!-- excerpt-end -->

> **Implementation status (updated July 31, 2026):** The REST API controller and dashboard are fully implemented and shipping. Two accuracy bugs surfaced during a later review and were fixed — see the [Status Accuracy and Library Filtering update](#update-status-accuracy-and-library-filtering) at the end of this article: `GetStatus` originally reported `TotalFiles`/`PendingFiles` straight from the scan-results table (which never reflected the real library size, and double-counted items scanned in both phases), and `libraryId` on `GET /Results` was accepted but silently ignored.

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

That `setInterval(loadStatus, 10000)` at the bottom is doing more work than it looks like. A new file landing in a watched folder while someone's mid-episode doesn't show up as a quick blip — the scan sits waiting for playback to end before it ever touches ffmpeg, and the dashboard keeps polling `IsScanning` through the whole wait:

```mermaid
%%{init: {"theme": "base", "themeVariables": {
  "actorBkg": "#17221f",
  "actorBorder": "#3e6e67",
  "actorTextColor": "#e7ede9",
  "actorLineColor": "#3e6e67",
  "signalColor": "#a8b8bd",
  "signalTextColor": "#e7ede9",
  "labelBoxBkgColor": "#2a2013",
  "labelBoxBorderColor": "#e3a857",
  "labelTextColor": "#f4d9a8",
  "loopTextColor": "#e7ede9",
  "noteBkgColor": "#1d2b27",
  "noteBorderColor": "#3e6e67",
  "noteTextColor": "#e7ede9",
  "activationBorderColor": "#5fa88f",
  "activationBkgColor": "#16332c",
  "sequenceNumberColor": "#101a18",
  "fontFamily": "monospace",
  "fontSize": "13px"
}}}%%
sequenceDiagram
    participant JF as Jellyfin Core
    participant LM as LibraryMonitor
    participant SE as ScanEngine
    participant SM as SessionManager
    participant DB as scan_results

    JF->>LM: ItemAdded (new episode copied in)
    activate LM
    LM->>LM: ScanOnItemAdded == true?
    LM->>SE: ScanItemAsync(item, Header)
    deactivate LM
    activate SE
    SE->>SE: acquire concurrency slot
    SE->>SM: any session with NowPlayingItem?
    SM-->>SE: yes, someone is watching
    loop every 30 seconds
        SE->>SM: still playing?
        SM-->>SE: yes
    end
    Note over SE: playback ends
    SM-->>SE: no
    SE->>SE: apply DelayBetweenFilesMs
    SE->>SE: ffprobe the file
    SE->>DB: SaveResultAsync(Pass, Header)
    deactivate SE
    Note over DB: the dashboard's next<br/>GET /Status reflects the new file
```

None of that shows up as a distinct dashboard state — `IsScanning` is just `true` for however long the wait plus the actual scan takes, which is why the "Status" card can sit on "Scanning..." for a lot longer than the file itself would ever take to check.

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

## Update: Status Accuracy and Library Filtering

Two things in the original `GetStatus`/`GetResults` design didn't hold up once real libraries were scanned:

**`TotalFiles`/`PendingFiles` were derived entirely from the `scan_results` table** — `COUNT(*)` over rows that are only ever written as Pass/Fail/Error (nothing ever inserts a "Pending" row), so `PendingFiles` was always `0`, and `TotalFiles` always equaled `ScannedFiles`, even on a freshly-installed library with thousands of files that hadn't been scanned yet. Worse, an item scanned in both phases (header + deep) produced two rows in `scan_results`, so `COUNT(*)` double-counted it.

The fix: `GetStatisticsAsync` now dedupes by `item_id`, keeping only the highest-`scan_phase` (most authoritative) row per item via a `ROW_NUMBER() OVER (PARTITION BY item_id ...)` window query, and adds a distinct `ErroredFiles` bucket (previously errors counted toward the total but vanished from the pass/fail breakdown). The controller then derives the real `TotalFiles` from `ILibraryManager.GetItemList(...)` — the same query shape `ScanEngine` and the scheduled tasks already use — and computes `PendingFiles = TotalFiles - ScannedFiles`. The dashboard grew an "Errored" stat card to match.

**`libraryId` on `GET /Results` was a no-op.** The API accepted the parameter, the XML doc even said "not yet implemented," and the SQL query never touched it. Fixed by resolving `libraryId` to the set of item IDs currently in that library (via the same `ILibraryManager` query, scoped with `ParentId`) in the controller, then passing that set down to a parameterized `item_id IN (...)` clause — keeping the database layer free of any dependency on Jellyfin's library structure.

## Update: A Real Settings Page

Every field in `PluginConfiguration` — throttling, quiet hours, ffmpeg path overrides, the on-add/on-remove toggles — could originally only be changed by hand-editing the plugin's XML config file on disk. There was no in-app way to configure it at all, which meant Jellyfin's admin dashboard technically listed the plugin as "configurable" without actually offering a working configuration UI.

Fixed with a second web page (`integrity_settings.html`), registered alongside the dashboard via a second `PluginPageInfo` entry in `GetPages()`. It's a straightforward form over all twelve config properties, using the same `ApiClient.getPluginConfiguration`/`updatePluginConfiguration` JS calls Jellyfin's own plugin pages use to load and save. One gotcha worth flagging: the settings page's JS has to address the plugin by its **dashless** GUID (`c8f4a3b21d5e4f6a9b7c2e8d0f1a3b5c`, no hyphens) — Jellyfin 10.11.11's `/Plugins/{id}/Configuration` routes 404 on the canonical hyphenated form. The dashboard and settings pages now cross-link to each other via `configurationpage?name=...`.

## Update: The Dashboard Was Reading the Wrong JSON Casing

This one is worth calling out plainly: **the dashboard likely never rendered real data in any live browser session.** Its JS reads `data.isScanning`, `data.totalFiles`, `item.filePath`, and so on — camelCase, which is the ASP.NET Core default for JSON responses. But Jellyfin's host doesn't apply that default to controller output; it serializes using the raw C# property names, so a real `/MediaIntegrity/Status` response looks like `{"IsScanning":false,"TotalFiles":1,...}` — PascalCase. Every field read in `loadStatus`, `renderResults`, and `renderPagination` was silently reading `undefined`.

This surfaced only once an integration test piped a real response through `jq` and the PascalCase keys were staring back. Worth noting the asymmetry: incoming request bodies deserialize case-*insensitively* (the dashboard's own `triggerScan()` already sent `{ deepScan: deep }` and it correctly bound to `ScanRequest.DeepScan`), so only the outgoing side needed the fix. The settings page above was unaffected, since its JS was written by copying the C# `PluginConfiguration` property names directly — which happened to already be PascalCase.

Every `data.`/`item.` field access in the dashboard is now PascalCase, verified against a real Jellyfin 10.11.11 instance end-to-end (trigger a scan, poll status, render results) rather than just by reading the diff.

## Update: The Dashboard Was Never Actually Reachable in a Real Browser

The PascalCase fix above turned out not to be the whole story. Building a Playwright suite to drive this plugin's pages through an actual browser — not curl+grep, not a REST call — surfaced something more fundamental: **both config pages had likely never rendered at all in a genuine admin session.**

Jellyfin's classic (non-React) admin dashboard doesn't navigate to a plugin's config page the way a browser normally would. It fetches the page's HTML via AJAX through an internal `loadView`/`ViewManager` mechanism and injects the result as a *fragment* into the already-running single-page app — which is what supplies the global `ApiClient`/`Dashboard` objects this page's own JS depends on. Both `integrity_dashboard.html` and `integrity_settings.html` were written as full standalone documents (`<!DOCTYPE html><html><head>...<body>`), and that structural mismatch broke two different ways depending on how you reached the page:

- A direct URL (`.../configurationpage?name=...`) forces a real top-level page load, which never gets `ApiClient` injected: `ReferenceError: ApiClient is not defined`.
- A genuine in-app click on the plugin's own auto-generated "Settings" link instead throws inside *Jellyfin's own bundled code* — `Cannot read properties of undefined (reading 'classList')` in `Object.loadView` — because it's trying to graft a full document into the DOM where it expects a content fragment.

Both are the same root cause, confirmed via two distinct real stack traces, not two separate bugs. There's no public documentation for the expected fragment shape (this plugin ships with no external API access during development), so it was reverse-engineered by inspecting a real rendered session: wrap the content in `<div id="...Page" data-role="page" class="page type-interior pluginConfigurationPage"><div data-role="content" class="content-primary">...</div></div>`, with no `<!DOCTYPE>`/`<html>`/`<head>`/`<body>`/`<title>` wrapper.

Fixing the structure surfaced two smaller, related issues in the same pass:
- The pages' own internal cross-links (dashboard's "Settings »", settings' "« Back to Dashboard") used plain relative `href`s with no SPA hash prefix — clicking either one forced the exact same full-page-load path and reproduced `ApiClient is not defined`, even after the fragment fix. Jellyfin's own auto-generated links use `href="#/configurationpage?name=..."`; ours needed the same `#/` prefix.
- Those same nav links, positioned with `float: right`, sat directly underneath Jellyfin's fixed app-bar header on this Jellyfin version's React-based chrome — a real click-target problem for actual users, confirmed by bounding-box inspection, not just a browser-automation artifact. Fixed with more top padding on the page container.

Worth flagging as expected behavior rather than a bug: Jellyfin's `ViewManager` hides a previously-visited page (`display:none`) instead of removing it from the DOM when you navigate back to it, re-injecting a fresh copy — including a fresh copy of the page's own `<script>` block — on every visit. Each visit's `setInterval(loadStatus, 10000)` polling loop keeps running on the hidden, stale copy too. Harmless for a user (only the visible copy is ever read), but worth knowing if you're writing your own plugin-page tests against a classic Jellyfin dashboard page: scope element lookups to the visible page rather than a bare `#id`, since Jellyfin doesn't guarantee that ID stays unique for long.

## Update: An In-Plugin Update Checker

Running a demo instance on an LXC surfaced an obvious gap: nothing told an admin a newer build existed, and updating meant manually rebuilding and redeploying the DLL by hand. The fix leans on Jellyfin's own machinery rather than reinventing it — the same `IInstallationManager` interface Dashboard > Plugins > Catalog uses internally to list and install plugin versions, injected into a new plugin service exactly the way `ILibraryManager` already is in the controller. Its shape (confirmed by reflecting against the real Jellyfin 10.11.11 server assemblies rather than guessing from memory, since this plugin has no live internet access during development) is close to what you'd expect: `GetAvailablePackages` returns everything Jellyfin currently knows about across every registered plugin repository, `FilterPackages` narrows that down to one plugin by GUID, and `InstallPackage` triggers a real install using the exact same code path the Catalog page's own "Update" button does.

**The one hard constraint this whole feature sits on top of**: `IInstallationManager` only ever sees packages from repositories an admin has *already registered* under Dashboard > Plugins > Repositories. A plugin has no way to discover its own updates from a manifest Jellyfin doesn't know about — and this plugin deliberately doesn't write to that registration list on its own behalf, since it's global server config, not this plugin's own. That's a one-time, explicit setup step for whoever runs it, documented on the settings page itself rather than hidden.

That constraint is also what shaped the **stable vs. development channel** design. Since a registered repository can list many versions, and Jellyfin doesn't have a first-class idea of "channels," this plugin publishes two separate manifests — the existing `manifest.json` (stable, updated on tagged releases) and a new `manifest-unstable.json` (development builds, cut automatically on every push to `main` — more on that in the [deployment article](/jellyfin-media-integrity-deployment-operations/#update-automated-development-releases)). Each `VersionInfo` Jellyfin returns carries a `RepositoryUrl` stamped from whichever registered repository it came from, so the plugin classifies "stable" vs. "dev" by matching that URL against two configurable settings fields, rather than trusting a repository's free-text display name (which an admin could label anything).

One assumption that turned out to be wrong, caught only by hitting the real endpoints rather than trusting the usual ASP.NET Core default: **Jellyfin serializes this plugin's new channel enum as its string name** (`"Stable"`/`"Development"`), not the underlying `0`/`1` a bare `System.Text.Json` setup would produce. Both the dashboard's new version banner and the settings page's channel dropdown are written against that string, confirmed by POSTing both a string and (hypothetically) an int body directly against the live endpoint rather than assuming either would work.

The dashboard now shows the running version plus, when a newer one exists for the configured channel, an "Update Available" banner with a one-click "Update Now" button; settings gained the channel dropdown and the two manifest-URL overrides. A daily scheduled task keeps the check result cached so opening the dashboard doesn't fire a network call every time.

## What's Next

The [final article](/jellyfin-media-integrity-deployment-operations/) covers deployment and operations: installing the plugin in Proxmox LXC containers, configuring for CephFS storage, setting up monitoring/alerting, and the CI/CD pipeline for plugin releases.

## Series Navigation

1. [Introduction & Problem Statement](/jellyfin-media-integrity-scanner-introduction/)
2. [Architecture & Design Decisions](/jellyfin-media-integrity-architecture-design/)
3. [Building the Scanner Core](/jellyfin-media-integrity-scanner-core/)
4. **The Dashboard & API** (this post)
5. [Deployment & Operations](/jellyfin-media-integrity-deployment-operations/)
6. [v0.1.1 Release: Update Checker & Auto-Update](/jellyfin-media-integrity-release-and-updates/)
