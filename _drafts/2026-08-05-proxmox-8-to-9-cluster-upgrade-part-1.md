---
layout: post
title: "Proxmox VE 8 to 9 Cluster Upgrade, Part 1: Pre-Flight, Ceph Squid, and the Backup Safety Net"
image: /assets/images/og/proxmox-8-to-9-cluster-upgrade-part-1.png
categories: [homelab, proxmox, infrastructure]
tags: [proxmox, ceph, squid, debian, trixie, zfs, homelab, upgrade, cluster, backup, pbs]
excerpt: "Upgrading a live, multi-node hyper-converged homelab cluster is equal parts software engineering, operational discipline, and risk management. Part 1 covers everything that happens before the actual Proxmox OS upgrade: pre-flight hardening, the Ceph Reef to Squid migration, and building a real backup safety net."
description: "Part 1 of a two-part series on upgrading a 6-node Proxmox VE 8 cluster to Proxmox VE 9. Covers pre-flight hardening (dead apt repos, a persistent kernel pin, LXC maintenance), building a Proxmox Backup Server safety net from scratch, and the Ceph Reef to Squid upgrade — all on aging Dell OptiPlex 990 hardware with no out-of-band management."
date: 2026-08-05
last_modified_at: 2026-08-07
seo:
  type: BlogPosting
  date_published: 2026-08-05
  date_modified: 2026-08-07
---

Upgrading a live, multi-node hyper-converged homelab cluster is equal parts software engineering, operational discipline, and risk management. My 6-node Proxmox VE cluster—codenamed **AlteredCarbon** (`harlan`, `kovacs`, `poe`, `edgar`, `tanaka`, and `quell`)—runs a combination of ZFS root boot mirrors, Ceph storage (Reef 18.2.8), and High Availability (HA) LXC workloads.

With Proxmox VE 9 (built on Debian 13 "Trixie" and Ceph 19.2 "Squid") now available, it is time to move the cluster forward. However, upgrading a cluster with **no out-of-band management** (no IPMI, iDRAC, or PiKVM) on aging Dell OptiPlex 990 hardware (Sandy Bridge i7-2600 CPUs) requires a battle-tested execution plan where every risk is audited and every rollback path is verified before touching production workloads.

This turned into a two-part series. **Part 1** (this post) covers everything that happens *before* a single node touches Trixie: the pre-flight audit and hardening, building a real backup safety net from nothing, and the Ceph Reef → Squid migration that Proxmox requires before the OS upgrade can even begin. **Part 2** covers the actual OS upgrade itself — the canary node, the batch rollout, and verification — once it's actually run.

<!-- excerpt-end -->

## Cluster Topology & Constraints

Before touching package repositories or running upgrade scripts, it is vital to map out the hardware and software topology:

- **Cluster Nodes (6 Total):**
  - `harlan` (.11) — OSD Host
  - `kovacs` (.12) — OSD Host
  - `poe` (.13) — OSD Host
  - `edgar` (.14) — OSD Host + USB OSDs + Backup Host
  - `tanaka` (.15) — Non-OSD / Canary Host (recently rebuilt)
  - `quell` (.16) — OSD Host
- **Compute & Architecture:** Legacy BIOS / GRUB boot with ZFS root boot mirrors across all 6 nodes (UEFI is non-viable on this Dell OptiPlex 990 family; see prior boot drive post). Sandy Bridge i7-2600 processors without AVX2 support — flagged early as a watch item for Squid/Trixie compatibility, and it shapes how the Ceph upgrade gets staged below.
- **Storage:** Ceph Reef (18.2.8) across 15 OSDs (5 hosts), with a mix of internal SATA SSDs and external USB-backed OSDs. We also have some external USB-backed ZFS pools (`replica28`) for large 20Tb+ drives used for backups.
- **Workloads:**
  - `ct:109` — Proxmox Backups Server (PBS) LXC
- **High Availability Workloads:**
  - `ct:101` — Technitium DNS Primary LXC
  - `ct:500` — Caddy Reverse Proxy LXC
  - `ct:502` — Jellyfin Media Server LXC
  - `ct:601` / `ct:602` / `ct:603` - Agentic Development Services
- **ZFS Boot Mirror:** requires some hard drive swaps documented in the on going [ZFS Boot Mirrors](/proxmox-zfs-boot-mirrors-part-4/) series.

---

## Pre-Flight Audit & Hardening Findings

A live audit of all six nodes uncovered several subtle issues that had to be addressed before embarking on a major OS upgrade:

### 1. Silent APT Repository Failures on `edgar` and `tanaka`
During recent node rebuilds, community post-install scripts on `edgar` and `tanaka` had left `/etc/apt/sources.list.d/ceph.list` entirely commented out. Both nodes were running Ceph Reef, but were silently unable to pull future package updates via `apt`.

**Fix:** Re-enabled the `ceph-reef bookworm no-subscription` repo line across both nodes and verified `apt update` resolution.

### 2. The Persistent Kernel Pin Mystery on `quell`
Node `quell` was stuck booting kernel `6.8.12-18-pve`, while the rest of the fleet had moved to `-30` or `-39`. Deleting `/etc/default/grub.d/proxmox-kernel-pin.cfg` and running `update-grub` initially failed—a test reboot still brought `quell` back on the old `-18` kernel.

**Root Cause:** Proxmox's `proxmox-boot-tool kernel pin` feature persists state in `/etc/kernel/proxmox-boot-pin` and automatically regenerates the GRUB configuration via the `zz-proxmox-boot` hook during package triggers.

**Fix:**
```bash
ssh quell "proxmox-boot-tool kernel unpin"
ssh quell "proxmox-boot-tool refresh"
```
A subsequent reboot confirmed `quell` booted kernel `6.8.12-30-pve` cleanly with full cluster quorum.

### 3. Cleanup of `systemd-boot` on Legacy GRUB Systems
Running `pve8to9 --full` flagged `systemd-boot` as unnecessary on legacy BIOS systems. It was purged across all 6 nodes without impacting GRUB functionality.

`pve8to9 --full` itself was run three separate times across this pre-flight work — once as the initial audit, once to confirm items 1-3 actually took effect, and once more after the LXC maintenance below. Given the kernel-pin lesson above (a fix that looked complete but silently wasn't), re-running the checker after every batch of changes rather than trusting a single clean run once was worth the extra few minutes each time.

### 4. Predictable Network Interface MAC Mapping
Because Debian 13 "Trixie" could theoretically alter device naming schemes, a physical MAC address table was compiled across all nodes:

| Node | vmbr0 (Public) | MAC | vmbr1 (SAN) | MAC |
|---|---|---|---|---|
| `harlan` | `enp0s25` | `18:03:73:d4:db:19` | `enp6s4` | `00:08:c7:73:22:19` |
| `kovacs` | `enp0s25` | `d4:be:d9:95:11:97` | `enp6s4` | `00:50:8b:68:d3:32` |
| `poe` | `enp0s25` | `5c:f9:dd:76:61:6d` | `enp6s4` | `00:03:47:b3:98:74` |
| `edgar` | `enp0s25` | `18:03:73:30:cc:a9` | `enp5s2f0` | `6c:b3:11:4c:cc:ec` |
| `tanaka` | `enp5s0` | `d4:be:d9:bd:c1:49` | `enp4s0f0` | `00:1b:21:38:43:a2` |
| `quell` | `enp0s25` | `18:03:73:c1:75:70` | `enp5s2f1` | `6c:b3:11:4b:2b:11` |

If an interface renames post-upgrade, matching physical MACs allows quick remediation in `/etc/network/interfaces`. This table gets put to real use verifying the network survived the jump in Part 2.

### 5. Pre-Upgrade LXC Container OS and Application Maintenance — the Real Story
LXC guest operating system distros do not need to be upgraded from Debian 12 to 13 before the PVE host upgrade. However, updating userspace packages (such as `systemd` and base tools) inside existing LXCs ensures smooth compatibility with the newer host kernel.

The obvious approach — Community Scripts' `update-lxcs.sh` — turned out to have a real gap. Pulling the actual script source (not just trusting a summary of what it does) showed all three of its `whiptail` dialogs — initial confirm, skip-not-running, container-exclusion checklist — are unconditional. There is no environment-variable bypass for this script, and a sandboxed remote shell can't supply whiptail a real TTY even with `ssh -t`.

The real answer was a separate, purpose-built worker script normally installed by a different helper (`cron-update-lxcs.sh`) for scheduled runs: `update-lxcs-cron.sh`. Verified via source to have zero interactive dependencies, it does exactly what's needed — iterate every container, run the OS-appropriate update command (`apt-get update && dist-upgrade` for Debian-based, with `DEBIAN_FRONTEND=noninteractive`), starting and stopping containers as needed:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/tools/pve/update-lxcs-cron.sh)"
```

`update-apps.sh` (application-*version* updates, as opposed to OS packages), by contrast, does support proper unattended env vars:

```bash
var_backup=yes var_backup_storage=local var_container=all_running var_unattended=yes var_skip_confirm=yes var_auto_reboot=no \
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/tools/pve/update-apps.sh)"
```

Only `ct:101` (Technitium DNS) is actually tagged as community-script-managed, so it was the only container this pass touched — the rest were correctly skipped, not broken, since the tool has no safe update path for anything it didn't install itself.

Since `pct exec`/`pct list` are node-scoped, `update-lxcs-cron.sh` had to be run once per node actually hosting containers (poe, kovacs, quell, harlan) — not once cluster-wide.

**An unplanned find along the way:** a slow, 161-package update on one of two identically-named `jellyfin` containers on `harlan` (`ct:501` and `ct:502`) prompted a closer look at why. Comparing their configs showed `501` was an explicit prior generation of `502` — tagged `deprecated`, set to not start on boot, and sharing a MAC address with `502` specifically so the two could never run at once. After confirming it carried no HA dependency and its rootfs was a private volume separate from the CephFS mounts both containers reference, it was destroyed — freeing 22GB from the `cephrbd` pool.

**Also added, prompted by this exercise rather than the upgrade itself:** a persistent weekly cron job (`update-lxcs-cron.sh` plus a matching `/etc/update-lxcs.conf`) installed on all 6 nodes — including the two hosting no containers today — as a hedge against Proxmox HA someday relocating a workload to a node that's never had this maintenance run before.

---

## Phase 0: Building the Safety Net (PBS & Off-Cluster Backups)

To safeguard HA guest data during a multi-day maintenance window, a Proxmox Backup Server (PBS) instance was provisioned — as an LXC container on `edgar`, via the [Community Scripts helper](https://community-scripts.org/scripts/proxmox-backup-server), not a QEMU VM. That choice was easy. Two other decisions took real diligence to get right, because an earlier internal plan had already answered them differently, on paper, without anyone confirming the answers still held.

**Storage architecture.** The earlier plan called for passing the entire USB drive through to the PBS LXC as a raw block device, letting the container import and own the ZFS pool itself. The decision made here goes the other way: **edgar, the host, creates and owns the `replica28/pbs` dataset**, bind-mounted into the container via a plain `mp0` line. The reason is concrete, not aesthetic — a separate piece of this same safety-net work (refreshing a stale, several-months-old CephFS backup copy) depends on `zfs send`/`receive` running directly on the host, between `quell` and `edgar`. Handing the whole USB drive to a container would take that pool out of the host's hands and break it.

**Network address and VMID.** A candidate IP was already written down in that same earlier plan, but nothing had actually confirmed it was still free months later. Rather than trust old paper, the full `/23` got cross-referenced three independent ways: every Proxmox node and container config, a live ARP table dump, and an actual `nmap -sn` sweep of all 512 addresses. All three agreed that `192.168.86.9` — deliberately chosen to sit right before `.10`/`.11`, the first Proxmox node — was genuinely unused. The container itself landed on VMID `109`, a deliberate exception to a proposed VMID range convention (backups were slated for an `800-899` block) made because `109` still reads clearly as core infrastructure and matches a much older reservation that predates the new scheme.

```bash
# On edgar — the host owns the dataset
zfs create -o quota=8T replica28/pbs
mkdir -p /replica28/pbs/datastore

# The container itself, via the Community Scripts helper
# (interactive by design — no unattended bypass exists for LXC creation)
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/ct/proxmox-backup-server.sh)"

# Bind-mount the dataset in, once the container exists
pct set 109 -mp0 /replica28/pbs/datastore,mp=/mnt/datastore
```

**Three real issues, found by actually trying it, not by reading the docs:**

1. **The post-install script URL in the original plan was wrong.** `misc/post-pbs-install.sh` returns a 404 — the real path, confirmed via the GitHub API rather than guessing again, is `tools/pve/post-pbs-install.sh`.
2. **Root login to the PBS web UI didn't work.** `passwd -S root` inside the fresh container showed `root L` — locked, no password at all. Community-scripts LXC templates expect access via `pct enter`/`pct exec` from the host, not a password, so PBS's `root@pam` realm (which authenticates against the container's real PAM database) had nothing to check against. Fixed by setting a root password directly in the container.
3. **`EPERM` on the first datastore-create attempt.** The dataset's host-side ownership had been set with the *raw* host UID 34 — but this is an **unprivileged** container, where host UIDs are shifted by the container's subuid/subgid mapping (`root:100000:65536` here, confirmed via `/etc/subuid`). Container UID 34 (the `backup` user PBS runs as) actually needed **host UID 100034**. Once ownership was corrected, the chunkstore initialized cleanly.

**Cluster integration used a dedicated API token, not the root password directly:**
```bash
proxmox-backup-manager user generate-token root@pam pve-cluster --comment 'PVE cluster backup integration'
proxmox-backup-manager acl update /datastore/main DatastoreAdmin --auth-id 'root@pam!pve-cluster'
```
Then registered cluster-wide with `pvesm add pbs`, confirmed active at roughly 8TB capacity matching the dataset quota.

**The first real backup run** covered all 6 HA-managed containers (`101`, `500`, `502`, `601`, `602`, `603`) — all succeeded, with useful incremental dedup already kicking in on the very first run. Speeds ranged 7.8-13.4 MiB/s, which prompted a closer look: not the USB interface (confirmed at full USB 3.0 SuperSpeed, `5000 Mbps`, via `lsusb -t`), and not a slow drive class either (`smartctl` identifies it as a 7200 RPM, 3.5" desktop unit). At 28TB, this drive is almost certainly **SMR** (shingled magnetic recording) — the only way consumer drives reach that density — and SMR's known weakness is exactly this workload: PBS writes its datastore as thousands of discrete ~4MB chunk files rather than one sequential stream, which triggers costly read-modify-write cycles inside SMR's shingled zones. A second NIC was added to the container on the dedicated SAN network (`10.10.10.9`, confirmed reachable from all 6 nodes) in case rerouting backup traffic there would help — but given the bottleneck is the drive's write pattern rather than network capacity, it likely won't move the needle much on its own.

**A fourth real issue, found two days later during routine patching, not the upgrade itself:** a fleet-wide reboot to pick up the latest PVE 8.4.x kernel (`6.8.12-41-pve`, unrelated to this project's own upgrade work) left CT 109 stopped. `journalctl` on edgar told the whole story in an 8-second window: the kernel found the USB drive at `19:59:31`, but `zfs-import-cache.service` — a one-shot that runs early in boot — checked for importable pools one second later and found none, since the drive hadn't finished settling yet. `zfs-import.target` reported "active" anyway (root's `rpool` was already mounted by the initramfs, so nothing in the default boot chain was actually waiting on `replica28`). `pve-guests.service` made its one and only startup attempt at `19:59:44`, found CT 109's `mp0` bind-mount source missing, and gave up. `replica28` finished importing at `19:59:57` — 8 seconds too late, and `pve-guests.service` doesn't retry. CT 109 sat stopped for nearly three hours until a manual start from the web UI.

The fix: a small systemd oneshot (`replica28-import-wait.service`) ordered `Before=pve-guests.service` that polls for the pool to actually mount, capped at 60 seconds, paired with a `pve-guests.service.d` drop-in adding `Wants=`+`After=` on it — deliberately a soft dependency (`Wants=`, not `Requires=`), so one slow USB drive can never block every *other* guest on the host from starting if the wait ever times out. It's the same category of problem as the USB-OSD timing issue below — enumeration speed racing boot-time service ordering — just hitting a different unit this time.

---

## Phase A: Ceph Reef (18.2.8) → Ceph Squid (19.2.x) Upgrade

Proxmox requires upgrading Ceph across all nodes **before** performing the OS upgrade to Proxmox VE 9. The first pass at this plan restarted every monitor, manager, and OSD host in one continuous, cluster-wide sweep — a real risk given the Sandy Bridge/no-AVX2 watch item flagged back at the top of this post. If Squid genuinely didn't run cleanly on this hardware, that design would find out by potentially taking down mon quorum and OSD availability everywhere at once. It got restructured to add a canary stage, the same discipline Part 2's OS upgrade already uses.

That fixed the daemon-restart risk, but a second look turned up a quieter version of the same problem: the original plan still flipped every node's `ceph.list` to Squid and upgraded every node's Ceph packages **up front, across all 6 nodes**, before a single daemon had actually proven Squid works on this hardware. Nothing gets restarted at that point, so it's not a runtime risk — but it does mean every node is sitting there with Squid packages installed and its repo already pointed at Squid before the canary has said anything. If the canary *had* turned up a real problem, "roll back" would have meant re-pointing and downgrading all 6 nodes, not just the 2 that were actually touched. The fix: fold the repo flip and package upgrade into each node's own turn, so nothing about a node's Ceph install changes until it's specifically that node's turn to go.

### 1. Set Cluster Safety Flags
```bash
ssh poe "ceph osd set noout; ceph osd set nobackfill"
```
This is a cluster-wide OSD map flag, not a package or repo change, so it's the one thing that's genuinely safe to set fleet-wide up front. It stays set through the entire staged process below.

### 2. Canary Stage 1 — `tanaka`: Flip Repo, Upgrade Packages, Restart Mon+Mgr
Isolated to this one node — no other node's `ceph.list` or Ceph packages get touched yet. No OSDs on tanaka, making it the simplest possible test of whether Squid's mon/mgr code runs cleanly on Sandy Bridge. Using a detached `tmux` session so `apt full-upgrade` survives a dropped SSH connection:
```bash
ssh tanaka "sed -i 's/ceph-reef bookworm no-subscription/ceph-squid bookworm no-subscription/' /etc/apt/sources.list.d/ceph.list; apt update"
ssh tanaka "tmux new -d -s ceph-upgrade 'apt full-upgrade -y ceph ceph-common ceph-mds ceph-mgr ceph-mon ceph-osd ceph-mgr-dashboard; echo DONE > /root/ceph-upgrade-status'"
# poll /root/ceph-upgrade-status until DONE, then:
ssh tanaka "systemctl restart ceph-mon@tanaka ceph-mgr@tanaka"
ssh poe "ceph -s; ceph versions"   # tanaka now squid; every other node still fully on reef, repo AND packages — expected
```

### 3. Canary Stage 2 — `quell`: Same Pattern, Plus OSDs
The OSD-host canary, chosen deliberately: standard internal SATA/SSD OSDs with no known fragility, and already the first node verified elsewhere in this project. Deliberately *not* `edgar` — its USB-backed OSDs already have a known quirk (more on that below), and testing Squid there first would make it impossible to tell a real Squid problem apart from the existing USB issue. Still isolated to quell only:
```bash
ssh quell "sed -i 's/ceph-reef bookworm no-subscription/ceph-squid bookworm no-subscription/' /etc/apt/sources.list.d/ceph.list; apt update"
ssh quell "tmux new -d -s ceph-upgrade 'apt full-upgrade -y ceph ceph-common ceph-mds ceph-mgr ceph-mon ceph-osd ceph-mgr-dashboard; echo DONE > /root/ceph-upgrade-status'"
# poll until DONE, then:
ssh quell "systemctl restart ceph-mon@quell ceph-mgr@quell"
ssh quell "systemctl restart 'ceph-osd@*'"
ssh poe "ceph -s"   # HEALTH_OK (mod the flags above) — quell's 3 OSDs up/in on squid, no flapping
```

**Gate:** only once both canaries are confirmed clean does the rest of the cluster proceed — the same explicit go/no-go discipline Part 2 uses before its own batch rollout. At this point the remaining 4 nodes haven't had their `ceph.list` touched at all, so a real problem is contained to exactly the 2 canary nodes, at the package level as well as the daemon level.

### 4. Remaining Nodes, One at a Time — `edgar` Last
Each of the remaining 4 nodes gets its own repo flip, package upgrade, and full daemon restart — verified healthy — before the *next* node's repo is touched at all. `harlan`, `kovacs`, `poe` first, then `edgar` last, so its USB-backed OSDs (`osd.1`/`osd.4`/`osd.7`) get the extra scrutiny they'll get again in Part 2:
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
By this point every node is already on Squid packages, so a fleet-wide pass here is fine:
```bash
for n in harlan kovacs poe edgar tanaka quell; do
  ssh $n "systemctl restart ceph-mds@\$(hostname)"
  ssh poe "ceph fs status; ceph -s"
done
```

### 6. Unset Flags, Final Verification
```bash
ssh poe "ceph osd unset nobackfill; ceph osd unset noout
ceph versions   # expect squid everywhere, zero reef stragglers
ceph -s         # HEALTH_OK"
```

---

## Key Takeaways from Pre-Flight

1. **Never Assume APT Repository State:** Always audit `/etc/apt/sources.list.d/` manually before upgrades. Silent repo disablers can leave nodes stranded on old packages.
2. **Respect `proxmox-boot-tool`:** Don't manually edit GRUB files or remove `/etc/default/grub.d/` entries when kernel pins are active — always use `proxmox-boot-tool kernel unpin` and `refresh`.
3. **Pull the Actual Script Source, Not a Summary of It:** A helper script's documented behavior and its real behavior can diverge — `update-lxcs.sh` looked like it supported unattended runs until its actual source showed otherwise, and the same pattern repeated later with a wrong post-install script URL.
4. **Re-Verify Old Plans Against Current Reality:** A pre-existing backup plan had the right instinct but a stale IP and a storage architecture nobody had re-checked against what the cluster actually needed months later. Written plans decay; the systems they describe keep changing underneath them.
5. **Stage Risky Restarts, Even Within a Single Subsystem:** The same canary discipline that makes sense for an OS upgrade applies just as much to a hyper-converged storage layer's own version jump — a cluster-wide daemon restart sweep is still a single point of failure, even if every individual command is well-tested.
6. **Boot-Time Service Ordering Doesn't Know About Late-Arriving USB Devices:** `pve-guests.service` gets exactly one startup pass, and nothing in the default boot chain waits for a second, non-root ZFS pool to actually finish importing before that pass runs. Any guest with storage on a USB-attached pool needs its own explicit wait-gate — the fix is cheap, but only if you know to look for it before the next reboot, not after.

With pre-flight complete, a real backup safety net in place, and Ceph already sitting on Squid, the cluster is as ready as it can be without actually touching the Proxmox OS itself. **[Part 2](/proxmox-8-to-9-cluster-upgrade-part-2/)** covers the canary node, the batch rollout, and — hopefully — a clean bill of health at the end.
