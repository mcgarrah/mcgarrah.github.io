---
title:  "Thinkpad T480 WWAN SSD"
layout: post
published: true
---

# Adding another SSD Drive

In my etermal tinkering with my [Lenovo Thinkpad T480s](https://en.wikipedia.org/wiki/ThinkPad_T_series#T480), I have continued the trend of adding new features. So earlier, in [A new to me but old laptop](/new-but-old-laptop/) and [New Laptop update](/new-laptop-update/), I threw out a bunch of enhancement options. Some of those I've done and some I left on the backlog as things that just cost too much on my metric of usefulness per dollar. The WWAN SSD for extra storage was one of those that just seemed like a bad bang-for-the-buck for storage. I also like the option to add a SIM card and have cellular network available in case I have to go back to consulting on the road.

<!-- excerpt-end -->

So I found a way I thought to get the price to value down quite a bit. Or at least expand the options for the SSD drives to expand cost options. I also hit some frustration when downloading LLM Models and filling up large portions of my boot drive with those. My goal was to separate those and other models onto a data volume. Using the large SD Card Slot with a 500Gb or 1Tb SD card works but seemed slow.

So the WWAN M.2 slot on the T480 is a 2242 (42mm) B+M keyed PCIe slot. This means you need two notches in the right place on your card being inserted and it has to be 42mm long. Some folks have done crazy stuff like use hacksaws to cut out pieces of M keyed M.2 drives and/or solder wires across the traces for power. I am no where that adventureous or crazy.

Here is a picture of the M vs B+M keyed edges to get an idea of what I am talking about.

[![M.2 M key versus B+M key](/assets/images/thinkpad-t480-wwan-ssd-m2-slot.png){:width="30%" height="30%"}](/assets/images/thinkpad-t480-wwan-ssd-m2-slot.png){:target="_blank"}

There is a relatively cheap converter to take a M to a B+M key that only adds one unit length, about 12mm, to the length of the disk. So I bought a [2230mm 1Tb SSD](https://amzn.to/3xnGpDt) that was at my price point and added $10 for the [M to B+M key converter](https://amzn.to/3U8C1kF).

Sadly, after reviewing current prices and writing this up, I could have picked up a B+M keyed drive very close to the same price now.  But when I purchased, there were not many B+M keyed disks for less than $100 USD on Amazon. So the world has moved on and prices have come down since I bought this.  So buy beware and YMMV (your mileage my vary) when doing this.

Here is what I ended up installing into my Thinkpad WWAN slot and it worked on the first try.

[![M.2 M key to B+M key converter](/assets/images/thinkpad-t480-m2-m-to-bm.png){:width="30%" height="30%"}](/assets/images/thinkpad-t480-m2-m-to-bm.png){:target="_blank"}

| Price | Description / Link |
| -----:| ------- |
| $10 | [M.2 2230 to 2242 Extension Adapter,NGFF B+M Key NVME M-Key 2230 to 2242 Extension Adapter](https://amzn.to/3U8C1kF) |
| $70 | [TEAMGROUP MP44S High Performance SSD 1TB SLC Cache Gen 4x4 M.2 2230 PCIe 4.0 NVMe, Compatible with Steam Deck, ASUS ROG Ally, Mini PCs (R/W Speed up to 5,000/3,500MB/s) TM5FF3001T0C101](https://amzn.to/3xnGpDt) |
| **$80** | **Total** |

This is a larger picture what makes this whole thing work.

[![M.2 SSD and Converter](/assets/images/thinkpad-t480-wwan-ssd-and-converter.png){:width="30%" height="30%"}](/assets/images/thinkpad-t480-wwan-ssd-and-converter.png){:target="_blank"}

I have not tried booting from it and no major performance testing but it seems to work for what I needed. I wanted separate larger data volume for my LLM models separate from by OS and boot drive. I may at somepoint upgrade to a 2Tb or later drive at some later date but this is making my world better as it is right now.

# Appendix A: Pricing (April 2024)

## NVMe 2230 SSD + 12mm M to B+M key converter

| Price | Size | Description / Link |
| -----:| ---- | ------- |
| $70 | 1Tb | **[TEAMGROUP MP44S High Performance SSD 1TB SLC Cache Gen 4x4 M.2 2230 PCIe 4.0 NVMe, Compatible with Steam Deck, ASUS ROG Ally, Mini PCs (R/W Speed up to 5,000/3,500MB/s) TM5FF3001T0C101](https://amzn.to/3xnGpDt)** |
| $90 | 1Tb | [INLAND TN436 1TB M.2 2230 SSD PCIe Gen 4.0x4 NVMe Internal Solid State Drive, 3D TLC NAND Gaming Internal SSD, Compatible with Steam Deck ROG Ally Mini PCs](https://amzn.to/3vNkhBK) |
| $92 | 1Tb | [Addlink S91 1TB 2230 NVMe High Performance PCIe Gen4x4 2230 3D NAND SSD - Read Speed up to 4900 MB/s Compatible with Steam Deck, ROG Ally, Laptop, Internal Solid State Drive - (ad1TBS91M2P)](https://amzn.to/3PN1L3p) |
| $100 | 1Tb | [SABRENT Rocket 2230 NVMe 4.0 1TB High Performance PCIe 4.0 M.2 2230 SSD [SB-2130-1TB]](https://amzn.to/3U7vvdY) |
| | |
| $150 | 2Tb | [TEAMGROUP MP44S High Performance SSD 2TB SLC Cache Gen 4x4 M.2 2230 PCIe 4.0 NVMe, Compatible with Steam Deck, ASUS ROG Ally, Mini PCs (R/W Speed up to 5,000/3,500MB/s) TM5FF3002T0C101](https://amzn.to/3J8Vknw) |
| $160 | 2Tb | [INLAND QN446 2TB M.2 2230 SSD PCIe Gen 4.0x4 NVMe Internal Solid State Drive Gaming Internal SSD, Compatible with Steam Deck, ROG Ally Mini PCs](https://amzn.to/3PQAnBq) |
| $165 | 2Tb | [Addlink New S91 2TB 2230 NVMe High Performance PCIe Gen4x4 2230 3D NAND SSD - Read Speed up to 5000 MB/s Compatible with Steam Deck, ROG Ally, Laptop, Internal Solid State Drive - (ad2TBS91M2P)](https://amzn.to/3U6DBU8) |
| $219 | 2Tb | [SABRENT Rocket Q4 2230 NVMe 4.0 2TB High Performance PCIe 4.0 M.2 2230 SSD Compatible with Steam Deck, ASUS ROG Ally, Mini PCs [SB-213Q-2TB]](https://amzn.to/3U7vs1M) |
| | |
| $190 | 2Tb | [2TB M.2 2230 SSD, NVMe 1.4 PCIe Gen4 x4 Up to 5,200/4,000 MB/s(R&W) Internal Solid State Drive for Steam Deck, ROG Ally, Surface, Laptop, Desktop](https://amzn.to/3J5vHnF) |
| $215 | 2Tb | [WD_BLACK 2TB SN770M M.2 2230 NVMe SSD for Handheld Gaming Devices, Speeds up to 5,150MB/s, TLC 3D NAND, Great for Steam Deck and Microsoft Surface - WDBDNH0020BBK-WRSN](https://amzn.to/49pByyI) |

## NVMe 2242 SSD B+M key

| Price | Size | Description / Link |
| -----:| ---- | ------- |
| $80 | 1Tb | [1TB M.2 SATA SSD 2242 NGFF B&M Key Internal Solid State Drive 6Gb/s for Desktop Laptop PC](https://amzn.to/443PnlD) |
| $82 | 1Tb | [KingSpec M.2 SATA SSD, 1TB 2242 SATA III 6Gbps Internal M.2 SSD, Ultra-Slim NGFF State Drive for Desktop/Laptop/Notebook (2242, 1TB)](https://amzn.to/3U5OaWn) |
| $90 | 1Tb | [SHARKSPEED SSD 1TB M.2 2242 NGFF SATA 3 42mm 6Gb/s 3D NAND Internal Solid State Drive for Desktop Laptop PC (M.2 2242, 1TB)](https://amzn.to/3vNnXU4) |
| | |
| $140 | 2Tb | [2TB M.2 SATA SSD 2242 NGFF B&M Key Internal Solid State Drive 6Gb/s for Desktop Laptop PC](https://amzn.to/43LAvbi) |
| $150 | 2Tb | [KingSpec M.2 SATA SSD, 2TB 2242 SATA III 6Gbps Internal M.2 SSD, Ultra-Slim NGFF State Drive for Desktop/Laptop/Notebook (2242, 2TB)](https://amzn.to/49tsWai) |
| $210 | 2Tb | [SHARKSPEED SSD 2TB M.2 2242 NGFF SATA 3 42mm 6Gb/s 3D NAND Internal Solid State Drive for Desktop Laptop PC (M.2 2242, 2TB)](https://amzn.to/43PeuIC) |
