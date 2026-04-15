#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SCRIPT S02
=====================================
Nome:       Pré-Processamento HTML (iframes & colors)
Versão:     4.1  —  AXIS-NIDDHI Edition
Autor:      Lead SRE + Claude Sonnet 4.6
Data:       2026-02-28

POSIÇÃO NA SEQUÊNCIA:
  Step 5 — Roda APÓS S01 (extração).
  Lê 01-extracted-htmls/en-US/ → gera 02-preprocessed/en-US/

O QUE FAZ:
  - Remove artefatos WP (shortcodes, scripts, forms)
  - PRESERVA <iframe> (YouTube/Vimeo)  ← correção crítica vs versão antiga
  - PRESERVA classes e estilos de cor
  - Normaliza links (remove query strings)
  - Corrige zero-padding do Fin-dex na Tatuagem

BUG HISTÓRICO (versão antiga S02_preprocess_htmls.py):
  A lista de tags removidas incluía 'iframe', o que destruía os vídeos
  YouTube antes da tradução. Esse script corrige isso definitivamente.
  Nunca usar a versão antiga — renomeie-a para S02_preprocess_htmls.py.DEPRECATED

DELTA vs V4.0:
  ★ BASE_DIR / INPUT_DIR / OUTPUT_DIR → via config.py (/beng/pipeline)
  ★ Log estruturado com arquivo em /beng/pipeline/logs/
  ★ Idempotência: pula arquivos já processados
  ★ Summary final com contagem de iframes preservados
  ★ Verifica que 01-extracted-htmls é read-only antes de tocar nela
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, LOG_DIR, DIR_01_EXTRACTED, DIR_02_PREPROCESSED, SOURCE_LANG

INPUT_DIR  = DIR_01_EXTRACTED  / SOURCE_LANG   # /beng/pipeline/01-extracted-htmls/en-US
OUTPUT_DIR = DIR_02_PREPROCESSED / SOURCE_LANG  # /beng/pipeline/02-preprocessed/en-US

# ==============================================================================
# 🛠️  UTILITÁRIOS
# ==============================================================================

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"S02_preprocess_{ts}.log"

    def log(msg, level="INFO"):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌"}
        icon  = icons.get(level, "  ")
        ts_   = datetime.now().strftime("%H:%M:%S")
        print(f"{icon}  {msg}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{ts_}] [{level}] {msg}\n")

    return log, log_file


def fix_tattoo_findex(tattoo_text: str) -> str:
    """Garante zero-padding no Fin-dex da Tatuagem (ex: 1 → 0001)."""
    def replace_findex(match):
        number = int(match.group(1))
        return f"Fin-dex:      {str(number).zfill(4)}"
    return re.sub(r"Fin-dex:\s+(\d+)", replace_findex, tattoo_text)


def clean_html(content: str) -> tuple[str, int]:
    """
    Limpa o HTML preservando iframes.
    Retorna (html_limpo, n_iframes_preservados).
    """
    # 1. Separar e corrigir a Tatuagem (comentário canônico)
    tattoo = ""
    tattoo_match = re.search(r"(<!--.*?-->)", content, re.DOTALL)
    if tattoo_match:
        raw_tattoo = tattoo_match.group(1)
        tattoo     = fix_tattoo_findex(raw_tattoo)
        content    = content.replace(raw_tattoo, "")

    # 2. Remover shortcodes WordPress
    content = re.sub(r"\[/?caption.*?\]", "", content)
    content = re.sub(r"\[/?ref.*?\]", "", content)

    # 3. Parsing com BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # 4. ★ CORREÇÃO CRÍTICA: 'iframe' NÃO está nesta lista
    #    A versão antiga incluía 'iframe' aqui — esse era o bug que destruía vídeos.
    for tag in soup(["script", "form", "input", "button",
                     "link", "meta", "object", "embed"]):
        tag.decompose()

    # 5. Contar iframes preservados (YouTube/Vimeo)
    iframes_preserved = len(soup.find_all("iframe"))

    # 6. Limpar atributos mantendo os necessários
    #    Inclui atributos de iframe para que os vídeos funcionem
    allowed_attrs = {
        "href", "src", "alt", "title", "id", "name", "style", "class",
        "width", "height",
        # atributos de iframe:
        "allow", "allowfullscreen", "frameborder", "referrerpolicy", "loading",
        # atributos de link:
        "target", "rel",
    }
    for tag in soup.find_all(True):
        attrs_to_remove = [a for a in tag.attrs if a not in allowed_attrs]
        for attr in attrs_to_remove:
            del tag.attrs[attr]

    # 7. Normalizar links (remove query strings que causam problemas)
    for a in soup.find_all("a", href=True):
        if "?" in a["href"]:
            a["href"] = a["href"].split("?")[0]

    # 8. Reconstruir (SEM prettify — não quebra layout sensível a espaços)
    clean_body = str(soup)
    clean_body = re.sub(r"\n\s*\n", "\n", clean_body)  # remove linhas em branco duplas

    final = f"{tattoo}\n{clean_body}" if tattoo else clean_body
    return final, iframes_preserved


# ==============================================================================
# 🚀  MOTOR PRINCIPAL
# ==============================================================================

def main():
    log, log_file = setup_logger()

    print("\n" + "="*60)
    print("  💎 BRASILEIRINHO ENGINE — S02 Pré-Processamento v4.1")
    print(f"  Entrada : {INPUT_DIR}")
    print(f"  Saída   : {OUTPUT_DIR}")
    print("="*60 + "\n")

    # Verificar entrada
    if not INPUT_DIR.exists():
        log(f"INPUT_DIR não encontrado: {INPUT_DIR}", "ERROR")
        log("Execute S01 antes deste script.", "ERROR")
        sys.exit(1)

    # Verificar que 01 não está sendo modificada (é read-only)
    test_file = next(INPUT_DIR.glob("*.html"), None)
    if test_file and os.access(test_file, os.W_OK):
        log("ATENÇÃO: 01-extracted-htmls NÃO está em read-only!", "WARN")
        log("Execute: chmod -R a-w /beng/pipeline/01-extracted-htmls/en-US", "WARN")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(INPUT_DIR.glob("*.html"))
    if not files:
        log("Nenhum arquivo .html encontrado no INPUT_DIR.", "ERROR")
        sys.exit(1)

    log(f"Arquivos encontrados: {len(files)}", "INFO")
    print()

    processed   = 0
    skipped     = 0
    errors      = 0
    total_iframes = 0

    for in_path in files:
        out_path = OUTPUT_DIR / in_path.name

        # Idempotência
        if out_path.exists():
            skipped += 1
            continue

        try:
            raw = in_path.read_text(encoding="utf-8")
            clean, n_iframes = clean_html(raw)
            out_path.write_text(clean, encoding="utf-8")

            processed     += 1
            total_iframes += n_iframes

            if processed % 100 == 0:
                log(f"{processed} arquivos processados...", "INFO")

        except Exception as e:
            log(f"Erro em {in_path.name}: {e}", "ERROR")
            errors += 1

    # Summary
    print()
    print("="*60)
    print("  📊 PRÉ-PROCESSAMENTO CONCLUÍDO")
    print("="*60)
    print(f"  Total na entrada   : {len(files)}")
    print(f"  ✅ Processados      : {processed}")
    print(f"  ⏭️  Já existiam      : {skipped}  (idempotência)")
    print(f"  🎬 iframes preserv. : {total_iframes}  (YouTube/Vimeo)")
    print(f"  ❌ Erros            : {errors}")
    print(f"  📁 Saída            : {OUTPUT_DIR}")
    print(f"  📋 Log              : {log_file}")
    print("="*60)

    if errors > 0:
        print(f"\n  ⚠️  {errors} erro(s) — verifique o log antes de avançar.")
        sys.exit(1)
    else:
        print(f"\n  🌿 Pré-processamento limpo. Próximo: python3 S03_build_csl.py")
        sys.exit(0)


if __name__ == "__main__":
    main()
