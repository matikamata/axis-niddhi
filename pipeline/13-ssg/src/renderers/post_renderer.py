# pipeline/13-ssg/src/renderers/post_renderer.py
# V2.5.0 — AXIS-NIDDHI V5.4 Fix
# PATCH: template.render() agora passa todas as variáveis que post.html requer:
#   relative_root, content_en, content_pt, current_section_code,
#   current_section_title, position_index, section_total,
#   prev_post, next_post, meta_level, meta_reading_time, suggestion_block

import logging
import hashlib
import json
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bs4 import BeautifulSoup, NavigableString, Comment
import re

from models import Post, Section
from transformers.link_resolver import LinkResolver
from transformers.asset_mapper import process_assets

logger = logging.getLogger("Script13.PostRenderer")

# ── Helpers ─────────────────────────────────────────────────────────────────

def resolve_csl_root(start_path: Path) -> Path:
    current = start_path.resolve().absolute()
    while current.parent != current:
        if current.name == "09-csl":
            return current
        if (current / "09-csl").exists():
            return current / "09-csl"
        current = current.parent
    return start_path

def load_glossary(csl_root: Path) -> Dict[str, Any]:
    glossary_path = csl_root / "meta" / "glossary.core.json"
    if not glossary_path.exists():
        return {}
    with open(glossary_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def inject_marginalia(html_content: str, glossary: Dict[str, Any]) -> str:
    if not glossary:
        return html_content
    soup = BeautifulSoup(html_content, 'html.parser')
    sorted_terms = sorted(glossary.keys(), key=len, reverse=True)
    term_pattern = re.compile(
        r'\b(' + '|'.join(re.escape(term) for term in sorted_terms) + r')\b',
        re.IGNORECASE
    )
    text_nodes = soup.find_all(string=True)
    for node in text_nodes:
        if isinstance(node, Comment) or node.parent.name in ['script', 'style', 'a', '[document]']:
            continue
        text = str(node)
        if not term_pattern.search(text):
            continue
        new_soup = BeautifulSoup('<span></span>', 'html.parser').span
        last_end = 0
        for match in term_pattern.finditer(text):
            start, end = match.span()
            term = match.group(1)
            if start > last_end:
                new_soup.append(NavigableString(text[last_end:start]))
            # [PATCH-A 2026-03-09] term-highlight required by initPronunciation();
            # data-term normalizado para NFC — evita mismatch com chaves NFC do manifest.
            normalized_term = unicodedata.normalize('NFC', term.lower())
            span_tag = soup.new_tag('span', **{
                'class': 'pali-term term-highlight',
                'data-term': normalized_term
            })
            span_tag.string = term
            new_soup.append(span_tag)
            last_end = end
        if last_end < len(text):
            new_soup.append(NavigableString(text[last_end:]))
        node.replace_with(new_soup)
    return str(soup)


def extract_csl_tattoo(html_content: str) -> tuple:
    """
    [FF-017] Extrai o comentário canônico CSL do content.html.
    Retorna (tattoo_div, html_sem_comentario).

    Suporta dois formatos presentes no CSL:
      1) <!-- 💡 BRASILEIRINHO ENGINE - CANONICAL SOURCE ARTIFACT ... -->  (SG01)
      2) <!-- Canonical CSL Artifact ... -->                                (SP03)

    CRÍTICO: remove o comentário original ANTES de inject_marginalia —
    BS4 corrompe comentários injetando <span> dentro deles, tornando
    o conteúdo visível como texto no browser.
    """
    patterns = [
        r'<!--\s*💡\s*BRASILEIRINHO ENGINE\s*-\s*CANONICAL SOURCE ARTIFACT(.*?)-->',
        r'<!--\s*(Canonical CSL Artifact.*?)\s*-->',
    ]
    match = None
    for pattern in patterns:
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if match:
            break
    if not match:
        return '', html_content

    lines = [l.strip() for l in match.group(1).strip().splitlines() if l.strip()]
    rows = ''.join(f'<tr><td>{l}</td></tr>' for l in lines)
    tattoo_div = (
        f'<div class="csl-tattoo" aria-hidden="true">'
        f'<table>{rows}</table>'
        f'</div>'
    )
    # Remove the original comment from html to prevent BS4 corruption
    clean_html = html_content[:match.start()] + html_content[match.end():]
    return tattoo_div, clean_html.lstrip()

def _estimate_reading_time(html: str) -> int:
    """Rough reading time in minutes (200 wpm)."""
    text = re.sub(r'<[^>]+>', '', html)
    words = len(text.split())
    return max(1, round(words / 200))

def _classify_level(section_code: str) -> str:
    """Simple heuristic: AB, BA, QD = advanced; else intermediate."""
    advanced = {"AB", "BA", "QD", "PS"}
    return "advanced" if section_code in advanced else "intermediate"

# ── Section lookup helpers ────────────────────────────────────────────────────

def _build_section_map(nav_tree: List[Section]) -> Dict[str, Section]:
    """Returns {section_code: Section}."""
    return {s.code: s for s in nav_tree}

def _find_neighbours(post: Post, section: Optional[Section]):
    """Returns (prev_post, next_post) within the same section, or None."""
    if not section:
        return None, None
    posts = sorted(section.posts, key=lambda p: p.findex)
    idx = next((i for i, p in enumerate(posts) if p.pdpn == post.pdpn), None)
    if idx is None:
        return None, None
    prev_p = posts[idx - 1] if idx > 0 else None
    next_p = posts[idx + 1] if idx < len(posts) - 1 else None
    return prev_p, next_p

def modernize_iframes(html_content: str) -> str:
    """
    [FF-018] Modernizer for embedded videos (YouTube).
    - Injects modern 'allow' permissions.
    - Sets Referrer Policy per iframe.
    - Wraps in .video-container for responsive styling.
    """
    if "<iframe" not in html_content:
        return html_content

    soup = BeautifulSoup(html_content, 'html.parser')
    iframes = soup.find_all('iframe')

    for iframe in iframes:
        src = iframe.get('src', '')
        if 'youtube.com' in src or 'youtu.be' in src:
            # Standard YouTube permissions
            iframe['allow'] = (
                "accelerometer; autoplay; clipboard-write; encrypted-media; "
                "gyroscope; picture-in-picture; web-share"
            )
            iframe['allowfullscreen'] = "allowfullscreen"
            iframe['referrerpolicy'] = "strict-origin-when-cross-origin"

            # Wrap in container
            container = soup.new_tag('div', **{'class': 'video-container'})
            iframe.wrap(container)

    return str(soup)

# ── Core render function ──────────────────────────────────────────────────────

def render_post(
    post: Post,
    template_env: Environment,
    link_resolver: LinkResolver,
    asset_map: Dict[str, str],
    glossary: Dict[str, Any],
    nav_tree: Optional[List[Section]] = None,
) -> str:
    """
    Renders a single post to HTML, injecting ALL variables required by post.html:
      - relative_root       (../../ for pages/PDPN/index.html)
      - content_en          (resolved + asset-mapped EN HTML)
      - content_pt          (resolved + asset-mapped PT HTML, or "")
      - current_section_code / current_section_title
      - position_index / section_total
      - prev_post / next_post
      - meta_level / meta_reading_time
      - suggestion_block
    """

    # ── 1. EN content ─────────────────────────────────────────────────────
    artifact_en = post.artifacts.get("en-US")
    try:
        raw_en = artifact_en.file_path.read_text(encoding="utf-8") if artifact_en else ""
    except Exception as e:
        logger.error(f"❌ Falha ao ler EN content para {post.pdpn}: {e}")
        raw_en = ""

    # [FF-016 v3] Extract & remove CSL tattoo comment BEFORE any BS4 processing.
    # If comment absent (CSL rebuilt from scratch), generate tattoo from Post metadata.
    _tattoo, raw_en_clean = extract_csl_tattoo(raw_en)

    if not _tattoo:
        # Active injection — CSL may lack comment after full reset (Akasa/FF-016-v3)
        rows = ''.join(
            f'<tr><td>{k}</td><td>{v}</td></tr>'
            for k, v in [
                ('PD#PN',    post.pdpn),
                ('Fin-dex',  post.findex),
                ('Slug',     post.slug_root),
                ('Section',  post.section_code),
                ('Title EN', post.titles.get('en', '')),
            ]
        )
        _tattoo = (
            f'<div class="csl-tattoo" aria-hidden="true">'
            f'<table>{rows}</table>'
            f'</div>'
        )

    content_en = link_resolver.resolve_links(raw_en_clean, post.pdpn)
    content_en = process_assets(content_en, post.pdpn, asset_map)
    content_en = inject_marginalia(content_en, glossary)
    content_en = modernize_iframes(content_en)
    content_en = _tattoo + content_en

    # ── 2. PT content (if available) ──────────────────────────────────────
    content_pt = ""
    if post.has_pt:
        artifact_pt = post.artifacts.get("pt-BR")
        try:
            raw_pt = artifact_pt.file_path.read_text(encoding="utf-8") if artifact_pt else ""
        except Exception as e:
            logger.warning(f"⚠️  Falha ao ler PT content para {post.pdpn}: {e}")
            raw_pt = ""
        content_pt = link_resolver.resolve_links(raw_pt, post.pdpn)
        content_pt = process_assets(content_pt, post.pdpn, asset_map)
        content_pt = inject_marginalia(content_pt, glossary)
        content_pt = modernize_iframes(content_pt)

    # ── 3. Navigation context ─────────────────────────────────────────────
    section_map = _build_section_map(nav_tree) if nav_tree else {}
    section = section_map.get(post.section_code)

    current_section_code  = post.section_code
    current_section_title = section.title if section else post.section_code

    prev_post, next_post = _find_neighbours(post, section)

    position_index = 1
    section_total  = 1
    if section:
        posts_sorted = sorted(section.posts, key=lambda p: p.findex)
        idx = next((i for i, p in enumerate(posts_sorted) if p.pdpn == post.pdpn), 0)
        position_index = idx + 1
        section_total  = len(posts_sorted)

    # ── 4. Meta ───────────────────────────────────────────────────────────
    meta_level        = _classify_level(post.section_code)
    meta_reading_time = _estimate_reading_time(content_en)

    # ── 5. Suggestion block (only for advanced posts) ─────────────────────
    suggestion_block = None
    if meta_level == "advanced" and nav_tree:
        tl_section = section_map.get("TL")
        if tl_section and tl_section.posts:
            anchor = sorted(tl_section.posts, key=lambda p: p.findex)[0]
            suggestion_block = {
                "url":   f"../../pages/{anchor.pdpn}/index.html",
                "title": anchor.titles.get("en", "Three Levels of Practice"),
            }

    # ── 6. Relative root: pages/PDPN/index.html is 2 levels deep → ../../
    relative_root = "../../"

    # ── 7. Render ──────────────────────────────────────────────────────────
    template = template_env.get_template("post.html")
    return template.render(
        post                  = post,
        content_en            = content_en,
        content_pt            = content_pt,
        relative_root         = relative_root,
        current_section_code  = current_section_code,
        current_section_title = current_section_title,
        position_index        = position_index,
        section_total         = section_total,
        prev_post             = prev_post,
        next_post             = next_post,
        meta_level            = meta_level,
        meta_reading_time     = meta_reading_time,
        suggestion_block      = suggestion_block,
    )


# ── Batch renderer (called by build.py) ──────────────────────────────────────

def render_posts(
    posts: List[Post],
    output_dir: Path,
    templates_dir: Path,
    template_hash: str,
    cache_file: Path,
    nav_tree,
    slug_resolver: "LinkResolver",
    asset_map: Dict[str, str],
    glossary: Dict[str, Any],
) -> Dict[str, int]:
    """
    Renderiza todos os posts com build incremental via cache.
    slug_resolver: instância de LinkResolver já inicializada pelo build.py.
    Retorna stats: {rebuilt, skipped, errors}.
    """
    stats = {"rebuilt": 0, "skipped": 0, "errors": 0}

    # Carregar cache
    cache: Dict[str, str] = {}
    if cache_file.exists():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    csl_root = posts[0].source_dir.parent if posts else output_dir
    _glossary = load_glossary(csl_root) or glossary

    for post in posts:
        try:
            # Cache key: template_hash + sha256 do content.html EN
            artifact_en = post.artifacts.get("en-US")
            file_hash = hashlib.sha256(
                artifact_en.file_path.read_bytes()
            ).hexdigest()[:16] if artifact_en else "no-artifact"
            cache_key = f"{post.pdpn}:{template_hash[:8]}:{file_hash}"

            post_dir = output_dir / "pages" / post.pdpn
            out_file = post_dir / "index.html"

            if out_file.exists() and cache.get(post.pdpn) == cache_key:
                stats["skipped"] += 1
                continue

            post_dir.mkdir(parents=True, exist_ok=True)
            html = render_post(
                post          = post,
                template_env  = env,
                link_resolver = slug_resolver,
                asset_map     = asset_map,
                glossary      = _glossary or glossary,
                nav_tree      = nav_tree,
            )
            out_file.write_text(html, encoding="utf-8")

            cache[post.pdpn] = cache_key
            stats["rebuilt"] += 1

        except Exception as e:
            logger.error(f"❌ Erro ao renderizar {post.pdpn}: {e}")
            stats["errors"] += 1

    # Persistir cache
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as e:
        logger.warning(f"⚠️  Falha ao salvar cache: {e}")

    return stats
