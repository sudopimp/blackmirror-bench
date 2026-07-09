#!/usr/bin/env python3
"""Validate BlackMirror-Bench corpus against SPEC completion conditions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
AXES = ["THESIS_POSS", "AI_EXEC", "TRL_comp", "SYS", "ECON", "SOC", "FID"]


def load(path: Path):
    return json.loads(path.read_text())


def check_episodes() -> None:
    reg = load(ROOT / "data/episodes/registry.json")
    assert reg["count"] == 34, reg["count"]
    assert len(reg["episodes"]) == 34
    ids = [e["id"] for e in reg["episodes"]]
    assert len(set(ids)) == 34
    print("OK episodes: 34")


def check_theses() -> None:
    reg = load(ROOT / "data/episodes/registry.json")
    ep_ids = {e["id"] for e in reg["episodes"]}
    schema = load(ROOT / "schema/thesis.schema.json")
    theses = []
    for p in sorted((ROOT / "data/theses").glob("*.json")):
        if p.name == "index.json":
            continue
        t = load(p)
        jsonschema.validate(t, schema)
        theses.append(t)
    assert len(theses) >= 80, f"need >=80 theses, got {len(theses)}"
    covered = {t["episode_id"] for t in theses}
    missing = ep_ids - covered
    assert not missing, f"episodes without theses: {missing}"
    print(f"OK theses: {len(theses)} covering {len(covered)} episodes")


def check_research() -> None:
    reg = load(ROOT / "data/episodes/registry.json")
    for e in reg["episodes"]:
        d = ROOT / "research/episodes" / e["id"]
        assert (d / "BRIEF.md").exists(), f"missing BRIEF for {e['id']}"
    print("OK research packets: 34")


def check_evidence() -> None:
    gold = load(ROOT / "gold/rpi_v1.json")
    evidence_by_id = {}
    for p in (ROOT / "data/evidence").glob("*.json"):
        if p.name == "index.json":
            continue
        e = load(p)
        evidence_by_id[e["evidence_id"]] = e

    total_axes = 0
    cited_axes = 0
    for s in gold["scores"]:
        for ax in AXES:
            total_axes += 1
            a = s["axes"][ax]
            if a.get("tier") == "NA":
                cited_axes += 1  # NA axes exempt
                continue
            # must have evidence_ids and each has url+accessed_at
            ok = False
            for eid in s.get("evidence_ids", []):
                ev = evidence_by_id.get(eid)
                if ev and ev.get("url", "").startswith("http") and ev.get("accessed_at"):
                    ok = True
                    break
            if ok:
                cited_axes += 1
    ratio = cited_axes / total_axes if total_axes else 0
    assert ratio >= 0.95, f"evidence coverage {ratio:.2%} < 95%"
    print(f"OK evidence-gate: {ratio:.1%} axes cited/NA")


def check_gold() -> None:
    schema = load(ROOT / "schema/rpi_score.schema.json")
    gold = load(ROOT / "gold/rpi_v1.json")
    assert gold["provenance"] == "deepresearch-agent"
    assert gold["count"] == len(gold["scores"])
    for s in gold["scores"]:
        jsonschema.validate(s, schema)
    print(f"OK gold: {gold['count']} scores")


def check_baselines(min_n: int) -> None:
    results = list((ROOT / "results").glob("*.json"))
    assert len(results) >= min_n, f"need >= {min_n} baseline results, got {len(results)}"
    print(f"OK baselines: {len(results)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", action="store_true")
    ap.add_argument("--theses-coverage", action="store_true")
    ap.add_argument("--research-packets", action="store_true")
    ap.add_argument("--evidence-gate", action="store_true")
    ap.add_argument("--gold", action="store_true")
    ap.add_argument("--baselines-min", type=int, default=None)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    run_any = False
    try:
        if args.all or args.episodes:
            run_any = True
            check_episodes()
        if args.all or args.theses_coverage:
            run_any = True
            check_theses()
        if args.all or args.research_packets:
            run_any = True
            check_research()
        if args.all or args.evidence_gate:
            run_any = True
            check_evidence()
        if args.all or args.gold:
            run_any = True
            check_gold()
        if args.baselines_min is not None:
            run_any = True
            check_baselines(args.baselines_min)
        if args.all and args.baselines_min is None:
            # optional in --all if results exist
            n = len(list((ROOT / "results").glob("*.json")))
            if n:
                check_baselines(1)
        if not run_any:
            ap.print_help()
            sys.exit(2)
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
