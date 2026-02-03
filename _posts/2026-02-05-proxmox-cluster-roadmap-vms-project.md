---
title: "Proxmox Cluster Roadmap: Building VMS (Video Media Service)"
layout: post
categories: [technical, homelab, roadmap]
tags: [proxmox, homelab, infrastructure, planning, vms, jellyfin, arr-suite, dns, gpu, caddy, sso, kubernetes]
published: false
---

This is my comprehensive roadmap for transforming my Proxmox homelab cluster into a production-ready Video Media Service (VMS) accessible at `vms.home.mcgarrah.org` from both my Raleigh and Beach locations. The project spans infrastructure hardening, service deployment, and eventual Kubernetes migration.

<!-- excerpt-end -->

## Phase 1: Infrastructure Foundation (Current Priority)

### ZFS Boot Mirrors
**Status:** In Progress - Boot mirror redundancy restoration

**Current Drive Health Analysis:**

| Node | Drive Health | Power-On Hours | Age | Status | Priority |
|------|-------------|----------------|-----|--------|----------|
| **harlan** | ✅ Excellent | 291h (~12 days) | New SSDs | Healthy | Low |
| **kovacs** | ⚠️ Aging | 43,619h / 42,708h | ~5 years | Monitor | Medium |
| **poe** | ⚠️ Aging | 55,968h / 48,952h | ~6.4 / 5.6 years | Oldest drives | High |
| **edgar** | 🔴 Critical | 36,497h / 15,162h | **384 reallocated sectors** | **Failing** | **Immediate** |
| **tanaka** | ⚠️ Monitor | 24,632h / 19,329h | ~2.8 / 2.2 years | 1 reallocated sector | Medium |
| **quell** | ✅ Excellent | 59h / 52h | **New TimeTec SSDs** | **Recently upgraded** | **Complete** |

**Immediate Actions:**
- **Quell:** ✅ **Completed** - Replaced failed Brikmet SSDs with new TimeTec 128GB SSDs
- **Edgar:** 🔴 **Critical** - Toshiba MQ01ABD100 has 384 reallocated sectors, **waiting for SSDs (Feb 8th delivery)**
- **Poe:** ⚠️ **Plan replacement** - 55,968 hours (6.4 years) on sda, oldest drives in cluster

**Upgrade Strategy:**
- **Standardize on 128GB SSDs** for all boot mirrors (adequate for Proxmox)
- **Brand diversification** - Multiple reputable SSD manufacturers to reduce single-vendor risk
- **Lessons from Brikmet failure** - Avoid single-brand dependency across cluster
- **Cost-effective approach** - ~$40-60 per node for dual SSD setup
- **Performance benefit** - Eliminate mechanical wear, improve boot times
- **Reliability improvement** - Modern SSDs vs aging HDDs

### BIOS to UEFI Migration
**Status:** Immediate - Edgar first UEFI conversion

**Edgar Priority (Critical - First UEFI Conversion):**
- **Current Issue:** Toshiba sdb drive has 384 reallocated sectors (failing)
- **Hardware Status:** SSDs available, waiting for additional drives from Amazon (Feb 8th, 2026)
- **Boot Mode:** Legacy BIOS with MBR partitioning
- **Target:** First cluster node to migrate to UEFI boot with GPT partitioning
- **Benefits:** Modern boot capabilities, larger partition support, improved reliability
- **Strategy:** Use Edgar's failing drive situation as opportunity for UEFI migration
- **Timeline:** Blocked until Feb 8th SSD delivery

**Migration Process:**
- **Hardware:** Replace failing HDDs with 2x 128GB SSDs
- **Firmware:** Enable UEFI mode in BIOS settings
- **Installation:** Fresh Proxmox install with UEFI/GPT
- **Recovery:** Restore cluster configuration and rejoin

**Other Nodes (Future UEFI Conversions):**
- **Tanaka:** Desktop form factor, 4 SATA ports (2 available), easy SSD upgrade path
- **Poe:** ⚠️ Priority - Oldest drives (6+ years), combine UEFI migration with SSD replacement
- **Kovacs:** Aging Samsung HD161HJ drives (5 years), schedule for Q2-Q3 2026
- **Harlan:** Already on new SSDs (291 hours), evaluate UEFI conversion benefits
- **Quell:** Recently upgraded TimeTec SSDs (59/52 hours), currently BIOS/MBR, stable

### Log2RAM Implementation
**Status:** Planned - Reduce storage wear across infrastructure

**Proxmox Cluster Nodes (Dell Optiplex 990):**
- **Target Nodes:** Edgar, Harlan, Kovacs, Poe, Quell, Tanaka
- **Purpose:** Reduce write cycles on ZFS boot mirrors (SSDs/HDDs)
- **Benefits:** Extend boot drive lifespan, improve performance
- **Implementation:** RAM-based logging with periodic sync to disk

**Tailscale Node (Dell Wyse 3040):**
- **Target:** Standalone Wyse 3040 running Tailscale
- **Purpose:** Protect eMMC storage from log write wear
- **Benefits:** Extend eMMC lifespan on embedded storage
- **Critical:** eMMC has limited write cycles, Log2RAM essential

**Deployment Strategy:**
- **Phase 1:** Wyse 3040 Tailscale node (highest risk)
- **Phase 2:** Proxmox cluster nodes (systematic rollout)
- **Monitoring:** Track storage health metrics post-implementation

### Proxmox Storage Optimizations
**Status:** Planned - Reduce unnecessary disk writes

**ZFS atime Optimization:**
- **Setting:** Disable atime (access time) updates on ZFS boot mirrors
- **Command:** `zfs set atime=off rpool`
- **SSD Impact:** Reduces write amplification, extends SSD lifespan significantly
- **HDD Impact:** Reduces mechanical wear, improves performance on aging drives
- **Trade-off:** Applications that rely on atime include:
  - **tmpwatch/tmpreaper:** File cleanup based on access time (use mtime instead)
  - **mutt/mail clients:** "New mail" detection (most use mtime now)
  - **find -atime:** Scripts using access time for file management
  - **Backup tools:** Some legacy backup software (rsync uses mtime)
  - **File servers:** NFS/SMB access time tracking (rarely needed)
- **Proxmox Impact:** Minimal - Proxmox uses mtime for most operations

**RRDcached Optimization:**
- **Purpose:** Reduce SSD writes from Proxmox monitoring data
- **Implementation:** Disable or reduce rrdcached journaling frequency
- **Configuration:** Adjust `/etc/default/rrdcached` settings
- **Benefits:** Fewer small writes, better SSD endurance
- **Monitoring:** Ensure performance metrics still captured adequately

### DNS Infrastructure Overhaul
**Status:** In Progress - Split-brain DNS with redundancy

**Primary Options:**
- **Technitium DNS:** Modern web UI, Docker-friendly
- **PowerDNS:** Enterprise-grade, API-driven
- **Implementation:** LXC containers with Proxmox SDN integration
- **Features:** Split-brain DNS, internal/external resolution
- **Redundancy:** Multi-node deployment for high availability

### GPU Enablement
**Status:** Planned - Enable GPU passthrough for media processing

**Current Hardware:**
- **4x Nvidia P620 GPUs:** Harlan, Kovacs, Poe, Quell
- **2x Nvidia K600 GPUs:** Edgar, Tanaka
- **Use Cases:** Jellyfin transcoding, AI workloads
- **Implementation:** GPU passthrough to VMs and LXC containers

### Network Infrastructure Requirements
**Status:** Critical - Foundation for all services

**Current Network Architecture:**
- **Primary Network:** 192.168.86.0/23 (512 IPs) - Management, VMs, Services
- **SAN Network:** 10.10.10.0/23 (512 IPs) - Ceph storage traffic
- **Pod Network:** 10.244.0.0/16 (Kubernetes pods via Calico)
- **Service Network:** 10.96.0.0/12 (Kubernetes services)

**IP Allocation Plan:**
- **Proxmox Nodes:** 192.168.86.11-16 (6 nodes)
- **K8s VMs:** 192.168.86.101-200 (100 IPs available)
- **MetalLB Pool:** 192.168.87.100-200 (101 LoadBalancer IPs)
- **DHCP Pool:** 192.168.86.20-100 (81 IPs)
- **Static Services:** 192.168.86.201-254 (54 IPs)

**Critical Missing Components:**
- **Ingress Controller:** nginx-ingress or Traefik for HTTP routing
- **Certificate Management:** cert-manager for automatic SSL/TLS
- **DNS Automation:** External-DNS for automatic record creation

### Monitoring Infrastructure
**Status:** Post-VMS Priority - Critical for HA service management

**Implementation Timeline:**
- **Phase 1:** Deploy after Jellyfin and Arr Suite are operational
- **Priority:** Service delivery first, observability second
- **Rationale:** Focus on immediate VMS functionality, then add management tools

**Proxmox 8.4 Native Features:**
- **Built-in Metrics:** Enhanced node resource monitoring
- **Ceph Integration:** Native Ceph cluster health dashboards
- **ZFS Monitoring:** Pool health, scrub status, ARC statistics
- **Network Monitoring:** Interface statistics, bond status

**LXC Container Stack (Proxmox Helper Scripts):**
- **Prometheus:** Metrics collection and storage
- **Grafana:** Visualization dashboards and alerting
- **Node Exporter:** System metrics from all Proxmox nodes
- **Ceph Exporter:** Detailed Ceph cluster metrics
- **ZFS Exporter:** ZFS pool and dataset statistics

**Deployment Strategy:**
- **Helper Scripts:** Use tteck.github.io Proxmox Helper Scripts
- **HA Configuration:** Deploy monitoring LXCs across multiple nodes
- **Data Retention:** 30-day detailed, 1-year aggregated metrics
- **Alerting:** Critical alerts for hardware failures, storage issues
- **Integration:** Expose via Caddy proxy for internal access

**Key Metrics to Track:**
- **VMS Services:** Jellyfin transcoding performance, Arr Suite health
- **Node Resources:** CPU, RAM, disk I/O, network throughput
- **Ceph Health:** OSD status, pool utilization, replication lag
- **ZFS Performance:** ARC hit ratio, scrub progress, pool health
- **Storage Wear:** SSD endurance, HDD SMART attributes
- **Network:** LACP bond status, interface errors, bandwidth utilization

### Network Infrastructure Upgrades
**Status:** High Priority - Comprehensive network modernization

**Switch Infrastructure (ProCurve 2800 Deployment):**
- **Current:** Single 1GbE connections per node
- **Target:** LACP bonded connections for redundancy and throughput
- **Hardware:** HP ProCurve 2800 series switches (already acquired)
- **Limitations:** No IPv6 support (would require ProCurve 2900 series upgrade)
- **Benefits:** Link redundancy, improved bandwidth utilization
- **Future Upgrade Path:** ProCurve 2900 series for full IPv6 and advanced VLAN support

**LACP Configuration:**
- **Proxmox Nodes:** Configure bond0 with LACP (802.3ad)
- **Switch Config:** Configure port channels/trunks
- **Network Separation:** Management, Ceph public, Ceph cluster networks
- **Redundancy:** Eliminate single points of network failure

**Router & ISP Infrastructure Upgrade:**
- **Raleigh Location:** Upgrade from Google Wifi (original) to Google Nest Wifi 6
- **Beach Location:** ✅ Already upgraded to Google Nest Wifi 6
- **Hardware Status:** New Wifi 6 router and endpoints ready for installation
- **IPv6 Support:** Router-level IPv6 connectivity (limited by ProCurve 2800 switch capabilities)
- **Multi-Gigabit Capability:** Support Google Fiber multi-gig speeds (>1Gbps)
- **ISP Integration:** Full utilization of Google Fiber bandwidth capabilities
- **VLAN Limitations:** Advanced VLAN features constrained by ProCurve 2800 series
- **Benefits:** Wifi 6 performance, better coverage, improved client capacity, partial IPv6 support
- **Timeline:** Deploy alongside ProCurve switch installation

**Implementation Priority:**
- **Critical for VMS:** Network reliability essential for media streaming
- **Ceph Performance:** Bonded connections improve storage network performance
- **ISP Utilization:** Multi-gigabit Google Fiber support for high-bandwidth streaming
- **Partial IPv6:** Router-level IPv6 support (full network IPv6 requires ProCurve 2900 upgrade)
- **Wireless Performance:** Wifi 6 supports high-bandwidth media streaming
- **HA Requirements:** Network redundancy supports cluster availability
- **Future Considerations:** ProCurve 2900 series upgrade for complete IPv6 and advanced VLAN support LACP bond status, interface errors, bandwidth utilization

## Phase 2: Core Services Deployment

### Caddy Reverse Proxy
**Status:** Q1 Priority - Internal testing with split-brain DNS

- **Deployment:** LXC container with automatic HTTPS
- **Phase 1:** Internal testing with split-brain DNS resolution
- **Services:** Jellyfin, Arr Suite, monitoring dashboards
- **Features:** Automatic Let's Encrypt certificates for internal domains
- **Configuration:** Dynamic service discovery
- **Security:** Internal-only access until SSO implementation

### Arr Suite on LXC
**Status:** Planned - Media automation stack

**Components:**
- **Sonarr:** TV series management
- **Radarr:** Movie management  
- **Prowlarr:** Indexer management
- **Bazarr:** Subtitle management
- **Deployment:** Dedicated LXC containers
- **Storage:** Ceph RBD for configuration, CephFS for media

### Jellyfin Media Server
**Status:** Planned - Primary media streaming service

- **Deployment:** LXC with GPU passthrough for transcoding
- **Storage:** CephFS for media library
- **Features:** Hardware-accelerated transcoding
- **Access:** Internal and external via Caddy proxy

### SSO Authentication
**Status:** Planned - Unified authentication across services

**Options:**
- **Authentik:** Modern, container-native
- **Keycloak:** Enterprise-grade OIDC/SAML
- **Integration:** Jellyfin, Arr Suite, monitoring tools
- **Benefits:** Single sign-on, centralized user management

### Proxmox Backup Server (PBS)
**Status:** Planned - CephFS media library backup solution

**Hardware Configuration:**
- **Backup Drives:** 20TiB and 28TiB ZFS-formatted USB drives
- **Attachment:** Connected to cluster nodes with available USB ports
- **Total Capacity:** 48TiB raw backup storage

**Implementation Strategy:**
- **Deployment:** PBS as LXC container on node with attached drives
- **Target:** CephFS media library backup and retention
- **Scheduling:** Automated backup jobs for media content
- **Deduplication:** PBS native deduplication for space efficiency
- **Retention:** Configurable retention policies for media archives

**Planning Status:**
- **Current:** Placeholder - detailed planning required
- **Dependencies:** VMS services operational, monitoring in place
- **Timeline:** Q3 2026 after core services are stable

### Production-Ready Kubernetes Stack
**Status:** Planned - Critical components missing

**Phase 1 - Core Infrastructure (Critical):**
- **Ingress Controller:** nginx-ingress for HTTP/HTTPS routing
- **Certificate Management:** cert-manager with Let's Encrypt
- **Monitoring Stack:** Prometheus + Grafana + AlertManager
- **Logging Stack:** Loki + Promtail for centralized logging

**Phase 2 - Security & Operations:**
- **Secrets Management:** Sealed Secrets or External Secrets Operator
- **Policy Enforcement:** Kyverno for Pod Security Standards
- **Network Policies:** Calico microsegmentation
- **Backup Automation:** Velero with Ceph S3 backend

**Phase 3 - Advanced Features:**
- **Container Registry:** Harbor with vulnerability scanning
- **Service Mesh:** Istio for mTLS and traffic management
- **Database Operators:** PostgreSQL/MySQL operators
- **Developer Platform:** Kubero PaaS for Django applications

**Current Status:**
- ✅ Kubernetes 1.33 deployment
- ✅ MetalLB load balancer
- ✅ Ceph RBD/S3 integration
- ✅ ArgoCD GitOps
- ⚠️ Missing all Phase 1 critical components

## Phase 3: External Access & Security

### DNS Registrar Migration
**Status:** Current Priority - Move from SquareSpace to PorkBun

**Current Progress:**
- **Batch 1:** 5 domains (mathomancer.com, mathomancy.com, brainyzone.com/org, cshensley.com)
- **Remaining:** 11 domains in 5 batches through 2028
- **Q1 Target:** Complete Batches 1-3 (9 domains total)
- **Benefits:** Better API, lower costs, improved management
- **Integration:** API-driven DNS record management with new DNS infrastructure
- **Timeline:** Accelerated to support VMS public deployment

### Public Service Exposure
**Status:** Q3 Priority - Secure external access after SSO

**Components:**
- **Tailscale:** Mesh VPN for secure access
- **Cloudflare Tunnel:** Alternative public exposure method
- **Security:** Rate limiting, geo-blocking, fail2ban
- **Monitoring:** Access logs, intrusion detection
- **Target Services:** Jellyfin and Arr Suite public access
- **Prerequisites:** SSO implementation, security hardening, internal testing complete

### Multi-Location Access
**Status:** Planned - Seamless access from Raleigh and Beach

- **VPN:** Site-to-site connectivity
- **Replication:** Consider media sync between locations
- **Failover:** Backup access methods
- **Performance:** Optimize for remote streaming

### LACP Network Bonding & ProCurve Integration
**Status:** High Priority - Network infrastructure upgrade

**ProCurve 2800 Switch Deployment:**
- **Current:** Single 1GbE connections per node
- **Target:** LACP bonded connections for redundancy and throughput
- **Hardware:** HP ProCurve 2800 series switches (already acquired)
- **Benefits:** Link redundancy, improved bandwidth utilization

**LACP Configuration:**
- **Proxmox Nodes:** Configure bond0 with LACP (802.3ad)
- **Switch Config:** Configure port channels/trunks
- **Network Separation:** Management, Ceph public, Ceph cluster networks
- **Redundancy:** Eliminate single points of network failure

**Implementation Priority:**
- **Critical for VMS:** Network reliability essential for media streaming
- **Ceph Performance:** Bonded connections improve storage network performance
- **HA Requirements:** Network redundancy supports cluster availability

### UPS Power Management
**Status:** High Priority - Power protection for critical infrastructure

**Available Hardware:**
- **APC Smart UPS X 1500:** Primary UPS with USB management (unused)
- **APC Back-UPS ES 450:** 2-3 units available with USB cables
- **Current Status:** All units charged but not deployed

**Deployment Strategy:**
- **Network Stack:** Smart UPS X 1500 for switches and router
- **Proxmox Nodes:** Back-UPS ES 450 units for critical nodes
- **Priority Nodes:** Edgar (failing drive), Harlan/Quell (Ceph core)
- **Integration:** NUT (Network UPS Tools) for monitoring and shutdown

**Implementation Timeline:**
- **Phase 1:** Deploy with ProCurve 2800 switch installation
- **Phase 2:** Configure NUT for graceful shutdowns
- **Phase 3:** Test power failure scenarios
- **Benefits:** Prevent data corruption, extend hardware lifespan

## Phase 4: Advanced Infrastructure (Future)

### Kubernetes Migration
**Status:** Future - Based on `/k8s-proxmox` repository

**Foundation Articles (Planned):**
1. **Proxmox Foundation** - Base cluster preparation
2. **Ceph S3 RGW** - Object storage integration
3. **LXC Deployment Container** - K8s node preparation
4. **Kubernetes Deployment** - Cluster bootstrap
5. **MetalLB Load Balancer** - Service exposure
6. **Ingress & Cert Manager** - HTTPS automation
7. **Prometheus & Grafana** - Monitoring stack
8. **Loki Logging** - Centralized logging
9. **ArgoCD GitOps** - Deployment automation
10. **Cluster Autoscaler** - Dynamic scaling

**Advanced Features:**
- **Secrets Management** - Vault integration
- **Velero Backups** - Disaster recovery
- **Kyverno Policies** - Security enforcement
- **Calico Network Policies** - Microsegmentation
- **Harbor Registry** - Container image management
- **Istio Service Mesh** - Advanced networking
- **External DNS** - Automated DNS management
- **Database Operators** - Managed databases
- **Kubero PaaS** - Developer platform

### Production Readiness
**Status:** Future - Enterprise-grade capabilities

- **High Availability:** Multi-master Kubernetes
- **Disaster Recovery:** Cross-site replication
- **Monitoring:** Comprehensive observability
- **Security:** Zero-trust networking
- **Compliance:** Automated policy enforcement

### Proxmox SDN & OpenWRT Integration
**Status:** Planned - Advanced networking for HA services

**SDN Implementation:**
- **Purpose:** Inter-node networking for HA LXC containers
- **Technology:** VXLAN with EVPN for cluster-wide networking
- **Use Case:** OpenWRT LXC with HA failover capability
- **Benefits:** Advanced routing, firewall, and network services in HA

**OpenWRT LXC:**
- **Deployment:** LXC container with SDN networking
- **Features:** Advanced routing, VPN, firewall capabilities
- **HA Support:** Failover between cluster nodes
- **Management:** LuCI web interface for network configuration

## Implementation Timeline

### Q1 2026 (Current Focus)
- [ ] **Edgar BIOS to UEFI migration** (Feb 8th+ - waiting for SSD delivery)
- [ ] **Network infrastructure upgrades** (ProCurve switches + Google Nest Wifi 6)
- [ ] **UPS deployment** (Smart UPS X 1500 + Back-UPS ES 450 units)
- [ ] **DNS registrar migration completion** (Batch 1-3)
- [ ] **Caddy proxy deployment** (internal testing with split-brain DNS)
- [ ] **Proxmox storage optimizations** (ZFS atime=off, RRDcached tuning)
- [ ] ZFS boot mirror restoration
- [ ] Log2RAM deployment
- [ ] DNS infrastructure (Technitium/PowerDNS)
- [ ] GPU enablement testing

### Q2 2026
- [ ] **Arr Suite LXC containers** (Sonarr, Radarr, Prowlarr, Bazarr)
- [ ] **Jellyfin with GPU transcoding** (primary media server)
- [ ] **Basic SSO implementation** (Authentik or Keycloak)
- [ ] **Internal testing and optimization** (performance tuning)
- [ ] **Multi-location testing** (Raleigh and Beach access)

### Q3 2026
- [ ] **Public service exposure** (Jellyfin and Arr Suite external access)
- [ ] **Monitoring infrastructure deployment** (Prometheus + Grafana for HA management)
- [ ] **Proxmox Backup Server (PBS)** (LXC with ZFS USB drives for CephFS backups)
- [ ] **Security hardening** (fail2ban, rate limiting, geo-blocking)
- [ ] **Performance optimization** (4K transcoding, network tuning)
- [ ] **Backup strategies** (media library, configuration backups)
- [ ] **Monitoring and alerting** (service health, resource usage)

### Q4 2026 & Beyond - Kubernetes Platform
- [ ] **Kubernetes cluster deployment** (production-ready foundation)
- [ ] **Ingress Controller + cert-manager** (nginx-ingress, Let's Encrypt)
- [ ] **Prometheus + Grafana monitoring stack** (cluster observability)
- [ ] **Loki logging stack** (centralized logging)
- [ ] **Service migration to K8s** (gradual transition from LXC)
- [ ] **Advanced K8s features** (Istio, Harbor, Kubero PaaS)
- [ ] **Production readiness validation** (HA, security, compliance)

## Success Metrics

### Technical Goals
- **Uptime:** 99.9% availability for core services
- **Performance:** Sub-second response times for web interfaces
- **Security:** Zero successful intrusions, automated patching
- **Scalability:** Easy addition of new services and nodes

### User Experience Goals
- **Access:** Seamless streaming from both locations
- **Quality:** 4K transcoding with GPU acceleration
- **Management:** Single sign-on across all services
- **Reliability:** Automatic failover and recovery

## Resource Requirements

### Hardware Needs
- **Replacement drives** for ZFS boot mirrors
- **Network storage** expansion for media library
- **GPU optimization** for transcoding workloads
- **Network infrastructure** ProCurve switch deployment
- **UPS integration** NUT software and USB cable management
- **Backup storage** ZFS USB drive integration for PBS

### Software Licenses
- **Domain registrations** at PorkBun
- **SSL certificates** via Let's Encrypt (free)
- **Monitoring tools** (mostly open source)

### Time Investment
- **Phase 1-2:** ~40 hours over 6 months
- **Phase 3:** ~20 hours over 3 months  
- **Phase 4:** ~80 hours over 12+ months

## Risk Mitigation

### Technical Risks
- **Hardware failures:** Redundant storage, spare components
- **Network issues:** Multiple internet connections, VPN fallbacks
- **Security breaches:** Regular updates, monitoring, backups

### Operational Risks
- **Complexity creep:** Phased implementation, documentation
- **Time overruns:** Realistic timelines, priority focus
- **Scope expansion:** Clear phase boundaries, future roadmap

## Conclusion

This roadmap transforms my Proxmox homelab from a development cluster into a production-ready Video Media Service. The phased approach ensures stability while building toward advanced Kubernetes capabilities documented in my `/k8s-proxmox` repository.

The ultimate goal is `vms.home.mcgarrah.org` - a reliable, secure, and performant media service accessible from anywhere, with the infrastructure foundation to support future expansion into a full home operations platform.

**Next Steps:** Begin with ZFS boot mirror restoration and Log2RAM implementation, as these provide immediate stability improvements for the foundation work ahead.
