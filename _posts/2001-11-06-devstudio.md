---
title:  "Microsoft Developer Studio 6.0 Patches"
layout: post
categories: technical
---

This is a very old set of notes but might be useful for a developer dealling with Microsoft Visual Studio 6.0 for DOS and Windows 16-bit coding. This is from the era of Borland and Zortech Compilers being in play. I migrated this from my darkmagic.org website.

<!-- excerpt-end -->

---

Remove all "MSCREATE.DIR" files from your system.  These just
tie up space on the drive.  MSVC has several hundred of these
files in it's directory structure.

---

## Settings in VC6

Tools->Customize -- add the "View Full Screen" from the View Category to the menu bars.

Tools->Options
Tabs -- check "Insert spaces" for all code types.
Workspace -- "Display clock on status bar" and "Reload last workspace at startup"

---

## Running DevStudio 6.0 builds in low priority

Original article was written by Leigh Stivers.

Updates by J. Michael McGarrah.

During large project builds, it is usually useful to do other stuff with your computer, but I find that the computer becomes very sluggish, until I change the priority of the vcspawn.exe and cl.exe to low using the NT task manager. After doing so, the computer becomes quite responsive until the next build...

Since Microsoft didn't provide an option to automatically run the compiler/linker in low priority, I've figured a way that easily does this. What I have done is located in the vcspawn.exe executable, the call to CreateProcessA(). One of the parameters (dwCreationFlags) includes the priority at which you wish to run the created process. Vcspawn.exe normally runs everything with the dwCreationFlags set to 0x00000200, which decoded means use only the CREATE_NEW_PROCESS_GROUP flag. What I wish to include in the dwCreationFlags parameter is the flag, IDLE_PRIORITY_CLASS which is 0x00000040, so my replacement dwCreationFlags is 0x00000240 - a one byte difference. After making the simple one byte edit, all my builds are performed in low priority mode. Now you may think that by running at low priority, all your builds will take longer to complete, but you will be surprise at the little difference in actual build times, unless you were doing some other heavy duty task.

To make the one byte edit, first backup x:\Program Files\Microsoft Visual Studio\Common\MSDev98\Bin\vcspawn.exe and then from inside DevStudio, open in BINARY mode, vcspawn.exe. Bring up the Go To dialog by typing, control-g, and key in the address 0x27ec and close the Go To dialog. The byte should be 00 with the previous byte being 68 and the following byte being 02. If they are not, then you are running a different version of vcspawn.exe and you shouldn't attempt the change. If they are, then you can just type in the replacement byte of 40. The new byte sequence starting at 0x27eb should now read 68 40 02. Save and close the file. Now all further builds will be performed in low priority.

For VC++ 5.0 vcspawn.exe, you can do the same type of change at address 0x0e49, changing the byte from 00 to 40.

For VC++ 4.2b vcspawn.exe, you can do the same type of change at address 0x0d24, changing the byte from 00 to 40.

JMM: There was some talk on a forum about writing a replacement program for vcspawn.exe that would execute the Microsoft vcspawn.exe program but run at a lower priority. This program would just have to forward the commandline and execute vcspawn.exe. Don't see what would be so hard about it except for possible problems with process ID numbers of vcspawn versus the custom vcspawn.

JMM: I have the old code for ShellEx.exe that I wrote from my Ziff-Davis days that might give me a quick leg up on the work. There were additional issues that were solved by that code for Win31 environments.

---

## SysIncl.dat update removes BASETSD.H dependancy

Article was written by Michael McGarrah

Tired of BASETSD.H being added as a dependacy of every project. Add it to the x:\Program Files\Microsoft Visual Studio\Common\MSDev98\Bin\Sysincl.dat file and it will no longer be listed as a dependancy.

---

## XString 4245 warnings for UINT to INT conversions

Article was written by Michael McGarrah

Below are some modifications to x:\Program Files\Microsoft Visual Studio\VC98\Include\Xstring that remove a persistant warning for a unit to int conversion. Check for the lines with JMMFIX and add them.

```C
// xstring internal header (from <string>)

#if     _MSC_VER > 1000
#pragma once
#endif

#ifndef _XSTRING_
#define _XSTRING_
#include <xmemory>

#pragma warning(disable:4245) /*JMMFIX: line 600 uint to int conversion wrong */

#ifdef  _MSC_VER
#pragma pack(push,8)
#endif  /* _MSC_VER */
 #include <xutility>
_STD_BEGIN

.
.
.

_STD_END
#ifdef  _MSC_VER
#pragma pack(pop)
#endif  /* _MSC_VER */

#pragma warning(default:4245) /*JMMFIX: restore previous warning */

#endif /* _XSTRING */

/*
 * Copyright (c) 1995 by P.J. Plauger.  ALL RIGHTS RESERVED. 
 * Consult your license regarding permissions and restrictions.
 */
```

---

## Tabifying and settings for DevStudio

Article was written by Michael McGarrah

Here are my common settings as a registry file. I like spaces and not hard tabs in my code. I also like a few other settings that are reflected in this file.

```regedit
REGEDIT4

; Microsoft Visual Studio 6.0 settings
;

; Auto reload previous project and enable clock
;
[HKEY_CURRENT_USER\Software\Microsoft\DevStudio\6.0\Layout]
"Clock"=dword:00000001
"ReloadProject"=dword:00000001

; Do not auto reload files modified outside MSVC and
; save all files before building
[HKEY_CURRENT_USER\Software\Microsoft\DevStudio\6.0\Text Editor]
"SaveBeforeBuild"=dword:00000001
"AutoReload"=dword:00000000

; All TAB should be spaces and should be indented 4 spaces
;
[HKEY_CURRENT_USER\Software\Microsoft\DevStudio\6.0\Text Editor\Tabs/Language Settings\Default]
"InsertSpaces"=dword:00000001
"TabSize=dword:00000004
"IndentSize"=dword:00000004
"IndentType"=dword:00000001

[HKEY_CURRENT_USER\Software\Microsoft\DevStudio\6.0\Text Editor\Tabs/Language Settings\HTML]
"InsertSpaces"=dword:00000001
"TabSize=dword:00000004
"IndentSize"=dword:00000004
"IndentType"=dword:00000001

[HKEY_CURRENT_USER\Software\Microsoft\DevStudio\6.0\Text Editor\Tabs/Language Settings\ODL/IDL]
"InsertSpaces"=dword:00000001
"TabSize=dword:00000004
"IndentSize"=dword:00000004
"IndentType"=dword:00000001

[HKEY_CURRENT_USER\Software\Microsoft\DevStudio\6.0\Text Editor\Tabs/Language Settings\SQL]
"InsertSpaces"=dword:00000001
"TabSize=dword:00000004
"IndentSize"=dword:00000004
"IndentType"=dword:00000001

[HKEY_CURRENT_USER\Software\Microsoft\DevStudio\6.0\Text Editor\Tabs/Language Settings\VBS Macro]
"InsertSpaces"=dword:00000001
"TabSize=dword:00000004
"IndentSize"=dword:00000004
"IndentType"=dword:00000001
```

---

## Common problem and solution to linker errors

by Michael McGarrah

Here are two common problems I run into with the linker that I have to figure out everytime I run into them. Hope this saves someone some time.

```shell
"LNK2001: unresolved external symbol _main" error
generally mean you need to:
enable the checkbox in
 --> 'Project->Settings->Linker->General->Ignore all default libraries'

"error LNK2001: unresolved external symbol __chkesp"
generally means you need to:
remove the /GZ from the compiler switches
The "error LNK2001: unresolved external symbol __chkstk"
generally means you are using stack and need stack checking
which is buried in LIBC.

_chkstk is a libc function that makes sure there are no
stack overflows. It is automatically added to functions
that needs more than 4K of memory on the stack.
If you declare a buffer the size of 16000, it will be
added, but libc is not be added for optimizing purposes.
This saves about 40KB on the built module (EXE/DLL).
Thus, you are left with the automatically added __chkstk
calls but no LIBC with the function.
To fix this you either dynamically allocate all the large
buffers, or make all buffers static.  Static are
"statically allocated" (not on stack) only once in
memory and not with every call to the function.  Thus
they do not need stack checking and the __chkstk function.
```
