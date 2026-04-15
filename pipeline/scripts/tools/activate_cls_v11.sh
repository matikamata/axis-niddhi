# /beng-fut/pipeline/scripts/activate_cls_v11.sh
#!/usr/bin/env bash
# ==============================================================================
# AXIS-NIDDHI V5.2.1 — Ativação CLS V1.1
# ==============================================================================
# Roda os 4 passos de validação e backfill no CSL existente.
# Não cria pastas, não move nada, não altera estrutura.
#
# USO:
#   bash /beng-fut/pipeline/scripts/activate_cls_v11.sh
# ==============================================================================

set -euo pipefail

SCRIPTS="/beng-fut/pipeline/scripts"
CONFIG="/beng-fut/pipeline/config"
CSL="/beng-fut/pipeline/09-csl"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;96m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
info() { echo -e "${CYAN}━━━ $* ━━━${NC}"; }
err()  { echo -e "${RED}❌ $*${NC}"; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  AXIS-NIDDHI V5.2.1 — Ativação CLS V1.1             ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==============================================================================
# PASSO 1 — Confirmar que os arquivos existem
# ==============================================================================
info "PASSO 1 — Verificar arquivos CLS"

CLS_TOOLS="$SCRIPTS/cls_tools.py"
SCHEMA="$CONFIG/lineage_schema.json"

[ -f "$CLS_TOOLS" ] && ok "cls_tools.py existe: $CLS_TOOLS" \
                     || { err "cls_tools.py NÃO encontrado em $CLS_TOOLS"; exit 1; }

[ -f "$SCHEMA" ]    && ok "lineage_schema.json existe: $SCHEMA" \
                     || { err "lineage_schema.json NÃO encontrado em $SCHEMA"; exit 1; }

[ -d "$CSL" ]       && ok "CSL existe: $CSL ($(find "$CSL" -maxdepth 1 -mindepth 1 -type d | wc -l) entries)" \
                     || { err "CSL NÃO encontrado em $CSL"; exit 1; }

# ==============================================================================
# PASSO 2 — Validar que o schema carrega corretamente
# ==============================================================================
info "PASSO 2 — Validar schema JSON"

python3 - <<PY
import json
from pathlib import Path

schema = Path("$SCHEMA")
print("Schema exists:", schema.exists())
if schema.exists():
    data = json.loads(schema.read_text())
    print("Schema keys:", list(data.keys()))
    print("CLS version:", data.get("cls_version", "??"))
    print("Sprint:", data.get("sprint", "??"))
    # Verificar blocos esperados no lineage_block
    lb = data.get("lineage_block", {}).get("properties", {})
    print("Lineage blocks:", list(lb.keys()))
PY

# ==============================================================================
# PASSO 3 — Rodar backfill CLS no CSL existente
# ==============================================================================
info "PASSO 3 — Backfill CLS V1.1"

python3 "$CLS_TOOLS" backfill "$CSL" --apply

# ==============================================================================
# PASSO 4 — Estatísticas finais
# ==============================================================================
info "PASSO 4 — Estatísticas finais"

python3 - <<PY
import json, re
from pathlib import Path

CSL = Path("$CSL")
PDPN_RE = re.compile(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$')

total = injected = upgraded = already = no_identity = errors = 0

for folder in sorted(CSL.iterdir()):
    if not folder.is_dir() or not PDPN_RE.match(folder.name):
        continue
    total += 1
    ip = folder / "meta" / "identity.json"
    if not ip.exists():
        no_identity += 1
        continue
    try:
        data = json.loads(ip.read_text(encoding="utf-8"))
        lin = data.get("lineage")
        if lin is None:
            errors += 1
        elif lin.get("cls_version") == "1.1":
            already += 1
        elif lin.get("cls_version") == "1.0":
            upgraded += 1
        else:
            errors += 1
    except Exception as e:
        errors += 1

print()
print("━" * 48)
print(f"  Total entries CSL       : {total}")
print(f"  Com lineage V1.1        : {already}")
print(f"  Upgraded V1.0 → V1.1    : {upgraded}")
print(f"  Sem identity.json       : {no_identity}")
print(f"  Falhas / sem lineage    : {errors}")
print("━" * 48)

if errors == 0 and no_identity == 0:
    print("  ✅ CLS V1.1 ativo em todas as entries!")
else:
    print(f"  ⚠️  {errors + no_identity} entries precisam de atenção")
print()
PY

echo ""
ok "Ativação CLS V1.1 concluída. Sādhu 🙏"
