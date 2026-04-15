"""
💎 BRASILEIRINHO ENGINE - SCRIPT 08 (V5)
========================================
Nome:       Injetor WordPress (Resilient Overwrite Strategy)
Versão:     5.0 (Fallback Edition)
Autor:      Lead SRE & Sangha
Data:       2026-01-31

DESCRIÇÃO:
Injeta conteúdo traduzido no WordPress Local (Preview).

DIFERENCIAL V5 (RESILIÊNCIA):
- NÃO ABORTA se o título PT estiver ausente no JSON.
- Usa Fallback: "[PT-DRAFT] {Título EN}" para permitir o preview do conteúdo.
- Mantém a validação de Source-ID para garantir sobrescrita correta.

SEGURANÇA:
- Idempotente.
- Não cria posts fantasmas (exige Source-ID).
"""

import os
import csv
import json
import requests
import base64
import re
import time
from pathlib import Path
from datetime import datetime, timezone

# ==============================================================================
# ⚙️ CONFIGURAÇÃO
# ==============================================================================
WP_URL = "http://localhost/brasileirinho"
WP_API_ENDPOINT = f"{WP_URL}/wp-json/wp/v2/posts"
WP_PAGE_ENDPOINT = f"{WP_URL}/wp-json/wp/v2/pages" 

WP_USER = "guardiao"
WP_APP_PASSWORD = "36QW GoKO r0hl ZMor ebIE JyRh" # ATUALIZADA em 01-Fev-2026 @ 19:25

BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR = BASE_DIR / "09-csl"
MENU_FILE = BASE_DIR / "metadata" / "Translation_Control_Center.csv"
LOG_DIR = BASE_DIR / "logs"

# ==============================================================================
# 🛠️ UTILITÁRIOS
# ==============================================================================

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"injection_v5_resilient_{timestamp}.log"
    
    def log(msg, level="INFO"):
        icon = "✅" if level == "INFO" else "⚠️" if level == "WARN" else "❌"
        print(f"{icon} [{level}] {msg}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}\n")
    return log

def get_wp_auth_header():
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode())
    return {"Authorization": f"Basic {token.decode('utf-8')}"}

def get_utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def extract_source_id(html_path):
    """Lê o Source-ID do cabeçalho do HTML em Inglês (SRO)."""
    if not html_path.exists(): return None
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            head = f.read(2000)
            match = re.search(r"Source-ID:\s+(\d+)", head)
            if match: return int(match.group(1))
    except: pass
    return None

# atualizado por Claude Sonnet 4.6 em 20260220:

def find_folder_by_pdpn(pdpn):
    target = CSL_DIR / pdpn
    return target if target.is_dir() else None

# ==============================================================================
# 🚀 MOTOR DE INJEÇÃO
# ==============================================================================

def run_resilient_injection():
    log = setup_logger()
    log("=== 🚀 INICIANDO INJEÇÃO V5 (RESILIENT) ===", "INFO")

    if not MENU_FILE.exists():
        log("Menu de controle não encontrado.", "ERROR")
        return

    # 1. Identificar candidatos
    injection_queue = []
    with open(MENU_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["COMMAND"].strip().upper() in ["YES", "X", "SIM"]:
                injection_queue.append(row)

    if not injection_queue:
        log("Nenhum item marcado para injeção.", "WARN")
        return

    log(f"Fila de processamento: {len(injection_queue)} itens.", "INFO")
    headers = get_wp_auth_header()
    success_count = 0
    error_count = 0

    for item in injection_queue:
        pdpn = item['PD#PN']
        folder = find_folder_by_pdpn(pdpn)
        
        if not folder:
            log(f"Pasta não encontrada: {pdpn}", "ERROR")
            continue

        # Caminhos
        json_path = folder / "meta" / "identity.json"
        source_en_path = folder / "source" / "en-US" / "content.html"
        source_pt_path = folder / "source" / "pt-BR" / "content.html"

        try:
            # A. Validação de Schema V3.1
            with open(json_path, 'r', encoding='utf-8') as f:
                identity = json.load(f)

            # B. Obter ID do WordPress (Source-ID)
            wp_id = extract_source_id(source_en_path)
            if not wp_id:
                wp_id = identity.get("sro", {}).get("original_wp_id")
            
            if not wp_id:
                log(f"Source-ID não encontrado para {pdpn}. Impossível injetar.", "ERROR")
                error_count += 1
                continue

            # C. Preparar Conteúdo
            if not source_pt_path.exists():
                log(f"Arquivo HTML PT-BR não encontrado para {pdpn}.", "ERROR")
                error_count += 1
                continue

            with open(source_pt_path, 'r', encoding='utf-8') as f:
                content_html = f.read()

            # D. Preparar Título (COM FALLBACK)
            title_pt = identity.get("titles", {}).get("pt")
            title_en = identity.get("titles", {}).get("en", "Sem Titulo")
            
            if not title_pt:
                log(f"Título PT ausente para {pdpn}. Usando Fallback.", "WARN")
                title_pt = f"[PT-DRAFT] {title_en}"
            
            # E. Payload
            post_data = {
                "title": title_pt,
                "content": content_html,
                "status": "publish"
            }

            # F. Executar UPDATE
            log(f"💉 Injetando em WP ID {wp_id} ({pdpn})...", "INFO")
            
            # Tentativa 1: Posts
            response = requests.post(f"{WP_API_ENDPOINT}/{wp_id}", headers=headers, json=post_data)
            
            # Tentativa 2: Pages (se 404)
            if response.status_code == 404:
                log(f"   ⚠️ ID {wp_id} não é Post. Tentando Pages...", "WARN")
                response = requests.post(f"{WP_PAGE_ENDPOINT}/{wp_id}", headers=headers, json=post_data)

            if response.status_code == 200:
                link = response.json().get('link')
                log(f"   ✅ Sucesso! Link: {link}", "INFO")
                
                # Atualiza metadados
                identity["last_injected_at"] = get_utc_now()
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(identity, f, indent=2, ensure_ascii=False)
                
                success_count += 1
            else:
                log(f"   ❌ Falha WP {response.status_code}: {response.text}", "ERROR")
                error_count += 1

        except Exception as e:
            log(f"❌ Erro crítico em {pdpn}: {e}", "ERROR")
            error_count += 1
            
        time.sleep(0.2)

    log("="*50, "INFO")
    log(f"🏁 INJEÇÃO CONCLUÍDA. Sucessos: {success_count} | Erros: {error_count}", "INFO")

if __name__ == "__main__":
    run_resilient_injection()
