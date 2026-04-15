#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SCRIPT S00_migrate_ptbr
==================================================
Nome:       Migrador de Traduções PT-BR (HD Antigo → /beng/)
Versão:     1.1  — AXIS-NIDDHI Hardening Edition
Autor:      Aloka + Claude Sonnet 4.6
Data:       2026-02-28

POSIÇÃO NA SEQUÊNCIA:
  Step 2.5 — Roda APÓS reset v12.1, ANTES de S07a/S07b.
  Objetivo: aproveitar traduções DeepL já existentes em BrasileirinhoHD,
  evitando reprocessamento desnecessário e preservando cota.

O QUE FAZ:
  Para cada pasta em SRC_CSL (HD antigo), verifica:
    1. Existência de identity.json
    2. Existência de source/en-US/content.html
    3. Existência de source/pt-BR/content.html  ← o tesouro a migrar
    4. Consistência do slug no identity.json vs nome da pasta

  Se tudo válido E destino ainda não existe → copia.

RESULTADOS POSSÍVEIS POR POST:
  COPIED                  → copiado com sucesso
  SKIPPED_ALREADY_EXISTS  → pt-BR já existe em /beng/, não sobrescreve
  SKIPPED_INVALID_STRUCT  → falta identity.json, en-US ou pt-BR
  SKIPPED_SLUG_MISMATCH   → slug no JSON diverge do nome da pasta (suspeito)
  ERROR                   → exceção inesperada durante a cópia

HARDENING PASS — AXIS-NIDDHI (2026-03-05)
  ★ Removido: DST_CSL = Path("/beng/pipeline/09-csl")   ← hardcode absoluto
  ★ Removido: LOG_DIR = Path("/beng/pipeline/logs")      ← hardcode absoluto
  ★ Adicionado: import de DIR_09_CSL e LOG_DIR via config.py
  ★ SRC_CSL permanece configurável via argumento CLI (--src) — HD externo
  ★ Lógica inalterada.

USAGE:
  # Dry-run (padrão seguro):
  python3 S00_migrate_ptbr_v1.py

  # Aplicar de verdade:
  python3 S00_migrate_ptbr_v1.py --apply

  # Fonte alternativa (HD externo ou backup SD):
  python3 SP01_migrate_ptbr.py --apply --src /media/sanghop/GUARDIAN_SD/Backup_CAGAÇO_20260310_16h19/pipeline/09-csl

  # Detalhado (mostra cada SKIPPED também):
  python3 S00_migrate_ptbr_v1.py --apply --verbose
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent / "scripts"))

from config import DIR_09_CSL, DIR_03_PTBR, LOG_DIR

# Destino canônico do pipeline
DST_CSL = DIR_09_CSL   # /beng/pipeline/09-csl

# Origem: HD externo — configurável via --src (não faz parte do config.py porque
# é um dispositivo externo montável em caminhos variáveis).
# Fonte canônica local — alimentada uma vez via seed_ptbr.sh (do backup do SD card)
# Nunca mais depende de HD externo montado.
_DEFAULT_SRC = DIR_03_PTBR

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
VERBOSE = False


class Stats:
    def __init__(self):
        self.copied                 = 0
        self.skipped_exists         = 0
        self.skipped_invalid_struct = 0
        self.skipped_slug_mismatch  = 0
        self.errors                 = 0
        self.total                  = 0

    @property
    def total_skipped(self):
        return (self.skipped_exists +
                self.skipped_invalid_struct +
                self.skipped_slug_mismatch)


# ==============================================================================
# 🛠️  LOGGER
# ==============================================================================
def setup_logger(apply: bool) -> tuple:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode_tag = "APPLY" if apply else "DRY_RUN"
    log_path = LOG_DIR / f"migrate_ptbr_{mode_tag}_{ts}.log"

    lines = []

    def log(msg: str, level: str = "INFO", color: str = RESET,
            verbose_only: bool = False):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ",
                 "ERROR": "❌", "SKIP": "⏭️ ", "DRY": "🔍", "SUMMARY": "📊"}
        icon = icons.get(level, "  ")
        ts_  = datetime.now(timezone.utc).strftime("%H:%M:%S")
        lines.append(f"[{ts_}] [{level}] {msg}")
        if not verbose_only or VERBOSE:
            print(f"{color}{icon}  {msg}{RESET}")

    def flush(log_path=log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n{GRAY}    Log: {log_path}{RESET}")

    return log, flush, log_path


# ==============================================================================
# 🔍  VALIDAÇÃO DE PASTA FONTE
# ==============================================================================
def validate_src_folder(folder: Path, log, verbose: bool) -> tuple[bool, str]:
    """
    Validação adaptada para dois formatos de SRC:

    A) 03-ptbr/ (fonte canônica local) — estrutura mínima:
         PDPN/source/pt-BR/content.html

    B) HD externo (CSL completo) — estrutura completa:
         PDPN/meta/identity.json
         PDPN/source/en-US/content.html
         PDPN/source/pt-BR/content.html

    Em ambos os casos, o único requisito real é o pt-BR/content.html.
    identity.json e en-US são opcionais — o DST (09-csl) já os tem.
    """
    pt_html = folder / "source" / "pt-BR" / "content.html"

    if not pt_html.exists():
        return False, "SKIPPED_INVALID_STRUCT:no_pt-BR_content.html"

    # Se identity.json presente (HD externo), validar consistência de PDPN
    identity_p = folder / "meta" / "identity.json"
    if identity_p.exists():
        try:
            identity = json.loads(identity_p.read_text(encoding="utf-8"))
            pdpn_in_json = (
                identity.get("identity", {}).get("pdpn") or
                identity.get("pdpn") or
                ""
            ).strip()
            if pdpn_in_json and pdpn_in_json != folder.name:
                return False, f"SKIPPED_SLUG_MISMATCH:json_pdpn={pdpn_in_json}_folder={folder.name}"
        except json.JSONDecodeError as e:
            return False, f"SKIPPED_INVALID_STRUCT:identity_json_malformed({e})"

    return True, "OK"


# ==============================================================================
# 📦  CÓPIA DE UM POST
# ==============================================================================
def migrate_post(pdpn: str, src_pt: Path, dst_pt: Path,
                 apply: bool, log, stats: Stats) -> str:
    if dst_pt.exists():
        stats.skipped_exists += 1
        return "SKIPPED_ALREADY_EXISTS"

    if not apply:
        log(f"[DRY] {pdpn} → seria copiado", "DRY", CYAN)
        stats.copied += 1
        return "COPIED_DRY"

    try:
        dst_pt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_pt, dst_pt)
        stats.copied += 1
        return "COPIED"
    except Exception as e:
        stats.errors += 1
        return f"ERROR:{e}"


# ==============================================================================
# 🚀  MOTOR PRINCIPAL
# ==============================================================================
def run(src_csl: Path, apply: bool, verbose: bool) -> None:
    global VERBOSE
    VERBOSE = verbose

    log, flush, log_path = setup_logger(apply)
    stats = Stats()

    mode_label = f"{GREEN}APPLY{RESET}" if apply else f"{YELLOW}DRY-RUN{RESET}"
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 BRASILEIRINHO ENGINE — Migrador PT-BR  v1.1{RESET}")
    print(f"{CYAN}  Modo : {mode_label}")
    print(f"{CYAN}  SRC  : {src_csl}{RESET}")
    print(f"{CYAN}  DST  : {DST_CSL}{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    if not src_csl.exists():
        log(f"SRC não encontrada: {src_csl}", "ERROR", RED)
        log("Verifique se 03-ptbr/ existe em /beng-fut/pipeline/.", "ERROR", RED)
        log("Execute: bash scripts/seed_ptbr.sh --src <backup_path>", "ERROR", RED)
        sys.exit(1)

    if not DST_CSL.exists():
        log(f"DST não encontrada: {DST_CSL}", "ERROR", RED)
        log("Execute o reset v12.1 antes de rodar este script.", "ERROR", RED)
        sys.exit(1)

    folders = sorted([f for f in src_csl.iterdir() if f.is_dir() and f.name != 'meta'])
    log(f"Pastas encontradas na SRC: {len(folders)}", "INFO", CYAN)
    print()

    results = []

    for folder in folders:
        pdpn   = folder.name
        src_pt = folder / "source" / "pt-BR" / "content.html"
        dst_pt = DST_CSL / pdpn / "source" / "pt-BR" / "content.html"
        stats.total += 1

        valid, reason = validate_src_folder(folder, log, verbose)

        if not valid:
            kind   = reason.split(":")[0]
            detail = reason.split(":", 1)[1] if ":" in reason else ""

            if kind == "SKIPPED_INVALID_STRUCT":
                stats.skipped_invalid_struct += 1
                log(f"{pdpn}  [{kind}]  {detail}", "SKIP", GRAY, verbose_only=True)
                results.append(f"SKIPPED_INVALID_STRUCT | {pdpn} | {detail}")

            elif kind == "SKIPPED_SLUG_MISMATCH":
                stats.skipped_slug_mismatch += 1
                log(f"{pdpn}  [{kind}]  {detail}", "WARN", YELLOW)
                results.append(f"SKIPPED_SLUG_MISMATCH  | {pdpn} | {detail}")
            continue

        result = migrate_post(pdpn, src_pt, dst_pt, apply, log, stats)

        if result == "COPIED":
            log(f"{pdpn}  [COPIED]", "OK", GREEN)
            results.append(f"COPIED                 | {pdpn}")
        elif result == "COPIED_DRY":
            results.append(f"COPIED_DRY             | {pdpn}")
        elif result == "SKIPPED_ALREADY_EXISTS":
            log(f"{pdpn}  [SKIPPED_ALREADY_EXISTS]", "SKIP", GRAY, verbose_only=True)
            results.append(f"SKIPPED_ALREADY_EXISTS | {pdpn}")
        elif result.startswith("ERROR"):
            log(f"{pdpn}  {result}", "ERROR", RED)
            results.append(f"ERROR                  | {pdpn} | {result}")

    # ── SUMMARY ────────────────────────────────────────────────────────────
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  📊  SUMMARY — {'DRY-RUN' if not apply else 'APPLY'}{RESET}")
    print(f"{CYAN}{'='*62}{RESET}")
    print(f"  Total de pastas analisadas  : {stats.total}")
    print(f"  {GREEN}{'Seriam copiados' if not apply else 'Copiados':<28}: {stats.copied}{RESET}")
    print(f"  {GRAY}Já existiam (sem toque)     : {stats.skipped_exists}{RESET}")
    print(f"  {GRAY}Estrutura inválida (skip)   : {stats.skipped_invalid_struct}{RESET}")
    print(f"  {YELLOW}Slug/PD#PN mismatch (skip)  : {stats.skipped_slug_mismatch}{RESET}")
    print(f"  {RED}Erros                       : {stats.errors}{RESET}")
    print(f"{CYAN}{'='*62}{RESET}")

    if not apply:
        print(f"\n  {YELLOW}⚠️  Modo DRY-RUN — nada foi alterado.{RESET}")
        print(f"  Para aplicar: {CYAN}python3 S00_migrate_ptbr_v1.py --apply{RESET}\n")
    else:
        print(f"\n  {GREEN}✅  Migração concluída.{RESET}")
        print(f"  Próximo passo: {CYAN}python3 S07a_generate_menu_v6_schema_aware.py{RESET}\n")

    log("\n--- RESULTADOS DETALHADOS ---", "SUMMARY")
    for r in results:
        log(r, "SUMMARY")
    log(
        f"TOTAL={stats.total} COPIED={stats.copied} "
        f"EXISTS={stats.skipped_exists} "
        f"INVALID={stats.skipped_invalid_struct} "
        f"MISMATCH={stats.skipped_slug_mismatch} "
        f"ERRORS={stats.errors}",
        "SUMMARY",
    )
    flush()

    if stats.errors > 0:
        sys.exit(2)
    if stats.skipped_slug_mismatch > 0:
        sys.exit(1)
    sys.exit(0)


# ==============================================================================
# 🎯  ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="💎 Migrador PT-BR — BrasileirinhoHD → /beng/ (Step 2.5)"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Aplica a migração. Sem esta flag, roda em DRY-RUN (padrão seguro).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Mostra também os SKIPPED no terminal.",
    )
    parser.add_argument(
        "--src",
        type=Path,
        default=_DEFAULT_SRC,
        help=(
            "Caminho até a pasta 09-csl no HD externo. "
            f"Padrão: {_DEFAULT_SRC}"
        ),
    )
    args = parser.parse_args()
    run(src_csl=args.src, apply=args.apply, verbose=args.verbose)
