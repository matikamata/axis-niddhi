#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SD03_static_site_build.py
====================================================
Versão:  AXIS-NIDDHI V5.4 (Compatibility Shim)
Data:    2026-03-11

FUNÇÃO:
  Wrapper de compatibilidade — permite que run_full_pipeline.sh
  chame 'python3 SD03_static_site_build.py' dentro de 13-ssg/.

  O engine real está em build.py (mesma pasta após deploy por
  setup_v54_static_site.sh). Este shim garante que a chamada
  funcione mesmo que build.py seja o nome canônico no repositório.

DEPLOY:
  Este arquivo é copiado para 13-ssg/SD03_static_site_build.py
  pelo setup_v54_static_site.sh (junto com build.py).
  Ambos devem coexistir em 13-ssg/.

USO DIRETO (emergência):
  python3 SD03_static_site_build.py   → mesmo que python3 build.py

NEVER EDIT THIS SHIM — edite build.py diretamente.
"""

import sys
import runpy
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_BUILD = _HERE / "build.py"

if not _BUILD.exists():
    print(f"\n❌ [SD03 SHIM] build.py não encontrado em {_HERE}", file=sys.stderr)
    print(f"   Execute setup_v54_static_site.sh antes de usar SD03.", file=sys.stderr)
    sys.exit(1)

# Executa build.py no mesmo namespace — equivalente a 'python3 build.py'
runpy.run_path(str(_BUILD), run_name="__main__")
