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

| Drive | Model | Purchase Date | Cost | Cost/TB | Current Usage |
|-------|-------|---------------|------|---------|---------------|
| **20TB** | Avolusion PRO-X 20TB | June 16, 2024 | $219.99 | $11.00/TB | ZFS volume for CephFS backups |
| **28TB** | Seagate Expansion 28TB (STKP28000400) | November 21, 2025 | $289.99 | $10.36/TB | Planned as primary backup |

### Backup Strategy and Efficiency

The backup drives reveal something fascinating about my Ceph cluster's real-world efficiency. That 20TB drive currently holds complete rsync backups of my entire 50TB usable Ceph capacity, which tells me I'm getting compression ratios of 2.5:1 or better. This isn't just theoretical - it's actual data from VMs, containers, and file storage that compresses remarkably well due to similar base images and redundant content.

My plan is to promote the new 28TB drive to primary backup duty while relocating the 20TB drive for off-site backup rotation. This gives me both local and remote backup coverage at an average cost of $10.68/TB - less than half the cost of the Ceph storage, but without any of the redundancy or performance benefits. It's the perfect complement to the distributed storage: cheap, simple, and effective for disaster recovery scenarios.

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

### The Redundancy Tax vs Backup Value

The backup drives demonstrate why having multiple storage tiers makes sense. While Ceph's redundancy comes at a 50% capacity penalty, the backup drives show the true efficiency of the cluster - 50TB of usable data compresses well enough that a 20TB drive can hold complete backups. This compression comes from:

- **Similar VM/container base images** creating natural deduplication opportunities
- **Incremental rsync strategies** that only backup changed data
- **File-level compression** on the ZFS backup volumes

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

## The Real Story Behind the Numbers

Look, I'll be honest - when I started building this Ceph cluster, I wasn't thinking about cost per TB. I was thinking "this is cool distributed storage technology" and "I want to learn how this works." The economics came later when my wife asked why I needed another 5TB drive.

Turns out the math is actually pretty interesting. Yes, Ceph costs me 3x more per usable TB than just buying big external drives. But here's the thing - when one of those 5TB drives dies (and they will), I don't even notice. The cluster just keeps running. Compare that to the heart attack I'd have if my single 28TB backup drive failed.

The $89 Costco drives were a steal, and I kick myself for not buying more when they were available. But even at $110 each, building this cluster has been worth it for the learning experience alone. Plus, there's something deeply satisfying about having 15 drives working together as one big storage pool.

The backup drives? They're the unsung heroes of this setup. That 20TB drive backing up my entire 50TB Ceph cluster shows just how well compression and deduplication work in the real world. It's like having a safety net that costs $11/TB.

**Bottom Line**: If you're just looking for cheap storage, buy the biggest external drive you can afford. But if you want to learn about distributed systems, have some redundancy, and don't mind paying the "education tax," Ceph is pretty amazing. Just don't tell my wife how much those drives actually cost.

The real lesson here? Different storage serves different purposes. Sometimes you pay for convenience, sometimes for reliability, and sometimes just for the fun of learning something new. In my homelab, all three have their place.
