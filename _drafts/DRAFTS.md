# Drafts Review — Publish Readiness Analysis

Reviewed: All 44 drafts in `_drafts/` folder
Cross-referenced against: All 139 published posts in `_posts/` and `_substack/`
Last updated: 2026-05-10

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
| ~~`2025-10-05-ceph-ssd-wal-db-usb-storage.md`~~ | `2026-04-22-ceph-ssd-wal-db-usb-storage.md` | Promoted 2026-04-13 |

---

## Substack Publication Schedule

| Date | Title | Blog Posts Referenced |
|------|-------|---------------------|
| 2026-04-04 | From Homelabs to Machine Learning | Infrastructure series (Proxmox, Ceph, Dell Wyse, monitoring) |
| 2026-04-20 | From Markdown to Production | Jekyll series (feature reference, setup guide, SEO, GDPR, Pandoc, Mermaid, optimization) |
| TBD | Machine Learning (planned) | AI/ML research, phonemes, cloud DS platforms |

**Note:** The Apr 20 Substack references the following blog posts that should be live before publication:

- `2026-04-14-ceph-osd-recovery-power-failure.md` ✅
- `2026-04-15-zfs-ceph-overlapping-failures.md` ✅
- `2026-04-18-jekyll-markdown-feature-reference.md` ✅
- `2026-04-19-setting-up-jekyll-blog-github-pages.md` ✅

---

## Tier 1: Ready to Publish (Minor Polish Needed)

### 1. `2026-02-06-name-service-registrars.md` — ⭐ SHIP IT

- **Status:** Extremely detailed, well-structured, 56% migration complete with real data
- **Content quality:** Excellent — domain inventory tables, pricing, DNS backup scripts, migration checklists, deprecated records appendix
- **What's needed:** Update the progress section if more domains have migrated since writing. Fix the date (2026-02-06 is future-dated). Add proper `categories` and `tags` front matter.
- **Related published post:** None directly — this would be a new topic for the blog
- **Estimated effort:** 30 minutes

### 2. `2026-02-07-email-forwarding-evaluation.md` — ⭐ SHIP IT

- **Status:** Complete evaluation with cost comparison tables, migration strategy, and decision matrix
- **Content quality:** Thorough — compares 7 options with pricing, features, and clear winner
- **What's needed:** References the registrar post above (should publish that first). Minor date fix.
- **Related published post:** None — pairs naturally with the registrar migration post
- **Estimated effort:** 15 minutes (after registrar post is published)

### 3. `2025-02-25-proxmox-zfs-boot-mirrors-part-1.md` — ⭐ SHIP IT

- **Status:** Complete working example with full console output showing a successful ZFS boot mirror replacement on Edgar
- **Content quality:** Excellent hands-on walkthrough — exactly the kind of "I did this, here's how" content the blog excels at
- **What's needed:** Add proper `categories`, `tags`, and `excerpt` front matter. The intro text is solid. Needs a brief conclusion paragraph.
- **Related published post:** `2026-02-05-proxmox-zfs-boot-mirror-smart-analysis.md` exists in `_posts/` — this would be a natural companion/sequel
- **Estimated effort:** 30 minutes

### 4. `2026-03-15-google-service-sprawl.md` — ⭐ SHIP IT

- **Status:** Complete, opinionated, relatable blog post
- **Content quality:** Good personal voice, covers a real frustration. Shorter than most posts but that's fine — it's an opinion piece
- **What's needed:** Minimal — maybe add a few more specific examples or link to GDPR/AdSense posts. Date fix.
- **Related published post:** `2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md` and `2026-04-06-adsense-verification-gdpr-script-loading-fix.md` — reference these
- **Estimated effort:** 15 minutes

---

## Tier 2: Near-Complete (Need Some Work)

### 7. `2026-02-15-starvoyager-game.md`

- **Status:** Well-written overview of the StarVoyager modernization project
- **What's needed:** Verify the GitHub repo links work, confirm the stats (87 files, 261 tests) are current. Could use screenshots.
- **Related published post:** None — new topic area (game dev)
- **Estimated effort:** 1 hour

### 8. `2026-03-01-godot-vscode.md`

- **Status:** Solid overview of the tower defense game project with good personal backstory
- **What's needed:** The title says "Godot VSCode" but the content is broader. Retitle. Verify repo link. Could trim some of the roadmap sections.
- **Related published post:** None — pairs with StarVoyager post above
- **Estimated effort:** 1 hour

### 9. `2026-02-01-powerdns-lxc-proxmox-sdn-integration.md`

- **Status:** Marked "DRAFT ahead of submitting Pull Request" — comprehensive technical guide
- **What's needed:** Confirm the PR status. If the PR has been submitted/merged, update the text. The mermaid diagram and code examples are solid.
- **Related published post:** `2025-02-01-google-wifi-with-openwrt.md` (tangentially related networking)
- **Estimated effort:** 1 hour

### 10. `2026-02-02-openwrt-lxc-native-implementation-journey.md`

- **Status:** Also marked "DRAFT ahead of submitting Pull Request" — excellent technical narrative of 4 approaches tested
- **What's needed:** Same as PowerDNS — confirm PR status. The "four approaches tested" narrative structure is compelling.
- **Related published post:** `2025-02-01-google-wifi-with-openwrt.md` — directly related
- **Estimated effort:** 1 hour

### 11. `2026-05-01-claude-code-setup-guide.md`

- **Status:** Well-written, complete guide
- **What's needed:** Fix the front matter (add opening `---`, `title`, `layout`, `categories`, `tags` — currently broken/truncated). **Fact-check the claim about "Amazon Q being deprecated in favor of Kiro"** — Amazon Q Developer is still active; Kiro is a separate product, not a direct replacement. This factual issue needs correction before publishing.
- **Related published post:** None
- **Estimated effort:** 1 hour (mostly fact-checking the Amazon Q/Kiro relationship)

### 12. `2024-11-18-five-stages-cloud-data-science-platform.md` — STRONG OPINION PIECE

- **Status:** Well-articulated argument about why SDLC environments don't map to Data Science. The core insight — DS needs production data in development-like environments — is clearly explained.
- **Content quality:** Strong professional voice. The 5-stage promotion model (Infra Dev → Infra Pre-Prod → Prod Discovery → Prod Integration → Production) is well-reasoned. The "conflict" framing is effective.
- **What's needed:** Light editing. Could use a real-world example or diagram. The 3-environment variants at the end are a nice touch.
- **Related published post:** None — unique topic, shows cloud architecture expertise
- **Estimated effort:** 1-2 hours

### ~~13. `2026-04-01-jekyll-markdown-feature-reference.md`~~ — PROMOTED

- **Published as:** `2026-04-18-jekyll-markdown-feature-reference.md` — "How the Sausage Is Made: Every Feature Powering This Jekyll Blog"
- **Added:** Pandoc exports section, stack summary table, "What's Next" section, 10 related post cross-references, full SEO front matter
- **Referenced in:** Apr 20 Substack article

### ~~14. `2026-04-02-learning-jekyll.md`~~ — PROMOTED

- **Published as:** `2026-04-19-setting-up-jekyll-blog-github-pages.md` — "Building This Blog: Jekyll on GitHub Pages from Zero to 130+ Posts"
- **Added:** Why Jekyll section, SEO setup, Giscus comments, GDPR compliance, Pandoc/resume integration, "What I'd Do Differently" retrospective, 10 related post cross-references, full SEO front matter
- **Referenced in:** Apr 20 Substack article

---

## Tier 3: Substantial Content But Needs Significant Work

### ~~15. `2025-10-05-ceph-ssd-wal-db-usb-storage.md`~~ — PROMOTED

- **Published as:** `2026-04-22-ceph-ssd-wal-db-usb-storage.md` — "Hybrid Ceph Storage: SSD WAL/DB Acceleration with USB Drive Data"
- **Rewritten:** Updated from 9 OSDs/41 TiB to 15 OSDs/69 TiB, filled all stub sections, added single SSD risk analysis, three OSD creation methods, WAL vs DB performance gap analysis, cost analysis, and cross-references to Apr 14/15 Ceph incident posts
- **Related doc:** [CEPH-OSD-SSD-ACCELERATION.md](https://github.com/mcgarrah/k8s-proxmox/blob/main/docs/CEPH-OSD-SSD-ACCELERATION.md) in k8s-proxmox repo
- **Spawned draft:** `2026-04-26-ceph-wal-vs-db-performance-test.md` — formal A/B benchmark plan with ready-to-run scripts

### 16. `2026-04-01-phonemes-aiml-research.md`

- **Status:** Research plan/roadmap rather than a results article. Well-structured but reads more like a project proposal.
- **Related published post:** `2025-05-29-pytorch-asr-example.md` — directly referenced as prior work
- **Estimated effort:** Could publish as-is if framed as "research directions" rather than results. 1-2 hours to reframe.

### 17. `2026-04-01-homelab-infrastructure-upgrades.md`

- **Status:** Comprehensive upgrade plan covering VPN, switches, boot drives, Caddy proxy
- **What's needed:** Lots of overlap with the pre-K8s checklist and infrastructure overview drafts. Decide which one to publish — this one or those.
- **Related published post:** Many Proxmox posts — this is a meta-overview
- **Estimated effort:** 2 hours (mostly deduplication decisions)

### 18. `2024-09-23-zfs-boot-mirrors-proxmox8-part-1.md` — NEAR-DUPLICATE of `2025-02-25`

- **Status:** MASSIVE article — contains complete working console sessions for ZFS boot mirror replacement on both Tanaka and Harlan nodes, plus a documented mistake (`zpool detach` vs `zpool replace`) and recovery
- **Content quality:** Excellent real-world content with multiple scenarios, screenshots, and the "oh crap" moment of accidentally breaking a mirror on a primary Ceph node
- **Problem:** This is an earlier, longer version of `2025-02-25-proxmox-zfs-boot-mirrors-part-1.md` which covers the Edgar node. They share identical intro text.
- **Recommendation:** MERGE the best parts of both into one definitive article. The Tanaka session, the Harlan "oh crap" recovery, and the Edgar session from the 2025 version would make an outstanding multi-scenario guide.
- **Related published post:** `2026-02-05-proxmox-zfs-boot-mirror-smart-analysis.md`
- **Estimated effort:** 3-4 hours to merge and edit into one cohesive article

### 19. `2025-02-26-proxmox-zfs-boot-mirrors-part-2.md` — IN PROGRESS

- **Status:** The "shrink ZFS mirror to smaller SSDs" article. Has the problem statement, partition creation with `parted` on the Timetec 128GB SSD, and proxmox-boot-tool setup. Stops before the actual ZFS data copy.
- **Content quality:** The `parted` session showing manual partition creation (matching BIOS boot, EFI, and ZFS partitions on a smaller drive) is valuable and hard to find elsewhere.
- **What's needed:** Complete the ZFS send/receive or pool migration step. The references section has good links to solutions.
- **Related published post:** Companion to Part 1 above
- **Estimated effort:** 3-4 hours to complete the migration and document it

### 20. `2024-01-27-networking-site-2-site-vpn.md` — GOOD FOUNDATION

- **Status:** Substantial content — covers GL-iNet Slate AX and Brume 2 hardware, network requirements, CIDR planning, ISP details. Has product photos. Stops at "Network Diagrams — more tbd here..."
- **Problem:** Superseded by newer drafts (`homelab-infrastructure-upgrades.md`, `pre-kubernetes-homelab-checklist.md`) that cover the same Brume 2 deployment in more detail.
- **Recommendation:** Either finish this as a standalone "GL-iNet Brume 2 for site-to-site VPN" hardware review, or cannibalize the hardware details into the newer infrastructure posts.
- **Related published post:** None
- **Estimated effort:** 2-3 hours to finish, or 30 min to merge into newer drafts

### 21. `2024-04-03-pikvm-and-kvm.md` — GOOD FOUNDATION

- **Status:** Detailed parts list with pricing ($520 total, $65/machine), hardware choices explained, AIMOS 8-port KVM integration. Has excerpt. Stops before the configuration section.
- **Content quality:** The parts tables with prices and Amazon links are valuable. The 15-month journey narrative is relatable.
- **What's needed:** Write the Configuration section with the diagram, startup order, and cabling details. Add photos if available.
- **Related published post:** None — unique topic for the blog
- **Estimated effort:** 2-3 hours to complete

### 22. `2024-06-21-ceph-osd-moving-disks.md` — GOOD FOUNDATION

- **Status:** Clear problem statement (4 OSDs on 3 nodes → 3 OSDs on 4 nodes), screenshots, research links, and the key insight about disabling Ceph flags during migration.
- **What's needed:** Did you actually complete this migration? If so, add the results. If not, this could still publish as a "planning" article.
- **Related published post:** `2024-03-04-ceph-rebalance.md` — directly referenced
- **Estimated effort:** 1-2 hours if migration was completed; publish as-is with conclusion if not

### 23. `2024-03-11-lag-lacp-nic-bonding.md` — GOOD EXPLAINER

- **Status:** Nice highway/traffic analogy for explaining LAG vs LACP. Includes the critical misconception about LACP not splitting single TCP connections across interfaces. HP ProCurve 2810 setup link included.
- **What's needed:** Needs a practical section — your actual ProCurve switch configuration, Proxmox bond setup, and performance results.
- **Related published post:** None — would pair well with the infrastructure upgrade drafts
- **Estimated effort:** 2 hours to add practical examples

---

## Tier 4: Too Raw or Redundant

### 24. `2026-02-12-proxmox-homelab-infrastructure-overview.md` & `2026-02-13-pre-kubernetes-homelab-checklist.md` & `2026-02-05-proxmox-cluster-roadmap-vms-project.md`

- **Problem:** These three drafts have massive overlap — all describe the same cluster, same hardware, same plans. The VMS roadmap is the most detailed but also the longest.
- **Recommendation:** Pick ONE to publish. The infrastructure overview is the most self-contained. The checklist is the most actionable. The VMS roadmap is too long for a single post.
- **Related published post:** `2025-09-12-upcoming-articles-roadmap.md`, `2025-09-21-proxmox-8-lessons-learned.md`

### 25. `2025-12-18-jekyll-gdpr-plugin-development.md`

- **Status:** Ambitious plugin development plan but entirely aspirational — no actual code shipped
- **Related published post:** `2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md` — the custom implementation this would build on
- **Recommendation:** Hold until the plugin is actually started.

### 26. `2026-01-03-jekyll-resume-post-type-implementation.md`

- **Status:** Technical exploration of approaches but no implementation
- **Related published post:** `2026-04-13-jekyll-pandoc-exports-resume-integration.md` — may have already solved this differently
- **Recommendation:** Check if the Pandoc approach superseded this. If so, archive.

### 27. ~~`2024-12-31-jekyll-add-comments-section.md`~~, `2024-12-31-jekyll-add-header-links.md`, `2024-12-31-jekyll-code-copy-buttons.md`

- **Status:** Comments draft deleted — content merged into `2026-05-10-jekyll-giscus-comments-implementation.md` (#48). Remaining two are stub notes with links.
- **Recommendation:** Header links and code copy buttons drafts are still research notes. Either flesh them out or archive.

### 28. `2025-02-20-ceph-reef-to-squid-upgrade.md`

- **Status:** 4 lines total — just a link to the Proxmox wiki
- **Recommendation:** Archive or expand when the upgrade is actually performed

### 29. `2026-01-01-photosynth-update.md`

- **Status:** Expanded from old link dump into full article covering the Georgia Tech PyPhotoSynthExport project, Photosynth's shutdown, and open-source photogrammetry alternatives.
- **Recommendation:** Review for completeness. References the published 2016 blog post `2016-04-25-photosync-export-visualizer.md`.
- **Estimated effort:** 1 hour to finalize

### 30. `2024-11-18-research-as-a-model-for-data-science.md` — STUB WITH GOOD IDEA

- **Status:** Core thesis: DS fails more than it succeeds (1 in 5 vs SD's 4 in 5), and academic research is a better model than SDLC for DS work. Has notes for 4 related articles.
- **Recommendation:** Merge the key insight into the "Five Stages" article (#12 above), or expand into its own short opinion piece.
- **Estimated effort:** 1 hour to merge; 2 hours to expand standalone

### 31. `2024-12-01-k8s-on-proxmox-with-tf-ansible.md` — RESEARCH NOTES

- **Status:** Documents ClusterCreator project evaluation. Has Terraform provider details, Ansible configuration, and notes about adapting for Ceph storage.
- **Recommendation:** Superseded by the k8s-proxmox repository and newer K8s drafts. Decide if this adds value beyond those.
- **Estimated effort:** 2 hours to turn into article; may be better to archive

### 32. `2025-01-01-tankless-water-heater-flush.md` — FUN PERSONAL POST

- **Status:** Practical guide to flushing tankless water heaters. Equipment list ($100 first time, $6-7/year after), process overview, and lessons learned.
- **What's needed:** Add photos of your setup. Flesh out the process steps. Short and sweet is fine for this topic.
- **Related published post:** None — personal/home content, different from usual technical posts
- **Estimated effort:** 1 hour with photos

### 33. `2024-06-20-chocolatey-packaging-easywsl.md` — NICHE BUT COMPLETE-ISH

- **Status:** Covers setting up a Chocolatey account, reading Quick Start docs, finding dependency patterns from PowerToys package, and local testing needs.
- **What's needed:** Did you actually package easyWSL? If so, add the result. If not, this is a research log.
- **Related published post:** None
- **Estimated effort:** 1-2 hours if packaging was completed

### 34. `2025-02-02-multi-gpu-multi-node.md` — RESEARCH NOTES

- **Status:** Collection of links and ideas about distributing ML workloads across multiple GPUs/nodes. Covers Ollama multi-instance, LiteLLM, llama.cpp distributed inference, Exo, and GPU comparison links.
- **What's needed:** Needs actual experimentation results. Currently just links and ideas.
- **Related published post:** `2025-02-16-power-supplies-for-gpu.md` — tangentially related
- **Estimated effort:** 3-4 hours to add experiments; or publish as a "research roundup" with 1 hour of editing

### 35. `2025-02-10-oracle-cloud-infra-learning.md` — RESEARCH DUMP

- **Status:** Collection of links about OCI Always Free Tier (4-core Ampere, 24GB RAM, 200GB storage). Includes Reddit advice, Terraform modules for free K8s.
- **Recommendation:** Could become a quick "OCI Free Tier for Homelab" post if you actually tried it. Otherwise archive.
- **Estimated effort:** 2-3 hours if you have OCI experience to add; archive if not

### 36. `2025-01-01-hosting-for-hobbiest.md` — STUB

- **Status:** Comparison of Netlify, Koyeb, and Ploomber free tiers with bullet-point feature lists.
- **Recommendation:** Could be a quick "Free Hosting Options for Side Projects" post. Goes stale fast though.
- **Estimated effort:** 1-2 hours to flesh out with actual experience

### 43. `2026-04-26-ceph-wal-vs-db-performance-test.md` — NEW DRAFT

- **Status:** Complete test plan with ready-to-run benchmark scripts. Spawned from the WAL vs DB analysis in the Apr 22 post.
- **Content:** Four-phase test plan (baseline, matched OSD rebuild, targeted benchmarks, conversion decision), three shell scripts (latency comparison, scrub timing, peering time), built-in Ceph bench commands (`ceph tell osd.X bench`, `rados bench`, `perf dump`).
- **Prerequisite:** Maintenance window, cluster at HEALTH_OK, PBS backup
- **Related published post:** `2026-04-22-ceph-ssd-wal-db-usb-storage.md` — the article that promises this follow-up
- **Estimated effort:** 2-4 hours for test execution, 1-2 hours to write up results

### 44. `2026-05-10-jekyll-internal-formatting-front-matter.md` — NEW DRAFT

- **Status:** Stub with preserved acronym grep technique and section outlines for front matter, kramdown, Liquid, and content formatting conventions.
- **Content:** Migrated from JMM-TODO.md — the grep command for extracting abbreviation definitions across posts, plus planned sections on parsing engine behavior and front matter evolution.
- **Related published post:** `2026-04-18-jekyll-markdown-feature-reference.md` — complementary deep dive
- **Estimated effort:** 2-3 hours to flesh out all sections

### 45. `2026-05-10-jekyll-enhancements-without-plugins.md` — NEW DRAFT

- **Status:** Comprehensive reference of jekyllcodex.org without-plugin implementations, evaluated against what this blog uses. Also documents the `clean`/`upstream` template branch status.
- **Content:** Migrated from JMM-TODO.md — all jekyllcodex.org links with adoption status, Jekyll plugin development references, and template branch notes.
- **Related published post:** `2026-04-19-setting-up-jekyll-blog-github-pages.md` — covers the blog setup journey
- **Estimated effort:** 1-2 hours to add personal experience notes to each section

### 46. `2026-05-10-jekyll-tag-category-generator-plugin.md` — NEW DRAFT

- **Status:** Complete first draft. Covers the full plugin code, design decisions (URL structure, sitemap exclusion, noindex for thin content), both layouts, index pages, GitHub Actions requirement, and lessons learned from tag proliferation.
- **Content:** The `tag_category_generator.rb` plugin is mentioned in passing in two published posts but never got its own dedicated article. This fills that gap with real stats (237 tags, 53 categories across 139 posts).
- **Related published post:** `2026-04-07-jekyll-sitemap-bloat-tags-categories-pagination.md` — covers the sitemap problem this plugin caused; `2026-04-19-setting-up-jekyll-blog-github-pages.md` — mentions plugin in passing
- **Estimated effort:** 30 minutes — mostly review and polish

### 47. `2026-05-10-jekyll-github-actions-cicd-pipeline.md` — NEW DRAFT

- **Status:** Complete first draft covering all three GitHub Actions workflows (build/deploy, CodeQL, SEO health check), Dependabot configuration, Lighthouse CI setup, and how the pieces interact. Includes Mermaid pipeline diagram, git history evolution, the canonical URL grep bug story, and cost analysis.
- **Content:** No existing post covers the full CI/CD picture. The SEO health check has its own article, the build gets a brief mention in the setup guide, and CodeQL has zero coverage. This ties them all together.
- **Related published post:** `2026-01-01-jekyll-seo-health-checks.md` — deep dive on one workflow; `2026-04-19-setting-up-jekyll-blog-github-pages.md` — brief CI/CD section; `2025-09-09-github-actions-pip-audit-pr.md` — similar pattern for Python
- **Estimated effort:** 1 hour — verify workflow YAML snippets match current files, add any recent Dependabot PR examples

### 48. `2026-05-10-jekyll-giscus-comments-implementation.md` — NEW DRAFT

- **Status:** Complete first draft. Covers the stateless site problem, evaluation of six alternatives (Disqus, Isso, GitHub Issues API with Lambda, Utterances, Staticman, GDPR approaches), why Giscus won, full implementation walkthrough, config explanation, legacy dead code in the theme, and the GitHub ecosystem advantage.
- **Content:** No existing post covers the comment system decision in depth. The setup guide has ~15 lines, the feature reference has ~5 lines. The old `2024-12-31-jekyll-add-comments-section.md` draft has been merged into this article and deleted. Full Lambda prototype code, ChatGPT conversion link, and all research notes preserved here.
- **Related published post:** `2026-04-19-setting-up-jekyll-blog-github-pages.md` — brief Giscus section; `2025-05-31-website-feature-enhancements.md` — announcement; `2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md` — GDPR context
- **Estimated effort:** 30 minutes — review and add any screenshots of the Discussions tab

### 49. `2026-05-10-jekyll-content-plumbing-permalinks-reading-time.md` — NEW DRAFT

- **Status:** Complete first draft. Covers permalink structure (`/:title/` with comparison table of alternatives), reading time indicator (Liquid implementation, 200 WPM rationale, build-time vs client-side), custom excerpt separator (migration from default, the accidental revert), pagination (4 per page, sitemap interaction), and jekyll-redirect-from (SDD→SSD typo fix origin story). Includes git history for each feature.
- **Content:** These features are mentioned in passing across several posts but never explained together. The permalink setting came from the original Contrast theme (Jan 2019). Reading time was added May 2025 via Google Jules. Excerpt separator was customized June 2024 with a mass migration across all posts. Redirects added April 2026. The article shows how they interact as a system.
- **Related published post:** `2026-04-18-jekyll-markdown-feature-reference.md` — mentions excerpts and redirects; `2025-05-31-website-feature-enhancements.md` — brief reading time announcement; `2026-04-07-jekyll-sitemap-bloat-tags-categories-pagination.md` — pagination sitemap problem
- **Estimated effort:** 30 minutes — review and verify config snippets match current state

### 50. `2026-05-10-jekyll-small-things-polish-features.md` — NEW DRAFT

- **Status:** Complete first draft. Covers six small polish features: dark/light theme (CSS `prefers-color-scheme` + Mermaid dark mode fix), print stylesheet (134 lines, triggered the SASS circular dependency), custom 404/500 error pages with haiku and RFC links, author bio with E-E-A-T signals and `rel="me"` links, archive page (history back to Jan 2020), and favicon. Includes git history for each feature.
- **Content:** These items were individually too thin for standalone articles but together tell the story of polishing a Jekyll blog beyond the defaults. Each took less than a day; together they're about a week of work across two years.
- **Related published post:** `2026-04-02-improving-eeat-jekyll-adsense.md` — author bio origin; `2025-12-14-sass-circular-dependency-nightmare.md` — print stylesheet trigger; `2025-11-09-jekyll-website-optimization-part-1.md` — theme improvements
- **Estimated effort:** 1 hour — add screenshots of dark/light mode, 404 page, and print output

### 51. `2026-05-10-jekyll-content-distribution-pipeline.md` — NEW DRAFT

- **Status:** Complete first draft. Covers six distribution channels: RSS feed (jekyll-feed, zero effort), sitemap + sitemap index (multi-site solution), Google Search Console (indexing journey, canonical fixes), Substack newsletter (cross-posting workflow, 47 inbound links, publication scheduling), social sharing (Open Graph, permalink contract), and internal cross-references (16/139 posts). Includes Mermaid pipeline diagram and the flywheel effect.
- **Content:** No existing post covers how content reaches readers after publishing. Individual channels are documented (SEO posts, sitemap posts) but the end-to-end pipeline and how channels reinforce each other is new. The Substack workflow with `_substack/` archival is undocumented elsewhere.
- **Related published post:** `2025-12-31-jekyll-seo-sitemap-canonical-url-fixes.md` — GSC indexing; `2026-04-07-jekyll-sitemap-bloat-tags-categories-pagination.md` — sitemap cleanup; `2026-04-09-managing-multiple-jekyll-sites-sitemap-challenges.md` — multi-site sitemaps
- **Estimated effort:** 1 hour — add actual GSC screenshots, verify Substack link counts, add social sharing examples

---

## Tier 5: Too Thin to Publish — Archive Candidates

### 37. `2024-08-15-ghp-jekyll-upgrade.md` — REWRITTEN

- **Status:** Complete first draft. Rewritten from a bare outline into a full chronological article covering two years of Jekyll upgrades: webrick addition (Mar 2024), Ubuntu 24.04 local dev (Jun 2024), Jekyll 4.2→4.3.3 with SASS breakage (Aug 2024), Dart Sass 3.0 module system migration (May 2025), Google Jules SASS dialect issues (May 2025), Jekyll 4.3.3→4.4.1 + circular dependency (Sep 2025), and Node.js 24 GitHub Actions forced update (Apr 2026). All from git history.
- **What's needed:** Review for accuracy, add any missing upgrade pain points. Could use a timeline diagram.
- **Estimated effort:** 30 minutes — review and polish

### 38. `2024-08-01-oh-my-zshell-wslv2.md` — EXPANDED

- **Status:** Now covers Oh My Zsh setup with plugin list (git, tmux, vscode), plus T480 "Thomas" development environment setup (WSLv2 + VSCode + Chocolatey), nvidia MX150 for AI/ML with Automatic1111 and ComfyUI, WSLv2 CUDA symlink known issue, and TheTinkerDad LXC/LXD permissions video references.
- **What's needed:** Flesh out the OMZ installation steps into a proper walkthrough. Add the actual nvidia MX150 setup commands. Consolidate the TheTinkerDad LXC permissions content into a concise cheatsheet section.
- **Related published post:** None — could pair with the Chocolatey draft (`2024-06-20`)
- **Estimated effort:** 2 hours

### 39. `2025-03-01-thoughts-on-directions-for-aiml.md` — 2 LINES

- **Status:** "I have some opinions on AI/ML... The hype-cycle is at maximum right now." That's it.
- **Recommendation:** Archive. If you want to write this, start fresh.

### 40. `2024-06-11-promox-sdn-options.md` — SUPERSEDED

- **Status:** Early notes about SDN for HA failover with OpenWRT LXC.
- **Recommendation:** Archive — superseded by PowerDNS SDN and OpenWRT LXC drafts (#9, #10).

### 41. `2024-09-09-proxmox-sdn-openwrt-lxc.md` — SUPERSEDED

- **Status:** Early exploration of SDN + OpenWRT on Proxmox. Has some markdown formatting tests mixed in.
- **Recommendation:** Archive — superseded by `2026-02-02-openwrt-lxc-native-implementation-journey.md`.

### 42. `2024-09-13-proxmox-lxc-template-openwrt.md` — SUPERSEDED

- **Status:** Short notes about LXC ostype for OpenWRT, discovery of the hidden `openwrt.common.conf` in Proxmox.
- **Recommendation:** Archive — the `openwrt.common.conf` discovery is covered in the newer OpenWRT LXC draft. Merge that detail if not already there.

---

## Top 10 Quick Wins — Publish Order

| Priority | File | Effort | Topic |
|----------|------|--------|-------|
| 1 | `name-service-registrars.md` | 30 min | Domain migration from SquareSpace to Porkbun |
| 2 | `email-forwarding-evaluation.md` | 15 min | Email forwarding comparison (companion to #1) |
| 3 | `google-service-sprawl.md` | 15 min | Google services frustration (opinion piece) |
| 4 | `proxmox-zfs-boot-mirrors-part-1.md` | 30 min | ZFS boot mirror replacement walkthrough |
| 5 | `five-stages-cloud-data-science-platform.md` | 1-2 hrs | Cloud DS platform environments (opinion piece) |
| 6 | `ceph-wal-vs-db-performance-test.md` | 2-4 hrs | WAL vs DB benchmark (requires maintenance window) |
| 7 | `starvoyager-game.md` | 1 hr | StarVoyager game modernization project |
| 8 | `powerdns-lxc-proxmox-sdn-integration.md` | 1 hr | PowerDNS + Proxmox SDN guide |
| 9 | `openwrt-lxc-native-implementation-journey.md` | 1 hr | OpenWRT LXC implementation (4 approaches) |

**Total estimated effort for top 4:** ~1-2 hours
**Total estimated effort for all 8:** ~7-9 hours

---

## Summary Stats

| Category | Count |
|----------|-------|
| **Total drafts in `_drafts/`** | **49** |
| Ready to publish (Tier 1) | 4 |
| Near-complete (Tier 2) | 6 |
| Needs significant work (Tier 3) | 8 |
| Too raw or redundant (Tier 4) | 16 |
| Archive candidates (Tier 5) | 5 |
| New drafts (spawned/migrated) | 9 |
| **Tier totals** | **49 ✓** |

*Tier 2 reduced from 8 to 6 (items #13, #14 promoted). Tier 3 reduced from 9 to 8 (item #15 promoted). New draft #43 added.*
*Tier 4 has 12 entries but #24 groups 3 files and #27 groups 2 files (16 files total). Comments draft from #27 merged into #48 and deleted.*
*Drafts #44 and #45 added 2026-05-10 — migrated from JMM-TODO.md cleanup.*
*Draft #46 added 2026-05-10 — dedicated article for tag_category_generator.rb plugin.*
*Draft #47 added 2026-05-10 — comprehensive CI/CD pipeline article covering all three workflows, Dependabot, and Lighthouse.*
*Draft #48 added 2026-05-10 — Giscus comment system decision and implementation article.*
*Draft #49 added 2026-05-10 — Jekyll content plumbing: permalinks, reading time, excerpts, pagination, and redirects.*
*Drafts #50 and #51 added 2026-05-10 — Polish features (dark mode, print, 404 haiku, author bio, archive, favicon) and content distribution pipeline (RSS, sitemap, GSC, Substack, social).*
*Also updated: PiKVM draft (#21) with config notes, VPN draft (#20) with Tailscale/WireGuard/CARP content, OMZ draft (#38) with T480/LXC notes.*

### Previously Removed

| Category | Count |
|----------|-------|
| Superseded drafts (deleted 2025-07-15) | 3 |
| Promoted to _posts (2026-04-12–13) | 4 |
| Duplicate deleted (2026-04-12) | 1 |
| Template/test files (consolidated earlier) | 10 |
