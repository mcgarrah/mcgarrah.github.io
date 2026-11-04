---
layout: post
title: "Seagate USB Drives, SMART, and UAS: What the Quirk Really Does"
categories: [homelab, ceph, proxmox]
tags: [seagate, usb, smart, uas, usb-storage, smartctl, linux-kernel, quirks, grub, ceph, proxmox, homelab, pcie]
excerpt: "I wrote two posts saying you must disable UAS to read SMART from Seagate USB drives. The commands work, but my explanation was wrong: the quirk keeps UAS on and removes a flag the kernel puts on every Seagate bridge. Here is what the kernel does, how I tested it, what 24 drives across seven nodes show, and what I still cannot explain."
description: "Why smartctl fails on Seagate USB drives under UAS, what the usb-storage quirks parameter actually changes (an empty-flag entry clears the kernel's built-in NO_ATA_1X flag and leaves UAS on), how to apply it with GRUB, modprobe or sysfs, a survey of 24 Seagate and other USB drives across a seven-node Proxmox Ceph cluster, and the open questions about UAS stability and PCIe link speed."
date: 2026-10-19
last_modified_at: 2026-10-19
seo:
  type: BlogPosting
  date_published: 2026-10-19
  date_modified: 2026-10-19
---

I published two posts telling you to disable UAS to get SMART data out of Seagate USB drives. The commands in them work. The explanation is wrong, and I only found that out this week, when I plugged a spare drive into one of my Ceph nodes and checked which driver it was really using. It was `uas`, the driver I had said I turned off.

This post replaces both: [Enabling SMART Monitoring on Seagate USB Drives](/usb-drive-smart/) and [USB Drive SMART Updates](/usb-drive-smart-updates/). It covers what the kernel actually does, how I tested it, what 24 drives across seven nodes show, and the parts I still cannot explain.

<!-- excerpt-end -->

## What I told you before

My earlier posts said that Seagate USB bridges hide SMART behind UAS quirks. They said that adding the drive's `vendor:product` ID to the `usb-storage` quirks list with empty flags "disables UAS completely". They told you to confirm the drive now shows `usb-storage` instead of `uas`. I also said the price was a 10 to 30 percent performance hit.

Every one of those statements about the mechanism was wrong. I never measured the 10 to 30 percent. I repeated it because it sounded right.

## What the kernel actually does

There are two Linux drivers for a USB disk. `usb-storage` speaks the older Bulk-Only protocol and handles one command at a time. `uas` speaks USB Attached SCSI, which can queue many commands at once and needs a USB 3 link and a bridge that supports it. If a bridge offers UAS, the kernel uses it unless something says otherwise.

The part I missed is in `drivers/usb/storage/uas-detect.h`. For the Seagate vendor ID, `0bc2`, the kernel sets a flag called `NO_ATA_1X` on every device. The comment above that line (Linux 6.8) reads: "All Seagate disk enclosures have broken ATA pass-through support." SMART is read through ATA pass-through. With that flag set, `smartctl` fails with the error you have probably seen:

```
Read Device Identity failed: scsi error unsupported field in scsi command
```

The kernel then applies your `usb_storage.quirks` list on top. An entry with **empty flags**, like `0bc2:ac41:`, replaces the built-in flags for that device with nothing. The `NO_ATA_1X` flag goes away, pass-through works, SMART works, and the drive stays on UAS. The flag that disables UAS is a separate letter, `u`. This is not a bug someone fixed and I missed. The same rule is in Linux 5.15, in the 6.8 kernel my nodes run, and in current mainline, so the quirk is still needed on newer systems. Two letters matter here:

| Flag | Kernel name | Effect |
|---|---|---|
| `t` | `NO_ATA_1X` | Blocks ATA pass-through. This is the thing that breaks SMART |
| `u` | `IGNORE_UAS` | Forces the older `usb-storage` driver |

My earlier post described `t` as "ignore TRIM" and an empty entry as "disable UAS completely". Both were wrong.

## The test

I had a spare 5 TB Seagate drive, a `0bc2:ac41` One Touch, plugged into a node whose other three USB ports carry Ceph OSD drives. I changed the quirk list at runtime for that one ID, rebound only that device, and tried `smartctl` each time. The kernel reported the driver in use in every case.

| Quirk entry for the spare | Driver | SMART |
|---|---|---|
| `0bc2:ac41:` (empty flags, as booted) | `uas` | Works: full attribute table in 0.13 seconds |
| No entry at all (built-in flags apply) | `uas` | Fails with the error above |
| `0bc2:ac41:u` | `usb-storage` | I could not finish this one |

The first two rows are the whole story: same driver, same drive, and the only difference is whether the quirk entry exists. The third row needs an honest note. With the `u` flag set, the kernel logged "UAS is ignored for this device, using usb-storage instead", started the SCSI scan, and then reset the device 22 seconds later without ever producing a disk. I tried a plain rebind, a longer wait, and a full de-authorize and re-authorize. None worked. That says something about this drive and this USB card, not about `usb-storage` in general: three drives with a different bridge model on another node run `usb-storage` every day.

## How to apply it

You have three places to put the list. All three set the same module parameter.

**Kernel command line (what I use on six nodes).** On a GRUB-booted Proxmox host:

```bash
cat > /etc/default/grub.d/usb-quirks.cfg << 'EOF'
GRUB_CMDLINE_LINUX="$GRUB_CMDLINE_LINUX usb_storage.quirks=0bc2:2344:,0bc2:ac41:"
EOF
update-grub   # on a BIOS + GRUB + ZFS node, `proxmox-boot-tool refresh` alone did not rewrite grub.cfg for me
```

My earlier post said this works "regardless of boot mode". It does not. A Proxmox ZFS install that boots with systemd-boot ignores `/etc/default/grub.d`; there the command line lives in `/etc/kernel/cmdline`. Check with `proxmox-boot-tool status` before you choose.

**A modprobe file.** `options usb-storage quirks=0bc2:ac41:` in `/etc/modprobe.d/` works too. My jaeger node has used one across reboots since mid-October, so my earlier claim that this method is unreliable was too strong.

**At runtime.** Writing to `/sys/module/usb_storage/parameters/quirks` takes effect only for devices that enumerate afterwards. Switching a live drive from one driver to the other can leave it without a disk device, as the test above showed, so never try it on a drive that holds data.

To see what you actually have:

```bash
cat /sys/module/usb_storage/parameters/quirks
lsusb -t | grep "Mass Storage"      # shows Driver=uas or Driver=usb-storage
smartctl -H -A /dev/sdX              # plain smartctl is enough; -d sat is optional
```

If you followed my old advice and the verify step told you to expect `usb-storage`, you were reading a correct result as a failure.

## Seven nodes, 24 drives

I wrote a small read-only script that lists every USB storage device on a node, reads the bridge descriptors from sysfs, and runs the same `smartctl` query my monitoring does. Nothing is rebound or written. Across the cluster:

| Bridge ID | Product | Drives | Driver | SMART |
|---|---|--:|---|---|
| `0bc2:2344` | Portable | 10 | uas | works |
| `0bc2:ab83` | One Touch w/PW | 3 | uas | works |
| `0bc2:ab9a` | One Touch HDD | 1 | uas | works |
| `0bc2:ac35` | BUP Portable | 1 | uas | works |
| `0bc2:ac41` | One Touch HDD | 4 | uas | works |
| `0bc2:2038` | Expansion, 28 TB | 1 | uas | works |
| Avolusion, 20 TB | not Seagate | 1 | uas | works, no quirk needed |
| `0bc2:ac2b` | BUP Portable, One Touch | 3 | `usb-storage` | works |

Every bridge generation I own offers UAS, including the oldest. Twenty-one of the 24 devices already run UAS with full SMART, some with more than 20,000 power-on hours. The three on `usb-storage` are the odd node: jaeger, which I configured separately with the `u` flag before I understood any of this.

The surprise is where the resets are. The OSD drives on the six UAS nodes logged between zero and one USB reset each in eight days, my spare drive aside. Jaeger, on `usb-storage`, logged over a hundred in three days, most of them while a large rebalance was writing to its three drives. So `usb-storage` is not the safe choice I assumed it was. *(Update below: jaeger's resets turned out to be hardware, so this over-reads that node.)*

## The link speed matters more than the driver

None of this is where my throughput went. Before any of the driver questions, the USB card on six of seven nodes was negotiating PCIe at 2.5 GT/s. The card and chipset both support 5 GT/s, and a BIOS default was holding the link back. Three drives that each read 125 to 140 MB/s alone summed to 160 MB/s through the shared link. Raising the root port's target speed took the same three drives to 283 MB/s. I wrote that up in [a USB3 Card Stuck at PCIe Gen1 Was Capping My Ceph Backfill](/usb3-pcie-link-stuck-at-2-5-gts-ceph-backfill/).

It also explains why I never measured the UAS cost. With the shared link capping every drive at about 53 MB/s, no difference between the drivers could have shown up. All seven cards now link at 5 GT/s, so that comparison is finally possible, and I have not done it yet.

## What I still cannot explain

Three things, in the order they bother me.

1. **The spare drive stalls under load on UAS.** A `fio` read test produced command aborts, five USB resets, and single reads that took 30 seconds (the SCSI timeout). A plain queue-depth-1 read of the same region, with the neighbors idle, ran at 145 MB/s with no stalls. The same bridge ID, at the same revision, runs three of my production OSDs with no resets. My suspects are contention with the busy neighbors on the shared card, port power, or that one drive, which has the worst timeout history of the four 2018 drives. I do not know which.
2. **Jaeger's resets under `usb-storage`.** The pattern points at that node's cabling, power or controller, not at the driver choice. It is a separate problem from this post's question.
3. **Whether `ac2b`, the bridge on jaeger's drives, works under UAS.** It is the one generation I have not seen with SMART on UAS, and testing it means touching live OSD drives.

I will not claim UAS is faster until I measure it on a healthy drive under a realistic queue depth. I have no like-for-like number yet, because the only spare I could test refuses to come up under `usb-storage`. The queueing benefit is the claim worth testing, and the sequential speed is probably identical.

## Update, 2026-11-03: jaeger's resets were hardware, not the driver

The second item above has an answer, and it is not the driver. Two hardware faults sat on jaeger's USB path: a bad FebSmart card, where a new SATA-powered card fixed some of the problems, and an Anker 7-port powered USB3 hub (12 V, 3000 mA) that was conclusively causing errors on both jaeger and tanaka. [AUTHOR: add the evidence: how the hub was proven, before and after reset counts, and the dates of the card swap.] I wrote the card and link-speed story up in [the USB3 post](/usb3-pcie-link-stuck-at-2-5-gts-ceph-backfill/).

That withdraws one conclusion in this post. Jaeger's resets under `usb-storage` do not show that `usb-storage` is unsafe, because the drives were resetting for reasons that had nothing to do with the driver. Jaeger has also moved to the standard since I wrote the section below: by 25 October its `ac2b` drives were on `uas` with SMART counters readable, which answers the third question above. [AUTHOR: confirm, and add the date jaeger moved to UAS.] The spare drive's stalls under load (the first item) may have the same cause if it sat behind a hub. [AUTHOR: was the spare behind the Anker hub?]

## My standard, and how I check it

I want every node to look identical, so I wrote down one standard. Every node gets the same eight-ID quirk list with empty flags, delivered on the kernel command line by the same file, with no second source. Every Seagate drive runs on `uas` with readable SMART, and the USB card links at 5 GT/s. A read-only script checks a node against it and prints PASS, WARN or FAIL. Today six nodes pass. Three of them carry warnings: one reset on harlan, the spare drive's resets on tanaka, and a leftover modprobe file on poe from my own earlier advice. Jaeger fails, on purpose. Jaeger moves last, after a one-node canary with the new setting, and with the old `u` setting kept as the way back.

One correction with real consequences. My second post said to reboot "2 or 3 nodes at a time". On a six-node cluster that was running six monitors, three down at once loses quorum, and even two can stall I/O. Reboot one node at a time and wait for the cluster to settle.

## What I would do differently

I would have looked at `lsusb -t` the first time the fix worked. I verified that SMART came back and stopped there, so the wrong explanation stood for a year and I repeated it with a made-up performance number attached. The cheap check, reading which driver the kernel chose, was one command.

The larger lesson is the one I keep relearning: when a fix works, find out which part of it worked. For a homelab it costs little. At scale, an explanation you have not tested spreads through runbooks.
