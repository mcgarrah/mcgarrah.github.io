---
title:  "Power Supply upgrade for GPUs in the Homelab"
layout: post
published: true
tags: [gpu, power-supply, hardware, homelab, upgrade, planning, dell-optiplex]
categories: [technical, homelab, hardware]
---

I want an extra ~350w of power available for a GPU that cannot run off PCIe bus power of 75w or 25w in some very old [Dell Optiplex 990 Mini Tower](https://www.dell.com/support/home/en-us/product-support/product/optiplex-990/overview) nodes in my Proxmox cluster.

When one of my power supplies died earlier and I bought on eBay a [NEW 750W Dell OptiPlex 9010 990 790 Power Supply Replace / Upgrade](https://www.ebay.com/itm/334146551516) that was ~750w and the same form factor as those nodes PSU. This was just fast purchase to grab something that would ship the next day with no plan for an upgrade but I did pay attention that was both better and newer with a warranty.

So I have one machine that has the extra wattage available for a much better GPU like a [Nvidia GeForce RTX 3060 12Gb](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3060-3060ti/).

<!-- excerpt-end -->

Now the hard question, should I even do this? These are much older machines over a decade old. I'm really making them do something that they are not best suited to do. Maybe I should be buying newer better base hardware or god-forbid servers?!? I've already lamented this in an earlier post [ProxMox 8.2 for the Homelabs](/proxmox-8-homelab/) and more pain in [Proxmox VE 8.1 to 8.2 upgrade issues in the Homelabs](/proxmox-upgrade-issues/) where I question the sanity of this build.

At this point, I think I am going to keep going and extend what I have setup. If I change direction later, I can move most of the costly components of the investment to a new system.

The original power supply in the Dell Optiplex 990s are 265w. I found a reasonable 750w-775w one to replace into the unit with ~500w extra to support a GPU. We want some headroom for the GPU in case I get a better one on an eBay auction.

## Power Supply Capabilies

Here is me learning and writing down about how to get power to different pieces of a machine. I've been doing this awhile so some of it is common sense for me but a lot has changed in the last couple years to catch up on.

PCIe slot power (motherboard):

* `PCIe x1`: Can provide up to 10 W of power, unless configured as a high-power card
* `PCIe x4 and x8`: Can provide up to 25 W of power
* `PCIe x16`: Can provide up to 75 W of power

Power Supply connector power:

* SATA power connectors: Can safely provide up to 54 Watts of power.
* PCIe 6-pin power connector: Can provide up to 75 W of power
* PCIe 8-pin power connector: Can provide up to 150 W of power
* Molex power connectors: Can safely provide up to 132 Watts* of power.
  * Molex has two power pins, 12V and 5V. Max current is 11A. This means that the theoretical limit is 187 Watts.

Connectors for the [KDMPower 750W Dell OptiPlex 9010 990 790 Power Supply Replace / Upgrade](https://www.ebay.com/itm/334146551516) which I have already bought one as a replacement for a bad PSU.

* 1 x Mother Board Connector
* 4 x CPU connectors
* 6 x SATA Connectors
* 3 x 4-Pin Molex
* **2 x PCI-E (6+2)**

The last connector is the one that typically helps with the GPUs. Those mean I can just plug in the GPU.

For extra options, converting the Molex with a converter cable is the next place to go. There is a lot of variety in here and reading tells me to be careful as there are some that can burn and damage your system.

* Dual 4Pin IDE Molex to GPU Dual 8Pin(6+2)Pin Supply Cable
* 4 Pin Molex to 8 Pin 6+2Pin Video Card GPU Power Supply Cable

## Conclusions

I'm going to keep an eye out for a deal on a [nVidia RTX 3060 12gb](https://www.ebay.com/sch/i.html?_dmd=1&_nkw=rtx+3060+12gb) card either on eBay or Facebook Marketplace. This will let me test out some ideas with a relatively small incremental investment of a couple hundred dollars on a new GPU. I'll write up whatever comes of this as it happens.
