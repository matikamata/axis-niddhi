#!/usr/bin/env python3
"""
AXIS-NIDDHI DM01 - scan local derived media staging.

This tool inspects operator-generated companion media without making it
canonical. It never copies binaries and never writes absolute local paths to
the registry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import re


PIPELINE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PIPELINE_ROOT.parent
DEFAULT_SOURCE = REPO_ROOT.parent / "axis-derived-media-staging" / "raw"
DEFAULT_REGISTRY = PIPELINE_ROOT / "metadata" / "derived_media_registry.csv"

PDPN_RE = re.compile(r"[A-Z]{2}\.[A-Z]{2}\.\d{3}")
AUDIO_EXTS = {".m4a", ".mp3", ".wav"}
VIDEO_EXTS = {".mp4", ".webm"}
SUMMARY_EXTS = {".md", ".txt"}

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

FORBIDDEN_OUTPUT_MARKERS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "PRIVATE KEY",
    "SECRET",
    "/home/",
    "C:\\",
]


@dataclass(frozen=True)
class Candidate:
    pdpn: str
    kind: str
    path: Path
    filename: str
    rel_display: str
    sha256: str
    bytes_size: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan local derived media candidates by PDPN."
    )
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE),
        help="Source folder to scan recursively.",
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY),
        help="Registry CSV path.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Append missing draft rows.")
    mode.add_argument("--dry-run", action="store_true", help="Report only. This is default.")
    parser.add_argument("--verbose", action="store_true", help="Print skipped files.")
    return parser.parse_args()


def resolve_existing_path(value: str, fallback_base: Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute() or path.exists():
        return path

    repo_relative = (fallback_base / path).resolve()
    if repo_relative.exists():
        return repo_relative

    pipeline_relative = (PIPELINE_ROOT / path).resolve()
    if pipeline_relative.exists():
        return pipeline_relative

    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(path: Path) -> Optional[str]:
    suffix = path.suffix.lower()
    if suffix in AUDIO_EXTS:
        return "audio"
    if suffix in VIDEO_EXTS:
        return "video"
    if suffix in SUMMARY_EXTS:
        return "summary"
    return None


def load_registry(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    if not path.exists():
        return REGISTRY_COLUMNS[:], []

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"registry has no header: {path}")
        missing = [c for c in REGISTRY_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"registry missing required columns: {', '.join(missing)}")
        rows = [row for row in reader]
        return list(reader.fieldnames), rows


def ensure_registry(path: Path, fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()


def is_safe_output(value: str) -> bool:
    if not value:
        return True
    if "\n" in value or "\r" in value:
        return False
    upper_value = value.upper()
    for marker in FORBIDDEN_OUTPUT_MARKERS:
        if marker.upper() in upper_value:
            return False
    if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
        return False
    return True


def safe_join(values: Iterable[str]) -> str:
    return " | ".join(v for v in values if v)


def select_single(
    pdpn: str,
    kind: str,
    items: List[Candidate],
    warnings: List[str],
) -> Optional[Candidate]:
    if not items:
        return None
    if len(items) == 1:
        return items[0]
    names = safe_join(item.filename for item in items)
    warnings.append(
        f"{pdpn}: multiple {kind} candidates found; operator must choose manually: {names}"
    )
    return None


def build_registry_row(pdpn: str, items: List[Candidate], warnings: List[str]) -> Dict[str, str]:
    by_kind = {
        "audio": [c for c in items if c.kind == "audio"],
        "video": [c for c in items if c.kind == "video"],
        "summary": [c for c in items if c.kind == "summary"],
    }

    audio = select_single(pdpn, "audio", by_kind["audio"], warnings)
    video = select_single(pdpn, "video", by_kind["video"], warnings)
    summary = select_single(pdpn, "summary", by_kind["summary"], warnings)

    notes_parts = []
    for kind in ("summary", "audio", "video"):
        if by_kind[kind]:
            notes_parts.append(
                f"{kind}_candidates={safe_join(c.filename for c in by_kind[kind])}"
            )

    row = {col: "" for col in REGISTRY_COLUMNS}
    row["pdpn"] = pdpn
    row["status"] = "draft"
    row["notes"] = "; ".join(notes_parts)

    if summary:
        row["summary_path"] = f"derived_media/summaries/{pdpn}.pt-BR{summary.path.suffix.lower()}"
        row["summary_sha256"] = summary.sha256

    if audio:
        row["source_audio_filename"] = audio.filename
        row["audio_sha256"] = audio.sha256
        row["audio_bytes"] = str(audio.bytes_size)

    if video:
        row["source_video_filename"] = video.filename
        row["video_sha256"] = video.sha256
        row["video_bytes"] = str(video.bytes_size)

    for key, value in row.items():
        if not is_safe_output(value):
            raise ValueError(f"unsafe registry output for {pdpn} field {key}: {value!r}")

    return row


def scan_source(source: Path, verbose: bool) -> Tuple[Dict[str, List[Candidate]], List[str], List[str]]:
    grouped: Dict[str, List[Candidate]] = {}
    warnings: List[str] = []
    skipped: List[str] = []

    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue

        kind = classify(path)
        if kind is None:
            msg = f"skipped unsupported extension: {path.name}"
            warnings.append(msg)
            if verbose:
                skipped.append(msg)
            continue

        match = PDPN_RE.search(path.name)
        if not match:
            msg = f"skipped recognized media without valid PDPN: {path.name}"
            warnings.append(msg)
            if verbose:
                skipped.append(msg)
            continue

        pdpn = match.group(0)
        try:
            size = path.stat().st_size
            digest = sha256_file(path)
            rel_display = path.relative_to(source).as_posix()
        except Exception as exc:
            msg = f"skipped unreadable file {path.name}: {exc}"
            warnings.append(msg)
            if verbose:
                skipped.append(msg)
            continue

        grouped.setdefault(pdpn, []).append(
            Candidate(
                pdpn=pdpn,
                kind=kind,
                path=path,
                filename=path.name,
                rel_display=rel_display,
                sha256=digest,
                bytes_size=size,
            )
        )

    return grouped, warnings, skipped


def print_report(
    source: Path,
    grouped: Dict[str, List[Candidate]],
    warnings: List[str],
    skipped: List[str],
    existing_pdpns: set[str],
    apply: bool,
) -> None:
    total = sum(len(items) for items in grouped.values())
    print("AXIS-NIDDHI Derived Media Scan")
    print(f"source: {source}")
    print(f"mode: {'apply' if apply else 'dry-run'}")
    print(f"pdpn groups: {len(grouped)}")
    print(f"recognized candidates: {total}")
    print()

    for pdpn in sorted(grouped):
        marker = "existing-registry-row" if pdpn in existing_pdpns else "new"
        print(f"{pdpn} ({marker})")
        for item in sorted(grouped[pdpn], key=lambda c: (c.kind, c.filename)):
            print(
                f"  {item.kind:<7} {item.filename} "
                f"bytes={item.bytes_size} sha256={item.sha256[:16]}..."
            )

    if warnings:
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if skipped:
        print()
        print("Skipped:")
        for item in skipped:
            print(f"  - {item}")


def append_rows(path: Path, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        for row in rows:
            writer.writerow(row)


def main() -> int:
    args = parse_args()
    source = resolve_existing_path(args.source, REPO_ROOT)
    registry = Path(args.registry).expanduser()
    apply = bool(args.apply)

    if not source.exists() or not source.is_dir():
        print(f"ERROR: source directory not found: {source}", file=sys.stderr)
        return 1

    try:
        fieldnames, registry_rows = load_registry(registry)
    except ValueError as exc:
        print(f"ERROR: malformed registry: {exc}", file=sys.stderr)
        return 2

    existing_pdpns = {
        (row.get("pdpn") or "").strip()
        for row in registry_rows
        if (row.get("pdpn") or "").strip()
    }

    grouped, warnings, skipped = scan_source(source, args.verbose)

    rows_to_append: List[Dict[str, str]] = []
    for pdpn in sorted(grouped):
        if pdpn in existing_pdpns:
            statuses = {
                (row.get("status") or "").strip()
                for row in registry_rows
                if (row.get("pdpn") or "").strip() == pdpn
            }
            if "approved" in statuses:
                warnings.append(f"{pdpn}: approved registry row already exists; preserving it")
            continue
        try:
            rows_to_append.append(build_registry_row(pdpn, grouped[pdpn], warnings))
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 3

    print_report(source, grouped, warnings, skipped, existing_pdpns, apply)

    if apply:
        ensure_registry(registry, fieldnames)
        append_rows(registry, fieldnames, rows_to_append)
        print()
        print(f"appended draft rows: {len(rows_to_append)}")
        print(f"registry: {registry}")
    else:
        print()
        print(f"dry-run only; rows that would be appended: {len(rows_to_append)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
