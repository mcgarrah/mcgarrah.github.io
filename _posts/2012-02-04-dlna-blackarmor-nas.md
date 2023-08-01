---
title:  "DLNA server for BlackArmor NAS"
layout: post
categories: personal black_armor hardware nas seagate
---

Today I was reading a couple of forums and bumped into a write up on the "[BubbleUPnP](http://forum.xda-developers.com/showthread.php?t=1118891) - UPnP/DLNA Control Point and Renderer" application for Android that has both DLNA client and server support. The BubbleUPnP setup also has a Java based server mentioned in their section on [NAS devices](http://bubbleguuum.free.fr/upnpserver/), such as the QNAP which is very similar to the BlackArmor NAS.

[Earlier](/2011-11-08-sun-java-se-embedded) in my writing, I was reviewing a version of Java for the ARM that was called "[Sun Java SE for Embedded](http://www.oracle.com/technetwork/java/embedded/downloads/javase/index.html)".  It would allow for executing a Java application on the BlackArmor.  Up until now, I did not have a Java application to really motivate me to install and test this but the BubbleUPnP DLNA server might allow for my BlueRay Play, Roku and Android cell phone to play my movies directly off the BlackArmor NAS.

There is one problem which is getting the ffmpeg library compiled and running. This is described in the docs above for the QNAP NAS but I've not been successful at getting a working toolchain yet.  I may have to backtrack and see if I can just use the toolchain provided by Seagate to compile this newer version of ffmpeg.

Another issue is that the Java SE for Embedded is licensed strangely by Oracle. It cannot be redistributed and requires licensing costs if it is redistributed by a professional package.

So step one would be to compile the ffmpeg library and test it out.  I hope to try that out with the existing Seagate toolchain.  The next step would be to get the Java SE Embedded to run a basic HelloWorld application on the console.  After that, try to get the BubbleUPnP server running.

I'll see if I can get a couple hours together to work on this this coming week. It would be nicer to have an open source DLNA server but I'll take what I can get.  Since I'm talking about taking some time to compile C/C++ code anyway to get this working, I checked on open source DLNA servers and popped up something from [eLinux](http://elinux.org/DLNA_Open_Source_Projects) that was interesting to read over.  It looks like [MediaTomb](http://mediatomb.cc/), [uShare](http://ushare.geexbox.org/), and [Serviio](http://www.serviio.org/) are candidates that could replace the BubbleUPnP server if I get the compiler toolchain working.

We will just have to see how much time I can get together to play around with this.
