# /beng-fut/pipeline/scripts/sp12_guardian/sp12_logic.py
"""
💎 BRASILEIRINHO ENGINE — SP12 Guardian Review Tool
====================================================
Versão:  V5.3.0 — AXIS-NIDDHI
Módulo:  sp12_logic.py — backend puro (sem UI)

Responsabilidades:
  · Carregar posts do CSL para revisão
  · Aplicar ações do Guardião (approve/edit/retranslate/note/skip)
  · Atualizar STATUS no Translation_Control_Center.csv
  · Integrar com CLS via cls_tools
  · Calcular world_map_status()
"""

import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Bootstrap path ────────────────────────────────────────────────
_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from config import DIR_09_CSL, METADATA_DIR
from pipeline_utils import atomic_write_json, get_utc_now

try:
    from cls_tools import append_translation_event, set_flag, get_lineage
    _CLS_OK = True
except ImportError:
    _CLS_OK = False

PDPN_RE    = re.compile(r'^[A-Z]{2}\.[A-Z]{2}\.\d{3}$')
TCC_FILE   = METADATA_DIR / "Translation_Control_Center.csv"
SECTIONS_F = METADATA_DIR / "MasterPDPN_Sections.csv"  # ou config

# ── STATUS state machine ───────────────────────────────────────────
VALID_STATUSES = ["pending", "translated", "reviewed", "approved"]


# ==============================================================================
# CARREGAMENTO
# ==============================================================================

def _detect_delimiter(path: Path) -> str:
    """Detecta o delimitador real do CSV (vírgula ou ponto-e-vírgula)."""
    try:
        first = path.read_text(encoding="utf-8").split("\n")[0]
        return ";" if first.count(";") > first.count(",") else ","
    except Exception:
        return ","


def _normalize_status(raw: str) -> str:
    """
    Normaliza status do TCC para o vocabulário interno do SP12.
    TCC legado usa DONE/PENDING — SP12 usa translated/pending/reviewed/approved.
    """
    mapping = {
        "DONE":     "translated",
        "PENDING":  "pending",
        "translated": "translated",
        "reviewed":   "reviewed",
        "approved":   "approved",
    }
    return mapping.get((raw or "").strip().upper(), "pending")


def load_tcc() -> list[dict]:
    """Carrega Translation_Control_Center.csv como lista de dicts."""
    if not TCC_FILE.exists():
        return []
    delim = _detect_delimiter(TCC_FILE)
    with open(TCC_FILE, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        rows = list(reader)
    # Normalizar STATUS para vocabulário SP12
    for row in rows:
        raw = row.get("STATUS") or row.get("Status") or ""
        row["STATUS"] = _normalize_status(raw)
    return rows


def save_tcc(rows: list[dict]) -> None:
    """Salva TCC de volta ao CSV preservando todas as colunas."""
    if not rows:
        return
    for row in rows:
        if "STATUS" not in row:
            row["STATUS"] = _infer_status(row)

    fieldnames = list(rows[0].keys())
    if "STATUS" not in fieldnames:
        fieldnames.append("STATUS")

    # Usar mesmo delimitador do arquivo original
    delim = _detect_delimiter(TCC_FILE) if TCC_FILE.exists() else ","
    tmp = TCC_FILE.with_suffix(".csv.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(TCC_FILE)


def _infer_status(row: dict) -> str:
    """
    Infere status SP12 a partir dos dados disponíveis.
    Prioridade: STATUS SP12 > Status TCC (DONE/PENDING) > presença de content.html PT
    """
    # Se já tem STATUS SP12 normalizado, usar
    sp12_status = row.get("STATUS", "")
    if sp12_status in ("translated", "reviewed", "approved"):
        return sp12_status

    # Mapear Status legado DONE/PENDING
    legacy = (row.get("Status") or row.get("status") or "").strip().upper()
    if legacy == "DONE":
        return "translated"

    # Fallback: verificar se content.html PT existe no disco
    pdpn = str(row.get("PD#PN", "")).strip()
    if PDPN_RE.match(pdpn):
        pt_html = DIR_09_CSL / pdpn / "source" / "pt-BR" / "content.html"
        if pt_html.exists() and pt_html.stat().st_size > 100:
            return "translated"
    return "pending"


def load_posts_for_review(status_filter: Optional[str] = None) -> list[dict]:
    """
    Retorna posts prontos para revisão.
    status_filter: None = todos | 'translated' | 'reviewed' | 'approved'
    Cada item: {pdpn, section, status, en_content, pt_content,
                en_title, pt_title, identity, identity_path}
    """
    tcc = load_tcc()
    posts = []

    for row in tcc:
        pdpn = str(row.get("PD#PN", "")).strip()
        if not PDPN_RE.match(pdpn):
            continue

        current_status = row.get("STATUS") or _infer_status(row)

        # Só mostrar posts que têm conteúdo PT
        pt_html = DIR_09_CSL / pdpn / "source" / "pt-BR" / "content.html"
        if not pt_html.exists() or pt_html.stat().st_size < 100:
            continue

        if status_filter and current_status != status_filter:
            continue

        identity_path = DIR_09_CSL / pdpn / "meta" / "identity.json"
        try:
            identity = json.loads(identity_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        en_html = DIR_09_CSL / pdpn / "source" / "en-US" / "content.html"

        posts.append({
            "pdpn":          pdpn,
            "section":       row.get("Section", ""),
            "status":        current_status,
            "en_content":    en_html.read_text(encoding="utf-8") if en_html.exists() else "(sem conteúdo EN)",
            "pt_content":    pt_html.read_text(encoding="utf-8"),
            "en_title":      identity.get("titles", {}).get("en", ""),
            "pt_title":      identity.get("titles", {}).get("pt", ""),
            "identity":      identity,
            "identity_path": identity_path,
            "tcc_row":       row,
        })

    return posts


# ==============================================================================
# AÇÕES DO GUARDIÃO
# ==============================================================================

def sha256_str(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _update_tcc_status(pdpn: str, new_status: str) -> None:
    """Atualiza STATUS de um post no TCC CSV."""
    rows = load_tcc()
    for row in rows:
        if str(row.get("PD#PN", "")).strip() == pdpn:
            row["STATUS"] = new_status
            break
    save_tcc(rows)


def action_approve(post: dict, reviewer_id: str = "guardian") -> dict:
    """
    Approve: STATUS → approved, CLS registra review_event.
    """
    pdpn          = post["pdpn"]
    identity_path = post["identity_path"]
    pt_content    = post["pt_content"]
    now           = get_utc_now()

    # CLS event
    if _CLS_OK:
        try:
            append_translation_event(
                identity_path=identity_path,
                event="approved",
                engine=f"SP12_v5.3_{reviewer_id}",
                lang="pt-BR",
                result_hash=sha256_str(pt_content),
                note=f"Aprovado por {reviewer_id}",
            )
        except Exception as e:
            return {"ok": False, "msg": f"CLS error: {e}"}

    _update_tcc_status(pdpn, "approved")
    return {"ok": True, "msg": f"{pdpn} aprovado por {reviewer_id}"}


def action_edit(post: dict, new_pt_content: str,
                new_pt_title: str, reviewer_id: str = "guardian",
                note: str = "") -> dict:
    """
    Edit: salva novo conteúdo PT, flags.manual_pt_edit=true,
          STATUS → reviewed, CLS registra edição.
    """
    pdpn          = post["pdpn"]
    identity_path = post["identity_path"]
    identity      = json.loads(identity_path.read_text(encoding="utf-8"))
    pt_html       = DIR_09_CSL / pdpn / "source" / "pt-BR" / "content.html"
    now           = get_utc_now()

    # Salvar content.html editado
    pt_html.write_text(new_pt_content, encoding="utf-8")

    # Atualizar título se mudou
    if new_pt_title and new_pt_title != identity.get("titles", {}).get("pt", ""):
        identity.setdefault("titles", {})["pt"] = new_pt_title
        identity["titles"]["pt_source"] = f"guardian_{reviewer_id}"
        identity["last_updated_utc"] = now
        atomic_write_json(identity_path, identity)

    # CLS
    if _CLS_OK:
        try:
            set_flag(identity_path, "manual_pt_edit", True)
            append_translation_event(
                identity_path=identity_path,
                event="edited",
                engine=f"SP12_v5.3_{reviewer_id}",
                lang="pt-BR",
                result_hash=sha256_str(new_pt_content),
                note=note or f"Editado manualmente por {reviewer_id}",
            )
        except Exception as e:
            return {"ok": False, "msg": f"CLS error: {e}"}

    _update_tcc_status(pdpn, "reviewed")
    return {"ok": True, "msg": f"{pdpn} editado e marcado como reviewed"}


def action_add_note(post: dict, note_text: str,
                    reviewer_id: str = "guardian") -> dict:
    """Add Note: registra nota no CLS sem alterar status."""
    if not note_text.strip():
        return {"ok": False, "msg": "Nota vazia"}
    if _CLS_OK:
        try:
            append_translation_event(
                identity_path=post["identity_path"],
                event="note_added",
                engine=f"SP12_v5.3_{reviewer_id}",
                lang="pt-BR",
                note=note_text,
            )
        except Exception as e:
            return {"ok": False, "msg": f"CLS error: {e}"}
    return {"ok": True, "msg": "Nota registrada no CLS"}


def action_fix_title_hash(post: dict) -> dict:
    """
    Fix SP11 gap: adiciona title_hash ao último evento title_translated
    no lineage.translations[], se ainda não tiver.
    """
    identity_path = post["identity_path"]
    pt_title = post.get("pt_title", "")
    if not pt_title:
        return {"ok": False, "msg": "Sem título PT para hashar"}

    try:
        data = json.loads(identity_path.read_text(encoding="utf-8"))
        lin = data.get("lineage", {})
        translations = lin.get("translations", [])
        changed = False
        for t in reversed(translations):
            if t.get("event") == "title_translated" and not t.get("result_hash"):
                t["result_hash"] = sha256_str(pt_title)
                changed = True
                break
        if changed:
            atomic_write_json(identity_path, data)
            return {"ok": True, "msg": f"title_hash adicionado: {sha256_str(pt_title)[:12]}..."}
        return {"ok": True, "msg": "title_hash já presente"}
    except Exception as e:
        return {"ok": False, "msg": str(e)}


# ==============================================================================
# WORLD MAP STATUS
# ==============================================================================

def world_map_status() -> list[dict]:
    """
    Retorna progresso de tradução/revisão por seção do PD#PN.
    Fonte: MasterPDPN_Sections.csv + TCC (campo Section) + CSL.

    O código da seção é o PRIMEIRO segmento do PDPN:
      TL.BB.003 → seção TL → "07 - Three Levels of Practice"
      AB.AA.000 → seção AB → "13 - Abhidhamma"
    """
    # Carregar mapa de seções: code → name
    # Fonte 1: MasterPDPN_Sections.csv (formato "Nome;CÓDIGO")
    section_map = {}
    if SECTIONS_F.exists():
        with open(SECTIONS_F, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ";" in line:
                    name, code = line.rsplit(";", 1)
                    section_map[code.strip()] = name.strip()

    # Fonte 2: TCC campo Section ("07 - Three Levels of Practice")
    # e PDPN para extrair o código
    tcc_by_pdpn = {}
    tcc_section_names = {}  # code → nome completo vindo do TCC
    for row in load_tcc():
        pdpn = str(row.get("PD#PN", "")).strip()
        if not PDPN_RE.match(pdpn):
            continue
        tcc_by_pdpn[pdpn] = _infer_status(row)
        sec_code = pdpn.split(".")[0]  # ← pos 0: TL, AB, PS, etc.
        section_name = row.get("Section", "").strip()
        if section_name and sec_code not in tcc_section_names:
            tcc_section_names[sec_code] = section_name

    # Varrer CSL
    section_stats: dict[str, dict] = {}

    for folder in sorted(DIR_09_CSL.iterdir()):
        if not folder.is_dir() or not PDPN_RE.match(folder.name):
            continue
        pdpn     = folder.name
        sec_code = pdpn.split(".")[0]  # ← pos 0, não pos 1

        if sec_code not in section_stats:
            # Nome: TCC > MasterSections > fallback código
            name = (tcc_section_names.get(sec_code)
                    or section_map.get(sec_code)
                    or sec_code)
            section_stats[sec_code] = {
                "code": sec_code,
                "name": name,
                "total": 0, "translated": 0,
                "reviewed": 0, "approved": 0,
            }

        s = section_stats[sec_code]
        s["total"] += 1

        status = tcc_by_pdpn.get(pdpn, "pending")
        if status in ("translated", "reviewed", "approved"):
            s["translated"] += 1
        if status in ("reviewed", "approved"):
            s["reviewed"] += 1
        if status == "approved":
            s["approved"] += 1

    result = []
    for sec in sorted(section_stats.values(), key=lambda x: x["code"]):
        total = sec["total"] or 1
        sec["translated_pct"] = round(sec["translated"] / total * 100)
        sec["reviewed_pct"]   = round(sec["reviewed"]   / total * 100)
        sec["approved_pct"]   = round(sec["approved"]   / total * 100)
        result.append(sec)

    return result


# ==============================================================================
# BOOTSTRAP STATUS (para inicializar coluna STATUS no TCC)
# ==============================================================================

def bootstrap_status_column() -> int:
    """
    Adiciona coluna STATUS ao TCC se não existir,
    inferindo o valor de cada post. Retorna nº de posts atualizados.
    """
    rows = load_tcc()
    updated = 0
    for row in rows:
        if not row.get("STATUS"):
            row["STATUS"] = _infer_status(row)
            updated += 1
    save_tcc(rows)
    return updated
