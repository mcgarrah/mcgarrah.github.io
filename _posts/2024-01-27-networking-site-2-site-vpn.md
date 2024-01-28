---
title:  "Site to Site VPN for the Homelabs"
layout: post
published: false
---

I have two homes with one in the city and one at the beach. With remote work being a real thing, I can seamlessly transition between my two houses for work... but not for my homelab hobby.

In the business world, my two physical sites would be connected via a VPN to make the two networks seamlessly connected. This is called a site-to-site VPN which come is different implementations. I would want a split-tunnel so that public internet traffic at each site uses the closest access and not back-haul the traffic to one site. Corporations will often not do split-tunnel so they can monitor all network traffic in one pipeline.

GL.iINET has some very nice network products. I bought a Slate Travel Router (VPN Client only) earlier and it was very helpful to supply a stable consistent network as I worked in hotels for part of a year.

So during one of their sales, I picked up two of their Brume2 VPN Servers (GL-MT2500A). They are the size of a deck of cards but pack a punch.

https://www.gl-inet.com/products/gl-mt2500/

The MT2500 has options of using OpenVPN or WireGuard on the OpenWrt OS.

