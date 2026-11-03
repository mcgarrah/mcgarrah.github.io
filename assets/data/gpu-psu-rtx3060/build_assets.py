#!/usr/bin/env python3
"""Rebuild every figure and processed table for the RTX 3060 / PSU article from the raw logs in ./raw.

Run from anywhere:   python3 assets/data/gpu-psu-rtx3060/build_assets.py
Refresh the raw logs first with ./refresh_from_quell.sh (needs ssh access to the node named "quell").
Writes figures to assets/images/gpu-psu-rtx3060-*.png and tables to ./processed/.
"""
import csv, gzip, json, os, re
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HERE = os.path.dirname(os.path.abspath(__file__))
RAW, PROC = os.path.join(HERE, "raw"), os.path.join(HERE, "processed")
IMG = os.path.abspath(os.path.join(HERE, "..", "..", "images"))
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.25, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 110, "savefig.dpi": 110})
C = dict(power="#1f77b4", cap="#d62728", temp="#ff7f0e", mem="#2ca02c", anon="#9467bd", marker="#444444")


def lines(name):
    with gzip.open(os.path.join(RAW, name + ".gz"), "rt", errors="ignore") as f:
        return f.read().splitlines()


def dt(s, ms=False):
    return datetime.strptime(s[:23] if ms else s[:19], "%Y/%m/%d %H:%M:%S.%f" if ms else "%Y/%m/%d %H:%M:%S")


def power2s(name):          # 2-second logs: "2026/10/05 09:13:24.266, 150.89 W, 170.00 W, 68, 1897 MHz, 100 %"
    out = []
    for l in lines(name):
        m = re.match(r"(\S+ \S+), ([\d.]+) W, ([\d.]+) W, (\d+), (\d+) MHz, (\d+) %", l)
        if m:
            out.append((dt(m[1], True), float(m[2]), float(m[3]), int(m[4]), int(m[5]), int(m[6])))
    return out


def hires(name="hires_130w.csv"):   # 100 ms log: ts, instant W, avg W, sm MHz, mem MHz, temp, util, pcie gen, pcie width, throttle
    out = []
    for l in lines(name):
        p = [x.strip() for x in l.split(",")]
        if len(p) >= 10:
            try:
                out.append((dt(p[0], True), float(p[1]), float(p[2]), int(float(p[3])), int(float(p[5])), int(float(p[6])),
                            int(float(p[7])), int(float(p[8])), int(p[9], 16)))
            except ValueError:
                pass
    return out


def memlog(name):           # "2026-10-05 09:13:42,MemAvailable_kB=...,ct604_current_B=...,ct604_anon_B=..."
    out = []
    for l in lines(name):
        m = re.match(r"(\S+ \S+),MemAvailable_kB=(\d+),ct604_current_B=(\d*),ct604_anon_B=(\d*)", l)
        if m and m[3] and m[4]:
            out.append((datetime.strptime(m[1], "%Y-%m-%d %H:%M:%S"), int(m[2]) / 1048576, int(m[3]) / 2**30, int(m[4]) / 2**30))
    return out


def burn(name, seconds):    # "91.8%  proc'd: 4692 (9406 Gflop/s)   errors: 0   temps: 80 C"
    runs, cur, last = [], [], -1
    for l in lines(name):
        m = re.search(r"([\d.]+)%\s+proc'd:\s+\d+\s+\((\d+) Gflop/s\)\s+errors:\s+(\d+)\s+temps:\s+(\d+) C", l)
        if not m:
            continue
        pct = float(m[1])
        if pct < last and cur:
            runs.append(cur); cur = []
        cur.append((pct / 100 * seconds, int(m[2]), int(m[3]), int(m[4]))); last = pct
    if cur:
        runs.append(cur)
    return runs


def save(fig, name):
    path = os.path.join(IMG, f"gpu-psu-rtx3060-{name}.png")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
    print("wrote", os.path.relpath(path, os.path.join(HERE, "..", "..", "..")))


def write_csv(name, header, rows):
    with open(os.path.join(PROC, name), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


def window(rows, t0, t1):
    a, b = datetime.strptime(t0, "%Y-%m-%d %H:%M:%S"), datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
    return [r for r in rows if a <= r[0] <= b]


def main():
    os.makedirs(PROC, exist_ok=True)
    HI = hires()
    busy = [r for r in HI if r[5] > 50]

    # ---- Fig 1: 100 ms power while generating at the 130 W cap, and the distribution of all busy samples
    w1 = window(HI, "2026-10-05 12:30:00", "2026-10-05 12:31:30")
    write_csv("fig1_hires_130w_window.csv", ["time", "instant_w", "avg_w", "sm_mhz", "temp_c", "util_pct"],
              [(r[0].strftime("%H:%M:%S.%f")[:-3], r[1], r[2], r[3], r[4], r[5]) for r in w1])
    steps = [(abs(b[1] - a[1]), a[0], a[1], b[1]) for a, b in zip(w1, w1[1:])]
    big = max(steps)
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [2.2, 1]})
    ax[0].plot([r[0] for r in w1], [r[1] for r in w1], lw=0.8, color=C["power"])
    ax[0].axhline(130, color=C["cap"], ls="--", lw=1); ax[0].text(w1[-1][0] - timedelta(seconds=14), 140, "130 W cap", color=C["cap"], fontsize=9)
    ax[0].annotate(f"{big[2]:.0f} W -> {big[3]:.0f} W in 100 ms", (big[1], big[3]), (big[1] + timedelta(seconds=7), 62),
                   arrowprops=dict(arrowstyle="->", color=C["marker"]), fontsize=9)
    ax[0].set_ylim(0, 150); ax[0].set_ylabel("GPU power (W), 100 ms samples"); ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax[0].set_title("Image generation at a 130 W cap: a load step every ~19 s")
    vals = [r[1] for r in busy]
    ax[1].hist(vals, bins=60, color=C["power"]); ax[1].set_yscale("log"); ax[1].axvline(130, color=C["cap"], ls="--", lw=1)
    ax[1].set_xlabel("instantaneous W while busy"); ax[1].set_ylabel("samples (log)")
    ax[1].set_title(f"busy samples: n={len(vals):,}, max {max(vals):.0f} W", fontsize=9)
    save(fig, "fig1-load-steps-100ms")

    # ---- Fig 2: gpu-burn (steady) vs generation at 170 W cap vs generation at 130 W cap
    burn_w = window(power2s("gpu_power_soak.csv"), "2026-10-05 08:15:00", "2026-10-05 08:18:00")
    gen170 = window(power2s("gpu_power_170w.csv"), "2026-10-05 07:27:00", "2026-10-05 07:30:00")
    gen130 = window(HI, "2026-10-05 12:30:00", "2026-10-05 12:33:00")
    fig, axs = plt.subplots(3, 1, figsize=(10, 7.2), sharey=True)
    for ax, data, label, cap in ((axs[0], burn_w, "gpu-burn at the 170 W cap (2 s samples)", 170),
                                 (axs[1], gen170, "Image generation at the 170 W cap (2 s samples)", 170),
                                 (axs[2], gen130, "Image generation at the 130 W cap (100 ms samples)", 130)):
        t0 = data[0][0]
        x = [(r[0] - t0).total_seconds() for r in data]; y = [r[1] for r in data]
        ax.plot(x, y, lw=0.9, color=C["power"]); ax.axhline(cap, color=C["cap"], ls="--", lw=1)
        ax.set_title(f"{label}: mean {sum(y)/len(y):.0f} W, max {max(y):.0f} W", fontsize=10, loc="left"); ax.set_ylim(0, 185)
        ax.set_ylabel("W")
    axs[2].set_xlabel("seconds (3-minute windows)")
    save(fig, "fig2-burn-vs-generation")
    write_csv("fig2_windows.csv", ["panel", "seconds", "watts"],
              [("burn170", round((r[0] - burn_w[0][0]).total_seconds(), 1), r[1]) for r in burn_w] +
              [("gen170", round((r[0] - gen170[0][0]).total_seconds(), 1), r[1]) for r in gen170] +
              [("gen130", round((r[0] - gen130[0][0]).total_seconds(), 2), r[1]) for r in gen130])

    # ---- Fig 3: the last minutes before reset #2 (quell only), GPU side and host memory
    pw = window(power2s("gpu_power_soak.csv"), "2026-10-05 09:00:00", "2026-10-05 09:15:00")
    mm = window(memlog("mem_soak.csv"), "2026-10-05 09:00:00", "2026-10-05 09:15:00")
    write_csv("fig3_reset2_gpu_2s.csv", ["time", "watts", "limit_w", "temp_c", "sm_mhz", "util_pct"],
              [(r[0].strftime("%H:%M:%S"), r[1], r[2], r[3], r[4], r[5]) for r in pw])
    write_csv("fig3_reset2_memory_2s.csv", ["time", "host_mem_available_gb", "ct604_total_gb", "ct604_anon_gb"],
              [(r[0].strftime("%H:%M:%S"), round(r[1], 2), round(r[2], 2), round(r[3], 2)) for r in mm])
    T = lambda t: datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    fig, ax = plt.subplots(3, 1, figsize=(10.5, 9.2), gridspec_kw={"height_ratios": [1.1, 2.3, 1]})
    for a in ax[:2]:
        a.plot([r[0] for r in pw], [r[1] for r in pw], color=C["power"], lw=1.1)
        a.set_ylabel("GPU power (W)"); a.set_ylim(0, 190)
        t2 = a.twinx(); t2.plot([r[0] for r in pw], [r[3] for r in pw], color=C["temp"], lw=1); t2.set_ylabel("GPU temp (C)"); t2.set_ylim(40, 95); t2.grid(False)
    ax[0].set_xlim(T("2026-10-05 09:00:00"), T("2026-10-05 09:15:00")); ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax[0].set_title("Reset #2 (quell only): 13 minutes of steady load, then the data simply stops", fontsize=10)
    ax[0].axvspan(T("2026-10-05 09:12:00"), T("2026-10-05 09:14:40"), color="#ffe9a8", alpha=0.5)
    z0, z1 = T("2026-10-05 09:12:00"), T("2026-10-05 09:14:40")
    ax[1].set_xlim(z0, z1); ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    marks = [("09:12:37 gpu-burn 2 ends:\n170 W -> 16 W in ~4 s", "2026-10-05 09:12:37", 182, "right"),
             ("09:13:19 batch 2 starts:\n16 W -> 150 W in ~2 s", "2026-10-05 09:13:19", 150, "right"),
             ("09:13:50 last logged\nsample (155 W, 74 C)", "2026-10-05 09:13:50", 88, "right"),
             ("09:13:56 poe: quell\nlink is down", "2026-10-05 09:13:56", 182, "left"),
             ("09:14:28 quell\nboots again", "2026-10-05 09:14:28", 150, "right")]
    for text, t, y, ha in marks:
        for a in ax[:3]:
            if a is not ax[0]:
                a.axvline(T(t), color=C["marker"], ls=":", lw=1)
        dx = -3 if ha == "right" else 3
        ax[1].text(T(t) + timedelta(seconds=dx), y, text, fontsize=8, ha=ha, va="top")
    ax[2].set_xlim(z0, z1); ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax[2].plot([r[0] for r in mm], [r[1] for r in mm], color=C["mem"], label="host MemAvailable (GB)")
    ax[2].plot([r[0] for r in mm], [r[3] for r in mm], color=C["anon"], label="SD.Next container anonymous memory (GB)")
    ax[2].set_ylabel("GB"); ax[2].set_ylim(6, 15); ax[2].legend(loc="center left", fontsize=8)
    save(fig, "fig3-reset2-final-minutes")

    # ---- Fig 4: gpu-burn throughput and temperature, three runs at 170 W
    single = burn("gpu_burn_170w.log", 600)
    runs = [("10 min (single test)", single[-1])] + \
           [(f"15 min, soak burn {i+1}", r) for i, r in enumerate(burn("soak_gpu_burn.log", 900))]
    long_burn = burn("burn_soak_gpu_burn.log", 10800)
    runs += [("3 hour soak", max(long_burn, key=len))] if long_burn else []
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    rows = []
    for label, r in runs:
        ax[0].plot([p[0] for p in r], [p[1] for p in r], lw=1.2, label=f"{label} (errors: {max(p[2] for p in r)})")
        ax[1].plot([p[0] for p in r], [p[3] for p in r], lw=1.2)
        rows += [(label, round(p[0]), p[1], p[2], p[3]) for p in r]
    ax[0].set_ylabel("GFLOP/s"); ax[0].set_ylim(7000, 10000); ax[0].legend(fontsize=8, loc="lower left")
    ax[0].set_title("gpu-burn at the full 170 W, up to 3 hours: flat throughput, zero compute errors, 80-81 C")
    ax[1].set_ylabel("GPU temp (C)"); ax[1].set_xlabel("seconds into the burn")
    save(fig, "fig4-gpu-burn-throughput")
    write_csv("fig4_gpu_burn.csv", ["run", "seconds", "gflops", "errors", "temp_c"], rows)

    # ---- Fig 5: container memory through the SD.Next offload-mode investigation
    ml = memlog("mem_130w.csv")
    step = max(1, len(ml) // 4000)
    ml = ml[::step]
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot([r[0] for r in ml], [r[3] for r in ml], color=C["anon"], lw=1, label="container anonymous memory (GB)")
    ax.plot([r[0] for r in ml], [r[1] for r in ml], color=C["mem"], lw=1, label="host MemAvailable (GB)")
    ax.axhline(16, color=C["cap"], ls="--", lw=1); ax.text(ml[0][0], 16.3, "16 GB container cap (later raised to 18)", color=C["cap"], fontsize=8)
    ax.set_xlim(datetime(2026, 10, 4, 20, 45), datetime(2026, 10, 5, 1, 0)); ax.set_ylim(0, 27)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M")); ax.set_ylabel("GB"); ax.legend(loc="upper right", fontsize=8)
    ax.set_title("SD.Next memory in the container: where the 15 GB went", fontsize=10)
    T5 = lambda h, m: datetime(2026, 10, 4, h, m) if h >= 12 else datetime(2026, 10, 5, h, m)
    for (h, m), y, text in (((20, 47), 23.4, "A: default offload mode,\n15.8 GB (pinned at the cap)"),
                            ((21, 3), 11.3, "B: offload=none,\n~8 GB"),
                            ((21, 40), 23.4, "C: switching checkpoints through the API:\nold + new model stacked, 15.8 GB, thrashing"),
                            ((22, 25), 9.4, "D: one fresh SD.Next per\ncheckpoint, ~8 GB")):
        ax.text(T5(h, m), y, text, fontsize=8, va="bottom")
    save(fig, "fig5-memory-offload")
    write_csv("fig5_memory_downsampled.csv", ["time", "host_mem_available_gb", "ct604_total_gb", "ct604_anon_gb"],
              [(r[0].strftime("%Y-%m-%d %H:%M:%S"), round(r[1], 2), round(r[2], 2), round(r[3], 2)) for r in ml])

    # ---- Fig 6: checkpoint start-up cost vs generation time
    res = json.load(open(os.path.join(PROC, "checkpoint_benchmark_results.json")))
    names = [k for k, v in res.items() if isinstance(v, dict) and "shared" in v and "start_and_load_seconds" in v]
    pre = [res[k].get("preread_seconds", 0) / 60 for k in names]; st = [res[k]["start_and_load_seconds"] / 60 for k in names]
    img = [sum(x["seconds"] for x in res[k]["shared"][1:]) / max(1, len(res[k]["shared"]) - 1) for k in names]
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.bar(names, pre, color="#8c564b", label="pre-read of files off Ceph (min)")
    ax.bar(names, st, bottom=pre, color="#17becf", label="SD.Next start + model load (min)")
    ax.set_ylabel("minutes before the first image"); ax.tick_params(axis="x", rotation=30)
    a2 = ax.twinx(); a2.plot(names, img, "o-", color=C["cap"], label="seconds per image once warm"); a2.set_ylim(0, 25); a2.set_ylabel("s / image"); a2.grid(False)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = a2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
    ax.set_title("Eight SDXL checkpoints: identical speed (~18.6 s/image), wildly different cold-start cost")
    save(fig, "fig6-checkpoint-startup")
    write_csv("fig6_checkpoint_timings.csv", ["checkpoint", "preread_s", "start_and_load_s", "first_image_s", "avg_image_2to4_s"],
              [(k, res[k].get("preread_seconds"), res[k]["start_and_load_seconds"], res[k]["shared"][0]["seconds"], round(i, 2))
               for k, i in zip(names, img)])

    # ---- Fig 7: storage speeds measured with dd on the same node (single stream unless noted)
    labels = ["USB HDD (ZFS)", "CephFS", "Ceph RBD", "Ceph RBD, 8 parallel\nreaders"]
    wr = [106, 25.9, 18.2, None]; rd = [164, 29.3, 11.7, 136]
    fig, ax = plt.subplots(figsize=(8.5, 4))
    xs = range(len(labels))
    ax.bar([x - 0.2 for x in xs], [w or 0 for w in wr], 0.4, label="sequential write (MB/s)", color="#7f7f7f")
    ax.bar([x + 0.2 for x in xs], rd, 0.4, label="cold sequential read (MB/s)", color=C["power"])
    for x, w, r in zip(xs, wr, rd):
        if w: ax.text(x - 0.2, w + 3, f"{w:g}", ha="center", fontsize=8)
        ax.text(x + 0.2, r + 3, f"{r:g}", ha="center", fontsize=8)
    ax.set_xticks(list(xs)); ax.set_xticklabels(labels, fontsize=9); ax.set_ylabel("MB/s"); ax.legend(fontsize=8)
    ax.set_title("Cold reads are latency-bound: one stream 11.7 MB/s, eight streams 136 MB/s")
    save(fig, "fig7-storage-speeds")


    # ---- Fig 8: 100 ms power at the 170 W cap, image generation vs the 3 hour gpu-burn (same scale)
    g170 = window(HI, "2026-10-05 17:30:00", "2026-10-05 17:31:30")
    b170 = window(HI, "2026-10-05 20:00:00", "2026-10-05 20:01:30")
    fig, axs = plt.subplots(2, 1, figsize=(10.5, 6), sharey=True)
    for ax_, data, label in ((axs[0], g170, "Image generation at the 170 W cap"), (axs[1], b170, "gpu-burn at the 170 W cap")):
        ys = [r[1] for r in data]; st = max(abs(b[1] - a[1]) for a, b in zip(data, data[1:]))
        ax_.plot([r[0] for r in data], ys, lw=0.8, color=C["power"]); ax_.axhline(170, color=C["cap"], ls="--", lw=1)
        ax_.set_title(f"{label}: mean {sum(ys)/len(ys):.0f} W, max {max(ys):.0f} W, largest 100 ms step {st:.0f} W", fontsize=10, loc="left")
        ax_.set_ylim(0, 190); ax_.set_ylabel("W (100 ms samples)"); ax_.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    save(fig, "fig8-170w-generation-vs-burn")
    write_csv("fig8_windows.csv", ["panel", "time", "instant_w"],
              [("gen170", r[0].strftime("%H:%M:%S.%f")[:-3], r[1]) for r in g170] + [("burn170", r[0].strftime("%H:%M:%S.%f")[:-3], r[1]) for r in b170])

    # ---- Fig 9: the stepped power ladder, from the phase logs
    pat = re.compile(r"(?:LEVEL (\d+)W )?BATCH \d+ POWER \(100ms\): (\d+) samples \| busy W: max ([\d.]+).*? mean ([\d.]+) \|.*?largest 100ms step ([\d.]+)W \| max temp (\d+)C")
    rungs = {}
    for l in lines("soak2_phases.log") + lines("ladder_phases.log"):
        m = pat.search(l)
        if m:
            cap = int(m[1] or 130); n, mx, mean, stp, tmp = int(m[2]), float(m[3]), float(m[4]), float(m[5]), int(m[6])
            r = rungs.setdefault(cap, dict(n=0, wsum=0.0, mx=0.0, stp=0.0, tmp=0, batches=0))
            r["n"] += n; r["wsum"] += mean * n; r["mx"] = max(r["mx"], mx); r["stp"] = max(r["stp"], stp); r["tmp"] = max(r["tmp"], tmp); r["batches"] += 1
    caps = sorted(rungs)
    burn_row = None
    for l in lines("burn_soak_phases.log"):
        m = re.search(r"BURN SOAK COMPLETE.*?max ([\d.]+) C.*?busy W: max ([\d.]+).*? mean ([\d.]+) \|.*?largest 100ms step ([\d.]+)W", l)
        if m:
            burn_row = (float(m[2]), float(m[3]), float(m[4]), int(float(m[1])))
    if burn_row:   # the logged step of 137 W is the idle-to-full-load launch; report the steady-state swing from the 100 ms log instead
        steady = window(HI, "2026-10-05 19:46:00", "2026-10-05 22:40:00")
        steady_step = max(abs(b[1] - a[1]) for a, b in zip(steady, steady[1:]))
        burn_row = (burn_row[0], burn_row[1], round(steady_step, 1), burn_row[3])
    write_csv("fig9_ladder.csv", ["rung", "batches_of_100_images", "busy_samples", "mean_w", "max_w", "largest_100ms_step_w", "max_temp_c"],
              [(f"{c} W generation", rungs[c]["batches"], rungs[c]["n"], round(rungs[c]["wsum"] / rungs[c]["n"], 1), rungs[c]["mx"], rungs[c]["stp"], rungs[c]["tmp"]) for c in caps] +
              ([("170 W gpu-burn, 3 h", 0, "", burn_row[1], burn_row[0], burn_row[2], burn_row[3])] if burn_row else []))
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    xs = [str(c) for c in caps]
    ax[0].plot(xs, [rungs[c]["mx"] for c in caps], "o-", color=C["power"], label="maximum instantaneous W")
    ax[0].plot(xs, [rungs[c]["wsum"] / rungs[c]["n"] for c in caps], "s-", color=C["mem"], label="mean W while busy")
    ax[0].plot(xs, caps, "--", color=C["cap"], label="the cap")
    ax[0].set_xlabel("power cap (W)"); ax[0].set_ylabel("W"); ax[0].legend(fontsize=8); ax[0].set_title("Generation never reaches a 170 W cap", fontsize=10)
    ax[1].bar(xs, [rungs[c]["stp"] for c in caps], color=C["power"], label="image generation")
    if burn_row:
        ax[1].bar(["170 burn"], [burn_row[2]], color="#7f7f7f", label="gpu-burn, 3 h (steady state; the launch itself was a 137 W step)")
    ax[1].set_xlabel("rung"); ax[1].set_ylabel("largest 100 ms step (W)"); ax[1].legend(fontsize=8)
    ax[1].set_title("Largest single 100 ms swing per rung", fontsize=10)
    save(fig, "fig9-power-ladder")

    # ---- Summary tables
    summ = {"samples_100ms": len(HI), "busy_samples": len(busy), "max_instant_w_busy": max(vals),
            "over_145w": sum(1 for v in vals if v > 145), "hw_slowdown_samples": sum(1 for r in busy if r[8] & 0xC8),
            "pcie_link_under_load": sorted({(r[6], r[7]) for r in busy}), "max_temp_c": max(r[4] for r in HI),
            "first": HI[0][0].isoformat(timespec="seconds"), "last": HI[-1][0].isoformat(timespec="seconds")}
    json.dump(summ, open(os.path.join(PROC, "hires_summary.json"), "w"), indent=2, default=str)
    print("summary:", summ)
    batches = [l for l in lines("soak2_phases.log") + lines("ladder_phases.log") if re.search(r"BATCH \d+(/\d+)? (DONE|POWER)|LEVEL|LADDER|INDICATOR", l)]
    open(os.path.join(PROC, "batch_summaries.txt"), "w").write("\n".join(batches) + "\n")


if __name__ == "__main__":
    main()
