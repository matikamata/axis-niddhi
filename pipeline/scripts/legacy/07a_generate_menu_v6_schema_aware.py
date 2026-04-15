"""
💎 BRASILEIRINHO ENGINE - SCRIPT 07a (V6)
=========================================
Nome:       Gerador de Menu de Tradução (Schema V3.1 Aware)
Versão:     6.0
Autor:      Lead SRE & Sangha
Data:       2026-01-31

DESCRIÇÃO:
Gera o 'Translation_Control_Center.csv'.
Lê a CSL, interpreta corretamente o Schema V3.1 (dados aninhados)
e calcula custos para a cota DeepL.
"""

import os
import csv
import json
import re
from pathlib import Path
from datetime import datetime

# ==============================================================================
# ⚙️ CONFIGURAÇÃO
# ==============================================================================
BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR = BASE_DIR / "09-csl"
MENU_FILE = BASE_DIR / "metadata" / "Translation_Control_Center.csv"
SECTIONS_FILE = BASE_DIR / "metadata" / "MasterPDPN_Sections.csv"
LOG_DIR = BASE_DIR / "logs"

FREE_QUOTA_LIMIT = 500000
COST_PER_CHAR_USD = 25 / 1000000

# ==============================================================================
# 🛠️ UTILITÁRIOS
# ==============================================================================

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"menu_gen_v6_{timestamp}.log"
    def log(msg):
        print(f"ℹ️ {msg}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    return log

def load_sections_map():
    sections = {}
    if SECTIONS_FILE.exists():
        try:
            with open(SECTIONS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if ";" in line:
                        name, prefix = line.strip().split(";")
                        sections[prefix.strip()] = name.strip()
        except: pass
    return sections

def clean_html_tags(text):
    return re.sub(r'<.*?>', '', text)

# ==============================================================================
# 🚀 MOTOR PRINCIPAL
# ==============================================================================

def generate_menu_v6():
    log = setup_logger()
    log("=== 🚀 GERADOR DE MENU V6 (SCHEMA V3.1 AWARE) ===")
    
    sections_map = load_sections_map()
    inventory = []
    
    if not CSL_DIR.exists():
        log("❌ CSL não encontrada.")
        return

    folders = sorted([f for f in CSL_DIR.iterdir() if f.is_dir()])
    log(f"📂 Analisando {len(folders)} pastas...")

    for folder in folders:
        try:
            json_path = folder / "meta" / "identity.json"
            source_en = folder / "source" / "en-US" / "content.html"
            source_pt = folder / "source" / "pt-BR" / "content.html"

            if not json_path.exists(): continue

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # --- CORREÇÃO CRÍTICA: LEITURA DO SCHEMA V3.1 ---
            # Os dados agora estão dentro de "identity": { ... }
            identity_block = data.get("identity", {})
            
            pdpn = identity_block.get("pdpn", "UNKNOWN")
            findex = identity_block.get("findex", "0000")
            slug = identity_block.get("slug_root") or data.get("slug_en") or data.get("slug", "unknown")
            
            # Fallback para Schema antigo se necessário
            if pdpn == "UNKNOWN": pdpn = data.get("pdpn", "UNKNOWN")
            if findex == "0000": findex = data.get("findex", "0000")

            # Determinar Seção
            prefix = pdpn.split('.')[0] if '.' in pdpn else "MS"
            section = sections_map.get(prefix, f"{prefix} - Uncategorized")

            # Contar Caracteres
            chars = 0
            if source_en.exists():
                with open(source_en, 'r', encoding='utf-8') as f:
                    chars = len(clean_html_tags(f.read()))

            # Status
            status = "DONE" if source_pt.exists() else "PENDING"

            # Métricas
            cost = chars * COST_PER_CHAR_USD
            quota = (chars / FREE_QUOTA_LIMIT) * 100

            inventory.append({
                "Fin-dex": findex,
                "PD#PN": pdpn,
                "Section": section,
                "Slug": slug,
                "Status": status,
                "Chars": chars,
                "Est_Cost_USD": round(cost, 4),
                "Quota_Impact_%": round(quota, 2),
                "COMMAND": ""
            })

        except Exception as e:
            log(f"❌ Erro em {folder.name}: {e}")

    # Ordenar
    inventory.sort(key=lambda x: x['Fin-dex'])

    # Salvar CSV
    header = ["Fin-dex", "PD#PN", "Section", "Slug", "Status", "Chars", "Est_Cost_USD", "Quota_Impact_%", "COMMAND"]
    with open(MENU_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for item in inventory:
            row = item.copy()
            row["Quota_Impact_%"] = f"{item['Quota_Impact_%']}%"
            writer.writerow(row)

    log(f"✅ MENU GERADO: {MENU_FILE}")
    log(f"📊 Total de Arquivos: {len(inventory)}")

if __name__ == "__main__":
    generate_menu_v6()
