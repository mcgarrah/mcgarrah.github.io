---
title:  "ProxMox 8.2 SDN options for the Homelabs"
layout: post
published: false
---

I just added a fourth set of three 5tb hard drives to my Ceph cluster on Proxmox 8.2.2.  So I'm up to about 20tb of highly available storage with no means of serving it out. So the plan is to build my multi-media services platform on a Proxmox Clusters with CephFS for the storage using LXC containers as a first options over VMs.

NovaSpirit Youtube channel had a great series on doing this but not in a HA Cluster.
TODO: Add Don's list of youtube videos here... and and outline of why I think they are really interesting for my use-case.

Outline the LXC ARRs and OpenWRT network...

Issue is that I want to use a cluster for HA failover and not just a single server like NovaSpirit Don's configuration.

https://pve.proxmox.com/pve-docs/chapter-pvesdn.html#pvesdn_setup_example_vxlan
https://pve.proxmox.com/pve-docs/chapter-pvesdn.html#pvesdn_setup_example_evpn

So I want the OpenWRT LXC but want to use the SDN shared networking between the cluster nodes for HA.

https://forum.proxmox.com/threads/inter-node-sdn-networking-using-evpn-vxlan.146266/ might have the solution in it... I think he was doing what I'm trying to do with OpenWRT or close enough.

Ceph 3/2 default configuration with a set of three (3) OSDs per three (3) nodes. You can run a diagonal and see the layout of the data across the three nodes. There are three copies of the data written and the Ceph cluster continues to serve data as long as two copies exist so you can have a single node down.

```
5 5 5
5 5 5
5 5 5
```

I just upgraded to an extra OSD per node so I have four (4) OSDs on each of the three (3) nodes. This was a choice where I could have added another nodes or another OSD per node. I'm not sure I made an informed decision there.