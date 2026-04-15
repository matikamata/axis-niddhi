#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SA02 Freeze Manifest
===============================================
Versão:   1.0 (AXIS-NIDDHI V5.1)
Objetivo: gerar hash global da CSL e registrar manifesto de imutabilidade.
          Apenas lê — nunca modifica arquivos de posts.

Saída: /beng-fut/pipeline/09-csl/manifest.json
"""

import sys
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import DIR_09_CSL, SCHEMA_VERSION

MANIFEST_PATH = DIR_09_CSL / "manifest.json"
_PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")

# Arquivos que participam do hash global (por post)
HASH_TARGETS = ["content.html", "semantic.json", "identity.json"]

GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RESET  = "\033[0m"


def sha256_path(path: Path) -> str | None:
    """Retorna SHA-256 hex de um arquivo, ou None se não existir."""
    if not path.exists():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_manifest() -> dict:
    posts = sorted(
        [d for d in DIR_09_CSL.iterdir() if d.is_dir() and _PDPN_RE.match(d.name)],
        key=lambda d: d.name,
    )

    total = len(posts)
    print(f"{CYAN}🔒 SA02 — Gerando manifesto de imutabilidade da CSL...{RESET}")
    print(f"   {GRAY}Posts PDPN encontrados: {total}{RESET}")

    # Acumular hashes de todos os posts em ordem determinística
    global_hasher = hashlib.sha256()
    post_hashes: dict[str, dict] = {}
    missing_files = 0

    for post_dir in posts:
        pdpn = post_dir.name
        per_post: dict[str, str | None] = {}

        for target in HASH_TARGETS:
            # Localização real dos arquivos na CSL schema 3.1:
            #   content.html  → source/en-US/content.html
            #   identity.json → meta/identity.json
            #   semantic.json → meta/semantic.json (ou source/en-US/)
            candidates = {
                "content.html":  [post_dir / "source" / "en-US" / "content.html"],
                "identity.json": [post_dir / "meta" / "identity.json"],
                "semantic.json": [
                    post_dir / "meta" / "semantic.json",
                    post_dir / "source" / "en-US" / "semantic.json",
                ],
            }.get(target, [post_dir / target])
            file_hash = None
            for c in candidates:
                file_hash = sha256_path(c)
                if file_hash:
                    break

            per_post[target] = file_hash
            if file_hash:
                global_hasher.update(f"{pdpn}:{target}:{file_hash}".encode())
            else:
                missing_files += 1

        post_hashes[pdpn] = per_post

    csl_hash = global_hasher.hexdigest()

    manifest = {
        "schema":       SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_posts":  total,
        "csl_hash":     csl_hash,
        "missing_files": missing_files,
        "post_hashes":  post_hashes,
    }

    return manifest


def main():
    if not DIR_09_CSL.exists():
        print(f"\033[91m❌ CSL não encontrada: {DIR_09_CSL}{RESET}")
        sys.exit(1)

    manifest = build_manifest()

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"{GREEN}✅ manifest.json gerado:{RESET}")
    print(f"   {GRAY}Posts:    {manifest['total_posts']}{RESET}")
    print(f"   {GRAY}Hash CSL: {manifest['csl_hash'][:16]}...{RESET}")
    print(f"   {GRAY}Schema:   {manifest['schema']}{RESET}")
    if manifest["missing_files"]:
        print(f"   {YELLOW}⚠️  Arquivos ausentes: {manifest['missing_files']}{RESET}")
    print(f"   {GRAY}Salvo em: {MANIFEST_PATH}{RESET}")


if __name__ == "__main__":
    main()
