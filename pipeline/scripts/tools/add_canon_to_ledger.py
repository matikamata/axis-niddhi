#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — add_canon_to_ledger.py
========================================
Nome:       Canon Ledger Entry Writer
Versão:     1.0 — Canon Ledger Phase
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)

PURPOSE:
  Register a canon release into the immutable ledger.

  Reads from:
    metadata/canon_manifest.json
    metadata/build_seal.json
    seeds/<corpus_id>_seed/seed_manifest.json

  Writes:
    ledger/entries/<canon_id>.json   ← individual entry
    ledger/ledger.json               ← appends canon_id (if not present)

  Ledger is append-only. Existing entries are never modified.

USAGE:
  python3 scripts/tools/add_canon_to_ledger.py
  python3 scripts/tools/add_canon_to_ledger.py --tag puredhamma-v1
  python3 scripts/tools/add_canon_to_ledger.py --tag puredhamma-v1 --corpus puredhamma
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
# scripts/tools/ → scripts/ → pipeline/
_PIPELINE_DIR = _SCRIPT_DIR.parent.parent
_CORE_DIR = _SCRIPT_DIR.parent / "core"
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from config import BASE_DIR, METADATA_DIR

LEDGER_DIR        = BASE_DIR / "ledger"
LEDGER_ENTRIES    = LEDGER_DIR / "entries"
LEDGER_JSON       = LEDGER_DIR / "ledger.json"

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


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def init_ledger() -> dict:
    """Initialize ledger.json if absent."""
    if LEDGER_JSON.exists():
        return load_json(LEDGER_JSON)
    ledger = {
        "axis_engine":  "AXIS-NIDDHI",
        "version":      1,
        "created":      datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entries":      []
    }
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_ENTRIES.mkdir(parents=True, exist_ok=True)
    save_json(LEDGER_JSON, ledger)
    return ledger


# ==============================================================================
# 📋  BUILD ENTRY
# ==============================================================================
def build_entry(tag: str, corpus_id: str) -> dict:
    """Assemble a ledger entry from live metadata."""
    manifest_path = METADATA_DIR / "canon_manifest.json"
    seal_path     = METADATA_DIR / "build_seal.json"
    seed_path     = BASE_DIR / "seeds" / f"{corpus_id}_seed" / "seed_manifest.json"

    # Require manifest + seal
    for p in [manifest_path, seal_path]:
        if not p.exists():
            print(f"{RED}❌ Required file absent: {p}{RESET}")
            print("   Run: axis build")
            sys.exit(1)

    manifest = load_json(manifest_path)
    seal     = load_json(seal_path)

    # Seed is optional — enrich if present
    seed_integrity_hash = "ABSENT"
    seed_hash           = "ABSENT"
    if seed_path.exists():
        seed = load_json(seed_path)
        seed_integrity_hash = seed.get("seed_integrity_hash", "ABSENT")
        seed_hash           = sha256_file(seed_path)
    else:
        print(f"  {YELLOW}⚠ Seed absent at {seed_path} — entry registered without seed hashes{RESET}")

    # Entry-level integrity hash: hash of canon_hash + seed_integrity_hash + tag
    entry_hasher = hashlib.sha256()
    entry_hasher.update(manifest.get("canon_hash", "").encode())
    entry_hasher.update(seed_integrity_hash.encode())
    entry_hasher.update(tag.encode())
    entry_hash = entry_hasher.hexdigest()

    entry = {
        "canon_id":           tag,
        "corpus_id":          corpus_id,
        "corpus_name":        manifest.get("corpus", "PureDhamma"),
        "engine":             manifest.get("engine", "AXIS-NIDDHI"),
        "engine_version":     manifest.get("engine_version", "5.4"),
        "entries":            manifest.get("csl_entries", 0),
        "translations":       manifest.get("translations_frozen", 0),
        "languages":          ["en", "pt-BR"],
        "source_zip":         manifest.get("source_zip", "UNKNOWN"),
        "source_zip_sha256":  manifest.get("source_zip_sha256", "UNKNOWN"),
        "canon_hash":         manifest.get("canon_hash", "UNKNOWN"),
        "csl_hash":           manifest.get("csl_hash", "UNKNOWN"),
        "translations_hash":  manifest.get("translations_hash", "UNKNOWN"),
        "pipeline_hash":      manifest.get("pipeline_hash", "UNKNOWN"),
        "manifest_hash":      sha256_file(manifest_path),
        "build_seal_hash":    sha256_file(seal_path),
        "seed_integrity_hash": seed_integrity_hash,
        "seed_file_hash":     seed_hash,
        "build_timestamp":    seal.get("build_timestamp", "UNKNOWN"),
        "registered":         datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reproducible":       seal.get("reproducible", True),
        "entry_hash":         entry_hash,
    }
    return entry


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Add canon release to ledger")
    parser.add_argument("--tag",    default="puredhamma-v1", help="Release tag (e.g. puredhamma-v1)")
    parser.add_argument("--corpus", default="puredhamma",    help="Corpus ID (e.g. puredhamma)")
    args = parser.parse_args()

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — Canon Ledger Entry Writer{RESET}")
    print(f"  Tag    : {args.tag}")
    print(f"  Corpus : {args.corpus}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    # Init ledger
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_ENTRIES.mkdir(parents=True, exist_ok=True)
    ledger = init_ledger()

    # Check for duplicate
    entry_path = LEDGER_ENTRIES / f"{args.tag}.json"
    if entry_path.exists():
        existing = load_json(entry_path)
        print(f"  {YELLOW}⚠ Entry already exists: {args.tag}{RESET}")
        print(f"     canon_hash : {existing.get('canon_hash','')[:24]}...")
        print(f"     registered : {existing.get('registered','')}")
        print(f"\n  Ledger is append-only. Use a new tag to add a different release.")
        print(f"  Existing entry preserved.\n")
        return

    # Build entry
    print(f"  {GRAY}Building entry from live metadata...{RESET}")
    entry = build_entry(args.tag, args.corpus)

    # Write entry file
    save_json(entry_path, entry)
    print(f"  {GREEN}✔ Entry written: {entry_path}{RESET}")

    # Append to ledger.json (only if not already listed)
    if args.tag not in ledger["entries"]:
        ledger["entries"].append(args.tag)
        ledger["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ledger["entry_count"]  = len(ledger["entries"])
        save_json(LEDGER_JSON, ledger)
        print(f"  {GREEN}✔ Appended to ledger.json (entry #{len(ledger['entries'])}){RESET}")

    # Report
    print(f"\n{GREEN}{'='*62}{RESET}")
    print(f"{GREEN}  ✅ CANON REGISTERED IN LEDGER{RESET}")
    print(f"{'='*62}")
    print(f"  {GRAY}canon_id     : {entry['canon_id']}{RESET}")
    print(f"  {GRAY}corpus       : {entry['corpus_id']} ({entry['corpus_name']}){RESET}")
    print(f"  {GRAY}entries      : {entry['entries']}{RESET}")
    print(f"  {GRAY}canon_hash   : {entry['canon_hash'][:24]}...{RESET}")
    print(f"  {GRAY}entry_hash   : {entry['entry_hash'][:24]}...{RESET}")
    print(f"  {GRAY}seed_hash    : {entry['seed_integrity_hash'][:24]}...{RESET}")
    print(f"  {GRAY}registered   : {entry['registered']}{RESET}")
    print(f"{GREEN}{'='*62}{RESET}\n")


if __name__ == "__main__":
    main()
