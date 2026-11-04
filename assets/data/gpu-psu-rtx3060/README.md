# Data for "A Used RTX 3060, a $60 PSU, and Two Unexplained Reboots"

Everything behind the figures and claims in the draft article `_drafts/2026-10-05-used-rtx-3060-cheap-psu-and-two-unexplained-reboots.md`.
All logs were captured on the node named `quell` (Dell OptiPlex 990, RTX 3060 12 GB). Private addresses, UUIDs (Ceph fsid etc.)
and MAC addresses were removed from everything in this folder; no credentials are present.

## Layout

| Path | What it is |
|---|---|
| `raw/*.gz` | Measurement logs, gzipped. `hires_130w.csv` is the 100 ms GPU log (instant W, average W, SM MHz, memory MHz, temp, utilisation, PCIe gen and width, throttle bitmask); `gpu_power_*.csv` are 2 s GPU logs; `mem_*.csv` are 2 s host and container memory logs; `*_phases.log` are the orchestrators' phase logs; `gpu_burn_170w.log`, `soak_gpu_burn.log` and `burn_soak_gpu_burn.log` (the 3 hour run) are raw `gpu-burn` output |
| `processed/` | Small tables the figures are drawn from, the benchmark results, `hires_summary.json`, `batch_summaries.txt` and `exposure_estimate.md` (hours of each load by power cap) |
| `evidence/` | Sanitised journal excerpts around both resets, boot history of all seven nodes, boot history around the 2026-09-11/12 utility outage and the 2026-10-11 cluster-wide event (`all_nodes_boot_history_sep12_oct11.txt`), what another node's corosync saw, the Ceph cluster log around the first reset, hardware identity, and the per-hour image counts the exposure table is built from |
| `scripts/` | The soak, stepped-power-ladder, image-batch, checkpoint-benchmark and boot-retry scripts that produced the data |
| `build_assets.py` | Rebuilds every figure (`assets/images/gpu-psu-rtx3060-*.png`) and the processed tables from `raw/` |
| `refresh_from_quell.sh` | Re-pulls the latest logs from the node, sanitises and gzips them into `raw/`, then runs `build_assets.py` |

## Rebuild the figures

```bash
python3 assets/data/gpu-psu-rtx3060/build_assets.py          # from the committed raw logs
assets/data/gpu-psu-rtx3060/refresh_from_quell.sh            # pull fresh logs first (needs ssh access to the node)
```

Needs `matplotlib`. The figure windows (for example 12:30:00 to 12:31:30 on 2026-10-05 for figure 1) are fixed in `build_assets.py`;
the all-samples histogram and summary statistics use whatever the log currently contains. Figures 8 and 9 use fixed windows (17:30:00 and 20:00:00 for figure 8) and the ladder phase logs.

## Known limits of this data

- **The journal loses the last seconds before a crash.** For reset #2 the persistent journal ends at 09:13:20 while the real end was about 09:13:50 to 09:13:56 (GPU log and another node's corosync log); that is why the 100 ms log was also streamed off the node.
- **There is no 100 ms data from the moment of reset #2** (the 170 W power was only logged at 2 s then); the 100 ms 170 W data comes from the later ladder and burn soak, which did not reset.
- **Image counts are estimates** (two log lines per image, 18.6 s per warm image) and the container journal does not reach back before 2026-10-02.
- **No voltage sensor is exposed** on this hardware, so the PSU's 12 V rail cannot be observed directly.

## Checkpoint names

The eight image-generation checkpoints are labelled `checkpoint-01` to `checkpoint-08` everywhere in this folder. The mapping to real names lives in a
private file outside the repository (`~/.config/gpu-psu-article/checkpoint-map.json`, regex to generic id); `refresh_from_quell.sh` applies it and
refuses to run if it is missing, so real names cannot leak back in. The scripts under `scripts/` are documentation copies with the generic ids substituted.
