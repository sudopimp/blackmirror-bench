"""Shared visual tokens for BlackMirror-Bench SOTA SVG charts."""

from __future__ import annotations

# Canvas
W = 1200
# Avoid nested double-quotes inside SVG attribute values.
FONT = "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
MONO = "ui-monospace, SF Mono, Cascadia Code, Menlo, Consolas, monospace"

# Palette — dark mirror glass
BG0 = "#06080F"
BG1 = "#0B1020"
CARD = "#0F1524"
CARD_EDGE = "rgba(255,255,255,0.08)"
RAIL = "#151C2C"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
FAINT = "#64748B"
ACCENT = "#7DD3FC"
ACCENT_2 = "#A78BFA"
TEAL = "#2DD4BF"
GOLD = "#FBBF24"
GREEN = "#4ADE80"
PINK = "#F472B6"
AMBER = "#FBBF24"

# Gradients for model bars (start → end)
MODEL_GRADS = {
    "Grok 4.5": ("#2DD4BF", "#67E8F9"),
    "Codex Sol (max)": ("#8B5CF6", "#C4B5FD"),
    "Codex Sol (high)": ("#7C3AED", "#A78BFA"),
    "MiniMax M3": ("#22C55E", "#86EFAC"),
    "z.ai GLM-5.2": ("#EAB308", "#FDE68A"),
    "z.ai GLM-5.2 (Coding Plan)": ("#EAB308", "#FDE68A"),
    "z.ai GLM-4.5": ("#CA8A04", "#FBBF24"),
    "Heuristic baseline": ("#64748B", "#94A3B8"),
}

TRACK_COLORS = {
    "T1": "#2DD4BF",
    "T2": "#38BDF8",
    "T3": "#A78BFA",
    "T4": "#F472B6",
    "T5": "#FBBF24",
}


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def defs_block(uid: str = "main") -> str:
    """Common gradients + soft glow for all charts."""
    return f"""  <defs>
    <linearGradient id="bg-{uid}" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="#0C1222"/>
      <stop offset="55%" stop-color="#080C16"/>
      <stop offset="100%" stop-color="#05070E"/>
    </linearGradient>
    <radialGradient id="glowL-{uid}" cx="12%" cy="0%" r="55%">
      <stop offset="0%" stop-color="rgba(125,211,252,0.14)"/>
      <stop offset="100%" stop-color="rgba(125,211,252,0)"/>
    </radialGradient>
    <radialGradient id="glowR-{uid}" cx="92%" cy="8%" r="45%">
      <stop offset="0%" stop-color="rgba(167,139,250,0.12)"/>
      <stop offset="100%" stop-color="rgba(167,139,250,0)"/>
    </radialGradient>
    <linearGradient id="bar-teal-{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#14B8A6"/><stop offset="100%" stop-color="#67E8F9"/>
    </linearGradient>
    <linearGradient id="bar-violet-{uid}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#7C3AED"/><stop offset="100%" stop-color="#C4B5FD"/>
    </linearGradient>
    <linearGradient id="card-shine-{uid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="rgba(255,255,255,0.04)"/>
      <stop offset="40%" stop-color="rgba(255,255,255,0)"/>
    </linearGradient>
    <filter id="soft-{uid}" x="-20%" y="-50%" width="140%" height="200%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="soft-sm-{uid}" x="-10%" y="-40%" width="120%" height="180%">
      <feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>"""


def canvas(w: int, h: int, uid: str, aria: str) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(aria)}">',
        defs_block(uid),
        f'  <rect width="100%" height="100%" fill="url(#bg-{uid})" rx="28"/>',
        f'  <rect width="100%" height="100%" fill="url(#glowL-{uid})" rx="28"/>',
        f'  <rect width="100%" height="100%" fill="url(#glowR-{uid})" rx="28"/>',
        # fine top edge line
        f'  <rect x="1" y="1" width="{w - 2}" height="1.5" fill="rgba(255,255,255,0.06)" rx="1"/>',
    ]


def text(
    x: float,
    y: float,
    s: str,
    *,
    size: int = 16,
    fill: str = TEXT,
    weight: str = "600",
    anchor: str = "start",
    mono: bool = False,
    opacity: float | None = None,
) -> str:
    fam = MONO if mono else FONT
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (
        f'  <text x="{x}" y="{y}" fill="{fill}" font-family="{fam}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{op}>{esc(s)}</text>'
    )


def model_bar_gradient(name: str, uid: str, idx: int) -> tuple[str, str]:
    """Return (gradient_id_def_snippet, fill_url)."""
    start, end = MODEL_GRADS.get(name, ("#64748B", "#94A3B8"))
    gid = f"mg-{uid}-{idx}"
    defn = (
        f'    <linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{start}"/>'
        f'<stop offset="100%" stop-color="{end}"/>'
        f"</linearGradient>"
    )
    return defn, f"url(#{gid})"
