---
title:  "Sun Java SE for Embedded Systems (Jazelle DBX)"
layout: post
categories: personal black_armor hardware nas seagate arm armv5
---

Earlier I mentioned a technology called "Jazelle DBX" for the ARM processor that allows for Java Bytecode eXecution (JBX) directly in the ARM hardware which should make it run faster. That DBX technology is being phased out with newer Thumb-2 instruction set being the new preference by ARM for acceleration.  However, the processor in the BlackArmor NAS was the first processor to have this Jazelle DBX feature and I want to see if it has any merit. I did some digging around, like I mentioned I would, and found that Sun had produced a version of Java that may have this technology.

Sun has two small version of Java.  Once is called Java ME (micro-edition) and the other is Java SE for Embedded. The micro-edition was only for really tightly constrained environments like older cell phones that only had 8MB to 16MB of RAM. It was a feature reduced subset of Java with lots of limitations to make it work in that environment. Remember my old Motorola Razor cellphone from earlier posts and that is where this version of Java lived. That version of Java was crippled and never really seemed to take off.  On the other hand that version of Java is in some of our BlueRay players so it wasn't all bad. We just don't want this version of Java on the BlackArmor as it doesn't give us any interesting things other than cell phone Tetris.

The other version of Java is called "Sun Java SE for Embedded" and lifts many of the limitations of the ME version of Java.  It is a mostly full implementation of Java and allows for most libraries to be used from the reading. The downside is that it requires licensing when being used by a business. Fortunately, development work is free. I pulled a copy of the software as a tarball from Sun and will be taking a look at it when I get an environments setup and some times to play.  It has some requirements that may make is hard to use as it takes a minimum of 32MB of RAM per virtual-machine. Remember that the BlackArmor, only has 128MB total of RAM so that is a quite a lot of memory for just one Java VM.

We'll have to see if this is even feasible but it may open up a huge number of possibilities when you look at the diversity of Java code running out there.

Well that was my fun reading for the evening.  I hope you enjoyed my brain dump or at least found it tolerable. Anyone with experience in the area, please drop comment.
