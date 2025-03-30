---
title:  "ZFS Boot Mirrors on Proxmox 8.3 for the Homelab - Part 2"
layout: post
published: false
---

ZFS Boot Mirrors are awesome for keeping my old systems up and running as I have drive failures.

From that description, you might see my problem. Anticipating this problem, I bought a pair of cheap 120Gb SSD drives as a longer term solution. 

Unfortunately, I have larger paired 500Gb HDDs in the boot mirror and smaller replacement 120Gb SSDs. The boot drives are sporting about 3-4Gb of actual disk usage since I use Ceph & CephFS for the shared storage and not local storage on the nodes. This makes the smaller disks better options for my use-case and from a cost perspective.

So I need to figure out how to migrate the content from the existing paired mirror 500Gb HDD to the new 120Gb SSD while preserving the **bootable** ZFS mirror. Welcome to the adventure of using old hardware.

[![Proxmox 8.2.4 ZFS Boot Mirror](/assets/images/zfs-boot-mirror-proxmox8-001.png){:width="40%" height="40%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/zfs-boot-mirror-proxmox8-001.png){:target="_blank"}

<!-- excerpt-end -->

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
