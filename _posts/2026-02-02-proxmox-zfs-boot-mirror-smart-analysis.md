---
layout: post
title: "Monitoring ZFS Boot Mirror Health in Proxmox 8 Clusters"
date: 2026-02-02
excerpt: "Automated SMART monitoring and cost planning for ZFS boot mirrors across a six-node Proxmox homelab cluster with mixed SSD/HDD hardware. Track drive health, plan replacements, and manage homelab storage costs effectively."
categories: [proxmox, zfs, storage, monitoring]
tags: [proxmox, zfs, smart, storage, cluster, hardware]
published: false
---

<!-- TODO: 

Add script contents from /mnt/pve/cephfs/bin/storage-tests/ before publishing:
- check-boot-disk-types.sh (1707 bytes)
- check-boot-final.sh (2046 bytes)
- check-boot-simple.sh (1088 bytes)
- check-boot-smart.sh (1333 bytes)
- check-zfs-boot-types.sh (1490 bytes)

Review the BOOT-DRIVE-ANALYSIS.md in /docs of k8s-proxmox private repository in Github

-->

# ZFS Boot Mirror Drive Analysis

## Overview

Managing storage in a homelab Proxmox cluster requires balancing reliability with cost constraints. This article documents automated monitoring scripts that track ZFS boot mirror health across six nodes, identify drives approaching end-of-life, and enable proactive replacement planning to spread costs over time.

## Summary

| Node | Disks | Type | Size | Power-On Hours | Health | Notes |
|------|-------|------|------|----------------|--------|-------|
| **harlan** | sda, sdb | SSD | 119.2G | 291h (~12 days) | ✅ Excellent | New SSDs, 100% reserved space |
| **kovacs** | sda, sdb | HDD | 149G | 43,619h / 42,708h (~5 years) | ⚠️ Aging | Samsung HD161HJ drives |
| **poe** | sda, sdb | HDD | 149G | 55,968h / 48,952h (~6.4 / 5.6 years) | ⚠️ Aging | Seagate/Samsung mixed |
| **edgar** | sda, sdb | HDD | 931.5G | 36,497h / 15,162h (~4.2 / 1.7 years) | ⚠️ sdb has 384 reallocated sectors | Toshiba has bad sectors |
| **tanaka** | sda, sdb | HDD | 465.8G | 24,632h / 19,329h (~2.8 / 2.2 years) | ⚠️ sdb has 1 reallocated sector | Apple/Seagate mixed, Desktop form factor |
| **quell** | sda, sdb | SSD | 119.2G | 59h / 52h (~2-3 days) | ✅ Excellent | New Timetec SSDs, 100% reserved space |

## Key Findings

### ✅ Good Health (SSD Nodes)
- **harlan**: Brand new SSDs (291 hours), perfect health
- **quell**: Brand new SSDs (52-59 hours), perfect health

### ⚠️ Aging HDDs (Needs Monitoring)
- **kovacs**: 5+ year old Samsung HDDs, still healthy but aging
- **poe**: 6+ year old mixed drives (Seagate/Samsung), oldest in cluster
- **edgar**: **384 reallocated sectors on sdb** - drive showing wear, monitor closely
- **tanaka**: 2-3 year old drives, 1 reallocated sector on sdb

### 🔧 Recommendations

**Immediate Action:**
1. **edgar sdb (Toshiba MQ01ABD100)**: 384 reallocated sectors is concerning. Consider replacement soon.
2. **tanaka**: Single 3.5" HDD boot - upgrade to dual 2.5" SSD mirror (4 SATA ports available)

**Short-term (6-12 months):**
3. **poe**: 55,968 hours (6.4 years) on sda - oldest drive, plan replacement
4. **kovacs**: 43,619 hours (5 years) - aging but stable, monitor quarterly

**Long-term:**
5. Standardize all nodes on SSD boot mirrors for reliability and performance

### SATA Port Availability

| Node | SATA Ports | Current Usage | Available |
|------|------------|---------------|-----------|
| harlan | 6 | 2 (boot) + 3 (Ceph OSDs) | 1 |
| kovacs | 6 | 2 (boot) + 3 (Ceph OSDs) | 1 |
| poe | 6 | 2 (boot) + 3 (Ceph OSDs) | 1 |
| edgar | 6 | 2 (boot) + 3 (Ceph OSDs) | 1 |
| tanaka | 4 | 2 (boot) | 2 |
| quell | 6 | 2 (boot) + 3 (Ceph OSDs) | 1 |

**Note:** Tanaka has 2 available SATA ports, sufficient for upgrading to dual 2.5" SSD boot mirror.

## Detailed SMART Data

### harlan (SSD - Excellent)
- **Type:** 2x 119.2G SSDs (ZFS mirror)
- **Power-On:** 291 hours (~12 days)
- **Cycles:** 20-21
- **Temperature:** 40°C
- **Reallocated Sectors:** 0
- **Pending Sectors:** 0
- **Reserved Space:** 100%
- **Status:** ✅ New drives, perfect health

### kovacs (HDD - Aging)
- **Type:** 2x Samsung HD161HJ 149G HDDs (ZFS mirror)
- **Power-On:** 43,619h / 42,708h (~5 years)
- **Cycles:** 211 / 166
- **Temperature:** 31°C / 33°C
- **Reallocated Sectors:** 0
- **Pending Sectors:** 0
- **Status:** ⚠️ Aging but healthy, monitor quarterly

### poe (HDD - Aging, Oldest)
- **Type:** Seagate ST3160812AS + Samsung HD161HJ 149G (ZFS mirror)
- **Power-On:** 55,968h / 48,952h (~6.4 / 5.6 years)
- **Cycles:** 201 / 192
- **Temperature:** 38°C / 33°C
- **Reallocated Sectors:** 0
- **Pending Sectors:** 0
- **Status:** ⚠️ Oldest drives in cluster, plan replacement

### edgar (HDD - Degraded)
- **Type:** Seagate ST31000524AS + Toshiba MQ01ABD100 931.5G (ZFS mirror)
- **Power-On:** 36,497h / 15,162h (~4.2 / 1.7 years)
- **Cycles:** 124 / 162
- **Temperature:** 39°C / 35°C
- **Reallocated Sectors:** 0 / **384** ⚠️
- **Pending Sectors:** 0
- **Status:** ⚠️ **sdb has 384 reallocated sectors - replace soon**

### tanaka (HDD - Desktop, Single Boot Option)
- **Type:** Apple HDD HTS547550A9E384 + Seagate ST3500418AS 465.8G (ZFS mirror)
- **Power-On:** 24,632h / 19,329h (~2.8 / 2.2 years)
- **Cycles:** 910 / 2,859
- **Temperature:** 30°C / 27°C
- **Reallocated Sectors:** 0 / 1
- **Pending Sectors:** 0
- **Status:** ⚠️ Dell Optiplex 990 Desktop (not Tower), 4 SATA ports, 2 available for SSD upgrade

### quell (SSD - Excellent)
- **Type:** 2x Timetec 30TT253X2-128G 119.2G SSDs (ZFS mirror)
- **Power-On:** 59h / 52h (~2-3 days)
- **Cycles:** 10 / 4
- **Temperature:** 40°C
- **Reallocated Sectors:** 0
- **Pending Sectors:** 0
- **Reserved Space:** 100%
- **Status:** ✅ New drives, perfect health

## Monitoring Scripts

The solution consists of five specialized scripts stored in `/mnt/pve/cephfs/bin/storage-tests/`:

1. **check-boot-disk-types.sh** (1707 bytes): Identifies disk types and models
2. **check-boot-simple.sh** (1088 bytes): Basic disk information gathering
3. **check-zfs-boot-types.sh** (1490 bytes): ZFS-specific disk type detection
4. **check-boot-smart.sh** (1333 bytes): SMART health data collection
5. **check-boot-final.sh** (2046 bytes): Comprehensive disk inventory report

### Usage Example

```bash
# Copy and execute the comprehensive check
scp scripts/check-boot-final.sh root@192.168.86.11:/root/
ssh root@192.168.86.11 'bash /root/check-boot-final.sh'

# Run SMART health analysis
scp scripts/check-boot-smart.sh root@192.168.86.11:/root/
ssh root@192.168.86.11 'bash /root/check-boot-smart.sh'
```

## Tanaka Upgrade Path

**Current:** Single 3.5" HDD boot option (Dell Optiplex 990 Desktop)
**Target:** Dual 2.5" SSD ZFS mirror

**Requirements:**
- 2x 2.5" SATA SSDs (120-128GB recommended)
- 2x 2.5" to 3.5" drive bay adapters (if needed)
- SATA ports: 4 available, 2 currently used, **2 available for upgrade**

**Recommended SSDs (Budget-friendly):**
- Kingston A400 120GB
- Crucial BX500 120GB
- Samsung 870 EVO 120GB (premium option)

**Installation Steps:**
1. Verify 2 available SATA ports on motherboard
2. Install 2x 2.5" SSDs (may need adapters for 3.5" bays)
3. Reinstall Proxmox with ZFS mirror on new SSDs
4. Restore configuration and rejoin cluster
5. Repurpose old HDDs for backup/archive storage

## Monitoring Schedule

**Monthly:**
- Check SMART health on all nodes: `smartctl -H /dev/sdX`

**Quarterly:**
- Full SMART report on aging HDDs (kovacs, poe, edgar, tanaka)
- Review reallocated sector counts

**Annual:**
- Plan HDD to SSD migrations based on age and health
- Budget for drive replacements

### Automated Scheduled Reporting

For homelab cost management, schedule automated reports to track drive health trends:

```bash
# Add to crontab on management node
# Weekly summary report
0 8 * * 1 /mnt/pve/cephfs/bin/storage-tests/check-boot-final.sh | mail -s "Weekly ZFS Boot Status" admin@homelab

# Monthly detailed SMART report
0 9 1 * * /mnt/pve/cephfs/bin/storage-tests/check-boot-smart.sh | mail -s "Monthly SMART Report" admin@homelab
```

This enables:
- Early warning of drive degradation
- Planned replacement budgeting (vs emergency purchases)
- Historical tracking of drive longevity
- Cost spreading across multiple months

## Cost Estimate for Full SSD Migration

**Strategy:** Replace all HDDs with standardized 128GB SSDs to minimize costs while providing adequate boot storage. This migration will be performed in conjunction with BIOS to UEFI conversion for modern boot capabilities.

| Node | Current | Target | Est. Cost |
|------|---------|--------|-----------|
| harlan | ✅ SSD 128GB | - | $0 |
| kovacs | HDD 149GB | 2x 128GB SSD | $40-60 |
| poe | HDD 149GB | 2x 128GB SSD | $40-60 |
| edgar | HDD 931GB | 2x 128GB SSD | $40-60 |
| tanaka | HDD 465GB | 2x 128GB SSD | $40-60 |
| quell | ✅ SSD 128GB | - | $0 |
| **Total** | | | **$160-240** |

**Notes:**
- 128GB provides ample space for Proxmox boot (typically uses <20GB)
- Standardizing on single SSD size simplifies inventory and reduces costs
- BIOS to UEFI migration enables modern boot features and GPT partitioning
- All data storage handled by Ceph cluster, not boot drives

**Priority Order:**
1. edgar (sdb failing, 384 reallocated sectors) - $40-60
2. tanaka (Desktop form factor, easy upgrade) - $40-60
3. poe (oldest drives, 6+ years) - $40-60
4. kovacs (aging but stable, 5 years) - $40-60

## Resources

- [Proxmox ZFS Documentation](https://pve.proxmox.com/wiki/ZFS_on_Linux)
- [SMART Attribute Reference](https://en.wikipedia.org/wiki/S.M.A.R.T.)
- [ZFS Best Practices](https://pve.proxmox.com/wiki/ZFS:_Tips_and_Tricks)

---

*Analysis generated from automated monitoring scripts in the k8s-proxmox repository.*
