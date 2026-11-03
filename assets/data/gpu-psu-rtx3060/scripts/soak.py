#!/usr/bin/env python3
# Long GPU/PSU soak on quell: alternate 15 min of gpu-burn with batches of 100 random-seed SDXL images.
# SD.Next stays loaded the whole time (gpu-burn is limited to 3.5GB of VRAM) so there are no reloads.
import json, re, shlex, subprocess, time

LOG = "/root/crashlogs/soak_phases.log"
BURN_LOG = "/root/crashlogs/soak_gpu_burn.log"
POWER_CSV = "/root/crashlogs/gpu_power_soak.csv"
CT = "604"
TITLE = "checkpoint-03"
FILE = "checkpoint-03"
VENV_PY = "/home/mcgarrah/sdnext/venv/bin/python"
BURN_S, BATCH, ROUNDS = 900, 100, 3
TEMP_ABORT = 88
tot = dict(images=0, failures=0, canary_mismatches=0, dark=0, burn_errors=0, burns_ok=0, burns=0, aborted=False)


def now():
    return time.strftime("%F %T")


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{now()} {msg}\n")


def sh(cmd, timeout=None, cwd=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    return (r.stdout or "").strip()


def ct(cmd, timeout=None):
    return sh(f"pct exec {CT} -- bash -c {shlex.quote(cmd)}", timeout)


def gpu(field):
    return sh(f"nvidia-smi --query-gpu={field} --format=csv,noheader,nounits")


def window_stats(t0, t1):
    pk = mt = n = busy = 0
    s = 0.0
    try:
        for line in open(POWER_CSV):
            p = line.split(", ")
            if len(p) < 6 or not (t0 <= p[0][:19] <= t1):
                continue
            w = float(p[1].split()[0]); pk = max(pk, w); mt = max(mt, int(p[3]))
            if int(p[5].split()[0]) > 50:
                s += w; busy += 1
    except Exception:
        pass
    return f"GPU peak {pk:.1f}W avg-busy {s / max(busy, 1):.1f}W max {mt}C"


def setup():
    log("SETUP: stopping sdnext/comfyui/open-webui, selecting " + TITLE)
    ct("systemctl stop sdnext comfyui open-webui", 240)
    sh(f"pct pull {CT} /home/mcgarrah/sdnext/config.json /tmp/soak_cfg.json")
    cfg = json.load(open("/tmp/soak_cfg.json"))
    cfg["sd_model_checkpoint"] = TITLE
    cfg.pop("sd_checkpoint_hash", None)   # SD.Next prefers the saved hash over the title
    cfg.pop("diffusers_to_gpu", None)
    cfg["diffusers_offload_mode"] = "none"
    json.dump(cfg, open("/tmp/soak_cfg.json", "w"), indent=2)
    sh(f"pct push {CT} /tmp/soak_cfg.json /home/mcgarrah/sdnext/config.json --user mcgarrah")
    t = time.time()
    cmds = ["find /home/mcgarrah/sdnext/venv -type f -size +20M | xargs -P 8 -n 1 cat > /dev/null",
            "cd /home/mcgarrah/sdnext/venv/lib/python3.11/site-packages && ls | xargs -P 32 -I{} sh -c "
            "'find {} -type f -size -20M -print0 | xargs -0 -n 40 cat > /dev/null 2>&1'",
            f"/root/prewarm.sh /home/mcgarrah/models/stable-diffusion/{FILE} 8"]
    procs = [subprocess.Popen(f"pct exec {CT} -- bash -c {shlex.quote(c)}", shell=True) for c in cmds]
    for p in procs:
        p.wait()
    log(f"SETUP: pre-read done in {time.time() - t:.0f}s, starting sdnext")
    ct("systemctl start sdnext", 120)
    out = sh(f"pct exec {CT} -- {VENV_PY} /root/gen_batch.py --title {TITLE} --init", 3600)
    summ = [l for l in out.splitlines() if l.startswith("BATCH_SUMMARY")]
    info = json.loads(summ[-1].split(" ", 1)[1]) if summ else {"error": "no summary"}
    log(f"SETUP: canary reference captured: {info}")
    if "error" in info:
        raise SystemExit("setup failed")


def burn(k):
    tot["burns"] += 1
    t0 = now().replace("-", "/")
    start = sh(f"stat -c %s {BURN_LOG} 2>/dev/null") or "0"
    log(f"BURN {k} START ({BURN_S}s at 170W, 3.5GB VRAM)")
    p = subprocess.Popen(f"./gpu_burn -m 3500 {BURN_S} 2>&1 | tr '\\r' '\\n' >> {BURN_LOG}", shell=True,
                         cwd="/root/gpu-burn")
    hot = 0
    while p.poll() is None:
        try:
            hot = hot + 1 if int(gpu("temperature.gpu")) > TEMP_ABORT else 0
        except Exception:
            pass
        if hot >= 3:
            sh("pkill -x gpu_burn")
            tot["aborted"] = True
            log(f"BURN {k} ABORT: GPU above {TEMP_ABORT}C for 30s, stopping the test to protect the card")
            break
        time.sleep(10)
    p.wait()
    text = open(BURN_LOG, errors="ignore").read()[int(start):]
    rows = re.findall(r"\((\d+) Gflop/s\)\s+errors:\s+(\d+)\s+temps:\s+(\d+) C", text)
    gf = [int(r[0]) for r in rows if int(r[0]) > 0]
    errs = max([int(r[1]) for r in rows] or [0])
    mt = max([int(r[2]) for r in rows] or [0])
    verdict = "OK" if re.search(r"GPU 0: OK", text) else ("FAULTY" if "FAULTY" in text else "no verdict")
    tot["burn_errors"] += errs
    tot["burns_ok"] += verdict == "OK"
    log(f"BURN {k} DONE: verdict {verdict}, compute errors {errs}, "
        f"{(sum(gf) / max(len(gf), 1)):.0f} Gflop/s avg (min {min(gf or [0])}), max {mt}C | "
        + window_stats(t0[:19], now().replace('-', '/')[:19]))


def batch(k):
    t0 = now().replace("-", "/")
    log(f"BATCH {k} START: {BATCH} random-seed images (every 10th is the seed-1001 canary)")
    out = sh(f"pct exec {CT} -- {VENV_PY} /root/gen_batch.py --title {TITLE} --count {BATCH} --tag b{k}", 7200)
    for line in out.splitlines():
        if "!!" in line:
            log(f"BATCH {k} {line.strip()}")
    summ = [l for l in out.splitlines() if l.startswith("BATCH_SUMMARY")]
    s = json.loads(summ[-1].split(" ", 1)[1]) if summ else {"error": "no summary"}
    if "error" not in s:
        tot["images"] += s["images_ok"]; tot["failures"] += s["failures"]
        tot["canary_mismatches"] += s["canary_mismatches"]; tot["dark"] += s["dark_images"]
    log(f"BATCH {k} DONE: {s} | " + window_stats(t0[:19], now().replace('-', '/')[:19]))
    if "error" in s:
        tot["aborted"] = True


def main():
    log("SOAK START: 4 burns of 15 min alternating with 3 batches of 100 images")
    setup()
    for k in range(1, ROUNDS + 1):
        burn(k)
        if tot["aborted"]:
            break
        batch(k)
        if tot["aborted"]:
            break
    if not tot["aborted"]:
        burn(ROUNDS + 1)
    ct("systemctl start comfyui open-webui", 120)
    ok = (not tot["aborted"] and tot["burn_errors"] == 0 and tot["burns_ok"] == tot["burns"]
          and tot["failures"] == 0 and tot["canary_mismatches"] == 0 and tot["dark"] == 0)
    log(f"SOAK COMPLETE: {'PASS' if ok else 'ISSUES FOUND'} | {tot}")


main()
