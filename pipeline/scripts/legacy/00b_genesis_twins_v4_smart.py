# Salve como: /media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/00b_genesis_twins_v4_smart.py
import pandas as pd
import pymysql
import os
import sys
import re
from urllib.parse import urlparse

# ==============================================================================
# 👯 ESTRATÉGIA DAS IRMÃS GÊMEAS - GÊNESE INTELIGENTE (V4)
# Objetivo: Gerar Irmã Operacional limpa, filtrando lixo e duplicatas
# ==============================================================================

# --- CONFIGURAÇÕES ---
BASE_DIR = "/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline"
INPUT_CSV = os.path.join(BASE_DIR, "metadata", "MasterPDPN_Raw.csv")
OUTPUT_OPERATIONAL = os.path.join(BASE_DIR, "metadata", "PDPN_01_Operational.csv")
OUTPUT_HISTORICAL = os.path.join(BASE_DIR, "metadata", "PDPN_02_Historical_Updated.csv")

COLS_OPERATIONAL = [
    'Fin-dex', 'id_10WEB.io', 'PD#PN', 'Post_Name_English', 
    'Nome_do_Post_Brasileirinho', 'MainSection_Code', 'URL', 'Slug_Derived'
]

DB_CONFIG = {
    'user': 'root', 'password': '', 'host': 'localhost',
    'database': 'puredhamma_clean',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_slug_from_url(url):
    if not isinstance(url, str) or not url.strip(): return None
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split('/') if p]
    return parts[-1] if parts else None

def detect_table_prefix(conn):
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE '%_posts'")
        result = cursor.fetchone()
        if result:
            return list(result.values())[0].replace('posts', '')
    return 'wp_' # Fallback

def is_valid_pdpn(pdpn):
    """Verifica se o PD#PN segue o padrão XX.YY.NNN"""
    if not isinstance(pdpn, str): return False
    # Regex: 2 letras, ponto, 2 letras, ponto, 3 digitos (ex: BD.CC.006)
    # Aceita variações leves, mas rejeita '..' ou vazio
    return bool(re.match(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}', pdpn.strip()))

def main():
    print(">>> 👯 INICIANDO GÊNESE INTELIGENTE (V4)...")
    
    # 1. Carregar CSV Bruto
    try:
        # dtype=str para evitar conversão automática de números
        df = pd.read_csv(INPUT_CSV, sep=';', encoding='utf-8', dtype=str)
        print(f"    -> Bruto carregado: {len(df)} linhas.")
    except Exception as e:
        print(f"❌ Erro CSV: {e}")
        return

    # 2. HIGIENE DE DADOS (O Filtro)
    print(">>> Aplicando Higiene de Dados...")
    
    # a) Remover linhas sem PD#PN ou com PD#PN inválido (ex: '..')
    df['PD#PN'] = df['PD#PN'].fillna('').str.strip()
    df_clean = df[df['PD#PN'].apply(is_valid_pdpn)].copy()
    print(f"    -> Após filtro de PD#PN inválido: {len(df_clean)} linhas.")

    # b) Remover linhas sem Fin-dex válido (deve ser numérico)
    # Converte para numérico, erros viram NaN
    df_clean['Fin-dex_Num'] = pd.to_numeric(df_clean['Fin-dex'], errors='coerce')
    df_clean = df_clean.dropna(subset=['Fin-dex_Num'])
    print(f"    -> Após filtro de Fin-dex inválido: {len(df_clean)} linhas.")

    # c) Deduplicação Inteligente
    # Se houver PD#PN duplicado, mantemos o que tem o maior Fin-dex (assumindo ser o mais recente/correto)
    # Ou, se preferir, o menor. Mas duplicatas geralmente são referências posteriores.
    # Vamos ordenar por Fin-dex e remover duplicatas de PD#PN mantendo o primeiro.
    df_clean = df_clean.sort_values('Fin-dex_Num')
    df_clean = df_clean.drop_duplicates(subset=['PD#PN'], keep='first')
    print(f"    -> Após deduplicação (Unique PD#PN): {len(df_clean)} linhas.")

    # 3. Conectar ao Banco e Mapear IDs
    print(">>> Conectando ao SQL...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        prefix = detect_table_prefix(conn)
        table = f"{prefix}posts"
        
        db_map = {}
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT ID, post_name FROM {table} WHERE post_type IN ('post', 'page')")
            for row in cursor.fetchall():
                db_map[row['post_name']] = row['ID']
        conn.close()
    except Exception as e:
        print(f"❌ Erro SQL: {e}")
        return

    # 4. Enriquecer Dados
    matches = 0
    for index, row in df_clean.iterrows():
        slug = get_slug_from_url(row.get('URL', ''))
        df_clean.at[index, 'Slug_Derived'] = slug
        
        if slug and slug in db_map:
            df_clean.at[index, 'id_10WEB.io'] = str(db_map[slug])
            matches += 1
            
    print(f"✅ IDs Vinculados: {matches}/{len(df_clean)}")

    # 5. Gerar Irmã Operacional
    # Seleciona apenas colunas canônicas
    for col in COLS_OPERATIONAL:
        if col not in df_clean.columns: df_clean[col] = ''
            
    df_operational = df_clean[COLS_OPERATIONAL]
    
    # Salvar
    df_operational.to_csv(OUTPUT_OPERATIONAL, index=False, sep=';', encoding='utf-8')
    print(f"💎 Irmã Operacional Gerada: {OUTPUT_OPERATIONAL}")
    
    # Salvar Histórica (Opcional, se quiser guardar o estado limpo completo)
    # df_clean.to_csv(OUTPUT_HISTORICAL, index=False, sep=';', encoding='utf-8')

if __name__ == "__main__":
    main()
