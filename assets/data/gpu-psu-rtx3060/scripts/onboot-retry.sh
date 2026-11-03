#!/bin/bash
# onboot-retry: safety net for guests with onboot=1 that fail to autostart after a node HARD reset.
#
# Why it is needed (found 2026-10-05, ct:604 agent-gpu on quell): after a hard reset the guest's RBD disk still has
# exclusive locks held by the dead client; the kernel must break them and ext4's multi-mount protection then waits,
# so the rootfs only mounts ~90s after the start began. Meanwhile the host's CephFS mount (/mnt/pve/cephfs, the source of
# the shared /opt bind mount) is not mounted until after pve-guests has already given up, and the start fails with
# "lxc.hook.pre-start ... exited with status 2". A manual start a few minutes later always works.
#
# This runs once per boot AFTER pve-guests.service. It waits until Ceph has no inactive PGs and every host-path mount
# source of the guest exists, then starts the guest. It skips HA-managed guests (HA owns those) and onboot=0 guests.
# Test without starting anything: DRY_RUN=1 MAX_WAIT=10 INTERVAL=2 /usr/local/sbin/onboot-retry.sh

CONF_LXC=${CONF_LXC:-/etc/pve/lxc}
CONF_QM=${CONF_QM:-/etc/pve/qemu-server}
MAX_WAIT=${MAX_WAIT:-1800}
INTERVAL=${INTERVAL:-30}
DRY_RUN=${DRY_RUN:-0}
LOG=${LOG:-/var/log/onboot-retry.log}

log() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; logger -t onboot-retry -- "$*"; }

ha_managed() { ha-manager config 2>/dev/null | grep -qx "$1:$2"; }

is_running() {
    if [ "$1" = ct ]; then pct status "$2" 2>/dev/null | grep -q 'status: running'
    else qm status "$2" 2>/dev/null | grep -q 'status: running'; fi
}

ceph_ready() {
    timeout 30 ceph pg stat -f json 2>/dev/null | python3 -c '
import json, sys
d = json.load(sys.stdin)
bad = sum(x["num"] for x in d.get("pg_summary", {}).get("num_pg_by_state", []) if "active" not in x["name"])
sys.exit(0 if (d.get("pg_ready", True) and bad == 0) else 1)'
}

bind_sources_ready() {   # every host-path mountpoint source (mpN: /abs/path,...) must exist
    local conf=$1 src ok=0
    while read -r src; do
        [ -d "$src" ] || { ok=1; log "  waiting for mount source $src"; }
    done < <(grep -E '^mp[0-9]+: /' "$conf" | sed -E 's/^mp[0-9]+: (\/[^,]*).*/\1/')
    [ $ok -eq 0 ] || pvesm status >/dev/null 2>&1   # activating storages is what mounts /mnt/pve/cephfs
    return $ok
}

declare -A CONF
pending=()
for kind in ct vm; do
    dir=$CONF_LXC; [ "$kind" = vm ] && dir=$CONF_QM
    for conf in "$dir"/*.conf; do
        [ -f "$conf" ] || continue
        id=$(basename "$conf" .conf)
        grep -q '^onboot: 1' "$conf" || continue
        ha_managed "$kind" "$id" && continue
        CONF["$kind:$id"]=$conf
        pending+=("$kind:$id")
    done
done

[ ${#pending[@]} -gt 0 ] || { log "no non-HA onboot guests on this node, nothing to do"; exit 0; }
log "watching ${pending[*]} (MAX_WAIT=${MAX_WAIT}s, DRY_RUN=$DRY_RUN)"
deadline=$(( $(date +%s) + MAX_WAIT ))

while [ ${#pending[@]} -gt 0 ] && [ "$(date +%s)" -lt "$deadline" ]; do
    still=()
    for g in "${pending[@]}"; do
        kind=${g%%:*}; id=${g##*:}
        if is_running "$kind" "$id"; then log "$kind $id is running"; continue; fi
        if ceph_ready && { [ "$kind" = vm ] || bind_sources_ready "${CONF[$g]}"; }; then
            if [ "$DRY_RUN" = 1 ]; then log "DRY RUN: would start $kind $id (Ceph PGs active, mount sources present)"; continue; fi
            log "starting $kind $id (Ceph PGs active, mount sources present)"
            if [ "$kind" = ct ]; then timeout 300 pct start "$id" >>"$LOG" 2>&1; else timeout 300 qm start "$id" >>"$LOG" 2>&1; fi
            if is_running "$kind" "$id"; then log "$kind $id started"; continue; fi
            log "start of $kind $id failed, will retry"
        else
            log "$kind $id not started yet: Ceph or its mount sources not ready"
        fi
        still+=("$g")
    done
    pending=("${still[@]}")
    [ ${#pending[@]} -eq 0 ] && break
    sleep "$INTERVAL"
done

if [ ${#pending[@]} -gt 0 ]; then
    log "GAVE UP after ${MAX_WAIT}s on: ${pending[*]}"
    logger -p daemon.crit -t onboot-retry -- "GAVE UP starting: ${pending[*]}"
    exit 1
fi
log "done"
