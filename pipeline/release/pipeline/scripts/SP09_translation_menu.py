#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SCRIPT S09
=====================================
Nome:       Gerador de Menu de Tradução (Schema V3.1 Aware)
Versão:     6.1  —  AXIS-NIDDHI Edition
Autor:      Lead SRE + Claude Sonnet 4.6
Data:       2026-02-28

POSIÇÃO NA SEQUÊNCIA:
  Step 8 — Roda APÓS S04 (upgrade v3.1) e S08b (Glossary Gate).
  Lê toda a CSL → gera Translation_Control_Center.csv

O QUE FAZ:
  Para cada post na 09-csl/:
    1. Lê identity.json (Schema V3.1, com fallback para schemas antigos)
    2. Conta caracteres do EN (exclui tags HTML)
    3. Detecta se pt-BR já existe → Status = DONE ou PENDING
    4. Calcula custo estimado DeepL e impacto na cota
    5. Grava linha no CSV

  O CSV gerado é o "cardápio" da tradução:
    - Posts DONE  → S10 vai pular automaticamente (idempotência)
    - Posts PENDING → S10 vai traduzir (se COMMAND = YES/SIM/X)

COMO USAR O CSV:
  Após rodar este script, abra o Translation_Control_Center.csv,
  revise a coluna COMMAND, escreva YES/SIM nos posts que quer traduzir
  e execute S10. Não precisa editar nada nos posts DONE.

DELTA vs V6.0 (versão anterior no Grimório):
  ★ BASE_DIR / paths → via config.py (/beng/pipeline)
  ★ COST_PER_CHAR / FREE_QUOTA → via config.py
  ★ Log estruturado em /beng/pipeline/logs/
  ★ Summary terminal com totais DONE/PENDING/custo
  ★ Sem --apply: este script é sempre write (só escreve o CSV de menu,
    nunca toca nos posts da CSL — é safe rodar múltiplas vezes)
"""

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  CONFIGURAÇÃO — via config.py canônico
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import (
    LOG_DIR,
    DIR_09_CSL,
    MENU_CSV,
    METADATA_DIR,
    FREE_QUOTA_LIMIT,
    COST_PER_CHAR_USD,
)

CSL_DIR       = DIR_09_CSL
MENU_FILE     = MENU_CSV
SECTIONS_FILE = METADATA_DIR / "MasterPDPN_Sections.csv"

# ==============================================================================
# 🎨  CORES
# ==============================================================================
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
RED    = "\033[91m"
RESET  = "\033[0m"

# ==============================================================================
# 🛠️  UTILITÁRIOS
# ==============================================================================

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"S09_menu_gen_{ts}.log"
    lines    = []

    def log(msg: str, level: str = "INFO"):
        icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERROR": "❌"}
        icon  = icons.get(level, "  ")
        ts_   = datetime.now(timezone.utc).strftime("%H:%M:%S")
        lines.append(f"[{ts_}] [{level}] {msg}")
        print(f"{icon}  {msg}")

    def flush():
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n{GRAY}    Log: {log_file}{RESET}")

    return log, flush


def load_sections_map() -> dict:
    """
    Retorna mapa {prefixo: nome_seção}.

    Prioridade:
      1. MasterPDPN_Sections.csv (se existir e for legível)
      2. Mapa canônico embutido (fonte: Script 13 / build.py)

    # TODO-FLAG: seções aparecendo como "PD - Uncategorized" indica que
    # MasterPDPN_Sections.csv está ausente ou com formato inesperado.
    # Investigar em sessão dedicada:
    #   cat /beng/pipeline/metadata/MasterPDPN_Sections.csv | head -10
    # O formato esperado é: "Nome da Seção;PREFIXO"  (separado por ponto-e-vírgula)
    # Se o arquivo usar vírgula ou outra ordem de colunas, ajustar o parser.
    # Enquanto isso, o mapa canônico embutido abaixo garante nomes corretos.
    """
    # Mapa canônico embutido — fonte: Script 13/build.py (sync manual necessário se novas seções)
    CANONICAL_SECTIONS = {
        "AB": "Abhidhamma",
        "BA": "Buddha Dhamma – Advanced",
        "BC": "Buddhist Chanting",
        "BD": "Buddha Dhamma",
        "BM": "Bhāvanā (Meditation)",
        "CH": "Buddhism in Charts",
        "DD": "Dhammapada",
        "DP": "Dhamma and Philosophy",
        "DS": "Dhamma and Science",
        "ER": "Elephants in the Room",
        "FT": "FootNotes",
        "HB": "Historical Background",
        "IS": 'Is There a "Self"?',
        "KD": "Key Dhamma Concepts",
        "LD": "Living Dhamma",
        "MR": "Myths or Realities?",
        "MS": "Miscellaneous",
        "NP": "NEW POSTS",
        "PD": "Pure Dhamma",
        "PS": "Paṭicca Samuppāda",
        "QD": "Quantum Mechanics and Dhamma",
        "SI": "Sutta Interpretations",
        "TL": "Three Levels of Practice",
        "TS": "Tables and Summaries",
        "CC": "Core Concepts",         # adicionado por precaução
    }

    # Tentar carregar do CSV (override do canônico)
    if SECTIONS_FILE.exists():
        try:
            csv_sections = {}
            with open(SECTIONS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if ";" in line:
                        parts = line.split(";", 1)
                        if len(parts) == 2:
                            name, prefix = parts[0].strip(), parts[1].strip()
                            if name and prefix:
                                csv_sections[prefix] = name
            if csv_sections:
                # CSV válido: merge com canônico (CSV tem precedência)
                merged = {**CANONICAL_SECTIONS, **csv_sections}
                return merged
        except Exception:
            pass
        # CSV existe mas não foi lido corretamente → usar canônico
    return CANONICAL_SECTIONS


def clean_html_tags(text: str) -> str:
    """Remove tags HTML para contar apenas caracteres de texto."""
    return re.sub(r"<[^>]+>", "", text)


# ==============================================================================
# 🚀  MOTOR PRINCIPAL
# ==============================================================================

def generate_menu():
    log, flush = setup_logger()

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 BRASILEIRINHO ENGINE — S09 Menu de Tradução v6.1{RESET}")
    print(f"{CYAN}  CSL    : {CSL_DIR}{RESET}")
    print(f"{CYAN}  Output : {MENU_FILE}{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    if not CSL_DIR.exists():
        log(f"CSL não encontrada: {CSL_DIR}", "ERROR")
        log("Execute S03 e S04 antes deste script.", "ERROR")
        sys.exit(1)

    sections_map = load_sections_map()
    if SECTIONS_FILE.exists():
        log(f"Seções: {len(sections_map)} entradas (CSV + mapa canônico embutido)")
    else:
        log(f"Seções: mapa canônico embutido ({len(sections_map)} seções) — MasterPDPN_Sections.csv ausente", "WARN")

    folders = sorted([f for f in CSL_DIR.iterdir() if f.is_dir() and f.name != 'meta'])
    log(f"Pastas na CSL: {len(folders)}")
    print()

    inventory  = []
    skipped    = 0
    total_chars_pending = 0
    total_cost_pending  = 0.0

    for folder in folders:
        json_path  = folder / "meta" / "identity.json"
        source_en  = folder / "source" / "en-US" / "content.html"
        source_pt  = folder / "source" / "pt-BR" / "content.html"

        if not json_path.exists():
            log(f"identity.json ausente em {folder.name} — pulando.", "WARN")
            skipped += 1
            continue

        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))

            # ── Leitura Schema V3.1 com fallback para schemas antigos ──────
            identity_block = data.get("identity", {})

            pdpn   = identity_block.get("pdpn")   or data.get("pdpn",   "UNKNOWN")
            findex = identity_block.get("findex")  or data.get("findex", "0000")
            slug   = (identity_block.get("slug_root")
                      or data.get("slug_en")
                      or data.get("slug", "unknown"))

            # ── Seção ──────────────────────────────────────────────────────
            prefix  = pdpn.split(".")[0] if "." in pdpn else "MS"
            section = sections_map.get(prefix, f"{prefix} - (seção desconhecida — verificar MasterPDPN_Sections.csv)")

            # ── Contagem de caracteres (texto limpo, sem tags) ─────────────
            chars = 0
            if source_en.exists():
                raw   = source_en.read_text(encoding="utf-8")
                chars = len(clean_html_tags(raw))

            # ── Status: DONE se pt-BR existe, PENDING se não ───────────────
            status = "DONE" if source_pt.exists() else "PENDING"

            # ── Métricas DeepL ─────────────────────────────────────────────
            cost  = chars * COST_PER_CHAR_USD
            quota = (chars / FREE_QUOTA_LIMIT) * 100

            if status == "PENDING":
                total_chars_pending += chars
                total_cost_pending  += cost

            inventory.append({
                "Fin-dex":       findex,
                "PD#PN":         pdpn,
                "Section":       section,
                "Slug":          slug,
                "Status":        status,
                "Chars":         chars,
                "Est_Cost_USD":  round(cost, 4),
                "Quota_Impact_%": round(quota, 2),
                "COMMAND":       "",   # operador preenche: YES/SIM/X para traduzir
            })

        except json.JSONDecodeError as e:
            log(f"identity.json malformado em {folder.name}: {e}", "ERROR")
            skipped += 1
        except Exception as e:
            log(f"Erro em {folder.name}: {e}", "ERROR")
            skipped += 1

    # ── Ordenar por Fin-dex ────────────────────────────────────────────────
    inventory.sort(key=lambda x: str(x["Fin-dex"]).zfill(4))

    # ── Salvar CSV ─────────────────────────────────────────────────────────
    MENU_FILE.parent.mkdir(parents=True, exist_ok=True)
    header = ["Fin-dex", "PD#PN", "Section", "Slug", "Status",
              "Chars", "Est_Cost_USD", "Quota_Impact_%", "COMMAND"]

    with open(MENU_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for item in inventory:
            row = item.copy()
            row["Quota_Impact_%"] = f"{item['Quota_Impact_%']}%"
            writer.writerow(row)

    # ── Contagens ──────────────────────────────────────────────────────────
    n_done    = sum(1 for i in inventory if i["Status"] == "DONE")
    n_pending = sum(1 for i in inventory if i["Status"] == "PENDING")
    total_quota_pending = (total_chars_pending / FREE_QUOTA_LIMIT) * 100

    # ── Summary ────────────────────────────────────────────────────────────
    print()
    print(f"{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  📊  SUMMARY — Menu de Tradução{RESET}")
    print(f"{CYAN}{'='*62}{RESET}")
    print(f"  Total de posts analisados : {len(inventory) + skipped}")
    print(f"  {GREEN}DONE  (pt-BR existe)      : {n_done}{RESET}")
    print(f"  {YELLOW}PENDING (aguarda tradução): {n_pending}{RESET}")
    print(f"  {GRAY}Pulados (sem identity.json): {skipped}{RESET}")
    print()
    print(f"  📋 Posts PENDING — estimativas DeepL:")
    print(f"     Caracteres totais   : {total_chars_pending:,}")
    print(f"     Custo estimado      : ${total_cost_pending:.2f} USD")
    print(f"     Impacto na cota     : {total_quota_pending:.1f}% de {FREE_QUOTA_LIMIT:,} chars/mês")
    print()
    print(f"  📄 CSV salvo em: {MENU_FILE}")
    print(f"{CYAN}{'='*62}{RESET}")
    print()
    print(f"  {YELLOW}📌 PRÓXIMOS PASSOS:{RESET}")
    print(f"  1. Abra o CSV e preencha COMMAND = YES nos posts a traduzir")
    print(f"     (ou use o one-liner no OPERATOR_GUIDE.md para marcar todos)")
    print(f"  2. Execute: {CYAN}python3 SP10_translate_deepl.py{RESET}")
    print()

    flush()
    sys.exit(0)


if __name__ == "__main__":
    generate_menu()
