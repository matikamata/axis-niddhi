#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — build_release_snapshot.sh
# ==============================================================================
# Versão:  V5.4 (Final Hardening Pass)
# Data:    2026-03-11
#
# PROPÓSITO:
#   Criar um release limpo e reproduzível em /beng-release
#   a partir do workspace de desenvolvimento /beng-fut.
#
#   O release contém APENAS:
#   • axis CLI (axis_cli.sh → executável como 'axis')
#   • 30 scripts CORE canonicais
#   • config.py + credenciais placeholder
#   • O ZIP fonte do PureDhamma (backup original)
#   • Estrutura de diretórios vazia (workspace limpo)
#   • README de onboarding do operador
#
#   O objetivo é criar um Canonical Corpus Publishing Engine
#   portátil: qualquer operador com o ZIP pode reconstruir
#   o site completo sem dependência do ambiente /beng-fut.
#
# GARANTIAS:
#   ✔ /beng-fut NÃO É MODIFICADO
#   ✔ Apenas cópia — zero mutações na fonte
#   ✔ config.py de release aponta para /beng-release (não /beng-fut)
#   ✔ Credenciais sensíveis NÃO são copiadas
#   ✔ Release é idempotente: pode ser re-executado com segurança
#
# USO:
#   sudo bash build_release_snapshot.sh
#   sudo bash build_release_snapshot.sh --dry-run    # simula sem copiar
#   sudo bash build_release_snapshot.sh --force      # sobrescreve release existente
#
# PRÉ-REQUISITOS:
#   • /beng-fut/pipeline/scripts/ com os 30 scripts CORE presentes
#   • /beng-fut/sources/*.zip (backup PureDhamma)
#   • verify_pipeline_integrity.sh passou sem erros CORE
#
# ESTRUTURA CRIADA:
#   /beng-release/
#   ├── axis*                           → CLI entry point (executável)
#   ├── README.md                       → guia de onboarding
#   ├── pipeline/
#   │   ├── scripts/                    → 30 CORE scripts
#   │   ├── 09-csl/                     → vazio (preenchido pelo SG)
#   │   ├── 01-extracted-htmls/en-US/   → vazio
#   │   ├── 02-preprocessed/en-US/      → vazio
#   │   ├── 13-ssg/                     → vazio (preenchido por setup_v54)
#   │   ├── 13-static-site/             → vazio (output do SSG)
#   │   ├── metadata/                   → dados de controle copiados
#   │   ├── logs/                       → vazio
#   │   ├── recovery/                   → vazio
#   │   └── snapshots/                  → vazio
#   └── sources/
#       └── *.zip                       → backup PureDhamma (copiado)
# ==============================================================================

set -euo pipefail

# ==============================================================================
# 1. FLAGS E CONFIGURAÇÃO
# ==============================================================================

DRY_RUN=false
FORCE=false

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --force)   FORCE=true ;;
    esac
done

# Source (development workspace — NEVER modified)
SRC_ROOT="/beng-fut"
SRC_PIPELINE="$SRC_ROOT/pipeline"
SRC_SCRIPTS="$SRC_PIPELINE/scripts"
SRC_SOURCES="$SRC_ROOT/sources"
SRC_METADATA="$SRC_PIPELINE/metadata"
SRC_13SSG="$SRC_PIPELINE/13-ssg"

# Destination (clean release — created by this script)
RELEASE_ROOT="/beng-release"
REL_PIPELINE="$RELEASE_ROOT/pipeline"
REL_SCRIPTS="$REL_PIPELINE/scripts"
REL_SOURCES="$RELEASE_ROOT/sources"
REL_METADATA="$REL_PIPELINE/metadata"

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;96m'; GRAY='\033[0;37m'; BOLD='\033[1m'; NC='\033[0m'

ok()    { echo -e "${GREEN}  ✔ $*${NC}"; }
fail()  { echo -e "${RED}  ✘ $*${NC}" >&2; exit 1; }
warn()  { echo -e "${YELLOW}  ⚠ $*${NC}"; }
info()  { echo -e "\n${CYAN}── $* ──────────────────────────────────────────${NC}"; }
detail(){ echo -e "${GRAY}    $*${NC}"; }
dryrun(){ echo -e "${YELLOW}  [DRY-RUN] $*${NC}"; }

copy_file() {
    local src="$1" dst="$2"
    if $DRY_RUN; then
        dryrun "cp $src → $dst"
    else
        cp "$src" "$dst"
        ok "$(basename "$src")"
    fi
}

make_dir() {
    if $DRY_RUN; then
        dryrun "mkdir -p $1"
    else
        mkdir -p "$1"
    fi
}

# ==============================================================================
# 2. BANNER
# ==============================================================================

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║  💎 AXIS-NIDDHI — Release Snapshot Builder V5.4          ║${NC}"
echo -e "${CYAN}${BOLD}║  Canonical Corpus Publishing Engine                       ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GRAY}  Source : $SRC_ROOT  (untouched)${NC}"
echo -e "${GRAY}  Release: $RELEASE_ROOT${NC}"
$DRY_RUN && echo -e "${YELLOW}  Mode   : DRY-RUN — no files will be created${NC}" \
         || echo -e "${GRAY}  Mode   : LIVE${NC}"
echo ""

# ==============================================================================
# 3. PRE-FLIGHT — SOURCE VALIDATION
# ==============================================================================

info "PRE-FLIGHT — Validating source workspace"

[[ -d "$SRC_PIPELINE" ]]  || fail "Source pipeline not found: $SRC_PIPELINE"
[[ -d "$SRC_SCRIPTS" ]]   || fail "Source scripts not found: $SRC_SCRIPTS"
[[ -d "$SRC_SOURCES" ]]   || fail "Sources dir not found: $SRC_SOURCES (ZIP must be here)"
[[ -f "$SRC_SCRIPTS/config.py" ]] || fail "config.py not found in source"
[[ -f "$SRC_SCRIPTS/run_full_pipeline.sh" ]] || fail "run_full_pipeline.sh not found"

# Detect source ZIP
ZIP_FILE=$(find "$SRC_SOURCES" -maxdepth 1 -name "*.zip" 2>/dev/null | sort | tail -1)
[[ -n "$ZIP_FILE" ]] || fail "No .zip found in $SRC_SOURCES — PureDhamma backup required"
ZIP_SIZE=$(du -sh "$ZIP_FILE" | awk '{print $1}')
ok "Source validated"
ok "ZIP: $(basename "$ZIP_FILE") ($ZIP_SIZE)"

# Verify integrity guard passes on source (CORE scripts check only)
if [[ -f "$SRC_SCRIPTS/verify_pipeline_integrity.sh" ]]; then
    detail "Running integrity guard on source..."
    if BENG_BASE="$SRC_PIPELINE" bash "$SRC_SCRIPTS/verify_pipeline_integrity.sh" --quiet; then
        ok "Source integrity guard: PASS"
    else
        warn "Source integrity guard reported errors — proceeding with caution"
        warn "CORE scripts may be incomplete in source"
    fi
fi

# ==============================================================================
# 4. RELEASE EXISTENCE CHECK
# ==============================================================================

info "Release directory"

if [[ -d "$RELEASE_ROOT" ]]; then
    if $FORCE; then
        warn "$RELEASE_ROOT already exists — --force: removing and rebuilding"
        $DRY_RUN || rm -rf "$RELEASE_ROOT"
    else
        warn "$RELEASE_ROOT already exists"
        warn "Use --force to rebuild from scratch, or remove manually."
        warn "Proceeding with incremental copy (existing files will be overwritten)."
    fi
else
    ok "$RELEASE_ROOT will be created"
fi

# ==============================================================================
# 5. CREATE DIRECTORY STRUCTURE
# ==============================================================================

info "Creating workspace directory tree"

# Core structure
make_dir "$REL_PIPELINE/scripts"
make_dir "$REL_PIPELINE/09-csl"
make_dir "$REL_PIPELINE/01-extracted-htmls/en-US"
make_dir "$REL_PIPELINE/02-preprocessed/en-US"
make_dir "$REL_PIPELINE/13-ssg"
make_dir "$REL_PIPELINE/13-static-site"
make_dir "$REL_PIPELINE/metadata"
make_dir "$REL_PIPELINE/logs"
make_dir "$REL_PIPELINE/recovery"
make_dir "$REL_PIPELINE/snapshots"
make_dir "$RELEASE_ROOT/sources"

ok "Directory tree created"

# ==============================================================================
# 6. COPY 30 CORE SCRIPTS
# ==============================================================================

info "Copying 30 CORE scripts"

CORE_SCRIPTS=(
    # Infrastructure
    "config.py" "pipeline_utils.py" "cls_tools.py" "models.py"
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
    "SD01_generate_asset_map.py" "SD03_static_site_build.py"
    "build.py" "SD04_wordpress_inject.py"
    # Reporting
    "MI99_mission_report.py"
)

COPIED=0
MISSING=0
for script in "${CORE_SCRIPTS[@]}"; do
    src="$SRC_SCRIPTS/$script"
    dst="$REL_SCRIPTS/$script"
    if [[ -f "$src" ]]; then
        copy_file "$src" "$dst"
        COPIED=$((COPIED + 1))
    else
        warn "MISSING in source — skipping: $script"
        MISSING=$((MISSING + 1))
    fi
done

[[ "$MISSING" -gt 0 ]] && warn "$MISSING CORE scripts were absent in source"
ok "$COPIED/30 CORE scripts copied"

# ==============================================================================
# 7. COPY CLI ENTRY POINTS
# ==============================================================================

info "Copying CLI entry points"

for cli in "axis_cli.sh" "verify_pipeline_integrity.sh" "setup_v54_static_site.sh"; do
    src="$SRC_SCRIPTS/$cli"
    [[ -f "$src" ]] && copy_file "$src" "$REL_SCRIPTS/$cli" || warn "Not found: $cli"
done

# Copy SSG modules needed by setup_v54
info "Copying SSG modules (deployed by setup_v54)"
SSG_MODULES=(
    "csl_loader.py" "identity_loader.py"
    "post_renderer.py" "index_renderer.py"
    "nav_builder.py" "link_resolver.py" "asset_mapper.py" "language_router.py"
    "base.html" "post.html" "index.html"
    "style.css" "main.js" "sw.js"
)
for mod in "${SSG_MODULES[@]}"; do
    src="$SRC_SCRIPTS/$mod"
    [[ -f "$src" ]] && copy_file "$src" "$REL_SCRIPTS/$mod" || warn "Not found: $mod"
done
if [[ -f "$SRC_SCRIPTS/reading-flow.js" ]]; then
    copy_file "$SRC_SCRIPTS/reading-flow.js" "$REL_SCRIPTS/reading-flow.js"
fi

# ==============================================================================
# 8. COPY METADATA (control data, no CSL content)
# ==============================================================================

info "Copying metadata control files"

# Safe to copy: these are reference data, not workspace state
METADATA_FILES=(
    "PDPN_01_Operational.csv"       # canonical post index (748 posts)
    "PDPN_02_Historical_Updated.csv" # historical record
    "MasterPDPN_Sections.csv"       # section canonical names
    "Glossario_v5.csv"              # Pāli glossary source
    "MasterPDPN_Raw.csv"            # raw PD index
)

for f in "${METADATA_FILES[@]}"; do
    src="$SRC_METADATA/$f"
    [[ -f "$src" ]] && copy_file "$src" "$REL_METADATA/$f" || warn "Metadata not found: $f"
done

# lineage_schema.json lives in config/ (not metadata/)
SRC_LINEAGE="$SRC_PIPELINE/config/lineage_schema.json"
if [[ -f "$SRC_LINEAGE" ]]; then
    make_dir "$REL_PIPELINE/config"
    copy_file "$SRC_LINEAGE" "$REL_PIPELINE/config/lineage_schema.json"
fi

# ==============================================================================
# 9. COPY PURЕDHAMMA SOURCE ZIP
# ==============================================================================

info "Copying PureDhamma source ZIP"

DST_ZIP="$RELEASE_ROOT/sources/$(basename "$ZIP_FILE")"
if $DRY_RUN; then
    dryrun "cp $ZIP_FILE → $DST_ZIP ($ZIP_SIZE)"
else
    cp "$ZIP_FILE" "$DST_ZIP"
    ok "$(basename "$ZIP_FILE") ($ZIP_SIZE) → /beng-release/sources/"
fi

# ==============================================================================
# 10. PATCH config.py FOR RELEASE (BENG_BASE override)
# ==============================================================================

info "Patching config.py for release environment"

# config.py in release: BENG_BASE points to /beng-release/pipeline by default.
# The script already supports env-var override: os.environ.get("BENG_BASE", ...)
# We only need to confirm the fallback path is self-consistent.
# Since config.py derives BASE_DIR from __file__ parent's parent, and the
# release places config.py at /beng-release/pipeline/scripts/config.py,
# the derived BASE_DIR will be /beng-release/pipeline — correct without any patch.

if $DRY_RUN; then
    dryrun "config.py self-consistent (BASE_DIR derived from __file__)"
else
    # Verify the derivation will work
    DERIVED_BASE=$(python3 - <<PYEOF 2>/dev/null || echo "ERROR"
import os
from pathlib import Path
cfg = Path("$REL_SCRIPTS/config.py")
if cfg.exists():
    # Simulate the derivation: config.py → scripts/ → pipeline/
    derived = cfg.parent.parent
    print(str(derived))
else:
    print("MISSING")
PYEOF
)
    if [[ "$DERIVED_BASE" == "$REL_PIPELINE" ]]; then
        ok "config.py BASE_DIR derivation correct: $DERIVED_BASE"
    else
        warn "config.py BASE_DIR may not match release path"
        warn "Expected: $REL_PIPELINE — Got: $DERIVED_BASE"
        warn "Set BENG_BASE=$REL_PIPELINE in operator shell if needed"
    fi
fi

# ==============================================================================
# 11. WRITE axis CLI ENTRY POINT
# ==============================================================================

info "Creating axis CLI entry point"

AXIS_EXEC="$RELEASE_ROOT/axis"

if $DRY_RUN; then
    dryrun "create $AXIS_EXEC (executable)"
else
    cat > "$AXIS_EXEC" << 'AXISCLI'
#!/usr/bin/env bash
# ==============================================================================
# axis — AXIS-NIDDHI CLI Entry Point
# ==============================================================================
# Installation:
#   echo "alias axis='bash /beng-release/axis'" >> ~/.bashrc
#   source ~/.bashrc
#
# Usage:
#   axis build-site     → generate full static site
#   axis preview        → local server on port 8080
#   axis status         → CSL / page / translation counts
#   axis doctor         → pre-flight integrity check (alias: axis integrity)
#   axis pipeline       → launch run_full_pipeline.sh (menu)
#   axis build-release  → instructions to build a new release from the Lab
# ==============================================================================

RELEASE_ROOT="/beng-release"
SCRIPTS="$RELEASE_ROOT/pipeline/scripts"
export BENG_BASE="$RELEASE_ROOT/pipeline"
CMD="${1:-help}"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

case "$CMD" in
    build-site)
        echo -e "${BOLD}▶ axis build-site${NC}"
        cd "$RELEASE_ROOT/pipeline/13-ssg"
        python3 build.py
        PAGES=$(find "$RELEASE_ROOT/pipeline/13-static-site/pages" \
            -name "index.html" 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ Build complete → $RELEASE_ROOT/pipeline/13-static-site/ ($PAGES pages)${NC}"
        ;;
    preview)
        PORT="${2:-8080}"
        OUTPUT="$RELEASE_ROOT/pipeline/13-static-site"
        echo -e "${CYAN}▶ axis preview — http://localhost:$PORT${NC}"
        echo "   Ctrl+C to stop"
        cd "$OUTPUT" && python3 -m http.server "$PORT"
        ;;
    status)
        echo -e "${BOLD}── AXIS-NIDDHI Release Status ──${NC}"
        CSL=$(find "$BENG_BASE/09-csl" -maxdepth 1 -mindepth 1 -type d \
            -regextype posix-extended \
            -regex ".*/[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}" 2>/dev/null | wc -l)
        PAGES=$(find "$BENG_BASE/13-static-site/pages" \
            -name "index.html" 2>/dev/null | wc -l)
        printf "  %-24s %s\n" "CSL entries:"   "$CSL"
        printf "  %-24s %s\n" "Pages built:"   "$PAGES"
        printf "  %-24s %s\n" "Release root:"  "$RELEASE_ROOT"
        printf "  %-24s %s\n" "BENG_BASE:"     "$BENG_BASE"
        ;;
    integrity|doctor)
        # axis doctor is the canonical UX name; axis integrity is preserved as alias
        echo -e "${BOLD}▶ axis doctor${NC}"
        bash "$SCRIPTS/verify_pipeline_integrity.sh"
        ;;
    pipeline)
        exec sudo --preserve-env=BENG_BASE \
            bash "$SCRIPTS/run_full_pipeline.sh" "${@:2}"
        ;;
    build-release)
        # build-release must always run from the Lab, not from within a release.
        echo -e "${BOLD}▶ axis build-release${NC}"
        echo ""
        echo -e "  This command must be run from the Lab workspace, not from a release."
        echo -e "  The release builder copies from /beng-fut and writes to /beng-release."
        echo ""
        echo -e "  Run:"
        echo -e "    sudo bash /beng-fut/pipeline/scripts/build_release_snapshot.sh"
        echo ""
        echo -e "  Options:"
        echo -e "    --dry-run    Simulate without copying files"
        echo -e "    --force      Rebuild from scratch (removes existing /beng-release)"
        echo ""
        ;;
    help|*)
        echo -e "${BOLD}axis${NC} — AXIS-NIDDHI CLI V5.4"
        echo ""
        echo "Commands:"
        echo "  axis build-site     Generate static site (748 pages)"
        echo "  axis preview        Local server on port 8080"
        echo "  axis status         Pipeline status"
        echo "  axis doctor         Pre-flight integrity check"
        echo "  axis pipeline       Launch full pipeline menu"
        echo "  axis build-release  Instructions to build a new release from the Lab"
        echo ""
        echo "Environment:"
        echo "  BENG_BASE=$BENG_BASE"
        echo ""
        ;;
esac
AXISCLI

    chmod +x "$AXIS_EXEC"
    ok "axis CLI created: $RELEASE_ROOT/axis"
fi

# ==============================================================================
# 12. WRITE OPERATOR README
# ==============================================================================

info "Writing operator README"

README="$RELEASE_ROOT/README.md"
if $DRY_RUN; then
    dryrun "create $README"
else
    cat > "$README" << 'README_CONTENT'
# AXIS-NIDDHI — Canonical Corpus Publishing Engine
**Version:** V5.4  
**Release:** /beng-release

---

## What this is

A self-contained, reproducible pipeline to rebuild the PureDhamma knowledge
archive from the original WordPress backup and publish it as a multilingual
static site.

---

## Quick start

```bash
# 1. Install alias (once)
echo "alias axis='bash /beng-release/axis'" >> ~/.bashrc && source ~/.bashrc

# 2. Check integrity
axis integrity

# 3. Run full rebuild (requires MySQL, Apache, WP-CLI)
axis pipeline --full

# 4. Preview the site
axis preview
```

---

## What's in this release

```
/beng-release/
├── axis                   CLI entry point
├── README.md              This file
├── sources/
│   └── *.zip              PureDhamma WordPress backup (canonical source)
└── pipeline/
    ├── scripts/           30 CORE pipeline scripts
    ├── metadata/          PDPN index, glossary, section map
    ├── 09-csl/            Canonical Source Library (empty → filled by SG phase)
    ├── 01-extracted-htmls/ Working dir (empty → filled by SG01)
    ├── 02-preprocessed/    Working dir (empty → filled by SG02)
    ├── 13-ssg/            SSG engine (empty → bootstrapped by setup_v54)
    ├── 13-static-site/    Site output (empty → filled by SD03)
    ├── logs/              Pipeline logs
    ├── recovery/          Crash recovery files
    └── snapshots/         CSL snapshots
```

---

## System requirements

- Ubuntu 22.04+ (or Debian 12+)
- Python 3.11+
- MySQL 8+
- Apache 2 + PHP 8.1 + mod_rewrite
- WP-CLI
- Python packages: `pandas pymysql beautifulsoup4 requests deepl jinja2 markdown`

---

## Configuration

All paths are derived from `BENG_BASE` environment variable:

```bash
export BENG_BASE=/beng-release/pipeline   # default for this release
```

Credentials (required before first run):
- DeepL API key → place in `pipeline/scripts/deepl_key.txt`
- WordPress App Password → place in `pipeline/scripts/wp_password.txt`

These files are NOT included in the release for security reasons.

---

## Pipeline phases

| Phase | Command | Effect |
|---|---|---|
| Full rebuild | `axis pipeline --full` | SG → SP → SA → SD |
| Genesis only | `axis pipeline --genesis` | WP extract → CSL build |
| Translation | `axis pipeline --preservation` | Identity + DeepL |
| Audit | `axis pipeline --audit` | SHA-256 integrity |
| Distribution | `axis pipeline --distribution` | Static site + WP |

---

## SSG bootstrap (first run only)

Before the SD phase can run, the SSG engine must be initialized:

```bash
bash /beng-release/pipeline/scripts/setup_v54_static_site.sh
```

This is automatic on `axis pipeline --full`.

---

*AXIS-NIDDHI — Preserving the Dhamma for future generations.*
README_CONTENT

    ok "README.md written"
fi

# ==============================================================================
# 13. SET PERMISSIONS
# ==============================================================================

info "Setting permissions"

if ! $DRY_RUN; then
    chmod +x "$RELEASE_ROOT/axis"
    chmod +x "$REL_SCRIPTS/run_full_pipeline.sh" 2>/dev/null || true
    chmod +x "$REL_SCRIPTS/SG00_reset_workspace.sh" 2>/dev/null || true
    chmod +x "$REL_SCRIPTS/SN01_snapshot_csl.sh" 2>/dev/null || true
    chmod +x "$REL_SCRIPTS/setup_v54_static_site.sh" 2>/dev/null || true
    chmod +x "$REL_SCRIPTS/verify_pipeline_integrity.sh" 2>/dev/null || true
    ok "Executable permissions set"
fi

# ==============================================================================
# 14. FINAL VERIFICATION (non-dry-run only)
# ==============================================================================

if ! $DRY_RUN; then
    info "Release verification"

    REL_ERRORS=0
    for f in "axis" "README.md" "sources/$(basename "$ZIP_FILE")"; do
        [[ -e "$RELEASE_ROOT/$f" ]] && ok "$f" || \
            { warn "MISSING in release: $f"; REL_ERRORS=$((REL_ERRORS + 1)); }
    done

    # Run integrity guard against the release (BENG_BASE = /beng-release/pipeline)
    if [[ -f "$REL_SCRIPTS/verify_pipeline_integrity.sh" ]]; then
        echo ""
        echo -e "${GRAY}  Running integrity guard against release...${NC}"
        if BENG_BASE="$REL_PIPELINE" bash "$REL_SCRIPTS/verify_pipeline_integrity.sh" --quiet; then
            ok "Release integrity guard: PASS (target: $REL_PIPELINE)"
        else
            warn "Release integrity guard: warnings present (see above)"
        fi
    fi
fi

# ==============================================================================
# 14b. SHA-256 FREEZE MANIFEST (P1 — archival seal)
# ==============================================================================
# Generates a cryptographic manifest of every file in the release.
# This seals the release: any future bitrot or tampering is detectable.
#
# Verification (by any future operator):
#   cd /beng-release && sha256sum --check release-manifest.sha256
# ==============================================================================

if ! $DRY_RUN; then
    info "Generating cryptographic seal"

    MANIFEST="$RELEASE_ROOT/release-manifest.sha256"
    MANIFEST_META="$RELEASE_ROOT/release-sealed-at.txt"

    # Generate SHA-256 for every file in the release
    # Excludes the manifest and metadata files themselves (no circular hash)
    find "$RELEASE_ROOT" -type f \
        ! -name "release-manifest.sha256" \
        ! -name "release-sealed-at.txt" \
        | sort \
        | while read -r f; do
            sha256sum "$f"
        done > "$MANIFEST"

    FILE_COUNT=$(wc -l < "$MANIFEST")

    # Write seal metadata
    cat > "$MANIFEST_META" << SEALEOF
engine:    AXIS-NIDDHI V5.4
corpus:    PureDhamma (748 posts · EN + PT-BR)
sealed_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
builder:   build_release_snapshot.sh
files:     ${FILE_COUNT}
SEALEOF

    ok "Cryptographic seal: release-manifest.sha256 (${FILE_COUNT} files)"
    ok "Seal metadata:      release-sealed-at.txt"
else
    dryrun "generate release-manifest.sha256 + release-sealed-at.txt"
fi

# ==============================================================================
# 15. SUMMARY
# ==============================================================================

echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
if $DRY_RUN; then
    echo -e "${YELLOW}${BOLD}║  DRY-RUN COMPLETE — No files were created                 ║${NC}"
else
    echo -e "${GREEN}${BOLD}║  ✅ RELEASE SNAPSHOT COMPLETE + SEALED                    ║${NC}"
fi
echo -e "${GREEN}${BOLD}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}${BOLD}║  Release: $RELEASE_ROOT                          ║${NC}"
echo -e "${GREEN}${BOLD}║  Source:  $SRC_ROOT (untouched)                  ║${NC}"
echo -e "${GREEN}${BOLD}║  Seal:    release-manifest.sha256                         ║${NC}"
echo -e "${GREEN}${BOLD}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}${BOLD}║  Next steps:                                              ║${NC}"
echo -e "${GREEN}${BOLD}║  1. Add DeepL key:  pipeline/scripts/deepl_key.txt        ║${NC}"
echo -e "${GREEN}${BOLD}║  2. Add WP password: pipeline/scripts/wp_password.txt     ║${NC}"
echo -e "${GREEN}${BOLD}║  3. Install alias:  echo \"alias axis='bash /beng-release/axis'\" >> ~/.bashrc${NC}"
echo -e "${GREEN}${BOLD}║  4. Check:          axis doctor                            ║${NC}"
echo -e "${GREEN}${BOLD}║  5. Run:            axis pipeline --full                   ║${NC}"
echo -e "${GREEN}${BOLD}║  6. Verify seal:    cd /beng-release && sha256sum --check release-manifest.sha256${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
