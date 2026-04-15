#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — SP01b_restore_translations.py
===============================================
Nome:       Restaurador de Traduções PT-BR (03-translations/ → CSL)
Versão:     1.0 — Translation Preservation Layer
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)
Data:       2026-03-12

POSIÇÃO NA SEQUÊNCIA:
  SP01 (migrate legacy) → [SP01b — este script] → SP02 (upgrade identity)

  Roda automaticamente em run_full_pipeline.sh após SP01.
  Garante que todas as traduções PT-BR preservadas em 03-translations/
  sejam restauradas no CSL antes que SP10 (DeepL) seja executado.

O QUE FAZ:
  Para cada pasta em 03-translations/{PDPN}/:
    1. Verifica existência de pt-BR.html e translation.json
    2. Verifica que o PDPN correspondente existe no CSL (09-csl/)
    3. Valida integridade SHA-256 do pt-BR.html contra translation.json
    4. Se CSL/{PDPN}/source/pt-BR/content.html ausente → copia (restaura)
    5. Se já existe → verifica hash — iguais: skip / diferentes: warn

RESULTADOS POSSÍVEIS POR POST:
  RESTORED              → copiado com sucesso para CSL
  SKIPPED_ALREADY_EXISTS → pt-BR já existe no CSL com hash idêntico
  SKIPPED_HASH_CONFLICT → pt-BR existe no CSL mas hash diferente (CSL é mais recente)
  SKIPPED_NO_CSL_ENTRY  → PDPN não existe no CSL (novo dump não tem este post)
  SKIPPED_CORRUPT       → hash do arquivo não bate com translation.json
  ERROR                 → exceção inesperada

INVARIANTES:
  • Nunca sobrescreve pt-BR existente no CSL (CSL tem prioridade se já traduzido)
  • Nunca modifica translation.json nem manifest.json
  • Idempotente: pode ser executado múltiplas vezes sem efeito colateral
  • SP10 é idempotente — vai pular posts que já têm pt-BR restaurado

USAGE:
  # Dry-run (padrão seguro):
  python3 scripts/SP01b_restore_translations.py

  # Aplicar:
  python3 scripts/SP01b_restore_translations.py --apply

  # Verbose (mostra todos os SKIPPED):
  python3 scripts/SP01b_restore_translations.py --apply --verbose

  # Forçar sobrescrita mesmo se pt-BR já existe no CSL:
  python3 scripts/SP01b_restore_translations.py --apply --force
  # ⚠️  USAR COM CAUTELA — sobrescreve traduções manuais no CSL
"""

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, DIR_09_CSL, LOG_DIR

DIR_03_TRANSLATIONS = BASE_DIR / "03-translations"

# ==============================================================================
# 🎨  CORES
# ==============================================================================
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

VERBOSE = False


# ==============================================================================
# 📋  CONTADORES
# ==============================================================================
class Stats:
    def __init__(self):
        self.restored              = 0
        self.skipped_exists        = 0
        self.skipped_hash_conflict = 0
        self.skipped_no_csl        = 0
        self.skipped_corrupt       = 0
        self.errors                = 0
        self.total                 = 0

    @property
    def total_skipped(self):
        return (self.skipped_exists + self.skipped_hash_conflict +
                self.skipped_no_csl + self.skipped_corrupt)


# ==============================================================================
# 🛠️  LOGGER
# ==============================================================================
def setup_logger(apply: bool):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode_tag = "APPLY" if apply else "DRY_RUN"
    log_path = LOG_DIR / f"SP01b_restore_translations_{mode_tag}_{ts}.log"

    lines = []

    def log(msg: str, level: str = "INFO", color: str = RESET,
            verbose_only: bool = False):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ",
                 "ERROR": "❌", "SKIP": "⏭️ ", "DRY": "🔍", "SUMMARY": "📊"}
        icon = icons.get(level, "  ")
        ts_ = datetime.now(timezone.utc).strftime("%H:%M:%S")
        lines.append(f"[{ts_}] [{level}] {msg}")
        if not verbose_only or VERBOSE:
            print(f"{color}{icon}  {msg}{RESET}")

    def flush():
        log_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\n{GRAY}    Log: {log_path}{RESET}")

    return log, flush


# ==============================================================================
# 🔐  HASH
# ==============================================================================
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ==============================================================================
# 🔄  RESTAURAR UM POST
# ==============================================================================
def restore_post(trans_dir: Path, apply: bool, force: bool,
                 log, stats: Stats) -> str:
    pdpn = trans_dir.name
    stats.total += 1

    # 1. Verificar arquivos na camada de tradução
    src_html = trans_dir / "pt-BR.html"
    src_meta = trans_dir / "translation.json"

    if not src_html.exists() or not src_meta.exists():
        stats.errors += 1
        log(f"  {pdpn} — 03-translations/ corrompido (falta html ou json)", "ERROR", RED)
        return "ERROR"

    # 2. Ler translation.json
    try:
        meta = json.loads(src_meta.read_text(encoding="utf-8"))
        expected_hash = meta.get("source_sha256")
        slug_root     = meta.get("slug_root", "unknown")
    except Exception as e:
        stats.errors += 1
        log(f"  {pdpn} — translation.json inválido: {e}", "ERROR", RED)
        return "ERROR"

    # 3. Verificar integridade do arquivo congelado
    actual_hash = sha256_file(src_html)
    if expected_hash and actual_hash != expected_hash:
        stats.skipped_corrupt += 1
        log(f"  {pdpn} — INTEGRIDADE FALHOU (arquivo corrompido desde freeze)", "WARN", RED)
        log(f"    esperado : {expected_hash[:16]}...", "WARN", RED, verbose_only=True)
        log(f"    atual    : {actual_hash[:16]}...", "WARN", RED, verbose_only=True)
        return "SKIPPED_CORRUPT"

    # 4. Verificar se PDPN existe no CSL
    csl_pdpn_dir = DIR_09_CSL / pdpn
    if not csl_pdpn_dir.exists():
        stats.skipped_no_csl += 1
        log(f"  {pdpn} — não existe no CSL (novo dump pode não ter este post)", "WARN", YELLOW,
            verbose_only=True)
        return "SKIPPED_NO_CSL_ENTRY"

    # 5. Verificar destino no CSL
    dst_pt = csl_pdpn_dir / "source" / "pt-BR" / "content.html"

    if dst_pt.exists() and not force:
        dst_hash = sha256_file(dst_pt)
        if dst_hash == actual_hash:
            # Idêntico — nada a fazer
            stats.skipped_exists += 1
            log(f"  {pdpn} — já existe, hash idêntico", "SKIP", GRAY, verbose_only=True)
            return "SKIPPED_ALREADY_EXISTS"
        else:
            # Hash diferente — CSL tem versão mais recente (manual edit?)
            stats.skipped_hash_conflict += 1
            log(f"  {pdpn} — CONFLITO: CSL tem versão diferente de 03-translations/", "WARN", YELLOW)
            log(f"    03-translations: {actual_hash[:16]}...", "WARN", YELLOW, verbose_only=True)
            log(f"    CSL atual      : {dst_hash[:16]}...", "WARN", YELLOW, verbose_only=True)
            log(f"    → CSL preservado (use --force para sobrescrever)", "WARN", YELLOW,
                verbose_only=True)
            return "SKIPPED_HASH_CONFLICT"

    # 6. Dry-run
    if not apply:
        log(f"  {pdpn} [DRY_RESTORE] {slug_root}", "DRY", CYAN)
        stats.restored += 1
        return "DRY_RESTORED"

    # 7. Restaurar
    try:
        dst_pt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_html, dst_pt)
        stats.restored += 1
        log(f"  {pdpn} [RESTORED] {slug_root}", "OK", GREEN)
        return "RESTORED"

    except Exception as e:
        stats.errors += 1
        log(f"  {pdpn} — ERRO ao copiar: {e}", "ERROR", RED)
        return "ERROR"


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main():
    global VERBOSE

    parser = argparse.ArgumentParser(
        description="SP01b — Restore PT-BR translations from 03-translations/ → CSL"
    )
    parser.add_argument("--apply",   action="store_true",
                        help="Escrever no disco (padrão: dry-run)")
    parser.add_argument("--force",   action="store_true",
                        help="Sobrescrever pt-BR no CSL mesmo se já existir ⚠️")
    parser.add_argument("--verbose", action="store_true",
                        help="Mostrar todos os SKIPPED")
    args = parser.parse_args()

    VERBOSE = args.verbose
    apply   = args.apply
    force   = args.force

    log, flush = setup_logger(apply)

    # Verificar manifest
    manifest_path = DIR_03_TRANSLATIONS / "manifest.json"
    manifest_hash = "N/A"
    manifest_total = 0
    if manifest_path.exists():
        try:
            m = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_hash  = m.get("global_hash", "N/A")[:24] + "..."
            manifest_total = m.get("total_frozen", 0)
        except Exception:
            pass

    # Header
    mode = f"{CYAN}APPLY{RESET}" if apply else f"{YELLOW}DRY-RUN{RESET}"
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — SP01b Restore Translations{RESET}")
    print(f"  Modo      : {mode}")
    print(f"  Fonte     : {DIR_03_TRANSLATIONS}")
    print(f"  Destino   : {DIR_09_CSL}")
    print(f"  Manifest  : {manifest_total} frozen · hash {manifest_hash}")
    if force:
        print(f"  {RED}⚠️  --force ATIVO: pt-BR existente no CSL será sobrescrito{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    # Verificações pré-voo
    if not DIR_03_TRANSLATIONS.exists():
        print(f"{YELLOW}ℹ️  03-translations/ não encontrada: {DIR_03_TRANSLATIONS}{RESET}")
        print(f"   {GRAY}Nenhuma tradução congelada identificada. Saltando restauração graciosamente.{RESET}\n")
        sys.exit(0)

    if not DIR_09_CSL.exists():
        print(f"{RED}❌ CSL não encontrada: {DIR_09_CSL}{RESET}")
        print("   Execute SG03 primeiro.")
        sys.exit(1)

    # Iterar 03-translations/
    stats   = Stats()
    folders = sorted([
        f for f in DIR_03_TRANSLATIONS.iterdir()
        if f.is_dir()
    ])

    log(f"Entradas em 03-translations/: {len(folders)}")
    print()

    for folder in folders:
        restore_post(folder, apply=apply, force=force, log=log, stats=stats)

    # Summary
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  📊 RESUMO{RESET}")
    print(f"{'='*62}")
    print(f"  Total processado        : {stats.total}")
    print(f"  {GREEN}Restored               : {stats.restored}{RESET}")
    print(f"  Já existe (idêntico)    : {stats.skipped_exists}")
    print(f"  {YELLOW}Conflito de hash        : {stats.skipped_hash_conflict}{RESET}")
    print(f"  PDPN ausente no CSL     : {stats.skipped_no_csl}")
    print(f"  {RED}Arquivo corrompido      : {stats.skipped_corrupt}{RESET}")
    print(f"  {RED}Erros                   : {stats.errors}{RESET}")

    if stats.skipped_hash_conflict > 0:
        print(f"\n  {YELLOW}⚠️  {stats.skipped_hash_conflict} conflitos detectados.{RESET}")
        print(f"  CSL preservado. Use --verbose para detalhes.")
        print(f"  Use --force para sobrescrever com versão congelada.")

    if not apply:
        print(f"\n  {YELLOW}⚠️  DRY-RUN — nada foi escrito.{RESET}")
        print(f"  Para aplicar: python3 scripts/SP01b_restore_translations.py --apply")

    print(f"{CYAN}{'='*62}{RESET}\n")

    flush()

    if stats.errors > 0 or stats.skipped_corrupt > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
