---
title:  "Power Supply upgrade for GPUs in the Homelab"
layout: post
published: false
---

I want an extra ~350w of power available for a GPU that cannot run off PCIe bus power of 75w or 25w in some very old [Dell Optiplex 990 Mini Tower](https://www.dell.com/support/home/en-us/product-support/product/optiplex-990/overview) nodes in my Proxmox cluster.

When one of my power supplies died earlier I bought on eBay a [NEW 750W Dell OptiPlex 9010 990 790 Power Supply Replace / Upgrade](https://www.ebay.com/itm/334146551516) that was ~750w and the same form factor as those units. This was just fast purchase to grab something that would ship the next day with no plan for an upgrade but I did pay attention that was both better and new.

So I have one machine that has the extra wattage available for a much bettern GPU like a [Nvidia GeForce RTX 3060 12Gb](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3060-3060ti/).

<!-- excerpt-end -->

Now the hard question, should I do this? These are much older machines. I'm really making them do something that they are not best suited to do. Maybe I should be buying newer better base hardware or god-forbid servers?!? I've already lamented this in an earlier post [ProxMox 8.2 for the Homelabs](https://www.mcgarrah.org/proxmox-8-homelab/) and more pain in [Proxmox VE 8.1 to 8.2 upgrade issues in the Homelabs](https://www.mcgarrah.org/proxmox-upgrade-issues/) where I question the sanity of this build.

The original power supply in the Dell Optiplex 990s are 265w. I found a reasonable 750w-775w one to replace into the unit with ~500w extra to support a GPU. We want some headroom for the GPU in case I get a better one on an auction.

## Power Supply Capabilies

PCIe slot power (motherboard):

* PCIe x1: Can provide up to 10 W of power, unless configured as a high-power card
* PCIe x4 and x8: Can provide up to 25 W of power
* PCIe x16: Can provide up to 75 W of power

Power Supply connector power:

* SATA power connectors: Can safely provide up to 54 Watts of power.
* PCIe 6-pin power connector: Can provide up to 75 W of power
* PCIe 8-pin power connector: Can provide up to 150 W of power
* Molex power connectors: Can safely provide up to 132 Watts* of power.
  * Molex has two power pins, 12V and 5V. Max current is 11A. This means that the theoretical limit is 187 Watts.

Connectors for the [KDMPower 750W Dell OptiPlex 9010 990 790 Power Supply Replace / Upgrade](https://www.ebay.com/itm/334146551516)

* 1 x Mother Board Connector
* 4 x CPU connectors
* 6 x SATA Connectors
* 3 x 4-Pin Molex
* **2 x PCI-E (6+2)**

The last connector is the one that typically helps with the GPUs.

The Molex with a converter is the next place to go. There is a lot of variety in here.

* Dual 4Pin IDE Molex to GPU Dual 8Pin(6+2)Pin Supply Cable
* 4 Pin Molex to 8 Pin 6+2Pin Video Card GPU Power Supply Cable


## GPU comparisons

[Nvidia Tesla K80](https://www.nvidia.com/en-gb/data-center/tesla-k80/) that are just two 12gb vram gpu cards plastered together which are all over the place for pricing between $50 - $250 on [ebay](https://www.ebay.com/itm/285269093876).

Here is a list of GPUs to review:

* Nvidia Tesla P40
* Nvidia Tesla K40m
* Nvidia Tesla M40
* Nvidia Tesla M60
* NVIDIA GeForce GTX TITAN XP
* Nvidia GeForce RTX 3060 12GB on [ebay](https://www.ebay.com/itm/126046122624)
