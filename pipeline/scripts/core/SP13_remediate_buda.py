#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SP13_remediate_buda.py
===================================================
Versão:  1.0 (AXIS-NIDDHI V5.4 — Emergency Remediation)
Data:    2026-04-19

FUNÇÃO:
  Corrige TODAS as ocorrências da grafia PROIBIDA "Buda" nos conteúdos PT
  e nos títulos PT já gravados no CSL (09-csl).

  Esta é uma correção de emergência — one-shot.
  Futuras traduções serão protegidas pelo sanitize_pt.py integrado ao SP10/SP11.

ESCOPO:
  1. content.html PT-BR → sanitize_pt_output() + recalcular hash
  2. identity.json titles.pt → sanitize_pt_output()
  3. Não toca content.html EN-US (canônico)

USO:
  python3 SP13_remediate_buda.py              # dry-run
  python3 SP13_remediate_buda.py --apply      # corrige e grava
"""

import json
import re
import sys
import hashlib
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DIR_09_CSL, LOG_DIR
from pipeline_utils import atomic_write_json, atomic_write_bytes, get_utc_now, log_timestamp, backup_file
from sanitize_pt import sanitize_pt_output, audit_pt_text

# Cores
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

_PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")


def sha256_text(text: str) -> str:
    """Calcula SHA-256 de um texto normalizado (LF)."""
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SP13 — Remediação 'Buda' → 'Buddha'")
    parser.add_argument("--apply", action="store_true", help="Gravar correções (padrão: dry-run)")
    args = parser.parse_args()
    apply = args.apply
    mode = "APPLY" if apply else "DRY_RUN"

    # Logger
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = log_timestamp()
    log_file = LOG_DIR / f"SP13_remediate_buda_{mode}_{ts}.log"
    log_lines = []

    def log(msg, level="INFO"):
        icon = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "FIX": "🔧", "DRY": "🔍", "ERROR": "❌"}.get(level, "  ")
        line = f"{icon} [{level}] {msg}"
        print(line)
        log_lines.append(f"[{get_utc_now()}] {line}")

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  🔧 SP13 — Remediação de Emergência: 'Buda' → 'Buddha'{RESET}")
    print(f"{CYAN}  Modo: {mode}{RESET}")
    print(f"{CYAN}  CSL:  {DIR_09_CSL}{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    # Percorrer todos os posts CSL
    posts = sorted(
        [d for d in DIR_09_CSL.iterdir() if d.is_dir() and _PDPN_RE.match(d.name)],
        key=lambda d: d.name,
    )

    content_fixed  = 0
    title_fixed    = 0
    content_errors = 0
    title_errors   = 0
    total_replacements = 0

    for post_dir in posts:
        pdpn = post_dir.name
        pt_html_path  = post_dir / "source" / "pt-BR" / "content.html"
        identity_path = post_dir / "meta" / "identity.json"

        # ── 1. Corrigir content.html PT-BR ───────────────────────────────
        if pt_html_path.exists():
            try:
                original = pt_html_path.read_text(encoding="utf-8")
                violations = audit_pt_text(original)

                if violations:
                    sanitized = sanitize_pt_output(original)
                    num_fixes = len(violations)
                    total_replacements += num_fixes
                    terms = ", ".join(set(v["term"] for v in violations))

                    if apply:
                        # Backup antes de correção
                        backup_file(pt_html_path)

                        # Escrever conteúdo corrigido
                        atomic_write_bytes(pt_html_path, sanitized)

                        # Recalcular hash e atualizar identity.json
                        new_hash = sha256_text(sanitized)
                        if identity_path.exists():
                            try:
                                data = json.loads(identity_path.read_text(encoding="utf-8"))
                                pt_artifact = data.get("artifacts", {}).get("pt-BR", {})
                                if pt_artifact:
                                    pt_artifact["integrity_sha256"] = new_hash
                                    pt_artifact["remediated_at"] = get_utc_now()
                                    data["last_updated_utc"] = get_utc_now()
                                    atomic_write_json(identity_path, data)
                            except Exception as e:
                                log(f"  {pdpn}: hash não atualizado — {e}", "WARN")

                        log(f"  {pdpn}: {num_fixes}x corrigido ({terms})", "FIX")
                    else:
                        log(f"  {pdpn}: {num_fixes}x seria corrigido ({terms})", "DRY")

                    content_fixed += 1

            except Exception as e:
                log(f"  {pdpn}: ERRO content.html — {e}", "ERROR")
                content_errors += 1

        # ── 2. Corrigir title PT no identity.json ────────────────────────
        if identity_path.exists():
            try:
                data = json.loads(identity_path.read_text(encoding="utf-8"))
                pt_title = data.get("titles", {}).get("pt", "")

                if pt_title:
                    title_violations = audit_pt_text(pt_title)
                    if title_violations:
                        new_title = sanitize_pt_output(pt_title)

                        if apply:
                            backup_file(identity_path)
                            data["titles"]["pt"] = new_title
                            data["titles"]["pt_remediated"] = True
                            data["last_updated_utc"] = get_utc_now()
                            atomic_write_json(identity_path, data)
                            log(f"  {pdpn}: título '{pt_title}' → '{new_title}'", "FIX")
                        else:
                            log(f"  {pdpn}: título seria '{pt_title}' → '{new_title}'", "DRY")

                        title_fixed += 1

            except Exception as e:
                log(f"  {pdpn}: ERRO identity.json — {e}", "ERROR")
                title_errors += 1

    # ── Relatório ────────────────────────────────────────────────────────
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"  SP13 CONCLUÍDO ({mode})")
    print(f"  📄 Conteúdos corrigidos  : {content_fixed}")
    print(f"  📝 Títulos corrigidos    : {title_fixed}")
    print(f"  🔢 Total substituições   : {total_replacements}")
    print(f"  ❌ Erros                 : {content_errors + title_errors}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    if apply and (content_fixed > 0 or title_fixed > 0):
        print(f"{YELLOW}⚠️  PRÓXIMOS PASSOS OBRIGATÓRIOS:{RESET}")
        print(f"  1. python3 {_SCRIPT_DIR}/SP02_upgrade_identity.py --apply --force  (re-selar)")
        print(f"  2. Rebuild do site estático (SSG)")
        print(f"  3. Deploy no Netlify\n")

    log_file.write_text("\n".join(log_lines), encoding="utf-8")
    log(f"Log: {log_file}", "OK")


if __name__ == "__main__":
    main()
