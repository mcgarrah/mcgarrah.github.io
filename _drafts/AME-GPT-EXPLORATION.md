---
layout: none
date: 1999-12-31
sitemap: false
---

# Autonomous Model Evolution (AME) — Project Tracker

Extension of the AASR project that digs deeper into GPT/Transformer architecture evolution.
AME applies the AASR Manager-Worker evolutionary loop specifically to GPT internals —
attention head scaling, normalization placement, and other Transformer components.

Source material: Google Gemini conversation (2026) — "Building GPT From Scratch" on AlteredCarbon cluster.
Inspired by Andrej Karpathy's [AutoResearch](https://github.com/karpathy/autoresearch) and [nanoGPT](https://github.com/karpathy/nanoGPT).

See also: `AASR-PROJECT.md` (canonical AASR reference), `2026-07-01-aasr-proxmox-overview.md` (AASR Part 1 article draft).

Last updated: 2026-07-28

---

## GPT Architecture Foundations (from Karpathy)

The training substrate for AME is a nanoGPT-style decoder-only Transformer. These are the
core concepts the AI researcher will be mutating. Source: Karpathy's "Let's build GPT: from
scratch, in code, spelled out" lecture and the nanoGPT/minGPT/microGPT repositories.

### Key Resources

| Resource | URL | Notes |
|----------|-----|-------|
| Video lecture | https://www.youtube.com/watch?v=kCc8FmEb1nY | 2 hours, definitive entry point |
| nanoGPT repo | https://github.com/karpathy/nanoGPT | ~300 lines model.py + ~300 lines train.py |
| minGPT repo | https://github.com/karpathy/minGPT | Older, simpler, prioritizes readability |
| microGPT gist | https://gist.github.com/karpathy/8627fe009c40f57531cb18360106ce95 | April 2026 "code golf" version |
| Zero to Hero course | https://karpathy.ai/zero-to-hero.html | Full course, start here |
| Attention Is All You Need | https://arxiv.org/abs/1706.03762 | Original 2017 Transformer paper |
| Transformer Explainer | https://poloclub.github.io/transformer-explainer/ | Georgia Tech — live browser visualization |

### GPT as a Probability Distribution

A GPT is a probability distribution over the next token in a sequence, conditioned on
previous tokens. It is a **decoder-only Transformer** — the encoder-decoder setup from the
original "Attention Is All You Need" paper is simplified to focus on auto-regressive language
modeling: predicting the next token based on preceding context.

**Programmer's mental model:**

```
Input:       Array of integers (token IDs)
Embedding:   Look up row in learnable matrix We for each integer.
             Add positional encoding vector (so "dog bites man" ≠ "man bites dog").
Block:       Self-Attention (tokens communicate) → Feed-Forward Network (per-token compute)
             Repeated N times (AME target: 3–4 layers on P620)
Output:      Final matrix multiplication → vocabulary-size logits (e.g., 50,000)
Sampling:    Softmax logits → probabilities → sample next integer index
```

### Self-Attention: The Core Mechanism

Self-attention is a **content-based lookup** — think of a fuzzy Python dictionary.
Every token emits three vectors:

- **Q (Query):** "What am I looking for?"
- **K (Key):** "What information do I contain?"
- **V (Value):** "If you find me interesting, here is what I pass on."

The attention formula:

```
Attention(Q, K, V) = softmax( Q·Kᵀ / √d_k ) · V
```

1. `Q·Kᵀ` — dot product computes similarity score between every pair of tokens
2. `/ √d_k` — scaling factor keeps variance unit-level at initialization, prevents softmax saturation
3. `softmax(...)` — normalizes scores to sum to 1.0 (probability distribution)
4. `· V` — weighted sum of Value vectors using those probabilities

**The "Matrix Trick" (causal masking):** Karpathy demonstrates using lower triangular matrices
(`tril`) to ensure tokens only communicate with the past — they cannot "cheat" by looking at
future tokens. This is what makes it auto-regressive.

### Repeating Block Structure

Each Transformer Block (see `model.py` → `CausalSelfAttention`) has two parts:

1. **Communication (Multi-Head Attention):** Tokens look at each other to gather context
2. **Computation (Feed-Forward Network):** Each token "thinks" about gathered information individually

### Training Stability Components (AME mutation targets)

- **Residual Connections (Skip Connections):** "Gradient super-highways" — allow gradient to
  flow from output back to input unimpeded during backpropagation. Critical for deep models.
- **Layer Normalization:** Normalizes features of a single token to keep training stable.
  Karpathy notes **Pre-Norm vs Post-Norm** as a key departure from the original paper —
  this is a primary AME mutation target.

### Primary Evaluation Metric

- **`val_bpb` (bits per byte):** Primary metric from AutoResearch. Lower = model is "smarter".
- **`val_loss`:** Secondary metric, used for frontier promotion decisions.
- If `val_bpb` improves → commit the mutation to frontier branch.
- If `val_bpb` regresses or OOM → `git revert`, destroy worker LXC.

---

## Project Relationship: AASR → AME

```
AASR (Autonomous AI Scientific Research)
  └── Manager-Worker pattern on AlteredCarbon cluster
  └── Evolutionary Git Loop (hypothesize → mutate → execute → evaluate → select)
  └── General ML research automation

AME (Autonomous Model Evolution)  ← this project
  └── Extends AASR with GPT-specific mutation targets
  └── Focuses on Transformer internals: attention, normalization, embeddings
  └── "Building GPT From Scratch" as the training substrate
  └── Deeper visualization of internal math (attention maps, VRAM graphs)
```

AME is a series of articles that extends AASR. AASR articles establish the infrastructure;
AME articles dig into what the AI researcher actually discovers about GPT architecture.

---

## Hardware Context (AlteredCarbon Cluster)

| Node   | CPU               | RAM    | GPU         | VRAM       | AME Role         |
|--------|-------------------|--------|-------------|------------|------------------|
| harlan | i7-2600 (8 cores) | 31 GiB | Quadro P620 | 2 GB GDDR5 | Primary GPU worker |
| kovacs | i7-2600 (8 cores) | 31 GiB | Quadro P620 | 2 GB GDDR5 | GPU worker       |
| poe    | i7-2600 (8 cores) | 31 GiB | Quadro P620 | 2 GB GDDR5 | GPU worker       |
| quell  | i7-2600 (8 cores) | 31 GiB | Quadro P620 | 2 GB GDDR5 | GPU worker       |
| edgar  | i7-2600 (8 cores) | 31 GiB | Quadro K600 | 1 GB GDDR3 | CPU-only comparison |
| tanaka | i7-2600 (4 cores) | 15 GiB | Quadro K600 | 1 GB GDDR3 | Excluded         |

**Hard constraints for AME:**
- Sandy Bridge (2011): AVX supported, **AVX2 not supported** — all binaries must be AVX-only
- P620 Pascal: no Tensor Cores, FP32/FP16 only, 2 GB VRAM hard ceiling
- PCIe 2.0: slower GPU↔RAM transfers — CPU offloading via DeepSpeed ZeRO-2 or Accelerate
- OptiPlex 990 SFF: thermal throttling under sustained load — 3-minute cooldown enforced
- Dataset: TinyStories (not enwik8 — lower entropy, learns faster on constrained hardware)

**Training parameters tuned for P620:**

| Setting          | Default (H100) | P620 (2 GB VRAM) |
|------------------|----------------|------------------|
| Max Seq Len      | 1024           | 128–256          |
| Batch Size       | 128            | 8–16             |
| Model Depth      | 8–12 layers    | 3–4 layers       |
| Vocab Size       | 8192           | 1024–2048        |
| Experiment Window| 5 min          | 15 min           |
| Step Target      | N/A            | 500 steps        |
| Cool Down        | None           | 3 min            |

---

## AME Research Focus: GPT Internals

AME targets specific Transformer components as mutation candidates for the evolutionary loop.
Each mutation class maps to a hypothesis the AI researcher can propose and test.

### Mutation Target Classes

| Component | Mutation Examples | Metric Impact |
|-----------|-------------------|---------------|
| Attention heads | Scale head count (1→2→4), head dimension | val_loss, VRAM usage |
| Normalization placement | Pre-norm vs post-norm, RMSNorm vs LayerNorm | Training stability, convergence speed |
| Embedding dimensions | Shrink/grow d_model relative to depth | Parameter efficiency |
| FFN ratio | 4× → 2× or 8× expansion factor | VRAM vs expressiveness |
| Positional encoding | Learned vs RoPE vs ALiBi at seq_len 128–256 | Generalization |
| Activation function | GELU vs SwiGLU vs ReLU | Speed vs quality |
| Residual connections | Pre/post scaling, depth-dependent scaling | Gradient flow |
| Dropout placement | Attention dropout vs residual dropout | Regularization |

### The AME Hypothesis Format

The AI researcher proposes mutations in a structured format that the Manager validates:

```
# Hypothesis: [one-line description]
# Target component: [attention|normalization|embedding|ffn|positional|activation|residual]
# Expected effect: [val_loss direction and reasoning]
# VRAM delta estimate: [+/- MB]
# Risk: [low|medium|high]
[unified diff of train.py]
```

### Suggested program.md Research Goal (from Gemini conversation)

The exact wording Gemini suggested for directing the agent at GPT Block mutations:

```markdown
"Explore architectural mutations in the Block class (e.g., number of heads, MLP expansion
ratios, or LayerNorm placement) to achieve the lowest bits-per-byte (bpb) on Tiny Shakespeare
within a 15-minute training window on a P620 GPU."
```

Hardware-aware variant (platform engineering angle):

```markdown
"Optimize the nanoGPT architecture specifically for the CPU/GPU constraints of the
AlteredCarbon cluster (i7-2600, P620 2GB VRAM, PCIe 2.0). Minimize latency while keeping
val_loss below 1.5. AVX only — no AVX2 code paths."
```

### Three Key Metrics to Monitor During AME Runs

From the Gemini conversation — these three metrics directly expose GPT underpinnings:

| Metric | GPT Underpinning | What It Tells You |
|--------|-----------------|-------------------|
| Gradient Norm | Backpropagation | Is the new architecture stable, or did the mutation break the "Gradient Super-highway"? |
| Throughput (Tokens/sec) | Platform Efficiency | Did the mutation (e.g., adding more heads) make the model too slow for the P620s? |
| Attention Maps | Self-Attention | Visualizing where the model is "looking" after the agent changes Key/Query dimensions |

These map directly to the three Phase 3 visualization targets: gradient flow graphs,
throughput counters, and attention map overlays in the Gradio worker UI.

---

## Three-Phase Implementation Strategy

### Phase One: Proxmox Testing Framework

**Goal:** Ensure legacy hardware reliability before running evolutionary experiments.

- [ ] Automated LXC provisioning for worker nodes (harlan, kovacs, poe, quell)
- [ ] AVX compatibility checks — verify no AVX2 instructions in PyTorch wheel
- [ ] Thermal guardrails — monitor CPU/GPU temps, enforce 3-minute cooldown
- [ ] GPU passthrough validation — `nvidia-smi` accessible inside LXC
- [ ] CephFS mount verification — dataset reads from `/mnt/pve/cephfs/` in worker
- [ ] Baseline train.py run — 500 steps on TinyStories, record val_loss and VRAM peak
- [ ] Worker results JSON schema validated end-to-end (worker → Manager `/api/results`)
- [ ] Forgejo LXC running at 192.168.86.201 with `autoresearch` repo
- [ ] Manager LXC running at 192.168.86.202 with Flask + proxmoxer

**Success criteria:** Clean 15-minute training burst on all 4 P620 nodes, metrics posted to Manager, worker LXC destroyed cleanly.

### Phase Two: AME GPT Underpinnings

**Goal:** Apply the evolutionary loop specifically to Transformer components.

- [ ] Baseline GPT implementation in `train.py` (nanoGPT-style, 3-4 layers, TinyStories)
- [ ] `program.md` hardware manifest written and fed to AI researcher
- [ ] Attention head scaling mutations — test 1, 2, 4 heads at fixed d_model
- [ ] Normalization placement mutations — pre-norm vs post-norm comparison
- [ ] Embedding dimension sweep — d_model 64, 128, 256 at fixed depth
- [ ] FFN ratio mutations — 2×, 4×, 8× expansion at fixed d_model
- [ ] Positional encoding comparison — learned vs RoPE at seq_len 128
- [ ] Activation function comparison — GELU vs SwiGLU
- [ ] Multi-model A/B testing — assign different AI models to different P620 nodes
- [ ] Leaderboard tracking — val_loss improvement per mutation class
- [ ] Frontier branch evolution — track which mutation classes produce consistent wins

**Success criteria:** At least 10 successful evolutionary cycles with measurable val_loss improvement over baseline.

### Phase Three: Deep Visualization

**Goal:** Extend the Gradio worker interface to visualize internal math in real time.

- [ ] Attention map overlays — heatmap of attention weights per head per layer (QKᵀ matrix visualization)
- [ ] VRAM offloading graphs — live GPU vs CPU memory split, showing KV cache and optimizer state offload from 2GB P620 to 32GB system RAM
- [ ] Residual Stream Analysis — monitoring the "Gradient Super-highway" to detect if a mutation has made the model too deep or unstable for the legacy i7-2600 CPUs
- [ ] Gradient flow visualization — per-layer gradient norms over training steps
- [ ] Loss landscape snapshots — 2D projections of loss surface around current weights
- [ ] Head specialization analysis — what each attention head learns to attend to
- [ ] Mutation diff viewer — side-by-side before/after train.py with highlighted changes
- [ ] Experiment timeline — visual history of frontier evolution with branch annotations
- [ ] Flask dashboard integration — embed Gradio iframes per active worker node

**Success criteria:** Gradio UI shows attention maps and VRAM graphs live during a 15-minute training burst.

---

## The AME Research Loop (Extended from AASR)

```
1. HYPOTHESIZE (AME-specific)
   Manager sends: experiment history + current train.py + program.md hardware manifest
   AI proposes: a targeted GPT component mutation with hypothesis comment
   ↓
2. VALIDATE
   Syntax check (ast.parse), policy check (no shell calls, no network outside allowed endpoints)
   Reject malformed or forbidden mutations without executing
   ↓
3. MUTATE
   Commit new train.py to experiment branch: experiment-<YYYYMMDD-HHMMSS>-<component>-<slug>
   ↓
4. EXECUTE
   Clone Gold Template LXC to idle P620 node
   Push train.py via pct push or CephFS shared path
   Start 15-minute training burst via pct exec
   ↓
5. EVALUATE (AME-specific)
   Worker trains 500 steps (or 15 min, whichever first)
   Gradio shows: loss curve + attention maps + VRAM graph (Phase 3)
   Worker POSTs results JSON to Manager /api/results
   ↓
6. SELECT
   val_loss improved → merge to frontier, record winning mutation class
   val_loss regressed or OOM → discard branch, log failure pattern
   ↓
7. COOL DOWN
   3-minute thermal pause
   Manager updates mutation class leaderboard
   ↓
   Loop back to step 1
```

---

## AI Provider Strategy

### Primary: GitHub Models (OpenAI-compatible)

```python
# manager/ai_provider.py
import os
from openai import OpenAI

HARDWARE_CONTEXT = """
Hardware: Dell OptiPlex 990 cluster (AlteredCarbon)
- CPU: Intel i7-2600 Sandy Bridge, 8 cores, 32GB DDR3
- GPU: NVIDIA Quadro P620, 2GB GDDR5, Pascal (GP107GL), no Tensor Cores
- Bus: PCIe 2.0
- AVX: Yes. AVX2: NO. All binaries must be AVX-only compiled.
Experiment constraints:
- VRAM ceiling: 2GB. Active model weights must fit.
- System RAM: 32GB — use for gradient offloading (DeepSpeed ZeRO-2, Accelerate).
- Max seq len: 128-256. Batch size: 8-16. Model depth: 3-4 layers.
- Experiment window: 15 min wall clock or 500 steps (whichever first).
- Cooldown: 3 min between experiments (thermal management).
- Dataset: TinyStories (not enwik8).
AME focus: Propose mutations targeting GPT Transformer internals.
Mutation classes: attention heads, normalization placement, embedding dims,
FFN ratio, positional encoding, activation functions, residual connections.
"""
```

**Recommended models:**

| Model                       | Context | Best For                                      |
|-----------------------------|---------|-----------------------------------------------|
| `claude-sonnet-4-5`         | 1M      | Primary — large context, strong code reasoning |
| `gpt-4o`                    | 128K    | Secondary — faster iteration cycles           |
| `gpt-4o-mini`               | 128K    | History summarization (cheap)                 |
| `meta-llama-3-70b-instruct` | 128K    | Open-weights alternative                      |

### Optional: Gemini API

- `google-generativeai` SDK, 2M token context
- Useful for very long experiment histories (>50 experiments)
- Original inspiration for this project (see PDF source material)

### Multi-Model A/B Testing

Assign different AI models to different P620 nodes to compare which produces better val_loss improvements:

```python
MODEL_ROTATION = {
    "harlan": "claude-sonnet-4-5",
    "kovacs": "gpt-4o",
    "poe":    "claude-sonnet-4-5",
    "quell":  "gpt-4o",
}
```

Track `model_name` in the `experiments` table alongside `val_loss` to analyze which model writes more hardware-efficient GPT mutations.

---

## Repository Layout

```text
aasr/
  manager/
    app.py                  # Flask + HTMX dashboard
    ai_provider.py          # Provider abstraction (GitHub Models / Gemini)
    scheduler.py            # Experiment orchestration loop
    evaluator.py            # val_loss comparison and frontier promotion
    models.py               # SQLAlchemy schema
    templates/              # HTMX dashboard templates
  worker/
    train.py                # GPT training script (mutation sandbox)
    prepare.py              # TinyStories data pipeline
    gradio_monitor.py       # Live visualization (loss, attention maps, VRAM)
    start.sh                # Worker boot: train → report → exit
    requirements.txt
  prompts/
    program.md              # Human goals, hardware constraints, scoring objective
    hardware_manifest.md    # AlteredCarbon hardware context for AI researcher
  ops/
    proxmox/
      lxc-template.conf     # Gold Template LXC config (GPU passthrough)
      create-core-services.sh
    forgejo/
      bootstrap-repo.sh
  docs/
    runbook.md
    troubleshooting.md
```

---

## Infrastructure: Core Service LXCs

### Forgejo Git Server (192.168.86.201)

```bash
pct create 201 local:vztmpl/debian-13-standard_13.0-1_amd64.tar.zst \
  --hostname forgejo \
  --cores 1 --memory 1024 --swap 512 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.86.201/23,gw=192.168.86.1 \
  --nameserver 192.168.86.3 \
  --mp0 /mnt/pve/cephfs/aasr/forgejo,mp=/var/lib/gitea
```

Post-setup: create API token for Flask orchestrator; create `autoresearch` repo with `main` and `frontier` branches.

### Manager LXC (192.168.86.202)

- 2 vCPU, 4 GB RAM, Debian 13
- Flask + HTMX dashboard, Flask-SQLAlchemy, proxmoxer, openai SDK
- CephFS mount at `/mnt/data` for shared datasets and results

**Key Flask routes:**

| Route             | Method | Purpose                                          |
|-------------------|--------|--------------------------------------------------|
| `/`               | GET    | Dashboard: node grid, leaderboard, live console  |
| `/node-status`    | GET    | HTMX fragment: node temps, GPU idle/busy         |
| `/start-research` | POST   | Trigger new experiment cycle                     |
| `/kill/<vmid>`    | POST   | Emergency destroy of a rogue worker              |
| `/api/results`    | POST   | Worker callback with final metrics               |
| `/config/model`   | POST   | Switch active AI model without restart           |

### Gold Template Worker LXC

- 4 vCPU, 28 GB RAM, Debian 13
- NVIDIA production drivers, uv, git, gradio, PyTorch (AVX-only)
- GPU passthrough: P620 device nodes
- CephFS mount at `/data` (read-only)

```conf
# /etc/pve/lxc/<TEMPLATE_ID>.conf
lxc.cgroup2.devices.allow: c 195:* rwm
lxc.cgroup2.devices.allow: c 234:* rwm
lxc.mount.entry: /dev/nvidia0 dev/nvidia0 none bind,optional,create=file
lxc.mount.entry: /dev/nvidiactl dev/nvidiactl none bind,optional,create=file
lxc.mount.entry: /dev/nvidia-uvm dev/nvidia-uvm none bind,optional,create=file
lxc.cgroup2.cpuset.cpus: 0-3
lxc.cgroup2.memory.max: 28G
```

**Worker results JSON schema:**
```json
{
  "experiment_id": "20260601-143022-attention-heads-2",
  "mutation_class": "attention",
  "steps_completed": 500,
  "duration_seconds": 847,
  "val_loss": 1.2341,
  "val_bpb": 1.7812,
  "peak_vram_mb": 1820,
  "peak_ram_mb": 14200,
  "temperature_max_c": 78,
  "success": true,
  "error": null
}
```

---

## Git Model: Branch-per-Experiment

```
main ──────────────────────────────────────────────►  (stable, human-controlled)
  │
  ├── frontier ──────────┬──────────┬──────────────►  (best machine-evolved GPT)
  │                      │          │
  │   experiment-001-attention-heads-2 ────┘
  │   (merged: val_loss 1.41 → 1.38)
  │
  │   experiment-002-prenorm-rmsnorm ───── X
  │   (discarded: OOM at seq_len 256)
  │
  │   experiment-003-ffn-ratio-2x ─────────────────┘
  │   (merged: val_loss 1.38 → 1.35, VRAM -180MB)
```

Workers never touch git directly — Manager drives all Forgejo API calls.

---

## Security and Isolation

- Worker LXC network egress restricted to Manager (192.168.86.202) and Forgejo (192.168.86.201) only — no internet
- Worker git credentials scoped to experiment branches only — no write access to `main` or `frontier`
- Manager Proxmox API token scoped to `PVEVMAdmin` for LXC lifecycle only
- AI token scoped to `models:read` only — no repo write access
- AI output validated before execution: `ast.parse()` → forbidden API/path check
- Strict CPU pinning (4 cores) and memory caps (28 GB) per worker
- Fresh LXC clone for every experiment — no state leaks between runs
- Every mutation logged with diff, reasoning, and metrics in Flask DB and Forgejo commit history

---

## Open Questions

- [ ] Exact NVIDIA host + container driver version for Proxmox 8.4 kernel (6.8.12-18-pve)
- [ ] Whether `pct push` / `pct exec` is sufficient or SSH-based orchestration is more reliable
- [ ] CephFS read amplification impact on parallel worker throughput during training
- [ ] GitHub Models rate limits per hour — max experiment frequency before throttling
- [ ] Whether `claude-sonnet-4-5` remains consistently available via GitHub Models
- [ ] Thermal telemetry source — can Proxmox sensor data be read from within an LXC?
- [ ] Parallel experiment git strategy — linear frontier vs. branching tournament selection
- [ ] Streaming responses: GitHub Models supports `stream=True` — surface reasoning tokens on dashboard?
- [ ] Which attention map visualization library works best with Gradio + PyTorch on P620?
- [ ] Whether K600 nodes (edgar) deliver enough signal for CPU-only comparison experiments

---

## Blog Article Series

### AASR Series (prerequisite — establishes infrastructure)

| Part | Topic                        | Status  | File |
|------|------------------------------|---------|------|
| 1    | Architecture                 | Draft   | `2026-07-01-aasr-proxmox-overview.md` |
| 2    | GPU Passthrough in LXC       | Planned | — |
| 3    | The Evolutionary Git Loop    | Planned | — |
| 4    | Training on 2 GB VRAM        | Planned | — |
| 5    | AI Provider Abstraction      | Planned | — |

### AME Series (this project — GPT deep dive)

| Part | Topic                              | Status  | Notes |
|------|------------------------------------|---------|-------|
| 1    | AME: Building GPT From Scratch     | Planned | nanoGPT baseline on TinyStories, hardware constraints |
| 2    | Attention Head Scaling             | Planned | What the AI discovers about head count on 2GB VRAM |
| 3    | Normalization Placement            | Planned | Pre-norm vs post-norm on legacy hardware |
| 4    | Visualizing Transformer Internals  | Planned | Attention maps, VRAM graphs, Gradio Phase 3 |
| 5    | What the AI Researcher Discovered  | Planned | Results: winning mutation classes, frontier evolution |

**Publication cadence:** MWF slots, AASR series first, AME series follows.
AASR Part 1 draft exists (`2026-07-01-aasr-proxmox-overview.md`) — needs promotion to `_posts/`.

---

## Status Summary

| Phase | Status | Blocker |
|-------|--------|---------|
| Phase 1: Proxmox Testing Framework | 🔲 Not started | Forgejo LXC not yet provisioned |
| Phase 2: AME GPT Underpinnings | 🔲 Not started | Depends on Phase 1 |
| Phase 3: Deep Visualization | 🔲 Not started | Depends on Phase 2 |
| AASR Part 1 article | 📝 Draft ready | Needs promotion to `_posts/` |
| AME articles | 📝 Planned | Depends on implementation |

**Next action:** Provision Forgejo LXC (192.168.86.201) on harlan or kovacs to begin Phase 1.

---

## Related Files

| File | Purpose |
|------|---------|
| `AASR-PROJECT.md` | Canonical AASR reference and implementation guide |
| `2026-07-01-aasr-project-series-overview.md` | AASR five-part series index article |
| `2026-07-01-aasr-proxmox-overview.md` | AASR Part 1 article draft (nearest to publishable) |
| `AME-GPT-EXPLORATION.md` | This file — AME project tracker |
