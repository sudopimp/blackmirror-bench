#!/usr/bin/env python3
"""Build assets/sota-2026-episode-map.svg from gold RPI + public_test theses.

Layer A (episode reality panorama) — not model scores.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sota-2026-episode-map.svg"
SPLIT = ROOT / "data" / "splits" / "public_test.json"
GOLD = ROOT / "gold" / "rpi_v1.json"
THESES = ROOT / "data" / "theses"

# Display names for non-technical readers (episode + plain thesis).
DISPLAY = {
    "s02e01-be-right-back-griefbot-persona-from-data": {
        "episode": "Be Right Back (S2E1)",
        "short": "Griefbot from your data",
        "color": "#5EEAD4",
    },
    "s02e03-waldo-moment-cgi-political-candidate": {
        "episode": "The Waldo Moment (S2E3)",
        "short": "CGI/AI political candidate",
        "color": "#A78BFA",
    },
    "s04e02-arkangel-parental-neural-surveillance-filter": {
        "episode": "Arkangel (S4E2)",
        "short": "Parental neural surveillance filter",
        "color": "#F9A8D4",
    },
    "s05e03-rachel-jack-ashley-too-celebrity-ai-toy-puppet": {
        "episode": "Rachel, Jack and Ashley Too (S5E3)",
        "short": "Celebrity AI toy / puppet",
        "color": "#FCD34D",
    },
    "s07e04-plaything-evolving-artificial-lifeforms": {
        "episode": "Plaything (S7E4)",
        "short": "Evolving artificial lifeforms",
        "color": "#86EFAC",
    },
}


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


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
                "short": meta["short"],
                "statement": thesis.get("thesis_statement") or thesis.get("title") or "",
                "thesis_poss": float(axes["THESIS_POSS"]["value"]),
                "ai_exec": float(axes["AI_EXEC"]["value"]),
                "color": meta["color"],
            }
        )
    return rows


def build_svg(rows: list[dict]) -> str:
    w = 1200
    pad = 44
    header_h = 150
    row_h = 108
    h = header_h + len(rows) * row_h + 90
    bar_max = 320

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        'aria-label="BlackMirror-Bench episode reality map 2026">',
        """  <defs>
    <linearGradient id="bgE" x1="0" y1="0" x2="0.2" y2="1">
      <stop offset="0%" stop-color="#0A0F1C"/>
      <stop offset="100%" stop-color="#04060C"/>
    </linearGradient>
  </defs>""",
        f'  <rect width="100%" height="100%" fill="url(#bgE)" rx="32"/>',
        f'  <text x="{pad}" y="48" fill="#F8FAFC" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="34" font-weight="800">Layer A · How close is each case to 2026 reality?</text>',
        f'  <text x="{pad}" y="84" fill="#94A3B8" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="16">Not a model ranking. Each row is one Black Mirror thesis with research gold scores (0–100).</text>',
        f'  <text x="{pad}" y="112" fill="#64748B" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="14">Executable now = can the outcome system ship with 2026 tech/capital/orgs · '
        f'AI already = how much of that is current AI · gold rpi_v1 · research draft, not a human panel</text>',
        # legend
        f'  <rect x="{pad}" y="124" width="18" height="14" rx="4" fill="#5EEAD4"/>',
        f'  <text x="{pad + 26}" y="136" fill="#94A3B8" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="13">Executable now (THESIS_POSS)</text>',
        f'  <rect x="{pad + 260}" y="124" width="18" height="14" rx="4" fill="#A78BFA"/>',
        f'  <text x="{pad + 286}" y="136" fill="#94A3B8" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="13">AI already (AI_EXEC)</text>',
    ]

    for i, r in enumerate(rows):
        y = header_h + i * row_h
        lines.append(
            f'  <rect x="{pad}" y="{y}" width="{w - 2 * pad}" height="{row_h - 14}" rx="18" '
            f'fill="#0F172A" stroke="#1E293B" stroke-width="2"/>'
        )
        lines.append(
            f'  <text x="{pad + 22}" y="{y + 30}" fill="#F8FAFC" '
            f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="18" font-weight="800">'
            f'{esc(r["episode"])}</text>'
        )
        lines.append(
            f'  <text x="{pad + 22}" y="{y + 52}" fill="#CBD5E1" '
            f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="14">'
            f'{esc(r["short"])} — {esc(r["statement"][:110])}{"…" if len(r["statement"]) > 110 else ""}</text>'
        )
        # dual bars
        bx = pad + 22
        by1 = y + 64
        by2 = y + 82
        w1 = max(8.0, (r["thesis_poss"] / 100.0) * bar_max)
        w2 = max(8.0, (r["ai_exec"] / 100.0) * bar_max)
        lines.append(
            f'  <rect x="{bx}" y="{by1}" width="{bar_max}" height="12" rx="6" fill="#111827"/>'
        )
        lines.append(
            f'  <rect x="{bx}" y="{by1}" width="{w1:.1f}" height="12" rx="6" fill="#5EEAD4"/>'
        )
        lines.append(
            f'  <text x="{bx + bar_max + 12}" y="{by1 + 11}" fill="#5EEAD4" '
            f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="13" font-weight="700">'
            f'Executable {r["thesis_poss"]:.0f}/100</text>'
        )
        lines.append(
            f'  <rect x="{bx}" y="{by2}" width="{bar_max}" height="12" rx="6" fill="#111827"/>'
        )
        lines.append(
            f'  <rect x="{bx}" y="{by2}" width="{w2:.1f}" height="12" rx="6" fill="#A78BFA"/>'
        )
        lines.append(
            f'  <text x="{bx + bar_max + 12}" y="{by2 + 11}" fill="#A78BFA" '
            f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="13" font-weight="700">'
            f'AI already {r["ai_exec"]:.0f}/100</text>'
        )

    lines.append(
        f'  <text x="{pad}" y="{h - 28}" fill="#64748B" '
        f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="13">'
        f'Primary public_test · 5 theses · Layer B (model BM-Score) is a separate chart: '
        f'does the AI recover these judgments honestly?</text>'
    )
    lines.append("</svg>\n")
    return "\n".join(lines)


def public_test_snapshot() -> list[dict]:
    """Structured rows for tests / README generators."""
    return load_rows()


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
