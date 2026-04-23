# pipeline/13-ssg/src/transformers/asset_mapper.py
import logging
import re
from typing import Dict

logger = logging.getLogger("Script13.AssetMapper")
LOCAL_WP_PREFIXES = {"beng_feb2026", "brasileirinho"}

def process_assets(html_content: str, pdpn: str, asset_map: Dict[str, str]) -> str:
    """
    Scans for localhost URLs and replaces them with relative CAS paths.
    
    Args:
        html_content: The raw HTML of the post.
        pdpn: The ID of the post (for logging context).
        asset_map: Dict mapping '/wp-content/uploads/...' -> 'assets/...' or absolute external URL
    
    Returns:
        The HTML with links rewritten to relative paths (../../assets/...) or external URLs.
    """
    if not html_content:
        return ""

    # Optimization: Skip if no local-hosted links are present
    if (
        "localhost" not in html_content
        and "127.0.0.1" not in html_content
        and "/wp-content/uploads/" not in html_content
    ):
        return html_content

    replacements = 0
    
    # Iterate through the map and replace occurrences.
    # NOTE: asset_map keys are usually path-only (e.g. /wp-content/uploads/x.png).
    # We replace localhost absolute URLs first, then true path-only references.
    for original_url, web_path in asset_map.items():
        # All posts are rendered at pages/PDPN/index.html (depth 2 from site root).
        # Local asset targets become ../../assets/...
        # Absolute targets (externalized oversized artifacts) must stay absolute.
        target_path = web_path
        if not re.match(r"^(?:https?:)?//", web_path):
            target_path = f"../../{web_path.lstrip('/')}"

        if original_url.startswith("/"):
            escaped_original = re.escape(original_url)
            localhost_pattern = re.compile(
                rf"https?://(?:localhost|127\.0\.0\.1)(?:/[^\s\"'<>]*)?{escaped_original}"
            )
            html_content, count = localhost_pattern.subn(target_path, html_content)
            replacements += count

            # Handle path-only references (e.g. src="/wp-content/...") without
            # corrupting absolute localhost URLs that include extra path prefixes.
            for prefix in ['"', "'", "(", "="]:
                source = f"{prefix}{original_url}"
                target = f"{prefix}{target_path}"
                if source in html_content:
                    html_content = html_content.replace(source, target)
                    replacements += 1
        elif original_url in html_content:
            html_content = html_content.replace(original_url, target_path)
            replacements += 1

    # Final safety net: never leak localhost URLs in release HTML.
    if "localhost" in html_content or "127.0.0.1" in html_content:
        localhost_pattern = re.compile(
            r"https?://(?:localhost|127\.0\.0\.1)(/[^\s\"'<>]*)?",
            re.IGNORECASE
        )

        def _to_public(match):
            path = match.group(1) or "/"
            parts = [p for p in path.split("/") if p]
            if parts and parts[0].lower() in LOCAL_WP_PREFIXES:
                parts = parts[1:]
            normalized_path = "/" + "/".join(parts) if parts else "/"
            return f"https://puredhamma.net{normalized_path}"

        html_content, count = localhost_pattern.subn(_to_public, html_content)
        replacements += count

    return html_content
