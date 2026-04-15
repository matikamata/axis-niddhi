#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — SP00_freeze_translations.py
=============================================
Nome:       Freezer de Traduções PT-BR (CSL → 03-translations/)
Versão:     1.0 — Translation Preservation Layer
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)
Data:       2026-03-12

POSIÇÃO NA SEQUÊNCIA:
  Utilitário de preservação — roda UMA VEZ para capturar traduções existentes.
  Deve ser re-executado após cada sessão de tradução manual ou DeepL.
  NÃO faz parte do run_full_pipeline.sh (é um freeze point, não um step).

O QUE FAZ:
  Para cada pasta em 09-csl/{PDPN}/, verifica:
    1. Existência de source/pt-BR/content.html  ← a tradução a preservar
    2. Existência de meta/identity.json         ← para extrair slug_root
  Se válido → copia pt-BR.html + gera translation.json em 03-translations/{PDPN}/
  Ao final → gera 03-translations/manifest.json com hash global.

RESULTADOS POSSÍVEIS POR POST:
  FROZEN                  → copiado com sucesso para 03-translations/
  UPDATED                 → já existia, conteúdo diferente → atualizado
  SKIPPED_NO_PTBR         → sem source/pt-BR/content.html no CSL (não traduzido)
  SKIPPED_IDENTICAL       → já existe em 03-translations/ e hash idêntico
  SKIPPED_NO_IDENTITY     → identity.json ausente (estrutura inválida)
  ERROR                   → exceção inesperada

USAGE:
  # Dry-run (padrão seguro — mostra o que faria sem escrever):
  python3 scripts/SP00_freeze_translations.py

  # Aplicar:
  python3 scripts/SP00_freeze_translations.py --apply

  # Verbose (mostra cada SKIPPED também):
  python3 scripts/SP00_freeze_translations.py --apply --verbose

  # Forçar re-freeze mesmo se hash idêntico:
  python3 scripts/SP00_freeze_translations.py --apply --force
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
        self.frozen   = 0
        self.updated  = 0
        self.skipped_no_ptbr    = 0
        self.skipped_identical  = 0
        self.skipped_no_identity = 0
        self.errors   = 0
        self.total    = 0

    @property
    def total_skipped(self):
        return self.skipped_no_ptbr + self.skipped_identical + self.skipped_no_identity


# ==============================================================================
# 🛠️  LOGGER
# ==============================================================================
def setup_logger(apply: bool):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode_tag = "APPLY" if apply else "DRY_RUN"
    log_path = LOG_DIR / f"SP00_freeze_translations_{mode_tag}_{ts}.log"

    lines = []

    def log(msg: str, level: str = "INFO", color: str = RESET,
            verbose_only: bool = False):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ",
                 "ERROR": "❌", "SKIP": "⏭️ ", "DRY": "🔍", "SUMMARY": "📊"}
        icon = icons.get(level, "  ")
        if verbose_only and not VERBOSE:
            lines.append(f"[{level}] {msg}")
            return
        print(f"{color}{icon} {msg}{RESET}")
        lines.append(f"[{level}] {msg}")

    def flush():
        log_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"{GRAY}📄 Log: {log_path}{RESET}")

    return log, flush


# ==============================================================================
# 🔐  HASH
# ==============================================================================
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ==============================================================================
# 📖  LER IDENTITY.JSON — extrai slug_root com fallback schema v3.1 / legacy
# ==============================================================================
def read_identity(identity_path: Path) -> dict | None:
    try:
        data = json.loads(identity_path.read_text(encoding="utf-8"))
        identity_block = data.get("identity", {})

        pdpn      = identity_block.get("pdpn")      or data.get("pdpn")
        slug_root = identity_block.get("slug_root")  or data.get("slug_en") or data.get("slug")
        findex    = identity_block.get("findex")     or data.get("findex", "0000")

        if not pdpn:
            return None

        return {
            "pdpn":      pdpn,
            "slug_root": slug_root or "unknown",
            "findex":    findex,
        }
    except Exception:
        return None


# ==============================================================================
# ❄️  PROCESSAR UM POST
# ==============================================================================
def freeze_post(pdpn_dir: Path, apply: bool, force: bool, log, stats: Stats) -> str:
    pdpn = pdpn_dir.name
    stats.total += 1

    # 1. Verificar identity.json
    identity_path = pdpn_dir / "meta" / "identity.json"
    if not identity_path.exists():
        stats.skipped_no_identity += 1
        log(f"  {pdpn} — identity.json ausente", "SKIP", GRAY, verbose_only=True)
        return "SKIPPED_NO_IDENTITY"

    identity = read_identity(identity_path)
    if not identity:
        stats.skipped_no_identity += 1
        log(f"  {pdpn} — identity.json inválido", "WARN", YELLOW)
        return "SKIPPED_NO_IDENTITY"

    # 2. Verificar pt-BR
    ptbr_src = pdpn_dir / "source" / "pt-BR" / "content.html"
    if not ptbr_src.exists():
        stats.skipped_no_ptbr += 1
        log(f"  {pdpn} — sem pt-BR (não traduzido ainda)", "SKIP", GRAY, verbose_only=True)
        return "SKIPPED_NO_PTBR"

    # 3. Calcular hash da fonte
    src_hash = sha256_file(ptbr_src)

    # 4. Destino em 03-translations/
    dst_dir       = DIR_03_TRANSLATIONS / pdpn
    dst_html      = dst_dir / "pt-BR.html"
    dst_meta      = dst_dir / "translation.json"

    # 5. Idempotência — verificar se hash idêntico
    if dst_html.exists() and not force:
        existing_hash = sha256_file(dst_html)
        if existing_hash == src_hash:
            stats.skipped_identical += 1
            log(f"  {pdpn} — idêntico, sem alteração", "SKIP", GRAY, verbose_only=True)
            return "SKIPPED_IDENTICAL"
        else:
            # Hash diferente → vai atualizar
            action = "UPDATED"
    else:
        action = "FROZEN"

    # 6. Dry-run
    if not apply:
        label = f"DRY_{action}"
        log(f"  {pdpn} [{label}] {identity['slug_root']}", "DRY", CYAN)
        if action == "FROZEN":
            stats.frozen += 1
        else:
            stats.updated += 1
        return label

    # 7. Escrever
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)

        # Copiar HTML
        shutil.copy2(ptbr_src, dst_html)

        # Gerar translation.json
        translation_meta = {
            "schema_version": "1.0",
            "pdpn":           pdpn,
            "slug_root":      identity["slug_root"],
            "findex":         identity["findex"],
            "lang":           "pt-BR",
            "source_sha256":  src_hash,
            "frozen_at":      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status":         "frozen",
        }
        dst_meta.write_text(
            json.dumps(translation_meta, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        color = GREEN if action == "FROZEN" else YELLOW
        log(f"  {pdpn} [{action}] {identity['slug_root']}", "OK", color)

        if action == "FROZEN":
            stats.frozen += 1
        else:
            stats.updated += 1

        return action

    except Exception as e:
        stats.errors += 1
        log(f"  {pdpn} — ERRO: {e}", "ERROR", RED)
        return "ERROR"


# ==============================================================================
# 📋  GERAR MANIFEST GLOBAL
# ==============================================================================
def write_manifest(stats: Stats, apply: bool):
    if not apply:
        return

    # Coletar todos os translation.json para hash global determinístico
    global_hasher = hashlib.sha256()
    entries = []

    for pdpn_dir in sorted(DIR_03_TRANSLATIONS.iterdir()):
        if not pdpn_dir.is_dir():
            continue
        meta_path = pdpn_dir / "translation.json"
        html_path = pdpn_dir / "pt-BR.html"
        if meta_path.exists() and html_path.exists():
            file_hash = sha256_file(html_path)
            global_hasher.update(f"{pdpn_dir.name}:{file_hash}".encode())
            entries.append(pdpn_dir.name)

    manifest = {
        "schema_version":    "1.0",
        "layer":             "03-translations",
        "generated_at":      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_frozen":      len(entries),
        "global_hash":       global_hasher.hexdigest(),
        "pdpn_list":         entries,
    }

    manifest_path = DIR_03_TRANSLATIONS / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\n{GREEN}📋 manifest.json gerado:{RESET}")
    print(f"   {GRAY}Total frozen : {len(entries)}{RESET}")
    print(f"   {GRAY}Global hash  : {manifest['global_hash'][:16]}...{RESET}")
    print(f"   {GRAY}Salvo em     : {manifest_path}{RESET}")


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main():
    global VERBOSE

    parser = argparse.ArgumentParser(
        description="SP00 — Freeze PT-BR translations from CSL → 03-translations/"
    )
    parser.add_argument("--apply",   action="store_true", help="Escrever no disco (padrão: dry-run)")
    parser.add_argument("--force",   action="store_true", help="Re-freeze mesmo se hash idêntico")
    parser.add_argument("--verbose", action="store_true", help="Mostrar todos os SKIPPED")
    args = parser.parse_args()

    VERBOSE = args.verbose
    apply   = args.apply
    force   = args.force

    log, flush = setup_logger(apply)

    # Header
    mode = f"{CYAN}APPLY{RESET}" if apply else f"{YELLOW}DRY-RUN{RESET}"
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — SP00 Freeze Translations{RESET}")
    print(f"  Modo   : {mode}")
    print(f"  Fonte  : {DIR_09_CSL}")
    print(f"  Destino: {DIR_03_TRANSLATIONS}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    if not DIR_09_CSL.exists():
        print(f"{RED}❌ CSL não encontrada: {DIR_09_CSL}{RESET}")
        print("   Execute SG03 primeiro.")
        sys.exit(1)

    if apply:
        DIR_03_TRANSLATIONS.mkdir(parents=True, exist_ok=True)

    # Iterar CSL
    stats   = Stats()
    folders = sorted([
        f for f in DIR_09_CSL.iterdir()
        if f.is_dir() and f.name != "meta"
    ])

    log(f"Pastas CSL encontradas: {len(folders)}")
    print()

    for folder in folders:
        freeze_post(folder, apply=apply, force=force, log=log, stats=stats)

    # Manifest
    write_manifest(stats, apply)

    # Summary
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  📊 RESUMO{RESET}")
    print(f"{'='*62}")
    print(f"  Total processado   : {stats.total}")
    print(f"  {GREEN}Frozen (novo)      : {stats.frozen}{RESET}")
    print(f"  {YELLOW}Updated (alterado) : {stats.updated}{RESET}")
    print(f"  Sem pt-BR          : {stats.skipped_no_ptbr}")
    print(f"  Idêntico (skip)    : {stats.skipped_identical}")
    print(f"  Sem identity       : {stats.skipped_no_identity}")
    print(f"  {RED}Erros              : {stats.errors}{RESET}")
    if not apply:
        print(f"\n  {YELLOW}⚠️  DRY-RUN — nada foi escrito.{RESET}")
        print(f"  Para aplicar: python3 scripts/SP00_freeze_translations.py --apply")
    print(f"{CYAN}{'='*62}{RESET}\n")

    flush()

    if stats.errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
