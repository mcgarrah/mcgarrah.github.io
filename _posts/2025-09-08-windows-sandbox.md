---
title: "Windows Sandbox for Safe Testing"
layout: post
categories: [technical]
tags: [windows, vm, sandbox]
published: true
---

I've been doing more experimental stuff on my Windows 11 laptops lately - testing sketchy PowerShell scripts, trying out random software, and generally doing things that could completely wreck my system. While I have disk images for recovery, that's a nuclear option that would cost me a day or two of rebuilding.

Turns out Windows has had a built-in solution for this exact problem: **Windows Sandbox**. It's basically a lightweight, disposable VM that resets itself every time you close it. Perfect for testing things without the paranoia.

<!-- excerpt-end -->

## What is Windows Sandbox?

Windows Sandbox is Microsoft's built-in virtualization feature that creates a lightweight, temporary desktop environment. Every time you start it, you get a clean Windows installation. When you close it, everything disappears - no persistence, no leftover files, no registry changes on your host system.

It's perfect for:

- Testing suspicious downloads
- Running PowerShell scripts that might break things
- Trying out software before committing to install it
- Debugging system-level changes
- General "what happens if I do this?" experimentation

## The Problem with Setup

The annoying part is that every time you start Sandbox, you're back to a vanilla Windows install. No Chrome, no VS Code, no Git - nothing. So I've been iterating on scripts to get my basic tooling installed quickly.

## Getting Started

First, you need to enable the Windows Sandbox feature. This requires a reboot, so plan accordingly.

### Method 1: Command Line (Fastest)

Run this in an Admin PowerShell:

``` powershell
DISM /Online /Enable-Feature /FeatureName:"Containers-DisposableClientVM" /All
```

### Method 2: GUI Method

Search for "Turn Windows features on or off" and check the "Windows Sandbox" box. Hit OK and reboot.

[![enabled feature](/assets/images/windows-sandbox-000.png "enabled features"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/windows-sandbox-000.png){:target="_blank"}

### Method 3: PowerShell Script (My Preference)

Create `enable-sandbox.ps1` and right-click to run as Admin:

``` powershell
# Check for Administrator privileges
If (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run this script as Administrator!"
    Start-Process PowerShell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    Exit
}

# Enable Windows Sandbox
Write-Host "Enabling Windows Sandbox..."
DISM /Online /Enable-Feature /FeatureName:"Containers-DisposableClientVM" /All /NoRestart
Write-Host "Windows Sandbox feature enabled. Restart your computer for changes to take effect."
```

With any of the methods above, you'll end up watching this update dialog for awhile.

[![updating](/assets/images/windows-sandbox-001.png "updating"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/windows-sandbox-001.png){:target="_blank"}

## My Sandbox Setup Script

After enabling Sandbox and rebooting, you'll have a "Windows Sandbox" app in your Start menu. The first time you run it, Windows will download and install updates, which takes a few minutes.

Once you're in the sandbox, you need to get your tools installed quickly. Here's my current setup script that installs the essentials:

### Current Setup Script (updatesandbox.cmd)

This script does three things:

1. Tweaks visual effects and desktop settings for better performance
2. Installs Chocolatey package manager
3. Installs my essential tools (Chrome, Git, VS Code, Notepad++)

``` batch
@echo off
echo Setting up Windows Sandbox environment...

:: Configuration - add or remove packages as needed
set "CHOCO_PACKAGES=googlechrome git vscode notepadplusplus 7zip"

:: Part 1: Performance tweaks and desktop setup
echo Configuring visual effects and desktop...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "New-Item -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects' -Force | Out-Null; " ^
    "Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects' -Name 'VisualFXSetting' -Value 2; " ^
    "New-Item -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel' -Force | Out-Null; " ^
    "Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel' -Name '{20D04FE0-3AEA-1069-A2D8-08002B30309D}' -Value 0"

:: Part 2: Install Chocolatey
echo Installing Chocolatey package manager...
powershell -NoProfile -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

:: Part 3: Install essential software
echo Installing software packages...
choco install %CHOCO_PACKAGES% -y

echo Setup complete! Your sandbox is ready to use.
pause
```

## How I Use It

1. **Start Windows Sandbox** from the Start menu
2. **Copy/paste the setup script** into Notepad and save as `setup.cmd`
3. **Run the script** - takes about 5-10 minutes depending on your internet
4. **Do whatever sketchy testing** I need to do
5. **Close the sandbox** when done - everything disappears

## What I'm Still Working On

The current setup works well, but I'm exploring a few improvements:

### WSB Configuration Files

Windows Sandbox supports `.wsb` configuration files that can pre-configure settings and map folders. I haven't fully explored this yet, but it could automate the setup process.

### Persistent Tool Storage

I'm considering keeping a shared folder with portable versions of tools, but that defeats some of the isolation benefits.

### PowerShell Profile

Setting up a basic PowerShell profile with useful aliases and functions for the sandbox environment.

## Useful Chocolatey Packages for Testing

Here are some packages I commonly add depending on what I'm testing:

``` batch
:: Development tools
choco install python nodejs golang

:: System utilities  
choco install sysinternals procexp wireshark

:: Text editors and IDEs
choco install sublimetext3 atom

:: Browsers for testing
choco install firefox brave

:: Network tools
choco install putty winscp
```

## Tips and Gotchas

- **Internet access**: Sandbox has full internet access, so be careful with malware testing
- **Performance**: It's surprisingly fast on modern hardware, but still a VM
- **File sharing**: You can copy/paste files between host and sandbox
- **No persistence**: Seriously, everything disappears when you close it
- **Updates**: The sandbox gets its own Windows updates on first run

## When Not to Use Sandbox

- **Long-term development**: No persistence means you lose everything
- **GPU-intensive tasks**: Limited graphics acceleration
- **Hardware testing**: Can't access most hardware directly
- **Network isolation testing**: Shares your network connection

## Wrapping Up

Windows Sandbox has become an essential tool in my testing workflow. It's not perfect - the lack of persistence means setup time every session - but for quick "will this break my system?" testing, it's fantastic.

The setup script saves me about 10 minutes each time, and I'm constantly tweaking it based on what I'm working on. Much better than the old days of hoping System Restore would save me.