#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — S08b
================================
Nome:       Glossary Gate (Parada Obrigatória)
Versão:     1.0
Sequência:  S08b → entre S08 e S09 (NÃO PULAR)
Criado:     2026-02-27 (Genesis v2.0)
Sugestão:   Aloka (ChatGPT) — proteção do ciclo de tradução

FUNÇÃO:
Parada cerimonial obrigatória para revisão humana do glossário
antes de iniciar qualquer tradução DeepL.

VERIFICA:
  - metadata/Glossario_v5.csv existe e tem conteúdo
  - metadata/glossary_config.json foi gerado (S08 rodou)
  - Exibe estatísticas do glossário atual

CONFIRMAR digitando: GLOSSARY_OK
"""

import os
import json
import csv
import sys
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO — via config.py canônico (AXIS-NIDDHI V5.4 hardening)
# ==============================================================================

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import METADATA_DIR, GLOSSARY_JSON as _GLOSSARY_JSON_PATH

GLOSSARY_CSV  = METADATA_DIR / "Glossario_v5.csv"
GLOSSARY_JSON = _GLOSSARY_JSON_PATH

def main():
    print()
    print("=" * 60)
    print("⛩️  GLOSSARY GATE — S08b")
    print("    Parada obrigatória antes de S09 (tradução DeepL)")
    print("=" * 60)
    print()

    # 1. Verificar CSV
    if not GLOSSARY_CSV.exists():
        print(f"❌ ERRO: {GLOSSARY_CSV} não encontrado.")
        sys.exit(1)

    with open(GLOSSARY_CSV, encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter=';'))
    print(f"📋 Glossario_v5.csv: {len(rows)-1} termos")

    # 2. Verificar JSON gerado pelo S08
    if not GLOSSARY_JSON.exists():
        print(f"❌ ERRO: glossary_config.json não encontrado.")
        print(f"   → Rode S08 antes de S08b.")
        sys.exit(1)

    with open(GLOSSARY_JSON, encoding='utf-8') as f:
        gconfig = json.load(f)
    print(f"✅ glossary_config.json: {len(gconfig.get('entries', []))} entradas compiladas")
    print()

    # 3. Exibir amostra
    print("📖 Amostra (primeiros 5 termos):")
    for row in rows[1:6]:
        if row:
            print(f"   {' | '.join(row[:3])}")
    print()

    # 4. Gate
    print("─" * 60)
    print("ANTES DE CONTINUAR, VERIFIQUE:")
    print("  1. Há termos novos que precisam ser adicionados?")
    print("  2. Há conflitos com traduções PT já existentes?")
    print("  3. O glossário está aprovado para este ciclo?")
    print()
    print("Abra o arquivo se necessário:")
    print(f"  {GLOSSARY_CSV}")
    print()

    confirmacao = input("Digite GLOSSARY_OK para continuar (ou Ctrl+C para abortar): ").strip()

    if confirmacao != "GLOSSARY_OK":
        print()
        print("⛔ Gate não confirmado. Pipeline pausado.")
        print("   Revise o glossário e rode S08b novamente.")
        sys.exit(1)

    print()
    print("✅ GLOSSARY GATE APROVADO — pode prosseguir com S09.")
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
