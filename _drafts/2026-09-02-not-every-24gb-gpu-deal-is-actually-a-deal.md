---
layout: post
title: "Not Every 24GB GPU Deal Is Actually a Deal"
image: /assets/images/og/not-every-24gb-gpu-deal-is-actually-a-deal.png
categories: [homelab, proxmox, ai]
tags: [nvidia, gpu, llm, cuda, proxmox, homelab, hardware]
excerpt: "A GPU upgrade for a Proxmox node that also runs live Ceph OSDs and HA-managed containers isn't the same shopping problem as a GPU upgrade for a gaming PC — the cheapest VRAM per dollar came from a card I ended up rejecting, and the reason why is the actual lesson here."
description: "Working through a real GPU upgrade decision for quell, one of four Proxmox nodes running Quadro P620s on a driver branch NVIDIA has already begun sunsetting. Covers why the RTX 3060 12GB was the obvious starting point, why the tempting 24GB Tesla M40/P40 detour fell apart on closer inspection (power connectors, passive cooling, and a driver-support horizon that's already closing), an external report that validated the P620 fleet's own caution about Proxmox 9.2's kernel breaking Pascal drivers, and the price-per-VRAM-gigabyte math that ruled out the RTX 3090 despite its headline capacity. Ends with the actual decision framework — a two-candidate, price-gated rule — rather than a single answer, since the used GPU market was moving faster than any one number could keep up with."
date: 2026-09-02
last_modified_at: 2026-09-02
seo:
  type: BlogPosting
  date_published: 2026-09-02
  date_modified: 2026-09-02
---

Four of AlteredCarbon's six Proxmox nodes run Quadro P620s on a driver branch NVIDIA has already started sunsetting. That fact — not "I want a bigger GPU" — is what actually kicked off this upgrade decision. One of those four nodes, `quell`, picked up a 750W power supply during an earlier unrelated repair, which left it the one node in the cluster with real headroom for something more capable than a 40W low-profile Pascal card. The question wasn't whether to spend the headroom, it was what to spend it on, for a machine that also happens to run live Ceph OSDs and HA-managed containers — which turns out to change the math more than the GPU spec sheets do.

<!-- excerpt-end -->

## The obvious starting point: RTX 3060 12GB

For local LLM work, VRAM capacity matters more than raw compute — it's what determines which model sizes and quantization levels actually fit without heavy CPU offload. The RTX 3060 12GB is the standout budget pick for exactly that reason: at roughly $260 used, its $21.70/GB beats the 3060 Ti and 4060 (both 8GB, both faster cores, both worse VRAM-per-dollar), it draws about 170W through a standard PCIe 8-pin the PSU already provides, and it stays on CUDA — no ecosystem migration away from the llama.cpp/nvidia-smi workflow already running on the P620 fleet. Ampere also sits comfortably on the current side of NVIDIA's driver-support line, which matters more than it sounds like it should, as the next section covers.

## The tempting detour: 24GB for less than you'd think

Two Tesla cards kept coming up in the same breath: the M40 and the P40, both 24GB, both originally datacenter parts now circulating on the used market at homelab prices. Twenty-four gigabytes for around the same money as a 12GB consumer card is the kind of number that's worth taking seriously rather than dismissing on vibes — so I did.

The M40 didn't survive the first pass. It used to be the actual budget standout at $70-90, but used pricing has since converged with the P40 (~$229 vs. ~$239-330) while staying strictly worse on every axis that matters: Maxwell exited full driver support in October 2025, the P40 is 20-40% faster at the same price, and there's no scenario left where M40 beats P40. Price convergence had quietly erased its only advantage.

The P40 held up longer, and it's the more interesting rejection. Twenty-four gigabytes at a price competitive with the 3060 is a real number, not a trick — but three things it doesn't advertise on the spec sheet stack up against it specifically here:

- **Power.** It needs an EPS-style 8-pin connector, not a standard PCIe 8-pin. `quell`'s PSU has exactly one EPS 4+4, and the CPU already owns it — the P40 needs an EPS-to-PCIe adapter, not a free port.
- **Cooling.** It's a server part with no fan at all, designed for chassis with forced front-to-back airflow. In a normal tower case it needs an aftermarket shroud and fan, and it will thermal-throttle within minutes without one.
- **Operational risk on a shared node.** This is the one that actually decided it. A passively-cooled card that depends on a hand-fitted shroud to avoid throttling is a reasonable risk to accept on a dedicated AI box. It's a different risk profile entirely on a node the Ceph cluster depends on for quorum and OSD availability. The extra 12GB wasn't worth introducing a new failure mode into infrastructure the rest of the cluster relies on.

Rejecting both wasn't a wasted step — it's what makes the eventual decision rule trustworthy instead of just convenient.

## The driver-support boundary is real, and it's not just this cluster's problem

While this was in progress, an independent report surfaced describing the exact failure this cluster has been planning around: a Pascal GPU (a GTX 1080, same generation as the P620) hitting real DKMS build failures against Proxmox 9.2's newer kernel, on the same 580.x driver branch this fleet already runs. The fix was a newer point release within that branch, not a kernel-side workaround — which is good news (Pascal isn't dead on the new kernel, it just needs a current build) but also direct, external confirmation that the caution already built into this cluster's own upgrade plan wasn't overcaution.

Pulling on that thread turned into a broader mapping exercise: NVIDIA has drawn a hard line between Maxwell, Pascal, and Volta (final regular driver already shipped, quarterly security updates only through October 2028) and Turing onward (full support, years of runway left). Every 24GB option under about $500 used — M40, P40, even a modded 22GB Turing-era card discussed below — sits somewhere in or adjacent to that closing window. This is the same risk-management discipline that applies to any hardware refresh or software end-of-life planning at organizational scale: know exactly where a component sits on its vendor's support timeline before it becomes the thing blocking a kernel upgrade, not after.

## What actually beats the 3060's price-per-gigabyte

Assuming Ampere-or-newer as a baseline, three real candidates for "24GB or a better ratio than the 3060" turned up:

- **RTX 3090 (24GB, Ampere)** — the "official" NVIDIA answer, and a worse deal than it looks. At ~$1,050 typical (range $820-1,900), that's $34-44/GB — you're paying a real premium for the capacity, not getting a value pick. AI-driven demand has kept the entire 24GB tier expensive, not just the budget end.
- **RTX 4060 Ti 16GB (Ada Lovelace)** — the actual winner on the metric that matters. Used pricing has apparently settled around $270-320, putting it at $17-20/GB — better than the 3060, on a newer architecture, with no compromises on cooling, power, or video output.
- **A modded RTX 2080 Ti with 22GB of VRAM** (~$499, a specific Hong Kong-based eBay seller, independently covered by several tech outlets) — genuinely close to the 3060's ratio at $22.70/GB, on Turing, which sits on the current side of NVIDIA's support line rather than the closing one, and in a card that keeps its original cooler — no shroud-fitting required. The real caveat: it's an aftermarket VRAM modification with no manufacturer warranty. Interesting enough to research, not worth the reliability risk on a cluster node at this price point.

## The actual decision: a rule, not a number

The used GPU market moved faster than any single "best card" answer could keep up with over the course of this research — prices for the same model shifted between searches performed days apart. Rather than commit to one card at a stale price point, the decision landed on a threshold rule instead:

- RTX 4060 Ti 16GB wins outright if found at $300 or under — newer generation, more VRAM, no compromises.
- Otherwise, the RTX 3060 12GB is still worth it at $250 or under — the price floor where less VRAM is an acceptable trade for zero hassle.
- Neither in range yet: keep watching. There's no GPU installed today, so there's no cost to waiting for the market to come to the threshold instead of the reverse.

## What this actually settles

The interesting output here isn't which card wins — it's that a hardware decision for a node with dual duty (compute plus live infrastructure role) needs an explicit operational-risk axis sitting alongside the usual price and performance ones. Price-per-gigabyte told a clean story right up until cooling, power connectors, and shared-node blast radius entered the picture, and every one of those turned out to matter more than the sticker VRAM number. The same framework — capacity vs. simplicity vs. driver-support horizon vs. what happens to the rest of the system if this specific part fails — is the one that'll get reused when the P620 fleet's own 580.x window actually closes and a real refresh decision has to get made across four nodes at once, not just one.

## Key takeaways

1. **Price-per-gigabyte, not sticker capacity, is the right comparison metric — and it doesn't always favor the biggest card.** The RTX 3090's 24GB looked like the obvious upgrade over 12GB right up until the actual $/GB math showed it costing roughly double what the ratio should predict.
2. **A hardware pick for a shared or production-adjacent node needs an operational-risk axis, not just price and performance.** The Tesla P40 was a legitimate 24GB value on paper — it lost specifically because `quell` also runs Ceph OSDs, not because 24GB stopped mattering.
3. **Driver-support lifecycle is a decision input, not a footnote.** An independent report confirming real DKMS failures on the exact driver branch and kernel combination this cluster is planning to adopt was worth more than any benchmark — verify where a part sits on the vendor's support timeline before assuming a used listing is a safe bet.
4. **A decision framework beats a single answer when the market moves faster than your certainty does.** A price-gated rule with two candidates and a "keep watching" fallback survives stale research better than a single number ever could.
