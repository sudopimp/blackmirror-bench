"""Schema validation smoke tests."""

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]


def test_sample_thesis_schema():
    schema = json.loads((ROOT / "schema/thesis.schema.json").read_text())
    theses = list((ROOT / "data/theses").glob("s01e01*.json"))
    assert theses
    for p in theses:
        jsonschema.validate(json.loads(p.read_text()), schema)


def test_gold_schema_sample():
    schema = json.loads((ROOT / "schema/rpi_score.schema.json").read_text())
    gold = json.loads((ROOT / "gold/rpi_v1.json").read_text())
    jsonschema.validate(gold["scores"][0], schema)
