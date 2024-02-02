---
title:  "ProxMox 8.1 for the Homelabs"
layout: post
published: false
---

I'm building a Proxmox 8 Cluster with Ceph in an HA configuration using very low-end hardware and questionable choices on various buses.

First I'm updating from an older Plex server hosted on Windows 10 Pro with several Portable Seagate USB Hard Drives attached to it and planning to reuse those drives. I hit a wall on disks for this system and tried out Windows Spaces on the portable USB drives to no avail. RAID5 or better was just too time intensive and prone to issues. If I had added a JBOD, RAID controller or some other server style stuff to the mix, I might have gotten it working.

I also used to host a pile of content on a VMWare ESXi server at my house with some content I'd like to push back out.

The easy out would have been a Synology NAS which I considered seriously. But thinking about this for awhile, I starting thinking about how Google and Amazon handled this storage issue with large disks and replication.  GlusterFS and Ceph seemed to be the winners in this space.  Proxmox has builtin Ceph support so that is the direction I started digging into learning.

I built a Proxmox 7.4 three node clusters and messed around with it for a month or two to learn about LXC, VMs, HA and the SDN features. Pushing ISO images, some older VMs converted from VMware ESXi and general linux admin stuff left me thinking this was a good direction. I added Ceph to the mix with some extra USB Drives and things got complex fast.

Ceph is a beast to learn but really easy to install and just use on Proxmox. There is a terrible depth to it that they just make work for you upfront.

Full disclosure, I'm not using a separate 10Gbps networking for the Ceph cluster which is likely the root of some of the problems I have encountered. But I did create a separate 1Gbps SAN on a separate physcial NIC port for Ceph so I'm a little disappointed with some of those issues. I'm also making Ceph work hard using a UAS (USB) interface on portable external USB hard drives that are not very SMART compliant. Ceph is not very resilient to network or device failures in my experience so far. Often the mount point will hang requiring a hard reboot to get it back up.

I'm also using Dell OptiPlex 990 era hardware which means decade old motherboards and technology. These are the lower-end of viable and are aging out of Windows support so cheaper. I also have some other VDI client equipment for a super low-end component to swap in like a Raspberry Pi if I needed those.

Existing hardware includes a five node Proxmox cluster with 4 x Dell OptiPlex 990 Towers, 1 x Dell Optiplex Desktop, some USB3 PCIe cards and hubs, PCI and PCIe 1Gbps NIC cards and three Nvidia P620 GPUs. I have 9 x Seagate 5Tb Portable USB Hard Drives with varied internal hard disks. I also had the typical piles of old spinning rust 3.5" hard drives in varied sets of 320Gb, 500Gb, 1Tb along with some varied SSD in 100Gb, 250Gb, and 500Gb varieties as well to build OS boot drive arrays and fast caching disks.

I also have various Netgear 1Gbps switches of all flavors including a couple that are managed switches. These are in five (5) and eight (8) port varieties. A mess of varied CAT 5, CAT 5e, and CAT 6 network cables are floating around. I'm leaving out the pile of network hardware that is 100Mbps as too old to care about using.

My legacy pile also includes a couple of decent residencial APC Back-UPS 550 and similar battery backups along with the USB/Serial cables. The APC SMX1500 2u rack mount UPS is tested with new batteries as the big boy for my core network devices.

Along the way, I got a couple other nifty pieces of hardware like a four (4) port KVM with hot-key support, a fully built out PiKVM v3, an IP (network) enabled remote power switch, 

I'm also not including my WAN/LAN network configuration or devices but those are in a separate post. Just consider those as existing and mostly working.

## Why am I doing this

At this point, somebody should shake their head and just tell me I'm the architect of my own pain.

To learn and build something interesting. The simple path would be to buy a Synology NAS, a Ubiquiti Switch and Access Points, and add a decent couple year old server. The other path is to just avoid all the hardware and create a DigitalOcean Droplet or AWS EC2 instance which I've done in the past.

# Lessons Learned

##

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