#!/usr/bin/env python3
"""
Audit CSL identity metadata for suspicious PT title language contamination.

Read-only by design:
- reads pipeline/09-csl/*/meta/identity.json
- never writes to CSL
- never calls DeepL or translation services
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MARKERS = [
    " il ",
    " lo ",
    " gli ",
    " della ",
    " del ",
    " delle ",
    " degli ",
    " nell",
    " sull",
    " alla ",
    " al ",
]


def default_csl_root() -> Path:
    return Path(__file__).resolve().parents[3] / "pipeline" / "09-csl"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON is not an object")
    return data


def audit(csl_root: Path) -> tuple[int, int, list[tuple[str, Path, str, list[str]]]]:
    if not csl_root.exists():
        raise FileNotFoundError(f"CSL root does not exist: {csl_root}")
    if not csl_root.is_dir():
        raise NotADirectoryError(f"CSL root is not a directory: {csl_root}")

    identity_paths = sorted(csl_root.glob("*/meta/identity.json"))
    if not identity_paths:
        raise FileNotFoundError(f"No identity.json files found under: {csl_root}")

    checked = 0
    null_pt_titles = 0
    hits: list[tuple[str, Path, str, list[str]]] = []

    for identity_path in identity_paths:
        checked += 1
        data = load_json(identity_path)

        identity = data.get("identity", {})
        titles = data.get("titles", {})
        pdpn = identity.get("pdpn") or identity_path.parent.parent.name

        pt_title = titles.get("pt") if isinstance(titles, dict) else None
        if pt_title is None:
            null_pt_titles += 1
            continue

        title = str(pt_title)
        low_title = f" {title.lower()} "
        matched = [marker.strip() for marker in MARKERS if marker in low_title]

        if matched:
            hits.append((str(pdpn), identity_path, title, matched))

    return checked, null_pt_titles, hits


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only audit for suspicious Italian markers in CSL titles.pt fields."
    )
    parser.add_argument(
        "--csl-root",
        type=Path,
        default=default_csl_root(),
        help="Path to pipeline/09-csl (default: repository pipeline/09-csl)",
    )
    args = parser.parse_args()

    try:
        checked, null_pt_titles, hits = audit(args.csl_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"checked={checked}")
    print(f"null_pt_titles={null_pt_titles}")
    print(f"hits={len(hits)}")

    for pdpn, path, title, markers in hits:
        print(f"{pdpn} | {path} | {title} | {', '.join(markers)}")

    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
