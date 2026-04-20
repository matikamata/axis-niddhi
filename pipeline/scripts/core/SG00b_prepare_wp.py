#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — SG00b_prepare_wp.py
======================================
Script Pré-Pipeline: WordPress Clean State Extractor

Versão   : 1.1 — PATCH Errno 36 (2026-04-20)
Sequência: SG00b → roda ANTES do SG04_harvest_assets.py

PATCH v1.1:
  ★ Abandonado zipfile do Python — corrompia nomes Unicode/Cingalês
    causando [Errno 36] File name too long em nomes de .mp3 longos.
  ★ Extração delegada ao `unzip` nativo do SO via subprocess.
    O `unzip` resolve nomes e codificação diretamente no kernel.
  ★ Sem filtro de extensão na extração — tudo é extraído (mp3, wav,
    imagens, etc.) para garantir que novos usuários tenham todos os
    arquivos necessários para rodar o pipeline do zero.

OBJETIVO:
  1. Varre sources/ em busca de arquivos .zip de backup do WP.
  2. Apresenta lista enumerada — input interativo do usuário.
  3. CLEAN STATE: apaga /wordpress completamente se existir.
  4. Extrai o .zip selecionado → /wordpress/ via `unzip` nativo.
  5. Garante programaticamente que /wordpress/ está no .gitignore.

PORTABILIDADE:
  Todos os paths derivam de config.py (BASE_DIR) — zero hardcode.

USO:
  python3 pipeline/scripts/core/SG00b_prepare_wp.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP — config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, LOG_DIR

# BASE_DIR = pipeline/  →  PROJECT_ROOT = bengyond-playground/
PROJECT_ROOT = BASE_DIR.parent
SOURCES_DIR  = PROJECT_ROOT / "sources"
WP_DIR       = PROJECT_ROOT / "wordpress"
GITIGNORE    = PROJECT_ROOT / ".gitignore"


# ==============================================================================
# 🔒  GITIGNORE GUARD — garante /wordpress/ bloqueado
# ==============================================================================
def ensure_gitignore(gitignore_path: Path) -> None:
    """Adiciona /wordpress/ ao .gitignore se ainda não estiver presente."""
    protect_lines = [
        "\n# ============================================================",
        "# WORDPRESS RUNTIME — ephemeral workspace, NEVER commit",
        "# Dados sensíveis: uploads, wp-config.php",
        "# Reconstruído via: python3 pipeline/scripts/core/SG00b_prepare_wp.py",
        "# ============================================================",
        "/wordpress/",
        "wordpress/",
    ]

    if not gitignore_path.exists():
        print(f"⚠️  .gitignore não encontrado em {gitignore_path}. Criando...")
        gitignore_path.write_text("\n".join(protect_lines) + "\n", encoding="utf-8")
        print("✅ .gitignore criado com proteção /wordpress/")
        return

    content = gitignore_path.read_text(encoding="utf-8")
    if "wordpress/" in content or "/wordpress/" in content:
        print("✅ .gitignore já protege /wordpress/ — sem alterações.")
        return

    with gitignore_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(protect_lines) + "\n")

    print("✅ /wordpress/ adicionado ao .gitignore.")


# ==============================================================================
# 🗂️  DISCOVERY — localiza backups .zip em sources/
# ==============================================================================
def find_zip_backups(sources_dir: Path) -> list[Path]:
    """FAIL-FAST: retorna lista de .zip ou aborta."""
    if not sources_dir.exists():
        print(f"❌ FAIL-FAST: Pasta sources/ não encontrada: {sources_dir}", file=sys.stderr)
        sys.exit(1)

    zips = sorted(sources_dir.glob("*.zip"))
    if not zips:
        print(f"❌ FAIL-FAST: Nenhum .zip encontrado em {sources_dir}", file=sys.stderr)
        sys.exit(1)

    return zips


# ==============================================================================
# 🖨️  MENU INTERATIVO
# ==============================================================================
def present_menu(zips: list[Path]) -> Path:
    """Exibe lista enumerada e coleta escolha do usuário."""
    print("\n" + "=" * 60)
    print("📦  BACKUPS WORDPRESS DISPONÍVEIS EM sources/")
    print("=" * 60)
    for i, z in enumerate(zips, 1):
        size_mb = z.stat().st_size / (1024 * 1024)
        print(f"  [{i}] {z.name}  ({size_mb:,.0f} MB)")
    print("-" * 60)

    while True:
        try:
            raw = input(f"Qual backup usar? Digite o número [1-{len(zips)}]: ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(zips):
                selected = zips[idx]
                print(f"\n✅ Selecionado: {selected.name}\n")
                return selected
            print(f"❌ Número inválido. Digite entre 1 e {len(zips)}.")
        except (ValueError, EOFError):
            print("❌ Entrada inválida. Digite um número inteiro.")


# ==============================================================================
# 🧹  CLEAN STATE — remove /wordpress/ existente
# ==============================================================================
def clean_state(wp_dir: Path) -> None:
    """Remove /wordpress/ completamente para garantir estado limpo."""
    if wp_dir.exists():
        try:
            n_files = sum(1 for f in wp_dir.rglob("*") if f.is_file())
            size_mb = sum(
                f.stat().st_size for f in wp_dir.rglob("*") if f.is_file()
            ) / (1024 * 1024)
            print(
                f"⚠️  /wordpress/ encontrado ({n_files} arquivos, {size_mb:.1f} MB)."
                " Aplicando CLEAN STATE..."
            )
            shutil.rmtree(wp_dir)
            print("🗑️   /wordpress/ removido. Clean state alcançado.")
        except Exception as e:
            print(f"❌ FAIL-FAST: Não foi possível remover /wordpress/: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("ℹ️  /wordpress/ não existe — nenhuma remoção necessária.")


# ==============================================================================
# 📂  EXTRAÇÃO — via unzip nativo (resolve Errno 36 / Unicode Cingalês)
# ==============================================================================
def extract_zip(zip_path: Path, target_dir: Path) -> None:
    """
    Extrai zip_path → target_dir usando o `unzip` nativo do sistema.

    Por que não zipfile do Python?
      O módulo zipfile re-encoda nomes internos do ZIP na codificação do
      sistema, podendo gerar nomes > 255 bytes para caracteres Cingaleses
      (multi-byte UTF-8), estourando o limite do kernel Linux com
      [Errno 36] File name too long.
      O `unzip` nativo delega a resolução de nomes ao kernel diretamente,
      contornando o problema.
    """
    # Verifica disponibilidade do unzip
    if not shutil.which("unzip"):
        print("❌ FAIL-FAST: comando `unzip` não encontrado no sistema.", file=sys.stderr)
        print("   Instale com: sudo apt install unzip", file=sys.stderr)
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"⏳ Extraindo {zip_path.name} → {target_dir}")
    print("   (usando `unzip` nativo — suporte completo a Unicode/Cingalês)")

    try:
        result = subprocess.run(
            ["unzip", "-q", str(zip_path), "-d", str(target_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        # unzip -q é silencioso em sucesso; stderr só aparece em warnings
        if result.stderr:
            print(f"   ⚠️  Avisos do unzip:\n{result.stderr.strip()}")

    except subprocess.CalledProcessError as e:
        print(f"❌ FAIL-FAST: `unzip` falhou com código {e.returncode}", file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("❌ FAIL-FAST: `unzip` não encontrado. Instale com: sudo apt install unzip", file=sys.stderr)
        sys.exit(1)

    print("✅ Extração concluída.")


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main() -> None:
    print("\n" + "=" * 60)
    print("🚀  SG00b — WordPress Clean State Extractor  (v1.1)")
    print(f"    PROJECT_ROOT : {PROJECT_ROOT}")
    print(f"    SOURCES_DIR  : {SOURCES_DIR}")
    print(f"    WP_DIR       : {WP_DIR}")
    print(f"    GITIGNORE    : {GITIGNORE}")
    print("=" * 60)

    # FAIL-FAST: valida PROJECT_ROOT
    if not PROJECT_ROOT.exists():
        print(f"❌ FAIL-FAST: PROJECT_ROOT não existe: {PROJECT_ROOT}", file=sys.stderr)
        sys.exit(1)

    # Passo 1: Descobre backups
    zips = find_zip_backups(SOURCES_DIR)

    # Passo 2: Menu interativo
    selected_zip = present_menu(zips)

    # Passo 3: Clean state
    clean_state(WP_DIR)

    # Passo 4: Extração via unzip nativo
    extract_zip(selected_zip, WP_DIR)

    # Passo 5: Proteção gitignore
    ensure_gitignore(GITIGNORE)

    # Relatório final
    wp_uploads = WP_DIR / "runtime_wp" / "wp-content" / "uploads"
    print("\n" + "=" * 60)
    print("📊  RELATÓRIO SG00b")
    print("=" * 60)
    print(f"  ✅ Backup usado    : {selected_zip.name}")
    print(f"  ✅ Destino         : {WP_DIR}")
    print(f"  ✅ .gitignore      : protegido")

    if wp_uploads.exists():
        n_media = sum(1 for f in wp_uploads.rglob("*") if f.is_file())
        size_mb = sum(
            f.stat().st_size for f in wp_uploads.rglob("*") if f.is_file()
        ) / (1024 * 1024)
        print(f"  ✅ wp-content/uploads: {n_media} arquivos  ({size_mb:.1f} MB)")
    else:
        found_subdirs = [d.name for d in WP_DIR.iterdir() if d.is_dir()][:5]
        print(f"  ⚠️  uploads não em {wp_uploads}")
        print(f"     Pastas extraídas  : {found_subdirs}")
        print(f"     Ajuste WP_UPLOADS_DIR no SG04 conforme estrutura real.")

    print("\n▶️  Próximos passos:")
    print("   python3 pipeline/scripts/core/SD01_generate_asset_map.py")
    print("   python3 pipeline/scripts/core/SG04_harvest_assets.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
