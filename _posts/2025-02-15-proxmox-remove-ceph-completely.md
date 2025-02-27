---
title:  "Ceph Cluster Complete Removal on Proxmox for the Homelabs"
layout: post
published: true
---

My test Proxmox Cluster is used for *testing* and along the way I broke the Ceph Cluster part of it badly while doing a lot of physical media replacements. The test cluster is the right place to try out risky stuff instead of on my main cluster that is loaded up with my data. Fixing it often teaches you something but in this case I already know the lessons and just want to fast track getting a clean ceph cluster back online.

I need it back in place to test the Proxmox 8.2 to Proxmox 8.3 upgrade of my main cluster. So this is a quick guide on how to completely clean out your Ceph Cluster installation as if it never existed on your Proxmox Cluster 8.2 or 8.3 environment.

[![proxmox ceph install dialog](/assets/images/proxmox-ceph-upgrade.png "proxmox ceph install dialog"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/proxmox-ceph-upgrade.png){:target="_blank"}

<!-- excerpt-end -->

This is a brutal set of commands to just burn down the ceph components. You are welcome to use this as it was successful for my system cleanup but I take no responsiblity for your cluster if you use them. I am *nuking* stuff indiscrimately to just get it cleared out. Beware the `rm -rf` as it is crazy bad news under the wrong circumstances. This could damage your system and I again take no responsibility for any damage done.

Everything here assumes you are logged in as the `root` user. There is no `sudo` going on here. You are playing with fire.

## Clean up steps

Here is how to turn off all the ceph services and remove the larger parts of the startups along with killing off straggle processes.

``` console
systemctl stop ceph-mon.target
systemctl stop ceph-mgr.target
systemctl stop ceph-mds.target
systemctl stop ceph-osd.target
rm -rf /etc/systemd/system/ceph*
killall -9 ceph-mon ceph-mgr ceph-mds
```

These are some extra steps to remove more of the pieces that `systemctl` throws into various other places. I did not spend the time to figure out how to do this the right way with `systemctl clean`. I am in a hurry.

``` console
ls -l /etc/systemd/system/*/ceph*
rm -rf /etc/systemd/system/*/ceph*
ls /lib/systemd/system/ceph*
rm -rf /lib/systemd/system/ceph*
```

While testing this out on different nodes, I found that ceph often has left the ceph OSD mount-point mounted even after stopping the OSD service. So this step unmounts it if it exists. This makes the `pveceph purge` work better without errors.

``` console
mount | grep ceph | cut -d' ' -f3 | xargs umount
rm -rf /var/lib/ceph/mon/  /var/lib/ceph/mgr/  /var/lib/ceph/mds/  /var/lib/ceph/osd/
pveceph purge
```

This section removes all the OS packages, then their dependencies and finally cleans out the cached packages.

``` console
apt purge -y ceph-mon ceph-osd ceph-mgr ceph-mds ceph-base ceph-mgr-modules-core
apt autoremove -y
apt clean
```

Finally this last step goes thru and completely removes all remnants of ceph from your system. These are the pieces I determined as safe to remove for my system.

``` console
rm -rf /etc/ceph/*
rm -rf /etc/pve/ceph.conf
rm -rf /etc/pve/ceph
rm -rf /etc/pve/priv/ceph
rm -rf /var/lib/ceph
rm -rf /var/log/ceph
```

*Note*: Leaving the `/etc/ceph` directory in place as it is needed later when reinstalling Ceph on the system. The error "command 'cp /etc/pve/priv/ceph.client.admin.keyring /etc/ceph/ceph.client.admin.keyring' failed: exit code 1 (500)" requires the directory to exist.

## Unlocking the OSD media

Error when trying to wipe the old Ceph OSD media came up when trying to setup the new Ceph Cluster.

``` text
Error
disk/partition '/dev/sda' has a holder (500)
```

You need the long label name for the Ceph partition. You can get this from a `lsblk` call.

``` console
root@pve3:~# lsblk
NAME                                                        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda                                                           8:0    1  28.7G  0 disk
└─sda1                                                        8:1    1  28.7G  0 part /mnt/pve/osdisk-usr
                                                                                      /usr
sdb                                                           8:16   1 117.2G  0 disk
└─ceph--553fe20d--4cc0--4e58--9f9e--914b40d3403d-osd--block--57263386--2463--4f23--9848--6e7dee2c129d
                                                            252:0    0 117.2G  0 lvm
mmcblk0                                                     179:0    0   7.3G  0 disk
├─mmcblk0p1                                                 179:1    0   512M  0 part /boot/efi
├─mmcblk0p2                                                 179:2    0   5.8G  0 part /
└─mmcblk0p3                                                 179:3    0   976M  0 part [SWAP]
mmcblk0boot0                                                179:8    0     4M  1 disk
mmcblk0boot1                                                179:16   0     4M  1 disk
```

Pass that value to the `dmsetup remove xxxx` to remove the hold.

``` console
root@pve3:~# dmsetup remove ceph--553fe20d--4cc0--4e58--9f9e--914b40d3403d-osd--block--57263386--2463--4f23--9848--6e7dee2c129d
```

Now you can use the Disks "Wipe Disk" option on that media before setting Ceph back up.

Found this in [Proxmox Forum sda has a holder...](https://forum.proxmox.com/threads/sda-has-a-holder.97771/post-513875) from 2021.

## Clear out shared storage entries

Notice the question marks next to the `cephrbd` and `cephfs` storage entries.

[![Shared Storage](/assets/images/proxmox-ceph-storage-cleanup.png "Shared Storage"){:width="25%" height="25%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/proxmox-ceph-storage-cleanup.png){:target="_blank"}

You need to remove these from the `/etc/pve/storage.cfg` file that is in the shared PVE location used by the Proxmox Cluster to share configuration settings.

``` text
dir: local
        path /var/lib/vz
        content snippets,images,rootdir,backup,vztmpl,iso
        prune-backups keep-all=1

cephfs: cephfs
        path /mnt/pve/cephfs
        content iso,vztmpl,backup
        fs-name cephfs

rbd: cephrbd
        content rootdir,images
        krbd 0
        pool cephrbd

dir: osdisk-usr
        path /mnt/pve/osdisk-usr
        content rootdir
        is_mountpoint 1
        nodes pve2,pve3,pve1
```

We need to remove the two sections with `ceph` RBD and FS in the name. You should only need to do this once and the cluster will share the file to the other nodes in the cluster.

``` text
dir: local
        path /var/lib/vz
        content snippets,images,rootdir,backup,vztmpl,iso
        prune-backups keep-all=1
```

*Note*: You will probably not have a section called `osdisk-usr` as that is my special volume used when I migrated the `/usr` from root to external USB storage.

## Orphan LXC and VM

I had a couple of orphaned VMs and LXCs that would not allow themselves to be deleted because their disk images were in shared Ceph RBD storage. So out comes the `rm` command.

I navigated to `/etc/pve/qemu-server` for the VMs on the node hosting it in the cluster. Once there, I found the VM ID which was `1001`. I just did a `rm 1001.conf` on the file to clear it out. It will be reflected in the Proxmox webui almost immediately.

If it was a LXC that was locked, I would go to `/etc/pve/lxc` and find the file by LCX ID. Then do the same `rm` on that file.

You'll have to go to each node that is hosting your VM or LXC to remove them.

Something that came up later, if you have Cluster level HA Resources configured for your VM or LXC, you will also need to remove them from it before doing this or face problems with it later.

## Last thoughts

This was what I needed to get my test cluster back where I needed it after really screwing up my `cephfs` and `cephrbd` by tearing out external storage used for OSDs and remapping my `/usr` to separate external storage. This test system is highly constrained on RAM and Storage so I have had to play games to keep it working and being useful. You can see some of those challenges in [ProxMox 8.2.2 Cluster on Dell Wyse 3040s](/proxmox-8-dell-wyse-3040/) and again in [ProxMox 8.2.4 Upgrade on Dell Wyse 3040s](/proxmox-8-dell-wyse-3040-upgrade/). I am sharing this with the best intentions and hope you find it useful.

[![Proxmox SFF Cluster](/assets/images/proxmox-8-sff-testbed-upgrade.png "Proxmox SFF Cluster"){:width="25%" height="25%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/proxmox-8-sff-testbed-upgrade.png){:target="_blank"}

This cheap low-end cluster just keeps delivering value as I experiment.
