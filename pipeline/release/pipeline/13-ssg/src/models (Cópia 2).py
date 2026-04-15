# src/models.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, List

@dataclass(frozen=True)
class ArtifactMetadata:
    """Represents the metadata for a specific language version (en-US or pt-BR)."""
    status: str                  # e.g., "canonical", "derived"
    integrity_sha256: Optional[str] # The hash from identity.json (Source of Truth)
    file_path: Path              # Absolute path to the content.html file

@dataclass(frozen=True)
class Post:
    """
    The internal representation of a CSL Post.
    Immutable (frozen) to prevent accidental mutation during the pipeline.
    """
    # Identity
    pdpn: str                    # Primary Key: TL.BB.003
    section_code: str            # Grouping: TL
    findex: str                  # Sorting: 0396
    slug_root: str               # URL generation: law-of-attraction...

    # Content
    titles: Dict[str, str]       # {'en': '...', 'pt': '...'}
    artifacts: Dict[str, ArtifactMetadata] # Keyed by 'en-US', 'pt-BR'

    # System
    source_dir: Path             # Origin directory in CSL

    @property
    def has_pt(self) -> bool:
        """Backward-compat alias for has_pt_content. Never remove — used throughout."""
        return self.has_pt_content

    @property
    def has_pt_content(self) -> bool:
        """True when pt-BR content.html exists on disk (loaded as artifact)."""
        return 'pt-BR' in self.artifacts

    @property
    def has_pt_title(self) -> bool:
        """True when titles['pt'] is present, even without body translation.
        [FF-011] 2026-03-09 — permite mostrar titulo PT em index/cards/SEO
        sem depender de has_pt_content.
        """
        pt = self.titles.get('pt', '')
        return bool(pt and str(pt).strip())


@dataclass
class Section:
    code: str
    title: str
    posts: List[Post]

    def __post_init__(self):
        # Ensure posts are sorted by findex upon creation/modification
        self.posts.sort(key=lambda p: p.findex)
