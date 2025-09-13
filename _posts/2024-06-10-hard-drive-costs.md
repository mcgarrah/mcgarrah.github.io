---
title:  "Hard Drives for the Homelabs"
layout: post
categories: [technical, homelab, hardware]
tags: [storage, hard-drives, homelab, hardware, ceph, cost-analysis, technical]
published: true
---

We live in a world with a penny ($0.01 USD) per GB of storage. I just found this bare drive [MDD (MD20TS25672NAS) 20TB 7200 RPM 256MB Cache SATA 6.0Gb/s 3.5" Internal Hard Drive (for NAS, Network Storage) - 5 Years Warranty (Renewed)](https://amzn.to/45fYeRH) for $199.99 USD. I also found [Avolusion PRO-X USB 3.0 External Hard Drive (Black) - 2 Year Warranty (20TB)](https://amzn.to/3VBhwxC) for ~~$229.99~~ $219.99 USD with the USB C enclosure.

<!-- excerpt-end -->

I just updated my primary Ceph Cluster with another batch of three (3) 5Tb drives to a total of twelve (12) drives as OSDs serving out storage. That has me at 60Tb of raw storage that I have configured to be a Ceph 3/2 configuration (3 replicas with 2 minimum) for a highly available 20Tb of storage accessible. I have three copies of each block of data and require a minimum of two copies to be active for usage. So I can loose one full compute node (that hosts 3+ drives) or up to three drives without a loss of service.

With the addition of that last set of drives, I jumped to needing 20Tb of external storage to meet my one (1) offsite copy of data for my modified [3-2-1 backup strategy](https://www.backblaze.com/blog/the-3-2-1-backup-strategy/). I remembered that jumping from sub-14Tb to above 20Tb was a big jump in price. Those big drives were a lot more expensive earlier just this year and these renewed ones seem like too good a deal especially with a 5-year warranty. I'm going to have to grab one and try it out.

What a world?

Updated on June 19th 2024 - The price dropped $10 on the USB-C enclosure drive and I bought it. So I'll be figuring out how to replica a CephFS to ZFS enabled 20Tb drive in the near future as an active offsite read-only backup.
