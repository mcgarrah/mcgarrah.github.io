---
title:  "Proxmox and Ceph scripts for the Homelabs"
layout: post
published: false
---

A couple of useful scripts I've found or created to help manage my Proxmox 8.2 with Ceph Reef (18) cluster. Some are simplistic but useful. I also have some fun commands I've found along the way that I just keep as a cheat-sheet item.

<!-- excerpt-end -->

```console
root@harlan:/mnt/pve/cephfs/bin# ls
ceph-down.sh  cssh                osd-optimize.md     rsync-drive-tvshows.sh
ceph-up.sh    dev-host-rescan.sh  rsync-drive-sdg.sh  set-osd-mclock-max-cap-iops.sh
```

Ceph Mon won't start because 95% full disk. Or less than 5% free. After upgrade of cluster I'm tight on space.

```console
root@pve3:~# bash /mnt/pve/cephfs/bin/cssh "hostname && df -h /"
pve1
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  5.4G  283M  95% /
pve3
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  5.4G  285M  95% /
pve2
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  5.5G  228M  96% /
```

### APT CACHE

First step is clean out the APT CACHE for a good 10% reduction.

```console
root@pve3:~# bash /mnt/pve/cephfs/bin/cssh "hostname && apt-get clean && df -h /"
pve1
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.6G  771M  86% /
pve3
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.5G  874M  85% /
pve2
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.6G  828M  85% /
```

### `atop` issue

`atop` stores logs daily in `/var/log/atop/atop_YYYYMMDD` which is consuming lots of space for these systems. You can `man atop` and search for `RAW DATA STORAGE` section for details.

```console
root@pve1:/etc/default# cat atop 
# /etc/default/atop
# see man atoprc for more possibilities to configure atop execution

LOGOPTS=""
LOGINTERVAL=600
LOGGENERATIONS=28
LOGPATH=/var/log/atop
root@pve1:/etc/default# du -msh /var/log/atop
277M    /var/log/atop
```

```console
root@pve1:/etc/default# bash /mnt/pve/cephfs/bin/cssh "hostname && apt-get install jq -y && apt-get remove atop -y"
```

Be very careful with `rm -rf` commands but this was appropriate.

```console
root@pve1:~# bash /mnt/pve/cephfs/bin/cssh "hostname && df -h / && rm -rf /var/log/atop && df -h /"
pve2
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.6G  827M  85% /
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.3G  1.1G  80% /
pve1
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.6G  769M  86% /
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.4G  1.1G  81% /
pve3
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.5G  872M  85% /
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  4.3G  1.2G  80% /
```

### Find big packages

Here is a quick way to find the size of debian packages and their on disk sizes

```console
root@pve1:~# dpkg-query -W -f='${Installed-Size;8}  ${Package}\n' | sort -n | tail -10
   51483  proxmox-backup-restore-image
   83933  ceph-osd
   93078  ceph-common
  114610  libllvm15
  308160  pve-qemu-kvm
  308520  pve-firmware
  398601  linux-image-6.1.0-18-amd64
  398628  linux-image-6.1.0-23-amd64
  538392  proxmox-kernel-6.8.12-1-pve-signed
  564229  proxmox-kernel-6.8.8-3-pve-signed
```

#### PVE kernel cleanups

[Proxmox VE Kernel Clean](https://tteck.github.io/Proxmox/#proxmox-ve-kernel-clean] Cleaning unused kernel images is beneficial for reducing the length of the GRUB menu and freeing up disk space. By removing old, unused kernels, the system is able to conserve disk space and streamline the boot process.

This is an easy one to recover some disk space after an upgrade of the PVE Cluster. You can run this from the website or the one-liner below.

---

One liner for quick execution

```console
apt purge -y $(dpkg --list | grep 'kernel-.*-pve' | awk '{print $2}' | grep -v "$(uname -r)" | sort -V)
```

```console
root@pve3:~# apt purge -y $(dpkg --list | grep 'kernel-.*-pve' | awk '{print $2}' | grep -v "$(uname -r)" | sort -V)
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages will be REMOVED:
  proxmox-kernel-6.8.8-3-pve-signed*
0 upgraded, 0 newly installed, 1 to remove and 1 not upgraded.
After this operation, 578 MB disk space will be freed.
(Reading database ... 60726 files and directories currently installed.)
Removing proxmox-kernel-6.8.8-3-pve-signed (6.8.8-3) ...
Examining /etc/kernel/postrm.d.
run-parts: executing /etc/kernel/postrm.d/initramfs-tools 6.8.8-3-pve /boot/vmlinuz-6.8.8-3-pve
update-initramfs: Deleting /boot/initrd.img-6.8.8-3-pve
run-parts: executing /etc/kernel/postrm.d/proxmox-auto-removal 6.8.8-3-pve /boot/vmlinuz-6.8.8-3-pve
run-parts: executing /etc/kernel/postrm.d/zz-proxmox-boot 6.8.8-3-pve /boot/vmlinuz-6.8.8-3-pve
Re-executing '/etc/kernel/postrm.d/zz-proxmox-boot' in new private mount namespace..
No /etc/kernel/proxmox-boot-uuids found, skipping ESP sync.
run-parts: executing /etc/kernel/postrm.d/zz-update-grub 6.8.8-3-pve /boot/vmlinuz-6.8.8-3-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
Adding boot menu entry for UEFI Firmware Settings ...
done
(Reading database ... 53021 files and directories currently installed.)
Purging configuration files for proxmox-kernel-6.8.8-3-pve-signed (6.8.8-3) ...
Examining /etc/kernel/postrm.d.
run-parts: executing /etc/kernel/postrm.d/initramfs-tools 6.8.8-3-pve /boot/vmlinuz-6.8.8-3-pve
update-initramfs: Deleting /boot/initrd.img-6.8.8-3-pve
run-parts: executing /etc/kernel/postrm.d/proxmox-auto-removal 6.8.8-3-pve /boot/vmlinuz-6.8.8-3-pve
run-parts: executing /etc/kernel/postrm.d/zz-proxmox-boot 6.8.8-3-pve /boot/vmlinuz-6.8.8-3-pve
Re-executing '/etc/kernel/postrm.d/zz-proxmox-boot' in new private mount namespace..
No /etc/kernel/proxmox-boot-uuids found, skipping ESP sync.
run-parts: executing /etc/kernel/postrm.d/zz-update-grub 6.8.8-3-pve /boot/vmlinuz-6.8.8-3-pve
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
Adding boot menu entry for UEFI Firmware Settings ...
done
```

#### debian kernel cleanup

```console
root@pve3:~# echo $(dpkg --list | grep -Ei 'linux-image|linux-headers' | awk '{print $2}' | grep -v "$(uname -r)" | sort -V)
linux-image-6.1.0-18-amd64 linux-image-6.1.0-23-amd64 linux-image-amd64
root@pve3:~# apt purge -y $(dpkg --list | grep -Ei 'linux-image|linux-headers' | awk '{print $2}' | grep -v "$(uname -r)" | sort -V)
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages will be REMOVED:
  linux-image-6.1.0-18-amd64* linux-image-6.1.0-23-amd64* linux-image-amd64*
0 upgraded, 0 newly installed, 3 to remove and 1 not upgraded.
After this operation, 0 B of additional disk space will be used.
(Reading database ... 60728 files and directories currently installed.)
Purging configuration files for linux-image-6.1.0-18-amd64 (6.1.76-1) ...
I: /vmlinuz.old is now a symlink to boot/vmlinuz-6.8.8-3-pve
I: /initrd.img.old is now a symlink to boot/initrd.img-6.8.8-3-pve
I: /vmlinuz is now a symlink to boot/vmlinuz-6.8.12-1-pve
I: /initrd.img is now a symlink to boot/initrd.img-6.8.12-1-pve
Purging configuration files for linux-image-amd64 (6.1.99-1) ...
Purging configuration files for linux-image-6.1.0-23-amd64 (6.1.99-1) ...
```

```console
root@pve3:~# update-grub
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
Found linux image: /boot/vmlinuz-6.8.8-3-pve
Found initrd image: /boot/initrd.img-6.8.8-3-pve
Adding boot menu entry for UEFI Firmware Settings ...
done
```

---

I missed cleaning up some of the Debian Kernels and not **purging** them.

Remove the meta-package for Debian Kernel

```console
root@pve1:~# apt-get --purge remove linux-image-amd64
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages will be REMOVED:
  linux-image-amd64*
0 upgraded, 0 newly installed, 1 to remove and 1 not upgraded.
After this operation, 0 B of additional disk space will be used.
Do you want to continue? [Y/n] Y
(Reading database ... 53076 files and directories currently installed.)
Purging configuration files for linux-image-amd64 (6.1.99-1) ...
```

Remove the debian kernel images

```console
root@pve1:~# dpkg-query -W -f='${Package}\n' | grep -Ei 'linux-image|linux-headers' | sort -n
linux-image-6.1.0-18-amd64
linux-image-6.1.0-23-amd64
root@pve1:~# apt-get --purge remove $(dpkg-query -W -f='${Package}\n' | grep -Ei 'linux-image|linux-headers' | sort -n) -y
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages will be REMOVED:
  linux-image-6.1.0-18-amd64* linux-image-6.1.0-23-amd64*
0 upgraded, 0 newly installed, 2 to remove and 1 not upgraded.
After this operation, 0 B of additional disk space will be used.
(Reading database ... 53076 files and directories currently installed.)
Purging configuration files for linux-image-6.1.0-18-amd64 (6.1.76-1) ...
I: /vmlinuz.old is now a symlink to boot/vmlinuz-6.8.12-1-pve
I: /initrd.img.old is now a symlink to boot/initrd.img-6.8.12-1-pve
I: /vmlinuz is now a symlink to boot/vmlinuz-6.8.12-1-pve
I: /initrd.img is now a symlink to boot/initrd.img-6.8.12-1-pve
Purging configuration files for linux-image-6.1.0-23-amd64 (6.1.99-1) ...
```

Regenerate the grub boot images

```console
root@pve1:~# update-grub
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-6.8.12-1-pve
Found initrd image: /boot/initrd.img-6.8.12-1-pve
Adding boot menu entry for UEFI Firmware Settings ...
done
```

## Final Disk Space

After clean up `atop` and the logs for it, the Debian Kernel Images, and the Proxmox Kernels, we are down from 95% to about 70% on our root disks.

```console
root@pve2:~# bash /mnt/pve/cephfs/bin/cssh "hostname && df -h /"
pve1
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  3.8G  1.6G  71% /
pve3
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  3.7G  1.7G  70% /
pve2
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.7G  3.8G  1.7G  70% /
```
