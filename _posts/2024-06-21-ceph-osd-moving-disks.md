---
title:  "Moving Ceph OSD (disks) between Ceph nodes"
layout: post
published: false
---

My Proxmox Ceph Cluster setup and configuration is a lessons learned as I go along. I think I made a mistake in adding the third batch of three disks on the existing three nodes hosting my Ceph Cluster. From reading and thinking this through, I believe I should have spread out the OSDs across more than the minimum three ceph nodes to a fourth ceph node. Three ceph nodes is the minimum and you should have more to protect against failures in a 3 copies and 2 active (3/2) ceph pool.



You can see in post [Ceph Cluster rebalance issue](/ceph-rebalance/) my OSD maps before I added the three new OSDs.

[![Older Ceph OSD Status](/assets/images/ProxMox-Ceph-OSD-usage.png){:width="50%" height="50%"}](/assets/images/ProxMox-Ceph-OSD-usage.png){:target="_blank"}

Current state is four OSDs on three proxmox ceph nodes. I want to transition to three OSDs on four proxmox ceph nodes. So I'm trying to figure out if I can un-screw this up without having to do the ceph normal method of remove the OSDs, wipe them, and re-add and re-balance the contents on the cluster. That will take a lot of background processing to complete and stress the system the whole time. I'd rather take a short-cut if possible and reuse the data on those disk.

[![Newer Ceph OSD Status](/assets/images/proxmox-ceph-osd-usage-four-disks.png){:width="50%" height="50%"}](/assets/images/proxmox-ceph-osd-usage-four-disks.png){:target="_blank"}

My hope is that I can just take those three new OSDs offline (osd.9, osd.10, osd.11), power-down the ceph node hosting the drive, unplug the disk from those ceph nodes, power the ceph nodes back up without the disk, and then plug those disks into the new fourth proxmox ceph node I just added (called quell) that can handle those recently added and fully loaded OSDs. From briefly reading on Ceph OSDs, this sounds like it might actually work.

That said, I'm not sure how to remove the OSD from the original location cleanly. Or if the ceph cluster keeps up with the OSD IDs between nodes... this is all unexplored space for me and the documentation so far makes this sound possible but I'm obviously missing steps in that list of steps.

And while write this down I found this reddit article "[Moving OSDs from multiple hosts to new host](https://www.reddit.com/r/ceph/comments/1atfaug/moving_osds_from_multiple_hosts_to_new_host/)" that has a lot of what I'm looking to do with some extra steps I forgot like disabling ceph ```balancing``` and ```recovery```. I should also probably disable ```scrubbing``` and ```deep-scrubbing``` too.

[![Proxmox Ceph Global OSD Flags](/assets/images/proxmox-ceph-osd-flags.png){:width="50%" height="50%"}](/assets/images/proxmox-ceph-osd-flags.png){:target="_blank"}

Above is a complete list of the Global OSD Flags from the Proxmox WebUI. And from that I can see the ```nobackfill``` is likely another one to enable to keep activity to a minimum while it sorts out the migration of the OSD.
