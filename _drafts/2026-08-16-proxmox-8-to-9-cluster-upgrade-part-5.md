---
layout: post
title: "Proxmox VE 8 to 9 Cluster Upgrade, Part 5: The Canary, the Batch, and Verification"
image: /assets/images/og/proxmox-8-to-9-cluster-upgrade-part-5.png
categories: [homelab, proxmox, infrastructure]
tags: [proxmox, ceph, squid, debian, trixie, zfs, homelab, upgrade, cluster, gpu, networking]
excerpt: "Part 1 covered everything that happens before touching Proxmox itself — pre-flight hardening and a real backup safety net; Part 2 covered the Ceph Squid migration; Part 3 covered the NVIDIA GPU driver work done ahead of the jump; Part 4 covered standing up a full media automation stack, also ahead of the jump, plus two capacity incidents it surfaced. Part 5 is the actual OS upgrade: one canary node, five more in sequence, and verifying nothing quietly broke along the way — including under the real workload Part 4 added."
description: "Part 5 of a five-part series upgrading a 6-node Proxmox VE 8 cluster to Proxmox VE 9. Covers the tanaka canary upgrade with a tested ZFS rollback path, the sequential batch rollout of the remaining five nodes, and post-upgrade verification — including confirming the NVIDIA drivers installed in Part 3 survive the kernel jump, and network interface naming, the two things most likely to break quietly on a kernel jump this large."
date: 2026-08-16
last_modified_at: 2026-08-16
seo:
  type: BlogPosting
  date_published: 2026-08-16
  date_modified: 2026-08-16
---

**[Part 1](/proxmox-8-to-9-cluster-upgrade-part-1/)** covered everything that happens before a single node touches Proxmox VE 9: pre-flight hardening across all six nodes and building a real Proxmox Backup Server safety net from nothing. **[Part 2](/proxmox-8-to-9-cluster-upgrade-part-2/)** covered the Ceph Reef → Squid upgrade required before the OS jump can even start — staged with a canary instead of one cluster-wide sweep, plus release-note research and a before/after performance baseline. **[Part 3](/proxmox-8-to-9-cluster-upgrade-part-3/)** covered the NVIDIA GPU driver work on the four Pascal-generation nodes, done deliberately out of sequence — ahead of this OS upgrade rather than after it, to test the new driver against a known-stable kernel first. **[Part 4](/proxmox-8-to-9-cluster-upgrade-part-4/)** covered standing up a full *arr media automation stack on top of that, also deliberately ahead of the OS jump — and two real capacity incidents (a Jellyfin memory ceiling, a CephFS I/O ceiling) that its first real burst of activity surfaced. With Ceph fully on Squid, the GPU drivers validated, and a real workload now actually running on the cluster instead of an idle one, the actual OS upgrade can start.

This post covers the part that actually carries risk to the running cluster: rebooting six nodes with **no out-of-band management** into a kernel roughly four major versions newer (`6.8` → `7.0`, targeting the current PVE 9.2 point release rather than bare 9.0) than what they're running today, on hardware where UEFI has already failed four separate times. One canary node first, then the remaining five in sequence, then verification — including network interface naming, and confirming the NVIDIA drivers installed in Part 3 survive the jump.

<!-- excerpt-end -->

*A note on timing: this post is being written and scheduled before the upgrade itself runs, the same way Part 1's Ceph and backup work was planned out before execution. The plan below reflects what's designed to happen — expect this post to get a pass of real results, corrections, and probably at least one surprise once it's actually run, the same way nearly every phase in Part 1 turned up something the plan didn't originally account for.*

---

## Phase B: Canary Node Upgrade (`tanaka` → PVE 9 / Trixie)

`tanaka` has no Ceph OSDs and is HA-idle, making it the ideal canary: the smallest possible blast radius if something goes wrong, and the node already carrying the freshest, best-understood configuration in the cluster from its own recent rebuild.

### 1. Testing the Rollback Mechanism First
A ZFS snapshot is only a real safety net if the recovery path has actually been exercised once, not just written down. Before touching anything for real:
1. Snapshot: `zfs snapshot rpool/ROOT/pve-1@rollback-test`.
2. Create a marker file and install a small, disposable test package — something trivially easy to confirm is gone afterward.
3. Boot the Proxmox 8.4 installer's Debug/Rescue shell, import `rpool`, run `zfs rollback -r rpool/ROOT/pve-1@rollback-test`, export `rpool`.
4. Boot back into the installed OS and confirm the marker file and test package are completely gone, and the node still rejoins the cluster cleanly.

Only once this round-trip is proven does the real upgrade get a snapshot of its own.

### 2. Executing the Canary Upgrade
1. Fresh pre-upgrade snapshot: `zfs snapshot rpool/ROOT/pve-1@pre-v9-upgrade`.
2. Flip apt sources from `bookworm` to `trixie` in `/etc/apt/sources.list.d/pve-install-repo.list` and `ceph.list`.
3. Run the OS upgrade inside `tmux`, so a dropped SSH session doesn't kill it mid-flight:
   ```bash
   tmux new -d -s pve9-upgrade 'apt update && apt full-upgrade -y; echo DONE > /root/pve9-upgrade-status'
   ```
4. Reboot into the new Trixie kernel on-site — physical presence is the recovery plan here, not a nicety, given there's no IPMI/BMC to fall back on.
5. Verify: `pveversion -v`, `zpool status`, `pvecm status`, and confirm `tanaka` rejoins the Ceph cluster cleanly.

If anything goes wrong, the rollback path proven in step 1 above is the actual answer, not a hopeful assumption.

---

## Phase C: Sequential Batch Upgrade of the Remaining Five Nodes

Once `tanaka` passes its soak period, the rest go in this order:

1. **`quell`** — already proved it tolerates a fresh kernel earlier in this project (its stale kernel pin was resolved and verified via two real reboots back in Part 1's pre-flight), so it goes first among the OSD hosts too.
2. **`poe`**, **`kovacs`**, **`harlan`** — standard OSD host upgrades, no known complications.
3. **`edgar`** — last, deliberately. Its three OSDs (`osd.1`, `osd.4`, `osd.7`) live on USB-attached drives, which already caused one real incident during an earlier, unrelated migration. Going last here isn't superstition — it's giving every other node's turn a chance to surface a general Trixie-kernel problem first, before combining that risk with a known-fragile storage path.

### Per-Node Workflow
For each node:
1. **Relocate HA workloads** to peer nodes (`ha-manager migrate ct:<id> <peer>`) rather than letting a mid-reboot HA fencing event handle it reactively.
2. **Take a ZFS root snapshot** (`zfs snapshot rpool/ROOT/pve-1@pre-v9-upgrade`) — the exact mechanism already proven on `tanaka`.
3. **Flip repositories, upgrade, reboot** — same `tmux`-wrapped pattern as the canary.
4. **`edgar`-specific:** verify the `usb_storage.quirks` kernel parameter survived the upgrade, check all 4 USB drives via `lsblk`, run `smartctl` health checks, and confirm all 3 USB-backed OSDs rejoin `ceph osd tree` cleanly before moving on.

---

## Phase D: Verification — Including the Two Things Most Likely to Break Quietly

The obvious checks come first:

```bash
# Versions across all nodes
for n in harlan kovacs poe edgar tanaka quell; do ssh $n "pveversion -v | head -3"; done

# Cluster quorum & Ceph health
ssh poe "ceph -s; ceph versions; pvecm status"
```

Every node should report `PVE 9.2`, `Ceph 19.2 Squid`, and `HEALTH_OK`. But a kernel jump this large (`6.8` to `7.0`) doesn't just risk the things with obvious error messages — it risks the things that quietly keep working *almost* correctly, or fail somewhere a `ceph -s` will never show you.

### GPU Passthrough — Confirming What Part 3 Already Installed
Unlike the rest of this post, GPU passthrough isn't something to investigate fresh here — **[Part 3](/proxmox-8-to-9-cluster-upgrade-part-3/)** already did that work, deliberately ahead of this OS upgrade: `nouveau` confirmed running by default on both hardware generations, the K600 (Kepler) nodes ruled out as a dead end (`R470` broken past kernel `6.10`, compute capability too old for ML anyway), and the P620 (Pascal) nodes running NVIDIA's proprietary `580.x` driver via DKMS, installed and verified on `harlan`, `kovacs`, `poe`, and `quell` before this kernel jump — specifically so the driver wasn't also an unknown at the same time as the kernel.

Post-upgrade verification here is narrower: confirm the DKMS-built `580.x` module survives the `6.8` → `7.0` jump and rebuilds cleanly against the new kernel headers, rather than re-deriving whether proprietary drivers are viable at all.

```bash
for n in harlan kovacs poe quell; do
  ssh $n "dkms status; nvidia-smi --query-gpu=driver_version,name --format=csv,noheader"
done
```

Expected: `nvidia/580.142` reported as `installed` against the new `7.0` kernel on all four nodes, and `nvidia-smi` still reporting the Quadro P620 cleanly. If DKMS didn't rebuild automatically against the new kernel headers, the fallback is the same `proxmox-boot-tool kernel pin` mechanism from Part 1 — hold that node back on its prior kernel until the driver branch is confirmed compatible, rather than running a node with a broken GPU module. `edgar` and `tanaka` stay on `nouveau`, unaffected either way — nothing to re-investigate there beyond passthrough itself still working, which the kernel's built-in driver guarantees.

### Network Interface Naming
Part 1 compiled a full MAC-address-to-interface table across all 6 nodes specifically because Debian 13 could, in theory, alter predictable network interface naming. The real verification here isn't "does the node have network access" — DHCP or a static IP misconfigured to the wrong physical port can still technically pass a ping test while quietly routing management traffic over the wrong NIC, or the SAN bridge over the public one. The actual check is confirming each node's `vmbr0` (public) and `vmbr1` (SAN) bridges still have the *same physical MAC addresses* bound to them as `bridge-ports` that Part 1's table recorded — not just that connectivity exists, but that it's going over the intended physical path.

### Final Cleanup
Once every node reports clean on both fronts, the pre-upgrade ZFS snapshots get destroyed (after a short soak period, not immediately), and infrastructure documentation (`CLUSTER-SUMMARY.md`, `BOOT-DRIVE-ANALYSIS.md`) gets updated to reflect the new baseline.

---

## Key Takeaways from the Upgrade Itself

1. **Respect Out-of-Band Realities:** When nodes lack IPMI/BMC management, schedule OS reboots only when physical access to the hardware is actually available — the rollback plan is only as good as your ability to execute it if remote access disappears.
2. **Test Rollback Paths Before You Need Them:** A ZFS snapshot is a real safety net only after the rescue-shell rollback workflow has actually been exercised once, end to end.
3. **A Clean `ceph -s` Isn't the Whole Verification:** Passthrough devices and network path integrity can both degrade in ways a health check will never surface — verify the things that don't have their own error messages.
4. **Order Matters When One Node Has a Known Fragility:** Save the node with the pre-existing quirk for last, so a new problem elsewhere doesn't get confused with the old one.

With a methodical, phase-gated plan — and a canary at both the storage layer and the OS layer — even a complex hyper-converged homelab cluster on hardware this old can move to Proxmox VE 9 without betting the whole cluster on a single untested step.
