---
title: "Proxmox & Ceph Homelab Guide"
permalink: "/proxmox-ceph-guide/"
layout: page
description: "A comprehensive guide to building and managing a Proxmox VE cluster with Ceph storage in a homelab environment, based on hands-on experience with Dell Wyse 3040s and enterprise hardware."
last_modified_at: 2026-04-02
---

Everything I've learned building and running Proxmox VE clusters with Ceph storage in my homelab. These articles are based on direct, hands-on experience — real problems, real fixes, and real hardware.

## Getting Started with Proxmox

- [ProxMox 8.2 for the Homelabs](/proxmox-8-homelab/) — Initial cluster setup and architecture decisions
- [Proxmox VE 8.1 to 8.2 Upgrade Issues](/proxmox-upgrade-issues/) — Upgrade pitfalls and how to avoid them
- [Proxmox 8 Lessons Learned](/proxmox-8-lessons-learned/) — Hard-won tips from running Proxmox in production

## Ceph Storage

- [Proxmox Ceph Settings for the Homelab](/proxmox-ceph-homelab-settings/) — Tuning Ceph for low-power hardware
- [Ceph Cluster Rebalance Issue](/ceph-rebalance/) — Diagnosing and fixing rebalance problems
- [Managing Ceph Nearfull Warnings](/proxmox-ceph-nearfull/) — Handling capacity warnings before they become outages
- [Optimizing Ceph Performance in Proxmox](/proxmox-ceph-performance/) — Performance tuning and benchmarking
- [Adding Ceph Dashboard to Your Proxmox Cluster](/proxmox-add-ceph-dashboard/) — Web-based monitoring setup
- [Ceph Cluster Complete Removal on Proxmox](/proxmox-remove-ceph-completely/) — Clean removal when you need to start over
- [Homelab Storage Economics: Ceph vs Single Drive](/homelab-storage-economics/) — Cost analysis of distributed storage

## Dell Wyse 3040 Cluster

My test cluster runs on Dell Wyse 3040 thin clients — $15 each on eBay:

- [ProxMox 8.2.2 Cluster on Dell Wyse 3040s](/proxmox-8-dell-wyse-3040/) — Building a cluster from thin clients
- [ProxMox 8.2.4 Upgrade on Dell Wyse 3040s](/proxmox-8-dell-wyse-3040-upgrade/) — Upgrading the low-resource cluster
- [Dell Wyse 3040 CMOS Battery Replacement](/dell-wyse-3040-cmos-battery/) — Hardware maintenance
- [Debian 12 on Dell Wyse 3040s](/dell-wyse-3040-debian12/) — Base OS installation
- [Tailscale on Dell Wyse 3040](/dell-wyse-3040-tailscale/) — Remote access setup
- [Dell Wyse 3040 eMMC Storage Health Monitoring](/dell-wyse-3040-emmc-monitoring/) — Keeping tabs on embedded storage
- [Debian 12 SystemD Nightly Reboots on Dell Wyse 3040s](/dell-wyse-3040-reboot/) — Stability workarounds

## Monitoring & Maintenance

- [Monitoring ZFS Boot Mirror Health in Proxmox 8](/proxmox-zfs-boot-mirror-smart-analysis/) — SMART monitoring for boot drives
- [Consolidating Proxmox Notes: A Python Export Script](/proxmox-consolidated-notes/) — Automating cluster documentation
- [Optimizing Jellyfin on Proxmox: Moving Metadata to CephFS](/jellyfin-lxc-proxmox-disk-full/) — LXC container optimization with Ceph

## Supporting Infrastructure

- [Caddy Reverse Proxy for Proxmox Web UI](/caddy-reverse-proxy-proxmox-web-ui/) — Single entry point with load balancing and health checks
- [Caddy Reverse Proxy for Ceph Dashboard](/caddy-reverse-proxy-ceph-dashboard/) — Stable URL for the floating ceph-mgr dashboard
- [Buying a 10Gbps Network on a Homelab Budget](/homelab-sfp-plus-networking/) — SFP+ networking on the cheap
- [Linux Disk I/O Performance in the Homelab](/linux-disk-io-quick-tests/) — Quick benchmarking methods
- [Enabling SMART Monitoring on Seagate USB Drives](/usb-drive-smart/) — Getting health data from USB storage
