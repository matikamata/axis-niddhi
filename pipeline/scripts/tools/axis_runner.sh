#!/usr/bin/env bash
# AXIS-NIDDHI runner — ponto de entrada unificado V5.5
# USO: axis sp12 | axis audit | axis status | axis pipeline | axis sd | axis translate | axis preview

SCRIPTS="/beng-fut/pipeline/scripts"
OUTPUT="/beng-fut/pipeline/13-static-site"
CMD="${1:-help}"

YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

_require_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}⚡ Relançando com sudo...${NC}"
        exec sudo bash "$SCRIPTS/axis_runner.sh" "$@"
    fi
}

case "$CMD" in
    sp12)
        echo "🚀 Iniciando SP12 Guardian Review Tool..."
        streamlit run "$SCRIPTS/sp12_guardian/sp12_app.py" \
            --server.port 8512 \
            --server.headless false \
            --browser.gatherUsageStats false
        ;;
    audit)
        python3 "$SCRIPTS/cls_tools.py" audit /beng-fut/pipeline/09-csl
        ;;
    status)
        echo -e "${BOLD}── AXIS-NIDDHI Status ──${NC}"
        CSL=$(find /beng-fut/pipeline/09-csl -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
        PAGES=$(find "$OUTPUT/pages" -name "index.html" 2>/dev/null | wc -l)
        PT=$(find /beng-fut/pipeline/09-csl -path "*/source/pt-BR/content.html" 2>/dev/null | wc -l)
        printf "  %-22s %s\n" "CSL entries:"   "$CSL"
        printf "  %-22s %s\n" "Páginas built:" "$PAGES"
        printf "  %-22s %s / %s\n" "Traduzidos PT:" "$PT" "$CSL"
        MANIFEST=/beng-fut/pipeline/09-csl/manifest.json
        if [[ -f "$MANIFEST" ]]; then
            BUILD=$(python3 -c "import json; m=json.load(open('$MANIFEST')); print(m.get('generated_at','?')[:10])" 2>/dev/null)
            printf "  %-22s %s\n" "Último manifest:" "$BUILD"
        fi
        ;;
    menu|run)
        _require_root "$@"
        exec bash "$SCRIPTS/run_full_pipeline.sh"
        ;;
    pipeline|full)
        _require_root "$@"
        exec bash "$SCRIPTS/run_full_pipeline.sh" --full
        ;;
    sd|distribution)
        _require_root "$@"
        exec bash "$SCRIPTS/run_full_pipeline.sh" --distribution
        ;;
    sg|genesis)
        _require_root "$@"
        exec bash "$SCRIPTS/run_full_pipeline.sh" --genesis
        ;;
    translate)
        echo -e "${BOLD}── axis translate — Ciclo Mensal DeepL ──${NC}"
        echo -e "${CYAN}Passo 1/4: Gerando menu de tradução...${NC}"
        python3 "$SCRIPTS/SP09_translation_menu.py"
        echo ""
        echo -e "${YELLOW}Passo 2/4: Marque COMMAND=YES no CSV (≤ 450k chars):${NC}"
        echo "   /beng-fut/pipeline/metadata/Translation_Control_Center.csv"
        read -rp "   Pressione ENTER quando pronto... " _
        echo -e "${CYAN}Passo 3/4: Traduzindo com DeepL...${NC}"
        python3 "$SCRIPTS/SP10_translate_deepl.py"
        echo -e "${CYAN}Passo 4/4: SEAL 2 — selando hashes...${NC}"
        python3 "$SCRIPTS/SP02_upgrade_identity.py" --apply --force
        python3 "$SCRIPTS/SA01_final_audit.py" --apply
        echo ""
        echo -e "${GREEN}✅ Ciclo concluído. Rode: axis sd${NC}"
        ;;
    preview)
        PORT="${2:-8080}"
        echo -e "${CYAN}▶ http://localhost:$PORT  (Ctrl+C para encerrar)${NC}"
        cd "$OUTPUT" && python3 -m http.server "$PORT"
        ;;
    help|*)
        echo ""
        echo -e "  ${BOLD}AXIS-NIDDHI V5.5 — Mission Control${NC}"
        echo "  ==================================="
        echo "  axis menu         → Menu interativo do pipeline"
        echo "  axis pipeline     → Full pipeline SG→SP→SA→SD"
        echo "  axis sd           → Só distribuição (rápido, pós-tradução)"
        echo "  axis translate    → Ciclo de tradução mensal guiado"
        echo "  axis preview      → Servidor local :8080"
        echo "  axis status       → Status CSL / páginas / traduções"
        echo "  axis sp12         → Guardian Review Tool (Streamlit)"
        echo "  axis audit        → Auditar CLS em todo o CSL"
        echo ""
        ;;
esac
