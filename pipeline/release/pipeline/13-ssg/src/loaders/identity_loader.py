# src/loaders/identity_loader.py
import json
import logging
from pathlib import Path
from typing import Optional, Dict
from models import Post, ArtifactMetadata

logger = logging.getLogger("Script13.Loader")

REQUIRED_FIELDS = ["pdpn", "findex", "section_code", "slug_root"]

def load_identity(json_path: Path, post_dir: Path) -> Optional[Post]:
    """
    Parses identity.json and validates strict adherence to Schema V3.0.
    Returns None if validation fails.
    """
    try:
        if json_path.is_symlink():
            logger.error(f"⛔ REJECTED: Symlink detected at {json_path}")
            return None

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Schema Validation
        identity = data.get("identity")
        if not identity:
            logger.warning(f"⚠️  SKIPPED: Missing 'identity' block in {json_path}")
            return None

        for field in REQUIRED_FIELDS:
            if field not in identity or not identity[field]:
                logger.warning(f"⚠️  SKIPPED: Missing field '{field}' in {json_path}")
                return None

        # 2. Artifacts & Paths Resolution
        artifacts_data = data.get("artifacts", {})
        artifacts_map: Dict[str, ArtifactMetadata] = {}

        # Check en-US (Canonical) - MANDATORY
        en_path = post_dir / "source" / "en-US" / "content.html"
        if _validate_content_file(en_path):
            artifacts_map["en-US"] = ArtifactMetadata(
                status=artifacts_data.get("en-US", {}).get("status", "unknown"),
                integrity_sha256=artifacts_data.get("en-US", {}).get("integrity_sha256"),
                file_path=en_path
            )
        else:
            logger.error(f"❌ INVALID: Missing canonical content.html for {identity['pdpn']}")
            return None

        # Check pt-BR (Derived) - OPTIONAL
        pt_path = post_dir / "source" / "pt-BR" / "content.html"
        if _validate_content_file(pt_path):
            artifacts_map["pt-BR"] = ArtifactMetadata(
                status=artifacts_data.get("pt-BR", {}).get("status", "unknown"),
                integrity_sha256=artifacts_data.get("pt-BR", {}).get("integrity_sha256"),
                file_path=pt_path
            )

        # 3. Construct Immutable Post Object
        return Post(
            pdpn=identity["pdpn"],
            section_code=identity["section_code"],
            findex=identity["findex"],
            slug_root=identity["slug_root"],
            titles=data.get("titles", {}),
            artifacts=artifacts_map,
            source_dir=post_dir
        )

    except json.JSONDecodeError:
        logger.error(f"💥 CORRUPT: Invalid JSON in {json_path}")
        return None
    except Exception as e:
        logger.exception(f"💥 ERROR: Unexpected failure loading {json_path}")
        return None

def _validate_content_file(path: Path) -> bool:
    """Checks if file exists, is a file, and is not a symlink."""
    if path.exists() and path.is_file() and not path.is_symlink():
        return True
    return False
