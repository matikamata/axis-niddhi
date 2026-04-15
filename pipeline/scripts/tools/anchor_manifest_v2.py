#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — anchor_manifest_v2.py
========================================
Versão:  2.0  —  Long-Term Canon Survival Layer
Data:    2026-03-12
Autores: Aloka + Vayo (AXIS-NIDDHI Architectural Session)

PURPOSE
-------
Generate a timestamped anchor record for the V5.4 canonical release manifest
and publish the manifest hash as a public GitHub Gist, creating an external
witness for long-term canonical integrity verification.

VERIFICATION CHAIN
------------------
    208 files
        → release-manifest.sha256          (seals all files)
            → anchor_YYYYMMDD_HHMMSS.json  (seals the manifest)
                → GitHub Gist (public URL) (external independent witness)

A future operator who holds only the Gist URL can verify the entire V5.4
release without trusting any internal infrastructure.

TOKEN SUPPLY (two methods — consistent with pipeline credential pattern)
---------------------------------------------------------------------------
  Priority 1: Environment variable
      export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

  Priority 2: Key file at scripts/github_token.txt
      GITHUB_TOKEN=ghp_xxxxxxxxxxxx

  If neither is present, anchor is written locally and Gist is skipped
  with a clear warning — anchor creation always succeeds.

USAGE
-----
    python3 scripts/anchor_manifest_v2.py
    python3 scripts/anchor_manifest_v2.py --release /beng-release
    python3 scripts/anchor_manifest_v2.py --dry-run
    python3 scripts/anchor_manifest_v2.py --skip-gist   # local anchor only

ARCHITECTURE INVARIANTS RESPECTED
----------------------------------
    ✔  /beng-fut/ is never modified
    ✔  /beng-release/ is never modified
    ✔  Anchor written only to archaeology/anchors/ (Lab workspace)
    ✔  sha256_file() used for all hash computation (pipeline standard)
    ✔  atomic_write_json() used for all file writes (crash-safe)
    ✔  Script is idempotent — safe to run multiple times
    ✔  No pipeline script is imported or modified

EXIT CODES
----------
    0  — anchor written; Gist created (or skipped intentionally)
    1  — manifest not found or unreadable (anchor not written)
    2  — anchor directory not writable (anchor not written)
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ── Pipeline utilities ────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from pipeline_utils import sha256_file, atomic_write_json, get_utc_now
except ImportError as e:
    print(f"\n❌  Cannot import pipeline_utils: {e}", file=sys.stderr)
    print(f"    Expected at: {_SCRIPT_DIR / 'pipeline_utils.py'}", file=sys.stderr)
    sys.exit(1)

try:
    from config import BASE_DIR
except ImportError:
    BASE_DIR = _SCRIPT_DIR.parent

# ── Constants ─────────────────────────────────────────────────────────────────
MANIFEST_FILENAME = "release-manifest.sha256"
MANIFEST_FALLBACK = "manifest.sha256"
ANCHOR_DIR        = BASE_DIR / "archaeology" / "anchors"
GITHUB_API_GIST   = "https://api.github.com/gists"
TOKEN_FILE        = _SCRIPT_DIR / "github_token.txt"


# ==============================================================================
# CREDENTIAL LOADER  (mirrors get_deepl_key / get_wp_password pattern)
# ==============================================================================

def get_github_token() -> str | None:
    """
    Returns the GitHub personal access token without hardcoding.

    Priority:
      1. Environment variable  GITHUB_TOKEN
      2. File                  scripts/github_token.txt
         Format:               GITHUB_TOKEN=ghp_xxxxxxxxxxxx

    Returns None (never aborts) — Gist publication is optional.
    Token must have scope: gist
    """
    # 1. Environment variable
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token

    # 2. Key file
    if TOKEN_FILE.exists():
        for line in TOKEN_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if line.startswith("GITHUB_TOKEN="):
                token = line.split("=", 1)[1].strip()
                if token:
                    return token

    return None


# ==============================================================================
# MANIFEST OPERATIONS
# ==============================================================================

def find_manifest(release_root: Path) -> Path:
    """Locate release manifest. Tries canonical name, then legacy fallback."""
    for name in (MANIFEST_FILENAME, MANIFEST_FALLBACK):
        candidate = release_root / name
        if candidate.exists():
            if name == MANIFEST_FALLBACK:
                print(f"  ⚠  Using fallback manifest name: {name}", file=sys.stderr)
            return candidate
    raise FileNotFoundError(
        f"Manifest not found in {release_root}\n"
        f"  Tried: {MANIFEST_FILENAME}, {MANIFEST_FALLBACK}\n"
        f"  Run build_release_snapshot_v4.sh first."
    )


def read_seal_metadata(release_root: Path) -> dict:
    """
    Parse release-sealed-at.txt into a dict.
    Returns empty dict if file absent — anchor remains valid without it.
    """
    seal_file = release_root / "release-sealed-at.txt"
    if not seal_file.exists():
        return {}
    meta = {}
    for line in seal_file.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip().lower()] = v.strip()
    return meta


def count_manifest_lines(manifest_path: Path) -> int:
    """Count non-empty lines in manifest = number of sealed files."""
    return sum(
        1 for ln in manifest_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    )


# ==============================================================================
# ANCHOR RECORD
# ==============================================================================

def build_anchor(manifest_path: Path, manifest_hash: str,
                 seal_meta: dict, sealed_files: int) -> dict:
    """Construct the anchor record. All fields are human-readable."""
    return {
        # ── Verification-critical ────────────────────────────────────────────
        "manifest_sha256":    manifest_hash,
        "manifest_filename":  manifest_path.name,
        "manifest_path":      str(manifest_path),
        "sealed_files":       sealed_files,
        "anchored_at":        get_utc_now(),

        # ── Provenance from release-sealed-at.txt ────────────────────────────
        "engine":             seal_meta.get("engine",    "AXIS-NIDDHI V5.4"),
        "corpus":             seal_meta.get("corpus",    "PureDhamma"),
        "release_sealed_at":  seal_meta.get("sealed_at", "unknown"),

        # ── Verification instructions for future operators ───────────────────
        "verify_command": (
            f"cd /beng-release && "
            f"sha256sum {MANIFEST_FILENAME} | awk '{{print $1}}'"
            f"  # must equal manifest_sha256 above"
        ),
    }


# ==============================================================================
# GITHUB GIST PUBLICATION
# ==============================================================================

def build_gist_payload(anchor: dict) -> dict:
    """
    Construct the Gist payload.
    Two files: a human-readable summary and the full anchor JSON.
    Public Gist — permanent, citable, independently verifiable.
    """
    corpus  = anchor["corpus"]
    engine  = anchor["engine"]
    ts      = anchor["anchored_at"]
    h       = anchor["manifest_sha256"]
    files_n = anchor["sealed_files"]
    sealed  = anchor["release_sealed_at"]

    summary = (
        f"AXIS-NIDDHI — Canonical Manifest Anchor\n"
        f"{'=' * 48}\n"
        f"Corpus:          {corpus}\n"
        f"Engine:          {engine}\n"
        f"Release sealed:  {sealed}\n"
        f"Anchor created:  {ts}\n"
        f"Sealed files:    {files_n}\n"
        f"\n"
        f"manifest_sha256:\n"
        f"  {h}\n"
        f"\n"
        f"Verification (any operator, any location):\n"
        f"  cd /path/to/release\n"
        f"  sha256sum {MANIFEST_FILENAME} | awk '{{print $1}}'\n"
        f"  # Must equal the manifest_sha256 above.\n"
        f"\n"
        f"This Gist is an independent external witness for the integrity\n"
        f"of the {corpus} canonical corpus sealed under {engine}.\n"
        f"It was generated by anchor_manifest_v2.py and does not contain\n"
        f"any corpus content — only the cryptographic fingerprint of the\n"
        f"canonical release manifest.\n"
    )

    return {
        "description": (
            f"AXIS-NIDDHI canonical manifest anchor — "
            f"{corpus} — {engine} — {ts}"
        ),
        "public": True,
        "files": {
            "AXIS_NIDDHI_anchor_summary.txt": {"content": summary},
            "AXIS_NIDDHI_anchor_full.json":   {
                "content": json.dumps(anchor, indent=2, ensure_ascii=False)
            },
        },
    }


def publish_gist(payload: dict, token: str) -> tuple[bool, str, str]:
    """
    POST to GitHub Gist API.
    Returns (success: bool, gist_url: str, error_message: str).
    Never raises — failures are returned, not raised.
    """
    body = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        GITHUB_API_GIST,
        data    = body,
        method  = "POST",
        headers = {
            "Authorization": f"token {token}",
            "Accept":        "application/vnd.github+json",
            "Content-Type":  "application/json",
            "User-Agent":    "AXIS-NIDDHI-anchor/2.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data.get("html_url", "URL not returned"), ""
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        return False, "", f"HTTP {e.code}: {body_text[:200]}"
    except urllib.error.URLError as e:
        return False, "", f"Network error: {e.reason}"
    except Exception as e:
        return False, "", f"Unexpected error: {e}"


# ==============================================================================
# MAIN
# ==============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="AXIS-NIDDHI Long-Term Canon Survival Layer V2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Token supply:\n"
            "  export GITHUB_TOKEN=ghp_xxxxxxxxxxxx\n"
            "  — or —\n"
            f"  echo 'GITHUB_TOKEN=ghp_xxx' > {TOKEN_FILE}\n"
        ),
    )
    parser.add_argument("--release",    type=Path, default=Path("/beng-release"),
                        help="Release root directory (default: /beng-release)")
    parser.add_argument("--anchor-dir", type=Path, default=ANCHOR_DIR,
                        help=f"Anchor storage directory (default: {ANCHOR_DIR})")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Print all planned actions without writing or posting")
    parser.add_argument("--skip-gist",  action="store_true",
                        help="Write local anchor only; skip Gist publication")
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  💎 AXIS-NIDDHI — Canon Survival Layer V2               ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # ── 1. Locate and hash the manifest ─────────────────────────────────────
    try:
        manifest_path = find_manifest(args.release)
    except FileNotFoundError as e:
        print(f"❌  {e}", file=sys.stderr)
        return 1

    manifest_hash = sha256_file(manifest_path)
    if manifest_hash is None:
        print(f"❌  Could not compute SHA-256 for {manifest_path}", file=sys.stderr)
        return 1

    sealed_files = count_manifest_lines(manifest_path)
    seal_meta    = read_seal_metadata(args.release)

    print(f"  ✔  Manifest:      {manifest_path}")
    print(f"  ✔  Sealed files:  {sealed_files}")
    print(f"  ✔  SHA-256:       {manifest_hash}")
    if seal_meta:
        print(f"  ✔  Release:       {seal_meta.get('engine','?')} · "
              f"{seal_meta.get('corpus','?')} · {seal_meta.get('sealed_at','?')}")

    # ── 2. Build anchor record ───────────────────────────────────────────────
    anchor       = build_anchor(manifest_path, manifest_hash, seal_meta, sealed_files)
    gist_payload = build_gist_payload(anchor)

    # ── 3. Dry-run: print and exit ───────────────────────────────────────────
    if args.dry_run:
        print("\n── DRY RUN — local anchor (would write) ──────────────────")
        ts          = get_utc_now().replace(":", "").replace("-", "")[:15]
        anchor_path = args.anchor_dir / f"anchor_{ts}.json"
        print(f"  Path: {anchor_path}")
        print(f"  Content:\n{json.dumps(anchor, indent=2, ensure_ascii=False)}")
        print("\n── DRY RUN — Gist payload (would POST) ───────────────────")
        print(json.dumps(gist_payload, indent=2, ensure_ascii=False))
        print("\n── DRY RUN COMPLETE — nothing written or posted ──────────\n")
        return 0

    # ── 4. Write local anchor atomically ────────────────────────────────────
    from datetime import datetime, timezone
    ts          = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    anchor_path = args.anchor_dir / f"anchor_{ts}.json"

    try:
        args.anchor_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(anchor_path, anchor)
        print(f"\n  ✔  Anchor written: {anchor_path}")
    except PermissionError as e:
        print(f"\n❌  Cannot write anchor: {e}", file=sys.stderr)
        print(f"    Try: sudo python3 scripts/anchor_manifest_v2.py", file=sys.stderr)
        return 2

    # ── 5. GitHub Gist publication ───────────────────────────────────────────
    gist_url    = None
    gist_error  = None

    if args.skip_gist:
        print("  ⚠   Gist skipped (--skip-gist flag set)")
    else:
        token = get_github_token()
        if not token:
            print("\n  ⚠   GITHUB_TOKEN not found — Gist skipped.")
            print(f"      Supply via:  export GITHUB_TOKEN=ghp_xxx")
            print(f"      — or —      GITHUB_TOKEN=ghp_xxx > {TOKEN_FILE}")
            gist_error = "Token not supplied"
        else:
            print("\n  →   Publishing to GitHub Gist...")
            success, gist_url, err = publish_gist(gist_payload, token)
            if success:
                print(f"  ✔   Gist created:  {gist_url}")
                # Patch anchor file with Gist URL now that we have it
                anchor["gist_url"] = gist_url
                atomic_write_json(anchor_path, anchor)
            else:
                gist_error = err
                print(f"  ✘   Gist failed:   {err}", file=sys.stderr)
                print(f"      Anchor is still valid locally.", file=sys.stderr)

    # ── 6. Terminal summary ──────────────────────────────────────────────────
    print("\n══════════════════════════════════════════════════════════")
    print("  ✅ CANON SURVIVAL ANCHOR COMPLETE")
    print(f"\n  manifest_sha256:")
    print(f"    {manifest_hash}")
    print(f"\n  Local anchor:  {anchor_path}")
    if gist_url:
        print(f"  Gist URL:      {gist_url}")
        print(f"\n  External witness active.")
        print(f"  Cite the Gist URL as the canonical integrity reference.")
    elif gist_error:
        print(f"  Gist:          SKIPPED ({gist_error})")
        print(f"  Local anchor is the sole witness for this run.")
    else:
        print(f"  Gist:          SKIPPED (--skip-gist)")

    print(f"\n  Verification (any operator, any location, any time):")
    print(f"    cd /path/to/beng-release")
    print(f"    sha256sum {MANIFEST_FILENAME} | awk '{{print $1}}'")
    print(f"    # Must equal: {manifest_hash}")
    print("══════════════════════════════════════════════════════════\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
