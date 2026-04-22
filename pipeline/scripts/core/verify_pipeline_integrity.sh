#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — verify_pipeline_integrity.sh
# ==============================================================================
# Versão:  V5.4 (Final Hardening Pass)
# Data:    2026-03-11
#
# PROPÓSITO:
#   Verificação rápida de integridade antes de executar o pipeline.
#   Confirma que todos os 30 scripts CORE existem, config.py é
#   importável, diretórios necessários existem e o SSG está pronto.
#
# USO:
#   bash verify_pipeline_integrity.sh              # verbose
#   BENG_BASE=/path bash verify_pipeline_integrity.sh
#   bash verify_pipeline_integrity.sh --quiet      # exit-code only (CI)
#
# EXIT CODES:
#   0 = PASS (incluindo PASS WITH WARNINGS)
#   1 = FAIL (scripts CORE ausentes ou config.py não importável)
#
# TEMPO DE EXECUÇÃO: < 1 segundo
# ==============================================================================

set -uo pipefail

# ==============================================================================
# 1. CONFIGURAÇÃO
# ==============================================================================

BENG_BASE="${BENG_BASE:-/beng-fut/pipeline}"
BENG_ROOT="${BENG_BASE%/pipeline}"
SCRIPTS="$BENG_BASE/scripts/core"
SSG_DIR="$BENG_BASE/13-ssg"
QUIET="${1:-}"

if [[ "$QUIET" != "--quiet" ]]; then
    GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
    CYAN='\033[0;96m'; GRAY='\033[0;37m'; BOLD='\033[1m'; NC='\033[0m'
else
    GREEN=''; RED=''; YELLOW=''; CYAN=''; GRAY=''; BOLD=''; NC=''
fi

# ==============================================================================
# 2. HELPERS
# ==============================================================================

ERRORS=0
WARNINGS=0

pass()  { [[ "$QUIET" != "--quiet" ]] && echo -e "${GREEN}  ✔ $*${NC}"; }
fail()  { echo -e "${RED}  ✘ $*${NC}" >&2; ERRORS=$((ERRORS + 1)); }
warn()  { [[ "$QUIET" != "--quiet" ]] && echo -e "${YELLOW}  ⚠ $*${NC}"; WARNINGS=$((WARNINGS + 1)); }
info()  { [[ "$QUIET" != "--quiet" ]] && echo -e "${CYAN}$*${NC}"; }
detail(){ [[ "$QUIET" != "--quiet" ]] && echo -e "${GRAY}    $*${NC}"; }

# ==============================================================================
# 3. BANNER
# ==============================================================================

if [[ "$QUIET" != "--quiet" ]]; then
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  💎 AXIS-NIDDHI — Pipeline Integrity Guard V5.4          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo -e "${GRAY}   BENG_BASE: $BENG_BASE${NC}"
    echo ""
fi

# ==============================================================================
# 4. CHECK 1 — 30 CORE SCRIPTS
# ==============================================================================

info "── [1/6] CORE Scripts ──────────────────────────────────────"

# 28 scripts live in scripts/; models.py lives in 13-ssg/src/; build.py in 13-ssg/
CORE_SCRIPTS=(
    # Infrastructure (in scripts/)
    "config.py" "pipeline_utils.py" "cls_tools.py"
    # Orchestration
    "run_full_pipeline.sh" "SN01_snapshot_csl.sh"
    # [SG] Genesis
    "SG00_reset_workspace.sh" "SG01_extract_html.py"
    "SG02_preprocess_html.py" "SG03_build_csl.py" "SG04_harvest_assets.py"
    # [SP] Preservation
    "SP01_migrate_ptbr.py" "SP02_upgrade_identity.py"
    "SP03_mass_migration.py" "SP04_phase5_migration.py"
    "SP05_fix_headers.py" "SP06_audio_converter.py"
    "SP07_compile_glossary.py" "SP08_glossary_gate.py"
    "SP09_translation_menu.py" "SP10_translate_deepl.py" "SP11_translate_titles.py"
    # [SA] Audit
    "SA01_final_audit.py" "SA02_freeze_manifest.py" "SA03_translation_progress.py"
    # [SD] Distribution
    "SD01_generate_asset_map.py" "SD03_static_site_build.py" "SD04_wordpress_inject.py"
    # Reporting
    "MI99_mission_report.py"
)

# SSG engine files checked separately (live in 13-ssg/, not scripts/)
SSG_DIR="$BENG_BASE/13-ssg"

CORE_TOTAL=${#CORE_SCRIPTS[@]}
CORE_FOUND=0

for script in "${CORE_SCRIPTS[@]}"; do
    if [[ -f "$SCRIPTS/$script" ]]; then
        CORE_FOUND=$((CORE_FOUND + 1))
    else
        fail "MISSING CORE: $script"
    fi
done

# Check models.py (real location: 13-ssg/src/models.py)
# Also accept scripts/models.py as valid (release copies it there for setup_v54)
if [[ -f "$SSG_DIR/src/models.py" || -f "$SCRIPTS/models.py" ]]; then
    CORE_FOUND=$((CORE_FOUND + 1))
else
    fail "MISSING CORE: models.py (checked: 13-ssg/src/models.py and scripts/models.py)"
fi

# Check build.py (real location: 13-ssg/build.py)
# Also accept scripts/build.py (release copies it there for reference)
if [[ -f "$SSG_DIR/build.py" || -f "$SCRIPTS/build.py" ]]; then
    CORE_FOUND=$((CORE_FOUND + 1))
else
    fail "MISSING CORE: build.py (checked: 13-ssg/build.py and scripts/build.py)"
fi

CORE_TOTAL=$((CORE_TOTAL + 2))  # account for models.py + build.py
[[ "$CORE_FOUND" -eq "$CORE_TOTAL" ]] && pass "CORE scripts verified ($CORE_FOUND/$CORE_TOTAL)"

# ==============================================================================
# 5. CHECK 2 — config.py IMPORTABLE
# ==============================================================================

info "── [2/6] config.py importability ──────────────────────────"

if [[ ! -f "$SCRIPTS/config.py" ]]; then
    fail "config.py not found: $SCRIPTS/config.py"
else
    CONFIG_RESULT=$(python3 - <<PYEOF 2>&1
import sys
sys.path.insert(0, "$SCRIPTS")
try:
    import config
    required = ['BASE_DIR','DIR_09_CSL','DIR_01_EXTRACTED','DIR_02_PREPROCESSED',
                'DIR_13_SSG_ENGINE','DIR_13_SSG_OUTPUT','METADATA_DIR',
                'LOG_DIR','SCHEMA_VERSION']
    missing = [a for a in required if not hasattr(config, a)]
    if missing:
        print("MISSING_ATTRS:" + ",".join(missing))
    else:
        print("OK:" + str(config.BASE_DIR))
except ImportError as e:
    print("IMPORT_ERROR:" + str(e))
except Exception as e:
    print("ERROR:" + str(e))
PYEOF
)
    if [[ "$CONFIG_RESULT" == OK:* ]]; then
        pass "config.py importable — BASE_DIR=${CONFIG_RESULT#OK:}"
    elif [[ "$CONFIG_RESULT" == MISSING_ATTRS:* ]]; then
        fail "config.py missing attributes: ${CONFIG_RESULT#MISSING_ATTRS:}"
    else
        fail "config.py not importable: $CONFIG_RESULT"
    fi
fi

# ==============================================================================
# 6. CHECK 3 — CSL DIRECTORY
# ==============================================================================

info "── [3/6] CSL Directory ─────────────────────────────────────"

CSL_DIR="$BENG_BASE/09-csl"
if [[ -d "$CSL_DIR" ]]; then
    CSL_COUNT=$(find "$CSL_DIR" -maxdepth 1 -mindepth 1 -type d \
        -regextype posix-extended \
        -regex ".*/[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}" 2>/dev/null | wc -l)
    if [[ "$CSL_COUNT" -gt 0 ]]; then
        pass "CSL directory detected ($CSL_COUNT entries)"
    else
        warn "CSL exists but empty — run: ./run_full_pipeline.sh --genesis"
    fi
else
    warn "CSL absent (first run) — will be created by SG03"
fi

# ==============================================================================
# 7. CHECK 4 — REQUIRED DIRECTORIES
# ==============================================================================

info "── [4/6] Required Directories ──────────────────────────────"

DIRS_FOUND=0
for dir in "01-extracted-htmls" "02-preprocessed" "metadata" "logs"; do
    if [[ -d "$BENG_BASE/$dir" ]]; then
        DIRS_FOUND=$((DIRS_FOUND + 1))
    else
        warn "Directory absent (SG00 will create): $dir/"
    fi
done
[[ "$DIRS_FOUND" -eq 4 ]] && pass "Required directories present (4/4)"

if [[ -d "$SSG_DIR" ]]; then
    pass "SSG engine directory present: 13-ssg/"
else
    warn "13-ssg/ absent — run: bash $BENG_BASE/scripts/tools/setup_v54_static_site.sh"
fi

# ==============================================================================
# 8. CHECK 5 — SSG ENGINE
# ==============================================================================

info "── [5/6] SSG Engine ────────────────────────────────────────"

SSG_ISSUES=0
if [[ -f "$SSG_DIR/build.py" ]]; then
    pass "13-ssg/build.py present (engine real)"
else
    warn "13-ssg/build.py absent"; SSG_ISSUES=$((SSG_ISSUES + 1))
fi

if [[ -f "$SSG_DIR/SD03_static_site_build.py" ]]; then
    pass "13-ssg/SD03_static_site_build.py present (compat shim)"
else
    detail "Shim SD03 ausente (ok no modelo vivo: run_full usa build.py)"
fi

if [[ -d "$SSG_DIR/src/loaders" && \
      -d "$SSG_DIR/src/renderers" && \
      -d "$SSG_DIR/src/transformers" ]]; then
    pass "13-ssg/src/ package structure present"
else
    warn "13-ssg/src/ incomplete or absent"; SSG_ISSUES=$((SSG_ISSUES + 1))
fi

if [[ -f "$SSG_DIR/templates/base.html" && \
      -f "$SSG_DIR/templates/post.html" && \
      -f "$SSG_DIR/templates/index.html" && \
      -f "$SSG_DIR/templates/welcome.html" ]]; then
    pass "13-ssg/templates payload mínimo presente (inclui welcome.html)"
else
    warn "13-ssg/templates incompleto (base/post/index/welcome)"; SSG_ISSUES=$((SSG_ISSUES + 1))
fi

if [[ -f "$SSG_DIR/static/css/style.css" && \
      -f "$SSG_DIR/static/css/typography-pro.css" && \
      -f "$SSG_DIR/static/js/main.js" && \
      -f "$SSG_DIR/static/js/sw.js" && \
      -f "$SSG_DIR/static/favicon.svg" && \
      -f "$SSG_DIR/static/buddha-2.jpg" && \
      -f "$SSG_DIR/static/assets/BodhiCircuitLeaf.png" && \
      -f "$SSG_DIR/static/leaf.html" ]]; then
    pass "13-ssg/static payload mínimo presente"
else
    warn "13-ssg/static payload mínimo incompleto"; SSG_ISSUES=$((SSG_ISSUES + 1))
fi

[[ "$SSG_ISSUES" -gt 0 ]] && \
    detail "Auto-bootstrap no SD. Ou execute: bash $BENG_BASE/scripts/tools/setup_v54_static_site.sh"

# ==============================================================================
# 9. CHECK 6 — PYTHON ENVIRONMENT
# ==============================================================================

info "── [6/6] Python Environment ────────────────────────────────"

if command -v python3 &>/dev/null; then
    pass "Python available: $(python3 --version 2>&1)"
else
    fail "python3 not found in PATH"
fi

VENV_DIR="$BENG_ROOT/.venv"
if [[ -d "$VENV_DIR" ]]; then
    pass "Virtual environment present: .venv/"
else
    warn "Virtual environment absent: $VENV_DIR"
    detail "Create: python3 -m venv $VENV_DIR"
    detail "Install: pip install pandas pymysql beautifulsoup4 requests deepl jinja2 markdown"
fi

PKG_FOUND=0; PKG_MISSING=()
for pkg in pandas pymysql bs4 requests jinja2; do
    python3 -c "import $pkg" 2>/dev/null && \
        PKG_FOUND=$((PKG_FOUND + 1)) || PKG_MISSING+=("$pkg")
done

if [[ "${#PKG_MISSING[@]}" -eq 0 ]]; then
    pass "Python packages present ($PKG_FOUND/5: pandas pymysql bs4 requests jinja2)"
else
    warn "Python packages missing: ${PKG_MISSING[*]}"
    detail "Install: pip install ${PKG_MISSING[*]}"
fi

# ==============================================================================
# 10. RESULT
# ==============================================================================

echo ""
[[ "$QUIET" != "--quiet" ]] && \
    echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"

if [[ "$ERRORS" -eq 0 && "$WARNINGS" -eq 0 ]]; then
    [[ "$QUIET" != "--quiet" ]] && {
        echo -e "${GREEN}${BOLD}  ══ INTEGRITY: PASS ✔ ══${NC}"
        echo -e "${GRAY}  All checks passed. Pipeline is ready.${NC}"
        echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
        echo ""
    }
    exit 0
elif [[ "$ERRORS" -eq 0 ]]; then
    [[ "$QUIET" != "--quiet" ]] && {
        echo -e "${YELLOW}${BOLD}  ══ INTEGRITY: PASS WITH WARNINGS ($WARNINGS) ⚠ ══${NC}"
        echo -e "${GRAY}  Warnings are non-blocking. Pipeline can run.${NC}"
        echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
        echo ""
    }
    exit 0
else
    [[ "$QUIET" != "--quiet" ]] && {
        echo -e "${RED}${BOLD}  ══ INTEGRITY: FAIL ($ERRORS error(s), $WARNINGS warning(s)) ✘ ══${NC}"
        echo -e "${GRAY}  Resolve errors above before running the pipeline.${NC}"
        echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
        echo ""
    }
    exit 1
fi
