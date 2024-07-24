---
title:  "ProxMox 8.2.2 Cluster on Dell Wyse 3040s"
layout: post
published: false
---

I want a place to test and try out new features and capabilities in [Proxmox 8.2.2 SDN](https://pve.proxmox.com/pve-docs/chapter-pvesdn.html) ([Software Defined Networking](https://en.wikipedia.org/wiki/Software-defined_networking)). I would also like to be able to test some Ceph Cluster configuration changes that are risky as well. I do not want to do it on my semi-production Proxmox 8.2.2 Ceph enabled Cluster that I have mentioned in earlier posts. With 55TiB of raw storage and 29TiB of it loaded up with content, that would be painful to rebuild or reload if I made a mistake during my testing of SDN or Ceph capabilies.

[![Test in Prod, what could go wrong?](/assets/images/what-could-go-wrong.jpg){:width="30%" height="30%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/what-could-go-wrong.jpg){:target="_blank"}

<!-- excerpt-end -->

Fortunately for me, [Apalrd](https://www.apalrd.net) post on this [Installing Proxmox VE 7 on Debian Bullseye](https://www.apalrd.net/posts/2022/pve_bullseye/) that used an earlier [Install Proxmox VE on Debian Buster](https://pve.proxmox.com/wiki/Install_Proxmox_VE_on_Debian_Buster) document for his exploration is where I got the idea to create an extremely low-end Proxmox 8 cluster for any testing that I didn't want on my main cluster.

Also fortunately, I have an extra three (3) [Dell Wyse 3040s](https://www.parkytowers.me.uk/thin/wyse/3040/) that will eventually become a [Wifi 6e Tailscale](https://tailscale.com/) endpoint, or [Home Assistant](https://www.home-assistant.io/) server, or an OpenWRT router from [Recompiling OpenWrt to run natively on the 3040](https://blog.m0les.com/2023/08/thin-client-router-part3-bare-metal-atom.html) but are currently just sitting on my shelf in a shoebox. With just two nodes, I can test Proxmox HA but with three nodes, I can test Proxmox HA, add a Ceph Cluster, and new SDN Datacenter features as well.

I added three (3) [Amazon Basics USB 3.0 to 10/100/1000 Gigabit Ethernet Internet Adapter](https://amzn.to/3ybtOUw) so I can have two network interfaces to make testing more expansive and interesting. I also pulled out three 8GB USB2 Thumbdrives from an old box to use as the Ceph OSD media and found a three pack of [SanDisk 32GB 3-Pack Ultra Fit USB 3.1 Flash Drive (3x32GB)](https://amzn.to/3YesqLq) for under $20 to upgrade the Ceph storage and learn about transitioning between media in Ceph Clusters.

The 2GB of RAM is extremely restrictive and makes you think about every bit of additional workload you are adding. The 6GB of available eMMC storage makes you consider each package installed to the OS drive. So this makes the environment both frustrating and interesting at the same time.

[So I'm going to pull from an earlier draft post I never released]
[/2024-04-02-dell-wyse-3040-initial-boot]

[Install a New Linux OS On a Dell Wyse 3040](https://qubitsandbytes.co.uk/install-a-new-os-on-a-dell-wyse-3040/) from Feb 2022 is an excellent article for starting out...

https://blog.m0les.com/2023/05/misusing-dell-wyse-3040-thin-client.html

https://blog.m0les.com/2023/06/thin-client-router-part-2-virtual.html

https://blog.m0les.com/2023/08/thin-client-router-part3-bare-metal-atom.html

https://www.apalrd.net/posts/2022/pve_bullseye/

https://blog.kroy.io/2020/01/17/the-baby-wyse-the-dell-3040/


