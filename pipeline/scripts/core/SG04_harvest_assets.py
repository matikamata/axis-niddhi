#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — SG04_harvest_assets.py
=========================================
Nome:       Asset Harvester (A Colheitadeira)
Versão:     2.0 — bengyond-playground (2026-04-20)
Sequência:  SG04 → roda após SG00b_prepare_wp.py

OBJETIVO:
  Vasculhar o WordPress extraído (wordpress/runtime_wp/wp-content/uploads),
  encontrar APENAS imagens e documentos originais do Prof. Lal, e
  copiá-los para assets/images/ com deduplicação SHA-256.

  ⚠️  ÁUDIOS (*.mp3, *.wav, *.ogg) SÃO IGNORADOS TERMINANTEMENTE.
      O pipeline de áudio (SP06 + assets/audio/) trata isso separadamente.

PATHS: todos derivados do config.py canônico — zero hardcode.

USO:
  python3 pipeline/scripts/core/SG04_harvest_assets.py
"""

import hashlib
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP — config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, DIR_STATIC_SITE, LOG_DIR

# PROJECT_ROOT = BASE_DIR.parent  (config.py: BASE_DIR = pipeline/)
PROJECT_ROOT   = BASE_DIR.parent
WP_UPLOADS_DIR = PROJECT_ROOT / "wordpress" / "wp-content" / "uploads"

# Destino canônico das imagens
IMAGE_DEST = DIR_STATIC_SITE / "assets" / "images"

# ==============================================================================
# 🎛️  FILTROS DE EXTENSÃO
# ==============================================================================
# BLOQUEIO ABSOLUTO — áudios têm pipeline dedicado (SP06 / assets/audio/)
BLOCKED_EXTS = {".mp3", ".wav", ".ogg", ".aac", ".flac", ".m4a", ".mp4", ".m4v"}

# Apenas imagens e documentos estáticos
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf"}

# Regex para miniaturas geradas pelo WordPress (ex: imagem-150x150.jpg)
_WP_THUMB_RE = re.compile(
    r"-\d+x\d+\.(jpg|jpeg|png|gif|webp)$", re.IGNORECASE
)


# ==============================================================================
# 🔑  SHA-256 — deduplicação por conteúdo
# ==============================================================================
def sha256(path: Path) -> str:
    """Calcula hash SHA-256 de um arquivo em blocos (memory-safe)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65_536), b""):
            h.update(chunk)
    return h.hexdigest()


# ==============================================================================
# 🚜  MOTOR DE COLHEITA
# ==============================================================================
def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"SG04_harvest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    def log(msg: str) -> None:
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    log("\n" + "=" * 60)
    log("🚜  INICIANDO COLHEITA DE ASSETS (SG04 v2.0)")
    log("=" * 60)
    log(f"   PROJECT_ROOT   : {PROJECT_ROOT}")
    log(f"   WP_UPLOADS_DIR : {WP_UPLOADS_DIR}")
    log(f"   IMAGE_DEST     : {IMAGE_DEST}")
    log(f"   LOG            : {log_file}")
    log("=" * 60)

    # ------------------------------------------------------------------
    # FAIL-FAST — valida paths críticos
    # ------------------------------------------------------------------
    if not PROJECT_ROOT.exists():
        log(f"❌ FAIL-FAST: PROJECT_ROOT não existe: {PROJECT_ROOT}")
        sys.exit(1)

    if not WP_UPLOADS_DIR.exists():
        log(f"❌ FAIL-FAST: WP uploads não encontrado: {WP_UPLOADS_DIR}")
        log("   Execute primeiro: python3 pipeline/scripts/core/SG00b_prepare_wp.py")
        sys.exit(1)

    if not DIR_STATIC_SITE.exists():
        log(f"❌ FAIL-FAST: DIR_STATIC_SITE não existe: {DIR_STATIC_SITE}")
        sys.exit(1)

    # Garante destino
    IMAGE_DEST.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # COLHEITA
    # ------------------------------------------------------------------
    log("\n🔍 Vasculhando wp-content/uploads...")

    seen_hashes: dict[str, str] = {}   # sha256 → filename no destino
    stats = {
        "scanned": 0,
        "copied": 0,
        "deduplicated": 0,
        "skipped_thumb": 0,
        "skipped_audio": 0,
        "skipped_other": 0,
        "errors": 0,
    }

    for src in WP_UPLOADS_DIR.rglob("*"):
        if not src.is_file():
            continue

        stats["scanned"] += 1
        ext = src.suffix.lower()

        # 1. Bloqueio absoluto de áudio
        if ext in BLOCKED_EXTS:
            stats["skipped_audio"] += 1
            continue

        # 2. Apenas extensões permitidas
        if ext not in IMAGE_EXTS:
            stats["skipped_other"] += 1
            continue

        # 3. Ignora miniaturas WordPress
        if _WP_THUMB_RE.search(src.name):
            stats["skipped_thumb"] += 1
            continue

        # 4. Deduplicação SHA-256
        try:
            checksum = sha256(src)
        except OSError as e:
            log(f"   ⚠️  Erro ao ler {src.name}: {e}")
            stats["errors"] += 1
            continue

        if checksum in seen_hashes:
            stats["deduplicated"] += 1
            continue

        # 5. Cópia — resolve colisão de nome com sufixo hash
        dest_filename = src.name
        dest = IMAGE_DEST / dest_filename
        if dest.exists():
            # Arquivo diferente com mesmo nome → sufixo de 8 chars do hash
            stem, suffix = Path(dest_filename).stem, Path(dest_filename).suffix
            dest_filename = f"{stem}_{checksum[:8]}{suffix}"
            dest = IMAGE_DEST / dest_filename

        try:
            shutil.copy2(src, dest)
            seen_hashes[checksum] = dest_filename
            stats["copied"] += 1
        except OSError as e:
            log(f"   ⚠️  Erro ao copiar {src.name}: {e}")
            stats["errors"] += 1

    # ------------------------------------------------------------------
    # RELATÓRIO
    # ------------------------------------------------------------------
    final_count = sum(1 for f in IMAGE_DEST.iterdir() if f.is_file())
    total_size_mb = sum(
        f.stat().st_size for f in IMAGE_DEST.rglob("*") if f.is_file()
    ) / (1024 * 1024)

    log("\n" + "=" * 60)
    log("📊  RESUMO DA COLHEITA — SG04")
    log("=" * 60)
    log(f"   Arquivos varridos             : {stats['scanned']}")
    log(f"   ✅ Imagens copiadas           : {stats['copied']}")
    log(f"   ♻️  Deduplicadas (SHA-256)    : {stats['deduplicated']}")
    log(f"   🔇 Áudios bloqueados          : {stats['skipped_audio']}")
    log(f"   🖼️  Miniaturas WP ignoradas   : {stats['skipped_thumb']}")
    log(f"   ⏭️  Outros formatos ignorados  : {stats['skipped_other']}")
    log(f"   ❌ Erros                      : {stats['errors']}")
    log("-" * 60)
    log(f"   📁 Destino       : {IMAGE_DEST}")
    log(f"   📊 Total no dest : {final_count} arquivos")
    log(f"   💾 Tamanho total : {total_size_mb:.2f} MB")
    log("=" * 60)
    log(f"   📝 Log completo  : {log_file}")

    if stats["errors"] > 0:
        log(f"\n⚠️  {stats['errors']} erros encontrados. Revise o log acima.")
    else:
        log("\n✅ Colheita concluída sem erros!")

    log("\n▶️  Próximo passo:")
    log("   python3 pipeline/scripts/core/SD01_generate_asset_map.py")
    log("=" * 60 + "\n")


if __name__ == "__main__":
    main()
