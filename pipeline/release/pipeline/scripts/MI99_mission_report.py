#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — SCRIPT S99
=====================================
Nome:       Mission Intelligence Report (O Relator)
Versão:     2.0 (Canonical Edition)
Objetivo:   Condensar logs gigantescos em um resumo de alto sinal.
"""

import sys
import re
from pathlib import Path
from datetime import datetime

# ==============================================================================
# ⚙️ CONFIGURAÇÃO CANÔNICA
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from config import LOG_DIR, DIR_09_CSL, BASE_DIR

REPORT_PATH = BASE_DIR / "mission_report.txt"

# Tokens que indicam anomalias reais
# Excluídos intencionalmente:
#   "FORCED"         → operação legítima do SEAL 1/2
#   "Título PT ausente" → esperado para posts ainda não traduzidos
ANOMALY_TOKENS = ["[ERROR]", "FAIL", "❌"]
WARN_WHITELIST  = ["Título PT ausente", "Usando Fallback"]

# Regex para pasta PDPN válida (exclui meta/, slug_map.json, etc.)
import re as _re
_PDPN_RE = _re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")

def analyze_logs():
    if not LOG_DIR.exists():
        print(f"❌ Diretório de logs não encontrado: {LOG_DIR}")
        return

    all_logs = sorted(LOG_DIR.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    report = []
    report.append(f"🛡️ MISSION INTELLIGENCE REPORT")
    report.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("="*60)

    today = datetime.now().date()
    logs_today = [l for l in all_logs if datetime.fromtimestamp(l.stat().st_mtime).date() == today]

    if not logs_today:
        report.append("Nenhum log gerado hoje.")
    else:
        # Cálculo de tempo da rodada (diferença entre o log mais antigo e o mais novo de hoje)
        logs_today.sort(key=lambda x: x.stat().st_mtime)
        start_time = datetime.fromtimestamp(logs_today[0].stat().st_mtime)
        end_time = datetime.fromtimestamp(logs_today[-1].stat().st_mtime)
        duration = end_time - start_time
        report.append(f"⏱️ Tempo total da missão (hoje): {duration}")
        report.append("-" * 60)

        # Analisar do mais recente para o mais antigo
        for log_file in reversed(logs_today):
            try:
                with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.readlines()
            except Exception as e:
                report.append(f"\n📄 FILE: {log_file.name} - ERRO AO LER: {e}")
                continue
                
            total_lines = len(content)
            
            # Filtra linhas que contêm qualquer um dos tokens de anomalia
            anomalies = []
            for line in content:
                line_clean = line.strip()
                if any(token in line_clean for token in ANOMALY_TOKENS):
                    # Ignorar linhas whitelistadas (WARNs esperados)
                    if not any(w in line_clean for w in WARN_WHITELIST):
                        anomalies.append(line_clean)
            
            status = "🔴 ISSUES/FORCES FOUND" if anomalies else "🟢 CLEAN"
            report.append(f"\n📄 FILE: {log_file.name}")
            report.append(f"   Status: {status} ({total_lines} linhas processadas)")
            
            if anomalies:
                report.append("   Critical Snippets:")
                for a in anomalies[:10]:
                    # Limita o tamanho da linha para não quebrar a formatação
                    report.append(f"    > {a[:120]}..." if len(a) > 120 else f"    > {a}")
                if len(anomalies) > 10:
                    report.append(f"    > ... e mais {len(anomalies)-10} alertas ocultos.")

    # Resumo de Integridade da CSL
    report.append("\n" + "="*60)
    if DIR_09_CSL.exists():
        count = sum(1 for d in DIR_09_CSL.iterdir() if d.is_dir() and _PDPN_RE.match(d.name))
        report.append(f"🏛️ INTEGRITY: CSL contém {count} posts (pastas PDPN válidas).")
    else:
        report.append("🏛️ INTEGRITY: CSL não encontrada (Fase Genesis pendente?).")
    report.append("="*60)

    final_report = "\n".join(report)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(final_report)

    # Resumo de uma linha para o terminal
    issues = sum(1 for line in report if "🔴" in line)
    clean  = sum(1 for line in report if "🟢" in line)
    if issues:
        print(f"⚠️  MI99: {issues} log(s) com issues, {clean} limpos → {REPORT_PATH}")
    else:
        print(f"✅ MI99: todos os logs limpos → {REPORT_PATH}")

if __name__ == "__main__":
    analyze_logs()
