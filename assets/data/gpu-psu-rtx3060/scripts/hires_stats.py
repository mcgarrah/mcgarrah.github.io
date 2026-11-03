#!/usr/bin/env python3
# Shared analyzer for the 100 ms GPU log. Columns (csv, nounits):
# timestamp, power.draw.instant, power.draw.average, clocks.sm, clocks.mem, temperature.gpu, utilization.gpu,
# pcie.link.gen.current, pcie.link.width.current, clocks_throttle_reasons.active
import collections


def parse(line):
    p = [x.strip() for x in line.split(",")]
    if len(p) < 10:
        return None
    try:
        return dict(ts=p[0], w=float(p[1]), wavg=float(p[2]), sm=int(float(p[3])), mem=int(float(p[4])),
                    temp=int(float(p[5])), util=int(float(p[6])), gen=int(float(p[7])), width=int(float(p[8])),
                    thr=int(p[9], 16))
    except Exception:
        return None


def window(path, t0, t1):
    """Stats for samples whose timestamp (first 19 chars, 'YYYY/MM/DD HH:MM:SS') is within [t0, t1]."""
    rows = []
    with open(path, errors="ignore") as f:
        for line in f:
            if len(line) > 19 and t0 <= line[:19] <= t1:
                r = parse(line)
                if r:
                    rows.append(r)
    return summarize(rows)


def summarize(rows):
    if not rows:
        return "no samples"
    busy = [r for r in rows if r["util"] > 50] or rows
    w = sorted(r["w"] for r in busy)
    n = len(w)
    pct = lambda q: w[min(n - 1, int(q * n))]
    max_step = max((abs(b["w"] - a["w"]) for a, b in zip(rows, rows[1:])), default=0)
    over = {t: sum(1 for x in w if x > t) for t in (135, 145, 155, 170)}
    links = collections.Counter((r["gen"], r["width"]) for r in busy)
    thr = collections.Counter(r["thr"] for r in rows)
    hw = sum(c for v, c in thr.items() if v & 0xC8)           # HW slowdown / HW thermal / HW power brake
    return (f"{len(rows)} samples | busy W: max {w[-1]:.1f} p99.9 {pct(0.999):.1f} p99 {pct(0.99):.1f} "
            f"mean {sum(w) / n:.1f} | >135W:{over[135]} >145W:{over[145]} >155W:{over[155]} >170W:{over[170]} | "
            f"largest 100ms step {max_step:.1f}W | max temp {max(r['temp'] for r in rows)}C | "
            f"PCIe link under load {dict(links)} | HW-slowdown/brake samples {hw}")


if __name__ == "__main__":
    import sys
    print(window(sys.argv[1], sys.argv[2], sys.argv[3]))
