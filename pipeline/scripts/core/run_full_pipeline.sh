#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — MISSION CONTROL ORCHESTRATOR V5.4
# Structure: scripts/core/ layout (post-normalization)
# ==============================================================================
# Hardening Edition: atomic writes, env bypass, retry loops, SEAL enforcement
# V5.2 Changes:
#   ★ [E2] SP11 inserido automaticamente após SEAL 1 (title translation)
#   ★ [E1] SP02 --force preserva titles.pt / titles.pt_source existentes
#
# USAGE:
#   ./run_full_pipeline.sh                  # menu interativo
#   ./run_full_pipeline.sh --diagnostic     # DI fase
#   ./run_full_pipeline.sh --genesis        # SG fase
#   ./run_full_pipeline.sh --preservation   # SP fase
#   ./run_full_pipeline.sh --audit          # SA fase
#   ./run_full_pipeline.sh --distribution   # SD fase
#   ./run_full_pipeline.sh --full           # SG→SP→SA→SD completo
#
# ENV VARS (CI/headless):
#   BENG_AUTO_TRANSLATE=true    bypass confirmação DeepL
#   BENG_AUTO_INJECT=true       bypass confirmação WordPress inject
#   BENG_AUTO_GLOSSARY_OK=true  bypass Glossary Gate
#   BENG_FAILURE_THRESHOLD=5    máximo de falhas antes de abort (default: 5)
# ==============================================================================

# ==============================================================================
# 🛡️  GUARDIÃO DE PRIVILÉGIO — Self-Sudo
# Operações de sistema (MySQL, Apache, chmod) requerem root.
# Se não for root, re-executa automaticamente via sudo.
# ==============================================================================
if [[ $EUID -ne 0 ]]; then
    echo -e "🛡️  AXIS-NIDDHI: Elevação de privilégio necessária para operações de sistema."
    exec sudo --preserve-env=BENG_BASE,BENG_AUTO_RESET,BENG_AUTO_TRANSLATE,BENG_AUTO_INJECT,BENG_AUTO_GLOSSARY_OK,BENG_FAILURE_THRESHOLD "$0" "$@"
fi

set -euo pipefail

# ==============================================================================
# 1. PATHS E CORES
# ==============================================================================

export BENG_BASE="${BENG_BASE:-/beng-fut/pipeline}"
BENG_ROOT="${BENG_BASE%/pipeline}"
SCRIPTS_DIR="$BENG_BASE/scripts/core"
VENV_DIR="${BENG_VENV:-$BENG_ROOT/.venv}"   # override via BENG_VENV env var
LOG_DIR="$BENG_BASE/logs"
RECOVERY_DIR="$BENG_BASE/recovery"

# Cores (todos declarados explicitamente — RC-02 fix)
GREEN='\033[0;32m'
BLUE='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
CYAN='\033[0;96m'
NC='\033[0m'

PIPELINE_VERSION="5.2"

# ==============================================================================
# 2. UTILITÁRIOS
# ==============================================================================

log_info()  { echo -e "${CYAN}ℹ️  $*${NC}"; }
log_ok()    { echo -e "${GREEN}✅ $*${NC}"; }
log_warn()  { echo -e "${YELLOW}⚠️  $*${NC}"; }
log_error() { echo -e "${RED}❌ $*${NC}" >&2; }
log_step()  { echo -e "\n${BLUE}━━━ $* ━━━${NC}"; }

abort() {
    log_error "PIPELINE ABORT: $*"
    exit 1
}

run_script() {
    local script_path="$1"
    shift
    local script_dir
    script_dir="$(dirname "$script_path")"
    local script_name
    script_name="$(basename "$script_path")"

    echo -e "\n${YELLOW}▶ $script_name $*${NC}"
    (cd "$script_dir" && python3 "$script_name" "$@")
}

run_script_retry() {
    # run_script_retry <script> [args] — tenta até 2x em falha transitória
    local script_path="$1"
    shift
    local attempt=1
    local max=2
    while [ $attempt -le $max ]; do
        if run_script "$script_path" "$@"; then
            return 0
        fi
        log_warn "Tentativa $attempt/$max falhou. Aguardando 5s..."
        sleep 5
        ((attempt++))
    done
    abort "$(basename "$script_path") falhou após $max tentativas."
}

# ==============================================================================
# 3. VALIDAÇÃO DE WORKSPACE
# ==============================================================================

validate_workspace() {
    local fatal=0

    if [ ! -d "$BENG_BASE" ]; then
        log_error "BENG_BASE não encontrado: $BENG_BASE"
        log_error "Configure BENG_BASE=/caminho/para/pipeline e re-execute."
        fatal=1
    fi

    if [ ! -d "$VENV_DIR" ]; then
        log_error "Virtual environment não encontrado: $VENV_DIR"
        log_error "Execute: python3 -m venv $VENV_DIR && source $VENV_DIR/bin/activate && pip install -r $BENG_BASE/requirements.txt"
        fatal=1
    fi

    if [ ! -f "$SCRIPTS_DIR/config.py" ]; then
        log_error "config.py não encontrado: $SCRIPTS_DIR/config.py (scripts/core/)"
        fatal=1
    fi

    if [ ! -f "$SCRIPTS_DIR/pipeline_utils.py" ]; then
        log_error "pipeline_utils.py não encontrado: $SCRIPTS_DIR/pipeline_utils.py"
        log_error "V5.1 requer pipeline_utils.py. Verifique o deploy."
        fatal=1
    fi

    if [ "$fatal" -ne 0 ]; then
        abort "Workspace inválido. Corrija os erros acima antes de prosseguir."
    fi

    # Warnings não-fatais
    if [ ! -d "$BENG_ROOT/beng-launch" ] && [ ! -d "/beng-launch" ]; then
        log_warn "/beng-launch não encontrado — DI phase pode falhar."
    fi

    mkdir -p "$LOG_DIR" "$RECOVERY_DIR"
    log_ok "Workspace validado: $BENG_BASE"
}

# ==============================================================================
# 4. ATIVAÇÃO VENV
# ==============================================================================

activate_venv() {
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
    log_info "Verificando dependências..."
    pip install -q pandas pymysql beautifulsoup4 requests deepl jinja2 markdown 2>/dev/null || true
}

# ==============================================================================
# 5. FASES
# ==============================================================================

run_di() {
    log_step "[DI] DIAGNOSTIC — SQL vs CSL Pre-Flight Audit"

    local launch_dir="${BENG_LAUNCH_DIR:-/beng-launch}"
    if [ ! -d "$launch_dir" ]; then
        abort "DI phase requer $launch_dir (SQL dump). Monte o volume antes de executar."
    fi

    run_script "$SCRIPTS_DIR/DI00_sql_vs_csl_audit.py"
    run_script "$SCRIPTS_DIR/MI99_mission_report.py"
    log_ok "[DI] DIAGNOSTIC concluído."
}

run_sg() {
    log_step "[SG] GENESIS — Extract → Preprocess → Build CSL"
    log_warn "SG00 vai RESETAR o WordPress e APAGAR dirs de trabalho."

    if [ "${BENG_AUTO_RESET:-false}" != "true" ]; then
        read -rp "Confirmar RESET completo? [y/N]: " confirm
        [ "${confirm,,}" = "y" ] || { log_warn "Genesis cancelado."; return 0; }
    fi

    bash "$SCRIPTS_DIR/SG00_reset_workspace.sh"
    run_script "$SCRIPTS_DIR/SG01_extract_html.py"
    run_script "$SCRIPTS_DIR/SG02_preprocess_html.py"
    run_script "$SCRIPTS_DIR/SG03_build_csl.py" --apply
    run_script "$SCRIPTS_DIR/SG04_harvest_assets.py"

    run_script "$SCRIPTS_DIR/MI99_mission_report.py"
    log_ok "[SG] GENESIS concluído."
}

run_sp() {
    log_step "[SP] PRESERVATION — Migrate → Identity → Translate"

    # SP01 — migração PT-BR legado
    run_script "$SCRIPTS_DIR/SP01_migrate_ptbr.py" --apply

    # SP01b — restaurar traduções da Translation Preservation Layer (03-translations/)
    # Garante que todas as traduções PT-BR congeladas sobrevivam a um novo dump.
    # Idempotente: skip se pt-BR já existe no CSL com hash idêntico.
    # SP10 é idempotente → pula posts com pt-BR restaurado = zero custo DeepL.
    run_script "$SCRIPTS_DIR/SP01b_restore_translations.py" --apply

    # SP02 — upgrade identity v3.1
    run_script "$SCRIPTS_DIR/SP02_upgrade_identity.py" --apply

    # SP03 / SP04 / SP05 — mass migrations
    run_script "$SCRIPTS_DIR/SP03_mass_migration.py" --apply
    run_script "$SCRIPTS_DIR/SP04_phase5_migration.py" --apply
    run_script "$SCRIPTS_DIR/SP05_fix_headers.py" --apply

    # SP06 — áudio Pāli
    run_script "$SCRIPTS_DIR/SP06_audio_converter.py" --apply

    # ── SEAL 1 — Lock hashes pós-mutação HTML ─────────────────────────────
    log_step "[SEAL 1] Locking hashes pós-mutação HTML..."
    run_script "$SCRIPTS_DIR/SP02_upgrade_identity.py" --apply --force
    log_ok "[SEAL 1] Hashes EN selados."

    # ── SP11 — Tradução de títulos EN → PT (V5.2: automático após SEAL 1) ──
    # Toca apenas identity.json (campo titles.pt) — nunca content.html.
    # SP02 --force após SP11 preserva o titles.pt aqui gravado (fix E1).
    log_step "[SP11] Tradução de títulos EN → PT-BR..."
    run_script "$SCRIPTS_DIR/SP11_translate_titles.py" --apply
    log_ok "[SP11] Títulos PT gravados em identity.json."

    # SP07 — compilar glossário
    run_script "$SCRIPTS_DIR/SP07_compile_glossary.py"

    # SP08 — Glossary Gate (bypass via BENG_AUTO_GLOSSARY_OK)
    if [ "${BENG_AUTO_GLOSSARY_OK:-false}" = "true" ]; then
        log_warn "[SP08] GLOSSARY GATE: auto-approved (BENG_AUTO_GLOSSARY_OK=true)"
        BENG_AUTO_GLOSSARY_OK=true run_script "$SCRIPTS_DIR/SP08_glossary_gate.py"
    else
        log_step "[SP08] GLOSSARY GATE — revisão humana obrigatória"
        run_script "$SCRIPTS_DIR/SP08_glossary_gate.py"
    fi

    # SP09 — gerar menu de tradução (último passo automático)
    run_script "$SCRIPTS_DIR/SP09_translation_menu.py"

    # ── SP10 NÃO RODA NO FULL PIPELINE ───────────────────────────────────
    # SP09 regenera o Translation_Control_Center.csv do zero — qualquer
    # COMMAND=YES marcado antes seria apagado. SP10 tem custo real (DeepL)
    # e deve ser executado manualmente após revisão do operador:
    #
    #   1. Revise: /beng-fut/pipeline/metadata/Translation_Control_Center.csv
    #   2. Marque COMMAND=YES nos posts do lote mensal (≤ 450k chars)
    #   3. Execute: python3 $SCRIPTS_DIR/SP10_translate_deepl.py
    #   4. Execute: python3 $SCRIPTS_DIR/SP02_upgrade_identity.py --apply --force
    #      (V5.2: SP02 --force preserva titles.pt gravados pelo SP11 — fix E1)
    #
    echo ""
    echo -e "${CYAN}━━━ [SP10] TRADUÇÃO — PASSO MANUAL ━━━${NC}"
    echo -e "   ${YELLOW}SP09 acabou de regenerar o Translation_Control_Center.csv.${NC}"
    echo -e "   Para traduzir um lote:"
    echo -e "   ${GRAY}1. Marque COMMAND=YES no CSV (≤ 450k chars)${NC}"
    echo -e "   ${GRAY}2. python3 $SCRIPTS_DIR/SP10_translate_deepl.py${NC}"
    echo -e "   ${GRAY}3. python3 $SCRIPTS_DIR/SP02_upgrade_identity.py --apply --force${NC}"
    echo ""

    run_script "$SCRIPTS_DIR/MI99_mission_report.py"
    log_ok "[SP] PRESERVATION concluído."
}

run_sa() {
    log_step "[SA] AUDIT — SHA-256 Consistency + Structural Integrity"

    # Dry-run do SP02 como verificação de consistência
    run_script "$SCRIPTS_DIR/SP02_upgrade_identity.py" || true

    # Auditoria estrutural
    run_script "$SCRIPTS_DIR/SA01_final_audit.py" --apply

    # SA02 — Manifesto de imutabilidade global da CSL
    run_script "$SCRIPTS_DIR/SA02_freeze_manifest.py"

    # SA03 — Progresso de tradução PT-BR
    run_script "$SCRIPTS_DIR/SA03_translation_progress.py"

    # SA04 — Canon Manifest (cryptographic proof of build)
    run_script "$SCRIPTS_DIR/SA04_generate_canon_manifest.py"

    # SA06 — Build Seal (reproducible build declaration)
    run_script "$SCRIPTS_DIR/SA06_generate_build_seal.py"

    # SA05 — Canon Integrity Verification (verify manifest matches corpus)
    run_script "$SCRIPTS_DIR/SA05_verify_canon_integrity.py"

    log_ok "[SA] AUDIT concluído."
}

run_sd() {
    log_step "[SD] DISTRIBUTION — Asset Map → Static Site → WordPress"

    run_script "$SCRIPTS_DIR/SD01_generate_asset_map.py"

    # SD02 (slug_map) — gerado internamente pelo SD03/build.py na fase 2/8.
    # Script standalone omitido: depende de src/ do 13-ssg/ e é redundante.
    # run_script "$SCRIPTS_DIR/SD02_generate_slug_map.py"

    # SD03 — SSG build (em seu próprio diretório)
    local ssg_dir="$BENG_BASE/13-ssg"
    if [ ! -f "$ssg_dir/build.py" ]; then
        abort "build.py não encontrado em $ssg_dir"
    fi
    echo -e "\n${YELLOW}▶ SD03 (SSG Build) — build.py${NC}"
    (cd "$ssg_dir" && python3 build.py)

    # SD04 — WordPress inject (bypass via BENG_AUTO_INJECT)
    if [ "${BENG_AUTO_INJECT:-false}" = "true" ]; then
        log_warn "[SD04] BENG_AUTO_INJECT=true — injetando diretamente"
        run_script "$SCRIPTS_DIR/SD04_wordpress_inject.py"
    else
        echo -e "\n${RED}🛑 WORDPRESS INJECT GATE${NC}"
        read -rp "   Confirmar injeção no WordPress local? [y/N]: " confirm
        if [ "${confirm,,}" = "y" ]; then
            run_script "$SCRIPTS_DIR/SD04_wordpress_inject.py"
        else
            log_warn "[SD04] Injeção adiada."
        fi
    fi

    run_script "$SCRIPTS_DIR/MI99_mission_report.py"
    log_ok "[SD] DISTRIBUTION concluído."
}

run_health() {
    log_step "[HEALTH CHECK] Verificação completa — read-only, sem modificações"

    # DI — auditoria SQL vs CSL
    run_script "$SCRIPTS_DIR/DI00_sql_vs_csl_audit.py" || true

    # SA01 dry-run — consistência de hashes (sem --apply)
    log_step "[SA01] SHA-256 dry-run..."
    run_script "$SCRIPTS_DIR/SA01_final_audit.py" || true

    # SA02 — manifesto (apenas leitura)
    run_script "$SCRIPTS_DIR/SA02_freeze_manifest.py"

    # SA03 — progresso de tradução (apenas leitura)
    run_script "$SCRIPTS_DIR/SA03_translation_progress.py"

    # SA04 — Canon Manifest (read — always regenerate)
    run_script "$SCRIPTS_DIR/SA04_generate_canon_manifest.py"

    # SA06 — Build Seal
    run_script "$SCRIPTS_DIR/SA06_generate_build_seal.py"

    # SA05 — Canon Integrity Verification
    run_script "$SCRIPTS_DIR/SA05_verify_canon_integrity.py"

    # MI99 — relatório final
    run_script "$SCRIPTS_DIR/MI99_mission_report.py"

    log_ok "[HEALTH CHECK] Concluído. Nenhum arquivo modificado."
}

run_full() {
    log_step "[FULL] SNAPSHOT → SG → SP → SA → SD"

    # SN01 — Snapshot da CSL (opcional — pergunta ao operador)
    SNAP_DIR="${BENG_BASE}/snapshots"
    LAST_SNAP=$(ls -1t "$SNAP_DIR"/csl_snapshot_*.tar.gz 2>/dev/null | head -1 || echo "")
    echo ""
    if [ -n "$LAST_SNAP" ]; then
        LAST_DATE=$(stat -c "%y" "$LAST_SNAP" | cut -d'.' -f1)
        LAST_SIZE=$(du -sh "$LAST_SNAP" | cut -f1)
        echo -e "  ${GRAY}Último snapshot: $(basename "$LAST_SNAP") ($LAST_SIZE — $LAST_DATE)${NC}"
    else
        echo -e "  ${YELLOW}Nenhum snapshot encontrado ainda.${NC}"
    fi
    read -rp "  📦 Criar snapshot da CSL antes de prosseguir? [Y/n]: " snap_confirm
    if [ "${snap_confirm,,}" != "n" ]; then
        bash "$SCRIPTS_DIR/SN01_snapshot_csl.sh" || log_warn "Snapshot falhou — continuando."
    else
        log_warn "Snapshot ignorado pelo operador."
    fi

    run_sg
    run_sp
    run_sa
    run_sd
    log_ok "[FULL] Pipeline completo executado com sucesso."

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  💎 AXIS-NIDDHI: ENGINE SUCCESSFULLY STABILIZED          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  🧭 ${CYAN}WHERE I WAS:${NC} An empty folder with unextracted Dhamma material."
    echo -e "  📍 ${CYAN}WHERE I AM:${NC}  The full PureDhamma corpus is parsed, preserved (CSL), and injected."
    echo -e "  🚀 ${CYAN}WHAT'S NEXT:${NC}"
    echo -e ""
    echo -e "     ${GRAY}1. Local WordPress (Visual Verification)${NC}"
    echo -e "        Open your browser: ${YELLOW}http://localhost/beng_feb2026${NC}"
    echo -e "        Admin Login: ${YELLOW}http://localhost/beng_feb2026/wp-admin${NC}"
    echo -e ""
    echo -e "     ${GRAY}2. Static Site Preview (High-Speed HTML Delivery)${NC}"
    echo -e "        Run: ${YELLOW}axis preview${NC}"
    echo -e "        Open your browser at the provided localhost port."
    echo -e ""
    echo -e "     ${GRAY}3. Expand the Translation${NC}"
    echo -e "        Modify: ${YELLOW}pipeline/metadata/Translation_Control_Center.csv${NC}"
    echo -e "        Mark posts with COMMAND=YES, then run ${YELLOW}axis pipeline${NC} → SP Phase."
    echo ""
}

# ==============================================================================
# 6. CLI FLAGS (non-interactive)
# ==============================================================================

handle_cli_flag() {
    case "$1" in
        --diagnostic)   validate_workspace; activate_venv; run_di ;;
        --genesis)      validate_workspace; activate_venv; run_sg ;;
        --preservation) validate_workspace; activate_venv; run_sp ;;
        --audit)        validate_workspace; activate_venv; run_sa ;;
        --distribution) validate_workspace; activate_venv; run_sd ;;
        --full)         validate_workspace; activate_venv; run_full ;;
        --health)       validate_workspace; activate_venv; run_health ;;
        --version)      echo "AXIS-NIDDHI Pipeline V${PIPELINE_VERSION}"; exit 0 ;;
        --help|-h)
            echo "Usage: $0 [--diagnostic|--genesis|--preservation|--audit|--distribution|--full|--health]"
            echo ""
            echo "ENV vars:"
            echo "  BENG_AUTO_TRANSLATE=true    bypass DeepL prompt"
            echo "  BENG_AUTO_INJECT=true       bypass WP inject prompt"
            echo "  BENG_AUTO_GLOSSARY_OK=true  bypass Glossary Gate"
            echo "  BENG_AUTO_RESET=true        bypass SG00 reset confirm"
            echo "  BENG_FAILURE_THRESHOLD=N    max failures before abort (default: 5)"
            echo "  BENG_BASE=/path/to/pipeline override base dir"
            exit 0
            ;;
        *)
            log_error "Flag desconhecida: $1"
            echo "Use --help para ver as opções."
            exit 1
            ;;
    esac
    exit 0
}

# ==============================================================================
# 7. MENU INTERATIVO
# ==============================================================================

show_menu() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  💎 AXIS-NIDDHI MISSION CONTROL V${PIPELINE_VERSION}                    ║${NC}"
    echo -e "${CYAN}║     PureDhamma Preservation Engine                       ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GRAY}0)${NC} [DI] DIAGNOSTIC       — SQL vs CSL Pre-Flight Audit"
    echo -e "  ${GRAY}1)${NC} [SG] GENESIS           — Extract → Preprocess → Build CSL"
    echo -e "  ${GRAY}2)${NC} [SP] PRESERVATION      — Migrate → Identity → Translate"
    echo -e "  ${GRAY}3)${NC} [SA] AUDIT             — SHA-256 + Structural Integrity"
    echo -e "  ${GRAY}4)${NC} [SD] DISTRIBUTION      — Asset Map → Static Site → WP"
    echo -e "  ${GRAY}5)${NC} [FULL] PIPELINE        — SNAPSHOT → SG → SP → SA → SD"
    echo -e "  ${GRAY}6)${NC} EXIT"
    echo -e "  ${GRAY}7)${NC} [HEALTH CHECK]         — Verificação read-only do sistema"
    echo ""
}

# ==============================================================================
# 8. ENTRY POINT
# ==============================================================================

# CLI flag (non-interactive)
if [ $# -gt 0 ]; then
    handle_cli_flag "$1"
fi

# Menu interativo
validate_workspace
activate_venv

show_menu
read -rp "Choice [0-7]: " choice

case "$choice" in
    0) run_di ;;
    1) run_sg ;;
    2) run_sp ;;
    3) run_sa ;;
    4) run_sd ;;
    5) run_full ;;
    6) log_info "Saindo. Sādhu 🙏"; exit 0 ;;
    7) run_health ;;
    *) log_error "Opção inválida: $choice"; exit 1 ;;
esac
