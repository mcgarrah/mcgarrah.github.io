---
layout: post
title: "Optimizing Jellyfin on Proxmox: Moving Metadata to CephFS and Shrinking LXC Footprints"
date: 2026-02-04
categories: [homelab, proxmox, jellyfin, ceph]
tags: [proxmox, jellyfin, cephfs, lxc, storage, high-availability, virtualization]
excerpt: "A comprehensive guide to resolving Jellyfin LXC disk space issues by migrating metadata to CephFS and optimizing container size for faster HA failovers."
published: true
---

When your Jellyfin LXC container hits 95% disk usage, it's more than just a storage problem—it's an architectural opportunity. This guide documents the journey from a disk space crisis to a scalable, high-availability media server configuration using Proxmox 8.4.16 and CephFS.

<!-- excerpt-end -->

## The Problem: When 22GB Isn't Enough

My Jellyfin LXC container on Proxmox filled its 22GB root filesystem to 95% capacity. I have expanded this rootfs twice so far and cleared out the `/var/logs` a few times along with limiting log sizes. The major culprits for Jellyfin were predictable but substantial:

- `/var/lib/jellyfin/metadata`: 7.2GB (movie posters, actor photos, chapter images)
- `/var/cache/jellyfin/images`: 3.6GB (cached thumbnails and artwork)
- `/var/lib/jellyfin/data`: 1.9GB (database and library information)

Total: ~12GB of media metadata consuming over half the container's storage. For those trying to calculate my media library size, it is about 10Tib pulled from VHS, DVDs, and BluRays.

This is also an issue as I want the LXC to be HA across nodes in the Proxmox Cluster. The large size of the `rootfs` mean transitions take longer between nodes during a migration. So this also factors into this issue.

## The Solution: Architectural Separation

The fix involves separating concerns:

- **RootFS (RBD)**: OS, binaries, and configs (~4-8GB)
- **Bulk Data (CephFS)**: Metadata, cache, and growing data

This approach provides:

- Unlimited metadata growth without resizing containers
- Faster HA failovers with smaller root disks
- Better resource utilization across the Ceph cluster

## Phase 1: Immediate Triage

Before architectural changes, free up immediate space:

```bash
# Clear package cache
apt-get clean
apt-get autoremove

# Analyze disk usage
du -sh /var/lib/jellyfin/* | sort -h

# Find largest files
find / -type f -printf '%s %p\n' | sort -nr | head -10

# Clear transcode temp files (safe to delete)
rm -rf /var/lib/jellyfin/transcoding-temp/*
```

### Taming systemd Journal Logs

Systemd journals can grow to 600MB+ over time. Set permanent limits:

```bash
# Clean current logs
journalctl --vacuum-size=100M

# Set permanent limits
echo "SystemMaxUse=200M" >> /etc/systemd/journald.conf
echo "SystemMaxFileSize=50M" >> /etc/systemd/journald.conf

# Restart journald
systemctl restart systemd-journald
```

I need to add observability to my cluster to retain useful logs in a central location. But that is something for later.

### Interactive Disk Analysis

For interactive exploration, install `ncdu`:

```bash
apt-get update && apt-get install ncdu -y
ncdu /var/lib/jellyfin /var/cache/jellyfin
```

## Understanding Unprivileged LXC Permissions

Before diving into the migration, understanding how unprivileged containers handle permissions is critical. This is the foundation that makes the entire solution work.

### The UID/GID Mapping Challenge

Unprivileged LXCs use subuid and subgid mappings to isolate container processes from the host. Without custom mappings, Proxmox adds 100000 to every container UID:

- Container UID 0 → Host UID 100000
- Container UID 501 → Host UID 100501

This creates a "permissions gap" when using shared storage like CephFS.

### Creating Dedicated CephFS Service Accounts

On the Proxmox host, I created dedicated service accounts for CephFS access:

```bash
# Create group for media access
groupadd -g 501 cephfs-media

# Create read-write user
useradd -u 501 -g 501 -s /usr/sbin/nologin cephfs-rw

# Create read-only user (shares same group)
useradd -u 502 -g 501 -s /usr/sbin/nologin cephfs-ro
```

This gives us:

- `cephfs-rw` (UID 501, GID 501): Write access for services like Jellyfin
- `cephfs-ro` (UID 502, GID 501): Read-only access for media consumption
- `cephfs-media` (GID 501): Shared group for all media services

### Configuring subuid and subgid

To allow containers to use these host UIDs, update `/etc/subuid` and `/etc/subgid`:

```bash
# /etc/subuid
root:100000:65536    # Standard range for container UIDs
root:501:2           # Direct passthrough for cephfs-rw and cephfs-ro

# /etc/subgid  
root:100000:65536    # Standard range for container GIDs
root:501:1           # Direct passthrough for cephfs-media group
```

These entries give Proxmox permission to "pass through" specific host UIDs to containers.

### The LXC ID Mapping

The LXC configuration uses these ranges to create a bridge between container and host:

```conf
lxc.idmap: u 0 100000 5001      # Map UIDs 0-5000 to host 100000-105000
lxc.idmap: g 0 100000 5001      # Map GIDs 0-5000 to host 100000-105000
lxc.idmap: u 5001 501 1         # Map container UID 5001 to host UID 501
lxc.idmap: g 5001 501 1         # Map container GID 5001 to host GID 501
lxc.idmap: u 5002 105002 60534  # Map remaining UIDs
lxc.idmap: g 5002 105002 60534  # Map remaining GIDs
```

This creates a "trusted path" where:

1. Files owned by host UID 501 (`cephfs-rw`) are accessible inside the container
2. The container can write to CephFS with proper permissions
3. Security isolation is maintained for other UIDs

### Security Consideration

Multiple containers using the same `root:501:2` mapping will share access to CephFS files. This is beneficial for a media stack (Jellyfin, Sonarr, Radarr) but important to understand for security isolation.

## Phase 2: Preparing CephFS Storage

With the permission foundation in place, create the directory structure on the Proxmox host:

```bash
# Create CephFS directories
mkdir -p /mnt/pve/cephfs/jellyfin/metadata
mkdir -p /mnt/pve/cephfs/jellyfin/cache
mkdir -p /mnt/pve/cephfs/jellyfin/lib_data

# Set ownership to cephfs-rw user (UID 501)
chown -R 501:501 /mnt/pve/cephfs/jellyfin
chmod -R 775 /mnt/pve/cephfs/jellyfin
```

Note: We use UID 501 directly (not 100501) because the LXC idmap configuration handles the translation.

## Phase 3: The Migration Process

### Step 1: Disable Jellyfin Service

Critical step to prevent startup failures during migration:

```bash
systemctl stop jellyfin
systemctl disable jellyfin
```

Why disable instead of just stop? If the container reboots unexpectedly during migration, Jellyfin won't start with empty directories and create a blank database. Ask me how I know this?!?

### Step 2: Stage the Data

Move data to temporary location before mount points hide it:

```bash
mkdir -p /migration_temp
mv /var/lib/jellyfin/metadata /migration_temp/
mv /var/lib/jellyfin/data /migration_temp/
mv /var/cache/jellyfin /migration_temp/cache

# Shutdown container
poweroff
```

### Step 3: Configure Mount Points

Edit `/etc/pve/lxc/501.conf` on the Proxmox host:

```conf
mp0: /mnt/pve/cephfs/jellyfin/metadata,mp=/var/lib/jellyfin/metadata,shared=1
mp1: /mnt/pve/cephfs/jellyfin/cache,mp=/var/cache/jellyfin,shared=1
mp2: /mnt/pve/cephfs/jellyfin/lib_data,mp=/var/lib/jellyfin/data,shared=1
```

The `shared=1` flag is essential for CephFS mounts in HA clusters—it tells Proxmox this storage can be accessed by multiple nodes during migration. Adding this required the command line as I could not find this in the Proxmox GUI.

### Step 4: Verify Mounts

Start the LXC and verify before moving data:

```bash
# Check mounts are active
mount | grep jellyfin

# Test write permissions
touch /var/lib/jellyfin/metadata/perm_test && rm /var/lib/jellyfin/metadata/perm_test
```

If the touch command fails with "Permission Denied," verify the host-side ownership is set to UID 501.

### Step 5: Migrate Data

Use rsync to preserve permissions and provide progress:

```bash
# Sync data to CephFS mounts
rsync -avP /migration_temp/metadata/ /var/lib/jellyfin/metadata/
rsync -avP /migration_temp/data/ /var/lib/jellyfin/data/
rsync -avP /migration_temp/cache/ /var/cache/jellyfin/

# Fix ownership inside container
chown -R jellyfin:jellyfin /var/lib/jellyfin/metadata
chown -R jellyfin:jellyfin /var/lib/jellyfin/data
chown -R jellyfin:jellyfin /var/cache/jellyfin
```

### Understanding rsync Progress

The rsync output shows cryptic status indicators:

- **xfr#**: Transfer count—how many files have been physically copied
- **ir-chk=N/M**: Incremental check—N files remaining to check out of M total discovered

For metadata migrations with thousands of small files, expect the ir-chk number to count down slowly. The bottleneck is file creation latency on CephFS, not network bandwidth.

### Step 6: Re-enable Service

```bash
systemctl enable jellyfin
systemctl start jellyfin

# Verify service status
systemctl status jellyfin
journalctl -u jellyfin -f
```

### Step 7: Cleanup

Once Jellyfin is running correctly and you've verified all media libraries are accessible:

```bash
rm -rf /migration_temp
```

Verify the migration freed up space:

```bash
df -h /
```

## Phase 4: Shrinking the Root Disk

With ~12GB moved to CephFS, the root disk now uses less than 4GB. Shrinking to 8GB improves HA migration speed. Smaller here is faster migration times.

### The Backup/Restore Method

Proxmox doesn't support live shrinking, but backup/restore is safe:

1. In Proxmox GUI: Select Jellyfin LXC → Backup → Backup Now
2. Once complete: Select backup → Restore
3. In Restore Options:
   - Set Root Disk size to 8G
   - Choose new ID to test first, or overwrite existing
4. Start restored LXC and verify functionality

### Why 8GB?

With system files and binaries using 2-3GB, 8GB provides:

- Comfortable overhead for OS updates
- Faster HA failover (smaller disk to migrate)
- Reduced storage consumption on Ceph RBD pool

## Final LXC Configuration

The optimized configuration:

```conf
arch: amd64
cores: 2
dev0: /dev/dri/card0,gid=44
dev1: /dev/dri/renderD128,gid=104
features: keyctl=1,nesting=1
hostname: jellyfin
memory: 2048
mp0: /mnt/pve/cephfs/jellyfin/metadata,mp=/var/lib/jellyfin/metadata,shared=1
mp1: /mnt/pve/cephfs/jellyfin/cache,mp=/var/cache/jellyfin,shared=1
mp2: /mnt/pve/cephfs/jellyfin/lib_data,mp=/var/lib/jellyfin/data,shared=1
mp3: /mnt/pve/cephfs/movies,mp=/mnt/media/movies,ro=1,shared=1
net0: name=eth0,bridge=vmbr0,hwaddr=BC:24:11:23:DB:1E,ip=dhcp,type=veth
onboot: 1
ostype: ubuntu
protection: 0
rootfs: cephrbd:vm-501-disk-0,size=8G
swap: 512
tags: community-script;media
unprivileged: 1
lxc.idmap: u 0 100000 5001
lxc.idmap: g 0 100000 5001
lxc.idmap: u 5001 501 1
lxc.idmap: g 5001 501 1
lxc.idmap: u 5002 105002 60534
lxc.idmap: g 5002 105002 60534
```

## Key Takeaways

1. **Separate concerns**: Keep OS on RBD, data on CephFS
2. **Disable services**: Prevent startup failures during migrations
3. **Use shared=1**: Essential for CephFS mounts in HA clusters
4. **Mind the UID mapping**: Unprivileged containers require careful permission management
5. **Shrink after migration**: Smaller root disks improve HA performance

## Benefits Achieved

- **Unlimited growth**: Metadata can expand without container resizing
- **Faster HA failovers**: 8GB root disk migrates much faster than 22GB
- **Better stability**: No more 95% disk warnings
- **Maintained compatibility**: Jellyfin sees standard paths, upgrades work normally

## Performance Considerations

CephFS is network-based storage, so expect:

- Slight delay in poster loading compared to local RBD
- Higher I/O operations for thousands of small files
- Potential MDS (metadata server) load during library scans

On Proxmox 8.4.16 with decent networking (10GbE or better), these impacts are typically negligible for home media server use. With my 1GbE SAN it is not noticeable even with multiple TV clients running at the same time.

## Troubleshooting

If Jellyfin fails to start after migration:

```bash
# Check mount status
mount | grep jellyfin

# Verify permissions
ls -la /var/lib/jellyfin/metadata

# Check service logs
journalctl -u jellyfin -n 50

# Test database access
sudo -u jellyfin touch /var/lib/jellyfin/data/test
```

Common issues:

- **Permission denied**: Verify host-side ownership is set to UID 501 and LXC idmap is configured correctly
- **Empty library**: Data not moved before enabling service
- **Database locked**: CephFS mount not using shared=1 flag

## Conclusion

What started as a disk space crisis became an opportunity to build a more scalable architecture. By leveraging CephFS for growing data and keeping the OS lean on RBD, the Jellyfin LXC is now optimized for both capacity and high availability.

This pattern applies to any LXC service with growing data requirements—separate the static (OS) from the dynamic (data) for better resource utilization and operational flexibility.

## References

- [Proxmox LXC Documentation](https://pve.proxmox.com/wiki/Linux_Container)
- [Proxmox Unprivileged LXC](https://pve.proxmox.com/wiki/Unprivileged_LXC_containers)
- [CephFS Best Practices](https://docs.ceph.com/en/latest/cephfs/)
- [Jellyfin Documentation](https://jellyfin.org/docs/)
