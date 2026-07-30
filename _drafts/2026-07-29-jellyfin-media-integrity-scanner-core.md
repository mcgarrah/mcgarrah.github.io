---
layout: post
title: "Jellyfin Media Integrity Scanner: Building the Scanner Core"
image: /assets/images/og/jellyfin-media-integrity-scanner-core.png
categories: [homelab, media-server]
tags: [jellyfin, media-integrity, ffmpeg, dotnet, csharp, plugin-development, cross-platform]
excerpt: "Implementing the scanner engine — FFmpeg process management, bounded task queues, cross-platform binary resolution, and the .NET 8 plugin structure that ties it all together."
description: "Building the core scanning engine for the Jellyfin Media Integrity Scanner plugin. Covers .NET 8 plugin scaffolding, FFmpeg process wrapper, bounded concurrent task queue, cross-platform path resolution, and production-safe error handling. Part 3 of a 5-part development series."
date: 2026-07-29
last_modified_at: 2026-07-29
seo:
  type: BlogPosting
  date_published: 2026-07-29
  date_modified: 2026-07-29
---

The [architecture article](/jellyfin-media-integrity-architecture-design/) laid out the design decisions — two-phase scanning, I/O throttling, SQLite persistence, event-driven updates. This article implements the core: the plugin skeleton, FFmpeg integration, and the bounded scan engine.

<!-- excerpt-end -->

> **Implementation status:** The code in this article represents the target implementation for the scanner core. The [v0.1.0 release](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner/releases/tag/v0.1.0) contains the plugin scaffold (interfaces, models, and project structure) but not yet the full implementations shown here. These are being built in the next development milestone.

This is Part 3 of the [Jellyfin Media Integrity Scanner](/jellyfin-media-integrity-scanner-introduction/) development series.

## Project Structure

Following the [jellyfin-plugin-template](https://github.com/jellyfin/jellyfin-plugin-template) pattern:

> **Build environment note:** The .NET 9 SDK build environment is being provisioned as a dedicated Proxmox LXC container with `jellyfin-ffmpeg` installed for integration testing. Until that's operational, project structure validation runs via GitHub Actions on hosted runners.

```
jellyfin-plugin-media-integrity-scanner/
├── Jellyfin.Plugin.MediaIntegrityScanner/
│   ├── Plugin.cs                    # Plugin entry point
│   ├── PluginConfiguration.cs       # User-configurable settings
│   ├── ScheduledTasks/
│   │   ├── HeaderScanTask.cs        # Phase 1 scheduled task
│   │   └── DeepScanTask.cs          # Phase 2 scheduled task
│   ├── Scanner/
│   │   ├── IScanEngine.cs           # Scanner interface
│   │   ├── ScanEngine.cs            # Bounded, throttled scan orchestrator
│   │   ├── FfmpegWrapper.cs         # FFmpeg/ffprobe process management
│   │   ├── FfmpegResolver.cs        # Cross-platform binary resolution
│   │   └── ScanResult.cs            # Result model
│   ├── Data/
│   │   ├── IDatabaseManager.cs      # Database interface
│   │   ├── SqliteDatabaseManager.cs # SQLite implementation
│   │   └── Models/
│   │       └── ScanRecord.cs        # Database entity
│   ├── EventHandlers/
│   │   └── LibraryMonitor.cs        # ItemAdded/Removed hooks
│   ├── Api/
│   │   └── MediaIntegrityController.cs  # REST API
│   └── Web/
│       └── integrity_dashboard.html # Admin UI
├── Jellyfin.Plugin.MediaIntegrityScanner.csproj
├── Jellyfin.Plugin.MediaIntegrityScanner.sln
├── Directory.Build.props
├── .github/workflows/build.yml
└── manifest.json
```

## Plugin Entry Point

The plugin registers its services with Jellyfin's dependency injection:

```csharp
using MediaBrowser.Common.Plugins;
using MediaBrowser.Model.Plugins;
using Microsoft.Extensions.DependencyInjection;

namespace Jellyfin.Plugin.MediaIntegrityScanner;

public class Plugin : BasePlugin<PluginConfiguration>,
    IHasWebPages
{
    public Plugin(
        IApplicationPaths applicationPaths,
        IXmlSerializer xmlSerializer)
        : base(applicationPaths, xmlSerializer)
    {
        Instance = this;
    }

    public static Plugin? Instance { get; private set; }

    public override string Name => "Media Integrity Scanner";
    public override string Description =>
        "Validates media file integrity using FFmpeg. " +
        "Detects corrupt, truncated, and damaged files.";
    public override Guid Id =>
        Guid.Parse("c8f4a3b2-1d5e-4f6a-9b7c-2e8d0f1a3b5c");

    public IEnumerable<PluginPageInfo> GetPages()
    {
        return new[]
        {
            new PluginPageInfo
            {
                Name = "Media Integrity",
                EmbeddedResourcePath = GetType().Namespace + ".Web.integrity_dashboard.html"
            }
        };
    }
}
```

## Plugin Configuration

```csharp
using MediaBrowser.Model.Plugins;

namespace Jellyfin.Plugin.MediaIntegrityScanner;

public class PluginConfiguration : BasePluginConfiguration
{
    // Scanning behavior
    public int MaxConcurrentScans { get; set; } = 1;
    public int DelayBetweenFilesMs { get; set; } = 5000;
    public bool PauseDuringPlayback { get; set; } = true;
    public bool EnableDeepScan { get; set; } = false;

    // Throttling
    public int MaxReadRateMbPerSec { get; set; } = 10;

    // Scheduling
    public bool UseQuietHoursOnly { get; set; } = false;
    public string QuietHoursStart { get; set; } = "02:00";
    public string QuietHoursEnd { get; set; } = "06:00";

    // FFmpeg
    public string? FfmpegPathOverride { get; set; }
    public string? FfprobePathOverride { get; set; }

    // Event-driven scanning
    public bool ScanOnItemAdded { get; set; } = true;
    public bool PurgeOnItemRemoved { get; set; } = true;
}
```

## FFmpeg Binary Resolution

The cross-platform resolver finds ffmpeg regardless of installation method:

```csharp
namespace Jellyfin.Plugin.MediaIntegrityScanner.Scanner;

public class FfmpegResolver
{
    private readonly IServerConfigurationManager _config;
    private readonly ILogger<FfmpegResolver> _logger;

    public FfmpegResolver(
        IServerConfigurationManager config,
        ILogger<FfmpegResolver> logger)
    {
        _config = config;
        _logger = logger;
    }

    public string ResolveFfmpegPath()
    {
        // 1. User override from plugin config
        var pluginConfig = Plugin.Instance?.Configuration;
        if (!string.IsNullOrEmpty(pluginConfig?.FfmpegPathOverride))
        {
            if (File.Exists(pluginConfig.FfmpegPathOverride))
                return pluginConfig.FfmpegPathOverride;

            _logger.LogWarning(
                "Configured ffmpeg path not found: {Path}",
                pluginConfig.FfmpegPathOverride);
        }

        // 2. Jellyfin's own configured ffmpeg
        var serverFfmpeg = _config.GetEncodingOptions().EncoderAppPath;
        if (!string.IsNullOrEmpty(serverFfmpeg) && File.Exists(serverFfmpeg))
            return serverFfmpeg;

        // 3. Platform-specific known locations
        var candidates = GetPlatformCandidates();
        foreach (var candidate in candidates)
        {
            if (File.Exists(candidate))
                return candidate;
        }

        // 4. PATH lookup
        var pathResult = FindInPath("ffmpeg");
        if (pathResult != null)
            return pathResult;

        throw new InvalidOperationException(
            "FFmpeg not found. Install ffmpeg or configure the path " +
            "in Media Integrity Scanner settings.");
    }

    private static IEnumerable<string> GetPlatformCandidates()
    {
        if (OperatingSystem.IsLinux())
        {
            yield return "/usr/lib/jellyfin-ffmpeg/ffmpeg";
            yield return "/usr/bin/ffmpeg";
            yield return "/usr/local/bin/ffmpeg";
        }
        else if (OperatingSystem.IsWindows())
        {
            yield return Path.Combine(
                Environment.GetFolderPath(
                    Environment.SpecialFolder.CommonApplicationData),
                "Jellyfin", "Server", "ffmpeg.exe");
            yield return @"C:\ffmpeg\bin\ffmpeg.exe";
        }
        else if (OperatingSystem.IsMacOS())
        {
            yield return "/opt/homebrew/bin/ffmpeg";
            yield return "/usr/local/bin/ffmpeg";
        }
    }

    private static string? FindInPath(string executable)
    {
        var pathVar = Environment.GetEnvironmentVariable("PATH");
        if (string.IsNullOrEmpty(pathVar)) return null;

        var separator = OperatingSystem.IsWindows() ? ';' : ':';
        var extension = OperatingSystem.IsWindows() ? ".exe" : "";

        return pathVar.Split(separator)
            .Select(dir => Path.Combine(dir, executable + extension))
            .FirstOrDefault(File.Exists);
    }
}
```

## The Scan Engine

The bounded, thread-safe scan engine processes files sequentially with configurable throttling:

```csharp
namespace Jellyfin.Plugin.MediaIntegrityScanner.Scanner;

public class ScanEngine : IScanEngine, IDisposable
{
    private readonly SemaphoreSlim _scanLock;
    private readonly FfmpegWrapper _ffmpeg;
    private readonly IDatabaseManager _db;
    private readonly ISessionManager _sessions;
    private readonly ILogger<ScanEngine> _logger;
    private CancellationTokenSource? _cts;

    public ScanEngine(
        FfmpegWrapper ffmpeg,
        IDatabaseManager db,
        ISessionManager sessions,
        ILogger<ScanEngine> logger)
    {
        _ffmpeg = ffmpeg;
        _db = db;
        _sessions = sessions;
        _logger = logger;

        var config = Plugin.Instance?.Configuration;
        _scanLock = new SemaphoreSlim(
            config?.MaxConcurrentScans ?? 1);
    }

    public bool IsScanning { get; private set; }

    public async Task ScanItemAsync(
        BaseItem item,
        ScanPhase phase,
        CancellationToken cancellationToken)
    {
        await _scanLock.WaitAsync(cancellationToken);
        try
        {
            // Check playback pause
            if (ShouldPauseForPlayback())
            {
                _logger.LogInformation(
                    "Pausing scan — active playback detected");
                await WaitForPlaybackEnd(cancellationToken);
            }

            // Apply inter-file delay
            var config = Plugin.Instance?.Configuration;
            var delay = config?.DelayBetweenFilesMs ?? 5000;
            await Task.Delay(delay, cancellationToken);

            // Execute scan
            var result = phase switch
            {
                ScanPhase.Header => await _ffmpeg.ProbeAsync(
                    item.Path, cancellationToken),
                ScanPhase.FullDecode => await _ffmpeg.DecodeAsync(
                    item.Path, cancellationToken),
                _ => throw new ArgumentException(
                    $"Unknown phase: {phase}")
            };

            // Persist result
            await _db.SaveResultAsync(new ScanRecord
            {
                ItemId = item.Id.ToString(),
                FilePath = item.Path,
                FileSize = new FileInfo(item.Path).Length,
                LastModified = File.GetLastWriteTimeUtc(item.Path)
                    .ToString("O"),
                ScanPhase = (int)phase,
                ScanStatus = result.Success
                    ? (int)ScanStatus.Pass
                    : (int)ScanStatus.Fail,
                ScanTimestamp = DateTime.UtcNow.ToString("O"),
                ErrorOutput = result.ErrorOutput,
                ScanDurationMs = result.DurationMs
            });
        }
        finally
        {
            _scanLock.Release();
        }
    }

    private bool ShouldPauseForPlayback()
    {
        var config = Plugin.Instance?.Configuration;
        if (config?.PauseDuringPlayback != true) return false;

        return _sessions.Sessions
            .Any(s => s.NowPlayingItem != null);
    }

    private async Task WaitForPlaybackEnd(
        CancellationToken cancellationToken)
    {
        while (ShouldPauseForPlayback() &&
               !cancellationToken.IsCancellationRequested)
        {
            await Task.Delay(
                TimeSpan.FromSeconds(30), cancellationToken);
        }
    }

    public void Dispose()
    {
        _scanLock.Dispose();
        _cts?.Dispose();
    }
}
```

## FFmpeg Process Wrapper

```csharp
namespace Jellyfin.Plugin.MediaIntegrityScanner.Scanner;

public class FfmpegWrapper
{
    private readonly string _ffmpegPath;
    private readonly string _ffprobePath;
    private readonly ILogger<FfmpegWrapper> _logger;

    public FfmpegWrapper(
        FfmpegResolver resolver,
        ILogger<FfmpegWrapper> logger)
    {
        _ffmpegPath = resolver.ResolveFfmpegPath();
        _ffprobePath = resolver.ResolveFfprobePath();
        _logger = logger;
    }

    /// <summary>
    /// Phase 1: Quick header/metadata validation via ffprobe.
    /// </summary>
    public async Task<ScanResult> ProbeAsync(
        string filePath, CancellationToken ct)
    {
        var sw = Stopwatch.StartNew();
        var args = $"-v error -show_entries format=duration,size " +
                   $"-show_entries stream=codec_type,codec_name " +
                   $"-of json \"{filePath}\"";

        var (exitCode, _, stderr) = await RunProcessAsync(
            _ffprobePath, args, ct);

        sw.Stop();
        return new ScanResult
        {
            Success = exitCode == 0 &&
                      string.IsNullOrWhiteSpace(stderr),
            ErrorOutput = stderr,
            DurationMs = (int)sw.ElapsedMilliseconds
        };
    }

    /// <summary>
    /// Phase 2: Full decode — reads every frame, outputs nothing.
    /// </summary>
    public async Task<ScanResult> DecodeAsync(
        string filePath, CancellationToken ct)
    {
        var sw = Stopwatch.StartNew();
        var args = $"-v error -i \"{filePath}\" -f null -";

        var (exitCode, _, stderr) = await RunProcessAsync(
            _ffmpegPath, args, ct);

        sw.Stop();
        return new ScanResult
        {
            Success = exitCode == 0 &&
                      string.IsNullOrWhiteSpace(stderr),
            ErrorOutput = stderr,
            DurationMs = (int)sw.ElapsedMilliseconds
        };
    }

    private static async Task<(int ExitCode, string Stdout, string Stderr)>
        RunProcessAsync(string exe, string args, CancellationToken ct)
    {
        using var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = exe,
                Arguments = args,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            }
        };

        process.Start();

        var stdoutTask = process.StandardOutput.ReadToEndAsync(ct);
        var stderrTask = process.StandardError.ReadToEndAsync(ct);

        await process.WaitForExitAsync(ct);

        return (
            process.ExitCode,
            await stdoutTask,
            await stderrTask
        );
    }
}
```

## Scheduled Task Registration

```csharp
namespace Jellyfin.Plugin.MediaIntegrityScanner.ScheduledTasks;

public class HeaderScanTask : IScheduledTask
{
    private readonly ILibraryManager _library;
    private readonly IScanEngine _scanner;
    private readonly IDatabaseManager _db;

    public string Name => "Media Integrity - Header Scan";
    public string Key => "MediaIntegrityHeaderScan";
    public string Description =>
        "Quick validation of media file headers and metadata.";
    public string Category => "Media Integrity";

    public IEnumerable<TaskTriggerInfo> GetDefaultTriggers()
    {
        return new[]
        {
            new TaskTriggerInfo
            {
                Type = TaskTriggerInfo.TriggerDaily,
                TimeOfDayTicks = TimeSpan.FromHours(3).Ticks
            }
        };
    }

    public async Task ExecuteAsync(
        IProgress<double> progress,
        CancellationToken cancellationToken)
    {
        var items = _library.GetItemList(new InternalItemsQuery
        {
            MediaTypes = new[] { MediaType.Video, MediaType.Audio },
            IsVirtualItem = false
        });

        var total = items.Count;
        var processed = 0;

        foreach (var item in items)
        {
            cancellationToken.ThrowIfCancellationRequested();

            // Skip if already scanned and file unchanged
            if (await _db.IsCurrentAsync(item.Id.ToString(), item.Path))
            {
                processed++;
                progress.Report((double)processed / total * 100);
                continue;
            }

            await _scanner.ScanItemAsync(
                item, ScanPhase.Header, cancellationToken);

            processed++;
            progress.Report((double)processed / total * 100);
        }
    }
}
```

## What's Next

The [next article](/jellyfin-media-integrity-dashboard-api/) adds the admin-facing layer: the REST API controller for querying scan results and triggering scans, and the HTML dashboard that gives at-a-glance library health visibility.

## Series Navigation

1. [Introduction & Problem Statement](/jellyfin-media-integrity-scanner-introduction/)
2. [Architecture & Design Decisions](/jellyfin-media-integrity-architecture-design/)
3. **Building the Scanner Core** (this post)
4. [The Dashboard & API](/jellyfin-media-integrity-dashboard-api/)
5. [Deployment & Operations](/jellyfin-media-integrity-deployment-operations/)
