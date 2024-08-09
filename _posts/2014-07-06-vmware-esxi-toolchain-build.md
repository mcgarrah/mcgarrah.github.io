---
title:  "VMware ESXi toolchain build"
layout: post
categories: technical
---

I’ve been back to the toolchain for ESXi again and had some success.

I was really getting frustrated with my lack of success in building the VMware ESXi 5.5 toolchain and compilers. It was a multi-week effort and I’m usually able to get something like that working eventually. I took a couple of month break from it while I worked on some other things including this website(WordPress) and my email servers. This gave me some perspective.

<!-- excerpt-end -->

The real frustration was that the ESXi 5.0 version that everyone else was writing about seemed like it was easy to get done. I never tried it so didn’t have a gauge on how easy or hard it would be. Now I’ve tried the 5.0 OSS download and it is simple in comparison. In the 5.0 version they provide binary toolchain files to jump start the build. These are not provided in the 5.5 series. So you have a larger footprint to dig through before you even get started. Toolchains builds are never easy in my experience. There is always something to figure out. The 5.5 build included some dependencies on several environments all the way back to Redhat 7.3. This was not simple to setup quickly.

So I’ve now got a ESXi 5.0 series toolchain and compiler setup in a virtual machine ready to use. I’m building the pieces I need for my original project to build a sample application to be followed by UPS management software.

My 5.5 series toolchain is going to get some additional work as I get some time. This looks like a more comprehensive build with additional features available so I’ll definitely want to get this working.

And I’ve now discovered that I can get the ESXi 5.1 OSS as a CD/DVD from EMC/VMware if I request it. I’m probably going to do that at some point soon so I have a copy floating around.

Ideas on how to share a pre-built development environment are next on my list of things to do. It would have been nice to have had an easy starting point for my original work which was to build the APCupsd software natively in ESXi.

The APCupsd software will allow for managing my current UPS hardware I hope. Currently, the only sane option is to install the software into a virtual machine and do USB pass-through to the hardware to manage them. This just seems kludgy to me. I want the software to be loaded in the base operating system of the server not a virtual machine hosted above it.
