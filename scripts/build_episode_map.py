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
    text,
)

OUT = ROOT / "assets" / "sota-2026-episode-map.svg"
SPLIT = ROOT / "data" / "splits" / "public_test.json"
GOLD = ROOT / "gold" / "rpi_v1.json"
THESES = ROOT / "data" / "theses"

# Short plain-language case names only (no long truncated blurbs under bars).
DISPLAY = {
    "s02e01-be-right-back-griefbot-persona-from-data": {
        "episode": "Be Right Back",
        "code": "S2E1",
        "short": "Griefbot trained on a dead person’s data",
    },
    "s02e03-waldo-moment-cgi-political-candidate": {
        "episode": "The Waldo Moment",
        "code": "S2E3",
        "short": "CGI / AI character runs for politics",
    },
    "s04e02-arkangel-parental-neural-surveillance-filter": {
        "episode": "Arkangel",
        "code": "S4E2",
        "short": "Parent implant tracks & filters a child’s world",
    },
    "s05e03-rachel-jack-ashley-too-celebrity-ai-toy-puppet": {
        "episode": "Rachel, Jack and Ashley Too",
        "code": "S5E3",
        "short": "Celebrity persona sold as AI toys",
    },
    "s07e04-plaything-evolving-artificial-lifeforms": {
        "episode": "Plaything",
        "code": "S7E4",
        "short": "Game creatures evolve into real artificial life",
    },
}


def load_rows() -> list[dict]:
    ids = json.loads(SPLIT.read_text(encoding="utf-8"))["thesis_ids"]
    gold = {g["thesis_id"]: g for g in json.loads(GOLD.read_text(encoding="utf-8"))["scores"]}
    rows = []
    for tid in ids:
        # thesis file kept for API stability / tests
        _ = json.loads((THESES / f"{tid}.json").read_text(encoding="utf-8"))
        g = gold[tid]
        axes = g["axes"]
        meta = DISPLAY[tid]
        rows.append(
            {
                "thesis_id": tid,
                "episode": meta["episode"],
                "code": meta["code"],
                "short": meta["short"],
                # keep statement field for tests that may check non-empty blurbs
                "statement": meta["short"],
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
        f'  <rect x="{x}" y="{y}" width="{max_w}" height="16" rx="8" fill="{RAIL}"/>',
        f'  <rect x="{x}" y="{y}" width="{bw:.1f}" height="16" rx="8" fill="{fill}" '
        f'filter="url(#soft-sm-{uid})"/>',
    ]


def build_svg(rows: list[dict]) -> str:
    uid = "ep"
    w = W
    pad = 48
    header_h = 128
    row_h = 96
    h = header_h + len(rows) * row_h + 56
    bar_w = 280

    lines = canvas(w, h, uid, "BlackMirror-Bench episode reality map 2026")
    lines += [
        text(pad, 42, "Layer A · Episode reality 2026", size=32, weight="800"),
        text(
            pad,
            72,
            "How close is each Black Mirror case to real life in 2026? (not a model ranking)",
            size=15,
            fill=MUTED,
            weight="500",
        ),
        # compact legend
        f'  <rect x="{pad}" y="90" width="12" height="12" rx="3" fill="{TEAL}"/>',
        text(pad + 20, 101, "Executable now", size=13, fill=MUTED, weight="600"),
        f'  <rect x="{pad + 160}" y="90" width="12" height="12" rx="3" fill="{ACCENT_2}"/>',
        text(pad + 180, 101, "AI already", size=13, fill=MUTED, weight="600"),
        text(
            pad + 300,
            101,
            "·  research gold scores 0–100  ·  not Netflix",
            size=12,
            fill=FAINT,
            weight="500",
        ),
    ]

    for i, r in enumerate(rows):
        y = header_h + i * row_h
        card_h = row_h - 12
        accent = TEAL if r["thesis_poss"] >= 70 else (ACCENT if r["thesis_poss"] >= 50 else ACCENT_2)

        lines.append(
            f'  <rect x="{pad}" y="{y}" width="{w - 2 * pad}" height="{card_h}" rx="18" '
            f'fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="1"/>'
        )
        lines.append(
            f'  <rect x="{pad}" y="{y}" width="5" height="{card_h}" rx="2" fill="{accent}"/>'
        )
        # code pill
        lines.append(
            f'  <rect x="{pad + 20}" y="{y + 28}" width="50" height="26" rx="8" '
            f'fill="rgba(125,211,252,0.12)" stroke="rgba(125,211,252,0.28)" stroke-width="1"/>'
        )
        lines.append(
            text(
                pad + 45,
                y + 46,
                r["code"],
                size=12,
                fill=ACCENT,
                mono=True,
                weight="800",
                anchor="middle",
            )
        )
        # title + one short line only (no truncated paragraph under bars)
        lines.append(text(pad + 82, y + 36, r["episode"], size=18, weight="800"))
        lines.append(
            text(pad + 82, y + 60, r["short"], size=14, fill="#CBD5E1", weight="500")
        )

        # bars + labels on the right, aligned mid-card
        mx = pad + 560
        mid = y + card_h / 2
        by1 = mid - 22
        by2 = mid + 6
        lines += _bar(mx, by1, bar_w, r["thesis_poss"], TEAL, uid)
        lines += _bar(mx, by2, bar_w, r["ai_exec"], ACCENT_2, uid)

        # tiny metric labels left of bars
        lines.append(
            text(mx - 8, by1 + 13, "Exec", size=11, fill=TEAL, mono=True, weight="700", anchor="end")
        )
        lines.append(
            text(mx - 8, by2 + 13, "AI", size=11, fill=ACCENT_2, mono=True, weight="700", anchor="end")
        )

        # big numbers
        lines.append(
            text(
                w - pad - 24,
                by1 + 14,
                f'{r["thesis_poss"]:.0f}',
                size=26,
                fill=TEAL,
                mono=True,
                weight="800",
                anchor="end",
            )
        )
        lines.append(
            text(
                w - pad - 24,
                by2 + 14,
                f'{r["ai_exec"]:.0f}',
                size=20,
                fill=ACCENT_2,
                mono=True,
                weight="700",
                anchor="end",
            )
        )

    lines.append(
        text(
            pad,
            h - 22,
            "Same 5 cases for every model  ·  Layer B = can AIs recover these scores honestly?",
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
                        "short": r["short"],
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
