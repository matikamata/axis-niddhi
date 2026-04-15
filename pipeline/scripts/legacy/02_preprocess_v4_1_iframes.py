import os
import re
from bs4 import BeautifulSoup

# ==============================================================================
# 🧹 BRASILEIRINHO ENGINE - FASE 2: PRÉ-PROCESSAMENTO (V4.1 - IFRAMES & COLORS)
# Objetivo: Limpar artefatos, PRESERVAR CORES/CLASSES e PERMITIR VÍDEOS (IFRAMES)
# Atualização V4.1: Suporte a embeds do YouTube/Vimeo
# ==============================================================================

BASE_DIR = "/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline"
INPUT_DIR = os.path.join(BASE_DIR, "01-extracted-htmls", "en-US")
OUTPUT_DIR = os.path.join(BASE_DIR, "02-preprocessed", "en-US")

def setup_environment():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def fix_tattoo_findex(tattoo_text):
    def replace_findex(match):
        number = int(match.group(1))
        return f"Fin-dex:      {str(number).zfill(4)}"
    return re.sub(r'Fin-dex:\s+(\d+)', replace_findex, tattoo_text)

def clean_html(content):
    # 1. Separar Tatuagem (Metadata)
    tattoo = ""
    tattoo_match = re.search(r'(<!--.*?-->)', content, re.DOTALL)
    if tattoo_match:
        raw_tattoo = tattoo_match.group(1)
        tattoo = fix_tattoo_findex(raw_tattoo)
        content = content.replace(raw_tattoo, '')
    
    # 2. Remover Shortcodes do WP
    content = re.sub(r'\[/?caption.*?\]', '', content)
    content = re.sub(r'\[/?ref.*?\]', '', content)
    
    # 3. Parsing
    soup = BeautifulSoup(content, 'html.parser')
    
    # 4. Remover tags indesejadas (script, form, etc)
    # [V4.1 UPDATE] Removido 'iframe' desta lista para preservar vídeos
    for tag in soup(['script', 'form', 'input', 'button', 'link', 'meta', 'object', 'embed']):
        tag.decompose()
        
    # 5. Limpar atributos sujos
    # [V4.1 UPDATE] Adicionados atributos de iframe (allow, frameborder, etc)
    allowed_attrs = [
        'href', 'src', 'alt', 'title', 'id', 'name', 'style', 'class', 'width', 'height',
        'allow', 'allowfullscreen', 'frameborder', 'referrerpolicy', 'loading', 'target'
    ]
    
    for tag in soup.find_all(True):
        attrs = dict(tag.attrs)
        for attr in attrs:
            # Remove atributos que não estão na lista permitida
            if attr not in allowed_attrs:
                del tag.attrs[attr]
                
    # 6. Normalizar Links
    for a in soup.find_all('a', href=True):
        if '?' in a['href']:
            a['href'] = a['href'].split('?')[0]

    # 7. Reconstruir (SEM PRETTIFY para não quebrar layout sensível)
    clean_body = str(soup)
    # Remove excesso de quebras de linha
    clean_body = re.sub(r'\n\s*\n', '\n', clean_body)
    
    return f"{tattoo}\n{clean_body}"

def main():
    print(">>> 🧹 INICIANDO PRÉ-PROCESSAMENTO V4.1 (IFRAMES SUPPORT)...")
    setup_environment()
    
    files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".html")])
    print(f"    -> Processando {len(files)} arquivos...")
    
    count = 0
    for filename in files:
        in_path = os.path.join(INPUT_DIR, filename)
        out_path = os.path.join(OUTPUT_DIR, filename)
        
        try:
            with open(in_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            clean_content = clean_html(raw_content)
            
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            
            count += 1
            if count % 100 == 0: print(f"    ... {count} processados.")
            
        except Exception as e:
            print(f"❌ Erro em {filename}: {e}")

    print(f"✅ LIMPEZA V4.1 CONCLUÍDA. Vídeos preservados.")

if __name__ == "__main__":
    main()
