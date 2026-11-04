---
layout: post
title: "A USB3 Card Stuck at PCIe Gen1 Was Capping My Ceph Backfill, and a BIOS Default Was Why"
categories: [homelab, ceph, proxmox]
tags: [ceph, proxmox, pcie, usb3, setpci, link-speed, renesas, uPD720201, backfill, systemd, dell-optiplex-990, troubleshooting]
excerpt: "Six of seven nodes in my Ceph cluster were running their USB3 controller at PCIe 2.5 GT/s although the card and the chipset both support 5 GT/s. The BIOS left the root port's target link speed at Gen1. Raising it with two setpci writes took three USB drives from 160 MB/s to 283 MB/s aggregate, and a small systemd unit makes it stick across reboots. Here is how I isolated it, tested it safely on live storage, and how to check whether your own hardware has the same problem."
description: "Diagnosing and fixing a PCIe link negotiated below its capability on a Dell OptiPlex 990 (Intel Q67) with a Renesas uPD720201 USB3 card carrying Ceph OSD drives. Covers lspci link status analysis, isolating the shared link as the bottleneck with idle drives, raising the root port Target Link Speed with setpci, a node-agnostic discovery script, a boot-time systemd unit ordered before Ceph and ZFS, and the safety procedure for retraining a link under live storage."
date: 2026-10-13
last_modified_at: 2026-10-13
seo:
  type: BlogPosting
  date_published: 2026-10-13
  date_modified: 2026-10-13
---

A storage cluster is only as fast as its narrowest shared path, and the narrowest path is rarely the one you instrumented. I spent weeks tuning Ceph backfill concurrency, reweights and scheduler profiles on a cluster of 2011-era desktops, and the thing that was quietly capping every USB drive on every node was a PCIe link running at half its rated speed because of a default nobody had set deliberately.

This is the investigation, the test design, the fix, and the safety procedure, written so you can check your own hardware in a few minutes.

<!-- excerpt-end -->

## Context: why a USB card carries storage here

The cluster is seven Dell OptiPlex 990 mini-towers running Proxmox and Ceph. Each node has a four-port USB3 PCIe card built on a Renesas uPD720201 controller (two brands across the fleet, one of which draws extra power from a SATA lead) and three 5 TB Seagate laptop-class SMR drives on it, each running as a Ceph OSD. Two nodes also hang a large ZFS backup drive off the same card. It is not a design I would recommend for production, but it is what the budget bought, and it makes the shared PCIe link between the card and the chipset the one component every OSD on a node depends on.

During a multi-week rebalance I measured about 150 MB/s of combined throughput from three drives that each read 125 to 140 MB/s on their own. That ratio is the clue: three independent devices that sum to far less than their parts are sharing a bottleneck.

## Step one: read the link, not the datasheet

PCIe link state is one command away:

```bash
lspci -s <card> -vv | grep -E "LnkCap:|LnkSta:"
LnkCap: Port #0, Speed 5GT/s, Width x1 ...
LnkSta: Speed 2.5GT/s (downgraded), Width x1
```

`LnkCap` is what the device can do; `LnkSta` is what it negotiated. The kernel even labels the gap: `(downgraded)`. A x1 Gen1 link carries 250 MB/s raw per direction, and after framing and xHCI overhead I measured about 160 MB/s of real throughput through it, which matched the drive-side measurement exactly.

Across the fleet, six of seven cards showed the downgrade. One card, on quell, ran at 5 GT/s. Same board, same controller chip.

## Step two: find out why one node was different

`dmidecode -t slot` plus `lspci -tv` map physical slots to chipset root ports. On this board the cards sat in one of two slots:

* **Slot 2**, a x4 electrical slot in an x16 connector, hangs off chipset root port 3 (`00:1c.2`).
* **Slot 4**, a x1 slot, hangs off root port 5 (`00:1c.4`).

Quell's card was in Slot 4. Reading the root ports themselves:

```bash
lspci -s 00:1c.2 -vv | grep -E "LnkCap:|LnkSta:|LnkCtl2:"
LnkCap:   Port #3, Speed 5GT/s, Width x1
LnkSta:   Speed 2.5GT/s, Width x1
LnkCtl2:  Target Link Speed: 2.5GT/s
```

Port 3 is *capable* of 5 GT/s, but its **Target Link Speed**, a field in the Link Control 2 register that the firmware initializes, was set to 2.5 GT/s. Port 5 on the same chipset had its target at 5 GT/s. The card was doing exactly what it was told: training to the target. This was a firmware default per port, not a hardware limitation of the card, the slot or the chipset.

## Step three: prove the shared link is the bottleneck, with controls

Before changing anything I wanted to rule out the alternatives, and I wanted a measurement I could trust. Two design points mattered:

1. **Use idle drives.** Production nodes were mid-backfill, so each drive read only 10 to 60 MB/s and their aggregate (93 to 151 MB/s) said more about contention than about the controller. I had exactly one node whose drives were idle: a newly added host whose OSDs sat at CRUSH weight zero and held no data. That is a clean instrument.
2. **Test alone, then together.** Using read-only direct I/O (`hdparm -t --direct`), each drive alone read 127 to 140 MB/s. All three together totalled 160 MB/s, 53 each. If the drives were the limit, adding drives would not reduce the per-drive figure. It did.

I also sampled per-core CPU during the parallel read (no core above 5%) and confirmed the drives negotiated SuperSpeed (5 Gb/s) to the card. Everything pointed at the one remaining shared element: the PCIe link.

## Step four: raise the target speed and retrain

The PCIe specification lets software raise a downstream port's target speed and ask the link to retrain. Two register writes do it:

```bash
setpci -s 00:1c.2 CAP_EXP+30.w=0002:000f   # Link Control 2: target = 5 GT/s (1=2.5, 2=5, 3=8)
setpci -s 00:1c.2 CAP_EXP+10.w=0020:0020   # Link Control: set Retrain Link
lspci -s 03:00.0 -vv | grep LnkSta:        # Speed 5GT/s, Width x1
```

The result on the idle node:

| Link | Each drive alone | Three at once | Per drive in parallel |
|---|---|---|---|
| 2.5 GT/s | 127-140 MB/s | 160 MB/s | 53 MB/s |
| 5 GT/s | 127-140 MB/s | 283 MB/s | 95 MB/s |

A 77% improvement in aggregate read throughput for two register writes. It is not the full 3 x 135 and I have not pinned down why: xHCI and bridge overhead are the likely candidates, and which USB storage driver each node uses is a separate question I take apart in a follow-up post. The honest caveat: this is a *read-path* gain. Sustained SMR writes run at 30 to 60 MB/s per drive, which is below either link's ceiling. The win is for recovery reads, erasure-coded reads and scrubs, which is where a rebalance spends a lot of its time.

## The safety problem: retraining resets the card

A retrain drops the link, so the card resets and every USB device behind it disconnects and reconnects. On storage, that is not a trivial side effect. On this cluster I had already been bitten once by USB re-enumeration leaving stale LVM device-mapper entries that made an OSD fail with `attempt to access beyond end of device`. The procedure that made it safe on jaeger, and which I scripted for the rest:

1. Pre-flight: all OSDs up, no undersized, degraded, inactive or peering PGs, `noout` set so stopping OSDs does not trigger rebalancing.
2. Stop the node's USB OSDs and **deactivate their LVM volume groups** so no device-mapper entry points at a device that is about to vanish.
3. Retrain, confirm 5 GT/s and that every drive came back.
4. Reactivate the volume groups, `ceph-volume lvm activate` each OSD, wait for all OSDs up and zero bad PGs on three consecutive checks.
5. Refuse to run at all if any USB disk behind the card is not a Ceph OSD (a mounted filesystem, a ZFS pool). Those need a manual quiesce: stop the consumers, export the pool, retrain, import.

One node at a time. The whole sequence is two to four minutes per node, with the node's PGs running on two copies for that time, which is exactly what `size=3` and `min_size=2` are for.

## Making it survive reboots

The firmware restores its default on every power-on, so a one-time `setpci` is not enough. A small systemd oneshot repeats the retrain at boot. Two details matter:

* **Ordering.** The unit must run before anything uses those drives, so it declares `Before=ceph-osd.target zfs-import-cache.service zfs-import-scan.service zfs-import.target` in addition to `sysinit.target`. I checked it with `systemd-analyze verify` for ordering cycles, because a cycle makes systemd silently drop a job.
* **Idempotence and safety.** The script exits 0 in every case so it can never block a boot, and does nothing when the link is already at the target.

I tested it the only honest way: a real reboot of the test node. The journal showed the BIOS default (`link now gen1 (2.5 GT/s), BIOS target gen1`), then `retrain ok, root port 00:1c.2 now gen2 after 100 ms`. All OSDs came up with no stale LVM, and the read test gave 284 and 282 MB/s.

## Not hard-coding the port

My first version named the root port. That is wrong for a fleet: the same card sat behind the same root port (`00:1c.2`) on six nodes but showed up as bus `03:00.0` on four of them and `02:00.0` on two, and sat behind a different port on the seventh. The final script discovers it:

1. Find every PCI device of class `0x0c0330` (xHCI USB3 controller).
2. Take its parent in sysfs; require a PCIe **Root Port** with only xHCI devices behind it, so no NIC or GPU shares the retrained link.
3. Read the maximum link speed of the port and the card, target the lower, capped at Gen2 (the only speed I have tested).
4. Skip if the link is already there.

A `--dry-run` flag prints what it found and what it would do. Running it across all seven nodes before touching any of them confirmed which five would change and which two (the node already at 5 GT/s and the test node) would not.

## How to check your own hardware

```bash
# any USB3 card or NVMe adapter: is the link below its capability?
for d in $(lspci | awk '/USB 3|xHCI|Non-Volatile/{print $1}'); do
  echo "== $d"; lspci -s $d -vv | grep -E "LnkCap:|LnkSta:"
done
# then the port above it: is the target speed below the port's capability?
lspci -s <root-port> -vv | grep -E "LnkCap:|LnkCtl2:"
```

If `LnkSta` is below `LnkCap` and the *root port's* `LnkCtl2` target is below its own `LnkCap`, you probably have this problem. Two caveats: a Gen1-only card or port cannot be raised, and not every slot on a board shares the same default. On this board simply moving the card from the long slot to the x1 slot gave 5 GT/s with no software at all.

## Later: the link speed was one of three faults

Raising the link fixed the shared bottleneck on every node. It did not stop the resets on the two nodes that kept logging them, and the explanation turned out to be hardware in two more places.

* **A bad card in jaeger.** The FebSmart card in jaeger, which takes no SATA power lead, was a faulty unit. Replacing it with a new SATA-powered card fixed some of the problems there, though not all of them. The model itself is not the issue: edgar and tanaka carry the same unpowered FebSmart and logged no resets on their OSD ports in the same week. [AUTHOR: add which problems the new card fixed and which remain, with reset counts before and after, and the swap date.]
* **A powered hub.** The Anker 7-port powered USB3 hub (12 V, 3000 mA) that I used to attach extra drives to jaeger and tanaka was conclusively causing some of the errors on both nodes. As of 2026-10-23 all 42 of tanaka's resets that week came from test drives behind its powered hub, and none from the OSD drives on the card's direct ports. [AUTHOR: confirm that tanaka's test hub is the Anker, and add how it was proven (hub removed, drives direct), the before and after counts, and the dates.]

A `(downgraded)` link, a bad card and an underpowered hub all produce the same symptom, USB resets under load, and each one hides the next. Change one thing, re-measure, then look again; a fix that improves the numbers is not proof that it was the only fault.

## What I would do differently

* **Measure the shared path before tuning the consumers.** I tuned reservation concurrency, mClock profiles and reweights first. Those mattered, but a link running at half speed was a standing tax under all of them.
* **Test on idle hardware.** The one node with idle drives gave a clean answer in minutes. The same test on busy nodes produced numbers that looked like a result and were not.
* **Treat any `(downgraded)` in `lspci` output as a finding.** It costs nothing to check and it is on every PCIe device.

Rollout status: proven and rebooted on the first node, then rolled out to the rest of the fleet the same day, one node at a time, each in two to four minutes with the cluster back to zero bad PGs before the next. The node with a ZFS backup pool on its USB card (28 TB, bind-mounted into two containers) needed its own variant that shuts down the containers and exports the pool first; the pool re-imported itself within seconds of the disk reappearing, which I had not planned for and which turned out to be harmless. All seven cards now report 5 GT/s. *[Add the before/after backfill rate over the following days here.]*

The scripts, the unit and the full procedure live in my infrastructure repo under `scripts/pcie-retrain-5gt.sh`, `scripts/pcie-retrain-5gt.service`, `scripts/pcie-retrain-rollout-node.sh` and `docs/usb/USB3-PCIE-LINK-SPEED.md`.
