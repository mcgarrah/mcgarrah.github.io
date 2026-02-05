---
layout: post
title: "Monitoring ZFS Boot Mirror Health in Proxmox 8 Clusters"
excerpt: "Automated SMART monitoring and cost planning for ZFS boot mirrors across a six-node Proxmox homelab cluster with mixed SSD/HDD hardware. Track drive health, plan replacements, and manage homelab storage costs effectively."
categories: [proxmox, zfs, storage, monitoring]
tags: [proxmox, zfs, smart, storage, cluster, hardware]
published: true
---

# ZFS Boot Mirror Drive Analysis

## The Problem

Two nodes in my six-node Proxmox 8.4 cluster experienced catastrophic boot drive failures that threatened cluster availability. **Harlan** and **Quell** required emergency migrations to SSDs to restore stability. This was a risk I accepted when using aging hardware, but mitigated with ZFS boot mirrors that kept the nodes operational during the crisis.

**Harlan** had aging spinning rust HDDs that began failing on both sides of the mirror simultaneously. **Quell** had newer 120GB Bliksem SSDs (purchased Feb/Mar 2024) that stopped reporting SMART data correctly and threw ZFS errors without warning. Both drives were out of warranty and headed for the discard pile.

Both nodes were migrated to new 128GB SSDs, but with different approaches:

- **Harlan**: Required full Proxmox reinstall due to disk size reduction (larger HDDs → smaller SSDs), then migrated configuration from old to new installation
- **Quell**: Used ZFS resilver approach - dropped one failing SSD from mirror, added new SSD to resilver from the partially-working drive, then replaced the second failing drive

These emergency replacements provided valuable lessons for proactive planning. Four remaining nodes still show concerning ZFS boot mirror health issues:

1. **edgar**: 384 reallocated sectors on sdb (Toshiba MQ01ABD100) - active drive degradation
2. **poe**: 56,048 power-on hours (6.4 years) - oldest drive in cluster
3. **tanaka**: Aging HDDs (24,725h / 19,422h) with 1 reallocated sector - upgrade recommended
4. **kovacs**: 43,712 hours (5 years) - aging but stable, monitor quarterly

All six nodes currently run BIOS boot mode with legacy MBR partitioning. No nodes have been migrated to UEFI yet - this is planned for future drive replacements requiring complete Proxmox reinstalls.

Two nodes (**harlan** and **quell**) now have new 128GB SSDs but still boot in BIOS mode. The remaining HDD-based nodes (**kovacs**, **poe**, **edgar**, **tanaka**) require proactive replacement planning to avoid repeating the emergency migration experience.

The challenge: Reinstalling Proxmox 8.4 on new media is time-intensive, especially when migrating from BIOS to UEFI boot. Spreading these upgrades across multiple months makes the cost and effort manageable for a homelab environment.

## The Solution

Implement automated SMART monitoring scripts to track drive health across all nodes, enabling proactive replacement planning. The solution provides:

- **Health visibility**: Automated SMART data collection across six nodes
- **Cost planning**: Spread replacements over 6-12 months based on priority
- **Standardization**: Migrate all nodes to 128GB SSD mirrors for reliability
- **UEFI migration**: Combine drive replacement with BIOS-to-UEFI conversion (planned for next reinstall)

## Replacement Priority

### Immediate (0-3 months)
1. **edgar**: 384 reallocated sectors on sdb - active drive degradation
2. **tanaka**: Aging HDDs with 1 reallocated sector, 2 available SATA ports for easy upgrade

### Short-term (3-6 months)
3. **poe**: 56,048 power-on hours (6.4 years) - oldest drive in cluster

### Medium-term (6-12 months)
4. **kovacs**: 43,712 hours (5 years) - aging but stable, monitor quarterly

### Completed ✅
- **harlan**: Emergency migration to 128GB SSD mirror after HDD boot mirror failure (384 hours, BIOS boot - UEFI planned)
- **quell**: Emergency migration to 128GB Timetec SSD mirror after HDD boot mirror failure (145-152 hours, BIOS boot - UEFI planned)

**Note:** Both harlan and quell migrations were unplanned emergency responses to imminent HDD failures that threatened node availability. These rapid migrations validated the process and informed the proactive replacement strategy for remaining nodes.

## Current Cluster Status

| Node | Disks | Type | Size | Power-On Hours | Health | Priority |
|------|-------|------|------|----------------|--------|----------|
| **harlan** | sda, sdb | SSD | 119.2G | 384h (~16 days) | ✅ Excellent | Complete |
| **quell** | sda, sdb | SSD | 119.2G | 152h / 145h (~6 days) | ✅ Excellent | Complete |
| **edgar** | sda, sdb | HDD | 931.5G | 36,590h / 15,255h | ⚠️ 384 reallocated sectors | **Immediate** |
| **tanaka** | sda, sdb | HDD | 465.8G | 24,725h / 19,422h | ⚠️ 1 reallocated sector | **Immediate** |
| **poe** | sda, sdb | HDD | 149G | 56,048h / 49,045h | ⚠️ Oldest drives | Short-term |
| **kovacs** | sda, sdb | HDD | 149G | 43,712h / 42,801h | ⚠️ Aging | Medium-term |

**Hardware readiness:**
- **edgar**: 2x 128GB SSDs on shelf, ready for immediate installation
- **tanaka**: 2x 128GB SSDs ordered from Amazon, arriving next week

### Benefits of Spreading Costs

- **Budget management**: \$30-40/month vs \$160 upfront
- **Learning curve**: Refine BIOS-to-UEFI process across multiple installations
- **Risk mitigation**: Test migration process before critical nodes
- **Operational continuity**: Maintain cluster availability during upgrades

## Detailed Node Analysis

### harlan (SSD - Excellent)
- **Type:** 2x 119.2G SSDs (ZFS mirror)
- **Power-On:** 384 hours (~16 days)
- **Cycles:** 22 / 21
- **Temperature:** 40°C
- **Reallocated Sectors:** 0
- **Pending Sectors:** 0
- **Reserved Space:** 100%
- **Status:** ✅ New drives, perfect health
- **Boot Mode:** BIOS (UEFI migration planned)

### kovacs (HDD - Aging)
- **Type:** 2x Samsung HD161HJ 149G HDDs (ZFS mirror)
- **Power-On:** 43,712h / 42,801h (~5 years)
- **Cycles:** 212 / 167
- **Temperature:** 33°C / 36°C
- **Reallocated Sectors:** 0
- **Pending Sectors:** 0
- **Status:** ⚠️ Aging but healthy, monitor quarterly

### poe (HDD - Aging, Oldest)
- **Type:** Seagate ST3160812AS + Samsung HD161HJ 149G (ZFS mirror)
- **Power-On:** 56,048h / 49,045h (~6.4 / 5.6 years)
- **Cycles:** 202 / 193
- **Temperature:** 40°C / 36°C
- **Reallocated Sectors:** 0
- **Pending Sectors:** 0
- **Status:** ⚠️ Oldest drives in cluster, plan replacement

### edgar (HDD - Degraded)
- **Type:** Seagate ST31000524AS + Toshiba MQ01ABD100 931.5G (ZFS mirror)
- **Power-On:** 36,590h / 15,255h (~4.2 / 1.7 years)
- **Cycles:** 125 / 163
- **Temperature:** 42°C / 37°C
- **Reallocated Sectors:** 0 / **384** ⚠️
- **Pending Sectors:** 0
- **Status:** ⚠️ **sdb has 384 reallocated sectors - replace immediately**

### tanaka (HDD - Aging, Desktop Form Factor)
- **Type:** Apple HDD HTS547550A9E384 + Seagate ST3500418AS 465.8G (ZFS mirror)
- **Power-On:** 24,725h / 19,422h (~2.8 / 2.2 years)
- **Cycles:** 911 / 2,860
- **Temperature:** 33°C / 30°C
- **Reallocated Sectors:** 0 / 1
- **Pending Sectors:** 0
- **Status:** ⚠️ Dell Optiplex 990 Desktop, 4 SATA ports (2 boot + 2 available), good upgrade candidate

### quell (SSD - Excellent)
- **Type:** 2x Timetec 30TT253X2-128G 119.2G SSDs (ZFS mirror)
- **Power-On:** 152h / 145h (~6 days)
- **Cycles:** 12 / 6
- **Temperature:** 40°C
- **Reallocated Sectors:** 0
- **Pending Sectors:** 0
- **Reserved Space:** 100%
- **Status:** ✅ New drives, perfect health
- **Boot Mode:** BIOS (UEFI migration planned)

## SATA Port Availability

| Node | SATA Ports | Boot | Ceph OSDs | Available | Notes |
|------|------------|------|-----------|-----------|-------|
| harlan | 6 | 2 | 3 | 1 | Dell Optiplex 990 Mini Tower |
| kovacs | 6 | 2 | 3 | 1 | Dell Optiplex 990 Mini Tower |
| poe | 6 | 2 | 3 | 1 | Dell Optiplex 990 Mini Tower |
| edgar | 6 | 2 | 3 | 1 | Dell Optiplex 990 Mini Tower |
| tanaka | 4 | 2 | 0 | **2** | Dell Optiplex 990 Desktop |
| quell | 6 | 2 | 3 | 1 | Dell Optiplex 990 Mini Tower |

**Key Insight:** Tanaka has 2 available SATA ports, sufficient for in-place upgrade to dual SSD mirror without removing existing drives during installation.

## Monitoring Scripts

Two scripts provide comprehensive health monitoring across all cluster nodes. Scripts are stored in `/mnt/pve/cephfs/bin/` for cluster-wide access and automatically discover nodes using Proxmox API. Scripts use IP addresses instead of hostnames for DNS-independent operation.

### 1. check-zfs-boot-disks.sh - Comprehensive Inventory (Recommended)

Provides detailed disk information including model numbers and SATA port availability.

```bash
#!/bin/bash
# Comprehensive boot disk inventory for ZFS mirrors

echo "NODE       DISKS       SIZE      ROTA  TYPE       MODEL                      SATA"
echo "------------------------------------------------------------------------------------"

for ip in $(pvesh get /cluster/status --output-format json | jq -r '.[] | select(.type=="node") | .ip'); do
    node=$(pvesh get /cluster/status --output-format json | jq -r ".[] | select(.ip==\"$ip\") | .name")
    ssh -o ConnectTimeout=5 root@$ip "
        DEVS=\$(zpool status rpool | grep -E 'ata-|sd[a-z][0-9]|nvme' | awk '{print \$1}')
        DISKS=\"\"
        SIZES=\"\"
        ROTAS=\"\"
        TYPES=\"\"
        MODELS=\"\"
        for dev in \$DEVS; do
            if [[ \$dev == ata-* ]]; then
                DISK=\$(readlink -f /dev/disk/by-id/\$dev 2>/dev/null | sed 's|/dev/||;s|[0-9]*$||')
            else
                DISK=\$(echo \$dev | sed 's|[0-9]*$||')
            fi
            [ -z \"\$DISK\" ] && continue
            ROTA=\$(cat /sys/block/\$DISK/queue/rotational 2>/dev/null)
            SIZE=\$(lsblk -d -o SIZE /dev/\$DISK 2>/dev/null | tail -1 | xargs)
            MODEL=\$(lsblk -d -o MODEL /dev/\$DISK 2>/dev/null | tail -1 | xargs)
            [ \"\$ROTA\" = \"0\" ] && TYPE=\"SSD\" || TYPE=\"HDD\"
            DISKS=\"\$DISKS\$DISK,\"
            SIZES=\"\$SIZES\$SIZE,\"
            ROTAS=\"\$ROTAS\$ROTA,\"
            TYPES=\"\$TYPES\$TYPE,\"
            MODELS=\"\$MODELS\$MODEL|\"
        done
        DISKS=\$(echo \$DISKS | sed 's/,$//' | tr ',' '\n' | sort -u | tr '\n' ',' | sed 's/,$//')
        SIZES=\$(echo \$SIZES | sed 's/,$//')
        ROTAS=\$(echo \$ROTAS | sed 's/,$//')
        TYPES=\$(echo \$TYPES | sed 's/,$//')
        MODELS=\$(echo \$MODELS | sed 's/|$//')
        SATA=\$(ls -1 /sys/class/ata_port/ 2>/dev/null | wc -l)
        printf \"%-10s %-11s %-9s %-5s %-10s %-26s %s\n\" \"$node\" \"\$DISKS\" \"\$SIZES\" \"\$ROTAS\" \"\$TYPES\" \"\$MODELS\" \"\$SATA\"
    " 2>/dev/null || printf "%-10s %-11s %-9s %-5s %-10s %-26s %s\n" "$node" "-" "-" "-" "-" "Connection failed" "-"
done
```

**Example output:**
```
NODE       DISKS       SIZE      ROTA  TYPE       MODEL                      SATA
------------------------------------------------------------------------------------
harlan     sda,sdb     119.2G,119.2G 0,0   SSD,SSD    SSD|SSD                    6
kovacs     sda,sdb     149G,149G 1,1   HDD,HDD    SAMSUNG HD161HJ|SAMSUNG HD161HJ 6
poe        sda,sdb     149G,149G 1,1   HDD,HDD    ST3160812AS|SAMSUNG HD161HJ 6
edgar      sda,sdb     931.5G,931.5G 1,1   HDD,HDD    ST31000524AS|TOSHIBA MQ01ABD100 6
tanaka     sda,sdb     465.8G,465.8G 1,1   HDD,HDD    APPLE HDD HTS547550A9E384|ST3500418AS 4
quell      sda,sdb     119.2G,119.2G 0,0   SSD,SSD    Timetec 30TT253X2-128G|Timetec 30TT253X2-128G 6
```

### 2. check-zfs-boot-smart.sh - SMART Health Analysis

Collects critical SMART attributes for health assessment.

```bash
#!/bin/bash
# SMART health monitoring for ZFS boot mirrors

echo "=== ZFS Boot Mirror SMART Health Report ==="
echo ""

for ip in $(pvesh get /cluster/status --output-format json | jq -r '.[] | select(.type=="node") | .ip'); do
    node=$(pvesh get /cluster/status --output-format json | jq -r ".[] | select(.ip==\"$ip\") | .name")
    echo "Node: $node ($ip)"
    echo "---"
    
    ssh -o ConnectTimeout=5 root@$ip "
        DEVS=\$(zpool status rpool | grep -E 'ata-|sd[a-z][0-9]|nvme' | awk '{print \$1}')
        for dev in \$DEVS; do
            if [[ \$dev == ata-* ]]; then
                DISK=\$(readlink -f /dev/disk/by-id/\$dev 2>/dev/null | sed 's|/dev/||;s|[0-9]*$||')
            else
                DISK=\$(echo \$dev | sed 's|[0-9]*$||')
            fi
            [ -z \"\$DISK\" ] && continue
            
            echo \"Disk: /dev/\$DISK\"
            smartctl -H /dev/\$DISK 2>/dev/null | grep -E 'SMART overall-health|SMART Health Status'
            smartctl -A /dev/\$DISK 2>/dev/null | grep -E 'Power_On_Hours|Power_Cycle_Count|Reallocated_Sector|Current_Pending_Sector|Offline_Uncorrectable|Temperature_Celsius|Wear_Leveling_Count|Media_Wearout_Indicator|Available_Reservd_Space|Percentage Used'
            echo \"\"
        done
    " 2>/dev/null || echo "Connection failed"
    
    echo "========================================"
    echo ""
done
```

**Example output (edgar - showing degraded drive):**
```
Node: edgar (192.168.86.14)
---
Disk: /dev/sda
SMART overall-health self-assessment test result: PASSED
  5 Reallocated_Sector_Ct   0x0033   100   100   036    Pre-fail  Always       -       0
  9 Power_On_Hours          0x0032   059   059   000    Old_age   Always       -       36590
 12 Power_Cycle_Count       0x0032   100   100   020    Old_age   Always       -       125
194 Temperature_Celsius     0x0022   042   053   000    Old_age   Always       -       42
197 Current_Pending_Sector  0x0012   100   100   000    Old_age   Always       -       0

Disk: /dev/sdb
SMART overall-health self-assessment test result: PASSED
  5 Reallocated_Sector_Ct   0x0033   100   100   050    Pre-fail  Always       -       384
  9 Power_On_Hours          0x0032   062   062   000    Old_age   Always       -       15255
 12 Power_Cycle_Count       0x0032   100   100   000    Old_age   Always       -       163
194 Temperature_Celsius     0x0022   100   100   000    Old_age   Always       -       37
```

**Key findings from latest scan:**
- **harlan/quell SSDs**: 384/145-152 hours, 100% reserved space, perfect health
- **edgar sdb**: 384 reallocated sectors confirmed (immediate replacement needed)
- **poe sda**: 56,048 hours (6.4 years) - oldest drive in cluster
- **tanaka sdb**: 1 reallocated sector, 19,422 hours
- **kovacs**: 43,712/42,801 hours, no reallocated sectors (aging but stable)

### Usage

```bash
# Comprehensive inventory with model numbers (recommended)
/mnt/pve/cephfs/bin/check-zfs-boot-disks.sh

# Detailed SMART health analysis
/mnt/pve/cephfs/bin/check-zfs-boot-smart.sh
```

## Migration Strategy

### Current Boot Configuration

**All nodes currently use BIOS boot mode:**
- Legacy MBR partitioning
- No UEFI support enabled
- Works reliably but lacks modern features

**UEFI migration planned for next reinstall:**
- Requires complete Proxmox reinstallation
- Cannot be done in-place
- Will be combined with drive replacements
- First UEFI migration target: edgar or tanaka

### BIOS to UEFI Conversion (Planned)

All future drive replacements will include BIOS-to-UEFI migration:

1. **Enable UEFI in BIOS** (Dell OptiPlex 990 supports both)
2. **Backup node configuration** (network, storage, VM configs)
3. **Install new SSDs** alongside existing drives
4. **Boot from Proxmox USB installer** in UEFI mode
5. **Install Proxmox 8.4** with ZFS mirror on new SSDs (GPT partitioning)
6. **Restore configuration** and rejoin cluster
7. **Migrate VMs/containers** back to node
8. **Repurpose old drives** for backup/archive storage

**Benefits of UEFI:**
- GPT partitioning (supports >2TB boot drives)
- Secure Boot capability (optional)
- Faster boot times
- Modern firmware interface
- Better hardware compatibility

### Hardware Requirements per Node

**Standard Upgrade (harlan, kovacs, poe, edgar, quell):**
- 2x 128GB SATA SSDs
- Existing SATA ports (1 available per node)
- 2.5" drive bays or adapters

**Tanaka Specific (Dell Optiplex 990 Desktop):**
- 2x 128GB SATA SSDs (2.5" form factor)
- 2 available SATA ports (4 total, 2 in use by current HDD mirror)
- 2x 2.5" to 3.5" drive bay adapters
- Desktop form factor allows easy side-by-side installation

### Recommended SSDs

**Budget-friendly options:**
- Kingston A400 128GB (~$15-20)
- Crucial BX500 128GB (~$15-20)
- Samsung 870 EVO 128GB (~$25-30, premium)

**⚠️ Avoid: Bliksem SSDs**

Bliksem 128GB SSDs purchased from Amazon (Feb/Mar 2024) failed within 2 years:
- Stopped reporting SMART data correctly
- ZFS reported bad blocks and corruption
- CrystalDiskInfo couldn't diagnose issues
- Proactive replacement prevented data loss
- **Stick with established brands** (Kingston, Crucial, Samsung)

## Monitoring Schedule

### Automated Reporting

```bash
# Add to crontab on management node or CephFS shared location
# Weekly disk inventory (quick status check)
0 8 * * 1 /mnt/pve/cephfs/bin/check-zfs-boot-disks.sh | mail -s "Weekly ZFS Boot Status" admin@homelab

# Monthly detailed SMART report (health metrics)
0 9 1 * * /mnt/pve/cephfs/bin/check-zfs-boot-smart.sh | mail -s "Monthly SMART Report" admin@homelab
```

### Manual Checks

**Monthly (aging HDDs only):**
```bash
# Check specific node SMART health
ssh root@192.168.86.14 'smartctl -A /dev/sdb | grep Reallocated_Sector'
```

**Quarterly (all HDD nodes):**
```bash
# Full SMART report for kovacs, poe, edgar, tanaka
/mnt/pve/cephfs/bin/check-zfs-boot-smart.sh
```

**Annual:**
- Review drive replacement timeline
- Update budget for upcoming migrations
- Assess new SSD pricing and availability

### Alert Thresholds

**Immediate action required:**
- Reallocated sectors > 100
- Current pending sectors > 0
- SMART overall health: FAILED
- Power-on hours > 70,000 (8 years)

**Plan replacement (3-6 months):**
- Reallocated sectors: 1-100
- Power-on hours > 50,000 (5.7 years)
- Temperature consistently > 50°C

## Lessons Learned

### Emergency Migrations (harlan, quell)

**Context:** Both nodes experienced HDD boot mirror failures requiring immediate replacement to prevent node loss.

**What worked:**

1. **ZFS mirror redundancy** - degraded pool kept nodes operational
2. **Quick decision-making** - prioritized stability over perfection
3. **Two migration approaches** - full reinstall (harlan) vs resilver (quell) both successful

**What we learned:**
1. **Emergency migrations are stressful** - proactive replacement is far better
2. **ZFS mirror saved us** - degraded pool continued operating until replacement
3. **Have spare SSDs on hand** - eliminated ordering delays during crisis
4. **Document the process** - enabled faster execution under pressure
5. **UEFI can wait** - BIOS boot works fine, don't add complexity during emergencies

### Challenges

1. **Time investment**: 2-4 hours per node for complete migration
2. **Cluster coordination**: Requires temporary VM migration
3. **BIOS/UEFI decision**: UEFI migration deferred to reduce complexity
4. **Drive compatibility**: Verify SATA port availability before purchase
5. **Configuration backup**: Document all settings before reinstall

### Bliksem SSD Failure Analysis (Root Cause)

**What triggered the emergency migrations:**

The Bliksem SSDs installed in harlan and quell (Feb/Mar 2024) began failing catastrophically in early 2026, forcing emergency replacements.

**Timeline:**
- Feb/Mar 2024: Purchased Bliksem 128GB SSDs from Amazon
- Jan 2026: SMART data reporting anomalies
- Feb 2026: ZFS reporting bad blocks, proactive replacement

**Symptoms:**
- SMART attributes stopped updating correctly
- ZFS scrub found checksum errors
- CrystalDiskInfo showed "Good" health despite ZFS errors
- No advance warning before degradation

**Root cause:** Unknown (possibly controller firmware issues)

**Resolution:** Replaced with Kingston A400 and Timetec SSDs

**Recommendation:** Avoid no-name brands for critical boot drives

## Conclusion

Proactive monitoring and phased replacement planning enables reliable homelab operations without emergency failures or budget strain. The automated scripts provide visibility into drive health across all nodes, while the 12-month migration timeline spreads costs and effort.

**Next steps:**
1. Install SSDs in edgar (hardware on hand, ready to proceed)
2. Install SSDs in tanaka when Amazon delivery arrives next week
3. Monitor poe quarterly for degradation signs
4. Continue monthly SMART checks on all HDD nodes

**Key takeaway:** Emergency replacements during HDD failures taught us the value of proactive monitoring. Spending $30-40 every few months on planned upgrades prevents the stress and risk of emergency replacements during production failures.

## Cost Planning

### Full Cluster Migration Budget

**Strategy:** Replace all HDDs with standardized 128GB SSDs, spreading costs over 6-12 months.

| Node | Current | Target | Est. Cost | Timeline |
|------|---------|--------|-----------|----------|
| **quell** | ✅ SSD 128GB | Complete | $0 | Done |
| **harlan** | ✅ SSD 128GB | Complete | $0 | Done |
| **edgar** | HDD 931GB | 2x 128GB SSD | $30-40 | Month 1 (Immediate) |
| **tanaka** | HDD 465GB | 2x 128GB SSD | $30-40 | Month 2 (Immediate) |
| **poe** | HDD 149GB | 2x 128GB SSD | $30-40 | Month 4-6 (Short-term) |
| **kovacs** | HDD 149GB | 2x 128GB SSD | $30-40 | Month 8-12 (Medium-term) |
| **Total** | | | **$120-160** | 12 months |

**Notes:**
- **Current usage**: Nodes use 2.3-7.1GB for Proxmox boot (harlan: 2.3GB, quell: 6.8GB, edgar: 6.6GB, poe: 7.1GB, kovacs: 7.0GB, tanaka: 4.5GB)
- **128GB provides ample space**: 10-20x current usage with room for growth
- Standardizing on single SSD size simplifies inventory and reduces costs
- BIOS to UEFI migration enables modern boot features and GPT partitioning
- All data storage handled by Ceph cluster, not boot drives
