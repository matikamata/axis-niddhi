# pipeline/13-ssg/src/transformers/asset_mapper.py
import logging
from typing import Dict

logger = logging.getLogger("Script13.AssetMapper")

def process_assets(html_content: str, pdpn: str, asset_map: Dict[str, str]) -> str:
    """
    Scans for localhost URLs and replaces them with relative CAS paths.
    
    Args:
        html_content: The raw HTML of the post.
        pdpn: The ID of the post (for logging context).
        asset_map: Dict mapping 'http://localhost/...' -> 'assets/xx/hash.ext'
    
    Returns:
        The HTML with links rewritten to relative paths (../assets/...)
    """
    if not html_content:
        return ""

    # Optimization: Skip if no localhost links present
    if "localhost" not in html_content:
        return html_content

    replacements = 0
    
    # Iterate through the map and replace occurrences
    # Note: This is a simple string replacement. 
    # Since we are replacing full URLs, collision risk is minimal.
    for original_url, web_path in asset_map.items():
        if original_url in html_content:
            # Calculate relative path
            # All posts are at depth 1 (ROOT/PDPN/index.html)
            # So we go up one level (../) to reach ROOT, then into assets/
            relative_path = f"../{web_path}"
            
            html_content = html_content.replace(original_url, relative_path)
            replacements += 1

    # Log remaining localhost links (potential missing assets)
    if "localhost" in html_content:
        # We don't log every single one to avoid spam, but we note it.
        # logger.debug(f"⚠️  {pdpn}: Some localhost links remained after mapping.")
        pass

    return html_content
