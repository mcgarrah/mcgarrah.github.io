---
title:  "Black Armor NAS Information"
layout: post
categories: personal black_armor hardware nas seagate
---

Here is the beginning of a dump of information on the Black Armor device from the Linux kernel and environment.  From this I learned the processor type and features. I also got some pointers to cross-compiler options used. These will all be important later.

<!-- excerpt-end -->

``` shell
$ uname -a
Linux NAS3 2.6.22.18 #1 Thu Aug 26 12:26:10 CST 2010 v0.0.8 armv5tejl unknown
$ cat /proc/cpuinfo
Processor       : ARM926EJ-S rev 1 (v5l)
BogoMIPS        : 794.62
Features        : swp half thumb fastmult edsp
CPU implementer : 0x56
CPU architecture: 5TE
CPU variant     : 0x2
CPU part        : 0x131
CPU revision    : 1
Cache type      : write-back
Cache clean     : cp15 c7 ops
Cache lockdown  : format C
Cache format    : Harvard
I size          : 16384
I assoc         : 4
I line length   : 32
I sets          : 128
D size          : 16384
D assoc         : 4
D line length   : 32
D sets          : 128

Hardware        : Feroceon-KW
Revision        : 0000
Serial          : 0000000000000000
$ cat kmsg
<5>Linux version 2.6.22.18 (root@jasonDev.localdomain) (gcc version 4.2.1) #1 Thu Aug 26 12:26:10 CST 2010 v0.0.8
<4>CPU: ARM926EJ-S [56251311] revision 1 (ARMv5TE), cr=00053977
<4>Machine: Feroceon-KW
<4>  Marvell Development Board (LSP Version KW_LSP_4.2.7_patch21_with_rx_desc_tuned)-- MONO  Soc: 88F6192 A1 LE
$ dmesg
... way too much stuff ...
```
