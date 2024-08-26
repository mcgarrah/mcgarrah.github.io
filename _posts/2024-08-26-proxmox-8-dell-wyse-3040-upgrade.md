---
title:  "ProxMox 8.2.4 Upgrade on Dell Wyse 3040s"
layout: post
published: true
---

My earlier post for [ProxMox 8.2.2 Cluster on Dell Wyse 3040s](/proxmox-8-dell-wyse-3040/) mentioned the tight constraints of the cluster both with RAM and DISK space. There are some extra steps involved in keeping a very lean Proxmox 8 cluster running on these extremely resource limited boxes. I am running Proxmox 8.2 and Ceph Reef on them which leaves them slightly under resourced as a default. So when the Ceph would not start up the Ceph Monitors after my upgrade from Proxmox 8.2.2 to 8.2.4, I had to dig a bit to find the problem.

[![Proxmox SFF Cluster](/assets/images/proxmox-8-sff-testbed-upgrade.png "Proxmox SFF Cluster"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/proxmox-8-sff-testbed-upgrade.png){:target="_blank"}

Ceph Monitor will not start up if there is not at least 5% free disk space on the root partition. My root volumes were sitting right at 95% used. So our story begins...

<!-- excerpt-end -->

### Cluster SSH for Proxmox (cssh)

To help with running commands across the cluster, I have a quick script for running `ssh` command across the cluster nodes. It requires the `jq` command to be installed on the node running the script. The commented out section is for those with DNS entries for their nodes. I use IP addresses for my testbed nodes for now.

```bash
#!/bin/bash

#for node in $(pvesh get /nodes --output-format json | jq -r '.[].node'); do
#  ssh root@$node "$*"
#done

for node in $(pvesh get /cluster/status --output-format json | jq -r '.[].ip' | grep -v null); do
  ssh root@$node "$*"
done
```

For ease of use, I have added the shell script to the cephfs share in `/mnt/pve/cephfs/bin/cssh` and execute it as needed.

```console
root@pve3:~# bash /mnt/pve/cephfs/bin/cssh "hostname -i"
192.168.89.11
192.168.89.12
192.168.89.13
```

**Note**: The first time you execute the `cssh`, you will be prompted to accept the `ssh` keys for each node.

I'm installing the `jq` command across the cluster so I can run `cssh` from any node in the cluster.

```console
root@pve1:~# bash /mnt/pve/cephfs/bin/cssh "hostname && apt-get install jq -y"
```

### Ceph-Mon will not start

Ceph-Mon would not start on two nodes after upgrading the cluster from Proxmox 8.2.2 to 8.2.4. I gathered this from the Proxmox WebUI Cluster Tasks at the bottom by double clicking the red error after pressing "Start" for the Ceph-Mon service.

```text
Job for ceph-mon@pve3.service failed because the control process exited with error code.
See "systemctl status ceph-mon@pve3.service" and "journalctl -xeu ceph-mon@pve3.service" for details.
TASK ERROR: command '/bin/systemctl start ceph-mon@pve3' failed: exit code 1
```

Digging into the `journalctl` logs, I find and entry about disk space being short of storage space.

```text
Aug 26 13:59:03 pve3 ceph-mon[2570]: 2024-08-26T13:59:03.058-0400 7c064bfd6d40 -1 error: monitor data filesystem reached concerning levels of available storage space (available: 5% 339 MiB)
Aug 26 13:59:03 pve3 ceph-mon[2570]: you may adjust 'mon data avail crit' to a lower value to make this go away (default: 5%)
Aug 26 13:59:03 pve3 systemd[1]: ceph-mon@pve3.service: Main process exited, code=exited, status=28/n/a
```

Checking the file systems on each node finds, I have 95% or higher usage on each. So we now have a root cause why Ceph-Mon won't start. It won't start because a disk 95% full or less than 5% free stops the Ceph-Mon service from starting.

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

#### Debian APT Cache

Here I'm going after a quick win to get us some space back fast. The first place I can think of is to clean out the Debian Apt Cache after upgrades. The gives us a good 10% reduction in disk space used.

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

#### Surprise of `atop` daily logs

Next some digging around with `du -msh *` in various locations of the file system find a tool I forgot about. `atop` stores logs daily in `/var/log/atop/atop_YYYYMMDD` which is consuming a good bit of space for these disk limited systems. You can `man atop` and search for `RAW DATA STORAGE` section for details.

The default for `atop` is to create log entries and retain them for 28 days. This amounts for a couple hundred MBs or the 227M shows below.

```console
root@pve1:/etc/default# du -msh /var/log/atop
277M    /var/log/atop
root@pve1:/etc/default# cat atop 
# /etc/default/atop
# see man atoprc for more possibilities to configure atop execution

LOGOPTS=""
LOGINTERVAL=600
LOGGENERATIONS=28
LOGPATH=/var/log/atop
```

We are removing the `atop` package from all the nodes in the cluster rather than configure it for less disk space usage. We could revisit this later to reduce the days of retention.

```console
root@pve1:~# bash /mnt/pve/cephfs/bin/cssh "hostname && apt-get remove atop -y"
```

We are also removing all the `atop` logs from each node in the cluster with an `rm -rf` command.

**Note**: Be very careful with `rm -rf` commands scripts but this was appropriate to remove the logs for `atop`.

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

#### Look for large Debian Packages

Here is a quick way to find the size of debian packages and their on size on disk. I've been using this for awhile when checking Debian based systems when recovering disk space.

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

##### PVE kernel cleanups

[Proxmox VE Kernel Clean](https://tteck.github.io/Proxmox/#proxmox-ve-kernel-clean) scripts cleans unused kernel images from your system. It is beneficial for reducing the length of the GRUB menu and freeing up disk space. By removing old, unused kernels, the system is able to conserve disk space and streamline the boot process.

This is an easy one to recover some disk space after an upgrade of the PVE Cluster. You can run this from the website or my one-liner below that can be run from a shell.

---

One liner for quick execution that works for me. For a safer experience, use the above script with more error checking and safety features.

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

##### Debian kernel image cleanup

I missed cleaning up all the Debian Kernel Image packages and meta-package in my [earlier post](/proxmox-8-dell-wyse-3040/). I'll have to update it.

```console
apt purge -y $(dpkg --list | grep -Ei 'linux-image|linux-headers' | awk '{print $2}' | grep -v "$(uname -r)" | sort -V)
```

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

<!--
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
-->

### Final Disk Space

After clean up `atop` and its logs, the **Debian Kernel Images**, and the extra **Proxmox Kernels**, we are down from about 95% usage on each node to about 70% on our root disk volumes.

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

## Post mortem

The Dell Wyse 3040s are really disk space constrained and I have to keep an eye on usage closely. This is just one of the challenges with a super small-form-factor homelab cluster.

[![Proxmox SFF Cluster](/assets/images/proxmox-8-sff-testbed-upgrade.png "Proxmox SFF Cluster"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/proxmox-8-sff-testbed-upgrade.png){:target="_blank"}

I just look at this picture and remember that the extra work is worth it. That is a full Proxmox 8 Cluster with Ceph Reef with a separate SAN network and a SDN capable configuration which is sitting on a table in my network closet sipping (not gulping) electricity.
