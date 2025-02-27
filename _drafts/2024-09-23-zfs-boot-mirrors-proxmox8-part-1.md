---
title:  "ZFS Boot Mirrors on Proxmox 8.2 for the Homelab - Part 1"
layout: post
published: false
---

From my earlier post [ProxMox 8.2 for the Homelabs](/proxmox-8-homelab/), I offhandedly mentioned that using the Proxmox ZFS boot drive mirrors saved my bacon a couple times. Me, not being a complete idiot, and having been burned multiple times in the past, setup email alerting for major failures including ZFS issues. Well we have disk number four of twelve dropping out of the race into a FAULTED state and I have to deal with recovering a boot mirror again. So I'm still ONLINE but in a DEGRADED state for the bootable ZFS pool for one of the nodes.

Anticipating this problem, I bought a pair of cheap 120Gb SSD drives as a longer term solution. I also have an extra 500Gb HDD sitting in the wings as well to resilver a copy of the good boot drive from the ZFS boot mirror. From that description, you might see my problem. I have larger paired 500Gb HDDs in the boot mirror and smaller replacement 120Gb SSDs. The boot drives are sporting about 3-4Gb of actual disk usage since I use Ceph & CephFS for the shared storage and not local storage on the nodes. This makes the smaller disks better options for my use-case and from a cost perspective.

So I need to figure out how to migrate the content from the existing single good 500Gb HDD to the new 120Gb SSD while preserving the **bootable** ZFS mirror. Welcome to the adventure of using old hardware.

[![Proxmox 8.2.4 ZFS Boot Mirror](/assets/images/zfs-boot-mirror-proxmox8-001.png){:width="40%" height="40%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/zfs-boot-mirror-proxmox8-001.png){:target="_blank"}

<!-- excerpt-end -->

## WORKING EXAMPLE IN ORDER

Here is a complete working session with a replacement of a bad disk in a ZFS Boot Mirror. I pulled the bad drive and replaced with a new wiped drive of the same size.

The steps at a high-level:

1. copy the existing partition structures from the working bootdisk to the new disk
2. replace the old disk with the new disk in the zfs rpool mirror
3. verify the disk is resilvering (copy data from good disk)
4. verify bootloader on good disk and error on new disk
5. initialize the new disk for proxmox booting and setup boot loader
6. verify both disks are now proxmox bootable drives
7. start a zfs scrub operation on the mirror (chkdsk for zfs)
8. verify no errors on scrub

``` console
Linux edgar 6.8.12-8-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.12-8 (2025-01-24T12:32Z) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Tue Feb 25 12:28:43 EST 2025 from 192.168.86.12 on pts/0
root@edgar:~# zpool status
  pool: rpool
 state: DEGRADED
status: One or more devices could not be used because the label is missing or
        invalid.  Sufficient replicas exist for the pool to continue
        functioning in a degraded state.
action: Replace the device using 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
  scan: scrub repaired 0B in 00:02:38 with 0 errors on Sun Feb  9 00:26:39 2025
config:

        NAME                                 STATE     READ WRITE CKSUM
        rpool                                DEGRADED     0     0     0
          mirror-0                           DEGRADED     0     0     0
            ata-ST31000524AS_5VPD6EX2-part3  ONLINE       0     0     0
            12573010284538016996             UNAVAIL      0     0     0  was /dev/disk/by-id/ata-ST31000528AS_5VP07Z06-part3

errors: No known data errors
root@edgar:~# fdisk -l
The backup GPT table is corrupt, but the primary appears OK, so that will be used.
Disk /dev/sda: 931.51 GiB, 1000204886016 bytes, 1953525168 sectors
Disk model: ST31000524AS    
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: E42473C4-29C7-4AA9-9DC9-383904626EAA

Device       Start        End    Sectors   Size Type
/dev/sda1       34       2047       2014  1007K BIOS boot
/dev/sda2     2048    2099199    2097152     1G EFI System
/dev/sda3  2099200 1953525134 1951425935 930.5G Solaris /usr & Apple ZFS


Disk /dev/sdb: 931.51 GiB, 1000204886016 bytes, 1953525168 sectors
Disk model: TOSHIBA MQ01ABD1
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes


Disk /dev/sdc: 476.94 GiB, 512110190592 bytes, 1000215216 sectors
Disk model: SAMSUNG MZ7LN512
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/mapper/ceph--aab6474c--ecbf--4f91--b894--b5401452a200-osd--wal--4b062820--ad60--4417--aa62--d7a920b6cd6a: 100 GiB, 107374182400 bytes, 209715200 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/mapper/ceph--aab6474c--ecbf--4f91--b894--b5401452a200-osd--wal--11933296--4c24--4e3b--a34e--63170f3db9f7: 100 GiB, 107374182400 bytes, 209715200 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/mapper/ceph--aab6474c--ecbf--4f91--b894--b5401452a200-osd--wal--42e93a7e--3c6c--48d1--928b--3f4f76cf9f83: 100 GiB, 107374182400 bytes, 209715200 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes


Disk /dev/sdd: 4.55 TiB, 5000981077504 bytes, 9767541167 sectors
Disk model: Portable        
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes


Disk /dev/mapper/ceph--d0c78e31--167c--44a6--afa4--95b4947ef5f8-osd--block--74d21c73--a133--49d6--9127--72cf18a04dcf: 4.55 TiB, 5000977711104 bytes, 9767534592 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes


Disk /dev/sde: 4.55 TiB, 5000981077504 bytes, 9767541167 sectors
Disk model: Portable        
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes


Disk /dev/mapper/ceph--19c9343e--24f7--47ea--a33c--f5451f8444bc-osd--block--0d2ea87f--04c1--4cc4--83ce--b4d9de60afbb: 4.55 TiB, 5000977711104 bytes, 9767534592 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes


Disk /dev/sdf: 4.55 TiB, 5000981077504 bytes, 9767541167 sectors
Disk model: BUP Portable    
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes


Disk /dev/mapper/ceph--20ba9f5a--0e68--4462--b4d8--c68768e7fc10-osd--block--21efa385--b8e0--4ffc--ab69--da6d79fd46d8: 4.55 TiB, 5000977711104 bytes, 9767534592 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
root@edgar:~# sfdisk -d /dev/sda
The backup GPT table is corrupt, but the primary appears OK, so that will be used.
label: gpt
label-id: E42473C4-29C7-4AA9-9DC9-383904626EAA
device: /dev/sda
unit: sectors
first-lba: 34
last-lba: 1953525134
sector-size: 512

/dev/sda1 : start=          34, size=        2014, type=21686148-6449-6E6F-744E-656564454649, uuid=D3D66523-CAA8-4D34-A4C3-94F5BBF3551B
/dev/sda2 : start=        2048, size=     2097152, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, uuid=14CD0815-2A97-4E42-8B21-687ADD2FF4B2
/dev/sda3 : start=     2099200, size=  1951425935, type=6A898CC3-1DD2-11B2-99A6-080020736631, uuid=2CC1871D-E802-4C79-969E-3931961FB1E9
root@edgar:~# sfdisk -d /dev/sdb
sfdisk: /dev/sdb: does not contain a recognized partition table
root@edgar:~# sfdisk -d /dev/sda | sfdisk /dev/sdb
The backup GPT table is corrupt, but the primary appears OK, so that will be used.
Checking that no-one is using this disk right now ... OK

Disk /dev/sdb: 931.51 GiB, 1000204886016 bytes, 1953525168 sectors
Disk model: TOSHIBA MQ01ABD1
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes

>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Created a new GPT disklabel (GUID: E42473C4-29C7-4AA9-9DC9-383904626EAA).
/dev/sdb1: Created a new partition 1 of type 'BIOS boot' and of size 1007 KiB.
/dev/sdb2: Created a new partition 2 of type 'EFI System' and of size 1 GiB.
/dev/sdb3: Created a new partition 3 of type 'Solaris /usr & Apple ZFS' and of size 930.5 GiB.
/dev/sdb4: Done.

New situation:
Disklabel type: gpt
Disk identifier: E42473C4-29C7-4AA9-9DC9-383904626EAA

Device       Start        End    Sectors   Size Type
/dev/sdb1       34       2047       2014  1007K BIOS boot
/dev/sdb2     2048    2099199    2097152     1G EFI System
/dev/sdb3  2099200 1953525134 1951425935 930.5G Solaris /usr & Apple ZFS

Partition 1 does not start on physical sector boundary.

The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.
root@edgar:~# zpool status
  pool: rpool
 state: DEGRADED
status: One or more devices could not be used because the label is missing or
        invalid.  Sufficient replicas exist for the pool to continue
        functioning in a degraded state.
action: Replace the device using 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
  scan: scrub repaired 0B in 00:02:38 with 0 errors on Sun Feb  9 00:26:39 2025
config:

        NAME                                 STATE     READ WRITE CKSUM
        rpool                                DEGRADED     0     0     0
          mirror-0                           DEGRADED     0     0     0
            ata-ST31000524AS_5VPD6EX2-part3  ONLINE       0     0     0
            12573010284538016996             UNAVAIL      0     0     0  was /dev/disk/by-id/ata-ST31000528AS_5VP07Z06-part3

errors: No known data errors
root@edgar:~# zpool status
  pool: rpool
 state: DEGRADED
status: One or more devices could not be used because the label is missing or
        invalid.  Sufficient replicas exist for the pool to continue
        functioning in a degraded state.
action: Replace the device using 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
  scan: scrub repaired 0B in 00:02:38 with 0 errors on Sun Feb  9 00:26:39 2025
config:

        NAME                                 STATE     READ WRITE CKSUM
        rpool                                DEGRADED     0     0     0
          mirror-0                           DEGRADED     0     0     0
            ata-ST31000524AS_5VPD6EX2-part3  ONLINE       0     0     0
            12573010284538016996             UNAVAIL      0     0     0  was /dev/disk/by-id/ata-ST31000528AS_5VP07Z06-part3

errors: No known data errors
root@edgar:~# ls /dev/disk/by-id/*-part3
/dev/disk/by-id/ata-ST31000524AS_5VPD6EX2-part3         /dev/disk/by-id/wwn-0x5000039743e86194-part3
/dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3  /dev/disk/by-id/wwn-0x5000c5005c9344c7-part3
root@edgar:~# zpool replace rpool /dev/disk/by-id/ata-ST31000528AS_5VP07Z06-part3 /dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3
root@edgar:~# zpool status
  pool: rpool
 state: DEGRADED
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Tue Feb 25 15:33:38 2025
        6.73G / 6.73G scanned, 40.7M / 6.73G issued at 40.7M/s
        25.2M resilvered, 0.59% done, 00:02:48 to go
config:

        NAME                                          STATE     READ WRITE CKSUM
        rpool                                         DEGRADED     0     0     0
          mirror-0                                    DEGRADED     0     0     0
            ata-ST31000524AS_5VPD6EX2-part3           ONLINE       0     0     0
            replacing-1                               DEGRADED     0     0     0
              12573010284538016996                    UNAVAIL      0     0     0  was /dev/disk/by-id/ata-ST31000528AS_5VP07Z06-part3
              ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3  ONLINE       0     0     0  (resilvering)

errors: No known data errors
root@edgar:~# ls /dev/disk/by-id/*-part2
/dev/disk/by-id/ata-ST31000524AS_5VPD6EX2-part2         /dev/disk/by-id/wwn-0x5000039743e86194-part2
/dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part2  /dev/disk/by-id/wwn-0x5000c5005c9344c7-part2
root@edgar:~# proxmox-boot-tool status
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
System currently booted with legacy bios
EEC6-6947 is configured with: grub (versions: 6.8.12-1-pve, 6.8.12-8-pve)
WARN: /dev/disk/by-uuid/EEC8-2CDA does not exist - clean '/etc/kernel/proxmox-boot-uuids'! - skipping
root@edgar:~# proxmox-boot-tool clean
Checking whether ESP 'EEC6-6947' exists.. Found!
Checking whether ESP 'EEC8-2CDA' exists.. Not found!
Sorting and removing duplicate ESPs..
root@edgar:~# proxmox-boot-tool format /dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part2
UUID="" SIZE="1073741824" FSTYPE="" PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b" PKNAME="sdb" MOUNTPOINT=""
Formatting '/dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part2' as vfat..
mkfs.fat 4.2 (2021-01-31)
Done.
root@edgar:~# proxmox-boot-tool init /dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part2 grub
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
UUID="A4AA-5148" SIZE="1073741824" FSTYPE="vfat" PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b" PKNAME="sdb" MOUNTPOINT=""
Mounting '/dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part2' on '/var/tmp/espmounts/A4AA-5148'.
Installing grub i386-pc target..
Installing for i386-pc platform.
Installation finished. No error reported.
Unmounting '/dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part2'.
Adding '/dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part2' to list of synced ESPs..
Refreshing kernels and initrds..
Running hook script 'proxmox-auto-removal'..
Running hook script 'zz-proxmox-boot'..
Copying and configuring kernels on /dev/disk/by-uuid/A4AA-5148
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.12-8-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-8-pve
Found initrd image: /boot/initrd.img-6.8.12-8-pve
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
done
Copying and configuring kernels on /dev/disk/by-uuid/EEC6-6947
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.12-8-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-8-pve
Found initrd image: /boot/initrd.img-6.8.12-8-pve
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
done
root@edgar:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: resilvered 6.92G in 00:07:21 with 0 errors on Tue Feb 25 15:40:59 2025
config:

        NAME                                        STATE     READ WRITE CKSUM
        rpool                                       ONLINE       0     0     0
          mirror-0                                  ONLINE       0     0     0
            ata-ST31000524AS_5VPD6EX2-part3         ONLINE       0     0     0
            ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3  ONLINE       0     0     0

errors: No known data errors
root@edgar:~# zpool scrub rpool
root@edgar:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: scrub in progress since Tue Feb 25 15:42:02 2025
        6.73G / 6.73G scanned, 301M / 6.73G issued at 60.3M/s
        0B repaired, 4.37% done, 00:01:49 to go
config:

        NAME                                        STATE     READ WRITE CKSUM
        rpool                                       ONLINE       0     0     0
          mirror-0                                  ONLINE       0     0     0
            ata-ST31000524AS_5VPD6EX2-part3         ONLINE       0     0     0
            ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3  ONLINE       0     0     0

errors: No known data errors
root@edgar:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: scrub in progress since Tue Feb 25 15:42:02 2025
        6.73G / 6.73G scanned, 616M / 6.73G issued at 32.4M/s
        0B repaired, 8.94% done, 00:03:13 to go
config:

        NAME                                        STATE     READ WRITE CKSUM
        rpool                                       ONLINE       0     0     0
          mirror-0                                  ONLINE       0     0     0
            ata-ST31000524AS_5VPD6EX2-part3         ONLINE       0     0     0
            ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3  ONLINE       0     0     0

errors: No known data errors
root@edgar:~# proxmox-boot-tool status
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
System currently booted with legacy bios
A4AA-5148 is configured with: grub (versions: 6.8.12-1-pve, 6.8.12-8-pve)
EEC6-6947 is configured with: grub (versions: 6.8.12-1-pve, 6.8.12-8-pve)
root@edgar:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: scrub in progress since Tue Feb 25 15:42:02 2025
        6.73G / 6.73G scanned, 1.86G / 6.73G issued at 33.4M/s
        0B repaired, 27.63% done, 00:02:29 to go
config:

        NAME                                        STATE     READ WRITE CKSUM
        rpool                                       ONLINE       0     0     0
          mirror-0                                  ONLINE       0     0     0
            ata-ST31000524AS_5VPD6EX2-part3         ONLINE       0     0     0
            ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3  ONLINE       0     0     0

errors: No known data errors
root@edgar:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: scrub repaired 0B in 00:04:06 with 0 errors on Tue Feb 25 15:46:08 2025
config:

        NAME                                        STATE     READ WRITE CKSUM
        rpool                                       ONLINE       0     0     0
          mirror-0                                  ONLINE       0     0     0
            ata-ST31000524AS_5VPD6EX2-part3         ONLINE       0     0     0
            ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3  ONLINE       0     0     0

errors: No known data errors
```

## BELOW ARE LOGS FOR OTHER ATTEMPTS

I have several of these events with issues in each.

## Confirm bad HDD

Before I get started, these are relatively old systems and occasionally have odd blips with the old hardware. It is worth doing a `zpool clear` and `zpool scrub` on the drive and pool to verify that the drive is actually bad. Pulling SMART values from it isn't a bad idea either. I can confirm this drive is BAD and not coming back. Again, remember this is a HomeLab using really old equipment and not in a production enterprise data center. These are all salvaged or purchased equipment that are hitting my bank account when I replace parts. So worth a test and careful documentation incase it happens again shortly.

<details>
<summary>Click here for detail console session for <b>zpool</b> status, clear and scrub</summary>

{% highlight console %}
root@tanaka:~# zpool status
  pool: rpool
state: DEGRADED
status: One or more devices are faulted in response to persistent errors.
        Sufficient replicas exist for the pool to continue functioning in a
        degraded state.
action: Replace the faulted device, or use 'zpool clear' to mark the device
        repaired.
  scan: scrub repaired 0B in 00:01:29 with 0 errors on Fri Aug 16 15:35:22 2024
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   DEGRADED     0     0     0
          mirror-0                                              DEGRADED     0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST9500325AS_5VE0S1MT-part3                      FAULTED      6     0     0  too many errors

errors: No known data errors
root@tanaka:~# zpool clear rpool
root@tanaka:~# zpool status
  pool: rpool
state: DEGRADED
status: One or more devices are faulted in response to persistent errors.
        Sufficient replicas exist for the pool to continue functioning in a
        degraded state.
action: Replace the faulted device, or use 'zpool clear' to mark the device
        repaired.
  scan: scrub repaired 0B in 00:01:29 with 0 errors on Fri Aug 16 15:35:22 2024
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   DEGRADED     0     0     0
          mirror-0                                              DEGRADED     0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST9500325AS_5VE0S1MT-part3                      FAULTED      3     0     0  too many errors

errors: No known data errors
root@tanaka:~# zpool scrub rpool
root@tanaka:~# zpool status
  pool: rpool
state: DEGRADED
status: One or more devices are faulted in response to persistent errors.
        Sufficient replicas exist for the pool to continue functioning in a
        degraded state.
action: Replace the faulted device, or use 'zpool clear' to mark the device
        repaired.
  scan: scrub in progress since Sat Aug 17 16:26:20 2024
        3.20G / 3.20G scanned, 169M / 3.20G issued at 33.8M/s
        0B repaired, 5.15% done, 00:01:32 to go
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   DEGRADED     0     0     0
          mirror-0                                              DEGRADED     0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST9500325AS_5VE0S1MT-part3                      FAULTED      6     0     0  too many errors

errors: No known data errors
root@tanaka:~# zpool status
  pool: rpool
state: DEGRADED
status: One or more devices are faulted in response to persistent errors.
        Sufficient replicas exist for the pool to continue functioning in a
        degraded state.
action: Replace the faulted device, or use 'zpool clear' to mark the device
        repaired.
  scan: scrub repaired 0B in 00:01:30 with 0 errors on Sat Aug 17 16:27:50 2024
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   DEGRADED     0     0     0
          mirror-0                                              DEGRADED     0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST9500325AS_5VE0S1MT-part3                      FAULTED      6     0     0  too many errors

errors: No known data errors
{% endhighlight %}
</details>

## Email on ZFS failure

The email from the node with ZFS failure report from `zpool status`:

```console
ZFS has finished a resilver:

   eid: 19
 class: resilver_finish
  host: tanaka
  time: 2024-08-15 23:03:10-0400
  pool: rpool
 state: ONLINE
status: One or more devices are faulted in response to persistent errors.
        Sufficient replicas exist for the pool to continue functioning in a
        degraded state.
action: Replace the faulted device, or use 'zpool clear' to mark the device
        repaired.
  scan: resilvered 268M in 00:02:46 with 0 errors on Thu Aug 15 23:03:10 2024
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   ONLINE       0     0     0
          mirror-0                                              ONLINE       0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST9500325AS_5VE0S1MT-part3                      FAULTED      6   294     3  too many errors

errors: No known data errors
```

In case somebody notices, the OEM APPLE_HDD is perfectly happy after I low level formatted and scrubbed the drive. It is a salvage from a dead Intel MacBook Pro from the 2008 or 2010 era. It behaves just like any other drive but keeps the APPLE identifier. That disk is actually the ONLINE booting hard drive at the moment.

## Plan a back out plan

Step one will be to power down and physically remove the bad HDD and swap in the spare HDD to get a copy of the boot disk using the ZFS mirror recovery. Likely the easy way to do this is just use the typical [ZFS Mirror replace bad disk](https://forum.proxmox.com/threads/zfs-mirror-replace-bad-disk.99469/) and resilver the spare then remove the resilvered spare as insurance. That leaves me a back out plan of swapping the spare as my primary boot disk in case I trash my current boot disk(s). I should probably do a `zpool scrub` when the two good 500Gb drives are is still attached to do a file system consistency check since these are all older HDDs.

Next is to drop in the SSD into the system and try to add it to the mirror with it being smaller. I dunno what will happen there. I assume ZFS will complain it is smaller and not do it.

Some good fortune happened as this particular node in the Proxmox Cluster just happens to not have Ceph OSDs and is the lower-end hardware node for the cluster. So loosing it and reinstalling would be the least painful node. I would still like to figure this out here so I can have a plan if this happened to the more critical nodes. I would like a path to replacing all the spinning rust drives with solid state drives.

## Execute on migration

Here are the steps I plan to do that I have done on prior systems but have not done all these steps for this system.

### Gather information

Here is me gathering up information about the system before I do things that break stuff.

<details>
<summary>Click to see below command details {% highlight console %}root@tanaka:~# zpool status{% endhighlight %}</summary>
{% highlight console %}
  pool: rpool
 state: DEGRADED
status: One or more devices are faulted in response to persistent errors.
        Sufficient replicas exist for the pool to continue functioning in a
        degraded state.
action: Replace the faulted device, or use 'zpool clear' to mark the device
        repaired.
  scan: scrub repaired 0B in 00:01:30 with 0 errors on Sat Aug 17 16:27:50 2024
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   DEGRADED     0     0     0
          mirror-0                                              DEGRADED     0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST9500325AS_5VE0S1MT-part3                      FAULTED      6     0     0  too many errors

errors: No known data errors
{% endhighlight %}
</details>

<details>
<summary>Click to see below command details {% highlight console %}root@tanaka:~# ls -1 /dev/disk/by-id/{% endhighlight %}</summary>
{% highlight console %}
root@tanaka:~# ls -1 /dev/disk/by-id/
ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C
ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part1
ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part2
ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3
ata-HL-DT-ST_DVD+_-RW_GH70N_K1NBANG1500
ata-ST3000DM001-1CH166_Z1F43C4V
ata-ST9500325AS_5VE0S1MT
ata-ST9500325AS_5VE0S1MT-part1
ata-ST9500325AS_5VE0S1MT-part2
ata-ST9500325AS_5VE0S1MT-part3
wwn-0x5000c5001231654d
wwn-0x5000c5001231654d-part1
wwn-0x5000c5001231654d-part2
wwn-0x5000c5001231654d-part3
wwn-0x5000c50065365276
wwn-0x5000cca70fc8e018
wwn-0x5000cca70fc8e018-part1
wwn-0x5000cca70fc8e018-part2
wwn-0x5000cca70fc8e018-part3
{% endhighlight %}
</details>

<details>
<summary>Click to see below command details {% highlight console %}root@tanaka:~# ls /dev/sd*{% endhighlight %}</summary>
{% highlight console %}
/dev/sda  /dev/sda1  /dev/sda2  /dev/sda3  /dev/sdb  /dev/sdc  /dev/sdc1  /dev/sdc2  /dev/sdc3
{% endhighlight %}
</details>

<details>
<summary>Click to see below command details {% highlight console %}root@tanaka:~# fdisk -l{% endhighlight %}</summary>
{% highlight console %}
Disk /dev/sda: 465.76 GiB, 500107862016 bytes, 976773168 sectors
Disk model: APPLE HDD HTS547
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: gpt
Disk identifier: B61233E8-D407-4AF2-9958-55BB3A77E732

Device       Start       End   Sectors   Size Type
/dev/sda1       34      2047      2014  1007K BIOS boot
/dev/sda2     2048   2099199   2097152     1G EFI System
/dev/sda3  2099200 976773134 974673935 464.8G Solaris /usr & Apple ZFS

Partition 1 does not start on physical sector boundary.


Disk /dev/sdb: 2.73 TiB, 3000592982016 bytes, 5860533168 sectors
Disk model: ST3000DM001-1CH1
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: gpt
Disk identifier: EC398D2C-9604-4553-B4DC-38EB57AB3162
{% endhighlight %}
</details>

[![Proxmox 8.2.4 ZFS Boot Mirror](/assets/images/zfs-boot-mirror-proxmox8-002.png){:width="40%" height="40%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/zfs-boot-mirror-proxmox8-002.png){:target="_blank"}

<details>
<summary>Click to see below command details {% highlight console %}root@tanaka:~# proxmox-boot-tool help{% endhighlight %}</summary>
{% highlight console %}
USAGE: /usr/sbin/proxmox-boot-tool format <partition> [--force]

    format <partition> as EFI system partition. Use --force to format even if <partition> is currently in use.

USAGE: /usr/sbin/proxmox-boot-tool init <partition>

    initialize EFI system partition at <partition> for automatic synchronization of Proxmox kernels and their associated initrds.

USAGE: /usr/sbin/proxmox-boot-tool reinit

    reinitialize all configured EFI system partitions from /etc/kernel/proxmox-boot-uuids.

USAGE: /usr/sbin/proxmox-boot-tool clean [--dry-run]

    remove no longer existing EFI system partition UUIDs from /etc/kernel/proxmox-boot-uuids. Use --dry-run to only print outdated entries instead of removing them.

USAGE: /usr/sbin/proxmox-boot-tool refresh [--hook <name>]

    refresh all configured EFI system partitions. Use --hook to only run the specified hook, omit to run all.

USAGE: /usr/sbin/proxmox-boot-tool kernel <add|remove> <kernel-version>

    add/remove proxmox-kernel with ABI <kernel-version> to list of synced kernels, in addition to automatically selected ones.
    NOTE: you need to manually run 'refresh' once you're finished with adding/removing kernels from the list

USAGE: /usr/sbin/proxmox-boot-tool kernel pin <kernel-version> [--next-boot]

    pin proxmox-kernel with ABI <kernel-version> as the default entry to be booted.
    with --next-boot sets <kernel-version> only for the next boot.
    NOTE: you need to manually run 'refresh' once you're finished with pinning kernels

USAGE: /usr/sbin/proxmox-boot-tool kernel unpin [--next-boot]

    unpin removes pinned and next-boot kernel settings.
    with --next-boot only removes the pin for the next boot.

USAGE: /usr/sbin/proxmox-boot-tool kernel list

    list kernel versions currently selected for inclusion on ESPs.

USAGE: /usr/sbin/proxmox-boot-tool status [--quiet]

    Print details about the ESPs configuration. Exits with 0 if any ESP is configured, else with 2.

{% endhighlight %}
</details>

<details>
<summary>Click to see below command details {% highlight console %}root@tanaka:~# proxmox-boot-tool status{% endhighlight %}</summary>
{% highlight console %}
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
System currently booted with legacy bios
1FDB-C48E is configured with: grub (versions: 6.8.12-1-pve, 6.8.4-3-pve)
mount: /var/tmp/espmounts/1FDE-91BC: can't read superblock on /dev/sdc2.
       dmesg(1) may have more information after failed mount system call.
mount of /dev/disk/by-uuid/1FDE-91BC failed - skipping
{% endhighlight %}
</details>

<details>
<summary>Click to see below command details {% highlight console %}root@tanaka:~# zpool list{% endhighlight %}</summary>
{% highlight console %}
NAME    SIZE  ALLOC   FREE  CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP    HEALTH  ALTROOT
rpool   464G  3.20G   461G        -         -     0%     0%  1.00x  DEGRADED  -
{% endhighlight %}
</details>

<details>
<summary>Click to see below command details {% highlight console %}root@tanaka:~# SOME COMMAND{% endhighlight %}</summary>
{% highlight console %}
root@tanaka:~# sfdisk -d /dev/sda
label: gpt
label-id: B61233E8-D407-4AF2-9958-55BB3A77E732
device: /dev/sda
unit: sectors
first-lba: 34
last-lba: 976773134
sector-size: 512

/dev/sda1 : start=          34, size=        2014, type=21686148-6449-6E6F-744E-656564454649, uuid=76368201-C41E-4138-BE10-B0F325DC27D5
/dev/sda2 : start=        2048, size=     2097152, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, uuid=02C96126-2D57-449A-BAD2-EF22A9788203
/dev/sda3 : start=     2099200, size=   974673935, type=6A898CC3-1DD2-11B2-99A6-080020736631, uuid=A3943407-F950-4977-9E50-82C37F9FAF16
{% endhighlight %}
</details>

### Replace Disk and a mistake

I'm going to show what I did and the mistake in order. Below is what I wanted to do when I get the new HDD physically installed to copy the partition tables.

```console
zpool detach rpool ata-ST9500325AS_5VE0S1MT
zpool status
sfdisk -d /dev/sda | sfdisk /dev/sdc
```

Here is the status after pulling the bad disk physically.

```console
root@tanaka:~# zpool status
  pool: rpool
 state: DEGRADED
status: One or more devices could not be used because the label is missing or
        invalid.  Sufficient replicas exist for the pool to continue
        functioning in a degraded state.
action: Replace the device using 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
  scan: scrub repaired 0B in 00:01:30 with 0 errors on Sat Aug 17 16:27:50 2024
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   DEGRADED     0     0     0
          mirror-0                                              DEGRADED     0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            17972357130737311890                                UNAVAIL      0     0     0  was /dev/disk/by-id/ata-ST9500325AS_5VE0S1MT-part3

errors: No known data errors
```

```console
root@tanaka:~# zpool detach rpool 17972357130737311890
root@tanaka:~# zpool status
  pool: rpool
 state: ONLINE
  scan: scrub repaired 0B in 00:01:30 with 0 errors on Sat Aug 17 16:27:50 2024
config:

        NAME                                                  STATE     READ WRITE CKSUM
        rpool                                                 ONLINE       0     0     0
          ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0

errors: No known data errors
```

**Note**: My mistake above was to `zpool detach rpool xxx` rather than replace it with `zpool replace rpool xxx with /dev/disk/by-id/newdisk` and everything would work in the mirror. I also made this mistake on another system and broke the boot mirror. You can see the issue below in the section on recovering a failed mirror.

Fix the boot for Proxmox

```console
root@tanaka:~# proxmox-boot-tool status
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
System currently booted with legacy bios
1FDB-C48E is configured with: grub (versions: 6.8.12-1-pve, 6.8.4-3-pve)
WARN: /dev/disk/by-uuid/1FDE-91BC does not exist - clean '/etc/kernel/proxmox-boot-uuids'! - skipping
root@tanaka:~# proxmox-boot-tool clean
Checking whether ESP '1FDB-C48E' exists.. Found!
Checking whether ESP '1FDE-91BC' exists.. Not found!
Sorting and removing duplicate ESPs..
```

How to find the new hard drive

```console
root@tanaka:~# fdisk -l
Disk /dev/sda: 465.76 GiB, 500107862016 bytes, 976773168 sectors
Disk model: ST3500418AS     
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x412c7110

Device     Boot     Start       End   Sectors   Size Id Type
/dev/sda1  *         2048   1026047   1024000   500M  7 HPFS/NTFS/exFAT
/dev/sda2         1026048 975787206 974761159 464.8G  7 HPFS/NTFS/exFAT
/dev/sda3       975788032 976769023    980992   479M 27 Hidden NTFS WinRE


Disk /dev/sdb: 2.73 TiB, 3000592982016 bytes, 5860533168 sectors
Disk model: ST3000DM001-1CH1
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: gpt
Disk identifier: EC398D2C-9604-4553-B4DC-38EB57AB3162


Disk /dev/sdc: 465.76 GiB, 500107862016 bytes, 976773168 sectors
Disk model: APPLE HDD HTS547
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: gpt
Disk identifier: B61233E8-D407-4AF2-9958-55BB3A77E732

Device       Start       End   Sectors   Size Type
/dev/sdc1       34      2047      2014  1007K BIOS boot
/dev/sdc2     2048   2099199   2097152     1G EFI System
/dev/sdc3  2099200 976773134 974673935 464.8G Solaris /usr & Apple ZFS

Partition 1 does not start on physical sector boundary.
```

From `fdisk` we have an idea of which drives are existing ZFS and not.

```console
root@tanaka:/dev/disk/by-id# ls -al
total 0
drwxr-xr-x 2 root root 420 Aug 22 21:43 .
drwxr-xr-x 8 root root 160 Aug 22 21:42 ..
lrwxrwxrwx 1 root root   9 Aug 22 21:43 ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C -> ../../sdc
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part1 -> ../../sdc1
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part2 -> ../../sdc2
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3 -> ../../sdc3
lrwxrwxrwx 1 root root   9 Aug 22 21:43 ata-HL-DT-ST_DVD+_-RW_GH70N_K1NBANG1500 -> ../../sr0
lrwxrwxrwx 1 root root   9 Aug 22 21:43 ata-ST3000DM001-1CH166_Z1F43C4V -> ../../sdb
lrwxrwxrwx 1 root root   9 Aug 22 21:43 ata-ST3500418AS_5VMQF6GN -> ../../sda
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-ST3500418AS_5VMQF6GN-part1 -> ../../sda1
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-ST3500418AS_5VMQF6GN-part2 -> ../../sda2
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-ST3500418AS_5VMQF6GN-part3 -> ../../sda3
lrwxrwxrwx 1 root root   9 Aug 22 21:43 wwn-0x5000c5002fb4f383 -> ../../sda
lrwxrwxrwx 1 root root  10 Aug 22 21:43 wwn-0x5000c5002fb4f383-part1 -> ../../sda1
lrwxrwxrwx 1 root root  10 Aug 22 21:43 wwn-0x5000c5002fb4f383-part2 -> ../../sda2
lrwxrwxrwx 1 root root  10 Aug 22 21:43 wwn-0x5000c5002fb4f383-part3 -> ../../sda3
lrwxrwxrwx 1 root root   9 Aug 22 21:43 wwn-0x5000c50065365276 -> ../../sdb
lrwxrwxrwx 1 root root   9 Aug 22 21:43 wwn-0x5000cca70fc8e018 -> ../../sdc
lrwxrwxrwx 1 root root  10 Aug 22 21:43 wwn-0x5000cca70fc8e018-part1 -> ../../sdc1
lrwxrwxrwx 1 root root  10 Aug 22 21:43 wwn-0x5000cca70fc8e018-part2 -> ../../sdc2
lrwxrwxrwx 1 root root  10 Aug 22 21:43 wwn-0x5000cca70fc8e018-part3 -> ../../sdc3
```

The new disk is found in the above... as `/dev/sda` with paritions.

```console
Disk /dev/sda: 465.76 GiB, 500107862016 bytes, 976773168 sectors
Disk model: ST3500418AS     
(also NTFS)

lrwxrwxrwx 1 root root   9 Aug 22 21:43 ata-ST3500418AS_5VMQF6GN -> ../../sda
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-ST3500418AS_5VMQF6GN-part1 -> ../../sda1
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-ST3500418AS_5VMQF6GN-part2 -> ../../sda2
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-ST3500418AS_5VMQF6GN-part3 -> ../../sda3
```

This is the current boot disk from the above... as `/dev/sdc` also with parititions.

```console
Disk /dev/sdc: 465.76 GiB, 500107862016 bytes, 976773168 sectors
Disk model: APPLE HDD HTS547

lrwxrwxrwx 1 root root   9 Aug 22 21:43 ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C -> ../../sdc
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part1 -> ../../sdc1
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part2 -> ../../sdc2
lrwxrwxrwx 1 root root  10 Aug 22 21:43 ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3 -> ../../sdc3
```

**Note**: These devices will be different on every system so don't just copy/paste my commands.

This is the big next step which is to copy the partitions and configuration to the new disk.
This command will extract and copy the configuration of the current boot disk to the new disk.

```console
sfdisk -d /dev/sdc | sfdisk /dev/sda
```

Run a test of the extract command to console.

```console
root@tanaka:~# sfdisk -d /dev/sdc
label: gpt
label-id: B61233E8-D407-4AF2-9958-55BB3A77E732
device: /dev/sdc
unit: sectors
first-lba: 34
last-lba: 976773134
sector-size: 512

/dev/sdc1 : start=          34, size=        2014, type=21686148-6449-6E6F-744E-656564454649, uuid=76368201-C41E-4138-BE10-B0F325DC27D5
/dev/sdc2 : start=        2048, size=     2097152, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, uuid=02C96126-2D57-449A-BAD2-EF22A9788203
/dev/sdc3 : start=     2099200, size=   974673935, type=6A898CC3-1DD2-11B2-99A6-080020736631, uuid=A3943407-F950-4977-9E50-82C37F9FAF16
```

Now run the above extract and pipe to the new disk.

```console
root@tanaka:~# sfdisk -d /dev/sdc | sfdisk /dev/sda
Checking that no-one is using this disk right now ... OK

Disk /dev/sda: 465.76 GiB, 500107862016 bytes, 976773168 sectors
Disk model: ST3500418AS     
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x412c7110

Old situation:

Device     Boot     Start       End   Sectors   Size Id Type
/dev/sda1  *         2048   1026047   1024000   500M  7 HPFS/NTFS/exFAT
/dev/sda2         1026048 975787206 974761159 464.8G  7 HPFS/NTFS/exFAT
/dev/sda3       975788032 976769023    980992   479M 27 Hidden NTFS WinRE

>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Script header accepted.
>>> Created a new GPT disklabel (GUID: B61233E8-D407-4AF2-9958-55BB3A77E732).
/dev/sda1: Created a new partition 1 of type 'BIOS boot' and of size 1007 KiB.
/dev/sda2: Created a new partition 2 of type 'EFI System' and of size 1 GiB.
Partition #2 contains a ntfs signature.
/dev/sda3: Created a new partition 3 of type 'Solaris /usr & Apple ZFS' and of size 464.8 GiB.
/dev/sda4: Done.

New situation:
Disklabel type: gpt
Disk identifier: B61233E8-D407-4AF2-9958-55BB3A77E732

Device       Start       End   Sectors   Size Type
/dev/sda1       34      2047      2014  1007K BIOS boot
/dev/sda2     2048   2099199   2097152     1G EFI System
/dev/sda3  2099200 976773134 974673935 464.8G Solaris /usr & Apple ZFS

The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.
```

Format the Proxmox Boot Partition for the new disk and be sure to use the partition not the full device.

```console
root@tanaka:~# proxmox-boot-tool format /dev/disk/by-id/ata-ST3500418AS_5VMQF6GN-part2
UUID="" SIZE="1073741824" FSTYPE="" PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b" PKNAME="sda" MOUNTPOINT=""
Formatting '/dev/disk/by-id/ata-ST3500418AS_5VMQF6GN-part2' as vfat..
mkfs.fat 4.2 (2021-01-31)
Done.
```

Initialize the new partition with GRUB if that is what you are using.

```console
root@tanaka:~# proxmox-boot-tool init /dev/disk/by-id/ata-ST3500418AS_5VMQF6GN-part2 grub
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
UUID="9BB0-3E21" SIZE="1073741824" FSTYPE="vfat" PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b" PKNAME="sda" MOUNTPOINT=""
Mounting '/dev/disk/by-id/ata-ST3500418AS_5VMQF6GN-part2' on '/var/tmp/espmounts/9BB0-3E21'.
Installing grub i386-pc target..
Installing for i386-pc platform.
Installation finished. No error reported.
Unmounting '/dev/disk/by-id/ata-ST3500418AS_5VMQF6GN-part2'.
Adding '/dev/disk/by-id/ata-ST3500418AS_5VMQF6GN-part2' to list of synced ESPs..
Refreshing kernels and initrds..
Running hook script 'proxmox-auto-removal'..
Running hook script 'zz-proxmox-boot'..
Copying and configuring kernels on /dev/disk/by-uuid/1FDB-C48E
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.4-3-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
Found linux image: /boot/vmlinuz-6.8.4-3-pve
Found initrd image: /boot/initrd.img-6.8.4-3-pve
done
Copying and configuring kernels on /dev/disk/by-uuid/9BB0-3E21
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.4-3-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
Found linux image: /boot/vmlinuz-6.8.4-3-pve
Found initrd image: /boot/initrd.img-6.8.4-3-pve
done
```

Do a status on the zfs pools... and you see no mirrors.

```console
root@tanaka:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: scrub repaired 0B in 00:01:48 with 0 errors on Thu Aug 22 22:18:33 2024
remove: Removal of vdev 3 copied 3.14G in 0h1m, completed on Thu Aug 22 22:54:20 2024
        183K memory used for removed device mappings
config:

        NAME                                                  STATE     READ WRITE CKSUM
        rpool                                                 ONLINE       0     0     0
          ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
```

Now attach the new prepared disk to the existing `rpool` and notice I used parition 3 from the new disk. Immediately do a zfs pool status and see the resilving process kick off.

```console
root@tanaka:~# zpool attach rpool ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3 /dev/disk/by-id/ata-ST3500418AS_5VMQF6GN-part3
root@tanaka:~# zpool status -v
  pool: rpool
 state: ONLINE
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Thu Aug 22 22:57:00 2024
        3.14G / 3.14G scanned, 69.1M / 3.14G issued at 9.88M/s
        37.3M resilvered, 2.15% done, no estimated completion time
remove: Removal of vdev 3 copied 3.14G in 0h1m, completed on Thu Aug 22 22:54:20 2024
        183K memory used for removed device mappings
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   ONLINE       0     0     0
          mirror-4                                              ONLINE       0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST3500418AS_5VMQF6GN-part3                      ONLINE       0     0     0  (resilvering)

errors: No known data errors
```

Check the status again shortly and it should be complete pretty quickly if you don't have a lot of data.

```console
root@tanaka:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: resilvered 3.21G in 00:02:23 with 0 errors on Thu Aug 22 22:59:23 2024
remove: Removal of vdev 3 copied 3.14G in 0h1m, completed on Thu Aug 22 22:54:20 2024
        183K memory used for removed device mappings
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   ONLINE       0     0     0
          mirror-4                                              ONLINE       0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST3500418AS_5VMQF6GN-part3                      ONLINE       0     0     0

errors: No known data errors
```

Run a zfs scrub against the rpool to do the equivolant of a CHKDSK on the file system and devices.

```console
root@tanaka:~# zpool scrub rpool
root@tanaka:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: scrub in progress since Thu Aug 22 23:00:16 2024
        3.14G / 3.14G scanned, 458M / 3.14G issued at 41.7M/s
        0B repaired, 14.24% done, 00:01:06 to go
remove: Removal of vdev 3 copied 3.14G in 0h1m, completed on Thu Aug 22 22:54:20 2024
        183K memory used for removed device mappings
config:

        NAME                                                    STATE     READ WRITE CKSUM
        rpool                                                   ONLINE       0     0     0
          mirror-4                                              ONLINE       0     0     0
            ata-APPLE_HDD_HTS547550A9E384_J2250055GMJ83C-part3  ONLINE       0     0     0
            ata-ST3500418AS_5VMQF6GN-part3                      ONLINE       0     0     0

errors: No known data errors
```

Double check the Proxmox Boot has both disks and for my case the `grub` boot initialized and ready.

```console
root@tanaka:~# proxmox-boot-tool status
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
System currently booted with legacy bios
1FDB-C48E is configured with: grub (versions: 6.8.12-1-pve, 6.8.4-3-pve)
9BB0-3E21 is configured with: grub (versions: 6.8.12-1-pve, 6.8.4-3-pve)
```

We now have a fully working mirrored zfs boot for Proxmox.







---

My "oh, crap" moment... I don't have a mirror on a primary ceph node...

```console
root@harlan:~# zpool status
  pool: rpool
 state: ONLINE
  scan: scrub repaired 0B in 00:01:49 with 0 errors on Sun Aug 11 00:25:50 2024
remove: Removal of vdev 1 copied 2.59M in 0h0m, completed on Mon Jan 15 20:01:38 2024
        1.95K memory used for removed device mappings
config:

        NAME                                    STATE     READ WRITE CKSUM
        rpool                                   ONLINE       0     0     0
          ata-ST500DM002-1BD142_Z3TGX1AS-part3  ONLINE       0     0     0
          ata-ST500DM002-1SB10A_ZA45K50E-part3  ONLINE       0     0     0

errors: No known data errors
root@harlan:~# zpool remove rpool ata-ST500DM002-1SB10A_ZA45K50E-part3
root@harlan:~# proxmox-boot-tool status
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
System currently booted with legacy bios
EAD4-484A is configured with: grub (versions: 6.8.12-1-pve, 6.8.4-3-pve)
WARN: /dev/disk/by-uuid/EAD6-7F83 does not exist - clean '/etc/kernel/proxmox-boot-uuids'! - skipping
root@harlan:~# ls -al /dev/disk/by-uuid/
total 0
drwxr-xr-x 2 root root  80 Aug 22 12:31 .
drwxr-xr-x 8 root root 160 Aug 22 12:30 ..
lrwxrwxrwx 1 root root  10 Aug 22 12:31 16326331070668978925 -> ../../sda3
lrwxrwxrwx 1 root root  10 Aug 22 12:31 EAD4-484A -> ../../sda2

root@harlan:~# ls -al /dev/disk/by-id/
total 0
drwxr-xr-x 2 root root 900 Aug 22 13:10 .
drwxr-xr-x 8 root root 160 Aug 22 12:30 ..
lrwxrwxrwx 1 root root   9 Aug 22 12:40 ata-CT500MX500SSD1_2204E6009C80 -> ../../sdc
lrwxrwxrwx 1 root root   9 Aug 22 12:31 ata-HL-DT-ST_DVDRAM_GH22NS50_K0022SM5854 -> ../../sr0
lrwxrwxrwx 1 root root   9 Aug 22 12:31 ata-ST5000LM000-2AN170_WCJ1YNBJ -> ../../sdf
lrwxrwxrwx 1 root root   9 Aug 22 12:31 ata-ST5000LM000-2AN170_WCJ62JB9 -> ../../sdd
lrwxrwxrwx 1 root root   9 Aug 22 12:31 ata-ST500DM002-1BD142_Z3TGX1AS -> ../../sda
lrwxrwxrwx 1 root root  10 Aug 22 12:31 ata-ST500DM002-1BD142_Z3TGX1AS-part1 -> ../../sda1
lrwxrwxrwx 1 root root  10 Aug 22 12:31 ata-ST500DM002-1BD142_Z3TGX1AS-part2 -> ../../sda2
lrwxrwxrwx 1 root root  10 Aug 22 12:31 ata-ST500DM002-1BD142_Z3TGX1AS-part3 -> ../../sda3
lrwxrwxrwx 1 root root   9 Aug 22 12:31 ata-ST500DM002-1SB10A_ZA45K50E -> ../../sdb
lrwxrwxrwx 1 root root  10 Aug 22 12:31 ata-ST500DM002-1SB10A_ZA45K50E-part1 -> ../../sdb1
lrwxrwxrwx 1 root root  10 Aug 22 12:31 ata-ST500DM002-1SB10A_ZA45K50E-part2 -> ../../sdb2
lrwxrwxrwx 1 root root  10 Aug 22 12:31 ata-ST500DM002-1SB10A_ZA45K50E-part3 -> ../../sdb3
...
```

```console
root@harlan:~# proxmox-boot-tool clean
Checking whether ESP 'EAD4-484A' exists.. Found!
Checking whether ESP 'EAD6-7F83' exists.. Not found!
Sorting and removing duplicate ESPs..
root@harlan:~# proxmox-boot-tool format /dev/disk/by-id/ata-ST500DM002-1SB10A_ZA45K50E-part2
UUID="" SIZE="1073741824" FSTYPE="" PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b" PKNAME="sdb" MOUNTPOINT=""
Formatting '/dev/disk/by-id/ata-ST500DM002-1SB10A_ZA45K50E-part2' as vfat..
mkfs.fat 4.2 (2021-01-31)
Done.
root@harlan:~# proxmox-boot-tool init /dev/disk/by-id/ata-ST500DM002-1SB10A_ZA45K50E-part2 grub
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
UUID="D72B-D02D" SIZE="1073741824" FSTYPE="vfat" PARTTYPE="c12a7328-f81f-11d2-ba4b-00a0c93ec93b" PKNAME="sdb" MOUNTPOINT=""
Mounting '/dev/disk/by-id/ata-ST500DM002-1SB10A_ZA45K50E-part2' on '/var/tmp/espmounts/D72B-D02D'.
Installing grub i386-pc target..
Installing for i386-pc platform.
Installation finished. No error reported.
Unmounting '/dev/disk/by-id/ata-ST500DM002-1SB10A_ZA45K50E-part2'.
Adding '/dev/disk/by-id/ata-ST500DM002-1SB10A_ZA45K50E-part2' to list of synced ESPs..
Refreshing kernels and initrds..
Running hook script 'proxmox-auto-removal'..
Running hook script 'zz-proxmox-boot'..
Copying and configuring kernels on /dev/disk/by-uuid/D72B-D02D
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.4-3-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
Found linux image: /boot/vmlinuz-6.8.4-3-pve
Found initrd image: /boot/initrd.img-6.8.4-3-pve
done
Copying and configuring kernels on /dev/disk/by-uuid/EAD4-484A
        Copying kernel 6.8.12-1-pve
        Copying kernel 6.8.4-3-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
Found linux image: /boot/vmlinuz-6.8.4-3-pve
Found initrd image: /boot/initrd.img-6.8.4-3-pve
done
root@harlan:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: scrub repaired 0B in 00:01:49 with 0 errors on Sun Aug 11 00:25:50 2024
remove: Removal of vdev 2 copied 1.95G in 0h0m, completed on Thu Aug 22 23:04:04 2024
        248K memory used for removed device mappings
config:

        NAME                                    STATE     READ WRITE CKSUM
        rpool                                   ONLINE       0     0     0
          ata-ST500DM002-1BD142_Z3TGX1AS-part3  ONLINE       0     0     0

errors: No known data errors
root@harlan:~# zpool attach rpool ata-ST500DM002-1BD142_Z3TGX1AS-part3 /dev/disk/by-id/ata-ST500
ata-ST5000LM000-2AN170_WCJ1YNBJ       ata-ST500DM002-1BD142_Z3TGX1AS-part2  ata-ST500DM002-1SB10A_ZA45K50E-part2
ata-ST5000LM000-2AN170_WCJ62JB9       ata-ST500DM002-1BD142_Z3TGX1AS-part3  ata-ST500DM002-1SB10A_ZA45K50E-part3
ata-ST500DM002-1BD142_Z3TGX1AS        ata-ST500DM002-1SB10A_ZA45K50E        
ata-ST500DM002-1BD142_Z3TGX1AS-part1  ata-ST500DM002-1SB10A_ZA45K50E-part1  
root@harlan:~# zpool attach rpool ata-ST500DM002-1BD142_Z3TGX1AS-part3 /dev/disk/by-id/ata-ST500DM002-1SB10A_ZA45K50E-part3
root@harlan:~# zpool status -v
  pool: rpool
 state: ONLINE
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Thu Aug 22 23:11:26 2024
        165M / 5.14G scanned at 8.70M/s, 0B / 5.14G issued
        0B resilvered, 0.00% done, no estimated completion time
remove: Removal of vdev 2 copied 1.95G in 0h0m, completed on Thu Aug 22 23:04:04 2024
        248K memory used for removed device mappings
config:

        NAME                                      STATE     READ WRITE CKSUM
        rpool                                     ONLINE       0     0     0
          mirror-0                                ONLINE       0     0     0
            ata-ST500DM002-1BD142_Z3TGX1AS-part3  ONLINE       0     0     0
            ata-ST500DM002-1SB10A_ZA45K50E-part3  ONLINE       0     0     0

errors: No known data errors
root@harlan:~# zpool status -v
  pool: rpool
 state: ONLINE
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Thu Aug 22 23:11:26 2024
        5.14G / 5.14G scanned, 407M / 5.14G issued at 25.4M/s
        387M resilvered, 7.74% done, 00:03:10 to go
remove: Removal of vdev 2 copied 1.95G in 0h0m, completed on Thu Aug 22 23:04:04 2024
        248K memory used for removed device mappings
config:

        NAME                                      STATE     READ WRITE CKSUM
        rpool                                     ONLINE       0     0     0
          mirror-0                                ONLINE       0     0     0
            ata-ST500DM002-1BD142_Z3TGX1AS-part3  ONLINE       0     0     0
            ata-ST500DM002-1SB10A_ZA45K50E-part3  ONLINE       0     0     0  (resilvering)

errors: No known data errors
root@harlan:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: resilvered 5.34G in 00:04:45 with 0 errors on Thu Aug 22 23:16:11 2024
remove: Removal of vdev 2 copied 1.95G in 0h0m, completed on Thu Aug 22 23:04:04 2024
        248K memory used for removed device mappings
config:

        NAME                                      STATE     READ WRITE CKSUM
        rpool                                     ONLINE       0     0     0
          mirror-0                                ONLINE       0     0     0
            ata-ST500DM002-1BD142_Z3TGX1AS-part3  ONLINE       0     0     0
            ata-ST500DM002-1SB10A_ZA45K50E-part3  ONLINE       0     0     0

errors: No known data errors
```

Scrub check

```console
root@harlan:~# zpool scrub rpool 
root@harlan:~# zpool status -v
  pool: rpool
 state: ONLINE
  scan: scrub in progress since Thu Aug 22 23:16:58 2024
        5.14G / 5.14G scanned, 89.7M / 5.14G issued at 44.9M/s
        0B repaired, 1.70% done, 00:01:55 to go
remove: Removal of vdev 2 copied 1.95G in 0h0m, completed on Thu Aug 22 23:04:04 2024
        248K memory used for removed device mappings
config:

        NAME                                      STATE     READ WRITE CKSUM
        rpool                                     ONLINE       0     0     0
          mirror-0                                ONLINE       0     0     0
            ata-ST500DM002-1BD142_Z3TGX1AS-part3  ONLINE       0     0     0
            ata-ST500DM002-1SB10A_ZA45K50E-part3  ONLINE       0     0     0

errors: No known data errors
```

THIS BIG MISTAKE on my part...

`zpool remove` and `zpool add` are not the same as `zpool attach` or `zpool replace`. The former are to extend a zpool to be larger without redundancy. The later are to extend a mirror.

PICTURE FROM HARDWARE - 2024-08-22 on Cell Phone

## References

Here are some reference links and interesting articles I found during researching how to do this particular operation of reducing the size of a ZFS pool device.

- [Migrate Proxmox VE to smaller root disks](https://aaronlauterer.com/blog/2021/proxmox-ve-migrate-to-smaller-root-disks/) by Aaron Lauterer sounds like what I was planning in part. He also has a follow up [Move GRUB and boot partition to another disk](https://aaronlauterer.com/blog/2021/move-grub-and-boot-to-other-disk/) that may be important for my GRUB legacy boot environments. I don't think I went UEFI boot on the main clusters.
- [proxmox/proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh](https://github.com/kneutron/ansitest/blob/master/proxmox/proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh) shell script to replace larger to smaller disks from Reddit post [Tutorial / HOWTO migrate a PVE ZFS boot/root mirror to smaller disks (256GB to 128GB)](https://www.reddit.com/r/Proxmox/comments/1cr6wn7/tutorial_howto_migrate_a_pve_zfs_bootroot_mirror/).
- [Zetto on Reddit](https://www.reddit.com/r/zfs/comments/sx6ohz/comment/hxqeanr/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) discusses a `ZFS send | ZFS receive` for a new ZFS pool on the new device.
- [ZFS: shrink pool](https://niziak.spox.org/wiki/linux:fs:zfs:shrink#:~:text=e%20nvmpool%20nvme0n1p3-,ZFS%3A%20shrink%20zpool,mirror%2C%20use%20attach%20not%20add) has an interesting trick that might help me out.

Here are my related posts

- [ProxMox 8.2 for the Homelabs](/proxmox-8-homelab/)
- [ZFS Boot Mirrors on Proxmox 8.2 for the Homelab - Part 1](/zfs-boot-mirrors-proxmox8-part-1/)
- ZFS Boot Mirrors on Proxmox 8.2 for the Homelab - Part 2 (coming soon)
