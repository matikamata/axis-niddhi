"""
💎 BRASILEIRINHO ENGINE - SCRIPT 09 (V1.1)
==========================================
Nome:       Migração de Identidade para Schema V3.0 (Audited Edition)
Versão:     1.1
Autor:      Gegên (COO) & Sangha (com Code Review do ChatGPT)
Data:       2026-01-30

DESCRIÇÃO:
Atualiza 'identity.json' para Schema V3.0.
Diferente da V1.0, esta versão NÃO ADIVINHA dados críticos.

MELHORIAS V1.1:
1. Recalcula SHA-256 em tempo real (Zero Trust).
2. Define SRO URL como null se não souber (evita 404).
3. Registra a fonte do título (H1 vs Slug).
4. Mantém backup (.bak).
"""

import os
import json
import re
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# ==============================================================================
# ⚙️ CONFIGURAÇÃO
# ==============================================================================
BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR = BASE_DIR / "09-csl"
LOG_DIR = BASE_DIR / "logs"

# ==============================================================================
# 🛠️ UTILITÁRIOS
# ==============================================================================

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"migration_v3_audited_{timestamp}.log"
    
    def log(msg, level="INFO"):
        print(f"[{level}] {msg}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}\n")
    return log

def calculate_sha256(file_path):
    """Gera o hash SHA-256 real do arquivo no disco."""
    if not file_path.exists(): return None
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def clean_html_text(raw_html):
    """Remove tags e limpa espaços."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def extract_title_data(html_path, slug_fallback):
    """
    Tenta extrair título do H1.
    Retorna: (titulo, fonte, confianca)
    """
    if not html_path.exists():
        return (slug_fallback.replace("-", " ").title(), "inferred_from_slug", "low")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read(5000) # Lê o cabeçalho
            
            # Busca H1
            match_h1 = re.search(r"<h1.*?>(.*?)</h1>", content, re.IGNORECASE)
            if match_h1:
                return (clean_html_text(match_h1.group(1)), "extracted_h1", "high")
            
            # Se falhar, usa slug
            return (slug_fallback.replace("-", " ").title(), "inferred_from_slug", "low")
    except Exception:
        return (slug_fallback.replace("-", " ").title(), "error_fallback", "low")

def get_utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def extract_wp_id_from_html(html_path):
    """Lê Source-ID do comentário de cabeçalho (Tatuagem)."""
    if not html_path.exists(): return None
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            head = f.read(2000)
            match = re.search(r"Source-ID:\s+(\d+)", head)
            if match: return int(match.group(1))
    except: pass
    return None

# ==============================================================================
# 🚀 MOTOR DE MIGRAÇÃO
# ==============================================================================

def upgrade_to_v3_audited():
    log = setup_logger()
    log("=== 🧬 INICIANDO MIGRAÇÃO V3.0 (AUDITED) ===", "INFO")

    if not CSL_DIR.exists():
        log("Diretório CSL não encontrado.", "ERROR")
        return

    count_upgraded = 0
    count_skipped = 0
    count_error = 0

    folders = [f for f in CSL_DIR.iterdir() if f.is_dir()]
    log(f"Analisando {len(folders)} pastas...", "INFO")

    for folder in sorted(folders):
        json_path = folder / "meta" / "identity.json"
        source_en = folder / "source" / "en-US" / "content.html"
        source_pt = folder / "source" / "pt-BR" / "content.html"

        if not json_path.exists():
            log(f"Identity ausente em {folder.name}. Pulando.", "WARN")
            count_skipped += 1
            continue

        try:
            # 1. Ler JSON Atual
            with open(json_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)

            # Verifica se já é V3
            if old_data.get("schema_version") == "3.0":
                count_skipped += 1
                continue

            # 2. Backup Seguro
            shutil.copy(json_path, json_path.with_suffix('.json.bak'))

            # 3. Extração de Dados Base
            pdpn = old_data.get("pdpn", folder.name.split('_')[0])
            findex = old_data.get("findex", "0000")
            slug = old_data.get("slug_en", old_data.get("slug", "unknown"))
            
            # 4. Auditoria de Integridade (Recalcular Hash)
            hash_en = calculate_sha256(source_en)
            if not hash_en:
                log(f"Arquivo fonte EN não encontrado em {pdpn}", "ERROR")
                hash_en = "missing_file"

            # 5. Extração de Título Inteligente
            title_en, title_source, title_confidence = extract_title_data(source_en, slug)

            # 6. Construção do Schema V3
            new_data = {
                "schema_version": "3.0",
                "last_updated_utc": get_utc_now(), # atualizado por Claude Sonnet 4.6 em 20260220
                
                "identity": {
                    "pdpn": pdpn,
                    "findex": findex,
                    "slug_root": slug,
                    "section_code": pdpn.split('.')[0] if '.' in pdpn else "MS"
                },

                "sro": {
                    "source": "PureDhamma.net",
                    "url": None, # ChatGPT estava certo: não adivinhe URLs.
                    "original_wp_id": extract_wp_id_from_html(source_en),
                    "author": "Lal A."
                },

                "titles": {
                    "en": title_en,
                    "en_source": title_source, # Metadado de confiança
                    "pt": None # Honesto. Será preenchido na tradução.
                },

                "artifacts": {
                    "en-US": {
                        "status": "canonical",
                        "file_path": "source/en-US/content.html",
                        "integrity_sha256": hash_en, # Hash fresco
                        "last_audit": get_utc_now()
                    },
                    "pt-BR": {
                        "status": "machine_translated" if source_pt.exists() else "missing",
                        "file_path": "source/pt-BR/content.html",
                        "engine": "DeepL API" if source_pt.exists() else None,
                        "translated_at": get_utc_now() if source_pt.exists() else None,
                        # Se existir PT, calculamos o hash dele também
                        "integrity_sha256": calculate_sha256(source_pt) if source_pt.exists() else None
                    }
                }
            }

            # 7. Salvar
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            
            count_upgraded += 1

        except Exception as e:
            log(f"Erro crítico em {folder.name}: {e}", "ERROR")
            count_error += 1

    log("="*50, "INFO")
    log(f"MIGRAÇÃO V3.0 (AUDITED) CONCLUÍDA", "INFO")
    log(f"✅ Atualizados: {count_upgraded}", "INFO")
    log(f"⏭️ Pulados: {count_skipped}", "INFO")
    log(f"❌ Erros: {count_error}", "INFO")
    log("="*50, "INFO")

if __name__ == "__main__":
    upgrade_to_v3_audited()
