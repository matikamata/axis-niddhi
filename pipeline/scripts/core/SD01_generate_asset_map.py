#!/usr/bin/env python3
"""
S14_ASSET_RESOLVER — generate_asset_map.py
===========================================
Escaneia CSL, detecta URLs WP, gera asset_map.json.

HARDENING PASS — AXIS-NIDDHI (2026-03-05)
  ★ Removido: CSL_DIR = Path("/beng/pipeline/09-csl")  ← hardcode absoluto
  ★ Adicionado: import de DIR_09_CSL e DIR_14_ASSETS via config.py
  ★ Lógica inalterada.
"""

import re
import json
import sys
from pathlib import Path

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent / "scripts"))

from config import DIR_09_CSL, DIR_14_ASSETS

CSL_DIR  = DIR_09_CSL                          # /beng/pipeline/09-csl
OUT_FILE = DIR_14_ASSETS / "asset_map.json"    # /beng/pipeline/S14_asset_resolver/asset_map.json

# ==============================================================================
# 🔍  SCANNER
# ==============================================================================
WP_RE = re.compile(
    r'(?:https?://(?:localhost|127\.0\.0\.1)[^"\']*)?'
    r'(/wp-content/uploads/[^\s"\'<>]+)'
)

urls: set[str] = set()
for html in CSL_DIR.rglob("*.html"):
    try:
        for m in WP_RE.finditer(html.read_text(encoding="utf-8", errors="ignore")):
            urls.add(m.group(1))
    except Exception:
        pass

asset_map = {
    url: f"assets/images/{Path(url).name}"
    for url in sorted(urls)
}

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(
    json.dumps(asset_map, indent=2, ensure_ascii=False, sort_keys=True),
    encoding="utf-8",
)
print(f"✅ asset_map.json: {len(asset_map)} URLs → {OUT_FILE}")
