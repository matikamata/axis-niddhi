import os
import json
import shutil
import re

# ==============================================================================
# 🏛️ BRASILEIRINHO ENGINE - FASE 3: CONSTRUÇÃO DA CSL
# Objetivo: Transformar arquivos lineares em estrutura hierárquica canônica
# ==============================================================================

BASE_DIR = "/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline"
INPUT_DIR = os.path.join(BASE_DIR, "02-preprocessed", "en-US")
CSL_ROOT = os.path.join(BASE_DIR, "09-csl")

def setup_environment():
    if not os.path.exists(CSL_ROOT):
        os.makedirs(CSL_ROOT)
        print(f"📁 Raiz CSL criada: {CSL_ROOT}")

def parse_filename(filename):
    """
    Extrai metadados do nome do arquivo canônico.
    Formato: [Fin-dex]__[PD#PN]__[Slug].html
    Ex: 0001__PD.AA.000__welcome.html
    """
    try:
        # Remove extensão
        name_no_ext = filename.replace('.html', '')
        parts = name_no_ext.split('__')
        
        if len(parts) < 3:
            return None
            
        return {
            'findex': parts[0],
            'pdpn': parts[1],
            'slug': parts[2],
            'original_filename': filename
        }
    except Exception:
        return None

def build_csl_entry(meta):
    """Cria a estrutura de pastas para um post."""
    pdpn = meta['pdpn']
    
    # Caminhos
    post_dir = os.path.join(CSL_ROOT, pdpn)
    source_dir = os.path.join(post_dir, "source", "en-US")
    meta_dir = os.path.join(post_dir, "meta")
    
    # Criar pastas
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(meta_dir, exist_ok=True)
    
    # 1. Copiar Conteúdo (Padronizado como content.html)
    src_file = os.path.join(INPUT_DIR, meta['original_filename'])
    dst_file = os.path.join(source_dir, "content.html")
    shutil.copy2(src_file, dst_file)
    
    # 2. Criar Identity JSON
    identity = {
        "pdpn": pdpn,
        "findex": meta['findex'],
        "slug_en": meta['slug'],
        "canonical_filename": meta['original_filename'],
        "schema_version": "1.0"
    }
    
    json_path = os.path.join(meta_dir, "identity.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(identity, f, indent=4)

def main():
    print(">>> 🏛️ INICIANDO CONSTRUÇÃO DA CSL...")
    setup_environment()
    
    files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".html")])
    print(f"    -> Processando {len(files)} arquivos...")
    
    count = 0
    errors = 0
    
    for filename in files:
        meta = parse_filename(filename)
        
        if meta:
            try:
                build_csl_entry(meta)
                count += 1
                if count % 100 == 0:
                    print(f"    ... {count} posts estruturados.")
            except Exception as e:
                print(f"❌ Erro ao processar {filename}: {e}")
                errors += 1
        else:
            print(f"⚠️  Nome de arquivo inválido (ignorado): {filename}")
            errors += 1

    print(f"✅ CSL CONSTRUÍDA: {count} posts organizados em {CSL_ROOT}")
    if errors > 0:
        print(f"⚠️  {errors} erros encontrados.")

if __name__ == "__main__":
    main()
