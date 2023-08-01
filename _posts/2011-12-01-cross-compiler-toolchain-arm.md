---
title:  "Cross-compiler toolchain update"
layout: post
categories: personal black_armor hardware nas seagate
---

I've been working on building a toolchain using the notes from OpenHardware [Building the ARM GNU 4.3.2](http://openhardware.net/Embedded_ARM/Toolchain/) with some success. I finally got the base set of GCC 4.3.2 tools to build successfully. I have not used the resulting GCC to produce an ARM executable or verified the executable works on the Black Armor NAS. Those are tests for tomorrow evening when I can get the NAS setup again on the network. It is currently in a box in the corner.

There were several minor things that needed to be updated and modified to get the scripts and environment to work. I've kept careful notes and will post those in the next couple of days once I've tested the output from the compiler works. I'm also attempting to update the versions of the libraries and software to more current versions as well. The GCC 4.3.2 and associated libraries are several years old and I'm trying to get the GCC 4.6.x to build along with newer newlib, binutils and insight/gdb using the same basic set of notes and scripts. I bumped into a zlib issues in the second phase GCC build that stumped me for the night. I'll hit it again tomorrow. Again, I'm keeping careful notes and build docs for the newer version as well.

The dependencies from the operating system are sometimes a pain to track down for the software. I picked a very stripped down install of Ubuntu. The operating system I am using is Ubuntu Server 11.10 because it is easy to install and update. Any Linux would do but the package names may change. Ubuntu Server has no frills so you add everything you need which means all the libraries like GPM, etc.

So there is some progress and in the next couple of days I'll let you know if the build produces working ARM executables. I'm really excited about getting a working "HelloWorld" out there.
