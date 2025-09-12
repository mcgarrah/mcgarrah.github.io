---
title:  "Google Wifi running OpenWRT"
layout: post
categories: [technical, networking]
tags: [openwrt, networking, hacking, google-wifi, router, firmware]
published: true
---

I have a pile of first generation [**Google Wifi**](https://en.wikipedia.org/wiki/Nest_Wifi#First_generation) units that I'm upgrading from to the latest [Nest Wifi Pro](https://store.google.com/product/nest_wifi_pro) that has WiFi 6e support. I want to reuse the older network devices for a secondary network but want greater control over them.

| ![](/assets/images/google-wifi-gale.png){:width="100%" height="100%" style="display:block; margin-left:auto; margin-right:auto"} | ![](/assets/images/google-wifi-gale.png){:width="100%" height="100%" style="display:block; margin-left:auto; margin-right:auto"} | ![](/assets/images/google-wifi-gale.png){:width="100%" height="100%" style="display:block; margin-left:auto; margin-right:auto"} |

<!-- excerpt-end -->

Enter **Closed Cased Debugging** (CCD) and the [SuzyQ](https://chromium.googlesource.com/chromiumos/third_party/hdctools/+/HEAD/docs/ccd.md#SuzyQ-SuzyQable) cable to gain access to modify these and other older Google devices like Chromebooks that also use ChromeOS. This *magic* cable will let me access the Google Wifi Gale (1st generation) units to put [OpenWRT](https://openwrt.org/) on them. [OpenWRT Google Wifi](https://openwrt.org/toh/google/wifi) has some details and after a lot of searching around I found [ChocolateLoverRaj](https://github.com/ChocolateLoverRaj/gsc-debug-board) who has a USB cable adapter hardware and some debug notes. Finding the SuzyQ was a challenge and I'm really happy to have found someone still making these.

Someplace in my piles of extra hardware, I have a USB C to USB A adapter/converter that I bought as part of my USB docking station setups. I have some extra brightly colored USB C to USB C cables from Ikea to add to the mix.

Something nice about the first generation Google Wifi units is that all of them are router capable unlike later iterations that had one unit that was the router and other units as repeaters only. So every unit is the same hardware and capabilities.

I also looked into [GaleForce](https://github.com/marcosscriven/galeforce) which is a project to customize (hack) the Google Wifi routers to gain root access. This didn't quite look like enough access for some of the things I want to do with it. I'm also doing a lot of OpenWRT work elsewhere so a consistent environment is likely a good thing for my sanity.

All this is predicated on me having the right versions of the Google Wifi hardware but I'm 95% sure I have the USB-C powered hardware that lets me do this. And another project gets added to the pile. So now the waiting begins for the ebay delivery.
