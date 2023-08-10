---
title:  "Black Armor Reading on ARM Architecture"
layout: post
categories: personal black_armor hardware nas seagate linux arm armv5
---

So earlier I was digging around trying to find out more about the Black Armor NAS hardware and pulled some interesting information.  Unfortunately, I don't have a lot of ARM background so a good bit of it was confusing as I reviewed it.

Snippet from earlier hardware information gathering:
```
$ uname -a
Linux NAS3 2.6.22.18 #1 Thu Aug 26 12:26:10 CST 2010 v0.0.8 armv5tejl unknown
$ cat /proc/cpuinfo
Processor       : ARM926EJ-S rev 1 (v5l)
```

To rectify my lack of knowledge I started reading on Wikipedia and found the [ARM architecture](http://en.wikipedia.org/wiki/ARM_architecture) which made me realize that I've been missing out on an entirely different ecology of technologic innovation.  The features that are available for each processor was an interesting ride down memory lane with my memory of Intel CPU features, that I'm familiar with, running parallel to the ARM decisions in the same areas. They have two completely different paths but seem to have interchange between the two. ARM has an interesting history as a company as well.




So, I found information on the processor on the Wikipedia page for [List of ARM Cores](http://en.wikipedia.org/wiki/List_of_ARM_microprocessor_cores) and the earlier reading on architecture helped me understand the differences between the Family, Arch and Core. Again, interesting ecology of processor technology.

```
ARM Family:       ARM9E
ARM Architecture: ARMv5TEJ
ARM Core:         ARM926EJ-S
Features:         Thumb, Jazelle DBX, Enhanced DSP instructions
Cache (I/D), MMU: variable, TCMs, MMU
Typical MIPS@MHz: 220 MIPS @ 200 MHz
```

This helps me understand what I will need in a toolchain and setup for that environment.  Earlier earlier I was not even aware that I was missing most of this background information. The ARMv# versus the ARM##XXX were confusing me but now I see the difference.

From the ARMv5TEJ, the "T" is the Thumb instruction set which is a subset of the overall ARM instructions optimized for performance by reducing some features.
```
T: Thumb Instructure Set support
```

So, the "J" in the ARMv5TEJ means we have "Jazelle" support. This feature initially stood out for me as it is direct execution of Java Bytecode against the underlying hardware. This could have be useful if a small Java VM could take advantage of the hardware but it looks like a dead-end since it is a closed implementation. It has also been made less relevant with the Thumb-2 implementation and it depends on the specific implementation if it is real hardware support or not now.  It is interesting to see the "Jazelle" feature was first implemented on this particular CPU.  I'll have to do more reading on it to see if anyone actually got a JVM running with hardware support.
```
J: Jazelle support
```

The "E" means Enhanced DSP support and that may be used for the streaming media or not. TDMI is implied by the E as well which gives us support for:
```
E: Enhanced DSP (digitial signal processing) support
T: Thumb Instructure Set support
D: JTAG debug support
M: Enhanced multiplier support
I: EmbeddedICE support
```

That is interesting in that each of those features can be enabled during compilation of software and might be used to improve performance.
