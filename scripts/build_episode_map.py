#!/usr/bin/env python3
"""Build refined assets/sota-2026-episode-map.svg (Layer A · episode reality)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chart_theme import (  # noqa: E402
    ACCENT,
    ACCENT_2,
    CARD,
    CARD_EDGE,
    FAINT,
    MUTED,
    RAIL,
    TEAL,
    TEXT,
    W,
    canvas,
    esc,
    text,
)

OUT = ROOT / "assets" / "sota-2026-episode-map.svg"
SPLIT = ROOT / "data" / "splits" / "public_test.json"
GOLD = ROOT / "gold" / "rpi_v1.json"
THESES = ROOT / "data" / "theses"

DISPLAY = {
    "s02e01-be-right-back-griefbot-persona-from-data": {
        "episode": "Be Right Back",
        "code": "S2E1",
        "short": "Griefbot from your data",
    },
    "s02e03-waldo-moment-cgi-political-candidate": {
        "episode": "The Waldo Moment",
        "code": "S2E3",
        "short": "CGI / AI political candidate",
    },
    "s04e02-arkangel-parental-neural-surveillance-filter": {
        "episode": "Arkangel",
        "code": "S4E2",
        "short": "Parental neural surveillance filter",
    },
    "s05e03-rachel-jack-ashley-too-celebrity-ai-toy-puppet": {
        "episode": "Rachel, Jack and Ashley Too",
        "code": "S5E3",
        "short": "Celebrity AI toy / puppet",
    },
    "s07e04-plaything-evolving-artificial-lifeforms": {
        "episode": "Plaything",
        "code": "S7E4",
        "short": "Evolving artificial lifeforms",
    },
}


def load_rows() -> list[dict]:
    ids = json.loads(SPLIT.read_text(encoding="utf-8"))["thesis_ids"]
    gold = {g["thesis_id"]: g for g in json.loads(GOLD.read_text(encoding="utf-8"))["scores"]}
    rows = []
    for tid in ids:
        thesis = json.loads((THESES / f"{tid}.json").read_text(encoding="utf-8"))
        g = gold[tid]
        axes = g["axes"]
        meta = DISPLAY[tid]
        rows.append(
            {
                "thesis_id": tid,
                "episode": meta["episode"],
                "code": meta["code"],
                "short": meta["short"],
                "statement": thesis.get("thesis_statement") or thesis.get("title") or "",
                "thesis_poss": float(axes["THESIS_POSS"]["value"]),
                "ai_exec": float(axes["AI_EXEC"]["value"]),
            }
        )
    return rows


def public_test_snapshot() -> list[dict]:
    return load_rows()


def _bar(x: float, y: float, max_w: float, value: float, fill: str, uid: str) -> list[str]:
    bw = max(10.0, (value / 100.0) * max_w)
    return [
        f'  <rect x="{x}" y="{y}" width="{max_w}" height="14" rx="7" fill="{RAIL}"/>',
        f'  <rect x="{x}" y="{y}" width="{bw:.1f}" height="14" rx="7" fill="{fill}" '
        f'filter="url(#soft-sm-{uid})"/>',
    ]


def build_svg(rows: list[dict]) -> str:
    uid = "ep"
    w = W
    pad = 44
    header_h = 148
    row_h = 118
    h = header_h + len(rows) * row_h + 72
    bar_max = 300

    lines = canvas(w, h, uid, "BlackMirror-Bench episode reality map 2026")
    lines += [
        text(pad, 44, "Layer A · Episode reality 2026", size=32, weight="800"),
        text(
            pad,
            76,
            "Not a model ranking. Each row is one Black Mirror thesis with research gold scores (0–100).",
            size=15,
            fill=MUTED,
            weight="500",
        ),
        # legend chips
        f'  <rect x="{pad}" y="96" width="14" height="14" rx="4" fill="{TEAL}"/>',
        text(pad + 22, 108, "Executable now — can the full outcome system ship in 2026?", size=13, fill=MUTED, weight="500"),
        f'  <rect x="{pad + 520}" y="96" width="14" height="14" rx="4" fill="{ACCENT_2}"/>',
        text(pad + 542, 108, "AI already — how much of that is current AI?", size=13, fill=MUTED, weight="500"),
        text(
            pad,
            132,
            "gold rpi_v1 · research draft with confidence intervals · not a human panel · not Netflix",
            size=12,
            fill=FAINT,
            weight="500",
        ),
    ]

    for i, r in enumerate(rows):
        y = header_h + i * row_h
        card_h = row_h - 14
        lines.append(
            f'  <rect x="{pad}" y="{y}" width="{w - 2 * pad}" height="{card_h}" rx="20" '
            f'fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="1"/>'
        )
        # left accent by “how real”
        accent = TEAL if r["thesis_poss"] >= 70 else (ACCENT if r["thesis_poss"] >= 50 else ACCENT_2)
        lines.append(
            f'  <rect x="{pad}" y="{y}" width="5" height="{card_h}" rx="2" fill="{accent}"/>'
        )
        # episode code pill
        lines.append(
            f'  <rect x="{pad + 22}" y="{y + 18}" width="52" height="24" rx="8" '
            f'fill="rgba(125,211,252,0.12)" stroke="rgba(125,211,252,0.25)" stroke-width="1"/>'
        )
        lines.append(
            text(
                pad + 48,
                y + 35,
                r["code"],
                size=12,
                fill=ACCENT,
                mono=True,
                weight="800",
                anchor="middle",
            )
        )
        lines.append(
            text(pad + 86, y + 36, r["episode"], size=18, weight="800")
        )
        lines.append(
            text(pad + 22, y + 58, r["short"], size=14, fill="#CBD5E1", weight="600")
        )
        stmt = r["statement"]
        if len(stmt) > 96:
            stmt = stmt[:93] + "…"
        lines.append(
            text(pad + 22, y + 80, stmt, size=13, fill=MUTED, weight="500")
        )

        # dual metric column on the right (bars + big numbers only — no mid clutter)
        mx = pad + 580
        bar_w = 260
        lines += _bar(mx, y + 34, bar_w, r["thesis_poss"], TEAL, uid)
        lines += _bar(mx, y + 62, bar_w, r["ai_exec"], ACCENT_2, uid)
        lines.append(
            text(
                w - pad - 20,
                y + 48,
                f'{r["thesis_poss"]:.0f}',
                size=30,
                fill=TEAL,
                mono=True,
                weight="800",
                anchor="end",
            )
        )
        lines.append(
            text(
                w - pad - 20,
                y + 78,
                f'{r["ai_exec"]:.0f}',
                size=22,
                fill=ACCENT_2,
                mono=True,
                weight="700",
                anchor="end",
            )
        )

    lines.append(
        text(
            pad,
            h - 28,
            "Primary public_test · 5 theses  ·  Layer B (model BM-Score) asks: do AIs recover these judgments honestly?",
            size=12,
            fill=FAINT,
            weight="500",
        )
    )
    lines.append("</svg>\n")
    return "\n".join(lines)


def main() -> None:
    rows = load_rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_svg(rows), encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(OUT),
                "rows": [
                    {
                        "episode": r["episode"],
                        "THESIS_POSS": r["thesis_poss"],
                        "AI_EXEC": r["ai_exec"],
                    }
                    for r in rows
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
