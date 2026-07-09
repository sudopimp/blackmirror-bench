#!/usr/bin/env python3
"""Rescore saved raw responses without re-calling the API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.runner import (  # noqa: E402
    TRACK_FILES,
    _score_response,
    load_gold,
    load_jsonl,
    load_theses,
)
from harness.metrics import bm_score  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--model", default="grok-4.5")
    ap.add_argument("--split", default="public_test")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir)
    gold = load_gold()
    theses = load_theses()
    track_scores: dict[str, list[float]] = {t: [] for t in TRACK_FILES}
    details = []

    for track, path in TRACK_FILES.items():
        tasks = [t for t in load_jsonl(path) if t.get("split") == args.split or args.split == "all"]
        for task in tasks:
            raw_path = raw_dir / f"{task['task_id']}.txt"
            if not raw_path.exists():
                continue
            resp = raw_path.read_text()
            tid = task["thesis_id"]
            g = gold.get(tid)
            th = theses.get(tid, {})
            s, d = _score_response(track, resp, g, th)
            track_scores[track].append(s)
            details.append({
                "task_id": task["task_id"],
                "track": track,
                "thesis_id": tid,
                "score": s,
                "detail": d,
                "response_preview": resp[:400],
            })

    means = {t: (sum(v) / len(v) if v else 0.0) for t, v in track_scores.items()}
    pen_vals = []
    for row in details:
        p = row.get("detail", {}).get("penalties", {})
        if isinstance(p, dict) and "total" in p:
            pen_vals.append(float(p["total"]))
    pen_mean = sum(pen_vals) / len(pen_vals) if pen_vals else 0.0
    result = {
        "model": args.model,
        "split": args.split,
        "track_means": means,
        "penalty_mean": pen_mean,
        "bm_score": bm_score(means, penalty_total=0.1 * pen_mean),
        "n_tasks": len(details),
        "as_of": "2026-07-09",
        "details": details,
        "rescored_from": str(raw_dir),
    }
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2) + "\n")
    summary = {k: result[k] for k in ("model", "split", "bm_score", "track_means", "penalty_mean", "n_tasks", "as_of")}
    out.with_name(out.stem + "_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
