#!/usr/bin/env python3
# Stepped power ladder on quell: raise the GPU power cap one rung at a time while generating images, watching for
# leading indicators of a hardware/PSU problem, and drop back to the safe 130W cap the moment one appears.
# Waits for the running 130W soak (soak2) to finish first. Usage: ladder.py [--selftest]
import json, shlex, subprocess, sys, threading, time

sys.path.insert(0, "/root/crashlogs")
import hires_stats

LOG = "/root/crashlogs/ladder_phases.log"
SOAK2_LOG = "/root/crashlogs/soak2_phases.log"
HIRES = "/root/crashlogs/hires_130w.csv"
CT = "604"
VENV_PY = "/home/mcgarrah/sdnext/venv/bin/python"
TITLE = "checkpoint-03"
REF = "/root/canary_ref_soak2.json"
GPU = "0000:01:00.0"
SAFE_CAP = 130
LEVELS = [(140, 1), (150, 1), (170, 6)]      # (power cap in W, number of 100-image batches)
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


def last_rows(path, nbytes=9000):
    try:
        with open(path, "rb") as f:
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
        log(f"INDICATOR: {reason} -> backing off to {SAFE_CAP}W cap now (cap reads {set_cap(SAFE_CAP)})")


def guardian():
    base = aer()
    while not stop.is_set():
        time.sleep(5)
        cur = aer()
        if any(cur.get(k, 0) > base.get(k, 0) for k in cur):
            trip(f"PCIe error counters rose {base} -> {cur}")
        load = [r for r in last_rows(HIRES) if r["util"] > 50]
        if any(r["thr"] & 0xC8 for r in load):
            trip("hardware slowdown / thermal / power-brake flag set under load")
        if any(r["width"] < 16 for r in load):
            trip("PCIe link width dropped below x16 under load")


def wait_for_soak2():
    log("LADDER queued: waiting for the 130W soak (soak2) to complete")
    end = time.time() + 8 * 3600
    while time.time() < end:
        if "SOAK2 COMPLETE" in open(SOAK2_LOG).read():
            return True
        time.sleep(30)
    return False


def main():
    if "--selftest" in sys.argv:
        print("AER:", aer())
        rows = last_rows(HIRES)
        print("hires rows parsed:", len(rows), "| last:", rows[-1] if rows else None)
        print("cap now:", sh("nvidia-smi --query-gpu=power.limit --format=csv,noheader"))
        return
    if not wait_for_soak2():
        log("LADDER gave up waiting for soak2")
        return
    time.sleep(20)
    log(f"LADDER START: levels {LEVELS}, AER at start {aer()}, safe cap {SAFE_CAP}W")
    threading.Thread(target=guardian, daemon=True).start()
    totals = dict(images=0, failures=0, mismatches=0)
    for cap, nbatches in LEVELS:
        if state["tripped"]:
            break
        log(f"LEVEL {cap}W START (cap reads {set_cap(cap)}), {nbatches} batch(es) of 100 images")
        aer0 = aer()
        for b in range(1, nbatches + 1):
            t0 = stamp()
            out = sh(f"pct exec {CT} -- {VENV_PY} /root/gen_batch.py --title {TITLE} --count 100 --ref {REF} "
                     f"--tag lad{cap}_{b}", 7200)
            summ = [l for l in out.splitlines() if l.startswith("BATCH_SUMMARY")]
            s = json.loads(summ[-1].split(" ", 1)[1]) if summ else {"error": "no summary"}
            log(f"LEVEL {cap}W BATCH {b}/{nbatches} DONE: {s}")
            log(f"LEVEL {cap}W BATCH {b} POWER (100ms): {hires_stats.window(HIRES, t0, stamp())}")
            log(f"LEVEL {cap}W BATCH {b} PCIe error counters {aer0} -> {aer()}")
            if "error" in s:
                trip("batch failed to complete")
            else:
                totals["images"] += s["images_ok"]; totals["failures"] += s["failures"]
                totals["mismatches"] += s["canary_mismatches"]
                if s["canary_mismatches"] or s["failures"] or s["dark_images"]:
                    trip(f"image problems: {s}")
            if state["tripped"]:
                break
    stop.set()
    final = set_cap(SAFE_CAP)
    verdict = "NO INDICATORS" if not state["tripped"] else f"STOPPED BY INDICATOR: {state['tripped']}"
    log(f"LADDER COMPLETE: {verdict} | {totals} | AER now {aer()} | cap restored to {final}")


main()
