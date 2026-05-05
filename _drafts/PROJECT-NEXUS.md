---
layout: none
date: 1999-12-31
sitemap: false
---

# Project Nexus: Strategic Fit Engine

This document captures the architectural planning for **Project Nexus**, a hybrid-cloud intelligence gateway designed to transform a professional resume and technical blog into a strategic decision-support platform for executive leadership.

## 1. Project Vision & Executive Branding

* **Name:** Project Nexus: Federated Career Intelligence & Strategic Fit Engine
* **Target Audience:** Senior Vice Presidents (SVPs) and Senior Directors
* **Core Value Proposition:** Solving "Information Density" in executive hiring by providing a fast-path to candidate data, semantic fit analysis, and consultative onboarding strategies

## 2. Technical Evolution & Library Selection

The project transitioned from a simple client-side search to a multi-layered hybrid system.

### Initial Search Options Evaluated

| Library | Size | Strengths | Weaknesses |
|---------|------|-----------|------------|
| Simple Filter/Highlight | ~0KB | Lightweight DOM filtering | No fuzzy matching, no ranking |
| MiniSearch | ~6KB | Fast, custom tokenization, fuzzy matching | No DOM awareness |
| Mark.js | ~8KB | DOM-aware highlighting, expands hidden content | Not a search engine |
| Fuse.js | ~25KB | Popular, fuzzy matching, handles typos | Heavier, no custom tokenization |

### Selection Verdict

* **MiniSearch** — Primary "search-as-you-type" engine. Selected for speed and custom tokenization via `processTerm` (critical for technical terms like "K8s" vs. "Kubernetes").
* **Mark.js** — Companion library for DOM-aware highlighting and expanding content hidden in collapsed `<details>` sections.

## 3. Hybrid Architecture

The architecture demonstrates "Executive Engineering" traits: Security, Cost Governance, and Resilience.

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  mcgarrah.org (GitHub Pages)                                    │
│  ┌──────────────┐  ┌──────────────────┐                        │
│  │  Blog (/)    │  │  Resume (/resume) │                        │
│  │  nexus-blog- │  │  nexus-resume-   │                        │
│  │  index.json  │  │  index.json      │                        │
│  └──────┬───────┘  └────────┬─────────┘                        │
│         └────────┬───────────┘                                  │
│                  ▼                                               │
│  ┌──────────────────────────────┐                               │
│  │  Nexus TypeScript            │                               │
│  │  Orchestrator (Browser)      │◄─── Phase 1: Local Fallback   │
│  └──────────────┬───────────────┘                               │
└─────────────────┼───────────────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        ▼                   ▼
┌───────────────┐   ┌───────────────────┐
│  DigitalOcean │   │  Proxmox Cluster  │
│  LiteLLM      │   │  (Tailscale       │
│  Proxy        │   │   Funnel)         │
│               │   │                   │
│  • Budget     │   │  • P620 GPU       │
│    governance │   │  • Embeddings     │
│  • Model      │   │  • ChromaDB       │
│    routing    │   │  • /status API    │
│  • API key    │   │  • /search-blog   │
│    protection │   │                   │
└───────┬───────┘   └───────────────────┘
        │                Phase 3: Edge
        ▼
┌───────────────────┐
│  Cloud LLMs       │
│  • AWS Bedrock    │
│    (Claude 3.5)   │
│  • Google Gemini  │
│    (Flash/Pro)    │
└───────────────────┘
     Phase 4: AI
```

### Components

* **Frontend:** Jekyll-based static sites (Resume & Blog) on GitHub Pages under a single domain (`mcgarrah.org`).
* **Edge Layer (Private Cloud):** A Proxmox 8.4 cluster using NVIDIA P620 GPUs (2GB VRAM) for local embedding generation and semantic cross-linking via Tailscale Funnel.
* **Intelligence Layer (Public Cloud):** Multi-cloud LLM orchestration using AWS Bedrock (Claude 3.5 Sonnet) for strategic reasoning and Google Gemini 1.5 Pro/Flash for deep-context data analysis.
* **Governance Proxy:** LiteLLM on DigitalOcean — protects API keys, enforces budget caps, routes models by query tier.

## 4. Implementation Roadmap (Phased Rollout)

### Phase 1: The Resilient Foundation (Jekyll & TypeScript)

* **Goal:** Build a zero-cost, local-first search that bridges blog and resume.
* **Actions:**
  * Jekyll generates `nexus-index.json` manifests for both sites at build time
  * TypeScript orchestrator fetches and merges both indexes in-browser
  * MiniSearch provides fuzzy, tokenization-aware search
  * Mark.js expands collapsed `<details>` sections when matches are found
* **Resilience:** Implements a "Circuit Breaker" pattern — if cloud/edge services fail, the system degrades gracefully to local keyword search.
* **Prerequisite:** Resume site refactor (Phases 1–4 in `REFACTOR.md`) must be complete — semantic HTML, `<details>`/`<summary>` structure, and machine-readable JSON-LD view.

### Phase 2: Secure Orchestration (The LiteLLM Gateway)

* **Goal:** Protect financials and API keys.
* **Actions:**
  * Deploy LiteLLM container on DigitalOcean
  * Configure as single OpenAI-compatible gateway for all providers
  * Implement $20–$50/month budget hard cap with real-time enforcement
  * Tiered model routing: Flash for discovery queries, Sonnet for strategic analysis
* **Governance:** Proxy checks monthly spend before forwarding any LLM call. Budget exceeded → returns "governance" signal → frontend falls back to local search.

### Phase 3: The Private Edge (Proxmox & Tailscale)

* **Goal:** Showcase infrastructure expertise with local semantic search.
* **Actions:**
  * Configure Tailscale Funnel on Proxmox LXC container
  * Deploy embedding model (`all-MiniLM-L6-v2` or `BGE-Small`) on P620 GPU
  * Set up ChromaDB/Faiss vector store for blog post embeddings
  * Expose `/status` and `/search-blog` APIs
  * Nightly cron job re-indexes new blog posts
* **Status Beacon:** Turns Green when edge node is reachable from the public site.

### Phase 4: The Executive Value Layer (AI Insights)

* **Goal:** Deliver strategic decision support for executive audiences.
* **Actions:**
  * **T-Shirt Sizing:** Translate technical confidence into XL/L/M fit categories
  * **5 Strategic Pillars:** Evaluate fit across Technical Vision, Operational Excellence, Organizational Leadership, Strategic Execution, and Business Alignment
  * **90-Day Plan:** Generate a consultative onboarding strategy and Gap Analysis based on a provided Job Description
* **Model routing:** Strategy requests burst to Claude 3.5 Sonnet via LiteLLM for highest-quality executive tone.

## 5. Key Executive Narratives

These are the "interview-ready" framings for each architectural decision:

* **Operational Risk Mitigation:** "The local fallback ensures 100% availability regardless of cloud status."
* **Fiscal Discipline:** "Hard budget caps and tiered reasoning (Flash vs. Sonnet) optimize cost-per-value."
* **Hybrid Vision:** "Innovation at the private edge combined with public cloud scale for complex reasoning."
* **Micro-Frontend Architecture:** "I decoupled the Resume Service from the Knowledge Base (Blog) for independent deployment while maintaining a unified Global Search at the root domain."
* **Multi-Layer Defense:** "I implemented a three-tier circuit breaker: LiteLLM at the proxy level for real-time budget enforcement, provider-level limits in the Anthropic dashboard, and CloudWatch Billing Alarms for my AWS Bedrock footprint."
* **Governed AI Environment:** "I architected Project Nexus with a 'Resilient-First' mindset. The first layer is a high-performance local engine ensuring that regardless of network latency or cloud costs, the user has instant search."

## 6. LiteLLM Proxy — AI Gateway Strategy

LiteLLM Proxy provides the technical implementation for the "Governance Proxy" and "Circuit Breaker" logic, solving multi-cloud API key management and operational budgets.

### Why LiteLLM

* **Unified Ingress:** Single OpenAI-compatible gateway for Bedrock, Gemini, Anthropic — no custom proxy logic per provider.
* **Real-Time Guardrails:** Solves the "lag" in native cloud billing dashboards. Critical for the budget Kill Switch.
* **Model Fallbacks:** Automatically switches providers or regions if the primary model hits a budget or technical limit.

### Smart Budget Routing

| Level | Query Type | Model | Rationale |
|-------|-----------|-------|-----------|
| 1 (Cheap) | "What are Michael's skills?" | `gpt-4o-mini` or `gemini-1.5-flash` | Simple retrieval, minimal cost |
| 2 (Strategic) | "Is Michael a fit for this SVP role?" | `claude-3-5-sonnet` | Complex reasoning, executive tone |

### Edge Integration

* Register Proxmox P620 (via Tailscale Funnel) as "Primary" provider for embeddings in LiteLLM `config.yaml`
* LiteLLM routes embedding requests to local edge node first, falling back to cloud providers if unavailable
* Completes the hybrid-cloud loop: local GPU for embeddings, cloud LLMs for reasoning, LiteLLM as unified orchestration

## 7. UI Components & Interaction Design

### Search Bar & Status Beacon

| Color | State | Meaning |
|-------|-------|---------|
| Green ⚡ | Edge Active | Proxmox P620 connected via Tailscale Funnel |
| Blue ☁️ | Cloud Bursting | Bedrock/Gemini ready for strategic analysis |
| Amber 🟡 | Local Only | JavaScript fallback — local search active |
| Red/Dim | Budget Reached | Governance limit hit — local search only |

### Executive UI Components

| Component | UI Treatment | Business Logic |
|-----------|-------------|----------------|
| Status Beacon | Small dot in the search bar | Demonstrates transparency and system observability |
| Competency Graph | Dynamic "Node" visualization of skills | Replaces static skill lists with interactive expertise map |
| Fit Scoreboard | T-shirt sizes (XL, L, M) for 5 Strategic Pillars | Provides "Bottom Line Up Front" (BLUF) for the executive |
| Strategy Output | "Generate 90-Day Plan" button | Moves from "Candidate Search" to "Consultative Partnership" |

### Governance Messaging

When the fallback triggers, display it as a governance feature, not an error:

> "Strategic Fit Analysis is currently paused for fiscal governance (budget limit reached). Local semantic search remains fully active."

## 8. Search Priority Hierarchy (Resilient Orchestrator)

The search follows a prioritized hierarchy ensuring the user always gets an answer:

| Priority | Layer | Source | Value | Timeout |
|----------|-------|--------|-------|---------|
| 1 | Primary | Nexus Edge (Proxmox via Tailscale) | Semantic blog links + local embeddings | 3s |
| 2 | Burst | Cloud Intelligence (Bedrock / Gemini) | Executive Fit Analysis + 90-Day Plan | 3s |
| 3 | Fallback | Local Engine (Browser TypeScript) | Fast keyword filtering of resume content | Instant |

### Circuit Breaker Implementation

```typescript
async function executeNexusSearch(query: string) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 3000);

  try {
    const results = await fetchNexusIntelligence(query, controller.signal);
    clearTimeout(timeoutId);
    renderAdvancedUI(results);
    updateStatus('EDGE');
  } catch (err) {
    console.warn("Nexus Intelligence unavailable. Falling back to Local Engine.");
    const localMatches = performLocalJSFiltering(query);
    renderSimpleUI(localMatches);
    updateStatus('LOCAL');
  }
}
```

## 9. Jekyll Integration & Search Manifests

### Same-Origin Architecture

Both sites share `mcgarrah.org` — no CORS issues. The resume repo is the "Primary Orchestrator" and the blog repo is a "Data Provider."

* **Blog Index:** `/assets/nexus-blog-index.json` (generated by blog repo at build time)
* **Resume Index:** `/resume/assets/nexus-resume-index.json` (generated by resume repo at build time)

### TypeScript Orchestrator

```typescript
async function fetchNexusData() {
  const [resumeData, blogData] = await Promise.all([
    fetch('/resume/assets/nexus-resume-index.json').then(r => r.json()),
    fetch('/assets/nexus-blog-index.json').then(r => r.json())
  ]);
  return [...resumeData, ...blogData];
}
```

### Resume Manifest Template (Liquid)

```liquid
---
layout: null
---
[
  {% for exp in site.data.data.experiences.info %}
  {
    "id": "{{ exp.company | slugify }}",
    "type": "experience",
    "source": "resume",
    "role": "{{ exp.role | escape }}",
    "company": "{{ exp.company | escape }}",
    "time": "{{ exp.time }}",
    "summary": {{ exp.summary | strip_html | strip_newlines | jsonify }},
    "details": {{ exp.details | strip_html | strip_newlines | jsonify | default: "null" }}
  }{% unless forloop.last %},{% endunless %}
  {% endfor %}
]
```

### Blog Manifest Template (Liquid)

```liquid
---
layout: null
---
[
  {% for post in site.posts %}
  {
    "id": "{{ post.url | slugify }}",
    "type": "blog",
    "source": "blog",
    "title": {{ post.title | jsonify }},
    "url": "{{ post.url }}",
    "date": "{{ post.date | date: '%Y-%m-%d' }}",
    "tags": {{ post.tags | jsonify }},
    "categories": {{ post.categories | jsonify }},
    "content": {{ post.content | strip_html | truncatewords: 100 | strip_newlines | jsonify }}
  }{% unless forloop.last %},{% endunless %}
  {% endfor %}
]
```

### Cross-Site "Evidence Loop"

When a recruiter searches for a skill (e.g., "Kubernetes"), the system returns:
1. The relevant job entries from the resume (the "What")
2. Links to specific blog posts about that topic (the "How" / "Proof of Work")

**Taxonomy alignment:** Skills in `data.yml` should share keywords with blog post tags/categories. Consider a shared naming convention or a `_data/tags.yml` reference file to prevent semantic drift (e.g., "k8s" vs "Kubernetes").

### Global Nexus — Search on Both Sites

The search bar will eventually appear on both the blog and resume:

* **On the Resume:** Defaults to "Executive Fit Analysis" mode
* **On the Blog:** Defaults to "Related Technical Deep Dives" with a subtle CTA: "Looking for leadership? Run a Strategic Fit Analysis."
* **Shared assets:** A single `nexus-search.js` and `nexus-search.css` hosted in the blog repo's `/assets/` folder, referenced by both sites
* **Context-aware:** Script detects its location and adjusts default behavior accordingly

## 10. P620 GPU — Semantic Search Architecture

The NVIDIA P620 (2GB VRAM) is well-suited for vector embeddings rather than text generation:

### Embedding Pipeline

| Step | Action | Location |
|------|--------|----------|
| 1. Pre-computation | Blog posts run through embedding model | Proxmox LXC (nightly cron) |
| 2. Storage | Vectors stored in lightweight database | ChromaDB/Faiss on Proxmox |
| 3. Query | User search converted to vector, nearest-neighbor lookup | P620 GPU (real-time) |

### Technical Specifications

* **Model:** `all-MiniLM-L6-v2` or `BGE-Small` (~100MB, fits easily in 2GB VRAM)
* **Runtime:** Ollama or Python/Flask wrapper around Sentence-Transformers
* **Vector Store:** ChromaDB or Faiss in LXC container
* **VRAM Management:** Embedding model stays "warm" — minimal power, millisecond response
* **Tailscale Integration:** Public site sends search request through Tailscale Funnel to local P620 node
* **Scalability:** A few hundred blog posts = nearly instantaneous vector lookups

## 11. Observability & Telemetry

* **Analytics layer:** Track search queries via lightweight custom events (Google Analytics or Proxmox node logging)
* **Data-driven insight:** Query pattern analysis reveals what recruiters are searching for — informs resume content strategy
* **Privacy guardrail:** No PII logging. Anonymous query patterns only. GDPR/CCPA compliant.
* **Kill Switch as telemetry:** Circuit breaker trips are logged events. Budget exhaustion rate = demand signal.

### Predictive Throttling

| Strategy | Implementation | Executive Rationale |
|----------|---------------|---------------------|
| Tiered Reasoning | Gemini Flash for first 500 queries; Claude 3.5 only for explicit "Plan of Action" requests | Cost optimization: cheapest tool that gets the job done |
| IP-Based Leaky Bucket | Limit single user to 5 "Strategic" queries per 24 hours via cookie or IP hash | Fair usage: prevents bots from draining budget |
| Budget Remaining Light | Small progress bar near status beacon | Transparency: sets expectations before user clicks "Analyze" |

**Decision:** Keep the system open initially. Let the Kill Switch be the data-gathering exercise. If it never trips, no access control needed. If it trips constantly, that's a great problem to solve.

## 12. Performance & Caching

* **Pre-fetching:** Eager-load JSON manifests from blog and resume on page load (don't wait for user to type)
* **Optimistic UI:** Show local results instantly; let "Blog Deep Dives" or "AI Analysis" pop in as they arrive
* **Cache strategy:** Use `localStorage` to cache the blog index — second visit is instantaneous
* **3-second rule:** If the "Smart" layers take longer than 3 seconds, the UI flips to local search immediately
* **Deployment independence:** Update a blog post without re-triggering a resume build. Adding a third site = one more URL in `Promise.all()`

## 13. Security Model

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| API Keys | Stored in LiteLLM proxy on DigitalOcean — never in frontend code | Prevents key exposure in page source |
| Tailscale ACLs | Most restrictive possible on Proxmox node | Limits who can reach the edge APIs |
| Budget enforcement | LiteLLM real-time spend tracking + hard cap | Prevents runaway costs |
| Rate limiting | IP-based leaky bucket at proxy layer | Prevents single user/bot from draining budget |
| Provider limits | Anthropic dashboard spend limits, AWS Bedrock quotas | Defense-in-depth: multiple budget gates |
| CloudWatch Alarms | AWS Billing Alarms on Bedrock spend | Final safety net for cloud costs |
| No PII logging | Anonymous query patterns only | GDPR/CCPA compliance |

## 14. Infrastructure Requirements

### Hardware (Existing)

| Resource | Specification | Role |
|----------|--------------|------|
| Proxmox Cluster | Proxmox 8.4, NVIDIA P620 GPUs (2GB VRAM) | Edge embedding generation, vector search |
| Tailscale Mesh | Already configured across home lab | Secure tunnel from public web to Proxmox |

### Cloud Services (New)

| Service | Provider | Estimated Cost | Role |
|---------|----------|---------------|------|
| LiteLLM Container | DigitalOcean App Platform | ~$5–12/month | API gateway, budget enforcement |
| Claude 3.5 Sonnet | AWS Bedrock | Pay-per-token (capped at $20–50/month) | Strategic reasoning, 90-Day Plans |
| Gemini 1.5 Flash | Google AI | Pay-per-token (included in cap) | Discovery queries, initial fit scoring |
| GitHub Pages | GitHub | Free | Static site hosting |

### Estimated Monthly Budget

| Tier | Scenario | Cost |
|------|----------|------|
| Minimum | Local search only (Phase 1) | $0 |
| Normal | DigitalOcean proxy + moderate LLM usage | $15–25/month |
| Maximum | Hard cap enforced | $50/month absolute ceiling |

## 15. Related Repositories & URLs

| Repository | URL | Role in Nexus |
|------------|-----|---------------|
| `mcgarrah.github.io` | Blog at `mcgarrah.org` | Data Provider — generates `nexus-blog-index.json` |
| `resume` | Resume at `mcgarrah.org/resume` | Primary Orchestrator — hosts search UI, TypeScript engine |
| `k8s-proxmox` | Proxmox K8s cluster configs | Infrastructure reference for edge layer |

### Live URLs (Post-Implementation)

| URL | Purpose |
|-----|---------|
| `mcgarrah.org/resume/` | Brief resume with Nexus search bar |
| `mcgarrah.org/resume/machine/` | JSON-LD structured data (feeds Nexus manifest) |
| `mcgarrah.org/resume/assets/nexus-resume-index.json` | Resume search manifest |
| `mcgarrah.org/assets/nexus-blog-index.json` | Blog search manifest |

## 16. Relationship to Resume Refactor

The resume site refactor (`REFACTOR.md` on the `refactor` branch) is a **prerequisite** for Project Nexus. The refactor builds the foundation:

| Refactor Output | Nexus Dependency |
|---|---|
| `/resume/machine/` JSON-LD | Becomes part of the `nexus-resume-index.json` manifest |
| Single-column semantic HTML | Clean DOM for Mark.js highlighting and section expansion |
| `<details>`/`<summary>` structure | MiniSearch + Mark.js can expand collapsed sections on match |
| `_data/data.yml` as single source | Jekyll generates both human views and machine manifests from same data |
| `assets/js/` directory structure | Houses the TypeScript orchestrator and MiniSearch client |
| Shared webroot with blog | Enables cross-site index merging under one domain |
| Phase 6 chat widget architecture | Evolves into the Nexus governance proxy + LLM orchestration layer |

**Sequencing:** Complete resume refactor Phases 1–4 → then begin Nexus Phase 1.

## 17. Consolidated Task Checklist

### Phase 1 Tasks (Local Foundation)
- [ ] Complete resume refactor (Phases 1–4 in REFACTOR.md)
- [ ] Update Jekyll templates: common class (`.experience-item`) and unique IDs on job entries
- [ ] Ensure `<details>` content has consistent class name for script targeting
- [ ] Create `nexus-resume-index.json` Liquid template in resume repo
- [ ] Create `nexus-blog-index.json` Liquid template in blog repo
- [ ] Build the `NexusLocalSearch` TypeScript class (MiniSearch + Mark.js + DOM filtering)
- [ ] Add search bar UI with Status Beacon (hardcoded to Amber initially)
- [ ] Implement `Promise.all()` fetch-and-merge logic for both indexes
- [ ] Align skill taxonomy between `data.yml` and blog post tags
- [ ] Test: search finds content in collapsed `<details>` and expands them

### Phase 2 Tasks (Secure Proxy)
- [ ] Deploy LiteLLM container on DigitalOcean
- [ ] Draft LiteLLM `config.yaml` with model routing rules
- [ ] Configure budget enforcement ($20–50/month hard cap)
- [ ] Implement tiered model routing (Flash for discovery, Sonnet for strategy)
- [ ] Add IP-based rate limiting (leaky bucket)
- [ ] Test: budget exceeded → frontend receives governance signal → falls back to local

### Phase 3 Tasks (Private Edge)
- [ ] Spin up LXC container on Proxmox for Tailscale Funnel
- [ ] Install Ollama or Sentence-Transformers wrapper for embedding model
- [ ] Vectorize all blog posts with `all-MiniLM-L6-v2`
- [ ] Set up ChromaDB/Faiss vector store
- [ ] Expose `/status` and `/search-blog` APIs via Tailscale Funnel
- [ ] Turn Status Beacon from Amber to Green when edge is reachable
- [ ] Set up nightly cron job to re-index new blog posts
- [ ] Register P620 as primary embedding provider in LiteLLM config
- [ ] Verify Tailscale Funnel throughput from Proxmox to public domain

### Phase 4 Tasks (Executive Value)
- [ ] Create "5 Pillars" system prompt for strategic analysis
- [ ] Implement T-shirt sizing logic for fit scores
- [ ] Build "Generate 90-Day Plan" button and UI
- [ ] Route strategy requests to Claude 3.5 Sonnet via LiteLLM
- [ ] Implement Gap Analysis output with "Strategic Alignment & Mitigation" table
- [ ] Add observability/telemetry for search query patterns
- [ ] Design the "Budget Remaining" progress indicator
- [ ] Design monitoring dashboard (model usage, cost per query tier, fallback frequency)

### Cross-Cutting Concerns
- [ ] Ensure Tailscale node has most restrictive ACLs possible
- [ ] Verify no PII logging in analytics layer
- [ ] Test latency targets: local < 100ms, edge < 1s, cloud < 3s
- [ ] Implement `localStorage` caching for blog index
- [ ] Design the "Related Deep Dives" UI for blog post results under job entries
- [ ] Evaluate DigitalOcean container hosting vs. App Platform for LiteLLM
