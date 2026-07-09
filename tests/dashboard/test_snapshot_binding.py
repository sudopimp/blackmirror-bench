"""Tests for dashboard score binding — drives real build_dashboard_snapshot code."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_dashboard_snapshot import (  # noqa: E402
    PRIMARY,
    build_snapshot,
    load_summary,
    row_from_summary,
)


def test_row_from_summary_maps_real_grok_file():
    path = ROOT / "results" / "grok-4.5_public_test_summary.json"
    assert path.exists(), "published grok summary must exist"
    data = load_summary(path)
    assert data is not None
    row = row_from_summary(data, "Grok 4.5", "xAI · evaluación real")
    assert row["model_id"] == "grok-4.5"
    assert row["display_name"] == "Grok 4.5"
    # Real published BM-Score ~0.773
    assert 0.77 <= row["bm_score"] <= 0.78
    assert row["tracks"]["T5"] == 1.0
    assert row["tracks"]["T1"] >= 0.85
    assert row["n_tasks"] == 100
    assert row["split"] == "public_test"


def test_build_snapshot_sorted_and_spanish_meta():
    snap = build_snapshot()
    assert snap["lang"] == "es"
    assert snap["gold"] == "rpi_v1"
    assert len(snap["leaderboard"]) >= 2
    # sorted descending by bm_score
    scores = [r["bm_score"] for r in snap["leaderboard"]]
    assert scores == sorted(scores, reverse=True)
    assert snap["leaderboard"][0]["model_id"] == "grok-4.5"
    # axes & tracks labeled in Spanish
    assert any("Posibilidad" in a["name"] for a in snap["axes"])
    assert any("Calibración" in t["name"] for t in snap["tracks_meta"])


def test_snapshot_json_on_disk_matches_builder():
    """Regenerate path: file on disk is what UI embeds."""
    snap = build_snapshot()
    disk = json.loads((ROOT / "dashboard" / "snapshot.json").read_text(encoding="utf-8"))
    assert disk["leaderboard"][0]["bm_score"] == snap["leaderboard"][0]["bm_score"]
    assert disk["leaderboard"][0]["model_id"] == "grok-4.5"


def test_primary_files_exist():
    for filename, _, _ in PRIMARY:
        assert (ROOT / "results" / filename).exists(), filename
