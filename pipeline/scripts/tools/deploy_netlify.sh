#!/bin/bash
set -euo pipefail

_SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
PIPELINE_DIR="$(cd "$_SELF_DIR/../.." && pwd)"

GREEN='\033[0;32m'
CYAN='\033[0;96m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🚀 AXIS-NIDDHI — Manual Netlify Cloud Deploy        ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}\n"

echo -e "   📌 ${YELLOW}Modo Manual Ativado!${NC}"
echo -e "   Este processo garante: "
echo -e "      1. Que os ${GREEN}1.2GB de áudios locais${NC} sejam enviados."
echo -e "      2. Que você gaste ${GREEN}ZERO minutos de Build${NC} na nuvem Netlify!\n"

STATIC_TARGET="$PIPELINE_DIR/13-static-site"

if [ ! -d "$STATIC_TARGET" ]; then
    echo -e "❌ ERRO: A pasta 13-static-site não foi encontrada em $STATIC_TARGET"
    echo -e "   Aborte e construa o site localmente primeiro.\n"
    exit 1
fi

echo -e "Conectando ao Netlify via CLI..."
npx netlify-cli deploy --prod --dir="$STATIC_TARGET" || echo "Deploy falhou ou foi abortado pelo usuário."

echo -e "\n${GREEN}» Missão Concluída! ${NC}"
