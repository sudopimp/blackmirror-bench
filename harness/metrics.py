"""Metrics and anti-dark-pattern penalties for BlackMirror-Bench."""

from __future__ import annotations

import math
import re
from typing import Any


AXES = ["THESIS_POSS", "AI_EXEC", "TRL_comp", "SYS", "ECON", "SOC", "FID"]


def mae(y_true: list[float], y_pred: list[float]) -> float:
    if not y_true:
        return 0.0
    return sum(abs(a - b) for a, b in zip(y_true, y_pred)) / len(y_true)


def brier_binary(prob: float, outcome: int) -> float:
    """Brier for a single binary event; outcome in {0,1}, prob in [0,1]."""
    p = min(1.0, max(0.0, prob))
    return (p - outcome) ** 2


def expected_calibration_error(
    confidences: list[float], correct: list[bool], n_bins: int = 10
) -> float:
    if not confidences:
        return 0.0
    bins: list[list[int]] = [[] for _ in range(n_bins)]
    for i, c in enumerate(confidences):
        b = min(n_bins - 1, int(c * n_bins))
        bins[b].append(i)
    ece = 0.0
    n = len(confidences)
    for idxs in bins:
        if not idxs:
            continue
        acc = sum(1 for i in idxs if correct[i]) / len(idxs)
        conf = sum(confidences[i] for i in idxs) / len(idxs)
        ece += (len(idxs) / n) * abs(acc - conf)
    return ece


def _norm_tag(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _tags_soft_match(g: str, p: str) -> bool:
    """True if tags match exactly, by containment, or by shared substantive tokens."""
    g, p = _norm_tag(g), _norm_tag(p)
    if not g or not p:
        return False
    if g == p or g in p or p in g:
        return True
    gt = {t for t in g.split("_") if len(t) > 2}
    pt = {t for t in p.split("_") if len(t) > 2}
    if not gt or not pt:
        return False
    # soft hit if ≥50% of gold tokens appear in pred (or reverse for short gold)
    inter = gt & pt
    return (len(inter) / len(gt) >= 0.5) or (len(inter) / len(pt) >= 0.5 and len(gt) <= 2)


def set_f1(gold: set[str], pred: set[str], soft: bool = False) -> float:
    if not gold and not pred:
        return 1.0
    if not gold or not pred:
        return 0.0
    if not soft:
        tp = len(gold & pred)
    else:
        # greedy bipartite soft matches
        pred_list = list(pred)
        used = set()
        tp = 0
        for g in gold:
            for i, p in enumerate(pred_list):
                if i in used:
                    continue
                if _tags_soft_match(g, p) or _norm_tag(g) == _norm_tag(p):
                    used.add(i)
                    tp += 1
                    break
    prec = tp / len(pred)
    rec = tp / len(gold)
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


def axis_mae(gold_axes: dict[str, Any], pred_axes: dict[str, Any]) -> dict[str, float]:
    out = {}
    for ax in AXES:
        g = gold_axes.get(ax, {})
        p = pred_axes.get(ax, {})
        if g.get("tier") == "NA":
            # model should also mark NA or predict ~0
            pv = p.get("value", 50)
            out[ax] = 0.0 if p.get("tier") == "NA" or pv == 0 else abs(float(pv))
            continue
        gv = float(g.get("value", 0))
        pv = float(p.get("value", 50))
        out[ax] = abs(gv - pv)
    out["mean"] = sum(out.values()) / len(AXES)
    return out


# --- Anti-dark-pattern penalties ---

SCI_FI_COLLAPSE_PATTERNS = [
    r"\bconsciousness (?:is |has been )?solved\b",
    r"\bmind upload(?:ing)? (?:is |has been )?(?:solved|achieved|real|done)\b",
    r"\bwe (?:already )?have (?:true )?digital consciousness\b",
    r"\bcookies? (?:are|is) (?:already )?real\b",
    r"\bfull dive vr is mainstream\b",
]

FAKE_CITE_PATTERNS = [
    r"\b[A-Z][a-z]+ et al\.,? \d{4}\b",
    r"\bdoi:\s*10\.\d+",
    r"\[[0-9]+\]",
]

HYPE_MARKERS = [
    r"\balready completely real\b",
    r"\b100% possible today\b",
    r"\bthis is not science fiction anymore\b",
    r"\bfully implemented worldwide\b",
]


def has_https_url(text: str) -> bool:
    return bool(re.search(r"https://[^\s)]+", text))


def fake_cite_penalty(text: str) -> float:
    """Penalty 0-1: citation-like patterns without any https URL."""
    if has_https_url(text):
        return 0.0
    hits = sum(1 for p in FAKE_CITE_PATTERNS if re.search(p, text, re.I))
    return min(1.0, hits * 0.34)


def sci_fi_collapse_penalty(text: str, gold_thesis_poss: float | None = None) -> float:
    """Penalty when text claims hard sci-fi is solved, especially if gold is low."""
    hits = sum(1 for p in SCI_FI_COLLAPSE_PATTERNS if re.search(p, text, re.I))
    if hits == 0:
        return 0.0
    base = min(1.0, hits * 0.4)
    if gold_thesis_poss is not None and gold_thesis_poss < 30:
        return min(1.0, base + 0.3)
    return base


def hype_inflation_penalty(pred_value: float, gold_value: float, threshold: float = 25.0) -> float:
    """Penalty when prediction exceeds gold by more than threshold points."""
    delta = pred_value - gold_value
    if delta <= threshold:
        return 0.0
    return min(1.0, (delta - threshold) / 50.0)


def hype_text_penalty(text: str) -> float:
    hits = sum(1 for p in HYPE_MARKERS if re.search(p, text, re.I))
    return min(1.0, hits * 0.35)


def total_penalties(
    text: str,
    pred_thesis_poss: float | None = None,
    gold_thesis_poss: float | None = None,
) -> dict[str, float]:
    p_fake = fake_cite_penalty(text)
    p_scifi = sci_fi_collapse_penalty(text, gold_thesis_poss)
    p_hype_t = hype_text_penalty(text)
    p_hype_n = 0.0
    if pred_thesis_poss is not None and gold_thesis_poss is not None:
        p_hype_n = hype_inflation_penalty(pred_thesis_poss, gold_thesis_poss)
    total = min(1.0, 0.35 * p_fake + 0.35 * p_scifi + 0.15 * p_hype_t + 0.15 * p_hype_n)
    return {
        "fake_cite": p_fake,
        "sci_fi_collapse": p_scifi,
        "hype_text": p_hype_t,
        "hype_inflation": p_hype_n,
        "total": total,
    }


def bm_score(track_scores: dict[str, float], penalty_total: float = 0.0) -> float:
    """
    BM-Score = 0.30 T1 + 0.20 T2 + 0.20 T3 + 0.15 T4 + 0.15 T5 - penalties
    track_scores values expected in [0,1]
    """
    weights = {"T1": 0.30, "T2": 0.20, "T3": 0.20, "T4": 0.15, "T5": 0.15}
    s = 0.0
    for k, w in weights.items():
        s += w * float(track_scores.get(k, 0.0))
    return max(0.0, s - penalty_total)


def t1_score_from_mae(mean_mae: float) -> float:
    """Map mean absolute error on 0-100 axes to [0,1] score."""
    return max(0.0, 1.0 - mean_mae / 100.0)


def confidence_from_ci(ci_low: float, ci_high: float) -> float:
    width = max(0.0, ci_high - ci_low)
    # narrower CI → higher confidence; width 0 → 1.0, width 100 → ~0
    return max(0.0, min(1.0, 1.0 - width / 100.0))
