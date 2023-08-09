---
title:  "Toolchains compiled"
layout: post
categories: personal black_armor hardware nas seagate
---

Two full toolchains built and a third that I still think might be made to work.  The first is using older versions of everything and was mostly done as a test to get the build environment working against known sources that are known to build. Even this known build process required some effort to get working in a current OS environment. Those docs, notes and scripts will be coming in the near future.




So to outline what works and not, I give you the following.

Toolchain that comes from older versions of software and the docs from [Tom Walsh](http://openhardware.net/Embedded_ARM/Toolchain/):
* binutils-2.19.1a.tar.bz2
* gcc-4.3.2.tar.bz2 (with a patch from Tom)
* newlib-1.16.0.tar.gz (with a patch from Tom)
* insight-weekly-CVS-7.0.50-20091130.tar.bz2

Newest versions that compiled based on Tom's scripts:
* binutils-2.22.tar.bz2
* gcc-4.4.6.tar.bz2
* newlib-1.19.0.tar.gz
* insight-CVS-20111130.tar.bz2 (pulled from CVS head and required patching by me)

Newest versions that fails to compile in GCC in zlib:
* binutils-2.22.tar.bz2
* gcc-4.6.2.tar.bz2
* newlib-1.19.0.tar.gz
* insight-CVS-20111130.tar.bz2 (pulled from CVS head and required patching by me)

The issue in GCC is well documented (if you know what you are looking for) as a bug in the ```"--enabled-multilib"``` during the build. The [zlib](http://en.wikipedia.org/wiki/Zlib) library that is packaged with the GCC source fails to build in a cross-compiled configuration. Who knew that GCC packages their own copy of zlib in the GCC sources? There appear to be a couple of solutions which might fix the problem. The first is to just use the native zlib from the host system and pass in ```"--with-system-zlib"``` but that feels like a hack instead of a fix. The other is to revert a change in GCC that is documented in a couple of places ([Bug45174](http://gcc.gnu.org/bugzilla/show_bug.cgi?id=45174) and [Bug43328](http://gcc.gnu.org/bugzilla/show_bug.cgi?id=43328)). This is a bug in the "configure" phase of the standard "configure;make;make install" but shows up in the "make" stage. So, I'll revisit this as time permits and see about getting the latest GCC 4.6 series working.

The more exciting thing is that it looks like both GCC versions that compiled will compile code to an intermediate state.  That is not proof that it generates a working executable but it is a step in the right direction.

For the GCC 4.3.2 version here is a test showing it compiling a quick test.
```
$ cat > test.c
int main (){return 0;}
Ctrl-D
$ ./arm-elf-gcc -Os -S test.c
$ cat test.s

        .file   "test.c"

        .text
        .align  2
        .global main
        .type   main, %function
main:
        @ args = 0, pretend = 0, frame = 0
        @ frame_needed = 0, uses_anonymous_args = 0
        @ link register save eliminated.
        mov     r0, #0
        bx      lr
        .size   main, .-main
        .ident  "GCC: (GNU) 4.3.2"
```

For the GCC 4.4.6 version here is a test showing it compiling a quick test.
```
$ cat > test.c
int main (){return 0;}
Ctrl-D
$ ./arm-elf-gcc -Os -S test.c
$ cat test.s

        .file   "test.c"
        .text
        .align  2
        .global main
        .type   main, %function
main:
        @ args = 0, pretend = 0, frame = 0
        @ frame_needed = 0, uses_anonymous_args = 0
        @ link register save eliminated.
        mov     r0, #0
        bx      lr
        .size   main, .-main
        .ident  "GCC: (GNU) 4.4.6"
```

While this is good news, it is not an ARM executable. My followup post will not be so upbeat.
