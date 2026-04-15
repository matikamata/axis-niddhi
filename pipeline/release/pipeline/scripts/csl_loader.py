# src/loaders/csl_loader.py
import logging
from pathlib import Path
from typing import List
from .identity_loader import load_identity
from models import Post

logger = logging.getLogger("Script13.CSL")

def load_csl_repository(csl_root: Path) -> List[Post]:
    """
    Scans the CSL root directory for valid Post structures.
    Enforces Read-Only access and rejects malformed structures.
    """
    valid_posts: List[Post] = []
    skipped_count = 0

    if not csl_root.exists():
        logger.critical(f"CSL Root not found: {csl_root}")
        return []

    logger.info(f"📂 Scanning CSL at: {csl_root}")

    # Iterate over top-level directories (e.g., TL.BB.003)
    for item in sorted(csl_root.iterdir()):
        if not item.is_dir():
            continue
        
        if item.is_symlink():
            logger.warning(f"⛔ SKIPPED: Symlink directory detected: {item.name}")
            skipped_count += 1
            continue

        # Check for identity.json
        identity_path = item / "meta" / "identity.json"
        if not identity_path.exists():
            # Not a valid post folder (maybe a system folder?), skip silently or log debug
            continue

        # Attempt to load
        post = load_identity(identity_path, item)
        
        if post:
            valid_posts.append(post)
        else:
            skipped_count += 1

    logger.info(f"✅ Loaded {len(valid_posts)} valid posts.")
    if skipped_count > 0:
        logger.warning(f"⚠️  Skipped {skipped_count} invalid or malformed entries.")

    return valid_posts
