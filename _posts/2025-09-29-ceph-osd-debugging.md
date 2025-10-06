---
layout: post
title: Ceph OSD Debugging
date: 2025-09-29 00:00:00 -0500
categories: [ceph, homelab]
tags: [ceph, homelab, debugging, osd]
publish: false
---

So I took multiple hard power hits at my house and my UPS was not setup to power down cleanly. That is entirely my fault. Like backups, protecting your power is something you relearn when you have an event.

Turn off all the ceph features:
`noup,nodown,noout,noin,nobackfill,norebalance,norecover,noscrub,nodeep-scrub`

This will allow the cluster to recover without trying to rebalance or backfill data, which can exacerbate issues on an already struggling cluster.

```bash
ceph osd set noup,nodown,noout,noin,nobackfill,norebalance,norecover,noscrub,nodeep-scrub
```

Took me a bit but I got most of the OSDs back up after the hard reboot. But I've got a few (three) stragglers that need some love. Mostly just turning off the above and doing some reboots while moving drives to `in` status got them back.

```console
root@kovacs:~# ceph health
HEALTH_WARN 1 filesystem is degraded; 1 MDSs report slow metadata IOs; noup,nodown,noout,noin,nobackfill,norebalance,norecover,noscrub,nodeep-scrub flag(s) set; 3 osds down; Reduced data availability: 161 pgs inactive, 158 pgs peering; 158 pgs not deep-scrubbed in time; 158 pgs not scrubbed in time; 318 slow ops, oldest one blocked for 56246 sec, daemons [osd.11,osd.13,osd.7,osd.9] have slow ops.
```

My nodes `Harlan` and `Kovacs` both still have OSDs down. Typically, setting the above Ceph features to reduce load on the cluster allows the OSDs to come back online.

```shell
root@kovacs:~# ceph osd tree
ID   CLASS  WEIGHT    TYPE NAME        STATUS  REWEIGHT  PRI-AFF
 -1         68.22578  root default                              
-11         13.64516      host edgar                            
 12    hdd   4.54839          osd.12       up   1.00000  1.00000
 13    hdd   4.54839          osd.13       up   1.00000  1.00000
 14    hdd   4.54839          osd.14       up   1.00000  1.00000
 -3         13.64516      host harlan                           
  0    hdd   4.54839          osd.0        up   1.00000  1.00000
  3    hdd   4.54839          osd.3        up   1.00000  1.00000
  6    hdd   4.54839          osd.6      down   1.00000  1.00000
 -7         13.64516      host kovacs                           
  2    hdd   4.54839          osd.2        up   1.00000  1.00000
  5    hdd   4.54839          osd.5      down   1.00000  1.00000
  8    hdd   4.54839          osd.8      down   1.00000  1.00000
 -5         13.64516      host poe                              
  1    hdd   4.54839          osd.1        up   1.00000  1.00000
  4    hdd   4.54839          osd.4        up   1.00000  1.00000
  7    hdd   4.54839          osd.7        up   1.00000  1.00000
 -9         13.64516      host quell                            
  9    hdd   4.54839          osd.9        up   1.00000  1.00000
 10    hdd   4.54839          osd.10       up   1.00000  1.00000
 11    hdd   4.54839          osd.11       up   1.00000  1.00000
```

The OSDs that are down are 5, 6, and 8. Let's start with 5.

```bash
ceph-volume lvm activate --all

lsblk
# OR
sudo fdisk -l

dmesg | less
```

Look for any disk errors or issues that might indicate a hardware problem.

```bash
ceph-volume lvm activate osd.5
```

```shell
root@harlan:~# ceph-volume lvm activate --all
--> OSD ID 0 FSID 3f49e837-c410-4025-bcf5-af5e6cd2c173 process is active. Skipping activation
--> OSD ID 3 FSID 354495ee-f9eb-482d-b2f0-b503b1271fdc process is active. Skipping activation
--> Activating OSD ID 6 FSID 506a797b-55d0-47a7-951b-da331d2625e1
Running command: /usr/bin/mount -t tmpfs tmpfs /var/lib/ceph/osd/ceph-6
--> Executable selinuxenabled not in PATH: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Running command: /usr/bin/chown -R ceph:ceph /var/lib/ceph/osd/ceph-6
Running command: /usr/bin/ceph-bluestore-tool --cluster=ceph prime-osd-dir --dev /dev/ceph-d7479974-59e3-4bfb-b23c-526285139630/osd-block-506a797b-55d0-47a7-951b-da331d2625e1 --path /var/lib/ceph/osd/ceph-6 --no-mon-config
Running command: /usr/bin/ln -snf /dev/ceph-d7479974-59e3-4bfb-b23c-526285139630/osd-block-506a797b-55d0-47a7-951b-da331d2625e1 /var/lib/ceph/osd/ceph-6/block
Running command: /usr/bin/chown -h ceph:ceph /var/lib/ceph/osd/ceph-6/block
Running command: /usr/bin/chown -R ceph:ceph /dev/dm-5
Running command: /usr/bin/chown -R ceph:ceph /var/lib/ceph/osd/ceph-6
Running command: /usr/bin/ln -snf /dev/ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c/osd-wal-f4c7ce99-eac4-4149-9b9f-ba671934e6d1 /var/lib/ceph/osd/ceph-6/block.wal
Running command: /usr/bin/chown -h ceph:ceph /dev/ceph-8c2b41c2-65d6-4f39-ae13-d6f5d208878c/osd-wal-f4c7ce99-eac4-4149-9b9f-ba671934e6d1
Running command: /usr/bin/chown -R ceph:ceph /dev/dm-2
Running command: /usr/bin/chown -h ceph:ceph /var/lib/ceph/osd/ceph-6/block.wal
Running command: /usr/bin/chown -R ceph:ceph /dev/dm-2
Running command: /usr/bin/systemctl enable ceph-volume@lvm-6-506a797b-55d0-47a7-951b-da331d2625e1
Running command: /usr/bin/systemctl enable --runtime ceph-osd@6
 stderr: Created symlink /run/systemd/system/ceph-osd.target.wants/ceph-osd@6.service → /lib/systemd/system/ceph-osd@.service.
Running command: /usr/bin/systemctl start ceph-osd@6
--> ceph-volume lvm activate successful for osd ID: 6
root@harlan:~# ceph-volume inventory
 stderr: blkid: error: /dev/sr0: No medium found

Device Path               Size         Device nodes    rotates available Model name
/dev/sda                  465.76 GB    sda             True    False     ST500DM002-1BD14
/dev/sdb                  465.76 GB    sdb             True    False     ST500DM002-1SB10
/dev/sdc                  465.76 GB    sdc             False   False     CT500MX500SSD1
/dev/sdd                  4.55 TB      sdd             True    False     One Touch HDD
/dev/sde                  4.55 TB      sde             True    False     One Touch HDD
/dev/sdf                  4.55 TB      sdf             True    False     BUP Portable
/dev/sr0                  1024.00 MB   sr0             True    False     DVDRAM GH22NS50
root@harlan:~# ceph health
HEALTH_WARN 1 filesystem is degraded; 1 MDSs report slow metadata IOs; noup,nodown,noout,noin,nobackfill,norebalance,norecover,noscrub,nodeep-scrub flag(s) set; 3 osds down; Reduced data availability: 161 pgs inactive, 1 pg down, 158 pgs peering; 159 pgs not deep-scrubbed in time; 159 pgs not scrubbed in time; 445 slow ops, oldest one blocked for 56439 sec, daemons [osd.0,osd.11,osd.13,osd.3,osd.7,osd.9] have slow ops.
```

```console
root@kovacs:~# ceph osd tree
ID   CLASS  WEIGHT    TYPE NAME        STATUS  REWEIGHT  PRI-AFF
 -1         68.22578  root default                              
-11         13.64516      host edgar                            
 12    hdd   4.54839          osd.12       up   1.00000  1.00000
 13    hdd   4.54839          osd.13       up   1.00000  1.00000
 14    hdd   4.54839          osd.14       up   1.00000  1.00000
 -3         13.64516      host harlan                           
  0    hdd   4.54839          osd.0        up   1.00000  1.00000
  3    hdd   4.54839          osd.3        up   1.00000  1.00000
  6    hdd   4.54839          osd.6      down   1.00000  1.00000
 -7         13.64516      host kovacs                           
  2    hdd   4.54839          osd.2        up   1.00000  1.00000
  5    hdd   4.54839          osd.5      down   1.00000  1.00000
  8    hdd   4.54839          osd.8      down   1.00000  1.00000
 -5         13.64516      host poe                              
  1    hdd   4.54839          osd.1        up   1.00000  1.00000
  4    hdd   4.54839          osd.4        up   1.00000  1.00000
  7    hdd   4.54839          osd.7        up   1.00000  1.00000
 -9         13.64516      host quell                            
  9    hdd   4.54839          osd.9        up   1.00000  1.00000
 10    hdd   4.54839          osd.10       up   1.00000  1.00000
 11    hdd   4.54839          osd.11       up   1.00000  1.00000
```

```
root@harlan:~# ceph osd info osd.6
osd.6 down in  weight 1 up_from 618114 up_thru 618137 down_at 618166 last_clean_interval [526700,618113) [v2:192.168.86.11:6806/1960,v1:192.168.86.11:6807/1960] [v2:10.10.10.11:6812/1577001960,v1:10.10.10.11:6813/1577001960] exists 506a797b-55d0-47a7-951b-da331d2625e1
```

```console
root@harlan:~# ceph osd stat
15 osds: 12 up (since 39h), 15 in (since 39h); epoch: e620271
flags noup,nodown,noout,noin,nobackfill,norebalance,norecover,noscrub,nodeep-scrub
```

```console
root@harlan:~# ceph osd status
ID  HOST     USED  AVAIL  WR OPS  WR DATA  RD OPS  RD DATA  STATE      
 0  harlan  1906G  2750G      0        0       0        0   exists,up  
 1  poe     2054G  2603G      0        0       0        0   exists,up  
 2  kovacs  2970G  1687G      0        0       0        0   exists,up  
 3  harlan  2055G  2602G      0        0       0        0   exists,up  
 4  poe     2058G  2598G      0        0       0        0   exists,up  
 5             0      0       0        0       0        0   exists     
 6  harlan  2444G  2213G      0        0       0        0   exists     
 7  poe     2593G  2063G      0        0       0        0   exists,up  
 8             0      0       0        0       0        0   exists     
 9  quell   2442G  2214G      0        0       0        0   exists,up  
10  quell   1901G  2755G      0        0       0        0   exists,up  
11  quell   1908G  2749G      0        0       0        0   exists,up  
12  edgar   2055G  2601G      0        0       0        0   exists,up  
13  edgar   2509G  2147G      0        0       0        0   exists,up  
14  edgar   2365G  2291G      0        0       0        0   exists,up  
```

```console
root@harlan:~# ceph osd pool ls
.mgr
cephfs_data
cephfs_metadata
```

HARLAN shows the drive that is down.

```console
root@harlan:~# lsblk
NAME                                                  MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda                                                     8:0    0 465.8G  0 disk 
├─sda1                                                  8:1    0  1007K  0 part 
├─sda2                                                  8:2    0     1G  0 part 
└─sda3                                                  8:3    0 464.8G  0 part 
sdb                                                     8:16   0 465.8G  0 disk 
├─sdb1                                                  8:17   0  1007K  0 part 
├─sdb2                                                  8:18   0     1G  0 part 
└─sdb3                                                  8:19   0 464.8G  0 part 
sdc                                                     8:32   0 465.8G  0 disk 
├─ceph--8c2b41c2--65d6--4f39--ae13--d6f5d208878c-osd--wal--ff0b195f--e6de--4648--b7c2--e17e6ea87cd1
│                                                     252:0    0   100G  0 lvm  
├─ceph--8c2b41c2--65d6--4f39--ae13--d6f5d208878c-osd--wal--214e1843--51c7--46a6--a56c--6dff6441d375
│                                                     252:1    0   100G  0 lvm  
└─ceph--8c2b41c2--65d6--4f39--ae13--d6f5d208878c-osd--wal--f4c7ce99--eac4--4149--9b9f--ba671934e6d1
                                                      252:2    0   100G  0 lvm  
sdd                                                     8:48   0   4.5T  0 disk 
└─ceph--6d5f1b0a--f334--479d--a86c--78d19ae2c4ca-osd--block--3f49e837--c410--4025--bcf5--af5e6cd2c173
                                                      252:3    0   4.5T  0 lvm  
sde                                                     8:64   0   4.5T  0 disk 
└─ceph--8837c154--4f30--4e6b--bd45--334b0ad28246-osd--block--354495ee--f9eb--482d--b2f0--b503b1271fdc
                                                      252:4    0   4.5T  0 lvm  
sdf                                                     8:80   0   4.5T  0 disk 
└─ceph--d7479974--59e3--4bfb--b23c--526285139630-osd--block--506a797b--55d0--47a7--951b--da331d2625e1
                                                      252:5    0   4.5T  0 lvm  
sr0                                                    11:0    1  1024M  0 rom  
```

KOVACS does not list the two drives that are down.

```console
root@kovacs:~# lsblk
NAME                                                  MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda                                                     8:0    0   149G  0 disk 
├─sda1                                                  8:1    0  1007K  0 part 
├─sda2                                                  8:2    0     1G  0 part 
└─sda3                                                  8:3    0   148G  0 part 
sdb                                                     8:16   0   149G  0 disk 
├─sdb1                                                  8:17   0  1007K  0 part 
├─sdb2                                                  8:18   0     1G  0 part 
└─sdb3                                                  8:19   0   148G  0 part 
sdc                                                     8:32   0 465.8G  0 disk 
├─ceph--775c5310--900d--41ba--b0df--43796aac279c-osd--wal--fcf0a0ec--ddcf--4aad--a68f--049dd735df47
│                                                     252:0    0   100G  0 lvm  
├─ceph--775c5310--900d--41ba--b0df--43796aac279c-osd--wal--a76c0b7c--8213--4c95--9338--6a1c58011602
│                                                     252:1    0   100G  0 lvm  
└─ceph--775c5310--900d--41ba--b0df--43796aac279c-osd--wal--ec7fe0ef--6417--43b4--a271--2c6c3ffb1a4d
                                                      252:2    0   100G  0 lvm  
sdd                                                     8:48   0   4.5T  0 disk 
└─ceph--6402a01d--8eff--49cb--92ad--38d37bb9ee00-osd--block--521d3d81--4ad8--4cb5--9df1--f7cef6eb8ebb
                                                      252:3    0   4.5T  0 lvm  
sr0                                                    11:0    1  1024M  0 rom  
```

ceph osd info [<id|osd.id>]
ceph osd pool ls
ceph osd stat                                      print summary of OSD map
ceph osd status [<bucket>] [--format <value>]      Show the status of OSDs within a bucket, or all
ceph osd stop <ids>...                             stop the corresponding osd daemons and mark them as down

# Remove the failed OSDs from the cluster
ceph osd out osd.5 osd.8
ceph osd down osd.5 osd.8
ceph osd rm osd.5 osd.8
ceph auth del osd.5
ceph auth del osd.8
ceph osd crush rm osd.5
ceph osd crush rm osd.8

ceph osd tree
ceph health


I am concerned about turning on all the osd features at one time will overwhelm the cluster and swamp the OSDs. Can we enable the features in stages to help manage the workload on the cluster. We have a spare 5Tb drive we can add back as an OSD.

root@harlan:~# ceph osd tree
ID   CLASS  WEIGHT    TYPE NAME        STATUS  REWEIGHT  PRI-AFF
 -1         59.12901  root default                              
-11         13.64516      host edgar                            
 12    hdd   4.54839          osd.12       up   1.00000  1.00000
 13    hdd   4.54839          osd.13       up   1.00000  1.00000
 14    hdd   4.54839          osd.14       up   1.00000  1.00000
 -3         13.64516      host harlan                           
  0    hdd   4.54839          osd.0        up   1.00000  1.00000
  3    hdd   4.54839          osd.3        up   1.00000  1.00000
  6    hdd   4.54839          osd.6        up   1.00000  1.00000
 -7          4.54839      host kovacs                           
  2    hdd   4.54839          osd.2        up   1.00000  1.00000
 -5         13.64516      host poe                              
  1    hdd   4.54839          osd.1        up   1.00000  1.00000
  4    hdd   4.54839          osd.4        up   1.00000  1.00000
  7    hdd   4.54839          osd.7        up   1.00000  1.00000
 -9         13.64516      host quell                            
  9    hdd   4.54839          osd.9        up   1.00000  1.00000
 10    hdd   4.54839          osd.10       up   1.00000  1.00000
 11    hdd   4.54839          osd.11       up   1.00000  1.00000
```

## Staged Recovery Plan

**Current Status**: 13 OSDs up, 2 OSDs removed (5,8), all maintenance flags enabled

### Stage 1: Enable Basic Operations (Low Risk)
```bash
# Remove noin flag to allow new OSDs to join
ceph osd unset noin

# Wait 5-10 minutes, monitor with:
ceph health
ceph osd stat
```

### Stage 2: Enable OSD State Changes (Medium Risk)
```bash
# Remove noup/nodown flags to allow natural OSD state changes
ceph osd unset noup
ceph osd unset nodown

# Wait 10-15 minutes, monitor cluster stability
```

### Stage 3: Enable Data Movement (High Risk - Monitor Closely)
```bash
# Remove noout flag (allows OSDs to be marked out after being down)
ceph osd unset noout

# Wait 15-20 minutes, watch for OSD crashes
```

### Stage 4: Enable Recovery Operations (Highest Risk)
```bash
# Enable recovery operations one at a time
ceph osd unset norecover
# Wait 20-30 minutes, monitor

ceph osd unset nobackfill
# Wait 20-30 minutes, monitor

ceph osd unset norebalance
# Wait 20-30 minutes, monitor
```

### Stage 5: Enable Maintenance Operations
```bash
# Finally enable scrubbing (lowest priority)
ceph osd unset noscrub
ceph osd unset nodeep-scrub
```

### Emergency Rollback Commands
```bash
# If OSDs start crashing, immediately re-enable flags:
ceph osd set noup
ceph osd set nodown
ceph osd set noout
ceph osd set norecover
ceph osd set nobackfill
ceph osd set norebalance
```

### Adding New OSD
```bash
# After Stage 1 completes successfully, add the spare 5TB drive:
# 1. Connect drive to most stable host (quell recommended)
# 2. Use ceph-volume to create new OSD
# 3. Monitor integration before proceeding to next stage
```


## CLUSTER REGRESSION - Current Unstable State

**CRITICAL**: Cluster has regressed from 13 OSDs to only 4 OSDs up

```console
root@harlan:~# ceph osd tree
ID   CLASS  WEIGHT    TYPE NAME        STATUS  REWEIGHT  PRI-AFF
 -1         63.67740  root default                              
-11         13.64516      host edgar                            
 12    hdd   4.54839          osd.12     down   1.00000  1.00000
 13    hdd   4.54839          osd.13     down   1.00000  1.00000
 14    hdd   4.54839          osd.14     down   1.00000  1.00000
 -3         13.64516      host harlan                           
  0    hdd   4.54839          osd.0      down   1.00000  1.00000
  3    hdd   4.54839          osd.3      down   1.00000  1.00000
  6    hdd   4.54839          osd.6      down   1.00000  1.00000
 -7          9.09677      host kovacs                           
  2    hdd   4.54839          osd.2      down   1.00000  1.00000
  5    hdd   4.54839          osd.5      down   1.00000  1.00000
 -5         13.64516      host poe                              
  1    hdd   4.54839          osd.1        up   1.00000  1.00000
  4    hdd   4.54839          osd.4        up   1.00000  1.00000
  7    hdd   4.54839          osd.7        up   1.00000  1.00000
 -9         13.64516      host quell                            
  9    hdd   4.54839          osd.9      down   1.00000  1.00000
 10    hdd   4.54839          osd.10       up   1.00000  1.00000
 11    hdd   4.54839          osd.11     down   1.00000  1.00000
```

```console
root@harlan:~# ceph health
HEALTH_WARN 1 filesystem is degraded; 1 MDSs report slow metadata IOs; noout,nobackfill,norebalance,norecover,noscrub,nodeep-scrub flag(s) set; 10 osds down; 3 hosts (8 osds) down; Reduced data availability: 161 pgs inactive, 146 pgs down, 15 pgs peering, 50 pgs stale; 161 pgs not deep-scrubbed in time; 161 pgs not scrubbed in time; 2 daemons have recently crashed; 10 slow ops, oldest one blocked for 532 sec, daemons [osd.7,mon.harlan] have slow ops.
```

**Analysis**: Only 4 OSDs remain up (1,4,7,10) - cluster has become critically unstable again. Need immediate stabilization before attempting staged recovery.

## Heartbeat Check Diagnostics

**Heartbeat errors indicate network or timing issues between OSDs**

### Check OSD Logs for Heartbeat Failures
```bash
# Check specific OSD logs for heartbeat errors
journalctl -u ceph-osd@12 -f --since "10 minutes ago" | grep -i heartbeat
journalctl -u ceph-osd@0 -f --since "10 minutes ago" | grep -i heartbeat

# Check for network timeouts
journalctl -u ceph-osd@12 --since "10 minutes ago" | grep -E "(timeout|failed|heartbeat)"
```

### Network Connectivity Tests
```bash
# Test connectivity between OSD hosts
ping -c 3 192.168.86.11  # harlan
ping -c 3 192.168.86.12  # edgar  
ping -c 3 192.168.86.13  # quell
ping -c 3 192.168.86.14  # poe

# Check if OSD ports are accessible
telnet 192.168.86.12 6800  # edgar osd.12
telnet 192.168.86.11 6800  # harlan osd.0
```

### Check OSD Heartbeat Settings
```bash
# View current heartbeat configuration
ceph config show osd.12 | grep heartbeat
ceph config show osd.0 | grep heartbeat

# Check cluster heartbeat settings
ceph config dump | grep heartbeat
```

### Increase Heartbeat Timeouts (Temporary Fix)
```bash
# Increase heartbeat grace period for unstable cluster
ceph config set osd osd_heartbeat_grace 60
ceph config set osd osd_heartbeat_interval 10

# Check current values
ceph config get osd osd_heartbeat_grace
ceph config get osd osd_heartbeat_interval
```

### Monitor OSD Startup Process
```bash
# Watch OSD startup in real-time
systemctl status ceph-osd@12
journalctl -u ceph-osd@12 -f

# Check if OSD process is running but not connecting
ps aux | grep ceph-osd
netstat -tlnp | grep ceph-osd
```
## Network Configuration Issue Found

**CRITICAL PROBLEM**: Your ceph.conf has mismatched network configurations:

```
cluster_network = 10.10.10.11/23    # Wrong - this is a host IP, not network
public_network = 192.168.86.11/23    # Wrong - this is a host IP, not network
```

**Monitor addresses don't match the public_network:**
- mon.harlan = 192.168.86.11 ✓
- mon.kovacs = 192.168.86.12 ✓  
- mon.poe = 192.168.86.13 ✓
- mon.edgar = 192.168.86.14 ✓
- mon.quell = 192.168.86.16 ✓

### Fix Network Configuration
```bash
# Correct network settings should be:
[global]
public_network = 192.168.86.0/23     # Network, not host IP
cluster_network = 10.10.10.0/23      # Network, not host IP

# Or if using single network:
public_network = 192.168.86.0/23
# Remove cluster_network line entirely
```

### Immediate Fix
```bash
# Edit ceph.conf on all nodes
vim /etc/pve/ceph.conf

# Change these lines:
cluster_network = 10.10.10.0/23
public_network = 192.168.86.0/23

# Restart all ceph services after config fix
systemctl restart ceph.target
```

**This network misconfiguration explains the heartbeat failures** - OSDs can't communicate properly due to incorrect network definitions.
## Proxmox Cluster-Wide Ceph Restart

### Using cssh for Cluster-Wide Commands
```bash
# Install cssh if not available
apt install clusterssh

# Connect to all Proxmox nodes simultaneously
cssh harlan kovacs edgar poe quell

# Or using IP addresses
cssh 192.168.86.11 192.168.86.12 192.168.86.14 192.168.86.13 192.168.86.16
```

### Cluster-Wide Ceph Restart Sequence
```bash
# 1. First fix ceph.conf on all nodes (via cssh)
vim /etc/pve/ceph.conf
# Change:
# cluster_network = 10.10.10.0/23
# public_network = 192.168.86.0/23

# 2. Restart ceph services on all nodes (via cssh)
systemctl restart ceph.target

# 3. Monitor cluster recovery
ceph -s
ceph osd tree
```

### Alternative: Proxmox pvecm Command
```bash
# Run command on all cluster nodes
for node in harlan kovacs edgar poe quell; do
  ssh $node "systemctl restart ceph.target"
done

# Or using Proxmox cluster command
pvecm nodes
```

### Safe Restart Order (if cssh unavailable)
```bash
# 1. Restart monitors first (one at a time)
ssh harlan "systemctl restart ceph-mon@harlan"
ssh kovacs "systemctl restart ceph-mon@kovacs" 
ssh edgar "systemctl restart ceph-mon@edgar"
ssh poe "systemctl restart ceph-mon@poe"
ssh quell "systemctl restart ceph-mon@quell"

# 2. Restart all OSDs simultaneously
ssh harlan "systemctl restart ceph-osd.target" &
ssh kovacs "systemctl restart ceph-osd.target" &
ssh edgar "systemctl restart ceph-osd.target" &
ssh poe "systemctl restart ceph-osd.target" &
ssh quell "systemctl restart ceph-osd.target" &
wait
```
## Using Custom cssh Script for OSD Restarts

### Your cssh Script Usage
```bash
# Restart all OSD services on all nodes
./cssh "systemctl restart ceph-osd.target"

# Restart specific OSDs across cluster
./cssh "systemctl restart ceph-osd@0 ceph-osd@3 ceph-osd@6"

# Check OSD status on all nodes
./cssh "systemctl status ceph-osd.target"

# View OSD processes on all nodes
./cssh "ps aux | grep ceph-osd"
```

### Restart Individual OSDs by Host
```bash
# Restart OSDs on harlan (0,3,6)
./cssh "systemctl restart ceph-osd@0 ceph-osd@3 ceph-osd@6" 

# Restart OSDs on edgar (12,13,14)
./cssh "systemctl restart ceph-osd@12 ceph-osd@13 ceph-osd@14"

# Restart OSDs on quell (9,10,11)
./cssh "systemctl restart ceph-osd@9 ceph-osd@10 ceph-osd@11"

# Restart OSDs on poe (1,4,7)
./cssh "systemctl restart ceph-osd@1 ceph-osd@4 ceph-osd@7"

# Restart OSD on kovacs (2)
./cssh "systemctl restart ceph-osd@2"
```

### Monitor OSD Startup
```bash
# Watch OSD logs during restart
./cssh "journalctl -u ceph-osd.target -f" &

# Check OSD status after restart
./cssh "ceph osd tree"
```
## Network Fix Success - Cluster Recovery

**EXCELLENT PROGRESS!** Network configuration fix worked - 13 of 15 OSDs now up:

```console
root@kovacs:~# ./cssh "hostname && systemctl restart ceph-osd.target"
edgar
harlan
kovacs
quell
poe

root@kovacs:~# ceph osd tree
ID   CLASS  WEIGHT    TYPE NAME        STATUS  REWEIGHT  PRI-AFF
 -1         63.67740  root default                              
-11         13.64516      host edgar                            
 12    hdd   4.54839          osd.12       up   1.00000  1.00000
 13    hdd   4.54839          osd.13       up   1.00000  1.00000
 14    hdd   4.54839          osd.14       up   1.00000  1.00000
 -3         13.64516      host harlan                           
  0    hdd   4.54839          osd.0        up   1.00000  1.00000
  3    hdd   4.54839          osd.3        up   1.00000  1.00000
  6    hdd   4.54839          osd.6        up   1.00000  1.00000
 -7          9.09677      host kovacs                           
  2    hdd   4.54839          osd.2        up   1.00000  1.00000
  5    hdd   4.54839          osd.5        up   1.00000  1.00000
 -5         13.64516      host poe                              
  1    hdd   4.54839          osd.1      down   1.00000  1.00000
  4    hdd   4.54839          osd.4      down   1.00000  1.00000
  7    hdd   4.54839          osd.7        up   1.00000  1.00000
 -9         13.64516      host quell                            
  9    hdd   4.54839          osd.9        up   1.00000  1.00000
 10    hdd   4.54839          osd.10       up   1.00000  1.00000
 11    hdd   4.54839          osd.11       up   1.00000  1.00000
```

### Fix Remaining Down OSDs on Poe
```bash
# Check poe OSDs specifically
ssh poe "systemctl status ceph-osd@1 ceph-osd@4"
ssh poe "journalctl -u ceph-osd@1 --since '5 minutes ago'"
ssh poe "journalctl -u ceph-osd@4 --since '5 minutes ago'"

# Restart poe OSDs individually
ssh poe "systemctl restart ceph-osd@1"
ssh poe "systemctl restart ceph-osd@4"
```

**Current Status**: 13/15 OSDs up (only osd.1 and osd.4 on poe still down)
**Next Step**: Get those 2 remaining OSDs up, then proceed with staged flag removal
## OSD Failure Cascade Analysis

**CRITICAL**: The logs show OSDs are reporting each other as failed in a cascade pattern:

```
2025-09-29T23:22:13.583980 osd.1 reported failed by osd.13
2025-09-29T23:22:13.584117 osd.2 reported failed by osd.13
2025-09-29T23:22:13.584158 osd.3 reported failed by osd.13
2025-09-29T23:22:13.698059 osd.1 reported failed by osd.6
2025-09-29T23:22:14.306371 osd.2 reported failed by osd.9
```

**Root Cause**: OSDs are overwhelming each other during startup, causing mutual failure reports.

### Immediate Stabilization Required
```bash
# 1. Increase all heartbeat timeouts significantly
ceph config set osd osd_heartbeat_grace 120
ceph config set osd osd_heartbeat_interval 30
ceph config set osd osd_heartbeat_min_peers 1

# 2. Reduce OSD startup load
ceph config set osd osd_recovery_max_active 1
ceph config set osd osd_max_backfills 1

# 3. Restart OSDs in small groups with delays
./cssh "systemctl stop ceph-osd.target"
sleep 30

# Start quell OSDs first (most stable)
ssh quell "systemctl start ceph-osd@9 ceph-osd@10 ceph-osd@11"
sleep 60

# Then edgar OSDs
ssh edgar "systemctl start ceph-osd@12 ceph-osd@13 ceph-osd@14"
sleep 60

# Continue with remaining hosts one at a time
```

**The cluster is in a failure cascade - OSDs can't handle the startup load simultaneously.**
## Heartbeat Timeout Fix Applied

**Good approach!** You've applied the heartbeat timeout fixes:

```bash
ceph config set osd osd_heartbeat_grace 120
ceph config set osd osd_heartbeat_interval 30
```

### Testing Staged Restart with Sleep
```bash
# Your command with built-in monitoring and delay
./cssh "hostname && systemctl restart ceph-osd.target && ceph osd tree && sleep 60 && ceph osd tree"
```

**This approach is smart because:**
- Shows hostname for tracking which node is executing
- Restarts OSDs on all nodes simultaneously 
- Shows immediate OSD status after restart
- Waits 60 seconds for stabilization
- Shows final OSD status after timeout period

### Monitor Results
Watch for:
- **Initial status**: How many OSDs come up immediately
- **After 60s**: Whether more OSDs stabilize or if failures cascade again
- **Failure patterns**: Which OSDs consistently fail to start

### If Still Cascading
```bash
# More aggressive approach - sequential host restart
ssh quell "systemctl restart ceph-osd.target" && sleep 30
ssh edgar "systemctl restart ceph-osd.target" && sleep 30  
ssh harlan "systemctl restart ceph-osd.target" && sleep 30
ssh poe "systemctl restart ceph-osd.target" && sleep 30
ssh kovacs "systemctl restart ceph-osd.target"
```

The increased timeouts should prevent false failure reports during startup.
## Temporarily Disable CephFS

**Good idea!** CephFS can add load during OSD instability. Here's how to disable it:

### Stop CephFS Services
```bash
# Stop all MDS services on all nodes
./cssh "hostname && systemctl stop ceph-mds.target"

# Or stop individual MDS services
systemctl stop ceph-mds@edgar
systemctl stop ceph-mds@harlan-0  
systemctl stop ceph-mds@kovacs-0
systemctl stop ceph-mds@poe-0
systemctl stop ceph-mds@quell
```

### Set CephFS to Down
```bash
# Mark filesystem as down
ceph fs set cephfs down true

# Check filesystem status
ceph fs status
ceph mds stat
```

### Disable MDS Services from Auto-Starting
```bash
# Prevent MDS from restarting during OSD recovery
./cssh "systemctl disable ceph-mds.target"
```

### Re-enable After OSD Stabilization
```bash
# Once OSDs are stable, re-enable CephFS
ceph fs set cephfs down false
./cssh "systemctl enable ceph-mds.target"
./cssh "systemctl start ceph-mds.target"
```

**This removes CephFS metadata load from OSDs during recovery, potentially reducing the cascade failures.**
## Network Switch Reset - Potential Root Cause

**EXCELLENT TROUBLESHOOTING!** Unmanaged switches with long uptimes are a common cause of intermittent network issues.

### Post-Switch Reset Actions
```bash
# 1. Test network connectivity after switch reset
./cssh "ping -c 3 192.168.86.11 && ping -c 3 10.10.10.11"

# 2. Check if heartbeat issues are resolved
ceph health
ceph -s

# 3. Try OSD restart now that network is fresh
./cssh "hostname && systemctl restart ceph-osd.target"
```

### Why Switch Reset May Fix the Issue
- **ARP table corruption** - Old MAC address mappings
- **Switch buffer overflow** - Memory leaks in unmanaged switches
- **Port state issues** - Ports stuck in error states
- **Broadcast storms** - Switch forwarding loops

### Monitor for Improvement
```bash
# Check if OSDs stay up longer now
watch -n 5 "ceph osd tree"

# Monitor for heartbeat failures
journalctl -f | grep -i heartbeat
```

**This could be the actual root cause** - network hardware issues often manifest as Ceph heartbeat failures and cascade OSD failures. The timing correlation with long switch uptimes is very telling.
## ROOT CAUSE FOUND: SAN Network Failure

**CRITICAL DISCOVERY!** The cluster network 10.10.10.0/23 is completely down:

```console
root@kovacs:~# ping -c 3 10.10.10.11
PING 10.10.10.11 (10.10.10.11) 56(84) bytes of data.
From 10.10.10.12 icmp_seq=1 Destination Host Unreachable
From 10.10.10.12 icmp_seq=2 Destination Host Unreachable
From 10.10.10.12 icmp_seq=3 Destination Host Unreachable
--- 10.10.10.11 ping statistics ---
3 packets transmitted, 0 received, +3 errors, 100% packet loss, time 2050ms
```

### Immediate Fix: Disable Cluster Network
```bash
# Remove cluster_network from ceph.conf to use single network
vim /etc/pve/ceph.conf

# Comment out or remove this line:
# cluster_network = 10.10.10.0/23

# Keep only:
public_network = 192.168.86.0/23

# Restart ceph services
./cssh "systemctl restart ceph.target"
```

### Verify Network Interfaces
```bash
# Check if 10.10.10.x interfaces exist
./cssh "hostname && ip addr show | grep 10.10.10"

# Check routing
./cssh "hostname && ip route | grep 10.10.10"
```

**This explains ALL the heartbeat failures** - OSDs were trying to use the dead 10.10.10.0/23 network for cluster communication!
## Network Interface Analysis - Links Down

**PERFECT DIAGNOSIS!** The interfaces exist but all links are DOWN:

```console
root@kovacs:~# ./cssh "hostname && ip addr show | grep 10.10.10"
harlan    inet 10.10.10.11/23 scope global vmbr1
quell     inet 10.10.10.16/23 scope global vmbr1  
poe       inet 10.10.10.13/23 scope global vmbr1
edgar     inet 10.10.10.14/23 scope global vmbr1
kovacs    inet 10.10.10.12/23 scope global vmbr1

root@kovacs:~# ./cssh "hostname && ip route | grep 10.10.10"
poe       10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.13 linkdown 
kovacs    10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.12 linkdown 
harlan    10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.11 linkdown 
quell     10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.16 linkdown 
edgar     10.10.10.0/23 dev vmbr1 proto kernel scope link src 10.10.10.14 linkdown
```

**Key finding**: All routes show `linkdown` - the vmbr1 bridge is down on all nodes.

### Fix Options

**Option 1: Remove cluster network (Recommended)**
```bash
# Edit ceph.conf and remove cluster_network line
vim /etc/pve/ceph.conf
# Remove: cluster_network = 10.10.10.0/23
./cssh "systemctl restart ceph.target"
```

**Option 2: Fix vmbr1 bridge**
```bash
# Check bridge status
./cssh "hostname && ip link show vmbr1"

# Try bringing up the bridge
./cssh "hostname && ip link set vmbr1 up"
```

**Recommendation**: Use Option 1 - single network is simpler and more reliable than fixing the broken bridge infrastructure.
## Deep Bridge Diagnostics

**Since `ip link set vmbr1 up` didn't work, let's diagnose further:**

### Check Bridge Configuration
```bash
# Check bridge details and member interfaces
./cssh "hostname && brctl show vmbr1"

# Check what physical interfaces should be in the bridge
./cssh "hostname && cat /etc/network/interfaces | grep -A 10 vmbr1"

# Check bridge state
./cssh "hostname && ip link show vmbr1"
```

### Check Physical Interface Status
```bash
# Check if underlying physical interfaces are up
./cssh "hostname && ip link show | grep -E '(eth|ens|enp)'"

# Check for interface errors
./cssh "hostname && ip -s link show vmbr1"
```

### Check Proxmox Network Config
```bash
# Check Proxmox network configuration
./cssh "hostname && cat /etc/pve/nodes/\$(hostname)/network.conf"
```

### Likely Issues
- **Missing physical interface** in bridge
- **Physical interface down** 
- **Bridge configuration error**
- **Hardware/cable problem**

**Recommendation**: Skip the bridge troubleshooting for now and remove cluster_network from ceph.conf to get your cluster stable first.
## Bridge Configuration Analysis

**Found the issue!** The network config shows vmbr1 is configured but the physical interface may be down:

```
auto vmbr1
iface vmbr1 inet static
        address 10.10.10.11/23
        bridge-ports enp6s4        # Physical interface
        bridge-stp off
        bridge-fd 0
#SAN - Ceph Network
```

### Check Physical Interface Status
```bash
# Check if enp6s4 is up on all nodes
./cssh "hostname && ip link show enp6s4"

# Check for cable/link issues
./cssh "hostname && ethtool enp6s4 | grep -E '(Link|Speed)'"

# Try bringing up the physical interface
./cssh "hostname && ip link set enp6s4 up"

# Then try the bridge again
./cssh "hostname && ip link set vmbr1 up"
```

### Alternative: Check Switch Connection
```bash
# Check if switch port is active
./cssh "hostname && mii-tool enp6s4"
```

**Most likely causes:**
1. **Physical interface enp6s4 is down**
2. **Cable disconnected/bad**
3. **Switch port issue**

**Still recommend**: Remove cluster_network from ceph.conf first to stabilize cluster, then fix the hardware issue.
## Priority: Fix SAN Network Hardware

**Understood!** You need the separate networks working. Let's fix the SAN network hardware issue:

### Step 1: Check Physical Interface Status
```bash
# Check enp6s4 status on all nodes
./cssh "hostname && ip link show enp6s4"

# Check for link detection
./cssh "hostname && ethtool enp6s4 | grep -E '(Link detected|Speed|Duplex)'"
```

### Step 2: Bring Up Physical Interfaces
```bash
# Bring up enp6s4 on all nodes
./cssh "hostname && ip link set enp6s4 up"

# Wait a moment for link negotiation
sleep 5

# Check if link is now up
./cssh "hostname && ethtool enp6s4 | grep 'Link detected'"
```

### Step 3: Restart Network Services
```bash
# Restart networking to reinitialize bridges
./cssh "hostname && systemctl restart networking"

# Or manually bring up vmbr1
./cssh "hostname && ip link set vmbr1 up"
```

### Step 4: Verify SAN Network
```bash
# Test SAN network connectivity
./cssh "hostname && ping -c 3 10.10.10.11"

# Check routing
./cssh "hostname && ip route | grep 10.10.10"
```

**Once SAN network is working, restart Ceph services:**
```bash
./cssh "systemctl restart ceph.target"
```
## Check Each Node's Network Configuration

**Good point!** Let's check what physical interface each node uses for vmbr1:

### Discover Physical Interfaces Per Node
```bash
# Check network config on each node
./cssh "hostname && cat /etc/network/interfaces | grep -A 5 'auto vmbr1'"

# Check what interfaces exist on each node
./cssh "hostname && ip link show | grep -E '^[0-9]+:' | grep -E '(eth|ens|enp)'"

# Check bridge configuration
./cssh "hostname && brctl show vmbr1"
```

### Check Physical Interface Status Per Node
```bash
# Check all potential interfaces that might be used
./cssh "hostname && for iface in enp6s4 enp6s5 enp4s0f0 enp4s0f1 eth1 eth2; do echo -n \"\$iface: \"; ip link show \$iface 2>/dev/null | grep -o 'state [A-Z]*' || echo 'not found'; done"
```

### Alternative: Check Each Node Individually
```bash
# Check harlan's vmbr1 config
ssh harlan "cat /etc/network/interfaces | grep -A 5 vmbr1"

# Check kovacs's vmbr1 config  
ssh kovacs "cat /etc/network/interfaces | grep -A 5 vmbr1"

# Continue for each node...
```

**This will show us which physical interface each node is supposed to use for the SAN network.**
## Physical Interface Mapping Found

**Perfect!** Now we know each node's SAN interface:

```
kovacs: enp6s4
edgar:  enp5s2f0  
harlan: enp6s4
poe:    enp6s4
quell:  enp5s2f1
```

### Check Physical Interface Status
```bash
# Check specific interfaces per node
ssh kovacs "ip link show enp6s4 && ethtool enp6s4 | grep 'Link detected'"
ssh edgar "ip link show enp5s2f0 && ethtool enp5s2f0 | grep 'Link detected'"
ssh harlan "ip link show enp6s4 && ethtool enp6s4 | grep 'Link detected'"
ssh poe "ip link show enp6s4 && ethtool enp6s4 | grep 'Link detected'"
ssh quell "ip link show enp5s2f1 && ethtool enp5s2f1 | grep 'Link detected'"
```

### Bring Up Physical Interfaces
```bash
# Bring up each node's SAN interface
ssh kovacs "ip link set enp6s4 up"
ssh edgar "ip link set enp5s2f0 up"  
ssh harlan "ip link set enp6s4 up"
ssh poe "ip link set enp6s4 up"
ssh quell "ip link set enp5s2f1 up"
```

### Bring Up Bridges
```bash
# After physical interfaces are up, bring up bridges
./cssh "ip link set vmbr1 up"
```

### Test SAN Network
```bash
# Test connectivity after bringing up interfaces
./cssh "ping -c 3 10.10.10.11"
```
## Using IP Addresses for SSH Commands

**Right!** Using IP addresses instead of hostnames:

### Check Physical Interface Status
```bash
# Check specific interfaces per node using IP addresses
ssh 192.168.86.12 "ip link show enp6s4 && ethtool enp6s4 | grep 'Link detected'"    # kovacs
ssh 192.168.86.14 "ip link show enp5s2f0 && ethtool enp5s2f0 | grep 'Link detected'"  # edgar
ssh 192.168.86.11 "ip link show enp6s4 && ethtool enp6s4 | grep 'Link detected'"    # harlan
ssh 192.168.86.13 "ip link show enp6s4 && ethtool enp6s4 | grep 'Link detected'"    # poe
ssh 192.168.86.16 "ip link show enp5s2f1 && ethtool enp5s2f1 | grep 'Link detected'"  # quell
```

### Bring Up Physical Interfaces
```bash
# Bring up each node's SAN interface using IP addresses
ssh 192.168.86.12 "ip link set enp6s4 up"      # kovacs
ssh 192.168.86.14 "ip link set enp5s2f0 up"    # edgar
ssh 192.168.86.11 "ip link set enp6s4 up"      # harlan
ssh 192.168.86.13 "ip link set enp6s4 up"      # poe
ssh 192.168.86.16 "ip link set enp5s2f1 up"    # quell
```

### Bring Up Bridges
```bash
# After physical interfaces are up, bring up bridges
./cssh "ip link set vmbr1 up"
```

### Test SAN Network
```bash
# Test connectivity after bringing up interfaces
./cssh "ping -c 3 10.10.10.11"
```
## Hardware Issue Confirmed - NO-CARRIER

**Critical finding!** The interface shows `NO-CARRIER` which means physical layer failure:

```console
root@harlan:~# ip link show enp6s4
2: enp6s4: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast master vmbr1 state DOWN mode DEFAULT group default qlen 1000

root@harlan:~# ip link show vmbr1  
8: vmbr1: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default qlen 1000
```

**NO-CARRIER means:**
- Cable unplugged/bad
- Switch port down/failed
- Network card hardware failure

### Check All Nodes for NO-CARRIER
```bash
# Check carrier status on all nodes
ssh 192.168.86.12 "ip link show enp6s4 | grep -o 'NO-CARRIER'"      # kovacs
ssh 192.168.86.14 "ip link show enp5s2f0 | grep -o 'NO-CARRIER'"    # edgar  
ssh 192.168.86.11 "ip link show enp6s4 | grep -o 'NO-CARRIER'"      # harlan
ssh 192.168.86.13 "ip link show enp6s4 | grep -o 'NO-CARRIER'"      # poe
ssh 192.168.86.16 "ip link show enp5s2f1 | grep -o 'NO-CARRIER'"    # quell
```

**If all show NO-CARRIER, the SAN switch is likely dead or all cables are bad.**

**DECISION TIME**: Fix hardware or disable cluster network temporarily to stabilize Ceph.
## Switch Back Online - Test SAN Network

**Excellent!** Now let's test if the SAN network is working:

### Test Link Status
```bash
# Check if interfaces now have carrier
ssh 192.168.86.12 "ip link show enp6s4"      # kovacs
ssh 192.168.86.14 "ip link show enp5s2f0"    # edgar  
ssh 192.168.86.11 "ip link show enp6s4"      # harlan
ssh 192.168.86.13 "ip link show enp6s4"      # poe
ssh 192.168.86.16 "ip link show enp5s2f1"    # quell
```

### Bring Up Interfaces and Bridges
```bash
# Bring up physical interfaces
ssh 192.168.86.12 "ip link set enp6s4 up"      # kovacs
ssh 192.168.86.14 "ip link set enp5s2f0 up"    # edgar
ssh 192.168.86.11 "ip link set enp6s4 up"      # harlan
ssh 192.168.86.13 "ip link set enp6s4 up"      # poe
ssh 192.168.86.16 "ip link set enp5s2f1 up"    # quell

# Bring up bridges
./cssh "ip link set vmbr1 up"
```

### Test SAN Connectivity
```bash
# Test SAN network connectivity
./cssh "ping -c 3 10.10.10.11"
```

### Restart Ceph Services
```bash
# Once SAN network is confirmed working
./cssh "systemctl restart ceph.target"

# Monitor cluster recovery
watch -n 5 "ceph osd tree"
```
## Re-enable SAN Network and CephFS

### Step 1: Add Cluster Network Back to ceph.conf
```bash
# Edit ceph.conf to add cluster network back
vim /etc/pve/ceph.conf

# Add this line back:
cluster_network = 10.10.10.0/23

# Verify both networks are configured:
# public_network = 192.168.86.0/23
# cluster_network = 10.10.10.0/23
```

### Step 2: Restart Ceph Services
```bash
# Restart ceph services to use SAN network
./cssh "systemctl restart ceph.target"

# Monitor cluster status
ceph -s
ceph osd tree
```

### Step 3: Re-enable CephFS
```bash
# Bring CephFS back online
ceph fs set cephfs down false

# Enable MDS services
./cssh "systemctl enable ceph-mds.target"

# Start MDS services
./cssh "systemctl start ceph-mds.target"

# Check CephFS status
ceph fs status
ceph mds stat
```

### Step 4: Monitor Cluster Health
```bash
# Watch for stability
watch -n 5 "ceph health && echo && ceph osd tree"
```

**This restores your dual-network configuration with CephFS enabled.**
## Restore Normal Ceph Operations

**Excellent!** Now let's safely remove the maintenance flags in stages:

### Stage 1: Enable Basic Operations (Low Risk)
```bash
# Remove noin flag first
ceph osd unset noin

# Wait 5 minutes and check stability
ceph health
ceph osd tree
```

### Stage 2: Enable OSD State Management (Medium Risk)
```bash
# Remove noup/nodown flags
ceph osd unset noup
ceph osd unset nodown

# Wait 10 minutes and monitor
ceph -s
```

### Stage 3: Enable Data Movement (High Risk - Monitor Closely)
```bash
# Remove noout flag
ceph osd unset noout

# Wait 15 minutes and watch for issues
watch -n 30 "ceph health"
```

### Stage 4: Enable Recovery Operations (Highest Risk)
```bash
# Enable recovery operations one at a time
ceph osd unset norecover
# Wait 20 minutes, monitor

ceph osd unset nobackfill  
# Wait 20 minutes, monitor

ceph osd unset norebalance
# Wait 20 minutes, monitor
```

### Stage 5: Enable Maintenance Operations
```bash
# Finally enable scrubbing
ceph osd unset noscrub
ceph osd unset nodeep-scrub
```

### Reset Heartbeat Timeouts to Normal
```bash
# Reset to default values
ceph config rm osd osd_heartbeat_grace
ceph config rm osd osd_heartbeat_interval
```