#!/usr/bin/env python3
"""
rebuild_translation_status.py
[FF-011] 2026-03-09 — Reconstroi translation_status.json varrendo CSL real.

O arquivo translation_status.json gerado pelo pipeline anterior estava stale:
contava apenas posts com content.html PT, ignorando posts com titles.pt mas
sem corpo traduzido. Este script separa os dois conceitos corretamente.

Uso:
    python3 rebuild_translation_status.py
    python3 rebuild_translation_status.py --csl /caminho/para/09-csl
    python3 rebuild_translation_status.py --out /caminho/saida/translation_status.json

Saida:
    translation_status.json com campos:
        with_pt_title    — posts com titles.pt preenchido
        with_pt_content  — posts com source/pt-BR/content.html no disco
        fully_complete   — posts com title + content PT
        missing_pt_title — posts sem titles.pt
        missing_pt_content — posts com title PT mas sem content PT
        progress_content_pct — % de posts com corpo PT
        progress_title_pct   — % de posts com titulo PT
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ── Locate CSL root ──────────────────────────────────────────────────────────
_HERE = Path(__file__).parent.resolve()

def find_csl_root(start: Path) -> Path:
    current = start
    while current.parent != current:
        candidate = current / "09-csl"
        if candidate.exists():
            return candidate
        if current.name == "09-csl":
            return current
        current = current.parent
    raise FileNotFoundError(f"09-csl not found from {start}")


def audit_csl(csl_root: Path) -> dict:
    """Scan all identity.json files and return aggregated stats + per-post data."""

    posts_data = []
    errors = []

    for identity_path in sorted(csl_root.rglob("meta/identity.json")):
        post_dir = identity_path.parent.parent
        pdpn = post_dir.name

        try:
            data = json.loads(identity_path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append({"pdpn": pdpn, "error": str(e)})
            continue

        titles = data.get("titles", {})
        pt_title = titles.get("pt", "")
        has_pt_title = bool(pt_title and str(pt_title).strip())

        pt_content_path = post_dir / "source" / "pt-BR" / "content.html"
        has_pt_content = (
            pt_content_path.exists()
            and pt_content_path.is_file()
            and not pt_content_path.is_symlink()
        )

        posts_data.append({
            "pdpn": pdpn,
            "title_en": titles.get("en", ""),
            "title_pt": pt_title,
            "has_pt_title": has_pt_title,
            "has_pt_content": has_pt_content,
            "fully_complete": has_pt_title and has_pt_content,
        })

    total = len(posts_data)
    with_pt_title   = sum(1 for p in posts_data if p["has_pt_title"])
    with_pt_content = sum(1 for p in posts_data if p["has_pt_content"])
    fully_complete  = sum(1 for p in posts_data if p["fully_complete"])

    # Posts that have content but are missing title (needs SP11 run)
    content_no_title = [p for p in posts_data if p["has_pt_content"] and not p["has_pt_title"]]
    # Posts that have title but no content body yet
    title_no_content = [p for p in posts_data if p["has_pt_title"] and not p["has_pt_content"]]

    return {
        "generated_at":         datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total_posts":          total,
        "with_pt_title":        with_pt_title,
        "with_pt_content":      with_pt_content,
        "fully_complete":       fully_complete,
        "missing_pt_title":     total - with_pt_title,
        "missing_pt_content":   total - with_pt_content,
        "content_no_title":     len(content_no_title),
        "title_no_content":     len(title_no_content),
        "progress_content_pct": round(with_pt_content / total * 100, 2) if total else 0,
        "progress_title_pct":   round(with_pt_title   / total * 100, 2) if total else 0,
        # Detail lists (useful for SP11 targeting)
        "posts_needing_title":  [p["pdpn"] for p in content_no_title],
        "posts_title_only":     [p["pdpn"] for p in title_no_content],
        "errors":               errors,
    }


def main():
    parser = argparse.ArgumentParser(description="Rebuild translation_status.json from CSL")
    parser.add_argument("--csl", type=Path, default=None, help="Path to 09-csl directory")
    parser.add_argument("--out", type=Path, default=None, help="Output path for translation_status.json")
    args = parser.parse_args()

    try:
        csl_root = args.csl if args.csl else find_csl_root(_HERE)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    out_path = args.out if args.out else _HERE / "translation_status.json"

    print(f"Scanning CSL: {csl_root}")
    result = audit_csl(csl_root)

    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"  Total posts:        {result['total_posts']}")
    print(f"  With PT title:      {result['with_pt_title']}  ({result['progress_title_pct']}%)")
    print(f"  With PT content:    {result['with_pt_content']}  ({result['progress_content_pct']}%)")
    print(f"  Fully complete:     {result['fully_complete']}")
    print(f"  Content, no title:  {result['content_no_title']}  ← run SP11 on these")
    print(f"  Title, no content:  {result['title_no_content']}  ← translation in progress")
    if result['errors']:
        print(f"  Errors:             {len(result['errors'])}")
    print(f"{'='*50}")
    print(f"  Saved: {out_path}")


if __name__ == "__main__":
    main()
