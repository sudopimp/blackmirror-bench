"""Ensure all MES tracks have tasks."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TRACKS = [
    "tasks/t1_calibration/tasks.jsonl",
    "tasks/t2_decomposition/tasks.jsonl",
    "tasks/t3_evidence/tasks.jsonl",
    "tasks/t4_update/tasks.jsonl",
    "tasks/t5_boundary/tasks.jsonl",
]


def test_tracks_nonempty():
    for rel in TRACKS:
        path = ROOT / rel
        assert path.exists(), rel
        lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
        assert len(lines) >= 80, f"{rel} has {len(lines)}"
