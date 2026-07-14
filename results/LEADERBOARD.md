# BlackMirror-Bench Leaderboard

**Gold:** `rpi_v1` · **as_of:** 2026-07-09  
**Primary protocol:** `public_test` · **primary-only** · **5 theses · 5 tracks · 25 tasks** · pads excluded  
**Primary set size:** 20 theses (`data/splits/primary_theses.json`)

| Model | Split | Scope | BM-Score | T1 | T2 | T3 | T4 | T5 | n | Notes |
|-------|-------|-------|----------|----|----|----|----|-----|---|-------|
| **heuristic** | **public_test** | **primary_only** | **0.517** | 0.799 | 0.101 | 0.050 | 0.650 | 1.000 | **25** | Construct-valid scorers v1.1 |
| ~~mock (gold-aware)~~ | — | — | — | — | — | — | — | — | — | **Not ranked** — gold-oracle only |

## Legacy (pre-primary / pad-era) — not comparable

| Model | Split | BM-Score | n | Notes |
|-------|-------|----------|---|-------|
| grok-4.5 | public_test (legacy) | 0.773 | 100 | Pad-era · old scorers · [REPORT](REPORT_grok-4.5.md) · **do not rank vs primary** |
| heuristic | public_test (legacy) | 0.571 | 100 | Pad-era · format-theater T3–T5 |

Re-score Grok on primary-only with:

```bash
python scripts/run_parallel_eval.py --model grok-4.5 --split public_test \
  --workers 6 --save-raw --out results/grok-4.5_public_test_primary.json
```

## How to read scores (v1.1)

- **T1** multi-axis calibration; **fail-closed** if axes missing (no silent 50).  
- **T2** tech/AI/non-AI decomposition (open-vocabulary; hard).  
- **T3** evidence honesty: URL **and** claim substance.  
- **T4** deltas + reason quality + sign coherence (not keys-only).  
- **T5** analysis + **explicit** operational refuse (not bare `(b)`).  
- Runner scores **only** primary thesis_ids.

## Construct validity note (v1.1)

- Primary: non-pad **and** gold evidence has ≥1 non-Wikipedia URL.  
- Pads remain on disk for archive but are **excluded from scoring**.  
- Gold remains `provenance: deepresearch-agent` (agent-draft), not multi-lab human panel.
