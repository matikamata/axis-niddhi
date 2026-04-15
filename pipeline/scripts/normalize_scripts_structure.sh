#!/usr/bin/env bash
# ==============================================================================
# AXIS-NIDDHI — normalize_scripts_structure.sh
# Script Structure Normalization — V5.4 → Distribution Ready
# Run from: /home/sanghop/beng_prelaunch/pipeline/scripts/
# ==============================================================================
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "📁 Normalizing: $SCRIPTS_DIR"

# ------------------------------------------------------------------------------
# 1. CREATE SUBDIRECTORIES
# ------------------------------------------------------------------------------
mkdir -p "$SCRIPTS_DIR/core"
mkdir -p "$SCRIPTS_DIR/legacy"
mkdir -p "$SCRIPTS_DIR/tools"
mkdir -p "$SCRIPTS_DIR/private"
echo "✅ Subdirectories created: core/ legacy/ tools/ private/"

# ------------------------------------------------------------------------------
# 2. MOVE CORE SCRIPTS
# ------------------------------------------------------------------------------
CORE=(
  config.py
  pipeline_utils.py
  cls_tools.py
  SG00_reset_workspace.sh
  SG01_extract_html.py
  SG02_preprocess_html.py
  SG03_build_csl.py
  SG04_harvest_assets.py
  SP00_freeze_translations.py
  SP01_migrate_ptbr.py
  SP01b_restore_translations.py
  SP02_upgrade_identity.py
  SP03_mass_migration.py
  SP04_phase5_migration.py
  SP05_fix_headers.py
  SP06_audio_converter.py
  SP07_compile_glossary.py
  SP08_glossary_gate.py
  SP09_translation_menu.py
  SP10_translate_deepl.py
  SP11_translate_titles.py
  SA01_final_audit.py
  SA02_freeze_manifest.py
  SA03_translation_progress.py
  SD01_generate_asset_map.py
  SD02_generate_slug_map.py
  SD03_static_site_build.py
  SD04_wordpress_inject.py
  MI99_mission_report.py
  DI00_sql_vs_csl_audit.py
  verify_pipeline_integrity.sh
  build_release_snapshot_v4.sh
  run_full_pipeline.sh
  SN01_snapshot_csl.sh
)

echo ""
echo "── Moving CORE scripts ──"
for f in "${CORE[@]}"; do
  if [ -f "$SCRIPTS_DIR/$f" ]; then
    mv "$SCRIPTS_DIR/$f" "$SCRIPTS_DIR/core/$f"
    echo "  ✔ core/$f"
  else
    echo "  ⚠ MISSING: $f"
  fi
done

# ------------------------------------------------------------------------------
# 3. MOVE CREDENTIALS TO PRIVATE
# ------------------------------------------------------------------------------
PRIVATE=(
  deepl_key.txt
  wp_password.txt
  github_token.txt
)

echo ""
echo "── Moving PRIVATE credentials ──"
for f in "${PRIVATE[@]}"; do
  if [ -f "$SCRIPTS_DIR/$f" ]; then
    mv "$SCRIPTS_DIR/$f" "$SCRIPTS_DIR/private/$f"
    echo "  ✔ private/$f"
  else
    echo "  ⚠ ABSENT (ok): $f"
  fi
done

# ------------------------------------------------------------------------------
# 4. MOVE LEGACY SCRIPTS
# ------------------------------------------------------------------------------
LEGACY=(
  "00b_genesis_twins_v4_smart.py"
  "01_extract_v3_global.py"
  "02_preprocess_v4_1_iframes.py"
  "03_build_csl_v1.py"
  "04_compile_glossary.py"
  "05_translate_pilot_v5_surgeon.py"
  "05a_upload_glossary_deepl.py"
  "06_inject_pilot_v3_pages.py"
  "07a_generate_menu_v6_schema_aware.py"
  "07b_execute_menu_v3_guardian.py"
  "08_mass_inject_v5_resilient.py"
  "09_upgrade_identity_v3_audited.py"
  "10_mass_migration_phase5.py"
  "11_final_audit_and_cleanup.py"
  "12_fix_headers_and_identity.py"
  "14_sync_titles_from_ledger.py"
  "15_Relatório_de_Estrutura_de_Subpastas.py"
  "S04_upgrade_identity_v3.py"
  "S07_fix_headers_identity.py"
  "S10_execute_translation_deepl.py"
  "SP05_fix_headers_v51.py"
  "reset_brasileirinho_v12.2.sh"
  "deploy_v51.sh"
  "run_full_pipeline (Cópia).sh"
  "SG01_extract_html (Cópia).py"
  "SG04_harvest_assets (Cópia).py"
  "SP06_audio_converter (Cópia).py"
  "SP07_compile_glossary (Cópia).py"
  "SP08_glossary_gate (Cópia).py"
  "SP02_upgrade_identity__Cópia_.py"
  "SP10_translate_deepl__Cópia_.py"
  "SP11_translate_titles__Cópia_.py"
  "cls_tools__Cópia_.py"
  "cls_tools__Cópia_2_.py"
)

echo ""
echo "── Moving LEGACY scripts ──"
for f in "${LEGACY[@]}"; do
  if [ -f "$SCRIPTS_DIR/$f" ]; then
    mv "$SCRIPTS_DIR/$f" "$SCRIPTS_DIR/legacy/$f"
    echo "  ✔ legacy/$f"
  else
    echo "  ⚠ ABSENT (ok): $f"
  fi
done

# Move DEPRECATED folder if present
if [ -d "$SCRIPTS_DIR/DEPRECATED" ]; then
  mv "$SCRIPTS_DIR/DEPRECATED" "$SCRIPTS_DIR/legacy/DEPRECATED"
  echo "  ✔ legacy/DEPRECATED/"
fi

# Move session artifact folders
for d in "20260311_Vayo" "sp12_guardian"; do
  if [ -d "$SCRIPTS_DIR/$d" ]; then
    mv "$SCRIPTS_DIR/$d" "$SCRIPTS_DIR/legacy/$d"
    echo "  ✔ legacy/$d/"
  fi
done

# ------------------------------------------------------------------------------
# 5. MOVE TOOLS
# ------------------------------------------------------------------------------
TOOLS=(
  anchor_manifest.py
  anchor_manifest_v2.py
  anchor_manifest_ultimate.py
  auditoria_forense_youtube_csl.py
  audit_ssg_zip.py
  rebuild_translation_status.py
  validate_cls_pipeline.sh
  test_cls_integration_dryrun.sh
  redeploy_cls_and_backfill.sh
  activate_cls_v11.sh
  seed_ptbr.sh
  setup_v54_static_site.sh
  run_sp11_and_report.sh
  axis_cli.sh
  axis_runner.sh
  build_release_snapshot.sh
  build_release_snapshot_v2.sh
)

echo ""
echo "── Moving TOOLS ──"
for f in "${TOOLS[@]}"; do
  if [ -f "$SCRIPTS_DIR/$f" ]; then
    mv "$SCRIPTS_DIR/$f" "$SCRIPTS_DIR/tools/$f"
    echo "  ✔ tools/$f"
  else
    echo "  ⚠ ABSENT (ok): $f"
  fi
done

# ------------------------------------------------------------------------------
# 6. MOVE MISC ARTIFACTS (not scripts)
# ------------------------------------------------------------------------------
echo ""
echo "── Moving MISC artifacts ──"
for f in resultado_passo10.txt translation_status.json; do
  if [ -f "$SCRIPTS_DIR/$f" ]; then
    mv "$SCRIPTS_DIR/$f" "$SCRIPTS_DIR/legacy/$f"
    echo "  ✔ legacy/$f (artifact)"
  fi
done

# ------------------------------------------------------------------------------
# 7. CREATE .gitignore IN scripts/
# ------------------------------------------------------------------------------
cat > "$SCRIPTS_DIR/.gitignore" << 'GITIGNORE'
# AXIS-NIDDHI — scripts/.gitignore
# Credentials — NEVER commit to any repository or release

private/
private/deepl_key.txt
private/wp_password.txt
private/github_token.txt

# Python cache
__pycache__/
*.pyc
*.pyo

# Session artifacts
*.log
resultado_passo10.txt
GITIGNORE

echo ""
echo "✅ .gitignore created → private/ protected"

# ------------------------------------------------------------------------------
# 8. SUMMARY
# ------------------------------------------------------------------------------
echo ""
echo "══════════════════════════════════════════"
echo "  NORMALIZATION COMPLETE"
echo "══════════════════════════════════════════"
echo "  core/    $(ls "$SCRIPTS_DIR/core/" | wc -l) files"
echo "  legacy/  $(ls "$SCRIPTS_DIR/legacy/" | wc -l) files"
echo "  tools/   $(ls "$SCRIPTS_DIR/tools/" | wc -l) files"
echo "  private/ $(ls "$SCRIPTS_DIR/private/" | wc -l) files"
echo ""
echo "  Run next:"
echo "  bash scripts/core/run_full_pipeline.sh"
echo "══════════════════════════════════════════"
