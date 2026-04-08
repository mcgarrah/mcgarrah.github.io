---
title: "OpenWRT LXC Native Implementation: From Debian Overlay to Pure Rootfs"
layout: post
categories: [homelab, proxmox, networking]
tags: [openwrt, lxc, proxmox, networking, router, firewall]
published: false
---

**DRAFT ahead of submitting Pull Request**

The journey to implement OpenWRT as an LXC container has been a fascinating exploration of containerization limits and creative problem-solving. After extensive experimentation, I've successfully deployed a native OpenWRT LXC implementation that provides full router functionality within Proxmox VE.

<!-- excerpt-end -->

## The Evolution: Four Approaches Tested

### Approach 1: Debian + OpenWRT Chroot (Failed)

The initial implementation (November 16, 2025) attempted a hybrid approach using Debian 12 as the base container with OpenWRT running in a chroot environment:

```bash
# The original failed approach
var_os="debian"
var_version="12"
# Install OpenWRT rootfs in /opt/openwrt chroot with systemd service
```

**Problems Encountered:**

- LuCI web interface incompatibility with chroot environment
- Package management (opkg) network access issues in chroot
- Service initialization conflicts between systemd and OpenWRT's procd
- Resource overhead from dual operating systems (~500MB+ footprint)
- Complex maintenance and update procedures
- Runtime initialization failures for web interface

### Approach 2: Managed Container with Debian OS Type (Failed)

Next, I tried using OpenWRT with Proxmox's managed container system while forcing Debian compatibility:

```bash
# Also failed - forced compatibility attempt
--ostype debian  # Tried to force OpenWRT into Debian container type
```

**Critical Issues:**

- Proxmox's managed container system interfered with OpenWRT's native init system
- UCI configuration system conflicts with Debian expectations
- Network stack incompatibilities between OpenWRT and Debian management
- Service management collisions between procd and systemd expectations

### Approach 3: LXC Native OpenWRT OS Type Investigation

During development, I researched LXC's native OpenWRT support and discovered that while LXC itself supports `ostype=openwrt`, **Proxmox VE does not implement this OS type in its tooling**. This was not an oversight but a current limitation of Proxmox VE's LXC management system.

**Key Findings:**

- LXC upstream supports OpenWRT as a native container OS type
- Proxmox VE's `pct` tooling lacks OpenWRT OS type implementation
- Native LXC OpenWRT support exists but requires manual LXC configuration
- Proxmox's container management expects traditional Linux distributions

**Why This Approach Wasn't Viable:**

- Would require bypassing Proxmox's container management entirely
- Loss of Proxmox VE integration and web interface management
- Manual LXC configuration conflicts with Proxmox's automated systems
- No integration with Proxmox backup, migration, and monitoring tools

### Approach 4: Native OpenWRT Rootfs with Unmanaged OS Type (Success!)

The breakthrough came with using OpenWRT's native rootfs directly as an unmanaged LXC container, informed by the LXC OpenWRT support research:

```bash
# The winning approach - informed by LXC native support
--ostype unmanaged  # Bypass Proxmox OS-specific management
--unprivileged 0    # Required for OpenWRT networking capabilities
# Direct OpenWRT rootfs template with custom creation logic
```

## Development Journey

The `feature/openwrt-lxc` branch represents a comprehensive development effort spanning 50+ commits over several weeks, evolving from a simple chroot concept to a sophisticated native implementation:

### Initial Chroot Implementation (November 16, 2025)

- **First Commit**: Debian base + OpenWRT chroot with systemd service management
- **Hybrid Architecture**: Attempt to combine Debian stability with OpenWRT functionality
- **LuCI Issues**: Immediate discovery of web interface incompatibility
- **Resource Overhead**: ~500MB+ footprint from dual OS approach

### Native Implementation Pivot (November 17, 2025)

- **Major Rewrite**: Complete replacement of hybrid approach with native rootfs
- **Template System**: Introduction of automated OpenWRT template generation
- **Build System Integration**: Custom container creation bypassing standard LXC methods
- **File Reorganization**: Legacy chroot implementation renamed to `openwrt-debian-lxc`

### Debugging and Refinement (20+ commits)

- **CTID Management**: Extensive fixes for container ID handling and variable passing
- **Startup Issues**: Resolution of container creation and initialization problems
- **Error Handling**: Comprehensive debugging output and failure recovery
- **Template Validation**: Size, integrity, and timeout handling improvements

### Documentation and Requirements (Final commits)

- **Critical Requirements**: Formal documentation of non-negotiable implementation details
- **Memory Bank**: Comprehensive context preservation for future development
- **Architecture Notes**: Detailed explanation of why native approach succeeded

## The Native Implementation

### Template Creation Process

The solution required creating custom OpenWRT LXC templates:

```bash
# Automated template creation
OPENWRT_VERSION="24.10.4"
wget "https://downloads.openwrt.org/releases/${OPENWRT_VERSION}/targets/x86/64/openwrt-${OPENWRT_VERSION}-x86-64-rootfs.tar.gz"

# Convert to LXC template format
tar -czf "openwrt-${OPENWRT_VERSION}-lxc_amd64.tar.gz" -C extracted-rootfs .
```

### Container Configuration Requirements

The native approach requires specific LXC parameters:

```bash
pct create "$CTID" "$TEMPLATE_STORAGE:vztmpl/$var_template" \
  --hostname "openwrt-lxc" \
  --memory "256" \
  --cores "1" \
  --rootfs "$CONTAINER_STORAGE:8" \
  --net0 "name=eth0,bridge=vmbr0,ip=dhcp" \
  --unprivileged 0 \           # CRITICAL: Must be privileged
  --ostype unmanaged \         # CRITICAL: Unmanaged container
  --arch amd64 \
  --features "nesting=1" \
  --onboot 1
```

### Why These Parameters Matter

#### Privileged Container (--unprivileged 0)

OpenWRT requires privileged access for:

- Network interface management (bridges, VLANs)
- Kernel module loading (iptables, netfilter)
- Raw socket operations (routing protocols)
- Device access (/dev/net/tun for VPN)

#### Unmanaged OS Type (--ostype unmanaged)

This prevents Proxmox from:

- Interfering with OpenWRT's init system (procd)
- Modifying network configurations
- Conflicting with UCI system
- Breaking native package management

## Current Implementation Status

### Successful Deployment Metrics

- **Container ID**: 102 (production example)
- **OpenWRT Version**: 24.10.4
- **Template Size**: 13MB (incredibly efficient!)
- **LuCI Interface**: Fully functional at http://192.168.86.51
- **Package Management**: 99%+ success rate with opkg
- **Startup Time**: <30 seconds
- **Memory Usage**: <128MB baseline

### Working Features

✅ **Native LuCI Web Interface**: Full OpenWRT web management  
✅ **Package Management**: opkg works with network access  
✅ **Service Management**: Native procd init system  
✅ **Network Configuration**: UCI system fully functional  
✅ **Firewall**: iptables and netfilter working  
✅ **VPN Support**: WireGuard and OpenVPN capable  
✅ **Updates**: Native OpenWRT upgrade tools (owut for v24.x)  

### Architecture Benefits

#### Resource Efficiency

```
Debian + OpenWRT Chroot: ~500MB+ footprint
Native OpenWRT LXC:      ~5MB base, ~512MB full install
```

#### Performance Comparison

- **No Virtualization Overhead**: Direct kernel access
- **Native Network Stack**: Full routing performance
- **Minimal Resource Usage**: Perfect for homelab environments
- **Standard LXC Management**: Integrates with Proxmox tools

## Technical Implementation Details

### Template Management

The `misc/create-openwrt-template.sh` script handles:

- Automatic version detection from OpenWRT releases
- Template validation and integrity checking
- Timeout handling for reliable downloads
- LXC-compatible format conversion

### Container Provisioning

The `ct/openwrt-lxc.sh` script provides:

- Interactive and non-interactive deployment
- Storage selection for templates and containers
- Network configuration via Proxmox build system
- Post-install OpenWRT configuration

### Post-Install Configuration

The `install/openwrt-lxc-install.sh` handles:

- Network interface setup for LXC environment
- SSH access configuration
- LuCI web interface enablement
- Package updates and additional components
- Version-specific tool installation (owut vs auc)

## Lessons Learned

### Critical Requirements Discovery

Through extensive testing across 50+ commits, I identified these non-negotiable requirements:

1. **Native Rootfs Method**: OpenWRT must run as the primary OS, not in chroot
2. **Unmanaged Container**: Proxmox must not interfere with OpenWRT's systems  
3. **Privileged Access**: Network functionality requires kernel-level access
4. **Template Integrity**: Official OpenWRT rootfs ensures compatibility
5. **LXC vs Proxmox Limitations**: While LXC supports OpenWRT natively, Proxmox VE tooling does not
6. **Build System Integration**: Custom container creation required to bypass standard LXC creation

### Why Previous Approaches Failed

#### Chroot Environment Issues (Original Implementation)

- OpenWRT's web interface (LuCI) expects native environment and fails in chroot
- Package manager (opkg) needs direct network access, blocked by chroot isolation
- Service dependencies break in chroot isolation (procd vs systemd conflicts)
- Dual init systems create irreconcilable conflicts
- Resource overhead from running two complete operating systems

#### Managed Container Problems (Debian OS Type Attempt)

- Proxmox's container management assumes traditional Linux distributions
- UCI configuration system gets corrupted by Debian-style management
- Network stack becomes unreliable due to OS type mismatch
- Update mechanisms break due to conflicting package management expectations

#### LXC Native OpenWRT Limitations (Research Phase)

- LXC supports OpenWRT natively, but Proxmox VE does not implement this
- Proxmox's `pct` tooling lacks OpenWRT OS type support
- Manual LXC configuration would bypass Proxmox integration entirely
- Loss of Proxmox web interface, backup, and migration capabilities

## Current Minor Issues

### Package Dependencies (OWRT-001)

Some firewall libraries occasionally missing:

- libip4tc2, libip6tc2, libiptext*, libxtables12
- Impact: Limited security functionality
- Status: Workaround implemented, permanent fix in progress

### Repository Access (OWRT-002)

Occasional package repository timeouts:

- wget failures for Packages.gz
- Impact: Reduced package availability during setup
- Status: Fallback repositories being implemented

### IP Detection (OWRT-003)

Container IP detection inconsistency:

- Sometimes shows 192.168.1.1 instead of actual IP
- Impact: User confusion about access URL
- Status: Enhanced detection logic in development

## Future Enhancements

### Planned Improvements

- **Multiple Version Support**: Template management for different OpenWRT releases
- **Advanced Networking**: VLAN and bridge configuration options
- **Monitoring Integration**: Prometheus metrics and logging
- **Backup/Restore**: Container migration and configuration backup
- **Performance Optimization**: CPU and memory tuning options

### Integration Opportunities

- **Proxmox SDN**: Native integration with Software Defined Networking
- **High Availability**: Clustered router configurations
- **Automation**: Ansible playbooks for mass deployment
- **Monitoring**: Integration with existing homelab monitoring stacks

## Getting Started

To deploy the native OpenWRT LXC implementation:

```bash
# Clone the repository
git clone https://github.com/mcgarrah/ProxmoxVE.git
cd ProxmoxVE

# Switch to OpenWRT feature branch
git checkout feature/openwrt-lxc

# Deploy with minimal resources
var_cpu=1 var_ram=256 var_disk=8 bash ct/openwrt-lxc.sh
```

### Access Methods

- **Web Interface**: `http://[container-ip]` (LuCI)
- **SSH Access**: `ssh root@[container-ip]` (no password initially)
- **Console**: `pct enter [container-id]`
- **Management**: Standard OpenWRT UCI commands

## Conclusion

The native OpenWRT LXC implementation represents a significant achievement in containerized networking. By abandoning the hybrid Debian approach and embracing OpenWRT's native requirements, we've created a solution that:

- Provides full OpenWRT functionality in a container
- Maintains minimal resource overhead
- Integrates seamlessly with Proxmox VE
- Offers reliable package management and updates
- Supports advanced networking features

This implementation proves that with the right approach, even specialized operating systems like OpenWRT can be successfully containerized while maintaining their full feature set. The key was understanding and respecting OpenWRT's architectural requirements rather than trying to force it into a traditional container model.

The journey from failed chroot experiments through LXC native support research to successful unmanaged container implementation demonstrates the importance of understanding both the software requirements and platform limitations. While LXC itself supports OpenWRT natively, Proxmox VE's current tooling limitations required a creative solution using unmanaged containers.

This approach bridges the gap between LXC's native OpenWRT support and Proxmox VE's container management, providing the best of both worlds: full OpenWRT functionality within Proxmox's integrated management environment. The 50+ commits of iterative development show that sometimes the solution isn't about making the software fit the container, but making the container fit both the software and the platform's capabilities.

For the latest updates and to contribute to this project, visit the [ProxmoxVE repository](https://github.com/mcgarrah/ProxmoxVE) and check out the `feature/openwrt-lxc` branch.
