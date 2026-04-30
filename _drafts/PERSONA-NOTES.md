---
layout: none
date: 1999-12-31
sitemap: false
---

# Persona Promotion Notes — Draft Readiness Assessment

Assessment of drafts against the `PERSONA.md` voice guide. Evaluates which drafts are ready to promote with persona alignment, what specific fixes each needs, and a recommended promotion order.

Created: 2026-07-30
Reference: `_drafts/PERSONA.md` (Persona Voice Guide — Applying the Senior Director Lens)

---

## Tier A: Ready to Promote with Persona Polish (< 1 hour each)

### 1. `2026-07-08-git-history-bloat-drafts-repo-cleanup.md` ⭐ Best candidate

- **Persona alignment:** Already strong. The opening ("something is not broken enough to page you, but it is inefficient enough to keep stealing attention") is exactly the right voice — deliberate investigation, not accidental discovery.
- **Trade-off analysis:** Present and well-structured (three options evaluated with clear rejection criteria).
- **Enterprise connection:** The "Why This Was Worth Solving" section nails the pattern — "annoyance is often just early signal."
- **Closing:** Has a solid "Final Takeaway" paragraph.
- **Persona fixes needed:** Almost none. One minor tweak — the phrase "that kind of annoyance is often where the useful maintenance work starts" could be strengthened to connect to infrastructure hygiene at scale. Otherwise this reads like it was written *after* the persona guide.
- **Effort:** 15 minutes
- **Verdict:** Promote as-is or with minimal polish.

### 2. `2026-07-09-git-repo-audit-methodology-findings.md` ⭐

- **Persona alignment:** Strong. Opens with "I am not treating this as a blanket campaign" — deliberate, scoped, systematic. This is the architect voice.
- **Trade-off analysis:** The decision matrix is excellent — exactly the kind of artifact a senior engineer produces.
- **Enterprise connection:** Implicit throughout (the methodology *is* the enterprise pattern).
- **Closing:** Good — "validate the cleanup once, then decide" is the right framing.
- **Persona fixes needed:** The opening could add one sentence connecting this to infrastructure audit discipline more broadly. The "Command Compatibility" section is useful but reads slightly tutorial-ish — consider a brief framing sentence like "Portability matters because this audit runs on both my macOS workstation and WSL2 environments."
- **Effort:** 20 minutes
- **Verdict:** Promote with light polish.

### 3. `2026-02-07-email-forwarding-evaluation.md`

- **Persona alignment:** Weak opening — "After migrating 16 domains... I need to decide on an email forwarding strategy." This is the "what I did" pattern from PERSONA.md Pattern #1.
- **Trade-off analysis:** Excellent — the cost comparison table and decision matrix are thorough.
- **Enterprise connection:** Missing. Managing 16 domains with email forwarding is a vendor dependency and operational surface area decision. One sentence connecting this to "reducing authentication boundaries and vendor relationships" would transform the framing.
- **Closing:** Functional but reads like a product review conclusion, not an architecture decision.
- **Persona fixes needed:**
  - Rewrite opening: Frame as "When your registrar migration changes your email infrastructure, you're making a vendor dependency decision that affects 16 domains simultaneously."
  - Add one enterprise connection sentence in the evaluation section.
  - Strengthen closing with an "implications" paragraph — what this enables (API-driven DNS automation, cert-manager integration, etc.).
  - Missing front matter fields: `description`, `last_modified_at`, `seo` block.
- **Effort:** 45 minutes
- **Verdict:** Promote with persona + front matter work.

### 4. `2026-04-01-macos-dock-jumping-between-monitors.md`

- **Persona alignment:** Per PERSONA.md, this is a "quick tactical reference" — leave alone. The voice is clean, direct, and practical.
- **Persona fixes needed:** None. This is the "Leave alone" category from the guide.
- **Missing:** Screenshots (TODO comments in the article). Complete without them but would benefit.
- **Effort:** 0 minutes (persona), 30 minutes (screenshots if desired)
- **Verdict:** Promote as-is. Light post, no persona treatment needed.

---

## Tier B: Near-Promotion but Need Persona Work (1–2 hours each)

### 5. `2026-01-01-photosynth-update.md`

- **Persona alignment:** Moderate. The opening establishes Georgia Tech context and technical depth but reads slightly retrospective/nostalgic rather than strategic.
- **Trade-off analysis:** Present in the "Open Source Alternatives" section — good comparison of tools.
- **Enterprise connection:** The "Practical Applications" section lists use cases but doesn't connect to the author's professional experience. One sentence like "Having built coordinate tracking systems for ergonomics research and worked with real-time rendering pipelines, the SfM pipeline maps directly to problems I've solved in production" would anchor it.
- **Closing:** The "lesson from Photosynth's shutdown" paragraph is strong — vendor dependency risk is exactly the right enterprise framing.
- **Persona fixes needed:**
  - Reframe opening: Lead with the vendor dependency lesson, not the nostalgia. "When Microsoft shut down Photosynth, years of user-created 3D reconstructions vanished overnight. This is the same vendor lock-in risk that applies to any cloud service..."
  - Add one sentence connecting the "Where My Project Fits" section to current professional relevance.
  - Front matter needs: `date`, `last_modified_at`, `seo` block.
- **Effort:** 1 hour
- **Verdict:** Strong candidate with moderate persona + front matter work.

### 6. `2026-05-01-claude-code-setup-guide.md`

- **Persona alignment:** Per PERSONA.md, this should be framed as "evaluating AI coding tools for engineering team adoption." The current opening ("I've been using Amazon Q Developer...") is personal setup narrative.
- **Trade-off analysis:** The IDE vs CLI comparison table is good but could be framed as an evaluation framework rather than personal preference.
- **Enterprise connection:** Missing. This is a tool evaluation — frame it as "what I'd recommend if equipping a team" rather than "what I set up for myself."
- **Persona fixes needed:**
  - Rewrite opening: "When evaluating AI coding assistants for a development workflow, the choice between IDE-integrated and CLI-first tools is an architectural decision about developer experience."
  - **BLOCKER:** The "Amazon Q being deprecated in favor of Kiro" claim needs fact-checking — Amazon Q Developer is not deprecated; Kiro is a separate product. Must fix before promotion.
  - Add one paragraph on team adoption considerations (cost at scale, security implications of API keys, context window management).
- **Effort:** 1 hour (persona work + fact-checking)
- **Verdict:** Good candidate but the Kiro claim is a blocker that must be resolved.

### 7. `2024-11-18-five-stages-cloud-data-science-platform.md`

- **Persona alignment:** The *content* is exactly the Senior Director / IT Architect voice — an opinion piece about platform architecture for data science. But the *writing* is rough draft quality. Incomplete sentences, informal tone ("But why!?!"), and no front matter beyond title/layout.
- **Trade-off analysis:** The core insight (DS needs production data in dev-like environments) is strong and well-argued.
- **Enterprise connection:** This *is* the enterprise connection — drawn directly from professional experience.
- **Persona fixes needed:**
  - Complete front matter (categories, tags, excerpt, description, seo block, dates).
  - Polish the prose — tighten sentences, remove informal exclamations, add section headers.
  - Add a concrete example from professional experience (anonymized) to ground the abstract framework.
  - The closing trails off ("This one likely has lots of new tooling...") — needs a proper conclusion.
- **Effort:** 1.5–2 hours
- **Verdict:** High-value article for the persona but needs significant prose polish.

---

## Tier C: Content Complete but Persona Misaligned (2+ hours)

### 8. `2026-07-01-starvoyager-game.md`

- **Persona alignment:** This is the article PERSONA.md specifically calls out. The opening ("Before working on my Godot tower defense game... I've been tackling a much larger challenge") reads as hobby narrative.
- The content is strong — security hardening, systematic refactoring, test coverage, upstream collaboration. These are all enterprise engineering patterns.
- **Persona fixes needed (significant):**
  - Rewrite opening: Lead with *why* a senior technologist modernizes legacy codebases — security posture assessment, CI/CD pipeline patterns, cross-platform build systems. Not "I've been tackling a challenge."
  - Frame the security section as "dependency evaluation before adoption" — assessing technical debt in a codebase before investing further.
  - The "Eight-Batch Approach" is excellent systematic engineering — frame it as "the same incremental migration strategy you'd use for any legacy system."
  - The conclusion is too enthusiastic/promotional ("Key Achievements" bullet list). Replace with implications — what this teaches about legacy modernization at scale.
  - Cut or significantly trim the "Future Roadmap" section — reads as aspirational rather than authoritative.
- **Effort:** 2 hours
- **Verdict:** Content is there but the voice needs a full pass.

### 9. `2026-07-03-godot-vscode.md`

- **Persona alignment:** Also called out in PERSONA.md. The opening ("After years of focusing on infrastructure and cloud technologies, I've decided to return to an old passion") is the hobbyist voice the guide warns against.
- The personal history section (NC State physics, VRA, coordinate motion capture) is actually strong professional context — it just needs reframing from "here's my backstory" to "here's why my professional background in real-time systems, computer vision, and coordinate tracking directly applies."
- **Persona fixes needed:**
  - Retitle — the content is broader than "Godot VSCode."
  - Rewrite opening: Frame as returning to real-time systems engineering after decades of enterprise infrastructure work, applying the same architectural patterns (component-based design, state machines, CI/CD) to a different domain.
  - The "Research-Driven Design" section is good — frame it as the same evaluation methodology used for any technology adoption.
  - Cut or compress the massive roadmap sections (Phases 1–4, "Future Ambitions") — speculative content undermines the "I build things" credibility.
  - The conclusion ("While this represents a significant departure from my usual infrastructure and cloud work") is the wrong framing — should be "the same systematic thinking transfers directly."
- **Effort:** 2 hours
- **Verdict:** Needs retitling, opening rewrite, and significant trimming.

---

## Tier D: Not Ready for Persona Work

### 10. AASR Series Overview + Part 1

- `2026-07-01-aasr-project-series-overview.md` — Well-structured, voice is already strong (infrastructure engineering + data science framing).
- `2026-07-01-aasr-proxmox-overview.md` — Earlier draft superseded by the overview's more detailed outline.
- The overview could promote, but it's a series index — needs at least Part 1 finalized first.
- **Verdict:** Hold until Part 1 is written to match the overview's quality.

---

## Recommended Promotion Order

Based on persona readiness and the MWF publication cadence:

| Priority | Article | Persona Work | Schedule Slot |
|----------|---------|-------------|---------------|
| 1 | Git History Bloat (Part 1) | 15 min | Next Mon |
| 2 | Git Repo Audit (Part 2) | 20 min | Next Wed |
| 3 | macOS Dock Jumping | None (leave alone) | Next Fri |
| 4 | Email Forwarding Evaluation | 45 min (+ front matter) | Following Mon |
| 5 | Photosynth Update | 1 hr (+ front matter) | Following Wed |
| 6 | Claude Code Setup | 1 hr (+ fact-check blocker) | Following Fri |
| 7 | StarVoyager | 2 hr (full voice pass) | After Claude Code |
| 8 | Godot Tower Defense | 2 hr (retitle + voice pass) | After StarVoyager |

### Rationale

- The git series (Parts 1 and 2) are the strongest candidates — they already read like the persona guide was followed.
- The macOS Dock article is a clean tactical post that the guide explicitly says to leave alone.
- Email forwarding needs front matter and a reframed opening but the analysis is solid.
- Photosynth has the right closing (vendor dependency risk) but needs the opening reframed to lead with that insight.
- Claude Code has a factual blocker (the Amazon Q / Kiro deprecation claim) that must be resolved before promotion.
- The game dev articles (StarVoyager, Godot) have the most content but need the most persona work. They are the ones DRAFTS.md specifically flagged, and the assessment holds — the content is strong but the voice needs a full pass.

---

## PERSONA.md Patterns Most Commonly Needed

Across all drafts reviewed, the four patterns from `PERSONA.md` appeared with this frequency:

| Pattern | Occurrences | Worst Offenders |
|---------|-------------|-----------------|
| **#1 Opening — Lead with Why** | 6 of 10 | Email forwarding, StarVoyager, Godot, Claude Code |
| **#2 Trade-off Analysis** | 2 of 10 | Photosynth (partial), Five Stages (missing) |
| **#3 Enterprise Connection** | 5 of 10 | Email forwarding, Claude Code, Photosynth, StarVoyager, Godot |
| **#4 Closing — What This Enables** | 4 of 10 | Email forwarding, Five Stages, StarVoyager, Godot |

The opening rewrite is the single highest-leverage fix across the draft portfolio.

---

## Reference

- **Persona voice guide:** `_drafts/PERSONA.md`
- **Authorial voice rules:** `.amazonq/rules/authorial-voice.md`
- **Draft tracker:** `_drafts/DRAFTS.md`
- **Product context:** `.amazonq/rules/memory-bank/product.md`
