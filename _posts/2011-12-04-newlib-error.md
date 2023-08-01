---
title:  "Newlib error during compile"
layout: post
categories: personal black_armor hardware nas seagate
---

Earlier I was working on the problem with compiling using the arm-elf-gcc on very basic programs.  After some work, I found the base problem is that the libc replacement from newlib are not being picked up at compile time and properly using the syscalls mechanism. Hardwired hacks to work around it produced an executable but something is still wrong with how the compiler was built.

I've distilled the error down to a single search.

[Google Search](https://www.google.com/search?gcx=c&sourceid=chrome&ie=UTF-8&q=%22%2Flib%2Flibc.a(lib_a-exit.o)%3A+In+function+%60exit%27%3A%22+%22newlib%2Flibc%2Fstdlib%2Fexit.c%3A65%3A+undefined+reference+to+%60_exit%27%22): "/lib/libc.a(lib_a-exit.o): In function `exit':" "newlib/libc/stdlib/exit.c:65: undefined reference to `_exit'"

Several other people appear to have run into the same problem, so I'll be reading up on the problem and see what solutions exist.
