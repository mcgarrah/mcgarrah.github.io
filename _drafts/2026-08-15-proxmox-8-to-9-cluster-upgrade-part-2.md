---
layout: post
title: "Proxmox VE 8 to 9 Cluster Upgrade, Part 2: The Canary, the Batch, and Verification"
image: /assets/images/og/proxmox-8-to-9-cluster-upgrade-part-2.png
categories: [homelab, proxmox, infrastructure]
tags: [proxmox, ceph, squid, debian, trixie, zfs, homelab, upgrade, cluster, gpu, networking]
excerpt: "Part 1 covered everything that happens before touching Proxmox itself — pre-flight hardening, the Ceph Squid migration, and a real backup safety net. Part 2 is the actual OS upgrade: one canary node, five more in sequence, and verifying nothing quietly broke along the way."
description: "Part 2 of a two-part series upgrading a 6-node Proxmox VE 8 cluster to Proxmox VE 9. Covers the tanaka canary upgrade with a tested ZFS rollback path, the sequential batch rollout of the remaining five nodes, and post-upgrade verification — including GPU passthrough and network interface naming, the two things most likely to break quietly on a kernel jump this large."
date: 2026-08-15
last_modified_at: 2026-08-06
seo:
  type: BlogPosting
  date_published: 2026-08-15
  date_modified: 2026-08-06
---

**[Part 1](/proxmox-8-to-9-cluster-upgrade-part-1/)** covered everything that happens before a single node touches Proxmox VE 9: pre-flight hardening across all six nodes and building a real Proxmox Backup Server safety net from nothing. **[Part 1.5](/proxmox-8-to-9-cluster-upgrade-part-1-5/)** covered the Ceph Reef → Squid upgrade required before the OS jump can even start — staged with a canary instead of one cluster-wide sweep, plus release-note research and a before/after performance baseline. With Ceph fully on Squid, the actual OS upgrade can start.

This post covers the part that actually carries risk to the running cluster: rebooting six nodes with **no out-of-band management** into a kernel roughly four major versions newer (`6.8` → `7.0`, targeting the current PVE 9.2 point release rather than bare 9.0) than what they're running today, on hardware where UEFI has already failed four separate times. One canary node first, then the remaining five in sequence, then verification — including network interface naming, and a GPU investigation that turned out different than expected.

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

### GPU Passthrough — and a Correction Along the Way
The cluster splits GPU passthrough across two hardware generations — Quadro K600 on `edgar` and `tanaka`, Quadro P620 on the other four. The initial assumption going into this verification was the obvious one: a kernel major-version jump this large (`6.8` to `7.0`) could easily break NVIDIA driver compatibility, so check the driver branch against the new kernel before assuming passthrough survives.

Checking it directly turned that assumption on its head. `lspci -k` on every GPU node showed **`nouveau`** — the open-source, kernel-builtin driver — not NVIDIA's proprietary stack. No `nvidia-smi` anywhere, no driver package installed. Since `nouveau` ships as part of the mainline Linux kernel itself rather than a separate out-of-tree module, there's no driver-branch compatibility question at all here: it builds and ships with every kernel release automatically, including `7.0`. Passthrough survival was never actually at risk.

That finding opened a more interesting, more consequential question: `nouveau` doesn't support NVIDIA's NVENC hardware encoding, only basic display and limited decode acceleration — so the *real* hardware-accelerated Jellyfin transcoding and any ML workload this hardware could theoretically support were never actually happening, upgrade or not. Investigating what it would take to fix that for real turned into its own can of worms:

- **The K600 (Kepler) nodes are a dead end.** `R470` is the last driver branch that ever supported Kepler, and it's confirmed broken on kernels past roughly `6.10` — a kernel function it depends on was removed. `7.0` is well beyond that, with no supported path back. Kepler's compute capability is also long past what any current ML framework will run. `edgar` and `tanaka` stay on `nouveau`; fixing this for real means a physical GPU swap, not a driver update.
- **The P620 (Pascal) nodes are a real, if not risk-free, option.** Pascal's last supported branch is `580.x` — the next major version drops Pascal entirely, so this is a closing window, not a permanent solution. Kernel `7.0` support on `580.x` is reportedly still being worked out as of mid-2026, not yet a sure thing. The plan: canary the driver on one P620 node first (installed from NVIDIA's official `.run` file, not a Debian package — Proxmox's kernel headers don't always line up cleanly with apt-based DKMS), confirm both an NVENC transcode and a basic CUDA workload actually run, and only then roll it out to the other three. If `580.x` doesn't build cleanly against `7.0` on the canary, the same `proxmox-boot-tool kernel pin` mechanism already proven during `quell`'s pre-flight work in Part 1 is the fallback — hold that one node back on its prior kernel until the driver branch catches up.

Post-upgrade verification, then, isn't just "does the GPU still show up" — it's confirming the thing that actually matters (real hardware acceleration) was correctly scoped to the hardware that can deliver it, and deliberately not chased on the hardware that can't.

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
