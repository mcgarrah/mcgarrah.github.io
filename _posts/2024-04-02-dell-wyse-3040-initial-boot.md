---
title:  "Dell Wyse 3040 Initial Setup"
layout: post
published: false
---

The Dell Wyse 3040 is a nifty little machine that is extremely small and a low power consumer. They are however not without issues. This is my foray into trying to get a couple of them working on my network. I've had these for about XXX months in a drawer waiting for a use.

<!-- excerpt-end -->

(TODO: Pull images from cell phone from 2024-04-02 in the afternoon ... lots of pictures to show the progress)

First was to find a a working DVI to DP converter for my old Dell 14" LCD monitor. There is something about active and passive DisplayPort adapters which I was not aware. The impact was the DisplayPort to DVI auto-detect on my older Dell LCD monitor failed horribly. I had to set it to the Digital (DVI) output or it would go blank and power down. Occasionally, I had to unplug and plug it back in until I got signal again. This was frustrating at first because the behavior was like these little boxes were dying right after bootup. Turning off the monitor and back on again, showed me the same BIOS screen so I could see the units were not rebooting but something wrong with the monitor or display output.

Finally got into BIOS...

(screen of the options for F1/F2/F5 and F12)

F12 is missing but I know Dell well enough to know that is the boot option that pulls you into a list to get to the other features.

BIOS settings are nice to see I've got 2GB RAM and a 4-core Atom processor.

(BIOS General Info)

Also the boot options are not working as I do not have my Ventoy USB in there... yet.

Run the full diagnostics to stress test the system a bit. I bought these on eBay awhile back and never got a chance to work on them.
I also have a second one of the 3040s and two more VDI machines that are even older than these 2018/2019 units.

These type of older VDI (virtual desktop interface) machines with linux are nice low power options for hosting a bastion or jumphost into my networks. They can also serve as network routers for Tailscale. Not sure if I need a second NIC on USB to make that happen or not.

The Youtuber Apalrd has a video on getting these booted up nicely. He also has the USB soldering hack for power.

BIOS is 1.2.3 and 1.2.5 is out in 2018. Not sure if the newer BIOS is a good idea as the UEFI stuff can lock you out of legacy boot according to some folks working on these.

I'm guessing I'll want to load Debian on this box... trying debian 12.x.5 with all defaults for a bootup and install. I've got no OS on this box so nothing to loose here.

Skipped network setup as I don't have a cable pulled upstairs yet.

Regular root and user account setup...

Made some choices on LVM and using all the MMC storage... it's only 8GB with 6.8GB avaiable so going to use it all. Also did a single root volume without breaking up the partitions. Old UNIX Admin me is shuddering at not breaking those up.

Depending on how much fun the install is versus reinstalling to get DHCP network setup... I am hoping that Debian 12 is kind to me when I have to configure networking from the command line. These boxes can run GUI but I'm going to reserve the memory and disk space for other purposes and leave those off the installs.

Apalrd mentioned in his video an issue with Debian booting up in UEFI mode and needing to add some boot parameters. Maybe Debian 12 fixes this issue...

* Reboot failed to load debian...  return to rescue mode boot up and pick the "advanced" and "uefi fix" then reboot
  * "Force GRUB installation to the EFI removale media path" is needed in rescue mode still
* Reboot still had issues due to CMOS battery being crap
* Reboot further had issues due to bad power down... fix with modprobe blacklist of dw_dmac_core module

CMOS battery are $10 a pop which I'm too cheap to buy... so I'll solder new $0.20 CR2032 batteries on the existing cable and connector pulled from the units when I'm back at my other workbench.

TODO: Search for Debian install on wyse3040 and cut/paste the blacklist.conf and init..

That change made the reboot and shutdown work which was exceptionally frustrating with the bad CMOS batteries forcing entering date/time on every reboot.

Need add intel audio driver when I add it to the network. I left that off the list as I really don't need the feature right now.

(picture of disk DF)

We are tight on disk space but not terrible. The 8GB MMC storage is workable if I don't go crazy on packages and keep an eye on log rotation (logrotate.d).

The Atom CPU has virtual machine capabilities but with RAM at 2Gb, it is really limited. There is no easy upgrade option for RAM without seriously skilled soldering. They are soldered to the board along with the MMC storage.

Running thru my second Dell Wyse 3040 installation...
Both are on BIOS 1.2.3, same 8GB MMC, same 2GB RAM, no wifi card, both with cmos batteries exhausted,

Booted into Ventoy at 4:30pm... and done in about 20 minutes.

Streamlined the process by using the rescue environment with a shell in root to add the blacklist.conf and run update-initramfs to fix the power issue. did that at same time as the UEFI issue being fix.

Need to read up how that EFI fix matters during upgrades of Debian.  do I need to do it again later.

I now have two Dell Wyse 3040 hockey puck computers that are on-par with a Raspberry Pi 4.
