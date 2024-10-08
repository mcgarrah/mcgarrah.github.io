---
title:  "Aggregated Network Connections with LAG/LACP"
layout: post
tags: technical networking lacp
published: true
---

This is a meandering post without an immediate happy outcome.

I am working on a five node ProxMox 8.1 cluster with three nodes as a Ceph cluster to host my media collection. I'm learning a bunch about Ceph and Proxmox which I'll post about later. The media collection I am importing into Ceph is a little over 16Tb from ripping my VHS, DVD, BluRay collections of movies and tv shows. Movies end up being less than a third of that content.

<!-- excerpt-end -->

So the history runs with my wife deciding a long time ago to turn off our cable subscription in favor of buying VHS Tape and DVDs or other media. We raided our local Block Buster when it went out of business. We also kept doing this even into the era of streaming service which had grown to now include content you cannot get on them. On the server side, this journey started with what I thought was an incredibly massive 4Tb USB hard drive hung off a Dell Optiplex 390 SFF (small form factor) desktop running [Plex Media Server](https://www.plex.tv/media-server-downloads). I had a prior set of work with a [DLNA server](https://en.wikipedia.org/wiki/DLNA) hacked into a Seagate BlackArmor NAS that I used as an initial import for the media collection. The new server quickly grew as I kept importing content since it had a DVD drive to do the ripping and a USB device for importing the VHS content. I eventually got concerned about the USB Drives reliablity and wanted to setup a better storage solution. My decision was to use Ceph rather than a NAS which is the use of lots of cheap redundant hardware vs expensive DASD or RAID hardware.

That is all to set the stage and I'll be writing about setting up Proxmox in a later post. Lots of lessons learned and problems along the way.

[![Netgear GS105Ev2](/assets/images/GS105Ev2.png){:width="50%" height="50%"}](/assets/images/GS105Ev2.png){:target="_blank"}

Enter my pile of hardware and a problem to be solved.

I'm frugal and don't buy new equipment so far as I can. My piles of network equipment included lots of unmanaged Netgear 5 and 8 port switches which also happened to include a [Netgear GS105Ev2](https://www.netgear.com/support/product/gs105ev2) which is labeled as a smart managed switch. With this in mind, I thought I could speed up my media import by using [LAG](https://en.wikipedia.org/wiki/Link_aggregation) or [LACP](https://en.wikipedia.org/wiki/Link_aggregation#Link_Aggregation_Control_Protocol) to aggregate a couple of the network ports on my servers [SAN (storage area network)](https://en.wikipedia.org/wiki/Storage_area_network) for faster movement of data between the storage nodes. I already had a separate 1Gbps switch and separate network setup for Ceph. That was an entire lesson in itself that Ceph will not work well without a separate network. This would let me take a couple of 1Gbps ports and get them closer to 2Gbps was the theory. Ceph folks are going to yell that you need 10Gbps network for Ceph to run well. I won't argue that 10Gbps would not be nice but adding 10Gbps network won't happen until prices come down further.

Here enters the marketing ***crap*** from Netgear to botch that idea. Netgear searches will mention LAG and LACP being available on their Smart or Pro switches and it is even in their user manuals. However, those miss letting you know that feature is only enabled on 24 or 48 port switches. The five (5) or eight (8) port versions do not have LAG enabled and their marketing materials don't make that very clear. It is also a closed system without SNMP support to pull metrics. The features it is missing just keep piling on. Netgear isn't my first choice for managed switches but I was trying to use what I had which was a this little ***goober*** that isn't good enough to be a managed switch or crappy enough to be a dumb switch. They fit a zone of stupid devices that make no sense. I'm not sure why I had it in my pile of equipment but likey somebody else learned this lesson as well and I got it handed over for free.

[![HP ProCurve 2810-24](/assets/images/hp-procurve-2810-24.jpg){:width="50%" height="50%"}](/assets/images/hp-procurve-2810-24.jpg){:target="_blank"}

Thus enters the combo of eBay and my prior experience with [HP ProCurve](https://en.wikipedia.org/wiki/ProCurve) 2500 switches. I use a ProCurve 2510 as the main work horse switch in my home network even with the majority of the ports being 100Mbps. After digging around I found that the [HP ProCurve 2800 and 2900](https://en.wikipedia.org/wiki/List_of_ProCurve_products#Mainstream) series switches are in a very reasonable price range for less than $25 USD each. Those switches are 1Gbps ethernet for every port and four SPF (not SFP+) if I want to run cheap 1Gbps SFP DAC (Direct Attach Copper) cables. But better yet, these are real enterprise switches with SNMP, VLAN, LACP and all the other high-end network features. What they lack is a nice web interface to manage them since their Java WebUI is deprecated. So you are on the serial console command line banging out changes and saving the configurations initially. As a prior network engineer who had to do this stuff for other folks, this does not phase me. I'm just frustrated at the wasted time on that Netgear device.

So here I sit waiting on my eBay order to arrive so I can test out LAG and/or LACP port aggregation on my ProxMox cluster. I'll probably upgrade my existing HP ProCurve 2510-24 while I'm getting this added to the mix. The VLAN support is excellent and I could use it in my home network. I'll do a follow up on setting up the HP ProCurve 2800s and how it goes for speeding up my media collection import and any issues I hit along they way.
