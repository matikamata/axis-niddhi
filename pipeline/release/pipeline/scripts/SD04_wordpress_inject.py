"""
💎 BRASILEIRINHO ENGINE — S11 (ex-Script 08 V5)
========================================
Nome:       Injetor WordPress (Resilient Overwrite Strategy)
Sequência:  S11 → roda após S10
Revisado:   2026-02-27 (Genesis v2.0)
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
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# ==============================================================================
# ⚙️ CONFIGURAÇÃO — via config.py canônico (V5.1)
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import (
    DIR_09_CSL,
    METADATA_DIR,
    LOG_DIR,
    WP_BASE_URL,
    WP_API_POSTS,
    WP_API_PAGES,
    WP_ADMIN_USER,
    get_wp_password,
)

WP_API_ENDPOINT  = WP_API_POSTS
WP_PAGE_ENDPOINT = WP_API_PAGES

CSL_DIR   = DIR_09_CSL
MENU_FILE = METADATA_DIR / "Translation_Control_Center.csv"

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
    password = get_wp_password()
    token    = base64.b64encode(f"{WP_ADMIN_USER}:{password}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }
    return {"Authorization": f"Basic {token.decode('utf-8')}"}

def get_utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def extract_source_id(html_path):
    """Lê o Source-ID do cabeçalho do HTML em Inglês (SRO)."""
    if not html_path.exists():
        return None
    try:
        head = html_path.read_text(encoding="utf-8")[:2000]
        match = re.search(r"Source-ID:\s+(\d+)", head)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return None


def resolve_wp_id_by_slug(slug_root: str, headers: dict) -> int | None:
    """
    Fallback: busca o WP ID pelo slug no WordPress local.
    Tenta /pages primeiro (corpus PureDhamma são páginas), depois /posts.
    Retorna o ID inteiro ou None se não encontrado.
    """
    for endpoint in [WP_PAGE_ENDPOINT, WP_API_ENDPOINT]:
        try:
            resp = requests.get(
                endpoint,
                params={"slug": slug_root, "per_page": 1, "_fields": "id,slug"},
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    return results[0]["id"]
        except Exception:
            pass
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

    # 1. Identificar candidatos — todos os posts com Status=DONE (pt-BR traduzido)
    # SD04 não depende de COMMAND=YES (esse campo é do SP10).
    # Idempotente: posts já injetados são atualizados sem dano.
    injection_queue = []
    with open(MENU_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Status", "").strip().upper() == "DONE":
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

            # B. Obter ID do WordPress — 3 fontes em cascata
            wp_id = extract_source_id(source_en_path)
            if not wp_id:
                wp_id = identity.get("sro", {}).get("original_wp_id")
            if not wp_id:
                # Fallback: buscar pelo slug no WP local
                slug = identity.get("identity", {}).get("slug_root")
                if slug:
                    wp_id = resolve_wp_id_by_slug(slug, headers)
                    if wp_id:
                        log(f"   ℹ️  {pdpn}: WP ID resolvido pelo slug '{slug}' → {wp_id}", "INFO")

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

            # F. Executar UPDATE — Pages primeiro (corpus PureDhamma), Posts como fallback
            log(f"💉 Injetando em WP ID {wp_id} ({pdpn})...", "INFO")

            response = requests.post(f"{WP_PAGE_ENDPOINT}/{wp_id}", headers=headers, json=post_data)

            if response.status_code == 404:
                response = requests.post(f"{WP_API_ENDPOINT}/{wp_id}", headers=headers, json=post_data)

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
