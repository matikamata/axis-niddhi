# /beng-fut/pipeline/scripts/validate_cls_pipeline.sh
#!/usr/bin/env bash
# ==============================================================================
# AXIS-NIDDHI V5.2.1 — Validação CLS + Pré-verificação Pipeline
# ==============================================================================
# Executa os 4 passos pedidos pela Aloka:
#   1. Verificar existência dos arquivos principais
#   2. Auditar CLS em todo o CSL (748 entries)
#   3. Validar SG01 / SP10 / SP11 (sem rodar — só checar)
#   4. Gerar relatório final
#
# USO:
#   bash /beng-fut/pipeline/scripts/validate_cls_pipeline.sh
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
info() { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }
err()  { echo -e "${RED}❌ $*${NC}"; }

REPORT_ERRORS=0

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  AXIS-NIDDHI V5.2.1 — Validação CLS + Pipeline      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==============================================================================
# PASSO 1 — Verificar arquivos principais
# ==============================================================================
info "PASSO 1 — Arquivos principais"

check_file() {
    local path="$1" label="$2"
    if [ -f "$path" ]; then
        ok "$label: $path"
    else
        err "$label NÃO encontrado: $path"
        REPORT_ERRORS=$((REPORT_ERRORS + 1))
    fi
}

check_dir() {
    local path="$1" label="$2"
    if [ -d "$path" ]; then
        local count
        count=$(find "$path" -maxdepth 1 -mindepth 1 -type d | wc -l)
        ok "$label: $path ($count entries)"
    else
        err "$label NÃO encontrado: $path"
        REPORT_ERRORS=$((REPORT_ERRORS + 1))
    fi
}

check_file "$SCRIPTS/cls_tools.py"          "cls_tools.py"
check_file "$CONFIG/lineage_schema.json"    "lineage_schema.json"
check_dir  "$CSL"                           "CSL 09-csl"

# ==============================================================================
# PASSO 2 — Audit CLS em todo o CSL
# ==============================================================================
info "PASSO 2 — Audit CLS (748 entries)"

python3 "$SCRIPTS/cls_tools.py" audit "$CSL"

# ==============================================================================
# PASSO 3 — Pré-verificação dos scripts SG01 / SP10 / SP11
# ==============================================================================
info "PASSO 3 — Pré-verificação SG01 / SP10 / SP11"

for script in SG01_extract_html.py SP10_translate_deepl.py SP11_translate_titles.py; do
    path="$SCRIPTS/$script"
    if [ ! -f "$path" ]; then
        err "$script não encontrado"
        REPORT_ERRORS=$((REPORT_ERRORS + 1))
        continue
    fi

    # Verificar syntax Python
    if python3 -m py_compile "$path" 2>/dev/null; then
        syntax_ok="✅ syntax OK"
    else
        syntax_ok="❌ SYNTAX ERROR"
        REPORT_ERRORS=$((REPORT_ERRORS + 1))
    fi

    # Verificar imports principais
    imports=$(python3 - <<PY
import ast, sys
try:
    tree = ast.parse(open("$path").read())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    # Filtrar só os relevantes
    relevant = [i for i in imports if i in ('config','pipeline_utils','cls_tools','requests','json','pathlib','sys','re','csv')]
    print(", ".join(sorted(set(relevant))))
except Exception as e:
    print(f"erro: {e}")
PY
)

    echo "  $script"
    echo "    $syntax_ok"
    echo "    imports detectados: $imports"

    # Verificar se cls_tools está importado ou se é compatível
    if grep -q "cls_tools\|append_translation_event\|append_transformation" "$path" 2>/dev/null; then
        echo "    ✅ CLS integrado neste script"
    else
        echo "    ℹ️  CLS não integrado ainda — adicionável via cls_tools import"
    fi
    echo ""
done

# Verificar que config.py e pipeline_utils.py estão presentes (dependências)
echo "  Dependências compartilhadas:"
for dep in config.py pipeline_utils.py; do
    [ -f "$SCRIPTS/$dep" ] && echo "    ✅ $dep" || { echo "    ❌ $dep AUSENTE"; REPORT_ERRORS=$((REPORT_ERRORS + 1)); }
done

# Verificar chave DeepL (necessária para SP10/SP11)
echo ""
echo "  Credenciais:"
if [ -f "$SCRIPTS/deepl_key.txt" ] && [ -s "$SCRIPTS/deepl_key.txt" ]; then
    echo "    ✅ deepl_key.txt presente e não vazio"
else
    warn "    deepl_key.txt ausente ou vazio — SP10/SP11 precisarão dela"
fi

# ==============================================================================
# PASSO 4 — Relatório final
# ==============================================================================
info "PASSO 4 — Relatório Final"

python3 - <<'PY'
import json, re
from pathlib import Path

CSL = Path("/beng-fut/pipeline/09-csl")
PDPN_RE = re.compile(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$')

total = v11 = translated = with_titles_pt = 0

for folder in CSL.iterdir():
    if not folder.is_dir() or not PDPN_RE.match(folder.name):
        continue
    total += 1
    ip = folder / "meta" / "identity.json"
    if not ip.exists():
        continue
    try:
        data = json.loads(ip.read_text(encoding="utf-8"))
        lin = data.get("lineage", {})
        if lin.get("cls_version") == "1.1":
            v11 += 1
        # Contar posts com conteúdo PT traduzido
        artifacts = data.get("artifacts", {})
        if "pt-BR" in artifacts:
            translated += 1
        # Contar posts com título PT
        titles = data.get("titles", {})
        if titles.get("pt"):
            with_titles_pt += 1
    except Exception:
        pass

print("━" * 52)
print("  RELATÓRIO CLS — AXIS-NIDDHI V5.2.1")
print("━" * 52)
print(f"  Total entries CSL          : {total}")
print(f"  CLS V1.1 ativo             : {v11}/{total} {'✅' if v11==total else '⚠️'}")
print(f"  Posts com conteúdo PT-BR   : {translated}")
print(f"  Posts com título PT-BR     : {with_titles_pt}")
print("━" * 52)
print()
print("  CHECKLIST PARA PRÓXIMA EXECUÇÃO:")
print(f"  {'✅' if v11==total else '❌'} CLS V1.1 ativo em 748 entries")
print(f"  {'✅' if total > 0 else '❌'} CSL íntegro e acessível")
print(f"  ℹ️  SG01: popula origin.source_html_sha256 + extracted_at")
print(f"  ℹ️  SP11: popula translations[title_translated] via cls_tools")
print(f"  ℹ️  SP10: popula translations[translated] via cls_tools")
print("━" * 52)
PY

echo ""
if [ "$REPORT_ERRORS" -eq 0 ]; then
    ok "Validação concluída sem erros. Pipeline pronto. Sādhu 🙏"
else
    warn "Validação concluída com $REPORT_ERRORS problema(s) — ver itens ❌ acima."
fi
