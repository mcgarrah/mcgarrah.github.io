---
title:  "Backlog of Posts"
layout: post
published: true
---

I've got a backlog of posts I want to do on various topics. A couple of recent posts, I figured getting out something rough was better than not getting it out and just posted soemthing that felt like it needed another draft or two. I'll likely review those quickly posted items and update them as time permits.

<!-- excerpt-end -->

Here is a dump of my unpublished posts that need polishing to release:

* Learning Jekyll
* Site to Site VPN for the Homelabs
* Link Aggregated (LAG) and LACP NIC Bonding
* HP ProCurve Switch Java WebUI (Java JNLP WebStart)
* Dell Wyse 3040 Initial Setup (tailscale endpoints)
* PiKVM v3 and AIMOS 8-port KVM Setup (hacking the webui)
* ProxMox 8 Lessons Learned in the Homelabs (pain points and solutions)

I am still working on the WireGuard VPN setup with [GL.iNet Brume 2 VPN Servers](https://www.gl-inet.com/products/gl-mt2500/) to link all my varies homelab networks. Those networks now include another physical location with fiber being installed next week. I'm waiting for fiber to be available at the beach house which will change my life. A triangle of linked networks makes for a more interesting configuration and I hope to get those done shortly and write about it.

So I have a **core** (capital city), **edge** (second city), and **beach** (beach house) as the three locations. I'll likely add a son and daughter network later. A network setup with three localities stresses the system more than just dual endpoints. You often find issues when you bump up to three that you miss with two.

My home network core switch needs to be updated from a [HP ProCurve 2500 (100Mbps)](https://support.hpe.com/hpesc/public/docDisplay?docId=c01955898&docLocale=en_US) to a [HP ProCurve 2800](https://support.hpe.com/hpesc/public/docDisplay?docId=emr_na-c01814383) so I have across the board 1Gbps ports to make the core network location a bit better. That core location also needs a Wifi 6e upgrade as well and I have the equipment ([Google Nest Wifi Pro 6e](https://store.google.com/product/nest_wifi_pro)) but not the time to update it. The Wifi 6e depends on the 2800 switch upgrade to be effective. I have the Wifi 6e at the beach but not core location and the Wifi 6e is really nice to have.

I am just throwing [Tailscale](https://tailscale.com/) nodes on all my networks using [Dell Wyse 3040](https://www.parkytowers.me.uk/thin/wyse/3040/) as the base hardware. Getting Tailscale on my laptops and cell phone as a fast way to get remote access has been awesome. I'm removing [TeamViewer](https://www.teamviewer.com) as fast as I can. Their updated policies, intrusive marketing and strange requests for restarts make them less interesting than earlier. Also their clients are getting heavy and goofy.

I also need to configure and add another HP ProCurve 2800 to my SAN (storage area network) backing my Ceph cluster on Proxmox. That will get me a better backplane with the ability to do link aggregation for a wider network for those nodes to exchange data. I've got spare NIC ports to burn to make the Ceph stuff go faster if I get that in there. Notice that I have an entire post about LAG/LACP or NIC Bonding that needs a little love and time to finish off along with just a bit of work to get it working.

All those changes are in-front of getting my **media server** back up and running. That depends on the Ceph and Proxmox clusters. I think I have those mapped out with LXC (linux containers) for most of the services and using unprivileged rather than full access. Reading the [TRaSH Guide](https://trash-guides.info/) has been an amazing. There is a lot of really good content in there. I need to write a post about all the ARR tools that can be installed on LXC rather than via Docker Containers or heavy VMs.

My post on the PiKVM ended up getting shelved when I ran into new issues on the AIMOS KVM interacting badly with the PiKVM after it worked well for a week. I thought I had the strange behavior sorted out but it returned and I'm still debugging it. I may bite the bullet and get the $300 KVM that is recommended instead of the cheap one that I have to hack to death. My write up included a section on how to add shortcuts to the PiKVM WebUI which I could probably break out and post for others.

Those are blocking other fun projects I want to do with Machine Learning. Sadly, I have to sleep and work and cannot finish all these fun projects and posts
