---
layout: none
date: 1999-12-31
sitemap: false
---

# Autonomous AI Scientific Research (AASR) — Project Tracker

Canonical reference for the AASR project on the AlteredCarbon Proxmox cluster.
Consolidated from: AASR-PROXMOX.md, AASR-PROXMOX-AMAZONQ.md, AASR-PROXMOX-COPILOT.md,
AASR-PROXMOX-CONSOLIDATED-COPILOT.md, AARC_Project_Manifest.md, and two Gemini conversation PDFs.

Inspired by Andrej Karpathy's [AutoResearch](https://github.com/karpathy/autoresearch).
See also: `AME-GPT-EXPLORATION.md` for the GPT deep-dive companion project.

Last updated: 2026-07-28

---

## 1. Origin Story

This project emerged from a Gemini conversation on April 20, 2026, exploring the AutoResearch
project by Andrej Karpathy and how it could be adapted to run on the AlteredCarbon homelab cluster.

### 1.1 The AutoResearch Concept

AutoResearch (github.com/karpathy/autoresearch) is an intentionally minimalist open-source project
released by Andrej Karpathy (co-founder of OpenAI, former Tesla AI Director) in early 2026.
It shifts AI from "coding assistant" to "autonomous researcher" that independently improves its own
performance while you sleep.

**The three-file architecture:**

| File | Role | Editable by AI? |
|------|------|-----------------|
| `prepare.py` | Data loading, tokenization, evaluation ground truth | No — locked |
| `train.py` | Model architecture, optimizer, hyperparameters — the mutation sandbox | Yes — only this file |
| `program.md` | Human goals, hardware constraints, scoring objective | No — human-controlled |

**The ReAct loop (Reasoning and Acting):**

1. **Read** — Agent reads current `train.py` and `results.tsv` from previous attempts
2. **Hypothesize** — Writes reasoning: "Run #12 failed with OOM. I will reduce batch size but increase gradient accumulation steps."
3. **Edit** — Uses diff/search-replace to rewrite specific lines in `train.py`
4. **Execute** — Triggers `uv run train.py`, pipes output to log file
5. **Observe** — Parses log for `val_bpb` (bits per byte) — lower = model is smarter

**"Survival of the Fittest" git logic:**
- If code improves `val_bpb` → `git commit` — this version becomes the new frontier
- If code fails or regresses → `git reset --hard HEAD~1` — bad code wiped, start from last success

**Why this matters in 2026:** Unlike AutoML (which tunes numbers within a predefined box),
AutoResearch lets the agent rewrite the box itself — changing neural network layer math,
inventing new activation functions, restructuring the training pipeline entirely.

### 1.2 Broader Context: AI Automating Research (2026)

| Project | Organization | Milestone |
|---------|-------------|-----------|
| AI Scientist v2 | Sakana AI | First fully AI-generated paper to pass peer review, published in Nature |
| AI Researcher Roadmap | OpenAI | "AI intern" planned Sept 2026; multi-agent platform by 2028 |
| Weak-to-Strong Research | Anthropic | Autonomous agents outperforming humans on targeted alignment tasks |
| AutoDiscovery | AI2 (Allen Institute) | Bayesian surprise algorithms for hypothesis generation in climate science and biology |

### 1.3 Portfolio Framing

This project sits at the intersection of two domains:
- **As a Platform Engineer:** Solving legacy hardware constraints (no AVX2, 2GB VRAM) by offloading
  the "Brain" to an API and using LXC for clean-room execution. Managing a distributed Ceph/Proxmox
  environment with a custom Flask orchestrator.
- **As a Data Scientist:** Implementing an Evolutionary Search algorithm. Not manually tuning a model
  but engineering a system that understands Bits Per Byte (BPB) and uses LLMs to optimize those metrics.

"Poor Man's H100" — aggregating VRAM and compute across 5 OptiPlex nodes turns a collection of
$50 office PCs into a sophisticated AI R&D laboratory.

---

## 2. Project Summary

Build a Manager-Worker system on the AlteredCarbon cluster that automates the ML research lifecycle:

1. Manager composes a prompt from `program.md` + compressed experiment history and calls an LLM
2. LLM proposes a code mutation to `train.py`
3. Manager validates the mutation (syntax, policy) and commits it to an experiment branch in Forgejo
4. Manager clones an ephemeral GPU-enabled worker LXC on an idle P620 node
5. Worker runs a bounded training burst (15 min wall clock, target 500 steps)
6. Worker posts structured metrics JSON to Manager
7. Manager compares against frontier baseline — merges winners, discards losers
8. Manager destroys worker, records audit trail, waits 3-minute cooldown, repeats

---

## 3. Hardware Inventory

From `k8s-proxmox/docs/CLUSTER-SUMMARY.md` (January 2026):

| Node   | CPU                | RAM    | GPU          | GPU Arch         | VRAM        | AASR Role            |
|--------|--------------------|--------|--------------|------------------|-------------|----------------------|
| harlan | i7-2600 (8 cores)  | 31 GiB | Quadro P620  | Pascal (GP107GL) | 2 GB GDDR5  | Primary GPU worker   |
| kovacs | i7-2600 (8 cores)  | 31 GiB | Quadro P620  | Pascal (GP107GL) | 2 GB GDDR5  | GPU worker           |
| poe    | i7-2600 (8 cores)  | 31 GiB | Quadro P620  | Pascal (GP107GL) | 2 GB GDDR5  | GPU worker           |
| quell  | i7-2600 (8 cores)  | 31 GiB | Quadro P620  | Pascal (GP107GL) | 2 GB GDDR5  | GPU worker           |
| edgar  | i7-2600 (8 cores)  | 31 GiB | Quadro K600  | Kepler (GK107GL) | 1 GB GDDR3  | CPU-only comparison  |
| tanaka | i7-2600 (4 cores)  | 15 GiB | Quadro K600  | Kepler (GK107GL) | 1 GB GDDR3  | Excluded             |

**Totals:** 44 CPU cores, ~173 GiB RAM, 4× P620 (2 GB), 2× K600 (1 GB)

**Hard constraints:**
- i7-2600 = Sandy Bridge (2011). AVX supported, **AVX2 not supported**. All binaries (torch,
  llama.cpp) must be compiled AVX-only. Modern pre-built wheels will crash with `Illegal instruction`.
- P620 = Pascal, no Tensor Cores. FP32/FP16 only. 2 GB VRAM is the hard ceiling for active weights.
- K600 = Kepler, 1 GB VRAM. Useful only for CPU-offload-only or smallest experiments.
- PCIe 2.0 on all nodes — slower GPU↔RAM transfers than modern hardware.
- OptiPlex 990 SFF chassis — thermal throttling under sustained load. Enforce 3-minute cooldown.

**AVX-only build for llama.cpp:**
```bash
cmake -B build -DGGML_AVX2=OFF -DGGML_AVX=ON
```

**Node policy for AASR:**
- GPU workers: harlan, kovacs, poe, quell (P620)
- CPU-only optional comparison worker: edgar (skip GPU passthrough, use 31 GiB RAM)
- Exclude tanaka (4 cores, 15 GiB — insufficient for worker LXC)

### 3.1 The 32GB RAM Advantage

Having 32GB system RAM on each node dramatically changes available techniques even with 2GB VRAM:

- **CPU Offloading:** Use DeepSpeed ZeRO-2 or Hugging Face Accelerate to offload optimizer states
  and gradients to system RAM. Allows models 4–8× larger than VRAM alone would permit (slower due
  to PCIe 2.0 transfer overhead).
- **Unsloth library:** Optimizes kernels for 70% less VRAM with zero accuracy loss. Combined with
  32GB RAM, a P620 can handle models that normally require 6–8GB VRAM.
- **Large dataset buffering:** Use 32GB RAM as a massive pre-fetch buffer. Workers pull data from
  system RAM at local speeds rather than hitting CephFS on every batch.

**program.md hardware manifest (feed this to the AI researcher):**
```markdown
## Hardware Context
- Node: Dell OptiPlex 990 (i7-2600 Sandy Bridge, 32GB DDR3)
- Accelerator: NVIDIA Quadro P620 (2GB GDDR5, Pascal, no Tensor Cores)
- Bus: PCIe 2.0 (slower GPU↔RAM transfers)
- Constraint: 2GB VRAM for active weights. 32GB system RAM for offloading.
- Objective: Prioritize micro-architectures (3-4 layers, small embedding dims).
  Use system RAM for gradient offloading and large data shuffling.
- AVX: Supported. AVX2: NOT supported. Do not use AVX2-dependent code paths.
- Each experiment: 15 minutes max, 500 training steps target.
- Dataset: TinyStories
```

### 3.2 K600 Nodes (edgar, tanaka)

The Quadro K600 has only 1 GB GDDR3 (Kepler architecture):
- **edgar:** CPU-only worker — skip GPU passthrough, use 31 GiB RAM for CPU-based training.
  Useful for comparison experiments against P620 GPU results.
- **tanaka:** Only 4 cores and 15 GiB RAM — exclude from AASR workers entirely.

---

## 4. Storage

| Pool    | Type   | Available | Purpose                                   |
|---------|--------|-----------|-------------------------------------------|
| cephfs  | CephFS | 6.5 TiB   | Shared datasets, experiment logs, results |
| cephrbd | RBD    | 6.5 TiB   | K8s PVs (not used for AASR)               |

- Total raw: 69 TiB across 15 OSDs on 5 hosts (3× replication)
- CephFS mount: `/mnt/pve/cephfs/` on all Proxmox hosts — workers mount for zero-copy dataset access
- Ceph public network: 192.168.86.0/23
- Ceph cluster/SAN network: 10.10.10.0/23 (OSD replication, isolated from client traffic)

---

## 5. Network

| Network     | CIDR            | Purpose                              |
|-------------|-----------------|--------------------------------------|
| Raleigh LAN | 192.168.86.0/23 | Management, LXC IPs, Flask dashboard |
| SAN         | 10.10.10.0/23   | Ceph OSD replication (isolated)      |
| DNS         | 192.168.86.3    | Technitium split-horizon DNS         |

**LXC IP allocation (static services range):**
- 192.168.86.201 — Forgejo LXC
- 192.168.86.202 — Manager LXC
- 192.168.86.203+ — reserved for future core services

---

## 6. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Proxmox Cluster                          │
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐               │
│  │  Manager LXC     │    │  Forgejo LXC     │               │
│  │  Flask + HTMX    │◄──►│  Git Server      │               │
│  │  AI Provider     │    │  Branch-per-     │               │
│  │  proxmoxer       │    │  Experiment      │               │
│  └────────┬─────────┘    └──────────────────┘               │
│           │ Proxmox API (clone/push/exec/destroy)           │
│           │                                                 │
│  ┌────────▼─────────┐  ┌─────────────────┐  ┌────────────┐  │
│  │ Worker LXC       │  │ Worker LXC      │  │ Worker LXC │  │
│  │ harlan (P620)    │  │ kovacs (P620)   │  │ poe (P620) │  │
│  │ Gradio UI :7860  │  │ Gradio UI :7860 │  │ Gradio     │  │
│  │ train.py (15min) │  │ train.py (15min)│  │ train.py   │  │
│  └──────────────────┘  └─────────────────┘  └────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CephFS (shared datasets + results)      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

External:
  Developer workstation
    └── VS Code + Copilot agent mode (builds Manager/Worker code)
    └── Gemini CLI / Amazon Q (alternative agent modes)
```

### 6.1 Component Roles

| Component | LXC Type   | GPU? | Purpose                                                                  |
|-----------|------------|------|--------------------------------------------------------------------------|
| Manager   | Persistent | No   | Flask dashboard, AI calls, Proxmox API orchestration, experiment history |
| Forgejo   | Persistent | No   | Git server for versioned experiment code, branch-per-experiment model    |
| Worker    | Ephemeral  | Yes  | Runs mutated `train.py` for 15 minutes, reports metrics, self-destructs  |
| CephFS    | Shared     | —    | Dataset access, logs, checkpoints, experiment artifacts                  |

### 6.2 Hybrid UI Architecture

- **Flask + HTMX** — Central "Ground Control" dashboard. Manages Proxmox API calls, tracks global
  leaderboard, stores all experiment metadata. Runs on Manager LXC (no GPU needed).
- **Gradio** — Per-worker "Lab Interface." Each spawned worker LXC runs a Gradio app on port 7860
  for real-time visualization of loss curves, GPU temperature, memory usage. Ephemeral — born with
  the worker, destroyed with it.
- **IFrame Gallery** — Flask dashboard embeds each active worker's Gradio UI via iframe:
  ```html
  <iframe src="http://192.168.86.x:7860" width="100%" height="500px"></iframe>
  ```
  When Flask spawns a worker on a node, it knows the Gradio app will be at `http://<node-ip>:7860`
  and dynamically adds the card to the dashboard.

---

## 7. The Research Loop

```
1. HYPOTHESIZE
   Manager sends experiment history + current train.py + program.md to AI provider.
   AI proposes a code mutation with one-line hypothesis comment.
   ↓
2. VALIDATE
   Manager syntax-checks (ast.parse) and policy-checks the mutation.
   Reject malformed or forbidden code (shell side effects, package installs, network calls).
   ↓
3. MUTATE
   Manager commits new train.py to experiment branch in Forgejo.
   Branch name: experiment-<YYYYMMDD-HHMMSS>-<hypothesis-slug>
   ↓
4. EXECUTE
   Manager uses Proxmox API to:
     a. Clone "Gold Template" LXC to an idle P620 node
     b. Push train.py into the worker via pct push (or CephFS shared path)
     c. Start the 15-minute training burst via pct exec
   ↓
5. EVALUATE
   Worker trains for 15 minutes (or 500 steps, whichever first).
   Worker POSTs structured results JSON to Manager /api/results.
   Gradio UI shows live loss curves on the worker.
   ↓
6. SELECT
   If val_loss improved → merge experiment branch into "frontier" branch.
   If val_loss regressed or OOM → discard branch, destroy worker.
   ↓
7. COOL DOWN
   3-minute thermal pause before next experiment.
   ↓
   Loop back to step 1.
```

### 7.1 Why 15 Minutes (Not 5)

The original AutoResearch uses 5-minute windows on RTX 3090/H100. On i7-2600 + P620:
- JIT compilation and kernel warm-up: 60–90 seconds
- CPU offloading over PCIe 2.0 adds latency per step
- 5 minutes yields too few iterations for val_loss to stabilize

**Rule:** 15-minute max wall clock. Primary metric is val_loss after **500 training steps**.
If hardware can't complete 500 steps in 15 minutes, the experiment is a failure (code too slow or OOM).

### 7.2 Why 3-Minute Cooldown

OptiPlex 990 SFF chassis was designed for spreadsheets, not sustained matrix multiplication.
Continuous 15-minute training bursts will trigger thermal throttling on both the P620 and i7-2600.
The 3-minute cooldown ensures each experiment starts with the same thermal headroom, keeping
scientific results consistent across runs.

### 7.3 Worker Results JSON Schema

```json
{
  "experiment_id": "20260601-143022-reduce-layers",
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

## 8. Training Parameters for P620 (2 GB VRAM)

| Setting           | Default (H100)  | P620 (2 GB VRAM) | Notes                                    |
|-------------------|-----------------|------------------|------------------------------------------|
| Dataset           | enwik8          | TinyStories       | Lower entropy, learns faster             |
| Max Seq Len       | 1024            | 128–256           | Fits in 2 GB                             |
| Batch Size        | 128             | 8–16              | Prevents OOM                             |
| Model Depth       | 8–12 layers     | 3–4 layers        | Micro-architecture                       |
| Vocab Size        | 8192            | 1024–2048         | Smaller embedding table                  |
| Experiment Window | 5 min           | 15 min            | Compensates for slower hardware          |
| Step Target       | N/A             | 500 steps         | Normalizes across nodes                  |
| Cool Down         | None            | 3 min             | Thermal management                       |

**CPU offloading strategy:**
- Use DeepSpeed ZeRO Stage 2 or Hugging Face Accelerate to offload optimizer states and gradients
- Consider Unsloth library for 70% VRAM reduction with zero accuracy loss
- The 32 GB system RAM acts as a large pre-fetch buffer for dataset batches from CephFS
- Treat repeated OOM for the same mutation class as a negative learned pattern

---

## 9. AI Provider Strategy

### 9.1 Default Provider: GitHub Models (Copilot path)

- Endpoint: `https://models.inference.ai.azure.com`
- Client: OpenAI-compatible SDK (`openai` Python package)
- Auth: fine-grained GitHub PAT with `models:read` scope only

**Recommended models (as of mid-2026):**

| Model                        | Context | Best For                                       |
|------------------------------|---------|------------------------------------------------|
| `claude-sonnet-4-5`          | 200K    | Primary — large context, strong code reasoning |
| `gpt-4o`                     | 128K    | Secondary — faster iteration cycles            |
| `gpt-4o-mini`                | 128K    | Summarization / compression tasks (cheap)      |
| `meta-llama-3-70b-instruct`  | 128K    | Open-weights alternative                       |

Check current availability: `https://github.com/marketplace/models`

### 9.2 Optional Providers

| Provider     | SDK                   | Context | Notes                                                  |
|--------------|-----------------------|---------|--------------------------------------------------------|
| Gemini API   | `google-generativeai` | 2M      | Largest context; best for very long experiment history |
| Local Ollama | `ollama` / `openai`   | varies  | No API cost; needs AVX-only builds for i7-2600         |

**Gemini advantage:** 2M token context window means the entire experiment history (results.tsv,
git diffs, logs) can be fed in every prompt. Gemini learns the hardware's quirks over weeks, not
just hours — identifying patterns like "every time we increase dropout on the third layer, the
i7-2600 CPU bottlenecks."

### 9.3 Copilot vs Gemini Trade-offs

| Dimension              | Gemini 3 Pro                    | GitHub Copilot / Models          |
|------------------------|---------------------------------|----------------------------------|
| Context window         | 2M tokens                       | 128K–200K (model-dependent)      |
| Long-term memory       | Feed entire history in one shot | Requires chunking/summarization  |
| API access             | `google-generativeai` SDK       | `openai`-compatible, GitHub PAT  |
| Cost model             | Per-token (pay-as-you-go)       | Included in Copilot subscription |
| Best for               | Long research sessions (weeks)  | Interactive development          |

### 9.4 Provider Abstraction (config-swap, not code-swap)

```python
# manager/ai_provider.py
class ResearchModel:
    def generate_mutation(self, history_summary: str, train_code: str, constraints: str) -> str:
        raise NotImplementedError

class GitHubModelsResearchModel(ResearchModel):
    ...

class GeminiResearchModel(ResearchModel):
    ...
```

### 9.5 Multi-Model A/B Testing

Assign different AI models to different P620 nodes to compare which produces better val_loss
improvements on the same hardware:

```python
MODEL_ROTATION = {
    "harlan": "claude-sonnet-4-5",
    "kovacs": "gpt-4o",
    "poe":    "claude-sonnet-4-5",
    "quell":  "gpt-4o",
}

def get_model_for_node(node_name: str) -> str:
    return MODEL_ROTATION.get(node_name, "claude-sonnet-4-5")
```

Track `model_name` in the `experiments` table alongside `val_loss` to analyze which model writes
more hardware-efficient training code for P620 constraints.

### 9.6 Context Window Management

With claude-sonnet-4-5 at 200K tokens, context budget per hypothesis request:

| Item                                  | Est. tokens   | Notes                                       |
|---------------------------------------|---------------|---------------------------------------------|
| System prompt + hardware context      | ~400          | Fixed                                       |
| Current `train.py`                    | ~1,500–3,000  | Grows as code evolves                       |
| Rolling history (last 30 experiments) | ~3,000–6,000  | ~100–200 tokens/experiment (compact format) |
| Summarized older history prefix       | ~600          | Replace oldest runs with summary at >50     |
| Response buffer                       | ~2,048        | For diff + reasoning                        |
| **Total typical**                     | **~8,000–12,000** | Well within 200K window                 |

**Summarization trigger:** When `len(experiments) > 50`, run `summarize_experiment_history()` on
experiments 1–30, store in `MetaInsight` table, clear those rows from main history.

**Rolling window helper:**
```python
def build_history_summary(db_session, max_experiments: int = 30) -> str:
    experiments = (
        db_session.query(Experiment)
        .order_by(Experiment.created_at.desc())
        .limit(max_experiments)
        .all()
    )
    lines = []
    for exp in reversed(experiments):
        outcome = "SUCCESS" if exp.improved else "FAILURE"
        lines.append(
            f"[{exp.id}] {outcome} | val_loss={exp.val_loss:.4f} | "
            f"steps={exp.steps_completed} | model={exp.model_name} | "
            f"hypothesis={exp.hypothesis_slug}"
        )
    return "\n".join(lines)
```

---

## 10. Implementation Code

### 10.1 Manager: ai_brain.py

```python
"""
AI brain module — abstracts the LLM provider.
Swap COPILOT_MODEL env var to change models without touching other code.
Supported via GitHub Models API: gpt-4o, gpt-4o-mini, claude-sonnet-4-5,
  meta-llama-3-70b-instruct
"""
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
"""

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=os.environ["GITHUB_TOKEN"],
        )
    return _client


def generate_hypothesis(history_summary: str, current_train_py: str) -> str:
    model = os.getenv("COPILOT_MODEL", "claude-sonnet-4-5")
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI research agent optimizing neural network training "
                    "code for a specific legacy hardware cluster. Propose minimal, "
                    "targeted code mutations to train.py based on past experiment results.\n\n"
                    + HARDWARE_CONTEXT
                ),
            },
            {
                "role": "user",
                "content": (
                    f"## Past experiment history (most recent first):\n{history_summary}\n\n"
                    f"## Current train.py (frontier branch):\n```python\n{current_train_py}\n```\n\n"
                    "Propose a single code mutation. Output the diff only. "
                    "Start your response with a one-line hypothesis comment."
                ),
            },
        ],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content


def summarize_experiment_history(full_history: str) -> str:
    """Compress old experiment logs. Use cheap model for this housekeeping task."""
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarize the following experiment results into bullet-point "
                    "learnings about what works and what fails on this specific hardware "
                    "(i7-2600, P620 2GB VRAM, PCIe 2.0 bus, 32GB DDR3). "
                    "Focus on patterns, not individual runs. Max 400 words.\n\n"
                    + full_history
                ),
            }
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content
```

**To switch to Gemini:** use `google-generativeai` SDK instead:

```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-3-pro')

def generate_hypothesis(history_logs: str) -> str:
    prompt = f"""Review these past experiments: {history_logs}
    Hardware: Dell OptiPlex 990, i7-2600, 32GB DDR3, NVIDIA P620 (2GB GDDR5 Pascal).
    Constraint: 2GB VRAM max for active weights. Use 32GB system RAM for gradient offloading.
    Objective: Propose a code change to train.py that improves val_loss.
    Prioritize micro-architectures (3-4 layers, small embedding dims)."""
    response = model.generate_content(prompt)
    return response.text
```

### 10.2 AI Output Validation

Before applying any AI-generated diff to `train.py`:

```python
import ast

def validate_python(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        app.logger.warning(f"AI generated invalid Python: {e}")
        return False
```

Also check for forbidden patterns: shell side effects, package installs, network calls outside
allowed endpoints (Manager IP and Forgejo IP only).

### 10.3 Manager: Proxmox Spawning Logic

```python
from proxmoxer import ProxmoxAPI

proxmox = ProxmoxAPI(
    "192.168.86.11",
    user="root@pam",
    token_id="aasr-manager",
    token_secret="<token>",
    verify_ssl=False
)

GOLD_TEMPLATE_ID = 9100
GPU_NODES = {
    "harlan": "192.168.86.11",
    "kovacs": "192.168.86.12",
    "poe":    "192.168.86.13",
    "quell":  "192.168.86.16",
}

def find_idle_gpu_node():
    for node_name in GPU_NODES:
        containers = proxmox.nodes(node_name).lxc.get()
        active = [c for c in containers if c['name'].startswith('aasr-worker')]
        if not active:
            return node_name
    return None

def run_experiment(node_name, experiment_id):
    vmid = 9200 + experiment_id
    proxmox.nodes(node_name).lxc.post(
        vmid=vmid,
        clone=GOLD_TEMPLATE_ID,
        hostname=f"aasr-worker-{experiment_id}",
        target=node_name
    )
    proxmox.nodes(node_name).lxc(vmid).status.start.post()
    proxmox.nodes(node_name).lxc(vmid).exec.post(
        command=["bash", "/app/start.sh"]
    )
    return vmid

def cleanup_worker(node_name, vmid):
    proxmox.nodes(node_name).lxc(vmid).status.stop.post()
    proxmox.nodes(node_name).lxc(vmid).delete(purge=1)
```

### 10.4 Manager: Key Flask Routes

```python
from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/")
def dashboard():
    # Cluster grid, leaderboard, live console, audit log
    ...

@app.route("/node-status")
def node_status():
    # HTMX fragment: node temps, GPU idle/busy — polled every 5s
    ...

@app.route("/start-research", methods=["POST"])
def start_research():
    # Trigger new experiment cycle
    ...

@app.route("/kill/<int:vmid>", methods=["POST"])
def kill_worker(vmid):
    # Emergency destroy of a rogue worker via pct destroy
    ...

@app.route("/api/results", methods=["POST"])
def receive_results():
    # Worker callback with final metrics JSON
    data = request.get_json()
    # Store in DB, compare against frontier, merge or discard
    ...

@app.route("/config/model", methods=["POST"])
def set_model():
    allowed = {"claude-sonnet-4-5", "gpt-4o", "gpt-4o-mini", "meta-llama-3-70b-instruct"}
    model = request.form["model"]
    if model not in allowed:
        return "Invalid model", 400
    os.environ["COPILOT_MODEL"] = model
    return f'<span class="badge">Model: {model}</span>'
```

**HTMX live polling (no JavaScript frameworks needed):**
```html
<!-- Poll node status every 5 seconds -->
<div hx-get="/node-status" hx-trigger="every 5s">
  Loading cluster status...
</div>
```

**Model selector HTMX fragment:**
```html
<form hx-post="/config/model" hx-target="#model-status">
  <select name="model">
    <option value="claude-sonnet-4-5">claude-sonnet-4-5 (200K)</option>
    <option value="gpt-4o">gpt-4o (128K, faster)</option>
    <option value="gpt-4o-mini">gpt-4o-mini (128K, cheapest)</option>
    <option value="meta-llama-3-70b-instruct">llama-3-70b (open weights)</option>
  </select>
  <button type="submit">Apply</button>
</form>
<div id="model-status"></div>
```

### 10.5 Manager: requirements.txt

```text
flask>=3.0
flask-sqlalchemy>=3.1
openai>=1.30
proxmoxer>=2.0
requests>=2.31
python-dotenv>=1.0
```

### 10.6 Manager: .env (never committed)

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
COPILOT_MODEL=claude-sonnet-4-5
PROXMOX_HOST=192.168.86.11
PROXMOX_TOKEN_ID=aasr-manager
PROXMOX_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
FORGEJO_URL=http://192.168.86.201:3000
FORGEJO_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MANAGER_IP=192.168.86.202
```

### 10.7 Worker: Gold Template LXC Config

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

### 10.8 Worker: Boot Script (start.sh)

```bash
#!/bin/bash
cd /app
uv run train.py --max-time 900 &
uv run gradio_monitor.py &
wait
curl -X POST http://192.168.86.202/api/results \
  -H "Content-Type: application/json" \
  -d @/app/results.json
```

### 10.9 VS Code Copilot Agent Mode (Development Workflow)

While the Manager LXC uses GitHub Models API for automated research cycles, the developer uses
VS Code Copilot agent mode to build the system itself:

```
Developer → VS Code + Copilot agent → edits Flask/proxmoxer code
                                    → pushes to Forgejo
                                    → Manager runs next experiment cycle
                                    → results feed back into Copilot context
```

**Useful agent mode prompts:**
```
"Using proxmoxer, write a function that finds the first P620 node
(harlan .11, kovacs .12, poe .13, quell .16) with no active aasr-worker
LXC and returns the node name and IP."

"Write the LXC .conf GPU passthrough stanzas for an NVIDIA Quadro P620
on Proxmox 8.4 with kernel 6.8.12-18-pve."

"Write a Flask route /api/results that receives val_loss, steps_completed,
experiment_id from a worker LXC and updates the SQLAlchemy Experiment table,
then triggers a Forgejo API merge if val_loss improved."
```

**`gh copilot` CLI for quick tasks:**
```bash
gh extension install github/gh-copilot
gh copilot suggest "proxmox pct clone command to clone VMID 9100 to VMID 9201 targeting node kovacs"
gh copilot explain "proxmoxer.backends.https.AuthenticationError: 401"
```

---

## 11. Git Model: Branch-per-Experiment

```
main ──────────────────────────────────────────────►  (stable, human-controlled)
  │
  ├── frontier ──────────┬──────────┬──────────────►  (best machine-evolved code)
  │                      │          │
  │   experiment-001 ────┘          │
  │   (merged: improved val_loss)   │
  │                                 │
  │   experiment-002 ───── X        │
  │   (discarded: regression)       │
  │                                 │
  │   experiment-003 ───────────────┘
  │   (merged: improved val_loss)
```

**Promotion rules:**
1. Mutation must pass syntax and policy checks
2. Run must complete with valid metrics payload
3. val_loss must improve relative to frontier baseline
4. Only then merge to frontier and delete experiment branch

Workers never touch git directly — the Manager drives all Forgejo API calls.

**Forgejo API actions used by Manager:**

| Action | API Call | Result |
|--------|----------|--------|
| New hypothesis | `POST /api/v1/repos/{owner}/{repo}/branches` | New sandbox branch created |
| Inject code | `PUT /api/v1/repos/{owner}/{repo}/contents/{filepath}` | Mutated train.py committed |
| Success | `POST /api/v1/repos/{owner}/{repo}/pulls` | PR opened and auto-merged into frontier |

---

## 12. Core Service LXC Setup

### 12.1 Forgejo Git Server (192.168.86.201)

```bash
pct create 201 local:vztmpl/debian-13-standard_13.0-1_amd64.tar.zst \
  --hostname forgejo \
  --cores 1 --memory 1024 --swap 512 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.86.201/23,gw=192.168.86.1 \
  --nameserver 192.168.86.3 \
  --mp0 /mnt/pve/cephfs/aasr/forgejo,mp=/var/lib/gitea

pct start 201
pct exec 201 -- bash -c "
  apt-get update && apt-get install -y wget git
  wget -O /tmp/forgejo.deb https://codeberg.org/forgejo/forgejo/releases/download/v11/forgejo_11-linux-amd64.deb
  dpkg -i /tmp/forgejo.deb
  systemctl enable --now forgejo
"
```

Post-setup: create API token for Flask orchestrator; create `autoresearch` repo with `main` and
`frontier` branches.

### 12.2 Manager LXC (192.168.86.202)

- OS: Debian 13, 2 vCPU, 4 GB RAM
- CephFS mount: `/mnt/data` for shared datasets and results
- Proxmox API token: needs `PVEVMAdmin` permissions to clone/start/stop/destroy LXCs

### 12.3 Gold Template Worker LXC

- OS: Debian 13, 4 vCPU, 28 GB RAM
- GPU passthrough: NVIDIA P620 device nodes (see LXC config in §10.7)
- Pre-installed: NVIDIA production drivers (match host kernel), `uv`, `git`, `gradio`,
  PyTorch (AVX-only compiled)
- CephFS mount: `/data` (read-only for workers)

---

## 13. Manager Database Schema

```sql
-- experiments
id, created_at, provider, model_name, node_name, vmid,
branch_name, hypothesis_slug, hypothesis_summary, status

-- results
experiment_id, steps_completed, duration_seconds,
val_loss, val_bpb, peak_vram_mb, peak_ram_mb,
temperature_max_c, success_flag

-- insights (compressed history summaries)
generated_at, summary_text, applies_to_hardware, source_run_range

-- artifacts
experiment_id, log_path, plot_path, diff_path, checkpoint_path
```

---

## 14. Security and Isolation

- Worker LXC network egress restricted to Manager (192.168.86.202) and Forgejo (192.168.86.201)
  only — no internet access
- Worker git credentials scoped to experiment branches only — no write access to `main` or `frontier`
- Manager Proxmox API token scoped to `PVEVMAdmin` for LXC lifecycle only — workers have no
  Proxmox API access
- AI token (`GITHUB_TOKEN`) scoped to `models:read` only — no repo write access
- AI output validated before execution: syntax parse → forbidden API/path check → optional static lint
- Strict CPU pinning (4 cores) and memory caps (28 GB) per worker — prevents rogue experiment from
  crashing host
- Fresh LXC clone for every experiment — no state leaks between runs ("Clean Room" benefit)
- Every mutation logged with diff, reasoning, and metrics in Flask DB and Forgejo commit history
  (Traceable AI Development Platform — useful for SOC2/audit trail purposes)
- `GITHUB_TOKEN` stored in `.env` on Manager LXC with `chmod 600` — never embedded in source code

---

## 15. Phase Plan with Acceptance Criteria

### Phase 1: Core Services
- Deploy Forgejo LXC (192.168.86.201) and Manager LXC (192.168.86.202)
- **Acceptance:** Manager can create branch in Forgejo via API; Manager DB is writable and queryable

### Phase 2: Gold Worker Template
- Build and snapshot worker template with NVIDIA drivers, uv, AVX-only PyTorch, Gradio
- **Acceptance:** `nvidia-smi` works inside worker clone; train bootstrap script executes without
  manual fixes

### Phase 3: Single Manual Experiment
- Run one mutation end-to-end with manual trigger
- **Acceptance:** metrics callback received and stored; worker destroyed after run

### Phase 4: Automated Loop
- Enable repeated experiment loop with cooldown
- **Acceptance:** at least 5 consecutive runs complete; no orphan worker containers

### Phase 5: Promotion and Leaderboard
- Wire merge/discard logic and dashboard views
- **Acceptance:** successful run merges into frontier automatically; leaderboard updates from DB
  without manual refresh

### Phase 6: Parallel Workers
- Add controlled parallel experiments across P620 nodes
- **Acceptance:** scheduler avoids node collisions; aggregate throughput improves without thermal
  instability

---

## 16. Quick Start Checklist

1. Build Forgejo LXC and create repository with `main` and `frontier` branches
2. Build Manager LXC with Flask, SQLAlchemy, proxmoxer, and OpenAI SDK
3. Configure GitHub token with `models:read` and verify inference call works
4. Build worker gold template and verify GPU visibility in LXC clone (`nvidia-smi`)
5. Run one manual mutation cycle and confirm artifact capture in DB
6. Enable automated loop and monitor first 10 runs

---

## 17. Implementation Order

1. **Forgejo LXC** — Git server on CephFS (§12.1)
2. **Gold Template LXC** — Worker template with NVIDIA drivers, uv, AVX-only PyTorch, Gradio (§12.3)
3. **Manual GPU test** — Clone template on harlan, verify P620 accessible in LXC, run `nvidia-smi`
4. **Manager LXC** — Flask app with proxmoxer, basic spawn/destroy cycle (§12.2)
5. **AI integration** — Wire `ai_brain.py`, test `generate_hypothesis()` interactively
6. **Dashboard** — HTMX live updates, leaderboard, model selector, audit log
7. **Parallel experiments** — Spawn workers on multiple P620 nodes with model rotation (§9.5)
8. **Blog articles** — Document the build on mcgarrah.org (§20)

---

## 18. K8s Coexistence

If the K8s cluster from `k8s-proxmox` is deployed simultaneously, AASR and K8s workers compete
for the same nodes and resources.

Options:
1. **Time-share:** Run AASR experiments during off-hours when K8s is idle
2. **Dedicated nodes:** Reserve 2 P620 nodes for AASR, 2 for K8s workers
3. **Sequential:** Deploy AASR first as standalone, add K8s later

**Recommendation:** Start with AASR standalone. Both projects share the same Ceph storage and
network infrastructure.

---

## 19. Repository Layout

```text
aasr/
  manager/
    app.py                  # Flask + HTMX dashboard
    ai_brain.py             # Provider abstraction (GitHub Models / Gemini)
    scheduler.py            # Experiment orchestration loop
    evaluator.py            # val_loss comparison and frontier promotion
    models.py               # SQLAlchemy schema
    templates/              # HTMX dashboard templates
  worker/
    train.py                # Training script (mutation sandbox)
    prepare.py              # TinyStories data pipeline
    gradio_monitor.py       # Live visualization (loss curves, GPU stats)
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

## 20. Open Questions

- [ ] Exact NVIDIA host + container driver version combination for Proxmox 8.4 kernel (6.8.12-18-pve)
- [ ] Whether `pct push` / `pct exec` is sufficient long-term or SSH-based orchestration is more reliable
- [ ] CephFS read amplification impact on parallel worker throughput during training
- [ ] GitHub Models rate limits per hour — max experiment frequency before throttling
- [ ] Whether `claude-sonnet-4-5` remains consistently available via GitHub Models
- [ ] Token cost accounting: monitor via `gh api user/copilot_usage`
- [ ] Whether K600 nodes (edgar) deliver enough signal to justify maintenance overhead
- [ ] Thermal telemetry source — can Proxmox sensor data be read from within an LXC, or must
      Manager query host API?
- [ ] Parallel experiment git strategy — linear frontier vs. branching tournament selection
- [ ] Streaming responses: GitHub Models supports `stream=True` — consider surfacing reasoning
      tokens in real-time on dashboard
- [ ] Dynamic memory balancing between system RAM and GPU VRAM across different models on older
      hardware, especially with multiple AI providers in the mix
- [ ] Security of autonomously running AI-generated code on the cluster, even with LXC isolation —
      review best practices periodically

---

## 21. Blog Article Series

| Part | Topic                       | Angle                                                         |
|------|-----------------------------|---------------------------------------------------------------|
| 1    | Architecture                | Manager-Worker pattern on legacy hardware                     |
| 2    | GPU Passthrough in LXC      | NVIDIA P620 on Proxmox with ephemeral containers              |
| 3    | The Evolutionary Git Loop   | AutoResearch + Forgejo + Flask orchestration                  |
| 4    | Training on 2 GB VRAM       | CPU offloading, micro-architectures, hardware-aware optimization |
| 5    | AI Provider Abstraction     | GitHub Models, Gemini, and local models via one interface     |
| 6    | Results                     | What the AI researcher actually discovered                    |

See `AME-GPT-EXPLORATION.md` for the companion AME series (GPT deep dive, 5 additional articles).

---

## 22. Related Files

| File | Purpose |
|------|---------|
| `AME-GPT-EXPLORATION.md` | AME companion project — GPT architecture deep dive |
| `2026-07-01-aasr-project-series-overview.md` | Series index article — five-part outline with key decisions per part |
| `2026-07-01-aasr-proxmox-overview.md` | Article draft — AASR Part 1 prose (nearest to publishable) |
