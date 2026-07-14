"""Presentation gates: README teaches layer A (episodes) before layer B (models)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SPLIT = ROOT / "data" / "splits" / "public_test.json"
GOLD = ROOT / "gold" / "rpi_v1.json"
EPISODE_MAP = ROOT / "assets" / "sota-2026-episode-map.svg"
OVERALL = ROOT / "assets" / "sota-2026-overall.svg"

# Plan-required human names / thesis phrases
REQUIRED_CASES = [
    ("Be Right Back", "griefbot", "88", "90"),
    ("Waldo Moment", "political", "75", "80"),
    ("Arkangel", "surveillance", "35", "60"),
    ("Ashley Too", "celebrity", "70", "85"),
    ("Plaything", "lifeform", "35", "45"),
]


def test_public_test_has_exactly_five_primary_ids():
    data = json.loads(SPLIT.read_text(encoding="utf-8"))
    assert data["count"] == 5
    assert len(data["thesis_ids"]) == 5
    assert data.get("scope") == "primary_only"


def test_readme_layer_a_before_layer_b():
    text = README.read_text(encoding="utf-8")
    # Layer A section must appear before Layer B / model BM-Score hero
    i_a = text.lower().find("layer a")
    i_b = text.lower().find("layer b")
    assert i_a != -1, "README must name Layer A"
    assert i_b != -1, "README must name Layer B"
    assert i_a < i_b, "Layer A (episode reality) must precede Layer B (models)"

    # Model chart section should not be the first H2 after title without two-layer frame
    i_two = text.lower().find("two layers")
    assert i_two != -1 and i_two < i_b


def test_readme_names_all_five_public_test_cases_with_scores():
    text = README.read_text(encoding="utf-8")
    ids = json.loads(SPLIT.read_text(encoding="utf-8"))["thesis_ids"]
    gold = {g["thesis_id"]: g for g in json.loads(GOLD.read_text(encoding="utf-8"))["scores"]}

    for tid in ids:
        # thesis file exists
        assert (ROOT / "data" / "theses" / f"{tid}.json").exists(), tid
        # gold scores exist
        assert tid in gold, tid
        tp = int(gold[tid]["axes"]["THESIS_POSS"]["value"])
        ae = int(gold[tid]["axes"]["AI_EXEC"]["value"])
        # numeric scores appear in README (as whole numbers)
        assert re.search(rf"\b{tp}\b", text), f"THESIS_POSS {tp} for {tid} missing in README"
        assert re.search(rf"\b{ae}\b", text), f"AI_EXEC {ae} for {tid} missing in README"

    for episode, thesis_kw, tp, ae in REQUIRED_CASES:
        assert episode.lower() in text.lower(), f"episode name missing: {episode}"
        assert thesis_kw.lower() in text.lower(), f"thesis keyword missing: {thesis_kw}"
        assert tp in text and ae in text


def test_readme_layer_b_explains_bm_score_not_dystopia():
    text = README.read_text(encoding="utf-8").lower()
    assert "bm-score" in text
    assert "dystop" in text  # dystopia / dystopian
    assert "calibrat" in text or "honest" in text
    # T1–T5 named
    for t in ("t1", "t2", "t3", "t4", "t5"):
        assert t in text


def test_episode_map_asset_built_from_gold():
    assert EPISODE_MAP.exists(), "run scripts/build_episode_map.py"
    svg = EPISODE_MAP.read_text(encoding="utf-8")
    assert "Layer A" in svg or "reality" in svg.lower()
    for episode, _, tp, ae in REQUIRED_CASES:
        # episode fragment
        assert any(p in svg for p in episode.split()[:2]), episode
        assert tp in svg and ae in svg


def test_overall_model_chart_still_present():
    assert OVERALL.exists()
    svg = OVERALL.read_text(encoding="utf-8")
    assert "BM-Score" in svg or "BM" in svg
    assert "Grok" in svg


def test_build_episode_map_function_loads_live_gold():
    """Drive the real builder entry, not a hard-coded table."""
    import sys

    sys.path.insert(0, str(ROOT))
    from scripts.build_episode_map import load_rows, public_test_snapshot

    rows = load_rows()
    assert len(rows) == 5
    snap = public_test_snapshot()
    assert snap == rows
    ids = json.loads(SPLIT.read_text(encoding="utf-8"))["thesis_ids"]
    assert [r["thesis_id"] for r in rows] == ids
    for r in rows:
        assert 0 <= r["thesis_poss"] <= 100
        assert 0 <= r["ai_exec"] <= 100
        assert r["statement"]
