# src/renderers/index_renderer.py
import logging
from pathlib import Path
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models import Section

logger = logging.getLogger("Script13.IndexRenderer")

def render_indices(nav_tree: List[Section], output_dir: Path, templates_dir: Optional[Path] = None):
    """
    Renders the showcase entry points.
    1. index.html   <- templates/welcome.html (Discovery Landing - Root)
    2. archive.html <- templates/index.html   (Archive Library)
    """
    _default_templates = Path(__file__).parent.parent.parent / "templates"
    effective_templates = templates_dir if templates_dir is not None else _default_templates

    env = Environment(
        loader=FileSystemLoader(effective_templates),
        autoescape=select_autoescape(['html', 'xml'])
    )

    try:
        # 1. Render Discovery Landing as THE ROOT (index.html)
        welcome_tpl = env.get_template("welcome.html")
        welcome_html = welcome_tpl.render(
            relative_root="./",
            title="AXIS-NIDDHI - Discovery Entry"
        )
        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(welcome_html)
        logger.info("✅ Discovery Entry (index.html) rendered.")

        # 2. Render Archive Library (archive.html)
        archive_tpl = env.get_template("index.html")
        archive_html = archive_tpl.render(
            nav_tree=nav_tree,
            relative_root="./",
            title="AXIS-NIDDHI - Archive Library"
        )
        with open(output_dir / "archive.html", "w", encoding="utf-8") as f:
            f.write(archive_html)
        logger.info("✅ Archive Library (archive.html) rendered.")

    except Exception as e:
        logger.error(f"❌ Error rendering indices: {e}")
