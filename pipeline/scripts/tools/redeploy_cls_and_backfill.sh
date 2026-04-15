#!/usr/bin/env bash
# /beng-fut/pipeline/scripts/redeploy_cls_and_backfill.sh
# ==============================================================================
# AXIS-NIDDHI V5.2.3 — Redeploy cls_tools + rebackfill CLS V1.1
# ==============================================================================
# Roda quando o cls_tools.py no servidor está desatualizado
# (ex: após reset de workspace ou deploy incompleto)
#
# USO:
#   bash /beng-fut/pipeline/scripts/redeploy_cls_and_backfill.sh
# ==============================================================================

set -euo pipefail

SCRIPTS="/beng-fut/pipeline/scripts"
CSL="/beng-fut/pipeline/09-csl"
GREEN='\033[0;32m'; CYAN='\033[0;96m'; RED='\033[0;31m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
info() { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }
err()  { echo -e "${RED}❌ $*${NC}"; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  AXIS-NIDDHI — Redeploy CLS + Backfill              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==============================================================================
# PASSO 1 — Verificar que os arquivos novos estão presentes
# ==============================================================================
info "PASSO 1 — Verificar arquivos a deployar"

# Esses arquivos devem ter sido copiados manualmente antes de rodar este script
for f in cls_tools.py SG01_extract_html.py SP10_translate_deepl.py SP11_translate_titles.py; do
    path="$SCRIPTS/$f"
    if [ ! -f "$path" ]; then
        err "$f não encontrado em $SCRIPTS"
        err "Copie os arquivos V5.2.3 para $SCRIPTS antes de rodar este script."
        exit 1
    fi
    # Verificar que é a versão nova (tem 'audit' e 'backfill')
    if [[ "$f" == "cls_tools.py" ]]; then
        if grep -q "def backfill_lineage\|cmd == .audit." "$path" 2>/dev/null; then
            ok "$f — versão V5.2.3 confirmada"
        else
            err "$f está desatualizado — substitua pelo arquivo V5.2.3 dos outputs"
            exit 1
        fi
    else
        python3 -m py_compile "$path" && ok "$f — syntax OK"
    fi
done

# ==============================================================================
# PASSO 2 — Rodar backfill CLS V1.1 em todos os 748 posts
# ==============================================================================
info "PASSO 2 — Backfill CLS V1.1 (748 entries)"

python3 "$SCRIPTS/cls_tools.py" backfill "$CSL" --apply --quiet
echo ""

# ==============================================================================
# PASSO 3 — Audit para confirmar
# ==============================================================================
info "PASSO 3 — Audit pós-backfill"

python3 "$SCRIPTS/cls_tools.py" audit "$CSL"

# ==============================================================================
# PASSO 4 — Verificar posts traduzidos (49 esperados)
# ==============================================================================
info "PASSO 4 — Verificar posts PT-BR"

python3 - <<'PY'
import json, re
from pathlib import Path

CSL = Path("/beng-fut/pipeline/09-csl")
PDPN_RE = re.compile(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$')

translated = titles = 0
for folder in CSL.iterdir():
    if not folder.is_dir() or not PDPN_RE.match(folder.name):
        continue
    pt_html = folder / "source" / "pt-BR" / "content.html"
    if pt_html.exists() and pt_html.stat().st_size > 100:
        translated += 1
        ip = folder / "meta" / "identity.json"
        try:
            data = json.loads(ip.read_text(encoding="utf-8"))
            if data.get("titles", {}).get("pt"):
                titles += 1
        except Exception:
            pass

print(f"  Posts com conteúdo PT-BR : {translated}")
print(f"  Posts com título PT-BR   : {titles}")
if translated == 49 and titles == 49:
    print("  ✅ 49/49 completos — SP12 pronto para carregar")
else:
    print(f"  ⚠️  Esperado 49/49 — verificar SP11")
PY

echo ""
ok "Redeploy concluído. Reinicie o SP12 com: axis sp12"
