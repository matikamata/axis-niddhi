#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — anchor_manifest.py
=====================================
Versão:  1.0  —  Archaeological Anchor Layer
Data:    2026-03-12
Autores: Aloka + Vayo (AXIS-NIDDHI Architectural Session)

PURPOSE
-------
Generate a timestamped anchor record containing the SHA-256 hash of the
canonical release manifest and store it under:

    /beng-fut/pipeline/archaeology/anchors/

An anchor record is a lightweight, standalone JSON document that encodes:
  - the SHA-256 of the release manifest (the "hash of the seal")
  - the engine and corpus identity
  - the seal timestamp of the release being anchored
  - the timestamp at which the anchor was created

WHAT THIS PROVIDES
------------------
The release manifest (release-manifest.sha256) seals 208 files.
The anchor record seals the manifest itself.

This creates a two-level verification chain:

    208 files  →  release-manifest.sha256  →  anchor_YYYYMMDD_HHMMSS.json
                      (sealed by manifest)       (sealed by anchor hash)

The anchor hash can optionally be published in:
  - GitHub commit messages or release notes
  - Zenodo dataset descriptions
  - Any external repository or public record

A future operator who holds only the anchor hash can verify the entire
release by checking: sha256(release-manifest.sha256) == anchor.manifest_hash

WHAT THIS DOES NOT DO
---------------------
- Does not modify the release in /beng-release/
- Does not modify any pipeline script or CSL entry
- Does not require network access
- Does not alter the V5.4 frozen baseline in any way

This script is purely additive. It reads one file and writes one file.

USAGE
-----
    python3 scripts/anchor_manifest.py

    # With explicit release path:
    python3 scripts/anchor_manifest.py --release /beng-release

    # Dry run (show what would be written, write nothing):
    python3 scripts/anchor_manifest.py --dry-run

EXIT CODES
----------
    0  — anchor created successfully
    1  — manifest not found or unreadable
    2  — anchor directory not writable
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Import pipeline utilities (sha256_file, atomic_write_json, get_utc_now) ──
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from pipeline_utils import sha256_file, atomic_write_json, get_utc_now
except ImportError as e:
    print(f"❌  Cannot import pipeline_utils: {e}", file=sys.stderr)
    print(f"    Expected at: {_SCRIPT_DIR / 'pipeline_utils.py'}", file=sys.stderr)
    sys.exit(1)

try:
    from config import BASE_DIR
except ImportError:
    # Graceful fallback if config is not importable from this context
    BASE_DIR = _SCRIPT_DIR.parent


# ==============================================================================
# CONSTANTS
# ==============================================================================

# Canonical manifest filename (V5.4 standard)
MANIFEST_FILENAME  = "release-manifest.sha256"
MANIFEST_FALLBACK  = "manifest.sha256"          # accept legacy name if present

# Anchor storage — inside the Lab, never inside /beng-release/
ANCHOR_DIR         = BASE_DIR / "archaeology" / "anchors"


# ==============================================================================
# CORE LOGIC
# ==============================================================================

def find_manifest(release_root: Path) -> Path:
    """
    Locate the release manifest. Tries canonical name first, then fallback.
    Raises FileNotFoundError with a clear message if neither exists.
    """
    canonical = release_root / MANIFEST_FILENAME
    if canonical.exists():
        return canonical

    fallback = release_root / MANIFEST_FALLBACK
    if fallback.exists():
        print(f"⚠️   Using fallback manifest name: {MANIFEST_FALLBACK}", file=sys.stderr)
        print(f"    Canonical name is: {MANIFEST_FILENAME}", file=sys.stderr)
        return fallback

    raise FileNotFoundError(
        f"Manifest not found in {release_root}\n"
        f"  Tried: {MANIFEST_FILENAME}\n"
        f"  Tried: {MANIFEST_FALLBACK}\n"
        f"  Run build_release_snapshot_v4.sh first."
    )


def read_seal_metadata(release_root: Path) -> dict:
    """
    Read release-sealed-at.txt to extract corpus identity and original seal time.
    Returns a dict with whatever fields are present; empty dict if file absent.
    The anchor is valid without this data — it is enrichment only.
    """
    seal_file = release_root / "release-sealed-at.txt"
    if not seal_file.exists():
        return {}

    metadata = {}
    for line in seal_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip().lower()] = value.strip()
    return metadata


def build_anchor(manifest_path: Path, seal_meta: dict) -> dict:
    """
    Construct the anchor record dict.
    The manifest_sha256 field is the core of the anchor — everything else
    is enrichment metadata to aid future operators.
    """
    manifest_hash = sha256_file(manifest_path)
    if manifest_hash is None:
        raise IOError(f"Could not compute SHA-256 for {manifest_path}")

    # Count lines in manifest = number of sealed files
    lines = [l for l in manifest_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    sealed_file_count = len(lines)

    return {
        # ── Core anchor fields (verification-critical) ──────────────────────
        "manifest_sha256":   manifest_hash,
        "manifest_filename": manifest_path.name,
        "manifest_path":     str(manifest_path),
        "sealed_files":      sealed_file_count,
        "anchored_at":       get_utc_now(),

        # ── Enrichment from release-sealed-at.txt ───────────────────────────
        "engine":            seal_meta.get("engine",    "AXIS-NIDDHI V5.4"),
        "corpus":            seal_meta.get("corpus",    "PureDhamma"),
        "release_sealed_at": seal_meta.get("sealed_at", "unknown"),

        # ── Verification instructions (for future operators) ─────────────────
        "_verify": (
            "sha256sum of the manifest file must equal manifest_sha256. "
            "Command: sha256sum release-manifest.sha256 | awk '{print $1}'"
        ),
    }


def write_anchor(anchor: dict, anchor_dir: Path, dry_run: bool) -> Path:
    """
    Write the anchor record to a timestamped JSON file.
    Uses atomic_write_json (temp + rename) for crash safety.
    """
    # Filename: anchor_YYYYMMDD_HHMMSS.json — one per run, never overwritten
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    anchor_path = anchor_dir / f"anchor_{ts}.json"

    if dry_run:
        print("\n── DRY RUN — would write ──────────────────────────────────")
        print(f"  Path: {anchor_path}")
        print(f"  Content:\n{json.dumps(anchor, indent=2, ensure_ascii=False)}")
        print("────────────────────────────────────────────────────────────\n")
        return anchor_path

    anchor_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(anchor_path, anchor)
    return anchor_path


# ==============================================================================
# MAIN
# ==============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate an archaeological anchor record for the canonical release manifest.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--release",
        type=Path,
        default=Path("/beng-release"),
        help="Path to the release root directory (default: /beng-release)",
    )
    parser.add_argument(
        "--anchor-dir",
        type=Path,
        default=ANCHOR_DIR,
        help=f"Directory to store anchor records (default: {ANCHOR_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without writing anything.",
    )
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  💎 AXIS-NIDDHI — Manifest Anchor Generator V1.0        ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # ── 1. Locate manifest ───────────────────────────────────────────────────
    try:
        manifest_path = find_manifest(args.release)
        print(f"  ✔ Manifest found:  {manifest_path}")
    except FileNotFoundError as e:
        print(f"\n❌  {e}", file=sys.stderr)
        return 1

    # ── 2. Read release seal metadata ────────────────────────────────────────
    seal_meta = read_seal_metadata(args.release)
    if seal_meta:
        print(f"  ✔ Release metadata: {seal_meta.get('engine','?')} · "
              f"{seal_meta.get('corpus','?')} · sealed {seal_meta.get('sealed_at','?')}")
    else:
        print("  ⚠  release-sealed-at.txt not found — anchor will use defaults")

    # ── 3. Build anchor record ───────────────────────────────────────────────
    try:
        anchor = build_anchor(manifest_path, seal_meta)
        print(f"  ✔ Manifest SHA-256: {anchor['manifest_sha256']}")
        print(f"  ✔ Sealed files:     {anchor['sealed_files']}")
    except IOError as e:
        print(f"\n❌  {e}", file=sys.stderr)
        return 1

    # ── 4. Write anchor record ───────────────────────────────────────────────
    try:
        anchor_path = write_anchor(anchor, args.anchor_dir, dry_run=args.dry_run)
    except PermissionError as e:
        print(f"\n❌  Cannot write to anchor directory: {e}", file=sys.stderr)
        print(f"    Try: sudo python3 scripts/anchor_manifest.py", file=sys.stderr)
        return 2

    if not args.dry_run:
        print(f"  ✔ Anchor written:   {anchor_path}")

    # ── 5. Summary ───────────────────────────────────────────────────────────
    print("\n══════════════════════════════════════════════════════════")
    if args.dry_run:
        print("  DRY RUN COMPLETE — no files written")
    else:
        print("  ✅ ANCHOR RECORD CREATED")
        print(f"\n  manifest_sha256:")
        print(f"    {anchor['manifest_sha256']}")
        print(f"\n  This hash can be published externally as an independent")
        print(f"  witness for the canonical V5.4 release integrity.")
        print(f"\n  Suggested publication targets:")
        print(f"    • GitHub release notes or commit message")
        print(f"    • Zenodo dataset description")
        print(f"    • Any public permanent record")
        print(f"\n  Verification command (for any future operator):")
        print(f"    cd /beng-release")
        print(f"    sha256sum {MANIFEST_FILENAME} | awk '{{print $1}}'")
        print(f"    # Must equal: {anchor['manifest_sha256']}")
    print("══════════════════════════════════════════════════════════\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
