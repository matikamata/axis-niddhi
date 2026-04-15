import csv
import json
import os
import re

# ==============================================================================
# 📜 BRASILEIRINHO ENGINE - FASE 4: COMPILAÇÃO DO GLOSSÁRIO
# Objetivo: Transformar CSV humano em JSON de alta performance para a Engine
# ==============================================================================

BASE_DIR = "/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline"
INPUT_CSV = os.path.join(BASE_DIR, "metadata", "Glossario_v5.csv")
OUTPUT_JSON = os.path.join(BASE_DIR, "metadata", "glossary_config.json")

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
