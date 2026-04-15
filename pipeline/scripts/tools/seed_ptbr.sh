#!/bin/bash
# seed_ptbr.sh — Alimenta 03-ptbr/ com as traduções PT-BR do backup
# Roda UMA VEZ após um reset de workspace onde 03-ptbr/ está vazia.
# Depois disso, SP01 usa 03-ptbr/ como fonte canônica local.
#
# Uso:
#   bash scripts/seed_ptbr.sh --src /media/sanghop/GUARDIAN_SD/Backup_CAGAÇO_20260310_16h19/pipeline/09-csl
#   bash scripts/seed_ptbr.sh --src /media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline/09-csl
#
# O que faz:
#   Para cada PDPN em SRC que tem source/pt-BR/content.html
#   → copia para 03-ptbr/PDPN/source/pt-BR/content.html
#   Idempotente: não sobrescreve se já existe.

set -euo pipefail

GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
CYAN="\033[96m"
GRAY="\033[90m"
RESET="\033[0m"

PIPELINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DST="$PIPELINE_DIR/03-ptbr"
SRC=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --src) SRC="$2"; shift 2 ;;
        *) echo -e "${RED}❌ Argumento desconhecido: $1${RESET}"; exit 1 ;;
    esac
done

if [[ -z "$SRC" ]]; then
    echo -e "${RED}❌ --src obrigatório.${RESET}"
    echo -e "   Uso: bash scripts/seed_ptbr.sh --src /caminho/para/09-csl"
    exit 1
fi

if [[ ! -d "$SRC" ]]; then
    echo -e "${RED}❌ SRC não encontrada: $SRC${RESET}"
    exit 1
fi

echo -e "\n${CYAN}══════════════════════════════════════════════════════${RESET}"
echo -e "${CYAN}  🌱 SEED PT-BR  —  03-ptbr/ canônica${RESET}"
echo -e "${CYAN}  SRC: $SRC${RESET}"
echo -e "${CYAN}  DST: $DST${RESET}"
echo -e "${CYAN}══════════════════════════════════════════════════════${RESET}\n"

mkdir -p "$DST"

copied=0
skipped=0
no_ptbr=0
errors=0

for pdpn_dir in "$SRC"/*/; do
    pdpn=$(basename "$pdpn_dir")
    [[ "$pdpn" == "meta" ]] && continue  # pasta global de metadados

    src_pt="$pdpn_dir/source/pt-BR/content.html"
    dst_pt="$DST/$pdpn/source/pt-BR/content.html"

    if [[ ! -f "$src_pt" ]]; then
        ((no_ptbr++)) || true
        continue
    fi

    if [[ -f "$dst_pt" ]]; then
        ((skipped++)) || true
        continue
    fi

    mkdir -p "$(dirname "$dst_pt")"
    if cp "$src_pt" "$dst_pt" 2>/dev/null; then
        echo -e "${GREEN}  ✅ $pdpn${RESET}"
        ((copied++)) || true
    else
        echo -e "${RED}  ❌ $pdpn — falha na cópia${RESET}"
        ((errors++)) || true
    fi
done

echo -e "\n${CYAN}══════════════════════════════════════════════════════${RESET}"
echo -e "${CYAN}  📊 SEED CONCLUÍDO${RESET}"
echo -e "${CYAN}══════════════════════════════════════════════════════${RESET}"
echo -e "  ${GREEN}Copiados        : $copied${RESET}"
echo -e "  ${GRAY}Já existiam     : $skipped${RESET}"
echo -e "  ${GRAY}Sem pt-BR       : $no_ptbr${RESET}"
echo -e "  ${RED}Erros           : $errors${RESET}"
echo -e "${CYAN}══════════════════════════════════════════════════════${RESET}"

if [[ $copied -gt 0 ]]; then
    echo -e "\n  ${GREEN}✅ 03-ptbr/ populada. SP01 usará esta pasta como fonte.${RESET}"
    echo -e "  Próximo: bash scripts/run_full_pipeline.sh\n"
elif [[ $skipped -gt 0 && $copied -eq 0 ]]; then
    echo -e "\n  ${YELLOW}⚠️  Tudo já existia — 03-ptbr/ já estava populada.${RESET}\n"
fi

if [[ $errors -gt 0 ]]; then
    exit 1
fi
exit 0
