---
title:  "Dell Wyse 3040 CMOS CR2032 Battery Replacement"
layout: post
published: true
---

I have collected nine (9) mostly functional [Dell Wyse 3040 thin clients](https://www.parkytowers.me.uk/thin/wyse/3040/) for use in my experimentation with [Proxmox Clusters and SDN](https://www.proxmox.com) and Site-2-Site VPN configurations with [Tailscale](https://tailscale.com/). Yes, I know I have a problem. :)

[![Dell Wyse 3040 with bad cmos battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-00.png){:width="30%" height="30%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-00.png){:target="_blank"}

On the upside, they are very small low power consuming Debian 12 servers that have a 1Gbps NIC and run headless nicely once you fix the BIOS settings and Debian configuration correctly. What is not nice is their CMOS batteries are all mostly dying on me and their connector is a odd type that is not supported by many vendors and are between $8-$12 USD to replace. For example the [Rome Tech CR2032 CMOS BIOS Battery for Dell Wyse 3040](https://amzn.to/3LzGnfg) is about $9.89 USD as of posting this. This bothers me intensely as the actual CR2032 can be picked up for well under a dollar ($1 USD) each at [LiCB CR2032 3V Lithium Battery(10-pack)](https://amzn.to/4bJTSUx) for a pack of 10 for $6 USD. Also, I'm picking these units up with power adapter for between $20 and $45 on eBay and the $10 bite jacks my price per unit up a good bit. So what to do?

<!-- excerpt-end -->

[![Dell Wyse 3040 opened up](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-01.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-01.png){:target="_blank"}

I thought originally that I would figure out how to solder the wire connectors to the CR2032 but I am horrible at soldering and absolutely hate doing it. A small arc welder to spot weld came to mind as well after I disassembled one of the batteries and saw how they spot welded thin pieces of metal to the wire and battery. Then I came to my senses and told myself ***no new projects***. Spot welding is a whole project and I have too many languishing right now.

Thus my first jack-rigged attempt at replacing the CMOS batteries was just using heat shrink with the original wires and thin pieces of metal. Surprisingly enough, it worked the first time, and the several other times I've had to replace the CMOS batteries. This will hopefully help someone else in the same bind that wants a cheap way out.

Below are some pictures of the process. You will need CR2032 batteries, some ~39/64" heat shrink, a heat source, double sided mounting tape, and a pair of needle-nose like plyers to do this.

Some of the Investory and Costs

| Price | Description / Link |
| -----:| ------- |
| $6 | [LiCB CR2032 3V Lithium Battery(10-pack)](https://amzn.to/4bJTSUx) |
| $8 | [3M Double Coated Foam Tape, 0.75" width x 5yd length (1 roll)](https://amzn.to/4ddA0dp) |
| $9 | [Heat Shrink Tubing, 3/4"(20mm)](https://amzn.to/3YijswU) |
| **$23** | **Total** |

[![CR2032 Batteries](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-02.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-02.png){:target="_blank"}

[![Double Sided Tape](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-03.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-03.png){:target="_blank"}

[![Heat Shrink Tubing](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-04.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-04.png){:target="_blank"}

You'll also need a cigarette lighter or heat gun to shrink the tubing. A needle nosed plyer will also be helpful.
I picked my supplies up at the local [Harbor Freight](https://www.harborfreight.com/).

Once you have the Wyse 3040 opened up, you will immediate see the 1mm cmos battery in the upper left corner. It is affixed by a piece of double sided tape to the mother board. You will have to pull it hard to get it off. I suggest unplugging it first. This prevents damaging the connector or wire that you will need to keep.

[![Old CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-05.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-05.png){:target="_blank"}

After pulling the battery off, you will need to get the heat shrink off the battery to expose the battery and metal connectors.

[![Exposed bad CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-06.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-06.png){:target="_blank"}

I usually at this point cut some heat shrink tubing to match the size of the battery before I pull the metal tabs off the expired battery.

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-07.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-07.png){:target="_blank"}

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-08.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-08.png){:target="_blank"}

Next is gently prying off the metal tabs from the face of the battery. I used needle nose plyers and a gentle twisting motion to overcome the electric spot welds.

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-09.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-09.png){:target="_blank"}

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-10.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-10.png){:target="_blank"}

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-11.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-11.png){:target="_blank"}

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-12.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-12.png){:target="_blank"}

Next step is to place the metal tabs inside the heat shrink and I hold them in place with the plyers as I apply heat to shrink the tubing. I would recommend using the plyers to flatten the metal tabs so they are as flat as possible.

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-13.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-13.png){:target="_blank"}

Make sure the heat shrink is tight and the metal tabs are flat and secured against the battery facings. Red cable on the (+) and black on the (-) side of the battery.

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-14.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-14.png){:target="_blank"}

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-15.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-15.png){:target="_blank"}

Last step is to put some of the double sided tape on the back of the battery and put it back on the motherboard. Then plug in the battery.  Do not force the connector in. It only fits one way.

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-16.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-16.png){:target="_blank"}

I added a little sticker to remind me the date I replaced the CMOS Battery and that it is not welded.

[![CMOS Battery](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-17.png){:width="50%" height="50%"}](/assets/images/wyse3040-cmos/wyse-3040-bad-cmos-17.png){:target="_blank"}

I have done about six or seven of these so far on my set of nine (9) Wyse 3040s. They all seems to be working fine. It makes no difference if they are 5v/3a or 12v/2a power adapter versions. If you are only doing one or two, then the $10 replacements might be a good choice. For me, this just made sense to make the investment.

Cheers from the frugal hardware hacking guy. Hope this helps someone out there.
