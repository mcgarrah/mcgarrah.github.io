---
layout: post
title: "Thirty-Three Ceph Mon Elections a Day, and the One Setting That Stopped Them"
categories: [homelab, ceph, proxmox]
tags: [ceph, proxmox, monitor, paxos, rocksdb, election, mon-compact-on-trim, homelab, dell-optiplex-990, troubleshooting]
excerpt: "My 6-mon Ceph quorum was calling a new election about every 45 minutes. I chased the network, a slow leader disk, and one 'bad' peon before reading all six mon logs side by side and finding the pattern: elections started seconds after a rocksdb compaction. One config flag later the cluster went 34 hours without one. Whether that flag would help yours is a different question, and I'll be honest about why it might not."
description: "A Ceph mon election storm on a 7-node Proxmox homelab cluster: how it was measured across all six mon logs, which theories were tested and discarded (network, leader disk, one slow peon), the evidence that pointed at mon_compact_on_trim, the fix, and a careful discussion of why this is probably specific to a compromised homelab setup rather than a general Ceph problem."
date: 2026-10-09
last_modified_at: 2026-10-09
seo:
  type: BlogPosting
  date_published: 2026-10-09
  date_modified: 2026-10-09
---

A Ceph monitor election is supposed to be a rare event. A mon restarts, a node reboots, a network link flaps, and the quorum re-forms in a second or two. Nobody notices. On my cluster it was happening about **33 times a day**, and every one of them was a few seconds where the cluster had no quorum and clients stalled.

This is how I found it, what I got wrong along the way, the single setting that stopped it, and why I think the fix is as much a statement about my hardware as it is about Ceph.

<!-- excerpt-end -->

## The setup, because it matters later

The cluster is seven Dell OptiPlex-class machines running Proxmox with Ceph Squid (19.2.5), `size=3, min_size=2`. It is a homelab built from what I had, and it shows:

- Six of the seven nodes run a mon and a mgr, and most also run OSDs. Six mons is an even number, which is not what anyone recommends; it happened by accident as nodes were added.
- Every mon store lives on the node's root filesystem. On two of the original nodes (poe and kovacs) that is a ZFS mirror of 160 GB 7200 rpm desktop hard drives that are older than some of the people who use the cluster. On the newer nodes it is a small SATA SSD.
- The OSDs are mostly 5 TB SMR USB laptop drives with a SATA SSD per node for the DB/WAL.
- The "cluster network" is a separate gigabit switch, but the mons talk on the main LAN, which also carries everything else in the house.
- For the last several weeks the whole thing has been in the middle of a rebalance that moved 40 to 70 percent of the data after I [accidentally rewrote every placement rule](/ceph-safety-flags-broke-failure-tolerance/). The `noout`, `noscrub` and `nodeep-scrub` flags have been set the whole time.

That is a lot of unusual at once. Keep it in mind.

## Noticing

I did not find this by looking for it. I was chasing a different problem (an unexpected hard reset of a node) and noticed in the cluster log that the quorum had re-elected eleven times between 01:29 and 13:33 that day. In every episode the same line showed up first:

```
mon.edgar@4(peon).paxos(paxos active c ...) lease_timeout -- calling new election
```

`mon.edgar`, a peon, was the first to give up on the leader's lease. `mon.poe` and `mon.kovacs` never were. It looked like a clean lead: one peon with a problem.

## Theory 1: the leader's disk (wrong)

The leader was `mon.poe`, which sits on one of those ancient mirrored hard drives. The theory wrote itself: poe stalls on a slow disk, fails to renew the lease on time, a peon notices, election.

So I tested it. I changed the election strategy to `disallow` and forbade poe, kovacs and quell from being leader, which pinned leadership to harlan. This is a cheap, fully reversible experiment.

It made no difference. Elections kept coming. I reversed the change a couple of hours later and put the config back exactly as it was. The leader's disk was not the (whole) story.

## Theory 2: the network (wrong)

If one peon keeps missing leases, maybe its path to the leader is flaky. I ran 200 pings from two other nodes to edgar: 0% loss, 0.23 ms average. Link negotiated at 1000/Full, no NIC errors. I also had Proxmox's corosync logs, which run on a separate path from Ceph, and they showed no link drops in the same windows. I did find some pause-frame bursts and receive-miss counters on the cluster network cards, which were worth chasing for other reasons, but they never lined up with the elections.

## The thing that cracked it: read all six logs at once

My early mistake was looking at one mon's log and believing the node that complained first. The data got much clearer when I pulled the election lines from **all six** mon logs for the whole retained window (September 28 to October 5, 262 distinct episodes) and lined them up by timestamp.

Three facts fell out:

1. **Every peon times out together.** The median spread between the first and last peon calling the election was **0.4 seconds**. Edgar was only "first" by a few hundred milliseconds, and it was first about as often as anyone else. There was no sick peon.
2. **The state was always the same.** Each time, the peons logged `paxos(paxos updating ...)`. In Ceph's mon Paxos, a peon in `updating` is waiting for the leader to finish a commit; the lease cannot be renewed until every peon has acknowledged it. If any step stalls, all peons hit `lease_timeout` together.
3. **Something was stalling the commit.** So I went looking for what the mons were doing right before each election and found rocksdb compaction events in the mon logs. Counting them:

   - **52% of elections began 10 to 15 seconds after a compaction burst** in the mon's store.
   - If compactions and elections were unrelated, the same window would catch about **3.5%** by chance.

That is not subtle. Elections were following compactions at roughly fifteen times the chance rate.

## What the setting does

By default, Ceph mons compact their rocksdb store every time they trim old Paxos versions (`mon_compact_on_trim`, default `true`). Trimming happens constantly while the cluster is changing state, because every change to the OSD map or PG state is a Paxos commit. Compaction is a burst of disk reads and writes. On a mon with a fast dedicated disk it should be invisible. On a mon whose disk is busy, or slow, the burst can delay the next Paxos commit long enough to miss the lease deadline.

The fix is one line, and it is live and reversible:

```bash
ceph config set mon mon_compact_on_trim false
ceph config get mon mon_compact_on_trim     # false
# undo:
ceph config rm mon mon_compact_on_trim
```

The trade-off is that the mon's store is no longer compacted at every trim, so it grows. Mine went from about 27 MB to about 33 MB over three days. If it ever gets large you can compact one mon at a time with `ceph tell mon.<name> compact`.

## The result

I applied it at 22:18 on October 5. The numbers, from the mon logs and the election epoch:

| Period | Elections |
|---|---|
| Before (Sept 28 to Oct 5) | about 33 a day |
| First 17 hours after | 2 unexplained episodes (02:33, and 11:25), plus one at 11:06 minutes before a planned reboot of a node |
| Following ~34 hours (Oct 7 12:00 to Oct 8 22:15) | **0** |

That last window includes no planned maintenance. The election epoch sat at 1290984 and the quorum age kept counting up to two days. At the old rate I would have seen about 47.

The elections in the first window that I could explain were my own: I rebooted a node, and power-cycled another for an SSD swap. Taking a mon away and bringing it back always causes an election, and that is correct behavior, not this problem.

## Is this a Ceph problem? Probably not

This is the part I most want to be careful about. I fixed my cluster. I did **not** find a bug in Ceph, and I would not tell anyone to copy that setting because I did.

`mon_compact_on_trim=true` is the default for good reason, and on normal hardware it does its job quietly. If you run mons on dedicated SSDs, or at least on a disk that is not also doing everything else, you will probably never see this. Several things about my setup could each make a compaction burst long enough to matter:

- **Slow, shared mon storage.** The mon store is on the root filesystem. On two nodes that is a mirrored pair of 2000s-era desktop HDDs also serving the OS, logs and ZFS. A compaction competes with all of it.
- **Weeks of rebalance.** I had been in a rebalance of tens of percent of the data for weeks, with repeated reweights. Every reweight and every PG state change is another Paxos commit and more trimming. A quiet cluster commits rarely and trims rarely; mine was doing it constantly, so compactions were frequent.
- **A busy host.** The mons share machines with OSDs, with USB SMR drives that stall the whole box under load, and with Proxmox itself. I/O contention on a small machine is the norm here.
- **An even mon count.** I have six mons, not five or seven. That alone does not cause lease timeouts, but a quorum of four out of six is less forgiving than three of five.
- **A shared LAN.** The mons are on the same network as everything else in the house.

Here is the uncomfortable bit: I have not proven which of these matters. The leader-pinning test says the leader's disk alone is not the issue, and edgar (which has an SSD, not an old HDD) was as likely as anyone to be first to time out. So "old hard drives" is not an obvious answer. My best guess is a combination: a constantly busy cluster that makes frequent compactions, on small machines where any I/O burst is felt everywhere. That is a guess.

## What I did not do, and what would prove it

I never ran the controlled test. The honest experiment is to revert the setting for a day and see if the elections come back. I chose not to, because a production-ish cluster in the middle of a rebalance is not where I want to deliberately re-break something, and because the improvement was large and sudden. But a skeptical reader is entitled to point out that the cluster's behavior also changed for other reasons in those days (the rebalance slowed, I fixed a gigabit link that had been stuck at 100 Mb/s, I moved some data to faster SSDs). None of those look like explanations to me, since the compaction timing correlation was measured before any of them. Still: one cluster, no revert test.

If you want to know whether this applies to you, the questions I would ask are:

1. Do your elections follow the pattern above: **all** peons timing out together in `paxos updating`, and not one sick node?
2. Does `grep -i compact` in the mon logs line up in time with the elections (within 10 to 15 seconds)? Count it against the chance rate.
3. While a compaction runs, what does `iostat -x` say about the device holding `/var/lib/ceph/mon`? If it is saturated or latency spikes into hundreds of milliseconds, you have your answer, and the real fix is faster or dedicated mon storage.

## What I would do differently

- **Look at all the logs at once from the start.** Following the first node to complain cost me a day. The pattern was only visible across all six.
- **Compare against chance.** "These elections follow compactions" is weak by itself. "52% versus 3.5%" is evidence.
- **Make every experiment reversible and write down the revert command first.** Both the leadership pin and the config flag could be undone in one line, which is why I was willing to try them on a cluster I care about.
- **Treat a cluster-wide config setting as something that needs a note.** `mon_compact_on_trim` lives in Ceph's config database, not in a file. Nothing will remind a future me that it is there. It is documented in the repo now, with a note to re-apply it if the mons are ever rebuilt.

Long term the real fix is boring: put the mon stores on dedicated SSDs and stop running a six-mon quorum. In the meantime, one flag bought me a quiet cluster.

*Related: [The Safety Flags That Protected My Ceph Rebalance Also Broke Its Failure Tolerance](/ceph-safety-flags-broke-failure-tolerance/).*
