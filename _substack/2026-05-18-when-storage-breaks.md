# When Storage Breaks: Ceph Failures, Recovery, and the Case for Hybrid Drives

**Subtitle:** Power Failures, Dead Switches, Overlapping Failures, and Why USB Drives With SSD Acceleration Actually Work

**Author:** McGarrah

**Planned:** May 18, 2026

**URL:** TBD

**Tags:** Homelab, Infrastructure, Ceph, Storage, Proxmox, Distributed Systems, Software Engineering

---

My first newsletter covered [building the homelab](https://mcgarrah.substack.com/p/from-homelabs-to-machine-learning). My second covered [the blog platform](https://mcgarrah.substack.com/p/from-markdown-to-production). This one covers what happens when the infrastructure breaks — and the engineering decisions that determine whether recovery takes minutes or days.

In April 2026, a power outage knocked my 15-OSD Ceph cluster down to 4 healthy OSDs. The recovery took days, not because Ceph is fragile, but because three separate problems were hiding behind each other: a dead SAN switch, a ceph.conf misconfiguration, and a USB drive that had silently failed weeks earlier. Untangling overlapping failures in a distributed storage system is the kind of debugging that teaches you more than any certification course.

This is also the story of a storage architecture decision that sounds insane on paper — running Ceph on USB drives — and why it actually works when you put the metadata on SSDs.

*Thanks for reading! Subscribe for free to receive new posts and support my work.*

## The Failure Cascade

A power outage shouldn't be catastrophic for a distributed storage system. Ceph is designed for exactly this — data is replicated across nodes, and the cluster self-heals when nodes come back online. In theory.

In practice, my cluster went from 15 healthy OSDs to 4, and the recovery path was anything but straightforward.

- [Ceph OSD Recovery After Power Failure: SAN Switch Was Dead the Whole Time](https://mcgarrah.org/ceph-osd-recovery-power-failure/) — The full recovery story. Eleven OSDs down, heartbeat cascades across the cluster, and the root cause hiding in plain sight: a dead SAN switch that showed NO-CARRIER on every node's cluster network interface. Plus a ceph.conf misconfiguration (host IP vs network CIDR) that had been silently wrong for months.

The debugging process is the real lesson here. When multiple things fail simultaneously, you can't trust your assumptions about which layer is broken. Network? Storage? Configuration? The answer was "all three, and they're masking each other."

## When Failures Overlap

The power failure recovery revealed a second problem that had been lurking for weeks: a dead USB drive hosting a Ceph OSD on one of the nodes. That failure had been masked by the cluster's replication — data was still accessible, just degraded. But when the power outage hit, the degraded state compounded the recovery.

Then a routine ZFS scrub alert fired on the same node, adding a third failure to debug simultaneously.

- [When ZFS and Ceph Problems Collide: Diagnosing Overlapping Failures on Proxmox](https://mcgarrah.org/zfs-ceph-overlapping-failures/) — A ZFS hostid mismatch, a dead USB Ceph drive, and a power failure recovery all happening on the same node at the same time. How to untangle overlapping storage problems when each one masks the symptoms of the others.

The key insight: **fix the most fundamental layer first**. Network before storage, storage before applications. And verify each fix independently before moving to the next layer.

## The Hybrid Storage Architecture

After the recovery, I had a decision to make about the cluster's storage architecture. The USB drives were the weak link — slow, unreliable, and the source of most OSD failures. But replacing them all with SSDs would cost more than the entire cluster was worth.

The compromise: keep the USB drives for bulk data, but move the metadata (WAL and DB) onto SSDs. This is the same tiered storage pattern used in enterprise Ceph deployments, just at homelab scale with consumer hardware.

- [Hybrid Ceph Storage: SSD WAL/DB Acceleration with USB Drive Data](https://mcgarrah.org/ceph-ssd-wal-db-usb-storage/) — The architecture and implementation guide. WAL vs DB differences, sizing calculations, ceph-volume creation, and the performance results. A Crucial MX500 SSD handling metadata for three USB OSDs transformed the cluster from sluggish to surprisingly capable.

- [Measuring the WAL vs DB Performance Gap on Ceph USB OSDs](https://mcgarrah.org/ceph-wal-vs-db-performance-test/) — I benchmarked WAL-only acceleration against full DB acceleration across the cluster. The headline result: DB is 5-15% faster on reads in matched-hardware comparisons. But the real discovery was that the USB 3.0 hardware ceiling dominates everything — the bus speed is the bottleneck, not the metadata placement. Includes ready-to-run benchmark scripts.

## The Prerequisite Nobody Writes About

All of this debugging required SSH access to six Proxmox nodes, repeatedly, under pressure. Typing passwords every time was not an option.

- [SSH Key-Based Access to a Proxmox Cluster](https://mcgarrah.org/ssh-key-access-proxmox-cluster/) — The setup that makes everything else possible. SSH key authentication, named hosts in SSH config, and the Proxmox-specific detail that shared authorized_keys across cluster nodes means you only deploy the key once.

This is the kind of foundational infrastructure that doesn't make for exciting reading until you're debugging a storage failure at midnight and every second of password typing feels like an eternity.

## The Bigger Picture: Storage Economics

The hybrid architecture decision didn't happen in a vacuum. It was informed by months of running Ceph on consumer hardware and tracking the real costs.

- [Homelab Storage Economics: Ceph vs Single Drive](https://mcgarrah.org/homelab-storage-economics/) — The cost analysis that informed the hybrid decision. Distributed storage has a replication tax — 3x replication means 69 TiB raw becomes 23 TiB usable. Is the redundancy worth it? For a homelab that runs 24/7 and stores data I care about, yes.

- [Optimizing Ceph Performance in Proxmox](https://mcgarrah.org/proxmox-ceph-performance/) — The baseline performance numbers before the hybrid architecture. You can't measure improvement without knowing where you started.

- [Managing Ceph Nearfull Warnings](https://mcgarrah.org/proxmox-ceph-nearfull/) — Capacity management. Ceph gets progressively more unhappy as disks fill up, and the warning thresholds are lower than you'd expect. This is the article I wish I'd read before my first nearfull panic.

- [Enabling SMART Monitoring on Seagate USB Drives](https://mcgarrah.org/usb-drive-smart/) — The monitoring that should have caught the dead USB drive before the power failure. USB-to-SATA bridges hide SMART data by default — you need specific passthrough flags to get health information from USB storage.

## What This Teaches About Distributed Systems

Every failure in this series maps to a distributed systems concept that shows up in production infrastructure:

- **Failure cascades** — One dead switch took out 11 of 15 OSDs because the cluster network was a single point of failure
- **Silent degradation** — The dead USB drive was invisible because replication covered for it, until a second failure exposed the weakness
- **Overlapping failures** — Three problems on one node, each masking the others. This is why observability matters more than redundancy
- **Tiered storage** — The same hot/cold data pattern used in every cloud provider's storage offering, implemented with consumer hardware
- **Hardware ceilings** — The USB 3.0 bus speed bottleneck is the same class of problem as network bandwidth limits in distributed training

The homelab is where I learn these lessons at low cost. The enterprise is where I apply them at scale.

## What's Next

The cluster is stable and the hybrid architecture is performing well. Next priorities:

- **Kubernetes on Proxmox** — Deploying K8s on top of this infrastructure with Ceph CSI for persistent storage
- **Ceph Reef to Squid upgrade** — The next major Ceph version brings performance improvements
- **LACP bonding for the SAN network** — Eliminating the single-switch failure point that started this whole story

## About Me

I'm Michael McGarrah — a cloud architect and data scientist with 25+ years in enterprise infrastructure. I hold an M.S. in Computer Science (AI/ML) from Georgia Tech, a B.S. in Computer Science from NC State, and I'm currently pursuing an Executive MBA at UNC Wilmington.

You can find more of my writing at [mcgarrah.org](https://mcgarrah.org), my detailed resume at [mcgarrah.org/resume](https://mcgarrah.org/resume), and my profiles on [LinkedIn](https://www.linkedin.com/in/michaelmcgarrah/), [GitHub](https://github.com/mcgarrah), and [Google Scholar](https://scholar.google.com/citations?user=Lt7T2SwAAAAJ).
