#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SP10_translate_deepl.py
===================================================
Versão:  V5.1 — AXIS-NIDDHI Hardening Edition
Data:    2026-03-07

HARDENING V5.1 (vs V3.0):
  ★ [DCV-01] Escrita atômica: identity.json ANTES de content.html
  ★ [DCV-01] Sentinel status="in_progress" — crash recovery automático
  ★ [RC-04]  Backup .json.bak criado ANTES de qualquer mutação
  ★ [RC-01]  Lock file por PDPN — previne runs concorrentes
  ★ [SF-01]  sys.exit(1) se erros > FAILURE_THRESHOLD
  ★ [ND-02]  Timestamp capturado UMA VEZ por post (now = get_utc_now())
  ★ Auto-recovery: ao iniciar, detecta e reprocessa posts in_progress
  ★ BENG_AUTO_TRANSLATE=true para bypass do prompt interativo (CI)
  ★ Retry loop: max 2 tentativas por post em caso de rede transiente

SEQUÊNCIA:
  SP10 → roda após SP09 (Translation_Control_Center.csv gerado)
  SEAL 2 → rodar SP02 --apply --force após SP10

USO:
  python3 SP10_translate_deepl.py           # interativo
  BENG_AUTO_TRANSLATE=true python3 ...      # CI/headless
"""

import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests

# ==============================================================================
# ⚙️  CONFIGURAÇÃO
# ==============================================================================

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import (
    DIR_09_CSL,
    METADATA_DIR,
    LOG_DIR,
    DEEPL_API_URL,
    DEEPL_GLOSSARY_ID,
    FAILURE_THRESHOLD,
    get_deepl_key,
)
from pipeline_utils import (
    atomic_write_bytes,
    atomic_write_json,
    backup_file,
    cleanup_orphaned_tmp,
    find_in_progress_posts,
    get_utc_now,
    FailureCounter,
    log_timestamp,
    mark_in_progress,
    PipelineAbort,
    sha256_file,
)

CSL_DIR   = DIR_09_CSL
MENU_FILE = METADATA_DIR / "Translation_Control_Center.csv"

# Cores
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

MAX_RETRIES = 2  # máximo de tentativas por post em falha de rede


# ==============================================================================
# 🛠️  LOGGER
# ==============================================================================

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = log_timestamp()  # sub-segundo — ND-01
    log_path = LOG_DIR / f"SP10_translate_{ts}.log"
    lines = []

    def log(msg: str, level: str = "INFO", color: str = RESET):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌", "SKIP": "⏭️ "}
        icon = icons.get(level, "  ")
        ts_ = get_utc_now()
        line = f"[{ts_}] [{level}] {msg}"
        lines.append(line)
        print(f"{color}{icon} {msg}{RESET}")

    def flush():
        try:
            log_path.write_text("\n".join(lines), encoding="utf-8")
        except Exception:
            pass

    return log, flush


# ==============================================================================
# 🔍  FIND FOLDER
# ==============================================================================

def find_folder_by_pdpn(pdpn: str) -> Optional[Path]:
    candidate = CSL_DIR / pdpn
    if candidate.is_dir():
        return candidate
    # Fallback: busca em toda a CSL (custo: O(n) — usar apenas se estrutura mudou)
    for d in CSL_DIR.iterdir():
        if d.is_dir() and d.name == pdpn:
            return d
    return None


# ==============================================================================
# 🌐  DEEPL API
# ==============================================================================

def translate_text(text: str, auth_key: str, glossary_id: str) -> str:
    """
    Traduz via DeepL API Free.
    Levanta RuntimeError em caso de falha — sem silent swallow.
    """
    resp = requests.post(
        f"{DEEPL_API_URL}/translate",
        headers={"Authorization": f"DeepL-Auth-Key {auth_key}"},
        data={
            "text": text,
            "source_lang": "EN",
            "target_lang": "PT-BR",
            "tag_handling": "html",
            "glossary_id": glossary_id,
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"DeepL HTTP {resp.status_code}: {resp.text[:200]}")
    translations = resp.json().get("translations", [])
    if not translations:
        raise RuntimeError("DeepL retornou resposta vazia.")
    return translations[0]["text"]


def check_quota(auth_key: str) -> tuple[int, int]:
    """Retorna (used_chars, limit_chars). Levanta em caso de erro."""
    resp = requests.get(
        f"{DEEPL_API_URL}/usage",
        headers={"Authorization": f"DeepL-Auth-Key {auth_key}"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("character_count", 0), data.get("character_limit", 0)


# ==============================================================================
# 🔄  AUTO-RECOVERY: POSTS IN_PROGRESS
# ==============================================================================

def recover_in_progress_posts(log) -> int:
    """
    Detecta posts com status="in_progress" ou identity.json corrompido.
    Limpa o sentinel (os posts serão reprocessados na iteração normal).
    Retorna contagem de posts encontrados.
    """
    problematic = find_in_progress_posts(CSL_DIR)
    if not problematic:
        return 0

    log(f"🔧 AUTO-RECOVERY: {len(problematic)} post(s) com estado in_progress detectados.", "WARN", YELLOW)
    for folder in problematic:
        pdpn = folder.name
        json_path = folder / "meta" / "identity.json"
        pt_html = folder / "source" / "pt-BR" / "content.html"

        # Se content.html existe mas sem hash → deletar para reprocessar
        if pt_html.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                pt_artifact = data.get("artifacts", {}).get("pt-BR", {})
                has_hash = bool(pt_artifact.get("integrity_sha256"))
                if not has_hash or pt_artifact.get("status") == "in_progress":
                    pt_html.unlink()
                    log(f"   {pdpn}: content.html sem hash removido — será reprocessado.", "WARN", YELLOW)
            except Exception:
                # JSON corrompido: restaurar do backup
                bak = json_path.with_suffix(".json.bak")
                if bak.exists():
                    bak.replace(json_path)
                    log(f"   {pdpn}: identity.json restaurado do .bak.", "OK", GREEN)
                else:
                    log(f"   {pdpn}: JSON corrompido sem .bak — post será ignorado.", "ERROR", RED)

    return len(problematic)


# ==============================================================================
# 📝  PROCESSAR UM POST
# ==============================================================================

def process_post(
    item: dict,
    auth_key: str,
    glossary_id: str,
    log,
    dry_run: bool = False,
) -> str:
    """
    Traduz um post com escrita totalmente atômica e sentinel de recovery.
    Retorna: "OK" | "SKIPPED" | "ERROR:<reason>"
    """
    pdpn      = item["PD#PN"]
    folder    = find_folder_by_pdpn(pdpn)
    if not folder:
        return f"ERROR:pasta não encontrada para {pdpn}"

    json_path = folder / "meta"   / "identity.json"
    source_en = folder / "source" / "en-US" / "content.html"
    target_pt = folder / "source" / "pt-BR" / "content.html"
    lock_file = folder / "source" / "pt-BR" / ".translate.lock"

    # ── Idempotência: post com hash já registrado → skip ──────────────────
    if target_pt.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            pt_artifact = data.get("artifacts", {}).get("pt-BR", {})
            if (pt_artifact.get("integrity_sha256") and
                    pt_artifact.get("status") != "in_progress"):
                return "SKIPPED"
        except Exception:
            pass  # JSON corrompido → prosseguir para reprocessar

    # ── Lock file: previne dupla execução concorrente (RC-01) ─────────────
    if lock_file.exists():
        return f"ERROR:lock file ativo em {pdpn} — outro processo em execução?"
    target_pt.parent.mkdir(parents=True, exist_ok=True)
    lock_file.touch()

    try:
        # ── Ler identity.json ────────────────────────────────────────────
        if not json_path.exists():
            return f"ERROR:identity.json ausente para {pdpn}"
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            return f"ERROR:identity.json corrompido: {e}"

        # ── Capturar timestamp UMA VEZ (ND-02) ──────────────────────────
        now = get_utc_now()

        # ── Backup ANTES de qualquer mutação (RC-04) ─────────────────────
        backup_file(json_path)

        # ── Sentinel in_progress (DCV-01) ────────────────────────────────
        if not dry_run:
            mark_in_progress(json_path, pdpn)

        # ── Ler conteúdo EN ──────────────────────────────────────────────
        if not source_en.exists():
            return f"ERROR:content.html EN ausente para {pdpn}"
        body_en = source_en.read_text(encoding="utf-8")

        # ── Traduzir Título ──────────────────────────────────────────────
        title_en = data.get("titles", {}).get("en", "Untitled")
        if not dry_run:
            title_pt = translate_text(title_en, auth_key, glossary_id)
        else:
            title_pt = f"[DRY-RUN] {title_en}"

        # ── Traduzir Corpo ───────────────────────────────────────────────
        if not dry_run:
            body_pt = translate_text(body_en, auth_key, glossary_id)
        else:
            body_pt = body_en

        # ── Montar HTML PT com header derivado ──────────────────────────
        header = (
            f"<!--\n"
            f"💎 BRASILEIRINHO ENGINE - DERIVED TRANSLATION ARTIFACT\n"
            f"PD#PN:        {pdpn}\n"
            f"Language:     pt-BR\n"
            f"Generated-At: {now}\n"
            f"Engine:       DeepL API (Glossary V5)\n"
            f"-->"
        )
        final_html = f"{header}\n\n{body_pt}"

        # ── Calcular hash do content que será escrito ─────────────────────
        import hashlib
        h = hashlib.sha256()
        h.update(final_html.replace("\r\n", "\n").encode("utf-8"))
        content_hash = h.hexdigest()

        # ── Construir identity.json atualizado ────────────────────────────
        data.setdefault("titles", {})
        data["titles"]["pt"] = title_pt
        data["titles"]["pt_source"] = "deepl_v5"
        data.setdefault("artifacts", {})
        data["artifacts"]["pt-BR"] = {
            "status":           "derived",
            "file_path":        "source/pt-BR/content.html",
            "engine":           "DeepL API",
            "translated_at":    now,           # mesmo timestamp (ND-02)
            "integrity_sha256": content_hash,  # hash da string que será escrita
        }

        # ── ESCRITA ATÔMICA: identity.json PRIMEIRO (DCV-01) ──────────────
        # Se crash aqui: identity.json tem status="derived" com hash.
        # target_pt ainda não existe → SP10 reprocessa na próxima run.
        if not dry_run:
            atomic_write_json(json_path, data)

        # ── ESCRITA ATÔMICA: content.html SEGUNDO ─────────────────────────
        # Se crash aqui: identity.json tem hash correto, content.html ausente.
        # Próxima run: idempotência detecta target_pt ausente → reprocessa.
        if not dry_run:
            atomic_write_bytes(target_pt, final_html)

            # ── Verificação pós-escrita: hash no disco deve bater ──────────
            actual_hash = sha256_file(target_pt)
            if actual_hash != content_hash:
                return f"ERROR:hash mismatch após escrita para {pdpn} (esperado={content_hash[:8]} real={actual_hash[:8]})"

        return "OK"

    finally:
        # Lock sempre removido — mesmo em caso de exceção
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass


# ==============================================================================
# 🚀  EXECUÇÃO PRINCIPAL
# ==============================================================================

def run_translation():
    log, flush = setup_logger()
    auth_key   = get_deepl_key()

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 BRASILEIRINHO ENGINE — SP10 Tradução DeepL V5.1{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    # ── Cleanup de temp files órfãos (RC-05) ──────────────────────────────
    cleaned = cleanup_orphaned_tmp(CSL_DIR, logger=None)
    if cleaned:
        log(f"Cleanup: {cleaned} arquivo(s) .tmp órfão(s) removidos.", "WARN", YELLOW)

    # ── Auto-recovery: posts in_progress (DCV-01) ─────────────────────────
    recovered = recover_in_progress_posts(log)
    if recovered:
        log(f"Auto-recovery: {recovered} post(s) serão reprocessados.", "INFO", CYAN)

    # ── Verificar CSV ─────────────────────────────────────────────────────
    if not MENU_FILE.exists():
        raise PipelineAbort(f"Translation_Control_Center.csv não encontrado: {MENU_FILE}")

    # ── Ler lote de tradução ──────────────────────────────────────────────
    batch = []
    with open(MENU_FILE, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cmd = row.get("COMMAND", "").strip().upper()
            status = row.get("Status", "").strip().upper()
            if cmd in ("YES", "SIM", "X") and status != "DONE":
                batch.append(row)

    if not batch:
        log("Nenhum post pendente com COMMAND=YES no CSV. Pipeline OK.", "INFO", GREEN)
        flush()
        return

    # ── Pre-flight: verificar saldo DeepL ────────────────────────────────
    try:
        used, limit = check_quota(auth_key)
        remaining = limit - used
        total_chars = sum(int(r.get("Chars", 0)) for r in batch)
        log(f"DeepL saldo: {remaining:,} chars disponíveis | Lote: {total_chars:,} chars estimados.", "INFO")
        if total_chars > remaining:
            raise PipelineAbort(
                f"Saldo DeepL insuficiente: precisa {total_chars:,}, tem {remaining:,}."
            )
    except PipelineAbort:
        raise
    except Exception as e:
        log(f"Aviso: não foi possível verificar saldo DeepL: {e}", "WARN", YELLOW)

    # ── Confirmação humana (bypass via env BENG_AUTO_TRANSLATE) ──────────
    auto = os.environ.get("BENG_AUTO_TRANSLATE", "").lower() == "true"
    if not auto:
        print(f"\n{YELLOW}⚠️  Prestes a traduzir {len(batch)} post(s).")
        print(f"   Custo estimado: {total_chars:,} chars{RESET}")
        confirm = input("\nConfirmar? [y/N]: ").strip().lower()
        if confirm != "y":
            log("Tradução cancelada pelo operador.", "WARN", YELLOW)
            flush()
            return

    # ── Loop de tradução com retry ────────────────────────────────────────
    fc = FailureCounter(max_failures=FAILURE_THRESHOLD, label="SP10")
    success = 0
    skipped = 0

    for item in batch:
        pdpn = item.get("PD#PN", "UNKNOWN")
        log(f"Processando {pdpn}...", "INFO")

        result = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = process_post(item, auth_key, DEEPL_GLOSSARY_ID, log)
                break
            except Exception as e:
                if attempt < MAX_RETRIES:
                    log(f"   Tentativa {attempt} falhou: {e} — retrying...", "WARN", YELLOW)
                    time.sleep(2 ** attempt)  # backoff exponencial
                else:
                    result = f"ERROR:{e}"

        if result == "OK":
            log(f"   ✅ {pdpn} traduzido.", "OK", GREEN)
            success += 1
        elif result == "SKIPPED":
            log(f"   ⏭️  {pdpn} já traduzido (skip).", "SKIP", GRAY)
            skipped += 1
        else:
            if fc.fail(pdpn, result or "UNKNOWN"):
                flush()
                fc.assert_clean()  # levanta PipelineAbort
                return

        time.sleep(1)  # rate limiting

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{CYAN}{'='*50}{RESET}")
    print(f"{CYAN}  SP10 CONCLUÍDO{RESET}")
    print(f"  ✅ Traduzidos : {success}")
    print(f"  ⏭️  Pulados    : {skipped}")
    print(f"  ❌ Falhas     : {fc.count}")
    print(f"{CYAN}{'='*50}{RESET}")
    print(f"\n{YELLOW}  ⚠️  PRÓXIMO PASSO OBRIGATÓRIO:")
    print(f"  python3 SP02_upgrade_identity.py --apply --force  (SEAL 2){RESET}\n")

    flush()

    # ── Abortar se houve qualquer falha (SF-01) ───────────────────────────
    fc.assert_clean()


if __name__ == "__main__":
    run_translation()
