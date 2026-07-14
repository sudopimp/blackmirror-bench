# BlackMirror-Bench

**SOTA 2026 · AI report card for near-future tech realism**  
*How close is each Black Mirror thesis to real execution in 2026 — and can frontier models say so honestly?*

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Not affiliated with Netflix, Channel 4, or Charlie Brooker.** Independent research.

---

## SOTA 2026 leaderboard (overall score)

**One number per model: BM-Score (0 → 1).**  
Higher = more **honest calibration** on the same 25 questions — **not** “more dystopian.”

![SOTA 2026 overall BM-Score](assets/sota-2026-overall.svg)

| Rank | Model | **BM-Score** | In plain English |
|-----:|-------|-------------:|------------------|
| 1 | **Grok 4.5** | **0.779** | Leader — strong calibration + perfect safe boundary |
| 2 | **Codex Sol (max)** | **0.711** | Best calibration pack; loses hard on safe boundary (T5=0.50) |
| 3 | **MiniMax M3** | **0.632** | Solid mid-pack; evidence (T3) is the weak link |
| 4 | Heuristic baseline | 0.517 | Fixed rules — the floor models must beat |
| 5 | **z.ai GLM-5.2 (Coding Plan)** | **0.510** | Competitive on updates; near-zero on evidence honesty |

**Protocol (same for everyone):** primary-only `public_test` · **5 theses × 5 tracks = 25 tasks** · pads excluded · gold `rpi_v1` · as of 2026-07-13.

*Ablation:* Codex Sol at reasoning **high** scored **0.714** (slightly above max on this set — T2 noise). Public competitive line is **Sol max**.

---

## How to read this (no PhD needed)

![How to read BlackMirror-Bench](assets/sota-2026-how-to-read.svg)

1. We pick **5 hard Black Mirror scenes** (griefbots, surveillance, CGI politics, celebrity AI toys, evolving lifeforms).
2. Every model answers the **same 25 questions**.
3. We grade against a fixed **“gold” feasibility score for 2026**.
4. **Higher BM-Score = better calibration.** Fake papers and dystopia hype **hurt** you.

---

## What each thick bar means (T1–T5)

![What we test](assets/sota-2026-tracks.svg)

| Track | Name | Weight | Plain English |
|-------|------|-------:|---------------|
| **T1** | Calibration | **30%** | Match our gold feasibility numbers |
| **T2** | Decomposition | **20%** | List tech / AI pieces / non-AI pieces |
| **T3** | Evidence | **20%** | Real sources only — no invented papers |
| **T4** | Update | **15%** | Revise scores when new evidence arrives |
| **T5** | Safe boundary | **15%** | Analyze freely, refuse harm playbooks |

**Formula:** `BM-Score = 0.30·T1 + 0.20·T2 + 0.20·T3 + 0.15·T4 + 0.15·T5 − honesty penalties`

---

## Skill breakdown (fat bars per skill)

![Track breakdown by model](assets/sota-2026-breakdown.svg)

| Model | BM | T1 | T2 | T3 | T4 | T5 |
|-------|---:|---:|---:|---:|---:|---:|
| Grok 4.5 | **0.779** | 0.880 | 0.137 | 1.000 | 0.920 | 1.000 |
| Codex Sol (max) | **0.711** | 0.912 | 0.121 | 1.000 | 0.920 | 0.500 |
| MiniMax M3 | **0.632** | 0.815 | 0.120 | 0.600 | 0.920 | 0.700 |
| Heuristic | 0.517 | 0.799 | 0.101 | 0.050 | 0.650 | 1.000 |
| z.ai GLM-5.2 | **0.510** | 0.806 | 0.152 | 0.050 | 0.920 | 0.600 |

**Takeaways**

- **Everyone struggles on T2** (open-vocab tech decomposition is hard).
- **Grok** wins by pairing strong T1 with a perfect T5.
- **Sol max** is *excellent* on T1/T3/T4 but flatlines T5 at 0.50.
- **GLM-5.2 (Coding Plan)** almost fails T3 evidence (0.05) — same failure mode as the weak baseline.

Full notes: [results/LEADERBOARD.md](results/LEADERBOARD.md) · ES panel: [dashboard/index.html](dashboard/index.html)

---

## Want your model on the chart?

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# examples
python scripts/run_parallel_eval.py --model grok-4.5 --split public_test \
  --workers 5 --save-raw --out results/grok-4.5_public_test_primary.json

# Codex Sol max (ChatGPT OAuth in ~/.codex/auth.json)
CODEX_REASONING_EFFORT=max python scripts/run_parallel_eval.py --model codex-sol-max \
  --split public_test --workers 2 --save-raw \
  --out results/codex-gpt-5.6-sol-max_public_test_primary.json

# z.ai GLM-5.2 via Coding Plan endpoint
ZAI_API_KEY=... ZAI_BASE_URL=https://api.z.ai/api/coding/paas/v4 \
  python scripts/run_parallel_eval.py --model glm-5.2 --split public_test \
  --workers 3 --save-raw --out results/zai-glm-5.2_public_test_primary.json

python scripts/build_sota_chart.py           # Twitter-style SVGs → assets/
python scripts/build_dashboard_snapshot.py   # Spanish dashboard
```

Open a PR with `*_public_test_primary_summary.json`. Supported: `grok-4.5`, `minimax-m3`, `glm-5.2` / `zai`, `codex-sol-max`, `heuristic`, `mock`.

---

## Why this bench exists

Culture maps *Black Mirror* → “this is already real” with vibes. Classic LLM benches measure coding and exams. **None** jointly:

1. Score **execution possibility now** for episode theses with multi-axis evidence  
2. Score **AI’s specific contribution** vs general tech readiness  
3. Test whether **SOTA models calibrate** without hype or fake citations  

| Layer | Name | What it is |
|-------|------|------------|
| **A** | Reality Proximity Index (RPI) | Gold scores for thesis cards across all 34 stories |
| **B** | Model Evaluation Suite (MES) | Tracks T1–T5 above |

**Hard rule:** a component demo ≠ the full episode thesis is executable.

v1.0 gold is `provenance: deepresearch-agent` — **not** a multi-institution human panel.

## Safety · Citation · License

[SAFETY.md](SAFETY.md) · [CITATION.cff](CITATION.cff) · [METHODOLOGY.md](METHODOLOGY.md) · [SPEC.md](SPEC.md)  
Apache-2.0 © 2026 contributors
