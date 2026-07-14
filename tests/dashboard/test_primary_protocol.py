"""Dashboard snapshot protocol matches primary-only public_test."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_snapshot_protocol_matches_primary_public_test():
    pt = json.loads((ROOT / "data/splits/public_test.json").read_text())
    snap = json.loads((ROOT / "dashboard/snapshot.json").read_text())
    expected = int(pt["count"]) * 5
    assert snap["protocol"]["theses"] == pt["count"]
    assert snap["protocol"]["tasks"] == expected
    assert snap["protocol"].get("scope") == "primary_only" or pt.get("scope") == "primary_only"
    for row in snap["leaderboard"]:
        assert row["n_tasks"] == expected
        assert row["n_tasks"] != 100


def test_heuristic_public_test_summary_is_primary_n():
    pt = json.loads((ROOT / "data/splits/public_test.json").read_text())
    s = json.loads((ROOT / "results/heuristic_public_test_summary.json").read_text())
    assert s["n_tasks"] == pt["count"] * 5
    assert s["split"] == "public_test"
