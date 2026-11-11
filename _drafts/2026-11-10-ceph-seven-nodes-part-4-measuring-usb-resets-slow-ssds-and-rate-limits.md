---
layout: post
title: "Seven Ceph Nodes, Part 4: Measuring USB Resets, a Slow SSD and a Rate Limit"
categories: [homelab, ceph, proxmox]
tags: [ceph, erasure-coding, usb-storage, bluestore, ssd, benchmarking, fio, observability, runbooks, dell-optiplex-990]
excerpt: "Part 4. The erasure-coding rewrite ran at a safe 8 MB/s, one node kept resetting its USB drives, and one SSD made five OSDs slow. I stopped guessing and set up controlled measurements: a rate ladder with written pass criteria, a fio acceptance harness for DB/WAL SSDs, and a hardware trial with a spare USB3 card. This is what each one found, including where my own tooling was wrong."
description: "How to raise the rate of a live CephFS erasure-coding rewrite in controlled steps, why a sampled verification mode with a checksum manifest halves the read load, how to isolate which USB3 controller or cable is resetting OSD drives by comparing identical drives across nodes, and how to acceptance-test a BlueStore DB/WAL SSD with fio before it goes into a production host. Measured numbers, the benchmark that tripped my own watchdog, and the safety bug I found in my own test script."
date: 2026-11-10
last_modified_at: 2026-11-10
seo:
  type: BlogPosting
  date_published: 2026-11-10
  date_modified: 2026-11-10
series: "Seven Ceph Nodes"
series_part: 4
---

[Part 2](/ceph-seven-nodes-part-2-moving-live-media-to-erasure-coding/) ended with the media library moving to a `k=4, m=2` pool at a deliberately cautious 8 MB/s, and with one node whose USB drives would not stop resetting. Four days later the rewrite of the movie library was still about two weeks from done, the same node had logged 35 resets, and one SSD was making five OSDs slower than the other twenty-seven. Each of those problems invites a guess. I had a guess for each, and every one of them would have cost real hardware money to test by trial and error.

<!-- excerpt-end -->

So this post is about method. I set the acceptance criteria before collecting data, changed one variable at a time, kept a rollback for each change, and wrote down what would count as a failure. Some of it worked. Some of it caught my own tools doing the wrong thing.

I did this work with an AI agent doing the hands-on typing under my direction, and I made the decisions. The numbers below come from the cluster's own logs and from test runs I kept.

## Raising the rate without finding the limit by accident

The rewrite tool copies each file into the erasure-coded pool at a capped rate, then reads it back and compares SHA-256 hashes before replacing the original. The two caps apply one after the other, so with both at 8 MB/s the overall speed is half of that. The measured figure was 3.9 MB/s (324 GB in 23.1 hours).

That is the first thing worth saying plainly: **a rate cap is not a throughput number.** Doubling the cap doubles the write load on the drives only while the job is writing. It is a duty-cycle question, not a bandwidth one.

### Cutting the read-back, and being honest about what it costs

Full read-back is the expensive half. I built a sampled mode: files up to 128 MiB are still read back in full; larger files get their first block, last block and a handful of random 8 MiB blocks, with the block hashes taken from the source while copying. On the real file trees that reads back 3.9% of the movie library's bytes and 8.8% of the TV library's.

The trade is explicit. Corruption inside an unsampled region of a big file is not caught at copy time, and the original is replaced at the rename. So every replaced file also gets its full SHA-256 recorded in a manifest, and a separate pass can re-read everything later at a rate I choose. I tested both sides: a deliberate corruption in a sampled block is rejected and the original is untouched; one in an unsampled block passes the copy and is then found by the manifest pass. That second result is the gap, written down and demonstrated, not discovered later.

### The ladder

With sampled verify, the average write load becomes roughly the cap, so switching modes was itself a step up from about 4 to about 8 MB/s. I then defined a ladder with increments of no more than 4 MB/s, and 2 MB/s above 16, capped at 24. Each step runs six hours and has gates written in advance:

| Gate | Fail when |
|---|---|
| Other nodes | any new USB reset outside the one known node |
| Known node | more than 2 reset events during the step |
| Latency | the median BlueStore latency over three snapshots is above 1.5 times baseline |
| Alerts | slow-operation alerts average above 10 |
| Throughput | below 60% of the cap |

Step 1 (sampled verify at 8 MB/s) passed: 156 GB in six hours, 7.2 MB/s, 90% of the cap, two reset events on the known node. The first latency snapshot looked like a failure, a write median of 475 ms against a 272 ms baseline. Two re-samples a minute apart gave 219 and 344 ms. Thirty-second windows are noisy, so the gate now uses the median of three.

Step 2 (12 MB/s) failed. The known node logged three events in five hours, the last two thirty-five minutes apart, and the watchdog trips at three in an hour. I wrote the cap back to 8 and waited twelve hours as the plan said. The retry at 10 MB/s is running now.

## The benchmark that tripped my own watchdog

The job's watchdog stops it if more than ten OSDs report slow BlueStore operations. During the hold I ran `ceph tell osd.N bench` on a few OSDs to compare SSDs. The bench itself raised slow-operation alerts, which sit in the health output for a day. The count went from 6 to 10 and then to 11, and the watchdog stopped the job. It cost 74 minutes.

The lesson is not subtle: **a diagnostic that perturbs the thing a safety control watches has to pause that control first.** I now stop the job at a file boundary, or pause the process, before any step that can touch the watchdog's inputs.

The same pattern showed up with a planned reboot. Shutting down a non-voting node causes a corosync link-down, which also trips the watchdog. Pausing the job process with a stop signal for the three minutes the check looks back is cleaner than stopping it, and nothing is lost. That node powered itself back on 70 seconds after a clean shutdown, because its network card had wake-on-LAN set to magic-packet wake and something sent one. Disabling it with `ethtool -s lan0 wol d` before the next shutdown fixed it. I never found the sender.

## One node, thirty-five resets, and the evidence for where the fault is

Tanaka's three OSD drives logged 35 USB resets between the October 26 boot and November 9. Every one is a read command aborted by the UAS driver followed by a successful device reset. There were no I/O errors, no PCIe errors, and the link was at 5 GT/s.

The shape of the data matters more than the count:

- **Before and after.** Three resets in the nine days before the migration began; thirty-two in the next five and a half. The rise starts the day the erasure-coding writes did.
- **Same drives, same bridge, same load, different result.** Edgar and quell use the same drive model (ST5000LM000-2U8170) behind the same `0bc2:2344` bridge. Since their boots, two and four weeks ago, they have logged none. The drives and the bridges are not the cause.
- **A timing correlation that does not hold up.** Telegraf polls SMART on every drive about every four minutes. All five resets on one drive followed that drive's own `smartctl` call within 18 to 99 seconds, which has about a 3% chance by luck. The other two drives showed nothing. I wrote it down as a weak lead and did not act on it.
- **Power.** Tanaka's card has no auxiliary power lead. Harlan, kovacs and poe have one and show no resets, but edgar has none and shows none either, so power alone does not explain it.

The fault is local to tanaka: its card, slot, cables or power supply. The cheapest discriminating test is a spare card of the same family with its SATA power lead connected, in the same slot, under the same load, with the pass condition written down first: zero or one events in 24 hours and at most two in 48, against two to four a day before.

<!-- RESULT PENDING: card trial started 2026-11-10 18:26 EST. Fill in the 24 and 48 hour reads here (events per drive), and whether the cause was the card, the power lead, or neither. -->

## Measuring the right number on a slow SSD

Poe's SSD (a Crucial MX300) holds the DB/WAL for four HDD OSDs and the data for one SSD OSD. I had one number that made it look slow: a flush await of 3.5 ms against 0.3 to 0.7 ms on the other nodes. Under load, the usual BlueStore latency counters turned out to be useless for comparing hosts: `kv_sync_lat` and `kv_flush_lat` ran 25 to 90 ms on every node while the rewrite was running. The counter that separated poe from the rest was `bs.kv_commit_lat`, the time of the commit itself.

| OSD group | `bs.kv_commit_lat` |
|---|---:|
| poe, DB/WAL on the MX300 (osd.12, 13, 14, 26) | 8.5 to 9.4 ms |
| poe, SSD OSD (osd.22) | 8.1 ms |
| tanaka (ORICO SSD) | 1.4 ms |
| harlan | 1.5 ms |
| quell (ORICO SSD) | 1.7 ms |

A `ceph tell osd.N bench` of 3,000 MiB showed a second, separate effect: one run on poe's SSD OSD gave 251 MB/s, in line with the other nodes, and a second run a minute and a half later gave 43 MB/s. A burst fits the fast region of a consumer SSD; a sustained load does not.

### An acceptance harness, not a benchmark

I had two candidate drives and a budget that rules out the good ones (a 500 GB MX500 was about $250 against $120 for a 1 TB ORICO). Rather than trust a spec sheet I wrote a destructive `fio` harness that runs on a test node only. It refuses to touch any disk unless its serial matches, and runs these phases on a freshly trimmed drive and again after a twenty-minute fill:

1. 4 KiB writes with `fdatasync`, with the write cache on, then off with O_SYNC.
2. Four concurrent writers on four 50 GiB regions, mimicking four DB/WAL volumes.
3. The same plus compaction-style bursts and a random read/write job like the SSD OSD's.
4. A sustained 1 MiB write to find where the fast region ends.

The pass criteria were fixed before the first run. Two drives, same harness:

| | Timetec 512 GB (spare) | KingSpec P3-512 ($80, bought) |
|---|---:|---:|
| 4 KiB `fdatasync`, fresh | 0.45 ms | 2.74 ms |
| Four WAL writers, fresh | 0.57 ms | 5.9 to 6.3 ms |
| Full mix, filled drive | 1.17 ms mean, worst 0.46 s | 10 ms mean, worst 2.18 s |
| Sustained write after the fast region | about 45 MB/s | 22 to 27 MB/s |

The KingSpec also did something worse than being slow. With its write cache switched off and O_SYNC writes, each write took 0.06 ms, which is faster than any real write-through to flash. The Timetec took 0.48 ms on the same test. A drive that acknowledges synchronous writes from volatile memory is the wrong choice for a device holding BlueStore's DB, so it is going back.

The Timetec passes, with a caveat I can't remove from the harness: nothing here shows what it does on a power cut, and the cluster has had two whole-cluster power losses. The plan is a one-OSD A/B on poe, with the old SSD kept as the rollback.

### The safety bug in my own script

When I pointed the harness at a node's boot disk to test its refusals, it did not refuse. My in-use check looked for mounts and LVM, and a ZFS pool member listed by ID path matched neither. Only a size check stopped it. The fix looks at filesystem signatures and at the pool's own device list. The lesson is old: **test the refusals, not only the happy path.**

## Moving things around a cluster that stays up

Tonight's change list had three parts: install the spare SSD in poe, move a 20 TB drive between nodes, and swap tanaka's USB3 card. The rules that kept it boring:

- **One OSD host down at a time.** With a `4+2` erasure-coded pool and `min_size 5`, two hosts down would make placement groups inactive. A clean-cluster check sits between the hosts.
- **Check before stopping.** `ceph osd ok-to-stop` on the node's OSDs, HA maintenance mode so the guests move first, and the manager and metadata daemons failed over off the node before its shutdown.
- **The session moves too.** The AI agent's own container is an HA guest, so it was moved ahead of everything else, and its tmux windows restored themselves afterwards.
- **A hot-plug with no downtime for the 20 TB drive.** Export the ZFS pool, move the cable to a free root port on the other node (not behind the hub that serves its four OSD drives), import, update the Proxmox storage definition. The weekly replication script looks up its destination host in the storage configuration by pool name, so the move required no edit to the script. The pool's last scrub, two days earlier, found zero errors.

## What I would tell someone doing this at scale

1. **Write the pass criteria before you see the data.** I would have talked myself into a pass on the first noisy latency sample.
2. **Compare identical components across hosts.** Two nodes with the same drives and bridges and no resets did more to localize the fault than any amount of log reading on the node that had them.
3. **Measure at the layer that decides.** Commit latency, not flush latency; the duty cycle, not the cap.
4. **Make every control pausable, and know what each one reads.** My diagnostics tripped my own safety stop twice.
5. **Test your tools' refusals.**

<!-- RESULT PENDING: add the card trial verdict, the poe osd.12 comparison (kv_commit_lat on osd.12 against osd.13/14/26 after the DB/WAL move) and the ladder's final cap when they exist. -->
