# src/transformers/link_resolver.py
# V2.6.0 — FF-015 Universal Localhost Resolver
# [FF-015] 2026-03-09 — PATCH: LINK_PATTERN generalized to match ANY
#   http://localhost/<any-prefix>/<...>/<slug>
#   Previously only matched /brasileirinho/ prefix, breaking links from
#   /beng_feb2026/ and any other WP installation paths in the CSL.

import re
import logging
from typing import Dict
from urllib.parse import urlsplit, unquote

logger = logging.getLogger("Script13.LinkResolver")

# V2.4.0 original (too narrow):
#   r'href=["\'"]http://localhost/brasileirinho/([^"\']+)["\'"]'
#
# V2.6.0 — captures any localhost/127.0.0.1 href (http/https).
LINK_PATTERN = re.compile(
    r'''href=(["'])(https?://(?:localhost|127\.0\.0\.1)[^"']*)\1''',
    re.IGNORECASE
)

LOCAL_WP_PREFIXES = {"beng_feb2026", "brasileirinho"}

def _normalize_wp_path(path: str) -> str:
    """
    Remove local WordPress mount prefixes from localhost URLs.
    Example:
      /beng_feb2026/forums/topic/x/ -> /forums/topic/x/
    """
    parts = [p for p in path.split("/") if p]
    if parts and parts[0].lower() in LOCAL_WP_PREFIXES:
        parts = parts[1:]
    return "/" + "/".join(parts) if parts else "/"

def _slug_candidates(raw_slug: str):
    """
    Generate slug variants to handle legacy percent/UTF-8 encodings
    present in WordPress-exported localhost links.
    """
    base = raw_slug.strip("/").lower()
    if not base:
        return []

    candidates = []
    seen = set()

    def add(value: str):
        if value and value not in seen:
            seen.add(value)
            candidates.append(value)

    add(base)
    add(base.replace("%", ""))

    decoded = unquote(base)
    add(decoded)

    # Example: taṇha -> tae1b987ha (legacy slug encoding seen in corpus).
    hex_mixed = []
    for ch in decoded:
        if ord(ch) < 128:
            hex_mixed.append(ch)
        else:
            hex_mixed.extend(f"{b:02x}" for b in ch.encode("utf-8"))
    add("".join(hex_mixed))

    return candidates

class LinkResolver:
    def __init__(self, slug_map: Dict[str, str]):
        """
        Args:
            slug_map: Dict[pdpn -> slug] from slug_map.json
                      Injected by build.py. Never built internally.
        """
        # Invert: slug -> pdpn (for link resolution)
        self._slug_to_pdpn: Dict[str, str] = {v: k for k, v in slug_map.items()}
        logger.info(f"🔗 LinkResolver v2.6.0 initialized: {len(self._slug_to_pdpn)} slugs")

    def resolve_links(self, html_content: str, current_pdpn: str) -> str:
        if not html_content:
            return ""

        def replacer(match):
            quote = match.group(1)
            url = match.group(2)
            parsed = urlsplit(url)
            normalized_path = _normalize_wp_path(parsed.path or "/")
            path_parts = [p for p in normalized_path.split("/") if p]
            raw_slug = path_parts[-1].rstrip('/') if path_parts else ""

            for candidate in _slug_candidates(raw_slug):
                target_pdpn = self._slug_to_pdpn.get(candidate)
                if target_pdpn:
                    return f'href={quote}../../pages/{target_pdpn}/index.html{quote}'

            # Not in slug_map — keep link external, but never leak localhost.
            logger.debug(f"Link not resolved: '{raw_slug}' in {current_pdpn}")
            public_url = f"https://puredhamma.net{normalized_path}"
            if parsed.query:
                public_url += f"?{parsed.query}"
            if parsed.fragment:
                public_url += f"#{parsed.fragment}"
            return f'href={quote}{public_url}{quote}'

        return LINK_PATTERN.sub(replacer, html_content)
