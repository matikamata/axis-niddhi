#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SA03 Translation Progress
====================================================
Versão:   1.0 (AXIS-NIDDHI V5.1)
Objetivo: medir progresso de tradução PT-BR da CSL.
          Apenas lê — nunca modifica arquivos.

Saída: /beng-fut/pipeline/metadata/translation_status.json
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DIR_09_CSL, METADATA_DIR

STATUS_PATH = METADATA_DIR / "translation_status.json"
_PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")

GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
BLUE   = "\033[94m"
RESET  = "\033[0m"


def has_pt_title(identity: dict) -> bool:
    # Tenta root-level titles.pt (schema 3.1 canônico)
    pt = identity.get("titles", {}).get("pt")
    if pt and str(pt).strip():
        return True
    # Fallback: alguns posts têm estrutura identity.identity.titles (legado)
    pt = identity.get("identity", {}).get("titles", {}).get("pt")
    return bool(pt and str(pt).strip())


def has_pt_content(post_dir: Path) -> bool:
    pt_html = post_dir / "source" / "pt-BR" / "content.html"
    if not pt_html.exists():
        return False
    # Arquivo existe mas pode estar vazio
    return pt_html.stat().st_size > 100


def main():
    if not DIR_09_CSL.exists():
        print(f"\033[91m❌ CSL não encontrada: {DIR_09_CSL}{RESET}")
        sys.exit(1)

    posts = sorted(
        [d for d in DIR_09_CSL.iterdir() if d.is_dir() and _PDPN_RE.match(d.name)],
        key=lambda d: d.name,
    )

    total          = len(posts)
    with_pt_title   = 0
    with_pt_content = 0
    both            = 0

    for post_dir in posts:
        identity_path = post_dir / "meta" / "identity.json"
        identity = {}
        if identity_path.exists():
            try:
                identity = json.loads(identity_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        title_ok   = has_pt_title(identity)
        content_ok = has_pt_content(post_dir)

        if title_ok:
            with_pt_title += 1
        if content_ok:
            with_pt_content += 1
        if title_ok and content_ok:
            both += 1

    # "Traduzido" = tem conteúdo PT (critério principal)
    translated  = with_pt_content
    missing     = total - translated
    progress    = round((translated / total * 100), 2) if total else 0.0

    status = {
        "generated_at":    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_posts":     total,
        "translated_pt":   translated,
        "with_pt_title":   with_pt_title,
        "fully_complete":  both,
        "missing_pt":      missing,
        "progress_percent": progress,
    }

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(
        json.dumps(status, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Terminal output
    bar_filled = int(progress / 5)   # 20-char bar
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    print(f"\n{CYAN}Translation Progress{RESET}")
    print(f"{GRAY}{'─' * 40}{RESET}")
    print(f"  Total posts  : {BLUE}{total}{RESET}")
    print(f"  PT content   : {GREEN}{translated}{RESET}")
    print(f"  PT title     : {GREEN}{with_pt_title}{RESET}")
    print(f"  Fully done   : {GREEN}{both}{RESET}")
    print(f"  Missing      : {YELLOW}{missing}{RESET}")
    print(f"  Progress     : {GREEN}{progress}%{RESET}  [{bar}]")
    print(f"{GRAY}  Salvo em: {STATUS_PATH}{RESET}\n")


if __name__ == "__main__":
    main()
