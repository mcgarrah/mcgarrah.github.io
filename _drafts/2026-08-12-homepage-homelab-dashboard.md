---
layout: post
title: "Two Days In: Why Homarr Got Replaced by Homepage"
image: /assets/images/og/homepage-homelab-dashboard.png
categories: [technical, homelab, infrastructure]
tags: [homelab, proxmox, homepage, dashboard, jellyfin, caddy, reverse-proxy, lxc, nodejs]
excerpt: "Homarr worked fine as a dashboard right up until a backup fleet landed alongside it and exposed a gap that wasn't theoretical anymore. Homepage replaced it two days later — same VMID, same IP, same MAC, a real UrBackup widget, and a config-as-code setup that actually matches the rest of this infrastructure."
description: "Migrating the AlteredCarbon homelab's landing-page dashboard from Homarr to Homepage: why a database-configured dashboard stopped fitting once UrBackup entered the picture, reusing a container's VMID/IP/MAC across a destroy-and-recreate swap, wiring up a real Proxmox API token and the UrBackup widget's self-signed-cert workaround, and the config-as-code setup that finally matches how the rest of this infrastructure is managed."
date: 2026-08-12
last_modified_at: 2026-08-12
seo:
  type: BlogPosting
  date_published: 2026-08-12
  date_modified: 2026-08-12
---

Homarr had been the landing-page dashboard for the AlteredCarbon cluster (`harlan`, `kovacs`, `poe`, `edgar`, `tanaka`, `quell`) for exactly two days before it got replaced. Not because it broke — because a backup fleet landed alongside it and turned a gap that had been theoretical into one that was concrete and daily.

<!-- excerpt-end -->

## Why Two Days Was Enough to Decide

Homarr's two real gaps had been visible from the start but easy to shrug off — right up until they weren't.

**No native UrBackup integration.** A UrBackup server (`ct:108`) had just gone in, covering all six Proxmox nodes and a small fleet of remote Wyse 3040 thin clients. Homarr could only offer it as a plain bookmark link — no client counts, no error status, no "is anything actually broken today" at a glance. For a dashboard whose entire job is surfacing status, a backup system with zero live status on it is a real omission, not a nice-to-have.

**No config-as-code path.** Homarr's configuration lives entirely in its own database, edited by dragging tiles around in a browser. Every other piece of this infrastructure — the LXC provisioning scripts, the Caddy reverse-proxy config, the UrBackup client templates, this whole documentation repo — lives in git as plain text, reviewable in a diff. Homarr was the one exception, and it stayed the one exception the whole time it ran.

Two other options got a real look before settling on Homepage. **Glance** is the other config-as-code dashboard, and its Proxmox widgets are actually more granular than Homepage's (four separate widget types via a community-maintained repo, versus Homepage's one built-in widget) — but it has no UrBackup integration at all, official or community. That's a direct regression on the exact gap driving the switch, so it was out immediately. **Dashy** doesn't compete on the axis that mattered here at all — it's UI/database-configured, same as Homarr, just with a different skin.

[Homepage](https://gethomepage.dev/) had both: an official, documented UrBackup widget, and YAML files as the actual source of truth.

## Deployment: Reusing a Container Instead of Placing a New One

Rather than stand up Homepage alongside Homarr and migrate traffic over, the old container was destroyed and a new one built in its place, deliberately keeping the same identity:

| Setting | Value |
|---|---|
| VMID | `501` — reused from Homarr, not a new placement |
| Node | quell |
| IP | `192.168.86.23/23` (static) — same address Homarr had |
| MAC | `BC:24:11:BA:C2:0E` — same MAC Homarr had |
| Port | `3000` (Homepage's own default — Homarr used `7575`) |
| Install method | [community-scripts](https://github.com/community-scripts/ProxmoxVE) `ct/homepage.sh` |

Nothing downstream — Caddy's routing, DHCP reservations, anything referencing this box by IP — needed to change identity, only the port.

The install itself hit the same limitation already known from Homarr's original setup: the script's top-level install menu (Default/Advanced/User Defaults/Settings) needs a real interactive terminal. Piped over SSH non-interactively, it either crashes on an early `clear` call (`TERM environment variable not set` — fixable with `export TERM=xterm`) or exits immediately once it hits the whiptail menu with no input available. Not every community-scripts installer behaves this way — some genuinely do respect `var_ctid` and friends non-interactively — but this one needs a console session. Running it interactively and entering the exact IP/MAC to reuse during Advanced Install meant no `pct set` cleanup was needed afterward.

```caddyfile
# Homepage Dashboard
https://192.168.86.30:3000 {
	reverse_proxy 192.168.86.23:3000
}
```

Applied live via `caddy validate` then `systemctl reload` — verified every other route on that Caddyfile (Proxmox UI, Ceph Dashboard, UrBackup) still returned `200` afterward before calling it done.

## Configuration: Real YAML, Not a Placeholder

Homepage's actual config is a handful of YAML files (`services.yaml`, `settings.yaml`, `bookmarks.yaml`) inside the container — the whole point of choosing it over Homarr. Two integrations got real widgets; two more are honest bookmarks for now.

**Proxmox** — a dedicated API token rather than reusing Homarr's old one:
```bash
pveum user token add root@pam Homepage --privsep 1 --comment 'Homepage Dashboard Token'
pveum acl modify / -token 'root@pam!Homepage' -role PVEAuditor
```
`PVEAuditor` is read-only, which is all a dashboard display needs. No separate cluster config file required — the token goes directly into the service's own `widget` block in `services.yaml`.

**UrBackup** — the actual integration this whole switch was for:
```yaml
widget:
  type: urbackup
  username: automation
  password: <the automation user's password>
  url: http://192.168.86.8:55414
  maxDays: 5
```
One real gotcha here: pointed at the HTTPS Caddy route instead of the backend directly, the widget fails outright — Node.js rejects the self-signed cert this cluster's Caddy setup currently uses (no real CA/ACME yet), and threading `NODE_EXTRA_CA_CERTS` into a systemd unit for what should be simple config isn't worth it. Homepage and UrBackup are both on the internal network anyway, so the plain-HTTP backend URL sidesteps the problem entirely rather than working around it.

**Jellyfin and Technitium DNS** stayed plain bookmark links for now — both need an API key generated through their own web UI (Jellyfin: Dashboard → API Keys; Technitium: Settings → API tokens), not something safely pulled from the filesystem directly.

## One Bug Found Along the Way

Getting the config working meant actually reading the service's logs to confirm the YAML changes took effect — which surfaced something unrelated to the migration entirely: the community-scripts installer runs Homepage's production server the wrong way, silently using roughly 7x more disk than necessary on every container it creates. That's a big enough finding to deserve its own writeup rather than a paragraph here — see [The Homelab Install Script Bug That Still Works](/homepage-lxc-standalone-nextjs-bug/) for the full diagnosis, the fix, and why the fix needed hardening to survive the installer's own update path.

## Where This Stands

Homepage is live, routed through Caddy, and serving real Proxmox and UrBackup widget data alongside Jellyfin and Technitium bookmarks. `HOMARR.md` — the old dashboard's own writeup — stays in the docs repo as a historical record rather than getting deleted; its two Proxmox API integration gotchas (privilege separation on fresh tokens, and a field-mapping trap between how Proxmox displays a token and how a form asks for it) are dashboard-agnostic and will resurface the next time anything authenticates against the Proxmox API the same way.

## Open Questions

- Full widget *rendering* hasn't been checked in an actual browser yet — Homepage is client-rendered, so `curl` testing can only confirm the underlying data (via `/api/services`), not that it paints correctly.
- Whether to pick up any of Homepage's non-service widgets (weather, RSS) or keep this strictly a service-status dashboard, matching Homarr's original scope.
- The old `root@pam!Homarr` Proxmox API token is now unused now that Homarr's LXC no longer exists — a cleanup candidate.
