#!/usr/bin/env python3
"""Export dataset package for Hugging Face (dry-run safe)."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", type=str, default=str(ROOT / "export/hf"))
    args = ap.parse_args()

    out = Path(args.out)
    files = [
        ROOT / "data/episodes/registry.json",
        ROOT / "data/theses/index.json",
        ROOT / "gold/rpi_v1.json",
        ROOT / "data/splits/public_dev.json",
        ROOT / "data/splits/public_test.json",
        ROOT / "METHODOLOGY.md",
        ROOT / "SAFETY.md",
        ROOT / "README.md",
    ]
    missing = [str(p) for p in files if not p.exists()]
    if missing:
        raise SystemExit(f"missing required export files: {missing}")

    manifest = {
        "name": "blackmirror-bench",
        "version": "1.0.0",
        "files": [str(p.relative_to(ROOT)) for p in files],
        "note": "private_test excluded from public HF export by default",
    }
    if args.dry_run:
        print(json.dumps({"dry_run": True, "manifest": manifest}, indent=2))
        return

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for p in files:
        dest = out / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    # copy all theses
    tdir = out / "data/theses"
    tdir.mkdir(parents=True, exist_ok=True)
    for p in (ROOT / "data/theses").glob("*.json"):
        shutil.copy2(p, tdir / p.name)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"exported to {out}")


if __name__ == "__main__":
    main()
