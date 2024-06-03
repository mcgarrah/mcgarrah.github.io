---
title:  "ProxMox 8.1 for the Homelabs"
layout: post
published: true
---

I am in the process of building a [Proxmox 8 Cluster](https://www.proxmox.com/) with Ceph in an HA (high availability) configuration using very low-end hardware and questionable options for the various buses. I'm going for both cheap and reusing existing hardware that I've gathered up over the years.

Over the COVID lockdown, I was running a [Plex Media Server (PMS)](https://www.plex.tv/media-server-downloads/#plex-media-server) on an older Dell Optiplex 390 SFF Desktop that I cobbled into it several Seagate USB3 portable drives that I just slapped on it as I needed more space. It hosted my extensive VHS, DVD and BluRay library as I ripped them into digital formats. To improve the experience I threw a Nvidia Quadro P400 into the mix and a PCIe USB3 card for faster access to the drives. Eventually, I had some drive issues and wanted to get some additional reliability into the mix so tried out [Microsoft Windows Storage Spaces (MWSS)](https://learn.microsoft.com/en-us/windows-server/storage/storage-spaces/overview). Windows and the associated fun I had with MWSS left me incredibly frustrated and I was trying to make an enterprise product work in a low-end workstation with a bunch of USB drives. The thing that made me fully abandon MWSS was the recovery options when you had a bad drive. MWSS probably works well with solid enterprise equipment but was misery on the stuff I cobbled together. So exit Windows OS.

For about ten (10) years, I had run an VMWare ESXi server that let me play with new technology and host some content and services. I let it go awhile back while I was in graduate school and working full-time but have missed this as an option ever since. So adding a homelab server or cluster will let me get some of that back.




The background is that I'm updating from an older Plex Media Server hosted on Windows 10 Pro with several Portable Seagate USB Hard Drives attached to it and planning to reuse those drives. I hit a wall on disks for this system and tried out Windows Spaces on the portable USB drives to no avail. RAID5 or better is just too time intensive and prone to issues. If I had added a JBOD, RAID controller or some other server style stuff to the mix, I might have gotten it working but at a good bit of cost and complexity.

Another thing is that I used to host a pile of content on a VMWare ESXi server at my house with some content I'd like to push back out. ESXi offered a great way to host Linux and Windows VMs with a nice storage options. Say what you want but VMWare ESXi just worked as long as you had compatible hardware and patience. Until the recent controversy, having an ESXi at home let me also had the advantage of keep my VMWare skills up to date which was valuable.

The easy out would have been a Synology NAS which I considered very seriously. But thinking about this for awhile, I starting contemplating how Google and Amazon handled this storage issue with large disks and replication. Google is famous for using lots of low-end hardware in redundant arrays to meet their needs. This led to GlusterFS and Ceph as the viable options and seemed to be the winners in this space. Proxmox has builtin Ceph support so that is the direction I started digging into learning.

I built a Proxmox 7.4 three node clusters and messed around with it (engineering evaluation) for a month or two early in 1Q2024 to learn about LXC, VMs, HA and the SDN features. Pushing ISO images, some older VMs converted from VMware ESXi and general linux admin stuff left me thinking this was a good direction. I added Ceph to the mix with some extra USB Drives and things got complex fast.

Ceph is a beast to learn but really easy to install and just use on Proxmox. There is a terrible depth to it that they just make work for you upfront.

Full disclosure, I'm not using a separate 10Gbps networking for the Ceph cluster which is likely the root of some of the problems I have encountered in Ceph. But I did create a separate 1Gbps SAN on a separate physcial NIC port for Ceph so I'm a little disappointed with some of those issues. I'm also making Ceph work hard using a UAS (USB) interface on portable external USB hard drives that are not very SMART compliant. Ceph is not very resilient to network or device failures in my experience so far. Often the mount point will hang requiring a hard reboot to get it back up.

The load up of the Ceph cluster with content is likely the most aggressive activity it will experience. I'm literally beating the crap out of it as I load up 25Tb of data over a locally mounted USB3 drive (5Mbps) and push the content to a switched 1Gbps network SAN between nodes. During one weird period, I accidentally bumped a network cable on the SAN and physically disconnected it for one node. The primary front-side NIC was engaged as a fail-back for the storage traffic and it was miserable. So the separate network is an absolute must. Don't bother trying Ceph for anything significant other than toy usage without breaking out the SAN.

I'm also using Dell OptiPlex 990 era hardware which means decade old motherboards and technology. These are the lower-end of viable and are aging out of Windows support so much cheaper to purchase. The upside is these are tower cases with lots of room. I also have some other VDI client equipment for a super low-end component to swap in like a Raspberry Pi if I needed those for quorum or other services.

Existing hardware includes a five node Proxmox cluster with 4 x Dell OptiPlex 990 Mini-Towers, 1 x Dell Optiplex Desktop, some USB3 PCIe 1x cards and powered hubs, PCI and PCIe 1Gbps NIC cards and three Nvidia P620 GPUs. I have 9 x Seagate 5Tb Portable USB Hard Drives with varied internal hard disks. I also had the typical piles of old spinning rust 3.5" hard drives in varied sets of 320Gb, 500Gb, 1Tb along with some varied SSD in 100Gb, 250Gb, and 500Gb varieties as well to build OS boot drive arrays and fast caching disks.

To protect against crappy old hardware, I am using ZFS RAID mirrors for the OS Boot Drives. I've already had two spinning rust drive fail but the mirror protected the machine until I could add another one. I'll be replacing those drives with small SSDs as they fail.

I also have various Netgear 1Gbps switches of all flavors including a couple that are managed switches. These are in five (5) and eight (8) port varieties. A mess of varied CAT 5, CAT 5e, and CAT 6 network cables are floating around. I'm leaving out the pile of network hardware that is 100Mbps as too old to care about using.

My legacy pile also includes a couple of decent residencial APC Back-UPS 550 and similar battery backups along with the USB/Serial cables. The APC SMX1500 2u rack mount UPS is tested with new batteries as the big boy for my core network devices.

Along the way, I got a couple other nifty pieces of hardware like a four (4) port KVM with hot-key support, a fully built out PiKVM v3, an IP (network) enabled remote power switch, 

I'm also not including my WAN/LAN network configuration or devices but those are in a separate post. Just consider those as existing and mostly working.

## Why am I doing this

At this point, somebody should shake their head and just tell me I'm the architect of my own pain.

To learn and build something interesting. The simple path would be to buy a Synology NAS, a Ubiquiti Switch and Access Points, and add a decent couple year old server. The other path is to just avoid all the hardware and create a DigitalOcean Droplet or AWS EC2 instance which I've done in the past.