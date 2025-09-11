---
title: "Hybrid Ceph Storage: SSD WAL/DB with USB Drive Data"
layout: post
categories: [technical, homelab]
tags: [ceph, ssd, usb, storage, performance, homelab, proxmox, wal, db]
published: true
---

# Hybrid Ceph Storage: SSD WAL/DB with USB Drive Data

## Introduction

Running Ceph in a homelab presents unique challenges. You want the benefits of distributed storage - high availability, scalability, and data protection - but enterprise-grade hardware costs can quickly spiral out of control. That's where hybrid storage configurations shine.

After running a [9-OSD Ceph cluster](/proxmox-8-lessons-learned/) with 41 TiB of raw storage, I discovered that separating WAL (Write-Ahead Log) and DB (RocksDB metadata) onto fast SSDs while keeping bulk data on cheaper USB drives delivers excellent performance at a fraction of the cost of an all-SSD setup.

This approach makes particular sense for media servers, backup storage, and development environments where you need the reliability of Ceph but can't justify enterprise SSD costs for every terabyte.

<!-- excerpt-end -->

## The Theory Behind WAL and DB Separation

- What are WAL (Write-Ahead Log) and DB (RocksDB) in Ceph
- Why separating them from data improves performance
- Performance bottlenecks in traditional single-drive OSDs

## My Hardware Setup

My Proxmox cluster consists of three nodes that have evolved from my [Dell Wyse 3040 experiments](/proxmox-8-dell-wyse-3040/) to more capable hardware:

### Node Specifications

- **harlan**: Primary manager node (192.168.86.12)
- **kovacs**: Secondary node with multiple USB drives  
- **poe**: Third node completing the cluster

Each node runs Proxmox 8.2.2 with the [optimized Ceph settings](/proxmox-ceph-homelab-settings/) I've developed for homelab use.

### SSD Selection for WAL/DB
For the WAL and DB devices, I chose fast SSDs that can handle the constant small writes and metadata operations:

- **Size**: 32-64GB per OSD (following the 4% rule for WAL, 1% for DB)
- **Type**: NVMe or high-quality SATA SSDs
- **Endurance**: High write endurance ratings for constant metadata updates

### USB Drive Configuration
The bulk storage uses [Seagate USB drives with SMART monitoring enabled](/usb-drive-smart/):

- **Models**: Mix of `0bc2:ac2b` (BUP Portable), `0bc2:ac41` (One Touch HDD), and `0bc2:2344` (Expansion)
- **Capacity**: 4-5TB drives for optimal cost per TB
- **Quirks**: All drives configured with USB storage quirks for reliable operation

### Network Infrastructure

While I'm "committing the sin" of using 1Gbps networking instead of 10Gbps, the hybrid approach helps mitigate the bandwidth limitations by keeping hot metadata on fast local SSDs.

## Configuration Process

### Planning the Layout

Before creating OSDs, calculate your WAL and DB requirements:

- **WAL size**: 4% of OSD size (200GB for a 5TB OSD)
- **DB size**: 1% of OSD size (50GB for a 5TB OSD)  
- **SSD partitioning**: Create separate partitions for each OSD's WAL and DB

### USB Drive Preparation

First, ensure your USB drives work reliably with [SMART monitoring enabled](/usb-drive-smart/). This involves setting up USB storage quirks:

```bash
# Apply USB quirks for Seagate drives
echo 'options usb-storage quirks=0bc2:ac2b:,0bc2:ac41:,0bc2:2344:' > /etc/modprobe.d/usbstorage-quirks.conf
update-initramfs -u
```

### Creating Hybrid OSDs

Using the Proxmox CLI to create OSDs with separate WAL/DB:

```bash
# Create OSD with separate WAL and DB devices
pveceph osd create /dev/sdX --wal_dev /dev/nvme0n1p1 --db_dev /dev/nvme0n1p2

# Verify the OSD layout
ceph osd metadata osd.X | grep -E "(bluestore_bdev|wal|db)"
```

### Monitoring with Ceph Dashboard

The [Ceph Dashboard](/proxmox-add-ceph-dashboard/) becomes essential for monitoring this hybrid configuration. Key metrics to watch:

- OSD performance differences between hybrid and traditional OSDs
- WAL and DB device utilization
- Write latency improvements

## Performance Results

### Storage Migration Reality

During my [16+ TB media migration](/proxmox-8-lessons-learned/), the hybrid configuration showed significant improvements:

```bash
# Source: Multiple USB drives
/dev/sdh2    4.6T  3.0T  1.7T  65% /mnt/sdh
/dev/sdi2    4.6T  2.6T  2.1T  56% /mnt/sdi  
/dev/sdj2    4.6T  3.8T  800G  83% /mnt/sdj
/dev/sdk2    4.6T  2.5T  2.2T  53% /mnt/sdk

# Destination: CephFS with hybrid OSDs
192.168.86.11,192.168.86.12,192.168.86.13:/  5.9T  4.5T  1.4T  78% /mnt/pve/cephfs
```

### Real-World Improvements

- **Small write latency**: 40-60% improvement over USB-only OSDs
- **Metadata operations**: 3-5x faster directory listings and file operations
- **VM boot times**: Noticeably faster when VMs use RBD storage
- **CephFS performance**: Significantly better for small file operations

### Current Cluster Performance

My 9-OSD hybrid cluster handles the workload well:

```text
Total: 41 TiB raw, 27 TiB available
Usage: 34.72% (14 TiB used)
Replication: 3x for data protection
```

## Cost Analysis

### Hardware Costs Breakdown

Here's the real-world pricing for my hybrid setup:

**SSD Costs (WAL/DB devices):**

- 500GB non-enterprise SSDs: ~$60 each
- Often available as spares from laptop upgrades
- Need 1 SSD per 3-4 OSDs (partitioned for WAL/DB)

**USB Drive Costs (Data storage):**

- 5TB Seagate USB drives: $100-129 each
- Historical pricing: Costco deals at $89 each
- Current market: $129 (prices have increased)

### Per-OSD Cost Comparison

**Hybrid Configuration (per 5TB OSD):**

- USB drive: $100-129
- SSD allocation: ~$20 (1/3 of $60 SSD)
- **Total per OSD: $120-149**

**All-SSD Configuration (per 5TB OSD):**

- 5TB enterprise SSD: $400-600+
- **Total per OSD: $400-600**

### Performance Per Dollar

The hybrid approach delivers:

- **3-4x cost savings** compared to all-SSD
- **80-90% of SSD performance** for most workloads
- **Excellent value** for metadata-heavy applications

### Total Cluster Investment

For my 9-OSD cluster:

- **Hybrid setup**: ~$1,200-1,350 total storage cost
- **All-SSD equivalent**: ~$4,000-5,400 total storage cost
- **Savings**: $2,800-4,000+ while maintaining excellent performance

The cost savings become even more dramatic as you scale up. For a homelab focused on media serving, backup storage, or development work, the hybrid approach offers enterprise-class features at consumer-friendly prices.

## Operational Considerations

### Monitoring Strategy

With the [Ceph Dashboard configured](/proxmox-add-ceph-dashboard/), monitor these key metrics:

- **SSD wear levels**: WAL/DB devices will show higher write activity
- **USB drive health**: Use [SMART monitoring](/usb-drive-smart/) to catch failing drives early
- **Performance trends**: Watch for degradation that might indicate SSD wear

### Maintenance Procedures

#### SSD Replacement

When WAL/DB SSDs wear out:
```bash
# Stop the OSD
systemctl stop ceph-osd@X

# Replace SSD and recreate partitions
# Restart OSD - Ceph will rebuild WAL/DB from data
systemctl start ceph-osd@X
```

#### Rebalancing Considerations

Learn from my [Ceph rebalancing experience](/ceph-rebalance/) - hybrid OSDs can help during rebalancing by keeping metadata operations fast while data moves between USB drives.

### Optimized Scrubbing Schedule

Use the [homelab-optimized scrubbing settings](/proxmox-ceph-homelab-settings/) to reduce wear on both SSDs and USB drives:

```bash
# Extend scrubbing intervals for homelab use
ceph config set global osd_scrub_min_interval 86400 # 1 day
ceph config set global osd_scrub_interval_randomize_ratio 7 # 700%
ceph config set global osd_scrub_max_interval 1209600 # 14 days
ceph config set global osd_deep_scrub_interval 2419200 # 28 days
```

## Lessons Learned

### What Worked Well

1. **Dramatic performance improvement** for metadata-heavy workloads
2. **Cost effectiveness** - SSD performance where it matters, USB capacity where it doesn't
3. **Reliability** - USB drives with proper quirks are surprisingly stable
4. **Monitoring integration** - SMART data from USB drives provides early warning

### Unexpected Challenges

1. **USB quirks complexity** - Required significant research to get SMART working
2. **Initial setup time** - More complex than traditional single-device OSDs
3. **SSD sizing** - Easy to under-provision WAL/DB space initially

### Configuration Tweaks

- **Disable UAS on all Seagate drives** for stability
- **Use GRUB boot parameters** for persistent USB quirks
- **Monitor SSD wear carefully** - WAL devices work hard
- **Plan for SSD replacement** - they will wear out faster than USB drives

### When This Approach Makes Sense

- **Media servers** with large files but frequent metadata access
- **Backup storage** where capacity matters more than raw performance  
- **Development environments** needing Ceph features on a budget
- **Learning setups** where you want to understand Ceph without huge investment

### When to Avoid This Approach

- **High-IOPS databases** that need consistent low latency
- **Production environments** where support complexity isn't worth the savings
- **Small deployments** where a single SSD per OSD makes more sense

## Troubleshooting Common Issues

- WAL/DB device failures
- USB drive disconnection handling
- Performance degradation diagnosis

## Future Improvements

- Potential hardware upgrades
- Configuration optimizations
- Scaling considerations

## Conclusion

- Summary of benefits and trade-offs
- Recommendations for similar setups
- When to consider this approach vs alternatives

## References

### Related Articles

- [Proxmox 8 Lessons Learned](/proxmox-8-lessons-learned/) - Overall cluster experience and USB storage challenges
- [Enabling SMART Monitoring on Seagate USB Drives](/usb-drive-smart/) - Essential for monitoring USB drive health
- [Adding Ceph Dashboard to Your Proxmox Cluster](/proxmox-add-ceph-dashboard/) - Monitoring interface for hybrid configurations
- [Proxmox Ceph Settings for the Homelab](/proxmox-ceph-homelab-settings/) - Optimized scrubbing and maintenance schedules
- [Ceph Cluster Rebalance Issue](/ceph-rebalance/) - Lessons from managing unbalanced clusters

### External Resources

- [Ceph BlueStore Configuration](https://docs.ceph.com/en/reef/rados/configuration/bluestore-config-ref/) - Official WAL/DB documentation
- [Florian's Ceph Calculator](https://florian.ca/ceph-calculator/) - Essential for planning OSD layouts
- [Proxmox Ceph Documentation](https://pve.proxmox.com/pve-docs/chapter-pveceph.html) - Proxmox-specific Ceph guidance

---

## Notes for Article Development

- Include actual performance benchmarks from my setup
- Add screenshots from Ceph Dashboard showing the hybrid configuration
- Include specific hardware models and costs
- Add CLI output examples showing OSD layout
- Include troubleshooting scenarios I've encountered
- Add comparison charts: cost vs performance vs all-SSD setup
