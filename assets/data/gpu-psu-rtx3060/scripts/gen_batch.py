#!/usr/bin/env python3
# Runs inside ct:604 with the sdnext venv's python (it has PIL). Generates a batch of random-seed images and
# checks a fixed-seed "canary" image against a reference: generation is deterministic (checked earlier, pixel-identical
# across power limits), so any canary mismatch means the GPU computed something differently = a hardware/power red flag.
import argparse, base64, hashlib, io, json, os, random, sys, time, urllib.request
from PIL import Image, ImageStat

BASE = "http://127.0.0.1:7860"
P = ("a young woman with auburn hair wearing a green wool coat, standing on a rainy city street at dusk, "
     "neon reflections on wet pavement, cinematic lighting, highly detailed")
NEG = "blurry, low quality, deformed, extra fingers, bad anatomy, watermark, text"
CANARY_SEED = 1001
SAMPLES = "/root/soak_samples"


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)


def wait_ready(title, deadline_s=2700):
    end = time.time() + deadline_s
    prefix = title.split(" [")[0]
    while time.time() < end:
        try:
            ok = (bool(get("/sdapi/v1/memory").get("model"))
                  and get("/sdapi/v1/progress")["state"].get("job", "") != "Load model"
                  and get("/sdapi/v1/options").get("sd_model_checkpoint", "").startswith(prefix))
            if ok:
                return True
        except Exception:
            pass
        time.sleep(5)
    return False


def gen(seed):
    body = dict(prompt=P, negative_prompt=NEG, seed=seed, width=1024, height=1024, steps=25, cfg_scale=6.0,
                sampler_name="DPM++ 2M")
    t = time.time()
    r = json.load(urllib.request.urlopen(urllib.request.Request(
        BASE + "/sdapi/v1/txt2img", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}),
        timeout=900))
    dt = time.time() - t
    imgs = r.get("images") or []
    if not imgs:
        return dt, None, None, None
    raw = base64.b64decode(imgs[0].split(",", 1)[-1])
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    brightness = sum(ImageStat.Stat(im).mean) / 3
    return dt, hashlib.md5(im.tobytes()).hexdigest(), brightness, raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--count", type=int, default=100)
    ap.add_argument("--ref", default="/root/canary_ref.json")
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--tag", default="batch")
    a = ap.parse_args()
    os.makedirs(SAMPLES, exist_ok=True)
    if not wait_ready(a.title):
        print("BATCH_SUMMARY " + json.dumps({"error": "model never ready / wrong checkpoint selected"}), flush=True)
        sys.exit(2)

    if a.init:
        _, h1, _, raw = gen(CANARY_SEED)            # first image also absorbs the one-time warmup
        _, h2, b2, raw = gen(CANARY_SEED)
        _, h3, _, _ = gen(CANARY_SEED)
        stable = h1 is not None and h1 == h2 == h3
        json.dump({"hash": h2, "stable": stable}, open(a.ref, "w"))
        if raw:
            open(f"{SAMPLES}/canary_reference.png", "wb").write(raw)
        print("BATCH_SUMMARY " + json.dumps({"init": True, "canary_stable": stable, "brightness": b2}), flush=True)
        return

    ref = json.load(open(a.ref))
    rng = random.SystemRandom()
    times, fails, mism, dark, kept = [], 0, 0, 0, 0
    first_saved = False
    seeds_log = []
    for i in range(a.count):
        canary = (i % 10 == 0)
        seed = CANARY_SEED if canary else rng.randint(1, 2**31 - 1)
        try:
            dt, h, brightness, raw = gen(seed)
        except Exception as e:
            fails += 1
            print(f"  !! image {i+1} seed {seed}: {e}", flush=True)
            continue
        if h is None:
            fails += 1
            print(f"  !! image {i+1} seed {seed}: empty image list", flush=True)
            continue
        times.append(dt)
        bad = None
        if brightness < 5:
            dark += 1
            bad = "dark"
        if canary and ref.get("stable") and h != ref["hash"]:
            mism += 1
            bad = "CANARY_MISMATCH"
        if bad and kept < 8:
            open(f"{SAMPLES}/{a.tag}_{i+1}_{bad}_seed{seed}.png", "wb").write(raw)
            kept += 1
            print(f"  !! image {i+1} seed {seed}: {bad}", flush=True)
        if not first_saved:
            open(f"{SAMPLES}/{a.tag}_first_seed{seed}.png", "wb").write(raw)
            first_saved = True
        if (i + 1) % 20 == 0:
            print(f"  {a.tag}: {i+1}/{a.count} done, last {dt:.1f}s", flush=True)
    s = dict(images_ok=len(times), failures=fails, canary_mismatches=mism, dark_images=dark,
             avg_s=round(sum(times) / max(1, len(times)), 2), min_s=round(min(times), 2) if times else None,
             max_s=round(max(times), 2) if times else None, canary_checked=bool(ref.get("stable")))
    print("BATCH_SUMMARY " + json.dumps(s), flush=True)


main()
