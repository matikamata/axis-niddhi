import logging
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from models import Post, Section
from ..transformers.link_resolver import LinkResolver
from ..transformers.asset_mapper import process_assets

logger = logging.getLogger("Script13.PostRenderer")

def render_posts(
    posts: List[Post],
    output_dir: Path,
    template_hash: str,
    cache_file: Path,
    nav_tree: List[Section],
    slug_index: LinkResolver,
    asset_map: Dict[str, str]
) -> Dict[str, int]:
    
    stats = {"rebuilt": 0, "skipped": 0, "errors": 0}
    
    # 1. Load Cache
    build_state = {}
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                build_state = json.load(f)
        except Exception:
            logger.warning("⚠️ Cache file corrupted. Starting fresh.")

    # 2. Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent.parent.parent / "templates"),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("post.html")
    resolver = slug_index

    # 3. Build Navigation Maps
    section_map = {sec.code: sec.posts for sec in nav_tree}
    section_titles = {sec.code: sec.title for sec in nav_tree}

    # 4. Iterate and Render
    for post in posts:
        try:
            content_hash = post.artifacts['en-US'].integrity_sha256 or "nohash"
            composite_hash = hashlib.sha256(f"{content_hash}|{template_hash}".encode()).hexdigest()
            
            if build_state.get(post.pdpn) == composite_hash:
                stats["skipped"] += 1
                continue

            post_dir = output_dir / post.pdpn
            post_dir.mkdir(parents=True, exist_ok=True)
            
            # Contexto de Navegação (Breadcrumbs & Pathways)
            section_code = post.section_code
            section_title = section_titles.get(section_code, section_code)
            prev_post = None
            next_post = None
            
            if section_code in section_map:
                section_posts = section_map[section_code]
                try:
                    idx = next(i for i, p in enumerate(section_posts) if p.pdpn == post.pdpn)
                    if idx > 0:
                        prev_p = section_posts[idx - 1]
                        prev_post = {"title_en": prev_p.titles.get('en'), "title_pt": prev_p.titles.get('pt'), "url": f"../{prev_p.pdpn}/index.html"}
                    if idx < len(section_posts) - 1:
                        next_p = section_posts[idx + 1]
                        next_post = {"title_en": next_p.titles.get('en'), "title_pt": next_p.titles.get('pt'), "url": f"../{next_p.pdpn}/index.html"}
                except StopIteration:
                    pass

            # Transform Content
            with open(post.artifacts['en-US'].file_path, 'r', encoding='utf-8') as f:
                html_en = process_assets(resolver.resolve_links(f.read(), post.pdpn), post.pdpn, asset_map)

            html_pt = ""
            if post.has_pt:
                with open(post.artifacts['pt-BR'].file_path, 'r', encoding='utf-8') as f:
                    html_pt = process_assets(resolver.resolve_links(f.read(), post.pdpn), post.pdpn, asset_map)

            # Render
            output_html = template.render(
                post=post,
                content_en=html_en,
                content_pt=html_pt,
                relative_root="../",
                current_section_code=section_code,
                current_section_title=section_title,
                prev_post=prev_post,
                next_post=next_post
            )

            with open(post_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(output_html)

            build_state[post.pdpn] = composite_hash
            stats["rebuilt"] += 1

        except Exception as e:
            logger.error(f"❌ Error rendering {post.pdpn}: {e}")
            stats["errors"] += 1

    with open(cache_file, 'w') as f:
        json.dump(build_state, f, indent=2)

    return stats
