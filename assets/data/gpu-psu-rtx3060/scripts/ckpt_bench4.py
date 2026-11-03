#!/usr/bin/env python3
# Checkpoint comparison, v4 (fresh SD.Next per checkpoint; API switching stacked RAM and thrashed). SD.Next runs with diffusers_offload_mode=none (whole pipeline on the GPU, no CPU copy),
# so checkpoints are switched through the API instead of restarting the service. A restart is only used as a
# fallback if SD.Next's RAM stays high after a switch.
import base64, json, os, subprocess, time, urllib.request

BASE = "http://127.0.0.1:7860"
OUT = "/home/mcgarrah/bench"
CONFIG = "/home/mcgarrah/sdnext/config.json"
MD = "/home/mcgarrah/models/stable-diffusion/"
SEEDS = [1001, 1002, 1003, 1004]
PROMPT = ("a young woman with auburn hair wearing a green wool coat, standing on a rainy city street at dusk, "
          "neon reflections on wet pavement, cinematic lighting, highly detailed")
NEG = "blurry, low quality, deformed, extra fingers, bad anatomy, watermark, text"
SETTINGS = dict(width=1024, height=1024, steps=25, cfg_scale=6.0, sampler_name="DPM++ 2M")
RAM_FALLBACK_GB = 13.0

MODELS = [  # (checkpoint title, label, optional tag prefix for a labeled second set, file)
    ("checkpoint-01", "checkpoint-01", None, "checkpoint-01"),
    ("checkpoint-02", "checkpoint-02", None, "checkpoint-02"),
    ("checkpoint-03", "checkpoint-03", None, "checkpoint-03"),
    ("checkpoint-04", "checkpoint-04", None, "checkpoint-04"),
    ("checkpoint-05", "checkpoint-05", None, "checkpoint-05"),
    ("checkpoint-06", "checkpoint-06", None, "checkpoint-06"),
    ("checkpoint-07", "checkpoint-07", "score_9, score_8_up, score_7_up, ", "checkpoint-07"),
    ("checkpoint-08", "checkpoint-08", "masterpiece, best quality, amazing quality, ", "checkpoint-08"),
]


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()


def get(path, timeout=10):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.load(r)


def post(path, payload, timeout):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return json.loads(body) if body else {}


def api_up():
    try:
        get("/sdapi/v1/options", 5)
        return True
    except Exception:
        return False


def wait_api(deadline_s=2400):
    end = time.time() + deadline_s
    while time.time() < end:
        if api_up():
            return True
        time.sleep(5)
    return False


def model_ready(title_prefix):
    # components listed on cuda, no load job running, and the selected checkpoint is the one we asked for
    try:
        mem = get("/sdapi/v1/memory", 5)
        job = get("/sdapi/v1/progress", 5).get("state", {}).get("job", "")
        sel = get("/sdapi/v1/options", 5).get("sd_model_checkpoint", "")
        return bool(mem.get("model")) and job != "Load model" and sel.startswith(title_prefix)
    except Exception:
        return False


def wait_model(title, deadline_s=2400):
    end = time.time() + deadline_s
    prefix = title.split(" [")[0]
    while time.time() < end:
        if model_ready(prefix):
            return True
        time.sleep(5)
    return False


def ram_used_gb():
    try:
        return round(get("/sdapi/v1/memory", 5)["ram"]["used"] / 1e9, 2)
    except Exception:
        return -1


def prewarm(fname):
    return subprocess.Popen(["/root/prewarm.sh", MD + fname, "8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def drop_cache():
    for _, _, _, fname in MODELS:
        try:
            fd = os.open(MD + fname, os.O_RDONLY)
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
            os.close(fd)
        except Exception:
            pass


def gen_set(label, variant, prompt, results):
    d = os.path.join(OUT, label, variant)
    os.makedirs(d, exist_ok=True)
    for seed in SEEDS:
        t0 = time.time()
        try:
            r = post("/sdapi/v1/txt2img", dict(prompt=prompt, negative_prompt=NEG, seed=seed, **SETTINGS), 1800)
        except Exception as e:
            print(f"  !! {label}/{variant} seed {seed}: {e}", flush=True)
            results[label][variant].append(dict(seed=seed, seconds=None, file=None, error=str(e)))
            return
        dt = time.time() - t0
        imgs = r.get("images", [])
        if not imgs:
            print(f"  !! {label}/{variant} seed {seed}: EMPTY images array", flush=True)
            results[label][variant].append(dict(seed=seed, seconds=round(dt, 2), file=None))
            continue
        fn = os.path.join(d, f"{seed}.png")
        with open(fn, "wb") as f:
            f.write(base64.b64decode(imgs[0].split(",", 1)[-1]))
        results[label][variant].append(dict(seed=seed, seconds=round(dt, 2), file=fn))
        print(f"  {label}/{variant} seed {seed}: {dt:.1f}s", flush=True)
    results[label][variant + "_ram_gb_after"] = ram_used_gb()


def preread_libs():
    # big libs (>20MB) with 8 readers, small files with 32 readers: cold Ceph reads are latency-bound
    big = subprocess.Popen("find /home/mcgarrah/sdnext/venv -type f -size +20M | xargs -P 8 -n 1 cat > /dev/null", shell=True)
    small = subprocess.Popen("cd /home/mcgarrah/sdnext/venv/lib/python3.11/site-packages && ls | xargs -P 32 -I{} sh -c 'find {} -type f -size -20M -print0 | xargs -0 -n 40 cat > /dev/null 2>&1'", shell=True)
    return [big, small]


def main():
    sh("systemctl stop comfyui open-webui")
    os.makedirs(OUT, exist_ok=True)
    results_path = os.path.join(OUT, "results.json")
    results = {"prompt": PROMPT, "negative": NEG, "settings": SETTINGS, "seeds": SEEDS,
               "gpu_power_limit_w": 130, "offload_mode": "none"}
    for idx, (title, label, prefix, fname) in enumerate(MODELS):
        print(f"=== {label}: stop sdnext, pre-read libs + checkpoint ===", flush=True)
        results[label] = {"shared": []}
        sh("systemctl stop sdnext")
        cfg = json.load(open(CONFIG))
        cfg["diffusers_offload_mode"] = "none"
        cfg.pop("diffusers_to_gpu", None)
        cfg["sd_model_checkpoint"] = title
        with open(CONFIG, "w") as f:
            json.dump(cfg, f, indent=2)
        t_pre = time.time()
        for p in preread_libs() + [prewarm(fname)]:
            p.wait()
        results[label]["preread_seconds"] = round(time.time() - t_pre, 1)
        t0 = time.time()
        sh("systemctl start sdnext")
        if not wait_api() or not wait_model(title):
            print(f"  !! sdnext did not come up with {label}", flush=True)
            results[label]["load_error"] = "sdnext/model never ready"
            continue
        results[label]["start_and_load_seconds"] = round(time.time() - t0, 1)
        results[label]["ram_gb_after_load"] = ram_used_gb()
        print(f"  pre-read {results[label]['preread_seconds']}s, start+load {results[label]['start_and_load_seconds']}s", flush=True)
        drop_cache()
        gen_set(label, "shared", PROMPT, results)
        if prefix:
            results[label]["tagged"] = []
            results[label]["tag_prefix"] = prefix
            gen_set(label, "tagged", prefix + PROMPT, results)
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
    cfg = json.load(open(CONFIG))
    cfg["sd_model_checkpoint"] = MODELS[0][0]
    with open(CONFIG, "w") as f:
        json.dump(cfg, f, indent=2)
    sh("chown -R mcgarrah:mcgarrah /home/mcgarrah/bench /home/mcgarrah/sdnext/config.json")
    sh("systemctl start sdnext comfyui open-webui")
    print("=== BENCHMARK COMPLETE ===", flush=True)


main()
