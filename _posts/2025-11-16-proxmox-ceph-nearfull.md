---
title:  "Managing Ceph Nearfull Warnings in Proxmox Homelab"
layout: post
categories: [technical, homelab]
tags: [proxmox, ceph, storage, monitoring, capacity, homelab, dell-wyse-3040]
published: true
---

When running Ceph in a homelab environment, especially on resource-constrained hardware like my [Dell Wyse 3040 cluster](/proxmox-8-dell-wyse-3040/), managing storage capacity becomes critical. Understanding Ceph's **Nearfull** warnings and how to respond to them can prevent your cluster from going read-only unexpectedly.

<!-- excerpt-end -->

## Understanding Ceph Storage Warnings

Ceph has three critical storage thresholds that trigger different behaviors:

### Storage Capacity Thresholds

Check your current ratios with:

```console
root@harlan:~# ceph osd dump | grep ratio
full_ratio 0.95
backfillfull_ratio 0.9
nearfull_ratio 0.85
```

**Nearfull Ratio (85% by default):**

- When OSDs reach 85% capacity, `nearfull_ratio` warning is triggered
- Cluster continues normal operations but issues warnings
- Time to start planning capacity expansion or data cleanup

**Backfillfull Ratio (90% by default):**

- When OSDs reach 90% capacity, `backfillfull_ratio` warning is triggered
- Cluster will deny backfilling to the OSD in question
- Recovery operations become limited

**Full Ratio (95% by default):**

- When OSDs reach 95% capacity, `full_ratio` is triggered
- All PGs (Placement Groups) on affected OSDs are marked Read Only
- Cluster becomes read-only to prevent corruption

## Monitor Node Storage Issues

Sometimes the warning isn't about OSD capacity but about the monitor nodes themselves:

```console
HEALTH_WARN: mons pve2,pve3 are low on available space
mon.pve2 has 27% avail
mon.pve3 has 25% avail
```

This warning appears when the root partition for the OS is getting full. For Dell Wyse 3040s with limited eMMC storage, this threshold needs adjustment or the root filesystem needs cleanup as covered in my [Proxmox maintenance scripts](/proxmox-misc-scripts/) article.

## Analyzing Current Cluster Usage

Use the `ceph osd df tree` command to get a detailed view of your cluster's storage distribution:

```console
root@harlan:~# ceph osd df tree
ID  CLASS  WEIGHT    REWEIGHT  SIZE     RAW USE  DATA     OMAP     META     AVAIL    %USE   VAR   PGS  STATUS  TYPE NAME
-1         54.58063         -   41 TiB   26 TiB   26 TiB  152 MiB   80 GiB   15 TiB  62.58  1.00    -          root default
-3         18.19354         -   14 TiB  8.2 TiB  8.2 TiB   48 MiB   26 GiB  5.4 TiB  60.34  0.96    -              host harlan
 0    hdd   4.54839   1.00000  4.5 TiB  2.8 TiB  2.7 TiB   18 MiB  6.9 GiB  1.8 TiB  60.48  0.97   48      up          osd.0
 3    hdd   4.54839   1.00000  4.5 TiB  2.5 TiB  2.5 TiB   16 MiB  6.0 GiB  2.0 TiB  55.66  0.89   47      up          osd.3
 6    hdd   4.54839   1.00000  4.5 TiB  3.0 TiB  2.9 TiB   13 MiB   13 GiB  1.6 TiB  64.88  1.04   46      up          osd.6
-7         18.19354         -   14 TiB  9.2 TiB  9.2 TiB   58 MiB   33 GiB  4.4 TiB  67.74  1.08    -              host kovacs
 2    hdd   4.54839   1.00000  4.5 TiB  3.6 TiB  3.6 TiB   11 MiB  7.6 GiB  942 GiB  79.78  1.27   57      up          osd.2
 5    hdd   4.54839   1.00000  4.5 TiB  2.4 TiB  2.4 TiB   34 MiB   12 GiB  2.1 TiB  53.79  0.86   49      up          osd.5
 8    hdd   4.54839   1.00000  4.5 TiB  3.2 TiB  3.2 TiB   13 MiB   13 GiB  1.4 TiB  69.64  1.11   51      up          osd.8
-5         18.19354         -   14 TiB  8.1 TiB  8.1 TiB   46 MiB   22 GiB  5.5 TiB  59.65  0.95    -              host poe
 1    hdd   4.54839   1.00000  4.5 TiB  2.8 TiB  2.8 TiB   11 MiB  6.4 GiB  1.8 TiB  60.95  0.97   43      up          osd.1
 4    hdd   4.54839   1.00000  4.5 TiB  2.5 TiB  2.5 TiB   19 MiB  5.9 GiB  2.0 TiB  56.06  0.90   47      up          osd.4
 7    hdd   4.54839   1.00000  4.5 TiB  2.8 TiB  2.8 TiB   17 MiB  9.7 GiB  1.7 TiB  61.94  0.99   52      up          osd.7
                        TOTAL   41 TiB   26 TiB   26 TiB  152 MiB   80 GiB   15 TiB  62.58
MIN/MAX VAR: 0.86/1.27  STDDEV: 7.64
```

Key observations from this output:

- **Total cluster usage**: 62.58% (well below nearfull threshold)
- **Uneven distribution**: OSD.2 at 79.78% is approaching nearfull
- **Variance**: MIN/MAX VAR of 0.86/1.27 shows some imbalance

## Calculating Safe Capacity Limits

The [Ceph documentation](https://docs.ceph.com/en/latest/rados/configuration/mon-config-ref/#storage-capacity) provides guidance for determining appropriate ratios:

**Planning Considerations:**

1. **Number of OSDs in your cluster**
2. **Total capacity of the cluster**
3. **Expected simultaneous OSD failures**

**Calculation Method:**

- Divide total capacity by number of OSDs for average OSD capacity
- Multiply by expected simultaneous failures during normal operations
- Factor in replication overhead (3x for replica pools)
- Set ratios with sufficient headroom for rebalancing operations

## Modifying Capacity Ratios

**Warning**: The defaults exist for good reasons. Only modify them with careful consideration of your specific environment.

These settings are changed in the OSDMap using:

```bash
# Modify nearfull ratio (default 0.85)
ceph osd set-nearfull-ratio 0.80

# Modify backfillfull ratio (default 0.90)
ceph osd set-backfillfull-ratio 0.85

# Modify full ratio (default 0.95)
ceph osd set-full-ratio 0.90
```

For homelab environments with limited expansion options, you might consider slightly more aggressive ratios, but always maintain adequate headroom for:

- Rebalancing operations when OSDs fail
- Temporary space usage during recovery
- Metadata overhead growth

## Responding to Nearfull Warnings

When you receive nearfull warnings, you have several options:

### Immediate Actions

1. **Identify hotspots**: Use `ceph osd df tree` to find heavily loaded OSDs
2. **Check for uneven distribution**: Look for high variance in OSD usage
3. **Review recent data additions**: Determine what caused the capacity increase

### Short-term Solutions

1. **Rebalance the cluster**: If distribution is uneven, rebalancing may help
2. **Clean up unnecessary data**: Remove old snapshots, unused VMs, or temporary files
3. **Adjust pool settings**: Review PG counts and pool configurations

### Long-term Solutions

1. **Add more OSDs**: Expand storage capacity
2. **Upgrade existing OSDs**: Replace with larger drives
3. **Implement data lifecycle policies**: Automated cleanup of old data

## Monitoring and Alerting

Set up proactive monitoring to catch capacity issues early:

```bash
# Check cluster status regularly
ceph status

# Monitor OSD usage trends
ceph osd df

# Set up automated alerts at 75% capacity
# (before nearfull threshold is reached)
```

Consider integrating with monitoring solutions like:

- Prometheus + Grafana for Ceph metrics
- Proxmox's built-in monitoring
- Custom scripts that alert on capacity thresholds

## Homelab-Specific Considerations

Running Ceph in a homelab presents unique challenges:

**Limited Hardware**: Unlike enterprise environments, you can't easily add more nodes or storage

**Budget Constraints**: Capacity expansion requires careful planning and budgeting

**Single Administrator**: No 24/7 operations team to respond to alerts

**Learning Environment**: Mistakes are learning opportunities, but data loss is still painful

## Prevention Strategies

1. **Monitor trends**: Track capacity growth over time
2. **Plan expansion**: Order new drives before reaching 70% capacity
3. **Test procedures**: Practice adding OSDs and rebalancing in test environments
4. **Document processes**: Keep runbooks for capacity management procedures

## Conclusion

Managing Ceph capacity in a homelab requires proactive monitoring and planning. Understanding the nearfull, backfillfull, and full ratios helps you respond appropriately to warnings before they become critical issues.

The key is maintaining enough headroom for normal operations while maximizing your storage investment. Regular monitoring, trend analysis, and capacity planning will keep your Ceph cluster healthy and available.

For more Ceph management guidance, see my articles on [Ceph performance tuning](/proxmox-ceph-performance/) and [Proxmox maintenance scripts](/proxmox-misc-scripts/).

## References

- [Ceph Storage Capacity Documentation](https://docs.ceph.com/en/latest/rados/configuration/mon-config-ref/#storage-capacity)
- [SUSE Support: Cluster Pools got marked read only, OSDs are near full](https://www.suse.com/support/kb/doc/?id=000019724)

*[PVE]: Proxmox Virtual Environment
*[OSD]: Object Storage Daemon
*[PG]: Placement Group
