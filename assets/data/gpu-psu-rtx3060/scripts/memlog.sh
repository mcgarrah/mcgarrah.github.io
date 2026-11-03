#!/bin/bash
# one line per 2s: host MemAvailable + ct:604 cgroup memory (total / anon), flushed each line
while true; do
  avail=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
  cur=$(cat /sys/fs/cgroup/lxc/604/memory.current 2>/dev/null)
  anon=$(awk '/^anon /{print $2}' /sys/fs/cgroup/lxc/604/memory.stat 2>/dev/null)
  echo "$(date '+%F %T'),MemAvailable_kB=$avail,ct604_current_B=$cur,ct604_anon_B=$anon" >> /root/crashlogs/mem_130w.csv
  sleep 2
done
