#!/usr/bin/env python3
# 3-hour gpu-burn-only soak at the full 170 W cap: the missing cell of the {gpu-burn, generation} x {130 W, 170 W} grid.
# Waits for the stepped power ladder to finish. Runs only if the ladder found no indicator; otherwise it skips and says why.
# SD.Next stays loaded and idle (same VRAM footprint as the earlier burns), gpu-burn is limited to 3.5 GB of VRAM.
# Usage: burn_soak.py [--selftest]
import os, re, subprocess, sys, threading, time

sys.path.insert(0, "/root/crashlogs")
import hires_stats

LOG = "/root/crashlogs/burn_soak_phases.log"
LADDER_LOG = "/root/crashlogs/ladder_phases.log"
BURN_LOG = "/root/crashlogs/burn_soak_gpu_burn.log"
HIRES = "/root/crashlogs/hires_130w.csv"
GPU = "0000:01:00.0"
SAFE_CAP, FULL_CAP = 130, 170
BURN_S = 3 * 3600
TEMP_ABORT = 88
state = {"tripped": None}
stop = threading.Event()


def now():
    return time.strftime("%F %T")


def stamp():
    return time.strftime("%Y/%m/%d %H:%M:%S")


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{now()} {msg}\n")


def sh(cmd, timeout=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "").strip()


def aer():
    out = {}
    for f in ("aer_dev_correctable", "aer_dev_nonfatal", "aer_dev_fatal"):
        try:
            for line in open(f"/sys/bus/pci/devices/{GPU}/{f}"):
                if line.startswith("TOTAL_"):
                    out[f] = int(line.split()[1])
        except Exception:
            pass
    return out


def last_rows(nbytes=9000):
    try:
        with open(HIRES, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - nbytes))
            lines = f.read().decode(errors="ignore").splitlines()[1:]
        return [r for r in map(hires_stats.parse, lines) if r]
    except Exception:
        return []


def set_cap(w):
    sh(f"nvidia-smi -pl {w}")
    return sh("nvidia-smi --query-gpu=power.limit --format=csv,noheader")


def trip(reason):
    if not state["tripped"]:
        state["tripped"] = reason
        sh("pkill -x gpu_burn")
        log(f"INDICATOR: {reason} -> stopping gpu-burn and backing off to {SAFE_CAP}W (cap reads {set_cap(SAFE_CAP)})")


def guardian():
    base = aer()
    while not stop.is_set():
        time.sleep(5)
        cur = aer()
        if any(cur.get(k, 0) > base.get(k, 0) for k in cur):
            trip(f"PCIe error counters rose {base} -> {cur}")
        load = [r for r in last_rows() if r["util"] > 50]
        if any(r["thr"] & 0xC8 for r in load):
            trip("hardware slowdown / thermal / power-brake flag set under load")
        if any(r["width"] < 16 for r in load):
            trip("PCIe link width dropped below x16 under load")


def burn_stats(text):
    rows = re.findall(r"\((\d+) Gflop/s\)\s+errors:\s+(\d+)\s+temps:\s+(\d+) C", text)
    gf = [int(r[0]) for r in rows if int(r[0]) > 0]
    return (sum(gf) / max(len(gf), 1), min(gf or [0]), max([int(r[1]) for r in rows] or [0]), max([int(r[2]) for r in rows] or [0]))


def main():
    if "--selftest" in sys.argv:
        print("AER:", aer(), "| hires rows:", len(last_rows()), "| cap:", sh("nvidia-smi --query-gpu=power.limit --format=csv,noheader"))
        print("gpu_burn present:", os.path.exists("/root/gpu-burn/gpu_burn"))
        return
    log(f"BURN SOAK queued: waiting for the stepped power ladder to finish; will then run gpu-burn for {BURN_S // 60} min at {FULL_CAP} W")
    end = time.time() + 16 * 3600
    ladder = ""
    while time.time() < end:
        ladder = open(LADDER_LOG).read() if os.path.exists(LADDER_LOG) else ""
        if "LADDER COMPLETE" in ladder or "LADDER gave up" in ladder:
            break
        time.sleep(30)
    if "LADDER COMPLETE" not in ladder:
        log("BURN SOAK SKIPPED: the ladder never completed (it may have been interrupted); re-queue by hand")
        return
    if "STOPPED BY INDICATOR" in ladder:
        log("BURN SOAK SKIPPED: the ladder stopped on an indicator, so I am not running an unattended 3 h burn at 170 W; needs a decision")
        return
    time.sleep(30)
    log(f"BURN SOAK START: cap now reads {set_cap(FULL_CAP)}, AER {aer()}")
    threading.Thread(target=guardian, daemon=True).start()
    start_size = os.path.getsize(BURN_LOG) if os.path.exists(BURN_LOG) else 0
    t0, t0s = time.time(), stamp()
    p = subprocess.Popen(f"./gpu_burn -m 3500 {BURN_S} 2>&1 | tr '\\r' '\\n' >> {BURN_LOG}", shell=True, cwd="/root/gpu-burn")
    hot, last_report, win_start = 0, time.time(), stamp()
    while p.poll() is None:
        try:
            hot = hot + 1 if int(sh("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits")) > TEMP_ABORT else 0
        except Exception:
            pass
        if hot >= 3:
            trip(f"GPU above {TEMP_ABORT} C for 30 s")
        text = open(BURN_LOG, errors="ignore").read()[start_size:]
        if burn_stats(text)[2] > 0:
            trip("gpu-burn reported compute errors")
        if time.time() - last_report >= 600 and not state["tripped"]:
            avg, mn, errs, mt = burn_stats(text)
            log(f"BURN SOAK +{int((time.time() - t0) / 60)} min: {avg:.0f} GFLOP/s avg (min {mn}), errors {errs}, max {mt} C | "
                f"{hires_stats.window(HIRES, win_start, stamp())} | AER {aer()}")
            last_report, win_start = time.time(), stamp()
        time.sleep(10)
    p.wait()
    stop.set()
    text = open(BURN_LOG, errors="ignore").read()[start_size:]
    avg, mn, errs, mt = burn_stats(text)
    verdict = "OK" if re.search(r"GPU 0: OK", text) else ("FAULTY" if "FAULTY" in text else "no verdict")
    final = set_cap(SAFE_CAP)
    outcome = "NO INDICATORS" if not state["tripped"] else f"STOPPED BY INDICATOR: {state['tripped']}"
    log(f"BURN SOAK COMPLETE: {outcome} | gpu-burn verdict {verdict}, compute errors {errs}, {avg:.0f} GFLOP/s avg (min {mn}), "
        f"max {mt} C | ran {int((time.time() - t0) / 60)} min | AER now {aer()} | cap restored to {final} | "
        f"power {hires_stats.window(HIRES, t0s, stamp())}")


main()
