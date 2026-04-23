#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — SD01_generate_asset_map.py
=============================================
Escaneia a CSL (09-csl/), detecta URLs /wp-content/uploads/,
e gera asset_map.json no diretório de metadados do pipeline.

Versão  : 2.0 (bengyond-playground — 2026-04-20)
Refactor:
  ★ sys.path corrigido — import direto de config.py em scripts/core/
  ★ Output: pipeline/metadata/asset_map.json  (não mais S14 legado)
  ★ Filtro por ACCEPTED_EXTS — consistente com SG04
  ★ Fail-fast se CSL não existir
  ★ Wrapper main() + relatório de contagem

USO:
  python3 pipeline/scripts/core/SD01_generate_asset_map.py
"""

import re
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

# ==============================================================================
# ⚙️  BOOTSTRAP — config.py canônico (scripts/core/config.py)
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent   # pipeline/scripts/core/
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, DIR_09_CSL, METADATA_DIR

# Output: pipeline/metadata/asset_map.json
# METADATA_DIR já aponta para pipeline/metadata/ conforme config.py
OUT_FILE = METADATA_DIR / "asset_map.json"
WP_UPLOADS_DIR = BASE_DIR.parent / "wordpress" / "wp-content" / "uploads"
CF_PAGES_MAX_BYTES = int(os.environ.get("BENG_PAGES_MAX_FILE_BYTES", str(25 * 1024 * 1024)))
EXTERNAL_UPLOADS_BASE = os.environ.get(
    "BENG_EXTERNAL_UPLOADS_BASE_URL",
    "https://puredhamma.net/wp-content/uploads",
).rstrip("/")

# Extensões aceitas — mesmo conjunto do SG04 (consistência garantida)
ACCEPTED_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf"}

# ==============================================================================
# 🔍  SCANNER — regex para URLs /wp-content/uploads/
# ==============================================================================
WP_RE = re.compile(
    r'(?:https?://(?:localhost|127\.0\.0\.1)[^"\']*)?'
    r'(/wp-content/uploads/[^\s"\'<>]+)'
)


def _target_for_upload_url(url: str) -> str:
    """
    Decide target path for an upload URL:
    - <= 25 MiB: local static asset path (assets/images/<filename>)
    - > 25 MiB: external canonical URL (EXTERNAL_UPLOADS_BASE/<relative_path>)
    """
    rel_upload = url.replace("/wp-content/uploads/", "", 1).lstrip("/")
    source_file = WP_UPLOADS_DIR / rel_upload

    if source_file.exists():
        try:
            if source_file.stat().st_size > CF_PAGES_MAX_BYTES:
                encoded_rel = quote(rel_upload, safe="/")
                return f"{EXTERNAL_UPLOADS_BASE}/{encoded_rel}"
        except OSError:
            pass

    return f"assets/images/{Path(url).name}"


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main() -> None:
    print(f"⚙️  BASE_DIR    : {BASE_DIR}")
    print(f"⚙️  CSL_DIR     : {DIR_09_CSL}")
    print(f"⚙️  OUT_FILE    : {OUT_FILE}")
    print(f"⚙️  WP_UPLOADS  : {WP_UPLOADS_DIR}")
    print(f"⚙️  MAX_FILE    : {CF_PAGES_MAX_BYTES} bytes ({CF_PAGES_MAX_BYTES / (1024 * 1024):.1f} MiB)")
    print(f"⚙️  EXTERNAL    : {EXTERNAL_UPLOADS_BASE}")

    # FAIL-FAST
    if not BASE_DIR.exists():
        print(f"❌ FAIL-FAST: BASE_DIR não existe: {BASE_DIR}", file=sys.stderr)
        sys.exit(1)

    if not DIR_09_CSL.exists():
        print(f"❌ FAIL-FAST: CSL não encontrada: {DIR_09_CSL}", file=sys.stderr)
        sys.exit(1)
    if not WP_UPLOADS_DIR.exists():
        print(f"❌ FAIL-FAST: uploads não encontrado: {WP_UPLOADS_DIR}", file=sys.stderr)
        sys.exit(1)

    # Scan
    html_files = list(DIR_09_CSL.rglob("*.html"))
    if not html_files:
        print(f"❌ FAIL-FAST: Nenhum .html encontrado em {DIR_09_CSL}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Varrendo {len(html_files)} arquivos HTML na CSL...")

    urls: set[str] = set()
    parse_errors = 0

    for html in html_files:
        try:
            text = html.read_text(encoding="utf-8", errors="ignore")
            for m in WP_RE.finditer(text):
                url = m.group(1)
                ext = Path(url).suffix.lower()
                if ext in ACCEPTED_EXTS:
                    urls.add(url)
        except Exception as e:
            print(f"   ⚠️  Erro ao processar {html.name}: {e}", file=sys.stderr)
            parse_errors += 1

    # Gera mapa: url → caminho local ou URL externa (se oversized)
    asset_map = {
        url: _target_for_upload_url(url)
        for url in sorted(urls)
    }
    externalized = sum(1 for target in asset_map.values() if target.startswith("http"))

    # Salva
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(asset_map, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )

    # Relatório
    delta = len(asset_map) - 185   # baseline da versão anterior
    delta_str = f"+{delta}" if delta >= 0 else str(delta)

    print("\n" + "=" * 55)
    print("📊  RELATÓRIO — SD01_generate_asset_map")
    print("=" * 55)
    print(f"   Arquivos HTML varridos  : {len(html_files)}")
    print(f"   Erros de parsing        : {parse_errors}")
    print(f"   URLs mapeadas           : {len(asset_map)}")
    print(f"   URLs externalizadas     : {externalized}")
    print(f"   vs versão anterior (185): {delta_str}")
    print(f"   Output                  : {OUT_FILE}")
    print("=" * 55)
    print("\n✅ asset_map.json gerado com sucesso!")
    print("\n▶️  Próximo passo:")
    print("   python3 pipeline/scripts/core/SG04_harvest_assets.py")


if __name__ == "__main__":
    main()
