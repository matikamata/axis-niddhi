"""
💎 BRASILEIRINHO ENGINE - SCRIPT 07b (V3)
=========================================
Nome:       Executor de Tradução (The Guardian Edition)
Versão:     3.0
Autor:      Lead SRE & Sangha
Data:       2026-01-31

DESCRIÇÃO:
Lê o CSV, executa tradução (Título + Corpo) e atualiza Schema V3.1.

RESTAURAÇÕES DE SEGURANÇA:
1. Pre-Flight Check (Saldo DeepL + Custo do Lote).
2. Confirmação Humana Obrigatória.
3. Idempotência (Não traduz se já existe).
"""

import os
import sys
import csv
import json
import requests
import time
import re
from pathlib import Path
from datetime import datetime, timezone

if os.environ.get("AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT") != "1":
    print(
        "ERROR: This retired translation script is fenced and must not be run "
        "during normal AXIS-NIDDHI operations. "
        "Set AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1 only for supervised archaeology/recovery.",
        file=sys.stderr,
    )
    sys.exit(2)

# ==============================================================================
# 🔐 CREDENCIAIS
# ==============================================================================
DEEPL_AUTH_KEY = "9298739e-55b6-4709-b557-806884a66041:fx"
GLOSSARY_ID = "bbebe104-0015-46a9-8f9e-98bb88431ecb" # V5
API_URL = "https://api-free.deepl.com/v2"

BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR = BASE_DIR / "09-csl"
MENU_FILE = BASE_DIR / "metadata" / "Translation_Control_Center.csv"
LOG_DIR = BASE_DIR / "logs"

# Cores
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# ==============================================================================
# 🛠️ UTILITÁRIOS
# ==============================================================================

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"execution_v3_{timestamp}.log"
    def log(msg, level="INFO", color=RESET):
        print(f"{color}[{level}] {msg}{RESET}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}\n")
    return log

def get_deepl_usage():
    try:
        headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_AUTH_KEY}"}
        response = requests.get(f"{API_URL}/usage", headers=headers)
        data = response.json()
        return data.get("character_count", 0), data.get("character_limit", 500000)
    except: return None, None

def translate_text(text, glossary_id):
    if not text: return None
    try:
        headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_AUTH_KEY}"}
        data = {
            "text": [text],
            "source_lang": "EN",
            "target_lang": "PT-BR",
            "glossary_id": glossary_id,
            "tag_handling": "html",
            "preserve_formatting": "1"
        }
        response = requests.post(f"{API_URL}/translate", headers=headers, data=data)
        response.raise_for_status()
        return response.json()["translations"][0]["text"]
    except Exception as e: raise e

def get_utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# atualizado por Claude Sonnet 4.6 em 20260220:

def find_folder_by_pdpn(pdpn):
    target = CSL_DIR / pdpn
    return target if target.is_dir() else None

# ==============================================================================
# 🚀 MOTOR DE EXECUÇÃO
# ==============================================================================

def run_guardian_execution():
    log = setup_logger()
    log("=== 🛡️ EXECUTOR DE TRADUÇÃO V3 (THE GUARDIAN) ===", "INFO", CYAN)

    if not MENU_FILE.exists():
        log("Menu não encontrado.", "ERROR", RED)
        return

    # 1. Carregar Lote
    batch = []
    total_chars = 0
    with open(MENU_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["COMMAND"].strip().upper() in ["YES", "X", "SIM"]:
                batch.append(row)
                total_chars += int(row["Chars"])

    if not batch:
        log("Nenhum comando 'YES' encontrado no CSV.", "WARN", YELLOW)
        return

    # 2. PRE-FLIGHT CHECK (O Retorno)
    log("\n🛫 PRE-FLIGHT CHECK...", "INFO", CYAN)
    current, limit = get_deepl_usage()
    
    if current is None:
        log("❌ Falha de conexão com DeepL.", "ERROR", RED)
        return

    remaining = limit - current
    projected = current + total_chars
    
    print(f"\n{YELLOW}📊 PAINEL DE CONTROLE DEEPL:{RESET}")
    print(f"   Uso Atual:      {current:,} / {limit:,} chars")
    print(f"   Disponível:     {remaining:,} chars")
    print(f"   Lote Atual:     {total_chars:,} chars ({len(batch)} arquivos)")
    print(f"   Uso Projetado:  {projected:,} / {limit:,}")
    
    if projected > limit:
        print(f"\n{RED}❌ ALERTA: ESTE LOTE ESTOURA A COTA!{RESET}")
        confirm = input(f"Digite 'IGNORE' para forçar (Custo Extra): ")
        if confirm != "IGNORE": return
    else:
        print(f"\n{GREEN}✅ Cota Suficiente.{RESET}")

    print(f"\nArquivos na fila: {[item['PD#PN'] for item in batch[:3]]} ...")
    confirm = input(f"\n{CYAN}Digite 'EXECUTE' para iniciar: {RESET}")
    if confirm != "EXECUTE": return

    # 3. Execução
    success = 0
    errors = 0

    for item in batch:
        pdpn = item['PD#PN']
        log(f"Processando {pdpn}...", "INFO")
        
        folder = find_folder_by_pdpn(pdpn)
        if not folder:
            log(f"Pasta não encontrada: {pdpn}", "ERROR", RED)
            continue

        json_path = folder / "meta" / "identity.json"
        source_en = folder / "source" / "en-US" / "content.html"
        target_pt = folder / "source" / "pt-BR" / "content.html"

        # Idempotência
        if target_pt.exists():
            log(f"   ⏭️ PT-BR já existe. Pulando.", "WARN", YELLOW)
            continue

        try:
            # Ler Identity V3.1
            with open(json_path, 'r', encoding='utf-8') as f:
                identity = json.load(f)

            # Traduzir Título
            title_en = identity.get("titles", {}).get("en", "Untitled")
            log(f"   Traduzindo Título: '{title_en}'", "INFO")
            title_pt = translate_text(title_en, GLOSSARY_ID)

            # Traduzir Corpo
            with open(source_en, 'r', encoding='utf-8') as f:
                body_en = f.read()
            log(f"   Traduzindo Corpo ({len(body_en)} chars)...", "INFO")
            body_pt = translate_text(body_en, GLOSSARY_ID)

            # Salvar HTML PT
            target_pt.parent.mkdir(parents=True, exist_ok=True)
            
            # Header Derivado
            header = f"<!--\nDerived Translation\nPD#PN: {pdpn}\nLang: pt-BR\nDate: {get_utc_now()}\n-->"
            final_html = f"{header}\n\n{body_pt}"
            
            with open(target_pt, 'w', encoding='utf-8') as f:
                f.write(final_html)

            # Atualizar Identity V3.1
            identity["titles"]["pt"] = title_pt
            identity["titles"]["pt_source"] = "deepl_v5"
            
            if "pt-BR" not in identity["artifacts"]:
                identity["artifacts"]["pt-BR"] = {}
            
            identity["artifacts"]["pt-BR"].update({
                "status": "derived",
                "file_path": "source/pt-BR/content.html",
                "engine": "DeepL API",
                "translated_at": get_utc_now()
            })
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(identity, f, indent=2, ensure_ascii=False)

            log(f"   ✅ Sucesso!", "INFO", GREEN)
            success += 1
            time.sleep(1)

        except Exception as e:
            log(f"   ❌ Erro: {e}", "ERROR", RED)
            errors += 1

    log(f"🏁 FIM. Sucessos: {success} | Erros: {errors}", "INFO", CYAN)

if __name__ == "__main__":
    run_guardian_execution()
