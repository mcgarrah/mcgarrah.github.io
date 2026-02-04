---
title: "USB Drive SMART Updates: Fast-Track to the GRUB Solution"
layout: post
categories: [technical, hardware, proxmox]
tags: [seagate, usb, smart, monitoring, storage, linux, proxmox, homelab, ceph, cluster]
published: true
---

New USB drives arrived for my Ceph cluster, and they're not reporting SMART data. Again. After solving this problem in my [October 2025 article](/2025/10/26/usb-drive-smart/), I need to update the configuration with new device IDs and share the lessons learned from running this solution across my entire cluster.

**The bottom line:** This was absolutely the right decision. SMART monitoring has already caught failing drives before they damaged data, and the performance trade-off is negligible compared to the stability benefits.

<!-- excerpt-end -->

## The Context: Ceph Storage Reality

My AlteredCarbon cluster runs 69 TiB of Ceph storage across 6 nodes. The Seagate USB drives aren't just backup storage—they're critical infrastructure:

- **Ceph OSDs**: Most USB drives serve as Ceph OSDs in the cluster
- **ZFS backup volume**: One 28TB drive provides CephFS backup via ZFS
- **Media serving**: Jellyfin libraries for the household
- **Disaster recovery**: Off-cluster backup copies

**SMART data is table stakes** for this setup. When a drive starts failing in a Ceph cluster, you need to know immediately, not when it's too late.

## The Problem: New Drives, Same Issue

Five new Seagate USB drives arrived for cluster expansion, and predictably, none report SMART data:

```bash
root@edgar:~# smartctl -d sat -a /dev/sdd
Read Device Identity failed: scsi error unsupported field in scsi command
SMART support is: Ambiguous
A mandatory SMART command failed: exiting.
```

The [original solution from October 2025](/2025/10/26/usb-drive-smart/) covered three methods. After months of production use, **GRUB boot parameters** proved most reliable across all cluster scenarios.

## The Fast-Track Solution

Skip the experimentation—go straight to what works:

### Updated Device Coverage

The new drives introduced additional device IDs that need quirks:

```bash
# Updated comprehensive configuration
cat > /etc/default/grub.d/usb-quirks.cfg << 'EOF'
# USB Storage Quirks for Seagate SMART Monitoring
GRUB_CMDLINE_LINUX="$GRUB_CMDLINE_LINUX usb_storage.quirks=0bc2:2038:,0bc2:2344:,0bc2:ab83:,0bc2:ab9a:,0bc2:ac25:,0bc2:ac2b:,0bc2:ac35:,0bc2:ac41:"
EOF

# Apply and reboot
proxmox-boot-tool refresh
reboot
```

### Device ID Mapping

| Device ID | Model Series | Cluster Nodes | Purchase Date |
|-----------|--------------|---------------|---------------|
| `0bc2:2038` | Newer models | edgar | Late 2025 |
| `0bc2:2344` | Expansion Portable | kovacs | 2024 |
| `0bc2:ab83` | Recent drives | poe | Late 2025 |
| `0bc2:ab9a` | Recent drives | edgar | Late 2025 |
| `0bc2:ac25` | Backup Plus | Various | 2024-2025 |
| `0bc2:ac2b` | BUP Portable | poe, kovacs | 2024 |
| `0bc2:ac35` | Newer models | edgar | Late 2025 |
| `0bc2:ac41` | One Touch HDD | harlan, kovacs | 2024 |

### Verification

```bash
# Confirm quirks loaded
cat /sys/module/usb_storage/parameters/quirks

# Test SMART access
smartctl -d sat -H /dev/sdX  # Health check
smartctl -d sat -a /dev/sdX  # Full report
```

## Why GRUB Works Best

After testing all three methods from the [original article](/2025/10/26/usb-drive-smart/), GRUB boot parameters proved superior:

- **Always applies**: Quirks active before any USB detection
- **Survives everything**: Kernel updates, system changes, reboots
- **BIOS/UEFI compatible**: Works regardless of boot mode
- **Cluster-friendly**: Easy deployment across multiple nodes

The other methods (runtime quirks, modprobe config) had reliability issues in production.

## Real-World Results

After 4+ months running this configuration across all cluster nodes:

### Success Stories
- **Early detection**: Caught one drive showing reallocated sectors before failure
- **Zero stability issues**: No crashes, corruption, or weird USB behavior
- **Complete monitoring**: All storage devices visible in Grafana dashboards
- **Automated alerts**: Proactive notifications when drives show wear

### Performance Reality
Yes, disabling UAS reduces USB performance by 10-30%. For Ceph OSDs and backup storage, this trade-off is absolutely worth it:

```
Before: Fast transfers, blind to drive health
After:  Slightly slower transfers, complete visibility
Result: Zero surprise failures, proactive maintenance
```

**The math is simple**: a slightly slower ceph cluster beat data loss every time.

## Cluster Deployment

For multi-node deployment, use shared storage:

```bash
# Store config on CephFS
cp /etc/default/grub.d/usb-quirks.cfg /mnt/pve/cephfs/configs/

# Deploy to all nodes
for node in harlan kovacs poe edgar tanaka quell; do
    scp /mnt/pve/cephfs/configs/usb-quirks.cfg root@$node:/etc/default/grub.d/
    ssh root@$node "proxmox-boot-tool refresh"
done

# Coordinate reboots (maintain quorum)
# Reboot 2-3 nodes at a time
```

## Troubleshooting

If you're still getting SMART errors:

```bash
# 1. Verify quirks loaded
cat /sys/module/usb_storage/parameters/quirks

# 2. Find your device ID
lsusb | grep -i seagate

# 3. Add missing device ID
echo "0bc2:XXXX:" >> /etc/default/grub.d/usb-quirks.cfg
proxmox-boot-tool refresh

# 4. Try permissive mode
smartctl -d sat -T permissive -a /dev/sdX
```

## Integration with Monitoring

With SMART data available, integrate into your monitoring stack:

```bash
# Health check in scripts
if ! smartctl -d sat -H /dev/sdX | grep -q "PASSED"; then
    echo "WARNING: Drive health check failed"
    # Send alert, skip backup, etc.
fi

# Export to Prometheus
smartctl -d sat -a /dev/sdX | grep -E "(Temperature|Reallocated|Power_On_Hours)"
```

## Conclusion

The GRUB method provides reliable USB SMART monitoring across Proxmox clusters. After months of production use, this solution has:

- **Prevented data loss**: Early detection of failing drives
- **Improved stability**: Complete storage health visibility
- **Simplified operations**: Consistent monitoring across all nodes
- **Proven reliability**: Zero issues across 6-node cluster

For Ceph environments, SMART monitoring isn't optional—it's essential. This solution ensures you catch drive problems before they become data disasters.

## References

- [Original USB SMART article](/2025/10/26/usb-drive-smart/) - Complete exploration of all methods
- [smartmontools documentation](https://www.smartmontools.org/) - SMART monitoring tools
