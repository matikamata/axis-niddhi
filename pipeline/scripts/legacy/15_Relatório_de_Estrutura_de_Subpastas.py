import os
import json
from pathlib import Path

CSL_ROOT = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline/09-csl")

def generate_subfolder_report():
    print(f"📊 GERANDO RELATÓRIO DE ESTRUTURA - CSL V3.0")
    print("="*60)
    
    # Pegar as primeiras 5 pastas para amostragem
    folders = sorted([f for f in CSL_ROOT.iterdir() if f.is_dir()])[:5]
    
    for folder in folders:
        print(f"\n📁 PASTA: {folder.name}")
        
        # Listar todos os arquivos e subpastas recursivamente
        for root, dirs, files in os.walk(folder):
            level = Path(root).relative_to(folder)
            indent = "  " * (len(level.parts) + 1)
            if level.parts:
                print(f"{indent}📂 {level}/")
            
            for f in files:
                file_path = Path(root) / f
                size = file_path.stat().st_size
                print(f"{indent}  📄 {f} ({size} bytes)")
                
                # Se for o identity.json, vamos ver o que ele diz sobre o caminho
                if f == "identity.json":
                    try:
                        with open(file_path, 'r', encoding='utf-8') as j:
                            data = json.load(j)
                            en_path = data.get("artifacts", {}).get("en-US", {}).get("file_path")
                            en_hash = data.get("artifacts", {}).get("en-US", {}).get("integrity_sha256")
                            print(f"{indent}     ↳ 🔑 Registro JSON: {en_path}")
                            print(f"{indent}     ↳ 🛡️ Hash Registrado: {en_hash[:10]}...")
                    except:
                        print(f"{indent}     ↳ ❌ Erro ao ler JSON")

    print("\n" + "="*60)
    print(f"✅ Amostragem concluída para as primeiras {len(folders)} pastas.")

if __name__ == "__main__":
    generate_subfolder_report()
