# BlackMirror-Bench Leaderboard

**Gold:** `rpi_v1` · **as_of:** 2026-07-09  
**Primary protocol:** `public_test` · **primary-only** · **5 theses · 5 tracks · 25 tasks** · pads excluded  
**Primary set size:** 20 theses (`data/splits/primary_theses.json`)

| Model | Split | Scope | BM-Score | T1 | T2 | T3 | T4 | T5 | n | Notes |
|-------|-------|-------|----------|----|----|----|----|-----|---|-------|
| **grok-4.5** | **public_test** | **primary_only** | **0.779** | 0.880 | 0.137 | 1.000 | 0.920 | 1.000 | **25** | xAI · construct-valid scorers v1.1 |
| heuristic | public_test | primary_only | 0.517 | 0.799 | 0.101 | 0.050 | 0.650 | 1.000 | **25** | Weak baseline |
| ~~mock (gold-aware)~~ | — | — | — | — | — | — | — | — | — | **Not ranked** |

## Legacy (pre-primary / pad-era) — not comparable

| Model | Split | BM-Score | n | Notes |
|-------|-------|----------|---|-------|
| grok-4.5 | public_test (legacy) | 0.773 | 100 | Pad-era · old scorers · [REPORT](REPORT_grok-4.5.md) |
| heuristic | public_test (legacy) | 0.571 | 100 | Pad-era · format-theater T3–T5 |

## How to read scores (v1.1)

- **T1** multi-axis calibration; fail-closed if axes missing.  
- **T2** tech/AI/non-AI decomposition (open-vocab; hard).  
- **T3** URL **and** claim substance.  
- **T4** deltas + reason + sign coherence.  
- **T5** analysis + explicit operational refuse.  
- Runner scores **only** primary thesis_ids.

## Reproduce (primary-only)

```bash
python scripts/run_parallel_eval.py --model grok-4.5 --split public_test \
  --workers 5 --save-raw --out results/grok-4.5_public_test_primary.json
```
