---
title:  "ZFS Boot Mirrors on Proxmox 8.2 for the Homelab"
layout: post
published: false
---

From my earlier post [ProxMox 8.2 for the Homelabs](/proxmox-8-homelab/), I offhandedly mentioned that using the Proxmox ZFS boot drive mirrors saved my bacon a couple times. Me, not being a complete idiot, and having been burned multiple times in the past, setup email alerting for major failures including ZFS issues. Well we have disk number four of twelve dropping out of the race into a FAULTED state and I have to deal with recovering a boot mirror again. So I'm still ONLINE but in a DEGRADED state for the bootable ZFS pool for one of the nodes.

Anticipating this problem, I bought a pair of cheap 120Gb SSD drives as a longer term solution. I also have an extra 500Gb HDD sitting in the wings as well to resilver a copy of the good boot drive from the ZFS boot mirror. From that description, you might see my problem. I have larger paired 500Gb HDDs in the boot mirror and smaller replacement 120Gb SSDs. The boot drives are sporting about 3-4Gb of actual disk usage since I use Ceph & CephFS for the shared storage and not local storage on the nodes. This makes the smaller disks better options for my use-case and from a cost perspective.

So I need to figure out how to migrate the content from the existing single good 500Gb HDD to the new 120Gb SSD while preserving the **bootable** ZFS mirror. Welcome to the adventure of using old hardware.

[![Proxmox 8.2.4 ZFS Boot Mirror](/assets/images/zfs-boot-mirror-proxmox8.png){:width="40%" height="40%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/zfs-boot-mirror-proxmox8.png){:target="_blank"}

<!-- excerpt-end -->

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

TODO: stuff when back physically near the machines...

## References

- [Migrate Proxmox VE to smaller root disks](https://aaronlauterer.com/blog/2021/proxmox-ve-migrate-to-smaller-root-disks/) by Aaron Lauterer sounds like what I was planning in part. He also has a follow up [Move GRUB and boot partition to another disk](https://aaronlauterer.com/blog/2021/move-grub-and-boot-to-other-disk/) that may be important for my GRUB legacy boot environments. I don't think I went UEFI boot on the main clusters.
- [proxmox/proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh](https://github.com/kneutron/ansitest/blob/master/proxmox/proxmox-replace-zfs-mirror-boot-disks-with-smaller.sh) shell script to replace larger to smaller disks from Reddit post [Tutorial / HOWTO migrate a PVE ZFS boot/root mirror to smaller disks (256GB to 128GB)](https://www.reddit.com/r/Proxmox/comments/1cr6wn7/tutorial_howto_migrate_a_pve_zfs_bootroot_mirror/).
- [Zetto on Reddit](https://www.reddit.com/r/zfs/comments/sx6ohz/comment/hxqeanr/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) discusses a `ZFS send | ZFS receive` for a new ZFS pool on the new device.
- [ZFS: shrink pool](https://niziak.spox.org/wiki/linux:fs:zfs:shrink#:~:text=e%20nvmpool%20nvme0n1p3-,ZFS%3A%20shrink%20zpool,mirror%2C%20use%20attach%20not%20add) has an interesting trick that might help me out.
