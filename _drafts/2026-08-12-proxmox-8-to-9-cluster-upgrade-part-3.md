---
layout: post
title: "Proxmox VE 8 to 9 Cluster Upgrade, Part 3: NVIDIA GPU Drivers, Installed Ahead of the OS Jump"
image: /assets/images/og/proxmox-8-to-9-cluster-upgrade-part-3.png
categories: [homelab, proxmox, infrastructure]
tags: [proxmox, nvidia, gpu, dkms, pascal, kepler, turing, ampere, vgpu, nvenc, jellyfin, cuda, pytorch, machine-learning, homelab, upgrade, cluster, rtd3, pcie]
excerpt: "Real hardware-accelerated Jellyfin transcoding was never actually happening on this cluster — every GPU node was quietly running the open-source nouveau driver instead of NVIDIA's proprietary stack. Fixing that turned into its own post, done deliberately out of sequence: before the Trixie kernel jump, not after, so the driver and the kernel weren't both unproven at the same time."
description: "Part 3 of a five-part series upgrading a 6-node Proxmox VE 8 cluster to Proxmox VE 9. Covers the real state of NVIDIA GPU support across the cluster's two hardware generations (Kepler K600, Pascal P620), the real 580.x driver install — done deliberately ahead of the PVE9 OS upgrade rather than after it — across all four Pascal nodes, including a driver load/unload gotcha that left one GPU stuck in PCI D3cold, a CUDA/PyTorch validation on a second container, confirming Jellyfin's hardware transcode actually works (past a Direct Play false negative), applying the NVENC session-cap unlock for multi-stream transcoding, proving the whole stack survives HA failover across all four GPU nodes, researching an actual physical GPU swap for the dead-end Kepler nodes, root-causing a second D3cold recurrence to NVIDIA's RTD3 power management and fixing it fleet-wide, disproving a plausible-looking PCIe link-speed correlation along the way, and finally a third reboot-triggered failure mode — a device-node boot race that fenced production Jellyfin out of HA entirely — root-caused and fixed fleet-wide with a real reboot test to prove it."
date: 2026-08-12
last_modified_at: 2026-08-14
seo:
  type: BlogPosting
  date_published: 2026-08-12
  date_modified: 2026-08-14
---

**[Part 1](/proxmox-8-to-9-cluster-upgrade-part-1/)** covered pre-flight hardening and building a real backup safety net. **[Part 2](/proxmox-8-to-9-cluster-upgrade-part-2/)** covered the Ceph Reef → Squid upgrade required before the OS jump can even start. This post is a detour from the storage/OS spine of the series, and deliberately so: while auditing GPU passthrough as part of pre-flight, it turned out every GPU node in the cluster was quietly running the open-source `nouveau` driver instead of NVIDIA's proprietary stack — meaning real hardware-accelerated Jellyfin transcoding was never actually happening, upgrade or not. Fixing that for real turned into substantial work on its own, and it got done here, out of sequence, before the Trixie kernel jump rather than after it.

This is that post. **[Part 4](/proxmox-8-to-9-cluster-upgrade-part-4/)** picks up after this one with a full *arr media automation stack, built deliberately ahead of the OS jump — the reason this GPU work needed doing before that stack existed, not after. **Part 5** covers the actual Proxmox OS upgrade to Trixie once all three are done.

<!-- excerpt-end -->

---

## Why This Jumped the Queue

The obvious place to check GPU passthrough is post-upgrade verification, once the new kernel is running — confirm nothing broke, note anything interesting, move on. That was the original plan. It didn't survive contact with the actual audit.

Checking `lspci -k` on every GPU node ahead of time, as part of general pre-flight due diligence, showed **`nouveau`** everywhere — the kernel-builtin, open-source driver — not NVIDIA's proprietary stack. No `nvidia-smi` anywhere, no driver package installed on any of the six nodes. Since `nouveau` ships as part of the mainline Linux kernel rather than a separate out-of-tree module, it has no driver-branch compatibility question at all: it builds and ships with every kernel release automatically, including the Trixie kernel this series is heading toward. Passthrough itself was never actually at risk from the OS upgrade.

But `nouveau` doesn't support NVIDIA's NVENC hardware video encoding — only basic display and limited decode acceleration. So the real question wasn't "will passthrough survive the upgrade," it was "was hardware-accelerated transcoding ever actually working on this hardware, and if not, is it fixable." That's a GPU-driver question, not an OS-upgrade question, and it doesn't depend on which kernel is running today versus after Part 5. Once that became clear, doing the driver work now — against the current, already-proven PVE 8.4 kernel — made more sense than waiting and testing a new driver against a new kernel at the same time. One unknown at a time, not two.

## Current GPU Inventory & Driver Reality

The cluster splits GPU passthrough across two hardware generations:

| Group | Nodes | GPU | Architecture | Compute Capability |
|---|---|---|---|---|
| K600 | `edgar`, `tanaka` | Quadro K600 (GK107GL) | Kepler | 3.0 |
| P620 | `harlan`, `kovacs`, `poe`, `quell` | Quadro P620 (GP107GL) | Pascal | 6.1 |

Confirmed live via `lspci -k` on all six GPU-bearing nodes: both generations were running `nouveau` before any of this work started.

### K600 (Kepler) — the proprietary driver is not viable

`R470` is the last driver branch that ever supported Kepler. It's confirmed broken on kernels newer than roughly `6.10` — it depends on the `follow_pfn` kernel function, which was removed — and PVE9's kernel is well past that. Unofficial community DKMS patches exist but aren't a foundation worth building production tooling on. Kepler's compute capability (3.0) is also long past what any current ML framework supports, so even a successful driver install wouldn't yield anything usable for ML workloads.

**Verdict: `edgar` and `tanaka` stay on `nouveau`.** Fixing this for real means a physical GPU swap, not a driver update — out of scope for the driver work in this post specifically, though not a closed door forever (see below).

**An option flagged for later, not tried here: [vGPU-Unlock-patcher](https://github.com/VGPU-Community-Drivers/vGPU-Unlock-patcher).** Worth being precise about what this actually is, since it's a different track entirely from the `R470`/`nouveau` question above — it doesn't touch the consumer/workstation driver at all. It patches NVIDIA's official **vGPU (GRID)** host driver to add PCI device IDs that aren't on its officially-supported list, by cloning an already-supported GPU's `vgpuConfig.xml` entry onto the unsupported card's device ID. The point of vGPU itself is splitting one physical GPU into multiple virtual GPUs handed out to separate VMs/containers — a genuinely different use case than the passthrough-to-one-container setup this cluster runs today.

Two real reasons this stays a flagged option rather than something attempted on `edgar`/`tanaka` here: it needs NVIDIA's official vGPU/GRID `.run` package as its base, which requires an NVIDIA account (an evaluation license is enough, per the project's docs, but it's a real prerequisite, not a plain download); and every worked example in the project's own README is Pascal-generation or newer (a Turing RTX 2070 Super, a Pascal GTX 1080 Ti/Tesla P40 pair) — nothing confirming a Kepler card specifically still works against a *current* vGPU driver branch. NVIDIA's original GRID K1/K2 vGPU cards were themselves Kepler-based, so Kepler vGPU support existed historically, but whether it's still present in whatever vGPU branch this patcher targets today is an open question, not a confirmed fact — the same "does this old architecture survive into the current driver branch" uncertainty that already ruled out `R470` above. Worth a real evaluation before the next GPU-focused pass on this cluster, but not worth blocking this post on.

### P620 (Pascal) — viable, with a closing window

Pascal's last supported branch is **`580.x`** — the next major NVIDIA driver version drops Pascal support entirely, so this is a closing window, not a long-term solution. Kernel `7.0` (the Trixie target) support on `580.x` was reportedly still "evolving" in community reports as of mid-2026 — another reason to prove the driver against the *current*, known-stable kernel first, rather than adding it to the same unknown pile as the kernel jump itself.

The plan going in: install from NVIDIA's official `.run` file rather than a Debian package (Proxmox's kernel headers don't reliably line up with apt-based DKMS builds), match the host driver version and the LXC's userspace libraries exactly, and canary one node before touching the other three.

## `harlan`: The Canary, and Two Real Gotchas

Done on a brief on-site visit, on the currently-running `6.8.12-41-pve` (PVE 8.4) kernel:

```bash
# 1. Blacklist nouveau — note this alone did NOT prove sufficient, see gotcha below
cat > /etc/modprobe.d/blacklist-nouveau.conf << 'EOF'
blacklist nouveau
options nouveau modeset=0
EOF
update-initramfs -u -k $(uname -r)

# 2. Reboot — nouveau can't be live-unloaded while it's the bound driver, and
#    a real reboot is the only reliable confirmation the blacklist actually took.
reboot

# 3. Confirm nouveau is genuinely gone:
lsmod | grep nouveau                        # should return nothing
lspci -k | grep -A3 'VGA.*NVIDIA'            # "Kernel driver in use" should be absent

# 4. Build prerequisites — correct Proxmox package name, NOT pve-headers-*:
apt-get install -y build-essential dkms proxmox-headers-$(uname -r)

# 5. Download once, cache on CephFS for reuse on the remaining P620 nodes:
mkdir -p /mnt/pve/cephfs/drivers/nvidia
wget -O /mnt/pve/cephfs/drivers/nvidia/NVIDIA-Linux-x86_64-580.142.run \
  https://download.nvidia.com/XFree86/Linux-x86_64/580.142/NVIDIA-Linux-x86_64-580.142.run

# 6. Install with DKMS, so it survives future kernel updates:
chmod +x /mnt/pve/cephfs/drivers/nvidia/NVIDIA-Linux-x86_64-580.142.run
/mnt/pve/cephfs/drivers/nvidia/NVIDIA-Linux-x86_64-580.142.run --dkms --silent --no-x-check --no-nouveau-check

# 7. Verify:
nvidia-smi     # Quadro P620, driver 580.142, CUDA 13.0
dkms status    # nvidia/580.142, <kernel>, x86_64: installed
```

Two real gotchas, both worth flagging so they don't cost anyone else the same troubleshooting time:

**The modprobe blacklist alone didn't stop `nouveau` loading on the first reboot.** Rebooted expecting a clean boot, and `lsmod | grep nouveau` still showed it loaded and bound to the GPU. The blacklist file was present and correctly baked into the initramfs — something else, likely udev auto-loading via a PCI ID match independent of the modprobe.d rule, still pulled it in. The fix that actually worked was simply retrying: an identical second attempt succeeded, with no config change in between. Root cause never fully pinned down in the time available — the working theory is a race between the blacklist's initramfs inclusion and module auto-load ordering on that specific boot. **Lesson: verify with a real reboot and `lsmod`, don't trust the blacklist file's mere presence.** If this recurs, the next things to check are a `nouveau.modeset=0` GRUB boot parameter and whether `nouveau` shows up in `lsinitramfs /boot/initrd.img-$(uname -r) | grep nouveau`.

**`--dkms` silently degrades to a non-DKMS build if the `dkms` package isn't installed first.** The installer doesn't error out — it just builds the module against the currently running kernel only, which won't survive the next kernel update, quietly defeating the entire point of passing `--dkms`. Caught by checking `dkms status` right after the first install attempt and finding it empty despite `nvidia-smi` working fine. Fixed by installing the `dkms` package and simply re-running the identical `.run` command — safe and idempotent, it detects the existing install and adds proper DKMS registration on top.

## LXC Passthrough into Jellyfin

`ct:502` (Jellyfin) is HA-managed and backed entirely by CephFS/Ceph RBD, so relocating it onto the driver-equipped node was fast — no data copy, just stop-on-old/start-on-new:

```bash
ha-manager migrate ct:502 harlan

# The 4 device nodes needed for non-MIG passthrough (nvidia-caps is for
# datacenter-GPU MIG partitioning, not relevant to a P620):
pct set 502 -dev8 /dev/nvidia0,gid=0 -dev9 /dev/nvidiactl,gid=0 \
            -dev10 /dev/nvidia-uvm,gid=0 -dev11 /dev/nvidia-uvm-tools,gid=0

# Config changes need a container reboot — note `pct restart` doesn't exist,
# the actual command is `pct reboot`:
pct reboot 502

# Userspace libraries inside the container must match the host driver
# version EXACTLY — reuse the same .run file, --no-kernel-module since the
# host already has the kernel module loaded and shares it via the device nodes:
pct push 502 /mnt/pve/cephfs/drivers/nvidia/NVIDIA-Linux-x86_64-580.142.run /tmp/nvidia-driver.run
pct exec 502 -- bash -c 'chmod +x /tmp/nvidia-driver.run && /tmp/nvidia-driver.run --no-kernel-module --silent --no-x-check --no-nouveau-check'

pct exec 502 -- nvidia-smi   # confirmed — Quadro P620, driver 580.142, CUDA 13.0
```

Confirmed working end to end: `nvidia-smi` succeeds both on the `harlan` host and inside the unprivileged `ct:502` container, the cluster stayed `HEALTH_OK` throughout (aside from the expected `noout`/`nobackfill` window during harlan's reboot — 3 OSDs live there), and Jellyfin itself came back up and responded normally after the migration/reboot. **Not yet done:** actually configuring Jellyfin's hardware-acceleration setting to use NVENC and running a real transcode — device access confirmed, an end-to-end transcode is a separate, still-open item.

## `kovacs`, `poe`, `quell`: The Rollout, and a Third Gotcha

Same day, repeating the identical host-side sequence on the remaining three P620 nodes, reusing the driver `.run` file already cached on CephFS — no re-download needed on any of them. `poe` and `quell` already had their prerequisite packages installed ahead of time; both came up with `nouveau` cleanly unloaded on the **first** reboot (no repeat of `harlan`'s mystery gotcha), and DKMS registered correctly on the first install attempt, having learned to install `dkms` before running the installer.

`kovacs` hit something new. After a clean install, `dkms status` correctly showed `nvidia/580.142 ... installed`, but `nvidia-smi` failed with *"NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver."* `dmesg` showed the driver had actually loaded successfully once, immediately post-install, then unloaded itself again moments later as part of the installer's own module test cycle — normal so far, matching `harlan` and `poe`. But on `kovacs`, every subsequent `modprobe nvidia` then failed:

```
nvidia 0000:01:00.0: Unable to change power state from D3cold to D0, device inaccessible
NVRM: The NVIDIA GPU 0000:01:00.0 ... has fallen off the bus and is not responding to commands.
nvidia: probe of 0000:01:00.0 failed with error -1
```

`/sys/bus/pci/devices/0000:01:00.0/power/control` was already `on` (runtime autosuspend disabled), so this wasn't a Linux runtime power-management policy problem — the installer's own load/unload cycle had power-gated the device into `D3cold` (fully powered off), and nothing short of hardware could bring it back live from there. The first fix attempted — a live PCI rescan (`echo 1 > .../remove` then `echo 1 > /sys/bus/pci/rescan`), hoping to force a fresh enumeration without a reboot — made things *worse*: the GPU's primary VGA function dropped off the bus entirely and didn't come back, leaving only its separate audio function still enumerated.

**The actual fix: a full node reboot.** Set `noout`/`nobackfill`, rebooted `kovacs` cleanly, and the GPU came back at `D0` with `nvidia-smi` working immediately.

**Lesson, worth remembering for any future node: if a freshly-installed NVIDIA driver's PCI device won't come back after the installer's own load/unload test cycle, don't try to fix it live with a PCI rescan — it can push the device further off the bus. Just reboot the node.** Root cause not fully pinned down — possibly an ACPI `_PS0`/`_PR3` quirk specific to this board's handling of a driver-initiated D3cold→D0 transition, as opposed to a normal boot-time power-up — but a plain reboot reliably recovered it, and none of the other three P620 nodes hit this at all.

## CUDA Validation Beyond `nvidia-smi`: PyTorch on a Dev Container

`nvidia-smi` proves the driver can see the GPU. It doesn't prove a real workload can use it — so the same day as the `kovacs`/`poe`/`quell` rollout, the driver stack got a second, different kind of test: passing the GPU into an existing Python dev container and running an actual CUDA compute workload, not just a device probe.

`nutrition-api-dev` (`ct:602`) already lived on `harlan` — no migration needed, unlike the `ct:502` Jellyfin move in the canary section above. Same passthrough pattern, different device numbers (`dev0` on this container was already in use for a Tailscale `/dev/net/tun` device):

```bash
pct set 602 -dev1 /dev/nvidia0,gid=0 -dev2 /dev/nvidiactl,gid=0 \
            -dev3 /dev/nvidia-uvm,gid=0 -dev4 /dev/nvidia-uvm-tools,gid=0
pct reboot 602

pct push 602 /mnt/pve/cephfs/drivers/nvidia/NVIDIA-Linux-x86_64-580.142.run /tmp/nvidia-driver.run
pct exec 602 -- bash -c 'chmod +x /tmp/nvidia-driver.run && /tmp/nvidia-driver.run --no-kernel-module --silent --no-x-check --no-nouveau-check'

pct exec 602 -- nvidia-smi   # confirmed — Quadro P620, driver 580.142, CUDA 13.0
```

That much matched the Jellyfin pattern exactly. The interesting part started once an actual ML framework got involved.

**A plain `pip install torch` installs a build with no kernels for this GPU at all.** It installs cleanly, `torch.cuda.is_available()` even returns `True`, and the GPU is correctly identified as a Quadro P620 — but the moment a tensor actually touches the device, it fails:

```
torch.AcceleratorError: CUDA error: no kernel image is available for execution on the device
```

The default PyPI wheel (`torch==2.13.0+cu130` as of this writing) only ships compiled kernels for `sm_75` and newer — Turing and later. Pascal's `sm_61` isn't in that list. This is a second, independent instance of the same "closing window" caveat flagged earlier in this post for the driver branch itself: NVIDIA is dropping Pascal after `580.x`, and separately, PyTorch's own default wheel has already dropped Pascal *kernels* to keep the package smaller — two different projects, on two different timelines, arriving at the same conclusion about this generation of hardware. Device access working and a specific framework's default build supporting this specific GPU's compute capability are two separate questions — `nvidia-smi` only answers the first one.

The fix: an explicit older CUDA-runtime build that still includes Pascal kernels. `torch==2.8.0` built against CUDA 12.6 (the `cu126` index, not the bare default index) still ships `sm_61`:

```bash
python3 -m venv /root/ml-venv
/root/ml-venv/bin/pip install --no-cache-dir torch==2.8.0 --index-url https://download.pytorch.org/whl/cu126
```

That build correctly ran a real GPU workload — a 2048×2048 matrix multiply on the device, not just a device query:

```python
import torch
torch.cuda.is_available()                    # True
torch.cuda.get_device_name(0)                # 'Quadro P620'
torch.cuda.get_device_capability(0)           # (6, 1)
a = torch.rand(2048, 2048, device='cuda')
b = torch.rand(2048, 2048, device='cuda')
(a @ b).sum().item()                          # real number back — GPU matmul confirmed working
```

One more small, practical gotcha along the way: `nutrition-api-dev`'s rootfs is only 30G, and two large CUDA-bundled torch downloads (~2GB+ each, before the pip cache is counted) filled it to 100% mid-install, failing with a plain `OSError: No space left on device`. `pip cache purge` recovered enough room to finish the second install; the rootfs was then grown live afterward — `pct resize 602 rootfs +10G`, no reboot required for an online ext4 grow — to leave real headroom for the packages (`numpy`, etc.) an actual ML workflow will need beyond `torch` itself.

## Getting a Real Transcode Out of Jellyfin: A False Negative First

Device access is not the same claim as "Jellyfin actually uses the GPU." Closing that gap surfaced two more things worth writing down, because the first attempt at testing it looked like a failure and wasn't.

**Jellyfin's own hardware-acceleration setting was still off**, separate from anything the driver install touches: `/etc/jellyfin/encoding.xml` had `<HardwareAccelerationType>none</HardwareAccelerationType>` even with `nvidia-smi` working cleanly inside the container. Backed up the file, flipped it to `nvenc`, added `hevc`/`mpeg2video`/`vp9` to the existing `h264`/`vc1` hardware-decoding codec list, restarted the service.

**The first real-world test then showed *zero* GPU activity — with `nvidia-smi` watched live, in real time, during an actual, actively-streaming session.** Played a file from an Android phone; the connection to Jellyfin was unmistakably real (`ss -tn` showed a large, actively-draining send queue), but the encoder and decoder engines sat at a flat 0% the entire time. The cause wasn't a broken setup — it was the Android app's "Auto" quality setting correctly choosing **Direct Play**, since the phone could decode the source file's 1080p H.264 natively. Direct Play sends the raw file straight through; no `ffmpeg`, no GPU, no transcode of any kind happens. Forcing a specific lower quality from the player's in-stream quality selector — rather than leaving it on Auto — is what actually triggers a server-side transcode.

That one change flipped `nvidia-smi` from flat zero to real numbers instantly: **37% GPU, 59% encoder, 77% decoder, GPU memory 0 → 77MiB.** Real hardware transcode, single stream, confirmed live.

**Lesson: a stream playing successfully proves nothing about whether the GPU was involved.** Confirming hardware transcode means confirming a transcode actually happened — checking that the client's quality setting forced one, not just that video showed up on screen.

## The Concurrent-Stream Problem: Nvidia's NVENC Session Cap, Unlocked

With single-stream transcoding confirmed working, this was the moment to actually apply the patch flagged earlier rather than leave it as a future item. Nvidia enforces an artificial cap on consumer- and workstation-grade cards — the P620 included — of roughly 2-3 simultaneous hardware encoding sessions, regardless of how much headroom the GPU actually has. One transcode at a time is fine; a second household member starting a second stream is exactly the scenario this cap exists to block on non-datacenter hardware.

[**keylase/nvidia-patch**](https://github.com/keylase/nvidia-patch) removes that cap by patching `libnvidia-encode.so` directly — a completely different project and mechanism from the vGPU-Unlock-patcher option noted above for the K600s. Where vGPU unlock is about splitting one GPU across multiple *VMs*, this is about removing a session-count limit within a single install — exactly the constraint that matters for one P620 serving more than one Jellyfin transcode from one container. Worth being precise about the terminology too: the cap and this patch are specifically about **NVENC (encode)** sessions. Jellyfin's hardware transcode pipeline decodes with NVDEC and re-encodes with NVENC, and it's the encode side Nvidia artificially limits, not decode.

The project's own version table lists driver `580.142` — the exact version already installed on all four P620 nodes — as confirmed supported, checked directly (`patch.sh -c 580.142` → `SUPPORTED`) before touching anything. **One detail that matters: the patch was applied inside `ct:502`, not on the `harlan` host.** The container has its own copy of the userspace NVIDIA libraries — installed earlier via `--no-kernel-module` — and that's the specific copy `jellyfin-ffmpeg` actually links against when it spawns a transcode. Patching the host's copy would have patched a library nothing on this box actually uses.

```bash
pct exec 502 -- curl -sSL https://raw.githubusercontent.com/keylase/nvidia-patch/master/patch.sh -o /tmp/nvidia-patch.sh
pct exec 502 -- chmod +x /tmp/nvidia-patch.sh
pct exec 502 -- /tmp/nvidia-patch.sh -c 580.142   # SUPPORTED
pct exec 502 -- /tmp/nvidia-patch.sh              # backs up, patches in place
```

No kernel module rebuild, no DKMS interaction, no Jellyfin restart even needed — `ffmpeg` is a fresh process per transcode, so the very next stream picks up the patched library automatically.

**Verified functionally, not just "the script exited 0":** launched four concurrent `h264_nvenc` encode sessions by hand against a real media file. All four completed cleanly with no session-cap errors, and `nvidia-smi` caught a genuine `100% encoder` spike mid-test. Worth being honest about the limits of this test, though: it wasn't a controlled before/after — confirming a *pre-patch* failure at four sessions would have meant reverting first and re-running, and that step got skipped. Four clean concurrent sessions comfortably clearing the well-documented stock limit (~3) is good evidence the patch is doing its job, not formal proof via a captured baseline failure. The `-r` rollback flag restores the pre-patch library from `/opt/nvidia/libnvidia-encode-backup/` if this ever needs undoing.

**Scope note for later:** this patch lives per-container, not per-host. If GPU passthrough gets wired into a container on `kovacs`, `poe`, or `quell` down the line, that container's driver install will include an unpatched `libnvidia-encode.so` of its own — this step doesn't travel with the host driver and would need repeating there too.

## Proving HA Actually Means HA: Failover Tested on All Four Nodes

`ct:502` was already sitting in HA group `P620` — `nodes quell,kovacs,poe,harlan`, unrestricted, no-failback disabled — before any of the driver work in this post even started. That configuration made it *eligible* to run on any of the four P620 nodes. It said nothing about whether it would actually *work* once it landed somewhere other than `harlan`, where every driver install and every test up to this point had happened. Eligible and functional are two different claims, and only one of them had been tested.

Checked device consistency across all four nodes first, since the container's passthrough config (`dev8`-`dev11`) references fixed `/dev/nvidiaN` paths with no per-node variation built in: identical major/minor numbers everywhere — `/dev/nvidia0` at `195:0`, `/dev/nvidiactl` at `195:255`, `/dev/nvidia-uvm` at `234:0`, `/dev/nvidia-uvm-tools` at `234:1` — on `harlan`, `kovacs`, `poe`, and `quell` alike. That meant the same container config should, in principle, work unmodified on any of them.

Then actually proved it, rather than trusting the principle: walked `ct:502` through all three remaining nodes with `ha-manager migrate`, testing on each stop before moving to the next.

```bash
ha-manager migrate ct:502 kovacs   # then poe, then quell, then back to harlan
```

On every node: `nvidia-smi` saw the GPU correctly, a `sha256sum` check confirmed the NVENC-patched `libnvidia-encode.so` was still the active copy (not the original backup) — because the patch lives inside the container's own CephFS/RBD-backed rootfs, it travels with the container automatically, no per-node reapplication required — and a real `h264_nvenc` transcode ran successfully every time.

**One thing looked like a real problem and turned out not to be.** Checking the container's boot history (`journalctl --list-boots`, which persists across node moves since it's stored in the container's own rootfs, not the host) initially looked like three unexplained reboots had happened back-to-back on `quell` alone — the kind of flapping that would suggest something was actually wrong there. Cross-checking the timestamps against the full boot list resolved it: it was exactly one fresh boot per migration hop — `harlan→kovacs`, `kovacs→poe`, `poe→quell` — each showing up in the same persistent log because the log itself moved with the container. Three hops, three boots, nothing anomalous once read correctly. Proxmox's LXC HA relocation is stop-on-old/start-on-new, not a live migration, so a fresh boot per hop is simply what's supposed to happen. A `ResourceNotFoundException: Configuration with key network not found` also showed up in the first second after every single boot — an HTTP request racing Jellyfin's own config loader during startup, harmless and self-resolving, present identically on all four nodes and unrelated to anything GPU-specific.

**Result: GPU passthrough, the NVENC patch, and a real hardware transcode all confirmed working on every P620 node in the cluster** — not just the one the driver happened to be installed on first. Migrated back to `harlan` as home base afterward.

## Closing the K600 Thread: Researching an Actual Physical Swap

Earlier in this post, the verdict on the K600 nodes was final short of one option: "a real fix would mean a physical GPU swap, not a driver change." That's no longer just a throwaway line — it's now an active, if not-yet-executed, research thread, and it started by throwing out an assumption rather than trusting it.

**Direct hardware inspection beat the docs.** Rather than assume `edgar` and `tanaka` share the same chassis as the rest of the fleet, `dmidecode` was run directly against both: `edgar` is a Dell OptiPlex 990 **Mini Tower**, `tanaka` is a Dell OptiPlex 390 **Desktop** — a genuinely smaller, more constrained case, not just a different generation. That distinction matters for everything that follows, and it wasn't written down anywhere in the project's own docs beforehand.

**The real constraint turned out to be power delivery, not just physical size.** The K600s currently in both boxes — and the P620s already proven out across the other four nodes — share a specific profile: low-profile, single-slot, and drawing power entirely from the PCIe x16 slot itself (confirmed via `lspci -vv`, showing a `SlotPowerLimit 75W` with no supplementary connector in use). That's almost certainly not a coincidence — it's what these particular OEM business desktops can actually deliver without a PSU upgrade. `dmidecode -t 39` (the SMBIOS power-supply table) came back empty on both nodes, so PSU wattage and the presence of a spare 6/8-pin connector couldn't be confirmed remotely at all — this needs eyes-on physical inspection, not another software check.

**Researched replacement options within that envelope first.** NVIDIA's Turing-generation T-series — T400 (2GB, 30W, ~$50-125 used), T600 (4GB, 40W, ~$270+), T1000 (4GB or 8GB, 50W, ~$400 for 8GB) — all genuinely fit: low-profile, single-slot, no external power, and critically, **real Tensor Cores** (compute capability 7.5), which solves the Pascal closing-window problem from earlier in this post outright — current default PyTorch wheels already target `sm_75`, no `cu126`-pinning workaround needed. One tempting-looking option got ruled out on close inspection: the RTX A2000 is marketed as low-profile, but it's confirmed **dual-slot** — a real, easy-to-miss mismatch against this specific constraint.

**Then the calculus changed on cost.** An RTX 3060 — 12GB GDDR6, real current-generation Ampere, roughly $250 used — beats the T1000 on both price and VRAM (12GB vs. 8GB for less money). But it breaks the physical envelope outright: dual-slot, full-height, ~170W, and it needs an 8-pin PCIe power connector that doesn't exist in either box today. Worth being upfront about the actual math: a T1000 at ~$400 for 8GB is a worse deal per gigabyte than a 3060 at ~$250 for 12GB, if the 3060 can physically go in.

**Where this stands:** worth actually checking, not assuming either way. One of these OptiPlex 990 MTs may already have had its stock ~300W PSU swapped for a 500-600W OEM unit at some point — if that swap included a real 6+2-pin PCIe connector (not just extra SATA/Molex power, which some generic PSU upgrades add without touching GPU power at all) and there's enough width/length/dual-slot clearance next to it, a 3060 in `edgar` becomes realistic. `tanaka`'s smaller Desktop chassis is a separate, more constrained problem regardless of what's found in `edgar` — a dual-slot full-height card is unlikely to fit there no matter the power situation, making the T1000 (or staying on `nouveau`) the more realistic path for that node specifically. **Nothing has been purchased or installed yet** — this is confirmed-viable-on-paper, pending an actual look inside the case.

## `kovacs`'s GPU Falls Off the Bus Again — This Time With a Root Cause, Not Just a Reboot

The `kovacs` D3cold incident earlier in this post got fixed with a reboot and a shrug: root cause "not fully pinned down," possibly some ACPI quirk, moving on. It happened again — not during a fresh driver install this time, but under ordinary operational load, weeks later. That gave this investigation a real chance to go past "reboot fixed it" to an actual, fixable root cause, and it turned up a second, unrelated-looking finding along the way that was worth chasing down separately rather than folding into the same story by assumption.

**The trigger wasn't a GPU alert.** It was a request to categorize error messages out of the [Media Integrity Scanner](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner) plugin — a separate side project scanning the media library for corrupt files via `ffprobe`/`ffmpeg`, running against `ct:590` (`jellyfin-test` on `kovacs`). Of 3,062 files the plugin currently listed as failing a Deep Scan, 98.5% shared the exact same error text: `CUDA_ERROR_NO_DEVICE: no CUDA-capable device is detected`. That's not a corrupt-file signature — it's the GPU not being there. Confirmed live, both on the `kovacs` host and inside the container: `nvidia-smi` failing with `Unable to determine the device handle for GPU0: 0000:01:00.0: Unknown Error / No devices were found`, and `lspci -vv` coming back truncated — no `LnkCap`, `LnkSta`, or `Status: D0` at all, just the bare BAR listing. A device that won't answer extended config-space reads isn't hung; it's not electrically there.

**`dmesg -T` on `kovacs`'s one continuous boot session showed exactly one hard fault:**

```
NVRM: Xid (PCI:0000:01:00): 79, GPU has fallen off the bus.
NVRM: GPU 0000:01:00.0: GPU has fallen off the bus.
NVRM: Xid (PCI:0000:01:00): 154, GPU recovery action changed from 0x0 (None) to 0x1 (GPU Reset Required)
```

Cross-referenced against `journalctl -u pve-container@590`: the fault landed **23 minutes after `ct:590` successfully started** with GPU passthrough active. Not proof by itself, but tight enough to take seriously — especially since the driver's own `Xid 154` message says this triggered its *own* internal recovery attempt. And it apparently worked, for a while: the plugin's scan-result database shows two genuine hardware-decode passes recorded roughly four hours later. Then, sometime before the next check, it died again — this time with **zero new `dmesg` output**. No second `Xid`, nothing. A true GPU-internal fault gets logged as an Xid event; a device that has its power rail cut before it can even raise an interrupt does not.

**Before accepting "one flaky card," the other three P620 nodes got checked for anything that would make `kovacs` different.** Identical board (Dell `06D7TR`), identical BIOS (`A24`), identical kernel, identical boot `cmdline` — confirmed, not assumed. And identical on the one setting that actually mattered:

```bash
$ for h in harlan kovacs poe quell; do ssh root@$h "cat /proc/driver/nvidia/params | grep DynamicPowerManagement"; done
DynamicPowerManagement: 3   # all four, no exceptions
$ for h in harlan kovacs poe quell; do ssh root@$h "grep -r . /etc/modprobe.d/ | grep -i nvidia"; done
(nothing on any of the four)
```

`DynamicPowerManagement: 3` is NVIDIA's out-of-the-box "Fine-Grained" RTD3 default — it lets the GPU power itself fully off (D3cold) when idle, relying on the motherboard's ACPI `_PR3`/`_PS0` methods to bring it back cleanly. These 2011-era Dell desktop boards were never validated against RTD3 by NVIDIA or Dell, and "GPU permanently falls off the bus after a power-down, needs a full reboot" is a well-documented failure class for exactly this combination. `kovacs` was the one that hit it because `ct:590`'s Deep Scan workload is the burstiest idle/active GPU pattern in the fleet — scan a batch, go idle, scan another batch — exactly the wake cycle that exercises RTD3's weak point. `harlan`, `poe`, and `quell` hadn't hit it yet, but nothing in their config made them immune. **Treated as a systemic exposure across all four nodes, not a `kovacs`-specific defect.**

**The fix: disable RTD3 outright rather than live with the exposure.**

```bash
echo 'options nvidia NVreg_DynamicPowerManagement=0x00' > /etc/modprobe.d/nvidia-power.conf
update-initramfs -u
reboot
```

Validated on `kovacs` under real load before touching anything else — not just `nvidia-smi` responding, but a direct `ffmpeg -hwaccel cuda` decode of a real library file, watched live: `nvidia-smi --query-gpu=utilization.decoder` hit a sustained 100% with zero errors.

**Then rolled out to the other three, with care taken over what was actually running where.** `quell` was empty — fixed first, no migration needed. `poe` was running `technitiumdns` (HA group `ALL`) — migrated to `edgar` before the reboot, back after. `harlan` was running production Jellyfin (`ct:502`, HA group `P620`) and `nutrition-api-dev` (`ct:602`) — both migrated off to already-fixed nodes first, `systemctl is-active jellyfin` checked as `active` on the temporary node, fixed `harlan`, migrated both back. Zero actual service downtime across the whole rollout — everything relocated via `ha-manager migrate`, nothing stopped and left down. All four now confirmed: `DynamicPowerManagement: 0`, `nvidia-smi` healthy.

### A Second Finding That Looked Related and Wasn't

Comparing `lspci -vv` across all four nodes during this same investigation turned up something else: three of the four P620 cards were negotiating their PCIe link at only 2.5GT/s instead of the card's rated 5GT/s. `harlan` was the one exception — until its own reboot in this same rollout, after which it came back downgraded too. Four for four, and the one exception stopped being an exception the moment it got rebooted. That felt like more than coincidence, sitting right next to a GPU power-management bug that had just been root-caused — both symptoms live in the same corner of the PCIe spec (ASPM, D3cold, the link power-state machine), so the instinct was that a board with a shaky D3cold implementation probably had a shaky link-training implementation too.

**Tested that instinct directly instead of writing it down as fact.** On `kovacs` (safe — only test workloads there), forced a live PCIe link retrain via `setpci` (writing the Retrain Link bit in the root port's Link Control register) without a reboot:

```bash
$ setpci -s 0000:00:01.0 CAP_EXP+10.w=0063   # set Retrain Link bit
$ lspci -s 00:01.0 -vv | grep LnkSta
LnkSta: Speed 2.5GT/s, Width x16   # settled right back at the same speed
```

Clean retrain, no training error, same result. Then went further and disabled ASPM entirely on the root port before retraining again — if ASPM's link-power negotiation were really the shared cause, removing it from the equation should have changed the outcome:

```bash
$ setpci -s 0000:00:01.0 CAP_EXP+10.w=0040   # clear ASPM bits
$ setpci -s 0000:00:01.0 CAP_EXP+10.w=0060   # retrain, ASPM off
$ lspci -s 00:01.0 -vv | grep LnkSta
LnkSta: Speed 2.5GT/s, Width x16   # still no change
```

It didn't change. That's the moment the ASPM-shared-root-cause theory should have died, and going back to check link speed **while the GPU was actually doing something** is what actually explained it:

```
# idle:
LnkSta: Speed 2.5GT/s (downgraded), Width x16

# mid hardware decode, nvidia-smi decoder utilization at 100%:
LnkSta: Speed 5GT/s, Width x16
```

**This is normal NVIDIA driver behavior, not a defect.** The driver scales the PCIe link down to Gen1 at idle as a legitimate, unrelated power-saving measure, and back up to full speed the instant real work shows up. Every idle reading taken during the original four-node comparison — including the "harlan flipped right after its reboot" pattern that looked so suspicious — just happened to catch each card between workloads. The apparent correlation with the RTD3 rollout was real (all four nodes genuinely were freshly rebooted and freshly idle at the moment they got checked) but coincidental, not causal. Restored ASPM to its original setting on `kovacs` afterward and confirmed the GPU stayed healthy through the whole experiment.

**Two separate investigations, two different outcomes: one real, fleet-wide bug fixed for good; one plausible-looking correlation tested to destruction and correctly ruled out.** Worth writing up the second one exactly as thoroughly as the first — an unresolved "suspicious but unconfirmed" note left standing in project documentation is exactly the kind of thing that gets treated as fact the next time someone reads it, and this one turned out to be wrong.

## A Third Reboot-Triggered Failure: The Device-Node Boot Race

The RTD3 rollout above involved rebooting all four P620 nodes in turn. That created the exact conditions for a fourth, completely different bug to surface — one that had nothing to do with power management and everything to do with what "the driver is installed" actually means at the moment a node comes back up.

**The symptom looked like a permissions problem.** Production Jellyfin (`ct:502`, HA-managed, group `P620`) turned up stopped, and `ha-manager status` showed it fenced in `error` state — requiring manual intervention, not just a routine restart. `pve-ha-lrm`'s journal had the real reason, and it wasn't ownership or gid mismatches at all:

```
unable to start service ct:502: Device /dev/nvidia0 does not exist
unable to start service ct:502: Device /dev/nvidia-uvm does not exist
```

Device ownership was fine throughout — `crw-rw-rw-` on the nvidia devices, `video`/`render` gids matching the container's `dev0`/`dev1` `/dev/dri` entries exactly, the same passthrough config already proven working across all four nodes earlier in this post. The devices weren't *misconfigured*. They didn't *exist yet*.

**The real cause: two different device families come up on two different timelines at boot, and nothing tells HA to wait for the slower one.** `/dev/nvidia0` and `/dev/nvidiactl` get created almost immediately — the `nvidia`/`nvidia-modeset` kernel modules load at PCI-probe time, seconds into boot. `/dev/nvidia-uvm` and `/dev/nvidia-uvm-tools` are backed by a separate module, `nvidia_uvm`, and that one is **lazy-loaded**: it only loads the first time something actually touches CUDA or Unified Memory — running `nvidia-smi`, for instance. Nothing on a bare Proxmox host does that on its own; none of these driver installs included an `nvidia-persistenced` unit. Confirmed directly in `dmesg -T` on `poe`: `nvidia`/`nvidia-modeset` loaded 11 seconds after boot; `nvidia_uvm` didn't load until nearly 30 minutes later, the moment `nvidia-smi` finally got run by hand. `pve-ha-lrm`'s own retry budget for a failed service start — two attempts, ten seconds apart — isn't remotely long enough to wait out a module that only loads on demand. Any HA-managed container racing that gap on a cold boot loses.

**This wasn't a `ct:502`-only fluke.** `ct:602` (`nutrition-api-dev`, HA group `CEPH-CORE`, GPU-passthrough for the PyTorch validation earlier in this post) hit the identical race on `quell` the same day — same two-line failure signature, same fenced error state. And checking the other two nodes turned up a live landmine, not just a historical one: `harlan` and `kovacs` had *also* rebooted as part of the same RTD3 rollout and were sitting with `/dev/nvidia-uvm*` silently missing at that exact moment — nothing had tried to start a GPU container there since, so nothing had failed yet, but the next reboot or HA relocation would have hit the exact same wall. Treated as a fleet-wide exposure across all four P620 nodes, the same call made for the RTD3 bug above, not a fix scoped to the two nodes that happened to fail first.

**The fix: force every `/dev/nvidia*` device node to exist before Proxmox's own container-start machinery ever runs.**

```ini
# /etc/systemd/system/nvidia-gpu-init.service
[Unit]
Description=Force NVIDIA GPU device node creation before HA/guest autostart
Before=pve-ha-lrm.service pve-guests.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/nvidia-smi
ExecStart=/usr/bin/nvidia-modprobe -c 0 -u

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now nvidia-gpu-init.service
```

`Before=` is declared entirely inside this new unit — no vendor Proxmox service file needed editing, so the fix survives `pve-manager` package upgrades cleanly. `nvidia-modprobe -c 0 -u` is the explicit, documented way to force the GPU-0 device file and the UVM device files into existence; `nvidia-smi` alone was empirically observed to trigger the same `nvidia_uvm` load on this driver version, and running both costs nothing. Deployed to all four P620 nodes at once — which immediately closed the latent gap on `harlan` and `kovacs` too, not just recovered the two that had already failed.

**Verified with an actual reboot, not just an enabled unit — the same discipline this post already paid for once with the `nouveau` blacklist gotcha earlier.** Rebooted `poe` for real. `nvidia-gpu-init.service` completed and all four device nodes existed within about two seconds of boot. `pve-ha-lrm`'s journal for that boot shows `ct:502` and `ct:101` both starting and reporting `OK` on the **first** attempt — no retries, no fenced error state. `ceph -s` stayed `HEALTH_OK` and the cluster stayed quorate 6/6 throughout.

Three separate reboot-triggered GPU failure modes have now shown up in this one project — the `nouveau` blacklist race on the very first canary install, `kovacs`'s D3cold/RTD3 fault, and this device-node boot race. None of them were visible from a running, already-booted system; every one of them only existed at the moment a node actually came back from a cold boot.

## Where This Leaves Things

**All four P620 nodes (`harlan`, `kovacs`, `poe`, `quell`) now have working host-side NVIDIA drivers**, confirmed via `nvidia-smi` and `dkms status`. Passthrough is wired up into two containers so far — Jellyfin (`ct:502`) and the `nutrition-api-dev` container, the latter proven with a real CUDA compute workload via PyTorch, not just a device probe. **Jellyfin's hardware-acceleration path is now fully validated across every dimension that matters:** single-stream transcode confirmed live via `nvidia-smi` (after working through the Direct Play false negative above), the NVENC session-cap patch applied and functionally verified with four concurrent encode sessions, and — the last gap — GPU passthrough, the patch, and a real transcode all confirmed working after HA failover to *every one* of the four P620 nodes, not just the one it happened to start on. `edgar` and `tanaka` stay on `nouveau` for now — but "dead end short of a physical GPU swap" has turned into real research toward that swap, not just a closed door: Turing T-series cards are a confirmed clean fit, and an RTX 3060 is a live possibility for `edgar` specifically if a prior PSU upgrade turns out to have the right connector, pending physical inspection.

**One more round after all of the above: `kovacs`'s GPU fell off the bus a second time, weeks later, under real operational load rather than a fresh install — and this time the investigation went all the way to a fixable root cause instead of stopping at "reboot fixed it again."** RTD3 (NVIDIA's default fine-grained power management) turned out to be the actual cause, confirmed identical and unfixed across all four P620 nodes, not a `kovacs`-specific fluke — disabled fleet-wide (`NVreg_DynamicPowerManagement=0x00`) with zero actual service downtime, migrating production Jellyfin and DNS off each node in turn before its reboot. A second-looking finding — a PCIe link speed "downgrade" that showed up right alongside it — got tested to destruction rather than written down as fact, and turned out to be normal idle power scaling, not a bug at all. Full writeup, including the live `setpci` experiments that disproved the more exciting theory, lives in the homelab's own infrastructure docs: [`GPU-PCIE-RTD3-INVESTIGATION.md`](https://github.com/mcgarrah/k8s-proxmox/blob/main/docs/GPU-PCIE-RTD3-INVESTIGATION.md).

**The RTD3 rollout's own reboots then surfaced a fourth, unrelated bug: production Jellyfin got fenced out of HA entirely by a device-node boot race.** `/dev/nvidia-uvm*` is lazy-created by a kernel module that only loads on first CUDA touch, and nothing on a bare host triggers that automatically — so HA's short two-attempt retry budget lost the race against the driver's own lazy loading on every P620 node that rebooted that day, not just the one (`poe`) that happened to be running the container that failed first. Fixed fleet-wide with a systemd oneshot unit ordered ahead of `pve-ha-lrm`/`pve-guests`, and confirmed with a real reboot test rather than trusting the enabled unit alone. Full details and the fix itself are documented alongside the RTD3 investigation in [`NVIDIA-GPU-KERNEL-PINNING.md`](https://github.com/mcgarrah/k8s-proxmox/blob/main/docs/NVIDIA-GPU-KERNEL-PINNING.md).

The driver install itself never touched Ceph, cluster quorum, or anything storage-related from Part 2 — it's genuinely a parallel track, which is exactly why it was safe to do out of sequence, ahead of the OS upgrade rather than folded into its post-upgrade verification.

**One last piece of insurance before moving on: all four P620 hosts got their kernel pinned.** With `580.x`'s support for the eventual Trixie kernel still an open question, and this same project having already found unattended package/kernel churn happening on these exact nodes (the wedged `apt-daily-upgrade` tasks from Part 2), leaving four freshly-working DKMS installs exposed to a silent, unattended kernel bump felt like an unnecessary way to find out the hard way. All four got `proxmox-boot-tool kernel pin 6.8.12-41-pve` (plus the required `refresh` — the pin file alone doesn't propagate to the ESPs, a lesson this series already paid for once in Part 1). They'll be unpinned deliberately, on-site, exactly when Part 5's kernel jump actually happens — not left to chance beforehand. Worth being precise about scope, too: this pin lives entirely on the hosts. An LXC has no kernel of its own to pin — it always runs whatever the host is currently booted into — so the only per-container thing that matters is keeping each container's NVIDIA userspace library version matched to its host, which was already the rule above.

---

## Key Takeaways

1. **A Driver-Compatibility Question and an OS-Upgrade Question Aren't the Same Question.** Passthrough surviving the kernel jump and hardware acceleration actually working were two separate things that happened to look like one item on a checklist — separating them is what made it obvious the GPU work didn't need to wait for the OS upgrade at all.
2. **Test the New Unknown Against the Old Known First.** With `580.x`'s Trixie-kernel support still "evolving" as of this writing, installing it against the current, already-proven PVE 8.4 kernel isolates whether a problem is the driver or the kernel — testing both at once on the same day the OS upgrade lands would make that much harder to tell apart.
3. **A Blacklist File's Presence Isn't Proof It Worked.** Same lesson as the kernel-pin gotcha back in Part 1: verify with a real reboot and a real `lsmod`, not by trusting that the config file got written correctly.
4. **When a GPU Falls Off the PCI Bus, Reboot — Don't Rescan.** A live rescan attempt made `kovacs`'s stuck GPU strictly worse. A plain reboot fixed it cleanly, on the first try, every time this category of problem has come up in this project.
5. **A Userspace-Library Patch Isn't the Same Risk as a Kernel-Module Patch.** The NVENC session-cap patch touches one shared library, with a built-in rollback flag — a meaningfully smaller blast radius than anything DKMS-related above, and worth keeping the terminology precise too: it's an encode-session limit, not a decode one.
6. **Device Access and Framework Support Are Two Different Questions.** `nvidia-smi` succeeding, and even `torch.cuda.is_available()` returning `True`, only confirms the driver and the device are talking — it says nothing about whether a specific framework's *default* build still ships compiled kernels for this specific, aging compute capability. Pascal's `sm_61` is missing from PyTorch's current default wheel the same way it's about to be missing from NVIDIA's next driver branch — check explicitly for older hardware rather than trusting a clean install.
7. **A Stream Playing Successfully Proves Nothing About the GPU.** The Android app's "Auto" quality quietly chose Direct Play — no `ffmpeg`, no transcode, no GPU involvement — and everything still looked like a working test right up until `nvidia-smi` was actually watched live. Confirming hardware acceleration means confirming a transcode was forced and happened, not that video appeared on a screen.
8. **A Userspace Patch Follows the Userspace Copy, Not the Host.** The NVENC session-cap patch had to be applied inside `ct:502` specifically, because that container has its own copy of `libnvidia-encode.so` from its `--no-kernel-module` install — patching the host's copy would have patched a library nothing here actually links against. That said, because the patch lives inside the *container's* rootfs rather than the host, it travels automatically whenever that same container migrates between nodes — the distinction that matters is container vs. host, not node vs. node. A genuinely new container getting GPU passthrough on another node for the first time would still need its own copy patched.
9. **"HA-Eligible" and "Actually Works There" Are Different Claims.** `ct:502` had been correctly configured to run on any of the four P620 nodes since before any of this GPU work started — that configuration alone proved nothing about whether it would actually function once it landed somewhere other than the one node everything had been tested on. Only walking it through every node and checking `nvidia-smi`, the patch, and a real transcode on each one closed that gap.
10. **Check the Actual Hardware Before Assuming It Matches the Fleet.** `edgar` and `tanaka` looked like they'd share a chassis with the rest of the cluster — they don't. `dmidecode` run directly against both turned up two different Dell OptiPlex form factors, a distinction with real consequences for what GPU could physically go in each one, and one that wasn't recorded anywhere in this project's own docs beforehand.
11. **"Reboot Fixed It" Isn't the Same as "Root Caused."** The first `kovacs` D3cold incident got a working fix and an honest shrug about *why*. It happened again, and going back with a real cross-node comparison instead of accepting round two as more bad luck turned up an actual, fixable, fleet-wide default (`DynamicPowerManagement: 3`) — the same class of workaround-vs-fix gap worth checking anywhere a "just restart it" fix has been living unquestioned for a while.
12. **A Plausible-Looking Correlation Deserves the Same Rigor as a Real Bug.** A PCIe link speed downgrade showing up right next to a freshly-root-caused power-management bug, on the same nodes, right after the same reboots, looked like more than coincidence. It would have been easy to write "likely related, needs more investigation" into a doc and move on. Testing it directly — a live link retrain, then the same retrain with ASPM disabled, then finally just checking the link speed under real load instead of at idle — took maybe twenty extra minutes and turned "probably connected" into "definitely not," which is a more useful thing to have on record than an unresolved suspicion.
13. **A Working System Proves Nothing About a Fresh Boot.** Three separate GPU failures in this one project — the `nouveau` blacklist race, `kovacs`'s D3cold/RTD3 fault, and the device-node boot race that fenced production Jellyfin out of HA — were all completely invisible on an already-running system and only existed in the narrow window right after a cold boot. "It's been up and working" is not the same claim as "it will come back up correctly," and the only way to actually know is to reboot it and watch.

**[Part 4](/proxmox-8-to-9-cluster-upgrade-part-4/)** picks up next: a full *arr media automation stack, built deliberately ahead of the OS jump to put these freshly-installed drivers to real use. **Part 5** covers the actual Proxmox OS upgrade to Trixie, including confirming these four drivers survive the kernel jump.
