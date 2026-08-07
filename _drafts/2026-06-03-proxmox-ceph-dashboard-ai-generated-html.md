---
title: "Building a Proxmox + Ceph Status Dashboard with AI-Generated HTML"
layout: post
categories: [technical, homelab, devtools]
tags: [proxmox, ceph, dashboard, html, ai agents, kiro, python, api, monitoring, github-pages]
excerpt: "Putting the AI-generated HTML report pattern into practice: pulling real metrics from a Proxmox 8 cluster and Ceph storage pool, generating a self-contained status dashboard, and publishing it to GitHub Pages. A concrete example of the pattern from Part 1."
description: "Part 2 of the AI-generated HTML reports series. A hands-on implementation pulling cluster status, node health, VM inventory, and Ceph OSD/pool metrics from the Proxmox API, generating a self-contained dark-mode HTML dashboard with CSS charts, and publishing it to GitHub Pages as a living report."
date: 2026-06-03
last_modified_at: 2026-06-03
published: false
seo:
  type: BlogPosting
  date_published: 2026-06-03
  date_modified: 2026-06-03
---

In [Part 1](/ai-generated-html-reports-jekyll-github-pages/), I described the pattern: AI agents generate self-contained HTML reports, you commit them to a Jekyll site, and GitHub Pages serves them at stable URLs. The theory is clean. Now let's build something real.

My Proxmox 8 cluster runs three nodes with Ceph storage. I want a single-page dashboard showing cluster health, node status, VM inventory, and Ceph pool utilization — generated from the Proxmox API, rendered as a zero-dependency HTML file, and published alongside this blog.

<!-- excerpt-end -->

## What We're Building

A self-contained HTML dashboard that shows:

- **Cluster overview** — node count, total CPU/RAM, cluster status
- **Node health** — per-node CPU usage, memory, uptime, kernel version
- **VM/CT inventory** — running vs stopped, resource allocation per guest
- **Ceph status** — overall health, OSD status (up/down/in/out), pool usage
- **Ceph pool details** — per-pool capacity, usage percentage, objects stored
- **Storage utilization** — bar charts showing pool fill levels

All from a single Python script that queries the Proxmox API and outputs one `.html` file.

## The Proxmox API

Proxmox VE exposes a full REST API at `https://<node>:8006/api2/json/`. Authentication uses either API tokens or ticket-based sessions.

### API Token Setup

TODO: Document creating a PVE API token
- User: `dashboard@pve` or `root@pam`
- Permissions needed: read-only access to `/cluster`, `/nodes`, `/storage`
- Token format: `user@realm!tokenid=secret`
- Security: read-only token, no privilege separation concerns

### Key API Endpoints

TODO: Investigate and document which endpoints provide the metrics we need

| Metric | Endpoint | Notes |
|--------|----------|-------|
| Cluster status | `GET /cluster/status` | Node membership, quorum |
| Node list | `GET /nodes` | CPU, memory, uptime per node |
| Node status | `GET /nodes/{node}/status` | Detailed node metrics |
| VM list | `GET /nodes/{node}/qemu` | VMs on a specific node |
| CT list | `GET /nodes/{node}/lxc` | Containers on a specific node |
| Ceph status | `GET /cluster/ceph/status` | Overall Ceph health |
| Ceph OSD list | `GET /nodes/{node}/ceph/osd` | OSD status per node |
| Ceph pools | `GET /nodes/{node}/ceph/pool` | Pool usage and stats |
| Storage list | `GET /storage` | All storage backends |
| Storage status | `GET /nodes/{node}/storage/{storage}/status` | Per-storage usage |

### Authentication Pattern

TODO: Document the API token auth header

```python
import urllib.request
import json

PROXMOX_HOST = "https://pve1.home.lab:8006"
API_TOKEN = "dashboard@pve!reporting=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

def pve_api(path):
    """Query the Proxmox API and return parsed JSON."""
    url = f"{PROXMOX_HOST}/api2/json{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"PVEAPIToken={API_TOKEN}",
    })
    # Note: self-signed cert handling needed for homelab
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read())["data"]
```

## Data Collection

TODO: Build the data collection script

### Cluster Metrics to Collect

```python
# Cluster-level
cluster_status = pve_api("/cluster/status")
nodes = pve_api("/nodes")

# Per-node details
for node in nodes:
    node_status = pve_api(f"/nodes/{node['node']}/status")
    vms = pve_api(f"/nodes/{node['node']}/qemu")
    containers = pve_api(f"/nodes/{node['node']}/lxc")

# Ceph
ceph_status = pve_api("/cluster/ceph/status")
ceph_osd = pve_api(f"/nodes/{nodes[0]['node']}/ceph/osd")
ceph_pools = pve_api(f"/nodes/{nodes[0]['node']}/ceph/pool")
```

### Data Questions to Answer

TODO: Figure out the exact response shapes and what's useful

- [ ] What does `/cluster/status` return? (node list, quorum status, cluster name)
- [ ] What CPU/memory format does `/nodes` use? (percentage? bytes? cores?)
- [ ] How are Ceph OSD states represented? (up/down/in/out booleans?)
- [ ] What pool metrics are available? (bytes_used, max_avail, objects?)
- [ ] Are there historical metrics available or only point-in-time?
- [ ] How to handle the self-signed certificate in the script?

## Report Generation

TODO: Build the HTML generator

### Dashboard Layout

```text
┌─────────────────────────────────────────────────────┐
│  Proxmox Cluster Dashboard          Generated: date │
├─────────────────────────────────────────────────────┤
│  [Cluster] [Nodes] [VMs] [Ceph] [Storage]          │  ← tabs
├─────────────────────────────────────────────────────┤
│                                                     │
│  Cluster Tab:                                       │
│    Status: HEALTHY    Nodes: 3/3    Quorum: Yes     │
│    Total CPU: 48 cores    Total RAM: 192 GB         │
│                                                     │
│  Nodes Tab:                                         │
│    ┌──────┬──────┬────────┬────────┬───────┐       │
│    │ Node │ CPU  │ Memory │ Uptime │ Status│       │
│    ├──────┼──────┼────────┼────────┼───────┤       │
│    │ pve1 │ 12%  │ 45 GB  │ 14d    │ ●     │       │
│    │ pve2 │ 8%   │ 38 GB  │ 14d    │ ●     │       │
│    │ pve3 │ 15%  │ 52 GB  │ 14d    │ ●     │       │
│    └──────┴──────┴────────┴────────┴───────┘       │
│                                                     │
│  Ceph Tab:                                         │
│    Health: HEALTH_OK    OSDs: 12/12 up              │
│    ┌────────────────────────────────────┐           │
│    │ ceph-pool  ████████░░░░  67%       │  ← CSS   │
│    │ ceph-meta  ██░░░░░░░░░░  12%       │    bars   │
│    └────────────────────────────────────┘           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Visualization Approach

| Metric | Chart Type | CSS Implementation |
|--------|-----------|-------------------|
| Pool fill level | Horizontal bar | `width: {pct}%` div inside container |
| OSD status | Status dots | Colored circles (green/red/yellow) |
| Node CPU | Horizontal bar | Same as pool fill |
| Node memory | Horizontal bar with label | Bar + text overlay |
| VM count by node | Grouped count | Simple number cards |

### Interactivity

- Tab navigation (Cluster / Nodes / VMs / Ceph / Storage)
- Sortable VM table (by name, node, CPU, memory, status)
- Ceph OSD expandable details (click OSD row to see weight, device, class)

## Publishing

### Manual Workflow

```bash
# Generate the dashboard
python3 tools/generate_proxmox_dashboard.py

# Verify locally
open reports/proxmox-cluster.html

# Commit and push
git add reports/proxmox-cluster.html
git commit -m "Update Proxmox cluster dashboard"
git push
```

### Automated Refresh (Future)

TODO: Consider automation options
- GitHub Actions with a self-hosted runner on the Proxmox network?
- Local cron job on one of the Proxmox nodes?
- Triggered manually from the homelab when needed?

The Proxmox API is only accessible from the home network, so GitHub Actions (cloud runners) can't reach it directly. Options:
1. **Self-hosted runner** on a Proxmox LXC container
2. **Local cron** that generates + commits + pushes
3. **Tailscale Funnel** to expose the API (probably overkill for a dashboard)
4. **Manual** — just run the script when you want a fresh snapshot

## File Structure

```text
mcgarrah.github.io/
├── _data/
│   └── proxmox-config.json      # API endpoint, token reference (not the secret)
├── tools/
│   └── generate_proxmox_dashboard.py
├── reports/
│   └── proxmox-cluster.html     # Generated output
└── _posts/
    └── 2026-06-03-proxmox-ceph-dashboard-ai-generated-html.md  # This article
```

## Security Considerations

- API token stored in environment variable or macOS Keychain, never in the repo
- Token should be **read-only** — no ability to modify VMs, storage, or cluster config
- Self-signed cert handling is acceptable for homelab (not production)
- Generated HTML contains point-in-time metrics, not live credentials
- Don't include IP addresses or hostnames in the published HTML if the dashboard is public

## TODO Checklist

- [ ] Create a read-only API token on the Proxmox cluster
- [ ] Test each API endpoint manually with curl to understand response shapes
- [ ] Document the exact JSON structure returned by each endpoint
- [ ] Build the data collection module (`tools/collect_proxmox_data.py`)
- [ ] Build the HTML generator (`tools/generate_proxmox_dashboard.py`)
- [ ] Design the CSS for dark-mode dashboard with bar charts
- [ ] Implement tab navigation (vanilla JS show/hide)
- [ ] Implement sortable tables for VM inventory
- [ ] Test the full pipeline: collect → generate → verify in browser
- [ ] Commit the generated HTML to `reports/proxmox-cluster.html`
- [ ] Verify it renders correctly on GitHub Pages
- [ ] Decide on refresh strategy (manual vs automated)
- [ ] Write up the results in this article

## Lessons Learned

TODO: Document after implementation:
- How much data the Proxmox API actually exposes vs what I expected
- Whether the self-signed cert handling was painful
- How large the generated HTML file ends up being
- Whether the CSS-only charts are sufficient or if SVG sparklines are needed
- How the dashboard looks on mobile (responsive considerations)

---

*This is Part 2 of the AI-generated HTML reports series:*
- *Part 1: [AI-Generated HTML Reports on GitHub Pages](/ai-generated-html-reports-jekyll-github-pages/) — The pattern*
- *Part 2: Proxmox + Ceph Dashboard (this article) — A concrete implementation*
