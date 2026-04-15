#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — AXIS-NIDDHI v3.0.2
SC_audio_converter.py — Patch: Shortcode [audio] → <audio> HTML nativo

ESTRATÉGIA (aprovada pela Aloka):
  Categoria A (localhost/beng_feb2026 + localhost/brasileirinho):
    - arquivo EXISTS (case-insensitive) → <audio> nativo com path relativo
    - arquivo MISSING                   → remove shortcode inteiro
  Categoria B (Google Drive / externo):
    - substitui por: <p><em>[áudio externo indisponível offline]</em></p>

ESCOPO: /beng/pipeline/09-csl/ (CSL canônico)
IDEMPOTENTE: sim — re-rodar não duplica conversões
MODO: dry-run por padrão, --apply para escrever

AUDIT LOG: /beng/pipeline/logs/SC_audio_YYYYMMDD_HHMMSS.log
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO — via config.py canônico (AXIS-NIDDHI V5.4 hardening)
# ==============================================================================

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DIR_09_CSL, DIR_13_SSG_ENGINE, LOG_DIR

CSL_DIR    = DIR_09_CSL
ASSETS_DIR = DIR_13_SSG_ENGINE / "assets" / "audio" / "en-US"
# LOG_DIR já importado de config

# URLs de origem conhecidas
LOCALHOST_PREFIXES = [
    "http://localhost/beng_feb2026/wp-content/uploads/",
    "http://localhost/brasileirinho/wp-content/uploads/",
]

GDRIVE_PATTERN = re.compile(r'drive\.google\.com')

# Padrão do shortcode WordPress (captura URL do mp3)
# Suporta aspas normais e &quot;
SHORTCODE_RE = re.compile(
    r'\[audio\s+(?:mp3|wav)=(?:&quot;|")((?:[^"&]|&amp;)*)(?:&quot;|")\](?:\[/audio\])?',
    re.IGNORECASE
)

NOTE_EXTERNAL = '<p><em>[áudio externo indisponível offline]</em></p>'

# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

def build_asset_index(assets_dir: Path) -> dict:
    """Índice case-insensitive: lowercase_filename → Path real"""
    index = {}
    if assets_dir.exists():
        for f in assets_dir.iterdir():
            if f.is_file():
                index[f.name.lower()] = f
    return index


def extract_filename(url: str) -> str:
    """Extrai o nome do arquivo da URL do shortcode."""
    return url.rstrip("/").split("/")[-1]


def is_external(url: str) -> bool:
    return bool(GDRIVE_PATTERN.search(url)) or (
        url.startswith("http") and
        not any(url.startswith(p) for p in LOCALHOST_PREFIXES)
    )


def convert_shortcodes(html: str, asset_index: dict, stats: dict) -> str:
    """
    Processa todos os shortcodes [audio] em um bloco HTML.
    Retorna HTML transformado.
    """
    def replace_match(m):
        url = m.group(1).strip()

        # Categoria B — externo (Google Drive etc.)
        if is_external(url):
            stats["external"] += 1
            return NOTE_EXTERNAL

        # Categoria A/C — localhost
        filename = extract_filename(url)
        filename_lower = filename.lower()

        asset_path = asset_index.get(filename_lower)
        # Fallback: espaços → hífens (ex: "Dasa Akusala.mp3" → "dasa-akusala.mp3")
        if asset_path is None:
            filename_hyphen = filename_lower.replace(" ", "-")
            asset_path = asset_index.get(filename_hyphen)

        if asset_path:
            # Arquivo existe — gera <audio> nativo
            real_name = asset_path.name
            relative = f"../../assets/audio/en-US/{real_name}"
            stats["converted"] += 1
            return (
                f'<audio controls preload="none" style="width:100%;margin:0.5em 0">'
                f'<source src="{relative}" type="audio/mpeg">'
                f'</audio>'
            )
        else:
            # Arquivo não existe — remove shortcode
            stats["removed"] += 1
            stats["removed_files"].append(filename)
            return ""

    return SHORTCODE_RE.sub(replace_match, html)


# ==============================================================================
# PROCESSAMENTO
# ==============================================================================

def process_file(html_path: Path, asset_index: dict, apply: bool, log) -> dict:
    stats = {"converted": 0, "external": 0, "removed": 0, "removed_files": []}

    original = html_path.read_text(encoding="utf-8")

    # Verificação rápida — evita processar arquivos sem shortcodes
    if "[audio" not in original.lower():
        return stats

    transformed = convert_shortcodes(original, asset_index, stats)

    total = stats["converted"] + stats["external"] + stats["removed"]
    if total == 0:
        return stats

    changed = transformed != original
    pdpn = html_path.parents[2].name  # 09-csl/PDPN/source/lang/content.html

    if not changed:
        log(f"  SKIP (sem mudança): {pdpn}")
        return stats

    log(f"  {pdpn} → converted={stats['converted']} external={stats['external']} removed={stats['removed']}")
    if stats["removed_files"]:
        for f in stats["removed_files"]:
            log(f"    REMOVED (not found): {f}")

    if apply:
        html_path.write_text(transformed, encoding="utf-8")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Converte shortcodes [audio] do CSL em <audio> HTML nativo."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Aplicar mudanças (padrão: dry-run)")
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY_RUN"

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"SC_audio_{mode}_{ts}.log"
    log_lines = []

    def log(msg: str):
        print(msg)
        log_lines.append(msg)

    log(f"=== SC_audio_converter.py ({mode}) ===")
    log(f"CSL:    {CSL_DIR}")
    log(f"ASSETS: {ASSETS_DIR}")
    log(f"LOG:    {log_path}")
    log("")

    # Construir índice de assets
    asset_index = build_asset_index(ASSETS_DIR)
    log(f"Assets indexados: {len(asset_index)}")
    log("")

    # Totais globais
    totals = {"converted": 0, "external": 0, "removed": 0,
              "files_touched": 0, "removed_files": []}

    # Iterar CSL
    html_files = sorted(CSL_DIR.rglob("content.html"))
    log(f"Arquivos content.html encontrados: {len(html_files)}")
    log("")

    for html_path in html_files:
        stats = process_file(html_path, asset_index, args.apply, log)
        touched = stats["converted"] + stats["external"] + stats["removed"]
        if touched > 0:
            totals["files_touched"] += 1
            totals["converted"]     += stats["converted"]
            totals["external"]      += stats["external"]
            totals["removed"]       += stats["removed"]
            totals["removed_files"] += stats["removed_files"]

    log("")
    log("=" * 50)
    log(f"RESULTADO FINAL ({mode})")
    log(f"  Arquivos tocados   : {totals['files_touched']}")
    log(f"  Shortcodes → audio : {totals['converted']}")
    log(f"  Externos → nota    : {totals['external']}")
    log(f"  Removidos (missing): {totals['removed']}")
    if totals["removed_files"]:
        log(f"  Arquivos não encontrados:")
        for f in sorted(set(totals["removed_files"])):
            log(f"    - {f}")
    if not args.apply:
        log("")
        log("  ⚠  DRY-RUN: nenhum arquivo foi alterado.")
        log("  ➜  Para aplicar: python3 SC_audio_converter.py --apply")
    log("=" * 50)

    log_path.write_text("\n".join(log_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
