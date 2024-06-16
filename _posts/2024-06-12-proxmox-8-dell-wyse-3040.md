---
title:  "ProxMox 8.2.2 Cluster on Dell Wyse 3040s"
layout: post
published: false
---

I need a place to test and try out [Proxmox 8.2.2 SDN](https://pve.proxmox.com/pve-docs/chapter-pvesdn.html) ([Software Defined Networking](https://en.wikipedia.org/wiki/Software-defined_networking)) features and capabilities and as a bonus would love to test from Ceph configuration changes as well. I do not want to do it on my semi-production Proxmox 8.2.2 Ceph enabled Cluster that I have mentioned in earlier posts. With 55TiB of raw storage and 29TiB of it loaded up with content, that would be painful to rebuild or reload if I made a mistake during my testing of SDN or Ceph capabilies.

Fortunately for me, [Apalrd](https://www.apalrd.net) post on this [Installing Proxmox VE 7 on Debian Bullseye(]https://www.apalrd.net/posts/2022/pve_bullseye/) that used an earlier [Install Proxmox VE on Debian Buster](https://pve.proxmox.com/wiki/Install_Proxmox_VE_on_Debian_Buster) document for his exploration is where I got the idea to create an extremely low-end Proxmox 8 cluster for any testing that I didn't want on my main cluster.

Also fortunately, I have three (3) extra [Dell Wyse 3040s](https://www.parkytowers.me.uk/thin/wyse/3040/) that will eventually become my [Wifi 6e Tailscale](https://tailscale.com/) endpoint, or [Home Assistant](https://www.home-assistant.io/) server, or an OpenWRT router from [Recompiling OpenWrt to run natively on the 3040](https://blog.m0les.com/2023/08/thin-client-router-part3-bare-metal-atom.html) but are currently just sitting on my shelf. With two nodes, I can test Proxmox HA but with three nodes, I can test Proxmox HA and a Ceph Cluster as well. So three is the magic number here...



So I'm going to pull from an earlier draft post I never released


[Install a New Linux OS On a Dell Wyse 3040](https://qubitsandbytes.co.uk/install-a-new-os-on-a-dell-wyse-3040/) from Feb 2022 is an excellent article for starting out...

https://blog.m0les.com/2023/05/misusing-dell-wyse-3040-thin-client.html

https://blog.m0les.com/2023/06/thin-client-router-part-2-virtual.html

https://blog.m0les.com/2023/08/thin-client-router-part3-bare-metal-atom.html

https://www.apalrd.net/posts/2022/pve_bullseye/

https://blog.kroy.io/2020/01/17/the-baby-wyse-the-dell-3040/


