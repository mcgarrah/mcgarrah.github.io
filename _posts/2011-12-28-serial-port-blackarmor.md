---
title:  "Serial Port on BlackArmor NAS"
layout: post
categories: personal black_armor hardware nas seagate
---

I found my old Samsung x426 USB cell phone programmer cable as I was cleaning out my home office. I might have mentioned this cable earlier when I wrote about adding a serial console to the BlackArmor NAS.  The cable is a really old style one that has a weird connector for the cell phone way before the mini-USB became standard. The interesting thing about this cable is that it has a serial to USB converter chip (2303HXC 0546) that does the magic of converting serial to USB. That is why that thing was ridiculously expensive ($35) when I bought it back in the day.

Why this is even on my radar as possible is that the website [CrapNAS](http://crapnas.blogspot.com/) had an entry for how to connect a serial or USB cable so you can watch the Linux boot up as a serial console session. They specify two different ways to do this. For the serial connection, they specify a MAX3232 as necessary.  The USB connection has a schematic that includes a 2303HX. I'm not sure what the difference is between that and my 2303HXC so I will be doing some reading before I cut into the cable and get out the soldering iron.

Why am I even messing around with a serial console?  Because as I am planning to mess around with the lower level system, I should have a back out plan if I do something wrong. A serial console on the device gives me more options during the boot up even if I cannot connect via a network connection.

As far as getting time to work on the compiler toolchain, I've been relaxing over the holiday break with family, cleaning my messy home office and have not even booted up the virtual machine since my last post. I intend to get back to it someday.
