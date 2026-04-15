import os
from pathlib import Path

# --- CONFIGURAÇÕES ---
CSL_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline/09-csl")

def audit_brute_force():
    print(f"🏛️ AUDITORIA DE FORÇA BRUTA - BUSCA POR RASTROS DE VÍDEO")
    print(f"📂 Analisando: {CSL_DIR}\n")
    
    folders = [d for d in CSL_DIR.iterdir() if d.is_dir()]
    
    stats = {
        'total': 0,
        'en_with_video': 0,
        'pt_with_video': 0,
        'translated': 0,
        'lost': []
    }

    for folder in folders:
        en_path = folder / "source" / "en-US" / "content.html"
        pt_path = folder / "source" / "pt-BR" / "content.html"

        has_video_en = False
        if en_path.exists():
            content_en = en_path.read_text(encoding='utf-8').lower()
            if "youtube" in content_en or "youtu.be" in content_en:
                has_video_en = True
                stats['en_with_video'] += 1

        if pt_path.exists():
            stats['translated'] += 1
            content_pt = pt_path.read_text(encoding='utf-8').lower()
            has_video_pt = ("youtube" in content_pt or "youtu.be" in content_pt)
            if has_video_pt:
                stats['pt_with_video'] += 1
            
            # Se tinha no inglês e sumiu no português (O CRIME)
            if has_video_en and not has_video_pt:
                stats['lost'].append(folder.name)

    print("="*60)
    print(f"📊 RESULTADOS REAIS (Busca por string 'youtube')")
    print("="*60)
    print(f"📦 Total de Pastas:             {len(folders)}")
    print(f"💰 Total Traduzidos:            {stats['translated']}")
    print(f"📺 Inglês com rastro YT:        {stats['en_with_video']}")
    print(f"🇧🇷 Português com rastro YT:     {stats['pt_with_video']}")
    print("-" * 60)
    
    if stats['lost']:
        print(f"🚨 FERIDOS ENCONTRADOS: {len(stats['lost'])} posts perderam o link!")
        for p in stats['lost']:
            print(f"   - ❌ {p}")
    else:
        print("✅ Se houve rastro de YouTube no Inglês, ele permanece no Português.")

if __name__ == "__main__":
    audit_brute_force()
