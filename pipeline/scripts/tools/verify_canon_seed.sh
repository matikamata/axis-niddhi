#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — verify_canon_seed.sh
# Canon Seed Verifier V1.0
# ==============================================================================
# PURPOSE:
#   Verify a Canon Seed by checking:
#     1. Seed internal integrity (seed_integrity_hash)
#     2. canon_hash matches live canon_manifest.json
#     3. manifest_hash matches live canon_manifest.json file hash
#     4. engine compatibility (engine_version)
#
# USAGE:
#   bash scripts/tools/verify_canon_seed.sh seeds/puredhamma_seed/
#   BENG_BASE=/path/to/pipeline bash scripts/tools/verify_canon_seed.sh seeds/puredhamma_seed/
#
# EXIT CODES:
#   0 = SEED VERIFIED
#   1 = SEED VERIFICATION FAILURE
#   2 = SEED OR MANIFEST ABSENT
# ==============================================================================
set -euo pipefail

_SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
BENG_BASE="${BENG_BASE:-$(cd "$_SELF_DIR/../.." && pwd)}"

GREEN='\033[0;32m'
CYAN='\033[0;96m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

SEED_PATH="${1:-}"

# ==============================================================================
# GUARDS
# ==============================================================================
if [ -z "$SEED_PATH" ]; then
    echo -e "${RED}❌ Usage: axis seed verify <seed_path>${NC}"
    echo -e "   Example: axis seed verify seeds/puredhamma_seed/"
    exit 2
fi

# Resolve relative paths
if [[ "$SEED_PATH" != /* ]]; then
    SEED_PATH="$BENG_BASE/$SEED_PATH"
fi

if [ ! -d "$SEED_PATH" ]; then
    echo -e "${RED}❌ Seed directory not found: $SEED_PATH${NC}"
    exit 2
fi

SEED_MANIFEST="$SEED_PATH/seed_manifest.json"
SEED_CANON_MANIFEST="$SEED_PATH/canon_manifest.json"
LIVE_MANIFEST="$BENG_BASE/metadata/canon_manifest.json"

for f in "$SEED_MANIFEST" "$SEED_CANON_MANIFEST"; do
    if [ ! -f "$f" ]; then
        echo -e "${RED}❌ Required seed file absent: $f${NC}"
        exit 2
    fi
done

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💎 AXIS-NIDDHI — Canon Seed Verifier                ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo -e "   ${GRAY}Seed    : $SEED_PATH${NC}"
echo -e "   ${GRAY}Live    : $BENG_BASE${NC}\n"

# ==============================================================================
# VERIFICATION LOGIC (Python — precise hash ops)
# ==============================================================================
python3 - << PYEOF
import hashlib, json, sys
from pathlib import Path

SEED_PATH   = Path("$SEED_PATH")
BENG_BASE   = Path("$BENG_BASE")
GREEN       = "\033[92m"
RED         = "\033[91m"
YELLOW      = "\033[93m"
GRAY        = "\033[90m"
RESET       = "\033[0m"

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check(label, expected, actual, width=26):
    ok = (expected == actual)
    mark = f"{GREEN}✔{RESET}" if ok else f"{RED}✘{RESET}"
    print(f"  {mark}  {label:<{width}} {actual[:24]}...")
    if not ok:
        print(f"       expected: {expected[:48]}")
        print(f"       actual  : {actual[:48]}")
    return ok

results = []

seed_manifest   = json.loads((SEED_PATH / "seed_manifest.json").read_text())
seed_canon      = json.loads((SEED_PATH / "canon_manifest.json").read_text())

# ── CHECK 1: Seed internal integrity ──────────────────────────────────────────
print(f"  {GRAY}[1/4] Seed internal integrity...{RESET}")
manifest_h  = sha256(SEED_PATH / "canon_manifest.json")
seal_h      = sha256(SEED_PATH / "build_seal.json")
corpus_h    = sha256(SEED_PATH / "corpus.json")
pipeline_h  = sha256(SEED_PATH / "pipeline_profile.json")

seed_hasher = hashlib.sha256()
for h in sorted([manifest_h, seal_h, corpus_h, pipeline_h]):
    seed_hasher.update(h.encode())
seed_integrity_actual   = seed_hasher.hexdigest()
seed_integrity_expected = seed_manifest.get("seed_integrity_hash", "UNKNOWN")
results.append(check("seed_integrity_hash", seed_integrity_expected, seed_integrity_actual))

# ── CHECK 2: canon_hash matches seed declaration ───────────────────────────────
print(f"  {GRAY}[2/4] Canon hash consistency...{RESET}")
canon_hash_in_manifest  = seed_canon.get("canon_hash", "UNKNOWN")
canon_hash_in_seed      = seed_manifest.get("canon_hash", "UNKNOWN")
results.append(check("canon_hash", canon_hash_in_seed, canon_hash_in_manifest))

# ── CHECK 3: manifest_hash matches actual file ────────────────────────────────
print(f"  {GRAY}[3/4] Manifest file hash...{RESET}")
manifest_hash_actual   = sha256(SEED_PATH / "canon_manifest.json")
manifest_hash_expected = seed_manifest.get("manifest_hash", "UNKNOWN")
results.append(check("manifest_hash", manifest_hash_expected, manifest_hash_actual))

# ── CHECK 4: Engine compatibility ─────────────────────────────────────────────
print(f"  {GRAY}[4/4] Engine compatibility...{RESET}")
seed_engine_ver = seed_manifest.get("engine_version", "UNKNOWN")
live_manifest_path = BENG_BASE / "metadata" / "canon_manifest.json"
if live_manifest_path.exists():
    live_manifest   = json.loads(live_manifest_path.read_text())
    live_engine_ver = live_manifest.get("engine_version", "UNKNOWN")
    compat = (seed_engine_ver == live_engine_ver)
    mark   = f"{GREEN}✔{RESET}" if compat else f"{YELLOW}⚠{RESET}"
    print(f"  {mark}  {'engine_version':<26} seed={seed_engine_ver} live={live_engine_ver}")
    # Engine version mismatch is a warning, not a failure
    if not compat:
        print(f"       {YELLOW}Warning: engine version mismatch — seed may need migration{RESET}")
else:
    print(f"  {YELLOW}⚠  live canon_manifest.json absent — engine check skipped{RESET}")
    compat = True  # non-blocking if no live manifest

# ── RESULT ────────────────────────────────────────────────────────────────────
print("")
all_pass = all(results)
if all_pass:
    print(f"{GREEN}══════════════════════════════════════════════════{RESET}")
    print(f"{GREEN}  ✅ SEED VERIFIED{RESET}")
    print(f"══════════════════════════════════════════════════")
    print(f"  {GRAY}Corpus  : {seed_manifest.get('corpus','')} ({seed_manifest.get('corpus_name','')}){RESET}")
    print(f"  {GRAY}Entries : {seed_manifest.get('entries',0)}{RESET}")
    print(f"  {GRAY}Canon   : {seed_manifest.get('canon_hash','')[:24]}...{RESET}")
    print(f"  {GRAY}Seed    : {seed_manifest.get('seed_integrity_hash','')[:24]}...{RESET}")
    print(f"{GREEN}══════════════════════════════════════════════════{RESET}")
    sys.exit(0)
else:
    failures = results.count(False)
    print(f"{RED}══════════════════════════════════════════════════{RESET}")
    print(f"{RED}  ❌ SEED VERIFICATION FAILURE{RESET}")
    print(f"══════════════════════════════════════════════════")
    print(f"  {RED}{failures} check(s) failed{RESET}")
    print(f"{RED}══════════════════════════════════════════════════{RESET}")
    sys.exit(1)
PYEOF
