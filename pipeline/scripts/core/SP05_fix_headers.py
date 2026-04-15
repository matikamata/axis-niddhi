#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SP05_fix_headers.py
===============================================
Versão:  V5.1 — AXIS-NIDDHI Hardening Edition
Data:    2026-03-07

HARDENING V5.1 (vs V1.0 / S07_fix_headers_identity.py):
  ★ [RC-03]  Escrita via atomic_write_bytes() — crash-safe
  ★ [DCV-03] Regex: count=1 — remove APENAS o primeiro comentário (header)
             Versão anterior removia TODOS os <!-- --> do documento
  ★ [SF-03]  Logging de exceções em extract_* — não swallows silenciosamente
  ★ Paths via config.py (era BASE_DIR = Path("/beng/pipeline") hardcoded)
  ★ FailureCounter com abort automático

SEQUÊNCIA: SP05 → roda após SP04 (phase5_migration)
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DIR_09_CSL, LOG_DIR, FAILURE_THRESHOLD
from pipeline_utils import (
    atomic_write_bytes,
    atomic_write_json,
    backup_file,
    FailureCounter,
    get_utc_now,
    log_timestamp,
    sha256_file,
)

CSL_DIR = DIR_09_CSL

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
RESET  = "\033[0m"


# ==============================================================================
# 🛠️  LOGGER
# ==============================================================================

def setup_logger(mode: str):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = log_timestamp()
    log_path = LOG_DIR / f"SP05_fix_headers_{mode}_{ts}.log"
    lines = []

    def log(msg: str, level: str = "INFO"):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌", "SKIP": "⏭️ "}
        icon = icons.get(level, "  ")
        lines.append(f"[{get_utc_now()}] [{level}] {msg}")
        print(f"{icon} {msg}")

    def flush():
        log_path.write_text("\n".join(lines), encoding="utf-8")

    return log, flush


# ==============================================================================
# 🔧  GERAÇÃO DE HEADER CANÔNICO
# ==============================================================================

def generate_derived_header(pdpn: str, extraction_date: str, now: str) -> str:
    return (
        f"<!--\n"
        f"💎 BRASILEIRINHO ENGINE - DERIVED TRANSLATION ARTIFACT\n"
        f"======================================================\n"
        f"PD#PN:        {pdpn}\n"
        f"Language:     pt-BR\n"
        f"Generated-At: {now}\n"
        f"Source-Ref:   {extraction_date}\n"
        f"Engine:       DeepL API (Glossary v5)\n"
        f"======================================================\n"
        f"DO NOT EDIT WITHOUT REVIEW LOG. THIS IS A DERIVATIVE WORK.\n"
        f"-->"
    )


# ==============================================================================
# 🔧  FIXAR UM POST
# ==============================================================================

def fix_post(folder: Path, apply: bool, log, stats: dict) -> str:
    """
    Corrige header PT-BR incorreto em um post.
    Retorna: FIXED | SKIPPED | DRY_FIXED | ERROR:<reason>
    """
    pdpn      = folder.name
    pt_file   = folder / "source" / "pt-BR" / "content.html"
    json_file = folder / "meta"   / "identity.json"

    if not pt_file.exists() or not json_file.exists():
        return "SKIPPED"

    try:
        identity = json.loads(json_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return f"ERROR:identity.json corrompido: {e}"

    try:
        content = pt_file.read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR:read failed: {e}"

    # Verificar se precisa de correção
    needs_fix = "THIS IS THE TREASURE" in content or "Language:     en-US" in content
    if not needs_fix:
        return "SKIPPED"

    # Capturar timestamp UMA VEZ (ND-02)
    now = get_utc_now()
    extraction_date = (identity.get("sro") or {}).get("extraction_date", "UNKNOWN")

    # ── DCV-03: remover APENAS o primeiro comentário HTML ─────────────────
    # count=1 garante que comentários no corpo (YouTube, etc.) são preservados
    body = re.sub(r"^<!--.*?-->\s*", "", content, count=1, flags=re.DOTALL).strip()

    new_header  = generate_derived_header(pdpn, extraction_date, now)
    new_content = f"{new_header}\n\n{body}"

    # Contar comentários removidos para auditoria
    original_comments = len(re.findall(r"<!--.*?-->", content, re.DOTALL))
    new_comments = len(re.findall(r"<!--.*?-->", new_content, re.DOTALL))
    if original_comments - new_comments > 1:
        log(f"   {pdpn}: WARN — {original_comments - new_comments} comentários removidos (esperado: 1)", "WARN")

    if not apply:
        return "DRY_FIXED"

    # ── Backup antes de escrever (RC-03) ──────────────────────────────────
    backup_file(json_file)
    backup_file(pt_file)

    # ── Escrita atômica do HTML (RC-03) ───────────────────────────────────
    atomic_write_bytes(pt_file, new_content)

    # ── Recalcular hash do arquivo escrito (fonte de verdade = disco) ─────
    new_hash = sha256_file(pt_file)

    # ── Atualizar identity.json ────────────────────────────────────────────
    pt_artifact = identity.setdefault("artifacts", {}).setdefault("pt-BR", {})
    pt_artifact["status"]           = "derived"
    pt_artifact["integrity_sha256"] = new_hash
    pt_artifact["fixed_at"]         = now
    pt_artifact.pop("last_audit", None)

    atomic_write_json(json_file, identity)

    stats["fixed"] += 1
    return "FIXED"


# ==============================================================================
# 🚀  MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Fix PT-BR headers — SP05 V5.1")
    parser.add_argument("--apply", action="store_true", help="Aplica mudanças. Sem isso: DRY-RUN.")
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY_RUN"
    log, flush = setup_logger(mode)
    fc = FailureCounter(max_failures=FAILURE_THRESHOLD, label="SP05")
    stats = {"fixed": 0, "skipped": 0, "dry": 0}

    log(f"=== SP05 Fix Headers ({mode}) ===")
    log(f"CSL: {CSL_DIR}")

    if not CSL_DIR.exists():
        raise SystemExit(f"❌ CSL não encontrada: {CSL_DIR}")

    folders = sorted([f for f in CSL_DIR.iterdir() if f.is_dir()])
    log(f"Posts encontrados: {len(folders)}")

    for folder in folders:
        pdpn = folder.name
        result = fix_post(folder, args.apply, log, stats)

        if result == "FIXED":
            log(f"  ✅ {pdpn}: header corrigido.", "OK")
        elif result == "DRY_FIXED":
            stats["dry"] += 1
            log(f"  🔍 {pdpn}: seria corrigido (DRY-RUN).", "INFO")
        elif result == "SKIPPED":
            stats["skipped"] += 1
        elif result.startswith("ERROR"):
            if fc.fail(pdpn, result):
                flush()
                fc.assert_clean()
                return

    print(f"\n{'='*50}")
    print(f"SP05 CONCLUÍDO ({mode})")
    print(f"  Corrigidos : {stats['fixed']}")
    print(f"  Dry-Run    : {stats['dry']}")
    print(f"  Pulados    : {stats['skipped']}")
    print(f"  Falhas     : {fc.count}")
    print(f"{'='*50}\n")

    flush()
    fc.assert_clean()


if __name__ == "__main__":
    main()
