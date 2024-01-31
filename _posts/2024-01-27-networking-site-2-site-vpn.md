---
title:  "Site to Site VPN for the Homelabs"
layout: post
published: false
---

## VPN in a multi-site Home Network

I have two separate networks and two physical locations that I'd like to link up together seamlessly. For the purposes of the discussion it could be a corporation with a main headquarters and a satelite office. For me it is two residences separated by a three (3) hour drive with one in the city and one at the beach. Since remote work has become a real thing, I can seamlessly transition between my two houses for work... but not for my homelab hobby.

In the business world, my two physical sites or locations would be connected via a VPN to make the two networks seamlessly connected. This is called a site-to-site VPN which can come in several different implementations. I would want a split-tunnel so that public internet traffic at each site uses the closest network access and not back-haul all the internet traffic to one site. Corporations will often not do split-tunnel so they can monitor all public internet network traffic in one pipeline with security tools to protect from malicious ingress or egress traffic.

To typically do this in a corporate setting, I'd spend a good bit of money on some expensive network equipment to set this up.

## GL.iNet GL-AXT1800 (Slate AX) Pocket-Sized Wi-Fi 6 Gigabit Travel Router, Extender/Repeater for Hotel

[![ATX1800](/assets/images/GL-AXT1800-Slate-AX.jpg){:width="50%" height="50%"}](/assets/images/GL-AXT1800-Slate-AX.jpg){:target="_blank"}

I bought a [Slate-AX](https://www.gl-inet.com/products/gl-axt1800/) with a nice travel case back in Jan 2023 as part of setting up to work remotely from hotels and jumping between numerous wifi networks. Their product was really helpful in that use case and left me with a really good impression on their product line. The price to value was pretty high at least for me. It made for a stable consistent network as I worked intermittantly from hotels for about a year.

[![ATX1800-setup](/assets/images/GL-AXT1800-Slate-AX-setup-with-case.jpg){:width="50%" height="50%"}](/assets/images/GL-AXT1800-Slate-AX-setup-with-case.jpg){:target="_blank"}

Along the way, I learned GL.iNET were using [OpenWRT](https://openwrt.org/) a very capable linux based operating system I've used before. OpenWRT had a pile of additional networking features available with a bit of extra work on my part. I actually have a hacked original [Linksys WRT54G Wifi router](https://en.wikipedia.org/wiki/Linksys_WRT54G_series) sitting in my closet. But decided to keep this device vanilla to have it _just work_ out of the box last year but the possiblity exists to make this part of a VPN solution with it likely being a VPN client.

## GL.iNet MT2500A (Brume 2) Mini VPN Security Gateway

[![MT2500A](/assets/images/GL-MT2500A-Brume2.jpg){:width="50%" height="50%"}](/assets/images/GL-MT2500A-Brume2.jpg){:target="_blank"}

So during a GL.iNET sale last year, I picked up two of their [Brume2 VPN Servers devices model GL-MT2500A](https://www.gl-inet.com/products/gl-mt2500/). They are the size of a deck of cards but pack a heck of a punch well above their weight class and price. I upgraded to an aluminum case as I figure I'll be pushing the units and the heat disappation might be nice to have. The base units have 2.5Gbps WAN port and 1Gbps LAN port. I specifically didn't want a Wifi enabled VPN Server so these can be focused on providing their VPN Services.

## Defining the Requirements (or problem to solve)

First things is first... I have to define the networks and my overall goals or requirements.

1. Seamless access to network resources between the two private LAN networks
2. Options for local and public DNS
3. Future options to expose services to public internet
4. Optimized for performance (split-tunnel)
5. Secure Remote VPN client access to the overall network
6. Relatively easy to maintain and update
7. Keep my Google Nest Wifi Pro 6e mesh units

## Features available

We have [Google Fiber](https://fiber.google.com/cities/triangle/) in the city and [Spectrum Cable](https://www.spectrum.com) at the beach location. The Google Fiber connection is by far the faster 1Gbps synchronous both up and down with the option to upgrade to 2Gbps at any time for an extra couple bucks. Spectrum Cable struggles to do 250Mbps down and 15Mbps up on what is supposed to be a 1Gbps subscription line.

Two MT2500A that offer OpenVPN or WireGuard on the OpenWrt OS with 2.5Gbps WAN ports. An extra AX1800 Wifi for portable testing as a Wifi enabled VPN client.

Both locations have [Google Nest Wifi Pro 6e](https://store.google.com/us/product/nest_wifi_pro) and I have numerous extra older [Google Wifi](https://www.amazon.com/Google-WiFi-system-3-Pack-replacement/dp/B01MAW2294) units (non-6e) available.

The city location has a homelab running a ProxMox Cluster that I'll be writing about in a later post. I have aspirations of using it to host some public network services and my personal media library. The cluster is setup be workable as an HA capable LXC container host but would need a lot of work figuring out how to setup OpnSense/PiHole/etc... with the typical mess of LACP, LAGG, CARP, VIP and other network acrynoms to get it working. Also, I'm not keen on virtual network devices being used without a lot of thought put into them. I don't want a reboot of a node in my cluster to drop all networking at my house.

Each of the two locations have CAT5e or better network cables pulled but not all of the cabling is punched down on a patch panel or wall jack for immediate usage. So we have options in hauling around network devices at the locations.

I thought ahead have my two locations setup with different CIDR ranges of IP addresses in usage. The default CIDR for Google Wifi is 192.168.86.0/24 or the 256 IP addresses 192.168.86.0 - 192.168.86.255. Thinking ahead, I set those to different non-overlapping ranges and extended them from a /24 to a /23 so I get 512 IPs for each private subnet. I considered moving from the non-routable 192.168.0.0/16 range to someplace in the 10.0.0.0/8 but corporate networks have sucked up those ranges and I don't want to overlap those if possible. For private Ceph SAN networks, I've used the 10.0.0.0/8 in a couple places and completely avoided the 172.16.0.0/12 range.

## Network Diagrams

more tbd here...
