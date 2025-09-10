---
title:  "Debian Linux Oh-Crap Moment in the Homelab"
layout: post
categories: [technical, troubleshooting]
tags: [linux, debian, bash, recovery, proxmox, homelab]
published: true
---

We have all done it if you work long enough. I blew up my Debian Linux system with an incredibly stupid mistake breaking the whole system. It is actually one of the questions I have when interviewing someone. "What is the worst mistake you've ever made?" And if they admit one, the follow up question, "What did you learn?"

I renamed my `/usr` directory to `/usr-root` with a `mv /usr /usr-root` as the root user. I knew I was treading on dangerous ground so I fortunately had two `ssh` console sessions up and both running as `root`. The goal was to migrate the `/usr` to separate storage to recover space for the very full root disk.

This happened during my [Proxmox 8.2 upgrade process](/proxmox-upgrade-issues/) where I was trying to free up space on the root filesystem before proceeding with the cluster upgrades.

``` shell
root@pve1:/mnt/pve/osdisk# mkdir /usr-new
root@pve1:/mnt/pve/osdisk# mount /usr-new
root@pve1:/# cp -pr /usr/* /usr-new/
root@pve1:/# mv /usr /usr-root
root@pve1:/# mv /usr-new /usr
-bash: /usr/bin/mv: No such file or directory
root@pve1:/# /usr-root/bin/mv /usr-new /usr
-bash: /usr-root/bin/mv: cannot execute: required file not found
```

This was the **oh crap** moment for me when I realized how badly I had just screwed up. When you break stuff this bad, it is time to stop for a minute and take stock. My absolutely worst case scenerio is a 150 mile drive to the box in question and a USB Recovery Boot Drive with my [***trash can*** **crash cart** (TC<sup>3</sup>)](https://www.mcgarrah.org/proxmox-upgrade-issues/). But I have been doing this long enough that I had left myself options with the two active root sessions *if* I worked carefully.

<!-- excerpt-end -->

The above mistake was me just being hasty trying to get to my Proxmox 8.3 upgrades on the main cluster and doing this a little after 1:00am in the morning. That is usually when I screw things up... when I'm in a hurry and a bit tired. There is probably a life lesson in there someplace that I need to think about.

## What Made This Worse: The Debian /usr Merge

Another thing I missed which made this situation much worse was [The Debian /usr Merge](https://wiki.debian.org/UsrMerge). In modern Debian systems, `/lib`, `/sbin` and `/bin` are actually symlinks to `/usr/lib`, `/usr/sbin` and `/usr/bin`. This [Linux Fu article](https://hackaday.com/2020/09/03/linux-fu-moving-usr/) explains the implications well.

I completely missed this major change in Debian file systems. I'm slightly old school UNIX where you could break up all the major volumes/partitions (var, usr, home, etc.) across different disks or partitions. This trend is falling off with the merged root volume approach.

So when I moved `/usr`, I didn't just break user programs - I broke the entire system because the core system directories were symlinked into `/usr`.

## Survival Mode: What You Have When Everything Breaks

When you've nuked your system this badly, what do you actually have left? Fortunately, bash has a lot of built-in commands that don't depend on external binaries.

### Basic File Listing

When `ls` is gone, you can still see what's in directories:

``` shell
echo /*
echo /home/*
echo /etc/*
```

### Useful Aliases for Sanity

These bash-only aliases can help you navigate:

``` console
alias myls='echo $*/*'
alias mycatin='(IFS=$'\n';while read line;do echo "$line";done) <'
alias mycatout='(IFS=$'\n';while read line;do echo "$line";done) >'
```

### Assessing What Commands You Have

First, figure out what's still working:

``` shell
type -a enable
```

``` console
root@pve1:~# type -a echo
echo is a shell builtin
echo is /usr/bin/echo
echo is /bin/echo
```

For a complete list of built-in bash commands:

``` shell
enable
```

The most useful ones for recovery are `echo`, `cd`, `export`, `type`, `read`, `printf`, and `help`.

``` console
root@pve1:~# enable
enable .
enable :
enable [
enable alias
enable bg
enable bind
enable break
enable builtin
enable caller
enable cd
enable command
enable compgen
enable complete
enable compopt
enable continue
enable declare
enable dirs
enable disown
enable echo
enable enable
enable eval
enable exec
enable exit
enable export
enable false
enable fc
enable fg
enable getopts
enable hash
enable help
enable history
enable jobs
enable kill
enable let
enable local
enable logout
enable mapfile
enable popd
enable printf
enable pushd
enable pwd
enable read
enable readarray
enable readonly
enable return
enable set
enable shift
enable shopt
enable source
enable suspend
enable test
enable times
enable trap
enable true
enable type
enable typeset
enable ulimit
enable umask
enable unalias
enable unset
enable wait
```

```
root@pve1:~# help
GNU bash, version 5.2.15(1)-release (x86_64-pc-linux-gnu)
These shell commands are defined internally.  Type `help' to see this list.
Type `help name' to find out more about the function `name'.
Use `info bash' to find out more about the shell in general.
Use `man -k' or `info' to find out more about commands not in this list.

A star (*) next to a name means that the command is disabled.

 job_spec [&]                                                  history [-c] [-d offset] [n] or history -anrw [filename] o>
 (( expression ))                                              if COMMANDS; then COMMANDS; [ elif COMMANDS; then COMMANDS>
 . filename [arguments]                                        jobs [-lnprs] [jobspec ...] or jobs -x command [args]
 :                                                             kill [-s sigspec | -n signum | -sigspec] pid | jobspec ...>
 [ arg... ]                                                    let arg [arg ...]
 [[ expression ]]                                              local [option] name[=value] ...
 alias [-p] [name[=value] ... ]                                logout [n]
 bg [job_spec ...]                                             mapfile [-d delim] [-n count] [-O origin] [-s count] [-t] >
 bind [-lpsvPSVX] [-m keymap] [-f filename] [-q name] [-u na>  popd [-n] [+N | -N]
 break [n]                                                     printf [-v var] format [arguments]
 builtin [shell-builtin [arg ...]]                             pushd [-n] [+N | -N | dir]
 caller [expr]                                                 pwd [-LP]
 case WORD in [PATTERN [| PATTERN]...) COMMANDS ;;]... esac    read [-ers] [-a array] [-d delim] [-i text] [-n nchars] [->
 cd [-L|[-P [-e]] [-@]] [dir]                                  readarray [-d delim] [-n count] [-O origin] [-s count] [-t>
 command [-pVv] command [arg ...]                              readonly [-aAf] [name[=value] ...] or readonly -p
 compgen [-abcdefgjksuv] [-o option] [-A action] [-G globpat>  return [n]
 complete [-abcdefgjksuv] [-pr] [-DEI] [-o option] [-A actio>  select NAME [in WORDS ... ;] do COMMANDS; done
 compopt [-o|+o option] [-DEI] [name ...]                      set [-abefhkmnptuvxBCEHPT] [-o option-name] [--] [-] [arg >
 continue [n]                                                  shift [n]
 coproc [NAME] command [redirections]                          shopt [-pqsu] [-o] [optname ...]
 declare [-aAfFgiIlnrtux] [name[=value] ...] or declare -p [>  source filename [arguments]
 dirs [-clpv] [+N] [-N]                                        suspend [-f]
 disown [-h] [-ar] [jobspec ... | pid ...]                     test [expr]
 echo [-neE] [arg ...]                                         time [-p] pipeline
 enable [-a] [-dnps] [-f filename] [name ...]                  times
 eval [arg ...]                                                trap [-lp] [[arg] signal_spec ...]
 exec [-cl] [-a name] [command [argument ...]] [redirection >  true
 exit [n]                                                      type [-afptP] name [name ...]
 export [-fn] [name[=value] ...] or export -p                  typeset [-aAfFgiIlnrtux] name[=value] ... or typeset -p [->
 false                                                         ulimit [-SHabcdefiklmnpqrstuvxPRT] [limit]
 fc [-e ename] [-lnr] [first] [last] or fc -s [pat=rep] [com>  umask [-p] [-S] [mode]
 fg [job_spec]                                                 unalias [-a] name [name ...]
 for NAME [in WORDS ... ] ; do COMMANDS; done                  unset [-f] [-v] [-n] [name ...]
 for (( exp1; exp2; exp3 )); do COMMANDS; done                 until COMMANDS; do COMMANDS-2; done
 function name { COMMANDS ; } or name () { COMMANDS ; }        variables - Names and meanings of some shell variables
 getopts optstring name [arg ...]                              wait [-fn] [-p var] [id ...]
 hash [-lr] [-p pathname] [-dt] [name ...]                     while COMMANDS; do COMMANDS-2; done
 help [-dms] [pattern ...]                                     { COMMANDS ; }
```

## The Long Road to Recovery

After discovering I still had `bash` built-ins, I had to figure out how to get my system commands working again. The problem was that even though I could see the binaries in `/usr-root/bin/`, they wouldn't execute because of missing shared libraries.

### Understanding the Library Problem

Linux binaries need shared libraries to run. When I moved `/usr`, I broke the library paths. The error "cannot execute: required file not found" wasn't about the binary - it was about the dynamic linker and shared libraries.

First part, being clever with file systems.

``` shell
root@pve1:/mnt/pve/osdisk# cat /etc/fstab
# /etc/fstab: static file system information.
#
# Use 'blkid' to print the universally unique identifier for a
# device; this may be used with UUID= as a more robust way to name devices
# that works even if disks are added and removed. See fstab(5).
#
# systemd generates mount units based on this file, see systemd.mount(5).
# Please run 'systemctl daemon-reload' after making changes here.
#
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
# / was on /dev/mmcblk0p2 during installation
UUID=9f9ef2f9-6ac3-499a-84b1-acd941e9c24b /               ext4    errors=remount-ro 0       1
# /boot/efi was on /dev/mmcblk0p1 during installation
UUID=6F92-F3D4  /boot/efi       vfat    umask=0077      0       1
# swap was on /dev/mmcblk0p3 during installation
UUID=04dee0a1-3780-4bba-83ae-54027e28759d none            swap    sw              0       0
root@pve1:/mnt/pve/osdisk# grep -ri 294d /etc/
/etc/systemd/system/mnt-pve-osdisk.mount:What=/dev/disk/by-uuid/294d2147-5657-41a7-9c6c-4de633c9d428
root@pve1:/mnt/pve/osdisk# vim /etc/fstab
root@pve1:/mnt/pve/osdisk# mkdir /usr-new
root@pve1:/mnt/pve/osdisk# mount /usr-new
mount: (hint) your fstab has been modified, but systemd still uses
       the old version; use 'systemctl daemon-reload' to reload.
root@pve1:/mnt/pve/osdisk# systemctl daemon-reload
root@pve1:/mnt/pve/osdisk# df
Filesystem                                  1K-blocks    Used Available Use% Mounted on
udev                                           930924       0    930924   0% /dev
tmpfs                                          192820    1724    191096   1% /run
/dev/mmcblk0p2                                5923864 4476644   1125380  80% /
tmpfs                                          964088   67488    896600   8% /dev/shm
tmpfs                                            5120       0      5120   0% /run/lock
efivarfs                                          256     202        50  81% /sys/firmware/efi/efivars
/dev/mmcblk0p1                                 523248   11932    511316   3% /boot/efi
/dev/fuse                                      131072      36    131036   1% /etc/pve
tmpfs                                          964088      28    964060   1% /var/lib/ceph/osd/ceph-3
192.168.89.11,192.168.89.12,192.168.89.13:/  25931776  122880  25808896   1% /mnt/pve/cephfs
tmpfs                                          192816       0    192816   0% /run/user/1000
/dev/sda1                                     7610676      24   7202592   1% /usr-new
root@pve1:/mnt/pve/osdisk# cd
root@pve1:~# cp -pr /usr/* /usr-new/
```

Next part with moving around file systems and broken world happens.

``` shell
root@pve1:/# mv /usr /usr-root
root@pve1:/# mv /usr-new /usr
```

The broken world begins with me diagnosing things along the way.

``` shell
-bash: /usr/bin/mv: No such file or directory
root@pve1:/# /usr-root/bin/mv /usr-new /usr
-bash: /usr-root/bin/mv: cannot execute: required file not found
root@pve1:/# /usr-root/bin/mv
bin             home/           lib64           opt/            sbin            usr-new/        vmlinuz.old
boot/           initrd.img      lost+found/     proc/           srv/            usr-root/
dev/            initrd.img.old  media/          root/           sys/            var/
etc/            lib             mnt/            run/            tmp/            vmlinuz
root@pve1:/# ls
-bash: /usr/bin/ls: No such file or directory
root@pve1:/# echo /lib64/*
/lib64/*
root@pve1:~# which mv
-bash: which: command not found
root@pve1:~# ln -s
-bash: ln: command not found
root@pve1:~# echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
root@pve1:~# export $PATH=/usr-root/bin:$PATH
-bash: export: `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin=/usr-root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin': not a valid identifier
root@pve1:~# $PATH=/usr-root/bin:$PATH
-bash: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin=/usr-root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin: No such file or directory
root@pve1:~# export PATH=/usr-root/bin:$PATH
root@pve1:~# echo $PATH
/usr-root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
root@pve1:~# ls
-bash: /usr-root/bin/ls: cannot execute: required file not found
root@pve1:~# ls -al /usr-root/bin/ls
-bash: /usr-root/bin/ls: cannot execute: required file not found
root@pve1:~# /usr-root/bin/sudo mv /usr-root /usr
-bash: /usr-root/bin/sudo: cannot execute: required file not found
root@pve1:~# export LD_LIBRARY_PATH=/usr-root/lib:/usr-root/local/lib:$LD_LIBRARY_PATH
root@pve1:~# ls
-bash: /usr-root/bin/ls: cannot execute: required file not found
root@pve1:~# echo /usr-root/bin/*
/usr-root/bin/[ /usr-root/bin/aa-enabled /usr-root/bin/aa-exec /usr-root/bin/aa-features-abi /usr-root/bin/addpart ... /usr-root/bin/zstdmt /usr-root/bin/zvol_wait
root@pve1:~# echo $PATH
/usr-root/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
root@pve1:~# echo $LD_LIBRARY_PATH
/usr-root/lib:/usr-root/local/lib:
root@pve1:~# env
-bash: /usr-root/bin/env: cannot execute: required file not found
root@pve1:~# echo /usr/
/usr/
root@pve1:~# echo /usr/*
/usr/*
root@pve1:~# echo /usr-root/*
/usr-root/bin /usr-root/games /usr-root/include /usr-root/lib /usr-root/lib64 /usr-root/libexec /usr-root/local /usr-root/sbin /usr-root/share /usr-root/src
root@pve1:~# LD_LIBRARY_PATH=/usr-root/lib64 /usr-root/bin/ls
-bash: /usr-root/bin/ls: cannot execute: required file not found
root@pve1:~# LD_LIBRARY_PATH=/usr-root/lib64 /usr-root/lib64/ld-linux-x86-64.so.2 /usr-root/bin/ls
-bash: /usr-root/lib64/ld-linux-x86-64.so.2: No such file or directory
root@pve1:~# LD_LIBRARY_PATH=/usr-root/lib64 /usr-root/lib64/ld-linux-x86-64.so.2 /usr-root/bin/ls
-bash: /usr-root/lib64/ld-linux-x86-64.so.2: No such file or directory
root@pve1:~# LD_LIBRARY_PATH=/lib/x86_64-linux-gnu /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /usr-root/bin/ls
-bash: /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2: No such file or directory
root@pve1:~# LD_LIBRARY_PATH=/lib/x86_64-linux-gnu /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /usr-root/bin/ls
-bash: /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2: No such file or directory
root@pve1:~# echo /lib/x86_64-linux-gnu/ld-linux-*
/lib/x86_64-linux-gnu/ld-linux-*
root@pve1:~# echo /lib/x86_64-linux-gnu/*
/lib/x86_64-linux-gnu/*
root@pve1:~# echo /lib
/lib
root@pve1:~# echo /lib/*
/lib/*
root@pve1:~# echo /
/
root@pve1:~# echo /*
/bin /boot /dev /etc /home /initrd.img /initrd.img.old /lib /lib64 /lost+found /media /mnt /opt /proc /root /run /sbin /srv /sys /tmp /usr-new /usr-root /var /vmlinuz /vmlinuz.old
root@pve1:~# LD_LIBRARY_PATH=/usr-root/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /usr-root/bin/ls  -bash: /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2: No such file or directory
root@pve1:~# LD_LIBRARY_PATH=/usr-root/lib/x86_64-linux-gnu /usr-root/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /usr-root/bin/ls
cssh  set-osd-mclock-max-cap-iops.sh  setup_openwrt_lxc_container_proxmox.sh
root@pve1:~# LD_LIBRARY_PATH=/usr-root/lib/x86_64-linux-gnu /usr-root/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /usr-root/bin/ls
```

### Finding the Dynamic Linker

I had to figure out where the dynamic linker was located. On a working system, I traced through the library locations to understand the path structure. The key was finding `/usr-root/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2` - the dynamic linker that could load and execute binaries.

### The Magic Recovery Command

Once I found the right library path, I could execute the `mv` command by manually specifying the dynamic linker:

``` console
root@pve1:~# LD_LIBRARY_PATH=/usr-root/lib/x86_64-linux-gnu /usr-root/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /usr-root/bin/mv /usr-root /usr
```

And just like that, the system was back:

``` console
root@pve1:/# ls
bin   dev  home        initrd.img.old  lib64       media  opt   root  sbin  sys  usr      var      vmlinuz.old
boot  etc  initrd.img  lib             lost+found  mnt    proc  run   srv   tmp  usr-new  vmlinuz
```

The key insight was that I needed to:
1. Set `LD_LIBRARY_PATH` to point to the relocated libraries
2. Use the dynamic linker directly to execute the `mv` command
3. Move `/usr-root` back to `/usr`

## Boot Failure

Full disclosure ... along the way ... I screwed up again with a bad `/etc/fstab` bind mount entry ... that meant I had to do the 150 mile drive to get past this screen... Unfortunately, I don't have the photo from my phone, but it was the dreaded "emergency mode" boot screen that every Linux admin fears.

The lesson learned was forgetting to add the `nofail` option to my `/etc/fstab` entries. I had learned this at some point in the past but had to re-learn it the hard way. The `nofail` option tells systemd to continue booting even if a mount fails, rather than dropping into emergency mode.

Also, the behavior of these options has changed since the SystemD transitions in recent years, so it's another thing to re-re-learn.

## What I Learned

1. **Never work on critical systems when tired** - Most of my worst mistakes happen after midnight
2. **Always have multiple SSH sessions open** - This saved me from a 150-mile drive
3. **Understand modern filesystem layouts** - The `/usr` merge changes everything
4. **Know your bash built-ins** - They're your lifeline when everything else breaks
5. **Use `nofail` in fstab** - Prevents boot failures from experimental mounts
6. **Test recovery procedures** - Practice these techniques on non-critical systems

## Useful References

These resources helped me understand bash-only recovery techniques:

- [Bash Copy Function](https://www.qfbox.info/bashcp)
- [Rescuing a Hosed System Using Only Bash](http://fendrich.se/blog/2010/08/27/rescuing-hosed-system-using-only-bash/)
- [Unix StackExchange: After accidentally renaming /usr](https://unix.stackexchange.com/questions/432002/after-accidentally-renaming-usr-how-do-i-rename-it-back)
- [Unix StackExchange: Moved /bin and other folders](https://unix.stackexchange.com/questions/17428/moved-bin-and-other-folders-how-to-get-them-back)

The moral of the story? We all make mistakes. The key is having enough knowledge and preparation to recover from them. And maybe don't do system administration at 1 AM.
