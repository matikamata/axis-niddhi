import os
import argparse
import filecmp
from pathlib import Path

# Configuração dos Paths
ZIP_DIR = None
ORIGINAL_DIR = None

def audit_diffs():
    print(f"\n🔍 AUDITORIA DE SINCRONIA — SSG v3 vs AXIS-NIDDHI")
    print(f"📂 Fonte (Zip): {ZIP_DIR}")
    print(f"📂 Destino: {ORIGINAL_DIR}\n")
    print(f"{'STATUS':<12} | {'ARQUIVO'}")
    print("-" * 50)

    # Varre a pasta do ZIP
    for root, dirs, files in os.walk(ZIP_DIR):
        for file in files:
            zip_file = Path(root) / file
            # Calcula o caminho relativo para comparar com a original
            relative_path = zip_file.relative_to(ZIP_DIR)
            original_file = ORIGINAL_DIR / relative_path

            if not original_file.exists():
                print(f"🆕 NOVO       | {relative_path}")
            else:
                # Compara conteúdo
                if not filecmp.cmp(zip_file, original_file, shallow=False):
                    print(f"⚠️  MODIFICADO | {relative_path}")
                else:
                    # Opcional: print(f"✅ IDÊNTICO   | {relative_path}")
                    pass

    # Varre a original para ver se algo foi deletado no ZIP (opcional)
    for root, dirs, files in os.walk(ORIGINAL_DIR):
        for file in files:
            original_file = Path(root) / file
            relative_path = original_file.relative_to(ORIGINAL_DIR)
            zip_file = ZIP_DIR / relative_path
            
            if not zip_file.exists() and ".git" not in str(relative_path):
                print(f"🗑️  AUSENTE NO ZIP | {relative_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare an extracted SSG directory with a local source directory.")
    parser.add_argument("zip_dir", type=Path)
    parser.add_argument("original_dir", type=Path)
    args = parser.parse_args()
    ZIP_DIR, ORIGINAL_DIR = args.zip_dir.expanduser().resolve(), args.original_dir.expanduser().resolve()
    if not ZIP_DIR.is_dir() or not ORIGINAL_DIR.is_dir():
        parser.error("Both paths must be existing directories")
    audit_diffs()
