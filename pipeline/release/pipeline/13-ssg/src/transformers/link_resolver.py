# src/transformers/link_resolver.py
# V2.5.0 — FF-015 Universal Localhost Resolver
# [FF-015] 2026-03-09 — PATCH: LINK_PATTERN generalized to match ANY
#   http://localhost/<any-prefix>/<...>/<slug>
#   Previously only matched /brasileirinho/ prefix, breaking links from
#   /beng_feb2026/ and any other WP installation paths in the CSL.

import re
import logging
from typing import Dict

logger = logging.getLogger("Script13.LinkResolver")

# V2.4.0 original (too narrow):
#   r'href=["\'"]http://localhost/brasileirinho/([^"\']+)["\'"]'
#
# V2.5.0 — matches any localhost path, any depth:
#   http://localhost/<anything>/<slug>/
LINK_PATTERN = re.compile(
    r'''href=["']http://localhost/[^"']+?/([^/"']+)/?["']''',
    re.IGNORECASE
)

class LinkResolver:
    def __init__(self, slug_map: Dict[str, str]):
        """
        Args:
            slug_map: Dict[pdpn -> slug] from slug_map.json
                      Injected by build.py. Never built internally.
        """
        # Invert: slug -> pdpn (for link resolution)
        self._slug_to_pdpn: Dict[str, str] = {v: k for k, v in slug_map.items()}
        logger.info(f"🔗 LinkResolver v2.5.0 initialized: {len(self._slug_to_pdpn)} slugs")

    def resolve_links(self, html_content: str, current_pdpn: str) -> str:
        if not html_content:
            return ""

        def replacer(match):
            original_url = match.group(0)
            # Last path segment = slug candidate
            # e.g. localhost/beng_feb2026/.../what-is-kamma.../  → what-is-kamma...
            raw_slug = match.group(1).rstrip('/')

            target_pdpn = self._slug_to_pdpn.get(raw_slug)

            if target_pdpn:
                return f'href="../../pages/{target_pdpn}/index.html"'
            else:
                # Not in slug_map — log and preserve (external / category link)
                logger.debug(f"Link not resolved: '{raw_slug}' in {current_pdpn}")
                return original_url

        return LINK_PATTERN.sub(replacer, html_content)
