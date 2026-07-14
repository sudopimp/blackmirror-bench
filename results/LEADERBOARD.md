# BlackMirror-Bench Leaderboard

**Gold:** `rpi_v1` · **as_of:** 2026-07-09  
**Primary protocol:** `public_test` · **primary-only** · 5 theses · 5 tracks · 25 tasks · pads excluded

| Model | Split | BM-Score | T1 | T2 | T3 | T4 | T5 | n | Notes |
|-------|-------|----------|----|----|----|----|----|---|-------|
| **grok-4.5** | **public_test** | **0.773** | **0.856** | 0.203 | **0.950** | **0.900** | **1.000** | 100 | xAI API · [REPORT](REPORT_grok-4.5.md) |
| heuristic | public_test | 0.571 | 0.737 | 0.124 | 0.200 | 0.900 | 1.000 | 100 | Midpoint + keyword baseline |
| ~~mock (gold-aware)~~ | — | — | — | — | — | — | — | — | **Not ranked** — gold-oracle harness ceiling only |
| heuristic | public_dev (partial) | ~0.58 | ~0.78 | ~0.10 | 0.20 | 0.90 | 1.00 | — | Legacy partial run |
| random_mid | public_test (partial) | ~0.57 | ~0.74 | ~0.11 | 0.20 | 0.90 | 1.00 | — | Legacy partial run |

## How to read scores

- **T1** multi-axis calibration vs gold RPI (higher = closer to gold, not “more dystopian”).  
- **T2** tech/AI/non-AI decomposition (open-vocabulary; currently hard).  
- **T3** evidence honesty (URLs + anti-fake-cite).  
- **T4** structured score updates under new evidence.  
- **T5** analysis OK + refuse operational harm.  
- Dark-pattern penalties (hype / sci-fi collapse / fake cites) applied when detected.

## Reproduce Grok 4.5

```bash
python scripts/run_parallel_eval.py --model grok-4.5 --split public_test \
  --workers 6 --save-raw --out results/grok-4.5_public_test.json
```

Full write-up: **[REPORT_grok-4.5.md](REPORT_grok-4.5.md)**  
Raw machine results: `grok-4.5_public_test.json` · `grok-4.5_public_test_summary.json`


## Construct validity note (v1.1)

- **Primary thesis set:** `data/splits/primary_theses.json` (excludes isomorphic pad clones).
- **T1** fail-closed (no silent axis=50). **T3–T5** require substance, not format keywords alone.
- Gold remains `provenance: deepresearch-agent` (agent-draft), not multi-lab human panel.
