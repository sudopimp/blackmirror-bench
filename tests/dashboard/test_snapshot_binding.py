"""Tests for dashboard score binding — drives real build_dashboard_snapshot code."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_dashboard_snapshot import (  # noqa: E402
    CANDIDATES,
    build_snapshot,
    load_summary,
    protocol_from_splits,
    row_from_summary,
)


def test_row_from_summary_maps_primary_heuristic():
    path = ROOT / "results" / "heuristic_public_test_summary.json"
    assert path.exists()
    data = load_summary(path)
    assert data is not None
    row = row_from_summary(data, "Heuristic", "primary-only")
    assert row["model_id"] == "heuristic"
    assert row["n_tasks"] == protocol_from_splits()["tasks"]
    assert row["n_tasks"] != 100
    assert row["split"] == "public_test"
    assert 0.0 < row["bm_score"] < 1.0


def test_build_snapshot_primary_protocol_no_stale_n100():
    snap = build_snapshot()
    proto = protocol_from_splits()
    assert snap["lang"] == "es"
    assert snap["gold"] == "rpi_v1"
    assert snap["protocol"]["tasks"] == proto["tasks"]
    assert snap["protocol"]["theses"] == proto["theses"]
    assert snap["protocol"]["tasks"] == 25
    assert len(snap["leaderboard"]) >= 1
    for row in snap["leaderboard"]:
        assert row["n_tasks"] == proto["tasks"]
        assert row["n_tasks"] != 100
    scores = [r["bm_score"] for r in snap["leaderboard"]]
    assert scores == sorted(scores, reverse=True)
    assert any("Posibilidad" in a["name"] for a in snap["axes"])
    assert any("Calibración" in t["name"] for t in snap["tracks_meta"])


def test_snapshot_json_on_disk_matches_builder():
    snap = build_snapshot()
    disk = json.loads((ROOT / "dashboard" / "snapshot.json").read_text(encoding="utf-8"))
    assert disk["protocol"]["tasks"] == snap["protocol"]["tasks"]
    assert disk["leaderboard"][0]["n_tasks"] == snap["leaderboard"][0]["n_tasks"]
    assert disk["leaderboard"][0]["bm_score"] == snap["leaderboard"][0]["bm_score"]


def test_candidates_prefer_primary_summaries():
    names = [f for f, _, _ in CANDIDATES]
    assert "heuristic_public_test_summary.json" in names
