# Drafts Review — Publish Readiness Analysis

Reviewed: All 44 drafts in `_drafts/` folder
Cross-referenced against: All published posts in `_posts/` and `_substack/`
Last updated: 2026-04-17

---

## Recently Promoted / Removed

| Draft file | Published as | Date |
|------------|-------------|------|
| ~~`2024-09-01-proxmox-ceph-nearfull.md`~~ | `2025-09-28-proxmox-ceph-nearfull.md` | Deleted 2025-07-15 |
| ~~`2024-09-02-proxmox-ceph-performance.md`~~ | `2025-10-12-proxmox-ceph-performance.md` | Deleted 2025-07-15 |
| ~~`2025-02-16-usb3-drive-smart.md`~~ | `2025-10-26-usb-drive-smart.md` + `2026-02-03-usb-drive-smart-updates.md` | Deleted 2025-07-15 |
| ~~`2025-09-29-ceph-osd-debugging.md`~~ | `2026-04-14-ceph-osd-recovery-power-failure.md` | Promoted 2026-04-12 |
| ~~`(written directly)`~~ | `2026-04-15-zfs-ceph-overlapping-failures.md` | Written directly to _posts 2026-04-12 |
| ~~`2024-08-26-proxmox-misc-scripts.md`~~ | `2024-08-26-proxmox-8-dell-wyse-3040-upgrade.md` | Deleted 2026-04-12 (duplicate) |
| ~~`2026-04-01-jekyll-markdown-feature-reference.md`~~ | `2026-04-20-jekyll-markdown-feature-reference.md` | Promoted 2026-04-13, rescheduled 2026-04-20 |
| ~~`2026-04-02-learning-jekyll.md`~~ | `2026-04-19-setting-up-jekyll-blog-github-pages.md` | Promoted 2026-04-13 |
| ~~`2025-10-05-ceph-ssd-wal-db-usb-storage.md`~~ | `2026-04-16-ceph-ssd-wal-db-usb-storage.md` | Promoted 2026-04-13, rescheduled 2026-04-16 |
| ~~`2024-12-31-jekyll-add-comments-section.md`~~ | Merged into `2026-05-10-jekyll-giscus-comments-implementation.md` | Deleted (content merged) |
| ~~`2026-04-25-ssh-key-access-proxmox-cluster.md`~~ | `2026-04-17-ssh-key-access-proxmox-cluster.md` | Promoted 2026-05-18, rescheduled 2026-04-16 |
| ~~`2025-12-16-ruby-gem-release-automation.md`~~ | `2026-04-11-ruby-gem-release-automation.md` | Deleted (superseded, published version has additional content) |
| ~~`2026-04-26-ceph-wal-vs-db-performance-test.md`~~ | `2026-04-18-ceph-wal-vs-db-performance-test.md` | Promoted 2026-05-18, rescheduled 2026-04-16 |
| ~~`2024-08-15-ghp-jekyll-upgrade.md`~~ | `2026-04-22-jekyll-upgrade-two-years-cascading-breakage.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-content-plumbing-permalinks-reading-time.md`~~ | `2026-04-25-jekyll-content-plumbing-permalinks-reading-time.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-small-things-polish-features.md`~~ | `2026-04-28-jekyll-small-things-polish-features.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-liquid-code-fence-rendering-trap.md`~~ | `2026-04-30-jekyll-liquid-code-fence-rendering-trap.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-tag-category-generator-plugin.md`~~ | `2026-05-02-jekyll-tag-category-generator-plugin.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-giscus-comments-implementation.md`~~ | `2026-05-05-jekyll-giscus-comments-implementation.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-github-actions-cicd-pipeline.md`~~ | `2026-05-07-jekyll-github-actions-cicd-pipeline.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-run-vscode-plugin-local-development.md`~~ | `2026-05-09-jekyll-run-vscode-plugin-local-development.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-draft-future-visual-indicators.md`~~ | `2026-05-12-jekyll-draft-future-visual-indicators.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-10-jekyll-content-distribution-pipeline.md`~~ | `2026-05-14-jekyll-content-distribution-pipeline.md` | Promoted 2026-04-16 (batch) |
| ~~`2026-05-15-caddy-reverse-proxy-proxmox-web-ui.md`~~ | `2026-05-16-caddy-reverse-proxy-proxmox-web-ui.md` | Promoted 2026-04-16 |
| ~~`2026-05-15-caddy-reverse-proxy-ceph-dashboard.md`~~ | `2026-05-19-caddy-reverse-proxy-ceph-dashboard.md` | Promoted 2026-04-16 |
| ~~`writing-to-think-two-decades-of-figuring-things-out.md`~~ | `2026-05-21-writing-to-think-two-decades-of-figuring-things-out.md` | Promoted 2026-04-16 |
| ~~`2025-02-25-proxmox-zfs-boot-mirrors-part-1.md`~~ | `2026-05-25-proxmox-zfs-boot-mirrors-part-1.md` | Promoted 2026-04-16, rescheduled to MWF |
| ~~`2024-09-23-zfs-boot-mirrors-proxmox8-part-1.md`~~ | Merged into `2026-05-25-proxmox-zfs-boot-mirrors-part-1.md` | Retired 2026-04-16 |
| ~~`2026-05-24-proxmox-zfs-boot-mirrors-part-3.md`~~ | `2026-05-29-proxmox-zfs-boot-mirrors-part-2.md` | Promoted 2026-04-17, renumbered Part 3→2 |
| ~~`2025-02-26-proxmox-zfs-boot-mirrors-part-2.md`~~ | `2026-06-03-proxmox-zfs-boot-mirrors-part-3.md` | Promoted 2026-04-17, renumbered Part 2→3 |
| ~~`2026-06-29-ai-coding-agent-context-files-reference.md`~~ | `2026-05-27-ai-coding-agent-context-files-reference.md` | Promoted 2026-04-17 |
| ~~`2026-06-30-managing-cross-ai-agent-context.md`~~ | `2026-06-01-managing-cross-ai-agent-context.md` | Promoted 2026-04-17 |

### MWF Cadence Correction (2026-04-17)

All 16 posts from April 20 onward were rescheduled from an incorrect Tue/Thu/Sat cadence to the intended Mon/Wed/Fri cadence. Filenames and all four date fields updated. Permalink is `/:title/` so URL slugs were unchanged.

### ZFS Series Renumbering (2026-04-17)

The ZFS boot mirror series was reordered to match the narrative arc:
- Part 1: Same-size drive replacement (routine)
- Part 2: Emergency recovery from dual-drive failure (Harlan — already happened)
- Part 3: Planned migration to smaller SSDs with UEFI upgrade (applying lessons learned)

Old Part 2 (send/receive migration) was rewritten as a fresh-install procedure with UEFI upgrade and became Part 3. Old Part 3 (emergency recovery) became Part 2.

---

## Substack Publication Schedule

| Date | Title | Blog Posts Referenced |
|------|-------|---------------------|
| 2026-04-04 | From Homelabs to Machine Learning | Infrastructure series (Proxmox, Ceph, Dell Wyse, monitoring) |
| 2026-04-20 | From Markdown to Production | Jekyll series (feature reference, setup guide, SEO, GDPR, Pandoc, Mermaid, optimization, AdSense debugging, SASS architecture) |
| 2026-05-18 | When Storage Breaks | Ceph failures & recovery, hybrid SSD/USB architecture, WAL vs DB benchmarks, ZFS overlapping failures, SSH access, storage economics |
| TBD | Machine Learning (planned) | AI/ML research, phonemes, cloud DS platforms |

---

## Article Clusters

Drafts that form natural publishing sequences or share a topic. Publish in order within each cluster.

| Cluster | Drafts | Notes |
|---------|--------|-------|
| 🌐 **Domain & Email Migration** | #1, #2 | Publish registrars first, email second |
| 🖥️ **Proxmox ZFS Boot Mirrors** | — | All 3 parts promoted (Part 1 Mon 5/25, Part 2 Fri 5/29, Part 3 Wed 6/3) |
| 🎮 **Game Development** | #9, #10 | StarVoyager and Godot — independent but pair well |
| 🌍 **Proxmox SDN & Networking** | #11, #12, #22 | PowerDNS, OpenWRT LXC, and LAG/LACP |
| 🔌 **Jekyll Run → Run Jekyll** | #19a (published), new drafts | macOS crash fix, fork/rename, bug fixes, testing |
| 📝 **Jekyll Deep Dives** | #16, #17, #18 | Remaining Jekyll drafts (10 promoted 2026-04-16) |
| 🗄️ **Ceph Storage** | #21, #28 | OSD moves, Reef→Squid upgrade |
| 🔧 **Caddy Reverse Proxy** | #22a, #22b | Proxmox Web UI + Ceph Dashboard — publish Proxmox first |
| 🔑 **SSH & Remote Access** | — | Published; prerequisite for #20 (WAL/DB benchmarks) |
| 🏗️ **Homelab Infrastructure** (overlapping) | #24, #25, #26 | Pick ONE of these three to publish |
| 🧠 **Data Science & AI/ML** | #23, #29 | Five Stages + Research model — merge or publish separately |
| 🔒 **Draft Preview Site** | new | 3-part series: options exploration, design refinement, implementation |

---

## Tier 1: Ready to Publish (< 30 min each)

### 0. ~~`writing-to-think-two-decades-of-figuring-things-out.md`~~ — ✍️ Personal/Writing — PROMOTED

- **Published as:** `2026-05-21-writing-to-think-two-decades-of-figuring-things-out.md`

### 1. `2026-02-06-name-service-registrars.md` — 🌐 Domain & Email

- **Status:** Extremely detailed, well-structured, 56% migration complete with real data
- **What's needed:** Update progress section if more domains migrated. Fix future date. Add `categories`/`tags` front matter.
- **Estimated effort:** 30 minutes

### 2. `2026-02-07-email-forwarding-evaluation.md` — 🌐 Domain & Email

- **Status:** Complete evaluation with cost comparison tables, migration strategy, decision matrix
- **What's needed:** Publish #1 first (referenced). Minor date fix.
- **Estimated effort:** 15 minutes

### 3. `2026-03-15-google-service-sprawl.md`

- **Status:** Complete opinion piece, good personal voice
- **What's needed:** Add links to GDPR/AdSense posts. Date fix.
- **Related:** `2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md`, `2026-04-06-adsense-verification-gdpr-script-loading-fix.md`
- **Estimated effort:** 15 minutes

### 4. ~~`2026-05-10-jekyll-tag-category-generator-plugin.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-05-02-jekyll-tag-category-generator-plugin.md`

### 5. ~~`2025-02-25-proxmox-zfs-boot-mirrors-part-1.md`~~ — 🖥️ ZFS Boot Mirrors — PROMOTED

- **Published as:** `2026-05-25-proxmox-zfs-boot-mirrors-part-1.md` (rescheduled MWF)

### 6. ~~`2026-05-10-jekyll-giscus-comments-implementation.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-05-05-jekyll-giscus-comments-implementation.md`

### 7. ~~`2026-05-10-jekyll-content-plumbing-permalinks-reading-time.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-04-25-jekyll-content-plumbing-permalinks-reading-time.md`

### 8. ~~`2024-08-15-ghp-jekyll-upgrade.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-04-22-jekyll-upgrade-two-years-cascading-breakage.md`

---

## Tier 2: Near-Complete (1–2 hours each)

### 9. `2026-02-15-starvoyager-game.md` — 🎮 Game Dev

- **Status:** Well-written overview of StarVoyager modernization
- **What's needed:** Verify GitHub repo links and stats (87 files, 261 tests). Add screenshots.
- **Estimated effort:** 1 hour

### 10. `2026-03-01-godot-vscode.md` — 🎮 Game Dev

- **Status:** Solid tower defense game project overview with personal backstory
- **What's needed:** Retitle (content is broader than "Godot VSCode"). Verify repo link. Trim roadmap sections.
- **Estimated effort:** 1 hour

### 11. `2026-02-01-powerdns-lxc-proxmox-sdn-integration.md` — 🌍 SDN & Networking

- **Status:** Comprehensive technical guide, marked "DRAFT ahead of PR"
- **What's needed:** Confirm PR status. Update text if merged. Mermaid diagram and code are solid.
- **Related:** `2025-02-01-google-wifi-with-openwrt.md`
- **Estimated effort:** 1 hour

### 12. `2026-02-02-openwrt-lxc-native-implementation-journey.md` — 🌍 SDN & Networking

- **Status:** Excellent narrative of 4 approaches tested, marked "DRAFT ahead of PR"
- **What's needed:** Confirm PR status. The "four approaches" structure is compelling.
- **Related:** `2025-02-01-google-wifi-with-openwrt.md`
- **Estimated effort:** 1 hour

### 13. ~~`2026-05-10-jekyll-github-actions-cicd-pipeline.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-05-07-jekyll-github-actions-cicd-pipeline.md`

### 14. ~~`2026-05-10-jekyll-small-things-polish-features.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-04-28-jekyll-small-things-polish-features.md`

### 15. ~~`2026-05-10-jekyll-content-distribution-pipeline.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-05-14-jekyll-content-distribution-pipeline.md`

### 16. `2026-05-10-jekyll-enhancements-without-plugins.md` — 📝 Jekyll Deep Dives

- **Status:** Comprehensive reference of jekyllcodex.org implementations evaluated against this blog. Documents `clean`/`upstream` template branch status.
- **What's needed:** Add personal experience notes to each section.
- **Related:** `2026-04-19-setting-up-jekyll-blog-github-pages.md`
- **Estimated effort:** 1-2 hours

### 17. `2026-05-01-claude-code-setup-guide.md`

- **Status:** Well-written, complete guide
- **What's needed:** Fix broken front matter. **Fact-check the Amazon Q / Kiro claim** — Amazon Q Developer is still active; Kiro is a separate product, not a replacement.
- **Estimated effort:** 1 hour (mostly fact-checking)

### 18. `2026-05-10-jekyll-internal-formatting-front-matter.md` — 📝 Jekyll Deep Dives

- **Status:** Stub with acronym grep technique and section outlines for front matter, kramdown, Liquid, content formatting.
- **What's needed:** Flesh out all sections.
- **Related:** `2026-04-18-jekyll-markdown-feature-reference.md`
- **Estimated effort:** 2-3 hours

### 19. `2024-11-18-five-stages-cloud-data-science-platform.md` — 🧠 Data Science & AI/ML

- **Status:** Strong opinion piece. Core insight: DS needs production data in dev-like environments. 5-stage promotion model is well-reasoned.
- **What's needed:** Light editing. Could use a real-world example or diagram.
- **Estimated effort:** 1-2 hours

### 19a. ~~`2026-05-10-jekyll-run-vscode-plugin-local-development.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-05-11-jekyll-run-vscode-plugin-local-development.md`
- **Related series (🔌 Jekyll Run Plugin → Run Jekyll):**
  - `_drafts/2026-05-22-jekyll-run-plugin-multiroot-workspace-bug.md` — macOS crash diagnosis, rbenv fix, terminal launch requirement
  - `_drafts/2026-05-25-forking-jekyll-run-to-run-jekyll.md` — CI/CD modernization, fork rename, Marketplace publishing
  - `_drafts/2026-05-28-vscode-marketplace-publisher-account-setup.md` — VS Code Marketplace publisher account setup
  - `_drafts/2026-05-29-run-jekyll-bug-fixes-and-code-review.md` — 3 bugs fixed in v1.7.1 + 15 more from deep code review
  - `_drafts/2026-06-01-run-jekyll-testing-and-test-harness.md` — Test harness setup, unit and integration tests
  - Publish order: published article (done), macOS crash, fork/rename, publisher account, bug fixes, testing

### 19b. ~~`2026-05-10-jekyll-liquid-code-fence-rendering-trap.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-04-30-jekyll-liquid-code-fence-rendering-trap.md`

### 19c. ~~`2026-05-10-jekyll-draft-future-visual-indicators.md`~~ — 📝 Jekyll Deep Dives — PROMOTED

- **Published as:** `2026-05-12-jekyll-draft-future-visual-indicators.md`

### 20. ~~`2026-04-26-ceph-wal-vs-db-performance-test.md`~~ — 🗄️ Ceph Storage — PROMOTED

- **Published as:** `2026-04-18-ceph-wal-vs-db-performance-test.md`
- **Benchmark data:** `assets/data/ceph-wal-db/`

### 21. `2026-01-01-photosynth-update.md`

- **Status:** Expanded into full article covering Georgia Tech PyPhotoSynthExport, Photosynth shutdown, open-source alternatives. Reads as wishful thinking about old tools without a concrete implementation to share.
- **Recommendation:** Split into two articles. Publish this one as a retrospective/eulogy for Photosynth and the export work. Write a **companion article** that actually implements a local photogrammetry pipeline using current open-source alternatives (e.g. OpenMVG, OpenMVS, COLMAP, or Meshroom) — something hands-on with real results rather than just evaluating options.
- **Related:** `2016-04-25-photosync-export-visualizer.md`
- **Estimated effort:** 1 hour for this article as-is; 3-4 hours for the companion implementation article

### 22. `2024-03-11-lag-lacp-nic-bonding.md` — 🌍 SDN & Networking

### 22a. ~~`2026-05-15-caddy-reverse-proxy-proxmox-web-ui.md`~~ — 🔧 Caddy Reverse Proxy — PROMOTED

- **Published as:** `2026-05-16-caddy-reverse-proxy-proxmox-web-ui.md`

### 22b. ~~`2026-05-15-caddy-reverse-proxy-ceph-dashboard.md`~~ — 🔧 Caddy Reverse Proxy — PROMOTED

- **Published as:** `2026-05-19-caddy-reverse-proxy-ceph-dashboard.md`

- **Status:** Nice highway/traffic analogy. Includes critical LACP misconception about single TCP connections. HP ProCurve 2810 link.
- **What's needed:** Add practical section — ProCurve config, Proxmox bond setup, performance results.
- **Estimated effort:** 2 hours

---

## Tier 3: Substantial Content, Needs Significant Work (3+ hours)

### 23. `2024-11-18-research-as-a-model-for-data-science.md` — 🧠 Data Science & AI/ML

- **Status:** Core thesis: DS fails more than it succeeds (1 in 5 vs SD's 4 in 5), academic research is a better model than SDLC.
- **Recommendation:** Merge key insight into #19 (Five Stages), or expand standalone.
- **Estimated effort:** 1 hour to merge; 2 hours standalone

### 24. `2026-02-12-proxmox-homelab-infrastructure-overview.md` — 🏗️ Homelab Infrastructure

### 25. `2026-02-13-pre-kubernetes-homelab-checklist.md` — 🏗️ Homelab Infrastructure

### 26. `2026-02-05-proxmox-cluster-roadmap-vms-project.md` — 🏗️ Homelab Infrastructure

- **Problem:** Massive overlap — all describe the same cluster, hardware, and plans.
- **Recommendation:** Pick ONE. Overview is most self-contained. Checklist is most actionable. VMS roadmap is too long for one post.
- **Related:** `2025-09-12-upcoming-articles-roadmap.md`, `2025-09-21-proxmox-8-lessons-learned.md`

### 27. `2026-04-01-homelab-infrastructure-upgrades.md` — 🏗️ Homelab Infrastructure

- **Status:** Comprehensive upgrade plan covering VPN, switches, boot drives, Caddy proxy
- **Problem:** Overlaps with #24-26. Decide which to publish.
- **Estimated effort:** 2 hours (mostly deduplication)

### 28. ~~`2024-09-23-zfs-boot-mirrors-proxmox8-part-1.md`~~ — 🖥️ ZFS Boot Mirrors — RETIRED

- **Merged into:** `2025-02-25-proxmox-zfs-boot-mirrors-part-1.md` (tanaka session, harlan recovery, zpool detach mistake)
- **Deleted:** 2026-04-16

### 29. ~~`2025-02-26-proxmox-zfs-boot-mirrors-part-2.md`~~ — 🖥️ ZFS Boot Mirrors — PROMOTED (as Part 3)

- **Published as:** `2026-06-03-proxmox-zfs-boot-mirrors-part-3.md`
- **Rewritten:** Abandoned incomplete zfs send/receive approach in favor of fresh install with UEFI upgrade. GRUB/Legacy BIOS is technical debt with PVE 9.x approaching. The fresh install path solves disk sizing, UEFI migration, and clean OS state in one operation.

### 29a. ~~`2026-05-24-proxmox-zfs-boot-mirrors-part-3.md`~~ — 🖥️ ZFS Boot Mirrors — PROMOTED (as Part 2)

- **Published as:** `2026-05-29-proxmox-zfs-boot-mirrors-part-2.md`
- **Renumbered:** Emergency dual-drive failure recovery (Harlan) now Part 2 — it teaches the backup checklist that Part 3 applies.

### 29b. `2026-06-29-ai-coding-agent-context-files-reference.md` — 🤖 AI/Tooling — PROMOTED

- **Published as:** `2026-05-27-ai-coding-agent-context-files-reference.md`
- **Content:** Reference guide for context/rules files across 9 AI coding assistants

### 29c. `2026-06-30-managing-cross-ai-agent-context.md` — 🤖 AI/Tooling — PROMOTED

- **Published as:** `2026-06-01-managing-cross-ai-agent-context.md`
- **Content:** Strategies for managing project context across multiple AI agents

### 30. `2024-01-27-networking-site-2-site-vpn.md` — 🌍 SDN & Networking

- **Status:** GL-iNet Slate AX and Brume 2 hardware, CIDR planning, ISP details, product photos. Stops at "Network Diagrams."
- **Problem:** Superseded by newer infrastructure drafts (#24-27).
- **Recommendation:** Finish as standalone hardware review, or cannibalize into newer drafts (30 min).
- **Estimated effort:** 2-3 hours to finish standalone

### 31. `2024-04-03-pikvm-and-kvm.md`

- **Status:** Detailed parts list ($520 total, $65/machine), AIMOS 8-port KVM integration. Stops before configuration section.
- **What's needed:** Write configuration section with diagram, startup order, cabling. Add photos.
- **Estimated effort:** 2-3 hours

### 32. `2024-06-21-ceph-osd-moving-disks.md` — 🗄️ Ceph Storage

- **Status:** Clear problem (4 OSDs on 3 nodes → 3 OSDs on 4 nodes), screenshots, research links, Ceph flags insight.
- **What's needed:** Add migration results if completed; publish as planning article if not.
- **Related:** `2024-03-04-ceph-rebalance.md`
- **Estimated effort:** 1-2 hours

### 33. `2026-04-01-phonemes-aiml-research.md` — 🧠 Data Science & AI/ML

- **Status:** Research plan/roadmap, reads like a project proposal.
- **Recommendation:** Reframe as "research directions" rather than results.
- **Related:** `2025-05-29-pytorch-asr-example.md`
- **Estimated effort:** 1-2 hours to reframe

### 34. `2025-01-01-tankless-water-heater-flush.md`

- **Status:** Practical guide. Equipment list ($100 first time, $6-7/year after), process overview, lessons learned.
- **What's needed:** Add photos. Flesh out process steps.
- **Estimated effort:** 1 hour with photos

### 35. `2024-08-01-oh-my-zshell-wslv2.md`

- **Status:** Oh My Zsh + T480 dev environment (WSLv2, VSCode, Chocolatey), nvidia MX150 for AI/ML, WSLv2 CUDA symlink issue.
- **What's needed:** Flesh out OMZ installation into proper walkthrough. Add nvidia setup commands.
- **Related:** Pairs with `2024-06-20-chocolatey-packaging-easywsl.md`
- **Estimated effort:** 2 hours

### 36. `2024-06-20-chocolatey-packaging-easywsl.md`

- **Status:** Covers Chocolatey account setup, Quick Start docs, PowerToys dependency patterns, local testing.
- **What's needed:** Add packaging results if completed; otherwise it's a research log.
- **Estimated effort:** 1-2 hours

### 37. `2025-02-02-multi-gpu-multi-node.md` — 🧠 Data Science & AI/ML

- **Status:** Link collection — Ollama multi-instance, LiteLLM, llama.cpp distributed inference, Exo, GPU comparisons.
- **What's needed:** Actual experimentation results. Could publish as "research roundup" with 1 hour editing.
- **Related:** `2025-02-16-power-supplies-for-gpu.md`
- **Estimated effort:** 1 hour (roundup) or 3-4 hours (with experiments)

---

## Tier 4: Too Raw / Redundant — Hold or Archive

### 38. `2025-12-18-jekyll-gdpr-plugin-development.md`

- **Status:** Aspirational plugin development plan — no code shipped.
- **Recommendation:** Complete the plugin, publish as a Ruby gem, and write a companion article following the same pattern as the Pandoc exports plugin (`2026-04-12-jekyll-pandoc-exports-plugin.md`) and gem release automation (`2026-04-11-ruby-gem-release-automation.md`). The GDPR implementation article (`2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md`) is the starting point; this draft is the follow-through.
- **Related:** `2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md`, `2026-04-12-jekyll-pandoc-exports-plugin.md`, `2026-04-11-ruby-gem-release-automation.md`
- **Cross-ref:** See TODO.md → High Impact → "GDPR Cookie Consent Ruby Plugin"

### 39. `2026-01-03-jekyll-resume-post-type-implementation.md`

- **Status:** Technical exploration, no implementation.
- **Recommendation:** Check if Pandoc approach (`2026-04-13-jekyll-pandoc-exports-resume-integration.md`) superseded this. If so, archive.

### 40. `2024-12-31-jekyll-add-header-links.md`

### 41. `2024-12-31-jekyll-code-copy-buttons.md`

- **Status:** Stub research notes with links.
- **Recommendation:** Flesh out or archive.

### 42. `2025-02-20-ceph-reef-to-squid-upgrade.md` — 🗄️ Ceph Storage

- **Status:** 4 lines — just a link to the Proxmox wiki.
- **Recommendation:** Archive or expand when upgrade is performed.

### 43. `2025-02-10-oracle-cloud-infra-learning.md`

- **Status:** Link collection about OCI Always Free Tier. Includes Reddit advice, Terraform modules.
- **Recommendation:** Publish as quick "OCI Free Tier for Homelab" if you tried it. Otherwise archive.

### 44. `2025-01-01-hosting-for-hobbiest.md`

- **Status:** Stub comparing Netlify, Koyeb, Ploomber free tiers.
- **Recommendation:** Goes stale fast. Flesh out with experience or archive.

### 45. `2024-12-01-k8s-on-proxmox-with-tf-ansible.md`

- **Status:** ClusterCreator project evaluation notes.
- **Recommendation:** Likely superseded by k8s-proxmox repo. Archive unless it adds unique value.

### 46. `2025-03-01-thoughts-on-directions-for-aiml.md`

- **Status:** 2 lines total. "I have some opinions on AI/ML... The hype-cycle is at maximum right now."
- **Recommendation:** Archive. Start fresh if writing this.

---

## Tier 5: Superseded — Archive Candidates

### 47. `2024-06-11-promox-sdn-options.md`

- **Status:** Early SDN notes for HA failover with OpenWRT LXC.
- **Superseded by:** #11 (PowerDNS SDN) and #12 (OpenWRT LXC)

### 48. `2024-09-09-proxmox-sdn-openwrt-lxc.md`

- **Status:** Early SDN + OpenWRT exploration. Has markdown formatting tests mixed in.
- **Superseded by:** `2026-02-02-openwrt-lxc-native-implementation-journey.md` (#12)

### 49. `2024-09-13-proxmox-lxc-template-openwrt.md`

- **Status:** Short notes about LXC ostype, `openwrt.common.conf` discovery.
- **Superseded by:** #12 — merge the `openwrt.common.conf` detail if not already there.

---

## Quick Wins — Publish Order

| # | File | Effort | Cluster |
|---|------|--------|---------|
| 1 | `name-service-registrars.md` | 30 min | 🌐 Domain & Email |
| 2 | `email-forwarding-evaluation.md` | 15 min | 🌐 Domain & Email |
| 3 | `google-service-sprawl.md` | 15 min | — |
| ~~5~~ | ~~`proxmox-zfs-boot-mirrors-part-1.md`~~ | PROMOTED | 🖥️ ZFS |
| ~~5~~ | ~~`writing-to-think-two-decades-of-figuring-things-out.md`~~ | PROMOTED | ✍️ Personal |
| ~~6~~ | ~~`caddy-reverse-proxy-proxmox-web-ui.md`~~ | PROMOTED | 🔧 Caddy |
| ~~7~~ | ~~`caddy-reverse-proxy-ceph-dashboard.md`~~ | PROMOTED | 🔧 Caddy |
| ~~—~~ | ~~`proxmox-zfs-boot-mirrors-part-2.md`~~ | PROMOTED (as Part 3) | 🖥️ ZFS |
| ~~—~~ | ~~`proxmox-zfs-boot-mirrors-part-3.md`~~ | PROMOTED (as Part 2) | 🖥️ ZFS |
| ~~—~~ | ~~`ai-coding-agent-context-files-reference.md`~~ | PROMOTED | 🤖 AI |
| ~~—~~ | ~~`managing-cross-ai-agent-context.md`~~ | PROMOTED | 🤖 AI |

**Note:** Posts written directly to `_posts` (not promoted from drafts): `2026-04-02-improving-eeat-jekyll-adsense.md`, `2026-04-06-adsense-verification-gdpr-script-loading-fix.md`, `2026-04-07-jekyll-sitemap-bloat-tags-categories-pagination.md`, `2026-04-08-jekyll-theme-missing-head-body-tags.md`
| 8 | `starvoyager-game.md` | 1 hr | 🎮 Game Dev |
| 9 | `godot-vscode.md` | 1 hr | 🎮 Game Dev |

**Total effort for top 5:** ~2 hours
**Total effort for all 9:** ~5.5 hours

---

## Summary Stats

| Category | Count |
|----------|-------|
| **Total drafts in `_drafts/`** | **38** |
| Ready to publish — Tier 1 | 3 (+ 12 promoted) |
| Near-complete — Tier 2 | 7 (+ 9 promoted) |
| New drafts (untiered) | 3 (Draft Preview Site series) |
| Needs significant work — Tier 3 | 15 |
| Too raw / hold — Tier 4 | 9 |
| Superseded / archive — Tier 5 | 3 |
| **Total tracked** | **38 drafts + 1 DRAFTS.md** |

### Previously Removed

| Category | Count |
|----------|-------|
| Superseded drafts (deleted 2025-07-15) | 3 |
| Promoted to _posts (2026-04-12–13) | 4 |
| Written directly to _posts (2026-04-02–08, AdSense/Jekyll series) | 4 |
| Promoted to _posts (2026-04-16 batch — 10 Jekyll deep dives) | 10 |
| Promoted to _posts (2026-04-16 — Caddy reverse proxy pair) | 2 |
| Promoted to _posts (2026-04-16 — Writing to Think essay) | 1 |
| Promoted to _posts (2026-04-16 — ZFS Boot Mirrors Part 1) | 1 |
| Promoted to _posts (2026-04-17 — ZFS Parts 2 & 3, AI agent pair) | 4 |
| Retired/merged drafts (2026-04-16) | 1 |
| Duplicate deleted (2026-04-12) | 1 |
| Comments draft merged into #6 | 1 |
| Template/test files (consolidated earlier) | 10 |
