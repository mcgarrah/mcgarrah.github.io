---
title:  "USB3 Thumbdrive and SMART for the Homelab"
layout: post
published: false
---

Auto device detect fails on my USB Drives

``` console
root@pve1:~# smartctl -T permissive -d scsi -A -i /dev/sda
smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.8.12-8-pve] (local build)
Copyright (C) 2002-22, Bruce Allen, Christian Franke, www.smartmontools.org

=== START OF INFORMATION SECTION ===
Vendor:               USB
Product:              SanDisk 3.2Gen1
Revision:             1.00
Compliance:           SPC-4
User Capacity:        30,784,094,208 bytes [30.7 GB]
Logical block size:   512 bytes
Serial number:        0401b215f4e1f174c906
Device type:          disk
Local Time is:        Sun Feb 16 16:26:24 2025 EST
SMART support is:     Available - device has SMART capability.
SMART support is:     Enabled
Temperature Warning:  Disabled or Not Supported

=== START OF READ SMART DATA SECTION ===
```

https://www.smartmontools.org/wiki/USB

Write a wrapper script for specific devices
https://forum.proxmox.com/threads/issues-with-hp-p420i-and-smart.79669/page-2#post-476493
