import csv
import json
import os
import re
import sys
from pathlib import Path

# ==============================================================================
# 💎 BRASILEIRINHO ENGINE — S08a
# Nome:      Compilação do Glossário (CSV → JSON)
# Versão:    1.1  — AXIS-NIDDHI V5.4 (path hardening)
# Sequência: S08 → roda antes de S09 (obrigatório)
# Revisado:  2026-03-11
#
# FUNÇÃO: Transforma Glossario_v5.csv em glossary_config.json de alta performance.
# INPUT:  metadata/Glossario_v5.csv
# OUTPUT: metadata/glossary_config.json
#
# ⛩️  ATENÇÃO: Após S08, executar S08b (Glossary Gate) antes de S09.
# ==============================================================================

# CONFIGURAÇÃO — via config.py canônico (AXIS-NIDDHI V5.4 hardening)
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import METADATA_DIR, GLOSSARY_JSON as _GLOSSARY_JSON_PATH

INPUT_CSV   = str(METADATA_DIR / "Glossario_v5.csv")
OUTPUT_JSON = str(_GLOSSARY_JSON_PATH)

def clean_term(term):
    """Remove espaços extras e normaliza."""
    if not term: return ""
    return term.strip()

def main():
    print(">>> 📜 INICIANDO COMPILAÇÃO DO GLOSSÁRIO...")
    
    if not os.path.exists(INPUT_CSV):
        print(f"❌ Erro: Arquivo {INPUT_CSV} não encontrado.")
        return

    entries = []
    
    # 1. Ler CSV
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            # Detecta delimitador automaticamente (pode ser , ou ;)
            sample = f.read(1024)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            
            reader = csv.reader(f, dialect)
            
            for row in reader:
                if len(row) >= 2:
                    source = clean_term(row[0])
                    target = clean_term(row[1])
                    
                    if source and target:
                        entries.append({'src': source, 'tgt': target})
                        
        print(f"    -> {len(entries)} termos lidos do CSV.")
        
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return

    # 2. Ordenação Estratégica (Do maior para o menor)
    # Isso evita que 'Sacca' substitua 'Saccāni' parcialmente
    entries.sort(key=lambda x: len(x['src']), reverse=True)
    
    # 3. Separação (Opcional - por enquanto tudo é substituição direta)
    # No futuro, podemos ter listas de 'Do Not Translate' separadas
    
    # 4. Salvar JSON
    config = {
        "version": "4.0",
        "source_lang": "en",
        "target_lang": "pt-BR",
        "entries": entries
    }
    
    try:
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"✅ GLOSSÁRIO COMPILADO: {OUTPUT_JSON}")
        print(f"    -> {len(entries)} regras de substituição ativas.")
        
    except Exception as e:
        print(f"❌ Erro ao salvar JSON: {e}")

if __name__ == "__main__":
    main()
