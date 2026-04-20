---
layout: none
date: 1999-12-31
sitemap: false
---

# Drafts — Publish Readiness & Planning

Working document for draft management. Focus: what needs work, what's next, and how drafts cluster together.

Last updated: 2026-04-20

---

## Upcoming Schedule (Drafts)

| Date | Day | Article | Effort Needed |
|------|-----|---------|---------------|
| 07-01 | Wed | StarVoyager: Legacy SDL to Cross-Platform | Screenshots, verify repo links |
| 07-03 | Fri | Godot Tower Defense Game | Retitle, verify repo, trim roadmap |
| 07-06 | Mon | Jekyll GDPR Plugin Development | Finish plugin, write companion article |

---

## Article Clusters

Drafts that form natural publishing sequences or share a topic.

| Cluster | Drafts | Notes |
|---------|--------|-------|
| 🌐 **Domain & Email Migration** | email-forwarding-evaluation | Registrars published; email is the follow-up |
| 🎮 **Game Development** | starvoyager, godot-vscode | Independent but pair well (July 1, 3) |
| 🌍 **Proxmox SDN & Networking** | powerdns-lxc, openwrt-lxc, lag-lacp | PowerDNS, OpenWRT LXC, and LAG/LACP |
| 📝 **Jekyll Deep Dives** | enhancements-without-plugins, internal-formatting | Remaining Jekyll drafts |
| 🗄️ **Ceph Storage** | ceph-osd-moving-disks, ceph-reef-to-squid | OSD moves, Reef→Squid upgrade |
| 🏗️ **Homelab Infrastructure** | overview, checklist, roadmap, upgrades | Massive overlap — pick ONE |
| 🧠 **Data Science & AI/ML** | five-stages, research-model, phonemes, multi-gpu | Merge or publish separately |
| 🔌 **Run Jekyll Extension** | See `RUNJEKYLL-EXTENSION.md` | All 7 articles published |
| 🔐 **Jekyll GDPR Plugin** | See `JEKYLLGDPR-PLUGIN.md` | Tracks 2026-07-06 plugin productization and reuse from prior plugin CI/CD work |
| 🔒 **Draft Preview Site** | — | All 3 parts published |
| 🔧 **Caddy Reverse Proxy** | — | Both articles published |

---

## Tracker Files

| Tracker | Purpose |
|---------|---------|
| `DRAFTS.md` | Master publication planning and readiness |
| `RUNJEKYLL-EXTENSION.md` | Run Jekyll extension project status and article sequence |
| `JEKYLLGDPR-PLUGIN.md` | GDPR plugin productization plan tied to the 2026-07-06 article |

---

## Quick Wins (< 1 hour)

| File | Effort | Cluster |
|------|--------|---------|
| `email-forwarding-evaluation.md` | 15 min | 🌐 Domain & Email |
| `starvoyager-game.md` | 1 hr | 🎮 Game Dev |
| `godot-vscode.md` | 1 hr | 🎮 Game Dev |

---

## Tier 1: Ready to Publish (< 30 min)

### `2026-02-07-email-forwarding-evaluation.md` — 🌐 Domain & Email

- Complete evaluation with cost comparison tables, migration strategy, decision matrix
- **What's needed:** Minor date fix. Registrars article (prerequisite) is now published.
- **Effort:** 15 minutes

---

## Tier 2: Near-Complete (1–2 hours each)

### `2026-07-01-starvoyager-game.md` — 🎮 Game Dev

- Well-written overview of StarVoyager modernization
- **What's needed:** Verify GitHub repo links and stats (87 files, 261 tests). Add screenshots.
- **Effort:** 1 hour

### `2026-07-03-godot-vscode.md` — 🎮 Game Dev

- Solid tower defense game project overview with personal backstory
- **What's needed:** Retitle (content is broader than "Godot VSCode"). Verify repo link. Trim roadmap sections.
- **Effort:** 1 hour

### `2026-02-01-powerdns-lxc-proxmox-sdn-integration.md` — 🌍 SDN & Networking

- Comprehensive technical guide, marked "DRAFT ahead of PR"
- **What's needed:** Confirm PR status. Update text if merged. Mermaid diagram and code are solid.
- **Effort:** 1 hour

### `2026-02-02-openwrt-lxc-native-implementation-journey.md` — 🌍 SDN & Networking

- Excellent narrative of 4 approaches tested, marked "DRAFT ahead of PR"
- **What's needed:** Confirm PR status. The "four approaches" structure is compelling.
- **Effort:** 1 hour

### `2026-05-10-jekyll-enhancements-without-plugins.md` — 📝 Jekyll Deep Dives

- Comprehensive reference of jekyllcodex.org implementations evaluated against this blog.
- **What's needed:** Add personal experience notes to each section.
- **Effort:** 1-2 hours

### `2026-05-01-claude-code-setup-guide.md`

- Well-written, complete guide
- **What's needed:** Fix broken front matter. Fact-check the Amazon Q / Kiro claim.
- **Effort:** 1 hour

### `2026-05-10-jekyll-internal-formatting-front-matter.md` — 📝 Jekyll Deep Dives

- Stub with acronym grep technique and section outlines.
- **What's needed:** Flesh out all sections.
- **Effort:** 2-3 hours

### `2024-11-18-five-stages-cloud-data-science-platform.md` — 🧠 Data Science & AI/ML

- Strong opinion piece. Core insight: DS needs production data in dev-like environments.
- **What's needed:** Light editing. Could use a real-world example or diagram.
- **Effort:** 1-2 hours

### `2026-01-01-photosynth-update.md`

- Georgia Tech PyPhotoSynthExport retrospective, Photosynth shutdown, open-source alternatives.
- **What's needed:** Split into retrospective + companion implementation article.
- **Effort:** 1 hour (retrospective) or 3-4 hours (with implementation)

### `2024-03-11-lag-lacp-nic-bonding.md` — 🌍 SDN & Networking

- Nice highway/traffic analogy. Includes critical LACP misconception about single TCP connections.
- **What's needed:** Add practical section — ProCurve config, Proxmox bond setup, performance results.
- **Effort:** 2 hours

---

## Tier 3: Substantial Work Needed (3+ hours)

### `2024-11-18-research-as-a-model-for-data-science.md` — 🧠 Data Science & AI/ML

- Core thesis: DS fails more than it succeeds (1 in 5 vs SD's 4 in 5).
- **Recommendation:** Merge into five-stages article, or expand standalone.

### `2026-02-12-proxmox-homelab-infrastructure-overview.md` — 🏗️ Homelab Infrastructure
### `2026-02-13-pre-kubernetes-homelab-checklist.md` — 🏗️ Homelab Infrastructure
### `2026-02-05-proxmox-cluster-roadmap-vms-project.md` — 🏗️ Homelab Infrastructure
### `2026-04-01-homelab-infrastructure-upgrades.md` — 🏗️ Homelab Infrastructure

- **Problem:** Massive overlap — all describe the same cluster, hardware, and plans.
- **Recommendation:** Pick ONE. Overview is most self-contained. Checklist is most actionable.

### `2024-01-27-networking-site-2-site-vpn.md` — 🌍 SDN & Networking

- GL-iNet Slate AX and Brume 2 hardware, CIDR planning. Stops at "Network Diagrams."
- **Effort:** 2-3 hours to finish standalone

### `2024-04-03-pikvm-and-kvm.md`

- Detailed parts list ($520 total, $65/machine). Stops before configuration section.
- **Effort:** 2-3 hours

### `2024-06-21-ceph-osd-moving-disks.md` — 🗄️ Ceph Storage

- Clear problem (4 OSDs on 3 nodes → 3 OSDs on 4 nodes), screenshots, research links.
- **Effort:** 1-2 hours

### `2026-04-01-phonemes-aiml-research.md` — 🧠 Data Science & AI/ML

- Research plan/roadmap. Reframe as "research directions" rather than results.
- **Effort:** 1-2 hours

### `2025-01-01-tankless-water-heater-flush.md`

- Practical guide. Equipment list, process overview, lessons learned.
- **What's needed:** Add photos. Flesh out process steps.
- **Effort:** 1 hour with photos

### `2024-08-01-oh-my-zshell-wslv2.md`

- Oh My Zsh + T480 dev environment (WSLv2, VSCode, Chocolatey), nvidia MX150.
- **Effort:** 2 hours

### `2024-06-20-chocolatey-packaging-easywsl.md`

- Chocolatey account setup, Quick Start docs, PowerToys dependency patterns.
- **Effort:** 1-2 hours

### `2025-02-02-multi-gpu-multi-node.md` — 🧠 Data Science & AI/ML

- Link collection — Ollama, LiteLLM, llama.cpp, Exo, GPU comparisons.
- **Effort:** 1 hour (roundup) or 3-4 hours (with experiments)

---

## Tier 4: Too Raw / Hold / Archive

### `2026-07-06-jekyll-gdpr-plugin-development.md` — Scheduled July 6

- Aspirational plugin development plan — no code shipped yet.
- **Action:** Complete the plugin, publish as a Ruby gem, write companion article.

### `2026-01-03-jekyll-resume-post-type-implementation.md`

- Technical exploration, no implementation. May be superseded by Pandoc approach.

### `2024-12-31-jekyll-add-header-links.md` / `2024-12-31-jekyll-code-copy-buttons.md`

- Stub research notes. Flesh out or archive.

### `2025-02-20-ceph-reef-to-squid-upgrade.md` — 🗄️ Ceph Storage

- 4 lines — just a link. Expand when upgrade is performed.

### `2025-02-10-oracle-cloud-infra-learning.md`

- OCI Always Free Tier link collection. Publish if tried, otherwise archive.

### `2025-01-01-hosting-for-hobbiest.md`

- Stub comparing free tiers. Goes stale fast.

### `2024-12-01-k8s-on-proxmox-with-tf-ansible.md`

- ClusterCreator evaluation. Likely superseded by k8s-proxmox repo.

### `2025-03-01-thoughts-on-directions-for-aiml.md`

- 2 lines total. Archive and start fresh.

---

## Tier 5: Superseded — Archive Candidates

### `2024-06-11-promox-sdn-options.md`

- Superseded by PowerDNS SDN (#11) and OpenWRT LXC (#12)

### `2024-09-09-proxmox-sdn-openwrt-lxc.md`

- Superseded by `openwrt-lxc-native-implementation-journey.md`

### `2024-09-13-proxmox-lxc-template-openwrt.md`

- Superseded by #12 — merge the `openwrt.common.conf` detail if not already there.

---

## Summary

| Category | Count |
|----------|-------|
| Drafts in `_drafts/` | 36 |
| Ready to publish (Tier 1) | 1 |
| Near-complete (Tier 2) | 10 |
| Substantial work (Tier 3) | 12 |
| Too raw / hold (Tier 4) | 8 |
| Superseded (Tier 5) | 3 |
| Scheduled (July) | 3 |
| Tracker files | 3 (`DRAFTS.md`, `RUNJEKYLL-EXTENSION.md`, `JEKYLLGDPR-PLUGIN.md`) |

---

## Substack Publication Schedule

| Date | Title | Blog Posts Referenced |
|------|-------|---------------------|
| 2026-04-04 | From Homelabs to Machine Learning | Infrastructure series |
| 2026-04-20 | From Markdown to Production | Jekyll series |
| 2026-05-18 | When Storage Breaks | Ceph & ZFS series |
| TBD | Machine Learning (planned) | AI/ML research, phonemes, cloud DS platforms |
