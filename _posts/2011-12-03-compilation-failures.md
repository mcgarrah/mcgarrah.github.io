---
title:  "Compilation failures"
layout: post
categories: personal black_armor hardware nas seagate
---

The problem is that I can get an ARM executable but not sure why the default system is not working to produce a basic HelloWorld.

<!-- excerpt-end -->

``` shell
$ cat test.c
int main (){return 0;}
$ arm-elf-gcc test.c -o test
...
/home/mcgarrah/DevelToolbin/binaries/arm-4.4.6/bin/../lib/gcc/arm-elf/4.4.6/../../../../arm-elf/lib/libc.a(lib_a-exit.o): In function `exit':
exit.c:(.text+0x54): undefined reference to `_exit'
collect2: ld returned 1 exit status

$ arm-elf-gcc test.c -o test -v
```

This spews a couple of pages of additional output which points me to something called the "Using built-in specs" and lots of directory path information for various things like include files and libraries. These all look about right. A directory /DevelToolbin/binaries/arm-4.4.6/arm-elf/lib has some interesting lib files in it.

``` shell
$ arm-elf-gcc test.c -o test ~/DevelToolbin/binaries/arm-4.4.6/arm-elf/lib/redboot-syscalls.o
$ file test
test: ELF 32-bit LSB executable, ARM, version 1, statically linked, not stripped
```

When you are facing a missing library like the above issue, you typically just have to find the right library and add it to your build.  In this case we are missing something so fundamental that we need to figure out why it is broken or will hit future issues.

While finding the above syscall libraries, I noticed some files called specs files which are:

* linux.specs
* rdimon.specs
* rdpmon.specs
* redboot.specs

RDP, RDI, RedBoot and Linux are all syscall (system call) protocols. A syscall protocol describes how a libc (standard C library) communicates with the operating system kernel. For our case this library is newlib which uses another syscall protocol called libgloss as an interface between libc and the above syscall protocols.  I'm not sure which protocols are the default but something is not right about this combination.

```shell
$ arm-elf-gcc -dumpspecs
```

This dumps even more output that is even more cryptic but looks important when taken with the above information. There are built-in defaults for GCC that are being overridden by these specs files.

There is an options to change the specs entries from the GCC command line which I use to identify what is happening.

```shell
$ arm-elf-gcc test.c -o test -specs=redboot.specs
$ arm-elf-gcc test.c -o test -specs=pid.specs
$ arm-elf-gcc test.c -o test -specs=linux.specs
```

The pids and redboot files are a very minor difference in a setting so are essentially the same.  Linux is significantly different as a system call interface.

```shell
$ arm-elf-gcc test.c -o test -specs=rdimon.specs
$ arm-elf-gcc test.c -o test -specs=rdpmon.specs
```

Both the RDI and RDP return basically the same error as the above missing library.  So we have identified what is probably the default libraries used by libgloss.

This is just a journey down the rabbit hole. So I need to revisit the newlib build process and see what I did wrong in it.

Update December 4th, 2011 7:30pm: What you see above happens in both the gcc 4.4.6 and gcc 4.3.2 compiled software sets. Same exact problem for both versions of gcc and associated other libraries. I did a full rebuild of the 4.3.2 and did some tracing of the path built into gcc and re-verified paths to all libraries. Same issue still happens. So we have a genuine problem in the build process that is impacting the compiler.  Could be in any place across the binutils, newlib or gcc compilations. So I'll be digging into each. The nice part is it looks like a common problem so if I fix it in the 4.3.2 series then it will probably fix in the 4.4.6 series as well.
