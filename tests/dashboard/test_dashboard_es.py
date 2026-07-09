"""Structural + Spanish UI checks on the shipped dashboard."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASH = ROOT / "dashboard"
INDEX = DASH / "index.html"
APP = DASH / "app.js"
CSS = DASH / "styles.css"


def test_lang_es_and_spanish_chrome():
    html = INDEX.read_text(encoding="utf-8")
    assert re.search(r'<html\s+lang="es"', html)
    # User-visible Spanish (not the old English stub)
    required = [
        "Ranking de modelos",
        "Ejes co-primarios",
        "Pistas de evaluación",
        "No está afiliado a Netflix",
        "Channel 4",
        "Charlie Brooker",
        "BM-Score",
        "Posibilidad de la tesis",  # may be in embedded JSON
        "Calibración",
    ]
    for s in required:
        assert s in html, f"missing Spanish UI string: {s}"
    # Old English stub must not be the main disclaimer
    assert "Not affiliated with Netflix" not in html


def test_sections_present():
    html = INDEX.read_text(encoding="utf-8")
    for sid in ("intro", "ranking", "ejes", "pistas", "aviso"):
        assert f'id="{sid}"' in html


def test_css_is_more_than_browser_defaults():
    css = CSS.read_text(encoding="utf-8")
    assert "--bg-0" in css or "background" in css
    assert "@media" in css  # responsive
    assert "font-family" in css
    assert "focus-visible" in css or ":focus" in css


def test_embedded_snapshot_has_real_scores():
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(
        r'<script type="application/json" id="bmb-data">\s*(\{.*?\})\s*</script>',
        html,
        re.S,
    )
    assert m, "embedded #bmb-data JSON required for file:// "
    data = json.loads(m.group(1))
    assert data["lang"] == "es"
    top = data["leaderboard"][0]
    assert top["model_id"] == "grok-4.5"
    assert abs(top["bm_score"] - 0.773) < 0.005


def test_app_js_no_es_modules():
    js = APP.read_text(encoding="utf-8")
    # No ES module syntax (allow the word "export" in comments)
    assert not re.search(r"(?m)^\s*export\s+", js)
    assert not re.search(r"(?m)^\s*import\s+", js)
    assert "type=\"module\"" not in js
    assert "shapeLeaderboard" in js
    assert "BMB" in js


def test_shape_leaderboard_via_node_if_available():
    """Drive the real shapeLeaderboard in app.js when Node is present."""
    node = subprocess.run(["which", "node"], capture_output=True, text=True)
    if node.returncode != 0:
        pytest.skip("node not available")
    script = r"""
const fs = require('fs');
const path = require('path');
const code = fs.readFileSync(process.argv[1], 'utf8');
// Evaluate app.js in a fake window
const window = global;
eval(code);
const rows = BMB.shapeLeaderboard([
  {model_id:'b', display_name:'B', bm_score:0.5, tracks:{T1:0.1,T2:0.2,T3:0.3,T4:0.4,T5:0.5}, n_tasks:10},
  {model_id:'a', display_name:'A', bm_score:0.9, tracks:{T1:0.9,T2:0.8,T3:0.7,T4:0.6,T5:1}, n_tasks:10}
]);
if (rows[0].model_id !== 'a' || rows[0].rank !== 1) process.exit(2);
if (rows[1].rank !== 2) process.exit(3);
console.log(JSON.stringify({ok:true, top: rows[0].bm_score}));
"""
    r = subprocess.run(
        ["node", "-e", script, str(APP)],
        capture_output=True,
        text=True,
        cwd=str(DASH),
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "ok" in r.stdout
