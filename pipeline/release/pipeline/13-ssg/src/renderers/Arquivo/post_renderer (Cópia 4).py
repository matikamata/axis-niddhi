# pipeline/13-ssg/src/renderers/post_renderer.py
import logging
import hashlib
import json
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bs4 import BeautifulSoup, NavigableString
import re

from models import Post, Section
from transformers.link_resolver import LinkResolver
from transformers.asset_mapper import process_assets

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
        if node.parent.name in ['script', 'style', 'a']:
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
            span_tag = soup.new_tag('span', **{'class': 'pali-term'})
            span_tag.string = term
            new_soup.append(span_tag)
            last_end = end
        if last_end < len(text):
            new_soup.append(NavigableString(text[last_end:]))
        node.replace_with(new_soup)
    return str(soup)

def render_post(post: Post, template_env: Environment, link_resolver: LinkResolver, asset_map: Dict[str, str], glossary: Dict[str, Any]) -> str:
    # 1. Resolve links internos
    content = link_resolver.resolve(post.content)
    
    # 2. Resolve assets (imagens)
    content = process_assets(content, asset_map)
    
    # 3. INJETA O GLOSSÁRIO (Pronúncia)
    content = inject_marginalia(content, glossary)
    
    template = template_env.get_template("post.html")
    return template.render(post=post, content=content)
