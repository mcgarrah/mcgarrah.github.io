---
layout: none
date: 1999-12-31
sitemap: false
---

# Drafts — Publish Readiness & Planning

Working document for draft management. Focus: what needs work, what's next, and how drafts cluster together.

Last updated: 2026-07-29

---

## Upcoming Schedule (Drafts)

| Date | Day | Article | Effort Needed |
|------|-----|---------|---------------|
| 07-30 | Wed | StarVoyager: Legacy SDL to Cross-Platform | Screenshots, verify repo links |
| 08-01 | Fri | Godot Tower Defense Game | Retitle, verify repo, trim roadmap |
| 08-04 | Mon | AASR Series Overview | Review, verify series links |
| 08-06 | Wed | AASR: AI Agent Cluster on Proxmox (Part 1) | Review, verify technical details |
| 08-08 | Fri | Git History Bloat Cleanup (Part 1) | Complete audit, document execution, console outputs |
| 08-11 | Mon | Git Repository Audit Methodology (Part 2) | Audit all repos, findings, decision matrix |
| 08-13 | Wed | Git Health Monitoring Outline (Part 3) | Convert outline after Parts 1-2 done |
| 08-15 | Fri | Claude Code Setup Guide | Fix front matter, fact-check claims |
| 08-18 | Mon | Photosynth: Open Source Alternatives | Split retrospective, verify links |
| 08-20 | Wed | Jekyll GDPR Plugin Development | Finish plugin, write companion article |
| 08-22 | Fri | Jekyll Dark Mode Toggle | Implement toggle, document |
| 08-25 | Mon | Tag Sprawl Consolidation | Audit, merge 138 singletons |
| 08-27 | Wed | Front Matter Hygiene Audit | Script + batch update 139 posts |
| 08-29 | Fri | Security Hardening (CSP, SRI) | Add integrity hashes, CSP meta tag |
| 09-01 | Mon | Plausible vs Google Analytics | Evaluate, decide, document |
| 09-03 | Wed | Post Series Navigation | Implement prev/next for multi-part series |
| 09-05 | Fri | Vanity URLs for AWS QuickSight with Terraform | Review, add real-world context |
| TBD | — | FastAPI Nutrition API (4-part series) | Build project first, then write articles |

---

## Article Clusters

Drafts that form natural publishing sequences or share a topic.

| Cluster | Drafts | Notes |
|---------|--------|-------|
| 🌐 **Domain & Email Migration** | email-forwarding-evaluation | Registrars published; email is the follow-up |
| 🎮 **Game Development** | starvoyager, godot-vscode | Independent but pair well (July 1, 3) |
| 🌍 **Proxmox SDN & Networking** | powerdns-lxc, openwrt-lxc, lag-lacp | PowerDNS, OpenWRT LXC, and LAG/LACP |
| 📝 **Jekyll Deep Dives** | enhancements-without-plugins, internal-formatting, dark-mode-toggle, tag-sprawl, front-matter-hygiene, post-series-navigation | Active cluster with 6 drafts |
| 🛡️ **Jekyll Security & Privacy** | security-hardening-csp-sri, plausible-vs-google-analytics | New cluster from TODO.md items |
| 🧰 **Git & Repository Maintenance** | git-history-bloat-drafts-repo-cleanup, git-repo-audit-methodology-findings, git-health-monitoring-github-actions-outline | Series in progress: Part 1 (cleanup execution), Part 2 (audit methodology), Part 3 outline (future automation) |
| 🗄️ **Ceph Storage** | ceph-osd-moving-disks, ceph-reef-to-squid | OSD moves, Reef→Squid upgrade |
| 🏗️ **Homelab Infrastructure** | overview, checklist, roadmap, upgrades | Massive overlap — pick ONE |
| 🧠 **Data Science & AI/ML** | five-stages, research-model, phonemes, multi-gpu | Merge or publish separately |
| 🤖 **AASR / AME** | See `AASR-PROJECT.md`, `AME-GPT-EXPLORATION.md` | AASR infrastructure series (5 parts) + AME GPT deep dive series. Series index: `2026-07-01-aasr-project-series-overview.md` |
| ☁️ **AWS Terraform Modules** | terraform-aws-quicksight-redirect | CloudFront vanity URL redirect for QuickSight |
| 🍎 **FastAPI Nutrition API** | See `FASTAPI-NUTRITION-API.md` | 4-article series: architecture, implementation, deployment, observability. Unified Food Intelligence API with USDA FDC, Open Food Facts, GS1 GPC |
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
| `GITREPO-CLEAN.md` | Git repository cleanup, audit, and future automation project tracking |
| `AASR-PROJECT.md` | Autonomous AI Scientific Research — canonical project tracker and implementation reference |
| `AME-GPT-EXPLORATION.md` | Autonomous Model Evolution — GPT deep dive extending the AASR project |
| `FASTAPI-NUTRITION-API.md` | FastAPI Nutrition API — project planning, Gemini conversation archive, 4-article series outline |

---

## Quick Wins (< 1 hour)

| File | Effort | Cluster |
|------|--------|---------|
| `email-forwarding-evaluation.md` | 15 min | 🌐 Domain & Email |
| `starvoyager-game.md` | 1 hr | 🎮 Game Dev |
| `godot-vscode.md` | 1 hr | 🎮 Game Dev |
| `jekyll-tag-sprawl-consolidation.md` | 1 hr | 📝 Jekyll Deep Dives |
| `plausible-vs-google-analytics.md` | 1 hr | 🛡️ Security & Privacy |
| `git-history-bloat-drafts-repo-cleanup.md` (Part 1) | 45 min | 🧰 Git & Repo Maintenance |
| `git-repo-audit-methodology-findings.md` (Part 2) | 45 min | 🧰 Git & Repo Maintenance |
| `terraform-aws-quicksight-redirect.md` | 30-45 min | ☁️ AWS Terraform Modules |

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

### `2026-07-08-jekyll-dark-mode-toggle.md` — 📝 Jekyll Deep Dives

- Site already has `prefers-color-scheme` CSS but no user override.
- **What's needed:** Implement toggle, refactor SASS to dual system, prevent FOWT, handle Mermaid/Giscus.
- **Effort:** 2-3 hours

### `2026-07-10-jekyll-tag-sprawl-consolidation.md` — 📝 Jekyll Deep Dives

- 138 of 237 tags used on exactly one post. Each generates a useless tag page.
- **What's needed:** Audit script, decision framework, perform merges, document results.
- **Effort:** 1-2 hours

### `2026-07-13-jekyll-front-matter-hygiene.md` — 📝 Jekyll Deep Dives

- 120 posts missing description, 50 missing tags, 34 missing excerpt separator, 62 missing last_modified_at.
- **What's needed:** Audit script, batch updates, prioritize by traffic.
- **Effort:** 2-3 hours

### `2026-07-15-jekyll-security-hardening-csp-sri.md` — 🛡️ Security & Privacy

- CDN scripts load with no integrity verification, no CSP restricting execution.
- **What's needed:** Generate SRI hashes, draft CSP, evaluate self-hosting.
- **Effort:** 2-3 hours

### `2026-07-17-plausible-vs-google-analytics.md` — 🛡️ Security & Privacy

- GA requires GDPR consent overhead. Plausible is cookie-free and $9/month.
- **What's needed:** Feature comparison, GDPR simplification analysis, decision.
- **Effort:** 1-2 hours

### `2026-07-20-jekyll-post-series-navigation.md` — 📝 Jekyll Deep Dives

- Multi-part series have manual cross-references that don't scale.
- **What's needed:** Design front matter convention, build Liquid include, retrofit existing series.
- **Effort:** 2-3 hours

### `2026-07-28-terraform-aws-quicksight-redirect.md` — ☁️ AWS Terraform Modules

- Complete draft covering CloudFront Function redirect pattern for QuickSight vanity URLs.
- **What's needed:** Add real-world context (enterprise BI rollout, multi-account scenario). Confirm GitHub repo is public. Consider Terraform Registry publication.
- **Effort:** 30-45 minutes

### `2026-07-08-git-history-bloat-drafts-repo-cleanup.md` — 🧰 Git & Repository Maintenance

- Complete draft documenting repo bloat root cause (historical binary blobs), mitigation options, and rewrite-history + re-clone runbook.
- **What's needed:** Confirm final migration checklist details, add post-cleanup metrics once executed.
- **Effort:** 30-45 minutes

### `2024-03-11-lag-lacp-nic-bonding.md` — 🌍 SDN & Networking

- Nice highway/traffic analogy. Includes critical LACP misconception about single TCP connections.
- **What's needed:** Add practical section — ProCurve config, Proxmox bond setup, performance results.
- **Effort:** 2 hours

---

## Tier 3: Substantial Work Needed (3+ hours)

### `2026-07-24-git-health-monitoring-github-actions-outline.md` — 🧰 Git & Repository Maintenance

- Outline only for a future Part 3 focused on GitHub Actions-based git-health reporting.
- **What's needed:** Convert outline into a real article after Part 1 is executed and Part 2 is revised with actual results.
- **Effort:** 3-4 hours

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

### FastAPI Nutrition API Series (4 articles) — 🍎 FastAPI Nutrition API

- **Article 1:** Architecture & Design — Ranked Truth Model, Canonical Data Model, resume connections
- **Article 2:** Implementation — async patterns, DataOrchestrator mapper, graceful degradation
- **Article 3:** Infrastructure & Deployment — Dockerfile, `.do/app.yaml`, GitHub Actions CI/CD on DigitalOcean App Platform
- **Article 4:** Observability & Production Readiness — OpenTelemetry, Prometheus, data freshness telemetry
- **What's needed:** Build the project repo first (`fastapi-nutrition-api`), then write articles from working code. Requires `usda_fdc_python` and `gs1_gpc_python` async wrappers.
- **Effort:** 3-4 hours per article (12-16 hours total), plus project implementation time
- **Tracker:** `FASTAPI-NUTRITION-API.md`

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
| Drafts in `_drafts/` | 46 |
| Ready to publish (Tier 1) | 1 |
| Near-complete (Tier 2) | 18 |
| Substantial work (Tier 3) | 13 |
| Too raw / hold (Tier 4) | 8 |
| Superseded (Tier 5) | 3 |
| Scheduled (upcoming) | 18 |
| Tracker files | 7 (`DRAFTS.md`, `RUNJEKYLL-EXTENSION.md`, `JEKYLLGDPR-PLUGIN.md`, `GITREPO-CLEAN.md`, `AASR-PROJECT.md`, `AME-GPT-EXPLORATION.md`, `FASTAPI-NUTRITION-API.md`) |

---

## Substack Publication Schedule

| Date | Title | Blog Posts Referenced |
|------|-------|---------------------|
| 2026-04-04 | From Homelabs to Machine Learning | Infrastructure series |
| 2026-04-20 | From Markdown to Production | Jekyll series |
| 2026-05-18 | When Storage Breaks | Ceph & ZFS series |
| 2026-06-15 | From Bug Fix to VS Code Marketplace | Run Jekyll extension series |
| 2026-07-13 | Building in Public | Preview site, domain migration, Google tax |
| TBD | Machine Learning (planned) | AI/ML research, phonemes, cloud DS platforms |
