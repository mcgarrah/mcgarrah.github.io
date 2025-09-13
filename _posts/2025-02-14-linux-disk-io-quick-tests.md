---
title:  "Linux Disk I/O Performance in the Homelab"
layout: post
categories: [technical, homelab, hardware]
tags: [linux, storage, performance, iops, benchmarking, homelab, testing]
published: true
---

I swapped my physical disks around in my low-end testing hardware cluster. I have a mixture of soldered to the motherboard eMMC and an external USB3 Thumbdrive serving for a root file systems and external `/usr` volumes now. I would like a quick performance check on reading and writing to those file systems. I also don't want to setup a huge performance benchmark suite or additional tooling. I just want some quick results at this point.

My basic question is what did I loose in this decision to break out my `/usr` out to an external USB3 drive. How much performance did I loose?

<!-- excerpt-end -->

Here is my file system layout after my updates. Notice the `/dev/mmcblk0p2` is my root file system `/` on the eMMC storage. I also now have a new `/dev/sda1` for my `/usr`. The advantage here is I suddenly have the drives not tipping against the 70% or higher in usage. This disk space gets especially tight when doing OS upgrades with multiple kernels and packages ready for fallbacks.

Here are the two important file systems.

``` console
root@pve1:~# df -h / /usr
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G 1021M  4.4G  19% /
/dev/sda1        29G  3.5G   24G  13% /usr
```

This is the complete layout for those interested in the broader setup on these Dell Wyse 3040s which are featured often in my testing.

``` console
root@pve1:~# df -h
Filesystem      Size  Used Avail Use% Mounted on
udev            910M     0  910M   0% /dev
tmpfs           189M  1.7M  187M   1% /run
/dev/mmcblk0p2  5.7G 1021M  4.4G  19% /
/dev/sda1        29G  3.5G   24G  13% /usr
tmpfs           942M   66M  876M   8% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
efivarfs        256K  167K   85K  67% /sys/firmware/efi/efivars
/dev/mmcblk0p1  511M   12M  500M   3% /boot/efi
/dev/fuse       128M   32K  128M   1% /etc/pve
tmpfs           189M     0  189M   0% /run/user/0
```

## Testing write performance

I decide to just pick a value of 1Gb for a file being generated for read and write testing by the `dd` command. There was no specific reason except it seemed like a size that would be big enough to stress the system. These systems have a total of 2GB of RAM so that will push the boxes.

Here are the commands to create two 1Gb files in the `/`/ and `/usr/` file systems.

``` console
root@pve1:~# dd if=/dev/zero of=/root-tempfile bs=1M count=1024 conv=fdatasync
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 99.4486 s, 10.8 MB/s
root@pve1:~# dd if=/dev/zero of=/usr/usr-tempfile bs=1M count=1024 conv=fdatasync
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 28.1933 s, 38.1 MB/s
```

Here are the file systems after the above two files are created.

``` console
root@pve1:~# df -h / /usr
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  2.0G  3.4G  38% /
/dev/sda1        29G  4.5G   23G  17% /usr
```

## Drop caching

[Emptying the buffers cache](https://unix.stackexchange.com/a/87909) by [slm](https://unix.stackexchange.com/users/7453/slm) looked right to me so I used his answer to clear the cache.

``` console
root@pve1:~# free && sync && echo 3 > /proc/sys/vm/drop_caches && free
               total        used        free      shared  buff/cache   available
Mem:         1928172     1516896      113516       69372      520256      411276
Swap:         999420         256      999164
               total        used        free      shared  buff/cache   available
Mem:         1928172     1483148      476584       69372      167920      445024
Swap:         999420         256      999164
```

## Testing read performance

We are reusing the two 1Gb files we generated in the earlier write tests to do the read tests.

``` console
root@pve1:~# dd if=/root-tempfile of=/dev/null bs=1M count=1024
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 8.23189 s, 130 MB/s
root@pve1:~# dd if=/usr/usr-tempfile of=/dev/null bs=1M count=1024
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 7.90485 s, 136 MB/s
```

Finally, I am doing a retest of the read performance to see if caching the files helps me out much. Which was not a barn stormer of a change.

``` console
root@pve1:~# dd if=/root-tempfile of=/dev/null bs=1M count=1024
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 8.0213 s, 134 MB/s
root@pve1:~# dd if=/usr/usr-tempfile of=/dev/null bs=1M count=1024
1024+0 records in
1024+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 7.76729 s, 138 MB/s
```

## Clean up

The two 1Gb files need cleaning up and verification that they are gone.

``` console
root@pve1:~# rm /root-tempfile /usr/usr-tempfile
root@pve1:~# df -h / /usr
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G 1022M  4.4G  19% /
/dev/sda1        29G  3.5G   24G  13% /usr
```

## Conclusions

I had no idea how slow the write speed to the eMMC was as compared to the external USB3 drive. It is a 4x difference with the USB3 winning easily on write. Read speeds are basically the same. With this in mind, I may think about migrating the rest of the eMMC to the USB3. These are old systems and the eMMC is starting to wear out anyway.

A second benefit for migrating is that Proxmox does not see or find the eMMC storage when I used their installation media. To compensate, I have to do a two stage installation with a Debian 12 install that then adds the Proxmox repositories to get these boxes setup on the eMMC storage. If I just install the whole thing to USB3 storage, then Proxmox might see it during the installation stage and I can skip the extra steps.

This is why you test things like this as you sometime get surprises and subvert your expectations. I was honestly not expecting these results.
