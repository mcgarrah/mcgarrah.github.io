---
title: "Proxmox 8 Lessons Learned in the Homelab"
layout: post
categories: [technical, homelab]
tags: [proxmox, ceph, virtualization, homelab, storage, clustering]
---

I've been running Proxmox in my homelab since version 7.4, and the journey to Proxmox 8.2.2 was to say the least... educational. Let me share some hard-won lessons that might save you some headaches. These even apply to the Proxmox 9 upgrades as well which I have not scheduled in my cluster yet. I'm pretty sure I'll have updates when I get to that upgrade to share.

<!-- excerpt-end -->

## The Ceph Reality Check

Ceph is simultaneously amazing and terrifying. Proxmox makes the initial cluster setup incredibly easy with its auto-magic configuration. But when that auto-magic fails? You're suddenly staring into the abyss of distributed storage complexity.

Here's what I've learned the hard way:

### Shutting Down Ceph Properly

Don't just power off your nodes. Seriously. The [Proxmox forum has excellent guidance](https://forum.proxmox.com/threads/shutdown-of-the-hyper-converged-cluster-ceph.68085/post-619620) on clean Ceph shutdowns. Your future self will thank you.

### Sane Scrubbing Defaults

The default Ceph scrubbing schedule will murder your SSDs. Weekly deep scrubs? That's a fast track to drive replacement hell. You are running a homelab setup not an enterprise server farm so don't over do it.

Here's what I changed to save my storage:

```bash
# Schedule normal scrubs between 1-7 days
ceph config set global osd_scrub_min_interval 86400 # 1 day
ceph config set global osd_scrub_interval_randomize_ratio 7 # 700%

# Force scrub after 14 days max
ceph config set global osd_scrub_max_interval 1209600 # 14 days

# Deep scrub every 28 days instead of weekly
ceph config set global osd_deep_scrub_interval 2419200 # 28 days
```

**Important note**: Set these in the global namespace, not the osd namespace. The monitors need to see the same settings to avoid PG_NOT_DEEP_SCRUBBED warnings.

### Planning Your OSD Layout

Use [Florian's Ceph calculator](https://florian.ca/ceph-calculator/) before you start throwing drives at your cluster. Trust me on this one.

## The Seagate USB Nightmare

External USB drives and Proxmox don't always play nice. I learned this while trying to migrate 16+ TB of media files. The [smartmontools wiki](https://www.smartmontools.org/wiki/SAT-with-UAS-Linux) has the gory details about UAS issues.

Here's how to diagnose USB storage problems:

```bash
# Install diagnostic tools
apt install lsscsi sysfsutils -y

# Check what's using UAS vs AHCI
lsscsi -H

# Get detailed SCSI host info
systool -c scsi_host -v
```

In my case, the Seagate drives were using UAS (USB Attached SCSI) which caused random disconnects during large transfers. Sometimes the old ways really are better.

## Proxmox API Scripting

The Proxmox API is incredibly powerful once you figure out the patterns. Here are some useful commands I use regularly:

```bash
# Get cluster status
pvesh get /cluster/status
pvesh get /cluster/ceph/status

# Check all nodes
pvesh get /nodes

# My cluster SSH script
#!/bin/bash
for node in $(pvesh get /cluster/status --output-format json | jq -r '.[].ip' | grep -v null); do
  ssh root@$node "$*"
done
```

The **API viewer** on `https://<your_proxmox_ip_address>:8006/pve-docs/api-viewer/index.html`)` is your friend for exploring what's available.

## Storage Migration Reality

Moving 16+ TB of data taught me patience. Here's what my storage looked like during the great migration:

```bash
# Source drives
/dev/sdh2    4.6T  3.0T  1.7T  65% /mnt/sdh
/dev/sdi2    4.6T  2.6T  2.1T  56% /mnt/sdi  
/dev/sdj2    4.6T  3.8T  800G  83% /mnt/sdj
/dev/sdk2    4.6T  2.5T  2.2T  53% /mnt/sdk

# Destination CephFS
192.168.86.11,192.168.86.12,192.168.86.13:/  5.9T  4.5T  1.4T  78% /mnt/pve/cephfs
```

The breakdown:
- Movies: 4.2 TiB
- TV Shows: 11.9 TiB  
- Total: 16.2 TiB to migrate

Using `rsync -nrv` for dry runs saved me from several disasters. Always test your migration commands first.

## Current Cluster Stats

My 9-OSD cluster (3 nodes, 3 OSDs each) handles this workload pretty well:

```text
Total: 41 TiB raw, 27 TiB available
Usage: 34.72% (14 TiB used)
Replication: 3x (because I'm paranoid)
```

The uneven OSD usage you see in the stats? That's from the migration process. Ceph will eventually balance things out, but it takes time.

## Network Monitoring Bonus

I'm using a Netgear GS108Ev2 switch and found this [Home Assistant integration](https://github.com/ckarrie/ckw-ha-gs108e) super useful for monitoring cluster network traffic.

## Lessons Learned Summary

1. **Ceph is powerful but complex** - The Proxmox integration hides a lot of complexity until it doesn't
2. **Plan your scrubbing schedule** - Default settings will kill your drives
3. **USB storage is tricky** - UAS can cause problems with large transfers  
4. **Use the API** - Scripting cluster operations saves tons of time
5. **Test migrations thoroughly** - `rsync -n` is your friend
6. **Be patient** - Large data migrations take time, don't rush them

The homelab journey with Proxmox has been incredibly rewarding, even with the occasional 3 AM troubleshooting session. The platform is solid once you understand its quirks, and the learning experience is invaluable.

Got questions about any of these topics? The Proxmox community forums are fantastic, and I'm always happy to share war stories.
