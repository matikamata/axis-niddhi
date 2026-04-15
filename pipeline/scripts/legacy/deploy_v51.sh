#!/usr/bin/env bash
# ==============================================================================
# AXIS-NIDDHI V5.1 — DEPLOY & RENAME SCRIPT
# Alinha /beng-fut/pipeline/scripts/ com run_full_pipeline_v51.sh
# Gerado em: 2026-03-07
#
# COMO USAR:
#   cd /beng-fut/pipeline/scripts
#   bash deploy_v51.sh
# ==============================================================================

set -euo pipefail

SCRIPTS="/beng-fut/pipeline/scripts"
SSG_DIR="/beng-fut/pipeline/13-ssg"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
info() { echo -e "${CYAN}ℹ️  $*${NC}"; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  AXIS-NIDDHI V5.1 — Deploy & Rename                  ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$SCRIPTS"

# ==============================================================================
# STEP 1 — COPIAR NOVOS ARQUIVOS V5.1 (precisam estar em /tmp/v51/)
# ==============================================================================
# Coloque os arquivos gerados pelo Claude em /tmp/v51/ antes de rodar este script:
#   pipeline_utils.py
#   config_v51.py           → será copiado como config.py
#   SP02_upgrade_identity_v51.py
#   SP05_fix_headers_v51.py
#   SP10_translate_deepl_v51.py
#   SG00_reset_workspace.sh  (já deployado)
#   SA01_final_audit.py      (novo — substitui S06)
#   run_full_pipeline_v51.sh → será copiado como run_full_pipeline.sh

info "STEP 1 — Copiando novos arquivos V5.1..."

V51="/tmp/v51"

if [ ! -d "$V51" ]; then
    warn "Pasta /tmp/v51/ não encontrada — pulando cópias automáticas."
    warn "Copie manualmente os arquivos V5.1 antes de prosseguir."
else
    [ -f "$V51/pipeline_utils.py"              ] && cp "$V51/pipeline_utils.py"              "$SCRIPTS/pipeline_utils.py"              && ok "pipeline_utils.py copiado"
    [ -f "$V51/config_v51.py"                  ] && cp "$V51/config_v51.py"                  "$SCRIPTS/config.py"                      && ok "config.py atualizado (V5.1)"
    [ -f "$V51/SP02_upgrade_identity_v51.py"   ] && cp "$V51/SP02_upgrade_identity_v51.py"   "$SCRIPTS/SP02_upgrade_identity.py"        && ok "SP02_upgrade_identity.py"
    [ -f "$V51/SP05_fix_headers_v51.py"        ] && cp "$V51/SP05_fix_headers_v51.py"        "$SCRIPTS/SP05_fix_headers.py"             && ok "SP05_fix_headers.py"
    [ -f "$V51/SP10_translate_deepl_v51.py"    ] && cp "$V51/SP10_translate_deepl_v51.py"    "$SCRIPTS/SP10_translate_deepl.py"         && ok "SP10_translate_deepl.py"
    [ -f "$V51/SA01_final_audit.py"            ] && cp "$V51/SA01_final_audit.py"            "$SCRIPTS/SA01_final_audit.py"             && ok "SA01_final_audit.py"
    [ -f "$V51/run_full_pipeline_v51.sh"       ] && cp "$V51/run_full_pipeline_v51.sh"       "$SCRIPTS/run_full_pipeline.sh"            && ok "run_full_pipeline.sh atualizado"
fi

# ==============================================================================
# STEP 2 — RENAMES: arquivos existentes → nomes esperados pelo orquestrador
# ==============================================================================
info "STEP 2 — Aplicando renames..."

rename_mv() {
    local src="$1" dst="$2"
    if [ -f "$src" ] && [ ! -f "$dst" ]; then
        mv "$src" "$dst"
        ok "  mv $src → $dst"
    elif [ -f "$dst" ]; then
        warn "  $dst já existe — skip (verifique manualmente)"
    else
        warn "  $src não encontrado — skip"
    fi
}

# DI Phase
rename_mv "00a_auditoria_sql_vs_csl.py"       "DI00_sql_vs_csl_audit.py"

# SG Phase
# SG00_reset_workspace.sh — JÁ EXISTE ✅ (deployado anteriormente)
rename_mv "S01_extract_v3_global.py"           "SG01_extract_html.py"
rename_mv "S02_preprocess_v4_1_iframes.py"     "SG02_preprocess_html.py"
rename_mv "S03_build_csl_v1.py"                "SG03_build_csl.py"
rename_mv "S03b_harvest_assets.py"             "SG04_harvest_assets.py"

# SP Phase
rename_mv "S00_migrate_ptbr_v1.py"             "SP01_migrate_ptbr.py"
# SP02_upgrade_identity.py — JÁ EXISTE ✅ (copiado no STEP 1)
rename_mv "S05_mass_migration_schema31.py"      "SP03_mass_migration.py"
rename_mv "phase5_migration.py"                 "SP04_phase5_migration.py"
# SP05_fix_headers.py — JÁ EXISTE ✅ (copiado no STEP 1)
rename_mv "SC_audio_converter.py"              "SP06_audio_converter.py"
rename_mv "S08a_compile_glossary.py"           "SP07_compile_glossary.py"
rename_mv "S08b_glossary_gate.py"              "SP08_glossary_gate.py"
rename_mv "S09_generate_translation_menu.py"   "SP09_translation_menu.py"
# SP10_translate_deepl.py — JÁ EXISTE ✅ (copiado no STEP 1)

# SA Phase
# SA01_final_audit.py — JÁ EXISTE ✅ (copiado/já estava no HD)

# SD Phase
rename_mv "S14_generate_asset_map.py"          "SD01_generate_asset_map.py"
rename_mv "S13_generate_slug_map.py"           "SD02_generate_slug_map.py"
# SD03: build.py em 13-ssg/ — ver STEP 4
rename_mv "S11_inject_wordpress.py"            "SD04_wordpress_inject.py"

# MI Phase
rename_mv "S99_mission_report.py"              "MI99_mission_report.py"

# ==============================================================================
# STEP 3 — PERMISSÕES
# ==============================================================================
info "STEP 3 — Ajustando permissões..."
chmod +x "$SCRIPTS/SG00_reset_workspace.sh"
chmod +x "$SCRIPTS/run_full_pipeline.sh"
ok "Scripts .sh executáveis"

# ==============================================================================
# STEP 4 — SD03: renomear build.py em 13-ssg/
# ==============================================================================
info "STEP 4 — SD03 em 13-ssg/..."
if [ -f "$SSG_DIR/build.py" ] && [ ! -f "$SSG_DIR/SD03_static_site_build.py" ]; then
    cp "$SSG_DIR/build.py" "$SSG_DIR/SD03_static_site_build.py"
    ok "  13-ssg/build.py → SD03_static_site_build.py (cópia preserva original)"
elif [ -f "$SSG_DIR/SD03_static_site_build.py" ]; then
    warn "  SD03_static_site_build.py já existe em 13-ssg/ — OK"
else
    warn "  build.py não encontrado em $SSG_DIR"
fi

# ==============================================================================
# STEP 5 — VERIFICAÇÃO FINAL
# ==============================================================================
info "STEP 5 — Verificação: todos os scripts esperados pelo orquestrador..."

REQUIRED=(
    "SG00_reset_workspace.sh"
    "SG01_extract_html.py"
    "SG02_preprocess_html.py"
    "SG03_build_csl.py"
    "SG04_harvest_assets.py"
    "SP01_migrate_ptbr.py"
    "SP02_upgrade_identity.py"
    "SP03_mass_migration.py"
    "SP04_phase5_migration.py"
    "SP05_fix_headers.py"
    "SP06_audio_converter.py"
    "SP07_compile_glossary.py"
    "SP08_glossary_gate.py"
    "SP09_translation_menu.py"
    "SP10_translate_deepl.py"
    "SA01_final_audit.py"
    "SD01_generate_asset_map.py"
    "SD02_generate_slug_map.py"
    "SD04_wordpress_inject.py"
    "MI99_mission_report.py"
    "DI00_sql_vs_csl_audit.py"
    "config.py"
    "pipeline_utils.py"
    "run_full_pipeline.sh"
)

MISSING=0
for f in "${REQUIRED[@]}"; do
    if [ -f "$SCRIPTS/$f" ]; then
        ok "  $f"
    else
        echo -e "${RED}  ❌ MISSING: $f${NC}"
        MISSING=$((MISSING + 1))
    fi
done

# SD03 em 13-ssg/
if [ -f "$SSG_DIR/SD03_static_site_build.py" ]; then
    ok "  13-ssg/SD03_static_site_build.py"
else
    echo -e "${RED}  ❌ MISSING: 13-ssg/SD03_static_site_build.py${NC}"
    MISSING=$((MISSING + 1))
fi

echo ""
if [ "$MISSING" -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ DEPLOY COMPLETO — Todos os scripts presentes      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${CYAN}Próximo passo:${NC}"
    echo "  ./run_full_pipeline.sh --full"
else
    echo -e "${RED}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⚠️  DEPLOY INCOMPLETO — $MISSING arquivo(s) faltando   ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "  Resolva os arquivos MISSING acima antes de prosseguir."
fi
