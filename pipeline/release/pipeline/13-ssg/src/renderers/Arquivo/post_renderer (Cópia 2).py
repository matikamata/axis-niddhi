# pipeline/13-ssg/src/renderers/post_renderer.py
import logging
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape


from models import Post, Section
from transformers.link_resolver import LinkResolver
from transformers.asset_mapper import process_assets
import re

# SPRINT 8: Glossary & Consumer-Side Logic
def resolve_csl_root(start_path: Path) -> Path:
    """Climbs up to find the '09-csl' directory."""
    current = start_path.absolute()
    while current.parent != current:
        if current.name == "09-csl":
            return current
        if (current / "09-csl").exists():
            return current / "09-csl"
        current = current.parent
    return start_path # Fallback

def load_glossary(csl_root: Path) -> Dict[str, Any]:
    """Loads the core glossary and returns a dict mapping lower-case terms to definitions."""
    glossary_path = csl_root / "meta" / "glossary.core.json"
    if not glossary_path.exists():
        logger.warning(f"⚠️ Glossary not found at {glossary_path}")
        return {}
    
    try:
        with open(glossary_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Normalize keys to lowercase for case-insensitive matching
        # structure: "Term": { "term": "Term", "definition": "..." }
        glossary = {}
        for key, val in raw_data.items():
            glossary[key.lower()] = val
            
        return glossary
    except Exception as e:
        logger.error(f"❌ Failed to parse glossary: {e}")
        return {}

def inject_marginalia(html_content: str, glossary: Dict[str, Any]) -> str:
    """
    Scans HTML content and wraps known glossary terms in <em class="term-highlight">.
    Aviods replacing text inside HTML tags.
    """
    if not glossary:
        return html_content

    # Sort terms by length (descending) to match "Abhidhamma Pitaka" before "Abhidhamma"
    # Filter out very short terms (<= 2 chars) to avoid noise if any exist
    sorted_terms = sorted([k for k in glossary.keys() if len(k) > 2], key=len, reverse=True)
    
    if not sorted_terms:
        return html_content

    # Escape terms
    escaped_terms = [re.escape(t) for t in sorted_terms]
    
    # Chunking the regex to avoid "regular expression code size limit exceeded" if glossary is huge
    # But for ~2000 terms it might be okay. If it fails, we'll need a different approach.
    # Python re engine limit is quite high.
    pattern_str = '|'.join(escaped_terms)
    
    # 1. Match HTML Tags (Group 1)
    # 2. Match Glossary Terms (Group 2) - using word boundaries
    try:
        combined_pattern = re.compile(r'(<[^>]+>)|(\b(?:' + pattern_str + r')\b)', re.IGNORECASE)
    except re.error:
        # Fallback if pattern is too large: do nothing for now or log error
        logger.error("Glossary regex pattern too large.")
        return html_content

    def replacer(match):
        tag = match.group(1)
        term = match.group(2)
        
        if tag:
            return tag # Return tags unchanged
        
        if term:
            key = term.lower()
            entry = glossary.get(key)
            if entry:
                # Extract definition text for title attribute
                definition = entry.get('definition', '')
                # simplistic stripping of tags
                clean_def = re.sub('<[^<]+?>', '', definition).replace('"', '&quot;')
                return f'<em class="term-highlight" data-term="{key}" title="{clean_def}">{term}</em>'
            
        return term 

    return combined_pattern.sub(replacer, html_content)


logger = logging.getLogger("Script13.PostRenderer")

def calculate_reading_time(text: str) -> int:
    """Estimates reading time in minutes (200 wpm)."""
    word_count = len(text.split())
    minutes = max(1, round(word_count / 200))
    return minutes

def infer_level(section_code: str) -> str:
    """Heuristic for cognitive level based on section."""
    intro_sections = ['TL', 'BD']
    advanced_sections = ['AB', 'PS', 'QD']
    if section_code in intro_sections: return 'intro'
    elif section_code in advanced_sections: return 'advanced'
    return 'intermediate'

def get_safe_harbor(current_section_code: str) -> Optional[Dict[str, str]]:
    """Determines a safe harbor link for advanced content."""
    if current_section_code in ['TL', 'BD']: return None
    return {
        "code": "TL",
        "title": "Three Levels of Practice",
        "url": "../index.html#section-TL"
    }

def render_posts(
    posts: List[Post],
    output_dir: Path,
    template_hash: str,
    cache_file: Path,
    nav_tree: List[Section],
    slug_index: LinkResolver,
    asset_map: Dict[str, str],
    glossary: Dict[str, Any] = None
) -> Dict[str, int]:
    
    stats = {"rebuilt": 0, "skipped": 0, "errors": 0}
    
    # 1. Load Cache
    build_state = {}
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f: build_state = json.load(f)
        except Exception: pass

    # 2. Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent.parent.parent / "templates"),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("post.html")
    resolver = slug_index

    # 3. Build Section Map for Context
    section_map: Dict[str, List[Post]] = {s.code: s.posts for s in nav_tree}
    section_titles: Dict[str, str] = {s.code: s.title for s in nav_tree}

    # 4. Iterate and Render
    for post in posts:
        try:
            # A. Calculate Hash
            content_hash = post.artifacts['en-US'].integrity_sha256 or "nohash"
            composite_hash = hashlib.sha256(f"{content_hash}|{template_hash}".encode()).hexdigest()
            
            if build_state.get(post.pdpn) == composite_hash:
                stats["skipped"] += 1
                continue

            # B. Prepare Directory
            post_dir = output_dir / post.pdpn
            post_dir.mkdir(parents=True, exist_ok=True)
            
            # C. Read Content & Metadata
            with open(post.artifacts['en-US'].file_path, 'r', encoding='utf-8') as f:
                raw_en = f.read()
            
            import re
            clean_text = re.sub('<[^<]+?>', '', raw_en)
            reading_time = calculate_reading_time(clean_text)
            level = infer_level(post.section_code)

            html_en = resolver.resolve_links(raw_en, post.pdpn)
            html_en = process_assets(html_en, post.pdpn, asset_map)
            
            # SPRINT 8: Marginalia Injection
            if glossary:
                html_en = inject_marginalia(html_en, glossary)

            html_pt = ""
            if post.has_pt:
                with open(post.artifacts['pt-BR'].file_path, 'r', encoding='utf-8') as f:
                    raw_pt = f.read()
                html_pt = resolver.resolve_links(raw_pt, post.pdpn)
                html_pt = process_assets(html_pt, post.pdpn, asset_map)

                if glossary:
                    html_pt = inject_marginalia(html_pt, glossary)

            # SPRINT 3: Digestibility
            section_code = post.section_code
            section_title = section_titles.get(section_code, section_code)
            
            prev_post = None
            next_post = None
            position_index = 0
            section_total = 0
            
            if section_code in section_map:
                section_posts = section_map[section_code]
                section_total = len(section_posts)
                try:
                    idx = next(i for i, p in enumerate(section_posts) if p.pdpn == post.pdpn)
                    position_index = idx + 1
                    
                    if idx > 0: prev_post = section_posts[idx - 1]
                    if idx < len(section_posts) - 1: next_post = section_posts[idx + 1]
                except StopIteration: pass

            # SPRINT 3: Digestibility
            suggestion = None
            if level == 'advanced':
                suggestion = get_safe_harbor(post.section_code)

            # E. Render
            output_html = template.render(
                post=post,
                content_en=html_en,
                content_pt=html_pt,
                nav_tree=nav_tree,
                relative_root="../",
                current_section_code=section_code,
                current_section_title=section_title,
                prev_post=prev_post,
                next_post=next_post,
                position_index=position_index,
                section_total=section_total,
                meta_reading_time=reading_time,
                meta_level=level,
                suggestion_block=suggestion
            )

            # F. Write
            with open(post_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(output_html)

            build_state[post.pdpn] = composite_hash
            stats["rebuilt"] += 1

        except Exception as e:
            logger.error(f"❌ Error rendering {post.pdpn}: {e}")
            stats["errors"] += 1

    # 5. Save Cache
    cache_file.parent.mkdir(exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump(build_state, f, indent=2)

    return stats
