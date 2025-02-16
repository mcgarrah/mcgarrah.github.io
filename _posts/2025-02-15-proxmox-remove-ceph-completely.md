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
rm -rf /etc/ceph
rm -rf /etc/pve/ceph.conf
rm -rf /etc/pve/ceph
rm -rf /etc/pve/priv/ceph
rm -rf /var/lib/ceph
rm -rf /var/log/ceph
```

## Last thoughts

This was what I needed to get my test cluster back where I needed it after really screwing up my `cephfs` and `cephrbd` by tearing out external storage used for OSDs and remapping my `/usr` to separate external storage. This test system is highly constrained on RAM and Storage so I have had to play games to keep it working and being useful. You can see some of those challenges in [ProxMox 8.2.2 Cluster on Dell Wyse 3040s](/proxmox-8-dell-wyse-3040/) and again in [ProxMox 8.2.4 Upgrade on Dell Wyse 3040s](/proxmox-8-dell-wyse-3040-upgrade/). I am sharing this with the best intentions and hope you find it useful.

[![Proxmox SFF Cluster](/assets/images/proxmox-8-sff-testbed-upgrade.png "Proxmox SFF Cluster"){:width="25%" height="25%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/proxmox-8-sff-testbed-upgrade.png){:target="_blank"}

This cheap low-end cluster just keeps delivering value as I experiment.
