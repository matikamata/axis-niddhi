import os
import deepl
import csv

# ==============================================================================
# 🛡️ BRASILEIRINHO ENGINE - FASE 5a: UPLOAD DE GLOSSÁRIO (DEEPL API) - VERSÃO SAFE
# Objetivo: Evitar upload automático e preservar cota
# ==============================================================================

# Versão anterior antes da modificação da Aloka em 20260223 era (ela não colocou revisão de cabeçalho mesmo insistindo):

# ==============================================================================
# 🛡️ BRASILEIRINHO ENGINE - FASE 5a: UPLOAD DE GLOSSÁRIO (DEEPL API)
# Objetivo: Criar um Glossário Oficial no DeepL para forçar termos (Buddha, Dhamma)
# ==============================================================================

BASE_DIR = "/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline"
INPUT_CSV = os.path.join(BASE_DIR, "metadata", "Glossario_v5.csv")
DEEPL_AUTH_KEY = "9298739e-55b6-4709-b557-806884a66041:fx"
GLOSSARY_ID_FILE = os.path.join(BASE_DIR, "metadata", "deepl_glossary_id.txt")

def main():
    print(">>> 🛡️ CHECK DE GLOSSÁRIO EXISTENTE NO DEEPL...")

    # Se já existe ID, apenas informar
    if os.path.exists(GLOSSARY_ID_FILE):
        with open(GLOSSARY_ID_FILE, 'r') as f:
            glossary_id = f.read().strip()
        print(f"✅ Glossário já existe. ID: {glossary_id}")
        return

    # Caso não exista, proceder com upload
    print("⚠️ Glossário não encontrado. Criação permitida (usar cota!).")
    
    translator = deepl.Translator(DEEPL_AUTH_KEY)
    
    entries = {}
    try:
        with open(INPUT_CSV, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            reader = csv.reader(f, dialect)
            for row in reader:
                if len(row) >= 2:
                    src = row[0].strip()
                    tgt = row[1].strip()
                    if src and tgt:
                        entries[src] = tgt
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return

    try:
        my_glossary = translator.create_glossary(
            "Brasileirinho_Glossary_v5",
            source_lang="en",
            target_lang="pt",
            entries=entries
        )
        print(f"✅ Glossário criado! ID: {my_glossary.glossary_id}")

        with open(GLOSSARY_ID_FILE, 'w') as f:
            f.write(my_glossary.glossary_id)
    except deepl.DeepLError as e:
        print(f"❌ Erro na API DeepL: {e}")

if __name__ == "__main__":
    main()
