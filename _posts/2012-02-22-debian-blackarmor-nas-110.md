---
title:  "Debian on BA NAS 110"
layout: post
categories: [technical, hardware]
tags: [seagate, black-armor, nas, debian, linux, arm, installation]
published: true
---

Hajo on the BlackArmor Forums has an older posting about getting [Debian Linux 5.0 (Lenny) installed on BA NAS 110/220/4x0](http://forums.seagate.com/t5/BlackArmor-NAS-Network-Storage/Install-Debian-GNU-Linux-5-0-7-Lenny-on-the-Blackarmor-220-NAS/td-p/79422). This is not a port that includes the kernel but simply a minimum install that gets the system setup to install binaries out of the Lenny EABI ARM platform.  The kernel that comes with the BA NAS is compatible with those binaries.  The newer kernel for the Debian 6 or higher is not compatible with the BA NAS. This has some limitations but offers a way to get to some newer software pre-compiled.  I don't want to loose the existing functionality on my test system but the draw to DLNA services is pretty strong right now.

To top it off, Debian has a nicely setup [cross-compilation setup](http://wiki.debian.org/BuildingCrossCompilers) documented for people working on non-Intel platforms.  This offers a way to compile newer software without killing myself anymore on building the entire compiler and supporting software myself.

The goal has always been to make the NAS device useful and I want to play my movies off it to my TV upstairs so this might be the next thing I play with on the development NAS.
