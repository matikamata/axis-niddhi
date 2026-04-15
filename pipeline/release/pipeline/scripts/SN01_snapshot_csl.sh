#!/usr/bin/env bash
# ==============================================================================
# 💎 BRASILEIRINHO ENGINE — SN01 Snapshot CSL
# Versão: 1.0 (AXIS-NIDDHI V5.1)
# Objetivo: criar snapshot comprimido da CSL antes de operações destrutivas.
#           Não modifica nada — apenas preserva o estado atual.
# ==============================================================================
set -euo pipefail

PIPELINE_ROOT="${BENG_BASE:-/beng-fut/pipeline}"
CSL_DIR="$PIPELINE_ROOT/09-csl"
SNAP_DIR="/beng-fut/snapshots"

# Cores
GREEN="\033[92m"
CYAN="\033[96m"
YELLOW="\033[93m"
RED="\033[91m"
GRAY="\033[90m"
NC="\033[0m"

if [ ! -d "$CSL_DIR" ]; then
    echo -e "${YELLOW}⚠️  CSL não encontrada em $CSL_DIR — snapshot ignorado.${NC}"
    exit 0
fi

mkdir -p "$SNAP_DIR"

STAMP=$(date +"%Y%m%d_%H%M%S")
FILE="$SNAP_DIR/csl_snapshot_$STAMP.tar.gz"

# Contar posts antes de comprimir
POST_COUNT=$(find "$CSL_DIR" -mindepth 1 -maxdepth 1 -type d \
    | grep -cE '/[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}$' || echo "?")

echo -e "${CYAN}📦 Criando snapshot da CSL...${NC}"
echo -e "   ${GRAY}Posts: $POST_COUNT | Destino: $FILE${NC}"

tar -czf "$FILE" -C "$PIPELINE_ROOT" 09-csl

SIZE=$(du -sh "$FILE" | cut -f1)
echo -e "${GREEN}✅ Snapshot salvo: $FILE ($SIZE)${NC}"

# Manter apenas os 5 snapshots mais recentes (limpeza automática)
SNAP_COUNT=$(ls -1 "$SNAP_DIR"/csl_snapshot_*.tar.gz 2>/dev/null | wc -l)
if [ "$SNAP_COUNT" -gt 5 ]; then
    EXCESS=$(( SNAP_COUNT - 5 ))
    ls -1t "$SNAP_DIR"/csl_snapshot_*.tar.gz | tail -n "$EXCESS" | while read -r old; do
        rm -f "$old"
        echo -e "   ${GRAY}🗑️  Snapshot antigo removido: $(basename "$old")${NC}"
    done
fi
