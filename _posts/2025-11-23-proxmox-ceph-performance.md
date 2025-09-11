---
title:  "Optimizing Ceph Performance in Proxmox Homelab"
layout: post
categories: [technical, homelab]
tags: [proxmox, ceph, performance, mclock, iops, optimization, homelab]
published: true
---

Performance tuning Ceph in a homelab environment presents unique challenges, especially when running on USB storage and constrained hardware. After dealing with performance issues during cluster rebalancing and OSD expansion, I've learned valuable lessons about mClock configuration, IOPS optimization, and the realities of USB 3.0 storage performance.

[![Ceph Performance and Rebalance](/assets/images/ceph-performance-osds-new-node.png){:width="30%" height="30%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/ceph-performance-osds-new-node.png){:target="_blank"}

<!-- excerpt-end -->

## The Performance Challenge

I encountered two interconnected performance issues while expanding my cluster from three to four nodes:

1. **Inconsistent mClock IOPS settings**: Some OSDs had missing or incorrect `osd_mclock_max_capacity_iops_hdd` values
2. **Major cluster rebalancing**: Moving from 3 nodes with 4 OSDs each to 4 nodes with 3 OSDs each

The rebalancing process was taking much longer than expected, and I suspected the inconsistent mClock settings were contributing to the performance bottleneck.

## Understanding mClock in Ceph

The [mClock Config Reference](https://docs.ceph.com/en/reef/rados/configuration/mclock-config-ref/#mclock-config-reference) explains how Ceph implements the [dmClock algorithm](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Gulati.pdf) for scheduling storage activities.

### What is mClock?

mClock is Ceph's quality of service (QoS) scheduler that manages IOPS allocation between different operation types:

- **Client operations**: User-initiated reads and writes
- **Background recovery**: Data movement during rebalancing
- **Scrubbing**: Data integrity checks
- **Snap trimming**: Snapshot cleanup operations

### mClock Profiles

Rather than manually tuning individual parameters, Ceph provides three predefined profiles:

- **`balanced`** (default): Equal priority for client and background operations
- **`high_client_ops`**: Prioritizes client operations over background tasks
- **`high_recovery_ops`**: Prioritizes recovery operations for faster rebalancing

## Diagnosing mClock Configuration Issues

Check your current mClock settings:

```console
root@harlan:~# ceph config dump | grep mclock
WHO    MASK  LEVEL     OPTION                                             VALUE      RO
osd.0        basic     osd_mclock_max_capacity_iops_hdd                   86.136079
osd.1        basic     osd_mclock_max_capacity_iops_hdd                   87.204995
osd.4        basic     osd_mclock_max_capacity_iops_hdd                   89.152214
```

### The Problem: Missing IOPS Values

In my case, some OSDs were missing the `osd_mclock_max_capacity_iops_hdd` setting entirely. This happened when:

- Adding new OSDs to an existing cluster
- Ceph's automatic capacity detection failed
- Hardware changes affected the initial benchmarking

### Comparing Performance Across Clusters

My test cluster showed significantly different IOPS values:

**Test Cluster (Dell Wyse 3040s):**

```console
root@pve1:~# ceph config dump | grep mclock
osd.0         basic     osd_mclock_max_capacity_iops_hdd       194.542100        
osd.1         basic     osd_mclock_max_capacity_iops_hdd       192.359779        
osd.2         basic     osd_mclock_max_capacity_iops_hdd       205.899236        
```

**After Adding New USB Drives:**

```console
osd.3         basic     osd_mclock_max_capacity_iops_hdd       339.211615        
osd.5         basic     osd_mclock_max_capacity_iops_hdd       340.816549        
osd.6         basic     osd_mclock_max_capacity_iops_hdd       326.667183        
```

The newer USB drives (OSDs 3, 5, 6) showed significantly higher IOPS capacity, likely due to:

- Better USB 3.0 interface utilization
- Newer drive firmware
- Different USB controller chipsets

## Benchmarking OSD Performance

Use Ceph's built-in benchmarking to test individual OSD performance:

```console
root@harlan:~# ceph tell osd.0 bench 12288000 4096 4194304 100
{
    "bytes_written": 12288000,
    "blocksize": 4096,
    "elapsed_sec": 2.868101647,
    "bytes_per_sec": 4284366.9828972416,
    "iops": 1045.9880329338969
}
```

**Performance Comparison:**

**Main Cluster (Good Performance):**

- **IOPS**: 1,045
- **Throughput**: 4.28 MB/s
- **Latency**: Low and consistent

**Test Cluster (Constrained Performance):**

```console
root@pve1:~# ceph tell osd.0 bench 12288000 4096 4194304 100
{
    "bytes_written": 12288000,
    "blocksize": 4096,
    "elapsed_sec": 18.758997973,
    "bytes_per_sec": 655045.64890332799,
    "iops": 159.92325412678906
}
```

- **IOPS**: 159 (6.5x slower)
- **Throughput**: 655 KB/s (6.5x slower)
- **Latency**: Significantly higher

## USB 3.0 Performance Realities

### Theoretical vs. Actual Performance

**USB 3.0 Specifications:**

- USB 3.0: 5 Gbps theoretical (625 MB/s)
- USB 3.1: 10 Gbps theoretical (1.25 GB/s)
- USB 3.2: 20 Gbps theoretical (2.5 GB/s)

**Real-World Performance:**

- Protocol overhead reduces actual throughput by 15-20%
- USB-to-SATA bridge limitations
- Drive-specific performance characteristics
- USB controller quality and implementation

### Why 10-16 MiB/s Transfer Rates?

Several factors limit USB drive performance in Ceph:

1. **Random I/O patterns**: Ceph generates lots of small, random writes
2. **USB protocol overhead**: Especially problematic for small block sizes
3. **Drive caching**: USB drives often have limited write caches
4. **Concurrent operations**: Multiple OSDs competing for USB bandwidth

[![Ceph Recovery and Rebalance](/assets/images/ceph-recovery-rebalance-homelab.png){:width="30%" height="30%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/ceph-recovery-rebalance-homelab.png){:target="_blank"}

## Optimizing mClock for Rebalancing

### Using mClock Profiles

Instead of manually adjusting individual parameters, use mClock profiles:

```bash
# Enable high recovery operations during rebalancing
ceph config set global osd_mclock_profile high_recovery_ops

# Monitor rebalancing progress
ceph status

# Return to balanced profile after completion
ceph config set global osd_mclock_profile balanced
```

### Manual IOPS Configuration

If automatic detection fails, manually set IOPS values:

```bash
# Set IOPS for specific OSD
ceph config set osd.X osd_mclock_max_capacity_iops_hdd 200

# Set globally for all HDDs
ceph config set global osd_mclock_max_capacity_iops_hdd 200
```

## Monitoring Performance During Operations

### Real-time I/O Statistics

Monitor cluster I/O in real-time:

```console
root@harlan:~# ceph iostat -p 5
+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+
|                    Read |                   Write |                   Total |               Read IOPS |              Write IOPS |              Total IOPS |
+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+-------------------------+
|                   0 B/s |                   0 B/s |                   0 B/s |                       0 |                       0 |                       0 |
```

During active rebalancing, you should see significant write activity as data moves between OSDs.

### Performance Monitoring Commands

```bash
# Check cluster performance
ceph status
ceph osd perf

# Monitor individual OSD performance
ceph daemon osd.X perf dump

# Check rebalancing progress
ceph pg dump | grep active+clean
```

## Lessons Learned

### What Worked

1. **mClock profiles are better than manual tuning**: Use `high_recovery_ops` during rebalancing
2. **Consistent hardware helps**: Try to use similar USB drives across OSDs
3. **Monitor during changes**: Watch performance metrics when adding OSDs
4. **Patience with USB storage**: Accept that USB drives will be slower than enterprise SSDs

### What Didn't Work

1. **Ignoring mClock settings**: Missing IOPS values significantly impact performance
2. **Mixing drive types**: Different USB drives create performance imbalances
3. **Expecting SSD performance**: USB drives have inherent limitations

### Performance Bottlenecks Identified

1. **USB interface limitations**: Even USB 3.0 struggles with Ceph's I/O patterns
2. **Network bandwidth**: 1Gbps networking can become a bottleneck
3. **CPU constraints**: Dell Wyse 3040s have limited processing power
4. **Memory pressure**: 2GB RAM is tight for Ceph operations

## Recommendations for Homelab Ceph

### Hardware Considerations

1. **Use consistent USB drives**: Same model/manufacturer when possible
2. **Prefer USB 3.1/3.2**: Better performance than USB 3.0
3. **Consider USB-C interfaces**: Often have better controllers
4. **Monitor drive health**: USB drives can fail without warning

### Configuration Best Practices

1. **Set appropriate mClock profiles**: Use `high_recovery_ops` during maintenance
2. **Monitor IOPS settings**: Ensure all OSDs have proper capacity values
3. **Plan rebalancing windows**: USB storage makes operations slower
4. **Use [optimized scrubbing schedules](/proxmox-ceph-homelab-settings/)**: Reduce wear on USB drives

### Performance Expectations

- **Sequential throughput**: 20-40 MB/s per USB drive
- **Random IOPS**: 100-300 IOPS per USB drive  
- **Rebalancing time**: Plan for 2-3x longer than SSD-based clusters
- **Recovery operations**: Expect slower rebuild times after failures

## Conclusion

Optimizing Ceph performance in a homelab requires understanding the limitations of your hardware and adjusting expectations accordingly. While USB storage will never match enterprise SSD performance, proper mClock configuration and realistic expectations can deliver a functional distributed storage system.

Key takeaways:

- Use mClock profiles instead of manual parameter tuning
- Monitor and correct missing IOPS capacity values
- Accept USB storage limitations but optimize within those constraints
- Plan maintenance windows appropriately for slower operations

The performance may not be enterprise-grade, but for homelab use cases like media storage, backup, and learning Ceph administration, USB-based clusters can provide valuable experience with distributed storage concepts.

For more Ceph optimization guidance, see my articles on [Ceph nearfull management](/proxmox-ceph-nearfull/) and [ProxMox 8.2.4 Upgrade on Dell Wyse 3040s](/proxmox-8-dell-wyse-3040-upgrade/).

## References

- [Ceph mClock Configuration Reference](https://docs.ceph.com/en/reef/rados/configuration/mclock-config-ref/)
- [dmClock Algorithm Paper](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Gulati.pdf)
- [Proxmox Forum: mClock IOPS Issues](https://forum.proxmox.com/threads/when-adding-a-new-osd-to-ceph-the-osd_mclock_max_capacity_iops_-hdd-ssd-values-do-not-appear-in-the-configuration-database.129132/post-697088)
- [IBM Ceph OSD Capacity Determination](https://www.ibm.com/docs/en/storage-ceph/7?topic=scheduler-ceph-osd-capacity-determination)