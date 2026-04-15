#!/usr/bin/env bash
# ==============================================================================
# axis_cli.sh — AXIS-NIDDHI CLI dispatcher  (V5.5)
# Caminho canônico: /beng-fut/pipeline/scripts/axis_cli.sh
#
# INSTALAÇÃO (uma vez):
#   echo "alias axis='bash /beng-fut/pipeline/scripts/axis_cli.sh'" >> ~/.bashrc
#   source ~/.bashrc
#
# USO:
#   axis build-site     → gera site estático completo
#   axis preview        → servidor local porta 8080
#   axis status         → contagem CSL / páginas / traduções
# ==============================================================================

PIPELINE="/beng-fut/pipeline"
ENGINE="$PIPELINE/13-ssg"
OUTPUT="$PIPELINE/13-static-site"
CMD="${1:-help}"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

case "$CMD" in
    build-site)
        echo -e "${BOLD}▶ axis build-site${NC}"
        cd "$ENGINE"
        python3 build.py
        PAGES=$(find "$OUTPUT/pages" -name "index.html" 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ Build completo → $OUTPUT ($PAGES páginas)${NC}"
        ;;
    preview)
        PORT="${2:-8080}"
        echo -e "${CYAN}▶ axis preview — http://localhost:$PORT${NC}"
        echo "   Ctrl+C para encerrar"
        cd "$OUTPUT"
        python3 -m http.server "$PORT"
        ;;
    status)
        echo -e "${BOLD}── AXIS-NIDDHI Pipeline Status ──${NC}"
        CSL=$(find "$PIPELINE/09-csl" -name "csl.json" 2>/dev/null | wc -l)
        PAGES=$(find "$OUTPUT/pages" -name "index.html" 2>/dev/null | wc -l)
        TRANSLATED=$(python3 -c "
import json, pathlib
csl_dir = pathlib.Path('$PIPELINE/09-csl')
done = sum(
    1 for f in csl_dir.glob('*/csl.json')
    if any(t.get('lang') == 'pt'
           for t in (json.loads(f.read_text()).get('lineage', {})
                                              .get('translations', [])))
)
print(done)
" 2>/dev/null || echo "?")
        printf "  %-22s %s\n" "CSL entries:"   "$CSL"
        printf "  %-22s %s\n" "Páginas built:" "$PAGES"
        printf "  %-22s %s\n" "Traduzidos PT:" "$TRANSLATED"
        ;;
    pipeline|full)
        echo -e "${BOLD}▶ axis pipeline — Full Pipeline SG→SP→SA→SD${NC}"
        SCRIPTS="/beng-fut/pipeline/scripts"
        if [[ $EUID -ne 0 ]]; then
            echo -e "\033[1;33m⚡ Relançando com sudo...\033[0m"
            exec sudo bash "$SCRIPTS/run_full_pipeline.sh" --full
        else
            exec bash "$SCRIPTS/run_full_pipeline.sh" --full
        fi
        ;;

    sd|distribution)
        echo -e "${BOLD}▶ axis sd — Distribuição (SD) apenas${NC}"
        SCRIPTS="/beng-fut/pipeline/scripts"
        if [[ $EUID -ne 0 ]]; then
            echo -e "\033[1;33m⚡ Relançando com sudo...\033[0m"
            exec sudo bash "$SCRIPTS/run_full_pipeline.sh" --distribution
        else
            exec bash "$SCRIPTS/run_full_pipeline.sh" --distribution
        fi
        ;;

    menu|run)
        SCRIPTS="/beng-fut/pipeline/scripts"
        if [[ $EUID -ne 0 ]]; then
            echo -e "\033[1;33m⚡ Relançando com sudo...\033[0m"
            exec sudo bash "$SCRIPTS/run_full_pipeline.sh"
        else
            exec bash "$SCRIPTS/run_full_pipeline.sh"
        fi
        ;;

    translate)
        SCRIPTS="/beng-fut/pipeline/scripts"
        echo -e "${BOLD}── axis translate — Ciclo Mensal DeepL ──${NC}"
        echo -e "${CYAN}Passo 1/4: Gerando menu...${NC}"
        python3 "$SCRIPTS/SP09_translation_menu.py"
        echo ""
        echo -e "\033[1;33mPasso 2/4: Marque COMMAND=YES no CSV (≤ 450k chars):${NC}"
        echo "   /beng-fut/pipeline/metadata/Translation_Control_Center.csv"
        read -rp "   Pressione ENTER quando pronto... " _
        echo -e "${CYAN}Passo 3/4: Traduzindo...${NC}"
        python3 "$SCRIPTS/SP10_translate_deepl.py"
        echo -e "${CYAN}Passo 4/4: SEAL 2...${NC}"
        python3 "$SCRIPTS/SP02_upgrade_identity.py" --apply --force
        python3 "$SCRIPTS/SA01_final_audit.py" --apply
        echo -e "${GREEN}✅ Ciclo concluído. Rode: axis sd${NC}"
        ;;

    help|*)
        echo -e "${BOLD}axis${NC} — AXIS-NIDDHI CLI (V5.5)"
        echo ""
        echo "Comandos:"
        echo "  axis menu         Menu completo do pipeline (interativo)"
        echo "  axis pipeline     Full pipeline SG→SP→SA→SD"
        echo "  axis sd           Só distribuição (rápido, pós-tradução)"
        echo "  axis translate    Ciclo de tradução mensal guiado"
        echo "  axis build-site   Gera o site estático"
        echo "  axis preview      Servidor local porta 8080"
        echo "  axis status       Status do pipeline"
        ;;
esac
