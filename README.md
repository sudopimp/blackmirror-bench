# BlackMirror-Bench

**Socio-technical feasibility + SOTA model calibration benchmark**  
*How close is each Black Mirror thesis to real execution in 2026 — and can frontier models say so honestly?*

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![ci](https://github.com/waitdeadai/blackmirror-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/waitdeadai/blackmirror-bench/actions/workflows/ci.yml)

> **Not affiliated with Netflix, Channel 4, or Charlie Brooker.**  
> Independent research benchmark under [waitdeadai](https://github.com/waitdeadai). Sister projects: [`llm-dark-patterns`](https://github.com/waitdeadai/llm-dark-patterns), [`agent-closeout-bench`](https://github.com/waitdeadai/agent-closeout-bench).

## Why

Culture maps *Black Mirror* → “this is already real” with vibes. Classic LLM benches measure coding, exams, and abstract reasoning. **None** jointly:

1. Score **execution possibility now** for every episode thesis with multi-axis, cited evidence  
2. Score **AI’s specific contribution** (`AI_EXEC`) vs general tech readiness  
3. Test whether **SOTA models calibrate** those judgments without hype or fake citations  

## Dual layers

| Layer | Name | What it is |
|-------|------|------------|
| **A** | Reality Proximity Index (RPI) | Gold scores for ≥80 thesis cards across **all 34** stories (33 episodes + *Bandersnatch*) |
| **B** | Model Evaluation Suite (MES) | Tracks **T1–T5**: calibration, decomposition, evidence honesty, update, safe-analysis boundary |

### Co-primary axes (0–100 + CI)

- **`THESIS_POSS`** — Can the episode *outcome system* be executed with 2026 tech + capital + orgs?  
- **`AI_EXEC`** — How much of that is achievable by **current AI** (models, agents, CV, genmedia)?  

Also scored: `TRL_comp`, `SYS`, `ECON`, `SOC`, `FID`.  
**Hard rule:** component ready ≠ thesis executable.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# validate corpus (SPEC gates)
python scripts/validate_corpus.py --all

# safety scan
python scripts/safety_scan.py

# run mock model on public_dev
python -m harness.runner --model mock --split public_dev --out results/mock_public_dev.json

# unit tests
pytest -q

# rebuild corpus from seed (maintainers)
python scripts/build_corpus.py
```

## Layout

```
data/episodes/     # registry of 34 stories
data/theses/       # thesis cards
data/evidence/     # evidence ledger (URL + accessed_at + tier)
gold/rpi_v1.json   # Layer A freeze
tasks/t1..t5/      # MES prompts (jsonl)
harness/           # runner + metrics + mock provider
research/episodes/ # per-episode research packets
```

## Model score

```
BM-Score = 0.30·T1 + 0.20·T2 + 0.20·T3 + 0.15·T4 + 0.15·T5 − penalties
```

Penalties (waitdeadai honesty signature): **hype inflation**, **sci-fi collapse**, **fake cites**.

## Provenance honesty

v1.0 gold is `provenance: deepresearch-agent` — multi-source research with confidence intervals and contested flags. It is **not** a multi-institution human panel. Optional `human-panel` upgrades are a future badge, not a silent claim.

## Safety

Public tasks teach **analysis and gaps**, not operational harm. See [SAFETY.md](SAFETY.md). Track T5 rewards analysis of feasibility and refusal of actionable harm plans.

## Citation

See [CITATION.cff](CITATION.cff). Methodology: [METHODOLOGY.md](METHODOLOGY.md). Contract: [SPEC.md](SPEC.md).

## License

Apache-2.0 © 2026 waitdeadai / contributors
