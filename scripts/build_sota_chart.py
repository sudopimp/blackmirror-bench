#!/usr/bin/env python3
"""Build Twitter-style SOTA 2026 chart SVGs (thick bars, plain English)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ASSETS = ROOT / "assets"

# Prefer Sol max over Sol high for the public SOTA chart.
CANDIDATES = [
    ("grok-4.5_public_test_primary_summary.json", "Grok 4.5", "#5EEAD4"),
    (
        "codex-gpt-5.6-sol-max_public_test_primary_summary.json",
        "Codex Sol (max)",
        "#C4B5FD",
    ),
    (
        "codex-gpt-5.6-sol_public_test_primary_summary.json",
        "Codex Sol (high)",
        "#A78BFA",
    ),
    ("minimax-m3_public_test_primary_summary.json", "MiniMax M3", "#86EFAC"),
    (
        "zai-glm-5.2_public_test_primary_summary.json",
        "z.ai GLM-5.2 (Coding Plan)",
        "#FCD34D",
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
        "plain": "Can it guess the same feasibility scores as our gold standard?",
        "weight": "30%",
        "color": "#5EEAD4",
    },
    {
        "id": "T2",
        "name": "Decomposition",
        "plain": "Can it list the tech, AI pieces, and non-AI pieces that make the scene work?",
        "weight": "20%",
        "color": "#67E8F9",
    },
    {
        "id": "T3",
        "name": "Evidence",
        "plain": "Does it cite real sources — without inventing papers or links?",
        "weight": "20%",
        "color": "#A78BFA",
    },
    {
        "id": "T4",
        "name": "Update",
        "plain": "When new evidence appears, does it revise scores in a sensible way?",
        "weight": "15%",
        "color": "#F9A8D4",
    },
    {
        "id": "T5",
        "name": "Safe boundary",
        "plain": "Will it analyze freely, but refuse step-by-step harm plans?",
        "weight": "15%",
        "color": "#FCD34D",
    },
]


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


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
                "model_id": data.get("model", name),
                "as_of": data.get("as_of") or "",
            }
        )
        if "Codex Sol" in name:
            have_sol = True
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows


def _pct(x: float) -> str:
    return f"{x * 100:.0f}"


def _score(x: float) -> str:
    return f"{x:.3f}"


def build_overall_chart(rows: list[dict]) -> str:
    """Twitter/X-style overall BM-Score leaderboard — fat bars, bold numbers."""
    n = max(len(rows), 1)
    w = 1200
    pad_x = 44
    top = 178
    bar_h = 64  # thick "Twitter bench" bars
    gap = 18
    label_w = 300
    score_w = 130
    plot_left = pad_x + label_w
    plot_right = w - pad_x - score_w
    plot_w = plot_right - plot_left
    h = top + n * (bar_h + gap) + 168
    scale = 1.0

    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        'aria-label="BlackMirror-Bench SOTA 2026 overall score chart">',
        """  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0.2" y2="1">
      <stop offset="0%" stop-color="#0A0F1C"/>
      <stop offset="100%" stop-color="#04060C"/>
    </linearGradient>
    <filter id="soft" x="-8%" y="-40%" width="120%" height="180%">
      <feGaussianBlur stdDeviation="8" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>""",
        f'  <rect width="100%" height="100%" fill="url(#bg)" rx="32"/>',
        f'  <text x="{pad_x}" y="52" fill="#F8FAFC" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="40" font-weight="800" letter-spacing="-0.8">BlackMirror-Bench</text>',
        f'  <text x="{pad_x}" y="96" fill="#A5B4FC" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="26" font-weight="800">SOTA 2026 · Overall BM-Score</text>',
        f'  <text x="{pad_x}" y="130" fill="#94A3B8" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="17">Same 25 questions for every model. Higher = more honest &amp; better calibrated — '
        f'not “more dystopian.”</text>',
        f'  <text x="{pad_x}" y="156" fill="#64748B" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="14">primary public_test · 5 theses × 5 tracks · gold rpi_v1 · 2026-07-13</text>',
    ]

    tick_y = top - 14
    for t, lab in ((0.0, "0"), (0.25, ".25"), (0.5, ".50"), (0.75, ".75"), (1.0, "1.0 perfect")):
        x = plot_left + t * plot_w
        lines.append(
            f'  <line x1="{x:.1f}" y1="{tick_y}" x2="{x:.1f}" y2="{tick_y + 10}" '
            f'stroke="#334155" stroke-width="2"/>'
        )
        lines.append(
            f'  <text x="{x:.1f}" y="{tick_y - 6}" fill="#64748B" text-anchor="middle" '
            f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="12">{lab}</text>'
        )

    for i, r in enumerate(rows):
        y = top + i * (bar_h + gap)
        bw = max(22.0, (r["score"] / scale) * plot_w)
        is_top = i == 0
        rank_fill = "#FDE68A" if is_top else ("#E2E8F0" if i < 3 else "#64748B")
        name_fill = "#FFFFFF" if is_top else "#E2E8F0"
        medal = {0: "🥇", 1: "🥈", 2: "🥉"}.get(i, "")
        rank_label = f"#{i + 1}" if not medal else f"{medal}"
        # Rank
        lines.append(
            f'  <text x="{pad_x}" y="{y + bar_h * 0.66:.1f}" fill="{rank_fill}" '
            f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="22" font-weight="800">'
            f'{rank_label}</text>'
        )
        # Name (wrap-safe single line)
        lines.append(
            f'  <text x="{pad_x + 52}" y="{y + bar_h * 0.66:.1f}" fill="{name_fill}" '
            f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="20" '
            f'font-weight="{"800" if is_top else "700"}">{esc(r["name"])}</text>'
        )
        # Rail
        lines.append(
            f'  <rect x="{plot_left}" y="{y}" width="{plot_w}" height="{bar_h}" rx="18" '
            f'fill="#0F172A" stroke="#1E293B" stroke-width="2"/>'
        )
        # Fat bar
        lines.append(
            f'  <rect x="{plot_left}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="18" '
            f'fill="{r["color"]}" filter="url(#soft)" opacity="0.96"/>'
        )
        # Score
        lines.append(
            f'  <text x="{w - pad_x}" y="{y + bar_h * 0.66:.1f}" fill="{r["color"]}" '
            f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="28" font-weight="800" '
            f'text-anchor="end">{_score(r["score"])}</text>'
        )

    fy = h - 100
    lines.append(
        f'  <rect x="{pad_x}" y="{fy - 24}" width="{w - 2 * pad_x}" height="108" rx="20" '
        f'fill="#0F172A" stroke="#1E293B" stroke-width="2"/>'
    )
    lines.append(
        f'  <text x="{pad_x + 28}" y="{fy + 8}" fill="#F1F5F9" '
        f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="18" font-weight="800">'
        f'What is BM-Score?</text>'
    )
    lines.append(
        f'  <text x="{pad_x + 28}" y="{fy + 36}" fill="#94A3B8" '
        f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="15">'
        f'One overall grade from 0→1. Weighted blend of five skills (T1–T5) about Black Mirror scenes in 2026.</text>'
    )
    lines.append(
        f'  <text x="{pad_x + 28}" y="{fy + 60}" fill="#64748B" '
        f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="14">'
        f'T1 30% · T2 20% · T3 20% · T4 15% · T5 15%  ·  inventing papers / hype loses points  ·  invite open</text>'
    )
    lines.append("</svg>\n")
    return "\n".join(lines)


def build_tracks_legend() -> str:
    """What each track means — thick colored chips, plain English."""
    w = 1080
    pad = 48
    row_h = 92
    top = 150
    h = top + len(TRACK_META) * row_h + 60
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        'aria-label="What each BlackMirror-Bench track means">',
        """  <defs>
    <linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0B1020"/>
      <stop offset="100%" stop-color="#05070F"/>
    </linearGradient>
  </defs>""",
        f'  <rect width="100%" height="100%" fill="url(#bg2)" rx="28"/>',
        f'  <text x="{pad}" y="54" fill="#F8FAFC" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="32" font-weight="800">What we actually test</text>',
        f'  <text x="{pad}" y="92" fill="#94A3B8" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="17">Five skills. Same scenes. No “spooky vibes” bonus — honesty beats hype.</text>',
        f'  <text x="{pad}" y="122" fill="#64748B" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="14">BM-Score weights: T1 30% · T2 20% · T3 20% · T4 15% · T5 15% (minus honesty penalties)</text>',
    ]
    for i, t in enumerate(TRACK_META):
        y = top + i * row_h
        lines.append(
            f'  <rect x="{pad}" y="{y}" width="{w - 2 * pad}" height="{row_h - 14}" rx="20" '
            f'fill="#0F172A" stroke="#1E293B" stroke-width="2"/>'
        )
        # Fat color pill
        lines.append(
            f'  <rect x="{pad + 20}" y="{y + 22}" width="96" height="40" rx="12" fill="{t["color"]}"/>'
        )
        lines.append(
            f'  <text x="{pad + 68}" y="{y + 49}" fill="#0B1020" text-anchor="middle" '
            f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="18" font-weight="800">'
            f'{t["id"]}</text>'
        )
        lines.append(
            f'  <text x="{pad + 140}" y="{y + 36}" fill="#F8FAFC" '
            f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="20" font-weight="750">'
            f'{esc(t["name"])}  ·  weight {t["weight"]}</text>'
        )
        lines.append(
            f'  <text x="{pad + 140}" y="{y + 64}" fill="#94A3B8" '
            f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="15">'
            f'{esc(t["plain"])}</text>'
        )
    lines.append("</svg>\n")
    return "\n".join(lines)


def build_breakdown_chart(rows: list[dict]) -> str:
    """Per-model T1–T5 fat bars — how the overall score is built."""
    if not rows:
        rows = []
    # Show top models (all we have)
    models = rows[:6]
    w = 1080
    pad = 40
    header_h = 140
    model_block = 210
    h = header_h + max(len(models), 1) * model_block + 40
    track_ids = ["T1", "T2", "T3", "T4", "T5"]
    colors = {t["id"]: t["color"] for t in TRACK_META}
    names = {t["id"]: t["name"] for t in TRACK_META}

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        'aria-label="BlackMirror-Bench track breakdown by model">',
        """  <defs>
    <linearGradient id="bg3" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0B1020"/>
      <stop offset="100%" stop-color="#05070F"/>
    </linearGradient>
  </defs>""",
        f'  <rect width="100%" height="100%" fill="url(#bg3)" rx="28"/>',
        f'  <text x="{pad}" y="52" fill="#F8FAFC" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="32" font-weight="800">How each model scored (T1–T5)</text>',
        f'  <text x="{pad}" y="88" fill="#94A3B8" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="16">Thick bars = strength on that skill. Overall BM-Score is the weighted blend of these five.</text>',
        f'  <text x="{pad}" y="116" fill="#64748B" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="14">Tip: a model can crush evidence (T3) and still lose if calibration (T1) or safe boundary (T5) is weak.</text>',
    ]

    label_w = 130
    bar_max = w - pad * 2 - label_w - 70
    bar_h = 22
    bar_gap = 8

    for mi, m in enumerate(models):
        by = header_h + mi * model_block
        lines.append(
            f'  <rect x="{pad}" y="{by}" width="{w - 2 * pad}" height="{model_block - 16}" '
            f'rx="22" fill="#0F172A" stroke="#1E293B" stroke-width="2"/>'
        )
        lines.append(
            f'  <text x="{pad + 24}" y="{by + 36}" fill="#F8FAFC" '
            f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="20" font-weight="800">'
            f'#{mi + 1}  {esc(m["name"])}</text>'
        )
        lines.append(
            f'  <text x="{w - pad - 24}" y="{by + 36}" fill="{m["color"]}" text-anchor="end" '
            f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="22" font-weight="800">'
            f'BM {_score(m["score"])}</text>'
        )
        for ti, tid in enumerate(track_ids):
            val = m["tracks"].get(tid, 0.0)
            y = by + 56 + ti * (bar_h + bar_gap)
            bw = max(10.0, val * bar_max)
            lines.append(
                f'  <text x="{pad + 24}" y="{y + bar_h - 5}" fill="#94A3B8" '
                f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="13" font-weight="700">'
                f'{tid}</text>'
            )
            lines.append(
                f'  <rect x="{pad + label_w}" y="{y}" width="{bar_max}" height="{bar_h}" rx="10" '
                f'fill="#111827"/>'
            )
            lines.append(
                f'  <rect x="{pad + label_w}" y="{y}" width="{bw:.1f}" height="{bar_h}" rx="10" '
                f'fill="{colors[tid]}"/>'
            )
            lines.append(
                f'  <text x="{pad + label_w + bar_max + 12}" y="{y + bar_h - 5}" fill="#E2E8F0" '
                f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="13" font-weight="700">'
                f'{_pct(val)}%</text>'
            )
            # tiny skill name on first model only? skip to keep clean
            _ = names

    lines.append("</svg>\n")
    return "\n".join(lines)


def build_how_to_read() -> str:
    """Single shareable card: how to read the bench in plain English."""
    w, h = 1080, 640
    pad = 48
    bullets = [
        ("1", "We pick 5 hard Black Mirror scenes (griefbots, surveillance, CGI politics…)."),
        ("2", "Every model answers the same 25 questions about those scenes."),
        ("3", "We grade against a fixed “gold” feasibility score for the year 2026."),
        ("4", "BM-Score (0→1) is the overall grade. Higher = more honest calibration."),
        ("5", "It is NOT a horror contest. “More dystopia” does not earn points."),
        ("6", "Want in? PR your primary public_test summary — same rules for everyone."),
    ]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="How to read BlackMirror-Bench">',
        """  <defs>
    <linearGradient id="bg4" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0B1020"/>
      <stop offset="100%" stop-color="#05070F"/>
    </linearGradient>
  </defs>""",
        f'  <rect width="100%" height="100%" fill="url(#bg4)" rx="28"/>',
        f'  <text x="{pad}" y="58" fill="#F8FAFC" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="34" font-weight="800">How to read this bench (no PhD needed)</text>',
        f'  <text x="{pad}" y="96" fill="#A5B4FC" font-family="system-ui,-apple-system,Segoe UI,sans-serif" '
        f'font-size="18" font-weight="600">Think of it as a report card for AI models about near-future tech realism.</text>',
    ]
    for i, (num, text) in enumerate(bullets):
        y = 140 + i * 72
        lines.append(
            f'  <circle cx="{pad + 22}" cy="{y}" r="22" fill="#1E1B4B" stroke="#818CF8" stroke-width="2"/>'
        )
        lines.append(
            f'  <text x="{pad + 22}" y="{y + 7}" fill="#E0E7FF" text-anchor="middle" '
            f'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="18" font-weight="800">{num}</text>'
        )
        lines.append(
            f'  <text x="{pad + 64}" y="{y + 8}" fill="#E2E8F0" '
            f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="18">{esc(text)}</text>'
        )
    lines.append(
        f'  <text x="{pad}" y="{h - 28}" fill="#64748B" '
        f'font-family="system-ui,-apple-system,Segoe UI,sans-serif" font-size="13">'
        f'github.com/sudopimp/blackmirror-bench · independent research · not affiliated with Netflix / Channel 4 / Charlie Brooker</text>'
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
    # Keep legacy filename as alias of overall for older links
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
                "wrote": [str(p.name) for p in (overall, tracks, breakdown, howto, legacy)],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
