# BlackMirror-Bench: Measuring Socio-Technical Feasibility and Model Calibration on the Black Mirror Corpus

**Draft v1.0 · 2026-07-09 · waitdeadai**  
*Not affiliated with Netflix, Channel 4, or Charlie Brooker.*

## Abstract

We introduce **BlackMirror-Bench**, an open benchmark that (i) estimates how executable each *Black Mirror* episode thesis is in 2026 using multi-axis, evidence-backed scores, and (ii) evaluates whether frontier language models recover those judgments without hype or fabricated evidence. The corpus covers all 34 stories (33 episodes + *Bandersnatch*). Each story is decomposed into thesis cards (≥80 total). Co-primary axes are **thesis possibility now** (`THESIS_POSS`) and **AI contribution** (`AI_EXEC`), complemented by TRL, system integration, economics, socio-legal deployability, and fidelity. Model tracks T1–T5 measure calibration, decomposition, citation honesty, evidence updates, and safe-analysis boundaries. Anti-dark-pattern penalties target hype inflation, sci-fi collapse, and fake citations—aligned with the waitdeadai evaluation ethos.

## 1. Introduction

Popular media routinely equates cultural dystopias with “already real” technology. Simultaneously, standard LLM benchmarks (coding, exams, abstract reasoning) do not measure honest socio-technical feasibility judgment. BlackMirror-Bench fills this gap with a fixed, widely known corpus and a dual-layer design: a Reality Proximity Index (RPI) and a Model Evaluation Suite (MES).

## 2. Related work

We build on Technology Readiness Levels (NASA/DoD), METR time-horizon thinking for AI capability, contamination-aware eval design (LiveBench et al.), agent safety benches (AgentHarm, OS-Harm), and honesty/dark-pattern evaluation (DarkBench; waitdeadai llm-dark-patterns).

## 3. Corpus and thesis cards

Titles follow the Wikipedia featured list *List of Black Mirror episodes* (accessed 2026-07-09). Stories are split into thesis cards so multi-technology episodes (e.g. *White Christmas*) are not collapsed into a single dishonest scalar.

## 4. Scoring axes

See METHODOLOGY.md. Critical rule: **component readiness ≠ thesis executability**. Supernatural cores (e.g. *Demon 79*) use `NA` tiers rather than forced TRLs.

## 5. Model evaluation

| Track | Skill |
|-------|--------|
| T1 | Multi-axis calibration (MAE / mapped score) |
| T2 | Tech/AI/non-AI decomposition (set F1) |
| T3 | Evidence honesty (URLs + anti-fake-cite) |
| T4 | Score updates under new evidence |
| T5 | Analysis vs operational harm boundary |

## 6. Limitations

v1.0 gold is agent-deepresearch with explicit provenance—not a large human expert panel. Private splits and quarterly refresh mitigate contamination. Dual-use risk is mitigated via SAFETY.md and T5 design.

## 7. Conclusion

BlackMirror-Bench provides an open, time-anchored, honesty-first benchmark for 2026 socio-technical feasibility and model calibration on a complete Black Mirror corpus.

## References

See evidence ledger URLs in `data/evidence/` and research packets in `research/episodes/`.
