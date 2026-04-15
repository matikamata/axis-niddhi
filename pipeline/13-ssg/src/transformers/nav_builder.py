# src/transformers/nav_builder.py
import logging
import csv  # Adicionado para processar o MasterPDPN_Sections.csv
from pathlib import Path  # Adicionado para localizar o arquivo de metadados
from typing import List, Dict
from models import Post, Section

logger = logging.getLogger("Script13.NavBuilder")

def load_section_map() -> Dict[str, str]:
    """Lê o dicionário de seções do arquivo CSV oficial."""
    # Define o caminho para /media/.../pipeline/metadata/MasterPDPN_Sections.csv
    # Path(__file__) está em pipeline/13-ssg/src/transformers/nav_builder.py
    # .parent.parent.parent.parent sobe 4 níveis para chegar na raiz do pipeline
    csv_path = Path(__file__).parent.parent.parent.parent / "metadata" / "MasterPDPN_Sections.csv"
    
    mapping = {}
    if not csv_path.exists():
        logger.warning(f"⚠️  Section metadata not found at {csv_path}. Using fallback titles.")
        return mapping

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            # O formato é "01 - Welcome;PD", usamos o delimitador ';'
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if len(row) == 2:
                    full_name = row[0].strip()  # Ex: "01 - Welcome"
                    code = row[1].strip()       # Ex: "PD"
                    
                    # Limpeza: Transforma "01 - Welcome" em apenas "Welcome"
                    title = full_name.split(" - ", 1)[-1] if " - " in full_name else full_name
                    mapping[code] = title
        logger.info(f"📖 Loaded {len(mapping)} section titles from CSV.")
    except Exception as e:
        logger.error(f"❌ Error reading section CSV: {e}")
        
    return mapping

def build_navigation_tree(posts, pipeline_root=None):
    """
    Groups posts by Section Code and sorts them by Findex.
    Returns a list of Section objects, sorted by Section Code.
    """
    # 0. Carrega o mapeamento dinâmico em vez de usar o SECTION_TITLES estático
    section_map = load_section_map() # Chamada da nova função de carregamento
    
    grouped: Dict[str, List[Post]] = {}
    
    # 1. Grouping
    for post in posts:
        code = post.section_code
        if code not in grouped:
            grouped[code] = []
        grouped[code].append(post)
    
    # 2. Construction & Sorting
    sections: List[Section] = []
    
    # Ordena os códigos alfabeticamente (ex: AB, BC, BD...)
    sorted_codes = sorted(grouped.keys())
    
    for code in sorted_codes:
        post_list = grouped[code]
        # Ordena posts pelo findex (0001, 0002...)
        post_list.sort(key=lambda p: p.findex)
        
        # Busca o título no CSV. Se não encontrar, usa "Section [Código]" como reserva.
        title = section_map.get(code, f"Section {code}") # Usa o mapa carregado do CSV
        
        section = Section(
            code=code,
            title=title, # Agora virá como "Buddhist Chanting" em vez de "Section BC"
            posts=post_list
        )
        sections.append(section)
        
    logger.info(f"✅ Built Navigation Tree: {len(sections)} sections.")
    return sections
