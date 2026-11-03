#!/bin/bash
# Re-pull the latest measurement logs from the node ("quell"), sanitize and gzip them into ./raw, then rebuild all figures.
# Needs ssh access to the node. Everything copied is a measurement log; nothing here contains credentials.
set -euo pipefail
cd "$(dirname "$0")"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
scp -q "quell:/root/crashlogs/*.csv" "quell:/root/crashlogs/*.log" "$tmp/"
python3 - "$tmp" <<'PY'
import gzip, json, os, pathlib, re, sys
src = sys.argv[1]
# Real checkpoint names are deliberately NOT in this repo: they are mapped to generic ids from a private file kept outside it.
MAP_FILE = pathlib.Path(os.environ.get("CHECKPOINT_MAP", pathlib.Path.home() / ".config/gpu-psu-article/checkpoint-map.json"))
if not MAP_FILE.exists():
    sys.exit(f"missing {MAP_FILE}: create it as {{regex: generic-id}} before refreshing, or checkpoint names would leak into the repo")
CK = list(json.load(open(MAP_FILE)).items())
def sanitize(s):   # checkpoint names become generic ids; private addresses, UUIDs (Ceph fsid etc.) and MACs do not belong in a public repo
    s = re.sub(r"192\.168\.\d+\.\d+", "192.168.x.x", s)
    s = re.sub(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", "<uuid>", s)
    s = re.sub(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", "xx:xx:xx:xx:xx:xx", s)
    for pat, rep in CK:
        s = re.sub(pat, rep, s, flags=re.I)
    return s
for f in sorted(os.listdir(src)):
    with open(os.path.join(src, f), errors="ignore") as fh, gzip.open(f"raw/{f}.gz", "wt", compresslevel=9) as out:
        out.write(sanitize(fh.read()))
    print("staged", f)
PY
python3 build_assets.py
