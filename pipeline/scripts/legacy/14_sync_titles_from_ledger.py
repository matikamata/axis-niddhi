"""
💎 BRASILEIRINHO ENGINE - SCRIPT 14
===================================
Nome:       Sincronização de Títulos via Master Ledger (CSV)
Versão:     2.0 (Canonical Edition)
Autor:      Lead SRE
Data:       2026-02-01

OBJETIVO:
Restaurar a integridade dos títulos em Inglês no identity.json usando
o arquivo CSV operacional como Fonte de Verdade Única (SRO).

POR QUE ESTA ABORDAGEM?
1. O Banco de Dados local pode estar contaminado (sobrescrito).
2. O HTML source pode não conter o título em tags H1.
3. O CSV operacional foi gerado antes de qualquer modificação.
"""

import os
import sys
import csv
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

if os.environ.get("AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT") != "1":
    print(
        "ERROR: This retired translation script is fenced and must not be run "
        "during normal AXIS-NIDDHI operations. "
        "Set AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1 only for supervised archaeology/recovery.",
        file=sys.stderr,
    )
    sys.exit(2)

# ==============================================================================
# ⚙️ CONFIGURAÇÃO
# ==============================================================================
BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR = BASE_DIR / "09-csl"
LEDGER_FILE = BASE_DIR / "metadata" / "PDPN_01_Operational.csv"
LOG_DIR = BASE_DIR / "logs"

def get_utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"sync_titles_v2_{timestamp}.log"
    def log(msg):
        print(f"ℹ️ {msg}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    return log

# ==============================================================================
# 🚀 MOTOR DE SINCRONIZAÇÃO
# ==============================================================================

def sync_titles(dry_run=False):
    log = setup_logger()
    log("=== 📜 INICIANDO SINCRONIZAÇÃO DE TÍTULOS VIA LEDGER ===")

    if not LEDGER_FILE.exists():
        log(f"❌ Erro: Ledger não encontrado em {LEDGER_FILE}")
        return

    # 1. Carregar o Ledger para Memória (Dicionário PD#PN -> Título)
    title_map = {}
    try:
        with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
            # O delimitador pode ser ';' conforme scripts anteriores
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                pdpn = row.get('PD#PN')
                title = row.get('Post_Name_English')
                if pdpn and title:
                    title_map[pdpn] = title
        log(f"✅ Ledger carregado: {len(title_map)} títulos mapeados.")
    except Exception as e:
        log(f"❌ Erro ao ler Ledger: {e}")
        return

    # 2. Varrer CSL e Atualizar JSONs
    count_fixed = 0
    folders = [f for f in CSL_DIR.iterdir() if f.is_dir()]

    for folder in folders:
        json_path = folder / "meta" / "identity.json"
        if not json_path.exists(): continue

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            pdpn = data.get("identity", {}).get("pdpn")
            if pdpn in title_map:
                real_title = title_map[pdpn]
                
                # Só atualiza se for diferente para evitar I/O desnecessário
                if data["titles"]["en"] != real_title:
                    data["titles"]["en"] = real_title
                    data["titles"]["en_source"] = "master_ledger_csv"
                    
                    # Resetar PT para garantir que a próxima tradução use o título novo
                    data["titles"]["pt"] = None
                    data["titles"]["pt_source"] = None
                    data["last_updated_utc"] = get_utc_now()

                    if not dry_run:
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    log(f"✨ Sincronizado: {pdpn} -> {real_title}")
                    count_fixed += 1

        except Exception as e:
            log(f"❌ Erro em {folder.name}: {e}")

    log("="*50)
    log(f"🏁 FIM DA OPERAÇÃO. Títulos corrigidos: {count_fixed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    dry = not args.apply
    print(f"Modo: {'DRY-RUN' if dry else 'APPLY'}")
    sync_titles(dry_run=dry)
