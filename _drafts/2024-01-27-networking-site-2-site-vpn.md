---
title:  "Site to Site VPN for the Homelabs"
layout: post
published: false
categories: [technical, networking]
tags: [vpn, wireguard, tailscale, headscale, brume2, openwrt, gl-inet, networking, homelab, carp]
---

## VPN in a multi-site Home Network

I have two separate networks and two physical locations that I'd like to link up together seamlessly. For the purposes of this post, those could be a corporation with a main headquarters and a satelite office. For me it is two residences separated by a three (3) hour drive with one in the city and one at the beach. Since remote work has become a real thing, I can seamlessly transition between my two houses for work... but not for my homelab hobby.

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

## VPN Technology Comparison: Tailscale / Headscale vs WireGuard on Brume2

The Brume2 devices support both OpenVPN and WireGuard natively. The question is whether to use raw WireGuard directly on the Brume2 or layer a mesh VPN solution like Tailscale or Headscale on top.

### WireGuard Direct (on Brume2)

- Native support in GL.iNet firmware and OpenWRT
- Full control over routing and split-tunnel configuration
- No external dependencies or coordination servers
- Manual key management and peer configuration
- Best performance — runs directly on the hardware

### Tailscale

- WireGuard-based mesh VPN with automatic key management
- NAT traversal handled automatically (DERP relay servers)
- Easy client onboarding — works behind most firewalls without port forwarding
- Coordination server is Tailscale-hosted (SaaS dependency)
- Free tier available for personal use

### Headscale

- Self-hosted open-source implementation of the Tailscale coordination server
- Same client-side experience as Tailscale but fully self-hosted
- Could run as an LXC container on the Proxmox cluster
- More complex to set up and maintain than Tailscale SaaS
- Full control over the coordination plane

### Decision Factors

- Do I want to depend on Tailscale's SaaS for my homelab connectivity?
- Is the Brume2 powerful enough to run Tailscale/Headscale client alongside its other duties?
- How does this interact with the Google Nest Wifi Pro mesh at each site?
- CARP (Common Address Redundancy Protocol) considerations for HA if running VPN on the Proxmox cluster instead of dedicated hardware

TODO: Test WireGuard direct on Brume2 first, then evaluate Tailscale overlay.

## CARP and High Availability Networking

CARP (Common Address Redundancy Protocol) provides failover for network services using virtual IP addresses. Relevant if the VPN endpoint moves from dedicated Brume2 hardware to a virtualized solution on the Proxmox cluster.

This ties into the broader question of whether network-critical services (VPN, DNS, DHCP) should run on dedicated hardware or as HA containers on the cluster. The risk of a cluster node reboot dropping all house networking is a real concern.

Related: [Google WiFi with OpenWRT](/google-wifi-with-openwrt/) covers the OpenWRT side of this setup.

## Reference Links

- [Turn off DHCP on Google WiFi to use another DHCP Server](https://www.reddit.com/r/GoogleWiFi/comments/p0h4wu/turn_off_dhcp_on_google_wifi_to_use_another_dhcp/) — Relevant if running DHCP from the cluster
- [Link Aggregation (LAG/LACP) overview video](https://youtu.be/NVO2UV_HQhs?si=pueS2LnSDVEhaxmE)
- [LoRaWAN by Apalrd](https://youtu.be/HWF6Qm7JhJU?si=PwX1Ah21EFCPFa-j) — Long-range IoT networking option
- [HP ProCurve CLI Cheat Sheet](https://community.spiceworks.com/how_to/85991-hp-procurve-cli-cheat-sheet) — Includes LAG/LACP configuration
