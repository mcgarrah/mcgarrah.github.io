---
title: "Proxmox LXC Template for OpenWRT for the Homelabs"
layout: post
categories: [technical, homelab, proxmox]
tags: [proxmox, homelab, openwrt, lxc]
date: 2024-09-13
last_modified_at: 2026-08-07
excerpt: "Digging into Proxmox's unmanaged LXC ostype, the undocumented openwrt.common.conf template, and LXC hookscripts while working out a cleaner way to run OpenWRT in an LXC container."
description: "Notes on Proxmox's LXC ostype handling for OpenWRT — the unmanaged ostype workaround, an undocumented openwrt.common.conf template found on the host, and available LXC hookscript examples."
seo:
  type: BlogPosting
  date_published: 2024-09-13
  date_modified: 2026-08-07
---

OpenWRT in an LXC using a template... we currently have to do this as an unmanaged ostype and a manual download of rootfs. This should be easier.

<!-- excerpt-end -->


### LXC ostype

`ostype: <alpine | archlinux | centos | debian | devuan | fedora | gentoo | nixos | opensuse | ubuntu | unmanaged>`

[Proxmox Linux Container](https://pve.proxmox.com/wiki/Linux_Container) has several sections on this...

The lxc setup scripts in /usr/share/lxc/config/<ostype>.common.conf manage the OS implementations.  Unmanaged skips all the changes.

There is an unannounced OpenWRT entry in there...

``` console
root@pve2:/usr/share/lxc/config# ls -l openwrt.common.conf
-rw-r--r-- 1 root root 1353 Apr  5 07:12 openwrt.common.conf
```

### LXC scripts

`root@pve2:/usr/share/lxc` templates has some interesting stuff in there. `lxc-download` in particular.

### Hookscripts

LXC Hookscripts are one thing... to help out... `/usr/share/pve-docs/examples` with only one example.

``` console
root@pve1:/usr/share/pve-docs/examples# ls -l
-rwxr-xr-x 1 root root 1546 Jul 31 10:58 guest-example-hookscript.pl
```
