---
layout: post
title: "Proxmox VE 8 to 9 Cluster Upgrade, Part 1.5: Ceph Reef to Squid — Release Notes, a Deliberate Detour from the Official Order, and a Performance Baseline"
image: /assets/images/og/proxmox-8-to-9-cluster-upgrade-part-1-5.png
categories: [homelab, proxmox, infrastructure]
tags: [proxmox, ceph, squid, cephfs, bluestore, homelab, upgrade, cluster, performance]
excerpt: "Ceph Reef to Squid turned out to be substantial enough — its own release notes, its own known-issue list, and its own restart-order trade-offs against Proxmox's official guidance — to earn a post of its own between pre-flight and the actual OS upgrade. This is that post: what changed in Squid, where this plan intentionally diverges from Ceph's documented upgrade order and why, and a before/after performance baseline on hardware old enough that the answer wasn't obvious."
description: "Part 1.5 of a three-part series upgrading a 6-node Proxmox VE 8 cluster to Proxmox VE 9. Covers the Ceph Reef to Squid upgrade in depth: what actually changed in Squid (CephFS quiesce, BlueStore LZ4-by-default, the metadata balancer), a real known-issue audit (the elastic shared blob OSD bug, the iSCSI upgrade tracker issue), a deliberate divergence from Ceph's official mon/mgr/OSD restart order in favor of tighter per-node fault isolation, and a CPU/memory/throughput baseline captured before and after on Sandy Bridge hardware with no AVX2."
date: 2026-08-09
last_modified_at: 2026-08-09
seo:
  type: BlogPosting
  date_published: 2026-08-09
  date_modified: 2026-08-09
---

**[Part 1](/proxmox-8-to-9-cluster-upgrade-part-1/)** covered everything that happens before touching a single package: the pre-flight audit and hardening across all six nodes, and building a real Proxmox Backup Server safety net from nothing. What it didn't cover — deliberately, once it became clear how much there was to say — is the Ceph Reef to Squid upgrade itself. That work turned out to deserve its own post: Squid's release notes, a known-issue list worth actually reading before touching production, a restart-order decision that intentionally departs from what Ceph's own documentation recommends, and a performance question this cluster's hardware makes genuinely worth measuring rather than assuming.

This is that post. **Part 2** picks up after this one, once Ceph is fully on Squid, and covers the actual Proxmox OS upgrade to Trixie.

<!-- excerpt-end -->

*A note on timing, same as Part 2's: this is being drafted alongside the work itself, over the weekend the Ceph upgrade actually runs, rather than fully after the fact. The plan sections below reflect the design as decided; the performance-baseline numbers get filled in as the before/after runs actually complete.*

---

## Why This Needed Its Own Post

Proxmox VE 9 has a hard requirement: a hyper-converged Ceph cluster must already be on **Ceph 19.2 Squid** before the host OS upgrade to Trixie can even start. That makes the Ceph upgrade a genuine prerequisite phase, not an optional side quest — and once the plan for it grew to include real release-note research, a documented divergence from Ceph's own upgrade-order guidance, and a performance-testing plan, folding it into Part 1's pre-flight writeup started doing a disservice to both. Pre-flight is about hardening what already exists; this is about a major version jump in the storage layer everything else depends on. They deserve separate treatments.

## What Actually Changed in Squid

Reading the actual release notes — not just the "Ceph 19 is out" headline — surfaced a few changes worth knowing about before the upgrade, not after:

- **CephFS gets crash-consistent snapshot support.** A new suite of subcommands lets you pause write I/O and metadata mutations on a directory tree, which is the primitive distributed applications need to take a snapshot that's actually consistent across multiple clients. Not something this cluster's workloads (Jellyfin media, a handful of dev-service containers) currently need, but worth knowing it exists.
- **The CephFS metadata load balancer is now disabled by default**, gated behind a `balance_automate` flag. Worth being precise here, because it's easy to conflate with something else this cluster already has running: the **mgr balancer module** (`ceph balancer status` shows `mode: upmap`, `active: true` on this cluster today) balances OSD *data placement* across the cluster. The CephFS metadata balancer Squid just changed the default for is a completely different thing — it balances *directory subtree* ownership across active MDS ranks when running multiple active MDS. This cluster runs `max_mds: 1` (see below), so it doesn't apply here either way, but the two are easy to mix up and worth naming correctly.
- **BlueStore now enables RocksDB LZ4 compression by default**, plus optimizations aimed at snapshot-heavy workloads. This is the one item on this list that actually changes what gets measured further down — LZ4 compression trades some CPU for less I/O and metadata overhead, and "some CPU" is a more interesting number on a 2011-era Sandy Bridge i7-2600 with no AVX2 than it would be on anything built in the last five years.
- **`ceph fs swap`** is new — lets you atomically swap the roles of two filesystems, aimed at disaster-recovery failover scenarios. Filed away as a "good to know" rather than anything this upgrade touches.
- **Crimson/Seastore** gets a tech-preview mention for RBD-on-replicated-pools workloads. Explicitly out of scope — this is next-generation OSD internals territory, not a stable-cluster upgrade concern.

Sources: [Ceph v19.2.0 Squid release announcement](https://ceph.io/en/news/blog/2024/v19-2-0-squid-released/), [Proxmox Ceph Reef to Squid wiki](https://pve.proxmox.com/wiki/Ceph_Reef_to_Squid).

## Known Issues Worth Checking Before Touching Anything

The habit this whole project has built — pull the actual source, not a summary of it — applies just as much to release notes as it did to community scripts back in Part 1. Two real issues turned up:

**The Elastic Shared Blob OSD bug (versions 19.2.0 through 19.2.3).** BlueStore's Elastic Shared Blob implementation can cause OSD crashes or, worse, silent data corruption on OSDs created while running an affected version — with the fix in 19.2.4 preventing *new* corruption but not repairing anything already written under the bug. The documented mitigation is `ceph config set osd bluestore_elastic_shared_blobs 0` before creating new OSDs on an affected version.

The nuance worth being precise about: this cluster isn't creating any new OSDs during this upgrade — the existing 15 OSDs are getting their daemon binaries upgraded in place, not recreated. That meaningfully lowers the acute risk here versus a fresh deployment. It doesn't eliminate the need to check which exact point release Proxmox's no-subscription repo actually lands on — if it's still inside the 19.2.0-19.2.3 window, the mitigation gets set proactively regardless, purely as a hedge against any *future* OSD replacement work (a real possibility given `edgar`'s known-fragile USB-backed OSDs) happening before this gets revisited.

**The iSCSI upgrade tracker issue ([#68215](https://tracker.ceph.com/issues/68215)).** A bug specifically hit during 19.1.1 → 19.2.0 upgrades on iSCSI gateways. Not applicable here — this cluster has no iSCSI gateway configured anywhere — but it's the kind of thing worth a deliberate "checked, doesn't apply" rather than silently assuming release notes are all upside.

Source: [Clyso's Ceph Squid known-bugs tracker](https://docs.clyso.com/docs/kb/known-bugs/squid/).

## Where This Plan Diverges From Ceph's Official Restart Order — And Why

Ceph's documented upgrade order, echoed in [Proxmox's own wiki](https://pve.proxmox.com/wiki/Ceph_Reef_to_Squid), is by **daemon type, cluster-wide**: restart every monitor first (one node at a time, but all monitors before moving on), then every manager, then every OSD host (again one at a time), then handle CephFS MDS as a special case last. That's the order that minimizes the total time the cluster spends in a mixed-version state and keeps the upgrade window as short as possible.

This plan does something different: **each node gets its repo flip, package upgrade, and full local daemon restart (mon, mgr, and — where present — OSDs) done together, one node at a time**, before the next node's repository is touched at all. That's a deliberate trade against the official guidance, made for a reason specific to this hardware: every node in this cluster runs a 2011-era Sandy Bridge i7-2600 with no AVX2 support, already flagged back in Part 1 as an unresolved watch item for Squid compatibility. If Squid's mon or mgr code genuinely doesn't run cleanly on this CPU generation, the official order finds that out only after every monitor in the cluster has already been flipped — a much larger blast radius to walk back than one canary node. The per-node approach means that at the point a real incompatibility would surface, at most one node's Ceph packages and repository configuration have actually changed; every other node is provably untouched, at both the binary and the config level, not just the "hasn't been restarted yet" level.

The cost is real and worth naming plainly: this plan spends longer in a mixed Reef/Squid state across the fleet than the official order would, and mixed-version operation — while explicitly supported by Ceph for the duration of a rolling upgrade — is itself a slightly larger surface than a fast, uniform sweep. On a cluster with modern, well-supported CPUs, the official order would likely be the better call. On hardware this old, with a CPU-feature gap already flagged as an open question, trading upgrade-window length for tighter fault isolation is the right side of that trade.

## The Corrected Plan

Two gaps turned up in the original design while researching this post, both folded into the steps below:

1. **A pre-check on CephFS MDS state**, confirmed live before writing this: `ceph fs status` shows a single active MDS (`poe`) with `max_mds: 1` and three plain standbys (`harlan`, `quell`, `kovacs`) — no `standby-replay` daemons in the mix. That's the simple case Ceph's MDS upgrade guidance describes, meaning none of the "reduce ranks to 1, stop standbys, upgrade the active, restart standbys" dance is actually needed here — it's already a single active rank. Worth re-confirming this hasn't changed the moment before the real MDS restart, rather than assuming it still holds from this check.
2. **A missing finalization step.** The original plan unset the safety flags and confirmed `ceph versions` showed Squid everywhere, but never actually told Ceph the cluster's minimum supported OSD release has moved forward. `ceph osd require-osd-release squid` is the documented final step in Ceph's own upgrade guide — it's what unlocks Squid-only OSD map features going forward and is now added as its own line in the plan below.

### 1. Set Cluster Safety Flags
```bash
ssh poe "ceph osd set noout; ceph osd set nobackfill"
```
Cluster-wide, but a flag rather than a package or repo change — the one thing genuinely safe to set fleet-wide up front. Stays set through the entire staged process.

### 2. Canary Stage 1 — `tanaka`: Flip Repo, Upgrade Packages, Restart Mon+Mgr
No OSDs on tanaka — the simplest possible test of whether Squid's mon/mgr code runs cleanly on Sandy Bridge, isolated to this one node:
```bash
ssh tanaka "sed -i 's/ceph-reef bookworm no-subscription/ceph-squid bookworm no-subscription/' /etc/apt/sources.list.d/ceph.list; apt update"
ssh tanaka "tmux new -d -s ceph-upgrade 'apt full-upgrade -y ceph ceph-common ceph-mds ceph-mgr ceph-mon ceph-osd ceph-mgr-dashboard; echo DONE > /root/ceph-upgrade-status'"
# poll /root/ceph-upgrade-status until DONE, then:
ssh tanaka "systemctl restart ceph-mon@tanaka ceph-mgr@tanaka"
ssh poe "ceph -s; ceph versions"   # tanaka now squid; every other node still fully on reef, repo AND packages
```

### 3. Canary Stage 2 — `quell`: Same Pattern, Plus OSDs
The OSD-host canary — standard internal SATA/SSD OSDs, no known fragility, deliberately not `edgar` (whose USB-backed OSDs already have a known quirk that would confound a real Squid problem with the existing USB issue):
```bash
ssh quell "sed -i 's/ceph-reef bookworm no-subscription/ceph-squid bookworm no-subscription/' /etc/apt/sources.list.d/ceph.list; apt update"
ssh quell "tmux new -d -s ceph-upgrade 'apt full-upgrade -y ceph ceph-common ceph-mds ceph-mgr ceph-mon ceph-osd ceph-mgr-dashboard; echo DONE > /root/ceph-upgrade-status'"
# poll until DONE, then:
ssh quell "systemctl restart ceph-mon@quell ceph-mgr@quell"
ssh quell "systemctl restart 'ceph-osd@*'"
ssh poe "ceph -s"   # HEALTH_OK (mod the flags above) — quell's 3 OSDs up/in on squid, no flapping
```

**Gate:** only once both canaries are confirmed clean does the rest of the cluster proceed. At this point the remaining 4 nodes haven't had their `ceph.list` touched at all, so a real problem stays contained to exactly the 2 canary nodes, package level included.

### 4. Remaining Nodes, One at a Time — `edgar` Last
```bash
for n in harlan kovacs poe; do
  ssh $n "sed -i 's/ceph-reef bookworm no-subscription/ceph-squid bookworm no-subscription/' /etc/apt/sources.list.d/ceph.list; apt update"
  ssh $n "tmux new -d -s ceph-upgrade 'apt full-upgrade -y ceph ceph-common ceph-mds ceph-mgr ceph-mon ceph-osd ceph-mgr-dashboard; echo DONE > /root/ceph-upgrade-status'"
  # poll until DONE, then:
  ssh $n "systemctl restart ceph-mon@\$(hostname) ceph-mgr@\$(hostname)"
  ssh poe "ceph -s | grep -E 'quorum|HEALTH'"
  ssh $n "systemctl restart 'ceph-osd@*'"
  ssh poe "ceph -s"   # must show HEALTH_OK before the next node's repo gets touched at all
done

# edgar last — same isolation pattern, plus the USB-specific checks
ssh edgar "sed -i 's/ceph-reef bookworm no-subscription/ceph-squid bookworm no-subscription/' /etc/apt/sources.list.d/ceph.list; apt update"
ssh edgar "tmux new -d -s ceph-upgrade 'apt full-upgrade -y ceph ceph-common ceph-mds ceph-mgr ceph-mon ceph-osd ceph-mgr-dashboard; echo DONE > /root/ceph-upgrade-status'"
# poll until DONE, then:
ssh edgar "systemctl restart ceph-mon@edgar ceph-mgr@edgar"
ssh poe "ceph -s | grep -E 'quorum|HEALTH'"
ssh edgar "systemctl restart 'ceph-osd@*'"
ssh edgar "cat /sys/module/usb_storage/parameters/quirks; lsblk -o NAME,SIZE,TRAN,MODEL,SERIAL | grep usb"
ssh poe "ceph osd tree | grep -A5 'host edgar'; ceph -s"
```

### 5. Restart MDS Across All 6
Confirm the single-active-rank state above still holds, then restart — every node is already on Squid packages by this point, so a fleet-wide pass is fine:
```bash
ssh poe "ceph fs status"   # re-confirm max_mds:1, no standby-replay, before restarting anything
for n in harlan kovacs poe edgar tanaka quell; do
  ssh $n "systemctl restart ceph-mds@\$(hostname)"
  ssh poe "ceph fs status; ceph -s"
done
```

### 6. Unset Flags, Finalize the Release, Verify
```bash
ssh poe "ceph osd unset nobackfill; ceph osd unset noout
ceph versions                        # expect squid everywhere, zero reef stragglers
ceph osd require-osd-release squid   # the finalization step missing from the original plan
ceph -s                              # HEALTH_OK"
```

## Performance Testing Plan

Two real reasons make a before/after performance comparison worth doing here rather than just assuming Squid is a strict improvement: BlueStore's RocksDB now defaults to LZ4 compression (a genuine CPU/I-O trade-off, not a free win), and this cluster's Sandy Bridge CPUs have no AVX2 — already flagged as a watch item for correctness, and just as relevant for anything performance-sensitive that leans on newer instruction sets under the hood. If there's a hardware generation where Squid's overhead looks different from what's reported elsewhere, this is it.

**Captured before Phase A starts, and again after Section 6 completes, same commands, same node:**

1. **Idle CPU/memory baseline per daemon type**, one representative node per role:
   ```bash
   ssh poe   "ps -o %cpu,%mem,rss,cmd -C ceph-mon,ceph-mgr,ceph-osd | sort -k1 -n -r"
   ssh quell "free -h"
   ```
2. **A repeatable synthetic write/read benchmark** against a dedicated scratch pool (not `cephfs_data` — isolate the test from real workload noise):
   ```bash
   ssh poe "ceph osd pool create bench-scratch 32 32
   rados bench -p bench-scratch 60 write --no-cleanup
   rados bench -p bench-scratch 60 seq
   rados bench -p bench-scratch 60 rand
   ceph osd pool delete bench-scratch bench-scratch --yes-i-really-really-mean-it"
   ```
   Recording bandwidth (MB/s), IOPS, and average/99th-percentile latency from each run — the numbers that would actually show a LZ4-compression CPU tax if one exists on this hardware.
3. **Per-OSD internal bench**, cheaper and more targeted than a full `rados bench`, run against one OSD per host:
   ```bash
   ssh poe "ceph tell osd.0 bench"
   ```
4. **BlueStore memory footprint via mempool dump**, directly relevant to the LZ4-by-default change:
   ```bash
   ssh poe "ceph daemon osd.0 dump_mempools | python3 -m json.tool | grep -A3 bluestore"
   ```
5. **MDS metadata operation latency**, the CephFS-specific half of this comparison:
   ```bash
   ssh poe "ceph daemon mds.poe perf dump | python3 -m json.tool | grep -A5 '\"mds\"'"
   ```

The same five checks, run identically before Section 1 and after Section 6, is what turns "Squid feels about the same" into an actual number — and on hardware this old, actual numbers have already been worth more than assumptions more than once in this project.

---

## Key Takeaways

1. **A Canary Discipline Applies to Storage-Layer Upgrades, Not Just OS Upgrades.** The same reasoning that puts one node ahead of the rest for a Trixie kernel jump applies just as much to a hyper-converged storage layer's own major version bump — a cluster-wide daemon restart sweep is still a single point of failure, however well-tested each individual command is.
2. **Official Upgrade Order and Fault Isolation Aren't Always the Same Goal.** Ceph's documented restart order optimizes for the shortest possible mixed-version window. On hardware with a real, flagged unknown (no AVX2 here), optimizing instead for "how many nodes are affected if this specific node's upgrade goes wrong" is a defensible, deliberate departure — as long as it's a named trade-off, not an accidental deviation.
3. **Release Notes Have a Known-Issues Section for a Reason.** The Elastic Shared Blob bug only mattered here because of a nuance specific to this upgrade (no new OSDs being created) — a nuance that only surfaces by actually reading the bug, not by skimming a changelog headline.
4. **"It's Probably Fine" Isn't a Substitute for a Baseline.** A default-on compression change and a CPU generation with a known feature gap is exactly the combination worth measuring rather than assuming — especially when the measurement itself costs a handful of `rados bench` runs, not a research project.

With Ceph's own upgrade plan fully specified — including the two gaps this research turned up — **[Part 2](/proxmox-8-to-9-cluster-upgrade-part-2/)** covers what happens once Squid is confirmed clean everywhere: the actual Proxmox OS upgrade to Trixie.
