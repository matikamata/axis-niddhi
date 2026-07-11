#!/usr/bin/env python3
"""
AXIS-NIDDHI LA02 - generate Portuguese Desana long-audio manifest.

This layer is intentionally separate from the Derived Media Companion. It
supports multiple pt-BR audio items per PDPN and rejects local paths, file://
URLs, missing media metadata, and duplicate public URLs.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


PIPELINE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = PIPELINE_ROOT / "metadata" / "long_audio_registry.csv"
DEFAULT_OUTPUT = PIPELINE_ROOT / "metadata" / "long_audio_manifest.json"

PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
ORDER_RE = re.compile(r"^\d{2}(?:\.\d+)?$")
STATUS_VALUES = {"approved", "draft", "hidden"}
FORBIDDEN_MARKERS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "PRIVATE KEY",
    "SECRET",
    "/home/",
    "C:\\",
]

REGISTRY_COLUMNS = [
    "pdpn",
    "language",
    "order",
    "title",
    "part_label",
    "series_label",
    "audio_url",
    "audio_sha256",
    "audio_bytes",
    "duration_seconds",
    "source_filename",
    "source_youtube_url",
    "review_status",
    "notes",
]


class RegistryError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate metadata/long_audio_manifest.json from long_audio_registry.csv."
    )
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="Registry CSV path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Manifest JSON output path.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and preview a summary without writing the output file.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the registry only. Does not write the output file.",
    )
    return parser.parse_args()


def clean(value: object) -> str:
    return str(value or "").strip()


def reject_forbidden(value: str, row_number: int, field: str) -> None:
    if not value:
        return
    upper = value.upper()
    for marker in FORBIDDEN_MARKERS:
        if marker.upper() in upper:
            raise RegistryError(
                f"row {row_number} field {field} contains forbidden marker: {marker}"
            )
    if value.lower().startswith("file://"):
        raise RegistryError(f"row {row_number} field {field} uses forbidden file:// URL")
    if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
        raise RegistryError(f"row {row_number} field {field} contains an absolute path")


def validate_url(value: str, row_number: int, field: str, required: bool = False) -> None:
    if not value:
        if required:
            raise RegistryError(f"row {row_number} field {field} is required")
        return
    if not (value.startswith("https://") or value.startswith("http://")):
        raise RegistryError(f"row {row_number} field {field} must begin with http:// or https://")
    if value.lower().startswith(("file://", "javascript:", "data:")):
        raise RegistryError(f"row {row_number} field {field} uses a blocked URL scheme")


def validate_source_filename(value: str, row_number: int) -> None:
    if not value:
        raise RegistryError(f"row {row_number} source_filename is required")
    if "/" in value or "\\" in value:
        raise RegistryError(f"row {row_number} source_filename must be a filename, not a path")
    if not value.lower().endswith(".m4a"):
        raise RegistryError(f"row {row_number} source_filename must end with .m4a")


def parse_positive_int(value: str, row_number: int, field: str) -> int:
    if not value:
        raise RegistryError(f"row {row_number} field {field} is required")
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RegistryError(f"row {row_number} field {field} must be an integer") from exc
    if parsed <= 0:
        raise RegistryError(f"row {row_number} field {field} must be positive")
    return parsed


def parse_positive_float(value: str, row_number: int, field: str) -> float:
    if not value:
        raise RegistryError(f"row {row_number} field {field} is required")
    try:
        parsed = float(value)
    except ValueError as exc:
        raise RegistryError(f"row {row_number} field {field} must be a number") from exc
    if parsed <= 0:
        raise RegistryError(f"row {row_number} field {field} must be positive")
    return parsed


def order_sort_key(value: str) -> Tuple[int, ...]:
    if not ORDER_RE.match(value):
        raise RegistryError(f"invalid social order value: {value!r}")
    return tuple(int(part) for part in value.split("."))


def load_registry(path: Path) -> List[Tuple[int, Dict[str, str]]]:
    if not path.exists():
        raise RegistryError(f"registry not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise RegistryError(f"registry has no header: {path}")
        missing = [column for column in REGISTRY_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise RegistryError(f"registry missing required columns: {', '.join(missing)}")

        rows: List[Tuple[int, Dict[str, str]]] = []
        for index, row in enumerate(reader, start=2):
            if not any(clean(value) for value in row.values()):
                continue
            rows.append((index, {key: clean(value) for key, value in row.items()}))
        return rows


def validate_row(row_number: int, row: Dict[str, str]) -> None:
    pdpn = row.get("pdpn", "")
    language = row.get("language", "")
    order = row.get("order", "")
    status = row.get("review_status", "")
    sha256 = row.get("audio_sha256", "")

    if not PDPN_RE.match(pdpn):
        raise RegistryError(f"row {row_number} has invalid PDPN: {pdpn!r}")
    if language != "pt-BR":
        raise RegistryError(f"row {row_number} language must be pt-BR")
    if not ORDER_RE.match(order):
        raise RegistryError(f"row {row_number} has invalid order: {order!r}")
    if status not in STATUS_VALUES:
        raise RegistryError(f"row {row_number} review_status must be approved, draft, or hidden")
    if not row.get("title"):
        raise RegistryError(f"row {row_number} title is required")
    if not sha256 or not SHA256_RE.match(sha256):
        raise RegistryError(f"row {row_number} audio_sha256 must be a sha256 hex digest")

    for field in REGISTRY_COLUMNS:
        reject_forbidden(row.get(field, ""), row_number, field)

    validate_url(row.get("audio_url", ""), row_number, "audio_url", required=True)
    validate_url(row.get("source_youtube_url", ""), row_number, "source_youtube_url")
    parse_positive_int(row.get("audio_bytes", ""), row_number, "audio_bytes")
    parse_positive_float(row.get("duration_seconds", ""), row_number, "duration_seconds")
    validate_source_filename(row.get("source_filename", ""), row_number)


def build_manifest(rows: List[Tuple[int, Dict[str, str]]]) -> Dict[str, object]:
    seen_order_by_pdpn = set()
    seen_urls = set()
    manifest: Dict[str, Dict[str, object]] = {}

    for row_number, row in rows:
        validate_row(row_number, row)
        if row.get("review_status") != "approved":
            continue

        pdpn = row["pdpn"]
        order = row["order"]
        order_key = (pdpn, order)
        if order_key in seen_order_by_pdpn:
            raise RegistryError(f"row {row_number} duplicates order {order} for {pdpn}")
        seen_order_by_pdpn.add(order_key)

        audio_url = row["audio_url"]
        if audio_url in seen_urls:
            raise RegistryError(f"row {row_number} duplicates audio_url: {audio_url}")
        seen_urls.add(audio_url)

        entry = manifest.setdefault(pdpn, {"language": "pt-BR", "items": []})
        entry["items"].append(
            {
                "order": order,
                "title": row["title"],
                "part_label": row.get("part_label", ""),
                "series_label": row.get("series_label", ""),
                "audio": {
                    "url": audio_url,
                    "sha256": row["audio_sha256"],
                    "bytes": parse_positive_int(row["audio_bytes"], row_number, "audio_bytes"),
                    "duration_seconds": parse_positive_float(
                        row["duration_seconds"], row_number, "duration_seconds"
                    ),
                },
                "source": {
                    "filename": row["source_filename"],
                    "youtube_url": row.get("source_youtube_url", ""),
                },
            }
        )

    for entry in manifest.values():
        entry["items"].sort(key=lambda item: order_sort_key(str(item["order"])))

    return {pdpn: manifest[pdpn] for pdpn in sorted(manifest)}


def main() -> int:
    args = parse_args()
    registry_path = Path(args.registry)
    output_path = Path(args.output)

    try:
        rows = load_registry(registry_path)
        manifest = build_manifest(rows)
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    item_count = sum(len(entry["items"]) for entry in manifest.values())
    print(
        "Long audio manifest OK: "
        f"pdpns={len(manifest)} items={item_count} "
        f"registry={registry_path}"
    )

    if args.dry_run or args.check:
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
