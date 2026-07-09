# SAFETY — BlackMirror-Bench

## Purpose

This benchmark measures **feasibility assessment** and **model honesty** about socio-technical dystopias. It is not a how-to for implementing harm.

## Allowed content

- Scholarly / analytical discussion of technologies and social systems
- Public product names, papers, news, regulatory filings
- Gap analysis: what is missing for full thesis fidelity
- Policy and ethics framing
- Model refusal evaluation for **operational** harm requests

## Disallowed in public tasks and gold rationales

- Step-by-step instructions to build weapons, autonomous lethal systems for misuse, or non-consensual surveillance deployments
- Exploit chains, malware, credential theft, doxxing playbooks
- Detailed instructions to commit crimes depicted in episodes
- Personal data of real private individuals

## Track T5 design

T5 scores whether models:

1. Provide high-quality **analysis** when asked about feasibility (should NOT over-refuse)
2. Refuse or redirect when asked for **actionable operational** plans for harm

Success is **not** “always refuse Black Mirror topics.” Success is calibrated boundaries.

## Dual-use acknowledgment

Discussing swarm drones, social scoring, or griefbots can inform both researchers and bad actors. We mitigate by:

- Keeping tasks at architecture / societal / gap level
- Safety scanning public JSON before release
- Clear provenance and non-operational framing

## Incident response

If a public task is found to contain operational harm content, open an issue, remove or rewrite the task, and cut a patch release.
