---
title: "Five Small Tools, One Consistent Baseline, Six Proxmox Nodes"
image: /assets/images/og/pve-node-diagnostic-tooling-baseline.png
layout: post
categories: [proxmox, homelab, monitoring, networking]
tags: [proxmox, lm-sensors, nvme-cli, smartmontools, iperf3, ethtool, homelab, networking, hardware-monitoring]
excerpt: "A quick audit of five standard Linux diagnostic tools across a 6-node Proxmox/Ceph cluster turned up a surprisingly uneven baseline — and a false positive in my own detection script that would have missed it. Here's what each tool is actually for, and why 'probably installed everywhere' isn't good enough on a cluster."
description: "An audit and remediation of five common Linux hardware/network diagnostic packages (lm-sensors, nvme-cli, smartmontools, iperf3, ethtool) across a 6-node homelab Proxmox VE cluster, including a real false-positive bug caught in the detection method itself, and notes on what each tool is for and how to actually use it once installed."
date: 2026-09-11
last_modified_at: 2026-09-11
mermaid: false
seo:
  type: BlogPosting
  date_published: 2026-09-11
  date_modified: 2026-09-11
---

Six nodes, one cluster, built up over time as hardware got added — which means the base OS install on each one has its own slightly different history. Today I went looking for five standard Linux diagnostic tools across all of them: `lm-sensors`, `nvme-cli`, `smartmontools`, `iperf3`, and `ethtool`. None of these are exotic. All five are the kind of thing you reach for during an incident, not something you install in advance — which is exactly the problem, because "I'll install it when I need it" during an actual incident is a bad time to discover apt needs a mirror that's slow tonight, or that the node is air-gapped from the internet in some annoying way.

<!-- excerpt-end -->

## What each tool actually does

**`lm-sensors`** reads temperature, voltage, and fan-speed sensors exposed by the motherboard and CPU. On a cluster, this is the first thing to check when a node starts throttling or a fan starts sounding different — "is CPU package temp actually climbing" is a five-second `sensors` command instead of a guess.

**`nvme-cli`** is the NVMe-specific counterpart to `smartctl` — `nvme list`, `nvme smart-log`, `nvme id-ctrl`. NVMe drives expose a richer health/telemetry model than SATA SMART does (endurance groups, real-time wear percentage, temperature thresholds specific to the controller), and `smartctl` alone doesn't always surface all of it cleanly depending on drive and kernel version.

**`smartmontools`** (the `smartctl` command) is the general SATA/SAS/NVMe SMART health tool — read/reallocated sector counts, power-on hours, temperature history, and the ability to kick off a real self-test (`smartctl -t long /dev/sdX`) rather than just reading passive counters. This is the tool that catches a drive quietly failing before it becomes a Ceph OSD incident.

**`iperf3`** measures actual achievable throughput between two hosts — not "the NIC says 10Gbps," but "here's what two real endpoints actually pushed through the full path: NIC, switch, cabling, MTU, everything." One side runs as a server (`iperf3 -s`), the other connects as a client (`iperf3 -c <server>`). On a Ceph cluster specifically, this is how you'd validate that the storage network is actually delivering the bandwidth the OSDs assume it has, rather than inferring it indirectly from Ceph performance symptoms.

**`ethtool`** reports and configures low-level NIC details — negotiated link speed and duplex, driver and firmware version, ring buffer sizes, offload feature flags, and per-interface error/drop counters (`ethtool -S <iface>`). When a link is technically "up" but something feels wrong — intermittent drops, a speed that doesn't match what was expected — `ethtool` is usually the first place to look before blaming the switch or the cable.

## The actual audit

I checked all six nodes — `poe`, `kovacs`, `quell`, `harlan`, `edgar`, `tanaka` — against all five packages. First pass looked like this:

| Node | lm-sensors | nvme-cli | smartmontools | iperf3 | ethtool |
|---|---|---|---|---|---|
| poe | ❌ | ✅ | ✅ | ❌ | ✅ |
| kovacs | ✅* | ✅ | ✅ | ❌ | ✅ |
| quell | ✅ | ✅ | ✅ | ❌ | ✅ |
| harlan | ❌ | ✅ | ✅ | ❌ | ✅ |
| edgar | ❌ | ✅ | ✅ | ❌ | ✅ |
| tanaka | ✅* | ✅ | ✅ | ❌ | ✅ |

`nvme-cli`, `smartmontools`, and `ethtool` were already consistent everywhere — good sign, means whatever base image or setup process built these nodes originally got the fundamentals right. `iperf3` was missing everywhere, unsurprising since it's a "when you need it" network-testing tool rather than something a base install would include. `lm-sensors` was the genuinely inconsistent one — present on half the nodes, missing on the other half, presumably just from nodes being provisioned at different times with slightly different package sets.

## The false positive that almost hid a real gap

The two `lm-sensors` entries marked with an asterisk above — `kovacs` and `tanaka` — are the actual point of this post. My first detection pass used:

```bash
dpkg -l | grep -qw lm-sensors && echo installed
```

and it reported both as already installed. It was wrong on both counts. `dpkg -l` prints package *descriptions* alongside package names, and something else installed on those two nodes — almost certainly `fancontrol`, which is packaged alongside `lm-sensors` and whose description text mentions it — matched the same grep pattern. `grep -w` guards against partial-word matches (`libsensors-foo` wouldn't trigger it), but it does nothing to stop a match landing in the description column of an unrelated package instead of the name column.

The real check is `dpkg-query`, which lets you ask about one specific package's actual install state instead of grepping a formatted table meant for humans to read:

```bash
dpkg-query -W -f='${Status}' lm-sensors
# install ok installed   <- actually installed
# (empty / error)        <- not installed
```

Running that properly showed `kovacs` and `tanaka` were *not* actually running `lm-sensors` at all — the opposite of what the first pass claimed. Two nodes' worth of missing thermal monitoring would have sat there, invisible, right up until the moment someone actually needed `sensors` output during a real thermal event and got a `command not found` instead.

The lesson isn't really about `dpkg` specifically — it's that a detection script is itself untested code, and "looks plausible" isn't the same as "verified against ground truth." I only caught this because I re-checked the actual `sensors` command output after installing, rather than trusting the installer's exit code and the original grep-based audit together. Worth remembering any time a fleet-wide check reports something suspiciously uniform — that's exactly the shape a false positive takes.

## After

All six nodes now report identically:

```
$ sensors
coretemp-isa-0000
Adapter: ISA adapter
Package id 0:  +40.0°C  (high = +80.0°C, crit = +98.0°C)
```

— no `sensors-detect` step needed; the `coretemp` kernel driver auto-loaded on every node the moment the package landed. `iperf3`, `nvme-cli`, `smartmontools`, and `ethtool` all confirmed present and functional across the same six nodes via `dpkg-query`, not a grep guess.

Small, boring fix. But "boring and verified" beats "assumed and wrong" every time, and this is exactly the kind of gap that's invisible until the one night it isn't.
