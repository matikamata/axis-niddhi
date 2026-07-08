#!/usr/bin/env python3
"""
AXIS-NIDDHI DM02 - generate derived media manifest.

The manifest is downstream data. It includes only operator-approved registry
rows and rejects local paths, file:// URLs, and forbidden secret markers.
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
DEFAULT_REGISTRY = PIPELINE_ROOT / "metadata" / "derived_media_registry.csv"
DEFAULT_OUTPUT = PIPELINE_ROOT / "metadata" / "derived_media_manifest.json"

PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
STATUS_VALUES = {"draft", "approved", "hidden"}

REGISTRY_COLUMNS = [
    "pdpn",
    "status",
    "summary_path",
    "audio_url",
    "video_url",
    "telegram_url",
    "spotify_url",
    "youtube_url",
    "source_audio_filename",
    "source_video_filename",
    "summary_sha256",
    "audio_sha256",
    "video_sha256",
    "audio_bytes",
    "video_bytes",
    "notes",
]

URL_FIELDS = {
    "audio_url",
    "video_url",
    "telegram_url",
    "spotify_url",
    "youtube_url",
}

SHA_FIELDS = {"summary_sha256", "audio_sha256", "video_sha256"}
BYTE_FIELDS = {"audio_bytes", "video_bytes"}
SOURCE_FILENAME_FIELDS = {"source_audio_filename", "source_video_filename"}

FORBIDDEN_MARKERS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "PRIVATE KEY",
    "SECRET",
    "/home/",
    "C:\\",
]


class RegistryError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate metadata/derived_media_manifest.json from approved registry rows."
    )
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="Registry CSV path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Manifest JSON output path.")
    return parser.parse_args()


def clean(value: object) -> str:
    return str(value or "").strip()


def reject_forbidden(value: str, row_number: int, field: str) -> None:
    if not value:
        return
    upper_value = value.upper()
    for marker in FORBIDDEN_MARKERS:
        if marker.upper() in upper_value:
            raise RegistryError(
                f"row {row_number} field {field} contains forbidden marker: {marker}"
            )
    if value.lower().startswith("file://"):
        raise RegistryError(f"row {row_number} field {field} uses forbidden file:// URL")
    if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
        raise RegistryError(f"row {row_number} field {field} contains an absolute local path")


def validate_url(value: str, row_number: int, field: str) -> None:
    if not value:
        return
    if value.lower().startswith("file://"):
        raise RegistryError(f"row {row_number} field {field} uses forbidden file:// URL")
    if not (value.startswith("https://") or value.startswith("http://")):
        raise RegistryError(f"row {row_number} field {field} must begin with http:// or https://")


def validate_summary_path(value: str, row_number: int) -> None:
    if not value:
        return
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("~") or ".." in normalized.split("/"):
        raise RegistryError(f"row {row_number} summary_path must be a safe relative path")
    if not normalized.startswith("derived_media/summaries/"):
        raise RegistryError(
            f"row {row_number} summary_path must stay under derived_media/summaries/"
        )
    if Path(normalized).suffix.lower() not in {".md", ".txt"}:
        raise RegistryError(f"row {row_number} summary_path must be .md or .txt")


def validate_source_filename(value: str, row_number: int, field: str) -> None:
    if not value:
        return
    if "/" in value or "\\" in value:
        raise RegistryError(f"row {row_number} field {field} must be a filename, not a path")


def parse_bytes(value: str, row_number: int, field: str) -> int:
    if not value:
        return 0
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RegistryError(f"row {row_number} field {field} must be an integer") from exc
    if parsed < 0:
        raise RegistryError(f"row {row_number} field {field} must be non-negative")
    return parsed


def load_registry(path: Path) -> List[Tuple[int, Dict[str, str]]]:
    if not path.exists():
        print(f"WARNING: registry absent; writing empty manifest: {path}")
        return []

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise RegistryError(f"registry has no header: {path}")
        missing = [c for c in REGISTRY_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise RegistryError(f"registry missing required columns: {', '.join(missing)}")

        rows: List[Tuple[int, Dict[str, str]]] = []
        for index, row in enumerate(reader, start=2):
            if not any(clean(value) for value in row.values()):
                continue
            rows.append((index, {key: clean(value) for key, value in row.items()}))
        return rows


def validate_row(row_number: int, row: Dict[str, str]) -> None:
    pdpn = clean(row.get("pdpn"))
    status = clean(row.get("status"))

    if not PDPN_RE.match(pdpn):
        raise RegistryError(f"row {row_number} has invalid PDPN: {pdpn!r}")
    if status not in STATUS_VALUES:
        raise RegistryError(
            f"row {row_number} has invalid status {status!r}; expected draft, approved, or hidden"
        )

    for field in REGISTRY_COLUMNS:
        reject_forbidden(clean(row.get(field)), row_number, field)

    for field in URL_FIELDS:
        validate_url(clean(row.get(field)), row_number, field)

    validate_summary_path(clean(row.get("summary_path")), row_number)

    for field in SOURCE_FILENAME_FIELDS:
        validate_source_filename(clean(row.get(field)), row_number, field)

    for field in SHA_FIELDS:
        value = clean(row.get(field))
        if value and not SHA256_RE.match(value):
            raise RegistryError(f"row {row_number} field {field} must be a sha256 hex digest")

    for field in BYTE_FIELDS:
        parse_bytes(clean(row.get(field)), row_number, field)


def add_if_present(target: Dict[str, object], key: str, value: str) -> None:
    if value != "":
        target[key] = value


def build_entry(row: Dict[str, str]) -> Dict[str, object]:
    entry: Dict[str, object] = {
        "source_pdpn": row["pdpn"],
        "review_status": "approved",
    }

    summary: Dict[str, object] = {}
    add_if_present(summary, "path", clean(row.get("summary_path")))
    add_if_present(summary, "sha256", clean(row.get("summary_sha256")))
    if summary:
        entry["summary"] = summary

    audio: Dict[str, object] = {}
    add_if_present(audio, "url", clean(row.get("audio_url")))
    add_if_present(audio, "sha256", clean(row.get("audio_sha256")))
    audio_bytes = parse_bytes(clean(row.get("audio_bytes")), 0, "audio_bytes")
    if clean(row.get("audio_bytes")):
        audio["bytes"] = audio_bytes
    if audio:
        entry["audio"] = audio

    video: Dict[str, object] = {}
    add_if_present(video, "url", clean(row.get("video_url")))
    add_if_present(video, "sha256", clean(row.get("video_sha256")))
    video_bytes = parse_bytes(clean(row.get("video_bytes")), 0, "video_bytes")
    if clean(row.get("video_bytes")):
        video["bytes"] = video_bytes
    if video:
        entry["video"] = video

    external: Dict[str, object] = {}
    add_if_present(external, "telegram", clean(row.get("telegram_url")))
    add_if_present(external, "spotify", clean(row.get("spotify_url")))
    add_if_present(external, "youtube", clean(row.get("youtube_url")))
    if external:
        entry["external"] = external

    return entry


def write_manifest(path: Path, manifest: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    args = parse_args()
    registry = Path(args.registry).expanduser()
    output = Path(args.output).expanduser()

    try:
        rows = load_registry(registry)
        seen: set[str] = set()
        approved: Dict[str, Dict[str, object]] = {}

        for row_number, row in rows:
            validate_row(row_number, row)
            pdpn = row["pdpn"]
            if pdpn in seen:
                raise RegistryError(f"duplicate PDPN in registry: {pdpn}")
            seen.add(pdpn)

            if row["status"] == "approved":
                approved[pdpn] = build_entry(row)

        manifest = {pdpn: approved[pdpn] for pdpn in sorted(approved)}
        write_manifest(output, manifest)
    except RegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"derived media manifest entries: {len(manifest)}")
    print(f"output: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
