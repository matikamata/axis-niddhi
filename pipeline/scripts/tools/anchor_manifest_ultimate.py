#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — anchor_manifest_ultimate.py
==============================================
Versão:  3.0  —  Ultimate Canon Survival Layer
Data:    2026-03-12
Autores: Aloka + Vayo (AXIS-NIDDHI Architectural Session)

PURPOSE
-------
Generate a cryptographically sealed anchor record for the canonical release
manifest and publish it to three independent external witnesses, creating a
multi-location survival guarantee for the corpus across centuries.

VERIFICATION CHAIN
------------------
    208 sealed files
        → release-manifest.sha256            (seals all files)
            → anchor_YYYYMMDD_HHMMSS.json    (seals the manifest, atomic)
                → GitHub Gist       [W1]     (public URL, permanent, free)
                → Zenodo deposit    [W2]     (DOI, academic archive, permanent)
                → OpenTimestamps    [W3]     (Bitcoin blockchain, no credentials)

WITNESSES
---------
  W1 — GitHub Gist
       Requires: GITHUB_TOKEN env var or scripts/github_token.txt
       Scope needed: gist
       Result: public Gist URL, permanently citable

  W2 — Zenodo
       Requires: ZENODO_TOKEN env var or scripts/zenodo_token.txt
       Result: Zenodo deposit with DOI (may require manual publish confirmation)
       Note: First deposit from a new token may require one-time manual confirm.

  W3 — OpenTimestamps  (https://opentimestamps.org)
       Requires: nothing — free, no account, no credentials
       Result: .ots receipt file stored in anchor directory
       Verification: ots verify anchor_YYYYMMDD.ots  (after Bitcoin confirmation)
       Note: Full Bitcoin confirmation takes ~1 hour. Receipt is immediate.

TOKEN SUPPLY (consistent with pipeline credential pattern)
----------------------------------------------------------
  Priority 1: Environment variable   GITHUB_TOKEN / ZENODO_TOKEN
  Priority 2: Key file               scripts/github_token.txt / zenodo_token.txt
                                     Format: GITHUB_TOKEN=ghp_xxx
  Missing token → witness skipped, anchor still written. Never aborts.

CONSENSUS-READY ANCHOR FORMAT
------------------------------
  The anchor JSON includes a `consensus_records` array.
  Future independent operators append their manifest SHA-256 and timestamp
  to confirm independent reproducibility — V7 Council Consensus Layer.
  No pipeline modification required to add a consensus record.

USAGE
-----
    python3 scripts/anchor_manifest_ultimate.py
    python3 scripts/anchor_manifest_ultimate.py --release /beng-release
    python3 scripts/anchor_manifest_ultimate.py --dry-run
    python3 scripts/anchor_manifest_ultimate.py --skip-witnesses   # local only

ARCHITECTURE INVARIANTS RESPECTED
----------------------------------
    ✔  /beng-release/ is never modified
    ✔  Anchor written only to archaeology/anchors/
    ✔  sha256_file() for all hash computation
    ✔  atomic_write_json() for all file writes
    ✔  No third-party libraries — standard library only
    ✔  Idempotent — timestamped filenames, never overwrites
    ✔  All witness failures are logged, never fatal

EXIT CODES
----------
    0 — anchor written (witnesses may have been skipped or failed)
    1 — manifest not found or unreadable
    2 — anchor directory not writable
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
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
MANIFEST_FILENAME  = "release-manifest.sha256"
MANIFEST_FALLBACK  = "manifest.sha256"
ANCHOR_DIR         = BASE_DIR / "archaeology" / "anchors"
GITHUB_API_GIST    = "https://api.github.com/gists"
ZENODO_API_BASE    = "https://zenodo.org/api"
OTS_STAMP_URL      = "https://a.pool.opentimestamps.org/digest"


# ==============================================================================
# CREDENTIAL LOADERS  (mirrors get_deepl_key / get_wp_password pattern)
# ==============================================================================

def _load_credential(env_var: str, filename: str) -> str | None:
    """
    Generic credential loader. Priority: env var → key file → None.
    Never aborts — missing credentials mean the witness is skipped.
    """
    value = os.environ.get(env_var, "").strip()
    if value:
        return value

    key_file = _SCRIPT_DIR / filename
    if key_file.exists():
        for line in key_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == env_var:
                v = v.strip()
                if v:
                    return v
    return None


def get_github_token() -> str | None:
    return _load_credential("GITHUB_TOKEN", "github_token.txt")


def get_zenodo_token() -> str | None:
    return _load_credential("ZENODO_TOKEN", "zenodo_token.txt")


# ==============================================================================
# MANIFEST OPERATIONS
# ==============================================================================

def find_manifest(release_root: Path) -> Path:
    for name in (MANIFEST_FILENAME, MANIFEST_FALLBACK):
        candidate = release_root / name
        if candidate.exists():
            if name == MANIFEST_FALLBACK:
                print(f"  ⚠  Using fallback manifest name: {name}")
            return candidate
    raise FileNotFoundError(
        f"Manifest not found in {release_root}\n"
        f"  Tried: {MANIFEST_FILENAME}, {MANIFEST_FALLBACK}\n"
        f"  Run build_release_snapshot_v4.sh first."
    )


def read_seal_metadata(release_root: Path) -> dict:
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
    return sum(
        1 for ln in manifest_path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    )


# ==============================================================================
# ANCHOR RECORD
# ==============================================================================

def build_anchor(manifest_path: Path, manifest_hash: str,
                 seal_meta: dict, sealed_files: int) -> dict:
    """
    Construct the full anchor record.

    consensus_records is intentionally empty at creation time.
    Future operators append their own manifest_sha256 + timestamp
    to confirm independent reproducibility (V7 Council Consensus Layer).
    No pipeline modification is needed to use this field.
    """
    return {
        # ── Verification-critical ────────────────────────────────────────────
        "schema_version":     "3.0",
        "manifest_sha256":    manifest_hash,
        "manifest_filename":  manifest_path.name,
        "manifest_path":      str(manifest_path),
        "sealed_files":       sealed_files,
        "anchored_at":        get_utc_now(),

        # ── Post-creation fields (populated after witnesses) ─────────────────
        "verification_status": None,   # populated by verify_anchor()
        "witnesses":           {},     # populated by witness publishers
        "consensus_records":   [],     # appended by future independent operators

        # ── Provenance from release-sealed-at.txt ────────────────────────────
        "engine":             seal_meta.get("engine",    "AXIS-NIDDHI V5.4"),
        "corpus":             seal_meta.get("corpus",    "PureDhamma"),
        "release_sealed_at":  seal_meta.get("sealed_at", "unknown"),

        # ── Verification instructions ────────────────────────────────────────
        "verify_command": (
            f"cd /beng-release && "
            f"sha256sum {MANIFEST_FILENAME} | awk '{{print $1}}'"
            f"  # must equal manifest_sha256 above"
        ),
    }


def verify_anchor(anchor: dict, manifest_path: Path) -> bool:
    """
    Re-compute manifest SHA-256 and compare against anchor record.
    Writes result to anchor['verification_status'].
    Returns True if verified.
    """
    recomputed = sha256_file(manifest_path)
    match = (recomputed == anchor["manifest_sha256"])
    anchor["verification_status"] = {
        "verified":       match,
        "verified_at":    get_utc_now(),
        "recomputed_sha": recomputed,
    }
    return match


# ==============================================================================
# SHARED WITNESS UTILITIES
# ==============================================================================

def _human_summary(anchor: dict) -> str:
    """Human-readable block included in every external witness."""
    h = anchor["manifest_sha256"]
    return (
        f"AXIS-NIDDHI — Ultimate Canon Survival Anchor\n"
        f"{'=' * 52}\n"
        f"Corpus:          {anchor['corpus']}\n"
        f"Engine:          {anchor['engine']}\n"
        f"Release sealed:  {anchor['release_sealed_at']}\n"
        f"Anchor created:  {anchor['anchored_at']}\n"
        f"Sealed files:    {anchor['sealed_files']}\n"
        f"Schema:          {anchor['schema_version']}\n"
        f"\n"
        f"manifest_sha256:\n"
        f"  {h}\n"
        f"\n"
        f"Verification (any operator, any time, no infrastructure needed):\n"
        f"  cd /path/to/beng-release\n"
        f"  sha256sum {MANIFEST_FILENAME} | awk '{{print $1}}'\n"
        f"  # Must equal the manifest_sha256 above.\n"
        f"\n"
        f"This record is an independent cryptographic witness for the\n"
        f"canonical integrity of the {anchor['corpus']} corpus.\n"
        f"It contains no corpus content — only the cryptographic\n"
        f"fingerprint of the canonical release manifest.\n"
        f"\n"
        f"Consensus verification (V7 Council Consensus Layer):\n"
        f"  Any independent operator who rebuilds the corpus from the\n"
        f"  same source ZIP should obtain the same manifest_sha256.\n"
        f"  Append your result to consensus_records in the anchor JSON.\n"
    )


def _http_post(url: str, payload: dict | bytes, headers: dict,
               timeout: int = 20) -> tuple[bool, dict, str]:
    """
    Generic HTTP POST. Returns (success, response_dict, error_message).
    Never raises — all failures returned as (False, {}, error_str).
    """
    if isinstance(payload, dict):
        body = json.dumps(payload).encode("utf-8")
    else:
        body = payload

    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, json.loads(resp.read().decode("utf-8")), ""
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        return False, {}, f"HTTP {e.code}: {body_text[:300]}"
    except urllib.error.URLError as e:
        return False, {}, f"Network error: {e.reason}"
    except Exception as e:
        return False, {}, f"Unexpected: {e}"


def _http_put(url: str, payload: dict, headers: dict,
              timeout: int = 20) -> tuple[bool, dict, str]:
    body = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(url, data=body, method="PUT", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, json.loads(resp.read().decode("utf-8")), ""
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        return False, {}, f"HTTP {e.code}: {body_text[:300]}"
    except Exception as e:
        return False, {}, f"Unexpected: {e}"


# ==============================================================================
# WITNESS 1 — GITHUB GIST
# ==============================================================================

def publish_github_gist(anchor: dict, dry_run: bool) -> tuple[str, str]:
    """
    Publish anchor to a public GitHub Gist.
    Returns (gist_url_or_empty, error_message_or_empty).
    """
    token = get_github_token()
    if not token:
        return "", (
            "GITHUB_TOKEN not found. Supply via env var or "
            f"scripts/github_token.txt"
        )

    payload = {
        "description": (
            f"AXIS-NIDDHI anchor — {anchor['corpus']} — "
            f"{anchor['engine']} — {anchor['anchored_at']}"
        ),
        "public": True,
        "files": {
            "AXIS_NIDDHI_anchor_summary.txt": {
                "content": _human_summary(anchor)
            },
            "AXIS_NIDDHI_anchor_full.json": {
                "content": json.dumps(anchor, indent=2, ensure_ascii=False)
            },
        },
    }

    if dry_run:
        print("\n  [W1 DRY RUN] GitHub Gist payload:")
        print(f"    Description: {payload['description']}")
        print(f"    Files: {list(payload['files'].keys())}")
        return "DRY_RUN", ""

    success, data, err = _http_post(
        GITHUB_API_GIST, payload,
        headers={
            "Authorization": f"token {token}",
            "Accept":        "application/vnd.github+json",
            "Content-Type":  "application/json",
            "User-Agent":    "AXIS-NIDDHI-anchor/3.0",
        },
    )
    if success:
        return data.get("html_url", "URL not returned"), ""
    return "", err


# ==============================================================================
# WITNESS 2 — ZENODO
# ==============================================================================

def publish_zenodo(anchor: dict, dry_run: bool) -> tuple[str, str]:
    """
    Create a Zenodo deposit containing the anchor record.
    Returns (deposit_url_or_empty, error_message_or_empty).

    Flow:
      1. POST /api/deposit/depositions   → create empty draft
      2. PUT  /api/deposit/depositions/{id}  → set metadata
      3. POST /api/deposit/depositions/{id}/files  → upload anchor JSON
      4. POST /api/deposit/depositions/{id}/actions/publish  → publish
         (Step 4 may require manual confirmation for new accounts.)
    """
    token = get_zenodo_token()
    if not token:
        return "", (
            "ZENODO_TOKEN not found. Supply via env var or "
            "scripts/zenodo_token.txt"
        )

    headers_json = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }

    if dry_run:
        print("\n  [W2 DRY RUN] Zenodo deposit:")
        print(f"    Title: AXIS-NIDDHI Canonical Anchor — "
              f"{anchor['corpus']} — {anchor['anchored_at']}")
        print(f"    File: AXIS_NIDDHI_anchor_full.json")
        return "DRY_RUN", ""

    # Step 1 — create empty draft
    ok, data, err = _http_post(
        f"{ZENODO_API_BASE}/deposit/depositions", {}, headers_json
    )
    if not ok:
        return "", f"Zenodo create deposit failed: {err}"

    deposit_id  = data.get("id")
    deposit_url = data.get("links", {}).get("html", "")
    if not deposit_id:
        return "", "Zenodo returned no deposit ID"

    # Step 2 — set metadata
    metadata = {
        "metadata": {
            "title":         (
                f"AXIS-NIDDHI Canonical Anchor — "
                f"{anchor['corpus']} — {anchor['anchored_at']}"
            ),
            "upload_type":   "dataset",
            "description":   _human_summary(anchor).replace("\n", "<br>"),
            "creators":      [{"name": "AXIS-NIDDHI Preservation Engine"}],
            "keywords":      [
                "canonical preservation", "corpus integrity",
                "SHA-256", "AXIS-NIDDHI", anchor["corpus"].lower()
            ],
            "access_right":  "open",
            "license":       "cc-zero",
        }
    }
    ok, _, err = _http_put(
        f"{ZENODO_API_BASE}/deposit/depositions/{deposit_id}",
        metadata, headers_json
    )
    if not ok:
        return deposit_url, f"Zenodo metadata update failed: {err} (deposit {deposit_id} created)"

    # Step 3 — upload anchor JSON file
    file_content  = json.dumps(anchor, indent=2, ensure_ascii=False).encode("utf-8")
    boundary      = "AxisNiddhiBoundary"
    filename      = "AXIS_NIDDHI_anchor_full.json"
    multipart     = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/json\r\n\r\n"
    ).encode("utf-8") + file_content + f"\r\n--{boundary}--\r\n".encode("utf-8")

    upload_req = urllib.request.Request(
        f"{ZENODO_API_BASE}/deposit/depositions/{deposit_id}/files",
        data    = multipart,
        method  = "POST",
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type":  f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with urllib.request.urlopen(upload_req, timeout=30):
            pass
    except Exception as e:
        return deposit_url, f"Zenodo file upload failed: {e} (deposit {deposit_id} created)"

    # Step 4 — publish
    ok, pub_data, err = _http_post(
        f"{ZENODO_API_BASE}/deposit/depositions/{deposit_id}/actions/publish",
        {}, headers_json
    )
    if ok:
        doi_url = pub_data.get("doi_url", deposit_url)
        return doi_url or deposit_url, ""
    else:
        # Publish may require manual confirmation — deposit is still created
        return (
            deposit_url,
            f"Auto-publish failed (manual confirm may be needed): {err}"
        )


# ==============================================================================
# WITNESS 3 — OPENTIMESTAMPS
# ==============================================================================

def publish_opentimestamps(anchor: dict, anchor_dir: Path,
                           dry_run: bool) -> tuple[str, str]:
    """
    Submit manifest SHA-256 to OpenTimestamps for Bitcoin blockchain anchoring.

    OpenTimestamps accepts a raw 32-byte SHA-256 digest via HTTP POST and
    returns an .ots receipt. The receipt proves the hash existed at the time
    of submission. Full Bitcoin confirmation takes ~1 hour.

    Returns (receipt_path_or_empty, error_message_or_empty).
    The .ots receipt file is stored alongside the anchor JSON.
    Verification: ots verify <receipt.ots>  (requires ots client)
    Manual verification: https://opentimestamps.org
    """
    manifest_hash = anchor["manifest_sha256"]

    if dry_run:
        print(f"\n  [W3 DRY RUN] OpenTimestamps submission:")
        print(f"    Hash: {manifest_hash}")
        print(f"    URL:  {OTS_STAMP_URL}")
        print(f"    Receipt would be stored at: "
              f"{anchor_dir}/ots_receipt_<timestamp>.ots")
        return "DRY_RUN", ""

    # Convert hex digest to raw bytes for submission
    digest_bytes = bytes.fromhex(manifest_hash)

    req = urllib.request.Request(
        OTS_STAMP_URL,
        data    = digest_bytes,
        method  = "POST",
        headers = {
            "Content-Type":  "application/octet-stream",
            "Accept":        "application/octet-stream",
            "User-Agent":    "AXIS-NIDDHI-anchor/3.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            receipt_bytes = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return "", f"HTTP {e.code}: {body[:200]}"
    except urllib.error.URLError as e:
        return "", f"Network error: {e.reason}"
    except Exception as e:
        return "", f"Unexpected: {e}"

    if not receipt_bytes:
        return "", "OpenTimestamps returned empty receipt"

    # Store receipt alongside anchor JSON
    ts          = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    receipt_path = anchor_dir / f"ots_receipt_{ts}.ots"
    try:
        receipt_path.write_bytes(receipt_bytes)
    except PermissionError as e:
        return "", f"Cannot write receipt: {e}"

    return str(receipt_path), ""


# ==============================================================================
# MAIN
# ==============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="AXIS-NIDDHI Ultimate Canon Survival Layer V3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Token supply:\n"
            "  export GITHUB_TOKEN=ghp_xxx   # scope: gist\n"
            "  export ZENODO_TOKEN=xxx        # scope: deposit:write\n"
            "  W3 (OpenTimestamps) requires no credentials.\n"
        ),
    )
    parser.add_argument("--release",         type=Path, default=Path("/beng-release"),
                        help="Release root directory (default: /beng-release)")
    parser.add_argument("--anchor-dir",      type=Path, default=ANCHOR_DIR,
                        help=f"Anchor storage directory (default: {ANCHOR_DIR})")
    parser.add_argument("--dry-run",         action="store_true",
                        help="Print all planned actions without writing or posting")
    parser.add_argument("--skip-witnesses",  action="store_true",
                        help="Write local anchor only; skip all external witnesses")
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  💎 AXIS-NIDDHI — Ultimate Canon Survival Layer V3      ║")
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

    print(f"  ✔  Manifest:      {manifest_path.name}")
    print(f"  ✔  Sealed files:  {sealed_files}")
    print(f"  ✔  SHA-256:       {manifest_hash}")
    if seal_meta:
        print(f"  ✔  Release:       {seal_meta.get('engine','?')} · "
              f"{seal_meta.get('corpus','?')} · {seal_meta.get('sealed_at','?')}")

    # ── 2. Build anchor record ───────────────────────────────────────────────
    anchor = build_anchor(manifest_path, manifest_hash, seal_meta, sealed_files)

    # ── 3. Verify manifest integrity ────────────────────────────────────────
    verified = verify_anchor(anchor, manifest_path)
    status   = "✔  PASS" if verified else "✘  FAIL"
    print(f"\n  {status}  Post-hash verification")
    if not verified:
        print("  ⚠   SHA-256 mismatch during self-verification — investigate before continuing.",
              file=sys.stderr)

    # ── 4. Dry-run: show everything and exit ─────────────────────────────────
    if args.dry_run:
        ts          = get_utc_now().replace(":", "").replace("-", "")[:15]
        anchor_path = args.anchor_dir / f"anchor_{ts}.json"
        print(f"\n── DRY RUN ── local anchor (would write) ──────────────────")
        print(f"  Path:    {anchor_path}")
        print(f"  Content:\n{json.dumps(anchor, indent=2, ensure_ascii=False)}")
        if not args.skip_witnesses:
            publish_github_gist(anchor, dry_run=True)
            publish_zenodo(anchor, dry_run=True)
            publish_opentimestamps(anchor, args.anchor_dir, dry_run=True)
        print("\n── DRY RUN COMPLETE — nothing written or posted ───────────\n")
        return 0

    # ── 5. Write local anchor atomically ────────────────────────────────────
    ts          = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    anchor_path = args.anchor_dir / f"anchor_{ts}.json"

    try:
        args.anchor_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(anchor_path, anchor)
        print(f"\n  ✔  Local anchor: {anchor_path}")
    except PermissionError as e:
        print(f"\n❌  Cannot write anchor: {e}", file=sys.stderr)
        print(f"    Try: sudo python3 scripts/anchor_manifest_ultimate.py",
              file=sys.stderr)
        return 2

    # ── 6. External witnesses ────────────────────────────────────────────────
    witness_results = {}   # name → {status, detail}

    if args.skip_witnesses:
        print("\n  ⚠   All witnesses skipped (--skip-witnesses)")
    else:
        print("\n── Publishing to external witnesses ───────────────────────")

        # W1 — GitHub Gist
        print("  →  W1  GitHub Gist...")
        gist_url, err = publish_github_gist(anchor, dry_run=False)
        if gist_url:
            print(f"  ✔  W1  {gist_url}")
            witness_results["github_gist"] = {"status": "ok", "url": gist_url}
            anchor["witnesses"]["github_gist"] = gist_url
        else:
            print(f"  ✘  W1  Skipped: {err}", file=sys.stderr)
            witness_results["github_gist"] = {"status": "failed", "error": err}

        # W2 — Zenodo
        print("  →  W2  Zenodo...")
        zenodo_url, err = publish_zenodo(anchor, dry_run=False)
        if zenodo_url:
            label = "✔" if not err else "⚠ "
            note  = f" ({err})" if err else ""
            print(f"  {label}  W2  {zenodo_url}{note}")
            witness_results["zenodo"] = {
                "status": "ok" if not err else "partial",
                "url": zenodo_url,
                **({"note": err} if err else {}),
            }
            anchor["witnesses"]["zenodo"] = zenodo_url
        else:
            print(f"  ✘  W2  Skipped: {err}", file=sys.stderr)
            witness_results["zenodo"] = {"status": "failed", "error": err}

        # W3 — OpenTimestamps
        print("  →  W3  OpenTimestamps (Bitcoin blockchain)...")
        ots_path, err = publish_opentimestamps(anchor, args.anchor_dir, dry_run=False)
        if ots_path:
            print(f"  ✔  W3  Receipt: {ots_path}")
            print(f"         (Full Bitcoin confirmation ~1 hour)")
            witness_results["opentimestamps"] = {"status": "ok", "receipt": ots_path}
            anchor["witnesses"]["opentimestamps_receipt"] = ots_path
        else:
            print(f"  ✘  W3  Failed: {err}", file=sys.stderr)
            witness_results["opentimestamps"] = {"status": "failed", "error": err}

    # ── 7. Patch anchor with witness results and re-write ───────────────────
    anchor["witnesses"] = {
        k: v for k, v in anchor.get("witnesses", {}).items()
    }
    atomic_write_json(anchor_path, anchor)

    # ── 8. Terminal summary ──────────────────────────────────────────────────
    w_ok     = [k for k, v in witness_results.items() if v["status"] in ("ok","partial")]
    w_failed = [k for k, v in witness_results.items() if v["status"] == "failed"]

    print("\n══════════════════════════════════════════════════════════")
    print("  ✅ ULTIMATE CANON SURVIVAL ANCHOR COMPLETE")
    print(f"\n  manifest_sha256:")
    print(f"    {manifest_hash}")
    print(f"\n  Local anchor:      {anchor_path}")
    print(f"  Verification:      {'PASS ✔' if verified else 'FAIL ✘'}")

    if witness_results:
        print(f"\n  External witnesses:")
        labels = {
            "github_gist":     "W1  GitHub Gist  ",
            "zenodo":          "W2  Zenodo       ",
            "opentimestamps":  "W3  OpenTimestamps",
        }
        for key, res in witness_results.items():
            label  = labels.get(key, key)
            status = res["status"].upper()
            detail = res.get("url") or res.get("receipt") or res.get("error","")
            icon   = "✔" if res["status"] in ("ok","partial") else "✘"
            print(f"  {icon}  {label}  {status}  {detail[:60]}")

    print(f"\n  Verification commands (for any future operator):")
    print(f"    # 1. Verify release manifest")
    print(f"    cd /beng-release && sha256sum --check {MANIFEST_FILENAME}")
    print(f"    # 2. Verify anchor hash matches manifest")
    print(f"    sha256sum {MANIFEST_FILENAME} | awk '{{print $1}}'")
    print(f"    # Must equal: {manifest_hash}")
    if witness_results.get("opentimestamps", {}).get("receipt"):
        print(f"    # 3. Verify OpenTimestamps receipt (after ~1 hour)")
        print(f"    ots verify {witness_results['opentimestamps']['receipt']}")

    if w_failed:
        print(f"\n  Failed witnesses: {', '.join(w_failed)}")
        print(f"  The local anchor is valid regardless of witness failures.")

    if anchor.get("consensus_records") == []:
        print(f"\n  Consensus-ready: independent operators may append to")
        print(f"  consensus_records[] in the anchor JSON to confirm")
        print(f"  independent reproducibility (V7 Council Consensus Layer).")

    print("══════════════════════════════════════════════════════════\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
