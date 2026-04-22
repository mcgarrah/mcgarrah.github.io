---
title: "Autonomous AI Scientific Research: Building an AI Agent Cluster on Proxmox"
layout: post
categories: [ai, homelab, research]
tags: [proxmox, gemini, machine-learning, aarc, ceph, automation]
excerpt: "Automating the machine learning research lifecycle on a distributed cluster of legacy hardware using Proxmox, Gemini 3 Pro's 2M context window, and an evolutionary Git loop."
---

The idea of AI automating scientific research sounds like something reserved for hyperscalers with massive H100 clusters. But what if you could orchestrate a miniature version of this on 14-year-old enterprise desktops? 

This project is the Autonomous AI Research Cluster (AARC). The objective is to automate the machine learning research lifecycle on a distributed cluster of legacy hardware, using AI agents to hypothesize, code, and validate architectural improvements. It demonstrates proficiency in both Platform Engineering and Data Science constraints.

<!-- excerpt-end -->

## The Core Advantage: Gemini's 2M Context Window

The secret sauce making this possible isn't my hardware—it's Gemini's massive 2M token context window. In a typical AI coding workflow, you are severely limited by how much historical context you can feed the model. 

When automating an evolutionary research loop, the AI needs to "remember" what it tried 10 iterations ago, why it failed, and what the code looked like at that exact moment. With 2M tokens, I can feed the central Orchestrator the *entire* Git history of the experiment, all previous loss curves, and the full codebase simultaneously. It acts as a long-term memory buffer for scientific reasoning.

## The Hardware Reality: The AlteredCarbon Cluster

This system runs on my "AlteredCarbon" cluster. As a refresher, this isn't exactly modern silicon:

* **Compute Fleet:** 6x Dell OptiPlex 990 nodes (Intel i7-2600 Sandy Bridge, 32GB DDR3 RAM each).
* **Accelerators:** NVIDIA Quadro P620s (2GB GDDR5) on 4 nodes, and Quadro K600s on the remaining two.
* **Storage:** CephFS shared storage across the cluster (Reef 18.2.7), providing a persistent layer for training data and experiment metadata.
* **Network:** Dual-network architecture separating public LXC traffic (192.168.86.0/23) from the Ceph replication backbone (10.10.10.0/23).

Running AI research on 2GB of VRAM and CPUs that lack AVX2 instruction sets requires some serious platform engineering.

## Software & Orchestration Architecture

To map the AI's high-level reasoning to this hardware-constrained execution environment, I am using a strict **Manager-Worker** pattern.

### 1. Central Manager (The Orchestrator)
This is a persistent, long-lived Debian LXC running on Proxmox.
* **Stack:** Flask + HTMX for the observation dashboard, Flask-SQLAlchemy for tracking experiment metadata.
* **Cluster Management:** The `proxmoxer` Python library is used to dynamically clone and destroy worker LXCs via the Proxmox API.
* **Git Server:** A local Forgejo (Gitea fork) running in a "Core Service" LXC manages the versioned scientific history.
* **The Brain:** Gemini 3 Pro via the Python SDK, using its context window to hypothesize new architectures.

### 2. Worker Nodes (The Laboratories)
These are ephemeral, "Gold Template" LXCs spawned for each individual experiment.
* **Stack:** Gradio for real-time visualization of loss curves, wrapped around a standard `train.py` script.
* **Resources:** PCIe passthrough maps the Quadro GPUs into the containers. Memory offloads directly to the 32GB system RAM.

## The "Self-Improvement" Research Loop

The system operates on an automated "Evolutionary Git Loop":

1. **Hypothesize:** The Manager (Gemini 3 Pro) reviews past experiment results from the database, analyzes the current `train.py`, and proposes a code mutation.
2. **Mutate:** The Manager pushes the new code to a dedicated experiment branch in Forgejo.
3. **Execute:** The Manager uses `proxmoxer` to clone a fresh worker LXC on an idle OptiPlex node and triggers a training burst.
4. **Evaluate:** The worker trains for a strict **15-minute window** (extended for legacy hardware). It streams validation loss and metrics back to the Manager.
5. **Selection:** If the metrics improve over the baseline, the code is merged into the "Frontier" branch. If it fails, the LXC is destroyed, and the change is rolled back.

## Homelab Engineering Constraints & Solutions

When you build this on enterprise cast-offs, you hit walls quickly. Here is how AARC mitigates the hardware bottlenecks:

### Hardware-Aware Optimization
* **CPU Offloading and VRAM Limits:** With only 2GB of VRAM on the P620s, you cannot hold modern optimizer states in GPU memory. The architecture relies heavily on frameworks like Unsloth or DeepSpeed to offload optimizer states and gradients to the 32GB of system DDR3 RAM. It's slower, but it prevents Out-Of-Memory (OOM) crashes.
* **The AVX Dilemma:** The i7-2600 Sandy Bridge processors lack AVX2 support. If you try to run pre-compiled modern AI binaries (like standard `llama.cpp` releases or specific PyTorch wheels), they will instantly crash with an `Illegal instruction` core dump. Every worker template must use binaries compiled from source specifically mapped to older AVX1 instructions.
* **Thermal Throttling:** These OptiPlex Small Form Factor (SFF) cases were designed for spreadsheets, not sustained matrix multiplication. Continuous training runs will trigger thermal throttling. The Orchestrator enforces a mandatory 3-minute "cool down" phase between tearing down an old worker LXC and spinning up a new one on the same physical node.

### Security & Isolation
* **Least Privilege:** Worker LXCs should have minimal network access, restricted primarily to the Forgejo server for pushing results.
* **Git Isolation:** SSH keys provided to workers must only have write access to specific experiment branches, not the main "Gold" code.
* **Resource Limits:** Strictly limit CPU and RAM per worker to prevent a rogue experiment from crashing the Proxmox host.

### Multi-Model Support
While Gemini 3 Pro acts as the primary "Brain," the system should support local models (Gemma 2, Llama 3) or external tools (Claude Code, Amazon Q) to benchmark performance across different reasoning engines.

## What's Next?

The immediate next step is bootstrapping the Forgejo Git LXC and the Flask Orchestrator LXC on `harlan` or `kovacs`. Once the Proxmox API integration (`proxmoxer`) is successfully cloning the GPU-passthrough templates, the Gemini integration can begin.

I'll be tracking the actual API prompts, success rates, and inevitable hardware failures in follow-up posts.