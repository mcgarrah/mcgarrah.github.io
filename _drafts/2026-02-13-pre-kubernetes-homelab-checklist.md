---
title: "Friday the 13th: My Pre-Kubernetes Homelab Checklist"
layout: post
categories: [technical, homelab, roadmap]
tags: [proxmox, kubernetes, homelab, infrastructure, planning, dns, vpn, backup, jellyfin]
excerpt: "A comprehensive checklist of everything I need to complete before deploying Kubernetes on my Proxmox homelab cluster. Site-to-site VPN, DNS decisions, backups, media services, and more."
published: false
---

It's Friday the 13th, and what better day to confront the terrifying complexity of deploying Kubernetes on a homelab? After documenting my [AlteredCarbon cluster infrastructure](/proxmox-homelab-infrastructure-overview/), I realized I have a substantial list of prerequisites before I can run `terraform apply` and spin up my K8s cluster.

This post is my personal checklist—a roadmap of tasks that must be completed before Kubernetes deployment. Some are quick wins, others are multi-day projects. All are necessary.

<!-- excerpt-end -->

## The Big Picture

The [k8s-proxmox](https://github.com/mcgarrah/k8s-proxmox) repository contains 20 articles covering everything from Proxmox foundation to production-ready Kubernetes with GitOps. But those articles assume certain infrastructure is already in place:

- Reliable site-to-site networking
- DNS infrastructure with split-horizon capability
- Backup systems protecting existing infrastructure
- Media services (Jellyfin, ARR suite) operational
- Network hardware capable of handling the load

Without these foundations, Kubernetes deployment would be building on sand.

## Priority 0: Site-to-Site VPN

**Status:** Hardware ready, deployment pending  
**Estimated Time:** 2-3 days  
**Blocking:** Multi-site access to Kubernetes services

### The Problem

My Google Wifi and Google Nest Wifi routers are managed products—I can't configure static routes or routing tables. This means my Dell Wyse 3040 Tailscale gateways can only provide device-to-device VPN, not full subnet routing.

When Kubernetes is deployed with MetalLB LoadBalancer IPs in the 192.168.87.100-200 range, devices at Beach (192.168.88.0/23) won't be able to reach them without proper routing.

### The Solution

Deploy GL-iNet Brume 2 (GL-MT2500A) WireGuard VPN gateways in a hybrid topology:

- **Raleigh (server site)**: Brume 2 on LAN at 192.168.87.250 — WireGuard server (10.99.0.1/24). Port forwarding: Google Fiber Router → Google Wifi → Brume 2 (UDP 51820). Masquerades VPN traffic so responses route back without static routes on Google Wifi.
- **Beach and other spoke sites (consumer sites)**: Brume 2 inline between ISP modem and Google Wifi/Nest Wifi — WireGuard client. Transit network 192.168.2.0/24. All devices transparently reach Raleigh services through the VPN tunnel.

```
# Raleigh (Brume 2 on LAN — server)
Google Fiber → Google Wifi → [Brume 2 at 192.168.87.250] ← WireGuard server
                              ↕ WireGuard tunnel (10.99.0.1 ↔ 10.99.0.3)
# Beach (Brume 2 inline — consumer)
Spectrum → [Brume 2 WAN | LAN 192.168.2.1] → Google Nest Wifi → Devices
```

**Why hybrid (not inline at both sites):** Google Wifi/Nest Wifi can't modify default gateway or add static routes. Inline at consumer sites means all devices (TVs, phones) transparently reach Raleigh services. Raleigh stays on LAN because it's the server site — only needs to accept inbound VPN.

### Tasks

- [ ] Configure Raleigh Brume 2 (192.168.87.250 on LAN)
  - [ ] Initial setup and firmware update
  - [ ] Configure LAN: 192.168.87.250/23, gateway 192.168.86.1
  - [ ] Disable DHCP server (Google Wifi handles DHCP)
  - [ ] Configure WireGuard server (10.99.0.1/24, port 51820)
  - [ ] Connect to switch or Google Wifi LAN port (no downtime)
  - [ ] Port forward: Google Wifi UDP 51820 → 192.168.87.250
  - [ ] Port forward: Google Fiber Router UDP 51820 → Google Wifi WAN IP
  - [ ] Configure masquerade for VPN traffic
  - [ ] Test with mobile WireGuard client on cellular

- [ ] Configure Beach Brume 2 (inline, transit 192.168.2.0/24)
  - [ ] Initial setup and firmware update
  - [ ] Configure WAN: DHCP from Spectrum, LAN: 192.168.2.1/24
  - [ ] Configure WireGuard client (10.99.0.3/24) to Raleigh
  - [ ] Add static route: 192.168.86.0/23 via wg0
  - [ ] Physical installation: Spectrum → Brume 2 → Google Nest Wifi (~15 min downtime)
  - [ ] Test internet and cross-site connectivity

- [ ] DNS Configuration (all sites)
  - [ ] Change Google Wifi DNS from "Automatic" to Custom: 192.168.86.3, 192.168.86.2
  - [ ] Change Google Nest Wifi DNS from "Automatic" to Custom: 192.168.88.2, 192.168.86.3
  - [ ] Verify internal hostname resolution (jellyfin.home.mcgarrah.org)

- [ ] Validation
  - [ ] Beach TV can stream from Jellyfin (192.168.86.29)
  - [ ] Beach devices can reach Raleigh Proxmox nodes
  - [ ] DNS resolution works across sites (Technitium)
  - [ ] Performance test with iperf3 (expect 300-355 Mbps)

- [ ] Future spoke sites (Wilson, Katie, Sam)
  - [ ] Same inline topology as Beach
  - [ ] WireGuard tunnel IPs: Wilson 10.99.0.5, Katie 10.99.0.7, Sam 10.99.0.9
  - [ ] Upgrade Raleigh to Brume 3 (GL-MT5000, already purchased) before adding 3rd site

### Decision: Keep Tailscale as Backup

The Dell Wyse 3040 Tailscale gateways will remain as backup VPN and continue handling DNS replication for Technitium. Redundancy is good.

## Priority 1: DNS Infrastructure Decision

**Status:** Technitium deployed, PowerDNS evaluated  
**Estimated Time:** 1-2 days  
**Blocking:** Kubernetes DNS integration, cert-manager

### The Conflict

I have two viable DNS options, and I need to pick one:

| Feature | Technitium | PowerDNS |
|---------|------------|----------|
| Web UI | Excellent | Basic (PowerDNS-Admin) |
| API | REST API | Native REST API |
| Kubernetes Integration | Manual or RFC2136 | Native RFC2136 |
| Split-Horizon | Built-in | Requires configuration |
| Resource Usage | Light (.NET) | Light (C++) |
| Current Status | Deployed, working | Not deployed |

### The Decision Factors

**For Technitium:**
- Already deployed and working
- 5-node HA cluster across all sites
- Familiar interface
- Zone replication via Tailscale working

**For PowerDNS:**
- Better RFC2136 support for external-dns
- More "enterprise" feel
- Native API for automation
- Commonly used in production environments

### Tasks

- [ ] Evaluate RFC2136 support in Technitium
- [ ] Test external-dns webhook with Technitium
- [ ] Document decision rationale
- [ ] If switching to PowerDNS:
  - [ ] Deploy PowerDNS LXC
  - [ ] Migrate zones from Technitium
  - [ ] Update all DNS references
  - [ ] Decommission Technitium

**Current Leaning:** Stick with Technitium unless RFC2136 proves problematic. The working HA setup is valuable.

## Priority 2: Backup Infrastructure

**Status:** PBS planned, USB drives available  
**Estimated Time:** 3-4 days  
**Blocking:** Safe Kubernetes deployment

### Why This Matters

Before deploying Kubernetes, I need to ensure all existing infrastructure is backed up. If something goes wrong during K8s deployment, I need to be able to recover.

### Hardware Available

- **28 TiB USB Drive** (harlan): Primary backup storage
- **20 TiB USB Drive** (kovacs): Secondary/replication target

### PBS Architecture

```
Proxmox Nodes → PBS LXC (192.168.86.5) → 28TiB USB (ZFS)
                                              ↓
                                        ZFS Replication
                                              ↓
                                        20TiB USB (kovacs)
```

### Tasks

- [ ] Prepare USB drives
  - [ ] Format 28TiB drive as ZFS pool on harlan
  - [ ] Create datasets: `backup-pool/pbs` (8TiB), `backup-pool/cephfs-mirror` (20TiB)
  - [ ] Format 20TiB drive as ZFS pool on kovacs

- [ ] Deploy PBS
  - [ ] Create PBS LXC container (ID: 102)
  - [ ] Configure USB passthrough to LXC
  - [ ] Mount PBS dataset in container
  - [ ] Configure PBS datastore

- [ ] Configure backups
  - [ ] Add all Proxmox nodes as backup clients
  - [ ] Create backup jobs for critical LXCs (Technitium, Caddy, Jellyfin)
  - [ ] Configure retention: 7 daily, 4 weekly, 12 monthly
  - [ ] Test backup and restore procedure

- [ ] Configure replication
  - [ ] Set up SSH keys between harlan and kovacs
  - [ ] Configure Syncoid for daily ZFS replication
  - [ ] Test replication and verify snapshots

## Priority 3: Media Services (Jellyfin + ARR Suite)

**Status:** Jellyfin deployed, ARR suite pending  
**Estimated Time:** 2-3 days  
**Blocking:** Nothing (but want operational before K8s complexity)

### Current State

Jellyfin is running in an LXC container with:
- GPU passthrough (P620) for hardware transcoding
- Metadata on CephFS (migrated from rootfs)
- 8GB rootfs (shrunk from 22GB for faster HA failover)
- Media library on CephFS (~10 TiB)

### Missing: ARR Suite

The ARR suite automates media management:
- **Sonarr**: TV series management
- **Radarr**: Movie management
- **Prowlarr**: Indexer management
- **Bazarr**: Subtitle management

### Tasks

- [ ] Deploy ARR Suite LXCs
  - [ ] Create Sonarr LXC with CephFS mounts
  - [ ] Create Radarr LXC with CephFS mounts
  - [ ] Create Prowlarr LXC
  - [ ] Create Bazarr LXC
  - [ ] Configure shared media paths

- [ ] Configure integrations
  - [ ] Connect Sonarr/Radarr to Prowlarr
  - [ ] Configure download clients
  - [ ] Set up Jellyfin library refresh triggers
  - [ ] Configure Bazarr for subtitle downloads

- [ ] Expose via Caddy
  - [ ] Add reverse proxy rules for each service
  - [ ] Configure authentication (basic auth or SSO)
  - [ ] Add DNS records in Technitium

### Why Before Kubernetes?

Running media services in LXC containers is simpler and provides:
- Direct GPU access without device plugins
- Proxmox HA for automatic failover
- Familiar management interface
- Lower complexity than K8s for stateful media workloads

These services may eventually migrate to Kubernetes, but getting them operational now provides immediate value.

## Priority 4: Network Infrastructure

**Status:** Hardware available, deployment pending  
**Estimated Time:** 1-2 days  
**Blocking:** Optimal Ceph and cluster performance

### Switch Upgrades

Current backbone: HP ProCurve 2510-24 (J9019B) — 24x 10/100 ports + 2 dual-personality GbE uplinks, managed, fanless, no LACP  
Current SAN: Netgear 8-port consumer switch (unmanaged, hangs every 4-6 months requiring reboot)  
Target backbone: HP ProCurve 2824 (24x 1GbE ports, managed, LACP capable)  
Target SAN: HP ProCurve 2810 (24x 1GbE ports, managed, LACP capable)

### Tasks

- [ ] Deploy HP ProCurve 2810 for SAN network (priority)
  - [ ] Replace Netgear 8-port consumer switch
  - [ ] Configure LACP port channels
  - [ ] Migrate Ceph Core nodes to bonded connections
  - [ ] Verify improved replication performance

- [ ] Deploy HP ProCurve 2824 for primary network
  - [ ] Replace existing HP ProCurve 2510-24 backbone switch
  - [ ] Configure LACP for management traffic
  - [ ] Migrate edge Netgear switches as needed

- [ ] Router upgrade (Raleigh)
  - [ ] Replace Google Wifi (original) with Google Nest Wifi 6
  - [ ] Coordinate with Brume 2 deployment
  - [ ] Verify multi-gigabit Google Fiber utilization

### UPS Deployment

Available hardware:
- APC Smart UPS X 1500 (unused)
- 2-3x APC Back-UPS ES 450

Tasks:
- [ ] Deploy Smart UPS X 1500 for network stack
- [ ] Deploy Back-UPS units for critical Proxmox nodes
- [ ] Configure NUT for graceful shutdowns
- [ ] Test power failure scenarios

## Priority 5: Boot Drive Health

**Status:** Mixed health across nodes  
**Estimated Time:** 1-2 days per node  
**Blocking:** Cluster stability

### Current Drive Status

| Node | Health | Power-On Hours | Priority |
|------|--------|----------------|----------|
| harlan | ✅ Excellent | 291h | Low |
| kovacs | ⚠️ Aging | 43,619h | Medium |
| poe | ⚠️ Aging | 55,968h | High |
| edgar | 🔴 Critical | 36,497h (384 reallocated) | Immediate |
| tanaka | ⚠️ Monitor | 24,632h | Medium |
| quell | ✅ Excellent | 59h | Complete |

### Tasks

- [ ] Edgar (Critical)
  - [ ] Replace failing Toshiba drive with SSD
  - [ ] Consider UEFI migration during replacement
  - [ ] Restore ZFS boot mirror

- [ ] Poe (High Priority)
  - [ ] Plan SSD replacement for oldest drives
  - [ ] Schedule maintenance window

- [ ] Kovacs/Tanaka (Medium Priority)
  - [ ] Monitor SMART attributes
  - [ ] Order replacement SSDs
  - [ ] Schedule rolling upgrades

### Standardization Goal

All nodes on 128GB SSDs in ZFS mirror configuration:
- Faster boot times
- Reduced mechanical wear
- Consistent hardware across cluster
- ~$40-60 per node

## Priority 6: Documentation and Cleanup

**Status:** Ongoing  
**Estimated Time:** 2-3 hours  
**Blocking:** Nothing (but improves maintainability)

### Tasks from ACTIONABLE-TASKS.md

- [ ] Verify README.md links in k8s-proxmox
- [ ] Review and update CLUSTER-SUMMARY.md
- [ ] Consolidate network documentation
- [ ] Create documentation index (docs/README.md)
- [ ] Standardize manifest READMEs

### Blog Post Backlog

- [ ] Finish VMS roadmap post (currently unpublished)
- [ ] Update K8s-on-Proxmox draft (outdated)
- [ ] Document Brume 2 deployment (after completion)

## The Kubernetes Deployment Sequence

Once all prerequisites are complete, the Kubernetes deployment follows this sequence from the k8s-proxmox articles:

### Phase 1: Foundation (Articles 00-03)
1. **Article 00**: Verify Proxmox foundation ✅ (already complete)
2. **Article 01**: Configure Ceph S3 RGW (for Velero backups)
3. **Article 02**: Create LXC deployment container
4. **Article 03**: Deploy Kubernetes with Terraform + Ansible

### Phase 2: GitOps Infrastructure (Articles 04-05)
5. **Article 04**: Install ArgoCD immediately after K8s
6. **Article 05**: Bootstrap infrastructure via ArgoCD
   - Ceph CSI driver
   - MetalLB LoadBalancer
   - Monitoring stack (Prometheus/Grafana)

### Phase 3: Platform Services (Articles 06-11)
7. **Article 06**: Ingress + cert-manager (Porkbun DNS-01)
8. **Article 07**: Loki logging
9. **Article 08**: Cluster autoscaler
10. **Article 09**: Sealed Secrets
11. **Article 10**: Ceph S3 Kubernetes integration
12. **Article 11**: Velero backups

### Phase 4: Security and Governance (Articles 12-18)
13. **Article 12**: Kyverno policy enforcement
14. **Article 13**: Calico network policies
15. **Article 14**: Harbor container registry
16. **Article 15**: Istio service mesh (evaluation)
17. **Article 16**: External DNS automation
18. **Article 17**: Database operators
19. **Article 18**: Production readiness checklist

### Phase 5: Application Platform (Article 19)
20. **Article 19**: Kubero PaaS for Procfile-based deployments

## Timeline Estimate

| Priority | Tasks | Estimated Time |
|----------|-------|----------------|
| 0 | Site-to-Site VPN | 2-3 days |
| 1 | DNS Decision | 1-2 days |
| 2 | PBS Backups | 3-4 days |
| 3 | Media Services | 2-3 days |
| 4 | Network Infrastructure | 1-2 days |
| 5 | Boot Drive Health | 1-2 days per node |
| 6 | Documentation | 2-3 hours |

**Total before Kubernetes:** ~2-3 weeks of focused work

**Kubernetes deployment:** ~1 week (Articles 00-05)

**Full platform:** ~2-3 weeks additional (Articles 06-19)

## Success Criteria

Before running `terraform apply` for Kubernetes:

- [ ] Site-to-site VPN operational (Beach can reach Raleigh services via WireGuard)
- [ ] DNS infrastructure finalized (Custom Technitium DNS on all Google Wifi/Nest Wifi)
- [ ] PBS backing up all critical LXCs and VMs
- [ ] Jellyfin and ARR suite operational
- [ ] HP ProCurve 2810 deployed for SAN network (LACP for Ceph)
- [ ] HP ProCurve 2824 deployed for primary network (replacing ProCurve 2510-24)
- [ ] Edgar boot drive replaced
- [ ] All documentation current

## Conclusion

Friday the 13th seems appropriate for confronting this list. It's intimidating, but each task is well-defined and achievable. The key insight is that Kubernetes is not the goal—it's a tool. The real goal is a reliable, maintainable homelab that serves my needs.

By completing these prerequisites, I'm not just preparing for Kubernetes—I'm building a solid foundation that will make the entire infrastructure more resilient. The site-to-site VPN benefits all services, not just K8s. The backup infrastructure protects everything. The media services provide immediate value.

Kubernetes can wait until the foundation is solid. And when it's deployed, it will be on infrastructure I trust.

## References

- [k8s-proxmox Repository](https://github.com/mcgarrah/k8s-proxmox)
- [AlteredCarbon Infrastructure Overview](/proxmox-homelab-infrastructure-overview/)
- [Proxmox 8 Lessons Learned](/proxmox-8-lessons-learned/)
- [Jellyfin LXC Optimization](/optimizing-jellyfin-on-proxmox-moving-metadata-to-cephfs-and-shrinking-lxc-footprints/)
