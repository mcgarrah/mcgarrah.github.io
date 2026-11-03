---
layout: post
title: "Business Law, Ceph Repairs, and the Proxmox 9 Upgrade That Keeps Waiting"
categories: [homelab, personal, proxmox]
tags: [emba, business-law, ceph, proxmox, proxmox-9, homelab, writing, planning, time-management]
excerpt: "A Business Law course for my Executive MBA is now eating most of my free time. Meanwhile the Ceph cluster keeps teaching me things, the Proxmox 9 upgrade is fully planned and still not started, and I have been writing articles in batches whenever a gap opens. Here is where everything stands, and what the next few months of articles look like."
description: "A status update on balancing an Executive MBA Business Law course with a seven-node Proxmox and Ceph homelab: what has been fixed on the Ceph cluster since September, why the Proxmox 8 to 9 upgrade is planned but not yet executed, and the batch-writing approach behind the upcoming article queue."
date: 2026-11-03
last_modified_at: 2026-11-03
seo:
  type: BlogPosting
  date_published: 2026-11-03
  date_modified: 2026-11-03
---

If you have noticed the gap between posts here, this is the explanation. I started a Business Law course for my Executive MBA, and it is taking a large share of the free time that used to go to the homelab and to writing.

The lab did not stop. It just moved to the background. Ceph problems keep surfacing, the Proxmox 9 upgrade is waiting for a window, and I have been writing articles in batches whenever I find a free evening. This post is a status report on all three, and a preview of what is queued.

<!-- excerpt-end -->

## Where the time is going

I am working through an [Executive MBA](/about/) alongside a full-time engineering job. A law course is a different kind of load from the technical classes. It is dense reading, careful vocabulary, and cases where the exact wording of a sentence decides the outcome. That is not far from reading a Ceph log or a Terraform plan, but it does not fit into the odd twenty-minute gaps the way a quick `ceph -s` check does.

<!-- REVIEW: add one or two sentences on what the course covers and what has surprised you so far, if you want it in the article. I did not invent any course details. -->

The practical effect is simple. Long, uninterrupted homelab sessions are rare right now. Anything I do on the cluster has to be small, reversible, and written down as I go, because I may not get back to it for several days. That constraint turns out to match what the cluster needs anyway, as the next section shows.

## What the Ceph cluster has been teaching me

Since September I have been fixing Ceph problems in the background, mostly one at a time and mostly because something broke or alerted. The cluster is now seven Proxmox nodes: six hosting OSDs, plus `jaeger`, the newest and still the odd one out.

The short version of the fall:

- **A power outage exposed a 100Mb network bottleneck.** Three of five storage nodes had their Ceph network running at 100Mb/s instead of gigabit. The fix was quick. The follow-up, a hardware upgrade plan, was not.
- **Every OSD now has its database on SSD.** A recurring stalled-read alert sent me back to a problem I had written off in April. A tool I did not know about, `ceph-volume lvm migrate`, made an in-place conversion practical. All eighteen original OSDs now have right-sized combined WAL and DB volumes.
- **My own safety flags caused a two-hour outage.** I had set `noout` and `nobackfill` to protect a long rebalance. When I took a node down for planned maintenance with those flags still set, the cluster lost the ability to heal around the missing host. Nothing was broken in Ceph. I had treated a week-old decision as permanent.
- **Six monitors were calling an election every 45 minutes or so.** After reading all six monitor logs side by side, the elections lined up with RocksDB compactions. One setting, `mon_compact_on_trim`, gave me 34 hours without a single election. On 2026-10-14 I also cut the layout from six monitors to five, because an even monitor count buys no extra fault tolerance and adds elections.
- **There is now a fast pool.** As of 2026-11-02 a replicated SSD pool, `cephrbd-ssd`, exists, and the first containers (InfluxDB, Grafana, and UrBackup's root disk) have moved onto it.

None of this was on a schedule. Each item started as an alert or an annoyance and became a small project. That is the real pattern of a homelab: the plan says one thing, and the cluster decides the order.

## The Proxmox 9 upgrade: planned, prepared, not started

The Proxmox VE 8 to 9 upgrade is the project everything else keeps getting in front of. The plan is long, and a lot of it is already done:

- **Pre-flight is complete.** I fixed a dead Ceph repository on two nodes, removed a kernel pin that turned out to be a deliberate setting rather than a leftover, cleaned out an unneeded boot package, updated the guest containers, and ran `pve8to9 --full` three times to confirm a clean baseline.
- **The safety nets exist.** A Proxmox Backup Server container holds a full backup of the HA-managed containers, and the CephFS and Ceph metadata backups are copied off the cluster they protect.
- **Ceph is already on Squid.** The Reef to Squid upgrade ran on 2026-08-12. Every daemon is on 19.2.5, and I did it first on purpose, because Proxmox 9 requires it.

What has not happened is the OS upgrade itself, Phases B and C of the plan. Two things hold it back.

The first is physical presence. None of these OptiPlex nodes has out-of-band management. If a node does not come back from the reboot into Debian Trixie, the recovery path is me standing in front of it with a Clonezilla disk. I will not start that sequence remotely or in a hurry.

The second is that the plan keeps being corrected by reality. The canary node was originally `tanaka` because it hosted no OSDs. Then it gained OSDs. I switched the canary to `jaeger`, which had no Ceph daemons at all. Then `jaeger` gained OSDs too, and HA moved three containers onto it. A canary that is no longer isolated is still useful, but the safeguards have to change: wait for clean cluster state, check for at-risk placement groups, set `noout`, migrate the guests off first.

The lesson from the safety-flag outage applies directly here. An upgrade plan written in August is a record of what I knew in August. Before each phase I need to re-read it against the live cluster instead of trusting it.

## Writing in batches

I have not stopped writing. I have changed how. Instead of finishing one article per week, I write in bursts when a gap opens, and push each draft to the repository as soon as it is readable. They sit unpublished until I can review them properly.

That has a side effect I did not plan for. The draft folder is now a fairly honest record of what I have actually been doing, not what I intended to do. Right now it holds articles on:

- the Ceph network bottleneck and the node upgrade it triggered
- the in-place WAL/DB migration
- the safety flags and the outage they caused
- the monitor election storm and the setting that stopped it
- a diagnostic tooling baseline across all the nodes, including a bug in my own detection script that hid a real gap
- a GPU upgrade decision, and why the cheapest VRAM per dollar was a card I rejected
- session persistence for AI coding CLIs running in a container on the cluster
- the Proxmox 8 to 9 series, which only has real material through the preparation stage

The Proxmox 9 series is the awkward one. Parts one to four describe work I have finished. Part five describes the OS upgrade, which I have not run. I would rather hold part five than publish an account of something I have not done.

## What comes next

In rough order, and subject to what the cluster and my coursework allow:

1. **Publish the Ceph articles first.** They are written, they stand on their own, and they cover things I wish I had read before hitting them.
2. **Finish the CephFS erasure-coding migration.** The runbook is written. The fast SSD pool and the rest of the rebalance have to settle first.
3. **Run the Proxmox 9 canary on `jaeger`.** This needs a weekend with me physically in the room.
4. **Then Phase C, one node at a time,** with `edgar` last because of its USB-backed OSDs.
5. **Write the series conclusion after the upgrade, not before.**

The course will not leave much room for any of this for a while. I would rather publish fewer, correct posts than keep a schedule I cannot honestly meet.

## Related Posts

- [Proxmox and Ceph Homelab Guide](/proxmox-ceph-guide/) lists every Proxmox and Ceph article on the site.
