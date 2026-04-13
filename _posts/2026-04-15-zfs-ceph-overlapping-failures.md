---
title: "When ZFS and Ceph Problems Collide: Diagnosing Overlapping Failures on Proxmox"
layout: post
categories: [proxmox, zfs, ceph, homelab]
tags: [proxmox, zfs, ceph, osd, usb, debugging, homelab, storage, bluestore, dell-optiplex-990]
excerpt: "A routine ZFS scrub alert on harlan turned into a multi-hour debugging session when a hostid mismatch fix collided with a pre-existing Ceph OSD failure from a dead USB drive. Here's how overlapping storage problems can mask each other and how to untangle them."
description: "Diagnosing overlapping ZFS hostid mismatch and Ceph OSD failures on a Proxmox homelab cluster. Covers the correct Proxmox-specific fix for ZFS-8000-EY, recovering hung USB Ceph drives, replacing dead OSDs with specific IDs, and discovering WAL vs DB acceleration inconsistencies."
date: 2026-04-15
last_modified_at: 2026-04-15
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-15
  date_modified: 2026-04-15
---

A routine ZFS scrub email kicked off what turned into a much bigger investigation on my [AlteredCarbon Proxmox cluster](/proxmox-ceph-guide/). What started as a simple hostid mismatch on a boot mirror ended up uncovering a dead USB Ceph drive, a ghost OSD that had been missing for three months, and an inconsistency in how SSD acceleration was configured across the cluster.

This is the story of overlapping failures and why you should always check the full picture before rebooting.

<!-- excerpt-end -->

## The Alert

The ZFS scrub notification from harlan looked benign:

```console
ZFS has finished a scrub:

   pool: rpool
  state: ONLINE
 status: Mismatch between pool hostid and system hostid on imported pool.
   scan: scrub repaired 0B in 00:00:12 with 0 errors
 config:
        NAME                                STATE     READ WRITE CKSUM
        rpool                               ONLINE       0     0     0
          mirror-0                          ONLINE       0     0     0
            ata-SSD_YS202010015363AA-part3  ONLINE       0     0     0
            ata-SSD_YS202010025083AA-part3  ONLINE       0     0     0

 errors: No known data errors
```

Zero errors, both SSDs healthy, pool ONLINE. The only issue was a hostid mismatch — a leftover from harlan's emergency SSD migration months earlier when the original HDDs failed and required a full Proxmox reinstall.

## Problem 1: ZFS Hostid Mismatch

When harlan was reinstalled on new SSDs, the fresh Proxmox installation generated a new `/etc/hostid`. But the rpool metadata still carried the old hostid from the previous installation. Every scrub would emit this warning until fixed.

### The Wrong Fix (Don't Do This)

My first instinct was the textbook ZFS fix:

```bash
zpool export rpool
zpool import rpool
```

**This hangs immediately.** You cannot export rpool on a running system — it's your root filesystem. The `zpool export` tries to unmount `/` and blocks forever. I had to open a second SSH session and `pkill -9 -f "zpool export"` to recover.

### The Right Fix

The correct approach for a Proxmox ZFS boot mirror:

```bash
# Write the current system hostid to /etc/hostid
zgenhostid -f $(hostid)

# Rebuild initramfs so the hostid is included in early boot
proxmox-boot-tool refresh

# Verify both ESPs are synced
proxmox-boot-tool status
```

The `proxmox-boot-tool refresh` is the key step — it rebuilds the initramfs and syncs both boot partitions in the ZFS mirror. Without it, the hostid file won't be present during early boot when the pool is imported.

You can verify the initramfs includes the hostid:

```bash
lsinitramfs /boot/initrd.img-$(uname -r) | grep hostid
```

The warning clears on the next reboot.

## Problem 2: Ceph OSDs Were Already Down

Before rebooting harlan for the hostid fix, I checked Ceph status and found a pre-existing disaster:

```console
health: HEALTH_WARN
        noout,norebalance flag(s) set
        2 osds down
        Degraded data redundancy: 9.435% objects degraded
```

Two of harlan's three Ceph OSDs (osd.0 and osd.6) had been down since **March 16th** — almost four weeks. Someone (me) had set `noout,norebalance` flags to prevent rebalancing and then... forgot about it.

### osd.0: USB Drive Hung

The logs told the story:

```console
bluestore(/var/lib/ceph/osd/ceph-0/block) _read_bdev_label failed to read
from /var/lib/ceph/osd/ceph-0/block: (5) Input/output error
```

And `dmesg` confirmed USB drive failures:

```
sd 7:0:0:0: [sde] tag#14 FAILED Result: hostbyte=DID_ERROR driverbyte=DRIVER_OK
I/O error, dev sde, sector 9767536512 op 0x0:(READ)
usb 4-4: reset SuperSpeed USB device number 3 using xhci_hcd
```

The Seagate 5TB USB drive backing osd.0 was experiencing repeated USB bus resets and I/O errors. The USB-to-SATA bridge was hung — every command touching `/dev/sde` would block indefinitely. This meant `ceph-volume lvm list`, `smartctl`, even `lvs` would all hang waiting for I/O that would never complete.

### osd.6: Drive Completely Gone

osd.6 was worse — its backing drive had failed months earlier. This was the same Seagate BUP Portable that had [survived the power outage in September 2025](/ceph-osd-recovery-power-failure/) but apparently didn't survive long after:

```bash
root@harlan:~# ls -la /var/lib/ceph/osd/ceph-6/
total 1
drwxr-xr-x 2 ceph ceph 2 Jan 21 20:43 .
drwxr-xr-x 6 ceph ceph 6 Jan 21 20:43 ..
```

Empty directory since January 21st. The OSD logs showed:

```bash
auth: unable to find a keyring on /var/lib/ceph/osd/ceph-6/keyring:
(2) No such file or directory
```

Only two USB drives showed up in `lsusb` — the third was simply not on the bus. When I plugged the labeled osd.6 drive into a different USB port, it enumerated for half a second then immediately disconnected:

```bash
[77793.916270] usb 4-1: Product: BUP Portable
[77793.916273] usb 4-1: Manufacturer: Seagate
[77794.468387] usb 4-1: USB disconnect, device number 4
[77794.469556] sd 8:0:0:0: [sdf] Read Capacity(16) failed: Result: hostbyte=DID_ERROR
[77794.469577] sd 8:0:0:0: [sdf] 0 512-byte logical blocks: (0 B/0 B)
```

Zero bytes, zero blocks. The drive was dead as a door nail.

## The Recovery

### Step 1: Reboot to Clear USB Bus

Rather than trying to surgically unplug the hung drive, I rebooted harlan. This:

- Reset both USB bridges
- Cleared the hung I/O state on sde
- Applied the ZFS hostid fix (via the updated initramfs)

After reboot, osd.0 came back up — the USB reset recovered sde. But osd.6's drive was still dead.

### Step 2: Remove Dead osd.6

Through the Proxmox Web UI: **harlan → Ceph → OSD → select osd.6 → Out → Destroy** (with cleanup enabled).

This removed osd.6 from the CRUSH map, deleted its auth keys, and cleaned up the orphaned WAL LV on the MX500 SSD I use to accelerate access.

### Step 3: Add Replacement Drive as New osd.6

I had a replacement 5TB Seagate drive ready. The trick was ensuring it got OSD ID 6 (for my physical labeling) and matched the existing 100GB WAL configuration:

```bash
# Pre-create a 100GB WAL LV on the MX500 to match existing OSDs
lvcreate -L 100G -n osd-wal-osd6 ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c

# Create the OSD with specific ID and WAL device
ceph-volume lvm create --osd-id 6 --data /dev/sdd \
  --block.wal ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c/osd-wal-osd6
```

The `--osd-id 6` flag was critical — without it, Ceph would assign the next available ID. The pre-sized LV was necessary because the Ceph config default for `bluestore_block_wal_size` was only 96MB, while the existing WALs were 100GB (created with pre-sized LVs originally).

### Step 4: Clear Maintenance Flags

With all 15 OSDs back up:

```bash
ceph osd unset noout
ceph osd unset norebalance
```

Ceph immediately began backfilling data to the new osd.6. Within minutes, the cluster was recovering:

```console
root@harlan:~# ceph -s
  cluster:
    health: HEALTH_WARN
            Degraded data redundancy: 4.863% objects degraded
  services:
    osd: 15 osds: 15 up (since 16m), 15 in (since 17m)
  data:
    usage:   30 TiB used, 39 TiB / 69 TiB avail
  io:
    recovery: 21 MiB/s, 5 objects/s
```

All 15 OSDs up, 69 TiB total capacity restored, recovery in progress. The degraded PGs will heal over several hours as data backfills to the new osd.6 across the USB 3.0 links.

## Bonus Discovery: WAL vs DB Inconsistency

While investigating, I noticed the Proxmox UI showed different SSD acceleration types across nodes. Dumping the metadata revealed:

| Host | OSDs | SSD Acceleration |
|------|------|-----------------|
| harlan | 0, 3, 6 | WAL only |
| kovacs | 2, 5, 8 | WAL only |
| quell | 9, 10, 11 | WAL only |
| edgar | 1, 4, 7 | **DB** (WAL + metadata) |
| poe | 12, 13, 14 | **DB** (WAL + metadata) |

Edgar and Poe's OSDs were created through the Proxmox Web UI, which defaults to `--block.db`. The other nodes were set up via CLI with `--block.wal`. The DB configuration is slightly better — it accelerates both writes and metadata reads on the SSD — but the practical difference is minimal when the bottleneck is USB 3.0 bandwidth.

Future OSD rebuilds should standardize on DB to match the Proxmox UI default.

## Lessons Learned

1. **Check Ceph before rebooting for ZFS issues.** The hostid fix was trivial but the Ceph situation required careful handling. If I'd blindly rebooted with 2 OSDs down and degraded PGs, the recovery would have been messier.

2. **Don't `zpool export rpool` on a running system.** Use `zgenhostid` + `proxmox-boot-tool refresh` instead. The Proxmox tooling handles this correctly.

3. **Maintenance flags are dangerous when forgotten.** `noout,norebalance` prevented Ceph from healing for almost four weeks. Set a calendar reminder when you enable maintenance flags.

4. **USB Ceph drives fail in annoying ways.** A hung USB bridge blocks every LVM and Ceph command that touches the device. The only fix is physical disconnect or reboot. Label your drives — it saved significant time identifying which physical cable to check.

5. **Dead drives may not show up at all.** osd.6's drive wasn't just failing — it was completely absent from the USB bus. No amount of software troubleshooting will find a drive that doesn't enumerate.

6. **Document your OSD creation method.** The WAL vs DB inconsistency was invisible until I dumped metadata across all 15 OSDs. Knowing which tool created each OSD helps explain configuration differences.

## Cluster Hardware Context

For readers unfamiliar with this cluster: AlteredCarbon is a six-node Proxmox 8.4 cluster built from Dell OptiPlex 990 towers (2011-era i7-2600 CPUs). Each of the five Ceph OSD hosts has three 5TB Seagate USB drives for data and a Crucial MX500 500GB SATA SSD for WAL/DB acceleration. The sixth node (tanaka) runs without Ceph OSDs. Total raw storage is 69 TiB with 3x replication.

It's old hardware running enterprise software on a homelab budget. Things break. The key is having enough redundancy that nothing breaks catastrophically.

## Related Posts

- [Ceph OSD Recovery After Power Failure](/ceph-osd-recovery-power-failure/) — The prequel: a dead SAN switch caused OSD cascades, and the maintenance flags set during that recovery were still active months later
- [Monitoring ZFS Boot Mirror Health in Proxmox 8 Clusters](/proxmox-zfs-boot-mirror-smart-analysis/) — The SMART monitoring that caught harlan's original HDD failures
- [USB Drive SMART Updates](/usb-drive-smart-updates/) — Configuring SMART monitoring for the replacement Seagate USB drives
- [ProxMox 8.2 for the Homelabs](/proxmox-8-homelab/) — The original cluster build where ZFS boot mirrors saved the day
- [Proxmox Ceph Settings for the Homelab](/proxmox-ceph-homelab-settings/) — BlueStore configuration context for the WAL vs DB discovery
- [Homelab Storage Economics](/homelab-storage-economics/) — Cost analysis behind the USB drive replacement decisions
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — All Proxmox and Ceph articles

## References

- [ZFS-8000-EY: Pool hostid mismatch](https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-EY)
- [Proxmox Boot Tool documentation](https://pve.proxmox.com/wiki/Host_Bootloader)
- [Ceph BlueStore WAL vs DB](https://docs.ceph.com/en/reef/rados/configuration/bluestore-config-ref/)
