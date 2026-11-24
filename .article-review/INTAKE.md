# Intake — Infrastructure Workstreams → Article Coverage

**Created:** 2026-09-02
**Phase:** 7 (Cross-Repo Intake), started early because the August work volume made it urgent
**Sources:** `../k8s-proxmox` (206 commits, 140 of them in August 2026), `../jellyfin-plugin-media-integrity-scanner`
**Parent plan:** [`../KIRO-CLAUDE-OPUS5-MAX-ARTICLE-REVIEW.md`](../KIRO-CLAUDE-OPUS5-MAX-ARTICLE-REVIEW.md)

---

## The shape of the problem

August 2026 was the single densest month of infrastructure work in the repo's history: **140 commits in 24 days**, after **zero commits in May, June, and July**. Roughly 52 distinct workstreams moved. The owner named six of them from memory.

The blog did not keep up, and the reason is structural rather than lazy: **the drafts that exist were written *during* the work, and the work kept moving underneath them.** Four February drafts describe a cluster that no longer exists. The five-part upgrade series documents preparation for an upgrade that still hasn't run.

One more thing changed that isn't in any document: **Jellyfin and the *arr stack are now a production family service.** Wife and kids are users. Three Samsung TVs at the beach house stream over the site-to-site tunnel. That converts every future change from "homelab tinkering" into "change management with a customer," and it is the most editorially interesting thing that happened all month.

---

## Part 1 — Coverage matrix

Legend for substrate status (from the parent plan's Phase 2 rubric):
`S4` done and verified · `S3` done, verification stale/partial · `S2` partially done · `S1` planned only

| Workstream | Status | Article coverage | Verdict |
|---|---|---|---|
| PVE 8→9 pre-flight + PBS safety net | S4 (Aug 5–7) | `_drafts/2026-08-05-...part-1.md` | ✅ covered, unpublished |
| Ceph Reef → Squid 19.2.5 (31/31 daemons) | S4 (Aug 12) | `_drafts/2026-08-09-...part-2.md` | ✅ covered, unpublished |
| NVIDIA drivers + RTD3 + boot race + NVENC + HA failover | S4 (Aug 12–14) | `_drafts/2026-08-12-...part-3.md` (8,364w) | ✅ covered, **needs split** |
| *arr stack (11 LXCs) + 2 incidents | S2 (Phase 1 round-trip test open) | `_drafts/2026-08-15-...part-4.md` | ⚠️ covered, substrate incomplete |
| PVE 8→9 Phase B/C (the actual OS upgrade) | **S1 — not started** | `_drafts/2026-08-16-...part-5.md` | ⚠️ **plan article, not results** |
| UrBackup fleet (`ct:108`) | S4 (Aug 11) | `_drafts/2026-08-11-urbackup-...md` | ✅ covered, unpublished |
| Homarr → Homepage migration | S4 (Aug 12) | 3 drafts (`homarr`, `homepage`, `nextjs-bug`) | ✅ covered, unpublished |
| Gap-fill USB→CephFS copy + throttle step-test | S2 (in flight, ~10 days unattended) | `_drafts/2026-08-29-cephfs-gapfill-throttle-tuning.md` | ✅ covered, unpublished |
| `ct:603` agent-dev LXC + session persistence | S3 | 3 drafts (tmux, plain-shell, provisioner) | ✅ covered, unpublished |
| Media Integrity Scanner plugin | S2 (test→prod blocked) | 6 published + 6 candidates | ✅ well covered |
| **Observability stack** (InfluxDB, Grafana, 6 Telegraf collectors, 18-panel dashboard) | **S4 (Aug 16–25)** | **none — passing mentions only** | 🔴 **GAP** |
| **Site-to-site VPN — 3 sites live** (Raleigh hub, Beach, Wilson) | **S4 (Aug 30–31)** | `_drafts/2024-01-27-networking-site-2-site-vpn.md` — 1,363w, 2024 vintage, stops at "Network Diagrams" | 🔴 **GAP** |
| **Tailscale on Brume routers + route-hijack incident** | **S4 (Aug 30)** | published posts are all 2024 Wyse-era | 🔴 **GAP** |
| **Technitium two-tier multi-site DNS** | **S4** | passing mentions in 8 drafts, no dedicated article | 🔴 **GAP** |
| **CephFS LXC idmap permissions** (hit twice: PBS, Bazarr) | **S4** | mentions only; `k8s-proxmox/docs/CEPHFS-LXC-PERMISSIONS.md` exists | 🔴 **GAP** |
| **Recyclarr silently reverting hand-applied fixes** | **S4 (Aug 31)** | one section in part 4 | 🔴 **GAP** |
| **`openwrt-vm` 1001 — 3 weeks of silent backup failure** | **S4 (diagnosed)** | none | 🔴 **GAP** |
| **CephFS 3-tier backup pipeline** | S3 — built, **not in cron** | none | 🟡 gap, needs honest framing |
| **caddy-ui on `ct:500`** | S4 (Aug 14) | mention in part 4; 3 published Caddy posts predate it | 🟡 small gap |
| **Zero alerting across the estate** | — (absence) | none | 🔴 **GAP** (and a live risk) |
| **Family-production transition** | — (context) | **nothing, anywhere** | 🔴 **THE summary article** |
| Kubernetes 1.36 + Cilium + CAPI/CAPMOX | **S1 — never applied** | `k8s-proxmox/articles/` (21 files, stale) | ⛔ do not write as done |
| DHCP migration off Google Wifi/Nest | S1 | mentions | ⛔ not yet |
| ProCurve 2810/2824 + LACP + VLAN | S1 (on a shelf) | 2024 posts + stale drafts | ⛔ not yet |
| NUT / UPS graceful shutdown | S1 (since February) | mentions | ⛔ not yet |
| PiKVM + AIMOS 8-port KVM | S2 (research done, bench pending) | `_drafts/2024-04-03-pikvm-and-kvm.md` (1,048w stub) | ⛔ blocked on bench |
| Ebook stack (Chaptarr + Kavita) | S1 | none | ⛔ not yet |

---

## Part 2 — The two structural problems with existing drafts

### 2a. The five-part series can't conclude

Parts 1–4 document **preparation** for the PVE 9 upgrade: pre-flight and PBS, Ceph Reef→Squid, NVIDIA drivers, and the *arr stack. All four describe work that genuinely happened and is verified.

Part 5 documents **the upgrade itself** — Phase B canary, Phase C batch, Phase D verification. That work has not started. `docs/PVE9-UPGRADE-PLAN.md` still shows `B.0 [not yet run]`, and `JMM-TODO.md:107` is explicit:

> Phase B.0 (ZFS rollback dry-run on `tanaka`) and Phases B/C (the actual OS upgrade, canary then remaining 5 nodes) haven't started — every remaining phase requires physical presence, since none of these 6 nodes have out-of-band management.

**Credit where due: Part 5 does not pretend otherwise.** It carries an explicit note:

> *A note on timing: this post is being written and scheduled before the upgrade itself runs... expect this post to get a pass of real results, corrections, and probably at least one surprise once it's actually run.*

That satisfies gate G3 on honesty. But it creates an editorial problem the honesty doesn't solve: a series titled "Proxmox VE 8 to 9 Cluster Upgrade" where 80% is preparation and the finale is a plan. A reader arriving at Part 5 for the payoff gets a design document.

**Three options, in order of preference:**

1. **Reframe the series and add a real finale.** Retitle the arc to what it actually is — *Preparing a 6-Node Cluster for PVE 9* — publish Parts 1–4 as a complete, satisfying series about preparation being the real work, and hold Part 5. When the on-site window happens, Part 5 becomes *The Upgrade Itself* with real results. This is honest, it ships four verified articles now, and the eventual finale is stronger for having actual surprises in it.

2. **Publish 1–4, retitle Part 5 to "The Plan"** and promote it as a companion, with a stated commitment to a Part 6 results post. Weaker, because two articles then cover one phase.

3. **Hold all five until the upgrade runs.** Safest, but it strands ~19,800 words of verified work indefinitely behind an event that needs travel to happen.

**Recommendation: option 1.** Parts 1–4 stand on their own, and "the preparation was the hard part" is a genuinely good thesis — it's what the evidence actually shows.

### 2b. Four February drafts now describe a cluster that no longer exists

`2026-02-05-proxmox-cluster-roadmap-vms-project.md` (3,405w, **27 TODO markers**), `2026-02-12-proxmox-homelab-infrastructure-overview.md` (1,200w), `2026-02-13-pre-kubernetes-homelab-checklist.md` (2,529w, **115 TODO markers**), `2026-04-01-homelab-infrastructure-upgrades.md` (1,598w).

The parent plan already flagged these as a 4-way overlap needing a merge decision. August makes it worse: they describe pre-Squid Ceph, pre-NVIDIA GPUs, no *arr stack, no observability stack, a 5-node topology in places, and a Kubernetes deployment as imminent. They appear in nearly every coverage probe I ran, purely because they're sprawling catch-alls that mention everything and document nothing.

**These are now the single largest source of potential factual error in `_drafts/`.** The merge decision from Phase 3 should become: archive all four, and let the *actual* current-state article be the summary piece described in Part 4 below.

---

## Part 3 — Gap articles worth writing

Ranked by (reader value × substrate confidence) ÷ effort.

### Tier A — write these first

**A1 · Observability From Scratch on LXC, Not Kubernetes**
Source: `k8s-proxmox/docs/MONITORING.md`, `ARR-SUITE-DEPLOYMENT-PLAN.md:765`
InfluxDB v2 (`ct:111`) + Grafana (`ct:112`) + prometheus-pve-exporter + six Telegraf collectors (`qbittorrent`, `sabnzbd`, `jellyfin`, `arr_library`, `automation`, `bazarr`), plus an 18-panel *Media Pipeline Health* dashboard built programmatically. Deployed Aug 16, extended Aug 25.
The strong angle is the **deliberate architectural choice to not use Kubernetes** for the monitoring stack in a repo literally named `k8s-proxmox` — LXC was the right tool, and saying so is more credible than the alternative. Pairs with an honest admission that dashboards without alerting are still manual detection.
Substrate S4. **~4h.**

**A2 · The Dashboards Are Beautiful and Nothing Pages Me**
Source: `MONITORING.md:250`, `JMM-TODO.md:286`
A short, sharp companion to A1. Full observability stack, zero Alertmanager, zero Uptime Kuma. Every issue in the August logs was found by a human looking at a dashboard: qBittorrent stuck at 8 KB/s for five days, twelve imports blocked for three days, a quality-profile loophole reverting on every sync for a week, 137 unmonitored Sonarr series.
The enterprise connection writes itself — this is the difference between observability and monitoring, and it's a distinction plenty of production teams get wrong too. Best written *before* fixing it, while the evidence is fresh.
Substrate S4 (the absence is verified). **~2h.**

**A3 · Three Sites, One Tunnel: WireGuard Across Raleigh, Emerald Isle, and Wilson**
Source: `k8s-proxmox/docs/SITE-TO-SITE-VPN.md` (85K)
Hub-and-spoke WireGuard on GL.iNet Brume 2/3. Verified the right way — `curl ifconfig.me` from a genuine downstream LAN client behind the spoke router returned the *remote* site's real public IP. Wilson went live Aug 30–31 and is serving Jellyfin traffic.
Two real incidents make this more than a config walkthrough: a **Tailscale route hijack of `192.168.8.1`**, and **GL.iNet's Tailscale integration not wiring firewall forwarding** — so the tunnel was up and traffic still didn't pass. Also includes a long split-tunnel investigation that resolved as a *testing-methodology* error rather than a config bug, which is a genuinely useful thing to admit in print.
Substrate S4 for 3 sites. **Scope to what's live** — Katie and Sam are still placeholders. Likely a 2-parter. **~8h.**

**A4 · The Backup Job That Succeeded For Three Weeks While Failing**
Source: `JMM-TODO.md:259`
PBS `vzdump` with `all: 1` scope. Every LXC succeeded. The single VM in the fleet — `openwrt-vm` (1001), the OpenWRT router — failed with `timeout: no zvol device link for 'vm-1001-disk-1' found after 300 sec` on Aug 9, 16, and 23. The job reported success because the aggregate looked fine.
Short, self-contained, and a genuinely transferable lesson about aggregate-scope jobs masking per-item failure. The kind of article that gets linked years later.
Substrate S4 (diagnosed; fix may still be open — verify before publishing). **~2h.**

### Tier B — strong, slightly more work

**B1 · Unprivileged LXC, Shared CephFS, and the Permission Model That Bites Twice**
Source: `k8s-proxmox/docs/CEPHFS-LXC-PERMISSIONS.md` + plugin PR #40
Media owned by host UID/GID `501`, mode `770`, reached from unprivileged containers through a hand-written `lxc.idmap` punch. The doc's own warning is the thesis: *"Getting them confused is the fast way to spend an hour on a `Permission denied` that has nothing to do with file modes."* It has already been missed twice — once on PBS, once on Bazarr (`ct:507`), which shipped with a CephFS mount gap fixed after the fact.
Substrate S4. **~3h.**

**B2 · When Your Config Manager Reverts Your Fixes**
Source: `JMM-TODO.md:308`, `ARR-SUITE-DEPLOYMENT-PLAN.md`
Recyclarr with `reset_unmatched_scores: true`, plus a structural limitation: Recyclarr's v8 schema *requires* `trash_ids` for every `custom_formats` entry, so a locally-invented custom format cannot be expressed in its YAML at all. Anything applied by API and not written into `web-1080p.yml` silently reverts on the next sync. This bit twice — the HDTV-1080p cap reverted and was re-fixed Aug 31 after finding real exploitation, and a local custom-format score went the same way.
Fix is a chained `recyclarr sync && reassert-local-custom-formats.py`. The enterprise parallel is exact: this is configuration drift, and the answer is the same one Terraform and Kubernetes reach for — declare it or lose it.
Substrate S4. **~3h.**

**B3 · Two-Tier DNS Across Three Sites With Technitium**
Source: `JMM-TODO.md:280`
Technitium primary on `ct:101` plus a local secondary on each site's Dell Wyse 3040, so a site keeps resolving when the tunnel drops. Genuinely done and resilient.
Honest scoping note: **DHCP is still on the stock routers** (Google Wifi at Raleigh, Nest Wifi 6 at Emerald Isle) and the migration is designed but unexecuted. Write the DNS half; flag DHCP as the open half rather than implying it's done.
Substrate S4 for DNS. **~4h.**

**B4 · GPU RTD3 D3cold, and the Fix That Took Three Incidents**
Source: `k8s-proxmox/docs/GPU-PCIE-RTD3-INVESTIGATION.md`
Already listed in the parent plan's Appendix B, still valid, still 85%. Currently folded into the 8,364-word Part 3 — **this is the natural split point.** Extracting it solves the oversized-draft problem and produces a better standalone piece than either half is now.
Substrate S4 (validated on all four P620 nodes Aug 13). **~3h.**

### Tier C — worth doing, needs a decision first

**C1 · A Backup Pipeline You Built and Didn't Turn On**
Source: `docs/CEPHFS-BACKUP-PIPELINE.md:37`
Three-tier CephFS backup, built and Grafana-monitored Aug 25–26, **deliberately not in cron** — held back so it wouldn't compete with the gap-fill copy for I/O. Which means the only protection on the family media library is Ceph's `size=3` replication, and the previous backup was discovered ~6.5 months stale with no working cron job.
The article is genuinely good either way, but the framing depends on a decision you should make first: **enable the cron (two lines on edgar) and write it as a finished story, or publish it as-is and title it honestly.** `JMM-TODO.md:39` already argues the hold isn't justified — the nightly and weekly windows don't overlap the copy's heaviest hours, and Leg 1 writes to edgar's local drive, not the same CephFS path.
Substrate S3. **~5h** after the decision.

**C2 · The *arr Suite on Proxmox LXC** — series, 3–4 parts
Source: `docs/ARR-SUITE-DEPLOYMENT-PLAN.md` (170K)
The largest untapped body of verified work in either repo. Part 4 of the upgrade series covers the deployment at a summary level; this would go deep — 11 containers, the WireGuard-namespaced download client, the Ceph-health-gated adaptive throttles with asymmetric hysteresis (treating missing telemetry as YELLOW rather than GREEN is a nice touch worth calling out), stuck-import crons, the kill switch verified by force-killing the interface.
**Blocked on one thing:** Phase 1's real download→import→library-move round-trip test hasn't been done for each download client. That's the difference between "built" and "working." Close it, then write.
Substrate S2 → S4 once that test passes. **~14h** for the series.

### Tier D — do not write yet

Kubernetes 1.36 / Cilium / CAPI (never applied to a live cluster) · DHCP migration (designed only) · ProCurve + LACP + VLAN (switch on a shelf) · NUT/UPS (⬜ since February) · PiKVM (bench verification not done) · Ebook stack (`PLANNING ONLY — nothing has been built`) · Media Integrity test→prod migration (hard-blocked, and the check script deliberately refuses to run).

---

## Part 4 — The summary article

This is the one you asked to see, and it's the strongest single article available right now — because it's the only one that can honestly use August's whole arc as its subject.

### Working title

**"The Month the Homelab Became Production"**

Alternates: *When Your Users Are Your Family* · *140 Commits in 24 Days: What Actually Changed* · *The Homelab Grew Up*

### The thesis

A homelab is a place where breaking things is free. That stopped being true. Somewhere in August — not on a planned date, with no migration and no announcement — the cluster crossed from *evaluation lab* to *production service with users who did not opt in*. Jellyfin and the *arr stack now serve a wife, kids, and three TVs at a beach house over a WireGuard tunnel. The engineering didn't change much. **The change-management posture had to change completely.**

This is exactly the transition every internal platform team goes through, usually without noticing either — the day the internal tool acquires users who don't read your changelog.

### Why this framing works

It's true, it's verifiable, and it explains the August burst as something other than a list. Every workstream becomes evidence for a thesis rather than an inventory entry:

- The Ceph-health-gated throttle exists **because** a background copy caused a real Jellyfin playback stall mid-episode
- Jellyfin HA was tested on all four nodes **because** "it'll probably fail over" stopped being an acceptable answer
- The PVE 9 upgrade needs an announced window **because** six rolling reboots now have an audience
- The NVENC session cap got patched **because** a family of four generates concurrent streams
- The backup pipeline matters **because** the library is now the family's photo-album-equivalent

### Structure

| Section | Content | Word budget |
|---|---|---|
| **The moment it changed** | No announcement, no migration. A phone call about a show that wouldn't play. The realization that the blast radius now includes people who didn't sign up. | 300 |
| **What got built** (grouped, not listed) | Four themes: *storage and safety* (PBS, UrBackup, 3-tier CephFS backup), *the media platform* (11 *arr containers, NVENC, HA), *reach* (3-site WireGuard, two-tier DNS, Tailscale), *seeing* (InfluxDB, Grafana, 18 panels). Each with the one-line reason it now exists. | 700 |
| **What production actually cost** | The three-tier throttle. The `770`/idmap permission model. Verifying HA on all four nodes instead of assuming. The adaptive throttle treating missing telemetry as degraded. Concrete, specific, earned. | 600 |
| **What I got wrong** | The credibility section. Six weeks with no independent backup. A throttle left at 8 KB/s for five days. Recyclarr silently reverting fixes for a week. A backup job reporting success while one VM failed three weeks running. 137 shows unmonitored. **Do not soften these** — they are what makes the rest believable. | 600 |
| **What's still broken** | No alerting. Backup pipeline built and not enabled. Phase 1's round-trip test unclosed. The OS upgrade itself still pending, now needing a family maintenance window. | 400 |
| **What this maps to at scale** | The internal-platform parallel. Change management arriving whether you build it or not. Preparation being the actual work. Announced windows as a feature, not overhead. | 400 |

**Target: ~3,000 words.** That's above the published p75 of 1,698 but justified — this is a synthesis piece and the archive's other long posts carry their length fine.

### Voice notes

Applies all four `PERSONA.md` patterns naturally, which is rare:
- **Opens with why** — the posture change, not "here's what I built"
- **Rejected alternatives** — Tdarr rolled back mid-build rather than risk re-encoding curated media; Kubernetes deliberately not used for the monitoring stack; spare OSDs held as cold spares
- **Enterprise connection** — the whole thesis *is* the connection
- **What this enables** — an announced-window discipline that makes the PVE 9 upgrade tractable

One caution: the "what I got wrong" section carries this article. Written honestly it's the most credible thing on the blog. Softened, it's a victory lap and the reader will feel it.

### Sequencing

Publish this **first**, ahead of the individual gap articles. It establishes the frame that A1–B4 then fill in, and it turns a backlog into a series with a spine. It also works as the honest replacement for those four stale February overview drafts — same job, current facts, actual argument.

### Dependency

Needs **no new engineering.** Every fact is already recorded and dated in `JMM-TODO.md`, `PVE9-UPGRADE-PLAN.md`, `ARR-SUITE-DEPLOYMENT-PLAN.md`, `SITE-TO-SITE-VPN.md`, `MONITORING.md`, and `CEPHFS-BACKUP-PIPELINE.md`. It is a **writing** task, not a build task — which makes it the highest-value-per-hour item in the entire queue.

---

## Part 5 — Revised publication order

Assumes the parent plan's Wednesday anchor and weekly cadence. Twelve slots.

| Slot | Date | Article | Substrate |
|---|---|---|---|
| 1 | 2026-09-09 | **The Month the Homelab Became Production** (summary) | S4 |
| 2 | 2026-09-16 | PVE 8→9 Part 1 — Pre-Flight and the Backup Safety Net | S4 |
| 3 | 2026-09-23 | PVE 8→9 Part 2 — Ceph Reef to Squid | S4 |
| 4 | 2026-09-30 | PVE 8→9 Part 3a — NVIDIA Drivers on Two GPU Generations *(split)* | S4 |
| 5 | 2026-10-07 | PVE 8→9 Part 3b — GPU RTD3 D3cold, Three Incidents *(split, = B4)* | S4 |
| 6 | 2026-10-14 | PVE 8→9 Part 4 — A Media Automation Stack, and Two Incidents | S2→S4 |
| 7 | 2026-10-21 | Observability From Scratch on LXC, Not Kubernetes *(A1)* | S4 |
| 8 | 2026-10-28 | The Dashboards Are Beautiful and Nothing Pages Me *(A2)* | S4 |
| 9 | 2026-11-04 | Three Sites, One Tunnel — Part 1 *(A3)* | S4 |
| 10 | 2026-11-11 | Three Sites, One Tunnel — Part 2 *(A3)* | S4 |
| 11 | 2026-11-18 | The Backup Job That Succeeded While Failing *(A4)* | S4 |
| 12 | 2026-11-25 | Unprivileged LXC, Shared CephFS, Permissions *(B1)* | S4 |

**Held, deliberately:** PVE 8→9 Part 5 until the upgrade runs · *arr series (C2) until the round-trip test closes · CephFS backup pipeline (C1) until the cron decision · everything in Tier D.

**Already-drafted and slotted separately** (these don't compete for the Wednesday anchor since they're a different topic thread): the UrBackup draft, the three Homarr/Homepage drafts, the gap-fill throttle draft, and the three `ct:603` agent-LXC drafts. Eight more near-ready articles. Combined with the twelve above, that's **~20 articles ≈ five months of runway** without writing anything new.

---

## Part 6 — Things to fix before writing from these sources

Additions to the parent plan's [Appendix C](../KIRO-CLAUDE-OPUS5-MAX-ARTICLE-REVIEW.md#appendix-c--stale-claims-register). Each will propagate into an article if not corrected first.

| Location | Stale claim | Reality |
|---|---|---|
| `k8s-proxmox/docs/PVE9-UPGRADE-PLAN.md:3` | `Status: Planning only — no execution yet (as of Aug 4, 2026)` + `Nothing in this document has been run except the read-only audit steps` | Phase 0, 0b, all 8 pre-flight items, and all of Phase A executed and verified Aug 5–12. Phase A restarted all 31 Ceph daemons. **Most dangerous stale header in either repo** — a future agent session could re-run destructive steps. |
| `k8s-proxmox/PRE-K8S-TASKS.md` | Every task `Status: ⬜ Not Started` | Tasks 1.1 (edgar boot drive), 1.2 (PBS), 2.1 (VPN), 3.1 (*arr suite) are all done |
| `k8s-proxmox/docs/SITE-TO-SITE-VPN.md:3` | `Status: Deployed (Raleigh + Beach)`; Wilson `(future)` in 5 tables | Wilson live Aug 30–31, serving Jellyfin traffic |
| `k8s-proxmox/JMM-TODO.md:172` | Wilson `not yet shipped` | Contradicted by `:316` **in the same file** and by commit `ee603a0` |
| `k8s-proxmox/docs/MEDIA-CLEANUP.md:5` | `No ARR suite yet` | Suite built Aug 14–27; the 44-file re-acquisition backlog became actionable weeks ago |
| `k8s-proxmox/README.md` (Ansible section) | Kubernetes 1.33, Calico CNI | `ansible/group_vars/all.yml`: `k8s_version: "1.36"`, `cni_plugin: "cilium"` |
| `k8s-proxmox/TODO.md` | Site-to-Site VPN as `🔴 HIGH PRIORITY` task #1 | Done. File is dead (last touched Feb 8) |

---

## Appendix — verification boundary

Everything above about **what exists** comes from reading both repos: git history (206 commits, per-file last-touch, per-day distribution), document contents, and cross-checking status headers against commit evidence and other docs.

**Not verified:** live cluster state. Whether the gap-fill copy is still running (last recorded progress 2026-08-29 — `L 27%, M 8%` — with no commits since Sep 1, so it has likely been unattended ~10 days). Whether the CephFS backup cron got enabled. Whether `osd.3` has recurred a fourth time. Whether `openwrt-vm` failed a fourth and fifth week.

`S4` in this document means **someone recorded a dated live observation in the repo** — not that I confirmed it against hardware. The repos are unusually disciplined about this distinction, and several entries flag their own weaknesses, which is why the substrate scores are trustworthy enough to publish from after a spot-check.

**Two items to re-check before writing the articles that depend on them:** the `openwrt-vm` backup fix (A4) and the Phase 1 round-trip test (C2).
