#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SCRIPT 00
=====================================
Nome:       Auditoria Cirúrgica SQL vs CSL (pt-BR)
Versão:     1.0
Autores:    Vayo + Akasa (sugestão técnica)
Data:       2026-02-23

OBJETIVO:
Cruzar o SQL Dump (fonte da verdade absoluta) com os 29 posts traduzidos
na 09-csl/*/source/pt-BR/content.html para identificar:

  A) Posts traduzidos que perderam <iframe> (vídeos removidos pelo script 02 antigo)
  B) Posts traduzidos que estão íntegros (podem ser reutilizados sem gastar cota DeepL)
  C) Posts ainda não traduzidos que têm <iframe> no SQL (prioridade de tradução)

LÓGICA:
  - NÃO usa a Pasta 01 como referência (pode estar parcialmente corrompida)
  - Extrai os iframes DIRETAMENTE do SQL Dump
  - Compara com o que existe em pt-BR na CSL

OUTPUT:
  - Relatório no terminal
  - 3 arquivos CSV em /pipeline/metadata/
      → auditoria_corrompidos.csv     (posts pt-BR com iframe perdido)
      → auditoria_integros.csv        (posts pt-BR íntegros — reutilizar)
      → auditoria_pendentes_youtube.csv (posts sem pt-BR que têm YouTube no SQL)
"""

import os
import re
import csv
import json
from pathlib import Path
from datetime import datetime

# ==============================================================================
# ⚙️ CONFIGURAÇÃO — ajuste os paths se necessário
# ==============================================================================
BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR  = BASE_DIR / "09-csl"
SQL_PATH = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/runtime_wp/tenweb_backup_db.sql")
OUTPUT_DIR = BASE_DIR / "metadata"
LOG_DIR    = BASE_DIR / "logs"

# ==============================================================================
# 🛠️ UTILITÁRIOS
# ==============================================================================

def setup_log():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"auditoria_sql_vs_csl_{ts}.log"
    lines = []
    def log(msg, level="INFO"):
        icon = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌"}.get(level, "•")
        full = f"{icon} [{level}] {msg}"
        print(full)
        lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {full}\n")
    def flush():
        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"\n📄 Log salvo em: {log_path}")
    return log, flush


def extract_iframes_from_sql(sql_path: Path) -> dict:
    """
    Versão Akasa-Shield (Brute Force)
    Lê o SQL como um fluxo contínuo para capturar IDs e iframes 
    mesmo em arquivos de linha única (TenWeb/phpMyAdmin).
    """
    result = {}
    if not sql_path.exists():
        print(f"❌ SQL não encontrado: {sql_path}")
        return result
    
    print(f"📖 Lendo SQL Dump em modo 'Brute Force' para quebrar o monobloco...")
    
    try:
        # Lemos o arquivo inteiro. Com 315MB, o sistema aguenta bem na RAM.
        with open(sql_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        # Esta regex é a nossa 'escavadeira':
        # 1. Procura por (ID, 
        # 2. Pula o autor, data, etc.
        # 3. Procura o conteúdo que contenha youtube.com/embed
        # 4. Captura o ID e o link
        matches = re.findall(r"\((\d+),[^,]+,[^,]+,[^,]+,'([^']*(?:youtube\.com/embed)[^']*)'", content)
        
        for post_id, post_content in matches:
            # Extrai apenas os códigos dos vídeos do YouTube
            urls = re.findall(r'youtube\.com/embed/([^"\'\?& >]+)', post_content)
            if urls:
                result[int(post_id)] = [f"https://www.youtube.com/embed/{u}" for u in urls]

    except Exception as e:
        print(f"❌ Erro na extração Akasa-Shield: {e}")
        
    print(f"    → Sucesso! Posts com YouTube detectados no SQL: {len(result)}")
    return result
    
    print(f"📖 Lendo SQL Dump: {sql_path} ({sql_path.stat().st_size / 1024 / 1024:.1f} MB)...")
    
    # Padrão para encontrar linhas de INSERT de posts com conteúdo
    # Captura: ID do post e o conteúdo HTML completo
    # O SQL do WordPress tem o formato:
    # INSERT INTO `wp_posts` VALUES (ID, post_author, post_date, ..., post_content, ...)
    
    try:
        with open(sql_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler SQL: {e}")
        return result
    
    # Encontrar todas as linhas de INSERT em wp_posts
    # Cada linha começa com o ID do post
    # Usamos regex para capturar ID e buscar iframes no contexto
    
    # Estratégia: encontrar blocos com youtube.com/embed
    # e extrair o Source-ID (ID do WP) associado
    
    # Padrão para extrair post rows da tabela wp_posts
    # INSERT INTO `wp_posts` VALUES (ID, ...)
    
    # Dividir por INSERT INTO wp_posts para processar em blocos
    blocks = re.split(r"INSERT INTO `wp_posts` VALUES", content)
    
    iframe_pattern = re.compile(
        r'<iframe[^>]+src=["\']([^"\']*youtube\.com/embed[^"\']*)["\'][^>]*>',
        re.IGNORECASE
    )
    
    # Para cada bloco de VALUES, extrair todas as rows
    # Cada row começa com (ID,
    row_pattern = re.compile(r'\((\d+),', re.MULTILINE)
    
    posts_found = 0
    posts_with_yt = 0
    
    for block in blocks[1:]:  # pula o primeiro bloco (antes do primeiro INSERT)
        # Encontrar todos os IDs de posts neste bloco
        # e verificar se cada segmento tem iframe
        
        # Dividir o bloco em rows individuais
        # Cada row começa com (ID,
        rows = re.split(r'(?=\(\d+,)', block)
        
        for row in rows:
            id_match = re.match(r'\((\d+),', row)
            if not id_match:
                continue
            
            post_id = int(id_match.group(1))
            posts_found += 1
            
            # Buscar iframes nesta row
            iframes = iframe_pattern.findall(row)
            
            if iframes:
                result[post_id] = iframes
                posts_with_yt += 1
    
    print(f"    → Posts encontrados no SQL: {posts_found}")
    print(f"    → Posts com YouTube iframe: {posts_with_yt}")
    print(f"    → IDs com YouTube: {sorted(result.keys())[:10]}{'...' if len(result) > 10 else ''}")
    
    return result


def load_csl_index(csl_dir: Path, log) -> dict:
    """
    Lê todos os posts da CSL e retorna índice por Source-ID.
    
    Retorna: dict { source_id (int) -> {
        'pdpn': str,
        'folder': Path,
        'has_pt': bool,
        'pt_path': Path | None,
        'pt_has_iframe': bool,
        'en_path': Path | None,
        'source_id': int
    }}
    """
    index = {}
    
    if not csl_dir.exists():
        log(f"CSL não encontrada: {csl_dir}", "ERROR")
        return index
    
    folders = sorted([f for f in csl_dir.iterdir() if f.is_dir()])
    log(f"Analisando {len(folders)} pastas na CSL...")
    
    iframe_pattern = re.compile(
        r'<iframe[^>]+src=["\']([^"\']*youtube\.com/embed[^"\']*)["\'][^>]*>',
        re.IGNORECASE
    )
    source_id_pattern = re.compile(r'Source-ID:\s+(\d+)')
    
    for folder in folders:
        pdpn = folder.name
        en_path = folder / "source" / "en-US" / "content.html"
        pt_path = folder / "source" / "pt-BR" / "content.html"
        json_path = folder / "meta" / "identity.json"
        
        # Extrair Source-ID
        source_id = None
        
        # Tentar via identity.json primeiro
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    identity = json.load(f)
                # Suporta Schema V2 e V3
                source_id = (
                    identity.get("sro", {}).get("wp_id") or
                    identity.get("source_id") or
                    identity.get("wp_id")
                )
                if source_id:
                    source_id = int(source_id)
            except Exception:
                pass
        
        # Fallback: extrair do header do en-US HTML
        if not source_id and en_path.exists():
            try:
                with open(en_path, 'r', encoding='utf-8') as f:
                    head = f.read(1500)
                match = source_id_pattern.search(head)
                if match:
                    source_id = int(match.group(1))
            except Exception:
                pass
        
        if not source_id:
            log(f"Source-ID não encontrado para {pdpn} — pulando", "WARN")
            continue
        
        # Verificar pt-BR
        has_pt = pt_path.exists()
        pt_has_iframe = False
        
        if has_pt:
            try:
                with open(pt_path, 'r', encoding='utf-8') as f:
                    pt_content = f.read()
                pt_has_iframe = bool(iframe_pattern.search(pt_content))
            except Exception:
                pass
        
        index[source_id] = {
            'pdpn': pdpn,
            'folder': folder,
            'has_pt': has_pt,
            'pt_path': pt_path if has_pt else None,
            'pt_has_iframe': pt_has_iframe,
            'en_path': en_path if en_path.exists() else None,
            'source_id': source_id
        }
    
    log(f"CSL indexada: {len(index)} posts com Source-ID")
    return index


def run_audit():
    log, flush_log = setup_log()
    
    log("=" * 60)
    log("💎 AUDITORIA CIRÚRGICA SQL vs CSL (pt-BR)")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 60)
    
    # ── FASE 1: Extrair iframes do SQL ──────────────────────────
    log("")
    log("FASE 1 — Extraindo iframes do SQL Dump...", "INFO")
    sql_youtube = extract_iframes_from_sql(SQL_PATH)
    
    if not sql_youtube:
        log("AVISO: Nenhum iframe encontrado no SQL. Verifique o path.", "WARN")
        log("Tentando método alternativo (grep por linha)...", "INFO")
        # Método alternativo: grep linha a linha
        try:
            with open(SQL_PATH, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    if 'youtube.com/embed' in line:
                        # Extrair IDs da linha
                        ids = re.findall(r'^\((\d+),', line.strip())
                        for id_str in ids:
                            sql_youtube[int(id_str)] = ['youtube_detected_line_method']
        except Exception as e:
            log(f"Método alternativo falhou: {e}", "ERROR")
    
    log(f"Total Source-IDs com YouTube no SQL: {len(sql_youtube)}", "OK")
    
    # ── FASE 2: Indexar CSL ──────────────────────────────────────
    log("")
    log("FASE 2 — Indexando CSL...", "INFO")
    csl_index = load_csl_index(CSL_DIR, log)
    
    # ── FASE 3: Cruzamento ───────────────────────────────────────
    log("")
    log("FASE 3 — Cruzando SQL vs CSL...", "INFO")
    
    corrompidos    = []  # pt-BR existe mas perdeu iframe que SQL confirma
    integros       = []  # pt-BR existe e não tinha iframe no SQL (ok)
    pendentes_yt   = []  # sem pt-BR e SQL confirma que tem iframe (prioridade)
    pendentes_sem  = []  # sem pt-BR e sem iframe (tradução normal)
    sem_source_id  = []  # não foi possível cruzar
    
    for source_id, entry in csl_index.items():
        pdpn = entry['pdpn']
        has_sql_iframe = source_id in sql_youtube
        has_pt = entry['has_pt']
        pt_has_iframe = entry['pt_has_iframe']
        
        if has_pt:
            if has_sql_iframe and not pt_has_iframe:
                # CORROMPIDO: SQL diz que tinha iframe, pt-BR não tem
                corrompidos.append({
                    'PD#PN': pdpn,
                    'Source-ID': source_id,
                    'SQL_YouTube_URLs': ' | '.join(sql_youtube.get(source_id, [])),
                    'Status': 'CORROMPIDO — iframe perdido',
                    'Ação': 'RETRADUZIIR via DeepL'
                })
            else:
                # ÍNTEGRO: pt-BR existe e SQL não exigia iframe (ou pt-BR já tem iframe)
                integros.append({
                    'PD#PN': pdpn,
                    'Source-ID': source_id,
                    'pt_tem_iframe': pt_has_iframe,
                    'sql_tinha_iframe': has_sql_iframe,
                    'Status': 'ÍNTEGRO',
                    'Ação': 'REUTILIZAR — sem custo DeepL'
                })
        else:
            if has_sql_iframe:
                # Ainda não traduzido, mas tem YouTube — prioridade
                pendentes_yt.append({
                    'PD#PN': pdpn,
                    'Source-ID': source_id,
                    'SQL_YouTube_URLs': ' | '.join(sql_youtube.get(source_id, [])),
                    'Status': 'PENDENTE com YouTube',
                    'Ação': 'TRADUZIR — prioridade (tem vídeo)'
                })
            else:
                pendentes_sem.append({
                    'PD#PN': pdpn,
                    'Source-ID': source_id,
                    'Status': 'PENDENTE sem YouTube',
                    'Ação': 'TRADUZIR — padrão'
                })
    
    # Posts no SQL com YouTube que não estão na CSL
    csl_source_ids = set(csl_index.keys())
    sql_only = {sid: urls for sid, urls in sql_youtube.items() if sid not in csl_source_ids}
    
    # ── FASE 4: Relatório Terminal ───────────────────────────────
    log("")
    log("=" * 60)
    log("📊 RELATÓRIO FINAL")
    log("=" * 60)
    log(f"  Posts CSL indexados:              {len(csl_index)}")
    log(f"  Posts com YouTube no SQL:         {len(sql_youtube)}")
    log("")
    log(f"  ❌ CORROMPIDOS (pt-BR sem iframe): {len(corrompidos)}")
    for c in corrompidos:
        log(f"      → {c['PD#PN']} (Source-ID: {c['Source-ID']})", "WARN")
    log("")
    log(f"  ✅ ÍNTEGROS (reutilizar sem custo): {len(integros)}")
    log("")
    log(f"  ⏳ PENDENTES com YouTube (prioridade): {len(pendentes_yt)}")
    for p in pendentes_yt[:10]:
        log(f"      → {p['PD#PN']} (Source-ID: {p['Source-ID']})", "INFO")
    if len(pendentes_yt) > 10:
        log(f"      ... e mais {len(pendentes_yt) - 10}")
    log("")
    log(f"  ⏳ PENDENTES sem YouTube: {len(pendentes_sem)}")
    log("")
    
    # Estimativa de custo DeepL
    total_retraducao = len(corrompidos) + len(pendentes_yt) + len(pendentes_sem)
    log(f"  📈 Total que precisa de tradução DeepL: {total_retraducao}")
    log(f"      → Corrompidos:       {len(corrompidos)}")
    log(f"      → Pendentes c/ YT:   {len(pendentes_yt)}")
    log(f"      → Pendentes s/ YT:   {len(pendentes_sem)}")
    log(f"  💰 Cota poupada (íntegros reutilizáveis): {len(integros)} posts")
    
    if sql_only:
        log("")
        log(f"  ⚠️  Source-IDs no SQL com YouTube mas SEM pasta CSL: {len(sql_only)}", "WARN")
        for sid in list(sql_only.keys())[:5]:
            log(f"      → Source-ID {sid}", "WARN")
    
    # ── FASE 5: Salvar CSVs ──────────────────────────────────────
    log("")
    log("FASE 5 — Salvando CSVs...", "INFO")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    def save_csv(filename, rows, fieldnames):
        path = OUTPUT_DIR / filename
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        log(f"  → Salvo: {path}", "OK")
    
    if corrompidos:
        save_csv(
            "auditoria_corrompidos.csv",
            corrompidos,
            ['PD#PN', 'Source-ID', 'SQL_YouTube_URLs', 'Status', 'Ação']
        )
    
    if integros:
        save_csv(
            "auditoria_integros.csv",
            integros,
            ['PD#PN', 'Source-ID', 'pt_tem_iframe', 'sql_tinha_iframe', 'Status', 'Ação']
        )
    
    if pendentes_yt:
        save_csv(
            "auditoria_pendentes_youtube.csv",
            pendentes_yt,
            ['PD#PN', 'Source-ID', 'SQL_YouTube_URLs', 'Status', 'Ação']
        )
    
    # CSV consolidado de prioridades de tradução
    prioridades = (
        [{'PD#PN': r['PD#PN'], 'Source-ID': r['Source-ID'], 'Prioridade': '1-RETRADUCAO', 'Ação': r['Ação']} for r in corrompidos] +
        [{'PD#PN': r['PD#PN'], 'Source-ID': r['Source-ID'], 'Prioridade': '2-PENDENTE_YT', 'Ação': r['Ação']} for r in pendentes_yt] +
        [{'PD#PN': r['PD#PN'], 'Source-ID': r['Source-ID'], 'Prioridade': '3-PENDENTE_STD', 'Ação': r['Ação']} for r in pendentes_sem]
    )
    if prioridades:
        save_csv(
            "auditoria_fila_traducao.csv",
            prioridades,
            ['PD#PN', 'Source-ID', 'Prioridade', 'Ação']
        )
        log(f"  → Fila de tradução gerada: {len(prioridades)} posts", "OK")
    
    log("")
    log("=" * 60)
    log("✅ AUDITORIA CONCLUÍDA", "OK")
    log("=" * 60)
    log("")
    log("PRÓXIMOS PASSOS SUGERIDOS:")
    log("  1. Revisar auditoria_corrompidos.csv")
    log("  2. Rodar script 02 (V4.1) para gerar 02-preprocessed limpo")
    log("  3. Rodar script 03 para reconstruir 09-csl/en-US")
    log("  4. Copiar pt-BR ÍNTEGROS do backup para a CSL nova (sem gastar cota)")
    log("  5. Rodar 07b SOMENTE para posts em auditoria_fila_traducao.csv")
    
    flush_log()


if __name__ == "__main__":
    run_audit()
