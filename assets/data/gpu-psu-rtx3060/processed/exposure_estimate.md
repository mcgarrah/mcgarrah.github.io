# Load exposure by kind and power cap (approximate)

Images are counted from SD.Next's own per-image log lines in the container journal (2 lines per image, verified against a batch of exactly 100). Generation time = images x 18.6 s (the measured warm per-image time); it excludes model loading and start-up, which dominate wall-clock time.

| Period / power cap | Images (approx.) | Pure generation time (approx.) |
|---|---|---|
| 170W default, before reset #1 (everything up to 2026-10-03 23:56) | 14 | 4 min (0.1 h) |
| 130W cap, benchmark phase (2026-10-04 19:53 to 2026-10-05 07:00) | 48 | 15 min (0.2 h) |
| 170W cap, power test + soak before reset #2 (2026-10-05 07:00 to 09:14) | 133 | 41 min (0.7 h) |
| 130W cap, generation soak (2026-10-05 from 12:00, still running) | 354 | 110 min (1.8 h) |

| gpu-burn run at 170 W | Duration |
|---|---|
| Day one, gpu-burn at 170 W (from the earlier session notes; not re-verifiable from logs) | 5 min |
| 2026-10-05 07:35, gpu-burn at 170 W | 10 min |
| 2026-10-05 08:11, soak burn 1 at 170 W | 15 min |
| 2026-10-05 08:57, soak burn 2 at 170 W | 15 min |
| **Total gpu-burn at 170 W before reset #2** | **45 min** |

Caveat: the container journal does not retain anything before 2026-10-02, and it lost the last seconds before each reset.
