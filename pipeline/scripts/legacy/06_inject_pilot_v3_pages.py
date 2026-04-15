import os
import json
import requests
import base64
import sys

# ==============================================================================
# 💉 BRASILEIRINHO ENGINE - FASE 6: INJEÇÃO PILOTO V3 (PAGES EDITION)
# Objetivo: Localizar a PÁGINA pelo Slug e injetar a tradução
# ==============================================================================

# --- CONFIGURAÇÕES ---
BASE_DIR = "/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline"
TARGET_POST_DIR = os.path.join(BASE_DIR, "09-csl", "PD.AA.000")

# Configurações do WordPress Local
WP_API_URL = "http://localhost/brasileirinho/wp-json/wp/v2"
WP_USER = "Sanghop"
WP_APP_PASS = "5och DsQB 78Ii V99D lP3M LQCx" # Senha de 20260223

def get_auth_header():
    credentials = f"{WP_USER}:{WP_APP_PASS}"
    token = base64.b64encode(credentials.encode())
    return {'Authorization': f'Basic {token.decode("utf-8")}'}

def find_page_id_by_slug(slug):
    """Pergunta ao WP qual é o ID desta PÁGINA."""
    print(f"    -> Buscando ID para a PÁGINA: '{slug}'...")
    try:
        # MUDANÇA CRÍTICA: Endpoint mudou de /posts para /pages
        response = requests.get(
            f"{WP_API_URL}/pages?slug={slug}", 
            headers=get_auth_header()
        )
        
        if response.status_code == 200:
            items = response.json()
            if items:
                found_id = items[0]['id']
                print(f"    -> 🎯 ALVO LOCALIZADO: Page ID {found_id}")
                return found_id
            else:
                print(f"    ❌ Erro: Nenhuma página encontrada com o slug '{slug}'.")
                return None
        else:
            print(f"    ❌ Erro na busca: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"    ❌ Erro de conexão na busca: {e}")
        return None

def main():
    print(">>> 💉 INICIANDO INJEÇÃO PILOTO V3 (PAGES)...")

    # 1. Carregar Metadados
    identity_path = os.path.join(TARGET_POST_DIR, "meta", "identity.json")
    if not os.path.exists(identity_path):
        print("❌ Identity.json não encontrado.")
        return
        
    with open(identity_path, 'r') as f:
        identity = json.load(f)
        
    target_slug = identity['slug_en']

    # 2. DESCOBRIR O ID REAL (Modo Página)
    real_page_id = find_page_id_by_slug(target_slug)
    
    if not real_page_id:
        print("❌ Abortando: Página não encontrada.")
        return

    # 3. Carregar HTML Traduzido
    html_path = os.path.join(TARGET_POST_DIR, "source", "pt-BR", "content.html")
    if not os.path.exists(html_path):
        print("❌ HTML traduzido não encontrado.")
        return
        
    with open(html_path, 'r', encoding='utf-8') as f:
        content_pt = f.read()

    # 4. Preparar Payload
    title_pt = "Buddha Dhamma – Ensinamentos do Buddha"
    
    payload = {
        'title': title_pt,
        'content': content_pt,
    }

    # 5. Enviar para o WordPress (Endpoint /pages)
    print(f"    -> Injetando conteúdo na Página ID {real_page_id}...")
    
    try:
        # MUDANÇA CRÍTICA: Endpoint mudou de /posts para /pages
        response = requests.post(
            f"{WP_API_URL}/pages/{real_page_id}",
            headers=get_auth_header(),
            json=payload
        )
        
        if response.status_code == 200:
            print("\n✅ SUCESSO ABSOLUTO! Página atualizada.")
            print(f"    -> Link: {response.json().get('link')}")
            print("    -> Vá conferir no navegador!")
        else:
            print(f"❌ Falha na injeção: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro de conexão final: {e}")

if __name__ == "__main__":
    main()
