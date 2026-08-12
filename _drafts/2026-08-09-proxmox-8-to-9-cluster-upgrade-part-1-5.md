---
layout: post
title: "Proxmox VE 8 to 9 Cluster Upgrade, Part 1.5: Ceph Reef to Squid — Release Notes, a Deliberate Detour from the Official Order, and What Actually Happened"
image: /assets/images/og/proxmox-8-to-9-cluster-upgrade-part-1-5.png
categories: [homelab, proxmox, infrastructure]
tags: [proxmox, ceph, squid, cephfs, bluestore, homelab, upgrade, cluster, performance, troubleshooting]
excerpt: "Ceph Reef to Squid turned out to be substantial enough — its own release notes, its own known-issue list, and its own restart-order trade-offs against Proxmox's official guidance — to earn a post of its own between pre-flight and the actual OS upgrade. This is that post: what changed in Squid, where this plan intentionally diverges from Ceph's documented upgrade order and why, and what actually happened running it for real against six 2011-era nodes — including a rebuild-era gap in CephFS redundancy the upgrade itself surfaced."
description: "Part 1.5 of a three-part series upgrading a 6-node Proxmox VE 8 cluster to Proxmox VE 9. Covers the Ceph Reef to Squid upgrade in depth: what actually changed in Squid (CephFS quiesce, BlueStore LZ4-by-default, the metadata balancer), a real known-issue audit (the elastic shared blob OSD bug, the iSCSI upgrade tracker issue), a deliberate divergence from Ceph's official mon/mgr/OSD restart order in favor of tighter per-node fault isolation, and the real execution against six 2011-era Sandy Bridge nodes — wedged scheduled tasks, an interactive dialog `-y` doesn't suppress, a mirror-side slowdown, and a stale-cluster-state gap in CephFS MDS redundancy left over from two nodes' earlier rebuilds."
date: 2026-08-09
last_modified_at: 2026-08-12
seo:
  type: BlogPosting
  date_published: 2026-08-09
  date_modified: 2026-08-12
---

**[Part 1](/proxmox-8-to-9-cluster-upgrade-part-1/)** covered everything that happens before touching a single package: the pre-flight audit and hardening across all six nodes, and building a real Proxmox Backup Server safety net from nothing. What it didn't cover — deliberately, once it became clear how much there was to say — is the Ceph Reef to Squid upgrade itself. That work turned out to deserve its own post: Squid's release notes, a known-issue list worth actually reading before touching production, a restart-order decision that intentionally departs from what Ceph's own documentation recommends, and — now that it's actually run — a handful of real gotchas the plan alone couldn't have predicted.

This is that post. **Part 2** picks up after this one, once Ceph is fully on Squid, and covers the actual Proxmox OS upgrade to Trixie.

<!-- excerpt-end -->

*Updated Aug 12, 2026: the plan below is exactly what was designed before execution — kept as-is, since the reasoning behind it is still the point. A new section after it, "What Actually Happened," covers the real run: two gotchas the plan couldn't have anticipated, and a stale-cluster-state discovery that turned into its own small investigation.*

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

## What Actually Happened

The plan above was designed cleanly. Running it against six real, 2011-era nodes surfaced things a plan can't predict from a desk — two genuine environment gotchas, and a discovery that turned into its own small investigation. All six sections above executed cleanly in the end: both canaries clean, the remaining four nodes upgraded one at a time with zero cross-contamination, MDS restarted with real client traffic never interrupted, and a final `ceph -s` of `HEALTH_OK` with zero Reef stragglers across all 31 daemons. The interesting part is everything that happened in between.

**A scheduled task was wedged on four of six nodes, and it wasn't obviously related to this upgrade at all.** The first `apt update` (on the `tanaka` canary) hung indefinitely on a lock held by a process that turned out to be Proxmox's own built-in scheduled "refresh available updates" task — started that morning, still running roughly nine hours later. `/proc/<pid>/wchan` showed `do_select`: not slow, genuinely stuck, waiting on its own idle child processes. Safe to `kill -TERM` (it's a background convenience task, no live cluster state involved), but the real finding was checking the other nodes proactively afterward and finding the identical pattern already sitting on three more of them, at three different start times. Not a single shared event — a systemic issue with how this fleet's own scheduled apt-update task behaves, independent of anything this upgrade touched. Worth a `ps aux | grep apt` check before assuming an apt lock error means "try again in a minute," and worth its own look separately from this upgrade.

**`apt full-upgrade -y` still stops for an interactive dialog.** `-y` suppresses apt's own confirmation prompts, but not `needrestart`'s — a whiptail dialog titled "Daemons using outdated libraries" popped up mid-upgrade on the first real run, listing `ceph-mon`, `ceph-crash`, and, unexpectedly, `corosync` and several other PVE management daemons pulled in by the same dependency chain. Dismissed manually the first time (confirmed harmless — it auto-restarted `ceph-mon` and `corosync` ahead of the plan's own explicit restart step, no quorum impact), then fixed properly for every remaining node by prepending `NEEDRESTART_MODE=l` to the upgrade command — list-only, restart nothing automatically, leave each phase's own explicit `systemctl restart` as the sole trigger. That distinction — *what* needs restarting versus *when* it actually restarts — matters more here than it would on a single-server upgrade, since the whole point of the per-node isolation strategy above is controlling exactly when each daemon type bounces.

**One node's package download crawled to double digits of kB/s, with no obvious local cause.** `poe`'s upgrade sat at an estimated multi-hour ETA at one point — host load average under 1, no network interface errors, a small test file downloading fine. No fix applied; it kept making genuine (if slow) progress, and killing a partway-through `apt` transaction to retry a probably-transient mirror-side slowdown risked more than it solved. It finished in about 20 minutes end to end, well inside the worst-case estimate. Worth naming as a real possibility for anyone reusing this pattern: not every slow step is stuck, and the fix for "genuinely making progress, just slowly" is patience, not a kill switch.

**Every mon restart caused a brief, expected quorum blip — caught live once, mid-election.** One status check landed at exactly 0.47 seconds after a mon restart and showed the cluster one node short of full quorum, mid-handoff. A recheck three seconds later showed all 6 back. Genuinely useful to have caught this by accident rather than only in theory — it's the kind of transient state a health check script needs to tolerate (a short retry, not a hard failure) rather than something to treat as a real problem the instant it's observed.

### A Rebuild Left Two Nodes Missing From CephFS Redundancy

This part isn't strictly a Ceph-Squid-upgrade finding, but it surfaced directly because of this upgrade, and it's worth documenting for the same reason everything else in this series gets documented: it's a real, previously-invisible gap that a routine operational task (restarting MDS daemons cluster-wide, Section 5 above) happened to expose.

This cluster's own architecture documentation records the intended CephFS design as 6 MDS daemons — one active, five standby, one per node. Live, only 4 were actually running. `edgar` and `tanaka` — the same two nodes that had gotten SSD/fresh-install rebuilds back in early August, already the source of a stale-SSH-host-key cleanup in Part 1's pre-flight — were both silently missing an MDS instance entirely, with no error anywhere flagging it. `ceph -s`'s own health summary doesn't warn about running below a documented target; it only reports on the MDS ranks actually configured to exist, and from Ceph's point of view, a 4-daemon CephFS with 1 active and 3 standby is a completely valid, healthy configuration. Nothing was ever going to surface this on its own.

Trying to recreate the missing daemons (`pveceph mds create`, the same command used for every other daemon type in this series) failed immediately: `MDS 'edgar' already referenced in ceph config, abort!` — which turned out to be the actual interesting part. The node-level rebuild had wiped `edgar`'s *local* MDS keyring and data directory (confirmed: `/var/lib/ceph/mds/` was completely empty, with a directory modification time matching the rebuild date exactly, versus a working node's MDS keyring dated back to January). But two pieces of *cluster-side* state survived that local wipe untouched: a stale `mds.edgar` authentication key still sitting in `ceph auth list`, and a stale `[mds.edgar]` stanza still sitting in `/etc/pve/ceph.conf` — a file synced cluster-wide via Proxmox's own cluster filesystem, not stored locally on any one node's disk. Removing both (`ceph auth del mds.edgar`, then a precise, verified edit to `ceph.conf` leaving every other section — including edgar's legitimate `[mon.edgar]` entry — untouched) cleared the way, and `pveceph mds create` succeeded cleanly on the first retry. Same for `tanaka`.

The generalizable lesson: **a node rebuild wipes what's local to that node, not what the rest of the cluster still remembers about it.** This is the same category of gotcha as the stale SSH host keys from Part 1 — a rebuilt node's *identity*, as far as the rest of the cluster is concerned, doesn't necessarily start from zero, and the leftover half-state can silently block exactly the kind of straightforward "just recreate it" fix that seems like it should work without any investigation first.

## Performance Testing Plan

Two real reasons make a before/after performance comparison worth doing here rather than just assuming Squid is a strict improvement: BlueStore's RocksDB now defaults to LZ4 compression (a genuine CPU/I-O trade-off, not a free win), and this cluster's Sandy Bridge CPUs have no AVX2 — already flagged as a watch item for correctness, and just as relevant for anything performance-sensitive that leans on newer instruction sets under the hood. If there's a hardware generation where Squid's overhead looks different from what's reported elsewhere, this is it.

**Not yet run as of this update.** The methodology below is the plan as designed; the actual before/after numbers weren't captured as part of this upgrade pass and are left as a clearly-marked gap rather than backfilled with anything unverified. If this gets picked up in a follow-up, it belongs either as an update to this section or its own short post — not folded in after the fact without the real data behind it.

**The plan: capture before Phase A starts, and again after Section 6 completes, same commands, same node.**

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

1. **A Canary Discipline Applies to Storage-Layer Upgrades, Not Just OS Upgrades.** The same reasoning that puts one node ahead of the rest for a Trixie kernel jump applies just as much to a hyper-converged storage layer's own major version bump — a cluster-wide daemon restart sweep is still a single point of failure, however well-tested each individual command is. Both canaries here came back clean, and the plan still held up applying that same isolation to all four remaining nodes.
2. **Official Upgrade Order and Fault Isolation Aren't Always the Same Goal.** Ceph's documented restart order optimizes for the shortest possible mixed-version window. On hardware with a real, flagged unknown (no AVX2 here), optimizing instead for "how many nodes are affected if this specific node's upgrade goes wrong" is a defensible, deliberate departure — as long as it's a named trade-off, not an accidental deviation.
3. **Release Notes Have a Known-Issues Section for a Reason.** The Elastic Shared Blob bug only mattered here because of a nuance specific to this upgrade (no new OSDs being created) — a nuance that only surfaces by actually reading the bug, not by skimming a changelog headline. Confirmed moot in the end anyway: the point release this repo actually resolved to (19.2.5) was already well past the affected window.
4. **`-y` Doesn't Mean "Fully Non-Interactive."** `apt`'s own confirmation prompts and `needrestart`'s interactive dialog are two different things, suppressed two different ways — worth checking for *before* an unattended upgrade script hits it live, not after a run silently stalls on a whiptail screen no one's watching.
5. **A Health Check Only Warns About What It Knows to Expect.** `ceph -s` never once flagged that CephFS was running on 4 MDS instead of the documented 6 — a valid 1-active/3-standby configuration is, correctly, not an error from Ceph's point of view. The gap was only findable by checking live state against this cluster's own architecture documentation, not by watching for an alert that was never going to fire.
6. **A Node Rebuild Doesn't Reset Everything the Cluster Remembers.** Local state and cluster-side state can drift out of sync in exactly the way that turns a "just recreate it" fix into a real investigation — a rebuilt node's stale SSH host key or a stale cephx auth entry both look, from the outside, like they should have been cleared along with everything else on that disk. They weren't.

With Ceph's own upgrade plan fully specified, run for real, and one unrelated-but-real redundancy gap closed along the way — **[Part 2](/proxmox-8-to-9-cluster-upgrade-part-2/)** covers what happens once Squid is confirmed clean everywhere: the actual Proxmox OS upgrade to Trixie.
