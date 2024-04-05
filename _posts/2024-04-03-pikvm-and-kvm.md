---
title:  "PiKVM v3 and AIMOS 8-port KVM Setup"
layout: post
published: false
---

Setting up my [PiKVM v3](https://docs.pikvm.org/v3/) has been a journey spanning well over a year to get it the way I wanted. The goal was to get a ~cheap~ frugal setup that let me manage more than just one or a couple machines and both have the PiKVM WebUI and local KVM (keyboard / video / mouse). So I have a local keyboard/video/mouse on the test bench that functions when sitting near the servers and also the remote PiKVM WebUI with keyboard/video/mouse when remotely accessing or just across the house. That was a trippy path to get it all working cleanly. Hopefully, my final setup and failures along hte way are useful to someone else heading down this path.


To start off, below are all the parts I collected over the fifteen (15) months while figuring this out. Some of that time was me just not finishing or having other projects to sort out. I used the PiKVM on single machines along they way but it didn't feel like the best use of the expensive unit.

So full disclosure, I bought some extra pieces along the way. One was a $65 [CKLau KVM Switch HDMI 4 Port wit Audio and 4 kit Cables and Hotkey Switching](https://amzn.to/3U1OiXY) that only got me so far. A $35 [TCNEWCL KVM Switch 4 Port, HDMI KVM Switcher 4Kx2K@30Hz for 4 Computers](https://amzn.to/3xkMhNv) without hot-key support but did have a USB port for hacking was also another attempt at cheap solutions. They are both *good enough* KVMs but not for use with the PiKVM so far as I could get them going.

## Parts

So the center piece was the purchase of a [PiKVM v3 Pre-Assembled](https://cloudfree.shop/product/pikvm-v3-pre-assembled/) on Jan 19 2023 during the height of the Pi shortage and threw in some exta assessories shown below.

| Price | Description / Link |
| -----:| -------- |
| $250 | PiKVM V3 Pre-Assembled |
| $4 | Cat 6 Ethernet Patch Cable - 6 ft |
| $7 | USB 3.0 Cable - Type C to Type A - 6 ft |
| $5 | HDMI Cable - 6 ft |
| $8 | Raspberry Pi 4 Official USB-C Power Supply |
| $6 | Minigrabber Hooked Test Leads |
| **$280** | **Total** |

Parts bought for project:

| Price | Description / Link |
| -----:| -------- |
| $13 | [USB C Splitter USB C to USB C Female Adapter USB Y Splitter Cable](https://amzn.to/3U5C2FG) |
| $15 | [HDMI Splitter 4K, 1x2 HDMI Display Duplicate/Mirror, WARRKY HDMI Splitter 1 in 2 Out](https://amzn.to/3xqMmPV) |
| $10 | [Male to Female USB Type C USB-C Cable with On Off Power Switch](https://amzn.to/43HsLXT) |
| $15 | [Laptop Charger for Lenovo, Thinkpad, Yoga, 65W 45W, USB C Connector](https://amzn.to/3J7OxKW) |
| $11 | [5 Pack - 6FT HDMI Cables](https://amzn.to/3TIT4bC) |
|  $9 | [10 Pack - 4FT HDMI Cable](https://amzn.to/43KNhGR) Note: AVOID for this KVM |
| $21 | [Amazon Basics 4 Port USB to USB 3.0 Hub with 5V/2.5A power adapter](https://amzn.to/3TJ1sI8) |
| $81 | [HDMI KVM Switch, 8 in 1 Out USB 2.0 HDMI KVM Switcher Box](https://amzn.to/43ItIPz) AIMOS Branded |
| **$175** | **Total** |

Misc Parts laying around:

| Price | Description / Link |
| -----:| -------- |
| $20 | [Desk Clamp Power Strip Individual Switches](https://amzn.to/3J5YhoR) |
| $21 | 3 x [2 Pack - DVI to HDMI, Bidirectional DVI (DVI-D) to HDMI Male to Female Adapter](https://amzn.to/4cInJ1i) |
| $24 | 3 x [Mini DisplayPort to DVI, Mini DP to DVI Male to Female Adapter](https://amzn.to/3vEvdBL) |
| $xx | []() |
| **$65** | **Total** |

All in I'm at about at about **$520 USD** on this configuration and setup.  That has me at about **$65** per machine supported.

## Configuration

TODO: Diagram of the layout of all parts and accessories...

First the startup order and cabling up in a certain order is important for the EDID handling.

My choice of the AIMOS 8-port KVM has an impact on capabilies. The PiKVM V3 handles the backfeed power issues for me.

Putting the USB-C Y-Connector and HDMI Splitter in the right places matters a lot.  Ask me how I know?!? Yeah plugged them in wrong a couple times. I plan to label everything now that it works.
