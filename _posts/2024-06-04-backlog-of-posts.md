---
title:  "Backlog of Posts"
layout: post
published: true
---

I've got a backlog of posts I want to do on various topics. A couple of recent posts, I figured getting out something rough was better than not getting it out and just posted soemthing that felt like it needed another draft or two. I'll likely review those quickly posted items and update them as time permits.



Here is a dump of my unpublished posts that need polishing to release:

* Learning Jekyll
* Site to Site VPN for the Homelabs
* Link Aggregated (LAG) and LACP NIC Bonding
* HP ProCurve Switch Java WebUI (Java JNLP WebStart)
* Dell Wyse 3040 Initial Setup (tailscale endpoints)
* PiKVM v3 and AIMOS 8-port KVM Setup (hacking the webui)
* ProxMox 8 Lessons Learned in the Homelabs (pain points and solutions)

I am still working on the WireGuard VPN setup with [GL.iNet Brume 2 VPN Servers](https://www.gl-inet.com/products/gl-mt2500/) to link all my varies homelab networks. Those networks now include another physical location with fiber being installed next week. I'm waiting for fiber to be available at the beach house which will change my life. A triangle of linked networks makes for a more interesting configuration and I hope to get those done shortly and write about it.

My home network core switch needs to be updated from a HP ProCurve 2500 (100Mbps)) to a ProCurve 2800 so I have across the board 1Gbps ports to make the core network location a bit better. That location also needs a Wifi 6e upgrade as well and I have the equipment but not the time to update it. The Wifi 6e depends on the 2800 switch upgrade to be effective... so much to do.

I am just throwing [Tailscale](https://tailscale.com/) nodes on all my networks using Dell Wyse 3040 as the base hardware. Getting Tailscale on my laptops and cell phone as a fast way to get remote access has been awesome. I'm removing [TeamViewer](https://www.teamviewer.com) as fast as I can. Their updated policies, intrusive marketing and strange requests for restarts make them less interesting than earlier. Also their clients are getting heavy and goofy.

I also need to configure and add another HP ProCurve 2800 to my SAN (storage area network) backing my Ceph cluster on Proxmox. That will get me a better backplane with the ability to do link aggregation for a wider network for those nodes to exchange data. I've got spare NIC ports to burn to make the Ceph stuff go faster if I get that in there.

All those changes are in-front of getting my media server back up and running. That depends on the Ceph and Proxmox clusters. I think I have those mapped out with LXC for most of the container services and unprivileged rather than full access. Reading the [TRaSH Guide](https://trash-guides.info/) has been an amazing experience. Lots of really good content in there. I need to write a post about all the ARR tools that can be installed on LXC rather than via Docker Containers.

My post on the PiKVM ended up getting shelved when I ran into new issues on the AMOS KVM interacting badly with the PiKVM after it worked well for a week. I thought I had the strange behavior sorted out but it returned and I'm still debugging it. I may bite the bullet and get the $300 KVM that is recommended instead of the cheap one that I have to hack to death.

Those are blocking other fun projects I want to do with Machine Learning. Sadly, I have to sleep and work and cannot finish all these fun projects and posts.