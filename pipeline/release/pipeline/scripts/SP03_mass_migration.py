"""
💎 BRASILEIRINHO ENGINE — S05 (ex-Script 10 Fase 5)
============================================
Nome:       Mass Migration → Schema V3.1
Sequência:  S05 → roda após S04 (dry-run primeiro, depois --apply)
Revisado:   2026-02-27 (Genesis v2.0)
Versão:     1.1 (Hash Consistency Fix)                   # [20260220] v1.0 → v1.1
Autor:      Gegên (SRE)
Data:       2026-01-30
Revisado:   2026-02-20 por Claude Sonnet 4.6             # [20260220] adicionado

OBJETIVO:
Aplicar o molde do Golden Sample (SI.AA.005) a todos os posts da CSL.
Gera identity.json (v3.1), content.html (fragmento) e semantic.json (vazio).

REGRAS DE OURO (ANTI-PATTERNS):
1. Não interpretar.
2. Não adicionar CSS/JS.
3. Não inferir dados.
4. HTML deve ser fragmento puro.

MUDANÇAS V1.1:                                           # [20260220] adicionado
- Substituída calculate_sha256_string() por              # [20260220] adicionado
  calculate_sha256_file() para consistência com          # [20260220] adicionado
  o restante do pipeline (hash sempre em bytes/rb).      # [20260220] adicionado
- Hash calculado APÓS escrita do arquivo no disco,       # [20260220] adicionado
  garantindo que o valor registrado reflita o            # [20260220] adicionado
  conteúdo real persistido.                              # [20260220] adicionado
- Removido bloco incorreto inserido no início de         # [20260220] adicionado
  process_post() que usava variáveis ainda indefinidas.  # [20260220] adicionado
"""

import os
import json
import hashlib
import argparse
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

# ==============================================================================
# ⚙️ CONFIGURAÇÃO — via config.py canônico (hardcode removido V5.1)
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DIR_09_CSL, LOG_DIR

CSL_DIR = DIR_09_CSL

# ==============================================================================
# 🛠️ UTILITÁRIOS
# ==============================================================================

def setup_logger(mode):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"phase5_migration_{mode}_{timestamp}.log"
    
    def log(msg, status="INFO"):
        # Emojis para leitura visual rápida
        icon = "ℹ️"
        if status == "OK": icon = "✅"
        elif status == "WARN": icon = "⚠️"
        elif status == "ERROR": icon = "❌"
        elif status == "SKIP": icon = "⏭️"
        elif status == "DRY": icon = "🔍"
        
        print(f"{icon} [{status}] {msg}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{status}] {msg}\n")
    return log

# [20260220] calculate_sha256_string() REMOVIDA. Substituída por calculate_sha256_file()
# abaixo, que lê o arquivo em bytes (rb) — padrão consistente com Scripts 09 e 12.
def calculate_sha256_file(file_path):                    # [20260220] função nova
    """Calcula SHA-256 do arquivo em bytes — padrão do pipeline."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def clean_html_fragment(raw_html):
    """
    Transforma HTML em fragmento puro conforme Golden Sample.
    Remove wrappers <html>, <head>, <body>.
    Remove <script>, <style>.
    NÃO altera o texto <p>.
    """
    # Remove comentários antigos para reinserir o canônico limpo
    content = re.sub(r'<!--.*?-->', '', raw_html, flags=re.DOTALL)
    
    # Remove wrappers de documento completo se existirem
    content = re.sub(r'<!DOCTYPE.*?>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<html.*?>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<head>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<body.*?>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</body>', '', content, flags=re.IGNORECASE)
    
    # Remove scripts e styles (Anti-Pattern: HTML deve ser dados, não comportamento)
    content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    return content.strip()

def generate_canonical_comment(pdpn, extraction_date):
    """Gera o cabeçalho HTML canônico."""
    return f"""<!--
Canonical CSL Artifact
Derived from PureDhamma.net SRO
PD#PN: {pdpn}
Extraction: {extraction_date}
Integrity: PENDING_CALCULATION
-->"""

# ==============================================================================
# 🚀 MOTOR DE MIGRAÇÃO
# ==============================================================================

def process_post(folder, log, apply_changes):
    pdpn = folder.name
    
    # Caminhos
    meta_dir = folder / "meta"
    source_en_dir = folder / "source" / "en-US"
    
    old_json_path = meta_dir / "identity.json"
    html_path = source_en_dir / "content.html"
    semantic_path = meta_dir / "semantic.json"

    # Validação Básica
    if not old_json_path.exists():
        log(f"{pdpn} - Identity ausente", "ERROR")
        return False
    if not html_path.exists():
        log(f"{pdpn} - HTML ausente", "ERROR")
        return False

    try:
        # 1. Ler Dados Atuais
        with open(old_json_path, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        with open(html_path, 'r', encoding='utf-8') as f:
            raw_html = f.read()

        # 2. Preparar HTML (Fragmento Puro)
        clean_body = clean_html_fragment(raw_html)
        
        # Preservar data de extração original se existir, senão usa agora
        extraction_date = old_data.get("sro", {}).get("extraction_date", get_utc_now())
        
        canonical_comment = generate_canonical_comment(pdpn, extraction_date)
        final_html = f"{canonical_comment}\n\n{clean_body}"

        # 3. Preparar Identity JSON (Schema 3.1 - Golden Sample)
        # Extração segura de dados antigos
        findex = old_data.get("identity", {}).get("findex", old_data.get("findex", "0000"))
        slug = old_data.get("identity", {}).get("slug_root", old_data.get("slug_en", "unknown"))
        section = pdpn.split('.')[0] if '.' in pdpn else "MS"
        
        # Títulos: Tenta preservar se já existir, senão null (conforme Golden Sample)
        title_en = old_data.get("titles", {}).get("en", None)
        
        # SRO Data
        wp_id = old_data.get("sro", {}).get("original_wp_id", None)

        # 4. Preparar Semantic JSON (Vazio - Anti-Pattern 6)
        new_semantic = {
            "schema_version": "1.0",
            "pdpn": pdpn,
            "inventory": {}
        }

        # 5. Execução (Dry Run ou Apply)
        if not apply_changes:
            # [20260220] No dry-run, calculamos o hash da string em memória apenas
            # para exibir uma prévia — sem escrever no disco.
            preview_hash = hashlib.sha256(final_html.encode('utf-8')).hexdigest()
            log(f"{pdpn} - Seria atualizado para Schema 3.1. Hash preview: {preview_hash[:8]}...", "DRY")
            return True
        else:
            # Backup antes de escrever (Safety First)
            shutil.copy(old_json_path, old_json_path.with_suffix('.json.bak'))
            
            # [20260220] Escrever HTML PRIMEIRO — o hash é calculado do arquivo
            # real no disco, garantindo consistência com o restante do pipeline.
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(final_html)
            
            # [20260220] Hash calculado do arquivo recém-escrito (em bytes/rb),
            # substituindo calculate_sha256_string() que operava em memória/UTF-8.
            new_hash = calculate_sha256_file(html_path)

            # Montar Identity com o hash real do arquivo persistido
            new_identity = {                              # [20260220] movido para após escrita do HTML
                "schema_version": "3.1",
                "last_updated_utc": get_utc_now(),
                
                "identity": {
                    "pdpn": pdpn,
                    "findex": findex,
                    "slug_root": slug,
                    "section_code": section
                },
                
                "sro": {
                    "source": "PureDhamma.net",
                    "author": "Lal A.",
                    "original_url": f"https://puredhamma.net/?p={wp_id}" if wp_id else None, # Fallback seguro
                    "original_wp_id": wp_id,
                    "extraction_date": extraction_date
                },
                
                "titles": {
                    "en": title_en,
                    "en_source": "legacy_migration",
                    "pt": None,
                    "pt_source": None
                },
                
                "artifacts": {
                    "en-US": {
                        "status": "canonical",
                        "file_path": "source/en-US/content.html",
                        "integrity_sha256": new_hash  # [20260220] hash do arquivo real
                    },
                    "pt-BR": {
                        "status": "missing", # Reset forçado conforme instrução
                        "file_path": "source/pt-BR/content.html",
                        "integrity_sha256": None
                    }
                }
            }

            # Escrever Identity
            with open(old_json_path, 'w', encoding='utf-8') as f:
                json.dump(new_identity, f, indent=2, ensure_ascii=False)
                
            # Escrever Semantic
            with open(semantic_path, 'w', encoding='utf-8') as f:
                json.dump(new_semantic, f, indent=2, ensure_ascii=False)
                
            log(f"{pdpn} - Migrado com sucesso.", "OK")
            return True

    except Exception as e:
        log(f"{pdpn} - Falha crítica: {e}", "ERROR")
        return False

def main():
    parser = argparse.ArgumentParser(description="Mass Migration to Golden Sample (CSL v1.0)")
    parser.add_argument("--apply", action="store_true", help="Aplica as mudanças no disco. Sem isso, roda em DRY-RUN.")
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY_RUN"
    log = setup_logger(mode)
    
    log(f"=== INICIANDO MIGRAÇÃO FASE 5 ({mode}) ===", "INFO")
    log(f"Diretório Base: {CSL_DIR}", "INFO")
    
    if not CSL_DIR.exists():
        log("Diretório CSL não encontrado.", "ERROR")
        return

    # Filtro PDPN: ignora meta/, relatorio_csl.txt, etc. (V5.1)
    _PDPN_RE = re.compile(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$')
    folders = sorted([f for f in CSL_DIR.iterdir()
                      if f.is_dir() and _PDPN_RE.match(f.name)])
    log(f"Total de pastas encontradas: {len(folders)}", "INFO")

    success_count = 0
    error_count = 0

    for folder in folders:
        if process_post(folder, log, args.apply):
            success_count += 1
        else:
            error_count += 1

    log("="*50, "INFO")
    log(f"FIM DA EXECUÇÃO ({mode})", "INFO")
    log(f"Sucessos: {success_count}", "INFO")
    log(f"Erros: {error_count}", "INFO")
    if not args.apply:
        log("Para aplicar as mudanças, rode com --apply", "INFO")

if __name__ == "__main__":
    main()
