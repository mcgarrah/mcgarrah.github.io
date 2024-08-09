---
title:  "Proxmox Ceph Performance for the Homelab"
layout: post
published: false
---

### Performance

TODO: SPIN this off to another POST.

#### Limits of NIC and USB

Why am I getting 10-16 MiB/s transfer rates on my USB 3.0 USB Hard Drives? I have a 1Gbps switch for the network transfer portion.

USB 3.0 speed and media... https://qr.ae/p2NAQe https://qr.ae/p2NAdw

[![Ceph Recovery and Rebalance](/assets/images/ceph-recovery-rebalance-homelab.png){:width="30%" height="30%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/ceph-recovery-rebalance-homelab.png){:target="_blank"}

#### mclock iops

```console
root@harlan:~# ceph config dump
WHO    MASK  LEVEL     OPTION                                             VALUE      RO
mon          advanced  auth_allow_insecure_global_id_reclaim              false
mgr          advanced  mgr/dashboard/PWD_POLICY_CHECK_COMPLEXITY_ENABLED  false      *
mgr          advanced  mgr/dashboard/PWD_POLICY_ENABLED                   false      *
mgr          advanced  mgr/dashboard/ssl                                  true       *
osd.0        basic     osd_mclock_max_capacity_iops_hdd                   86.136079
osd.1        basic     osd_mclock_max_capacity_iops_hdd                   87.204995
osd.4        basic     osd_mclock_max_capacity_iops_hdd                   89.152214
```

```console
root@harlan:~# ceph tell osd.0 bench 12288000 4096 4194304 100
{
    "bytes_written": 12288000,
    "blocksize": 4096,
    "elapsed_sec": 2.868101647,
    "bytes_per_sec": 4284366.9828972416,
    "iops": 1045.9880329338969
}
```

I may have a bottle neck in performance on the first node in hte ceph cluster.

This might be from a couple of separate events or an overlap of them.

First event was when I accidentally bumped the SAN connection for one of the nodes and it was offline from the SAN for several days.

The second could have been when I overloaded the cluster with content and had the massive rebalancing events chewing the cluster up for over a week.

Lastly, I might have setup a subpar interface for the hard drives that was exceptionally slow and then fixed it.


#### [IOSTAT](https://docs.ceph.com/en/latest/mgr/iostat/)

No output during a rebalance event when I'm not hitting the ceph cluster for content or loading content into it.

``` shell
root@harlan:~# ceph iostat -p 5
+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+
|                    Read |                   Write |                   Total |               Read IOPS |              Write IOPS |              Total IOPS |
+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
^CInterrupted
```
