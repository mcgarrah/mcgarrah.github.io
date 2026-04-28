---
title:  "Seagate Black Armor 110 NAS"
layout: post
categories: [hardware, technical]
tags: [seagate, black-armor, nas, linux, embedded, hacking, arm]
published: true
last_modified_at: 2026-04-28
---

I found something fun.

The Seagate NAS (Network Attached Storage) that I've been using at my house is running an embedded Linux. A NAS is a big network hard drive you can share between computers.  I got a root account on it and have found a whole world of fun that could be done in there.  Root is the master administrative account for UNIX systems that let you do extra things beyond the normal.

First steps is getting a functional toolchain and then build some trivial tools.  The goal would be to have a full set of GNU tools available in a package format for people to use.  I want to publish a full working OpenSSH with scp support and rsync for this thing as a starting point. Maybe add some features for NFS. Just digging around on this thing reminded me how much I enjoy hacking on hardware.

<!-- excerpt-end -->

A starting point is this gentleman who cracked open the hardware:

* [https://crapnas.blogspot.com/](https://crapnas.blogspot.com/)

The Seagate Support Forums are surprisingly useful:

* [Seagate BlackArmor NAS Forums](https://web.archive.org/web/2024/http://forums.seagate.com/t5/BlackArmor-NAS-Network-Storage/bd-p/BlackArmorNAS) *(archived — Seagate forums shut down)*

Hajo Noerenberg's work gives us root access and details on image format:

* [https://www.noerenberg.de/hajo/pub/seagate-blackarmor-nas.txt](https://www.noerenberg.de/hajo/pub/seagate-blackarmor-nas.txt)
* [https://www.noerenberg.de/hajo/pub/](https://www.noerenberg.de/hajo/pub/)

Debian Lenny installed on 220 NAS:

* [Debian Lenny on BlackArmor 220 NAS](https://web.archive.org/web/2024/http://forums.seagate.com/t5/BlackArmor-NAS-Network-Storage/Install-Debian-GNU-Linux-5-0-7-Lenny-on-the-Blackarmor-220-NAS/td-p/79422) *(archived — Seagate forums shut down)*

I don't think I want a full Linux install but just extend the existing environment with additional tools that are useful.  A full platform and OS would be too much hassle. Besides, someone else already has that glory.

I'll post more if I get time to wack on this.
