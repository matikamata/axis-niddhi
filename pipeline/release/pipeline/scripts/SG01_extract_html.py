#!/usr/bin/env python3
# /beng-fut/pipeline/scripts/SG01_extract_html.py
"""
💎 BRASILEIRINHO ENGINE — SCRIPT S01
=====================================
Nome:       Extração Global SRO (Source of Record)
Versão:     3.2  —  AXIS-NIDDHI V5.2.3 (CLS Integration)
Autor:      Lead SRE + Claude Sonnet 4.6
Data:       2026-03-08

DELTA vs V3.1:
  ★ [CLS] Calcula SHA-256 de cada HTML extraído
  ★ [CLS] Grava origin.source_html_sha256 + origin.extracted_at
          no identity.json via cls_tools (se entry CSL já existir)
  ★ cls_tools import é optional — se não encontrado, extração continua
    normalmente sem CLS (graceful degradation)

POSIÇÃO NA SEQUÊNCIA:
  Step 4 — Roda APÓS reset v12.1 e S00_migrate_ptbr.
  Lê o CSV operacional + banco MySQL (beng_wp_21) →
  gera 01-extracted-htmls/en-US/ com nomenclatura canônica imutável.

PRINCÍPIO SRO (Source of Record):
  A pasta 01-extracted-htmls/en-US/ é READ-ONLY após extração.
  NÃO edite os arquivos gerados. Eles são o Tesouro Original.
"""

import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pymysql

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
# Adiciona /beng/pipeline/scripts ao path se necessário
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import (
    BASE_DIR,
    LOG_DIR,
    DIR_01_EXTRACTED,
    DIR_09_CSL,
    PDPN_CSV,
    DB_CONFIG,
    SOURCE_LANG,
)

OUTPUT_DIR = DIR_01_EXTRACTED / SOURCE_LANG   # /beng/pipeline/01-extracted-htmls/en-US

# CLS integration — graceful degradation se cls_tools não disponível
try:
    from cls_tools import inject_lineage_stub, get_lineage
    _CLS_AVAILABLE = True
except ImportError:
    _CLS_AVAILABLE = False

# ==============================================================================
# 🛠️  UTILITÁRIOS
# ==============================================================================

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"S01_extract_{ts}.log"

    def log(msg, level="INFO"):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌"}
        icon  = icons.get(level, "  ")
        ts_   = datetime.now().strftime("%H:%M:%S")
        line  = f"[{ts_}] [{level}] {msg}"
        print(f"{icon}  {msg}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    return log, log_file


def setup_environment(log):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log(f"Diretório SRO: {OUTPUT_DIR}", "INFO")


def detect_table_prefix(conn):
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE '%_posts'")
        result = cursor.fetchone()
        if result:
            table_name = list(result.values())[0]
            return table_name.replace("posts", "")
    sys.exit("❌ Tabela de posts não encontrada no banco.")


def clean_slug(slug: str) -> str:
    """Sanitiza o slug para nome de arquivo seguro (Linux/Windows)."""
    if not isinstance(slug, str):
        return "unknown-slug"
    slug = re.sub(r"[^a-zA-Z0-9\-]", "", slug)
    return slug.lower() or "unknown-slug"


def sha256_text(text: str) -> str:
    """Calcula SHA-256 de string em UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def update_cls_origin(pdpn: str, filename: str, sha256: str, extracted_at: str, log) -> None:
    """
    [CLS V5.2.3] Atualiza origin.source_html_sha256 + origin.extracted_at
    no identity.json da entry CSL correspondente ao PDPN.
    Só age se: CLS disponível, entry existe, lineage já injetado.
    Silencioso se entry ainda não existe (SG03 cria depois).
    """
    if not _CLS_AVAILABLE:
        return

    import json
    identity_path = DIR_09_CSL / pdpn / "meta" / "identity.json"
    if not identity_path.exists():
        return  # Entry ainda não existe — SG03 cria depois

    try:
        data = json.loads(identity_path.read_text(encoding="utf-8"))
        lin = data.get("lineage")
        if lin is None:
            return  # Sem lineage — não forçar aqui

        changed = False
        origin = lin.setdefault("origin", {})

        if not origin.get("source_html_sha256"):
            origin["source_html_sha256"] = sha256
            changed = True
        if not origin.get("source_html"):
            origin["source_html"] = filename
            changed = True
        if not origin.get("extracted_at"):
            origin["extracted_at"] = extracted_at
            changed = True

        if changed:
            from pipeline_utils import atomic_write_json
            atomic_write_json(identity_path, data)
            log(f"  [CLS] {pdpn}: origin atualizado (sha256={sha256[:12]}...)", "INFO")

    except Exception as e:
        log(f"  [CLS] {pdpn}: aviso ao atualizar origin — {e}", "WARN")


def generate_tattoo(row: dict) -> str:
    """
    Gera o cabeçalho canônico (Anti-Amnésia) de cada arquivo extraído.
    Este comentário é a 'Tatuagem' — identificação permanente do artefato.
    NÃO remova nem edite este bloco nos arquivos gerados.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!--
\U0001f4a1 BRASILEIRINHO ENGINE - CANONICAL SOURCE ARTIFACT
===================================================
Fin-dex:      {row['Fin-dex']}
PD#PN:        {row['PD#PN']}
Original-Slug:{row['Slug_Derived']}
Source-ID:    {row['id_10WEB.io']}
Language:     {SOURCE_LANG}
Extracted-At: {now}
Origin:       MySQL / {DB_CONFIG['database']}
===================================================
DO NOT EDIT THIS FILE MANUALLY. THIS IS THE TREASURE.
-->
"""

# ==============================================================================
# 🚀  MOTOR PRINCIPAL
# ==============================================================================

def main():
    log, log_file = setup_logger()

    print("\n" + "="*60)
    print("  💎 BRASILEIRINHO ENGINE — S01 Extração Global v3.1")
    print(f"  DB:  {DB_CONFIG['database']}  |  Saída: {OUTPUT_DIR}")
    print("="*60 + "\n")

    setup_environment(log)

    # ------------------------------------------------------------------
    # 1. Carregar Irmã Operacional (CSV)
    # ------------------------------------------------------------------
    if not PDPN_CSV.exists():
        log(f"CSV operacional não encontrado: {PDPN_CSV}", "ERROR")
        log("Execute S00b (genesis_twins) para gerar o CSV antes deste script.", "ERROR")
        sys.exit(1)

    try:
        df = pd.read_csv(PDPN_CSV, sep=";", encoding="utf-8", dtype=str)
        # Filtro de segurança: só posts com ID e PD#PN válidos
        df = df[df["id_10WEB.io"].notna() & (df["id_10WEB.io"].str.strip() != "")]
        log(f"CSV carregado: {len(df)} posts mapeados para extração.", "INFO")
    except Exception as e:
        log(f"Erro ao ler CSV: {e}", "ERROR")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Conectar ao Banco
    # ------------------------------------------------------------------
    db_conn_config = {**DB_CONFIG, "cursorclass": pymysql.cursors.DictCursor}
    try:
        conn   = pymysql.connect(**db_conn_config)
        prefix = detect_table_prefix(conn)
        table  = f"{prefix}posts"
        log(f"MySQL conectado. DB: {DB_CONFIG['database']} | Prefixo: '{prefix}'", "OK")
    except Exception as e:
        log(f"Falha na conexão MySQL: {e}", "ERROR")
        log(f"DB esperado: {DB_CONFIG['database']} | Usuário: {DB_CONFIG['user']}", "ERROR")
        log("Verifique se o reset v12.1 foi executado com sucesso.", "ERROR")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 3. Extração em loop
    # ------------------------------------------------------------------
    success  = 0
    skipped  = 0
    errors   = 0
    existing = 0

    log(f"Iniciando extração de {len(df)} posts...", "INFO")
    print()

    with conn.cursor() as cursor:
        for _, row in df.iterrows():
            try:
                wp_id  = int(row["id_10WEB.io"])
                findex = str(row["Fin-dex"]).zfill(4)
                pdpn   = str(row["PD#PN"]).strip()
                slug   = clean_slug(str(row.get("Slug_Derived", "")))

                # Nome canônico: [Fin-dex]__[PD#PN]__[slug].html
                filename = f"{findex}__{pdpn}__{slug}.html"
                filepath = OUTPUT_DIR / filename

                # Idempotência: pular se já existir
                if filepath.exists():
                    existing += 1
                    continue

                # Buscar conteúdo no banco
                cursor.execute(
                    f"SELECT post_content, post_title FROM {table} WHERE ID = %s",
                    (wp_id,)
                )
                result = cursor.fetchone()

                if result:
                    content  = result["post_content"] or ""
                    tattoo   = generate_tattoo(row)
                    final    = tattoo + "\n" + content

                    filepath.write_text(final, encoding="utf-8")
                    success += 1

                    # ── [CLS V5.2.3] Registrar SHA-256 da origem ──────────
                    extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    update_cls_origin(
                        pdpn=pdpn,
                        filename=filename,
                        sha256=sha256_text(final),
                        extracted_at=extracted_at,
                        log=log,
                    )

                    if success % 100 == 0:
                        log(f"{success} artefatos extraídos...", "INFO")
                else:
                    log(f"ID {wp_id} ({pdpn}) não encontrado no banco.", "WARN")
                    skipped += 1

            except Exception as e:
                log(f"Falha em Fin-dex {row.get('Fin-dex', '?')}: {e}", "ERROR")
                errors += 1

    conn.close()

    # ------------------------------------------------------------------
    # 4. Summary
    # ------------------------------------------------------------------
    total = success + skipped + errors + existing
    print()
    print("="*60)
    print("  📊 EXTRAÇÃO CONCLUÍDA")
    print("="*60)
    print(f"  Total processados  : {total}")
    print(f"  ✅ Extraídos        : {success}")
    print(f"  ⏭️  Já existiam      : {existing}  (idempotência)")
    print(f"  ⚠️  Não encontrados  : {skipped}")
    print(f"  ❌ Erros            : {errors}")
    print(f"  📁 Saída            : {OUTPUT_DIR}")
    print(f"  📋 Log              : {log_file}")
    print("="*60)

    if errors > 0:
        print(f"\n  ⚠️  {errors} erro(s) — verifique o log antes de avançar.")
    else:
        print(f"\n  🌿 Extração limpa. Próximo: python3 S02_preprocess_v4_1_iframes.py")
    print()

    # Blinda a pasta SRO em read-only (proteção do Tesouro)
    try:
        os.system(f"chmod -R a-w '{OUTPUT_DIR}'")
        log(f"Pasta SRO blindada em read-only: {OUTPUT_DIR}", "OK")
    except Exception as e:
        log(f"Aviso: não foi possível bloquear a pasta SRO: {e}", "WARN")

    sys.exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()
