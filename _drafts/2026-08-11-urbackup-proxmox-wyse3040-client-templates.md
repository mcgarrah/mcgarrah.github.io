---
layout: post
title: "One UrBackup Server, Three Very Different Clients: Proxmox, Wyse 3040, and the Gaps Between Them"
image: /assets/images/og/urbackup-proxmox-wyse3040-client-templates.png
categories: [technical, homelab, infrastructure]
tags: [homelab, proxmox, ceph, backup, zfs, lvm, debian, dell-wyse-3040, python, api, automation, troubleshooting, vpn]
excerpt: "Ceph and Proxmox Backup Server cover the virtual estate well. Neither backs up the bare-metal hosts underneath them, or the thin clients running the site-to-site VPN and DNS at the edge. Standing up UrBackup as a shared server for both surfaced a genuinely different failure mode per client type — and one assumption about LVM that turned out to be wrong."
description: "Deploying UrBackup as a shared backup server for a mixed fleet: six ZFS-root Proxmox VE cluster nodes and a resource-constrained Dell Wyse 3040 thin-client fleet. Covers the LXC deployment (unprivileged rebuild, the same UID-mapping gotcha Proxmox Backup Server hit), why Veeam was ruled out for LXC-heavy environments, an exponential-backoff trap solved via UrBackup's undocumented-but-real HTTP API, a wrong assumption about LVM image backup corrected by checking actual volume-group free space, two reusable shell-script templates published for reuse, and why a remote site behind a site-to-site VPN needed UrBackup's internet mode instead of its default LAN discovery."
date: 2026-08-11
last_modified_at: 2026-08-12
seo:
  type: BlogPosting
  date_published: 2026-08-11
  date_modified: 2026-08-12
---

Ceph replicates the data. Proxmox Backup Server images the VMs and containers. Between the two, the virtual estate on the "AlteredCarbon" cluster is well covered. Neither of them backs up anything else — not the six Proxmox hosts' own OS and cluster config, and not the Dell Wyse 3040 thin clients running DNS secondary and the Tailscale VPN gateway at each site. If a Proxmox node's boot drive dies, or a Wyse 3040 at a remote site does, the recovery plan was "reconfigure it by hand from memory." That's the gap this closes: one shared UrBackup server, covering both a six-node ZFS-root Proxmox cluster and a resource-constrained Atom-based thin-client fleet — two categories of client with almost nothing in common except both needing *something*.

<!-- excerpt-end -->

## Why Not Just Extend What Already Exists

Two existing tools looked like obvious extensions before UrBackup got picked specifically.

**Veeam** has a real, current Proxmox VE integration (Backup & Replication 12.2+, free Community Edition) plus a bare-metal Linux agent — genuinely a single vendor covering both physical and virtual. It's disqualified for this cluster for one specific reason, confirmed against Veeam's own current documentation rather than assumed: **its Proxmox plugin doesn't back up LXC containers, only KVM VMs.** This cluster is almost entirely LXC — DNS, Caddy, Homarr, Jellyfin, the dev-service containers, even the backup infrastructure itself. Veeam would leave nearly the whole virtual estate uncovered at the hypervisor level. Ruled out on a factual gap, not a preference.

**Proxmox Backup Server** was the other candidate — already deployed, already trusted, and `proxmox-backup-client` genuinely does support standalone file/directory backups from any Linux host, not just Proxmox VM/CT images. That's a real, usable path. What it doesn't do is bare-metal image backup with a bootable restore path, which matters for the Wyse 3040 fleet specifically — a thin client's whole value is being trivially replaceable, and getting there from a dead unit means either a fast image restore or a slow from-scratch rebuild. UrBackup does both image and file backup from one tool, on an actual schedule, from a single web console across many clients — the combination PBS alone doesn't offer.

## The Server: Same LXC Gotchas, Different Container

`ct:108`, deployed via the [community-scripts](https://github.com/community-scripts/ProxmoxVE) `urbackupserver` helper — colocated with the existing Proxmox Backup Server LXC (`ct:109`) on the same host, sharing the same 28TB USB-attached ZFS pool via its own dataset, split evenly at 4TB/4TB. PBS was using 13.5GB of its original 8TB quota at the time, so the resize was about tidy provisioning, not disk pressure.

Two things went wrong in ways that were productive rather than just annoying.

**First install came up privileged.** The community script's own default is `var_unprivileged="${var_unprivileged:-0}"` — checked directly in the script source, and there's no comment explaining why. Every other service LXC on this cluster runs unprivileged, including PBS, which needs the same FUSE capability UrBackup does. Destroyed the container and re-ran with `export var_unprivileged=1` set. Cheap fix, but only because it got caught before any real data landed on it — privileged-vs-unprivileged isn't something you change after the fact without recreating the container.

**Then the exact same permission bug Proxmox Backup Server hit, for the exact same reason.** Unprivileged LXCs shift UIDs by a fixed offset (`root:100000:65536` here) — container UID 0 maps to host UID 100000, and so on up the range. The bind-mounted storage directory was owned by raw host UID 0, which falls *outside* that mapped range entirely from the container's point of view — it showed up as `nobody:nogroup` inside the container, and the UrBackup service (running as its own `urbackup` user, UID 103 inside the container) couldn't write to its own storage path. Same arithmetic as the PBS fix months earlier: `chown 100103:100106` on the host side — container UID/GID plus 100000. Confirmed with a manual write test as the `urbackup` user before trusting it, then a clean service restart with nothing in the log.

Worth naming directly: this is now the second time this exact bug has cost real troubleshooting time on this cluster. Any future bind-mount into an unprivileged container should get this check *before* the first write attempt, not after watching a permission error in a log file.

## Proxmox Nodes: What ZFS Root Rules Out, and What's Worth Backing Up Instead

The Proxmox cluster nodes all boot from ZFS root mirrors — a deliberate, documented architectural choice on this hardware, unrelated to UrBackup. It has one consequence worth knowing up front: **UrBackup's Linux image backup only works against LVM or btrfs snapshots.** ZFS isn't in that list. No Proxmox node in this cluster will ever get image-level backup through UrBackup, and that's expected, not a misconfiguration to chase.

File-level backup doesn't have that dependency, and it's genuinely the more valuable tier here anyway — the actual bulk data (Ceph OSDs, CephFS content) is already triple-replicated by Ceph itself and doesn't need a second copy through a completely different backup path. What's worth protecting is the config that's small but expensive to reconstruct by hand:

```bash
urbackupclientctl add-backupdir -d /etc -n etc-config
urbackupclientctl add-backupdir -d /var/lib/pve-cluster -n pve-cluster-state
```

`/etc` covers ordinary Debian config, but it also covers `/etc/pve` — Proxmox's own cluster filesystem (`pmxcfs`), FUSE-mounted at that exact path. VM/CT configs, `corosync.conf`, `storage.cfg`, `ceph.conf` all live there as real, readable files through the mount, and a plain file-level backup tool walks right through it without needing to know it's anything special. Confirmed by actually checking the backed-up content afterward, not assuming it worked: `ceph.conf`, the cluster's `authkey`, and a site-to-site VPN routing script from earlier infrastructure work all round-tripped correctly. `/var/lib/pve-cluster` is the small local database backing that same mount.

Nothing here overlaps with `/var/lib/ceph` (OSD data — 12MB of local metadata, not the real bulk storage, which OSDs access directly via raw block device) or `/mnt/pve/cephfs` (the actual media mount). That's not an exclude-rule doing the work — it's just that neither bulk-data path lives anywhere under `/etc` or `/var/lib/pve-cluster` to begin with. A two-directory allowlist, verified against the real filesystem layout rather than assumed, turned out to be the whole solution.

One more deliberate choice: **no `--separate-hashes` flag.** UrBackup shares content hashes across all clients by default unless told not to. Six Proxmox nodes running the same Debian base with the same Proxmox packages are, for backup purposes, mostly clones of each other — leaving hash sharing on means the bulk of `/etc`'s content deduplicates automatically across the fleet the moment more than one node is backed up. No extra configuration, just not turning off something already on by default.

## The Trap: Exponential Backoff, and Finding the API by Accident

The first real client pilot ran against `harlan` — a Proxmox node, deliberately not a Wyse 3040 — specifically to validate the server end-to-end without also depending on a not-yet-fully-tested site-to-site VPN route to a remote thin client. Good call, because it immediately surfaced something that would have been much more annoying to debug on a remote box.

UrBackup's server attempts a backup automatically the moment a client is added. At that point no backup directories were configured yet, so it failed — twice, a few seconds apart — with "no backup dirs." Reasonable so far. What's not obvious: **UrBackup's own exponential backoff logic then suppressed the next automatic attempt for over an hour**, and adding the missing backup directory afterward didn't clear it. The scheduler just waits out its own timer regardless of whether the original cause got fixed.

Digging for a way around this surfaced something worth knowing generically, not just for this one incident: **UrBackup has a real JSON HTTP API**, the same one its own web UI uses internally, reachable at `/x` on the server. A community-maintained Python wrapper (`urbackup-server-web-api-wrapper` on PyPI) makes it trivial:

```python
from urbackup_api import urbackup_server_typed, BackupType

server = urbackup_server_typed("http://192.168.86.8:55414/x", "automation", "<password>")
server.login()
server.get_clients()                                    # -> [ClientInfo(id, name), ...]
server.start_backup([client_id], BackupType.FULL_FILE)   # start_ok=True
```

An API-triggered start bypasses the scheduler's backoff the same way a manual "start now" click in the web UI would — same underlying mechanism, just scriptable. Confirmed the fix worked by watching the backup actually complete and checking the resulting files on disk, not just trusting a success flag.

## Wyse 3040: A Wrong Assumption, Corrected by Actually Checking

Going in, the working assumption was that the Wyse 3040 fleet — LVM-formatted, unlike the Proxmox nodes' ZFS root — would support UrBackup's image backup where the Proxmox nodes couldn't. That assumption was wrong, and it only got caught by actually running the check rather than reasoning from "LVM is the right filesystem type in principle":

```
$ vgs
  VG              #PV #LV #SN Attr   VSize VFree
  wyse3040-ral-vg   1   2   0 wz--n- 6.30g    0
```

`VFree 0`. The entire volume group is fully allocated between the root and swap logical volumes — nothing left over for LVM to actually create a snapshot with. UrBackup's image backup depends on that snapshot as its consistent source; with zero free extents, `lvcreate --snapshot` fails outright regardless of the underlying filesystem being LVM at all. Checked a second unit at a different physical site (`wyse3040-ei`) to see if this was a one-off — identical layout, identical `VFree 0`. It's the standard provisioning image for this hardware, not a fluke on one box. File-level backup doesn't share that dependency and remains fully viable; image backup on this specific hardware, in its current state, doesn't.

The install process itself surfaced a second, smaller lesson about environment sensitivity: run non-interactively over a piped SSH command (as happened for the Proxmox nodes), the installer detects the missing TTY and silently proceeds with defaults, skipping any prompts entirely. Run with a genuine interactive terminal — `sudo su -` at the console, as was done for both Wyse units — it presents its full menu, including an explicit snapshot-method choice. "No snapshot" was the correct pick given the `VFree 0` finding, and choosing it up front avoided ever configuring a code path that was destined to fail.

One more real gotcha, this one taking considerably longer to actually close: the interactive install self-registered against the server directly (unlike the non-interactive Proxmox installs, which needed a manual "Add Client" via the web UI). For the on-site unit this worked cleanly. For the remote unit — reachable only through a site-to-site WireGuard tunnel, via a GL.iNet Brume 2 at that site and a Brume 3 back at the primary one — registration didn't just fail once, it stayed broken through several rounds of troubleshooting before the actual cause turned up.

## The Remote Site: Why a Second Fix Was Needed, and How It Was Actually Found

The first theory was a routing gap — the server's own outbound route to the remote subnet didn't exist yet when the first registration attempt happened, so of course it failed. Fair theory, and it was real: `ct:108` genuinely needed the same outbound route to the remote site that `ct:109` (PBS) had already needed for a different remote site earlier. Adding it was a five-minute fix. It also didn't solve the problem — the client record stayed broken after the route was in place, which meant the routing gap had only ever been part of the story.

The web UI's Status page has a "Client discovery hints" table that looked like the obvious next step — it showed the remote IP, with an Online column flapping between Yes and No. It has no working "Add" action, only "Remove." A real dead end, not a step that eventually works if you retry it enough times — confirmed by actually trying, not assumed from the UI looking unfinished.

The real "Add new client" button is a separate control on the main Status page. Using it did create a client record, but for this specific client, the record stayed stuck: empty client UID, a non-standard status code, and — misleadingly — `online: True` showing the *wrong* IP, the Raleigh Brume gateway's address rather than the remote unit's own. That turned out to be expected, not a new bug: the remote site's Brume 2 masquerades outbound tunnel traffic, so anything arriving at the server looks like it came from the gateway. The actual problem was underneath that cosmetic confusion — the pairing handshake itself was never completing. The client's own status kept reporting no server connection even while the server-side record showed the client as online.

The root cause, once found: **UrBackup's default LAN pairing depends on broadcast/multicast to discover clients, and broadcast/multicast doesn't cross a routed VPN tunnel** — the same category of limitation already hit once with the Proxmox nodes' LXC-to-bare-metal boundary, showing up again in a different shape. A client reachable only through a tunnel needs UrBackup's separate **internet mode** — an explicit outbound WebSocket connection — not LAN discovery at all:

```bash
# On the remote Wyse 3040, as root
urbackupclientctl wait-for-backend
urbackupclientctl set-settings --server-url "ws://192.168.86.8:55414/socket" --name "wyse3040-ei" --authkey "<any-string>"

# The client won't actually use that URL until internet mode is enabled:
sed -i 's/INTERNET_ONLY=false/INTERNET_ONLY=true/' /etc/default/urbackupclient
systemctl restart urbackupclientbackend
```

The `INTERNET_ONLY` step isn't optional decoration — `--server-url` alone only configures *where* to connect; the client still defaults to LAN-mode behavior otherwise, its internal status sitting at `wait_local` and waiting for a connection that will never arrive over a routed tunnel. Flipping that flag is what actually makes it dial out. The authkey itself doesn't need to be pre-generated or looked up anywhere — whatever string gets passed is accepted and recorded by the server on first successful connection, confirmed directly by checking the server's own settings for that client afterward.

Even after both fixes, the server-side status showed no change at all — and this is where the actual diagnosis happened. `LOGLEVEL=warn`, the default, is too coarse to show a handshake that starts but doesn't complete. Bumping it to `debug` and restarting both ends surfaced the real sequence:

```bash
# On ct:108
sed -i 's/LOGLEVEL="warn"/LOGLEVEL="debug"/' /etc/default/urbackupsrv
systemctl restart urbackupsrv
# restart the client on the remote box again here
tail -f /var/log/urbackup.log
```

`Authed+capa for client 'wyse3040-ei' (encrypted-v2, compressed-zstd, token auth)`, followed by `New Backupclient: wyse3040-ei` — confirmed via a real completed backup landing on disk afterward, not just a log line trusted at face value. `LOGLEVEL` went back to `warn` once confirmed. The one loose end that didn't clean itself up automatically: a duplicate client record from the earlier failed attempts, named after the raw IP instead of the hostname, needed an explicit `remove_client()` call — and even that is queued server-side rather than instant, so it doesn't vanish from the client list the moment the call succeeds.

Worth being honest about the shape of this one: three layered problems wearing what looked like a single symptom — a missing route, a UI dead end that ate real troubleshooting time, and a fundamentally different connection mode needed for anything behind a tunnel. Each fix in isolation looked complete and wasn't. Only checking the actual handshake at debug-log level, rather than trusting any single fix's apparent success, closed it for real.

## Two Scripts, Not a Built-In Template

UrBackup itself ships zero OS-specific preset configurations — it's a completely generic tool, no Proxmox or Debian defaults baked in anywhere. It does have a real, server-side "client groups" feature with group-level default backup paths — confirmed by inspecting the server's own settings schema directly, not just documentation — which is the more "native" way to avoid configuring the same six nodes by hand. The catch: the Python API wrapper in use here doesn't expose group creation or group-settings calls, only per-client settings, so standing that up cleanly needs a one-time manual web UI pass. Not automated yet, so not the mechanism actually used.

What shipped instead — and what's genuinely reusable, not just internal tooling — are two small idempotent shell scripts:

**Proxmox VE nodes**, applied fleet-wide across all six cluster nodes:
```bash
#!/bin/bash
set -e
if ! urbackupclientctl list-backupdirs 2>/dev/null | grep -q etc-config; then
    urbackupclientctl add-backupdir -d /etc -n etc-config
fi
if ! urbackupclientctl list-backupdirs 2>/dev/null | grep -q pve-cluster-state; then
    urbackupclientctl add-backupdir -d /var/lib/pve-cluster -n pve-cluster-state
fi
cat > /etc/logrotate.d/urbackupcli << 'EOF'
/var/log/urbackupclient.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

**Generic Debian / thin clients**, built for the Wyse 3040 fleet but not hard-coded to it — the optional block only fires if the path actually exists, rather than assuming every Debian box runs the same services:
```bash
#!/bin/bash
set -e
if ! urbackupclientctl list-backupdirs 2>/dev/null | grep -q etc-config; then
    urbackupclientctl add-backupdir -d /etc -n etc-config
fi
if [ -d /var/lib/tailscale ]; then
    if ! urbackupclientctl list-backupdirs 2>/dev/null | grep -q tailscale-state; then
        urbackupclientctl add-backupdir -d /var/lib/tailscale -n tailscale-state
    fi
fi
command -v logrotate &>/dev/null || { apt-get update -qq && apt-get install -y logrotate; }
cat > /etc/logrotate.d/urbackupcli << 'EOF'
/var/log/urbackupclient.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

That `/var/lib/tailscale` path isn't a guess dressed up as a fact — it's confirmed directly from a running `tailscaled` process's own `--state` argument on the actual pilot hardware, the same way the Proxmox paths were confirmed by reading real backed-up content afterward rather than trusting documentation alone.

Both scripts are idempotent — safe to re-run, including against `harlan`, which already had its directories configured by hand before either script existed. Running it again just confirmed the existing state and added the piece that was actually missing (log rotation), instead of erroring or duplicating entries.

## Log Rotation: What Was Actually Broken

Easy to overclaim a fix here, so worth being precise. `urbackupclient` already ships with built-in, size-based log rotation — `LOG_ROTATE_FILESIZE`/`LOG_ROTATE_NUM` in `/etc/default/urbackupclient`, defaulting to a 20MB-per-file, 10-file cap, roughly 200MB total. The client-side logrotate.d configs in both scripts above add compression and a predictable weekly cadence on top of a limit that already existed — genuinely nicer, not a fix for actually-unbounded growth.

The server is different. `urbackupsrv`'s own `/etc/default/urbackupsrv` has no equivalent setting at all — just `LOGFILE` and `LOGLEVEL`, confirmed by direct comparison against the client's config file. `/var/log/urbackup.log` on the server LXC was the one genuinely unbounded log across this whole deployment, and a small standalone script fixed it the same way, validated with a `logrotate -d` dry run before trusting it:

```bash
cat > /etc/logrotate.d/urbackupsrv << 'EOF'
/var/log/urbackup.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

## Where This Stands

Server infrastructure is solid — deployed, permission-fixed, boot-order-safe, log-rotation-safe on both ends. All six Proxmox nodes are paired and fully templated (`etc-config` and `pve-cluster-state` backup dirs confirmed present on every node). Both Wyse 3040 units have the client installed with the correct no-snapshot choice and are paired — including the remote one, once internet mode was actually configured correctly. The Debian template script (backup directories beyond `/etc`, log rotation) hasn't been run on either Wyse unit yet — that's still a manual step waiting on the fleet growing past two units before it's worth doing by hand a third and fourth time. Clonezilla — the bare-metal bootable-restore tier meant to sit alongside all of this — hasn't been started at all. Small, working system with one real edge still open, which is a fair description of most homelab infrastructure a couple weeks after it goes in.
