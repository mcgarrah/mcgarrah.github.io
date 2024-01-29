---
title:  "Site to Site VPN for the Homelabs"
layout: post
published: false
---

## VPN in a multi-site Home Network

I have a problem with two separate networks and locations that I'd like to link up together seamlessly. For the purposes of the discussion it could be a corporation with a main headquarters and a satelite office. For me it is two residences separated by a three (3) hour drive with one in the city and one at the beach. Since remote work has become a real thing, I can seamlessly transition between my two houses for work... but not for my homelab hobby.

In the business world, my two physical sites would be connected via a VPN to make the two networks seamlessly connected. This is called a site-to-site VPN which can come in several different implementations. I would want a split-tunnel so that public internet traffic at each site uses the closest network access and not back-haul all the internet traffic to one site. Corporations will often not do split-tunnel so they can monitor all public internet network traffic in one pipeline with security tools to protect from malicious ingress or egress traffic.

## GL.iNet GL-AXT1800 (Slate AX) Pocket-Sized Wi-Fi 6 Gigabit Travel Router, Extender/Repeater for Hotel

https://www.gl-inet.com/products/gl-axt1800/

I bought a Slate-AX with a nice case back in Jan 2023 as part of being able to work remotely from hotels and jumping between wifi networks. Their product was really helpful in that use case and left me with a really good impression on this products. The price to value was pretty high at least for me. It made for a stable consistent network as I worked intermittantly from hotels for a year.

## GL.iNet MT2500A (Brume 2) Mini VPN Security Gateway

https://www.gl-inet.com/products/gl-mt2500/

So during one of their sales, I picked up two of their Brume2 VPN Servers (GL-MT2500A). They are the size of a deck of cards but pack a heck of a punch well above their weight class and price. I upgraded to an aluminum case as I figure I'll be pushing the units and the heat disappation might be nice to have. The base units have 2.5Gbps WAN port an d 1Gbps LAN port. I specifically didn't want a Wifi enabled VPN Server so these can be focused on providing their VPN Services.

## Defining the Requirements (or problem to solve)

First things is first... I have to define the networks and my overall goals or requirements.

1. Seamless access to network resources between the two private LAN networks
2. Options for local and public DNS
3. Future options to expose services to public internet
4. Optimized for performance (split-tunnel)
5. Secure Remote VPN client access to the overall network
6. Relatively easy to maintain and update

## Features available

We have [Google Fiber](https://fiber.google.com/cities/triangle/) in the city and [Spectrum Cable](https://www.spectrum.com) at the beach location. The Google Fiber connection is by far the faster 1Gbps synchronous both up and down. Spectrum Cable struggles to do 250Mbps down and 15Mbps up on what is supposed to be a 1Gbps subscription line.

Two MT2500A that offer OpenVPN or WireGuard on the OpenWrt OS with 2.5Gbps WAN ports. An extra AX1800 Wifi for portable testing as a client.

Both locations have [Google Nest Wifi Pro 6e](https://store.google.com/us/product/nest_wifi_pro) and I have numerous extra older [Google Wifi](https://www.amazon.com/Google-WiFi-system-3-Pack-replacement/dp/B01MAW2294) units (non-6e) available.

The city location has a ProxMox Cluster that I'll be writing about in a later post. I have aspirations of using it to host some public network services and my media library. The cluster is setup be workable as an HA capable LXC container host but would need a lot of work figuring out how to setup OpnSense/PiHole/etc... with the typical mess of LACP, CARP, VIP and other network acrynoms to get it working. Also, I'm not keen on virtual network devices being used without a lot of thought put into them. I don't want a reboot of a node in my cluster to drop all networking at my house.

Each location has CAT5e or better cables pulled but not all of the cabling is punched down on a patch panel or wall jack for immediate usage.

more tbd here...
