---
title: "ZFS Boot Mirrors on Proxmox 8 for the Homelab - Part 2"
layout: post
categories: [proxmox, zfs, storage, homelab]
tags: [proxmox, zfs, storage, homelab, hardware, boot, mirror, ssd]
excerpt: "Migrating a Proxmox ZFS boot mirror from large spinning rust HDDs to smaller SSDs — the procedure ZFS makes deliberately difficult."
description: "How to migrate a Proxmox ZFS boot mirror to smaller replacement drives using ZFS send/receive, covering partition creation with parted, proxmox-boot-tool initialization, and data migration from a 500GB HDD mirror to 128GB SSDs."
published: false
seo:
  type: BlogPosting
  date_published: 2026-05-25
  date_modified: 2026-05-25
---

[Part 1](/proxmox-zfs-boot-mirrors-part-1/) covered replacing a failed ZFS boot mirror drive with one of the same size. This is the harder problem: your replacement drives are *smaller* than the originals.

In my case, the cluster nodes have 500GB spinning rust HDDs as boot mirrors but only use 3-7GB of actual space — Ceph handles all the real storage. Replacing them with 128GB SSDs makes sense on cost, speed, and reliability grounds. But ZFS won't let you add a smaller drive to an existing mirror.

[![Proxmox 8 ZFS Boot Mirror](/assets/images/zfs-boot-mirror-proxmox8-001.png){:width="40%" height="40%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/zfs-boot-mirror-proxmox8-001.png){:target="_blank"}

<!-- excerpt-end -->

## Which Path Is Right for You?

Before starting, decide which migration approach fits your situation:

| Situation | Approach |
|-----------|----------|
| One drive failed, replacement is smaller | This article (send/receive migration) |
| Both drives failed simultaneously | [Part 3](/proxmox-zfs-boot-mirrors-part-3/) (fresh install) |
| Node has no Ceph OSDs, drives are smaller | Fresh install is simpler — see [Part 3](/proxmox-zfs-boot-mirrors-part-3/) |
| Node has Ceph OSDs, drives are smaller | This article — preserves OSDs without reinstall |

The send/receive migration is more complex but keeps the running OS intact. If both drives have already failed and the OS is unbootable, skip to [Part 3](/proxmox-zfs-boot-mirrors-part-3/).

## The Problem

ZFS mirrors require the replacement drive to be the same size or larger than the existing drives. Attempting to add a smaller drive fails:

```console
root@tanaka:~# zpool attach rpool ata-existing-part3 /dev/disk/by-id/ata-smaller-ssd-part3
cannot attach /dev/disk/by-id/ata-smaller-ssd-part3 to rpool: device is too small
```

The workaround is to migrate the data to the new smaller pool using `zfs send | zfs receive` rather than resilvering.

---

## TODO: Complete This Article

The following sections need to be written with actual console sessions from a completed migration.

### What needs to be documented:

**1. Prerequisites and planning**
- Verify actual ZFS pool usage is smaller than the new drive (`zpool list`, `df -h`)
- Confirm new drive partition 3 size will fit the data
- Have a tested back-out plan (keep one original HDD until migration verified)

**2. Partition the new smaller SSD**
- Use `parted` to create the three Proxmox partitions on the new SSD:
  - Partition 1: BIOS boot (34s–2047s, bios_grub flag)
  - Partition 2: EFI System (2048s–2099199s, fat32, boot+esp flags)
  - Partition 3: ZFS (2099200s to end of disk)
- The `sfdisk -d | sfdisk` trick from Part 1 won't work here since the sizes differ
- The `parted` session for tanaka is already in this draft as a starting point

**3. Initialize the Proxmox boot partition**
- `proxmox-boot-tool format /dev/disk/by-id/<new-ssd>-part2`
- `proxmox-boot-tool init /dev/disk/by-id/<new-ssd>-part2 grub`
- Verify with `proxmox-boot-tool status`

**4. Create a new ZFS pool on the new SSD**
- `zpool create newpool /dev/disk/by-id/<new-ssd>-part3`
- Set matching ZFS properties from the existing rpool

**5. Migrate data with ZFS send/receive**
- `zfs snapshot -r rpool@migrate`
- `zfs send -R rpool@migrate | zfs receive -F newpool`
- This is the missing section — needs a real console session

**6. Swap the pools**
- Export newpool, import as rpool
- Update `/etc/kernel/proxmox-boot-uuids`
- Reboot and verify

**7. Add second SSD to mirror**
- Once booting from the new SSD, add the second SSD using `zpool attach` (same size, so standard Part 1 procedure applies)

**8. Verify and clean up**
- `proxmox-boot-tool status` — both SSDs listed
- `zpool scrub rpool` — no errors
- Keep original HDD for one week as insurance before repurposing

### Alternative approach to research:
The [Reddit tutorial](https://www.reddit.com/r/Proxmox/comments/1cr6wn7/tutorial_howto_migrate_a_pve_zfs_bootroot_mirror/) and [shell script](https://github.com/kneutron/ansitest/blob/master/proxmox/proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh) referenced below may offer a cleaner path. Worth testing against the manual approach.

---

## Existing Work (Starting Point)

The `parted` sessions below from tanaka are already captured and can be incorporated into the finished article.

### Partition the new SSD with parted

```console
root@tanaka:~# parted /dev/sdc
(parted) mklabel gpt
(parted) mkpart "" 34s 2047s
Warning: The resulting partition is not properly aligned for best performance: 34s % 2048s != 0s
Ignore/Cancel? i
(parted) toggle 1 bios_grub
(parted) mkpart "" fat32 2048s 2099199s
(parted) set 2 boot on
(parted) set 2 esp on
(parted) mkpart "" zfs 2099200s -1
(parted) print
Model: Timetec 30TT253X2-128G (scsi)
Disk /dev/sdc: 128GB
Number  Start     End         Size        File system  Name  Flags
 1      17.4kB    1049kB      1031kB                         bios_grub
 2      1049kB    1075MB      1074MB                         boot, esp
 3      1075MB    128GB       127GB
```

### Initialize Proxmox boot on the new SSD (via USB enclosure)

```console
root@tanaka:~# proxmox-boot-tool format \
  /dev/disk/by-id/usb-Timetec_30TT253X2-128G_012345678999-0:0-part2
Formatting as vfat.. Done.

root@tanaka:~# proxmox-boot-tool init \
  /dev/disk/by-id/usb-Timetec_30TT253X2-128G_012345678999-0:0-part2 grub
Installing grub i386-pc target.. Installation finished. No error reported.
Copying and configuring kernels on /dev/disk/by-uuid/D7D1-00F1
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.12-8-pve
done
```

### ZFS data migration (INCOMPLETE — needs real console session)

```console
# TODO: Complete this section with actual zfs send/receive output
```

## References

- [Migrate Proxmox VE to smaller root disks](https://aaronlauterer.com/blog/2021/proxmox-ve-migrate-to-smaller-root-disks/) — Aaron Lauterer
- [Move GRUB and boot partition to another disk](https://aaronlauterer.com/blog/2021/move-grub-and-boot-to-other-disk/) — Aaron Lauterer
- [Tutorial: migrate PVE ZFS boot mirror to smaller disks](https://www.reddit.com/r/Proxmox/comments/1cr6wn7/tutorial_howto_migrate_a_pve_zfs_bootroot_mirror/) — Reddit
- [proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh](https://github.com/kneutron/ansitest/blob/master/proxmox/proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh) — Shell script
- [ZFS send/receive for pool migration](https://www.reddit.com/r/zfs/comments/sx6ohz/comment/hxqeanr/) — Reddit
- [ZFS: shrink pool](https://niziak.spox.org/wiki/linux:fs:zfs:shrink) — niziak.spox.org

## Related Articles

- [ZFS Boot Mirrors on Proxmox 8 - Part 1](/proxmox-zfs-boot-mirrors-part-1/) — Same-size drive replacement
- [ZFS Boot Mirrors on Proxmox 8 - Part 3](/proxmox-zfs-boot-mirrors-part-3/) — Catastrophic dual-drive failure and fresh install recovery
- [Monitoring ZFS Boot Mirror Health in Proxmox 8 Clusters](/proxmox-zfs-boot-mirror-smart-analysis/) — SMART monitoring
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — All my Proxmox and Ceph articles in one place


## Plan a back out plan

I idea is to power down and grab one of the bootable HDDs and swap in a new SSD to figure out how to copy the data and boot information across.

Step one will be to power down and physically remove one of the good HDD and swap in the spare HDD to get a copy of the boot disk using the ZFS mirror recovery. Likely the easy way to do this is just use the typical [ZFS Mirror replace bad disk](https://forum.proxmox.com/threads/zfs-mirror-replace-bad-disk.99469/) and resilver the spare then remove the resilvered spare as insurance. That leaves me a back out plan of swapping the spare as my primary boot disk in case I trash my current boot disk(s). I should probably do a `zpool scrub` when the two good 500Gb drives are is still attached to do a file system consistency check since these are all older HDDs.

Next is to drop in the SSD into the system and try to add it to the mirror with it being smaller. I dunno what will happen there. I assume ZFS will complain it is smaller and not do it.

Some good fortune happened as this particular node in the Proxmox Cluster just happens to not have Ceph OSDs and is the lower-end hardware node for the cluster. So loosing it and reinstalling would be the least painful node. I would still like to figure this out here so I can have a plan if this happened to the more critical nodes. I would like a path to replacing all the spinning rust drives with solid state drives.

I have a USB enclosure for the SSD and just dropped it on a USB port to see what I can do to copy the bootable features on to it and replicate the data partitions.

## Execute on migration

Here are the steps I plan to do that I have done on prior systems but have not done all these steps for this system.

### figure out partition copying from large to smaller drive

``` console
root@tanaka:~# parted /dev/sda
GNU Parted 3.5
Using /dev/sda
Welcome to GNU Parted! Type 'help' to view a list of commands.
(parted) print                                                            
Model: ATA ST3500418AS (scsi)
Disk /dev/sda: 500GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start   End     Size    File system  Name  Flags
 1      17.4kB  1049kB  1031kB                     bios_grub
 2      1049kB  1075MB  1074MB  fat32              boot, esp
 3      1075MB  500GB   499GB   zfs
(parted) unit s                                                           
(parted) print                                                            
Model: ATA ST3500418AS (scsi)
Disk /dev/sda: 976773168s
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start     End         Size        File system  Name  Flags
 1      34s       2047s       2014s                          bios_grub
 2      2048s     2099199s    2097152s    fat32              boot, esp
 3      2099200s  976773134s  974673935s  zfs
```

``` console
root@tanaka:~# parted /dev/sdc
GNU Parted 3.5
Using /dev/sda
Welcome to GNU Parted! Type 'help' to view a list of commands.
(parted) mklabel gpt
(parted) mkpart "" 34s 2047s
Warning: The resulting partition is not properly aligned for best performance: 34s % 2048s != 0s
Ignore/Cancel? i                                                          
(parted) toggle 1 bios_grub
(parted) mkpart "" fat32 2048s 2099199s
(parted) set 2 boot on
(parted) set 2 esp on                                                     
(parted) print                                                            
Model: Timetec 30TT253X2-128G (scsi)
Disk /dev/sdc: 250069680s
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start  End       Size      File system  Name  Flags
 1      34s    2047s     2014s                        bios_grub
 2      2048s  2099199s  2097152s                     boot, esp

(parted) mkpart "" zfs 2099200s -1                                     
Warning: You requested a partition from 2099200s to 250069679s (sectors 2099200..250069679).
The closest location we can manage is 2099200s to 250069646s (sectors 2099200..250069646).
Is this still acceptable to you?
Yes/No? y                                                                 
(parted) print                                                            
Model: Timetec 30TT253X2-128G (scsi)
Disk /dev/sdc: 250069680s
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start     End         Size        File system  Name  Flags
 1      34s       2047s       2014s                          bios_grub
 2      2048s     2099199s    2097152s                       boot, esp
 3      2099200s  250069646s  247970447s  zfs
```

``` console
root@tanaka:~# parted /dev/sdc
GNU Parted 3.5
Using /dev/sdc
Welcome to GNU Parted! Type 'help' to view a list of commands.
(parted) print                                                            
Model: Timetec 30TT253X2-128G (scsi)
Disk /dev/sdc: 128GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start   End     Size    File system  Name  Flags
 1      17.4kB  1049kB  1031kB                     bios_grub
 2      1049kB  1075MB  1074MB                     boot, esp
 3      1075MB  128GB   127GB

(parted) align-check opt 1
1 not aligned: 34s % 2048s != 0s
(parted) align-check opt 2
2 aligned
(parted) align-check opt 3
3 aligned

(parted) select /dev/sda                                                  
Using /dev/sda
(parted) print                                                            
Model: ATA ST3500418AS (scsi)
Disk /dev/sda: 500GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: 

Number  Start   End     Size    File system  Name  Flags
 1      17.4kB  1049kB  1031kB                     bios_grub
 2      1049kB  1075MB  1074MB  fat32              boot, esp
 3      1075MB  500GB   499GB   zfs
(parted) align-check opt 1                                                
1 not aligned: 34s % 2048s != 0s
(parted) align-check opt 2
2 aligned
(parted) align-check opt 3
3 aligned
```

### Partition 2: Proxmox Boot

``` console
root@tanaka:~# proxmox-boot-tool format /dev/disk/by-id/
ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C        usb-Timetec_30TT253X2-128G_012345678999-0:0-part2
ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part1  usb-Timetec_30TT253X2-128G_012345678999-0:0-part3
ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part2  wwn-0x5000c5002fb4f383
ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  wwn-0x5000c5002fb4f383-part1
ata-HL-DT-ST_DVD+_-RW_GH70N_K1NBANG1500             wwn-0x5000c5002fb4f383-part2
ata-ST3500418AS_5VMQF6GN                            wwn-0x5000c5002fb4f383-part3
ata-ST3500418AS_5VMQF6GN-part1                      wwn-0x5000cca70fc8e018
ata-ST3500418AS_5VMQF6GN-part2                      wwn-0x5000cca70fc8e018-part1
ata-ST3500418AS_5VMQF6GN-part3                      wwn-0x5000cca70fc8e018-part2
usb-Timetec_30TT253X2-128G_012345678999-0:0         wwn-0x5000cca70fc8e018-part3
usb-Timetec_30TT253X2-128G_012345678999-0:0-part1   
root@tanaka:~# proxmox-boot-tool format /dev/disk/by-id/usb-Timetec_30TT253X2-128G_012345678999-0\:0-part2
UUID="" SIZE="1073741824" FSTYPE="" PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b" PKNAME="sdc" MOUNTPOINT=""
Formatting '/dev/disk/by-id/usb-Timetec_30TT253X2-128G_012345678999-0:0-part2' as vfat..
mkfs.fat 4.2 (2021-01-31)
Done.
```

``` console
root@tanaka:~# proxmox-boot-tool init /dev/disk/by-id/usb-Timetec_30TT253X2-128G_012345678999-0\:0-part2 grub
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
UUID="D7D1-00F1" SIZE="1073741824" FSTYPE="vfat" PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b" PKNAME="sdc" MOUNTPOINT=""
Mounting '/dev/disk/by-id/usb-Timetec_30TT253X2-128G_012345678999-0:0-part2' on '/var/tmp/espmounts/D7D1-00F1'.
Installing grub i386-pc target..
Installing for i386-pc platform.
Installation finished. No error reported.
Unmounting '/dev/disk/by-id/usb-Timetec_30TT253X2-128G_012345678999-0:0-part2'.
Adding '/dev/disk/by-id/usb-Timetec_30TT253X2-128G_012345678999-0:0-part2' to list of synced ESPs..
Refreshing kernels and initrds..
Running hook script 'proxmox-auto-removal'..
Running hook script 'zz-proxmox-boot'..
Copying and configuring kernels on /dev/disk/by-uuid/1FDB-C48E
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.12-8-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-8-pve
Found initrd image: /boot/initrd.img-6.8.12-8-pve
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
done
Copying and configuring kernels on /dev/disk/by-uuid/9BB0-3E21
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.12-8-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-8-pve
Found initrd image: /boot/initrd.img-6.8.12-8-pve
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
done
Copying and configuring kernels on /dev/disk/by-uuid/D7D1-00F1
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.12-8-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-8-pve
Found initrd image: /boot/initrd.img-6.8.12-8-pve
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
done
```

### Partition 3: ZFS

Copy the data from the zfs boot mirror partition 3 zfs pool to the smaller one on this new drive.

``` console

```

## References

Here are some reference links and interesting articles I found during researching how to do this particular operation of reducing the size of a ZFS pool device.

- [Migrate Proxmox VE to smaller root disks](https://aaronlauterer.com/blog/2021/proxmox-ve-migrate-to-smaller-root-disks/) by Aaron Lauterer sounds like what I was planning in part. He also has a follow up [Move GRUB and boot partition to another disk](https://aaronlauterer.com/blog/2021/move-grub-and-boot-to-other-disk/) that may be important for my GRUB legacy boot environments. I don't think I went UEFI boot on the main clusters.
- [proxmox/proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh](https://github.com/kneutron/ansitest/blob/master/proxmox/proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh) shell script to replace larger to smaller disks from Reddit post [Tutorial / HOWTO migrate a PVE ZFS boot/root mirror to smaller disks (256GB to 128GB)](https://www.reddit.com/r/Proxmox/comments/1cr6wn7/tutorial_howto_migrate_a_pve_zfs_bootroot_mirror/).
- [Zetto on Reddit](https://www.reddit.com/r/zfs/comments/sx6ohz/comment/hxqeanr/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) discusses a `ZFS send | ZFS receive` for a new ZFS pool on the new device.
- [ZFS: shrink pool](https://niziak.spox.org/wiki/linux:fs:zfs:shrink#:~:text=e%20nvmpool%20nvme0n1p3-,ZFS%3A%20shrink%20zpool,mirror%2C%20use%20attach%20not%20add) has an interesting trick that might help me out.
