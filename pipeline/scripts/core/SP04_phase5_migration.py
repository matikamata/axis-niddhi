#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — Phase 5 Migration
============================================
Mass Migration to Golden Sample (CSL v1.0)

HARDENING PASS — AXIS-NIDDHI (2026-03-05)
  ★ Removido: BASE_DIR = Path("/beng/pipeline")  ← hardcode absoluto
  ★ Removido: CSL_DIR  = BASE_DIR / "09-csl"     ← derivado do hardcode
  ★ Removido: LOG_DIR  = BASE_DIR / "logs"        ← derivado do hardcode
  ★ Adicionado: import de BASE_DIR, DIR_09_CSL, LOG_DIR via config.py
  ★ Lógica de migração inalterada.

USAGE:
  python3 phase5_migration.py           # dry-run (padrão seguro)
  python3 phase5_migration.py --apply   # aplica mudanças no disco
"""

import os
import json
import hashlib
import argparse
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent / "scripts"))

from config import BASE_DIR, DIR_09_CSL, LOG_DIR

CSL_DIR = DIR_09_CSL   # /beng/pipeline/09-csl

# ==============================================================================
# 🛠️  UTILITÁRIOS
# ==============================================================================
def setup_logger(mode: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = LOG_DIR / f"phase5_migration_{mode}_{timestamp}.log"

    def log(msg: str, status: str = "INFO"):
        icons = {
            "INFO":  "ℹ️",
            "OK":    "✅",
            "WARN":  "⚠️",
            "ERROR": "❌",
            "SKIP":  "⏭️",
            "DRY":   "🔍",
        }
        icon = icons.get(status, "ℹ️")
        print(f"{icon} [{status}] {msg}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] {msg}\n"
            )

    return log


# [20260220] calculate_sha256_string() REMOVIDA. Substituída por calculate_sha256_file()
# que lê o arquivo em bytes (rb) — padrão consistente com Scripts 09 e 12.
def calculate_sha256_file(file_path: Path) -> str:
    """Calcula SHA-256 do arquivo em bytes — padrão do pipeline."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clean_html_fragment(raw_html: str) -> str:
    """
    Transforma HTML em fragmento puro conforme Golden Sample.
    Remove wrappers <html>, <head>, <body>.
    Remove <script>, <style>.
    NÃO altera o texto <p>.
    """
    content = re.sub(r"<!--.*?-->", "", raw_html, flags=re.DOTALL)
    content = re.sub(r"<!DOCTYPE.*?>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<html[^>]*>.*?<body[^>]*>", "", content,
                     flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"</body>.*?</html>", "", content,
                     flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<script[^>]*>.*?</script>", "", content,
                     flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<style[^>]*>.*?</style>", "", content,
                     flags=re.DOTALL | re.IGNORECASE)
    return content.strip()


# ==============================================================================
# 🔄  MIGRAÇÃO DE UM POST
# ==============================================================================
def process_post(pdpn_dir: Path, apply: bool, log) -> bool:
    """
    Migra um único post para o Golden Sample format.
    Retorna True se processado com sucesso, False se erro/skip.
    """
    pdpn = pdpn_dir.name

    old_json_path = pdpn_dir / "meta" / "identity.json"
    source_en_path = pdpn_dir / "source" / "en-US" / "content.html"
    source_pt_path = pdpn_dir / "source" / "pt-BR" / "content.html"
    semantic_path  = pdpn_dir / "meta" / "semantic.json"

    # Validação mínima
    if not old_json_path.exists():
        log(f"{pdpn} - identity.json ausente. Skipping.", "SKIP")
        return False

    if not source_en_path.exists():
        log(f"{pdpn} - source/en-US/content.html ausente. Skipping.", "SKIP")
        return False

    try:
        old_data = json.loads(old_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"{pdpn} - Falha ao ler identity.json: {e}", "ERROR")
        return False

    # Dry-run: apenas reporta
    if not apply:
        log(f"[DRY] {pdpn} → seria migrado", "DRY")
        return True

    try:
        # Limpar fragmento HTML
        raw_html     = source_en_path.read_text(encoding="utf-8")
        clean_html   = clean_html_fragment(raw_html)
        source_en_path.write_text(clean_html, encoding="utf-8")

        # Hash calculado APÓS escrita — reflete conteúdo real persistido
        # [20260220] hash do arquivo real
        new_hash = calculate_sha256_file(source_en_path)

        # Recuperar campos do identity legado
        wp_id          = old_data.get("original_wp_id") or old_data.get("wp_id")
        title_en       = (
            old_data.get("titles", {}).get("en") or
            old_data.get("title_en") or
            "Unknown"
        )
        title_pt       = old_data.get("titles", {}).get("pt")
        extraction_date = old_data.get("origin", {}).get("extraction_date") or get_utc_now()

        # Novo identity canônico
        new_identity = {
            "schema_version": "3.1",
            "identity": {
                "pdpn":           pdpn,
                "slug_root":      old_data.get("identity", {}).get("slug_root") or "",
                "fin_dex":        old_data.get("identity", {}).get("fin_dex") or "",
            },
            "origin": {
                "source":         "wordpress_export",
                "original_url":   (
                    f"https://puredhamma.net/?p={wp_id}"
                    if wp_id else None
                ),
                "original_wp_id": wp_id,
                "extraction_date": extraction_date,
            },
            "titles": {
                "en":        title_en,
                "en_source": "legacy_migration",
                "pt":        title_pt,
                "pt_source": None,
            },
            "artifacts": {
                "en-US": {
                    "status":           "canonical",
                    "file_path":        "source/en-US/content.html",
                    "integrity_sha256": new_hash,  # [20260220]
                },
                "pt-BR": {
                    "status":           "missing",
                    "file_path":        "source/pt-BR/content.html",
                    "integrity_sha256": None,
                },
            },
        }

        # Novo semantic canônico
        new_semantic = {
            "schema_version": "1.0",
            "pdpn":           pdpn,
            "slug_root":      new_identity["identity"]["slug_root"],
            "generated_at":   get_utc_now(),
        }

        old_json_path.write_text(
            json.dumps(new_identity, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        semantic_path.parent.mkdir(parents=True, exist_ok=True)
        semantic_path.write_text(
            json.dumps(new_semantic, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        log(f"{pdpn} - Migrado com sucesso.", "OK")
        return True

    except Exception as e:
        log(f"{pdpn} - Falha crítica: {e}", "ERROR")
        return False


# ==============================================================================
# 🚀  MOTOR PRINCIPAL
# ==============================================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 5 Migration — Mass Migration to Golden Sample (CSL v1.0)"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as mudanças no disco. Sem isso, roda em DRY-RUN.",
    )
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY_RUN"
    log  = setup_logger(mode)

    log(f"=== INICIANDO MIGRAÇÃO FASE 5 ({mode}) ===", "INFO")
    log(f"Diretório Base  : {BASE_DIR}", "INFO")
    log(f"Diretório CSL   : {CSL_DIR}", "INFO")

    if not CSL_DIR.exists():
        log("Diretório CSL não encontrado. Abortando.", "ERROR")
        sys.exit(1)

    # Filtro PDPN: ignora meta/, relatorio_csl.txt, etc. (V5.1)
    _PDPN_RE = re.compile(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$')
    pdpn_dirs = sorted([d for d in CSL_DIR.iterdir()
                        if d.is_dir() and _PDPN_RE.match(d.name)])
    log(f"Posts encontrados: {len(pdpn_dirs)}", "INFO")

    success_count = 0
    error_count   = 0

    for pdpn_dir in pdpn_dirs:
        result = process_post(pdpn_dir, args.apply, log)
        if result:
            success_count += 1
        else:
            error_count += 1

    log("=" * 50, "INFO")
    log(f"MIGRAÇÃO CONCLUÍDA ({mode})", "INFO")
    log(f"  Sucesso : {success_count}", "INFO")
    log(f"  Erros   : {error_count}", "INFO")
    log("=" * 50, "INFO")

    if not args.apply:
        log("DRY-RUN: nenhum arquivo foi alterado.", "INFO")
        log("Para aplicar: python3 phase5_migration.py --apply", "INFO")

    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
