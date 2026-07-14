# BlackMirror-Bench Leaderboard

**Gold:** `rpi_v1` · **as_of:** 2026-07-13  
**Primary protocol:** `public_test` · **primary-only** · **5 theses · 5 tracks · 25 tasks** · pads excluded  
**Primary set size:** 20 theses (`data/splits/primary_theses.json`)

| Model | Split | Scope | BM-Score | T1 | T2 | T3 | T4 | T5 | n | Notes |
|-------|-------|-------|----------|----|----|----|----|-----|---|-------|
| **grok-4.5** | **public_test** | **primary_only** | **0.779** | 0.880 | 0.137 | 1.000 | 0.920 | 1.000 | **25** | xAI · construct-valid scorers v1.1 |
| **codex-gpt-5.6-sol** | **public_test** | **primary_only** | **0.714** | 0.917 | 0.158 | 1.000 | 0.880 | 0.500 | **25** | ChatGPT OAuth · reasoning high |
| **minimax-m3** | **public_test** | **primary_only** | **0.632** | 0.815 | 0.120 | 0.600 | 0.920 | 0.700 | **25** | MiniMax API · primary-only |
| heuristic | public_test | primary_only | 0.517 | 0.799 | 0.101 | 0.050 | 0.650 | 1.000 | **25** | Weak baseline |
| z.ai glm-4.5 | — | — | — | — | — | — | — | — | — | **Skipped** (API insufficient balance) |
| ~~mock (gold-aware)~~ | — | — | — | — | — | — | — | — | — | **Not ranked** |

## How to read this (non-technical)

Think of BlackMirror-Bench as a **report card for AI models**, not a horror contest.

1. We pick five hard “what if” scenes from *Black Mirror* (parental surveillance, griefbots, political CGI, celebrity AI toys, evolving lifeforms).
2. Each model answers **five kinds of questions** about each scene (25 answers total).
3. We grade them against a fixed “gold” feasibility score for 2026.
4. **Higher BM-Score = more honest and better calibrated**, not “more dystopian.”

| Track | Plain-language job |
|-------|--------------------|
| **T1** | Guess the same feasibility numbers as the gold standard |
| **T2** | Name the tech / AI pieces / non-AI pieces that make the scene work |
| **T3** | Cite real evidence without inventing papers or links |
| **T4** | Update scores when new evidence appears |
| **T5** | Analyze freely, but **refuse** step-by-step harm plans |

**First multi-model chart:** open [`dashboard/index.html`](../dashboard/index.html) (or GitHub Pages / local file). Bars compare BM-Score side by side.

### Want to participate?

1. Clone [sudopimp/blackmirror-bench](https://github.com/sudopimp/blackmirror-bench).
2. Run primary-only `public_test` (25 tasks) with your model provider.
3. Open a PR or issue with `*_public_test_primary_summary.json` + method note.
4. We will re-score or spot-check raw outputs when available.

```bash
python scripts/run_parallel_eval.py --model <your-model> --split public_test \
  --workers 4 --save-raw --out results/<your-model>_public_test_primary.json
```

Supported out of the box: `grok-4.5`, `minimax-m3`, `zai`, `codex-sol` (ChatGPT OAuth), plus `heuristic` / `mock` for dry runs.

## Legacy (pre-primary / pad-era) — not comparable

| Model | Split | BM-Score | n | Notes |
|-------|-------|----------|---|-------|
| grok-4.5 | public_test (legacy) | 0.773 | 100 | Pad-era · old scorers · [REPORT](REPORT_grok-4.5.md) |
| heuristic | public_test (legacy) | 0.571 | 100 | Pad-era · format-theater T3–T5 |

## How to read scores (v1.1, technical)

- **T1** multi-axis calibration; fail-closed if axes missing.  
- **T2** tech/AI/non-AI decomposition (open-vocab; hard).  
- **T3** URL **and** claim substance.  
- **T4** deltas + reason + sign coherence.  
- **T5** analysis + explicit operational refuse.  
- Runner scores **only** primary thesis_ids.

## Reproduce (primary-only)

```bash
# Grok (needs XAI_API_KEY or ~/.grok/auth.json)
python scripts/run_parallel_eval.py --model grok-4.5 --split public_test \
  --workers 5 --save-raw --out results/grok-4.5_public_test_primary.json

# MiniMax M3 (MINIMAX_API_KEY)
python scripts/run_parallel_eval.py --model minimax-m3 --split public_test \
  --workers 4 --save-raw --out results/minimax-m3_public_test_primary.json

# Codex Sol via ChatGPT OAuth (~/.codex/auth.json)
CODEX_REASONING_EFFORT=high python scripts/run_parallel_eval.py --model codex-sol \
  --split public_test --workers 3 --save-raw \
  --out results/codex-gpt-5.6-sol_public_test_primary.json

# Rebuild Spanish dashboard + chart
python scripts/build_dashboard_snapshot.py
```
