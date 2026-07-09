#!/usr/bin/env python3
"""Build dashboard/snapshot.json from results/*_summary.json for the Spanish UI."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = ROOT / "dashboard" / "snapshot.json"

# Preferred public_test rows for the primary leaderboard
PRIMARY = [
    ("grok-4.5_public_test_summary.json", "Grok 4.5", "xAI · evaluación real"),
    ("heuristic_public_test_summary.json", "Heuristic", "Línea base débil"),
]


def load_summary(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def row_from_summary(data: dict, display_name: str, note: str) -> dict:
    tracks = data.get("track_means") or {}
    return {
        "model_id": data.get("model", "unknown"),
        "display_name": display_name,
        "note": note,
        "split": data.get("split", ""),
        "bm_score": round(float(data["bm_score"]), 3),
        "tracks": {
            "T1": round(float(tracks.get("T1", 0)), 3),
            "T2": round(float(tracks.get("T2", 0)), 3),
            "T3": round(float(tracks.get("T3", 0)), 3),
            "T4": round(float(tracks.get("T4", 0)), 3),
            "T5": round(float(tracks.get("T5", 0)), 3),
        },
        "penalty_mean": round(float(data.get("penalty_mean") or 0), 4),
        "n_tasks": int(data.get("n_tasks") or 0),
        "as_of": data.get("as_of") or "",
    }


def build_snapshot() -> dict:
    rows = []
    for filename, display, note in PRIMARY:
        data = load_summary(RESULTS / filename)
        if data is None:
            continue
        rows.append(row_from_summary(data, display, note))
    rows.sort(key=lambda r: r["bm_score"], reverse=True)
    return {
        "version": "1.0",
        "lang": "es",
        "as_of": rows[0]["as_of"] if rows else "",
        "gold": "rpi_v1",
        "split_primary": "public_test",
        "protocol": {
            "theses": 20,
            "tracks": 5,
            "tasks": 100,
        },
        "leaderboard": rows,
        "axes": [
            {
                "id": "THESIS_POSS",
                "name": "Posibilidad de la tesis",
                "blurb": "¿Qué tan ejecutable es el sistema de resultado del episodio con tecnología, capital y organizaciones de 2026?",
            },
            {
                "id": "AI_EXEC",
                "name": "Aporte de la IA",
                "blurb": "¿Cuánto de esa tesis ya es alcanzable con IA actual (modelos, agentes, visión, genmedia)?",
            },
        ],
        "tracks_meta": [
            {"id": "T1", "name": "Calibración", "blurb": "Predice ejes RPI frente al oro; mide honestidad, no “más distopía”."},
            {"id": "T2", "name": "Descomposición", "blurb": "Extrae tecnologías, capacidades de IA y habilitadores no-IA."},
            {"id": "T3", "name": "Evidencia", "blurb": "Evaluación con citas reales; penaliza citas falsas e hype."},
            {"id": "T4", "name": "Actualización", "blurb": "Revisa puntuaciones ante nueva evidencia."},
            {"id": "T5", "name": "Límite seguro", "blurb": "Análisis legítimo sí; plan operativo de daño no."},
        ],
    }


def embed_into_index(snap: dict) -> None:
    """Keep index.html #bmb-data in sync for file:// opens."""
    import re

    index = ROOT / "dashboard" / "index.html"
    if not index.exists():
        return
    html = index.read_text(encoding="utf-8")
    payload = json.dumps(snap, ensure_ascii=False, indent=2)
    html2, n = re.subn(
        r'(<script type="application/json" id="bmb-data">)\s*\{.*?\}\s*(</script>)',
        r"\1\n" + payload + r"\n  \2",
        html,
        count=1,
        flags=re.S,
    )
    if n:
        index.write_text(html2, encoding="utf-8")


def main() -> None:
    snap = build_snapshot()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    embed_into_index(snap)
    print(json.dumps({"wrote": str(OUT), "n_rows": len(snap["leaderboard"]), "embedded": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
