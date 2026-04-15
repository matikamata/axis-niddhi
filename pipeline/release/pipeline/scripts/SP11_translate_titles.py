#!/usr/bin/env python3
# /beng-fut/pipeline/scripts/SP11_translate_titles.py
"""
💎 BRASILEIRINHO ENGINE — SP11 Translate Titles
================================================
Versão:   1.1 (AXIS-NIDDHI V5.2.3 — CLS Integration)
Objetivo: traduzir títulos EN → PT para posts que ainda não têm título PT.
          Cirúrgico: só toca identity.json, nunca o content.html.

DELTA vs V1.0:
  ★ [CLS] Após gravar titles.pt, chama append_translation_event()
          registrando evento "title_translated" em lineage.translations[]
  ★ [CLS] graceful degradation — funciona sem cls_tools se necessário

Uso:
    python3 SP11_translate_titles.py            # dry-run (mostra o que faria)
    python3 SP11_translate_titles.py --apply    # traduz e grava

Após o --apply, execute:
    python3 SP02_upgrade_identity.py --apply --force
"""

import sys
import json
import re
import argparse
import time
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DIR_09_CSL, LOG_DIR, get_deepl_key
from pipeline_utils import atomic_write_json, get_utc_now, log_timestamp

# CLS integration — graceful degradation
try:
    from cls_tools import append_translation_event
    _CLS_AVAILABLE = True
except ImportError:
    _CLS_AVAILABLE = False

_PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")

GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RED    = "\033[91m"
RESET  = "\033[0m"

# DeepL: máximo de textos por chamada
BATCH_SIZE = 50


# ==============================================================================
# 🌐  DEEPL
# ==============================================================================

def resolve_glossary_id(auth_key: str) -> str | None:
    """Busca o ID do glossário Glossario_v5 na conta DeepL. Nunca usa ID hardcoded."""
    import requests
    resp = requests.get(
        "https://api-free.deepl.com/v2/glossaries",
        headers={"Authorization": f"DeepL-Auth-Key {auth_key}"},
        timeout=15,
    )
    if resp.status_code != 200:
        return None
    for g in resp.json().get("glossaries", []):
        if "glossario_v5" in g.get("name", "").lower():
            return g["glossary_id"]
    # Fallback: primeiro glossário EN→PT-BR ativo
    for g in resp.json().get("glossaries", []):
        if g.get("source_lang", "").upper() == "EN" and "PT" in g.get("target_lang", "").upper():
            return g["glossary_id"]
    return None


def translate_batch(titles: list[str], auth_key: str, glossary_id: str | None = None) -> list[str]:
    """Traduz uma lista de títulos EN → PT-BR via DeepL REST API com requests."""
    import requests

    headers = {"Authorization": f"DeepL-Auth-Key {auth_key}"}
    payload = {
        "text":        titles,
        "source_lang": "EN",
        "target_lang": "PT-BR",
    }
    if glossary_id:
        payload["glossary_id"] = glossary_id

    resp = requests.post(
        "https://api-free.deepl.com/v2/translate",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if resp.status_code == 456:
        print(f"{YELLOW}⚠️  DeepL HTTP 456: cota esgotada.{RESET}")
        return "__QUOTA_EXCEEDED__"
    if resp.status_code != 200:
        print(f"{RED}❌ Erro DeepL HTTP {resp.status_code}: {resp.text[:200]}{RESET}")
        return []

    return [t["text"] for t in resp.json()["translations"]]


# ==============================================================================
# 🔍  SCANNER
# ==============================================================================

def find_posts_missing_pt_title(force: bool = False) -> list[tuple[Path, dict]]:
    """
    Retorna posts que TÊM conteúdo PT mas NÃO têm título PT.
    Com --force: retorna todos os posts com conteúdo PT (para re-traduzir).
    """
    posts = sorted(
        [d for d in DIR_09_CSL.iterdir() if d.is_dir() and _PDPN_RE.match(d.name)],
        key=lambda d: d.name,
    )
    result = []
    for post_dir in posts:
        # Só processar posts que já têm conteúdo PT
        pt_html = post_dir / "source" / "pt-BR" / "content.html"
        if not pt_html.exists() or pt_html.stat().st_size < 100:
            continue

        identity_path = post_dir / "meta" / "identity.json"
        if not identity_path.exists():
            continue
        try:
            identity = json.loads(identity_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        pt_title = identity.get("titles", {}).get("pt")
        has_title = bool(pt_title and str(pt_title).strip())

        if force or not has_title:
            result.append((post_dir, identity))

    return result


# ==============================================================================
# 🚀  MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="SP11 — Traduzir títulos EN→PT")
    parser.add_argument("--apply", action="store_true", help="Traduzir e gravar (padrão: dry-run)")
    parser.add_argument("--force", action="store_true", help="Re-traduzir mesmo que título PT já exista")
    args = parser.parse_args()
    mode = "APPLY" if args.apply else "DRY_RUN"
    force = args.force

    # Logger
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = log_timestamp()
    log_file = LOG_DIR / f"SP11_translate_titles_{mode}_{ts}.log"
    log_lines: list[str] = []

    def log(msg: str, level: str = "INFO"):
        icon = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌", "DRY": "🔍"}.get(level, "ℹ️ ")
        line = f"{icon} [{level}] {msg}"
        print(line)
        log_lines.append(f"[{get_utc_now()}] {line}")

    print(f"\n{CYAN}==================================================={RESET}")
    print(f"{CYAN}  SP11 — Tradução de Títulos PT-BR  ({mode}){RESET}")
    print(f"{CYAN}  CSL: {DIR_09_CSL}{RESET}")
    print(f"{CYAN}==================================================={RESET}\n")

    # 1. Encontrar posts
    missing = find_posts_missing_pt_title(force=force)
    label = "para re-traduzir (--force)" if force else "sem título PT"
    log(f"Posts {label}: {len(missing)}")

    if not missing:
        log("Todos os posts já têm título PT. Nada a fazer.", "OK")
        log_file.write_text("\n".join(log_lines), encoding="utf-8")
        return

    if mode == "DRY_RUN":
        log(f"Dry-run — {len(missing)} títulos seriam traduzidos:", "DRY")
        for post_dir, identity in missing[:10]:
            en_title = identity.get("titles", {}).get("en", "(sem título EN)")
            log(f"  {post_dir.name}: '{en_title}'", "DRY")
        if len(missing) > 10:
            log(f"  ... e mais {len(missing) - 10} posts.", "DRY")
        total_chars = sum(len(i.get("titles", {}).get("en", "")) for _, i in missing)
        cost = total_chars * 0.000020
        log(f"Estimativa: {total_chars} chars | ${cost:.4f} USD", "DRY")
        log("Execute com --apply para traduzir.", "DRY")
        log_file.write_text("\n".join(log_lines), encoding="utf-8")
        return

    # 2. APPLY — carregar chave DeepL e glossário
    auth_key = get_deepl_key()
    log(f"DeepL API key carregada.", "OK")

    glossary_id = resolve_glossary_id(auth_key)
    if glossary_id:
        log(f"Glossário DeepL encontrado: {glossary_id}", "OK")
    else:
        log("Glossário não encontrado — traduzindo sem glossário.", "WARN")

    # 3. Traduzir em batches
    success        = 0
    errors         = 0
    quota_exceeded = False

    for i in range(0, len(missing), BATCH_SIZE):
        batch = missing[i : i + BATCH_SIZE]
        titles_en = [identity.get("titles", {}).get("en", "") for _, identity in batch]

        log(f"Traduzindo batch {i//BATCH_SIZE + 1} ({len(batch)} títulos)...")
        translations = translate_batch(titles_en, auth_key, glossary_id)

        if translations == "__QUOTA_EXCEEDED__":
            log(f"Cota DeepL esgotada — interrompendo. Posts restantes serão traduzidos no próximo ciclo.", "WARN")
            quota_exceeded = True
            errors += len(batch)
            break
        if not translations or len(translations) != len(batch):
            log(f"Batch falhou — pulando {len(batch)} posts.", "ERROR")
            errors += len(batch)
            continue

        # 4. Gravar no identity.json
        for (post_dir, identity), pt_title in zip(batch, translations):
            identity_path = post_dir / "meta" / "identity.json"
            en_title = identity.get("titles", {}).get("en", "")
            identity["titles"]["pt"]        = pt_title
            identity["titles"]["pt_source"] = "deepl_v5_sp11"
            identity["last_updated_utc"]    = get_utc_now()

            try:
                atomic_write_json(identity_path, identity)
                log(f"  {post_dir.name}: '{en_title}' → '{pt_title}'", "OK")
                success += 1

                # ── [CLS V5.2.3] Registrar evento de tradução de título ───
                if _CLS_AVAILABLE:
                    try:
                        append_translation_event(
                            identity_path=identity_path,
                            event="title_translated",
                            engine="SP11_v5.2.3",
                            lang="pt-BR",
                            deepl_chars=len(en_title),
                            glossary_id=glossary_id,
                        )
                    except Exception as cls_err:
                        log(f"  {post_dir.name}: [CLS] aviso — {cls_err}", "WARN")

            except Exception as e:
                log(f"  {post_dir.name}: falha ao gravar — {e}", "ERROR")
                errors += 1

        # Pequena pausa entre batches
        if i + BATCH_SIZE < len(missing):
            time.sleep(0.5)

    # 5. Relatório final
    print(f"\n{CYAN}==================================================={RESET}")
    print(f"  SP11 CONCLUÍDO ({mode})")
    print(f"  ✅ Traduzidos : {success}")
    print(f"  ❌ Erros      : {errors}")
    print(f"{CYAN}==================================================={RESET}\n")

    if success > 0:
        print(f"{YELLOW}⚠️  Execute agora para re-selar os hashes:{RESET}")
        print(f"   python3 {_SCRIPT_DIR}/SP02_upgrade_identity.py --apply --force\n")

    log_file.write_text("\n".join(log_lines), encoding="utf-8")
    log(f"Log: {log_file}", "OK")

    if quota_exceeded:
        print(f"{YELLOW}⚠️  SP11: cota DeepL esgotada. Títulos PT serão traduzidos no próximo ciclo.{RESET}")
        print(f"{YELLOW}   Posts pendentes: {errors} — pipeline continua normalmente.{RESET}")
        # Sair com 0: quota exceeded é condição esperada, não erro do pipeline
        sys.exit(0)
    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
