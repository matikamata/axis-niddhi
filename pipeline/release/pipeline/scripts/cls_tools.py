# /beng-fut/pipeline/scripts/cls_tools.py
#!/usr/bin/env python3
"""
💎 BRASILEIRINHO ENGINE — cls_tools.py
=======================================
Sprint:  AXIS-NIDDHI V5.2.1 — CLS Hardening
Data:    2026-03-08

Content Lineage System — CLS Tools V1.1

CHANGELOG:
  V1.0 (V5.2)   — estrutura inicial: origin flat, translation_history,
                   publication_history, flags
  V1.1 (V5.2.1) — hardening criptográfico:
                   ★ origin.source_html_sha256 — auditoria da origem
                   ★ origin.extracted_at       — timestamp SG01
                   ★ csl block                 — pdpn + schema_version + created_at
                   ★ transformations[]         — log de mutações do pipeline
                   ★ translations[]            — substitui translation_history
                   ★ source_hash/result_hash   — rastreabilidade por evento
                   ★ upgrade automático V1.0→V1.1 (sem perda de dados)

FUNÇÃO:
  Toolkit para injetar, ler e atualizar o bloco 'lineage' dentro de
  identity.json, sem quebrar nenhum campo existente do schema V3.1.

REGRAS DE SEGURANÇA:
  • Nunca altera schema_version, identity, sro, titles, artifacts
  • Nunca altera content.html
  • Nunca altera hashes já selados nos artifacts
  • translation_history (V1.0) é migrado para translations[], nunca deletado
    antes da migração ser confirmada

COMO USAR:
  from cls_tools import (
      inject_lineage_stub,          # inicializa lineage em um identity.json
      upgrade_lineage_v10_to_v11,   # migra bloco V1.0 → V1.1
      append_transformation_event,  # registra mutação do pipeline
      append_translation_event,     # registra evento de tradução
      append_publication_event,     # registra evento de publicação
      get_lineage,                  # lê o bloco lineage
      set_flag,                     # define flag de estado
      backfill_lineage,             # injeta/atualiza em batch (748 entries)
  )
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

# Bootstrap: importa pipeline_utils do mesmo diretório
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from pipeline_utils import atomic_write_json, get_utc_now, sha256_file
except ImportError:
    # Fallback para uso fora do engine (testes, CI)
    import os
    from datetime import datetime, timezone

    def atomic_write_json(path, data):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)

    def get_utc_now():
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def sha256_file(path):
        import hashlib
        p = Path(path)
        if not p.exists():
            return None
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

CLS_VERSION     = "1.1"
CLS_VERSION_OLD = "1.0"
PDPN_RE         = re.compile(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$')


# ==============================================================================
# HELPERS INTERNOS
# ==============================================================================

def _load(path: Path) -> Optional[dict]:
    """Carrega identity.json. Retorna None em caso de erro."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        return None


def _save(path: Path, data: dict) -> bool:
    """Grava identity.json atomicamente. Retorna True se ok."""
    try:
        atomic_write_json(Path(path), data)
        return True
    except Exception:
        return False


def _empty_lineage(
    wp_post_id: Optional[int] = None,
    source_html: Optional[str] = None,
    source_html_sha256: Optional[str] = None,
    extracted_at: Optional[str] = None,
    pdpn: Optional[str] = None,
    csl_schema_version: str = "3.1",
    created_at: Optional[str] = None,
) -> dict:
    """Retorna um bloco lineage V1.1 vazio com metadados iniciais."""
    return {
        "cls_version": CLS_VERSION,
        "origin": {
            "wp_post_id":          wp_post_id,
            "source_html":         source_html or "",
            "source_html_sha256":  source_html_sha256,
            "extracted_at":        extracted_at,
        },
        "csl": {
            "pdpn":           pdpn,
            "schema_version": csl_schema_version,
            "created_at":     created_at or get_utc_now(),
        },
        "transformations":   [],
        "translations":      [],
        "publication_history": [],
        "flags": {
            "needs_retranslation": False,
            "manual_pt_edit":      False,
            "glossary_mismatch":   False,
        },
    }


# ==============================================================================
# LEITURA
# ==============================================================================

def get_lineage(identity_path: Path) -> Optional[dict]:
    """Lê o bloco 'lineage' de um identity.json. Retorna None se ausente."""
    data = _load(identity_path)
    return data.get("lineage") if data else None


def has_lineage(identity_path: Path) -> bool:
    return get_lineage(identity_path) is not None


def get_cls_version(identity_path: Path) -> Optional[str]:
    """Retorna a cls_version do bloco lineage, ou None se ausente."""
    lin = get_lineage(identity_path)
    return lin.get("cls_version") if lin else None


# ==============================================================================
# E10 — UPGRADE V1.0 → V1.1 (compatibilidade retroativa)
# ==============================================================================

def upgrade_lineage_v10_to_v11(identity_path: Path) -> str:
    """
    Migra um bloco lineage de V1.0 para V1.1 sem perda de dados.

    Mudanças aplicadas:
      - cls_version: "1.0" → "1.1"
      - origin (flat V1.0) → origin com source_html_sha256 + extracted_at
      - Adiciona bloco 'csl' (pdpn, schema_version, created_at)
      - translation_history[] → translations[] (com campos novos, sem remoção)
      - Preserva publication_history e flags intactos

    Retorna: 'UPGRADED' | 'ALREADY_V11' | 'NO_LINEAGE' | 'ERROR:<msg>'
    """
    p = Path(identity_path)
    data = _load(p)
    if data is None:
        return "ERROR:cannot_load"

    lin = data.get("lineage")
    if lin is None:
        return "NO_LINEAGE"

    current_version = lin.get("cls_version", "1.0")
    if current_version == CLS_VERSION:
        return "ALREADY_V11"

    # ── Migrar origin ──────────────────────────────────────────────────────
    old_origin = lin.get("origin", {})
    # V1.0 tinha campos diretos no lineage (source_html, migration_batch, etc.)
    # V1.1 tem tudo dentro de origin{}
    new_origin = {
        "wp_post_id":         old_origin.get("wp_post_id")
                              or lin.get("original_wp_id")
                              or data.get("sro", {}).get("original_wp_id"),
        "source_html":        old_origin.get("source_html")
                              or lin.get("source_html", ""),
        "source_html_sha256": old_origin.get("source_html_sha256"),  # novo — None ok
        "extracted_at":       old_origin.get("extracted_at"),        # novo — None ok
    }

    # ── Migrar/criar csl block ─────────────────────────────────────────────
    old_csl = lin.get("csl", {})
    identity_block = data.get("identity", {})
    new_csl = {
        "pdpn":           old_csl.get("pdpn") or identity_block.get("pdpn") or p.parent.parent.name,
        "schema_version": old_csl.get("schema_version") or data.get("schema_version", "3.1"),
        "created_at":     old_csl.get("created_at") or lin.get("csl_created_utc"),
    }

    # ── Migrar translation_history → translations ──────────────────────────
    # V1.0: translation_history com campos: event, utc, engine, deepl_chars,
    #        glossary_id, seal_hash_pt, note
    # V1.1: translations com: lang, event, engine, utc, source_hash,
    #        result_hash, deepl_chars, glossary_id, note
    old_th = lin.get("translation_history", [])
    existing_translations = lin.get("translations", [])

    migrated = []
    for entry in old_th:
        migrated.append({
            "lang":        "pt-BR",                           # V1.0 era implicitamente PT-BR
            "event":       entry.get("event", "translated"),
            "engine":      entry.get("engine", "unknown"),
            "utc":         entry.get("utc", get_utc_now()),
            "source_hash": None,                              # não existia em V1.0
            "result_hash": entry.get("seal_hash_pt"),         # era seal_hash_pt em V1.0
            "deepl_chars": entry.get("deepl_chars"),
            "glossary_id": entry.get("glossary_id"),
            "note":        entry.get("note"),
        })

    # Combinar: migrados primeiro, depois quaisquer entries V1.1 já existentes
    new_translations = migrated + [e for e in existing_translations if e not in migrated]

    # ── Preservar publication_history e flags ──────────────────────────────
    new_lineage = {
        "cls_version":       CLS_VERSION,
        "origin":            new_origin,
        "csl":               new_csl,
        "transformations":   lin.get("transformations", []),
        "translations":      new_translations,
        "publication_history": lin.get("publication_history", []),
        "flags":             lin.get("flags", {
            "needs_retranslation": False,
            "manual_pt_edit":      False,
            "glossary_mismatch":   False,
        }),
    }

    data["lineage"] = new_lineage
    ok = _save(p, data)
    return "UPGRADED" if ok else "ERROR:write_failed"


# ==============================================================================
# E9 — INJEÇÃO INICIAL (stub V1.1)
# ==============================================================================

def inject_lineage_stub(
    identity_path: Path,
    source_html: Optional[str] = None,
    source_html_sha256: Optional[str] = None,
    extracted_at: Optional[str] = None,
    migration_batch: Optional[str] = None,   # preservado para compatibilidade de chamada
    force: bool = False,
) -> str:
    """
    Injeta bloco lineage V1.1 em um identity.json existente.
    Preenche origin e csl a partir dos dados já presentes no identity.json.

    Args:
        source_html:          Nome do HTML original (ex: 'WP_12345_slug.html').
        source_html_sha256:   SHA-256 do HTML bruto extraído (SG01).
        extracted_at:         Timestamp UTC da extração.
        migration_batch:      Ignorado em V1.1 (mantido por compatibilidade).
        force:                Reinicializa mesmo que lineage já exista.

    Retorna: 'INJECTED' | 'ALREADY_EXISTS' | 'FORCED' | 'ERROR:<msg>'
    """
    p = Path(identity_path)
    data = _load(p)
    if data is None:
        return "ERROR:cannot_load"

    current_lin = data.get("lineage")

    # Se V1.0 existe e não é force, fazer upgrade automático
    if current_lin and current_lin.get("cls_version") == CLS_VERSION_OLD and not force:
        result = upgrade_lineage_v10_to_v11(p)
        return f"UPGRADED_V10_TO_V11:{result}"

    if current_lin and not force:
        return "ALREADY_EXISTS"

    # Herdar metadados do identity.json existente
    sro      = data.get("sro", {})
    identity = data.get("identity", {})
    pdpn     = identity.get("pdpn") or p.parent.parent.name

    wp_post_id = sro.get("original_wp_id")

    data["lineage"] = _empty_lineage(
        wp_post_id=wp_post_id,
        source_html=source_html,
        source_html_sha256=source_html_sha256,
        extracted_at=extracted_at,
        pdpn=pdpn,
        csl_schema_version=data.get("schema_version", "3.1"),
    )

    ok = _save(p, data)
    if not ok:
        return "ERROR:write_failed"
    return "FORCED" if force else "INJECTED"


# ==============================================================================
# E8 — append_transformation_event (NOVO em V1.1)
# ==============================================================================

def append_transformation_event(
    identity_path: Path,
    step: str,
    input_hash: Optional[str] = None,
    output_hash: Optional[str] = None,
    note: Optional[str] = None,
) -> bool:
    """
    Registra uma transformação do pipeline no bloco lineage.transformations[].

    Uso típico: chamar no final de SG02, SP03, SP04, SP05 para cada post
    que foi efetivamente modificado.

    Args:
        step:        Nome do script/etapa (ex: 'SG02_preprocess', 'SP05_fix_headers').
        input_hash:  SHA-256 do content.html ANTES da transformação.
        output_hash: SHA-256 do content.html APÓS a transformação.
        note:        Nota livre (ex: 'removed 3 iframes').

    Retorna True se gravou, False se lineage ausente ou erro.
    """
    p = Path(identity_path)
    data = _load(p)
    if data is None or "lineage" not in data:
        return False

    entry = {
        "step":        step,
        "utc":         get_utc_now(),
        "input_hash":  input_hash,
        "output_hash": output_hash,
        "note":        note,
    }
    data["lineage"].setdefault("transformations", []).append(entry)
    return _save(p, data)


# ==============================================================================
# E8 — append_translation_event (atualizado para V1.1)
# ==============================================================================

def append_translation_event(
    identity_path: Path,
    event: str,
    engine: str,
    lang: str = "pt-BR",
    source_hash: Optional[str] = None,
    result_hash: Optional[str] = None,
    deepl_chars: Optional[int] = None,
    glossary_id: Optional[str] = None,
    note: Optional[str] = None,
    # V1.0 compat: seal_hash_pt mapeado para result_hash
    seal_hash_pt: Optional[str] = None,
) -> bool:
    """
    Registra evento de tradução em lineage.translations[].

    Args:
        event:       'translated' | 'retranslated' | 'title_translated' |
                     'glossary_updated' | 'manual_edit'
        engine:      Script/sistema (ex: 'SP10_v5.2', 'SP11_v5.2').
        lang:        Língua alvo (default: 'pt-BR').
        source_hash: SHA-256 do content.html EN antes da tradução.
        result_hash: SHA-256 do content.html PT após a tradução.
        seal_hash_pt: Alias V1.0 para result_hash (compatibilidade).
        deepl_chars: Chars consumidos na API DeepL.
        glossary_id: ID do glossário DeepL.
        note:        Nota livre.
    """
    VALID_EVENTS = {"translated", "retranslated", "title_translated", "glossary_updated", "manual_edit"}
    if event not in VALID_EVENTS:
        raise ValueError(f"Evento inválido: '{event}'. Válidos: {VALID_EVENTS}")

    p = Path(identity_path)
    data = _load(p)
    if data is None or "lineage" not in data:
        return False

    # Compatibilidade V1.0: seal_hash_pt → result_hash
    effective_result_hash = result_hash or seal_hash_pt

    entry = {
        "lang":        lang,
        "event":       event,
        "engine":      engine,
        "utc":         get_utc_now(),
        "source_hash": source_hash,
        "result_hash": effective_result_hash,
        "deepl_chars": deepl_chars,
        "glossary_id": glossary_id,
        "note":        note,
    }
    data["lineage"].setdefault("translations", []).append(entry)
    return _save(p, data)


# ==============================================================================
# append_publication_event (inalterado em V1.1)
# ==============================================================================

def append_publication_event(
    identity_path: Path,
    event: str,
    wp_post_id: Optional[int] = None,
    wp_lang: Optional[str] = None,
    engine: Optional[str] = None,
) -> bool:
    """
    Registra evento de publicação em lineage.publication_history[].

    Args:
        event: 'injected' | 'updated' | 'failed'
    """
    VALID_EVENTS = {"injected", "updated", "failed"}
    if event not in VALID_EVENTS:
        raise ValueError(f"Evento inválido: '{event}'. Válidos: {VALID_EVENTS}")

    p = Path(identity_path)
    data = _load(p)
    if data is None or "lineage" not in data:
        return False

    entry = {
        "event":      event,
        "utc":        get_utc_now(),
        "wp_post_id": wp_post_id,
        "wp_lang":    wp_lang,
        "engine":     engine,
    }
    data["lineage"].setdefault("publication_history", []).append(entry)
    return _save(p, data)


# ==============================================================================
# record_seal1_hash (inalterado em V1.1)
# ==============================================================================

def record_seal1_hash(identity_path: Path, sha256_en: str) -> bool:
    """
    Registra o hash EN no momento do SEAL 1 em origin.source_html_sha256
    se ainda não preenchido, e também na futura chain de transformações.
    """
    p = Path(identity_path)
    data = _load(p)
    if data is None or "lineage" not in data:
        return False

    lin = data["lineage"]
    # Preencher source_html_sha256 no origin se vazio
    origin = lin.setdefault("origin", {})
    if not origin.get("source_html_sha256"):
        origin["source_html_sha256"] = sha256_en

    return _save(p, data)


# ==============================================================================
# FLAGS
# ==============================================================================

def set_flag(identity_path: Path, flag: str, value: bool) -> bool:
    """
    Define um flag no bloco lineage.flags.
    Válidos: needs_retranslation | manual_pt_edit | glossary_mismatch
    """
    VALID_FLAGS = {"needs_retranslation", "manual_pt_edit", "glossary_mismatch"}
    if flag not in VALID_FLAGS:
        raise ValueError(f"Flag inválido: '{flag}'. Válidos: {VALID_FLAGS}")

    p = Path(identity_path)
    data = _load(p)
    if data is None or "lineage" not in data:
        return False

    data["lineage"].setdefault("flags", {})[flag] = value
    return _save(p, data)


# ==============================================================================
# BACKFILL — E12: injeta V1.1 ou atualiza V1.0→V1.1 em batch
# ==============================================================================

def backfill_lineage(
    csl_root: Path,
    migration_batch: str = "backfill_v5.2.1",
    dry_run: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Percorre todas as entries CSL e:
      1. Injeta bloco lineage V1.1 onde não existe
      2. Atualiza V1.0 → V1.1 automaticamente (sem perda de dados)
      3. Não toca em entries já em V1.1

    Uso (primeira vez após deploy V5.2.1):
        python3 cls_tools.py backfill /beng-runtime/pipeline/csl --apply

    Retorna dict com contadores.
    """
    stats = {
        "total":          0,
        "injected":       0,
        "upgraded_v10":   0,
        "already_v11":    0,
        "errors":         0,
    }

    csl_root = Path(csl_root)
    if not csl_root.exists():
        print(f"❌ CSL root não encontrada: {csl_root}")
        return stats

    for folder in sorted(csl_root.iterdir()):
        if not folder.is_dir() or not PDPN_RE.match(folder.name):
            continue

        stats["total"] += 1
        identity_path = folder / "meta" / "identity.json"

        if not identity_path.exists():
            stats["errors"] += 1
            if verbose:
                print(f"  ⚠️  {folder.name}: identity.json ausente")
            continue

        current_version = get_cls_version(identity_path)

        # Caso 1: já em V1.1
        if current_version == CLS_VERSION:
            stats["already_v11"] += 1
            if verbose:
                print(f"  ─  {folder.name}: já V1.1")
            continue

        # Caso 2: V1.0 — upgrade automático
        if current_version == CLS_VERSION_OLD:
            if dry_run:
                stats["upgraded_v10"] += 1
                if verbose:
                    print(f"  🔄 {folder.name}: [DRY-RUN] upgrade V1.0 → V1.1")
            else:
                result = upgrade_lineage_v10_to_v11(identity_path)
                if result == "UPGRADED":
                    stats["upgraded_v10"] += 1
                    if verbose:
                        print(f"  🔄 {folder.name}: upgraded V1.0 → V1.1")
                else:
                    stats["errors"] += 1
                    if verbose:
                        print(f"  ❌ {folder.name}: upgrade falhou — {result}")
            continue

        # Caso 3: sem lineage — injetar V1.1
        if dry_run:
            stats["injected"] += 1
            if verbose:
                print(f"  ✨ {folder.name}: [DRY-RUN] injetaria lineage V1.1")
        else:
            result = inject_lineage_stub(identity_path)
            if result in ("INJECTED", "FORCED") or result.startswith("UPGRADED"):
                stats["injected"] += 1
                if verbose:
                    print(f"  ✅ {folder.name}: lineage V1.1 injetado")
            else:
                stats["errors"] += 1
                if verbose:
                    print(f"  ❌ {folder.name}: {result}")

    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"\n{'━'*52}")
    print(f"[CLS BACKFILL V1.1 — {mode}]")
    print(f"  Total entries    : {stats['total']}")
    print(f"  Injetados (novo) : {stats['injected']}")
    print(f"  Upgraded V1.0→V1.1: {stats['upgraded_v10']}")
    print(f"  Já em V1.1       : {stats['already_v11']}")
    print(f"  Erros            : {stats['errors']}")
    print(f"{'━'*52}\n")
    return stats


# ==============================================================================
# CLI
# ==============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="CLS Tools V1.1 — Content Lineage System (AXIS-NIDDHI V5.2.1)"
    )
    sub = parser.add_subparsers(dest="cmd")

    # backfill
    p_bf = sub.add_parser("backfill", help="Injetar/atualizar lineage em todas as entries CSL")
    p_bf.add_argument("csl_root", help="Caminho para a raiz do CSL")
    p_bf.add_argument("--apply", action="store_true", help="Gravar (default: dry-run)")
    p_bf.add_argument("--batch", default="backfill_v5.2.1")
    p_bf.add_argument("--quiet", action="store_true")

    # status — um único identity.json
    p_st = sub.add_parser("status", help="Mostrar lineage de um identity.json")
    p_st.add_argument("identity_path")

    # audit — varrer todo o CSL e gerar relatório
    p_au = sub.add_parser("audit", help="Auditar CLS em todo o CSL (aceita diretório)")
    p_au.add_argument("csl_root", help="Raiz do CSL (ex: /beng-fut/pipeline/09-csl)")
    p_au.add_argument("--verbose", action="store_true", help="Mostrar cada entry")

    # upgrade — um único identity.json
    p_up = sub.add_parser("upgrade", help="Forçar upgrade V1.0→V1.1 em um identity.json")
    p_up.add_argument("identity_path")

    args = parser.parse_args()

    if args.cmd == "backfill":
        backfill_lineage(
            csl_root=Path(args.csl_root),
            migration_batch=args.batch,
            dry_run=not args.apply,
            verbose=not args.quiet,
        )

    elif args.cmd == "status":
        p = Path(args.identity_path)
        # Aceita tanto identity.json direto quanto diretório PDPN
        if p.is_dir():
            p = p / "meta" / "identity.json"
        lin = get_lineage(p)
        if lin is None:
            print("❌ Sem bloco lineage neste identity.json.")
        else:
            print(json.dumps(lin, ensure_ascii=False, indent=2))

    elif args.cmd == "audit":
        # Varrer todo o CSL e gerar relatório de integridade CLS
        csl_root = Path(args.csl_root)
        stats = {
            "total": 0, "v11": 0, "v10": 0,
            "no_lineage": 0, "no_identity": 0, "errors": 0,
            "attention": [],
        }

        if not csl_root.exists():
            print(f"❌ CSL não encontrado: {csl_root}")
            sys.exit(1)

        for folder in sorted(csl_root.iterdir()):
            if not folder.is_dir() or not PDPN_RE.match(folder.name):
                continue
            stats["total"] += 1
            ip = folder / "meta" / "identity.json"

            if not ip.exists():
                stats["no_identity"] += 1
                stats["attention"].append((folder.name, "sem identity.json"))
                if args.verbose:
                    print(f"  ⚠️  {folder.name}: sem identity.json")
                continue

            try:
                data = json.loads(ip.read_text(encoding="utf-8"))
                lin = data.get("lineage")
                if lin is None:
                    stats["no_lineage"] += 1
                    stats["attention"].append((folder.name, "sem lineage"))
                    if args.verbose:
                        print(f"  ❌ {folder.name}: sem lineage")
                elif lin.get("cls_version") == "1.1":
                    stats["v11"] += 1
                    if args.verbose:
                        print(f"  ✅ {folder.name}: V1.1")
                elif lin.get("cls_version") == "1.0":
                    stats["v10"] += 1
                    stats["attention"].append((folder.name, "V1.0 — precisa upgrade"))
                    if args.verbose:
                        print(f"  🔄 {folder.name}: V1.0 (precisa upgrade)")
                else:
                    stats["errors"] += 1
                    stats["attention"].append((folder.name, f"cls_version desconhecida: {lin.get('cls_version')}"))
            except Exception as e:
                stats["errors"] += 1
                stats["attention"].append((folder.name, f"erro: {e}"))
                if args.verbose:
                    print(f"  ❌ {folder.name}: {e}")

        print()
        print("━" * 52)
        print("  CLS AUDIT REPORT — AXIS-NIDDHI V5.2.1")
        print("━" * 52)
        print(f"  CSL root          : {csl_root}")
        print(f"  Total entries     : {stats['total']}")
        print(f"  ✅ CLS V1.1       : {stats['v11']}")
        print(f"  🔄 CLS V1.0       : {stats['v10']}")
        print(f"  ❌ Sem lineage    : {stats['no_lineage']}")
        print(f"  ⚠️  Sem identity   : {stats['no_identity']}")
        print(f"  💥 Erros          : {stats['errors']}")
        print("━" * 52)
        needs_attention = len(stats["attention"])
        if needs_attention == 0:
            print(f"  ✅ CLS V1.1 ativo em todas as {stats['total']} entries.")
        else:
            print(f"  ⚠️  {needs_attention} entries precisam de atenção:")
            for pdpn, reason in stats["attention"]:
                print(f"     {pdpn}: {reason}")
        print("━" * 52)
        print()

    elif args.cmd == "upgrade":
        result = upgrade_lineage_v10_to_v11(Path(args.identity_path))
        print(f"Resultado: {result}")

    else:
        parser.print_help()
