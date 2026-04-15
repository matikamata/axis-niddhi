"""
💎 BRASILEIRINHO ENGINE - SCRIPT 11 (FINAL AUDIT)
=================================================
Nome:       Final Audit & Cleanup (CSL v1.0 Frozen Prep)
Versão:     1.0
Autor:      Gegên (SRE)
Data:       2026-01-31

OBJETIVO:
1. Remover artefatos residuais (content.json).
2. Validar conformidade estrita com Golden Sample.
3. Preparar para Congelamento.

REGRAS:
- NÃO alterar HTML.
- NÃO alterar Identity.json.
- APENAS remover lixo e reportar erros.
"""

import os
import json
import argparse
from pathlib import Path

# ==============================================================================
# ⚙️ CONFIGURAÇÃO
# ==============================================================================
BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR = BASE_DIR / "09-csl"

# ==============================================================================
# 🚀 MOTOR DE AUDITORIA
# ==============================================================================

def audit_csl(apply_fix=False):
    print(f"=== 🛡️ INICIANDO AUDITORIA FINAL CSL v1.0 ({'APPLY' if apply_fix else 'DRY-RUN'}) ===")
    
    if not CSL_DIR.exists():
        print("❌ ERRO: CSL não encontrada.")
        return

    folders = sorted([f for f in CSL_DIR.iterdir() if f.is_dir()])
    print(f"📂 Total de pastas: {len(folders)}")

    issues_found = 0
    cleaned_files = 0

    for folder in folders:
        pdpn = folder.name
        
        # Caminhos
        meta_dir = folder / "meta"
        source_en = folder / "source" / "en-US"
        
        identity_path = meta_dir / "identity.json"
        semantic_path = meta_dir / "semantic.json"
        html_path = source_en / "content.html"
        
        # Artefato Proibido
        forbidden_json = source_en / "content.json"

        # 1. Limpeza de Artefatos Proibidos
        if forbidden_json.exists():
            if apply_fix:
                forbidden_json.unlink()
                cleaned_files += 1
            else:
                print(f"🗑️  [LIXO] {pdpn}: content.json encontrado (seria removido).")
                issues_found += 1

        # 2. Validação Estrutural (Golden Sample)
        if not identity_path.exists():
            print(f"❌ [CRÍTICO] {pdpn}: identity.json ausente.")
            issues_found += 1
            continue
            
        if not semantic_path.exists():
            print(f"❌ [CRÍTICO] {pdpn}: semantic.json ausente.")
            issues_found += 1
        
        if not html_path.exists():
            print(f"❌ [CRÍTICO] {pdpn}: content.html ausente.")
            issues_found += 1

        # 3. Validação de Schema (Amostragem leve)
        try:
            with open(identity_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("schema_version") != "3.1":
                    print(f"⚠️ [SCHEMA] {pdpn}: Versão incorreta ({data.get('schema_version')}).")
                    issues_found += 1
        except Exception as e:
            print(f"❌ [JSON] {pdpn}: Erro ao ler identity: {e}")
            issues_found += 1

    print("="*50)
    print("🏁 RELATÓRIO FINAL")
    if apply_fix:
        print(f"🧹 Arquivos de lixo removidos: {cleaned_files}")
    else:
        print(f"⚠️  Problemas detectados: {issues_found}")
        if issues_found > 0:
            print("👉 Rode com --apply para corrigir a limpeza.")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Remove arquivos proibidos.")
    args = parser.parse_args()
    audit_csl(args.apply)
