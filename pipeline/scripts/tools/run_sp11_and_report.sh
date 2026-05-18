# /beng-fut/pipeline/scripts/run_sp11_and_report.sh
#!/usr/bin/env bash
# ==============================================================================
# AXIS-NIDDHI V5.2.3 — Rodar SP11 --apply + Relatório pós-execução
# ==============================================================================
# USO:
#   bash /beng-fut/pipeline/scripts/run_sp11_and_report.sh
# ==============================================================================

set -euo pipefail

: "${AXIS_ALLOW_HARDCODED_LEGACY_TOOL:=}"
if [ "$AXIS_ALLOW_HARDCODED_LEGACY_TOOL" != "1" ]; then
  echo "ERROR: This legacy hardcoded tool is fenced. Set AXIS_ALLOW_HARDCODED_LEGACY_TOOL=1 only after explicit review." >&2
  exit 2
fi

SCRIPTS="/beng-fut/pipeline/scripts"
CSL="/beng-fut/pipeline/09-csl"

GREEN='\033[0;32m'; CYAN='\033[0;96m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $*${NC}"; }
info() { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║  AXIS-NIDDHI V5.2.3 — SP11 Apply + Relatório        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ==============================================================================
# PASSO 1 — Rodar SP11 --apply
# ==============================================================================
info "PASSO 1 — SP11 translate_titles --apply"

python3 "$SCRIPTS/SP11_translate_titles.py" --apply

# ==============================================================================
# PASSO 2 — Relatório pós-SP11
# ==============================================================================
info "PASSO 2 — Relatório pós-SP11"

python3 - <<'PY'
import json, re
from pathlib import Path

sys_path = "/beng-fut/pipeline/scripts"
import sys
sys.path.insert(0, sys_path)

CSL     = Path("/beng-fut/pipeline/09-csl")
PDPN_RE = re.compile(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$')

total = cls_v11 = with_pt_content = with_pt_title = lineage_updated = still_missing = 0

for folder in sorted(CSL.iterdir()):
    if not folder.is_dir() or not PDPN_RE.match(folder.name):
        continue
    total += 1
    ip = folder / "meta" / "identity.json"
    if not ip.exists():
        continue

    try:
        data = json.loads(ip.read_text(encoding="utf-8"))
    except Exception:
        continue

    lin = data.get("lineage", {})
    if lin.get("cls_version") == "1.1":
        cls_v11 += 1

    pt_html = folder / "source" / "pt-BR" / "content.html"
    has_pt_content = pt_html.exists() and pt_html.stat().st_size > 100

    if has_pt_content:
        with_pt_content += 1

    titles = data.get("titles", {})
    if titles.get("pt"):
        with_pt_title += 1
        # Contar entries com title_translated no lineage
        translations = lin.get("translations", [])
        if any(t.get("event") == "title_translated" for t in translations):
            lineage_updated += 1
    elif has_pt_content:
        still_missing += 1  # tem conteúdo PT mas ainda sem título

print()
print("━" * 52)
print("  RELATÓRIO PÓS-SP11 — AXIS-NIDDHI V5.2.3")
print("━" * 52)
print(f"  Total entries CSL              : {total}")
print(f"  CLS V1.1 ativo                 : {cls_v11}/{total} {'✅' if cls_v11==total else '⚠️'}")
print(f"  Posts com conteúdo PT-BR       : {with_pt_content}")
print(f"  Posts com título PT-BR         : {with_pt_title}")
print(f"  lineage.translations atualizados: {lineage_updated}")
print(f"  Posts ainda sem título PT      : {still_missing}")
print("━" * 52)
if still_missing == 0 and with_pt_content > 0:
    print(f"  ✅ Todos os {with_pt_content} posts PT-BR têm título traduzido.")
elif still_missing > 0:
    print(f"  ⚠️  {still_missing} posts com conteúdo PT ainda sem título.")
print("━" * 52)
print()
PY

ok "SP11 + relatório concluídos. Sādhu 🙏"
