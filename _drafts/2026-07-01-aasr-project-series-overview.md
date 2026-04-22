---
title: "Autonomous AI Scientific Research: A Five-Part Series Overview"
layout: post
categories: [ai, homelab, research]
tags: [proxmox, machine-learning, aasr, ceph, automation, flask, gradio, forgejo]
excerpt: "Building an autonomous ML research cluster on legacy hardware — a five-part series covering the Manager-Worker architecture, GPU passthrough, the evolutionary Git loop, AI provider integration, and hardware-aware data science."
date: 2026-07-01
last_modified_at: 2026-07-28
sitemap: false
---

The idea of AI automating scientific research sounds like something reserved for hyperscalers
with massive H100 clusters. But what if you could orchestrate a miniature version of this on
14-year-old enterprise desktops?

This is the Autonomous AI Scientific Research (AASR) project. The goal is to automate the
machine learning research lifecycle on a homelab cluster built entirely from legacy hardware,
using AI agents to hypothesize, code, and validate architectural improvements to neural networks
using an evolutionary Git loop.

Inspired by Andrej Karpathy's [AutoResearch](https://github.com/karpathy/autoresearch), this
series documents the full build — from bare Proxmox infrastructure through to a running
autonomous AI researcher grinding away on your cluster overnight.

<!-- excerpt-end -->

This post is the series index. Each part is linked below as articles are published.

---

## The Core Architecture

This project sits at the intersection of **Platform Engineering** and **Data Science**. Because
the hardware is highly constrained, the system relies on strict resource isolation, ephemeral
containers, and aggressive memory offloading.

- **The Orchestrator (Manager LXC):** A persistent Debian LXC running Flask + HTMX,
  Flask-SQLAlchemy, and Proxmox API integrations. Acts as the brain — reviewing past experiment
  history and proposing code mutations via an LLM.
- **The Laboratories (Worker LXCs):** Ephemeral LXCs cloned on-demand to execute 15-minute
  training bursts with GPU passthrough. If an experiment improves validation loss, it gets merged
  into the frontier branch. If it fails, the container is destroyed.
- **The Git Engine:** A local Forgejo (Gitea fork) LXC tracking the evolutionary history of
  `train.py` across hundreds of automated commits.
- **The Visualization Layer:** Each worker runs a Gradio app on port 7860 for real-time loss
  curves and GPU metrics, embedded as iframes in the central Flask dashboard.

## The Hardware Foundation

AASR runs on the **AlteredCarbon** cluster — proving you don't need a hyperscaler to experiment
with autonomous AI agents:

- **Compute Fleet:** 6× Dell OptiPlex 990 nodes (Intel i7-2600 Sandy Bridge, 32GB DDR3 RAM each)
- **Accelerators:** NVIDIA Quadro P620s (2GB GDDR5) on 4 nodes; Quadro K600s (1GB GDDR3) on 2 nodes
- **Storage:** 69 TiB raw CephFS shared storage over a dual-network (LAN/SAN) architecture
- **Hard Constraints:** Sandy Bridge CPUs lack AVX2 (requiring custom-compiled PyTorch binaries);
  2GB VRAM ceiling requires heavy reliance on RAM offloading via DeepSpeed or Unsloth

## The AI Reasoning Engines

AASR uses a provider-agnostic abstraction layer, allowing different frontier models to act as
the "Brain" of the Orchestrator:

- **GitHub Models (primary):** `claude-sonnet-4-5` or `gpt-4o` via OpenAI-compatible API using
  a sliding-window summarization strategy to compress older experiments into hardware-specific insights
- **Google Gemini 3 Pro (optional):** 2M token context window allows the Orchestrator to ingest
  the entire historical git log and loss curve history in a single prompt for deep long-term reasoning
- **Amazon Q / Local models:** Evaluated for infrastructure automation and as CPU-only alternatives
  on nodes without viable GPU passthrough

---

## The Five-Part Series

### Part 1: Platform Engineering & Core Services
**Status:** Draft — `2026-07-01-aasr-proxmox-overview.md`

Covers the overall architecture decision and the two persistent core service LXCs that underpin
everything else.

- Designing the Manager-Worker pattern for legacy hardware constraints
- Bootstrapping the Forgejo Git Server LXC (192.168.86.201) on CephFS
- Building the Flask Manager LXC (192.168.86.202) with proxmoxer and SQLAlchemy
- The branch-per-experiment Git model: `main` → `frontier` → `experiment-<slug>`
- Security baseline: least privilege, network egress restriction, SSH key scoping per branch

**Key decisions to document:**
- Why Forgejo over bare git repos (API-driven branch/merge, audit trail, web UI)
- Why Flask + HTMX over Django (lightweight, HTMX polling replaces WebSockets)
- Proxmox API token scoping (`PVEVMAdmin` for LXC lifecycle only)

---

### Part 2: Ephemeral GPU Laboratories
**Status:** Planned

Covers building the Gold Template worker LXC and the dynamic orchestration logic that clones,
runs, and destroys it for each experiment.

- Building an AVX-safe, GPU-passthrough Proxmox LXC template for training bursts
  - NVIDIA production driver installation (matching host kernel 6.8.12-18-pve)
  - LXC `.conf` GPU passthrough stanzas (`lxc.cgroup2.devices.allow`, `lxc.mount.entry`)
  - AVX-only PyTorch build (`GGML_AVX2=OFF GGML_AVX=ON`)
  - `uv` package manager, `gradio`, pre-loaded TinyStories dataset via CephFS mount
- Writing the `proxmoxer` Python integration: `find_idle_gpu_node()`, `run_experiment()`, `cleanup_worker()`
- Worker boot script (`start.sh`): train → POST results → exit
- Worker results JSON schema (`val_loss`, `val_bpb`, `peak_vram_mb`, `temperature_max_c`)
- The "Clean Room" benefit: fresh LXC clone per experiment prevents environment pollution

**Key decisions to document:**
- `pct push` / `pct exec` vs SSH-based orchestration trade-offs
- CephFS read-only mount for dataset access (zero-copy, no per-worker download)
- CPU pinning (4 cores) and memory cap (28GB) to protect Proxmox host stability

---

### Part 3: The Evolutionary Git Loop
**Status:** Planned

Covers the full automated research cycle — from hypothesis generation through to frontier
promotion or rollback.

- The 7-step research loop: Hypothesize → Validate → Mutate → Execute → Evaluate → Select → Cool Down
- Why 15 minutes (not 5): JIT warmup 60–90s, PCIe 2.0 offload latency, val_loss stabilization
- Why 500 steps as the success criterion (normalizes across nodes regardless of load)
- Why 3-minute cooldown (OptiPlex 990 SFF thermal throttling under sustained load)
- Forgejo API automation: branch creation, file commit, PR open, auto-merge on success
- Flask dashboard: cluster grid, leaderboard, live console, kill switch, audit log
- Gradio worker UI: live loss curve, GPU temperature, VRAM usage, elapsed steps
- IFrame gallery: Flask dynamically embeds each active worker's Gradio app

**Key decisions to document:**
- Linear frontier vs. branching tournament selection (open question)
- `ast.parse()` + forbidden pattern check before applying any AI-generated diff
- Traceable AI development: every mutation logged with diff, reasoning, and metrics

---

### Part 4: AI Context and Hypothesis Generation
**Status:** Planned

Covers the AI provider integration layer — how the Manager talks to LLMs, manages context
budgets, and extracts useful mutations from experiment history.

- The `ai_brain.py` provider abstraction (`ResearchModel` base class, swappable implementations)
- GitHub Models implementation: OpenAI-compatible SDK, `GITHUB_TOKEN` with `models:read` scope
- Gemini implementation: `google-generativeai` SDK, 2M token context advantage
- Context budget planning: system prompt (~400 tokens) + train.py (~3K) + rolling history (~6K)
- Rolling window strategy: keep last 30 experiments in compact format (~100–200 tokens each)
- Summarization trigger: when `len(experiments) > 50`, compress oldest 30 into `MetaInsight` table
- Multi-model A/B testing: assign different models to different P620 nodes, compare val_loss outcomes
- Model selector Flask route + HTMX fragment (switch active model without restart)
- `gh copilot` CLI for development-time infrastructure queries

**Key decisions to document:**
- Why `gpt-4o-mini` for summarization (cheap, fast, good enough for compression tasks)
- GitHub Models rate limits and the 3-minute cooldown as a natural throttle
- Streaming responses (`stream=True`) for surfacing reasoning tokens on dashboard (future)

---

### Part 5: Hardware-Aware Data Science
**Status:** Planned

Covers the training configuration, memory management, and what the AI researcher actually
discovers when constrained to 2GB VRAM on 14-year-old hardware.

- Training parameter tuning for P620: TinyStories, seq_len 128–256, batch 8–16, 3–4 layers
- CPU offloading strategy: DeepSpeed ZeRO-2, Hugging Face Accelerate, Unsloth (70% VRAM reduction)
- The 32GB RAM advantage: optimizer state offloading, gradient offloading, dataset pre-fetch buffer
- Thermal management: monitoring OptiPlex 990 chassis sensors, enforcing cooldown guardrails
- K600 nodes (edgar): CPU-only comparison experiments, 1GB VRAM limitations
- Results: which mutation classes produce consistent val_loss improvements on P620 hardware
- The "Poor Man's H100" framing: aggregating VRAM and compute across 5 nodes

**Key decisions to document:**
- Why TinyStories over enwik8 (lower entropy, faster convergence on constrained hardware)
- Treating repeated OOM for the same mutation class as a negative learned pattern
- Whether K600 nodes deliver enough signal to justify maintenance overhead

---

## Companion Series: AME (Autonomous Model Evolution)

After the AASR infrastructure series, a companion series digs into GPT/Transformer internals
specifically — using the same evolutionary loop to mutate attention head scaling, normalization
placement, FFN ratios, and positional encoding. See `AME-GPT-EXPLORATION.md` for the full plan.

---

## Reference Materials

- `AASR-PROJECT.md` — Canonical technical reference (hardware, code, phase plan, open questions)
- `AME-GPT-EXPLORATION.md` — AME companion project tracker
- `k8s-proxmox` repository — Underlying cluster infrastructure and hardware documentation
- [AutoResearch by Andrej Karpathy](https://github.com/karpathy/autoresearch) — Upstream inspiration
- [Proxmox & Ceph Homelab Guide](/proxmox-ceph-guide/) — Prerequisites and baseline cluster setup
