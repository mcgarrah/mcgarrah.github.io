---
title:  "Buying a 10Gbps or higher network on a homelab budget"
layout: post
published: false
---

This is a project I've been thinking about for a long time...  how to get 10gbpe+ networking in a homelab without breaking the bank.

First option is just getting some DAC Cables and dual port 10Gbpe NICs then build a point to point ring network. That is relatively cheap and would set me up for future switched networks.  DACs could be swapped out for GBics that use copper (thermal issues) or fiber (delicate).

Next is a relatively cheap at a couple hundred dollars switch with likely a low number of SFP+ ports. This is ~$200-$500 with anywhere from 2 to 16 ports at 10Gbps. Often switches with 10Gbps advertised only have one or two ports at that speed so shop carefully. You still have the cost of the NICs and cabling but only need one port on the NIC.

Lastly, you could go all in with an enterprise switch like the HP ProCurve 5406zl which is a module hosting monster of a switch. These are massively upgradable but come with a lot of complexity to setup and manage. They are also incrediably loud (indended for server rooms) and suck a ton of power which generates lots of heat (thermal load). These are getting cheaper but are heavy to ship and still usually several hundred dollars with modules that can cost thousands. Don't expect a warantee on these as they are being pushed out of enterprise usage as end of life. 

1. Point to Point network

if you buy Dual port NICs then you can run a ring network between each node as Direct connections. it complicates your network config but worth it. 

2. Switched network

Here are a pile of network switches that are both new and ancient that could support 10Gbps.

Price per SFP+ port is one metric.

Power consumption and acoustic (noise) are others to consider.

Maybe get Amazon affilitate links for pricing (small kick back to me) on MikroTik switches

## Mikrotik switches

- Mikrotik CRS310-1G-5S-4S+IN 10Gigabit Switch 1G port 5 x SFP ports 4 x SFP+ port
 - ~$200 USD
 - 5 SFP 1Gbps
 - 4 SFP+ 10Gbps
 - 1 1Gbps Ethernet

- MikroTik CRS309-1G-8S+IN Switch Gigabit Ethernet Port and 8x SFP 10 Gbps Ports
 - ~$270 USD
 - 1 1Gbps Ethernet
 - 8 SFP+ 10Gbps

- MikroTik CRS305-1G-4S+IN 5-port Network Switch 10Gbps Gigabit Dual System
 - ~$200 USD
 - 1 1Gbps Ethernet
 - 4 SFP+ 10Gbps

- MikroTik CRS317-1G-16S+RM Cloud Router Switch Rack-mountable Manageable Switch with Layer 3 Features
 - ~$480 USD
 - 1 1Gbps Ethernet
 - 16 SFP+ 10Gbps

## ZL Chassis 
- HP Procurve 5406zl Switch
  - crazy price range on ebay $350 to $4000
  - Plugin modules for functionality range widely
  - Six module slots

## ZL modules
- J9309A - HP ProCurve 4-port 10GbE SFP+ ZL Module 2C3 (module)
  - 4 SFP+ 10Gbps
- HP Procurve J9535A 20-Port 4-SFP Gig-T/SFP PoE V2 ZL Module for 5400zl Switch
- HP ProCurve 24 Port Gig-T PoE+ V2 zl Module - J9534A

This only gets you part of the way to the price.


## Dual NIC 10Gbps

- 10Gb SFP+ PCI-E Network Card NIC, with Broadcom BCM57810S Chip, Dual SFP+ Port, PCI Express X8, Support Windows Server/Linux/VMware https://a.co/d/3iLT95r

- 10Gb NIC SFP+ PCIE Network Card with Broadcom BCM57810S Controller, Dual SFP+ Ports, Fits for PCI-E X 8/x16, PCI Express LAN Card Support Windows Server/Windows/Linux/VMware https://a.co/d/2e8q0UF

- 10Gb PCI-E NIC Network Card, with Broadcom BCM57810S Chipset, Dual SFP+ Port, PCI Express Ethernet Lan Adapter Support Windows Server/Windows/Linux/VMware https://a.co/d/aIRizA9

## DAC 

cable for direct connection without gbics in sfp ports

- SFP+ Cable, 10G SFP+ DAC, 0.5M(1.64ft), Passive Direct Attach Copper Twinax Cable for Cisco SFP-H10GB-CU0.5M, Ubiquiti UniFi UC-DAC-SFP+, Meraki, Mikrotik, Intel, Fortinet, Netgear, 0.25m-7m https://a.co/d/fuTFqlt

- SFP+ Cable, 10G SFP+ DAC, 1M(3.3ft), Passive Direct Attach Copper Twinax Cable for Cisco SFP-H10GB-CU1M, Ubiquiti UniFi UC-DAC-SFP+, Meraki, Mikrotik, Intel, Fortinet, Netgear and More https://a.co/d/9naZi3p
