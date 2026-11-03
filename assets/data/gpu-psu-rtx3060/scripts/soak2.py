#!/usr/bin/env python3
# Generation-only soak on quell at the 130W cap, instrumented with the 100 ms GPU power log.
# Runs on the host. SD.Next in ct:604 stays loaded; every batch is 100 random-seed images, every 10th a fixed-seed canary.
import json, shlex, subprocess, sys, time

sys.path.insert(0, "/root/crashlogs")
import hires_stats

LOG = "/root/crashlogs/soak2_phases.log"
HIRES = "/root/crashlogs/hires_130w.csv"
CT = "604"
TITLE = "checkpoint-03"
FILE = "checkpoint-03"
VENV_PY = "/home/mcgarrah/sdnext/venv/bin/python"
BATCHES = int(sys.argv[1]) if len(sys.argv) > 1 else 6
BATCH = 100
tot = dict(images=0, failures=0, canary_mismatches=0, dark=0, aborted=False)


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


def ct(cmd, timeout=None):
    return sh(f"pct exec {CT} -- bash -c {shlex.quote(cmd)}", timeout)


def setup():
    log(f"SETUP: GPU cap {sh('nvidia-smi --query-gpu=power.limit --format=csv,noheader')}, selecting {TITLE}")
    ct("systemctl stop comfyui open-webui sdnext", 300)
    sh(f"pct pull {CT} /home/mcgarrah/sdnext/config.json /tmp/soak2_cfg.json")
    cfg = json.load(open("/tmp/soak2_cfg.json"))
    cfg["sd_model_checkpoint"] = TITLE
    cfg.pop("sd_checkpoint_hash", None)
    cfg.pop("diffusers_to_gpu", None)
    cfg["diffusers_offload_mode"] = "none"
    json.dump(cfg, open("/tmp/soak2_cfg.json", "w"), indent=2)
    sh(f"pct push {CT} /tmp/soak2_cfg.json /home/mcgarrah/sdnext/config.json --user mcgarrah")
    t = time.time()
    cmds = ["find /home/mcgarrah/sdnext/venv -type f -size +20M | xargs -P 8 -n 1 cat > /dev/null",
            "cd /home/mcgarrah/sdnext/venv/lib/python3.11/site-packages && ls | xargs -P 32 -I{} sh -c "
            "'find {} -type f -size -20M -print0 | xargs -0 -n 40 cat > /dev/null 2>&1'",
            f"/root/prewarm.sh /home/mcgarrah/models/stable-diffusion/{FILE} 8"]
    for p in [subprocess.Popen(f"pct exec {CT} -- bash -c {shlex.quote(c)}", shell=True) for c in cmds]:
        p.wait()
    log(f"SETUP: pre-read {time.time() - t:.0f}s, starting sdnext")
    ct("systemctl start sdnext", 120)
    out = sh(f"pct exec {CT} -- {VENV_PY} /root/gen_batch.py --title {TITLE} --init --ref /root/canary_ref_soak2.json", 3600)
    summ = [l for l in out.splitlines() if l.startswith("BATCH_SUMMARY")]
    info = json.loads(summ[-1].split(" ", 1)[1]) if summ else {"error": "no summary"}
    old = json.loads(ct("cat /root/canary_ref.json") or "{}")
    new = json.loads(ct("cat /root/canary_ref_soak2.json") or "{}")
    log(f"SETUP: canary reference {info}; matches the reference from before this morning's reset: "
        f"{old.get('hash') == new.get('hash')}")
    if "error" in info:
        raise SystemExit("setup failed")


def batch(k):
    t0 = stamp()
    log(f"BATCH {k}/{BATCHES} START: {BATCH} random-seed images at the 130W cap")
    out = sh(f"pct exec {CT} -- {VENV_PY} /root/gen_batch.py --title {TITLE} --count {BATCH} "
             f"--ref /root/canary_ref_soak2.json --tag s2b{k}", 7200)
    for line in out.splitlines():
        if "!!" in line:
            log(f"BATCH {k} {line.strip()}")
    summ = [l for l in out.splitlines() if l.startswith("BATCH_SUMMARY")]
    s = json.loads(summ[-1].split(" ", 1)[1]) if summ else {"error": "no summary"}
    if "error" not in s:
        tot["images"] += s["images_ok"]; tot["failures"] += s["failures"]
        tot["canary_mismatches"] += s["canary_mismatches"]; tot["dark"] += s["dark_images"]
    else:
        tot["aborted"] = True
    log(f"BATCH {k} DONE: {s}")
    log(f"BATCH {k} POWER (100ms): {hires_stats.window(HIRES, t0, stamp())}")


def main():
    log(f"SOAK2 START: {BATCHES} batches of {BATCH} images (~{BATCHES * 31} min), generation only, 130W cap")
    setup()
    for k in range(1, BATCHES + 1):
        batch(k)
        if tot["aborted"]:
            break
    ct("systemctl start comfyui open-webui", 120)
    ok = not tot["aborted"] and tot["failures"] == 0 and tot["canary_mismatches"] == 0 and tot["dark"] == 0
    log(f"SOAK2 COMPLETE: {'PASS' if ok else 'ISSUES FOUND'} | {tot}")


main()
