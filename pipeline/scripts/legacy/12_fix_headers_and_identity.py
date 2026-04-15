"""
💎 BRASILEIRINHO ENGINE - SCRIPT 12 (SANEAMENTO)
================================================
Nome:       Fix Headers & Identity (Post-Audit Fix)
Versão:     1.0
Autor:      Gegên (SRE)
Data:       2026-01-31

OBJETIVO:
Corrige artefatos PT-BR existentes que têm headers incorretos ("THIS IS THE TREASURE").
Atualiza identity.json para status 'derived' e recalcula hashes.
"""

import os
import json
import re
import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR = BASE_DIR / "09-csl"

def get_utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def calculate_sha256(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def generate_derived_header(pdpn, extraction_date):
    return f"""<!--
💎 BRASILEIRINHO ENGINE - DERIVED TRANSLATION ARTIFACT
======================================================
PD#PN:        {pdpn}
Language:     pt-BR
Generated-At: {get_utc_now()}
Source-Ref:   {extraction_date}
Engine:       DeepL API (Glossary v5)
======================================================
DO NOT EDIT WITHOUT REVIEW LOG. THIS IS A DERIVATIVE WORK.
-->"""

def fix_artifacts(dry_run=False):
    print("=== 🛠️ INICIANDO SANEAMENTO DE ARTEFATOS PT-BR ===")
    
    count = 0
    for folder in CSL_DIR.iterdir():
        if not folder.is_dir(): continue
        
        pdpn = folder.name
        pt_file = folder / "source" / "pt-BR" / "content.html"
        json_file = folder / "meta" / "identity.json"

        if pt_file.exists() and json_file.exists():
            try:
                # 1. Ler Identity para pegar data de extração
                with open(json_file, 'r', encoding='utf-8') as f:
                    identity = json.load(f)
                
                extraction_date = identity["sro"].get("extraction_date", "UNKNOWN")

                # 2. Ler HTML PT Atual
                with open(pt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 3. Verificar se precisa de correção
                if "THIS IS THE TREASURE" in content or "Language:     en-US" in content:
                    print(f"🔧 Corrigindo {pdpn}...")
                    
                    # Remove header antigo
                    body = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL).strip()
                    
                    # Gera novo header
                    new_header = generate_derived_header(pdpn, extraction_date)
                    new_content = f"{new_header}\n\n{body}"
                    
                    # Salva
                    if not dry_run:
                        with open(pt_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                    
                    # Recalcula Hash
                    new_hash = calculate_sha256(new_content)
                    
                    # Atualiza Identity
                    if "pt-BR" in identity["artifacts"]:
                        identity["artifacts"]["pt-BR"]["status"] = "derived"
                        identity["artifacts"]["pt-BR"]["integrity_sha256"] = new_hash
                        # Remove campos antigos se existirem
                        identity["artifacts"]["pt-BR"].pop("last_audit", None)
                    
                    if not dry_run:
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(identity, f, indent=2, ensure_ascii=False)
                        
                    count += 1
                    print(f"   ✅ {pdpn} saneado. Novo Hash: {new_hash[:8]}")

            except Exception as e:
                print(f"❌ Erro em {pdpn}: {e}")

    print(f"=== SANEAMENTO CONCLUÍDO. {count} arquivos corrigidos. ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix PT-BR headers")
    parser.add_argument("--apply", action="store_true", help="Aplica mudanças. Sem isso, DRY-RUN.")
    args = parser.parse_args()
    dry = not args.apply
    print(f"Modo: {'DRY-RUN' if dry else 'APPLY'}")
    fix_artifacts(dry_run=dry)
