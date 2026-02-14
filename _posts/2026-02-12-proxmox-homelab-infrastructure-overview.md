---
title: "AlteredCarbon: My Proxmox Homelab Infrastructure Overview"
layout: post
categories: [technical, homelab]
tags: [proxmox, ceph, homelab, infrastructure, networking, kubernetes, virtualization]
excerpt: "A comprehensive overview of my six-node Proxmox cluster with Ceph storage, multi-site networking, and the foundation for Kubernetes deployment."
published: false
---

After two years of building, breaking, and rebuilding my homelab, it's time to document the current state of the "AlteredCarbon" cluster. This post serves as both a reference for myself and a foundation for the Kubernetes deployment I'm planning.

<!-- excerpt-end -->

## Cluster Overview

The AlteredCarbon cluster (named after the Netflix series) consists of six Dell OptiPlex 990 systems running Proxmox VE 8.4.16 with Ceph Reef 18.2.7 for distributed storage.

| Node | IP Address | CPU | RAM | Role |
|------|------------|-----|-----|------|
| harlan | 192.168.86.11 | 8 cores | 31 GB | Ceph Mon/OSD, P620 GPU |
| kovacs | 192.168.86.12 | 8 cores | 31 GB | Ceph Mon/OSD, P620 GPU |
| poe | 192.168.86.13 | 8 cores | 31 GB | Ceph Mon/OSD, P620 GPU |
| edgar | 192.168.86.14 | 8 cores | 31 GB | Ceph OSD, K600 GPU |
| tanaka | 192.168.86.15 | 4 cores | 16 GB | Ceph Mon (no OSD), K600 GPU |
| quell | 192.168.86.16 | 8 cores | 31 GB | Ceph Mon/OSD, P620 GPU |

Total resources: 44 CPU cores, 173 GB RAM, and 69 TiB raw Ceph storage.

## Ceph Storage Architecture

The Ceph cluster runs 15 OSDs across 5 hosts (tanaka is monitor-only due to limited SATA ports). Each OSD host has 3 drives providing approximately 13-14 TiB per host.

**Storage Pools:**

| Pool | Type | Used | Available | Purpose |
|------|------|------|-----------|---------|
| cephfs_data | CephFS | 10 TiB | 6.5 TiB | Media library, shared files |
| cephrbd | RBD | 74 GB | 6.5 TiB | VM disks, LXC rootfs |

With 3x replication, the cluster can survive losing 2 entire OSD hosts while maintaining data availability. The cephrbd pool is nearly empty and ready for Kubernetes persistent volumes.

### Network Separation

Ceph uses dual-network architecture for optimal performance:

- **Public Network (192.168.86.0/23)**: Client traffic, monitor communication
- **Cluster Network (10.10.10.0/23)**: OSD-to-OSD replication, heartbeats

This separation prevents heavy replication traffic from competing with client I/O—critical when running 3x replication across 15 OSDs.

## Multi-Site Network Architecture

The homelab spans four physical locations, each with its own /23 network:

| Location | Network | Gateway | Status |
|----------|---------|---------|--------|
| Raleigh | 192.168.86.0/23 | 192.168.86.1 | Primary (Proxmox cluster) |
| Beach (Emerald Isle) | 192.168.88.0/23 | 192.168.88.1 | Secondary |
| Wilson | 192.168.84.0/23 | 192.168.84.1 | Future |
| Katie | 192.168.82.0/23 | 192.168.82.1 | Future |

Each site has a Dell Wyse 3040 running Tailscale for VPN connectivity and Technitium DNS for local resolution.

### IP Allocation Strategy

The /23 CIDR provides 512 IPs per site. For Raleigh:

| Range | Purpose |
|-------|---------|
| 192.168.86.1 | Gateway (Google Wifi) |
| 192.168.86.2-3 | Infrastructure (Tailscale, DNS) |
| 192.168.86.11-19 | Proxmox nodes |
| 192.168.86.20-100 | DHCP pool |
| 192.168.86.101-200 | Kubernetes VMs |
| 192.168.87.100-200 | MetalLB LoadBalancer pool |

This allocation keeps Kubernetes resources cleanly separated from infrastructure while providing 101 IPs for LoadBalancer services.

## GPU Hardware

The cluster includes six NVIDIA Quadro GPUs for hardware transcoding:

- **4x Quadro P620** (GP107GL): harlan, kovacs, poe, quell
- **2x Quadro K600** (GK107GL): edgar, tanaka

Proxmox HA groups (P620, K600) enable automatic VM placement on nodes with the required GPU hardware. This is essential for Jellyfin transcoding and future ML workloads.

## Current Services

### Running LXC Containers

- **Jellyfin** (192.168.86.50): Media server with GPU passthrough, metadata on CephFS
- **Technitium DNS** (192.168.86.3): Primary DNS with zone replication
- **Caddy** (192.168.86.4): Reverse proxy for internal services

### Infrastructure Services

- **Tailscale**: Site-to-site VPN via Dell Wyse 3040 gateways
- **Technitium DNS**: 5-node HA cluster across all sites
- **Proxmox HA**: Configured for automatic VM/LXC failover

## Storage Strategy

The storage architecture separates concerns:

- **Ceph RBD**: VM disks, LXC rootfs (fast, block-level)
- **CephFS**: Shared data, media libraries (scalable, POSIX)
- **USB Drives**: Backups via PBS (28 TiB + 20 TiB ZFS pools)

This separation allows the media library to grow independently of VM storage while maintaining performance for both workloads.

## What's Missing for Kubernetes

While the infrastructure is solid, several components need attention before deploying Kubernetes:

1. **Site-to-Site VPN**: Brume 2 routers for full subnet routing (Tailscale is device-only)
2. **DNS Decision**: Finalize Technitium vs PowerDNS for Kubernetes integration
3. **Network Upgrades**: Deploy HP ProCurve 2800 switches for LACP bonding
4. **Backup Infrastructure**: Configure PBS with USB drives for VM/LXC backups
5. **Boot Drive Health**: Replace aging HDDs with SSDs on several nodes

## Hardware Considerations

The Dell OptiPlex 990 systems are 14 years old (Intel i7-2600, Sandy Bridge). They lack modern features like AVX2 but remain capable for homelab use. Key limitations:

- No 10GbE support (1GbE only)
- Limited PCIe slots
- Aging boot drives (some with 50,000+ power-on hours)

The cost-effectiveness of this hardware makes it ideal for learning, but production Kubernetes workloads may eventually require upgrades.

## Monitoring and Observability

Current monitoring is basic:

- Proxmox built-in metrics for nodes and Ceph
- Manual health checks via CLI
- No centralized logging or alerting

Post-Kubernetes, I plan to deploy Prometheus, Grafana, and Loki for comprehensive observability.

## Lessons Learned

Two years of homelab operation have taught me:

1. **Ceph scrubbing defaults are aggressive**: Weekly deep scrubs will kill SSDs. I changed to 28-day intervals.
2. **USB storage is tricky**: UAS (USB Attached SCSI) causes random disconnects during large transfers.
3. **Separate your networks**: Ceph replication on the same network as client traffic is painful.
4. **Document everything**: Future-you will thank present-you.
5. **Start simple**: LXC containers are easier than Kubernetes for single services.

## What's Next

The immediate priorities are:

1. Deploy site-to-site VPN (Brume 2 routers)
2. Finalize DNS infrastructure
3. Configure PBS backups
4. Complete Jellyfin and ARR suite deployment
5. Then: Kubernetes

The [k8s-proxmox](https://github.com/mcgarrah/k8s-proxmox) repository contains the detailed implementation guides for the Kubernetes deployment, but the foundation documented here must be solid first.

## Conclusion

The AlteredCarbon cluster represents a significant investment in learning distributed systems, storage, and virtualization. While the hardware is aging, the architecture is sound and ready for the next phase: Kubernetes.

The key insight from this journey is that infrastructure fundamentals matter more than the latest technology. A well-designed network, reliable storage, and proper backups are prerequisites for any successful deployment—whether it's a simple media server or a full Kubernetes cluster.

## References

- [Proxmox VE Documentation](https://pve.proxmox.com/wiki/Main_Page)
- [Ceph Documentation](https://docs.ceph.com/)
- [k8s-proxmox Repository](https://github.com/mcgarrah/k8s-proxmox)
- [Previous Proxmox Posts](/tags/#proxmox)
