---
title: "Proxmox VE 8 to 9 Cluster Upgrade: Moving 'AlteredCarbon' to Ceph Squid and Debian Trixie"
layout: post
categories: ["homelab", "proxmox", "infrastructure"]
tags: ["proxmox", "ceph", "squid", "debian", "trixie", "zfs", "homelab", "upgrade", "cluster", "backup", "pbs"]
---

Upgrading a live, multi-node hyper-converged homelab cluster is equal parts software engineering, operational discipline, and risk management. My 6-node Proxmox VE cluster—codenamed **AlteredCarbon** (`harlan`, `kovacs`, `poe`, `edgar`, `tanaka`, and `quell`)—runs a combination of ZFS root boot mirrors, Ceph storage (Reef 18.2.8), and High Availability (HA) LXC workloads.

With Proxmox VE 9 (built on Debian 13 "Trixie" and Ceph 19.2 "Squid") now available, it is time to move the cluster forward. However, upgrading a cluster with **no out-of-band management** (no IPMI, iDRAC, or PiKVM) on aging Dell OptiPlex 990 hardware (Sandy Bridge i7-2600 CPUs) requires a battle-tested execution plan where every risk is audited and every rollback path is verified before touching production workloads.

Here is the complete architectural strategy, pre-flight hardening checklist, and step-by-step rollout plan for upgrading AlteredCarbon from Proxmox VE 8.4.19 to Proxmox VE 9.

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
- **Compute & Architecture:** Legacy BIOS / GRUB boot with ZFS root boot mirrors across all 6 nodes (UEFI is non-viable on this Dell OptiPlex 990 family; see prior boot drive post). Sandy Bridge i7-2600 processors without AVX2 support.
- **Storage:** Ceph Reef (18.2.8) across 15 OSDs (5 hosts), with a mix of internal SATA SSDs and external USB-backed ZFS pools (`replica28`).
- **High Availability Workloads:**
  - `ct:101` — Technitium DNS Primary
  - `ct:500` — Caddy Reverse Proxy
  - `ct:502` — Jellyfin Media Server
  - `ct:601` / `ct:602` / `ct:603` — Ceph Core Services

![ZFS Boot Mirror Status - Node Baseline](/assets/images/zfs-boot-mirror-proxmox8-001.png)

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

![ZFS Boot Mirror Status - Cluster Baseline](/assets/images/zfs-boot-mirror-proxmox8-002.png)

### 3. Cleanup of `systemd-boot` on Legacy GRUB Systems
Running `pve8to9 --full` flagged `systemd-boot` as unnecessary on legacy BIOS systems. It was purged across all 6 nodes without impacting GRUB functionality.

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

If an interface renames post-upgrade, matching physical MACs allows quick remediation in `/etc/network/interfaces`.

### 5. Pre-Upgrade LXC Container OS and Application Maintenance
LXC guest operating system distros do not need to be upgraded from Debian 12 to 13 before the PVE host upgrade. However, updating userspace packages (such as `systemd` and base tools) inside existing LXCs ensures smooth compatibility with the newer host kernel. Using Community Scripts, LXC OS packages and apps are refreshed fleet-wide prior to host upgrade:
```bash
# Update base OS packages across LXC containers
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/tools/pve/update-lxcs.sh)"

# Update containerized application stacks
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/tools/pve/update-apps.sh)"
```

---

## Phase 0: Building the Safety Net (PBS & Off-Cluster Backups)

To safeguard HA guest data during a multi-day maintenance window, a Proxmox Backup Server (PBS) instance is provisioned on `edgar`.

### Option A: Proxmox Helper Script LXC (Recommended for Homelab Efficiency)
1. **PBS Dataset Allocation:** Create an 8TiB dataset (`replica28/pbs/datastore`) on `edgar`'s ZFS USB pool.
2. **Automated LXC Deployment:** Deploy PBS inside a lightweight LXC container using the [Community Script `proxmox-backup-server.sh`](https://community-scripts.org/scripts/proxmox-backup-server).
3. **Storage Bind-Mount:** Add `mp0: /replica28/pbs/datastore,mp=/mnt/datastore` to `/etc/pve/lxc/9000.conf` to mount the ZFS pool directly into the container.

### Option B: PBS in QEMU VM (Full Official Support Reference)
For official support standards, PBS can also be provisioned in a QEMU VM (`qm create 9000`) with an 8TB virtual disk mapped from `pbs-datastore`.

### Initial Backup Execution:
1. **Cluster Integration:** Register `pbs-backup` cluster-wide in Proxmox (`pvesm add pbs ...`).
2. **Full Guest Snapshot:** Run a full vzdump snapshot backup of all active containers (`ct:101`, `500`, `502`, `601`, `602`, `603`).
3. **CephFS Off-Cluster Replication:** Refresh CephFS backup snapshots on `quell`'s USB ZFS pool (`replica`) and transfer incremental deltas to `edgar`'s `replica28/replica` pool.

---

## Phase A: Ceph Reef (18.2.8) → Ceph Squid (19.2.x) Upgrade

Proxmox requires upgrading Ceph across all nodes **before** performing the OS upgrade to Proxmox VE 9.

### 1. Update Repository Configurations
Flip `ceph.list` on all 6 nodes to point to `ceph-squid`:
```bash
for n in harlan kovacs poe edgar tanaka quell; do
  ssh $n "sed -i 's/ceph-reef bookworm no-subscription/ceph-squid bookworm no-subscription/' /etc/apt/sources.list.d/ceph.list
  apt update"
done
```

### 2. Set Cluster Safety Flags
```bash
ssh poe "ceph osd set noout; ceph osd set nobackfill"
```

### 3. Rolling Upgrade of Ceph Packages
Using detached `tmux` sessions ensures `apt full-upgrade` survives temporary SSH disconnections:
```bash
for n in harlan kovacs poe edgar tanaka quell; do
  ssh $n "tmux new -d -s ceph-upgrade 'apt update && apt full-upgrade -y ceph ceph-common ceph-mds ceph-mgr ceph-mon ceph-osd ceph-mgr-dashboard; echo DONE > /root/ceph-upgrade-status'"
done
```

### 4. Sequential Daemon Restarts & Verification
Restart daemons in strict order, verifying health between steps:
1. **Monitors (`ceph-mon`):** Restart host-by-host across all 6 nodes, confirming quorum after each.
2. **Managers (`ceph-mgr`):** Restart host-by-host, confirming active/standby failover.
3. **OSDs (`ceph-osd`):** Restart OSDs host-by-host across `harlan`, `kovacs`, `poe`, `edgar`, and `quell`. Wait for `HEALTH_OK` before proceeding to the next host.
4. **Metadata Servers (`ceph-mds`):** Restart across all nodes.
5. **Unset Flags:** Clear `noout` and `nobackfill`, confirming `ceph versions` reports Squid fleet-wide.

---

## Phase B: Canary Node Upgrade (`tanaka` → PVE 9 / Trixie)

Node `tanaka` has no Ceph OSDs and is HA-idle, making it the ideal canary node.

### 1. Testing the Rollback Mechanism
Before upgrading, the ZFS root snapshot rollback procedure was validated hands-on:
1. Created snapshot: `zfs snapshot rpool/ROOT/pve-1@rollback-test`.
2. Created a test marker file and installed a temporary test package.
3. Booted into the Proxmox 8.4 ISO Debug/Rescue shell, imported `rpool`, ran `zfs rollback -r rpool/ROOT/pve-1@rollback-test`, and exported `rpool`.
4. Booted back into PVE 8.4 and confirmed the marker file and package were completely reverted while cluster state remained clean.

### 2. Executing the Canary Upgrade
1. Take a fresh pre-upgrade snapshot: `zfs snapshot rpool/ROOT/pve-1@pre-v9-upgrade`.
2. Update APT repositories from `bookworm` to `trixie` in `/etc/apt/sources.list.d/pve-install-repo.list` and `ceph.list`.
3. Perform the OS upgrade inside `tmux`:
   ```bash
   tmux new -d -s pve9-upgrade 'apt update && apt full-upgrade -y; echo DONE > /root/pve9-upgrade-status'
   ```
4. Reboot into the new Trixie kernel (`6.12+`) on-site.
5. Verify node health: `pveversion -v`, `zpool status`, `pvecm status`, and Ceph cluster re-join.

---

## Phase C: Sequential Batch Upgrade of Remaining Nodes

Once `tanaka` passes its 48-hour canary soak test, the remaining 5 nodes are upgraded sequentially in the following order:

1. **`quell`** — Confirms compatibility with the Trixie kernel now that its kernel pin is removed.
2. **`poe`** — Standard OSD host upgrade.
3. **`kovacs`** — Standard OSD host upgrade.
4. **`harlan`** — Standard OSD host upgrade.
5. **`edgar`** — Upgraded last due to its USB-backed OSDs (`osd.1`, `osd.4`, `osd.7`).

### Per-Node Execution Workflow
For each node:
1. **Relocate Workloads:** Live-migrate or relocate HA LXC containers to peer nodes (`ha-manager migrate ct:<id> <peer>`).
2. **Take ZFS Root Snapshot:** `zfs snapshot rpool/ROOT/pve-1@pre-v9-upgrade`.
3. **Upgrade & Reboot:** Flip repositories to `trixie`, run `apt full-upgrade` via `tmux`, and reboot on-site.
4. **`edgar`-Specific USB Check:** Verify `usb_storage.quirks` kernel parameter is active, verify all 4 USB drives via `lsblk`, run `smartctl` health checks, and confirm all 3 USB OSDs rejoin `ceph osd tree` cleanly.

---

## Phase D & E: Final Verification & Infrastructure Documentation

After the final node passes verification:

```bash
# Verify versions across all nodes
for n in harlan kovacs poe edgar tanaka quell; do ssh $n "pveversion -v | head -3"; done

# Verify cluster quorum & Ceph health
ssh poe "ceph -s; ceph versions; pvecm status"
```

Once all nodes report `PVE 9.x`, `Ceph 19.2 Squid`, and `HEALTH_OK`, the pre-upgrade ZFS snapshots are destroyed, documentation (`CLUSTER-SUMMARY.md` and `BOOT-DRIVE-ANALYSIS.md`) is updated, and normal operations resume.

## Key Takeaways for Proxmox Upgrades

1. **Never Assume APT Repository State:** Always audit `/etc/apt/sources.list.d/` manually before upgrades. Silent repo disablers can leave nodes stranded on old packages.
2. **Respect `proxmox-boot-tool`:** Don't manually edit GRUB files or remove `/etc/default/grub.d/` entries when kernel pins are active—always use `proxmox-boot-tool kernel unpin` and `refresh`.
3. **Test Your Rollback Paths First:** A ZFS boot snapshot is only a safety net if you have verified the rescue shell rollback workflow beforehand.
4. **Respect Out-of-Band Realities:** When nodes lack IPMI/BMC management, schedule OS reboots only when physical access to the hardware is available.

With a methodical, phase-gated plan, even complex hyper-converged homelab clusters can transition seamlessly to Proxmox VE 9.
