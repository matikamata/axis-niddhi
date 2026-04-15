#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — propagate_axis_core.sh
# Core Propagation Script V1.0
# ==============================================================================
# PURPOSE:
#   Package the golden AXIS core from beng_prelaunch and propagate
#   to bengyond and beng-fut.
#
#   SAFE — never touches:
#     09-csl/            Canon Source Library
#     03-translations/   Translation artifacts
#     13-static-site/    Generated site
#     01-source/         Extracted source HTML
#     02-preprocessed/   Preprocessed HTML
#     scripts/private/   Credentials
#     ledger/            Append-only ledger (merged, not overwritten)
#     seeds/             Rebuilt per-node
#
#   PROPAGATED:
#     scripts/core/       34 canonical pipeline scripts
#     scripts/tools/      All tool scripts (including axis_cli.sh)
#     semantic/           Concept index
#     navigator/          Concept map + study paths
#     mirror/             Mirror registry (mirrors.json)
#     capsule/            Time capsule snapshot
#     metadata/slug_map.json
#
# USAGE:
#   bash scripts/tools/propagate_axis_core.sh
#   GOLDEN=/path/to/golden bash scripts/tools/propagate_axis_core.sh
#   DRY_RUN=1 bash scripts/tools/propagate_axis_core.sh
# ==============================================================================
set -euo pipefail

_SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
GOLDEN="${GOLDEN:-$(cd "$_SELF_DIR/../.." && pwd)}"
DRY_RUN="${DRY_RUN:-0}"

GREEN='\033[0;32m'
CYAN='\033[0;96m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

TARGETS=(
    "$HOME/bengyond/pipeline"
    "/beng-fut/pipeline"
)

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATESTAMP=$(date -u +"%Y%m%d_%H%M%S")
PKG_NAME="axis_engine_core_${DATESTAMP}.tar.gz"
PKG_PATH="/tmp/$PKG_NAME"

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💎 AXIS-NIDDHI — Core Propagation                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo -e "   ${GRAY}Golden    : $GOLDEN${NC}"
echo -e "   ${GRAY}Targets   : ${TARGETS[*]}${NC}"
echo -e "   ${GRAY}Package   : $PKG_PATH${NC}"
if [ "$DRY_RUN" = "1" ]; then
    echo -e "   ${YELLOW}MODE: DRY-RUN — no files will be written${NC}"
fi
echo ""

# ==============================================================================
# GUARD: verify golden
# ==============================================================================
for REQUIRED in \
    "$GOLDEN/scripts/core" \
    "$GOLDEN/scripts/tools/axis_cli.sh" \
    "$GOLDEN/semantic/index.json" \
    "$GOLDEN/navigator/concept_map.json" \
    "$GOLDEN/capsule/capsule_manifest.json"; do
    if [ ! -e "$REQUIRED" ]; then
        echo -e "${RED}❌ Golden source incomplete: $REQUIRED${NC}"
        exit 1
    fi
done
echo -e "  ${GREEN}✔  Golden source validated${NC}"

# ==============================================================================
# STEP 1 — BUILD PACKAGE
# ==============================================================================
echo -e "\n  ${GRAY}[1/4] Building core package from golden...${NC}"

cd "$GOLDEN"

# Build tar from golden — include only safe propagation targets
tar -czf "$PKG_PATH" \
    --exclude="scripts/private" \
    --exclude="scripts/legacy" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude=".git" \
    scripts/core \
    scripts/tools \
    semantic \
    navigator \
    mirror \
    capsule \
    2>/dev/null || true

# Also add slug_map to metadata if present
if [ -f "$GOLDEN/metadata/slug_map.json" ]; then
    tar -rf /tmp/slug_map_tmp.tar \
        --transform 's|^|metadata/|' \
        -C "$GOLDEN/metadata" slug_map.json 2>/dev/null || true
fi

PKG_SIZE=$(du -sh "$PKG_PATH" | cut -f1)
PKG_FILES=$(tar -tzf "$PKG_PATH" | wc -l)

echo -e "     ${GRAY}Package   : $PKG_NAME${NC}"
echo -e "     ${GRAY}Size      : $PKG_SIZE${NC}"
echo -e "     ${GRAY}Files     : $PKG_FILES${NC}"
echo -e "  ${GREEN}✔  Package built${NC}"

if [ "$DRY_RUN" = "1" ]; then
    echo -e "\n  ${YELLOW}[DRY-RUN] Stopping before deployment${NC}"
    exit 0
fi

# ==============================================================================
# STEP 2 — PROPAGATE TO EACH TARGET
# ==============================================================================
echo -e "\n  ${GRAY}[2/4] Propagating to targets...${NC}"

PROP_RESULTS=()

for TARGET in "${TARGETS[@]}"; do
    echo -e "\n  ${CYAN}── Target: $TARGET${NC}"

    if [ ! -d "$TARGET" ]; then
        echo -e "     ${YELLOW}⚠ Target does not exist: $TARGET — skipping${NC}"
        PROP_RESULTS+=("SKIP:$TARGET")
        continue
    fi

    # Verify target has a scripts/core (is a real pipeline)
    if [ ! -d "$TARGET/scripts/core" ] && [ ! -d "$TARGET/scripts" ]; then
        echo -e "     ${YELLOW}⚠ Target has no scripts/ directory — skipping${NC}"
        PROP_RESULTS+=("SKIP:$TARGET")
        continue
    fi

    # Backup target scripts/tools/axis_cli.sh if exists
    if [ -f "$TARGET/scripts/tools/axis_cli.sh" ]; then
        cp "$TARGET/scripts/tools/axis_cli.sh" \
           "$TARGET/scripts/tools/axis_cli.sh.bak_${DATESTAMP}" 2>/dev/null || true
        echo -e "     ${GRAY}Backed up: axis_cli.sh.bak_${DATESTAMP}${NC}"
    fi

    # Extract package into target (overwrite core files)
    tar -xzf "$PKG_PATH" -C "$TARGET" 2>/dev/null

    # Ensure all scripts executable
    chmod +x "$TARGET/scripts/tools/"*.sh 2>/dev/null || true
    chmod +x "$TARGET/scripts/core/"*.sh  2>/dev/null || true
    chmod +x "$TARGET/scripts/tools/"*.py 2>/dev/null || true
    chmod +x "$TARGET/scripts/core/"*.py  2>/dev/null || true

    # Copy slug_map to metadata/ if needed
    if [ ! -f "$TARGET/metadata/slug_map.json" ] && \
       [ -f "$GOLDEN/metadata/slug_map.json" ]; then
        mkdir -p "$TARGET/metadata"
        cp "$GOLDEN/metadata/slug_map.json" "$TARGET/metadata/"
        echo -e "     ${GRAY}slug_map.json → metadata/  ✔${NC}"
    fi

    # Copy config.py if target is missing critical patches
    if [ -f "$GOLDEN/scripts/core/config.py" ]; then
        cp "$GOLDEN/scripts/core/config.py" "$TARGET/scripts/core/config.py"
        echo -e "     ${GRAY}config.py synced  ✔${NC}"
    fi

    # Bootstrap ledger if target has none (append-only — never overwrite existing)
    if [ ! -f "$TARGET/ledger/ledger.json" ] && [ -f "$GOLDEN/ledger/ledger.json" ]; then
        mkdir -p "$TARGET/ledger/entries"
        cp "$GOLDEN/ledger/ledger.json" "$TARGET/ledger/"
        cp "$GOLDEN/ledger/entries/"*.json "$TARGET/ledger/entries/" 2>/dev/null || true
        echo -e "     ${GRAY}ledger/ bootstrapped from golden  ✔${NC}"
    fi

    # Bootstrap seeds if target has none
    if [ ! -d "$TARGET/seeds" ] && [ -d "$GOLDEN/seeds" ]; then
        cp -r "$GOLDEN/seeds" "$TARGET/seeds"
        echo -e "     ${GRAY}seeds/ bootstrapped from golden  ✔${NC}"
    fi

    # Bootstrap releases/tags if target has none
    if [ ! -d "$TARGET/releases/tags" ] && [ -d "$GOLDEN/releases/tags" ]; then
        mkdir -p "$TARGET/releases"
        cp -r "$GOLDEN/releases/tags" "$TARGET/releases/tags"
        echo -e "     ${GRAY}releases/tags/ bootstrapped  ✔${NC}"
    fi

    echo -e "     ${GREEN}✔  Propagated${NC}"
    PROP_RESULTS+=("OK:$TARGET")
done

# ==============================================================================
# STEP 3 — VERSION CHECK ON EACH TARGET
# ==============================================================================
echo -e "\n  ${GRAY}[3/4] Version check...${NC}"

for TARGET in "${TARGETS[@]}"; do
    [[ ! -d "$TARGET" ]] && continue
    CLI="$TARGET/scripts/tools/axis_cli.sh"
    [[ ! -f "$CLI" ]] && continue

    echo -ne "     ${GRAY}$(basename $(dirname $TARGET))/$(basename $TARGET): ${NC}"
    VERSION_OUT=$(BENG_BASE="$TARGET" bash "$CLI" version 2>/dev/null | grep "CLI" | head -1 || echo "ERROR")
    echo -e "${GRAY}$VERSION_OUT${NC}"
done

# ==============================================================================
# STEP 4 — INTEGRITY SNAPSHOT
# ==============================================================================
echo -e "\n  ${GRAY}[4/4] Computing propagation manifest...${NC}"

python3 - << PYEOF
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path

golden = Path("$GOLDEN")
targets = [Path(t) for t in "$GOLDEN $HOME/bengyond/pipeline $HOME/beng-fut/pipeline".split()
           if Path(t).exists()]

results = {}
for t in [golden] + [Path("$HOME/bengyond/pipeline"), Path("$HOME/beng-fut/pipeline")]:
    if not t.exists():
        continue
    cli = t / "scripts/tools/axis_cli.sh"
    core = t / "scripts/core"
    label = "golden" if str(t) == "$GOLDEN" else t.name
    h = hashlib.sha256()
    if core.exists():
        for f in sorted(core.rglob("*.py")):
            h.update(f.name.encode())
    core_hash = h.hexdigest()[:16]
    cli_exists = cli.exists()
    results[label] = {
        "path":       str(t),
        "cli":        cli_exists,
        "core_hash":  core_hash,
    }

print("  Propagation results:")
print(f"  {'TARGET':<20} {'CLI':<6} {'CORE_HASH'}")
print(f"  {'-'*20} {'-'*6} {'-'*16}")
for label, r in results.items():
    cli_ok = "✔" if r["cli"] else "✘"
    print(f"  {label:<20} {cli_ok:<6} {r['core_hash']}")
PYEOF

# ==============================================================================
# SUMMARY
# ==============================================================================
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ PROPAGATION COMPLETE${NC}"
echo -e "══════════════════════════════════════════════════════════"
echo -e "  ${GRAY}Golden    : $GOLDEN${NC}"
echo -e "  ${GRAY}Package   : $PKG_NAME ($PKG_SIZE)${NC}"
echo -e "  ${GRAY}Timestamp : $TIMESTAMP${NC}"
echo ""
for R in "${PROP_RESULTS[@]}"; do
    STATUS="${R%%:*}"
    PATH_="${R#*:}"
    if [ "$STATUS" = "OK" ]; then
        echo -e "  ${GREEN}✔  $PATH_${NC}"
    else
        echo -e "  ${YELLOW}⚠  $PATH_ (skipped)${NC}"
    fi
done
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}\n"
echo -e "  ${CYAN}Next: run verification on each target:${NC}"
echo -e "  ${GRAY}bash scripts/tools/verify_propagation.sh${NC}\n"

# Cleanup
rm -f "$PKG_PATH" /tmp/slug_map_tmp.tar 2>/dev/null || true
