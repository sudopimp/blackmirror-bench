#!/usr/bin/env python3
"""Freeze content hash of gold + theses for reproducibility."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    paths = sorted((ROOT / "data/theses").glob("*.json"))
    paths += [ROOT / "gold/rpi_v1.json", ROOT / "data/episodes/registry.json"]
    h = hashlib.sha256()
    entries = []
    for p in paths:
        if not p.exists():
            continue
        digest = file_hash(p)
        rel = str(p.relative_to(ROOT))
        entries.append({"path": rel, "sha256": digest})
        h.update(digest.encode())
    freeze = {
        "snapshot_id": "rpi_v1",
        "aggregate_sha256": h.hexdigest(),
        "files": entries,
    }
    out = ROOT / "gold/FREEZE.json"
    out.write_text(json.dumps(freeze, indent=2) + "\n")
    print(json.dumps({"aggregate_sha256": freeze["aggregate_sha256"], "n_files": len(entries)}))


if __name__ == "__main__":
    main()
