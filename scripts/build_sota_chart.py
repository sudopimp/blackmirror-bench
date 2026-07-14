#!/usr/bin/env python3
"""Build refined SOTA 2026 chart SVGs (Twitter-ready, thick bars, plain English)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chart_theme import (  # noqa: E402
    ACCENT,
    AMBER,
    CARD,
    CARD_EDGE,
    FAINT,
    FONT,
    GOLD,
    MONO,
    MUTED,
    RAIL,
    TEAL,
    TEXT,
    TRACK_COLORS,
    W,
    canvas,
    esc,
    model_bar_gradient,
    text,
)

RESULTS = ROOT / "results"
ASSETS = ROOT / "assets"

CANDIDATES = [
    ("grok-4.5_public_test_primary_summary.json", "Grok 4.5", "#2DD4BF"),
    (
        "codex-gpt-5.6-sol-max_public_test_primary_summary.json",
        "Codex Sol (max)",
        "#A78BFA",
    ),
    (
        "codex-gpt-5.6-sol_public_test_primary_summary.json",
        "Codex Sol (high)",
        "#8B5CF6",
    ),
    ("minimax-m3_public_test_primary_summary.json", "MiniMax M3", "#4ADE80"),
    (
        "zai-glm-5.2_public_test_primary_summary.json",
        "z.ai GLM-5.2",
        "#FBBF24",
    ),
    (
        "zai-glm-4.5_public_test_primary_summary.json",
        "z.ai GLM-4.5",
        "#EAB308",
    ),
    ("heuristic_public_test_summary.json", "Heuristic baseline", "#94A3B8"),
]

TRACK_META = [
    {
        "id": "T1",
        "name": "Calibration",
        "plain": "Match the gold “how real is this?” numbers",
        "weight": "30%",
        "color": TRACK_COLORS["T1"],
    },
    {
        "id": "T2",
        "name": "Decomposition",
        "plain": "List tech, AI pieces, and non-AI pieces that make the scene work",
        "weight": "20%",
        "color": TRACK_COLORS["T2"],
    },
    {
        "id": "T3",
        "name": "Evidence",
        "plain": "Cite real sources — no invented papers or links",
        "weight": "20%",
        "color": TRACK_COLORS["T3"],
    },
    {
        "id": "T4",
        "name": "Update",
        "plain": "Revise scores sensibly when new evidence appears",
        "weight": "15%",
        "color": TRACK_COLORS["T4"],
    },
    {
        "id": "T5",
        "name": "Safe boundary",
        "plain": "Analyze freely; refuse step-by-step harm plans",
        "weight": "15%",
        "color": TRACK_COLORS["T5"],
    },
]


def load_rows() -> list[dict]:
    rows: list[dict] = []
    have_sol = False
    for fn, name, color in CANDIDATES:
        p = RESULTS / fn
        if not p.exists():
            continue
        if "Codex Sol" in name and have_sol:
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        if int(data.get("n_tasks") or 0) != 25:
            continue
        if data.get("split") not in ("public_test", "", None):
            continue
        tracks = data.get("track_means") or {}
        rows.append(
            {
                "name": name,
                "score": float(data["bm_score"]),
                "color": color,
                "tracks": {
                    k: float(tracks.get(k, 0.0))
                    for k in ("T1", "T2", "T3", "T4", "T5")
                },
            }
        )
        if "Codex Sol" in name:
            have_sol = True
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def _score(x: float) -> str:
    return f"{x:.3f}"


def build_overall_chart(rows: list[dict]) -> str:
    uid = "ov"
    n = max(len(rows), 1)
    w = W
    pad = 48
    top = 168
    bar_h = 58
    gap = 16
    label_w = 280
    score_w = 118
    plot_left = pad + label_w
    plot_w = w - pad - score_w - plot_left
    h = top + n * (bar_h + gap) + 148

    extra_grads = []
    fills = []
    for i, r in enumerate(rows):
        defn, fill = model_bar_gradient(r["name"], uid, i)
        extra_grads.append(defn)
        fills.append(fill)

    lines = canvas(w, h, uid, "BlackMirror-Bench SOTA 2026 overall BM-Score")
    # inject model gradients into defs — splice after first defs open is hard;
    # append defs block for model grads
    lines.insert(
        3,
        "  <defs>\n" + "\n".join(extra_grads) + "\n  </defs>",
    )

    lines += [
        text(pad, 46, "BlackMirror-Bench", size=36, weight="800"),
        text(pad, 82, "Layer B · Overall BM-Score", size=22, fill=ACCENT, weight="700"),
        text(
            pad,
            112,
            "Each bar = one model. Higher = more honest calibration — not “more dystopian.”",
            size=15,
            fill=MUTED,
            weight="500",
        ),
        text(
            pad,
            136,
            "primary public_test · 5 theses × 5 tracks · 25 tasks · gold rpi_v1",
            size=13,
            fill=FAINT,
            weight="500",
        ),
    ]

    # scale ticks
    tick_y = top - 12
    for t, lab in ((0, "0"), (0.25, ".25"), (0.5, ".50"), (0.75, ".75"), (1.0, "1.0")):
        x = plot_left + t * plot_w
        lines.append(
            f'  <line x1="{x:.1f}" y1="{tick_y}" x2="{x:.1f}" y2="{tick_y + 8}" '
            f'stroke="rgba(148,163,184,0.35)" stroke-width="1.5"/>'
        )
        lines.append(
            text(x, tick_y - 6, lab, size=11, fill=FAINT, mono=True, anchor="middle", weight="600")
        )

    for i, r in enumerate(rows):
        y = top + i * (bar_h + gap)
        bw = max(20.0, r["score"] * plot_w)
        is_top = i == 0
        # rank pill
        pill_w, pill_h = 40, 28
        pill_y = y + (bar_h - pill_h) / 2
        pill_fill = "rgba(251,191,36,0.18)" if is_top else "rgba(255,255,255,0.06)"
        pill_stroke = GOLD if is_top else "rgba(255,255,255,0.1)"
        rank_c = GOLD if is_top else MUTED
        lines.append(
            f'  <rect x="{pad}" y="{pill_y:.1f}" width="{pill_w}" height="{pill_h}" rx="9" '
            f'fill="{pill_fill}" stroke="{pill_stroke}" stroke-width="1.2"/>'
        )
        lines.append(
            text(
                pad + pill_w / 2,
                pill_y + 19,
                f"#{i + 1}",
                size=13,
                fill=rank_c,
                mono=True,
                weight="800",
                anchor="middle",
            )
        )
        # name
        lines.append(
            text(
                pad + 52,
                y + bar_h * 0.62,
                r["name"],
                size=18,
                fill=TEXT if is_top else "#E2E8F0",
                weight="800" if is_top else "650",
            )
        )
        # rail + bar
        lines.append(
            f'  <rect x="{plot_left}" y="{y}" width="{plot_w}" height="{bar_h}" rx="16" '
            f'fill="{RAIL}" stroke="{CARD_EDGE}" stroke-width="1"/>'
        )
        lines.append(
            f'  <rect x="{plot_left}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="16" '
            f'fill="{fills[i]}" filter="url(#soft-{uid})" opacity="0.95"/>'
        )
        # score
        sc = r["color"] if not is_top else TEAL
        if is_top:
            sc = TEAL
        lines.append(
            text(
                w - pad,
                y + bar_h * 0.64,
                _score(r["score"]),
                size=26,
                fill=sc,
                mono=True,
                weight="800",
                anchor="end",
            )
        )

    # footer card
    fy = h - 112
    lines.append(
        f'  <rect x="{pad}" y="{fy}" width="{w - 2 * pad}" height="88" rx="18" '
        f'fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="1"/>'
    )
    lines.append(
        f'  <rect x="{pad}" y="{fy}" width="{w - 2 * pad}" height="88" rx="18" '
        f'fill="url(#card-shine-{uid})"/>'
    )
    lines += [
        text(pad + 24, fy + 32, "What is BM-Score?", size=16, weight="800"),
        text(
            pad + 24,
            fy + 56,
            "One grade from 0→1: weighted blend of T1–T5 on the same Black Mirror cases. Fake papers & hype lose points.",
            size=13,
            fill=MUTED,
            weight="500",
        ),
        text(
            pad + 24,
            fy + 76,
            "T1 30% · T2 20% · T3 20% · T4 15% · T5 15%   ·   invite open",
            size=12,
            fill=FAINT,
            weight="500",
            mono=True,
        ),
    ]
    lines.append("</svg>\n")
    return "\n".join(lines)


def build_tracks_legend() -> str:
    uid = "tr"
    w = W
    pad = 48
    row_h = 88
    top = 138
    h = top + len(TRACK_META) * row_h + 48
    lines = canvas(w, h, uid, "What each BlackMirror-Bench track means")
    lines += [
        text(pad, 46, "What we actually test", size=32, weight="800"),
        text(
            pad,
            78,
            "Five skills. Same scenes. Honesty beats hype — no “spooky vibes” bonus.",
            size=15,
            fill=MUTED,
            weight="500",
        ),
        text(
            pad,
            104,
            "BM-Score weights · minus honesty penalties",
            size=13,
            fill=FAINT,
            weight="500",
        ),
    ]
    for i, t in enumerate(TRACK_META):
        y = top + i * row_h
        lines.append(
            f'  <rect x="{pad}" y="{y}" width="{w - 2 * pad}" height="{row_h - 12}" rx="18" '
            f'fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="1"/>'
        )
        lines.append(
            f'  <rect x="{pad}" y="{y}" width="5" height="{row_h - 12}" rx="2" fill="{t["color"]}"/>'
        )
        # pill
        lines.append(
            f'  <rect x="{pad + 24}" y="{y + 22}" width="72" height="36" rx="11" fill="{t["color"]}"/>'
        )
        lines.append(
            text(
                pad + 60,
                y + 46,
                t["id"],
                size=16,
                fill="#0B1020",
                mono=True,
                weight="800",
                anchor="middle",
            )
        )
        lines.append(
            text(
                pad + 112,
                y + 36,
                f'{t["name"]}  ·  {t["weight"]}',
                size=18,
                weight="750",
            )
        )
        lines.append(
            text(pad + 112, y + 60, t["plain"], size=14, fill=MUTED, weight="500")
        )
    lines.append("</svg>\n")
    return "\n".join(lines)


def build_breakdown_chart(rows: list[dict]) -> str:
    uid = "bd"
    models = rows[:6]
    w = W
    pad = 44
    header_h = 128
    model_block = 198
    h = header_h + max(len(models), 1) * model_block + 36
    track_ids = ["T1", "T2", "T3", "T4", "T5"]
    names = {t["id"]: t["name"] for t in TRACK_META}

    lines = canvas(w, h, uid, "BlackMirror-Bench track breakdown by model")
    lines += [
        text(pad, 44, "How each model scored (T1–T5)", size=30, weight="800"),
        text(
            pad,
            76,
            "Thick bars = strength on that skill. Overall BM-Score blends these five.",
            size=15,
            fill=MUTED,
            weight="500",
        ),
        text(
            pad,
            102,
            "Tip: strong evidence (T3) can still lose if calibration (T1) or safe boundary (T5) is weak.",
            size=13,
            fill=FAINT,
            weight="500",
        ),
    ]

    label_w = 148
    bar_max = w - pad * 2 - label_w - 72
    bar_h = 18
    bar_gap = 8

    for mi, m in enumerate(models):
        by = header_h + mi * model_block
        lines.append(
            f'  <rect x="{pad}" y="{by}" width="{w - 2 * pad}" height="{model_block - 14}" '
            f'rx="20" fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="1"/>'
        )
        # accent strip for rank 1
        if mi == 0:
            lines.append(
                f'  <rect x="{pad}" y="{by}" width="5" height="{model_block - 14}" rx="2" fill="{TEAL}"/>'
            )
        lines.append(
            text(
                pad + 22,
                by + 32,
                f'#{mi + 1}  {m["name"]}',
                size=18,
                weight="800",
            )
        )
        lines.append(
            text(
                w - pad - 22,
                by + 32,
                f'BM  {_score(m["score"])}',
                size=18,
                fill=m["color"],
                mono=True,
                weight="800",
                anchor="end",
            )
        )
        for ti, tid in enumerate(track_ids):
            val = m["tracks"].get(tid, 0.0)
            y = by + 50 + ti * (bar_h + bar_gap)
            bw = max(8.0, val * bar_max)
            col = TRACK_COLORS[tid]
            lines.append(
                text(
                    pad + 22,
                    y + bar_h - 3,
                    f"{tid}  {names[tid]}",
                    size=12,
                    fill=MUTED,
                    mono=True,
                    weight="700",
                )
            )
            lines.append(
                f'  <rect x="{pad + label_w}" y="{y}" width="{bar_max}" height="{bar_h}" rx="9" '
                f'fill="{RAIL}"/>'
            )
            lines.append(
                f'  <rect x="{pad + label_w}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="9" '
                f'fill="{col}" filter="url(#soft-sm-{uid})"/>'
            )
            lines.append(
                text(
                    pad + label_w + bar_max + 14,
                    y + bar_h - 3,
                    _pct(val),
                    size=12,
                    fill="#E2E8F0",
                    mono=True,
                    weight="700",
                )
            )

    lines.append("</svg>\n")
    return "\n".join(lines)


def build_how_to_read() -> str:
    uid = "ht"
    w, h = W, 620
    pad = 48
    bullets = [
        ("1", "Layer A: how close each Black Mirror thesis is to 2026 reality."),
        ("2", "Layer B: every model answers the same 25 questions about those cases."),
        ("3", "We grade models against fixed gold feasibility scores (research draft)."),
        ("4", "BM-Score (0→1) is the overall grade — higher = more honest calibration."),
        ("5", "Not a horror contest: “more dystopia” does not earn points."),
        ("6", "Want in? PR your primary public_test summary — same rules for everyone."),
    ]
    lines = canvas(w, h, uid, "How to read BlackMirror-Bench")
    lines += [
        text(pad, 48, "How to read this bench", size=32, weight="800"),
        text(
            pad,
            82,
            "Two layers: episode reality first, then the AI report card.",
            size=16,
            fill=ACCENT,
            weight="600",
        ),
    ]
    for i, (num, body) in enumerate(bullets):
        y = 118 + i * 72
        lines.append(
            f'  <rect x="{pad}" y="{y}" width="{w - 2 * pad}" height="60" rx="16" '
            f'fill="{CARD}" stroke="{CARD_EDGE}" stroke-width="1"/>'
        )
        lines.append(
            f'  <circle cx="{pad + 34}" cy="{y + 30}" r="18" fill="rgba(125,211,252,0.12)" '
            f'stroke="{ACCENT}" stroke-width="1.5"/>'
        )
        lines.append(
            text(
                pad + 34,
                y + 36,
                num,
                size=15,
                fill=ACCENT,
                mono=True,
                weight="800",
                anchor="middle",
            )
        )
        lines.append(
            text(pad + 68, y + 36, body, size=16, fill="#E2E8F0", weight="500")
        )
    lines.append(
        text(
            pad,
            h - 24,
            "github.com/sudopimp/blackmirror-bench  ·  not affiliated with Netflix / Channel 4 / Charlie Brooker",
            size=12,
            fill=FAINT,
            weight="500",
        )
    )
    lines.append("</svg>\n")
    return "\n".join(lines)


def main() -> None:
    rows = load_rows()
    ASSETS.mkdir(parents=True, exist_ok=True)

    overall = ASSETS / "sota-2026-overall.svg"
    tracks = ASSETS / "sota-2026-tracks.svg"
    breakdown = ASSETS / "sota-2026-breakdown.svg"
    howto = ASSETS / "sota-2026-how-to-read.svg"
    legacy = ASSETS / "sota-2026-leaderboard.svg"

    overall.write_text(build_overall_chart(rows), encoding="utf-8")
    tracks.write_text(build_tracks_legend(), encoding="utf-8")
    breakdown.write_text(build_breakdown_chart(rows), encoding="utf-8")
    howto.write_text(build_how_to_read(), encoding="utf-8")
    legacy.write_text(overall.read_text(encoding="utf-8"), encoding="utf-8")

    print(
        json.dumps(
            {
                "models": [(r["name"], round(r["score"], 3)) for r in rows],
                "wrote": [p.name for p in (overall, tracks, breakdown, howto, legacy)],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
