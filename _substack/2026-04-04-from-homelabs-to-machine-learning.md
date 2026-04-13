# From Homelabs to Machine Learning

**Subtitle:** Building Infrastructure That Teaches You Everything

**Author:** McGarrah

**Published:** April 4, 2026

**URL:** https://mcgarrah.substack.com/p/from-homelabs-to-machine-learning

**Tags:** Homelab, Infrastructure, Machine Learning, Open Source, Software Engineering

---

I've spent the last few years building and breaking Proxmox VE clusters with Ceph distributed storage in my homelab. What started as a way to learn virtualization turned into a deep education in distributed systems, storage engineering, networking, and automation — the exact same foundations that underpin modern machine learning infrastructure.

If you've ever wondered how ML engineers think about compute clusters, storage pipelines, and fault tolerance, the answer is: they learned it the same way I did. By building things, breaking them, and writing down what happened.

*Thanks for reading! Subscribe for free to receive new posts and support my work.*

This is a guide to everything I've documented along the way. Every article is based on direct, hands-on experience — real problems, real fixes, and real hardware.

## Why Infrastructure Matters for ML

Machine learning doesn't happen in a vacuum. Behind every trained model is:

- **Compute clusters** that need orchestration, scheduling, and resource management
- **Distributed storage** that must handle massive datasets with redundancy and performance
- **Networking** that can't be the bottleneck when moving terabytes between nodes
- **Monitoring** that catches failures before they corrupt a 72-hour training run

My homelab runs the same fundamental technologies — Proxmox for orchestration, Ceph for distributed storage, multiple 1Gbps networking (and hopefully 10Gbps in the future), and SMART monitoring for hardware health. The scale is different. The principles are identical.

## Getting Started with Proxmox

Proxmox VE is an open-source virtualization platform built on KVM and LXC. It's what VMware ESXi wants to be when it grows up and stops charging enterprise licensing fees.

- [ProxMox 8.2 for the Homelabs](https://mcgarrah.org/proxmox-8-homelab/) — Initial cluster setup and architecture decisions. How I designed a multi-node cluster from scratch.
- [Proxmox VE 8.1 to 8.2 Upgrade Issues](https://mcgarrah.org/proxmox-upgrade-issues/) — Upgrade pitfalls and how to avoid them. Spoiler: read the release notes before you hit enter.
- [Proxmox 8 Lessons Learned](https://mcgarrah.org/proxmox-8-lessons-learned/) — Hard-won tips from running Proxmox in production. The stuff the documentation doesn't tell you.

## Ceph Distributed Storage

Ceph is where the real distributed systems education happens. It's the same storage technology used by CERN, Bloomberg, and major cloud providers. Running it in a homelab teaches you replication, consistency, failure domains, and performance tuning in ways no textbook can.

- [Proxmox Ceph Settings for the Homelab](https://mcgarrah.org/proxmox-ceph-homelab-settings/) — Tuning Ceph for low-power hardware. Enterprise defaults will destroy consumer drives.
- [Ceph Cluster Rebalance Issue](https://mcgarrah.org/ceph-rebalance/) — Diagnosing and fixing rebalance problems. When your cluster decides to shuffle terabytes at 3 AM.
- [Managing Ceph Nearfull Warnings](https://mcgarrah.org/proxmox-ceph-nearfull/) — Handling capacity warnings before they become outages. Ceph gets very unhappy when disks fill up.
- [Optimizing Ceph Performance in Proxmox](https://mcgarrah.org/proxmox-ceph-performance/) — Performance tuning and benchmarking. Getting the most IOPS out of modest hardware.
- [Adding Ceph Dashboard to Your Proxmox Cluster](https://mcgarrah.org/proxmox-add-ceph-dashboard/) — Web-based monitoring setup. Because SSH'ing into nodes to check health gets old fast.
- [Ceph Cluster Complete Removal on Proxmox](https://mcgarrah.org/proxmox-remove-ceph-completely/) — Clean removal when you need to start over. Sometimes the best fix is a fresh start.
- [Homelab Storage Economics: Ceph vs Single Drive](https://mcgarrah.org/homelab-storage-economics/) — Cost analysis of distributed storage. Is the redundancy worth the hardware cost?

## The $15 Cluster: Dell Wyse 3040s

My test cluster runs on Dell Wyse 3040 thin clients — $15 each on eBay. They have 2GB RAM, 8GB eMMC, and an Atom x5 processor. They're terrible. I love them. They force you to understand resource constraints the way real-world ML deployments do.

- [ProxMox 8.2.2 Cluster on Dell Wyse 3040s](https://mcgarrah.org/proxmox-8-dell-wyse-3040/) — Building a cluster from thin clients. Yes, it actually works.
- [ProxMox 8.2.4 Upgrade on Dell Wyse 3040s](https://mcgarrah.org/proxmox-8-dell-wyse-3040-upgrade/) — Upgrading the low-resource cluster without bricking everything.
- [Dell Wyse 3040 CMOS Battery Replacement](https://mcgarrah.org/dell-wyse-3040-cmos-battery/) — Hardware maintenance on devices never designed to be maintained.
- [Debian 12 on Dell Wyse 3040s](https://mcgarrah.org/dell-wyse-3040-debian12/) — Base OS installation for when you want Linux without the Proxmox overhead.
- [Tailscale on Dell Wyse 3040](https://mcgarrah.org/dell-wyse-3040-tailscale/) — Remote access setup. Managing a cluster from anywhere.
- [Dell Wyse 3040 eMMC Storage Health Monitoring](https://mcgarrah.org/dell-wyse-3040-emmc-monitoring/) — Keeping tabs on embedded storage that was never meant to run 24/7.
- [Debian 12 SystemD Nightly Reboots on Dell Wyse 3040s](https://mcgarrah.org/dell-wyse-3040-reboot/) — Stability workarounds for hardware running beyond its design parameters.

## Monitoring & Maintenance

The unglamorous work that keeps everything running. In ML infrastructure, monitoring is the difference between catching a failed GPU node in minutes versus discovering a corrupted training run after three days.

- [Monitoring ZFS Boot Mirror Health in Proxmox 8](https://mcgarrah.org/proxmox-zfs-boot-mirror-smart-analysis/) — SMART monitoring for boot drives. Catching failures before they cascade.
- [Consolidating Proxmox Notes: A Python Export Script](https://mcgarrah.org/proxmox-consolidated-notes/) — Automating cluster documentation. Because tribal knowledge doesn't survive 3 AM outages.
- [Optimizing Jellyfin on Proxmox: Moving Metadata to CephFS](https://mcgarrah.org/optimizing-jellyfin-on-proxmox-moving-metadata-to-cephfs-and-shrinking-lxc-footprints/) — LXC container optimization with Ceph. Separating compute from storage — the same pattern used in ML pipelines.

## Supporting Infrastructure

The foundation everything else sits on.

- [Buying a 10Gbps Network on a Homelab Budget](https://mcgarrah.org/homelab-sfp-plus-networking/) — SFP+ networking on the cheap. Because Ceph replication over gigabit ethernet is painful.
- [Linux Disk I/O Performance in the Homelab](https://mcgarrah.org/linux-disk-io-quick-tests/) — Quick benchmarking methods. Know your baseline before you start tuning.
- [Enabling SMART Monitoring on Seagate USB Drives](https://mcgarrah.org/usb-drive-smart/) — Getting health data from USB storage. USB-to-SATA bridges hide everything useful.

## The Connection to Machine Learning

If you're reading this and thinking "this is just infrastructure, what does it have to do with ML?" — everything.

My M.S. in Computer Science from Georgia Tech focused on Interactive Intelligence (the academic name for AI/ML). My research covered perception systems, NLP, and computer vision. My professional career at Blue Cross NC involved building the cloud platform that ran production deep learning models for healthcare predictions.

The infrastructure skills I document here are the same ones I use professionally:

- **Ceph** teaches you distributed storage — the same concepts behind HDFS, S3, and the data lakes that feed ML pipelines
- **Proxmox/KVM** teaches you compute orchestration — the same principles behind Kubernetes, which runs most production ML workloads
- **Networking** teaches you throughput and latency — the bottlenecks that determine whether distributed training takes hours or days
- **Monitoring** teaches you observability — the practice that catches model drift, data quality issues, and infrastructure failures

The homelab is where I learn by breaking things. The enterprise is where I apply those lessons at scale.

## About Me

I'm Michael McGarrah — a cloud architect and data scientist with 25+ years in enterprise infrastructure. I hold an M.S. in Computer Science (AI/ML) from Georgia Tech, a B.S. in Computer Science from NC State, and I'm currently pursuing an Executive MBA at UNC Wilmington.

You can find more of my writing at [mcgarrah.org](https://mcgarrah.org), my detailed resume at [mcgarrah.org/resume](https://mcgarrah.org/resume), and my profiles on [LinkedIn](https://www.linkedin.com/in/michaelmcgarrah/), [GitHub](https://github.com/mcgarrah), and [Google Scholar](https://scholar.google.com/citations?user=Lt7T2SwAAAAJ).
