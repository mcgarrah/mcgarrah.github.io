---
title: "Homelab Infrastructure Upgrades: Addressing Network Bottlenecks and Reliability Issues"
layout: post
categories: ["homelab", "networking", "infrastructure"]
tags: ["glinet", "brume2", "tailscale", "procurve", "proxmox", "caddy", "vpn", "networking"]
published: false
---

After months of dealing with intermittent network issues, aging hardware bottlenecks, and reliability problems in my homelab, it's time for a comprehensive infrastructure upgrade. These aren't just nice-to-have improvements—they're addressing real pain points that have been impacting daily operations and limiting the lab's potential.

<!-- excerpt-end -->

## The Current Pain Points

My homelab has grown organically over the years, and like many homelabs, it's reached that point where the infrastructure is holding back progress rather than enabling it. Here are the key issues I'm facing:

### Network Connectivity Challenges

- **Site-to-site connectivity** across five family locations (Raleigh, Beach, Wilson, Katie, Sam) is unreliable
- **100Mb bottlenecks** on backbone switch (HP ProCurve 2510-24 J9019B has 24x 10/100 ports) limiting cluster and storage traffic
- **Netgear switch reliability** — consumer-grade SAN switches hang every 4-6 months requiring manual reboot
- **DNS resolution** inconsistencies across different network segments
- **Media streaming** performance issues due to proxy limitations

### Storage and Compute Reliability

- **ZFS boot drive failures** on Proxmox nodes causing cluster instability
- **Single points of failure** in the boot configuration
- **Maintenance windows** becoming too frequent due to hardware issues

## Planned Infrastructure Upgrades

### 1. GL-iNet Brume 2 VPN Implementation

**Problem**: Current site-to-site connectivity relies on consumer-grade solutions that frequently drop connections and provide inconsistent performance between my Raleigh lab and Emerald Isle remote location.

**Solution**: Deploy GL-iNet Brume 2 (GL-MT2500A) VPN appliances at both locations for enterprise-grade site-to-site connectivity.

**Implementation Plan**:

```bash
# Raleigh Location (Main Site)
- GL-iNet Brume 2 configured as WireGuard server on LAN
- Static IP: 192.168.87.250 on 192.168.86.0/23 network
- WireGuard tunnel: 10.99.0.1/24
- Port forwarding: Google Fiber Router → Google Wifi → Brume 2

# Emerald Isle Location (Remote Site)  
- GL-iNet Brume 2 configured inline (Spectrum → Brume 2 → Google Nest Wifi)
- Transit network: 192.168.2.0/24
- WireGuard tunnel: 10.99.0.3/24
- Routes Raleigh traffic (192.168.86.0/23) through VPN tunnel
```

**Expected Benefits**:

- **Always-on connectivity** between sites
- **Enterprise-grade encryption** for secure data transfer
- **Automatic failover** and reconnection capabilities
- **Centralized management** of both endpoints

### 2. Tailscale Infrastructure Upgrade

**Problem**: Current Tailscale deployment lacks advanced DNS features and misses recent security and performance improvements from the October 2025 release.

**Solution**: Upgrade to latest Tailscale with enhanced DNS and new features.

**Key Improvements**:

```yaml
# Enhanced DNS Configuration
dns:
  nameservers:
    - 100.100.100.100  # Tailscale MagicDNS
    - 192.168.86.3     # Local Technitium DNS
  search_domains:
    - home.mcgarrah.org
    - ts.net
  
# New October 2025 Features
features:
  - enhanced_exit_nodes    # Better performance routing
  - subnet_router_v2       # Improved subnet routing
  - dns_over_https        # Secure DNS resolution
  - mesh_vpn_optimization # Reduced latency
```

**Migration Steps**:

1. **Backup current configuration** and node keys
2. **Update Tailscale clients** across all devices
3. **Reconfigure DNS settings** with new MagicDNS features
4. **Test connectivity** between all nodes and subnets
5. **Update firewall rules** for new feature compatibility

### 3. Core Network Switch Upgrades

**Problem**: The HP ProCurve 2510-24 (J9019B) backbone switch has 24x 10/100 Mbps ports with only 2 dual-personality Gigabit uplinks (RJ-45 or SFP), creating 100Mb bottlenecks for all node traffic. The switch is fanless, 1U rack-mountable, and managed (CLI + [Java WebUI](/java-jnlp-webui/)), but lacks LACP support. The Netgear 8-port SAN switch is unmanaged and hangs every 4-6 months requiring manual reboot. Neither supports LACP, preventing link aggregation for:

- **Proxmox cluster traffic** between nodes
- **Ceph storage replication** and client access (single 1GbE link per node)
- **VM migration** operations
- **Media streaming** from NAS to clients

**Solution**: Upgrade both core switches to LACP-capable managed switches.

**Hardware Plan**:

```text
Primary Network:
  Current: HP ProCurve 2510-24 (J9019B) — 24x 10/100 ports + 2 dual-personality GbE uplinks, managed, fanless, no LACP
  Target:  HP ProCurve 2824 (24x 1GbE ports, managed, LACP capable)

SAN Network:
  Current: Netgear 8-port consumer switch (unmanaged, hangs every 4-6 months)
  Target:  HP ProCurve 2810 (24x 1GbE ports, managed, LACP capable)

Network Topology:
┌─────────────────────┐    ┌─────────────────────┐
│  HP ProCurve 2824   │    │  HP ProCurve 2810   │
│  Primary Network    │    │  SAN Network        │
│  192.168.86.0/23    │    │  10.10.10.0/23      │
└─────────────────────┘    └─────────────────────┘
```

**Implementation Strategy**:

1. **SAN first** - Replace Netgear 8-port with HP ProCurve 2810 (immediate Ceph benefit)
2. **Primary second** - Replace HP ProCurve 2510-24 with HP ProCurve 2824
3. **LACP bonding** - Configure 802.3ad on Ceph Core nodes for aggregate bandwidth
4. **Cable management** - Upgrade patch cables to Cat6
5. **Performance testing** - Validate throughput improvements with iperf3

### 4. Proxmox Boot Drive Reliability Upgrade

**Problem**: Current Proxmox cluster nodes use single ZFS boot drives that have experienced multiple failures, causing:

- **Unplanned downtime** during boot drive failures
- **Complex recovery procedures** requiring manual intervention
- **Data consistency concerns** during unexpected shutdowns
- **Maintenance overhead** from frequent hardware issues

**Solution**: Implement redundant SSD boot configuration for all cluster nodes.

**New Boot Architecture**:

```text
Current Configuration:
┌─────────────────┐
│  Single 500GB   │  ← Single point of failure
│  ZFS Boot Drive │
└─────────────────┘

New Configuration:
┌─────────────────┐    ┌─────────────────┐
│   120GB SSD #1  │────│   120GB SSD #2  │
│  (ZFS Mirror)   │    │  (ZFS Mirror)   │
└─────────────────┘    └─────────────────┘
```

**Implementation Details**:

```bash
# ZFS Mirror Boot Pool Configuration
zpool create -o ashift=12 \
  -O compression=lz4 \
  -O atime=off \
  -O relatime=on \
  rpool mirror /dev/sda /dev/sdb

# Proxmox Installation on Mirrored Boot
pve-install --target-hd /dev/sda,/dev/sdb \
  --filesystem zfs \
  --zfs-raid mirror
```

**Benefits**:

- **Zero downtime** boot drive failures
- **Automatic failover** to healthy drive
- **Smaller, faster SSDs** improve boot and system performance
- **Reduced maintenance** overhead and emergency interventions

### 5. Caddy Reverse Proxy for Media Services

**Problem**: Current Jellyfin media server setup lacks proper SSL termination, load balancing, and security features, resulting in:

- **Insecure HTTP connections** for remote access
- **No centralized authentication** or access control
- **Poor performance** for multiple concurrent streams
- **Limited monitoring** and logging capabilities

**Solution**: Deploy Caddy as a reverse proxy frontend for media services.

**Caddy Configuration**:

```caddyfile
# Jellyfin Media Server Proxy
jellyfin.home.mcgarrah.org {
    reverse_proxy 192.168.86.29:8096 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
    
    # Security headers
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
    
    # Rate limiting for API endpoints
    rate_limit {
        zone jellyfin_api {
            key {remote_host}
            events 100
            window 1m
        }
        match /api/*
    }
    
    # Logging for monitoring
    log {
        output file /var/log/caddy/jellyfin.log
        format json
    }
}

# Additional media services (planned)
sonarr.home.mcgarrah.org {
    reverse_proxy 10.10.10.51:8989
    basicauth {
        admin $2a$14$hashed_password
    }
}

radarr.home.mcgarrah.org {
    reverse_proxy 10.10.10.52:7878
    basicauth {
        admin $2a$14$hashed_password
    }
}
```

**Security and Performance Features**:

- **Automatic HTTPS** with Let's Encrypt certificates
- **HTTP/2 and HTTP/3** support for improved performance
- **Rate limiting** to prevent abuse
- **Access logging** for security monitoring
- **Basic authentication** for admin interfaces

## Implementation Timeline

### Phase 1: Network Foundation (Weeks 1-2)

1. **GL-iNet Brume 2 deployment** at both locations
2. **Site-to-site VPN** configuration and testing
3. **Routing table updates** for cross-site connectivity

### Phase 2: Core Infrastructure (Weeks 3-4)

1. **ProCurve switch replacement** (HP ProCurve 2810 for SAN, HP ProCurve 2824 for primary) with staged migration
2. **Network performance validation** and optimization
3. **VLAN reconfiguration** for improved segmentation

### Phase 3: Compute Reliability (Weeks 5-6)

1. **Proxmox boot drive upgrades** - one node at a time
2. **ZFS mirror configuration** and testing
3. **Cluster stability validation** and failover testing

### Phase 4: Service Enhancement (Weeks 7-8)
1. **Tailscale upgrade** and DNS reconfiguration

2. **Caddy proxy deployment** for media services
3. **SSL certificate automation** and security hardening

## Expected Performance Improvements

### Network Throughput

- **10x improvement** in backbone port speed (100Mb → 1GbE) with HP ProCurve 2824
- **LACP bonding** for aggregate bandwidth and link redundancy on both networks
- **Consistent site-to-site** connectivity with GL-iNet Brume 2 WireGuard VPN (300-355 Mbps per spoke)
- **Eliminated Netgear hangs** — managed HP ProCurve switches don't need periodic reboots

### Reliability Metrics

- **99.9% uptime** target with redundant boot drives
- **Zero-downtime** boot drive maintenance
- **Automated failover** for critical services

### Security Enhancements

- **End-to-end encryption** for all site-to-site traffic
- **Centralized SSL termination** with automatic certificate renewal
- **Enhanced monitoring** and logging for security events

## Risk Mitigation

### Backup Plans

- **Configuration backups** before each upgrade phase
- **Rollback procedures** documented for each component
- **Emergency access** methods for remote troubleshooting

### Testing Strategy

- **Staged implementation** to minimize service disruption
- **Performance benchmarking** before and after upgrades

- **Failover testing** for all redundant systems

### Monitoring and Validation

- **Network performance monitoring** with PRTG
- **Service health checks** with Uptime Kuma
- **Log aggregation** with centralized syslog

## Conclusion

These infrastructure upgrades address fundamental limitations that have been constraining my homelab's capabilities. While the investment in time and hardware is significant, the improvements in reliability, performance, and security will provide a solid foundation for future projects and experiments.

The systematic approach—starting with network foundation, then core infrastructure, compute reliability, and finally service enhancement—ensures that each phase builds upon the previous improvements while minimizing disruption to ongoing operations.

**Key Success Metrics**:

- **Network redundancy** with LACP bonding and 10x port speed upgrade on primary network
- **System uptime** improved to 99.9% with redundant boot drives
- **Eliminated Netgear reliability issues** — no more 4-6 month reboot cycles on SAN
- **Site connectivity** across all 5 family locations via WireGuard VPN
- **Security posture** enhanced with proper SSL termination and monitoring

This upgrade cycle represents a maturation of the homelab from a collection of individual systems to a cohesive, enterprise-grade infrastructure that can support more ambitious projects and provide reliable services for daily use.

*Next up: Documenting the GL-iNet Brume 2 configuration process and performance benchmarking results as the implementation progresses.*
