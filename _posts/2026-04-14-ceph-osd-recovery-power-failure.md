---
title: "Ceph OSD Recovery After Power Failure: SAN Switch Was Dead the Whole Time"
layout: post
categories: [proxmox, ceph, homelab, networking]
tags: [proxmox, ceph, osd, debugging, homelab, storage, networking, bluestore, power-failure, dell-optiplex-990]
excerpt: "A power outage knocked my Ceph cluster from 15 healthy OSDs down to 4. The recovery took days of debugging — heartbeat cascades, a ceph.conf misconfiguration, and a dead SAN switch hiding behind NO-CARRIER flags on every node."
description: "Recovering a Proxmox Ceph cluster after power failure. Covers OSD failure cascades, ceph.conf network misconfiguration (host IP vs network CIDR), dead SAN switch diagnosis via NO-CARRIER, staged flag removal, and heartbeat timeout tuning for homelab clusters."
date: 2026-04-14
last_modified_at: 2026-04-14
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-14
  date_modified: 2026-04-14
---

Multiple hard power hits at my house took down the entire AlteredCarbon Proxmox cluster. My UPS wasn't configured for graceful shutdowns — entirely my fault. Like backups, power protection is something you relearn when you have an event.

What followed was a multi-day debugging session that peeled back layer after layer of problems: OSD failures, a configuration error that had been silently lurking, heartbeat cascades that crashed OSDs faster than I could restart them, and ultimately a dead SAN switch that was the root cause of everything.

<!-- excerpt-end -->

## The Initial Damage

After the hard reboot, most of the cluster came back. But three OSDs refused to start — osd.5 and osd.8 on kovacs, and osd.6 on harlan.

My first move was to set all the Ceph maintenance flags to prevent the cluster from trying to heal itself while unstable:

```bash
ceph osd set noup,nodown,noout,noin,nobackfill,norebalance,norecover,noscrub,nodeep-scrub
```

This is the Ceph equivalent of "stop everything and let me think." With 12 of 15 OSDs up and 3x replication, the data was safe but degraded.

```console
root@kovacs:~# ceph osd tree
ID   CLASS  WEIGHT    TYPE NAME        STATUS  REWEIGHT  PRI-AFF
 -1         68.22578  root default
 -3         13.64516      host harlan
  0    hdd   4.54839          osd.0        up   1.00000  1.00000
  3    hdd   4.54839          osd.3        up   1.00000  1.00000
  6    hdd   4.54839          osd.6      down   1.00000  1.00000
 -7         13.64516      host kovacs
  2    hdd   4.54839          osd.2        up   1.00000  1.00000
  5    hdd   4.54839          osd.5      down   1.00000  1.00000
  8    hdd   4.54839          osd.8      down   1.00000  1.00000
```

## First Recovery Attempt

On harlan, `ceph-volume lvm activate --all` brought osd.6 back. The drive activated cleanly, but this was a Seagate BUP Portable that had already been through a hard power cut — a warning sign I should have taken more seriously. It would [fail completely four months later](/zfs-ceph-overlapping-failures/). But for now, it was working. Kovacs was a different story. The `lsblk` output told the story — osd.5 and osd.8's backing USB drives weren't even visible. The drives had disconnected during the power event and didn't re-enumerate on boot.

After physically reseating the USB cables and rebooting kovacs, only one of the two drives came back. osd.5 and osd.8 were permanently gone — the USB-to-SATA bridges in those Seagate enclosures had died.

I removed the dead OSDs from the cluster:

```bash
ceph osd out osd.5 osd.8
ceph osd down osd.5 osd.8
ceph osd crush rm osd.5
ceph osd crush rm osd.8
ceph auth del osd.5
ceph auth del osd.8
ceph osd rm osd.5 osd.8
```

Down to 13 OSDs across 5 hosts. Still functional with 3x replication, but I needed to start removing the maintenance flags to let Ceph heal.

## The Cluster Regression

This is where things went sideways. I started removing flags in stages — `noin` first, then `noup` and `nodown`. When I got to removing `noout` and `norecover`, the cluster collapsed. OSDs started reporting each other as failed in a cascade:

```console
osd.1 reported failed by osd.13
osd.2 reported failed by osd.13
osd.3 reported failed by osd.13
osd.1 reported failed by osd.6
osd.2 reported failed by osd.9
```

Within minutes, I went from 13 OSDs up to **4**. Only osd.1, osd.4, osd.7 (all on poe) and osd.10 (quell) survived. Three entire hosts — harlan, edgar, and kovacs — had all their OSDs down.

I immediately re-enabled the safety flags and started investigating.

## The Configuration Error

Digging into the OSD logs revealed heartbeat failures everywhere. OSDs couldn't communicate with each other reliably. I checked the Ceph configuration:

```console
root@harlan:~# cat /etc/pve/ceph.conf | grep network
cluster_network = 10.10.10.11/23
public_network = 192.168.86.11/23
```

**Those are host IPs, not network addresses.** The correct configuration should be:

```ini
cluster_network = 10.10.10.0/23
public_network = 192.168.86.0/23
```

This had been wrong since the cluster was set up, but it worked by accident — Ceph is somewhat forgiving about network definitions as long as the host IP falls within the specified CIDR range. Under normal conditions, the OSDs could still find each other. But under the stress of a recovery with 13 OSDs trying to peer simultaneously, the slightly wrong network definitions contributed to the instability.

I fixed the configuration in `/etc/pve/ceph.conf` (which is shared across all nodes via pmxcfs) and restarted Ceph services cluster-wide using a custom cssh script:

```bash
./cssh "systemctl restart ceph.target"
```

This brought us back to 13 OSDs. But two on poe (osd.1 and osd.4) kept going down. The heartbeat cascade was still happening.

## Heartbeat Tuning

The default Ceph heartbeat timeouts are aggressive for a homelab running on 2011-era Dell OptiPlex 990s with USB storage. During recovery, the I/O load from backfilling was causing OSDs to miss heartbeat deadlines, which triggered false failure reports, which caused more OSDs to go down, which increased load on the survivors.

I increased the timeouts significantly:

```bash
ceph config set osd osd_heartbeat_grace 120
ceph config set osd osd_heartbeat_interval 30
```

And throttled recovery to reduce I/O pressure:

```bash
ceph config set osd osd_recovery_max_active 1
ceph config set osd osd_max_backfills 1
```

I also temporarily disabled CephFS to remove the MDS metadata load:

```bash
ceph fs set cephfs down true
./cssh "systemctl stop ceph-mds.target"
```

Then restarted OSDs sequentially by host with 60-second delays between each, starting with the most stable nodes (quell, then edgar, then harlan, then poe, then kovacs).

This helped — but OSDs were still intermittently dropping. Something else was wrong.

## Root Cause: The SAN Switch Was Dead

I finally checked the SAN network directly:

```console
root@kovacs:~# ping -c 3 10.10.10.11
PING 10.10.10.11 (10.10.10.11) 56(84) bytes of data.
From 10.10.10.12 icmp_seq=1 Destination Host Unreachable
From 10.10.10.12 icmp_seq=2 Destination Host Unreachable
```

The entire 10.10.10.0/23 cluster network was unreachable. Checking the interfaces on every node:

```console
root@kovacs:~# ./cssh "hostname && ip route | grep 10.10.10"
poe       10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.13 linkdown
kovacs    10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.12 linkdown
harlan    10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.11 linkdown
quell     10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.16 linkdown
edgar     10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.14 linkdown
```

**Every single node showed `linkdown` on vmbr1.** The physical interfaces confirmed it:

```console
root@harlan:~# ip link show enp6s4
2: enp6s4: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast
   master vmbr1 state DOWN
```

`NO-CARRIER` means no physical link — the cable is unplugged, the switch port is dead, or the switch itself is dead. Since **all five nodes** showed NO-CARRIER simultaneously, the Netgear 8-port consumer switch that served as the SAN backbone had died during the power outage.

Each node had a different physical interface for the SAN bridge, which I had to map out:

| Node | SAN Interface | Bridge |
|------|--------------|--------|
| harlan | enp6s4 | vmbr1 |
| kovacs | enp6s4 | vmbr1 |
| poe | enp6s4 | vmbr1 |
| edgar | enp5s2f0 | vmbr1 |
| quell | enp5s2f1 | vmbr1 |

**The Netgear switch was the root cause of everything.** Without the cluster network, Ceph was trying to do all OSD replication over the public network (192.168.86.0/23), which shares bandwidth with management traffic, VM traffic, and CephFS client I/O. Under recovery load, this saturated the single 1GbE links and caused the heartbeat cascades.

## The Fix

I power-cycled the Netgear switch. After it came back, the links came up on all nodes:

```bash
# Bring up physical interfaces
ssh 192.168.86.12 "ip link set enp6s4 up"      # kovacs
ssh 192.168.86.14 "ip link set enp5s2f0 up"    # edgar
ssh 192.168.86.11 "ip link set enp6s4 up"      # harlan
ssh 192.168.86.13 "ip link set enp6s4 up"      # poe
ssh 192.168.86.16 "ip link set enp5s2f1 up"    # quell

# Bring up bridges
./cssh "ip link set vmbr1 up"

# Verify SAN connectivity
./cssh "ping -c 3 10.10.10.11"
```

With the SAN network restored, I restarted Ceph services and re-enabled CephFS:

```bash
./cssh "systemctl restart ceph.target"
ceph fs set cephfs down false
./cssh "systemctl enable ceph-mds.target"
./cssh "systemctl start ceph-mds.target"
```

## Staged Flag Removal

With the SAN network back and all 13 OSDs stable, I removed the maintenance flags in stages. This is the procedure I'd recommend for any Ceph cluster recovering from a major incident:

### Stage 1: Basic Operations (Low Risk)

```bash
ceph osd unset noin
# Wait 5-10 minutes, verify stability
```

### Stage 2: OSD State Changes (Medium Risk)

```bash
ceph osd unset noup
ceph osd unset nodown
# Wait 10-15 minutes
```

### Stage 3: Data Movement (High Risk)

```bash
ceph osd unset noout
# Wait 15-20 minutes, watch for OSD crashes
```

### Stage 4: Recovery Operations (Highest Risk)

```bash
ceph osd unset norecover
# Wait 20-30 minutes

ceph osd unset nobackfill
# Wait 20-30 minutes

ceph osd unset norebalance
# Wait 20-30 minutes
```

### Stage 5: Maintenance Operations

```bash
ceph osd unset noscrub
ceph osd unset nodeep-scrub
```

### Emergency Rollback

If OSDs start cascading at any stage:

```bash
ceph osd set noout
ceph osd set norecover
ceph osd set nobackfill
ceph osd set norebalance
```

After completing all stages, I reset the heartbeat timeouts to defaults:

```bash
ceph config rm osd osd_heartbeat_grace
ceph config rm osd osd_heartbeat_interval
```

The cluster stabilized at 13 OSDs with the two dead kovacs drives removed. Recovery completed over the next several hours as Ceph re-replicated data across the remaining OSDs.

## Aftermath

The `noout,norebalance` flags I set during this incident stayed set for weeks afterward — I left them as a safety net while monitoring stability. This turned out to be a mistake: when [another OSD failure hit harlan months later](/zfs-ceph-overlapping-failures/), those forgotten flags masked the problem and prevented Ceph from self-healing.

The Netgear switch that caused this entire incident is an unmanaged consumer switch that hangs every 4-6 months and requires a power cycle. As an immediate fix, I replaced the intermittently working 5-port Netgear (along with a label on it about failures) with a more reliable 8-port Netgear I had on hand — this also opened up SAN ports on all Proxmox nodes instead of just the original five. The long-term fix is an HP ProCurve 2810 (managed, LACP-capable) that's ready to deploy as part of the [pre-Kubernetes infrastructure work](/proxmox-ceph-guide/).

## Lessons Learned

1. **Check the physical network first.** I spent hours debugging Ceph configuration and heartbeat tuning when the actual problem was a dead switch. A simple `ip route | grep linkdown` would have found it immediately.

2. **`NO-CARRIER` on all nodes = switch is dead.** If every node shows NO-CARRIER on the same bridge, the common element is the switch, not the individual NICs or cables.

3. **Ceph.conf network entries should be network addresses, not host IPs.** Use `192.168.86.0/23` not `192.168.86.11/23`. Ceph tolerates the wrong format under normal conditions but it contributes to instability under load.

4. **Staged flag removal prevents cascades.** Removing all maintenance flags at once can overwhelm a recovering cluster. The staged approach with monitoring between each step is essential.

5. **Increase heartbeat timeouts on homelab hardware.** The defaults assume enterprise SSDs and 10GbE networking. USB HDDs on 1GbE with a consumer switch need more generous timeouts during recovery.

6. **Disable CephFS during OSD recovery.** MDS metadata operations add load that can tip an unstable cluster over the edge. Bring it back after OSDs are stable.

7. **Don't forget to remove maintenance flags.** Set a calendar reminder. Forgotten `noout,norebalance` flags prevent Ceph from self-healing when the next failure hits.

8. **Replace consumer network hardware.** Unmanaged switches with no monitoring, no LACP, and a tendency to hang are a liability for storage networks. This was the most expensive lesson — not in dollars, but in debugging hours.

## Related Posts

- [When ZFS and Ceph Problems Collide](/zfs-ceph-overlapping-failures/) — The sequel: forgotten maintenance flags from this incident masked a new OSD failure months later
- [Monitoring ZFS Boot Mirror Health in Proxmox 8 Clusters](/proxmox-zfs-boot-mirror-smart-analysis/) — SMART monitoring across the cluster
- [Managing Ceph Nearfull Warnings in Proxmox Homelab](/proxmox-ceph-nearfull/) — Capacity management when running degraded
- [Optimizing Ceph Performance in Proxmox Homelab](/proxmox-ceph-performance/) — mClock tuning and USB 3.0 storage realities on the same hardware
- [Enabling SMART Monitoring on Seagate USB Drives](/usb-drive-smart/) — Monitoring the exact USB drives that failed in this incident
- [Aggregated Network Connections with LAG/LACP](/lag-lacp-and-other-network-terms/) — The LACP bonding planned for the ProCurve 2810 SAN switch replacement
- [Proxmox 8 Lessons Learned](/proxmox-8-lessons-learned/) — Broader lessons from running this cluster
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — All Proxmox and Ceph articles

## References

- [Ceph OSD Maintenance Flags](https://docs.ceph.com/en/reef/rados/troubleshooting/troubleshooting-osd/#stopping-w-out-rebalancing)
- [Ceph Network Configuration](https://docs.ceph.com/en/reef/rados/configuration/network-config-ref/)
- [Ceph BlueStore Configuration](https://docs.ceph.com/en/reef/rados/configuration/bluestore-config-ref/)
