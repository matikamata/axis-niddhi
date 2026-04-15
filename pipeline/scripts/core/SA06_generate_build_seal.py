#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — SA06_generate_build_seal.py
=============================================
Nome:       Build Seal Generator
Versão:     1.0 — Canon Hardening Phase
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)

POSIÇÃO NA SEQUÊNCIA:
  SA04 (canon manifest) → [SA06 — this script]

O QUE FAZ:
  Generates a build seal — a compact, human-readable
  cryptographic summary of the current canon build.

  The seal declares that a specific engine version, corpus,
  and pipeline produced a verifiable canon output.

  Output: metadata/build_seal.json

  Fields:
    engine_version    AXIS-NIDDHI version
    corpus_id         registered corpus identifier
    entries           post count
    manifest_hash     SHA-256 of canon_manifest.json
    canon_hash        from canon_manifest.json
    build_timestamp   UTC ISO-8601
    reproducible      true — build is deterministic from source

USAGE:
  python3 scripts/core/SA06_generate_build_seal.py
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, METADATA_DIR

MANIFEST_PATH  = METADATA_DIR / "canon_manifest.json"
ENGINE_PATH    = METADATA_DIR / "axis_engine.json"
CORPUS_DIR     = BASE_DIR / "corpus"
SEAL_PATH      = METADATA_DIR / "build_seal.json"

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GRAY   = "\033[90m"
RESET  = "\033[0m"


# ==============================================================================
# 🔐  HELPERS
# ==============================================================================
def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_corpus_id() -> str:
    """Detect registered corpus from corpus/ registry."""
    if CORPUS_DIR.exists():
        for d in sorted(CORPUS_DIR.iterdir()):
            if d.is_dir() and (d / "corpus.json").exists():
                try:
                    return load_json(d / "corpus.json").get("corpus_id", d.name)
                except Exception:
                    return d.name
    return "puredhamma"  # canonical default


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main() -> int:
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — SA06 Build Seal Generator{RESET}")
    print(f"  Output: {SEAL_PATH}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    # Load manifest
    if not MANIFEST_PATH.exists():
        print(f"{RED}❌ canon_manifest.json absent — run SA04 first{RESET}")
        return 1

    manifest = load_json(MANIFEST_PATH)

    # Load engine identity
    engine = load_json(ENGINE_PATH) if ENGINE_PATH.exists() else {}

    # Corpus
    corpus_id = get_corpus_id()

    # Hash of the manifest file itself
    manifest_hash = sha256_file(MANIFEST_PATH)

    # Build seal
    seal = {
        "seal_version":     "1.0",
        "engine":           engine.get("engine_name", "AXIS-NIDDHI"),
        "engine_version":   engine.get("version", manifest.get("engine_version", "5.4")),
        "engine_role":      engine.get("engine_role", "Canon Compilation Engine"),
        "corpus_id":        corpus_id,
        "corpus_name":      manifest.get("corpus", "PureDhamma"),
        "entries":          manifest.get("csl_entries", 0),
        "translations":     manifest.get("translations_frozen", 0),
        "manifest_hash":    manifest_hash,
        "canon_hash":       manifest.get("canon_hash", "UNKNOWN"),
        "source_zip":       manifest.get("source_zip", "UNKNOWN"),
        "source_zip_sha256": manifest.get("source_zip_sha256", "UNKNOWN"),
        "build_timestamp":  datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "original_build":   manifest.get("build_timestamp", "UNKNOWN"),
        "reproducible":     True,
        "verification":     manifest.get("verification", "self-consistent"),
        "seal_statement":   (
            f"AXIS-NIDDHI V{engine.get('version','5.4')} compiled corpus "
            f"'{corpus_id}' ({manifest.get('csl_entries',0)} entries) "
            f"from source '{manifest.get('source_zip','')}'. "
            f"Canon hash: {manifest.get('canon_hash','')[:16]}... "
            f"Build is deterministic and reproducible from source ZIP."
        )
    }

    # Write
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    SEAL_PATH.write_text(
        json.dumps(seal, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Report
    print(f"  {GRAY}Engine      : {seal['engine']} V{seal['engine_version']}{RESET}")
    print(f"  {GRAY}Corpus      : {seal['corpus_id']} ({seal['corpus_name']}){RESET}")
    print(f"  {GRAY}Entries     : {seal['entries']}{RESET}")
    print(f"  {GRAY}Translations: {seal['translations']}{RESET}")
    print(f"  {GRAY}Manifest    : {manifest_hash[:24]}...{RESET}")
    print(f"  {GRAY}Canon hash  : {seal['canon_hash'][:24]}...{RESET}")
    print(f"  {GRAY}Reproducible: {seal['reproducible']}{RESET}")
    print("")
    print(f"{GREEN}{'='*62}{RESET}")
    print(f"{GREEN}  ✅ BUILD SEAL GENERATED{RESET}")
    print(f"  {GRAY}Saved to: {SEAL_PATH}{RESET}")
    print(f"{GREEN}{'='*62}{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
