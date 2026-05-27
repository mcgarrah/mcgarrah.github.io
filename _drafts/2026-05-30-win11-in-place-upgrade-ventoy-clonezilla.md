---
title: "Windows 11 In-Place Upgrade: Ventoy Boot Media, Clonezilla Backup, and the Nuclear Option"
image: /assets/images/win-11-error-0x80070490-001.png
layout: post
categories: [windows, troubleshooting]
tags: [windows 11, ventoy, clonezilla, in-place upgrade, sysadmin, backup, windows update, component store]
excerpt: "When DISM and SFC can't fix a corrupted Windows 11 component store, the in-place upgrade is the safest path forward — but not without a full disk backup first. Here's the complete process: resetting update components, preparing Ventoy boot media with both the Windows 11 ISO and Clonezilla, backing up the drive, and running the repair install."
description: "Part 3 of the Windows 11 repair series. After DISM/SFC failed to resolve error 0x80070490, this covers resetting Windows Update components, preparing Ventoy multi-boot USB with Windows 11 ISO and Clonezilla, creating a full disk backup before the in-place upgrade, and executing the repair install that replaces the component store while preserving files and apps."
date: 2026-05-30
last_modified_at: 2026-05-30
published: false
seo:
  type: BlogPosting
  date_published: 2026-05-30
  date_modified: 2026-05-30
---

[![Windows Update Error 0x80070490](/assets/images/win-11-error-0x80070490-001.png){:width="60%" height="60%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/win-11-error-0x80070490-001.png){:target="_blank"}

In [Part 1](/windows-11-dsm-hang/), DISM got stuck at 62.3% on one ThinkPad — that turned out to be normal behavior. In [Part 2](/win11-repair-error-0x80070490/), the *other* ThinkPad refused updates entirely with error 0x80070490, and I ran the standard DISM/SFC repair cycle hoping it would be enough.

It wasn't.

<!-- excerpt-end -->

Clean DISM and SFC runs.

```console
C:\Users\McGarrah>DISM /Online /Cleanup-Image /RestoreHealth

Deployment Image Servicing and Management tool
Version: 10.0.26100.5074

Image Version: 10.0.26200.8039

[==========================100.0%==========================] The restore operation completed successfully.
The operation completed successfully.

C:\Users\McGarrah>sfc /scannow

Beginning system scan.  This process will take some time.

Beginning verification phase of system scan.
Verification 100% complete.

Windows Resource Protection did not find any integrity violations.
```

No recent errors in `CBS.log` found.

```powershell
PS C:\Users\McGarrah> Get-Content "C:\Windows\Logs\CBS\CBS.log" | Select-String "0x80070490" | Select-Object -Last 20
PS C:\Users\McGarrah>
```

After three hours of DISM and SFC, a reboot, and another attempt at Windows Update — new error when I try to install the May 2026 Security Patches.

Screenshot: assets/images/win11-update-001.png

`Install error - 0x80028017`

Install error `0x80028017` typically occurs on Windows 11, specifically when attempting to install Insider Preview or Quality updates. It usually indicates a broken metadata issue, an incompatible Windows feature (like Windows Sandbox), or corrupted system and update caches.

The corrupted FodMetadataServicing and Windows Defender Application Guard packages are gone from the `CBS.log` but we have this new error.

```powershell
PS C:\Users\McGarrah> Get-Content "C:\Windows\Logs\CBS\CBS.log" | Select-String "0x800" | Select-Object -Last 20
PS C:\Users\McGarrah> Get-Content "C:\Windows\Logs\CBS\CBS.log" | Select-String "0x80028017" | Select-Object -Last 20
PS C:\Users\McGarrah> Get-Content "C:\Windows\Logs\CBS\CBS.log" | Select-String "0x80070490" | Select-Object -Last 20
PS C:\Users\McGarrah>
```

I have the "Windows Sandbox" Feature installed on both my systems but only use it occasionally now. It was being used extensively when I was testing software packages earlier but that slowed down. This could be the root cause of these issues.

We can try Step #1 and Step #2 below to see about cleaning up the logs and caches.

---

## Step 1: Reset Windows Update Components

Before jumping to the nuclear option, one more safe step: flushing the Windows Update cache. This clears any corrupted download state that might be blocking the update independently of the component store corruption.

Open **Command Prompt** as Administrator and run:

```cmd
net stop wuauserv
net stop cryptSvc
net stop bits
net stop msiserver
ren C:\Windows\SoftwareDistribution SoftwareDistribution.old
ren C:\Windows\System32\catroot2 catroot2.old
net start wuauserv
net start cryptSvc
net start bits
net start msiserver
```

Failed to rename the `catroot2` folder due to access denied. This is expected because it's protected by the system. However, the `SoftwareDistribution` folder was renamed successfully, which means the Windows Update cache has been cleared.

```powershell
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Users\McGarrah> net stop wuauserv
The Windows Update service is stopping.
The Windows Update service was stopped successfully.

PS C:\Users\McGarrah> net stop cryptSvc
The Cryptographic Services service is stopping..
The Cryptographic Services service could not be stopped.

PS C:\Users\McGarrah> net stop bits
The Background Intelligent Transfer Service service is stopping..
The Background Intelligent Transfer Service service was stopped successfully.

PS C:\Users\McGarrah> net stop msiserver
The Windows Installer service is not started.

More help is available by typing NET HELPMSG 3521.

PS C:\Users\McGarrah> ren C:\Windows\SoftwareDistribution SoftwareDistribution.old
PS C:\Users\McGarrah> ren C:\Windows\System32\catroot2 catroot2.old
ren : Access to the path 'C:\Windows\System32\catroot2' is denied.
At line:1 char:1
+ ren C:\Windows\System32\catroot2 catroot2.old
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : WriteError: (C:\Windows\System32\catroot2:String) [Rename-Item], IOException
    + FullyQualifiedErrorId : RenameItemIOError,Microsoft.PowerShell.Commands.RenameItemCommand

PS C:\Users\McGarrah>
```

```powershell
net stop bits
net stop wuauserv
net stop cryptsvc
```

```
PS C:\Users\McGarrah> net stop bits
The Background Intelligent Transfer Service service is not started.

More help is available by typing NET HELPMSG 3521.

PS C:\Users\McGarrah> net stop wuauserv
The Windows Update service is not started.

More help is available by typing NET HELPMSG 3521.

PS C:\Users\McGarrah> net stop cryptsvc
The Cryptographic Services service is stopping..
The Cryptographic Services service was stopped successfully.

PS C:\Users\McGarrah> ren C:\Windows\System32\catroot2 catroot2.old
PS C:\Users\McGarrah>
```

```powershell
net start wuauserv
net start cryptSvc
net start bits
net start msiserver
```

```powershell
PS C:\Users\McGarrah> net start wuauserv
The Windows Update service is starting.
The Windows Update service was started successfully.

PS C:\Users\McGarrah> net start cryptSvc
The requested service has already been started.

More help is available by typing NET HELPMSG 2182.

PS C:\Users\McGarrah> net start bits
The Background Intelligent Transfer Service service is starting..
The Background Intelligent Transfer Service service was started successfully.

PS C:\Users\McGarrah> net start msiserver
The Windows Installer service is starting.
The Windows Installer service was started successfully.
```

We have renamed and restarted all the services.  This should have both the cache and the pending updates cleared.  Let's try Windows Update again and see if it can now install the May 2026 Security Patches. Reboot and retry once more.

## Step 2: Clear the Applicability Evaluation Cache

One more low-risk attempt — clearing the registry cache that CBS uses to evaluate package applicability:

1. Press `Win + R`, type `regedit`, press Enter
2. Navigate to: `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing`
3. Look for a subkey called `ApplicabilityEvaluationCache`
4. Right-click → Delete (Windows rebuilds it on next reboot)
5. Reboot and try Windows Update again

If this doesn't resolve it either, we're past the point of incremental fixes. The component store itself needs to be replaced wholesale.

Time to escalate, but with a safety net. I'm skipping the risky package removal (Step 3 from Part 2) entirely and going straight to the in-place upgrade — but not before backing up the entire disk.

## Why I'm Skipping Step 3 (Package Removal)

In [Part 2](/win11-repair-error-0x80070490/), I outlined the option of force-removing the corrupted `FodMetadataServicing` package with DISM. I'm deliberately skipping this. The [first article in this series](/windows-11-dsm-hang/) documents how removing FodMetadataServicing packages on 24H2 has been known to brick the system entirely. The risk-reward ratio is terrible — if it works, great, but if it doesn't, I'm looking at a full reinstall with no backout path.

Instead, I'm going straight to the in-place upgrade, which replaces the entire component store cleanly. But first — a backup. Because even the "safe" nuclear option can go wrong.

## Preparing Ventoy Boot Media

[Ventoy](https://www.ventoy.net/) is a tool that turns a USB drive into a multi-boot device. You copy ISO files onto it and boot from whichever one you need. No burning, no reformatting — just drag and drop. This gives us a single USB stick with both the Windows 11 installer and Clonezilla for backup.

### Download Ventoy

TODO: Document Ventoy download and USB preparation

### Download the Windows 11 ISO

TODO: Document getting the official Windows 11 ISO from Microsoft

- Media Creation Tool vs direct ISO download
- Which edition (matching the installed edition)
- Version considerations for 24H2

### Download Clonezilla

TODO: Document Clonezilla ISO download
- Which version (stable vs alternative)
- AMD64 zip vs ISO

### Setting Up the Ventoy USB

TODO: Document copying ISOs to the Ventoy drive

## Backing Up with Clonezilla

Before touching the Windows installation, I want a full disk image I can restore if everything goes sideways. Clonezilla creates a sector-level backup of the entire drive — not just files, but partition tables, boot records, and the component store itself.

### Boot into Clonezilla

TODO: Document booting from Ventoy into Clonezilla

### Create the Disk Image

TODO: Document Clonezilla disk-to-image backup process
- Target drive selection (external USB drive or NAS)
- Compression options
- Verification step

### Verify the Backup

TODO: Document verifying the Clonezilla image is restorable

## The In-Place Upgrade

With a verified backup in hand, the in-place upgrade becomes a safe operation. If it fails or makes things worse, we restore from the Clonezilla image and we're back to exactly where we started.

### Running setup.exe

TODO: Document the in-place upgrade process
1. Boot into Windows normally
2. Mount the Windows 11 ISO (or boot from Ventoy)
3. Run `setup.exe`
4. Select "Keep personal files and apps"
5. Wait for the upgrade to complete (typically 30-60 minutes)

### Post-Upgrade Verification

TODO: Document verification steps
- Windows Update succeeds
- CBS.log no longer shows 0x80070490 errors
- All applications still work
- Driver state is healthy

## Lessons Learned

TODO: Document what this whole experience taught about:
- The importance of backout plans before any system repair
- Why incremental fixes have diminishing returns on deeply corrupted systems
- Ventoy as a permanent tool in the sysadmin toolkit
- The value of Clonezilla for pre-repair snapshots

---

*This is Part 3 of the Windows 11 system repair series:*
- *Part 1: [DISM RestoreHealth Stuck at 62.3%](/windows-11-dsm-hang/)*
- *Part 2: [Windows 11 Update Error 0x80070490](/win11-repair-error-0x80070490/)*
- *Part 3: In-Place Upgrade with Ventoy and Clonezilla (this article)*
