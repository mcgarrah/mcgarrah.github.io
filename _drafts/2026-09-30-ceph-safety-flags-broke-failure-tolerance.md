---
layout: post
title: "The Safety Flags That Protected My Ceph Rebalance Also Broke Its Failure Tolerance"
image: /assets/images/og/ceph-safety-flags-broke-failure-tolerance.png
categories: [homelab, ceph, proxmox]
tags: [ceph, proxmox, osd, bluestore, rebalance, backfill, noout, homelab, dell-optiplex-990, troubleshooting]
excerpt: "A week-long Ceph rebalance on my 7-node Proxmox cluster went through a hidden CRUSH rule bug, a whack-a-mole reweighting marathon, and a wrongly-accused SSD -- then a routine maintenance reboot turned into a two-hour outage. The cause wasn't bad luck. It was the exact flags I'd set to protect the rebalance quietly disabling Ceph's ability to survive losing a node."
description: "A real-world Ceph incident walkthrough covering a replicated_rule device-class scoping bug exposed by adding an SSD tier, OSD reweight whack-a-mole during a multi-week rebalance, a backfill_toofull stale-reservation bug, a false-positive SSD diagnosis caused by write-cache-masked benchmarks, and a two-hour outage caused by noout/nobackfill disabling Ceph's normal single-host failure tolerance during planned maintenance. Includes the operational checklist for doing maintenance safely during an active rebalance."
date: 2026-09-30
last_modified_at: 2026-09-30
seo:
  type: BlogPosting
  date_published: 2026-09-30
  date_modified: 2026-09-30
---

Losing one node out of seven should not be able to touch a Ceph cluster running `size=3, min_size=2`. That's the entire point of the replication factor -- any single host can vanish and every PG still has two good copies to serve from. I know that. I've written about [rebalances](/ceph-rebalance/) and [nearfull warnings](/proxmox-ceph-nearfull/) and [overlapping ZFS/Ceph failures](/zfs-ceph-overlapping-failures/) on this same cluster before. So when a planned maintenance reboot on one node turned into two hours of degraded I/O, blocked client reads, and 80%+ iowait across the cluster's primary nodes, the interesting question wasn't "how do I fix this" -- it was "why did this even happen at all."

<!-- excerpt-end -->

The short version: it took a week of accumulated decisions, each individually reasonable, to build a cluster that could no longer tolerate the one failure mode it's explicitly designed around. This is the whole story, in order, because the ending only makes sense with the beginning attached.

## Act 1: the bug an SSD tier accidentally exposed

This started with something good -- adding a small accelerator SSD tier, one drive per host, six drives total, meant to eventually host CephFS metadata and speed up small-write workloads. Standard stuff: `ceph-volume lvm create` six times, a new `ssd` device class shows up in `ceph osd tree`, done.

Except creating that second device class did something I didn't expect: it exposed a bug that had been sitting invisible in the cluster's CRUSH map for its entire life. The main `replicated_rule` -- the one every pool had been using since day one -- was never actually scoped to `crush-device-class=hdd`. It didn't matter while every OSD in the cluster *was* an HDD; an unscoped rule and an HDD-scoped rule produce identical placement when there's only one device class to place onto. The moment a second class existed, that same unscoped rule became ambiguous, and Ceph's CRUSH computation reacted by recomputing placement across the whole cluster.

The fix was correct -- a real `replicated_hdd_rule`, all ten pools reassigned to it -- but the fix itself *is* a full CRUSH recompute. ~73% of all objects went misplaced at once. Not gradually. Immediately. What should have been "add six small SSDs, mostly a non-event" became a multi-week rebalance of nearly the entire cluster, sustained at roughly 360 objects/min -- a 21-22 day clearance estimate the first time I measured it.

## Act 2: the whack-a-mole week

A rebalance that size doesn't fail loudly. It fails as a slow drip of `nearfull` warnings that migrate from OSD to OSD as the fill distribution shifts:

- `osd.9` crossed nearfull first. Reweighted 0.95 → 0.65 → 0.50 as it kept climbing anyway.
- Relief there pushed the tightest-constraint title to `osd.12`. Reweighted 0.95 → 0.85 → 0.65.
- Then `osd.13`. Then, days later, `osd.6`, all the way down to 0.60.

Every one of these ran the same shape: check `ceph osd df`, find whichever OSD had drifted into the high-80s, reweight it down a notch, wait, repeat. It's a legitimate, working pattern -- reweight really does redirect future placement away from a hot OSD -- but it only moves the bottleneck sideways to whichever OSD is now second-tightest. On a cluster this size, "sideways" takes days to fully show up, so the whack-a-mole rhythm was genuinely the right response each time, just never a final one.

Along the way, a second, separate problem surfaced: PGs reporting `backfill_toofull` even when none of their acting-set OSDs were anywhere near the 90% `backfillfull_ratio`. First occurrence: 11 PGs stuck this way, every one of them sitting on OSDs in the 55-75% range -- nowhere close to full. This turned out to be a known, documented Ceph behavior ([tracker #39555](https://tracker.ceph.com/issues/39555)): a PG's too-full status gets cached at the moment a backfill reservation is granted and isn't re-checked "until a free backfill slot happens" -- so an OSD that *was* tight for a moment can leave a PG permanently flagged too-full long after the real numbers recovered. The fix is mechanical: restart the OSD daemons in the stuck PG's acting set, forcing a fresh reservation check. Applied it twice over the week; cleared cleanly both times.

None of this is exotic. It's the normal texture of running a big rebalance on modest hardware -- tedious, explainable, each step individually boring. Worth a mention only because it set the stage: by the time Act 3 happened, the cluster had been living in a degraded, actively-remapping state for roughly a week straight, with somewhere between 40-55% of all objects misplaced at any given moment.

## Act 3: the wrongly-accused SSD

Midway through the week I got a confident, specific report: the SSD serving as both OSD data and DB/WAL accelerator on one particular node was "more than 10 times slower than peer devices" and dragging down overall cluster performance. Named node, named device.

I ran `ceph tell osd.<id> bench` on it and five peers. The named device benched *completely normally* -- 264 MB/s, right in line with its siblings. A different device, on a different node entirely, benched at 36 MB/s: a real, reproducible 7x deficit, but the wrong culprit.

Rather than stop there, I cross-checked an internal planning doc I'd written earlier in the week -- and found the *original* accused node really had benched badly, four days earlier, with a fully root-caused explanation: a raw `dd` write directly to the physical device, bypassing Ceph, BlueStore, and the filesystem entirely, had reproduced the same ~32 MB/s ceiling. Healthy reads (241 MB/s), crippled sustained writes -- a real, physical fault on a 4-year-old drive, already decided for replacement, replacement already on the shelf.

So which was it? Both, as it turned out -- and the disagreement between "clean today" and "broken four days ago" was itself the real finding. `ceph tell osd bench`'s default test writes 1GB in about 4 seconds. That fits entirely inside the write cache most consumer SATA SSDs carry, and never touches the real sustained-write ceiling underneath it. I re-ran the same raw, direct-I/O `dd` test used four days earlier -- this time a longer 4GB write, enough to exhaust any write cache -- against *all six* accelerator SSDs in the fleet:

| Node | Model | Sustained 4GB direct write |
|---|---|---:|
| harlan | Crucial MX500 | 243 MB/s |
| kovacs | Crucial MX500 | 233 MB/s |
| poe | Crucial MX300 | 192 MB/s |
| tanaka | ORICO | 218 MB/s |
| edgar | Samsung MZ7LN512HMJP | **33.7 MB/s** |
| quell | Timetec 512GB | **35.4 MB/s** |

Two drives, not one, genuinely broken -- both at roughly 1/6th to 1/7th the healthy band -- while four drives clustered tightly in a real, consistent range. Not a design flaw in the accelerator-SSD approach itself, just two specific bad units the short benchmark had been giving a false pass. The methodology lesson stuck: a 1GB cache-friendly write is not a valid test for this failure mode, and I won't trust that quick bench again without a longer direct-I/O follow-up.

Both drives, as it happens, also double as the `block.db`/`block.wal` device for three HDD OSDs apiece on their respective hosts -- the same physical device serving four roles at once. A cheap or failing accelerator SSD in this layout doesn't just hurt its own tier; it drags on every HDD OSD sharing the volume group with it.

## Act 4: the night one node took the cluster down

With two replacement SSDs identified and one already in hand, the next step was physical: pull one node, swap hardware, put it back. Routine. I'd done the equivalent on other nodes earlier in this same project without incident.

This time, thirty-plus minutes after the node went offline for what was meant to be a short maintenance window, the whole cluster was in trouble. `ceph health detail` showed a real mess: a monitor out of quorum, four OSDs down, 21 PGs fully **inactive** -- not degraded, *inactive*, meaning client I/O to those specific PGs was outright blocked -- 372 PGs degraded, 442 undersized, and iowait pinned above 80% on the Ceph primary nodes. The single-host outage I'd budgeted as "a brief, boring blip" was two hours and ten minutes long by the corosync log, and for the entire span, those 21 PGs simply sat there, unavailable.

That's not what a healthy Ceph cluster is supposed to do when it loses one host. So I went looking for the actual mechanism, not just the symptom, and ruled things out one at a time with real evidence rather than assumption:

- **Proxmox cluster quorum**: never at risk. Corosync logged a clean departure ("shut down by sysadmin"), 6 of 7 nodes remained, comfortably above the majority threshold the whole time.
- **HA manager**: `pve-ha-lrm`/`pve-ha-crm` logs showed zero entries for the entire window. No fencing, no forced migration, no compounding load from HA reacting to the loss.
- **CephFS/MDS**: the active metadata server lived on a *different* node the entire time. A cluster-wide CephFS stall from MDS failover -- which genuinely can freeze every client at once -- simply didn't happen here.

What was left, once those were eliminated, pointed at two things I'd set up myself, days earlier, for a completely different reason:

**`noout` and `nobackfill` had been standing cluster flags since the very start of the rebalance**, set to stop Ceph from doing expensive, wasteful work reacting to the constant OSD churn during the CRUSH-rule fix. That made sense at the time. What I hadn't fully internalized: those same two flags are the exact mechanism that lets a healthy Ceph cluster shrug off a single lost host in the first place.

Here's the normal path, the one I'd been relying on without thinking about it: a host goes down, and after `mon_osd_down_out_interval` (600 seconds, 10 minutes by default), Ceph marks its OSDs `out` and starts recruiting *replacement* OSDs on other hosts to backfill the missing replicas. The lost host stops mattering within 10-20 minutes because the data simply grows a new home elsewhere.

`noout` disables the first half of that -- OSDs never get marked `out`, no matter how long they're down, so Ceph never goes looking for a replacement. `nobackfill` disables the second half -- even if it wanted to recruit a replacement, it's blocked from actually moving data there. With both set, a lost host doesn't get routed around. The cluster just sits, waiting specifically for that host to come back, for however long that takes.

Combine that with the cluster's state going into the outage -- a week deep into an active rebalance, with a meaningful fraction of PGs already running thinner-than-normal acting sets mid-remap -- and the 21 inactive PGs make complete sense: those particular PGs had *already* dropped to a reduced number of real copies because of the in-flight rebalance, and losing one more copy to the offline host put them below `min_size`. In a fully healthy, steady-state cluster, this same single-host loss would have been a non-event -- every PG still has two full copies, nothing goes inactive, nothing needs a human. It was the *combination* -- mid-rebalance thin acting sets, plus flags that specifically disable the self-healing that would otherwise route around the gap -- that turned a routine maintenance window into a two-hour outage.

## What I'm actually changing

The uncomfortable part of this isn't that something broke. It's that the flags directly responsible were ones I'd set deliberately, for a good reason, and never revisited the tradeoff. `noout`/`nobackfill` protecting a rebalance from unnecessary churn is genuinely correct *while every host stays up*. The moment a host goes down on purpose, those same flags stop being a courtesy to the rebalance and start being a liability to availability.

So, the actual operational lesson, the one worth carrying into every future maintenance window on this cluster:

**Before taking any node down intentionally while `noout`/`nobackfill` are set for an active rebalance:**

1. Check `ceph -s` for the current misplaced/degraded picture first -- know whether PGs are already running thin before you take anything else away.
2. `ceph osd unset nobackfill` (and consider `noout` too) *immediately before* the planned outage, not after something goes wrong. Let Ceph's normal 10-minute auto-heal path do its job for the duration of the maintenance.
3. Accept that this means real backfill I/O will happen during the outage -- that's the intended trade, since the alternative is PGs sitting inactive for the full outage window instead of a normal recovery.
4. Once the node is back and confirmed stable, re-set the flags if the rebalance is still ongoing and still needs the protection.
5. If the rebalance is deep and volatile enough that even a normal 10-minute auto-heal cycle feels risky, that's a signal to wait for a calmer point in the rebalance before scheduling non-urgent maintenance at all -- not a reason to lean harder on flags that trade availability for convenience.

None of this is a Ceph bug. It behaved exactly as configured, on both sides of the story -- exactly as the original mitigation intended, and exactly as the flags' documented behavior says they would under a host loss. The gap was mine: treating a week-old safety decision as permanent background state instead of something to actively reconsider every time the situation around it changed. A cluster mid-rebalance and a cluster at rest are not the same cluster for the purposes of deciding which flags are safe to leave on, and I'm building that check into the actual maintenance runbook now instead of relying on remembering it at 3am.
