# SPEC — BlackMirror-Bench v1.0

**Goal:** Open, evidence-backed benchmark that (A) scores how executable every Black Mirror thesis is in 2026 with honest multi-axis data, and (B) tests whether SOTA models recover those scores without hype or fabricated evidence.

**Org:** waitdeadai · **License:** Apache-2.0  
**Not affiliated with Netflix, Channel 4, or Charlie Brooker.**

## Completion conditions

| # | Condition | verifyHint |
|---|-----------|------------|
| 1 | Registry lists exactly the 34 canon episode/film IDs | `python scripts/validate_corpus.py --episodes` exit 0 |
| 2 | Every episode has ≥1 thesis; total theses ≥40; **primary** set excludes pad clones | `python scripts/validate_corpus.py --theses-coverage` + `--primary-honesty` |
| 3 | Research packet dir exists for all 34 with BRIEF.md | `python scripts/validate_corpus.py --research-packets` |
| 4 | ≥95% of scored axis fields have ≥1 URL + accessed_at | `python scripts/validate_corpus.py --evidence-gate` |
| 5 | `gold/rpi_v1.json` schema-valid with provenance labeled | `python scripts/validate_corpus.py --gold` |
| 6 | T1–T5 public_dev non-empty and tests pass | `pytest tests/tasks -q` |
| 7 | Mock harness run produces score JSON | `python -m harness.runner --model mock --split public_dev` |
| 8 | ≥3 baseline result files in `results/` | `python scripts/validate_corpus.py --baselines-min 3` |
| 9 | Hype / fake-cite / sci-fi-collapse penalties unit-tested | `pytest tests/metrics/test_penalties.py -q` |
| 10 | Public tasks pass safety scan | `python scripts/safety_scan.py` exit 0 |
| 11 | README, METHODOLOGY, SAFETY, LICENSE, CITATION.cff exist; Netflix disclaimer present | files + `rg -n "not affiliated with Netflix" README.md` |
| 12 | HF export dry-run succeeds | `python scripts/export_hf.py --dry-run` |

**DONE when all 12 pass.**

## Non-goals

- Operational harm recipes, exploit chains, weaponization playbooks
- Redistribution of episode scripts/video
- Single clickbait “% dystopia complete” as the only published number

## Co-primary axes

- `THESIS_POSS` — can the episode outcome system be executed now?
- `AI_EXEC` — how much of that is achievable by current AI systems?
