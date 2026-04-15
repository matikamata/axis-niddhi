#!/usr/bin/env bash
# ==============================================================================
# AXIS-NIDDHI — propagate_patches.sh
# Propagate normalization patches to /bengyond and /beng-fut
# Run from: /home/sanghop/beng_prelaunch/pipeline/
# ==============================================================================
set -euo pipefail

SRC_PIPELINE="/home/sanghop/beng_prelaunch/pipeline"
TARGETS=(
    "/home/sanghop/bengyond/pipeline"
    "/beng-fut/pipeline"
)

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;96m'
GRAY='\033[0;37m'
NC='\033[0m'

echo -e "\n${CYAN}💎 AXIS-NIDDHI — Patch Propagation${NC}"
echo -e "   Source: $SRC_PIPELINE\n"

# ==============================================================================
# PATCH FUNCTION
# ==============================================================================
patch_target() {
    local TARGET="$1"
    echo -e "${CYAN}── Patching: $TARGET ──${NC}"

    if [ ! -d "$TARGET" ]; then
        echo -e "  ${YELLOW}⚠ Target absent: $TARGET — skipping${NC}"
        return
    fi

    local SCRIPTS_DIR="$TARGET/scripts"

    # 1. Create core/ structure if absent
    if [ ! -d "$SCRIPTS_DIR/core" ]; then
        echo -e "  ${YELLOW}⚠ scripts/core/ absent — run normalize_scripts_structure.sh first${NC}"
        echo -e "  ${GRAY}Skipping patch for $TARGET${NC}"
        return
    fi

    # 2. Patch config.py BASE_DIR (scripts/core/ depth = 3x parent)
    local CONFIG="$SCRIPTS_DIR/core/config.py"
    if [ -f "$CONFIG" ]; then
        if grep -q "parent.parent.parent" "$CONFIG"; then
            echo -e "  ${GREEN}✔ config.py already patched (parent×3)${NC}"
        else
            # Backup
            cp "$CONFIG" "$CONFIG.bak"
            # Apply patch
            sed -i 's|Path(os.environ.get("BENG_BASE", str(Path(__file__).resolve().parent.parent)))|Path(os.environ.get("BENG_BASE", str(Path(__file__).resolve().parent.parent.parent)))|g' "$CONFIG"
            echo -e "  ${GREEN}✔ config.py BASE_DIR patched (parent×3)${NC}"
        fi

        # Add DIR_03_TRANSLATIONS if absent
        if ! grep -q "DIR_03_TRANSLATIONS" "$CONFIG"; then
            sed -i 's|DIR_09_CSL         = BASE_DIR / "09-csl"|DIR_09_CSL         = BASE_DIR / "09-csl"\nDIR_03_TRANSLATIONS= BASE_DIR / "03-translations"          # Translation Preservation Layer (SP00/SP01b)|g' "$CONFIG"
            echo -e "  ${GREEN}✔ DIR_03_TRANSLATIONS added to config.py${NC}"
        else
            echo -e "  ${GREEN}✔ DIR_03_TRANSLATIONS already present${NC}"
        fi

        # Add DIR_03_PTBR if absent
        if ! grep -q "DIR_03_PTBR" "$CONFIG"; then
            echo "" >> "$CONFIG"
            echo "# Legacy alias — SP01 default src (BrasileirinhoHD external HD)." >> "$CONFIG"
            echo "DIR_03_PTBR = Path('/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline/09-csl')" >> "$CONFIG"
            echo -e "  ${GREEN}✔ DIR_03_PTBR legacy alias added${NC}"
        else
            echo -e "  ${GREEN}✔ DIR_03_PTBR already present${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠ config.py not found at $CONFIG${NC}"
    fi

    # 3. Patch verify_pipeline_integrity.sh SCRIPTS path
    local GUARD="$SCRIPTS_DIR/core/verify_pipeline_integrity.sh"
    if [ -f "$GUARD" ]; then
        if grep -q 'SCRIPTS="$BENG_BASE/scripts/core"' "$GUARD"; then
            echo -e "  ${GREEN}✔ verify_pipeline_integrity.sh already patched${NC}"
        else
            sed -i 's|SCRIPTS="$BENG_BASE/scripts"|SCRIPTS="$BENG_BASE/scripts/core"|g' "$GUARD"
            echo -e "  ${GREEN}✔ verify_pipeline_integrity.sh SCRIPTS path patched${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠ verify_pipeline_integrity.sh not found — may still be in scripts/ root${NC}"
        # Try scripts/ root (pre-normalization)
        local GUARD_ROOT="$SCRIPTS_DIR/verify_pipeline_integrity.sh"
        if [ -f "$GUARD_ROOT" ]; then
            sed -i 's|SCRIPTS="$BENG_BASE/scripts"|SCRIPTS="$BENG_BASE/scripts/core"|g' "$GUARD_ROOT"
            echo -e "  ${GREEN}✔ verify_pipeline_integrity.sh patched at scripts/ root${NC}"
        fi
    fi

    # 4. Copy SP00 + SP01b if absent
    for script in SP00_freeze_translations.py SP01b_restore_translations.py SA04_generate_canon_manifest.py; do
        local DST="$SCRIPTS_DIR/core/$script"
        local SRC_FILE="$SRC_PIPELINE/scripts/core/$script"
        if [ ! -f "$DST" ] && [ -f "$SRC_FILE" ]; then
            cp "$SRC_FILE" "$DST"
            echo -e "  ${GREEN}✔ $script copied to core/${NC}"
        elif [ -f "$DST" ]; then
            echo -e "  ${GREEN}✔ $script already present${NC}"
        else
            echo -e "  ${YELLOW}⚠ $script absent in source — skipping${NC}"
        fi
    done

    # 5. Copy axis_engine.json to metadata/
    local ENGINE_SRC="$SRC_PIPELINE/metadata/axis_engine.json"
    local ENGINE_DST="$TARGET/metadata/axis_engine.json"
    if [ -f "$ENGINE_SRC" ] && [ ! -f "$ENGINE_DST" ]; then
        cp "$ENGINE_SRC" "$ENGINE_DST"
        echo -e "  ${GREEN}✔ axis_engine.json → metadata/${NC}"
    fi

    # 6. Verify core count
    local CORE_COUNT
    CORE_COUNT=$(ls "$SCRIPTS_DIR/core/" 2>/dev/null | wc -l)
    echo -e "  ${GRAY}core/ scripts: $CORE_COUNT${NC}"

    # 7. Quick config resolution test
    local RESOLVED
    RESOLVED=$(python3 -c "
import sys; sys.path.insert(0, '$SCRIPTS_DIR/core')
import config
print(config.BASE_DIR)
" 2>/dev/null || echo "FAILED")
    if [ "$RESOLVED" = "$TARGET" ]; then
        echo -e "  ${GREEN}✔ BASE_DIR resolves correctly: $RESOLVED${NC}"
    else
        echo -e "  ${YELLOW}⚠ BASE_DIR: $RESOLVED (expected $TARGET)${NC}"
    fi

    echo ""
}

# ==============================================================================
# APPLY TO ALL TARGETS
# ==============================================================================
for TARGET in "${TARGETS[@]}"; do
    patch_target "$TARGET"
done

echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo -e "${CYAN}  PATCH PROPAGATION COMPLETE${NC}"
echo -e "${CYAN}══════════════════════════════════════════${NC}\n"
