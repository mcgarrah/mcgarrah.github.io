# Drafts Review — Publish Readiness Analysis

Reviewed: All 51 drafts in `_drafts/` folder
Cross-referenced against: All published posts in `_posts/` and `_substack/`
Last updated: 2026-04-16

---

## Recently Promoted / Removed

| Draft file | Published as | Date |
|------------|-------------|------|
| ~~`2024-09-01-proxmox-ceph-nearfull.md`~~ | `2025-09-28-proxmox-ceph-nearfull.md` | Deleted 2025-07-15 |
| ~~`2024-09-02-proxmox-ceph-performance.md`~~ | `2025-10-12-proxmox-ceph-performance.md` | Deleted 2025-07-15 |
| ~~`2025-02-16-usb3-drive-smart.md`~~ | `2025-10-26-usb-drive-smart.md` + `2026-02-03-usb-drive-smart-updates.md` | Deleted 2025-07-15 |
| ~~`2025-09-29-ceph-osd-debugging.md`~~ | `2026-04-14-ceph-osd-recovery-power-failure.md` | Promoted 2026-04-12 |
| ~~`2024-08-26-proxmox-misc-scripts.md`~~ | `2024-08-26-proxmox-8-dell-wyse-3040-upgrade.md` | Deleted 2026-04-12 (duplicate) |
| ~~`2026-04-01-jekyll-markdown-feature-reference.md`~~ | `2026-04-18-jekyll-markdown-feature-reference.md` | Promoted 2026-04-13 |
| ~~`2026-04-02-learning-jekyll.md`~~ | `2026-04-19-setting-up-jekyll-blog-github-pages.md` | Promoted 2026-04-13 |
| ~~`2025-10-05-ceph-ssd-wal-db-usb-storage.md`~~ | `2026-04-16-ceph-ssd-wal-db-usb-storage.md` | Promoted 2026-04-13, rescheduled 2026-04-16 |
| ~~`2024-12-31-jekyll-add-comments-section.md`~~ | Merged into `2026-05-10-jekyll-giscus-comments-implementation.md` | Deleted (content merged) |
| ~~`2026-04-25-ssh-key-access-proxmox-cluster.md`~~ | `2026-04-17-ssh-key-access-proxmox-cluster.md` | Promoted 2026-05-18, rescheduled 2026-04-16 |
| ~~`2025-12-16-ruby-gem-release-automation.md`~~ | `2026-04-11-ruby-gem-release-automation.md` | Deleted (superseded, published version has additional content) |
| ~~`2026-04-26-ceph-wal-vs-db-performance-test.md`~~ | `2026-04-18-ceph-wal-vs-db-performance-test.md` | Promoted 2026-05-18, rescheduled 2026-04-16 |

---

## Substack Publication Schedule

| Date | Title | Blog Posts Referenced |
|------|-------|---------------------|
| 2026-04-04 | From Homelabs to Machine Learning | Infrastructure series (Proxmox, Ceph, Dell Wyse, monitoring) |
| 2026-04-20 | From Markdown to Production | Jekyll series (feature reference, setup guide, SEO, GDPR, Pandoc, Mermaid, optimization) |
| TBD | Machine Learning (planned) | AI/ML research, phonemes, cloud DS platforms |

---

## Article Clusters

Drafts that form natural publishing sequences or share a topic. Publish in order within each cluster.

| Cluster | Drafts | Notes |
|---------|--------|-------|
| 🌐 **Domain & Email Migration** | #1, #2 | Publish registrars first, email second |
| 🖥️ **Proxmox ZFS Boot Mirrors** | #5, #18, #19 | #5 is ready; #18 is a merge candidate with #5; #19 depends on completing the migration |
| 🎮 **Game Development** | #9, #10 | StarVoyager and Godot — independent but pair well |
| 🌍 **Proxmox SDN & Networking** | #11, #12, #22 | PowerDNS, OpenWRT LXC, and LAG/LACP |
| 📝 **Jekyll Deep Dives** | #6, #7, #8, #13, #14, #15, #16, #17, #18, #19a, #19b, #19c (Jekyll cluster) | The 2026-05-10 batch — publish in any order |
| 🗄️ **Ceph Storage** | #20, #21, #28 | WAL/DB test, OSD moves, Reef→Squid upgrade |
| 🔑 **SSH & Remote Access** | — | Published; prerequisite for #20 (WAL/DB benchmarks) |
| 🏗️ **Homelab Infrastructure** (overlapping) | #24, #25, #26 | Pick ONE of these three to publish |
| 🧠 **Data Science & AI/ML** | #23, #29 | Five Stages + Research model — merge or publish separately |

---

## Tier 1: Ready to Publish (< 30 min each)

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

### 4. `2026-05-10-jekyll-tag-category-generator-plugin.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft. Covers full plugin code, design decisions, URL structure, sitemap exclusion, noindex, both layouts, real stats (237 tags, 53 categories).
- **Related:** `2026-04-07-jekyll-sitemap-bloat-tags-categories-pagination.md`, `2026-04-19-setting-up-jekyll-blog-github-pages.md`
- **Estimated effort:** 30 minutes

### 5. `2025-02-25-proxmox-zfs-boot-mirrors-part-1.md` — 🖥️ ZFS Boot Mirrors

- **Status:** Complete working example with full console output for Edgar node
- **What's needed:** Add `categories`, `tags`, `excerpt` front matter. Brief conclusion paragraph.
- **Related:** `2026-02-05-proxmox-zfs-boot-mirror-smart-analysis.md`
- **Estimated effort:** 30 minutes

### 6. `2026-05-10-jekyll-giscus-comments-implementation.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft. Covers six alternatives evaluated, why Giscus won, full implementation, legacy dead code, Lambda prototype.
- **What's needed:** Review and add Discussions tab screenshots.
- **Related:** `2026-04-19-setting-up-jekyll-blog-github-pages.md`, `2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md`
- **Estimated effort:** 30 minutes

### 7. `2026-05-10-jekyll-content-plumbing-permalinks-reading-time.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft. Permalinks, reading time, excerpt separator, pagination, jekyll-redirect-from — all with git history.
- **What's needed:** Verify config snippets match current state.
- **Related:** `2026-04-18-jekyll-markdown-feature-reference.md`, `2026-04-07-jekyll-sitemap-bloat-tags-categories-pagination.md`
- **Estimated effort:** 30 minutes

### 8. `2024-08-15-ghp-jekyll-upgrade.md` — 📝 Jekyll Deep Dives

- **Status:** Rewritten into full chronological article covering two years of Jekyll upgrades (webrick, Ubuntu 24.04, Jekyll 4.2→4.4.1, Dart Sass 3.0, Node.js 24 GHA).
- **What's needed:** Review for accuracy. Could use a timeline diagram.
- **Estimated effort:** 30 minutes

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

### 13. `2026-05-10-jekyll-github-actions-cicd-pipeline.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft. All three GHA workflows, Dependabot, Lighthouse CI, Mermaid pipeline diagram, canonical URL grep bug story, cost analysis.
- **What's needed:** Verify workflow YAML snippets match current files. Add recent Dependabot PR examples.
- **Related:** `2026-01-01-jekyll-seo-health-checks.md`, `2025-09-09-github-actions-pip-audit-pr.md`
- **Estimated effort:** 1 hour

### 14. `2026-05-10-jekyll-small-things-polish-features.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft. Six polish features: dark/light theme, print stylesheet, 404/500 haiku, author bio, archive page, favicon.
- **What's needed:** Add screenshots of dark/light mode, 404 page, print output.
- **Related:** `2026-04-02-improving-eeat-jekyll-adsense.md`, `2025-12-14-sass-circular-dependency-nightmare.md`
- **Estimated effort:** 1 hour

### 15. `2026-05-10-jekyll-content-distribution-pipeline.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft. Six distribution channels: RSS, sitemap, GSC, Substack, social sharing, internal cross-references. Mermaid pipeline diagram.
- **What's needed:** Add GSC screenshots, verify Substack link counts, add social sharing examples.
- **Related:** `2025-12-31-jekyll-seo-sitemap-canonical-url-fixes.md`, `2026-04-07-jekyll-sitemap-bloat-tags-categories-pagination.md`
- **Estimated effort:** 1 hour

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

### 19a. `2026-05-10-jekyll-run-vscode-plugin-local-development.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft. Jekyll Run VS Code extension config, settings precedence, `_config.yml` future flag trap, draft visibility gotcha, bash fallback script.
- **What's needed:** Verify settings paths match current VS Code version.
- **Related:** `2026-05-10-jekyll-draft-future-visual-indicators.md` (follow-up)
- **Estimated effort:** 30 minutes

### 19b. `2026-05-10-jekyll-liquid-code-fence-rendering-trap.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft. Documents the raw/endraw Liquid escaping issue in code fences.
- **What's needed:** Review for accuracy.
- **Related:** `2026-04-20-jekyll-markdown-feature-reference.md`
- **Estimated effort:** 15 minutes

### 19c. `2026-05-10-jekyll-draft-future-visual-indicators.md` — 📝 Jekyll Deep Dives

- **Status:** Complete first draft with screenshots. Font Awesome pencil/robot icons and italic styling for draft and future posts in archive and home page listings.
- **What's needed:** Review screenshots. Verify production safety claims.
- **Related:** `2026-05-10-jekyll-run-vscode-plugin-local-development.md` (predecessor)
- **Estimated effort:** 15 minutes

### 20. ~~`2026-04-26-ceph-wal-vs-db-performance-test.md`~~ — 🗄️ Ceph Storage — PROMOTED

- **Published as:** `2026-04-18-ceph-wal-vs-db-performance-test.md`
- **Benchmark data:** `assets/data/ceph-wal-db/`

### 21. `2026-01-01-photosynth-update.md`

- **Status:** Expanded into full article covering Georgia Tech PyPhotoSynthExport, Photosynth shutdown, open-source alternatives.
- **Related:** `2016-04-25-photosync-export-visualizer.md`
- **Estimated effort:** 1 hour

### 22. `2024-03-11-lag-lacp-nic-bonding.md` — 🌍 SDN & Networking

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

### 28. `2024-09-23-zfs-boot-mirrors-proxmox8-part-1.md` — 🖥️ ZFS Boot Mirrors

- **Status:** MASSIVE article — complete console sessions for Tanaka and Harlan nodes, plus a documented `zpool detach` vs `zpool replace` mistake and recovery.
- **Problem:** Near-duplicate of #5 (2025-02-25 version covers Edgar). Identical intro text.
- **Recommendation:** MERGE best parts of both into one definitive multi-scenario guide.
- **Related:** `2026-02-05-proxmox-zfs-boot-mirror-smart-analysis.md`
- **Estimated effort:** 3-4 hours to merge

### 29. `2025-02-26-proxmox-zfs-boot-mirrors-part-2.md` — 🖥️ ZFS Boot Mirrors

- **Status:** "Shrink ZFS mirror to smaller SSDs" — has problem statement, `parted` session, proxmox-boot-tool setup. Stops before actual ZFS data copy.
- **What's needed:** Complete the ZFS send/receive or pool migration step.
- **Estimated effort:** 3-4 hours

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
- **Recommendation:** Hold until plugin is actually started.
- **Related:** `2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md`

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
| 4 | `jekyll-tag-category-generator-plugin.md` | 30 min | 📝 Jekyll |
| 5 | `proxmox-zfs-boot-mirrors-part-1.md` | 30 min | 🖥️ ZFS |
| 6 | `jekyll-giscus-comments-implementation.md` | 30 min | 📝 Jekyll |
| 7 | `jekyll-content-plumbing-permalinks-reading-time.md` | 30 min | 📝 Jekyll |
| 8 | `ghp-jekyll-upgrade.md` | 30 min | 📝 Jekyll |
| 9 | `jekyll-run-vscode-plugin-local-development.md` | 30 min | 📝 Jekyll |
| 10 | `jekyll-liquid-code-fence-rendering-trap.md` | 15 min | 📝 Jekyll |
| 11 | `jekyll-draft-future-visual-indicators.md` | 15 min | 📝 Jekyll |
| 12 | `starvoyager-game.md` | 1 hr | 🎮 Game Dev |
| 13 | `godot-vscode.md` | 1 hr | 🎮 Game Dev |

**Total effort for top 8:** ~3 hours
**Total effort for all 13:** ~6 hours

---

## Summary Stats

| Category | Count |
|----------|-------|
| **Total drafts in `_drafts/`** | **51** |
| Ready to publish — Tier 1 | 11 |
| Near-complete — Tier 2 | 13 |
| Needs significant work — Tier 3 | 15 |
| Too raw / hold — Tier 4 | 9 |
| Superseded / archive — Tier 5 | 3 |
| **Total** | **52 (includes 1 DRAFTS.md)** |

### Previously Removed

| Category | Count |
|----------|-------|
| Superseded drafts (deleted 2025-07-15) | 3 |
| Promoted to _posts (2026-04-12–13) | 4 |
| Duplicate deleted (2026-04-12) | 1 |
| Comments draft merged into #6 | 1 |
| Template/test files (consolidated earlier) | 10 |
