#!/usr/bin/env python3
# pipeline/13-ssg/build.py
"""
💎 AXIS-NIDDHI ENGINE — Script 13 (SSG) v3.1
===========================================================
Nome:     Static Site Generator — The Architect
Versão:   3.1.0 — Showcase Edition
Data:     2026-04-14
Autores:  Aloka + Claude Sonnet 4.6

MUDANÇAS v3.0 vs v2.3:
  ★ slug_map.json gerado INTERNAMENTE a partir da CSL (zero dep. de Script 15)
  ★ asset_map.json OPCIONAL — warning, nunca abort
  ★ Paths via config.py — zero hardcode de /media/ ou /home/
  ★ SOVEREIGN ABORT apenas para erros estruturais reais (CSL ausente, templates ausentes)
  ★ nav_builder recebe pipeline_root explicitamente
  ★ Template hash injetado no cache para detecção de mudanças
  ★ Idempotente — seguro de rodar múltiplas vezes

SOVEREIGN ABORT (apenas):
  1. CSL não existe ou está vazia
  2. Templates ausentes (post.html ou index.html)
  3. Import error dos módulos src/

NUNCA ABORTA por:
  - asset_map.json ausente (warning + passthrough)
  - glossary_config.json ausente (warning + dict vazio)
  - MasterPDPN_Sections.csv ausente (usa mapa canônico embutido)
  - slug_map.json ausente (gerado internamente)
"""

import sys
import time
import json
import logging
import os
import shutil
import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import quote, unquote

# ── Import path: src/ relativo ao build.py ─────────────────────────────────
_HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(_HERE / "src"))

try:
    # Config canônico do pipeline
    sys.path.insert(0, str(_HERE.parent / "scripts"))
    sys.path.insert(0, str(_HERE.parent / "scripts" / "core"))
    from config import (
        DIR_09_CSL      as CSL_DIR_CFG,
        DIR_13_SSG      as SSG_DIR_CFG,
        DIR_14_ASSETS   as ASSETS_DIR_CFG,
        METADATA_DIR    as METADATA_DIR_CFG,
        GLOSSARY_JSON   as GLOSSARY_JSON_CFG,
        LOG_DIR         as LOG_DIR_CFG,
    )
    _CONFIG_LOADED = True
except ImportError:
    _CONFIG_LOADED = False

from loaders.csl_loader       import load_csl_repository
from models                   import Post, Section
from renderers.post_renderer  import render_posts
from renderers.index_renderer import render_indices
from transformers.nav_builder import build_navigation_tree
from transformers.link_resolver import LinkResolver

# ── Paths ───────────────────────────────────────────────────────────────────
if _CONFIG_LOADED:
    CSL_DIR      = Path(CSL_DIR_CFG)
    OUTPUT_DIR   = Path(SSG_DIR_CFG)
    ASSETS_DIR   = Path(ASSETS_DIR_CFG)
    METADATA_DIR = Path(METADATA_DIR_CFG)
    GLOSSARY_JSON= Path(GLOSSARY_JSON_CFG)
    LOG_DIR      = Path(LOG_DIR_CFG)
else:
    # Fallback: derivar da posição do build.py (/beng/pipeline/13-ssg/build.py)
    _PIPELINE = _HERE.parent
    CSL_DIR      = _PIPELINE / "09-csl"
    OUTPUT_DIR   = _PIPELINE / "13-static-site"
    ASSETS_DIR   = _PIPELINE / "14-assets"
    METADATA_DIR = _PIPELINE / "metadata"
    GLOSSARY_JSON= METADATA_DIR / "glossary_config.json"
    LOG_DIR      = _PIPELINE / "logs"

PIPELINE_ROOT  = CSL_DIR.parent          # /beng/pipeline
TEMPLATES_DIR  = _HERE / "templates"
STATIC_DIR     = _HERE / "static"
CACHE_FILE     = _HERE / "cache" / "build_state.json"
ASSET_MAP_PRIMARY_FILE = ASSETS_DIR / "asset_map.json"
ASSET_MAP_FALLBACK_FILE = METADATA_DIR / "asset_map.json"
SLUG_MAP_FILE  = METADATA_DIR / "slug_map.json"   # gerado internamente se ausente
GLOSSARY_CSV   = METADATA_DIR / "Glossario_v5.csv"  # fonte canônica: termo_en,termo_pt (sem cabeçalho)

ENGINE_VERSION = "3.0.2-S14-S15-C1-C3"  # PATCH S15: constante centralizada
CF_PAGES_MAX_BYTES = int(os.environ.get("BENG_PAGES_MAX_FILE_BYTES", str(25 * 1024 * 1024)))
EXTERNAL_UPLOADS_BASE = os.environ.get(
    "BENG_EXTERNAL_UPLOADS_BASE_URL",
    "https://puredhamma.net/wp-content/uploads",
).rstrip("/")
LOCAL_WP_PREFIXES = {"beng_feb2026", "brasileirinho"}

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / f"S13_build_{_ts}.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("S13")


# ══════════════════════════════════════════════════════════════════════════════
# UTILITÁRIOS
# ══════════════════════════════════════════════════════════════════════════════

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _calculate_template_hash(template_dir: Path) -> str:
    """Hash SHA-256 combinado de todos os templates + renderers.
    Qualquer mudança em template HTML ou em post_renderer.py → rebuild total."""
    hasher = hashlib.sha256()
    if not template_dir.exists():
        return "000000"
    # Templates HTML
    for p in sorted(template_dir.glob("**/*.html")):
        try:
            hasher.update(p.read_bytes())
        except Exception as e:
            logger.warning(f"⚠️  Não foi possível hashear {p.name}: {e}")
    # [FF-016] Python renderers — mudança no renderer invalida cache
    renderers_dir = template_dir.parent / "src" / "renderers"
    if renderers_dir.exists():
        for p in sorted(renderers_dir.glob("*.py")):
            try:
                hasher.update(p.read_bytes())
            except Exception as e:
                logger.warning(f"⚠️  Não foi possível hashear {p.name}: {e}")
    # [2026-04-23] Python transformers also affect rendered post output
    transformers_dir = template_dir.parent / "src" / "transformers"
    if transformers_dir.exists():
        for p in sorted(transformers_dir.glob("*.py")):
            try:
                hasher.update(p.read_bytes())
            except Exception as e:
                logger.warning(f"⚠️  Não foi possível hashear {p.name}: {e}")
    return hasher.hexdigest()


def _build_slug_map(posts: List[Post]) -> Dict[str, str]:
    """
    Gera slug_map { pdpn → slug_root } diretamente da CSL carregada.
    Persiste em METADATA_DIR/slug_map.json para auditoria.
    Zero dependência de Script 15.
    """
    slug_map = {p.pdpn: p.slug_root for p in posts}

    SLUG_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    SLUG_MAP_FILE.write_text(
        json.dumps(slug_map, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    logger.info(f"🔗 slug_map.json gerado internamente: {len(slug_map)} entradas → {SLUG_MAP_FILE}")
    return slug_map


def _load_asset_map() -> Dict[str, str]:
    """
    Carrega asset_map.json se existir. OPCIONAL — nunca aborta.
    Retorna dict vazio se ausente (asset_mapper opera em passthrough).
    """
    asset_map_path: Optional[Path] = None

    if ASSET_MAP_PRIMARY_FILE.exists():
        asset_map_path = ASSET_MAP_PRIMARY_FILE
        logger.info(f"📦 asset_map.json usando caminho primário: {ASSET_MAP_PRIMARY_FILE}")
    elif ASSET_MAP_FALLBACK_FILE.exists():
        asset_map_path = ASSET_MAP_FALLBACK_FILE
        logger.warning(
            f"⚠️  asset_map primário ausente ({ASSET_MAP_PRIMARY_FILE}) — "
            f"usando fallback: {ASSET_MAP_FALLBACK_FILE}"
        )
    else:
        logger.warning(
            f"⚠️  asset_map.json ausente (primário: {ASSET_MAP_PRIMARY_FILE}; "
            f"fallback: {ASSET_MAP_FALLBACK_FILE}) — "
            "assets não serão reescritos (passthrough). "
            "[S14_ASSET_RESOLVER não executado / SD01 não gerou metadata]"
        )
        return {}

    try:
        data = json.loads(asset_map_path.read_text(encoding="utf-8"))
        logger.info(f"📦 asset_map.json carregado de {asset_map_path}: {len(data)} entradas.")
        return data
    except Exception as e:
        logger.warning(
            f"⚠️  Erro ao ler asset_map.json em {asset_map_path}: {e} — passthrough ativado."
        )
        return {}


def _copy_static_assets() -> None:
    """Copia static/ (css, js, assets) para o output."""
    if not STATIC_DIR.exists():
        logger.warning(f"⚠️  Pasta static/ não encontrada: {STATIC_DIR}")
        return
    shutil.copytree(STATIC_DIR, OUTPUT_DIR, dirs_exist_ok=True)
    logger.info(f"📦 Static assets copiados → {OUTPUT_DIR}")


def _copy_nana_static_artifacts() -> None:
    """
    Copia os artefatos estáticos JSON do NANA para o output do SSG.
    Fail-closed guard para rejeitar segredos.
    Não executa LLM, não faz chamadas API.
    """
    source_dir = PIPELINE_ROOT / "capsule" / "nana"
    target_dir = OUTPUT_DIR / "assets" / "nana"

    if not source_dir.exists():
        logger.info("📦 NANA capsule not found; skipping static NANA artifacts.")
        return

    json_files = list(source_dir.rglob("*.json"))
    if not json_files:
        logger.info("📦 NANA capsule found but no JSON artifacts present.")
        return

    forbidden_markers = [
        "GOOGLE_APPLICATION_CREDENTIALS",
        "gen-lang-client",
        "private_key",
        "BEGIN PRIVATE KEY",
        "api_key",
        "access_token",
        "refresh_token",
        "github_token",
        "deepl_key",
        "wp_password",
        "/home/",
        "/media/",
        "pipeline/scripts/private"
    ]
    
    ignore_names = {"readme.md", ".gitkeep"}
    ignore_dirs = {"__pycache__", "private", ".git"}
    
    copied = 0
    blocked = 0

    for f in json_files:
        if f.is_dir() or f.name.startswith("."):
            continue
            
        if f.suffix.lower() != ".json":
            continue
            
        if f.name.lower() in ignore_names:
            continue
            
        rel_path = f.relative_to(source_dir)
            
        if any(part in ignore_dirs or part.startswith(".") for part in rel_path.parts):
            continue
            
        try:
            raw = f.read_bytes()
            content = raw.decode("utf-8")
        except Exception as e:
            logger.warning(f"⚠️  Falha ao ler artefato NANA {f.name}: {e}")
            continue
            
        rel_path_str = rel_path.as_posix()
        has_forbidden = False
        for marker in forbidden_markers:
            if marker in rel_path_str or marker in content:
                logger.warning(f"🚨 blocked NANA artifact due forbidden marker '{marker}': {f.name}")
                has_forbidden = True
                blocked += 1
                break
                
        if has_forbidden:
            continue
            
        target_file = target_dir / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            target_file.write_bytes(raw)
            copied += 1
        except Exception as e:
            logger.warning(f"⚠️  Falha ao escrever artefato NANA {rel_path}: {e}")
            
    if copied > 0 or blocked > 0:
        logger.info(f"🧠 copied {copied} NANA static artifact(s).")
        if blocked > 0:
            logger.warning(f"🚨 {blocked} blocked due to forbidden markers.")


def _ensure_github_pages_markers() -> None:
    """Garantias mínimas para deploy estático em GitHub Pages backup."""
    marker = OUTPUT_DIR / ".nojekyll"
    marker.write_text("", encoding="utf-8")
    logger.info("🧷 GitHub Pages marker: .nojekyll")


def _generate_search_index(posts: List[Post]) -> None:
    """Gera search_index.json para busca offline.
    [FF-010] 2026-03-09 — fixes:
      - title keys corrigidos: 'en'/'pt' (nao 'en-US'/'pt-BR')
      - campo 'content' adicionado: excerpt 2kb do EN, sem scripts/styles/HTML
    """
    index = []
    for p in posts:
        # Extrair texto limpo do EN para busca full-text
        excerpt = ""
        artifact_en = p.artifacts.get("en-US")
        if artifact_en and artifact_en.file_path.exists():
            try:
                raw = artifact_en.file_path.read_text(encoding="utf-8")
                raw = re.sub(r'<script.*?</script>', ' ', raw, flags=re.S)
                raw = re.sub(r'<style.*?</style>', ' ', raw, flags=re.S)
                excerpt = re.sub(r'<[^>]+>', ' ', raw)
                excerpt = re.sub(r'\s+', ' ', excerpt).strip()[:2000]
            except Exception as e:
                logger.warning(f"  excerpt falhou para {p.pdpn}: {e}")

        # Never leak localhost URLs in generated search excerpts.
        def _to_public_url(match):
            path = match.group(1) or "/"
            parts = [p for p in path.split("/") if p]
            if parts and parts[0].lower() in LOCAL_WP_PREFIXES:
                parts = parts[1:]
            normalized_path = "/" + "/".join(parts) if parts else "/"
            return f"https://puredhamma.net{normalized_path}"

        excerpt = re.sub(
            r"https?://(?:localhost|127\.0\.0\.1)(/[^\s\"'<>]*)?",
            _to_public_url,
            excerpt,
            flags=re.IGNORECASE,
        )

        index.append({
            "pdpn":     p.pdpn,
            "findex":   p.findex,
            "section":  p.section_code,
            "slug":     p.slug_root,
            "title_en": p.titles.get('en', p.pdpn),    # FF-010: era 'en-US'
            "title_pt": p.titles.get('pt', p.pdpn),    # FF-010: era 'pt-BR'
            "content":  excerpt,                         # FF-010: novo campo
            "has_pt":   p.has_pt,
            "url":      f"pages/{p.pdpn}/index.html",
        })
    out = OUTPUT_DIR / "search_index.json"
    out.write_text(json.dumps(index, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    logger.info(f"🔍 search_index.json: {len(index)} posts indexados.")


def _generate_nav_index(nav_tree: List[Section], posts: List[Post]) -> None:
    """Serializa a NavTree como index.json para uso por JS/IPFS."""
    data = {
        "generated_at":  _utc_now(),
        "total_posts":   len(posts),
        "schema":        "axis-niddhi-v3",
        "sections": [
            {
                "code":       s.code,
                "title":      s.title,
                "post_count": len(s.posts),
                "posts": [
                    {
                        "pdpn":     p.pdpn,
                        "findex":   p.findex,
                        "slug":     p.slug_root,
                        "title_en": p.titles.get('en', p.pdpn),  # FF-010
                        "title_pt": p.titles.get('pt', p.pdpn),  # FF-010
                        "has_pt":   p.has_pt,
                        "url":      f"pages/{p.pdpn}/index.html",
                    }
                    for p in s.posts
                ],
            }
            for s in nav_tree
        ],
    }
    out = OUTPUT_DIR / "index.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"🗂️  index.json gerado: {len(nav_tree)} seções.")


def _inject_build_id_into_sw() -> None:
    """
    Calcula tree_sha256 do output e injeta BUILD_ID no sw.js.
    BUILD_ID = tree_sha256[:16] — identidade criptográfica da árvore.
    Mesma árvore = mesmo BUILD_ID, em qualquer máquina.
    """
    sw_src  = STATIC_DIR / "js" / "sw.js"
    sw_dest = OUTPUT_DIR / "sw.js"

    if not sw_src.exists():
        logger.warning("⚠️  sw.js não encontrado em static/js/ — Service Worker pulado.")
        return

    # Hash de todo o output — determinístico:
    # - Exclui sw.js (seria circular), build_meta.json, index.json (generated_at muda)
    # - Exclui logs/ (timestamp no nome do arquivo), *.py (build.py no mesmo dir)
    # - Exclui cache/ (build_state interno) e *.tmp (writes atômicos em curso)
    # - Inclui relative path de cada arquivo (detecta renames) [M2.3]
    _HASH_EXCLUDE_NAMES = {"sw.js", "build_meta.json", "index.json", "CERTIFICATE.json"}
    _HASH_EXCLUDE_EXTS  = {".py", ".tmp", ".log"}
    _HASH_EXCLUDE_DIRS  = {"logs", "cache", "__pycache__", ".venv", "src"}

    hasher = hashlib.sha256()
    for f in sorted(OUTPUT_DIR.rglob("*")):
        if not f.is_file():
            continue
        # Excluir por nome
        if f.name in _HASH_EXCLUDE_NAMES:
            continue
        # Excluir por extensão
        if f.suffix in _HASH_EXCLUDE_EXTS:
            continue
        # Excluir por pasta pai
        if any(part in _HASH_EXCLUDE_DIRS for part in f.parts):
            continue
        try:
            rel = str(f.relative_to(OUTPUT_DIR)).encode()
            hasher.update(rel)
            hasher.update(f.read_bytes())
        except Exception:
            pass

    tree_sha256 = hasher.hexdigest()
    build_id    = tree_sha256[:16]  # BUILD_ID == identidade da árvore
    sw_content = sw_src.read_text(encoding="utf-8")
    sw_content = sw_content.replace("__BUILD_ID__", build_id)
    sw_dest.write_text(sw_content, encoding="utf-8")
    logger.info(f"⚙️  Service Worker: BUILD_ID={build_id} (tree={tree_sha256[:12]}...)")
    return build_id, tree_sha256  # BUILD_ID + tree_sha256 para build_meta


def _load_glossary_csv() -> Dict[str, Any]:
    """
    Carrega Glossario_v5.csv como glossário para inject_marginalia().

    Formato do CSV: termo_en,termo_pt  (sem cabeçalho, sem aspas obrigatórias)
    Saída: { "termo_en_normalizado": {"term": "termo_en", "definition": "termo_pt"} }

    A estrutura de valor {"term": ..., "definition": ...} é a esperada por
    inject_marginalia() em post_renderer.py.

    Nunca aborta — retorna {} se arquivo ausente ou inválido.
    """
    import csv
    import unicodedata as _ud

    if not GLOSSARY_CSV.exists():
        logger.warning(f"⚠️  Glossário CSV não encontrado: {GLOSSARY_CSV}")
        return {}

    glossary: Dict[str, Any] = {}
    try:
        with open(GLOSSARY_CSV, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    continue
                term_en = row[0].strip()
                term_pt = row[1].strip()
                if not term_en:
                    continue
                key = _ud.normalize("NFC", term_en.lower())
                glossary[key] = {"term": term_en, "definition": term_pt}
        logger.info(f"📖 Glossário carregado: {len(glossary)} termos ← {GLOSSARY_CSV.name}")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao carregar glossário CSV: {e}")
        return {}

    return glossary


def _copy_audio_files(csl_root: Path) -> Dict[str, str]:
    """
    Copia MP3s de CSL/meta/pronunciation/ para output/assets/audio/en-US/ incrementalmente.
    Path canônico: assets/audio/en-US/ — idêntico ao BrasileirinhoHD.
    Usa mtime para skip. Nunca aborta se diretório ausente.
    Arquivos > limite do Pages são externalizados para EXTERNAL_UPLOADS_BASE.
    Retorna mapa {filename.mp3: external_url} para reescrever referências.
    """
    audio_src = csl_root / "meta" / "pronunciation"
    audio_dst = OUTPUT_DIR / "assets" / "audio" / "en-US"

    if not audio_src.exists():
        logger.warning("⚠️  pronunciation/ não encontrado — áudio não copiado.")
        return {}

    audio_dst.mkdir(parents=True, exist_ok=True)
    copied = skipped = oversized = removed_stale = 0
    externalized: Dict[str, str] = {}

    for mp3 in sorted(audio_src.glob("*.mp3")):
        try:
            size_bytes = mp3.stat().st_size
        except OSError as e:
            logger.warning(f"⚠️  Audio inválido (stat falhou) {mp3.name}: {e}")
            continue

        if size_bytes > CF_PAGES_MAX_BYTES:
            externalized[mp3.name] = f"{EXTERNAL_UPLOADS_BASE}/{quote(mp3.name, safe='')}"
            oversized += 1
            stale = audio_dst / mp3.name
            if stale.exists():
                try:
                    stale.unlink()
                    removed_stale += 1
                except OSError as e:
                    logger.warning(f"⚠️  Falha removendo oversized antigo {stale.name}: {e}")
            continue

        target = audio_dst / mp3.name
        if not target.exists() or mp3.stat().st_mtime > target.stat().st_mtime:
            target.write_bytes(mp3.read_bytes())
            copied += 1
        else:
            skipped += 1

    logger.info(
        "🎵 Audio: "
        f"{copied} copiados | {skipped} sem alteração | "
        f"{oversized} externalizados (> {CF_PAGES_MAX_BYTES / (1024 * 1024):.1f} MiB) | "
        f"{removed_stale} removidos do output"
    )
    if externalized:
        logger.info(f"🌐 Audio externalizado base: {EXTERNAL_UPLOADS_BASE} ({len(externalized)} arquivos)")
    return externalized


def _rewrite_externalized_audio_references(external_audio: Dict[str, str]) -> None:
    """
    Reescreve referências locais de áudio para URL externa quando o arquivo
    foi externalizado por tamanho.
    """
    if not external_audio:
        return

    html_files = sorted((OUTPUT_DIR / "pages").rglob("index.html"))
    if not html_files:
        return

    prefixes = [
        "../../assets/audio/en-US/",
        "../assets/audio/en-US/",
        "assets/audio/en-US/",
        "/assets/audio/en-US/",
    ]
    updated_files = 0
    replacements = 0

    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8")
        original = text

        for filename, external_url in external_audio.items():
            encoded = quote(filename, safe="")
            candidates = {filename, encoded}
            for prefix in prefixes:
                for candidate in candidates:
                    local_ref = f"{prefix}{candidate}"
                    if local_ref in text:
                        text = text.replace(local_ref, external_url)
                        replacements += 1

        if text != original:
            html_file.write_text(text, encoding="utf-8")
            updated_files += 1

    logger.info(
        f"🔁 Audio refs externalizados em HTML: {replacements} substituições em {updated_files} páginas."
    )


def _rewrite_missing_local_audio_references() -> None:
    """
    Reescreve referências locais de áudio que apontam para arquivos ausentes
    no output para a URL externa canônica.
    """
    html_files = sorted((OUTPUT_DIR / "pages").rglob("index.html"))
    if not html_files:
        return

    audio_dst = OUTPUT_DIR / "assets" / "audio" / "en-US"
    pattern = re.compile(
        r'(?:\.\./){1,2}assets/audio/en-US/([^"\'<>\s?#]+)|'
        r'assets/audio/en-US/([^"\'<>\s?#]+)|'
        r'/assets/audio/en-US/([^"\'<>\s?#]+)'
    )

    updated_files = 0
    replacements = 0

    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8")
        original = text

        def repl(match):
            nonlocal replacements
            filename_token = next((g for g in match.groups() if g), "")
            filename = unquote(filename_token)
            if not filename:
                return match.group(0)

            local_file = audio_dst / filename
            if local_file.exists():
                return match.group(0)

            replacements += 1
            return f"{EXTERNAL_UPLOADS_BASE}/{quote(filename, safe='')}"

        text = pattern.sub(repl, text)

        if text != original:
            html_file.write_text(text, encoding="utf-8")
            updated_files += 1

    if replacements:
        logger.info(
            f"🔁 Audio refs ausentes externalizados: {replacements} substituições em {updated_files} páginas."
        )


def _rewrite_missing_local_image_references() -> None:
    """
    Reescreve referências locais de imagem ausentes no output para URL externa
    canônica. Evita placeholders quebrados por divergências de histórico WP.
    """
    html_files = sorted((OUTPUT_DIR / "pages").rglob("index.html"))
    if not html_files:
        return

    image_dst = OUTPUT_DIR / "assets" / "images"
    pattern = re.compile(
        r'(?:\.\./){1,2}assets/images/([^"\'<>\s?#]+)|'
        r'assets/images/([^"\'<>\s?#]+)|'
        r'/assets/images/([^"\'<>\s?#]+)'
    )

    updated_files = 0
    replacements = 0

    for html_file in html_files:
        text = html_file.read_text(encoding="utf-8")
        original = text

        def repl(match):
            nonlocal replacements
            filename_token = next((g for g in match.groups() if g), "")
            filename = unquote(filename_token)
            if not filename:
                return match.group(0)

            local_file = image_dst / filename
            if local_file.exists():
                return match.group(0)

            replacements += 1
            return f"{EXTERNAL_UPLOADS_BASE}/{quote(filename, safe='')}"

        text = pattern.sub(repl, text)

        if text != original:
            html_file.write_text(text, encoding="utf-8")
            updated_files += 1

    if replacements:
        logger.info(
            f"🔁 Imagens ausentes externalizadas: {replacements} substituições em {updated_files} páginas."
        )


def _generate_pronunciation_manifest(
    csl_root: Path,
    glossary: Dict[str, Any],
    external_audio: Optional[Dict[str, str]] = None,
) -> None:
    """
    Gera pronunciation_manifest.json: { termo → "assets/audio/en-US/arquivo.mp3" }
    Path canônico: assets/audio/en-US/ — idêntico ao BrasileirinhoHD.
    Verifica existência física no output (não na CSL) — inclui MP3s locais
    e fallback externo para arquivos externalizados.
    Nunca aborta se glossário ou diretório ausente.
    """
    audio_dst = OUTPUT_DIR / "assets" / "audio" / "en-US"
    manifest: Dict[str, str] = {}
    external_audio = external_audio or {}

    if (not audio_dst.exists() and not external_audio) or not glossary:
        (OUTPUT_DIR / "pronunciation_manifest.json").write_text(
            json.dumps({}, indent=2), encoding="utf-8"
        )
        logger.warning("⚠️  pronunciation_manifest.json vazio (sem áudio ou glossário ausente).")
        return

    # Índice de MP3s disponíveis no output (stem lowercase → nome real)
    available: Dict[str, str] = {
        f.stem.lower(): f.name
        for f in audio_dst.glob("*.mp3")
    }
    external_available: Dict[str, str] = {
        Path(filename).stem.lower(): external_url
        for filename, external_url in external_audio.items()
    }

    for term in glossary:
        # Match direto: dhamma → dhamma.mp3
        fname = available.get(term.lower())
        if fname:
            manifest[term] = f"assets/audio/en-US/{fname}"
            continue
        external = external_available.get(term.lower())
        if external:
            manifest[term] = external
            continue
        # Fallback NFKD: ā → a, ṭ → t etc.
        slug = unicodedata.normalize("NFKD", term).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
        fname = available.get(slug)
        if fname:
            manifest[term] = f"assets/audio/en-US/{fname}"
            continue
        external = external_available.get(slug)
        if external:
            manifest[term] = external

    out = OUTPUT_DIR / "pronunciation_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"🔊 pronunciation_manifest.json: {len(manifest)} termos com áudio.")


def _atomic_write(path: Path, content: str) -> None:
    """
    Write atômico: escreve em arquivo .tmp e renomeia.
    Elimina risco de corrupção por crash/kill entre abertura e fechamento.
    PATCH S15 — ISO Guardian Hardening.
    """
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)  # atômico no mesmo filesystem
    except Exception as e:
        logger.warning(f"⚠️  write atômico falhou para {path.name}: {e} — fallback direto")
        try:
            path.write_text(content, encoding="utf-8")
        except Exception:
            pass
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def _generate_build_meta(build_id: str, tree_sha256: str, elapsed: float, stats: dict) -> None:
    """
    Gera build_meta.json no output — rastreabilidade para ISO Guardian.
    Contém: BUILD_ID, engine version, timestamp, estatísticas do build.
    PATCH S15 — ISO Guardian Hardening.
    """
    meta = {
        "build_id":      build_id,
        "tree_sha256":   tree_sha256,
        "engine":        ENGINE_VERSION,
        "generated_at":  _utc_now(),
        "elapsed_s":     round(elapsed, 2),
        "posts_total":   stats.get("rebuilt", 0) + stats.get("skipped", 0),
        "posts_rebuilt": stats.get("rebuilt", 0),
        "posts_skipped": stats.get("skipped", 0),
        "errors":        stats.get("errors", 0),
    }
    out = OUTPUT_DIR / "build_meta.json"
    out.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"📋 build_meta.json → engine={ENGINE_VERSION} build_id={build_id[:12]}...")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Script 13 SSG")
    parser.add_argument("--clean", action="store_true", help="Limpa cache antes do build")
    parser.add_argument("--rebuild", action="store_true", help="Alias para --clean")
    args = parser.parse_args()
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if args.clean or args.rebuild:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
            logger.info("🧹 Cache limpo (build_state.json removido)")

    start = time.time()
    logger.info("=" * 70)
    logger.info("💎 AXIS-NIDDHI ENGINE — Script 13 v3.1")
    logger.info(f"   CSL:      {CSL_DIR}")
    logger.info(f"   Output:   {OUTPUT_DIR}")
    logger.info(f"   Config:   {'config.py' if _CONFIG_LOADED else 'fallback (config.py não encontrado)'}")
    logger.info("=" * 70)

    # ── SOVEREIGN ABORT 1: CSL ausente ─────────────────────────────────────
    if not CSL_DIR.exists():
        logger.critical(f"❌ SOVEREIGN ABORT: CSL não encontrada em {CSL_DIR}")
        sys.exit(1)

    # ── SOVEREIGN ABORT 2: Templates ausentes ──────────────────────────────
    for required_tpl in ["post.html", "index.html", "base.html"]:
        if not (TEMPLATES_DIR / required_tpl).exists():
            logger.critical(f"❌ SOVEREIGN ABORT: Template obrigatório ausente: {required_tpl}")
            sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. CARREGAR CSL ────────────────────────────────────────────────────
    logger.info("▶ Fase 1/8: Carregando CSL...")
    posts = load_csl_repository(CSL_DIR)
    if not posts:
        logger.critical("❌ SOVEREIGN ABORT: CSL vazia — nenhum post válido encontrado.")
        sys.exit(1)
    logger.info(f"   ✅ {len(posts)} posts carregados.")

    # ── 2. SLUG MAP (interno) ──────────────────────────────────────────────
    logger.info("▶ Fase 2/8: Gerando slug_map internamente...")
    slug_map = _build_slug_map(posts)

    # ── 3. ÁRVORE DE NAVEGAÇÃO ─────────────────────────────────────────────
    logger.info("▶ Fase 3/8: Construindo NavTree...")
    nav_tree = build_navigation_tree(posts, PIPELINE_ROOT)

    # ── 4. RESOLVEDORES ────────────────────────────────────────────────────
    logger.info("▶ Fase 4/8: Inicializando resolvedores...")
    slug_resolver = LinkResolver(slug_map)
    asset_map     = _load_asset_map()   # opcional — nunca aborta
    glossary      = _load_glossary_csv()  # carrega Glossario_v5.csv — nunca aborta

    # ── 5. RENDERIZAR POSTS (INCREMENTAL) ──────────────────────────────────
    logger.info("▶ Fase 5/8: Renderizando posts (build incremental)...")
    template_hash = _calculate_template_hash(TEMPLATES_DIR)
    asset_map_signature = hashlib.sha256(
        json.dumps(asset_map, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:12]
    template_hash = hashlib.sha256(
        f"{template_hash}:{asset_map_signature}".encode("utf-8")
    ).hexdigest()
    logger.info(
        f"   Template hash: {template_hash[:12]}... "
        f"(asset_map={asset_map_signature})"
    )

    # Detectar mudança de template (força rebuild total)
    prev_template_hash = ""
    if CACHE_FILE.exists():
        try:
            cache_data = json.loads(CACHE_FILE.read_text())
            prev_template_hash = cache_data.get("_template_hash", "")
        except Exception:
            pass

    if prev_template_hash != template_hash:
        logger.info("🎨 Templates alterados → rebuild total forçado.")
        CACHE_FILE.write_text("{}", encoding="utf-8")  # Limpa cache

    stats = render_posts(
        posts=posts,
        output_dir=OUTPUT_DIR,
        templates_dir=TEMPLATES_DIR,
        template_hash=template_hash,
        cache_file=CACHE_FILE,
        nav_tree=nav_tree,
        slug_resolver=slug_resolver,
        asset_map=asset_map,
        glossary=glossary,
    )

    # Persistir template_hash no cache — write atômico (PATCH S15)
    if CACHE_FILE.exists():
        try:
            cache_data = json.loads(CACHE_FILE.read_text())
            cache_data["_template_hash"] = template_hash
            _atomic_write(CACHE_FILE, json.dumps(cache_data, indent=2))
        except Exception:
            pass

    logger.info(
        f"   📊 Posts: rebuilt={stats['rebuilt']} | "
        f"skipped={stats['skipped']} | errors={stats['errors']}"
    )

    # ── 6. INDEX HTML + JSON ───────────────────────────────────────────────
    logger.info("▶ Fase 6/8: Gerando índices...")
    render_indices(nav_tree, OUTPUT_DIR, TEMPLATES_DIR)
    _generate_nav_index(nav_tree, posts)

    # ── 7. ASSETS + SEARCH INDEX + AUDIO PIPELINE ────────────────────────────
    logger.info("▶ Fase 7/8: Copiando assets estáticos e áudio...")
    _copy_static_assets()
    _copy_nana_static_artifacts()
    _ensure_github_pages_markers()
    _generate_search_index(posts)
    external_audio = _copy_audio_files(CSL_DIR)
    _rewrite_externalized_audio_references(external_audio)
    _rewrite_missing_local_audio_references()
    _rewrite_missing_local_image_references()
    _generate_pronunciation_manifest(CSL_DIR, glossary, external_audio)

    # ── 8. SERVICE WORKER + BUILD META (hardened — ÚLTIMO) ──────────────────
    logger.info("▶ Fase 8/8: Service Worker + Build Meta...")
    build_id, tree_sha256 = _inject_build_id_into_sw() or ("unknown", "unknown")
    _generate_build_meta(build_id, tree_sha256, time.time() - start, stats)

    # ── SUMÁRIO ────────────────────────────────────────────────────────────
    elapsed = time.time() - start
    total   = stats["rebuilt"] + stats["skipped"]
    done_pt = sum(1 for p in posts if p.has_pt)

    logger.info("=" * 70)
    logger.info("✨ BUILD COMPLETO")
    logger.info(f"   Posts total:     {total}")
    logger.info(f"   Posts PT-BR:     {done_pt} / {len(posts)}")
    logger.info(f"   Rebuilt:         {stats['rebuilt']}")
    logger.info(f"   Skipped (cache): {stats['skipped']}")
    logger.info(f"   Erros:           {stats['errors']}")
    logger.info(f"   Tempo:           {elapsed:.2f}s")
    logger.info(f"   Output:          {OUTPUT_DIR}")
    logger.info(f"   asset_map:       {'✅ carregado' if asset_map else '⚠️  passthrough'}")
    logger.info(f"   glossary:        {'✅ ' + str(len(glossary)) + ' termos' if glossary else '⚠️  vazio'}")
    logger.info(f"   build_id:        {build_id}")
    logger.info(f"   engine:          {ENGINE_VERSION}")
    logger.info("=" * 70)
    logger.info("▶ Para visualizar:")
    logger.info(f"   cd {OUTPUT_DIR} && python3 -m http.server 8080")
    logger.info(f"   Abrir: http://localhost:8080")
    logger.info("=" * 70)

    if stats["errors"] > 0:
        sys.exit(2)  # Código de saída não-zero para CI/automação


if __name__ == "__main__":
    main()
