#!/usr/bin/env python3
"""Read-only validator for the tracked CSL correction manifest."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = "review/csl-corrections/csl_metadata_corrections_manifest_v1.json"
REQUIRED_TOP_LEVEL = ("manifest_version", "corrections")
REQUIRED_CORRECTION_KEYS = ("flagfix", "pdpn", "file", "json_path", "new_value")
SUPPORTED_JSON_PATHS = ("titles.en", "titles.pt")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate tracked CSL metadata corrections against local identity.json files."
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help=f"Path to correction manifest JSON. Default: {DEFAULT_MANIFEST}",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used to resolve manifest and correction file paths. Default: cwd",
    )
    return parser.parse_args()


def fatal(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    return data


def validate_manifest_shape(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in manifest:
            errors.append(f"missing top-level key: {key}")

    corrections = manifest.get("corrections")
    if not isinstance(corrections, list):
        errors.append("corrections must be a list")
        return errors

    for idx, correction in enumerate(corrections):
        if not isinstance(correction, dict):
            errors.append(f"corrections[{idx}] must be an object")
            continue
        for key in REQUIRED_CORRECTION_KEYS:
            if key not in correction:
                errors.append(f"corrections[{idx}] missing key: {key}")
        json_path = correction.get("json_path")
        if json_path is not None and json_path not in SUPPORTED_JSON_PATHS:
            errors.append(f"corrections[{idx}] unsupported json_path: {json_path}")
    return errors


def resolve_json_path(data: dict[str, Any], json_path: str) -> tuple[bool, Any]:
    current: Any = data
    for part in json_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def validate_corrections(repo_root: Path, corrections: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()

    for correction in corrections:
        pdpn = str(correction["pdpn"])
        json_path = str(correction["json_path"])
        rel_file = str(correction["file"])
        target = repo_root / rel_file

        if not target.exists():
            status = "MISSING_FILE"
        else:
            try:
                data = json.loads(target.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001 - fatal for this correction, not whole run.
                status = "MISMATCH"
                print(f"READ_ERROR | {pdpn} | {json_path} | {rel_file} | {exc}")
                counts[status] += 1
                continue

            exists, current_value = resolve_json_path(data, json_path)
            if not exists:
                status = "MISSING_PATH"
            elif current_value == correction["new_value"]:
                status = "MATCH"
            else:
                status = "MISMATCH"

        print(f"{status} | {pdpn} | {json_path} | {rel_file}")
        counts[status] += 1

    return counts


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path

    try:
        manifest = load_manifest(manifest_path)
    except Exception as exc:  # noqa: BLE001 - report as invalid manifest/fatal read.
        return fatal(f"could not read manifest {manifest_path}: {exc}")

    shape_errors = validate_manifest_shape(manifest)
    if shape_errors:
        for error in shape_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    corrections = manifest["corrections"]
    counts = validate_corrections(repo_root, corrections)

    total = len(corrections)
    match = counts["MATCH"]
    mismatch = counts["MISMATCH"]
    missing_file = counts["MISSING_FILE"]
    missing_path = counts["MISSING_PATH"]

    print(
        "summary: "
        f"total={total} "
        f"match={match} "
        f"mismatch={mismatch} "
        f"missing_file={missing_file} "
        f"missing_path={missing_path}"
    )

    if mismatch or missing_file or missing_path:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
