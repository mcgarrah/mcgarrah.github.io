---
title:  "Dell Wyse 3040 CMOS CR2032 Battery Replacement"
layout: post
published: false
---

I have collected eight (8) mostly functional [Dell Wyse 3040 thin clients](https://www.parkytowers.me.uk/thin/wyse/3040/) for use in my experimentation with [Proxmox Clusters and SDN](https://www.proxmox.com) and Site-2-Site VPN configurations with [Tailscale](https://tailscale.com/). They are very small low power consuming Debian 12 servers that have a 1Gbps NIC and run headless nicely. What is not nice is their CMOS batteries are all mostly dying on me and their connector is a odd type that is not supported by many vendors and are between $8-$12 USD to replace. This bothers me intensely as the actual CR2032 can be picked up for well under a dollar each at [LiCB CR2032 3V Lithium Battery(10-pack)](https://amzn.to/4bJTSUx) for a pack of 10 for $6 USD. Also, I'm picking these units up for between $20 and $45 on eBay and the $10 bite jacks my price per unit up a good bit. So what to do?

<!-- excerpt-end -->

I thought originally that I would figure out how to solder the wire connectors to the CR2032 but I am horrible at soldering and absolutely hate doing it. A small arc welder to spot weld came to mind as well after I disassembled one of the batteries and saw how they spot welded thin pieces of metal to the wire and battery. Then I came to my senses and told myself no new projects. Spot welding is a whole project and I have too many languishing right now.

Thus my first jack-rigged attempt at replacing the CMOS batteries was just using heat shrink with the original wires and thin pieces of metal. Surprisingly enough, it worked the first time, and the several other times I've had to replace the CMOS batteries. This will hopefully help someone else in the same bind that wants a cheap way out.

Here are pictures of the process. You will need a CR2032 battery, 39/64" heat shrink, a heat source, double sided mounting tape, and a pair of needle-nose like plyers to do this.

Investory and costs
| | |
| | |

[PICTURES from WhatsApp]

List of 3040s:

- tailscale ral (raleigh)
- tailscale ei (beach)
- tailscale wilson (wilson)
- 2 x WIFI enabled 5v 3a
- 1 x 5v 3a with broken plug (hacked in USB cable)
- - 2 x 12v 2a
