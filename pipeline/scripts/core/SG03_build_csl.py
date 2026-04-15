#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SCRIPT SG03
=====================================
Nome:       Construção da CSL (Canonical Source Library)
Versão:     1.2  —  AXIS-NIDDHI Edition
Autor:      Lead SRE + Claude Sonnet 4.6
Data:       2026-03-09

DELTA vs V1.1 (FF-014):
  ★ Guard de idempotência migrado de existência de arquivo → checksum SHA-256
  ★ Checksums em: 09-csl/PDPN/source/checksums/en-US.sha256
  ★ Formato padrão Linux: "<hash>  content.html"
  ★ Hash calculado sobre 02-preprocessed/content.html (fonte, não destino)
  ★ Lógica: se checksum não existe → cria; se igual → skip; se diferente → overwrite
  ★ --force continua funcionando (bypassa checksum)
  ★ Retrocompatível: posts sem checksum são tratados como "sem checksum = criar"

POSIÇÃO NA SEQUÊNCIA:
  Step 6 — Roda APÓS SP02 (pré-processamento).
  Lê 02-preprocessed/en-US/ → estrutura 09-csl/[PD#PN]/

ESTRUTURA GERADA POR POST:
  09-csl/
  └── PD.AA.000/
      ├── source/
      │   ├── en-US/
      │   │   └── content.html       ← copiado de 02-preprocessed
      │   └── checksums/
      │       └── en-US.sha256       ← hash do content.html de origem ← NOVO FF-014
      └── meta/
          └── identity.json          ← schema v1.0 mínimo

FLAGS:
    --apply       executa de verdade (padrão: dry-run)
    --force       sobrescreve mesmo posts já existentes (bypassa checksum)
    --verbose     mostra SKIPPEDs no terminal
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, LOG_DIR, DIR_02_PREPROCESSED, DIR_09_CSL, SOURCE_LANG, SCHEMA_VERSION

INPUT_DIR = DIR_02_PREPROCESSED / SOURCE_LANG   # /beng-fut/pipeline/02-preprocessed/en-US
CSL_ROOT  = DIR_09_CSL                           # /beng-fut/pipeline/09-csl

# ==============================================================================
# 🎨  CORES
# ==============================================================================
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

# ==============================================================================
# 📋  CONTADORES
# ==============================================================================
class Stats:
    def __init__(self):
        self.total     = 0
        self.skipped   = 0   # hash idêntico — não tocado
        self.created   = 0   # novo post criado
        self.updated   = 0   # hash diferente — conteúdo atualizado  ← NOVO FF-014
        self.forced    = 0   # existia mas --force aplicado
        self.invalid   = 0   # nome de arquivo fora do padrão canônico
        self.errors    = 0   # exceção real

# ==============================================================================
# 🛠️  LOGGER
# ==============================================================================
def setup_logger(apply: bool, force: bool):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode_tag = "APPLY" if apply else "DRY_RUN"
    if force: mode_tag += "_FORCE"
    log_path = LOG_DIR / f"SG03_build_csl_{mode_tag}_{ts}.log"
    lines    = []

    def log(msg: str, level: str = "INFO", color: str = RESET, verbose_only: bool = False):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌",
                 "SKIP": "⏭️ ", "DRY": "🔍", "UPDATED": "🔄", "SUMMARY": "📊"}
        icon = icons.get(level, "  ")
        ts_  = datetime.now(timezone.utc).strftime("%H:%M:%S")
        line = f"[{ts_}] [{level}] {msg}"
        lines.append(line)
        if not verbose_only or VERBOSE:
            print(f"{color}{icon}  {msg}{RESET}")

    def flush():
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n{GRAY}    Log salvo em: {log_path}{RESET}")

    return log, flush, log_path

# ==============================================================================
# 🔐  CHECKSUM HELPERS  ← FF-014
# ==============================================================================
def compute_sha256(file_path: Path) -> str:
    """Calcula SHA-256 de um arquivo. Retorna hex string de 64 chars."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def read_checksum(checksum_path: Path) -> str | None:
    """
    Lê o hash de um arquivo .sha256 no formato Linux: "<hash>  <filename>"
    Retorna o hash (64 chars) ou None se o arquivo não existir/for inválido.
    """
    if not checksum_path.exists():
        return None
    try:
        line = checksum_path.read_text(encoding="utf-8").strip()
        parts = line.split()
        if parts and len(parts[0]) == 64:
            return parts[0]
    except Exception:
        pass
    return None

def write_checksum(checksum_path: Path, file_hash: str, filename: str = "content.html") -> None:
    """
    Escreve o checksum no formato padrão Linux: "<hash>  <filename>"
    Cria o diretório pai se necessário.
    """
    checksum_path.parent.mkdir(parents=True, exist_ok=True)
    checksum_path.write_text(f"{file_hash}  {filename}\n", encoding="utf-8")

# ==============================================================================
# 🔍  PARSER DE NOME DE ARQUIVO CANÔNICO
# ==============================================================================
def parse_filename(filename: str) -> dict | None:
    """
    Extrai metadados do nome canônico: [Fin-dex]__[PD#PN]__[slug].html
    Ex: 0001__PD.AA.000__welcome.html
    Retorna None se o formato for inválido.
    """
    try:
        name = filename.removesuffix(".html")
        parts = name.split("__")
        if len(parts) < 3:
            return None
        return {
            "findex":            parts[0],
            "pdpn":              parts[1],
            "slug":              parts[2],
            "original_filename": filename,
        }
    except Exception:
        return None

# ==============================================================================
# 🏗️  CONSTRUÇÃO DE UMA ENTRADA CSL
# ==============================================================================
def build_csl_entry(meta: dict, apply: bool, force: bool, log, stats: Stats) -> str:
    """
    Cria (ou valida) a estrutura de uma entrada CSL.

    Guard FF-014 (checksum):
      - Sem checksum salvo         → CREATED  (nova entrada)
      - Hash igual ao salvo        → SKIPPED  (sem mudança)
      - Hash diferente do salvo    → UPDATED  (conteúdo mudou em 02-preprocessed)
      - --force                    → FORCED   (bypassa tudo)

    Retorna: CREATED | SKIPPED | UPDATED | FORCED |
             DRY_CREATED | DRY_SKIP | DRY_WOULD_UPDATE | DRY_WOULD_FORCE | ERROR:...
    """
    pdpn = meta["pdpn"]

    src_file        = INPUT_DIR / meta["original_filename"]
    dst_content     = CSL_ROOT / pdpn / "source" / "en-US" / "content.html"
    dst_identity    = CSL_ROOT / pdpn / "meta" / "identity.json"
    checksum_path   = CSL_ROOT / pdpn / "source" / "checksums" / "en-US.sha256"

    # ── Calcular hash da FONTE (02-preprocessed) ──────────────────────────
    try:
        src_hash = compute_sha256(src_file)
    except Exception as e:
        stats.errors += 1
        return f"ERROR:sha256:{e}"

    saved_hash = read_checksum(checksum_path)

    # ── Guard FF-014 ───────────────────────────────────────────────────────
    if not force:
        if saved_hash is not None:
            if saved_hash == src_hash:
                # Hash idêntico: conteúdo não mudou → skip
                stats.skipped += 1
                return "SKIPPED"
            else:
                # Hash diferente: conteúdo mudou em 02-preprocessed → update
                if not apply:
                    return "DRY_WOULD_UPDATE"
                # continua para ESCRITA com flag update=True
                is_update = True
        else:
            # Sem checksum salvo: entrada nova ou migração de V1.1
            if not apply:
                if dst_content.exists() and dst_identity.exists():
                    return "DRY_CREATED"   # já existe mas sem checksum (migração)
                return "DRY_CREATED"
            is_update = False
    else:
        # --force: bypassa checksum
        if not apply:
            return "DRY_WOULD_FORCE"
        is_update = dst_content.exists()

    # ── ESCRITA REAL ──────────────────────────────────────────────────────
    try:
        # 1. Garantir estrutura de pastas
        dst_content.parent.mkdir(parents=True, exist_ok=True)
        dst_identity.parent.mkdir(parents=True, exist_ok=True)

        # 2. Copiar content.html (preserva timestamps)
        shutil.copy2(src_file, dst_content)

        # 3. Salvar checksum da fonte  ← FF-014
        write_checksum(checksum_path, src_hash)

        # 4. Criar/atualizar identity.json (schema mínimo v1.0)
        #    Preserva campos extras de versões anteriores (S09, títulos, CLS, etc.)
        existing_identity = {}
        if dst_identity.exists():
            try:
                existing_identity = json.loads(dst_identity.read_text(encoding="utf-8"))
            except Exception:
                existing_identity = {}

        identity = {
            **existing_identity,
            "pdpn":               pdpn,
            "findex":             meta["findex"],
            "slug_en":            meta["slug"],
            "canonical_filename": meta["original_filename"],
            "schema_version":     "1.0",
            "last_s03_build":     datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        dst_identity.write_text(
            json.dumps(identity, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        if force and is_update:
            stats.forced += 1
            return "FORCED"
        elif is_update:
            stats.updated += 1
            return "UPDATED"
        else:
            stats.created += 1
            return "CREATED"

    except Exception as e:
        stats.errors += 1
        return f"ERROR:{e}"

# ==============================================================================
# 🚀  MOTOR PRINCIPAL
# ==============================================================================
def run(apply: bool, force: bool, verbose: bool):
    global VERBOSE
    VERBOSE = verbose

    log, flush, log_path = setup_logger(apply, force)
    stats = Stats()

    mode_label  = f"{GREEN}APPLY{RESET}"   if apply else f"{YELLOW}DRY-RUN{RESET}"
    force_label = f"  {RED}+FORCE{RESET}" if force else ""

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 BRASILEIRINHO ENGINE — SG03 Build CSL v1.2{RESET}")
    print(f"{CYAN}  Modo   : {mode_label}{force_label}")
    print(f"{CYAN}  Entrada: {INPUT_DIR}{RESET}")
    print(f"{CYAN}  Saída  : {CSL_ROOT}{RESET}")
    print(f"{CYAN}  Guard  : checksum SHA-256 (FF-014){RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    if not INPUT_DIR.exists():
        log(f"INPUT_DIR não encontrado: {INPUT_DIR}", "ERROR", RED)
        log("Execute SP02 antes deste script.", "ERROR", RED)
        sys.exit(1)

    CSL_ROOT.mkdir(parents=True, exist_ok=True)

    files = sorted(INPUT_DIR.glob("*.html"))
    if not files:
        log("Nenhum arquivo .html em INPUT_DIR.", "ERROR", RED)
        sys.exit(1)

    log(f"Arquivos na entrada: {len(files)}", "INFO", CYAN)
    print()

    for in_file in files:
        stats.total += 1
        meta = parse_filename(in_file.name)

        if not meta:
            log(f"Nome inválido (ignorado): {in_file.name}", "WARN", YELLOW)
            stats.invalid += 1
            continue

        result = build_csl_entry(meta, apply, force, log, stats)
        pdpn   = meta["pdpn"]

        if result == "CREATED":
            log(f"{pdpn}  [CREATED]", "OK", GREEN)
        elif result == "UPDATED":
            log(f"{pdpn}  [UPDATED] conteúdo mudou em 02-preprocessed", "UPDATED", CYAN)
        elif result == "FORCED":
            log(f"{pdpn}  [FORCED] sobrescrito por --force", "WARN", YELLOW)
        elif result == "SKIPPED":
            log(f"{pdpn}  [SKIPPED] hash idêntico", "SKIP", GRAY, verbose_only=True)
        elif result == "DRY_CREATED":
            log(f"{pdpn}  [DRY] seria criado", "DRY", CYAN, verbose_only=True)
        elif result == "DRY_WOULD_UPDATE":
            log(f"{pdpn}  [DRY] hash diferente — seria atualizado", "DRY", YELLOW)
        elif result == "DRY_WOULD_FORCE":
            log(f"{pdpn}  [DRY] já existe — seria forçado", "DRY", YELLOW, verbose_only=True)
        elif result.startswith("ERROR"):
            log(f"{pdpn}  {result}", "ERROR", RED)

    # ── SUMMARY ──────────────────────────────────────────────
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  📊  SUMMARY — {'DRY-RUN' if not apply else 'APPLY'}"
          f"{'  +FORCE' if force else ''}{RESET}")
    print(f"{CYAN}{'='*62}{RESET}")
    print(f"  Total analisados        : {stats.total}")
    print(f"  {GREEN}Criados                 : {stats.created}{RESET}")
    print(f"  {CYAN}Atualizados (FF-014)    : {stats.updated}{RESET}")
    print(f"  {YELLOW}Forçados (--force)      : {stats.forced}{RESET}")
    print(f"  {GRAY}Skipped (hash idêntico) : {stats.skipped}{RESET}")
    print(f"  {YELLOW}Nomes inválidos         : {stats.invalid}{RESET}")
    print(f"  {RED}Erros                   : {stats.errors}{RESET}")
    print(f"{CYAN}{'='*62}{RESET}")

    if not apply:
        print(f"\n  {YELLOW}⚠️  Modo DRY-RUN — nada foi alterado.{RESET}")
        print(f"  Para aplicar: {CYAN}python3 SG03_build_csl.py --apply{RESET}\n")
    elif stats.skipped == stats.total - stats.invalid:
        print(f"\n  {GREEN}✅  CSL já completa — hashes idênticos.{RESET}\n")
    else:
        print(f"\n  {GREEN}✅  CSL construída/atualizada (FF-014 ativo).{RESET}\n")

    flush()

    if stats.errors > 0:
        sys.exit(1)
    if not apply:
        sys.exit(2)
    sys.exit(0)

# ==============================================================================
# 🎯  ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="💎 SG03 — Construção da CSL com guard checksum (FF-014)"
    )
    parser.add_argument("--apply",   action="store_true", default=False,
                        help="Aplica a construção. Sem esta flag: dry-run.")
    parser.add_argument("--force",   action="store_true", default=False,
                        help="Sobrescreve posts. Bypassa checksum. Requer --apply.")
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Mostra SKIPPEDs no terminal.")
    args = parser.parse_args()

    if args.force and not args.apply:
        print(f"{RED}❌  --force requer --apply. Abortando.{RESET}")
        sys.exit(1)

    run(apply=args.apply, force=args.force, verbose=args.verbose)
