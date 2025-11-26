---
title: "Homelab Storage Economics: Ceph vs Single Drive Costs"
layout: post
categories: [homelab, storage]
tags: [ceph, storage, costs, homelab, economics, backup]
published: true
---

After building and running a Ceph cluster for my homelab, I've gained valuable insights into the real-world economics of distributed storage versus traditional single-drive solutions. This analysis breaks down the actual costs per GB across different storage strategies in my setup.

<!-- excerpt-end -->

## My Current Storage Architecture

My homelab storage consists of three distinct tiers:

- **Ceph Cluster**: 15 × 5TB OSDs across 5 nodes (3 OSDs per node)
- **Primary Backup**: 20TB external drive for CephFS backups
- **Secondary Storage**: 28TB external drive for expanded backup capacity

Each tier serves different purposes and has dramatically different cost profiles when you factor in redundancy and usable capacity.

## Ceph Cluster Economics

### The Drive Acquisition Story

Building a 15-drive Ceph cluster happened in phases, with costs varying significantly based on timing and sourcing:

**Early Drives (Costco Special)**

- **Quantity**: 6-7 drives
- **Cost**: $89 each (Costco special pricing)
- **Cost per TB**: $17.80/TB

**Later Drives (Amazon/Seagate Sales)**

- **Quantity**: 8-9 drives  
- **Average Cost**: ~$110 each (sale pricing)
- **Cost per TB**: $22.00/TB

**Most Recent Drive**

- **Model**: Seagate Portable 5TB (STGX5000400)
- **Cost**: $109.99 (October 2025)
- **Cost per TB**: $22.00/TB

### Ceph Storage Math

**Raw Capacity**: 15 × 5TB = 75TB
**Total Investment**: ~$1,500 (averaging $100/drive)
**Raw Cost per TB**: $20.00/TB

**With 3/2 Erasure Coding**:

- **Usable Capacity**: ~50TB (66.7% efficiency)
- **Effective Cost per Usable TB**: $30.00/TB
- **Redundancy**: Can lose 1 drive per erasure group
- **Performance**: Distributed I/O across 15 spindles

### Ceph Advantages Beyond Cost

- **Fault Tolerance**: Automatic recovery from drive failures
- **Scalability**: Add capacity by adding nodes/drives
- **Performance**: Parallel I/O across multiple drives
- **Network Storage**: CephFS accessible from any node
- **Snapshots**: Built-in snapshot capabilities
- **Self-Healing**: Automatic data integrity checking

## Backup Storage Economics

### 20TB Primary Backup Drive

**Model**: Avolusion PRO-X 20TB
**Purchase Date**: June 16, 2024
**Cost**: $219.99
**Cost per TB**: $11.00/TB
**Usage**: ZFS volume for rsync backups of entire CephFS

**Key Insight**: This single drive can backup my entire 50TB usable Ceph capacity, demonstrating the storage efficiency of the cluster.

### 28TB Secondary Storage

**Model**: Seagate Expansion 28TB (STKP28000400)
**Purchase Date**: November 21, 2025
**Cost**: $289.99
**Cost per TB**: $10.36/TB
**Planned Usage**: Primary backup volume, with 20TB becoming off-site mirror

## Cost Comparison Analysis

| Storage Type | Raw Cost/TB | Usable Cost/TB | Redundancy | Performance |
|--------------|-------------|----------------|------------|-------------|
| **Ceph Cluster** | $20.00 | $30.00 | Built-in (3/2) | High (15 drives) |
| **20TB Backup** | $11.00 | $11.00 | None | Single drive |
| **28TB Backup** | $10.36 | $10.36 | None | Single drive |

### The Redundancy Tax

Ceph's redundancy comes at a 50% capacity penalty, effectively doubling the cost per usable TB. However, this "tax" provides:

- **Automatic failover** during drive failures
- **No data loss** from single drive failures  
- **No downtime** for drive replacements
- **Performance benefits** from distributed I/O

### Backup Drive Efficiency

The backup drives show the true efficiency of the Ceph cluster - 50TB of usable data compresses well enough that a 20TB drive can hold complete backups. This suggests:

- **Compression ratios** of 2.5:1 or better
- **Deduplication benefits** from similar VM/container images
- **Efficient backup strategies** using incremental rsync

## Real-World Storage Costs

### Total Storage Investment

- **Ceph Cluster**: ~$1,500 (75TB raw, 50TB usable)
- **Backup Drives**: $510 (48TB total)
- **Total Investment**: ~$2,010
- **Total Usable**: 98TB (50TB + 48TB)
- **Blended Cost**: $20.51/TB

### Operational Considerations

**Power Consumption**:

- Ceph: 15 drives × 8W = 120W continuous
- Backup drives: Powered only during backup operations
- Annual power cost difference: ~$100-150

**Maintenance**:

- Ceph: Occasional drive replacements, cluster maintenance
- Backup drives: Manual backup scheduling, drive rotation

## Lessons Learned

### 1. Timing Matters for Drive Purchases

The $89 Costco drives versus $110+ regular pricing shows a 24% cost difference. Patience and deal hunting significantly impact total cluster cost.

### 2. Redundancy Has Real Costs

Ceph's 3/2 erasure coding provides excellent protection but at a 50% capacity penalty. For homelab use, this trade-off provides peace of mind worth the cost.

### 3. Backup Drives Provide Excellent Value

Large external drives offer the best $/TB ratio and serve as an excellent complement to distributed storage for backup purposes.

### 4. Compression Is Your Friend

50TB of Ceph data fitting on a 20TB backup drive demonstrates the value of compression and deduplication in real-world scenarios.

## Future Storage Strategy

### Short Term

- Configure 28TB drive as primary backup volume
- Relocate 20TB drive for off-site backup rotation
- Implement automated backup verification

### Long Term

- Monitor drive prices for Ceph expansion opportunities
- Consider NVMe cache tiers for hot data
- Evaluate backup retention policies based on capacity

## Conclusion

Homelab storage economics involve more than just $/TB calculations. While Ceph costs 3x more per usable TB than backup drives, it provides:

- **Reliability**: No single points of failure
- **Performance**: Distributed I/O capabilities  
- **Convenience**: Always-available network storage
- **Scalability**: Growth path for future needs

The backup drives complement this by providing cost-effective bulk storage for archival and disaster recovery.

**Bottom Line**: For active storage requiring high availability, Ceph's $30/TB is justified. For backup and archival, external drives at $10-11/TB provide excellent value. The combination creates a robust, cost-effective homelab storage solution.

The key insight is that different storage tiers serve different purposes, and optimizing for pure $/TB misses the bigger picture of reliability, performance, and operational simplicity.
