#!/usr/bin/env python3
"""Parallel Grok eval for BlackMirror-Bench (thread pool)."""

from __future__ import annotations

import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness.runner import (  # noqa: E402
    TRACK_FILES,
    _get_response,
    _score_response,
    load_gold,
    load_jsonl,
    load_theses,
)
from harness.metrics import bm_score  # noqa: E402

print_lock = threading.Lock()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="grok-4.5")
    ap.add_argument("--split", default="public_test")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=None, help="per-track limit")
    ap.add_argument("--out", required=True)
    ap.add_argument("--save-raw", action="store_true")
    args = ap.parse_args()

    gold = load_gold()
    theses = load_theses()
    raw_dir = ROOT / "results" / "raw" / args.model.replace("/", "_")
    if args.save_raw:
        raw_dir.mkdir(parents=True, exist_ok=True)

    jobs = []
    for track, path in TRACK_FILES.items():
        tasks = [t for t in load_jsonl(path) if t.get("split") == args.split or args.split == "all"]
        if args.limit:
            tasks = tasks[: args.limit]
        for task in tasks:
            jobs.append((track, task))

    results_rows: list[dict] = []
    done = 0
    total = len(jobs)

    def work(item):
        track, task = item
        tid = task["thesis_id"]
        g = gold.get(tid)
        th = theses.get(tid, {})
        raw_path = raw_dir / f"{task['task_id']}.txt"
        # skip if raw already exists (resume)
        if args.save_raw and raw_path.exists() and raw_path.stat().st_size > 20:
            resp = raw_path.read_text()
            err = None
        else:
            try:
                resp = _get_response(args.model, track, task, th, g)
                err = None
                if args.save_raw:
                    raw_path.write_text(resp)
            except Exception as e:
                resp = ""
                err = str(e)
        if err:
            s, d = 0.0, {"error": err}
        else:
            s, d = _score_response(track, resp, g, th)
        return {
            "task_id": task["task_id"],
            "track": track,
            "thesis_id": tid,
            "score": s,
            "detail": d,
            "response_preview": (resp or "")[:400],
            "error": err,
        }

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, j): j for j in jobs}
        for fut in as_completed(futs):
            row = fut.result()
            results_rows.append(row)
            done += 1
            with print_lock:
                print(f"[{done}/{total}] {row['task_id']} score={row['score']:.3f}", flush=True)

    # stable order
    order = {tid: i for i, (tr, t) in enumerate(jobs) for tid in [t["task_id"]]}
    results_rows.sort(key=lambda r: order.get(r["task_id"], 0))

    track_scores: dict[str, list[float]] = {t: [] for t in TRACK_FILES}
    for row in results_rows:
        track_scores[row["track"]].append(row["score"])
    means = {t: (sum(v) / len(v) if v else 0.0) for t, v in track_scores.items()}
    pen_vals = []
    for row in results_rows:
        p = row.get("detail", {}).get("penalties", {})
        if isinstance(p, dict) and "total" in p:
            pen_vals.append(float(p["total"]))
    pen_mean = sum(pen_vals) / len(pen_vals) if pen_vals else 0.0
    model_name = "grok-4.5" if args.model in ("xai", "grok", "grok-4.5") else args.model
    result = {
        "model": model_name,
        "split": args.split,
        "track_means": means,
        "penalty_mean": pen_mean,
        "bm_score": bm_score(means, penalty_total=0.1 * pen_mean),
        "n_tasks": len(results_rows),
        "as_of": "2026-07-09",
        "workers": args.workers,
        "details": results_rows,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    summary = {k: result[k] for k in ("model", "split", "bm_score", "track_means", "penalty_mean", "n_tasks", "as_of", "workers")}
    out.with_name(out.stem + "_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
