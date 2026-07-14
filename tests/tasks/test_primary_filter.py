"""Primary set is wired into splits + runner filter (no pad scoring on public_test)."""

from __future__ import annotations

import json
from pathlib import Path

from harness.runner import TRACK_FILES, load_jsonl, load_primary_thesis_ids

ROOT = Path(__file__).resolve().parents[2]


def test_primary_excludes_pads_and_wiki_only_via_gold():
    primary = load_primary_thesis_ids()
    assert len(primary) >= 15
    for tid in primary:
        assert "partial-real-world-analogue" not in tid
        assert "full-fidelity-gap" not in tid
    gold = json.loads((ROOT / "gold/rpi_v1.json").read_text())
    scores = {s["thesis_id"]: s for s in gold["scores"]}
    ev = {}
    for p in (ROOT / "data/evidence").glob("*.json"):
        if p.name == "index.json":
            continue
        e = json.loads(p.read_text())
        ev[e["evidence_id"]] = e.get("url") or ""
    for tid in primary:
        sc = scores[tid]
        urls = [ev.get(eid, "") for eid in sc.get("evidence_ids") or []]
        urls = [u for u in urls if u]
        assert urls, tid
        assert any("wikipedia.org" not in u for u in urls), tid


def test_public_test_is_primary_only_no_pads():
    primary = load_primary_thesis_ids()
    pt = json.loads((ROOT / "data/splits/public_test.json").read_text())
    assert pt.get("scope") == "primary_only"
    assert pt["count"] == len(pt["thesis_ids"])
    for tid in pt["thesis_ids"]:
        assert tid in primary
        assert "partial-real-world-analogue" not in tid
        assert "full-fidelity-gap" not in tid


def test_runner_public_test_task_load_has_zero_pads():
    primary = load_primary_thesis_ids()
    for path in TRACK_FILES.values():
        tasks = [
            t
            for t in load_jsonl(path)
            if t.get("split") == "public_test" and t.get("thesis_id") in primary
        ]
        assert tasks
        pads = [
            t["thesis_id"]
            for t in tasks
            if "partial-real-world-analogue" in t["thesis_id"]
            or "full-fidelity-gap" in t["thesis_id"]
        ]
        assert pads == []
        # fraction of pad-like would be 0
        assert all(t["thesis_id"] in primary for t in tasks)
