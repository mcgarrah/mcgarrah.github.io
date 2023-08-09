---
title:  "Building the GNU ARM Toolchain: Part 1"
layout: post
categories: personal black_armor hardware nas seagate arm armv5 toolchain
---

I found the [GNU ARM Toolchain](http://www.gnuarm.com/) website awhile back and that they have several different versions out there for the toolchain. A toolchain is just the basic tools needed to build software.  In this case it is the standard libraries, the compiler, debugger and various other tools needed to write software.  The version of the toolchain that is provided by Seagate is version 3.0 and a very old version.  The oldest on the ARM website is 3.3 with 4.1 being the newest.




I've pulled down the 3.4, 4.0, and 4.1.  The 4.1 does not compile on my which is Ubuntu 10 LTS and may have to do with x86 versus x86_64 differences.  I'm not sure enough to diagnose yet so I dropped back a version to 4.0 and will check again.  The error in the 4.1 build was in the assembly code opcode section so that isn't an area I want to try debugging at this point.  The version 4.0 of the toolchain software is building cleanly for the initial libraries then failed in the GCC compiler. Sometime it pays to drop back a version to avoid bleeding edge pain and sometime you just find new pain.

Status:
So for 4.1: we have opcode errors in binutil which is very early in the build process and the errors look nasty.

For 4.0, we have an error in GCC "fcntl2.h:51: error: call to â__open_missing_modeâ declared with attribute error: open with O_CREAT" which looks like an error encountered before from some quick google searches. Not spent enough time yet to consider this a loss.

Building the toolchain makes it easier to understand the toolchain provided by Seagate even if it is an older version. Once I get done, I'll write up some details on a the process when I get it working right.


We'll see what happens with building the toolchains over the next day or so.
