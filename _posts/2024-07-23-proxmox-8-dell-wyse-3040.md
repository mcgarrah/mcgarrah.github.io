---
title:  "ProxMox 8.2.2 Cluster on Dell Wyse 3040s"
layout: post
published: false
---

I want a place to test and try out new features and capabilities in [Proxmox 8.2.2 SDN](https://pve.proxmox.com/pve-docs/chapter-pvesdn.html) ([Software Defined Networking](https://en.wikipedia.org/wiki/Software-defined_networking)). I would also like to be able to test some Ceph Cluster configuration changes that are risky as well. I do not want to do it on my semi-production Proxmox 8.2.2 Ceph enabled Cluster that I have mentioned in earlier posts. With 55TiB of raw storage and 29TiB of it loaded up with content, that would be painful to rebuild or reload if I made a mistake during my testing of SDN or Ceph capabilies.

[![Test in Prod, what could go wrong?](/assets/images/what-could-go-wrong.jpg){:width="30%" height="30%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/what-could-go-wrong.jpg){:target="_blank"}

<!-- excerpt-end -->

## Why I am doing this

Fortunately for me, [Apalrd](https://www.apalrd.net) post on this [Installing Proxmox VE 7 on Debian Bullseye](https://www.apalrd.net/posts/2022/pve_bullseye/) that used an earlier [Install Proxmox VE on Debian Buster](https://pve.proxmox.com/wiki/Install_Proxmox_VE_on_Debian_Buster) document for his exploration is where I got the idea to create an extremely low-end Proxmox 8 cluster for any testing that I didn't want on my main cluster.

Also fortunately, I have an extra three (3) [Dell Wyse 3040s](https://www.parkytowers.me.uk/thin/wyse/3040/) that will eventually become a [Wifi 6e Tailscale](https://tailscale.com/) endpoint, or [Home Assistant](https://www.home-assistant.io/) server, or an OpenWRT router from [Recompiling OpenWrt to run natively on the 3040](https://blog.m0les.com/2023/08/thin-client-router-part3-bare-metal-atom.html) but are currently just sitting on my shelf in a shoebox. With just two nodes, I can test Proxmox HA but with three nodes, I can test Proxmox HA failover, add a Ceph Cluster, use CephFS share storage, and try the new SDN Datacenter features as well.

I added three (3) [Amazon Basics USB 3.0 to 10/100/1000 Gigabit Ethernet Internet Adapter](https://amzn.to/3ybtOUw) so I can have two network interfaces to make testing more expansive and interesting. I also pulled out three 8GB USB2 Thumbdrives from an old box to use as the Ceph OSD media and found a three pack of [SanDisk 32GB 3-Pack Ultra Fit USB 3.1 Flash Drive (3x32GB)](https://amzn.to/3YesqLq) for under $20 to upgrade that Ceph storage and learn about transitioning between media in Ceph Clusters. I'd like to test moving a OSD that contains active data between nodes and recover it.

One area I will probably miss options for testing are the shared or passthru IOMMU devices. From the ```lspci``` results below, I might be able to do something with the **iGPU** and the **Built-in NIC** and we can maybe do something with a **USB Device** as seen in the ```lsusb``` results. The SDIO Controller on some of the units have a Wifi card.

``` shell
root@pve1:~# uname -a
Linux pve1 6.8.8-3-pve #1 SMP PREEMPT_DYNAMIC PMX 6.8.8-3 (2024-07-16T16:16Z) x86_64 GNU/Linux
root@pve1:~# lsb_release -a
No LSB modules are available.
Distributor ID: Debian
Description:    Debian GNU/Linux 12 (bookworm)
Release:        12
Codename:       bookworm
root@pve1:~# lscpu -e
CPU NODE SOCKET CORE L1d:L1i:L2 ONLINE    MAXMHZ   MINMHZ       MHZ
  0    0      0    0 0:0:0         yes 1920.0000 480.0000  899.3300
  1    0      0    1 2:2:0         yes 1920.0000 480.0000  650.6640
  2    0      0    2 4:4:1         yes 1920.0000 480.0000 1921.6100
  3    0      0    3 6:6:1         yes 1920.0000 480.0000 1920.0240
root@pve1:~# lspci -tvnn
-[0000:00]-+-00.0  Intel Corporation Atom/Celeron/Pentium Processor x5-E8000/J3xxx/N3xxx Series SoC Transaction Register [8086:2280]
           +-02.0  Intel Corporation Atom/Celeron/Pentium Processor x5-E8000/J3xxx/N3xxx Integrated Graphics Controller [8086:22b0]
           +-0b.0  Intel Corporation Atom/Celeron/Pentium Processor x5-E8000/J3xxx/N3xxx Series Power Management Controller [8086:22dc]
           +-11.0  Intel Corporation Atom/Celeron/Pentium Processor x5-E8000/J3xxx/N3xxx Series SDIO Controller [8086:2295]
           +-14.0  Intel Corporation Atom/Celeron/Pentium Processor x5-E8000/J3xxx/N3xxx Series USB xHCI Controller [8086:22b5]
           +-1a.0  Intel Corporation Atom/Celeron/Pentium Processor x5-E8000/J3xxx/N3xxx Series Trusted Execution Engine [8086:2298]
           +-1c.0-[01]----00.0  Realtek Semiconductor Co., Ltd. RTL8111/8168/8411 PCI Express Gigabit Ethernet Controller [10ec:8168]
           \-1f.0  Intel Corporation Atom/Celeron/Pentium Processor x5-E8000/J3xxx/N3xxx Series PCU [8086:229c]
root@pve1:~# lsusb -tv
/:  Bus 02.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/6p, 5000M
    ID 1d6b:0003 Linux Foundation 3.0 root hub
/:  Bus 01.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/7p, 480M
    ID 1d6b:0002 Linux Foundation 2.0 root hub
    |__ Port 1: Dev 2, If 0, Class=Mass Storage, Driver=usb-storage, 480M
        ID 8644:8005 Intenso GmbG
    |__ Port 3: Dev 3, If 0, Class=Communications, Driver=cdc_ncm, 480M
        ID 0b95:1790 ASIX Electronics Corp. AX88179 Gigabit Ethernet
    |__ Port 3: Dev 3, If 1, Class=CDC Data, Driver=cdc_ncm, 480M
        ID 0b95:1790 ASIX Electronics Corp. AX88179 Gigabit Ethernet
```

The Wyse 3040 hardware specs of 2GB RAM, 8GB of eMMC storage, and 4-core CPU are extremely limiting. The 2GB of RAM makes you think about every bit of additional CT/VM workload you are adding along with OS system services. The 6GB of available eMMC storage makes you consider each software package installed to the OS drive. So this makes the environment both frustrating and interesting at the same time. You really think about every bit of the system where on my main cluster I just install whatever and add however many CT or VM to a node.

## Debian 12 on Wyse 3040


## Proxmox 8.2.2 overlay on Debian 12.5.2

asdef

## References

[So I'm going to pull from an earlier draft post I never released]
[/2024-04-02-dell-wyse-3040-initial-boot]

[Install a New Linux OS On a Dell Wyse 3040](https://qubitsandbytes.co.uk/install-a-new-os-on-a-dell-wyse-3040/) from Feb 2022 is an excellent article for starting out...

https://blog.m0les.com/2023/05/misusing-dell-wyse-3040-thin-client.html

https://blog.m0les.com/2023/06/thin-client-router-part-2-virtual.html

https://blog.m0les.com/2023/08/thin-client-router-part3-bare-metal-atom.html

https://www.apalrd.net/posts/2022/pve_bullseye/

https://blog.kroy.io/2020/01/17/the-baby-wyse-the-dell-3040/


