# src/renderers/index_renderer.py
import logging
from pathlib import Path
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from models import Section

logger = logging.getLogger("Script13.IndexRenderer")

def render_indices(nav_tree: List[Section], output_dir: Path, templates_dir: Optional[Path] = None):
    """
    Renders the global index.html.
    Future expansion: could render section-specific indices (e.g. /TL/index.html).

    HARDENING PATCH (2026-03-06):
      ★ Adicionado: templates_dir — alinhado com call-site em build.py
        (que passa TEMPLATES_DIR explicitamente para relocatabilidade total).
      ★ Fallback: se templates_dir não fornecido, deriva do __file__ (comportamento anterior).
      ★ Lógica de renderização inalterada.
    """
    _default_templates = Path(__file__).parent.parent.parent / "templates"
    effective_templates = templates_dir if templates_dir is not None else _default_templates

    env = Environment(
        loader=FileSystemLoader(effective_templates),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("index.html")

    try:
        output_html = template.render(
            nav_tree=nav_tree,
            relative_root="./",  # Root is depth 0
            title="Brasileirinho - Dhamma Preservation"
        )

        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(output_html)

        logger.info("✅ Main Index rendered.")

    except Exception as e:
        logger.error(f"❌ Error rendering Main Index: {e}")
