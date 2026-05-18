import os
import sys

if os.environ.get("AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT") != "1":
    print(
        "ERROR: This retired translation script is fenced and must not be run "
        "during normal AXIS-NIDDHI operations. "
        "Set AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1 only for supervised archaeology/recovery.",
        file=sys.stderr,
    )
    sys.exit(2)

import deepl
import re

# ==============================================================================
# 🚀 BRASILEIRINHO ENGINE - FASE 5: TRADUÇÃO PILOTO V5 (THE SURGEON)
# Objetivo: Tradução + Sanitização Correta + Monitoramento de Cota
# ==============================================================================

BASE_DIR = "/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline"
TARGET_POST_DIR = os.path.join(BASE_DIR, "09-csl", "PD.AA.000")
GLOSSARY_ID_FILE = os.path.join(BASE_DIR, "metadata", "deepl_glossary_id.txt")
DEEPL_AUTH_KEY = "9298739e-55b6-4709-b557-806884a66041:fx"

# 🛡️ REGRAS DE SANITIZAÇÃO (CORRIGIDAS)
SANITIZATION_RULES = [
    # 1. FAMÍLIA BUDDHA
    # Regex captura o sufixo no grupo 1.
    # Ex: "budista" -> match "bud" + "ista" (grupo 1)
    {
        'pattern': r'(?i)\bbud(a|as|ismo|ista|ico|os|o)\b',
        'replacement': lambda m: "Buddh" + m.group(1) # Simplesmente cola o sufixo correto
    },
    
    # 2. FAMÍLIA DHAMMA
    {
        'pattern': r'(?i)\bdharm(a|as|ico|ic)\b',
        'replacement': lambda m: "Dhamm" + m.group(1)
    },

    # 3. FAMÍLIA KAMMA
    {
        'pattern': r'(?i)\bcarm(a|as|ico|ic)\b',
        'replacement': lambda m: "Kamm" + m.group(1)
    },
    
    # 4. FAMÍLIA NIBBANA
    {
        'pattern': r'(?i)\bnirvan(a|as|ico)\b',
        'replacement': lambda m: "Nibban" + m.group(1)
    },
    
    # 5. FAMÍLIA SUTTA
    {
        'pattern': r'(?i)\bsutr(a|as)\b',
        'replacement': lambda m: "Sutt" + m.group(1)
    },
    
    # 6. CORREÇÕES DIACRÍTICAS ESTRITAS
    {'pattern': r'(?i)\bpali\b', 'replacement': 'Pālī'},
    {'pattern': r'(?i)\btipitaka\b', 'replacement': 'Tipiṭaka'}
]

def apply_sanitization(text):
    """Aplica as regras de sanitização com lógica de capitalização corrigida."""
    processed_text = text
    
    for rule in SANITIZATION_RULES:
        pattern = rule['pattern']
        replacement = rule['replacement']
        
        if isinstance(replacement, str):
            processed_text = re.sub(pattern, replacement, processed_text)
        else:
            def smart_replace(match):
                # Reconstrói a palavra correta (Ex: Buddh + ista = Buddhista)
                new_word = replacement(match)
                
                # Lógica de Capitalização:
                # Se o original era Title Case (Buda), mantém Title Case (Buddha).
                # Se o original era lower (budista), FORÇA Title Case (Buddhista) 
                # pois são termos sagrados/técnicos no PureDhamma.
                return new_word[0].upper() + new_word[1:]

            processed_text = re.sub(pattern, smart_replace, processed_text)
            
    return processed_text

def check_usage(translator):
    """Monitora o consumo da API."""
    try:
        usage = translator.get_usage()
        if usage.character.limit_exceeded:
            print("❌ LIMITE DE CARACTERES EXCEDIDO!")
            return False
        
        percent = (usage.character.count / usage.character.limit) * 100
        print("-" * 50)
        print(f"📊 STATUS DA COTA DEEPL:")
        print(f"   Usado:     {usage.character.count:,} chars")
        print(f"   Total:     {usage.character.limit:,} chars")
        print(f"   Restante:  {usage.character.limit - usage.character.count:,} chars")
        print(f"   Utilização: {percent:.2f}%")
        print("-" * 50)
        return True
    except Exception as e:
        print(f"⚠️ Não foi possível verificar cota: {e}")
        return True

def main():
    print(">>> 🚀 INICIANDO TRADUÇÃO PILOTO V5 (THE SURGEON)...")
    
    translator = deepl.Translator(DEEPL_AUTH_KEY)
    
    # Verifica cota ANTES
    if not check_usage(translator): return

    # Recuperar Glossary ID
    if not os.path.exists(GLOSSARY_ID_FILE):
        print("❌ Arquivo de ID do glossário não encontrado.")
        return
    with open(GLOSSARY_ID_FILE, 'r') as f:
        glossary_id = f.read().strip()

    # Ler Fonte
    source_path = os.path.join(TARGET_POST_DIR, "source", "en-US", "content.html")
    with open(source_path, 'r', encoding='utf-8') as f:
        original_html = f.read()

    # Separar Tatuagem
    tattoo_match = re.search(r'(<!--.*?-->)', original_html, re.DOTALL)
    tattoo = tattoo_match.group(1) if tattoo_match else ""
    content_to_translate = original_html.replace(tattoo, "")

    # Envio para DeepL
    print("    -> Enviando para DeepL (pt-BR)...")
    try:
        result = translator.translate_text(
            content_to_translate,
            source_lang="EN",
            target_lang="PT-BR",
            tag_handling="html",
            preserve_formatting=True,
            glossary=glossary_id
        )
        translated_text = result.text
    except Exception as e:
        print(f"❌ Erro na API DeepL: {e}")
        return

    # PÓS-PROCESSAMENTO (SANITIZAÇÃO)
    print("    -> Aplicando Sanitização Cirúrgica...")
    final_text = apply_sanitization(translated_text)

    # Salvar Resultado
    target_dir = os.path.join(TARGET_POST_DIR, "source", "pt-BR")
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, "content.html")
    
    new_tattoo = tattoo.replace("Language:     en-US", "Language:     pt-BR")
    final_content = f"{new_tattoo}\n{final_text}"
    
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"✅ TRADUÇÃO V5 CONCLUÍDA!")
    print(f"    -> Salvo em: {target_path}")
    
    # Verifica cota DEPOIS
    check_usage(translator)

if __name__ == "__main__":
    main()
