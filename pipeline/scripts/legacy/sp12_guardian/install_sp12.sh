#!/usr/bin/env bash
# /beng-fut/pipeline/scripts/sp12_guardian/install_sp12.sh
# ==============================================================================
# AXIS-NIDDHI V5.3 — Instalação do SP12 Guardian Review Tool
# ==============================================================================
# USO:
#   bash /beng-fut/pipeline/scripts/sp12_guardian/install_sp12.sh
#
# Após instalar:
#   axis sp12
# ==============================================================================

set -euo pipefail

SCRIPTS="/beng-fut/pipeline/scripts"
SP12_DIR="$SCRIPTS/sp12_guardian"
GREEN='\033[0;32m'; CYAN='\033[0;96m'; NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  AXIS-NIDDHI V5.3 — SP12 Install                    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 1. Dependências Python
echo "📦 Verificando dependências..."
pip install streamlit --break-system-packages -q && echo -e "${GREEN}✅ streamlit OK${NC}"

# 2. Criar diretório SP12 se necessário
mkdir -p "$SP12_DIR"
echo -e "${GREEN}✅ Diretório: $SP12_DIR${NC}"

# 3. Copiar arquivos (se rodando de outro dir)
# Os arquivos já devem estar em $SP12_DIR após deploy manual

# 4. Criar alias 'axis' no .bashrc se não existir
ALIAS_LINE="alias axis='bash /beng-fut/pipeline/scripts/axis_runner.sh'"
if ! grep -q "alias axis=" ~/.bashrc 2>/dev/null; then
    echo "$ALIAS_LINE" >> ~/.bashrc
    echo -e "${GREEN}✅ Alias 'axis' adicionado ao .bashrc${NC}"
else
    echo -e "${GREEN}✅ Alias 'axis' já existe${NC}"
fi

# 5. Criar axis_runner.sh
cat > "$SCRIPTS/axis_runner.sh" << 'RUNNER'
#!/usr/bin/env bash
# AXIS-NIDDHI runner — ponto de entrada unificado
# USO: axis sp12 | axis audit | axis status

CMD="${1:-help}"

case "$CMD" in
    sp12)
        echo "🚀 Iniciando SP12 Guardian Review Tool..."
        streamlit run /beng-fut/pipeline/scripts/sp12_guardian/sp12_app.py \
            --server.port 8512 \
            --server.headless false \
            --browser.gatherUsageStats false
        ;;
    audit)
        python3 /beng-fut/pipeline/scripts/cls_tools.py audit /beng-fut/pipeline/09-csl
        ;;
    status)
        python3 /beng-fut/pipeline/scripts/cls_tools.py audit /beng-fut/pipeline/09-csl
        ;;
    help|*)
        echo ""
        echo "  AXIS-NIDDHI V5.3 — Runner"
        echo "  ========================="
        echo "  axis sp12     → Abrir Guardian Review Tool (Streamlit)"
        echo "  axis audit    → Auditar CLS em todo o CSL"
        echo "  axis status   → Status rápido do pipeline"
        echo ""
        ;;
esac
RUNNER
chmod +x "$SCRIPTS/axis_runner.sh"
echo -e "${GREEN}✅ axis_runner.sh criado${NC}"

echo ""
echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo ""
echo -e "${CYAN}Para usar:${NC}"
echo "  source ~/.bashrc"
echo "  axis sp12"
echo ""
echo -e "${CYAN}Ou diretamente:${NC}"
echo "  streamlit run $SP12_DIR/sp12_app.py --server.port 8512"
echo ""
