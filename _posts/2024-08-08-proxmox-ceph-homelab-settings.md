---
title:  "Proxmox Ceph settings for the Homelab"
layout: post
categories: [technical, homelab]
tags: [proxmox, ceph, homelab, storage, optimization, performance]
published: true
---

What is Ceph? Ceph is an open source software-defined storage system designed and built to address block, file and object storage needs for a modern homelab. [Proxmox Virtual Environment (PVE)](https://pve.proxmox.com/) makes creating and managing a [Hyper-Converged Ceph Cluster](https://pve.proxmox.com/pve-docs/chapter-pveceph.html) relatively easy for initially configuring and setting it up.

Why would you want a Hyper-Converged storage system like Ceph? So your PVE that runs Virtual Machines and Linux Containers has a highly available shared storage service making them portable between nodes in your cluster of machines and thus highly-available services.

There is a significant learning curve involved in understanding how the pieces of Ceph fit together which the Proxmox documentation does a decent job of helping you along. Proxmox VE sets some decent defaults for the Ceph Cluster that are good for an enterprise environment. What they do not do is help you set default to reduce wear and load on your Homelab system. This is where I am going to try out a few things to reduce load and wear on my Homelab equipment while maintaining a relatively high-availability environment.

My post on [Ceph Cluster rebalance issue](/ceph-rebalance/) from earlier was from figuring out issues in an unbalanced cluster from a strange data loaded into a cluster. This post is focused on a regular running cluster that needs some optimization for the homelab.

<!-- excerpt-end -->

### Information

You can just jump directly to the [Change Settings](#change-settings) and skip explanations and details.

If you have used any major cloud provider, they offer a storage solution that included block storage devices. AWS S3 (**S**imple **S**torage **S**ervice) is an example of this type of offering. These devices can be considered as raw hard-drives you can attach to a virtual machine and then build file systems on those to store files and other operating system artifacts.

As mentioned, Ceph can create block, file and object storage. Block storage is like a portable hard-drive. File storage is just like your file system on you operating system that just happens to be shared between virtual machines. Lastly, object storage is used for storing large volumes of unstructured data using key-values and optional meta-data. These combined are the foundation of the modern cloud infrastructure.

Ceph as part of the base functionality, provides for managing both the redundancy and consistency of the data. Those are important if you want your data to remain available. The redundancy is handle by making copies of the content and storing it in multiple locations in your Ceph Cluster. Consistency of the data that is stored is where I am hitting some issues that I want to address.

Ceph clusters automatically spread out the data and periodically, a "scrub" or "deep scrub" is performed on the data to confirm the data is the same in each place it has been copied for redundancy. That allows for maintaining consistency of the data in multiple places.

"Scrubbing" means that Ceph checks the consistency of your data using a background process. The action is to checks that the objects and relevant metadata exists. This usually takes place on a daily basis.

"Deep Scrubbing" is when Ceph compares the contents of the objects and their replicas for consistency. It usually on a weekly basis reads the data and uses checksums to ensure data integrity. This operation requires reading data for a bit-for-bit comparison and not just the lighter weight objects and metadata comparison.

So **Scrubbing** (daily) checks the object size and attributes. **Deep scrubbing** (weekly) reads the data and uses checksums to ensure data integrity.

To reduce the impact on our cluster, we can try both scheduling **scrubbing** and **deep scrubbing** for increased intervals such as 28 days rather than 7 for **deep scrubbing** and from 1 day to 14 days for **scrubbing** operations.

I am ignoring ~~randomizing the execution times~~, setting begin and end hours, and sleep periods. I just want this to be spread out over a longer period of time and reduce wear on the *spinning rust* hard drives.

**[`osd_scrub_min_interval`](https://docs.ceph.com/en/reef/rados/configuration/osd-config-ref/#confval-osd_scrub_min_interval)**
: Default: 86400 (1 day)
: Description: The minimal interval in seconds for scrubbing the Ceph OSD Daemon when the Ceph Storage Cluster load is low.

**[`osd_scrub_interval_randomize_ratio`](https://docs.ceph.com/en/reef/rados/configuration/osd-config-ref/#confval-osd_scrub_interval_randomize_ratio)**
: Default: 0.5 (1/2 day)
: Description: Add a random delay to `osd_scrub_min_interval` when scheduling the next scrub job for a PG. The delay is a random value less than `osd_scrub_min_interval` \* `osd_scrub_interval_randomized_ratio`. The default setting spreads scrubs throughout the allowed time window of `[1, 1.5]` \* `osd_scrub_min_interval`.

**[`osd_deep_scrub_interval`](https://docs.ceph.com/en/reef/rados/configuration/osd-config-ref/#confval-osd_deep_scrub_interval)**
: Default: 604800 (7 days)
: Description: The interval for “deep” scrubbing (fully reading all data). The `osd_scrub_load_threshold` does not affect this setting.

**`osd_deep_scrub_randomize_ratio`**
: Default: 0.15 or 15%.
: Description: The rate at which scrubs will randomly become deep scrubs (even before osd_deep_scrub_interval has past).  Note that this option has been around for awhile but not documented in the open source release very well. You can find it in RedHat and IBM documentation.
: Code: [osd: randomize deep scrubbing](https://github.com/ceph/ceph/pull/6550/files#diff-dfb9ddca0a3ee32b266623e8fa489626R3247)

### Retrieve Current Defaults

``` shell
root@harlan:~# ceph config get osd.0 osd_scrub_min_interval
86400.000000
root@harlan:~# ceph config get osd.0 osd_scrub_interval_randomize_ratio
0.500000
root@harlan:~# ceph config get osd.0 osd_scrub_max_interval
604800.000000
```

``` shell
root@harlan:~# ceph config get osd.0 osd_deep_scrub_interval
604800.000000
root@harlan:~# ceph config get osd.0 osd_deep_scrub_randomize_ratio
0.150000
```

### Change Settings

The **scrub** min interval set to 1 day with a random ratio of 700% spreads out those operations over a 7 day period.

The **deep scrub** being set to 28 days and randomly converts 15% of the **scrub** operations over to **deep scrubs**. This spreads out the intensive operations over a longer period so they do not overwhelm the storage network and iops available.

``` bash
# Schedule the next normal scrub in between 1-7 days.
ceph config set global osd_scrub_min_interval 86400 # 1 day
ceph config set global osd_scrub_interval_randomize_ratio 7 # 700%

# No more delays, normal scrub after 14 days.
ceph config set global osd_scrub_max_interval 1209600 # 14 days

# No more waiting on a random 15% chance to deep-scrub, just deep-scrub.
ceph config set global osd_deep_scrub_interval 2419200 # 28 days 
```

You can run the above commands on any of your PVE Ceph nodes from the shell. They are global settings so they will take effect across all the OSDs at the global cluster level. No restart should be needed.

So far I have tried this across my test Proxmox Ceph Cluster and the semi-production cluster that is currently rebalancing the removal of three (3) 5Tb OSDs that I am migrating to a new forth ceph cluster node. The reduction in `deep scrubs` is helping things along.

As always, I hope this helps somebody in a similar situation. Cheers.

### Reference

[Ceph and Deep-Scrubs](https://silvenga.com/posts/ceph-and-deep-scrubs/) by Silvenga is an excellent read.

[Ceph deep scrubbing and I/O saturation](https://www.disk91.com/2020/technology/openstack/ceph-deep-scrubbing-and-i-o-saturation/) has a nice section on **deep scrubbing** and code involved.

[How to close the "deep scrub"? #10617](https://github.com/rook/rook/discussions/10617) on why deep scrub is important and how to manage it.

[Adding/Removing OSDs](https://docs.ceph.com/en/latest/rados/operations/add-or-rm-osds/)

*[PVE]: Proxmox Virtual Environment
