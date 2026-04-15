#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SCRIPT S03b
=====================================
Nome:       Asset Harvester (A Colheitadeira)
Versão:     1.0 — AXIS-NIDDHI Edition
Autor:      Aethel & The Orchestra
Data:       2026-03-06

OBJETIVO:
Vasculhar o WordPress extraído (runtime_wp/wp-content/uploads),
encontrar todos os áudios e imagens originais do Prof. Lal, e
copiá-los para as pastas definitivas do pipeline.

Isso garante que o .ZIP seja a ÚNICA fonte da verdade, eliminando
a necessidade de copiar mídias de backups antigos manualmente.
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

# ==============================================================================
# ⚙️ CONFIGURAÇÃO — via config.py canônico (AXIS-NIDDHI V5.4 hardening)
# ==============================================================================

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, DIR_09_CSL, DIR_STATIC_SITE, LOG_DIR

BENG_ROOT      = BASE_DIR.parent
WP_UPLOADS_DIR = BENG_ROOT / "wordpress" / "runtime_wp" / "wp-content" / "uploads"

# Destinos no Pipeline — derivados de config.py
AUDIO_DEST = DIR_09_CSL / "meta" / "pronunciation"
IMAGE_DEST = DIR_STATIC_SITE / "assets" / "images"
# LOG_DIR já importado de config

AUDIO_EXTS = {".mp3", ".wav", ".ogg"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf"} # PDF entra como doc estático

# ==============================================================================
# 🚀 MOTOR DE COLHEITA
# ==============================================================================
def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"S03b_harvest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def log(msg):
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    log("\n" + "="*60)
    log("🚜 INICIANDO COLHEITA DE ASSETS (S03b)")
    log("="*60)

    if not WP_UPLOADS_DIR.exists():
        log(f"❌ ERRO: Pasta de uploads do WP não encontrada: {WP_UPLOADS_DIR}")
        log("   O reset.sh extraiu o ZIP corretamente?")
        sys.exit(1)

    AUDIO_DEST.mkdir(parents=True, exist_ok=True)
    IMAGE_DEST.mkdir(parents=True, exist_ok=True)

    count_audio = 0
    count_image = 0

    log("🔍 Vasculhando wp-content/uploads...")

    # rglob vasculha todas as subpastas (2014/, 2015/, etc)
    for file_path in WP_UPLOADS_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()
        
        # Ignorar miniaturas geradas pelo WP (ex: imagem-150x150.jpg)
        if re.search(r'-\d+x\d+\.(jpg|jpeg|png|gif|webp)$', file_path.name, re.IGNORECASE):
            continue

        if ext in AUDIO_EXTS:
            dest = AUDIO_DEST / file_path.name
            if not dest.exists() or file_path.stat().st_mtime > dest.stat().st_mtime:
                shutil.copy2(file_path, dest)
            count_audio += 1

        elif ext in IMAGE_EXTS:
            dest = IMAGE_DEST / file_path.name
            if not dest.exists() or file_path.stat().st_mtime > dest.stat().st_mtime:
                shutil.copy2(file_path, dest)
            count_image += 1

    log("\n" + "="*60)
    log("📊 RESUMO DA COLHEITA")
    log("="*60)
    log(f"🎵 Áudios colhidos : {count_audio} -> {AUDIO_DEST}")
    log(f"🖼️  Imagens colhidas: {count_image} -> {IMAGE_DEST}")
    log("✅ Colheita concluída com sucesso!")
    log("="*60 + "\n")

if __name__ == "__main__":
    import re
    main()
