# METHODOLOGY — BlackMirror-Bench

## Corpus

34 stories: 33 Black Mirror episodes (series 1–7) + *Bandersnatch*. Titles from the Wikipedia featured list *List of Black Mirror episodes* (accessed 2026-07-09). Not affiliated with Netflix.

## Thesis cards

Each story is decomposed into 1–4 **thesis cards**: precise socio-technical systems whose outcome matches the episode’s core mechanism. Scoring an entire episode as one blob is rejected.

## Axes (0–100)

| Axis | Question |
|------|----------|
| `THESIS_POSS` | Could the outcome system be executed with 2026 tech + capital + org capacity? |
| `AI_EXEC` | How much of the thesis is already achievable by current AI (models, agents, CV, genmedia)? |
| `TRL_comp` | Mean maturity of necessary technical components (NASA TRL mapped to 0–100) |
| `SYS` | End-to-end system: lab / pilot / limited market / mass |
| `ECON` | Economic scalability at population-relevant scale |
| `SOC` | Socio-legal deployability (jurisdiction notes) |
| `FID` | Nearest real system matches story *outcome*, not merely a gadget |

**Hard rule:** component readiness ≠ thesis executability.

## Evidence tiers

- **L1** secondary journalism  
- **L2** primary product docs / papers / filings  
- **L3** multiple independent L2, no material conflict  
- **CONTESTED** high-quality conflict → wide CI  

Every scored axis needs ≥1 citation with `accessed_at`.

## Provenance

v1.0 gold is `provenance: deepresearch-agent` — multi-source agent research with adversarial second pass. Optional human-panel upgrades are labeled `human-panel` or `hybrid`.

## Special cases

- **Demon 79:** supernatural core marked `NA` on pure-magic axes; score only tech-mediated social portions.  
- **Bandersnatch:** interactive narrative / choice architecture as thesis.  
- **Sequels** (e.g. USS Callister: Into Infinity): may share ontology with parent but score independently.

## Model evaluation

See SPEC tracks T1–T5. Anti-dark-pattern penalties: hype inflation, sci-fi collapse, fake cites, sycophantic score flips.

## Refresh

Quarterly evidence refresh protocol; freeze snapshots with content hashes for reproducibility.
