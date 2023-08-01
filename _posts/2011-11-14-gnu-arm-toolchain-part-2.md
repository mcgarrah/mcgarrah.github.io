---
title:  "Building the GNU ARM Toolchain: Part 2"
layout: post
categories: personal black_armor hardware nas seagate arm armv5 toolchain
---

Lesson learned on doing a toolchain build or anything else for that matter; make sure you are reading the most current documentation available.  I was working with very old versions of the software by using the GNU ARM website mentioned earlier.  In digging into the problems for those builds, I found a few other sites that have detailed discussions on building the toolchain for specific version of the ARM platform.

One of interest is the OpenHardware [Building the ARM GNU 4.3.2](http://openhardware.net/Embedded_ARM/Toolchain/) that has lots of useful hints.  Also, the [Installing Gnuarm ARM Toolchain on Ubuntu 9.04](http://blog.nutaksas.com/2009/05/installing-gnuarm-arm-toolchain-on.html) had some useful notes as well.  Both are very different approaches and for very different ARM platforms but they have lots of useful notes on how to create a toolchain.  I'll probably use something in the middle between the two to get the job done.

So I lost some time with old versions but learned a good bit about the software in the process.

The tools for the toolchain are:
* binutil: low level tools for manipulating object code such as the assembler and linker tools
* gcc: GNU compilers which has C/C++ and other tools related to compilation of code to object code
* gdb & insight: debugger allowing for finding problems in code
* newlib: a standard C library for embedded systems

Each tool builds forward until you have a complete toolchain that allows for creating programs for the platform. We are doing something even more interesting called cross-platform compilations. Since I don't have an ARM platform that I want to build a C compiler on and all the other tools, I am building those tools on my Intel Laptop under Ubuntu 10 LTS.  This means my Intel x86_32 processor will be running a compiler that will output an ARM executable. So the compiler is built to run on x86 but produce ARM.  This is cross platform compilation and is very typical for embedded systems work.

The problem I'm encountering is that I don't want to just use an existing binary build of the toolchain but produce one myself.  The age of the toolchain provided by Seagate is such that even if I wanted to find those versions of the software, I'm unlikely to find them and get them working.  So I'm looking for build a newer version of the compiler and see if the software will run afterwards.

My first program produced will likely be just a simple HelloWord app but from small things come larger ones.  Building OpenSSH, rsync and other tools will follow quickly if I get the toolchain up and running.
