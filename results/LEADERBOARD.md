# BlackMirror-Bench Leaderboard (local baselines)

**as_of:** 2026-07-09 · **gold:** `rpi_v1` · **split notes:** see filenames

| Model | Split | BM-Score | T1 | T2 | T3 | T4 | T5 | n_tasks |
|-------|-------|----------|----|----|----|----|----|---------|
| mock (gold-aware ceiling baseline) | public_dev | ~0.98 | 1.00 | 1.00 | 0.95 | 0.90 | 1.00 | 340 |
| heuristic | public_dev (limit 50/track) | ~0.58 | ~0.78 | ~0.10 | 0.20 | 0.90 | 1.00 | 250 |
| random_mid | public_test (limit 30/track) | ~0.57 | ~0.74 | ~0.11 | 0.20 | 0.90 | 1.00 | 100 |

Re-run:

```bash
python -m harness.runner --model mock --split public_dev --out results/mock_public_dev.json
python -m harness.runner --model heuristic --split public_dev --out results/heuristic_public_dev.json
```

**Note:** `mock` is intentionally gold-aware for harness smoke tests — not a claim about real model capability. Submit real API/local models via provider extensions.
