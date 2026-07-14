#!/usr/bin/env python3
"""Build dashboard/snapshot.json from results/*_summary.json for the Spanish UI."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SPLITS = ROOT / "data" / "splits"
OUT = ROOT / "dashboard" / "snapshot.json"

# Primary leaderboard: only primary-only public_test summaries with matching n_tasks.
# Ranked by BM-Score after load. Include real models + weak baseline.
CANDIDATES = [
    ("heuristic_public_test_summary.json", "Heuristic", "Baseline débil · reglas fijas"),
    ("grok-4.5_public_test_primary_summary.json", "Grok 4.5", "xAI · primary-only"),
    ("minimax-m3_public_test_primary_summary.json", "MiniMax M3", "MiniMax · primary-only"),
    (
        "codex-gpt-5.6-sol_public_test_primary_summary.json",
        "Codex GPT-5.6 Sol",
        "OpenAI ChatGPT OAuth · reasoning high",
    ),
    (
        "zai-glm-4.5_public_test_primary_summary.json",
        "z.ai GLM-4.5",
        "Zhipu · primary-only",
    ),
]


def load_summary(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def protocol_from_splits() -> dict:
    pt = json.loads((SPLITS / "public_test.json").read_text(encoding="utf-8"))
    n_theses = int(pt.get("count") or len(pt.get("thesis_ids") or []))
    return {
        "theses": n_theses,
        "tracks": 5,
        "tasks": n_theses * 5,
        "scope": pt.get("scope") or "primary_only",
    }


def row_from_summary(data: dict, display_name: str, note: str) -> dict:
    tracks = data.get("track_means") or {}
    return {
        "model_id": data.get("model", "unknown"),
        "display_name": display_name,
        "note": note,
        "split": data.get("split", ""),
        "scope": data.get("scope") or "primary_only",
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
    proto = protocol_from_splits()
    expected_n = proto["tasks"]
    rows = []
    for filename, display, note in CANDIDATES:
        data = load_summary(RESULTS / filename)
        if data is None:
            continue
        # Reject stale pad-era summaries (wrong n_tasks)
        n = int(data.get("n_tasks") or 0)
        if n != expected_n:
            continue
        if data.get("split") not in ("public_test", ""):
            continue
        rows.append(row_from_summary(data, display, note))
    rows.sort(key=lambda r: r["bm_score"], reverse=True)
    return {
        "version": "1.1",
        "lang": "es",
        "as_of": rows[0]["as_of"] if rows else "",
        "gold": "rpi_v1",
        "split_primary": "public_test",
        "protocol": proto,
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
            {"id": "T3", "name": "Evidencia", "blurb": "URL + sustancia de claims; no basta un enlace suelto."},
            {"id": "T4", "name": "Actualización", "blurb": "Deltas con razón y coherencia de signo; no solo keys JSON."},
            {"id": "T5", "name": "Límite seguro", "blurb": "Análisis sí; plan operativo de daño no (sin atajos de etiqueta)."},
        ],
        "legacy_note": (
            "Filas pre-primary (n=100, pad-era) no se listan. "
            "Ver results/LEADERBOARD.md § Legacy."
        ),
    }


def embed_into_index(snap: dict) -> None:
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
    print(
        json.dumps(
            {
                "wrote": str(OUT),
                "n_rows": len(snap["leaderboard"]),
                "protocol": snap["protocol"],
                "embedded": True,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
