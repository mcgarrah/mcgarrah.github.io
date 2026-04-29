---
title: "Caddy Reverse Proxy for Proxmox Web UI"
layout: post
categories: [technical, homelab]
tags: [proxmox, caddy, reverse-proxy, lxc, ssl, web-interface, homelab]
last_modified_at: 2026-05-18
seo:
  date_published: 2026-05-18
  date_modified: 2026-05-18
---

Managing a six-node Proxmox cluster means six different web interfaces on six different IPs, all on port 8006 with self-signed certificates. A Caddy reverse proxy in an LXC container gives you a single entry point with load balancing, health checks, and working WebSocket support for the console — all in about 30 lines of configuration. This is the same pattern you'd use for any clustered management plane — Kubernetes dashboards, Grafana instances, database admin consoles — a reverse proxy that abstracts the individual nodes behind a stable endpoint.

<!-- excerpt-end -->

## Why Proxy the Proxmox Web UI?

The Proxmox web interface runs on each node at `https://<node-ip>:8006`. In a multi-node cluster, this means:

- **Bookmarking a single node** — if that node goes down, you lose access to the UI
- **Self-signed certificate warnings** — every browser session starts with clicking through warnings
- **No load balancing** — all your management traffic hits one node
- **WebSocket issues** — the noVNC console needs proper proxy headers to work

A Caddy reverse proxy solves all of these with a single URL: `https://192.168.86.30/`

## Prerequisites

- A Proxmox cluster (mine has six nodes: harlan, kovacs, poe, edgar, quell, tanaka)
- An LXC container for Caddy (I used Debian 12 Bookworm)
- Static IP for the LXC (192.168.86.30 in my case)

## Step 1: Create the LXC Container

I created a Debian 12 LXC container on Proxmox using the [Proxmox Helper Scripts](https://helper-scripts.com). You can also create one manually:

```bash
# On a Proxmox node — adjust storage, bridge, and VMID as needed
pct create 130 local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
  --hostname caddy \
  --memory 512 \
  --cores 1 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.86.30/23,gw=192.168.86.1 \
  --storage local-lvm \
  --rootfs local-lvm:4 \
  --unprivileged 1 \
  --start 1
```

## Step 2: Install Caddy

Inside the LXC container:

```bash
apt update && apt install -y debian-keyring debian-archive-keyring apt-transport-https curl

curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | \
  gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg

curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | \
  tee /etc/apt/sources.list.d/caddy-stable.list

apt update && apt install -y caddy
```

Verify the installation:

```bash
caddy version
# v2.10.2
```

## Step 3: Configure the Caddyfile

Replace `/etc/caddy/Caddyfile` with the following configuration:

```caddyfile
https://192.168.86.30 {
	reverse_proxy * {
		to 192.168.86.11:8006
		to 192.168.86.12:8006
		to 192.168.86.13:8006
		to 192.168.86.14:8006
		to 192.168.86.15:8006
		to 192.168.86.16:8006

		lb_policy ip_hash
		health_uri /
		health_interval 10s
		health_timeout 2s
		health_status 200

		transport http {
			tls_insecure_skip_verify
		}

		# WebSocket support for noVNC console
		header_up Upgrade {http.request.header.Upgrade}
		header_up Connection {http.request.header.Connection}
	}
}
```

### Configuration Breakdown

- **All six nodes listed** — Caddy distributes requests across the cluster
- **`lb_policy ip_hash`** — Sticky sessions ensure your browser stays on the same node during a session, which is important for the Proxmox authentication token
- **Health checks** — Caddy automatically removes unhealthy nodes and re-adds them when they recover (10-second interval, 2-second timeout)
- **`tls_insecure_skip_verify`** — Required because Proxmox uses self-signed certificates on port 8006. Caddy needs to trust the upstream, and the Proxmox PVE CA isn't in the system trust store
- **WebSocket headers** — The `Upgrade` and `Connection` header forwarding is critical for the noVNC/xterm.js console to work through the proxy

### A Note on TLS Verification

For a more secure alternative, you could trust the PVE CA directly instead of skipping verification:

```caddyfile
# More secure alternative if you copy the PVE CA into the LXC:
# tls_trusted_ca_certs /etc/ssl/certs/pve-root-ca.pem
```

The `/etc/pve` filesystem isn't directly accessible from inside an LXC container, but you can copy the CA cert in manually. For an internal homelab proxy, `tls_insecure_skip_verify` is pragmatic — the traffic never leaves your LAN.

## Step 4: Enable and Start Caddy

```bash
systemctl enable caddy
systemctl restart caddy
systemctl status caddy
```

Caddy automatically generates a self-signed certificate for the HTTPS listener. You'll get one browser warning the first time you visit `https://192.168.86.30/` — after accepting it, you're done.

## Step 5: Verify It Works

1. Open `https://192.168.86.30/` in your browser
2. Accept the self-signed certificate warning (one time)
3. You should see the Proxmox login page
4. Log in and verify the noVNC console works (click a VM → Console)

## How It Behaves

### Node Failover

If a node goes down, Caddy's health checker detects it within 10 seconds and stops routing traffic to it. You'll see log entries like:

```
"msg":"host is down","host":"192.168.86.14:8006"
```

When the node comes back:

```
"msg":"host is up","host":"192.168.86.14:8006"
```

No manual intervention needed.

### Session Persistence

The `ip_hash` load balancing policy means your browser always hits the same backend node (based on your client IP). This is important because Proxmox authentication tickets are node-specific — without sticky sessions, you'd get logged out randomly as requests bounce between nodes.

## Troubleshooting

### Console Not Working

If the noVNC or xterm.js console shows a blank screen or disconnects immediately, verify the WebSocket headers are being forwarded:

```bash
caddy validate --config /etc/caddy/Caddyfile
```

### Health Check Timeouts

If you see frequent health check failures in the logs for a specific node, that node may be under heavy load. Increase the timeout:

```caddyfile
health_timeout 5s
```

### Checking Caddy Logs

```bash
journalctl -u caddy -f
```

## Future Improvements

- **DNS name** — Switch from IP to `proxmox.home.mcgarrah.org` once Technitium DNS is configured with the appropriate record
- **Proper TLS** — Use cert-manager or Caddy's ACME with Porkbun DNS-01 for a real certificate
- **Access logging** — Add structured logging for audit trails
- **Authentication layer** — Add Authentik/Keycloak SSO in front of the proxy

## My Running Configuration

| Component | Detail |
|-----------|--------|
| LXC Host | Debian 12 (Bookworm) |
| Caddy Version | v2.10.2 |
| LXC IP | 192.168.86.30 |
| Proxy URL | `https://192.168.86.30/` |
| Backend Nodes | 6 (192.168.86.11–16:8006) |
| Load Balancing | ip_hash (sticky sessions) |
| Health Checks | 10s interval, 2s timeout |
| Uptime | Running in production |

## Related Articles

- [Caddy Reverse Proxy for Ceph Dashboard](/caddy-reverse-proxy-ceph-dashboard/) — Adding the Ceph Dashboard as a second proxy site
- [Adding Ceph Dashboard to Your Proxmox Cluster](/proxmox-add-ceph-dashboard/) — Setting up the Ceph monitoring dashboard
- [Consolidating Proxmox Notes: A Python Export Script](/proxmox-consolidated-notes/) — Backing up cluster documentation
- [Proxmox 8 Lessons Learned in the Homelab](/proxmox-8-lessons-learned/) — Hard-won tips from running Proxmox
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — All my Proxmox and Ceph articles in one place
