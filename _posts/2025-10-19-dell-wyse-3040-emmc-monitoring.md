---
title:  "Dell Wyse 3040 eMMC Storage Health Monitoring"
layout: post
categories: [technical, hardware]
tags: [dell-wyse-3040, emmc, monitoring, storage, health, homelab]
published: true
---

I found out awhile ago that eMMC storage is a different thing entirely when it comes to health monitoring. This is especially true when you're booting from it like on the [Dell Wyse 3040s](/tags/wyse3040/) of which I have several in my homelab. The goal is to get some status information on the eMMC storage health, but the usual SMART utilities don't work on eMMC.

``` console
root@pve1:~# smartctl -H /dev/mmcblk0 -d auto
smartctl 7.3 2022-02-28 r5338 [x86_64-linux-6.8.12-1-pve] (local build)
Copyright (C) 2002-22, Bruce Allen, Christian Franke, www.smartmontools.org

/dev/mmcblk0: Unable to detect device type
Please specify device type with the -d option.
```

Turns out eMMC has its own health monitoring system that's actually pretty useful once you know how to access it. I figured I would share my experience since it took some time to figure out. Maybe this will help someone else.

<!-- excerpt-end -->

## What is eMMC?

eMMC (embedded MultiMediaCard) is basically flash storage that's soldered directly to the board. Unlike traditional SSDs, it doesn't support SMART monitoring, but it has its own health reporting system built into the [JEDEC standard](https://en.wikipedia.org/wiki/JEDEC_memory_standards).

The [Dell Wyse 3040s](/tags/wyse3040/) use 8GB eMMC for the boot drive, and since these are fanless units running 24/7, monitoring the storage health is pretty important.

## Installing eMMC Monitoring Tools

First, you need the `mmc-utils` package:

``` console
root@pve1:~# apt install mmc-utils
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following NEW packages will be installed:
  mmc-utils
0 upgraded, 1 newly installed, 0 to remove and 6 not upgraded.
Need to get 45.6 kB of archives.
After this operation, 141 kB of additional disk space will be used.
Get:1 http://deb.debian.org/debian bookworm/main amd64 mmc-utils amd64 0+git20220624.d7b343fd-1 [45.6 kB]
Fetched 45.6 kB in 0s (209 kB/s)
Selecting previously unselected package mmc-utils.
(Reading database ... 53077 files and directories currently installed.)
Preparing to unpack .../mmc-utils_0+git20220624.d7b343fd-1_amd64.deb ...
Unpacking mmc-utils (0+git20220624.d7b343fd-1) ...
Setting up mmc-utils (0+git20220624.d7b343fd-1) ...
Processing triggers for man-db (2.11.2-2) ...
```

## Basic eMMC Status Check

Check if the eMMC is responding properly:

``` console
root@pve1:~# mmc status get /dev/mmcblk0
SEND_STATUS response: 0x00000900
DEVICE STATE: TRANS
STATUS: READY_FOR_DATA
```

This shows the device is in transfer state and ready for data operations - basically healthy and operational.

## eMMC Health Monitoring

The key command for health monitoring is checking the Extended CSD (Card Specific Data):

``` console
root@pve1:~# mmc extcsd read /dev/mmcblk0 | grep -E 'LIFE|EOL'
eMMC Life Time Estimation A [EXT_CSD_DEVICE_LIFE_TIME_EST_TYP_A]: 0x01
eMMC Life Time Estimation B [EXT_CSD_DEVICE_LIFE_TIME_EST_TYP_B]: 0x02
eMMC Pre EOL information [EXT_CSD_PRE_EOL_INFO]: 0x01
```

## Understanding the Health Values

Here's what these values mean:

**Device Life Time Estimation Type A (0x01):**

- Life time estimation for the MLC user partition eraseblocks
- Provided in steps of 10%
- 0x01 means 0%-10% device life time used

**Device Life Time Estimation Type B (0x02):**

- Life time estimation for the SLC boot partition eraseblocks  
- Provided in steps of 10%
- 0x02 means 10%-20% device life time used

**Pre EOL Information (0x01):**

- Overall status for reserved blocks
- 0x01 = Normal: consumed less than 80% of reserved blocks
- 0x02 = Warning: consumed 80% of reserved blocks  
- 0x03 = Urgent: consumed 90% of reserved blocks

## What This Means for My Dell Wyse Units

My eMMC health looks pretty good:

- User partition: 0-10% wear (excellent)
- Boot partition: 10-20% wear (still very good)
- Reserved blocks: Normal status

Since these units have been running Proxmox for a while, this suggests the eMMC is holding up well under the workload.

## Creating a Simple Monitoring Script

I created a simple script to check eMMC health across my cluster:

``` bash
#!/bin/bash
# emmc-health.sh - Check eMMC health on Dell Wyse 3040s

echo "eMMC Health Check - $(date)"
echo "=================================="

if [ ! -e /dev/mmcblk0 ]; then
    echo "No eMMC device found"
    exit 1
fi

# Get health values
LIFE_A=$(mmc extcsd read /dev/mmcblk0 | grep "LIFE_TIME_EST_TYP_A" | awk '{print $NF}')
LIFE_B=$(mmc extcsd read /dev/mmcblk0 | grep "LIFE_TIME_EST_TYP_B" | awk '{print $NF}')
EOL=$(mmc extcsd read /dev/mmcblk0 | grep "PRE_EOL_INFO" | awk '{print $NF}')

echo "User Partition Wear: $LIFE_A (0x01 = 0-10%, 0x02 = 10-20%, etc.)"
echo "Boot Partition Wear: $LIFE_B"
echo "Reserved Block Status: $EOL (0x01 = Normal, 0x02 = Warning, 0x03 = Urgent)"

# Simple health assessment
if [ "$EOL" = "0x01" ] && [ "$LIFE_A" -le "0x03" ] && [ "$LIFE_B" -le "0x03" ]; then
    echo "Status: HEALTHY"
else
    echo "Status: CHECK REQUIRED"
fi
```

## Why This Matters

Unlike traditional hard drives or SSDs, eMMC doesn't give you SMART data, but the JEDEC health reporting is actually more straightforward. The 10% increments are coarse, but for homelab monitoring, knowing if you're in the "normal" range versus "warning" is usually sufficient.

For my [Dell Wyse 3040](/tags/wyse3040/) test cluster, this gives me confidence that the storage isn't wearing out prematurely under the Proxmox workload. Since these units are 150 miles away, early warning of storage issues is pretty valuable. Recently, I have converted all my [Tailscale on with Debian 12](/dell-wyse-3040-tailscale/) remote nodes running on these and want alerts if their storage is in trouble.

## References

The health monitoring was introduced in JEDEC standard revision 5.0. The [CNX Software article on eMMC wear estimation](https://www.cnx-software.com/2019/08/16/wear-estimation-emmc-flash-memory/) has good background on the technical details.

For more [Dell Wyse 3040 content](/tags/wyse3040/), check out my other posts on running [Proxmox clusters on these units](/proxmox-8-dell-wyse-3040/) or [Tailscale on with Debian 12](/dell-wyse-3040-tailscale/).
