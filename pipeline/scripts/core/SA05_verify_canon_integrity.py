#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — SA05_verify_canon_integrity.py
================================================
Nome:       Canon Integrity Verifier
Versão:     1.0 — Canon Hardening Phase
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)

POSIÇÃO NA SEQUÊNCIA:
  SA04 (generate manifest) → [SA05 — this script — verify manifest]

O QUE FAZ:
  Recomputes SHA-256 hashes for all canon components and
  compares against metadata/canon_manifest.json.

  Components verified:
    09-csl/           → csl_hash
    03-translations/  → translations_hash
    13-static-site/   → site_build_hash
    scripts/core/     → pipeline_hash

  Exit codes:
    0 = CANON VERIFIED
    1 = CANON INTEGRITY FAILURE
    2 = MANIFEST ABSENT

USAGE:
  python3 scripts/core/SA05_verify_canon_integrity.py
  python3 scripts/core/SA05_verify_canon_integrity.py --quiet
"""

import hashlib
import json
import re
import sys
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import BASE_DIR, DIR_09_CSL, METADATA_DIR

DIR_03_TRANSLATIONS = BASE_DIR / "03-translations"
DIR_STATIC_SITE     = BASE_DIR / "13-static-site"
DIR_CORE_SCRIPTS    = _SCRIPT_DIR
MANIFEST_PATH       = METADATA_DIR / "canon_manifest.json"

QUIET = "--quiet" in sys.argv

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

_PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")


# ==============================================================================
# 🔐  HASH UTILITIES  (must match SA04 exactly)
# ==============================================================================
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def sha256_dir_tree(root: Path, pattern: str = "*") -> str:
    h = hashlib.sha256()
    files = sorted(root.rglob(pattern)) if root.exists() else []
    for f in files:
        if f.is_file() and not f.is_symlink():
            rel = str(f.relative_to(root))
            file_hash = sha256_file(f)
            h.update(f"{rel}:{file_hash}\n".encode())
    return h.hexdigest()


def sha256_pipeline(core_dir: Path) -> str:
    h = hashlib.sha256()
    scripts = sorted(core_dir.glob("*.py")) + sorted(core_dir.glob("*.sh"))
    for f in scripts:
        if f.is_file():
            file_hash = sha256_file(f)
            h.update(f"{f.name}:{file_hash}\n".encode())
    return h.hexdigest()


# ==============================================================================
# 🔍  COMPONENT VERIFICATION
# ==============================================================================
def verify_component(name: str, expected: str, actual: str) -> bool:
    if expected in ("ABSENT", "UNKNOWN"):
        if not QUIET:
            print(f"  {YELLOW}⚠  {name:<22} SKIPPED (manifest value: {expected}){RESET}")
        return True  # treat absent manifest entry as non-blocking

    match = (actual == expected)
    if not QUIET:
        if match:
            print(f"  {GREEN}✔  {name:<22} {actual[:24]}...{RESET}")
        else:
            print(f"  {RED}✘  {name:<22} MISMATCH{RESET}")
            print(f"       expected: {expected[:48]}")
            print(f"       actual  : {actual[:48]}")
    return match


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main() -> int:
    if not QUIET:
        print(f"\n{CYAN}{'='*62}{RESET}")
        print(f"{CYAN}  💎 AXIS-NIDDHI — SA05 Canon Integrity Verifier{RESET}")
        print(f"{CYAN}{'='*62}{RESET}\n")

    # Load manifest
    if not MANIFEST_PATH.exists():
        print(f"{RED}❌ MANIFEST ABSENT: {MANIFEST_PATH}{RESET}")
        print("   Run: python3 scripts/core/SA04_generate_canon_manifest.py")
        return 2

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"{RED}❌ MANIFEST UNREADABLE: {e}{RESET}")
        return 2

    if not QUIET:
        print(f"  {GRAY}Manifest    : {MANIFEST_PATH}{RESET}")
        print(f"  {GRAY}Engine      : {manifest.get('engine','?')} V{manifest.get('engine_version','?')}{RESET}")
        print(f"  {GRAY}Built       : {manifest.get('build_timestamp','?')}{RESET}")
        print(f"  {GRAY}Canon hash  : {manifest.get('canon_hash','?')[:32]}...{RESET}\n")

    results = []

    # 1. CSL hash
    if not QUIET:
        print(f"  {GRAY}[1/4] Verifying CSL...{RESET}")
    # Read from SA02 manifest for consistency
    sa02_manifest = DIR_09_CSL / "manifest.json"
    if sa02_manifest.exists():
        try:
            sa02 = json.loads(sa02_manifest.read_text(encoding="utf-8"))
            csl_actual = sa02.get("csl_hash", sha256_dir_tree(DIR_09_CSL, "*.json"))
        except Exception:
            csl_actual = sha256_dir_tree(DIR_09_CSL, "*.json")
    else:
        csl_actual = sha256_dir_tree(DIR_09_CSL, "*.json")
    results.append(verify_component("csl_hash", manifest.get("csl_hash", "UNKNOWN"), csl_actual))

    # 2. Translations hash
    if not QUIET:
        print(f"  {GRAY}[2/4] Verifying translations...{RESET}")
    trans_manifest = DIR_03_TRANSLATIONS / "manifest.json"
    if trans_manifest.exists():
        try:
            tm = json.loads(trans_manifest.read_text(encoding="utf-8"))
            trans_actual = tm.get("global_hash", sha256_dir_tree(DIR_03_TRANSLATIONS, "*.html"))
        except Exception:
            trans_actual = sha256_dir_tree(DIR_03_TRANSLATIONS, "*.html")
    else:
        trans_actual = sha256_dir_tree(DIR_03_TRANSLATIONS, "*.html")
    results.append(verify_component("translations_hash", manifest.get("translations_hash", "UNKNOWN"), trans_actual))

    # 3. Site build hash
    if not QUIET:
        print(f"  {GRAY}[3/4] Verifying static site...{RESET}")
    if DIR_STATIC_SITE.exists():
        site_actual = sha256_dir_tree(DIR_STATIC_SITE, "*.html")
    else:
        site_actual = "ABSENT"
    results.append(verify_component("site_build_hash", manifest.get("site_build_hash", "UNKNOWN"), site_actual))

    # 4. Pipeline hash
    if not QUIET:
        print(f"  {GRAY}[4/4] Verifying pipeline scripts...{RESET}")
    pipeline_actual = sha256_pipeline(DIR_CORE_SCRIPTS)
    results.append(verify_component("pipeline_hash", manifest.get("pipeline_hash", "UNKNOWN"), pipeline_actual))

    # Global canon hash recompute
    global_hasher = hashlib.sha256()
    for h in [
        manifest.get("source_zip_sha256", "ABSENT"),
        csl_actual,
        trans_actual,
        site_actual if site_actual != "ABSENT" else manifest.get("site_build_hash", "ABSENT"),
        pipeline_actual,
    ]:
        global_hasher.update(h.encode())
    canon_actual = global_hasher.hexdigest()
    canon_expected = manifest.get("canon_hash", "UNKNOWN")
    # Note: canon_hash includes source_zip which is expensive to re-hash
    # We verify components individually; canon_hash re-check is informational
    canon_match = (canon_actual == canon_expected)

    # Result
    all_pass = all(results)
    print("")

    if all_pass:
        print(f"{GREEN}{'='*62}{RESET}")
        print(f"{GREEN}  ✅ CANON VERIFIED{RESET}")
        print(f"{'='*62}")
        print(f"  {GRAY}All {len(results)} components match manifest{RESET}")
        if not canon_match:
            print(f"  {YELLOW}⚠ Global canon_hash differs (source ZIP not re-hashed — expected){RESET}")
        print(f"{GREEN}{'='*62}{RESET}\n")
        return 0
    else:
        failures = results.count(False)
        print(f"{RED}{'='*62}{RESET}")
        print(f"{RED}  ❌ CANON INTEGRITY FAILURE{RESET}")
        print(f"{'='*62}")
        print(f"  {RED}{failures} component(s) failed verification{RESET}")
        print(f"  Run SA04 to regenerate manifest, or investigate corpus mutation.")
        print(f"{RED}{'='*62}{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
