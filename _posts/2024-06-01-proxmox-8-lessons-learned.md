---
title:  "ProxMox 8 Lessons Learned in the Homelabs"
layout: post
published: false
---

# Lessons Learned

I've learned a lot over the upgrades and scaling up since Proxmox 7.4 to the current Proxmox 8.2.2.

## Ceph Stuff

Ceph is really complicated but Proxmox makes it incredibly easy to setup the initial cluster with auto-magic under the covers. When the auto-magic fails, you have a very heavy lift to understand all the automation that just made things work.

### How to shutdown Ceph cleanly

[Ceph Shutdowns](https://forum.proxmox.com/threads/shutdown-of-the-hyper-converged-cluster-ceph.68085/post-619620) has nice notes on how to shutdown cleanly.

### Sane defaults for Ceph

Weekly deep scrubs are going to burn out my SSD and HDD

```osd_deep_scrub_interval 604800.000000
Description The interval for “deep” scrubbing (fully reading all data). The osd scrub load threshold does not affect this setting.
Type        Float
Default     Once per week. 60*60*24*7

root@harlan:~# ceph config show-with-defaults osd.0 | grep deep | grep scrub | less
osd_deep_scrub_interval    604800.000000    default

```

#### How to set a Deep-Scrub Interval

[How to set a Deep-Scrub Interval](https://silvenga.com/posts/ceph-and-deep-scrubs/)

Note: This is in the global namespace, not the osd namespace. This is important because the monitors that emit the PG_NOT_DEEP_SCRUBBED warning based on this OSD setting, so it needs to match between the osd and mon namespaces, or just use global.

```
# Schedule the next normal scrub in between 1-7 days.
ceph config set global osd_scrub_min_interval 86400 # 1 day
ceph config set global osd_scrub_interval_randomize_ratio 7 # 700%

# No more delays, normal scrub after 14 days.
ceph config set global osd_scrub_max_interval 1209600 # 14 days

# No more waiting on a random 15% chance to deep-scrub, just deep-scrub.
ceph config set global osd_deep_scrub_interval 2419200 # 28 days
```

### Ceph calculation for OSDs

https://florian.ca/ceph-calculator/

## Seagate USB Shitshow

https://www.smartmontools.org/wiki/SAT-with-UAS-Linux

```
root@kovacs:~# find /mnt/sdf/?\ Drive/Movies/ -type d -maxdepth 1 -name "[!a-tA-T]*" 2> /dev/null | wc -l
190
root@kovacs:~# find /mnt/sdf/?\ Drive/Movies/ -type d -maxdepth 1 -name "[a-tA-T]*" 2> /dev/null | wc -l
1856
root@kovacs:~# find /mnt/sdf/?\ Drive/Movies/ -type d -maxdepth 1  2> /dev/null | wc -l
2046
```


```
root@poe:~# apt install lsscsi sysfsutils -y
...
root@poe:~# lsscsi
[0:0:0:0]    disk    ATA      ST3160812AS      J     /dev/sda 
[1:0:0:0]    disk    ATA      SAMSUNG HD161HJ  0-22  /dev/sdb 
[2:0:0:0]    disk    ATA      Crucial_CT525MX3 R040  /dev/sdc 
[3:0:0:0]    cd/dvd  TSSTcorp DVD+-RW SH-216AB D300  /dev/sr0 
[6:0:0:0]    disk    Seagate  One Touch HDD    0002  /dev/sdd 
[7:0:0:0]    disk    Seagate  BUP Portable     0004  /dev/sde 
root@poe:~# lsscsi -H
[0]    ahci          
[1]    ahci          
[2]    ahci          
[3]    ahci          
[4]    ahci          
[5]    ahci          
[6]    uas           
[7]    uas           

root@poe:~# systool -c scsi_host
Class = "scsi_host"

  Class Device = "host0"
    Device = "host0"

  Class Device = "host1"
    Device = "host1"

  Class Device = "host2"
    Device = "host2"

  Class Device = "host3"
    Device = "host3"

  Class Device = "host4"
    Device = "host4"

  Class Device = "host5"
    Device = "host5"

  Class Device = "host6"
    Device = "host6"

  Class Device = "host7"
    Device = "host7"

root@poe:~# systool -c scsi_host -v
Class = "scsi_host"

  Class Device = "host0"
  Class Device path = "/sys/devices/pci0000:00/0000:00:1f.2/ata1/host0/scsi_host/host0"
    active_mode         = "Initiator"
    ahci_host_cap2      = "4"
    ahci_host_caps      = "e730ff45"
    ahci_host_version   = "10300"
    ahci_port_cmd       = "d617"
    can_queue           = "32"
    cmd_per_lun         = "0"
    eh_deadline         = "off"
    em_message_supported= "led "
    em_message_type     = "1"
    em_message          = "0"
    host_busy           = "0"
    host_reset          = <store method only>
    link_power_management_policy= "max_performance"
    nr_hw_queues        = "1"
    proc_name           = "ahci"
    prot_capabilities   = "0"
    prot_guard_type     = "0"
    scan                = <store method only>
    sg_prot_tablesize   = "0"
    sg_tablesize        = "168"
    state               = "running"
    supported_mode      = "Initiator"
    uevent              = 
    unique_id           = "1"
    use_blk_mq          = "1"

    Device = "host0"
    Device path = "/sys/devices/pci0000:00/0000:00:1f.2/ata1/host0"
      uevent              = "DEVTYPE=scsi_host"
...

``` 


## PVE Scripting


```
pvesh get /nodes
pvesh get /nodes/status
pvesh get /nodes/statu
pvesh get /nodes/status/time
pvesh get /nodes
pvesh get /cluster
pvesh get /cluster/ceph
pvesh get /cluster/ceph/status
pvesh get /cluster/ceph/flags
```
https://192.168.86.15:8006/pve-docs/api-viewer/index.html

```
root@tanaka:~# cat cssh 
#!/bin/bash

#for node in $(pvesh get /nodes --output-format json | jq -r '.[].node'); do
#  ssh root@$node "$*"
#done

for node in $(pvesh get /cluster/status --output-format json | jq -r '.[].ip' | grep -v null); do
  ssh root@$node "$*"
done
```


### look at changes in two directories

```
root@kovacs:~# rsync -nrv /mnt/sd?/?\ Drive/TVShows/ /mnt/pve/cephfs/tvshows/

root@kovacs:~# df -h /mnt/sd[hijk]
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdh2       4.6T  3.0T  1.7T  65% /mnt/sdh
/dev/sdi2       4.6T  2.6T  2.1T  56% /mnt/sdi
/dev/sdj2       4.6T  3.8T  800G  83% /mnt/sdj
/dev/sdk2       4.6T  2.5T  2.2T  53% /mnt/sdk

root@kovacs:~# df -h /mnt/sd[hijk] /mnt/pve/cephfs
Filesystem                                   Size  Used Avail Use% Mounted on
/dev/sdh2                                    4.6T  3.0T  1.7T  65% /mnt/sdh
/dev/sdi2                                    4.6T  2.6T  2.1T  56% /mnt/sdi
/dev/sdj2                                    4.6T  3.8T  800G  83% /mnt/sdj
/dev/sdk2                                    4.6T  2.5T  2.2T  53% /mnt/sdk
192.168.86.11,192.168.86.12,192.168.86.13:/  5.9T  4.5T  1.4T  78% /mnt/pve/cephfs
```

Get a list of TV Show directories with full path:
```
# find /mnt/sd?/?\ Drive/TVShows/ -mindepth 1 -maxdepth 1 -type d

# find /mnt/sd?/?\ Drive/TVShows/ -mindepth 1 -maxdepth 1 -type d -exec du -msh {} \;
```
~16.3TiB of storage to add to a Ceph Cluster

9 x 5Tb OSDs which are 4.5TiB each

```
movies   4.2 TiB
tvshow  11.9 TiB
------- -------
all     16.2 TiB

CephFS  20.4 TiB
```


### Netgear GS108Ev2
https://github.com/ckarrie/ckw-ha-gs108e

### Ceph OSD sizes
```
root@kovacs:~# date && ceph osd df tree
Wed Feb  7 11:34:16 PM EST 2024
ID  CLASS  WEIGHT    REWEIGHT  SIZE     RAW USE  DATA     OMAP     META     AVAIL    %USE   VAR   PGS  STATUS  TYPE NAME      
-1         40.93547         -   41 TiB   14 TiB   14 TiB  102 MiB   46 GiB   27 TiB  34.72  1.00    -          root default   
-3         13.64516         -   14 TiB  4.8 TiB  4.8 TiB   37 MiB   17 GiB  8.8 TiB  35.24  1.02    -              host harlan
 0    hdd   4.54839   1.00000  4.5 TiB  3.9 TiB  3.9 TiB   17 MiB   12 GiB  691 GiB  85.15  2.45  121      up          osd.0  
 3    hdd   4.54839   1.00000  4.5 TiB  616 GiB  615 GiB  8.5 MiB  2.9 GiB  3.9 TiB  13.24  0.38   24      up          osd.3  
 6    hdd   4.54839   1.00000  4.5 TiB  342 GiB  341 GiB   12 MiB  2.1 GiB  4.2 TiB   7.34  0.21   16      up          osd.6  
-7         13.64516         -   14 TiB  4.8 TiB  4.7 TiB   32 MiB   15 GiB  8.9 TiB  34.86  1.00    -              host kovacs
 2    hdd   4.54839   1.00000  4.5 TiB  3.6 TiB  3.6 TiB   11 MiB   11 GiB  944 GiB  79.74  2.30  111      up          osd.2  
 5    hdd   4.54839   1.00000  4.5 TiB  588 GiB  587 GiB   12 MiB  2.0 GiB  4.0 TiB  12.62  0.36   27      up          osd.5  
 8    hdd   4.54839   1.00000  4.5 TiB  570 GiB  569 GiB  8.1 MiB  1.5 GiB  4.0 TiB  12.23  0.35   23      up          osd.8  
-5         13.64516         -   14 TiB  4.6 TiB  4.6 TiB   33 MiB   14 GiB  9.0 TiB  34.04  0.98    -              host poe   
 1    hdd   4.54839   1.00000  4.5 TiB  3.6 TiB  3.6 TiB  9.1 MiB   11 GiB  981 GiB  78.94  2.27  109      up          osd.1  
 4    hdd   4.54839   1.00000  4.5 TiB  680 GiB  679 GiB   14 MiB  2.0 GiB  3.9 TiB  14.60  0.42   30      up          osd.4  
 7    hdd   4.54839   1.00000  4.5 TiB  400 GiB  399 GiB  9.7 MiB  1.2 GiB  4.2 TiB   8.59  0.25   22      up          osd.7  
                        TOTAL   41 TiB   14 TiB   14 TiB  102 MiB   46 GiB   27 TiB  34.72                                    
MIN/MAX VAR: 0.21/2.45  STDDEV: 33.03
```
