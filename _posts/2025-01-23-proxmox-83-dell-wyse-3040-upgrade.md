---
title:  "Proxmox VE 8.3.3 upgrade on Dell Wyse 3040s"
layout: post
published: false
---

First off, I have hyper constrained hardware for my Proxmox Cluster on Dell Wyse 3040s with Ceph on USB Thumbdrives. It is useful as a place to test upgrades before hitting my main cluster.

I started the upgrade from 8.2 to 8.3 and ended up on the CLI doing `apt update && apt dist-upgrade -y` directly so I could manage running out of disk space on the root volume. These systems are really low on both RAM (2GB) and eMMC disk (8GB). Nobody wants a failed install as these are about 160 miles (~260 km) drive to manually do anything to them.

*** OTHER ARTICLE ON RECOVERY in 2024-01-24-linux-oh-crap article...

<!-- excerpt-end -->

How did we get here?

- Debian 12 on Dell Wyse 3040s
- ProxMox 8.2.2 Cluster on Dell Wyse 3040s
- ProxMox 8.2.4 Upgrade on Dell Wyse 3040s
- Proxmox VE 8.1 to 8.2 upgrade issues in the Homelabs

The initial installation had three 3040s with just an 8GB Thumbdrive which was too small. So I grabbed three 32Gb thumbdrives from Amazon. But as an interesting test, I never removed the 8Gb drives. So I had an unbalanced OSDs sizing for playing around.

With the latest upgrade to Proxmox VE 8.3.3, we are just out of disk space on the eMMC 8GB root volume. So I am grabbing back the 8Gb drive for OS usage.

Removed my oldest 8Gb USB OSDs from the Ceph Cluster cleanly so the contents migrated to the newer 32Gb USBs.

Destroyed  my oldest 8Gb OSDs from Ceph Cluster.
Created an LVM Volume Group (vg) called `osdisk` in the webui
Manually on CLI created a Logical Volume (lv) also called `osdisk`
Finally created an Ext4 file system on the volume

``` console
root@pve1:~# lvs
  LV                                             VG                                        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  osd-block-1af3a95d-d3c8-44a0-940f-de11a163040f ceph-0391f8fe-42a1-4ff1-82f6-1412019e77eb -wi-ao---- <28.67g                
root@pve1:~# vgs
  VG                                        #PV #LV #SN Attr   VSize   VFree
  ceph-0391f8fe-42a1-4ff1-82f6-1412019e77eb   1   1   0 wz--n- <28.67g     0
  osdisk                                      1   0   0 wz--n-  <7.47g <7.47g
root@pve1:~# lvcreate -l 100%FREE -n osdisk osdisk
  Logical volume "osdisk" created.
root@pve1:~# lvs
  LV                                             VG                                        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  osd-block-1af3a95d-d3c8-44a0-940f-de11a163040f ceph-0391f8fe-42a1-4ff1-82f6-1412019e77eb -wi-ao---- <28.67g                
  osdisk                                         osdisk                                    -wi-a-----  <7.47g                
root@pve1:~# mkfs.ext4 /dev/osdisk/osdisk
mke2fs 1.47.0 (5-Feb-2023)
Creating filesystem with 1957888 4k blocks and 489600 inodes
Filesystem UUID: 1b04ef96-590d-404f-bb21-2ecaaa98afaf
Superblock backups stored on blocks:
        32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632

Allocating group tables: done
Writing inode tables: done
Creating journal (16384 blocks): done
Writing superblocks and filesystem accounting information: done

root@pve1:~#
```

Order matters: PVE, VGS and LVS

``` console
root@pve1:~# pvs
  PV         VG                                        Fmt  Attr PSize   PFree
  /dev/sda   osdisk                                    lvm2 a--   <7.47g    0
  /dev/sdb   ceph-0391f8fe-42a1-4ff1-82f6-1412019e77eb lvm2 a--  <28.67g    0
root@pve1:~# vgs
  VG                                        #PV #LV #SN Attr   VSize   VFree
  ceph-0391f8fe-42a1-4ff1-82f6-1412019e77eb   1   1   0 wz--n- <28.67g    0
  osdisk                                      1   1   0 wz--n-  <7.47g    0
root@pve1:~# lvs
  LV                                             VG                                        Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  osd-block-1af3a95d-d3c8-44a0-940f-de11a163040f ceph-0391f8fe-42a1-4ff1-82f6-1412019e77eb -wi-ao---- <28.67g                
  osdisk                                         osdisk                                    -wi-a-----  <7.47g                

```
