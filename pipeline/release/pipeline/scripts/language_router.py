# src/transformers/language_router.py
from typing import Dict, Optional
from models import Post

def get_language_alternates(post: Post) -> Dict[str, Optional[str]]:
    """
    Determines the link for the language switcher.
    Returns a dict: {'en': 'link_or_none', 'pt': 'link_or_none'}
    """
    # In our flat structure, the URL is the same for the post folder.
    # The language switching happens via query param or JS, 
    # BUT since this is a static site, we usually render separate files 
    # OR we use JS to toggle visibility.
    
    # ARCHITECTURE DECISION:
    # The prompt implies "Bilingual Navigation".
    # If we render ONE index.html per post, that HTML must contain BOTH languages
    # (hidden/shown by CSS/JS) OR we render index.html (EN) and index_pt.html (PT).
    
    # Given "IPFS" and "Clean URLs", the standard approach is:
    # 1. Single HTML with both contents, toggled by JS (Best for IPFS/Offline).
    # 2. Separate folders /en/ and /pt/ (Complex linking).
    
    # We will assume Strategy 1: Single HTML file containing both content blocks.
    # The "Router" here just confirms availability.
    
    return {
        "en": "available",
        "pt": "available" if post.has_pt else None
    }
