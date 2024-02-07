---
title:  "ProxMox 8.1 for the Homelabs"
layout: post
published: false
---

I am in the process of building a [Proxmox 8 Cluster](https://www.proxmox.com/) with Ceph in an HA (high availability) configuration using very low-end hardware and questionable options for various buses. I'm going for both cheap and reusing existing hardware that I've gathered up over the years.

Over the COVID lockdown, I was running a Plex Media Server (PMS) on an older Dell Optiplex 390 SFF Desktop that I cobbled into it several Seagate USB3 portable drives that I just slapped on it as I needed more space. It hosted my extensive VHS, DVD and BluRay library as I ripped them into digital formats. To improve the experience I threw a Nvidia Quadro P400 into the mix and a PCIe USB3 card for faster access to the drives. Eventually, I had some drive issues and wanted to get some additional reliability into the mix so tried out Microsoft Windows Storage Spaces (MWSS). Windows and the associated fun I had with MWSS left me frustrated and I was trying to make an enterprise product work in a low-end workstation with a bunch of USB drives. The thing that made me fully abandon MWSS was the recovery options when you had a bad drive. MWSS probably works well with solid enterprise equipment but was misery on the stuff I cobbled together. So exit Windows OS.

For about ten (10) years, I had run an VMWare ESXi server that let me play with new technology and host some content and services. I let it go awhile back but have missed this as an option ever since. So Proxmox will let me get some of that back.




The background is that I'm updating from an older Plex Media Server hosted on Windows 10 Pro with several Portable Seagate USB Hard Drives attached to it and planning to reuse those drives. I hit a wall on disks for this system and tried out Windows Spaces on the portable USB drives to no avail. RAID5 or better is just too time intensive and prone to issues. If I had added a JBOD, RAID controller or some other server style stuff to the mix, I might have gotten it working but at a good bit of cost and complexity.

Another thing is that I used to host a pile of content on a VMWare ESXi server at my house with some content I'd like to push back out. It offered a great way to host Linux and Windows VMs with a nice storage options. Say what you want but VMWare ESXi just worked as long as you had compatible hardware and patience.

The easy out would have been a Synology NAS which I considered seriously. But thinking about this for awhile, I starting contemplating how Google and Amazon handled this storage issue with large disks and replication. Google is famous for using lots of low-end hardware in redundant arrays to meet their needs. This led to GlusterFS and Ceph as the viable options and seemed to be the winners in this space. Proxmox has builtin Ceph support so that is the direction I started digging into learning.

I built a Proxmox 7.4 three node clusters and messed around with it (engineering evaluation) for a month or two to learn about LXC, VMs, HA and the SDN features. Pushing ISO images, some older VMs converted from VMware ESXi and general linux admin stuff left me thinking this was a good direction. I added Ceph to the mix with some extra USB Drives and things got complex fast.

Ceph is a beast to learn but really easy to install and just use on Proxmox. There is a terrible depth to it that they just make work for you upfront.

Full disclosure, I'm not using a separate 10Gbps networking for the Ceph cluster which is likely the root of some of the problems I have encountered. But I did create a separate 1Gbps SAN on a separate physcial NIC port for Ceph so I'm a little disappointed with some of those issues. I'm also making Ceph work hard using a UAS (USB) interface on portable external USB hard drives that are not very SMART compliant. Ceph is not very resilient to network or device failures in my experience so far. Often the mount point will hang requiring a hard reboot to get it back up.

The load up of the Ceph cluster with content is likely the most aggressive activity it will experience. I'm literally beating the crap out of it as I load up 25Tb of data over a locally mounted USB3 drive (5Mbps) and push the content to a switched 1Gbps network SAN between nodes. During a weird period, I accidentally bumped a network cable on the SAN and disconnected it for one node. The primary front-side NIC was engaged as a fail-back for the storage traffic and it was miserable. So the separate network is an absolute must. Don't bother trying Ceph for anything significant other than toy usage without breaking out the SAN.

I'm also using Dell OptiPlex 990 era hardware which means decade old motherboards and technology. These are the lower-end of viable and are aging out of Windows support so cheaper. The upside is these are tower cases with lots of room. I also have some other VDI client equipment for a super low-end component to swap in like a Raspberry Pi if I needed those for quorum or other services.

Existing hardware includes a five node Proxmox cluster with 4 x Dell OptiPlex 990 Mini-Towers, 1 x Dell Optiplex Desktop, some USB3 PCIe 1x cards and powered hubs, PCI and PCIe 1Gbps NIC cards and three Nvidia P620 GPUs. I have 9 x Seagate 5Tb Portable USB Hard Drives with varied internal hard disks. I also had the typical piles of old spinning rust 3.5" hard drives in varied sets of 320Gb, 500Gb, 1Tb along with some varied SSD in 100Gb, 250Gb, and 500Gb varieties as well to build OS boot drive arrays and fast caching disks.

To protect against crappy old hardware, I am using ZFS RAID mirrors for the OS Boot Drives. I've already had one spinning rust drive fail but the mirror protected the machine until I could add another one.

I also have various Netgear 1Gbps switches of all flavors including a couple that are managed switches. These are in five (5) and eight (8) port varieties. A mess of varied CAT 5, CAT 5e, and CAT 6 network cables are floating around. I'm leaving out the pile of network hardware that is 100Mbps as too old to care about using.

My legacy pile also includes a couple of decent residencial APC Back-UPS 550 and similar battery backups along with the USB/Serial cables. The APC SMX1500 2u rack mount UPS is tested with new batteries as the big boy for my core network devices.

Along the way, I got a couple other nifty pieces of hardware like a four (4) port KVM with hot-key support, a fully built out PiKVM v3, an IP (network) enabled remote power switch, 

I'm also not including my WAN/LAN network configuration or devices but those are in a separate post. Just consider those as existing and mostly working.

## Why am I doing this

At this point, somebody should shake their head and just tell me I'm the architect of my own pain.

To learn and build something interesting. The simple path would be to buy a Synology NAS, a Ubiquiti Switch and Access Points, and add a decent couple year old server. The other path is to just avoid all the hardware and create a DigitalOcean Droplet or AWS EC2 instance which I've done in the past.

# Lessons Learned

Ceph Shutdowns
https://forum.proxmox.com/threads/shutdown-of-the-hyper-converged-cluster-ceph.68085/post-619620


Weekly deep scrubs are going to burn out my SSD and HDD

osd_deep_scrub_interval 604800.000000
Description The interval for “deep” scrubbing (fully reading all data). The osd scrub load threshold does not affect this setting.
Type        Float
Default     Once per week. 60*60*24*7

root@harlan:~# ceph config show-with-defaults osd.0 | grep deep | grep scrub | less


##

https://florian.ca/ceph-calculator/

## Seagate Shitshow

https://www.smartmontools.org/wiki/SAT-with-UAS-Linux

root@kovacs:~# find /mnt/sdf/?\ Drive/Movies/ -type d -maxdepth 1 -name "[!a-tA-T]*" 2> /dev/null | wc -l
190
root@kovacs:~# find /mnt/sdf/?\ Drive/Movies/ -type d -maxdepth 1 -name "[a-tA-T]*" 2> /dev/null | wc -l
1856
root@kovacs:~# find /mnt/sdf/?\ Drive/Movies/ -type d -maxdepth 1  2> /dev/null | wc -l
2046



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


### PVE Scripting

  125  pvesh get /nodes
  126  pvesh get /nodes/status
  127* pvesh get /nodes/statu
  128  pvesh get /nodes/status/time
  129  pvesh get /nodes
  130  pvesh get /cluster
  131  pvesh get /cluster/ceph
  132  pvesh get /cluster/ceph/status
  133  pvesh get /cluster/ceph/flags

https://192.168.86.15:8006/pve-docs/api-viewer/index.html

root@tanaka:~# cat cssh 
#!/bin/bash

#for node in $(pvesh get /nodes --output-format json | jq -r '.[].node'); do
#  ssh root@$node "$*"
#done

for node in $(pvesh get /cluster/status --output-format json | jq -r '.[].ip' | grep -v null); do
  ssh root@$node "$*"
done



# look at changes in two directories


root@kovacs:~# rsync -nrv /mnt/sd?/?\ Drive/TVShows/ /mnt/pve/cephfs/tvshows/

root@kovacs:~# df -h /mnt/sd[hijk]
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdh2       4.6T  3.0T  1.7T  65% /mnt/sdh
/dev/sdi2       4.6T  2.6T  2.1T  56% /mnt/sdi
/dev/sdj2       4.6T  3.8T  800G  83% /mnt/sdj
/dev/sdk2       4.6T  2.5T  2.2T  53% /mnt/sdk




Netgear GS108Ev2
https://github.com/ckarrie/ckw-ha-gs108e
