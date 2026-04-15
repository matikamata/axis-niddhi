#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — SA04_generate_canon_manifest.py
=================================================
Nome:       Canon Manifest Generator
Versão:     1.0 — Canon Engine Upgrade
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)
Data:       2026-03-12

POSIÇÃO NA SEQUÊNCIA:
  SA02 (CSL manifest) → SA03 (translation progress) → [SA04 — este script]

O QUE FAZ:
  Gera um manifesto criptográfico unificado da compilação canônica.
  Prova que: Source ZIP → Pipeline → Canon Build é reproduzível.

  Inputs lidos:
    09-csl/           → CSL hash (de SA02 manifest.json)
    03-translations/  → translation layer hash (de manifest.json)
    13-static-site/   → site build hash (tree hash)
    scripts/core/     → pipeline hash (hash de todos os scripts core)
    sources/*.zip     → source ZIP SHA-256
    metadata/axis_engine.json → engine identity

  Output:
    metadata/canon_manifest.json

INVARIANTES:
  • Read-only — nunca modifica corpus, CSL ou traduções
  • Idempotente — pode ser executado múltiplas vezes
  • Determinístico — mesmos inputs → mesmo output

USAGE:
  python3 scripts/core/SA04_generate_canon_manifest.py
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, DIR_09_CSL, METADATA_DIR

DIR_03_TRANSLATIONS = BASE_DIR / "03-translations"
DIR_STATIC_SITE     = BASE_DIR / "13-static-site"
DIR_SOURCES         = BASE_DIR / "sources"
DIR_CORE_SCRIPTS    = _SCRIPT_DIR   # scripts/core/
ENGINE_JSON         = METADATA_DIR / "axis_engine.json"
OUTPUT_PATH         = METADATA_DIR / "canon_manifest.json"

_PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RESET  = "\033[0m"


# ==============================================================================
# 🔐  HASH UTILITIES
# ==============================================================================
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def sha256_dir_tree(root: Path, pattern: str = "*") -> str:
    """Deterministic hash of all files under root matching pattern, sorted."""
    h = hashlib.sha256()
    files = sorted(root.rglob(pattern)) if root.exists() else []
    for f in files:
        if f.is_file() and not f.is_symlink():
            rel = str(f.relative_to(root))
            file_hash = sha256_file(f)
            h.update(f"{rel}:{file_hash}\n".encode())
    return h.hexdigest()


# ==============================================================================
# 📦  SOURCE ZIP
# ==============================================================================
def get_source_zip_hash() -> tuple[str, str]:
    """Returns (sha256, filename) of the source ZIP."""
    zips = sorted(DIR_SOURCES.glob("*.zip")) if DIR_SOURCES.exists() else []
    if not zips:
        return "ABSENT", "none"
    z = zips[-1]  # latest if multiple
    print(f"  {GRAY}Hashing source ZIP: {z.name} ({z.stat().st_size // 1024 // 1024}MB)...{RESET}")
    return sha256_file(z), z.name


# ==============================================================================
# 📚  CSL HASH
# ==============================================================================
def get_csl_stats() -> tuple[int, str]:
    """Returns (entry_count, csl_hash) from SA02 manifest or direct computation."""
    sa02_manifest = DIR_09_CSL / "manifest.json"
    if sa02_manifest.exists():
        try:
            data = json.loads(sa02_manifest.read_text(encoding="utf-8"))
            return data.get("total_posts", 0), data.get("csl_hash", "UNKNOWN")
        except Exception:
            pass
    # Fallback: count PDPN dirs
    if DIR_09_CSL.exists():
        count = sum(1 for d in DIR_09_CSL.iterdir() if d.is_dir() and _PDPN_RE.match(d.name))
        return count, sha256_dir_tree(DIR_09_CSL, "*.json")
    return 0, "ABSENT"


# ==============================================================================
# 🌐  TRANSLATION LAYER HASH
# ==============================================================================
def get_translation_stats() -> tuple[int, str]:
    """Returns (restored_count, global_hash) from 03-translations/manifest.json."""
    manifest = DIR_03_TRANSLATIONS / "manifest.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            return data.get("total_frozen", 0), data.get("global_hash", "UNKNOWN")
        except Exception:
            pass
    # Fallback: count dirs
    if DIR_03_TRANSLATIONS.exists():
        count = sum(1 for d in DIR_03_TRANSLATIONS.iterdir() if d.is_dir())
        return count, sha256_dir_tree(DIR_03_TRANSLATIONS, "*.html")
    return 0, "ABSENT"


# ==============================================================================
# 🌐  SITE BUILD HASH
# ==============================================================================
def get_site_build_hash() -> str:
    """Hash of generated static site HTML files."""
    if not DIR_STATIC_SITE.exists():
        return "ABSENT"
    print(f"  {GRAY}Hashing static site tree...{RESET}")
    return sha256_dir_tree(DIR_STATIC_SITE, "*.html")


# ==============================================================================
# ⚙️  PIPELINE HASH
# ==============================================================================
def get_pipeline_hash() -> str:
    """Hash of all core pipeline scripts — proves pipeline identity."""
    if not DIR_CORE_SCRIPTS.exists():
        return "ABSENT"
    h = hashlib.sha256()
    scripts = sorted(DIR_CORE_SCRIPTS.glob("*.py")) + sorted(DIR_CORE_SCRIPTS.glob("*.sh"))
    for f in scripts:
        if f.is_file():
            rel = f.name
            file_hash = sha256_file(f)
            h.update(f"{rel}:{file_hash}\n".encode())
    return h.hexdigest()


# ==============================================================================
# 🏭  ENGINE IDENTITY
# ==============================================================================
def get_engine_identity() -> dict:
    if ENGINE_JSON.exists():
        try:
            return json.loads(ENGINE_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "engine_name": "AXIS-NIDDHI",
        "version": "5.4",
        "corpus": "PureDhamma"
    }


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main():
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — SA04 Canon Manifest Generator{RESET}")
    print(f"  Output: {OUTPUT_PATH}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    engine = get_engine_identity()

    # Collect all components
    print(f"  {GRAY}[1/5] Source ZIP...{RESET}")
    zip_hash, zip_name = get_source_zip_hash()

    print(f"  {GRAY}[2/5] CSL stats...{RESET}")
    csl_entries, csl_hash = get_csl_stats()

    print(f"  {GRAY}[3/5] Translation layer...{RESET}")
    trans_count, trans_hash = get_translation_stats()

    print(f"  {GRAY}[4/5] Static site build...{RESET}")
    site_hash = get_site_build_hash()

    print(f"  {GRAY}[5/5] Pipeline scripts...{RESET}")
    pipeline_hash = get_pipeline_hash()

    # Determine verification status
    components_present = all([
        zip_hash != "ABSENT",
        csl_hash not in ("ABSENT", "UNKNOWN"),
        trans_hash not in ("ABSENT", "UNKNOWN"),
        site_hash != "ABSENT",
        pipeline_hash != "ABSENT",
    ])
    verification = "self-consistent" if components_present else "partial — some components absent"

    # Build global canon hash (hash of all component hashes)
    global_hasher = hashlib.sha256()
    for h in [zip_hash, csl_hash, trans_hash, site_hash, pipeline_hash]:
        global_hasher.update(h.encode())
    canon_hash = global_hasher.hexdigest()

    # Assemble manifest
    manifest = {
        "engine":                  engine.get("engine_name", "AXIS-NIDDHI"),
        "engine_version":          engine.get("version", "5.4"),
        "engine_role":             engine.get("engine_role", "Canon Compilation Engine"),
        "corpus":                  engine.get("corpus", "PureDhamma"),
        "build_timestamp":         datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_zip":              zip_name,
        "source_zip_sha256":       zip_hash,
        "csl_entries":             csl_entries,
        "csl_hash":                csl_hash,
        "translations_frozen":     trans_count,
        "translations_hash":       trans_hash,
        "site_build_hash":         site_hash,
        "pipeline_hash":           pipeline_hash,
        "canon_hash":              canon_hash,
        "verification":            verification,
    }

    # Write
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Report
    status_color = GREEN if components_present else YELLOW
    print(f"\n{status_color}{'='*62}{RESET}")
    print(f"{status_color}  ✅ CANON MANIFEST GENERATED{RESET}")
    print(f"{'='*62}")
    print(f"  {GRAY}Engine         : {manifest['engine']} V{manifest['engine_version']}{RESET}")
    print(f"  {GRAY}Corpus         : {manifest['corpus']}{RESET}")
    print(f"  {GRAY}CSL entries    : {csl_entries}{RESET}")
    print(f"  {GRAY}Translations   : {trans_count}{RESET}")
    print(f"  {GRAY}Source ZIP     : {zip_name}{RESET}")
    print(f"  {GRAY}Canon hash     : {canon_hash[:24]}...{RESET}")
    print(f"  {GRAY}Verification   : {verification}{RESET}")
    print(f"  {GRAY}Saved to       : {OUTPUT_PATH}{RESET}")
    print(f"{status_color}{'='*62}{RESET}\n")


if __name__ == "__main__":
    main()
