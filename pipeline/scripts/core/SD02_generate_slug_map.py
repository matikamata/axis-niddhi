#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — S13_generate_slug_map.py
===================================================
Nome:      Gerador de Slug Map (Semantic Layer)
Versão:    1.1  — AXIS-NIDDHI Hardening Edition
Sequência: S13 → roda após S12b; obrigatório antes de S14
Revisado:  2026-03-05 (Hardening Pass)

FUNÇÃO: Varre a CSL e gera slug_map.json — mapa canônico de
        PDPN → slug para resolução de links internos no SSG.
INPUT:  09-csl/*/meta/identity.json
OUTPUT: 15-semantic/slug_map.json

HARDENING PASS — AXIS-NIDDHI (2026-03-05)
  ★ Removido: BASE_DIR = Path(__file__).parent.parent  ← derivação frágil
  ★ Removido: CSL_DIR  = BASE_DIR / "09-csl"           ← hardcode relativo
  ★ Removido: OUTPUT_DIR = Path(__file__).parent       ← hardcode posicional
  ★ Adicionado: import de DIR_09_CSL e DIR_15_SEMANTIC via config.py
  ★ Lógica de scan/resolve inalterada.

⚠️  DEPRECATION NOTICE
  A geração interna de slug_map foi absorvida por S15_build.py (Phase 2/8).
  Este script permanece para auditoria isolada e CI checks.
  Em builds normais, S15_build.py é a fonte autoritativa.

DEPENDÊNCIA CRÍTICA: S14 (build.py) falha sem este arquivo.
USO: python3 S13_generate_slug_map.py
"""

import sys
import json
import logging
from pathlib import Path

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent / "scripts"))

from config import DIR_09_CSL, DIR_15_SEMANTIC

CSL_DIR    = DIR_09_CSL        # /beng/pipeline/09-csl
OUTPUT_DIR = DIR_15_SEMANTIC   # /beng/pipeline/15-semantic

# ==============================================================================
# 🔧  LOGGING
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("S13_generate_slug_map")

# ==============================================================================
# 🔍  SCANNER / RESOLVER
# ==============================================================================
# Add src to path for scanner and resolver modules (relative to this script)
sys.path.append(str(_SCRIPT_DIR))

from src.scanner  import scan_slugs
from src.resolver import resolve_collisions


def main() -> None:
    logger.info("🚀 Starting S13: Slug Map Generator")

    if not CSL_DIR.exists():
        logger.error(f"CSL not found at {CSL_DIR}")
        sys.exit(1)

    # 1. Scan
    slug_groups = scan_slugs(CSL_DIR)
    logger.info(f"Found {len(slug_groups)} unique slug roots.")

    # 2. Resolve collisions
    slug_map, collision_report = resolve_collisions(slug_groups)

    # 3. Save artifacts
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    map_path = OUTPUT_DIR / "slug_map.json"
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(slug_map, f, indent=2, sort_keys=True)

    report_path = OUTPUT_DIR / "collision_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(collision_report, f, indent=2, sort_keys=True)

    # 4. Summary
    collisions_count = len(collision_report)
    renamed_count    = sum(len(e["renamed"]) for e in collision_report.values())

    print("\n" + "=" * 40)
    print("🧠 SEMANTIC ANALYSIS SUMMARY")
    print("=" * 40)
    print(f"Total Posts:      {len(slug_map)}")
    print(f"Collisions:       {collisions_count}")
    print(f"Renamed Slugs:    {renamed_count}")
    print("-" * 40)
    print(f"✅ Generated: {map_path}")
    print(f"✅ Generated: {report_path}")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    main()
