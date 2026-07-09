#!/usr/bin/env python3
"""Scan public tasks for operational-harm content that should not ship."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Patterns that indicate operational weaponization content in the *task gold* or
# static task body beyond the controlled T5 boundary prompt.
FORBIDDEN = [
    r"here is how to build a lethal",
    r"deploy malware against",
    r"step-by-step guide to assassinate",
    r"weaponize the swarm as follows",
    r"exploit chain:",
    r"paste this payload",
]

# T5 prompts intentionally mention operational plans as the thing to refuse.
ALLOW_IF_BOUNDARY = [
    "step-by-step operational plan",
    "non-consenting people",
]


def main() -> int:
    hits = []
    for path in (ROOT / "tasks").rglob("*.jsonl"):
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            text = obj.get("prompt", "")
            # allow T5 boundary prompts
            if obj.get("track") == "T5" and obj.get("safety_class") == "boundary":
                continue
            for pat in FORBIDDEN:
                if re.search(pat, text, re.I):
                    hits.append(f"{path}:{i}: matched {pat}")
    # also scan gold rationales briefly
    gold = json.loads((ROOT / "gold/rpi_v1.json").read_text())
    for s in gold["scores"]:
        for pat in FORBIDDEN:
            if re.search(pat, s.get("rationale_short", ""), re.I):
                hits.append(f"gold:{s['thesis_id']}: matched {pat}")

    if hits:
        print("SAFETY FAIL:")
        for h in hits:
            print(" ", h)
        return 1
    print("OK safety_scan: no forbidden operational content in public tasks/gold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
