#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SP02_upgrade_identity.py
====================================================
Versão:  V5.1 — AXIS-NIDDHI Hardening Edition (SEAL Script)
Data:    2026-03-07

HARDENING V5.1 (vs V1.2):
  ★ [SEAL]  Cobertura expandida: content.html + semantic.json + (optional) assets
  ★ [RC-03] atomic_write_json() — crash-safe
  ★ [SF-03] logging de exceções em extract_*() — não swallows
  ★ [ND-01] log_timestamp() com sub-segundo
  ★ [ND-02] get_utc_now() capturado UMA VEZ por post
  ★ [DCV-02] sha256_file() lê em bytes (rb) — encoding byte-stable
  ★ FailureCounter: abort se erros > FAILURE_THRESHOLD
  ★ SEAL REPORT: imprime resumo de integridade ao final
  ★ Exit code semântico: 0=clean, 1=erros, 2=dry-run

FUNÇÃO NO PIPELINE:
  SEAL 1: roda após SG — lock hashes EN pré-tradução
  SEAL 2: roda após SP10 — lock hashes PT pós-tradução
  Ambos usam: --apply --force
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import (
    DIR_09_CSL,
    LOG_DIR,
    SCHEMA_VERSION,
    SCHEMA_VERSION_SEAL,
    FAILURE_THRESHOLD,
)
from pipeline_utils import (
    atomic_write_json,
    backup_file,
    FailureCounter,
    get_utc_now,
    log_timestamp,
    sha256_file,
    PipelineAbort,
)

CSL_ROOT = DIR_09_CSL

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RESET  = "\033[0m"


# ==============================================================================
# 📋  CONTADORES
# ==============================================================================

@dataclass
class Stats:
    total:    int = 0
    upgraded: int = 0
    skipped:  int = 0
    forced:   int = 0
    errors:   int = 0
    seal_gaps: list = field(default_factory=list)  # posts com hash ausente após seal


# ==============================================================================
# 🛠️  LOGGER
# ==============================================================================

def setup_logger(apply: bool, force: bool):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = log_timestamp()
    mode_tag = "APPLY" if apply else "DRY_RUN"
    if force:
        mode_tag += "_FORCE"
    log_path = LOG_DIR / f"SP02_upgrade_identity_{mode_tag}_{ts}.log"
    lines = []

    def log(msg: str, level: str = "INFO", color: str = RESET, verbose_only: bool = False):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌", "SKIP": "⏭️ ", "DRY": "🔍"}
        icon = icons.get(level, "  ")
        lines.append(f"[{get_utc_now()}] [{level}] {msg}")
        print(f"{color}{icon} {msg}{RESET}")

    def flush():
        log_path.write_text("\n".join(lines), encoding="utf-8")

    return log, flush


# ==============================================================================
# 🔧  FUNÇÕES AUXILIARES
# ==============================================================================

def clean_html_text(raw: str) -> str:
    return re.sub(r"<[^>]+>", "", raw).strip()


def extract_title_from_html(html_path: Path, slug_fallback: str, log) -> tuple[str, str]:
    """
    Extrai título do <h1>. Fallback para slug.
    V5.1: logging de exceção — sem swallow silencioso (SF-03).
    """
    if not html_path.exists():
        return slug_fallback.replace("-", " ").title(), "inferred_from_slug"
    try:
        head = html_path.read_text(encoding="utf-8")[:5000]
        match = re.search(r"<h1[^>]*>(.*?)</h1>", head, re.IGNORECASE | re.DOTALL)
        if match:
            title = clean_html_text(match.group(1))
            if title:
                return title, "extracted_h1"
    except Exception as e:
        log(f"extract_title falhou para {html_path}: {e} — usando slug fallback", "WARN", YELLOW)
    return slug_fallback.replace("-", " ").title(), "inferred_from_slug"


def extract_wp_id(html_path: Path, log) -> int | None:
    """
    Lê Source-ID da Tatuagem canônica.
    V5.1: logging de exceção — sem swallow silencioso (SF-04).
    """
    if not html_path.exists():
        return None
    try:
        head = html_path.read_text(encoding="utf-8")[:2000]
        match = re.search(r"Source-ID:\s+(\d+)", head)
        if match:
            return int(match.group(1))
    except Exception as e:
        log(f"extract_wp_id falhou para {html_path}: {e}", "WARN", YELLOW)
    return None


# ==============================================================================
# 🔐  CALCULAR SEAL HASH (expansível)
# ==============================================================================

def compute_seal_hashes(folder: Path, log) -> dict:
    """
    Calcula hashes de todos os artefatos relevantes para o SEAL.
    V5.1: cobre content.html (EN), content.html (PT), semantic.json.
    Todos em bytes (rb) — encoding byte-stable (DCV-02).
    """
    hashes = {}
    artifacts = {
        "en-US": folder / "source" / "en-US" / "content.html",
        "pt-BR": folder / "source" / "pt-BR" / "content.html",
        "semantic": folder / "meta" / "semantic.json",
    }
    for key, path in artifacts.items():
        if path.exists():
            h = sha256_file(path)
            if h:
                hashes[key] = h
            else:
                log(f"sha256_file retornou None para {path} — arquivo corrompido?", "WARN", YELLOW)
    return hashes


# ==============================================================================
# 🧬  UPGRADE DE UM POST
# ==============================================================================

def upgrade_post(folder: Path, apply: bool, force: bool, log, stats: Stats) -> str:
    """
    Faz upgrade do identity.json para Schema V3.1 e sela hashes.
    V5.1: atomic write, backup, expanded seal, logging robusto.
    Retorna: UPGRADED | SKIPPED | FORCED | DRY_UPGRADED | DRY_SKIP | ERROR:<reason>
    """
    pdpn      = folder.name
    json_path = folder / "meta"   / "identity.json"
    source_en = folder / "source" / "en-US" / "content.html"
    source_pt = folder / "source" / "pt-BR" / "content.html"

    stats.total += 1

    if not json_path.exists():
        stats.errors += 1
        return "ERROR:identity.json ausente"

    try:
        old_data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        stats.errors += 1
        return f"ERROR:json_malformed({e})"

    current_schema = old_data.get("schema_version", "0")

    if current_schema == SCHEMA_VERSION_SEAL and not force:
        stats.skipped += 1
        return "SKIPPED"

    if not apply:
        return "DRY_UPGRADED" if current_schema != SCHEMA_VERSION_SEAL else "DRY_WOULD_FORCE"

    # ── ESCRITA REAL ──────────────────────────────────────────────────────

    # Capturar timestamp UMA VEZ (ND-02)
    now = get_utc_now()

    old_identity = old_data.get("identity", {})
    old_sro      = old_data.get("sro", {})
    old_titles   = old_data.get("titles", {})
    old_artifacts = old_data.get("artifacts", {})

    pdpn_val   = old_identity.get("pdpn")   or old_data.get("pdpn",   folder.name)
    findex_val = old_identity.get("findex")  or old_data.get("findex", "0000")
    slug_val   = (old_identity.get("slug_root")
                  or old_data.get("slug_en")
                  or old_data.get("slug", "unknown"))
    section    = pdpn_val.split(".")[0] if "." in pdpn_val else "MS"

    title_en = old_titles.get("en")
    title_en_source = old_titles.get("en_source", "preserved")
    if not title_en:
        title_en, title_en_source = extract_title_from_html(source_en, slug_val, log)

    title_pt = old_titles.get("pt", None)
    title_pt_source = old_titles.get("pt_source", None)

    wp_id = (old_sro.get("original_wp_id")
             or old_data.get("source_id")
             or extract_wp_id(source_en, log))

    # ── Calcular SEAL hashes (V5.1 expandido) ─────────────────────────────
    seal_hashes = compute_seal_hashes(folder, log)
    hash_en = seal_hashes.get("en-US") or "missing_file"
    hash_pt = seal_hashes.get("pt-BR")
    hash_semantic = seal_hashes.get("semantic")

    # ── Verificar gap de seal (post traduzido sem hash) ───────────────────
    if source_pt.exists() and not hash_pt:
        log(f"{pdpn}: pt-BR existe mas hash não calculável — arquivo corrompido?", "WARN", YELLOW)
        stats.seal_gaps.append(pdpn)

    # ── Backup ANTES de qualquer escrita ──────────────────────────────────
    backup_file(json_path)

    # ── Construir Schema V3.1 ─────────────────────────────────────────────
    new_artifacts = {
        "en-US": {
            "status":           "canonical",
            "file_path":        "source/en-US/content.html",
            "integrity_sha256": hash_en,
            "last_audit":       now,
        }
    }

    # Preservar pt-BR artifact se existe (não sobrescrever tradução feita pelo SP10)
    if hash_pt:
        existing_pt = old_artifacts.get("pt-BR", {})
        new_artifacts["pt-BR"] = {
            **existing_pt,
            "integrity_sha256": hash_pt,
            "last_audit":       now,
        }
        # Não alterar status="derived" se já estava correto
        if "status" not in new_artifacts["pt-BR"]:
            new_artifacts["pt-BR"]["status"] = "derived"

    # Adicionar hash do semantic.json se existir
    if hash_semantic:
        new_artifacts["semantic"] = {
            "integrity_sha256": hash_semantic,
            "last_audit":       now,
        }

    new_data = {
        "schema_version":   SCHEMA_VERSION_SEAL,
        "last_updated_utc": now,
        "identity": {
            "pdpn":         pdpn_val,
            "findex":       findex_val,
            "slug_root":    slug_val,
            "section_code": section,
        },
        "sro": {
            "source":         "PureDhamma.net",
            "url":            None,
            "original_wp_id": wp_id,
            "author":         "Lal A.",
        },
        "titles": {
            "en":         title_en,
            "en_source":  title_en_source,
            "pt":         title_pt,
            "pt_source":  title_pt_source,
        },
        "artifacts": new_artifacts,
    }

    # ── Escrita atômica (RC-03) ────────────────────────────────────────────
    atomic_write_json(json_path, new_data)

    if current_schema == SCHEMA_VERSION_SEAL:
        stats.forced += 1
        return "FORCED"
    else:
        stats.upgraded += 1
        return "UPGRADED"


# ==============================================================================
# 🚀  MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="SP02 Upgrade Identity — SEAL Script V5.1")
    parser.add_argument("--apply", action="store_true",
                        help="Aplica mudanças. Sem isso: DRY-RUN.")
    parser.add_argument("--force", action="store_true",
                        help="Reprocessa mesmo posts já em schema 3.1 (SEAL).")
    args = parser.parse_args()

    log, flush = setup_logger(args.apply, args.force)
    stats = Stats()
    fc = FailureCounter(max_failures=FAILURE_THRESHOLD, label="SP02")

    mode = "APPLY" + ("_FORCE" if args.force else "") if args.apply else "DRY_RUN"
    log(f"=== SP02 Upgrade Identity ({mode}) ===")
    log(f"CSL: {CSL_ROOT}")
    log(f"Target schema: {SCHEMA_VERSION_SEAL}")

    if not CSL_ROOT.exists():
        raise PipelineAbort(f"CSL não encontrada: {CSL_ROOT}")

    folders = sorted([f for f in CSL_ROOT.iterdir() if f.is_dir()])
    log(f"Posts encontrados: {len(folders)}")

    for folder in folders:
        pdpn = folder.name
        result = upgrade_post(folder, args.apply, args.force, log, stats)

        if result in ("UPGRADED", "FORCED"):
            log(f"  ✅ {pdpn}: {result}", "OK", GREEN)
        elif result.startswith("DRY"):
            pass  # silencioso em dry-run para não poluir output
        elif result == "SKIPPED":
            pass  # silencioso
        elif result.startswith("ERROR"):
            if fc.fail(pdpn, result):
                flush()
                fc.assert_clean()
                return

    # ── SEAL REPORT ──────────────────────────────────────────────────────
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  SP02 / SEAL REPORT ({mode}){RESET}")
    print(f"{CYAN}{'='*62}{RESET}")
    print(f"  Posts processados  : {stats.total}")
    print(f"  ✅ Upgraded         : {stats.upgraded}")
    print(f"  🔒 Forced (re-seal) : {stats.forced}")
    print(f"  ⏭️  Skipped (já OK)  : {stats.skipped}")
    print(f"  ❌ Erros            : {stats.errors}")

    if stats.seal_gaps:
        print(f"\n  {RED}⚠️  SEAL GAPS: {len(stats.seal_gaps)} post(s) com pt-BR sem hash:{RESET}")
        for p in stats.seal_gaps[:10]:
            print(f"     - {p}")
        if len(stats.seal_gaps) > 10:
            print(f"     ... +{len(stats.seal_gaps) - 10}")
    else:
        print(f"\n  {GREEN}🔐 HASH SEALS: TODOS OS HASHES COBERTOS{RESET}")

    print(f"{CYAN}{'='*62}{RESET}\n")

    flush()

    # ── Exit codes semânticos ─────────────────────────────────────────────
    if not args.apply:
        sys.exit(2)  # dry-run

    if stats.seal_gaps:
        print(f"{RED}❌ SEAL INCOMPLETO: {len(stats.seal_gaps)} post(s) sem hash.{RESET}")
        sys.exit(1)

    fc.assert_clean()
    sys.exit(0)


if __name__ == "__main__":
    main()
