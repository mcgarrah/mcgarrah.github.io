---
title: "Essential CLI Tools for Linux System Management"
layout: post
categories: [technical, reference]
tags: [linux, cli, monitoring, tools, sysadmin, homelab]
published: true
---

After years of managing Linux systems - from my [Dell Wyse 3040 Proxmox cluster](/tags/wyse3040/) to various VMs and containers - I've accumulated a collection of command-line tools that I reach for constantly. These aren't exotic utilities, but rather the practical tools that help me figure out what's actually happening when systems misbehave.

Most of these came from those "why is this server slow?" moments where you need to quickly diagnose CPU, memory, storage, or network issues. Here's what I actually use and why.

<!-- excerpt-end -->

## The Daily Drivers

These are the tools I install on every system because I know I'll need them:

### Process and System Monitoring

**htop** - Because `top` is painful to read
```bash
sudo apt install htop
```
Better colors, easier sorting, tree view of processes. I can actually see what's eating CPU without squinting.

**btop++** - The fancy new kid on the block
```bash
sudo apt install btop
```
Like htop but with graphs and better visuals. Overkill for servers, perfect for desktop systems.

**glances** - The all-in-one dashboard
```bash
sudo apt install glances
```
Shows CPU, memory, disk, network all in one screen. Great for getting a quick system overview.

### Storage Diagnostics

**ncdu** - Disk usage that doesn't suck
```bash
sudo apt install ncdu
```
Interactive disk usage analyzer. Way better than trying to parse `du` output when you're hunting for what's filling up your disk.

**iotop** - See what's hammering your disks
```bash
sudo apt install iotop
```
Like `top` but for disk I/O. Essential when your system is grinding and you need to know which process is causing it.

**lsblk** - Clean block device listing
```bash
lsblk
```
Built-in tool that shows your storage layout clearly. Much cleaner than parsing `/proc/mounts`.

### Network Troubleshooting

**iftop** - Network traffic by connection
```bash
sudo apt install iftop
```
Shows which connections are using bandwidth. Great for "why is my internet slow?" moments.

**nethogs** - Network usage by process
```bash
sudo apt install nethogs
```
Like iotop but for network. Shows which processes are using bandwidth.

**mtr** - Better traceroute
```bash
sudo apt install mtr
```
Combines ping and traceroute. Shows packet loss and latency to each hop. Much more useful than plain traceroute.

## The Specialists

Tools I don't use daily but are invaluable for specific problems:

### Hardware Monitoring

**lm-sensors** - Temperature monitoring
```bash
sudo apt install lm-sensors
sudo sensors-detect
sensors
```
Essential for monitoring temperatures, especially on my fanless Dell Wyse units that can get toasty.

**smartctl** - Drive health monitoring
```bash
sudo apt install smartmontools
sudo smartctl -a /dev/sda
```
Check if your drives are dying before they take your data with them.

### Performance Analysis

**iperf3** - Network performance testing
```bash
sudo apt install iperf3
```
Test actual network throughput between systems. Invaluable for diagnosing network performance issues.

**ioping** - Storage latency testing
```bash
sudo apt install ioping
```
Like ping but for storage. Helps identify if storage is slow or just busy.

## Tools I've Abandoned

**atop** - Too much storage overhead
I used to love atop's historical logging, but it filled up my Dell Wyse 3040s' limited storage. The daily logs were nice but not worth 20% of my root filesystem.

**nmon** - Overkill for most tasks
Powerful but complex. I found myself using simpler tools for 90% of my needs.

## Installation Shortcuts

For new Debian/Ubuntu systems, here's my standard monitoring toolkit:

```bash
# Essential monitoring tools
sudo apt install htop iftop iotop ncdu lm-sensors smartmontools

# Network tools
sudo apt install mtr iperf3 nethogs

# Optional but useful
sudo apt install glances btop ioping
```

## When to Use What

**System feels slow?** Start with `htop` and `iotop` to see if it's CPU or disk bound.

**Network issues?** Use `mtr` to test connectivity, `iftop` to see traffic patterns, `nethogs` to find the guilty process.

**Disk full?** Run `ncdu /` and navigate to find the space hogs.

**Hardware concerns?** Check `sensors` for temperatures, `smartctl` for drive health.

**Performance testing?** Use `iperf3` for network, `ioping` for storage latency.

## The Reality

Most system problems fall into a few categories: something's using too much CPU, disk I/O is saturated, network is slow, or you're out of space. These tools help you quickly identify which category you're dealing with.

I don't use exotic monitoring solutions for my homelab. These simple CLI tools give me the information I need without the overhead of complex monitoring stacks. Sometimes the old ways are the best ways.

## References

The [Monadical - Unix System Monitoring and Diagnostic CLI Tools](https://monadical.com/posts/system-monitoring-tools.html) has a comprehensive list if you want to explore more options. I borrowed some ideas from their organization of the tools.

For my Proxmox-specific monitoring needs, I covered some of these tools in my [Dell Wyse 3040 cluster posts](/proxmox-8-dell-wyse-3040/).
