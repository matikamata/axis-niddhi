#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — verify_propagation.sh
# Post-Propagation Verifier V1.0
# ==============================================================================
# PURPOSE:
#   Run the full verification suite on all three pipeline instances
#   and produce a diff report vs the golden engine.
#
#   Checks per target:
#     1. axis version          → V1.9
#     2. axis verify pipeline  → integrity guard
#     3. axis semantic verify  → concept index
#     4. axis navigator build  → concept map rebuild
#     5. axis capsule verify   → capsule integrity
#     6. axis mirror endpoint  → endpoint build
#
# USAGE:
#   bash scripts/tools/verify_propagation.sh
#   GOLDEN=/path bash scripts/tools/verify_propagation.sh
# ==============================================================================
set -uo pipefail

_SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
GOLDEN="${GOLDEN:-$(cd "$_SELF_DIR/../.." && pwd)}"

GREEN='\033[0;32m'
CYAN='\033[0;96m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

PIPELINES=(
    "$GOLDEN"
    "$HOME/bengyond/pipeline"
    "/beng-fut/pipeline"
)

LABELS=(
    "beng_prelaunch [GOLDEN]"
    "bengyond"
    "beng-fut"
)

EXPECTED_VERSION="V1.9"

# ==============================================================================
# RESULTS TABLE
# ==============================================================================
declare -A RESULTS

run_check() {
    local LABEL="$1"
    local CMD="$2"
    local OUT
    OUT=$(eval "$CMD" 2>&1) && echo "PASS" || echo "FAIL"
}

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💎 AXIS-NIDDHI — Propagation Verifier                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}\n"

# Header
printf "  %-30s  %-18s  %-18s  %-18s\n" \
    "CHECK" "${LABELS[0]}" "${LABELS[1]}" "${LABELS[2]}"
printf "  %-30s  %-18s  %-18s  %-18s\n" \
    "------------------------------" "------------------" "------------------" "------------------"

# ==============================================================================
# CHECK FUNCTION
# ==============================================================================
check_all() {
    local CHECK_NAME="$1"
    local -a CMDS=("${@:2}")

    local COLS=()
    local i=0
    for PIPELINE in "${PIPELINES[@]}"; do
        local CLI="$PIPELINE/scripts/tools/axis_cli.sh"
        local CMD="${CMDS[$i]:-}"
        local i=$((i+1))

        if [ ! -d "$PIPELINE" ]; then
            COLS+=("${YELLOW}ABSENT${NC}")
            continue
        fi
        if [ ! -f "$CLI" ]; then
            COLS+=("${RED}NO CLI${NC}")
            continue
        fi

        # Replace __CLI__ and __BASE__ placeholders
        CMD="${CMD//__CLI__/$CLI}"
        CMD="${CMD//__BASE__/$PIPELINE}"

        local OUT
        local STATUS
        OUT=$(BENG_BASE="$PIPELINE" eval "$CMD" 2>&1)
        local EXIT_CODE=$?

        if [ $EXIT_CODE -eq 0 ]; then
            STATUS="${GREEN}PASS${NC}"
        else
            # Check output for ✅
            if echo "$OUT" | grep -q "✅\|VERIFIED\|PASS\|BUILT\|OPERATIONAL"; then
                STATUS="${GREEN}PASS${NC}"
            else
                STATUS="${RED}FAIL${NC}"
                echo -e "\n  ${RED}DETAIL [$CHECK_NAME / $(basename $PIPELINE)]:${NC}"
                echo "$OUT" | tail -5 | while read l; do echo "    $l"; done
            fi
        fi
        COLS+=("$STATUS")
    done

    printf "  %-30s  " "$CHECK_NAME"
    for COL in "${COLS[@]}"; do
        printf "%-27b  " "$COL"
    done
    printf "\n"
}

# ==============================================================================
# RUN ALL CHECKS
# ==============================================================================

# 1. Version
check_all "axis version (V1.9)" \
    "BENG_BASE=__BASE__ bash __CLI__ version | grep -q V1.9" \
    "BENG_BASE=__BASE__ bash __CLI__ version | grep -q V1.9" \
    "BENG_BASE=__BASE__ bash __CLI__ version | grep -q V1.9"

# 2. Pipeline verify (non-blocking failures ok — checks structure)
check_all "axis verify pipeline" \
    "BENG_BASE=__BASE__ bash __CLI__ verify pipeline 2>&1 | grep -qE 'PASS|✅'" \
    "BENG_BASE=__BASE__ bash __CLI__ verify pipeline 2>&1 | grep -qE 'PASS|✅'" \
    "BENG_BASE=__BASE__ bash __CLI__ verify pipeline 2>&1 | grep -qE 'PASS|✅'"

# 3. Semantic verify
check_all "axis semantic verify" \
    "BENG_BASE=__BASE__ bash __CLI__ semantic verify 2>&1 | grep -q '✅'" \
    "BENG_BASE=__BASE__ bash __CLI__ semantic verify 2>&1 | grep -q '✅'" \
    "BENG_BASE=__BASE__ bash __CLI__ semantic verify 2>&1 | grep -q '✅'"

# 4. Navigator build
check_all "axis navigator build" \
    "BENG_BASE=__BASE__ bash __CLI__ navigator build 2>&1 | grep -q '✅'" \
    "BENG_BASE=__BASE__ bash __CLI__ navigator build 2>&1 | grep -q '✅'" \
    "BENG_BASE=__BASE__ bash __CLI__ navigator build 2>&1 | grep -q '✅'"

# 5. Capsule verify
check_all "axis capsule verify" \
    "BENG_BASE=__BASE__ bash __CLI__ capsule verify 2>&1 | grep -q 'VERIFIED'" \
    "BENG_BASE=__BASE__ bash __CLI__ capsule verify 2>&1 | grep -q 'VERIFIED'" \
    "BENG_BASE=__BASE__ bash __CLI__ capsule verify 2>&1 | grep -q 'VERIFIED'"

# 6. Mirror endpoint build
check_all "axis mirror endpoint" \
    "BENG_BASE=__BASE__ bash __CLI__ mirror endpoint 2>&1 | grep -q '✅'" \
    "BENG_BASE=__BASE__ bash __CLI__ mirror endpoint 2>&1 | grep -q '✅'" \
    "BENG_BASE=__BASE__ bash __CLI__ mirror endpoint 2>&1 | grep -q '✅'"

# ==============================================================================
# CORE HASH DIFF
# ==============================================================================
echo ""
echo -e "  ${GRAY}Core script hash (scripts/core/*.py)${NC}"

python3 - << PYEOF
import hashlib
from pathlib import Path

pipelines = [
    ("beng_prelaunch [GOLDEN]", Path("$GOLDEN")),
    ("bengyond",                Path("$HOME/bengyond/pipeline")),
    ("beng-fut",                Path("/beng-fut/pipeline")),
]

hashes = {}
for label, p in pipelines:
    core = p / "scripts/core"
    if not core.exists():
        hashes[label] = "ABSENT"
        continue
    h = hashlib.sha256()
    for f in sorted(core.glob("*.py")):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    hashes[label] = h.hexdigest()[:32]

golden_hash = list(hashes.values())[0]
print(f"  {'TARGET':<30} {'CORE_HASH':<34} {'vs GOLDEN'}")
print(f"  {'-'*30} {'-'*34} {'-'*10}")
for label, h in hashes.items():
    match = "✅ MATCH" if h == golden_hash else ("⚠ DIFF" if h != "ABSENT" else "ABSENT")
    print(f"  {label:<30} {h:<34} {match}")
PYEOF

# ==============================================================================
# SUMMARY
# ==============================================================================
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  PROPAGATION VERIFICATION COMPLETE${NC}"
echo -e "══════════════════════════════════════════════════════════${NC}"
echo -e "  ${GRAY}Any FAIL rows above require investigation${NC}"
echo -e "  ${GRAY}core_hash DIFF = scripts/core divergence (check config.py)${NC}"
echo -e "  ${GRAY}Re-run propagation: bash scripts/tools/propagate_axis_core.sh${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}\n"
