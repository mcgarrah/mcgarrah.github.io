---
title:  "ZFS Boot Mirrors on Proxmox 8.2 for the Homelab - Part 1"
layout: post
published: false
---

From my earlier post [ProxMox 8.2 for the Homelabs](/proxmox-8-homelab/), I offhandedly mentioned that I was using the Proxmox ZFS boot drive mirrors which saved my bacon a couple times. Me, not being a complete idiot, and having been burned multiple times in the past, setup email alerting for major failures including ZFS issues. Well we have drive number five of twelve dropping out of the race into a FAULTED or ERRORS state and I have to deal with recovering a boot mirror again. So I'm still ONLINE but in a DEGRADED state for the bootable ZFS pool for one of the nodes.

Having done this operation wrong several times now and then having to recover from missing steps, I am writing this down in a post so I can find it in the future. I'm also labeling this "Part 1" as I have a longer term goal of resizing the boot mirrors to much smaller cheaper and speedy SSDs and stop using the spinning rust HDDs over time. Unfortunately, ZFS does not like adding smaller drives to a mirror so that will be a "Part 2" post at some time in the distant future when I figure that migration out.

[![Proxmox 8.2.4 ZFS Boot Mirror](/assets/images/zfs-boot-mirror-proxmox8-001.png){:width="40%" height="40%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/zfs-boot-mirror-proxmox8-001.png){:target="_blank"}

<!-- excerpt-end -->

## Confirm bad HDD

Before I get started, these are relatively old systems and occasionally have odd blips with the old hardware. It is worth doing a `zpool clear` and `zpool scrub` on the drive and pool to verify that the drive is actually bad. Pulling SMART values from it isn't a bad idea either. I can confirm this drive is BAD and not coming back. Again, remember this is a HomeLab using really old equipment and not in a production enterprise data center with drives under warranties. These are all salvaged or purchased equipment that are hitting my bank account when I replace parts. So it is worth a test and careful documentation incase it errors again shortly.

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

That drive is not coming back.

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
```

``` console
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
```

``` console
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
```

``` console
root@edgar:~# sfdisk -d /dev/sdb
sfdisk: /dev/sdb: does not contain a recognized partition table
```

``` console
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
```

``` console
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
```

``` console
root@edgar:~# ls /dev/disk/by-id/*-part3
/dev/disk/by-id/ata-ST31000524AS_5VPD6EX2-part3         /dev/disk/by-id/wwn-0x5000039743e86194-part3
/dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3  /dev/disk/by-id/wwn-0x5000c5005c9344c7-part3
```

``` console
root@edgar:~# zpool replace rpool /dev/disk/by-id/ata-ST31000528AS_5VP07Z06-part3 /dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part3
```

``` console
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
```

``` console
root@edgar:~# ls /dev/disk/by-id/*-part2
/dev/disk/by-id/ata-ST31000524AS_5VPD6EX2-part2         /dev/disk/by-id/wwn-0x5000039743e86194-part2
/dev/disk/by-id/ata-TOSHIBA_MQ01ABD100_96EOC9BST-part2  /dev/disk/by-id/wwn-0x5000c5005c9344c7-part2
```

``` console
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
```

``` console
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
```

``` console
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
```

``` console
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
```

``` console
root@edgar:~# proxmox-boot-tool status
Re-executing '/usr/sbin/proxmox-boot-tool' in new private mount namespace..
System currently booted with legacy bios
A4AA-5148 is configured with: grub (versions: 6.8.12-1-pve, 6.8.12-8-pve)
EEC6-6947 is configured with: grub (versions: 6.8.12-1-pve, 6.8.12-8-pve)
```

``` console
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
```

``` console
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
