---
title:  "Some useful CLI tools for Linux"
layout: post
published: false
---

When working on various things in the Linux space, you end up needing to dig into performance or usage statistics for one of the big areas of management like storage, network or processes.
Here are some useful command line interface (CLI) tools for Linux or UNIX based systems. They are just a recent collection that I've found useful to checking the performance or status of a running system.

<!-- excerpt-end -->

## Earlier posts

[ProxMox 8.2.2 Cluster on Dell Wyse 3040s](https://www.mcgarrah.org/proxmox-8-dell-wyse-3040/)

`mcgarrah@pve1:~$ sudo apt install htop iftop iptraf dstat ioping iotop`

`mcgarrah@pve1:~$ sudo apt install lm-sensors -y`
`mcgarrah@pve1:~$ sensors`

[ProxMox 8.2.4 Upgrade on Dell Wyse 3040s](https://www.mcgarrah.org/proxmox-8-dell-wyse-3040-upgrade/)

**Surprise of atop daily logs** removal of `atop`

## List

ntop/ntopng and 

nethogs - Bandwidth Monitoring by Process

iptraf or iptraf-ng

iotop

apt show bwm-ng cbm dstat iftop iptraf-ng nethogs nload

bandwhich - https://github.com/imsnif/bandwhich

gtop - fancy visuals of system stats

slabtop – displays a listing of the top caches

## Other articles

This article has a really nice outline of tools with some organization that I was struggling with doing.

https://monadical.com/posts/system-monitoring-tools.html

All-in-one tools
    glances ⭐️ 🌈
    nmon 🌈
    dstat
    atop ⭐️
    tiptop/mactop 🌈
    osquery ⭐️
    sar
    landscape-sysinfo
    webmin/cockpit ⭐️ 🌈
CPU / Memory
    lscpu
    lsmem
    top
    htop ⭐️ 🌈
    mpstat
    btop++ ⭐️ 🌈
    pidstat
    free
    vmstat
    tsubame 🌈
    memray 🌈
GPU
    gpustat
    intel_gpu_top
    nvtop
    radeontop
    nvidia-smi
    glmark2
    glxgears
Filesystem
    iotop ⭐️
    ioping
    lsof ⭐️
    fuser
    blktrace
    debugfs
    iostat
    zpool iostat ⭐️
    nfsiostat
    cifsiostat
    hdparm
    bonnie++
    dd ⭐️
    rsync/rclone/rsnapshotd/sanoid+syncoid
    gddrescue/dd_rescue/ddrescue-gui/recoverdisk/safecopy/recoverypy
    df
    ncdu ⭐️🌈
    find
    parted
    blkid
    lsblk ⭐️
    lsscsi
    fdisk ⭐️🌈
    zfs/nfs/samba/glusterfs
Network
    nethogs ⭐️🌈
    iftop
    iptraf-ng🌈
    pktstat
    speedometer / nload / bmon / slurm / bwm-ng / cbm / netload / ifstat / etc. 🌈
    netstat ⭐️
    ethtool
    ip/ifconfig
    ping/tcping/arping
    arpwatch
    iperf/iperf3 ⭐️
    nuttcp
    speedtest-cli
    dig/dug/dog/host/nslookup/doggo 🌈
    mtr ⭐️
    nmap ⭐️
    tcpdump + wireshark
    ssldump
    wsrepl 🌈
    iptables/iptables-tui
    impala 🌈
Hardware
    sensors
    ipmitool
    i7z
    cpufreq-info ⭐️
    cpupower
    powertop ⭐️
    dmidecode
    smartctl ⭐️
    apcaccess status
    lshw ⭐️
    lsusb
    usb-devices ⭐️
    camcontrol
    dmesg ⭐️
    last
VM / Docker
    ctop ⭐️🌈
    docker stats
    virt-top
    esxtop
DB / Webserver
    pg_top ⭐️
    mytop
    redis-stat
    ngxtop ⭐️
    apachetop
    uwsgitop
OS / System
    nala 🌈
    uname
    lsmod
    lsb_release
    watchdog/auditd/acct
    systemd-analyze / isd
    dpkg/apt list/apt-file/apt-mark
Profiling / Debugging
    pv/progress ⭐️
    strace/dtrace/dtruss ⭐️
    ltrace
    binwalk/strings/hexyl/hexabyte/dissy 🌈

## Process Management

CPU, RAM, swap, etc...

### Built-in tools

`ps`

### Add-on tools

`top`
`htop`
`btop`

Note: Removed `atop` as it has default storage requirements that hurt me on some smaller systems. The storage of X days of results was nice but not worth it on my Dell Wyse 3040s were it filled a significatnt percentage of the the root disk volume.

## Storage Management

Space and I/O are the two parts of storage we always come back too...

### Built-in tools

`du`
`tree`
`df`
`iostat` ?

### Add-on tools

`ncdu`
`iotop`

## Network Management

Amount and speed of network traffic...

`iftop`

## Unknowns

`glances` (system monitoring dashboard)

