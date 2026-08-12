---
layout: post
title: "Homarr: A Single Pane of Glass for the AlteredCarbon Homelab"
image: /assets/images/og/homarr-homelab-dashboard.png
categories: [technical, homelab, infrastructure]
tags: [homelab, proxmox, homarr, dashboard, jellyfin, caddy, reverse-proxy, lxc, dell-wyse-3040, glances, monitoring, python]
excerpt: "A homelab that grows past a handful of services stops being navigable by memory. Homarr became the single dashboard surfacing Proxmox, Jellyfin, and DNS status across the AlteredCarbon cluster — deployed deliberately as a starting point, not a permanent commitment, with two real API integration gotchas along the way and a resource-constrained monitoring proposal now on deck."
description: "Deploying Homarr as the landing-page dashboard for a 6-node Proxmox/Ceph homelab: LXC placement decisions, Caddy reverse proxy integration, and two real troubleshooting stories from wiring up the Proxmox API (privilege separation and empty ACLs, and a field-mapping mismatch). Closes with a hardware-verified proposal for extending visibility to the resource-constrained Wyse 3040 thin client fleet via Glances."
date: 2026-08-10
last_modified_at: 2026-08-12
seo:
  type: BlogPosting
  date_published: 2026-08-10
  date_modified: 2026-08-12
---

A homelab that grows past a handful of services stops being navigable by memory. Between Proxmox's own web UI, Jellyfin, DNS management, and a growing list of LXC-hosted dev services, "where do I even check status" had become its own small tax on the AlteredCarbon cluster (`harlan`, `kovacs`, `poe`, `edgar`, `tanaka`, `quell`). The fix was a single landing-page dashboard — Homarr — deployed deliberately as an evaluation, not a permanent architectural commitment. Dashboards are cheap to swap and expensive to over-invest in before you know if the shape fits.

**Update (2026-08-12):** That evaluation ran its course fast. Homarr was retired two days after this was written and replaced with [Homepage](https://gethomepage.dev/) — the same VMID, IP, and MAC reused for the new container — once two gaps went from theoretical to concrete: no native UrBackup integration (a backup fleet had just landed alongside it), and no config-as-code path (Homarr's configuration lives in its own database, edited via browser, while everything else in this infrastructure lives in git as text). The two Proxmox API integration gotchas documented below are dashboard-agnostic and still apply to anything authenticating against the Proxmox API the same way — kept here as a working historical record, not a live deployment guide.

<!-- excerpt-end -->

## Deployment

Homarr runs as its own LXC — `ct:501` on `quell`, Debian 13, unprivileged, 2 vCPU / 2048 MiB RAM / 10 GB disk. The VMID itself came out of a small placement decision: `501` had been earmarked for a planned Caddy renumber that never materialized, so rather than let a stale placeholder block a new service, the caddy-move plan was dropped and `501` went to Homarr instead. Worth naming explicitly — infrastructure plans decay, and a VMID range document is only useful if it's corrected the moment reality diverges from it, not left to accumulate "reserved, but not really" entries.

Provisioned via the [community-scripts](https://github.com/community-scripts/ProxmoxVE) installer, non-interactively:

```bash
export var_ctid=501
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/ct/homarr.sh)"
```

`var_ctid` is read directly by the installer's `base_settings()` function — it only falls back to the next free ID (with a warning) if the requested one is already taken.

## Reverse Proxy

Exposed through the cluster's existing Caddy LXC (`ct:500`, quell) rather than standing up new TLS/routing infrastructure for one more service:

```caddyfile
# Homarr Dashboard
https://192.168.86.30:7575 {
    reverse_proxy 192.168.86.23:7575
}
```

Applied live — `caddy validate`, then `systemctl reload` rather than `restart`, specifically to avoid dropping the existing Proxmox UI and Ceph Dashboard routes already served from the same Caddyfile. This is still IP+port routing, not the domain-name/ACME approach sketched out for once local DNS is fully wired up — a deliberate, acknowledged gap between the live config and the longer-term plan, not an oversight.

## Integrations: Two Real Gotchas

Homarr's dashboard tiles are only as useful as the integrations behind them. Proxmox, Jellyfin (`ct:502`, harlan), and Technitium DNS are wired up today. The Proxmox integration in particular surfaced two separate failure modes worth documenting, because both produced the identical symptom — a generic "not authorized" error — from two unrelated root causes.

### Gotcha 1: Privilege separation on a fresh API token means *nothing* is authorized by default

An API token created under `root@pam` does not inherit root's superuser access when privilege separation is enabled — which is the default when creating a token through the Proxmox UI without explicitly unchecking it. The token only gets what's explicitly granted to it via ACL. Nothing granted means every request fails authorization, correctly formatted or not.

Diagnosis is a two-command read:

```bash
pveum user token list root@pam    # confirm privsep is actually on
pveum acl list                    # confirm nothing's actually granted
```

The fix follows Proxmox's own documented "limited API token for monitoring" pattern — grant the token itself a read-only role, rather than reaching for the easier-looking but wrong fix of disabling privilege separation on a *root*-owned token, which would hand a dashboard app literal superuser access to the cluster:

```bash
pveum acl modify / -token 'root@pam!Homarr' -role PVEAuditor
```

### Gotcha 2: the dashboard's own form fields don't match how Proxmox displays the token

Homarr's Proxmox integration form asks for `Username`, `Realm`, and `Token ID` as three separate fields, which it reassembles internally into the `user@realm!tokenid` format Proxmox actually expects. It's an easy trap to paste the full identifier Proxmox displays (`root@pam!Homarr`) into just the `Token ID` field — that double-includes the username and realm and breaks the request in a way that looks identical to Gotcha 1 from the outside.

Correct mapping for a token named `Homarr` under `root@pam`:

| Homarr field | Value |
|---|---|
| Username | `root` |
| Realm | `pam` |
| Token ID | `Homarr` |
| API Key | *(the secret value only)* |

A companion trap: Proxmox's token-creation screen displays the secret alongside surrounding UI chrome, and it's easy to select more than the secret itself when copying — which silently corrupts the token without any error until the very next authentication attempt.

Both failure modes turned out to be common enough to have their own GitHub issue thread ([homarr-labs/homarr#4980](https://github.com/homarr-labs/homarr/issues/4980)) with the identical symptom and the identical two root causes — a useful reminder that "not authorized" from a dashboard integration is really two different bugs wearing the same error message.

## What's Next: Extending Visibility to the Wyse 3040 Fleet

Homarr's built-in system monitoring widgets (System Resources, System Health) don't work by SSHing into a box — they talk to a small agent or API running on the target host, the same pattern as the Proxmox/Jellyfin integrations above. For hosts already inside the cluster, Proxmox's own integration already covers hypervisor-level stats. What it *doesn't* cover is a small fleet of Dell Wyse 3040 thin clients running standalone at the edge — one on-site (`wyse3040-ral`, Raleigh), with two more remote (`wyse3040-ei` at a GL.iNet Brume 2 VPN client site in Emerald Isle, and a third pending) reachable only through a GL.iNet Brume 3 VPN server back at the primary site.

[Glances](https://github.com/nicolargo/glances) is the standard lightweight choice for exactly this gap — a pure-Python system monitor with a web server mode Homarr can point directly at. Before committing to it across the fleet, though, "lightweight" needed to be verified against the actual hardware rather than assumed from a spec sheet, because a Wyse 3040 is genuinely resource-constrained in ways that aren't obvious until you look:

| Resource | `wyse3040-ral` (verified) |
|---|---|
| CPU | Intel Atom x5-Z8350, 4 cores @ 1.44 GHz (1.92 GHz burst) |
| RAM | 1.8 GiB total, ~1.5 GiB available |
| Disk | 5.2 GB root volume, **only 1.2 GB free (76% used)** |
| OS | Debian 12 (bookworm), kernel 6.1 |
| Python | 3.11.2 present; no system `pip3` |

RAM turned out not to be the binding constraint — Glances' web server mode runs at roughly 30-50 MB and under 2% CPU at baseline, comfortably inside the ~1.5 GB available. **Disk is the real constraint**: with only 1.2 GB free, a system-wide `pip3 install` pulling in a full dependency tree isn't a decision to make casually on this hardware.

The plan instead:

- **Install via `uv` into an isolated venv**, not system Python. `uv` is already the standard tool for this pattern across the cluster's dev LXCs — a single static binary that manages its own virtual environments without depending on system `pip`/`venv` packages, which matters more on an 8 GB eMMC thin client than on a normal server. It also uses the already-installed system Python 3.11 as its base interpreter rather than downloading a separate managed one, keeping the footprint to just Glances' own dependencies.
- **Disable the plugins that don't apply to this hardware** (`sensors`, `gpu`, `docker`) — these are a documented source of CPU spikes when they repeatedly probe hardware that isn't present, exactly the failure mode a thin client would hit.
- **Run as a systemd service** pointed at the venv's own binary, so it survives reboots without depending on a login shell:

```ini
[Unit]
Description=Glances web server
After=network.target

[Service]
ExecStart=/opt/glances-venv/bin/glances -w --disable-plugin sensors,gpu,docker
Restart=on-failure
User=glances

[Install]
WantedBy=multi-user.target
```

SSH key access from the cluster's agent-dev LXC is set up for `wyse3040-ral`; `wyse3040-ei` and the third unit are pending until VPN routing to their remote sites is confirmed. Rollout will go one box at a time, with actual measured RAM/CPU/disk delta checked before and after — this table gets a second column once that's done.

## Open Questions

- ~~Whether Homarr remains the long-term dashboard choice or gets swapped once its limits are better understood~~ — resolved two days later, see the Update note above.
- Domain-name access (`homarr.home.mcgarrah.org` or similar) once local DNS is fully wired up, replacing the current IP+port routing style.
- Whether the Wyse 3040 fleet's Glances instances get their own Homarr integration tiles per-host, or roll up into a single fleet view once all three are online.
