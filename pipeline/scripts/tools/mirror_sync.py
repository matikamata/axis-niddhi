#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — mirror_sync.py
================================
Nome:       Mirror Sync
Versão:     1.0 — Mirror Protocol Phase
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)

PURPOSE:
  Synchronize ledger and seeds from configured AXIS mirror nodes.

  For each mirror in mirror/mirrors.json:
    1. Fetch <mirror_url>/ledger.json
    2. Compare entries with local ledger/ledger.json
    3. For each new entry:
         - Download <mirror_url>/seeds/<canon_id>/seed_manifest.json
         - Verify seed integrity (seed_integrity_hash)
         - Write to local seeds/<corpus_id>_seed/ if verified

  Mirror transport: HTTP GET (requests) or file:// (local path)
  All fetched seeds are integrity-verified before writing.

USAGE:
  python3 scripts/tools/mirror_sync.py
  python3 scripts/tools/mirror_sync.py --dry-run
  python3 scripts/tools/mirror_sync.py --mirror file:///path/to/mirror_endpoint
"""

import argparse
import hashlib
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
_CORE_DIR   = _SCRIPT_DIR.parent / "core"
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from config import BASE_DIR, METADATA_DIR

MIRROR_DIR     = BASE_DIR / "mirror"
MIRRORS_JSON   = MIRROR_DIR / "mirrors.json"
LEDGER_JSON    = BASE_DIR / "ledger" / "ledger.json"
LEDGER_ENTRIES = BASE_DIR / "ledger" / "entries"
SEEDS_DIR      = BASE_DIR / "seeds"

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

SEED_FILES = [
    "corpus.json",
    "pipeline_profile.json",
    "canon_manifest.json",
    "build_seal.json",
    "seed_manifest.json",
]


# ==============================================================================
# 🌐  TRANSPORT
# ==============================================================================
def fetch_url(url: str, timeout: int = 15) -> bytes | None:
    """Fetch URL → bytes. Supports http://, https://, file://."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read()
    except urllib.error.URLError as e:
        print(f"  {RED}✘ Fetch failed: {url}{RESET}")
        print(f"    {GRAY}{e}{RESET}")
        return None
    except Exception as e:
        print(f"  {RED}✘ Error fetching {url}: {e}{RESET}")
        return None


def fetch_json(url: str) -> dict | None:
    data = fetch_url(url)
    if data is None:
        return None
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"  {RED}✘ JSON parse error at {url}: {e}{RESET}")
        return None


# ==============================================================================
# 🔐  INTEGRITY
# ==============================================================================
def verify_seed_integrity(seed_dir: Path) -> tuple[bool, str]:
    """Recompute seed_integrity_hash from seed files. Returns (ok, actual_hash)."""
    h = hashlib.sha256()
    hashes = {}
    for fname in ["canon_manifest.json", "build_seal.json", "corpus.json", "pipeline_profile.json"]:
        fpath = seed_dir / fname
        if not fpath.exists():
            return False, f"MISSING:{fname}"
        hashes[fname] = hashlib.sha256(fpath.read_bytes()).hexdigest()

    for fh in sorted(hashes.values()):
        h.update(fh.encode())
    return True, h.hexdigest()


# ==============================================================================
# 📥  SEED DOWNLOAD
# ==============================================================================
def download_seed(mirror_url: str, canon_id: str, corpus_id: str, dry_run: bool) -> bool:
    """Download all seed files for canon_id from mirror. Returns True on success."""
    seed_url_base = f"{mirror_url.rstrip('/')}/seeds/{canon_id}"
    seed_dest     = SEEDS_DIR / f"{corpus_id}_seed_{canon_id}"

    if not dry_run:
        seed_dest.mkdir(parents=True, exist_ok=True)

    print(f"    {GRAY}Downloading seed: {canon_id}{RESET}")
    downloaded = {}

    for fname in SEED_FILES:
        url  = f"{seed_url_base}/{fname}"
        data = fetch_url(url)
        if data is None:
            print(f"    {RED}✘ Failed to download: {fname}{RESET}")
            return False
        downloaded[fname] = data
        if not dry_run:
            (seed_dest / fname).write_bytes(data)
        print(f"    {GRAY}  {fname} ({len(data)} bytes){RESET}")

    if dry_run:
        print(f"    {YELLOW}[DRY-RUN] Seed not written{RESET}")
        return True

    # Verify integrity
    ok, actual_hash = verify_seed_integrity(seed_dest)
    if not ok:
        print(f"    {RED}✘ Seed integrity check failed: {actual_hash}{RESET}")
        import shutil; shutil.rmtree(seed_dest, ignore_errors=True)
        return False

    # Compare with seed_manifest declared hash
    seed_manifest_path = seed_dest / "seed_manifest.json"
    if seed_manifest_path.exists():
        declared = json.loads(seed_manifest_path.read_text()).get("seed_integrity_hash","")
        if declared and declared != actual_hash:
            print(f"    {RED}✘ seed_integrity_hash mismatch{RESET}")
            print(f"      declared: {declared[:24]}...")
            print(f"      actual  : {actual_hash[:24]}...")
            import shutil; shutil.rmtree(seed_dest, ignore_errors=True)
            return False

    print(f"    {GREEN}✔ Seed verified: {actual_hash[:24]}...{RESET}")
    return True


# ==============================================================================
# 🔄  SYNC ONE MIRROR
# ==============================================================================
def sync_mirror(mirror: dict, local_ledger: dict, dry_run: bool) -> dict:
    """Sync one mirror. Returns stats dict."""
    url    = mirror.get("url", "").rstrip("/")
    name   = mirror.get("name", url)
    stats  = {"new": 0, "skipped": 0, "failed": 0}

    print(f"\n  {CYAN}── Mirror: {name}{RESET}")
    print(f"     {GRAY}{url}{RESET}")

    # Fetch remote ledger
    remote_ledger = fetch_json(f"{url}/ledger.json")
    if remote_ledger is None:
        print(f"  {RED}✘ Could not reach mirror ledger{RESET}")
        stats["failed"] += 1
        return stats

    remote_entries = remote_ledger.get("entries", [])
    local_entries  = set(local_ledger.get("entries", []))

    print(f"     {GRAY}Remote entries: {len(remote_entries)}  Local: {len(local_entries)}{RESET}")

    new_entries = [e for e in remote_entries if e not in local_entries]
    if not new_entries:
        print(f"     {GREEN}✔ Already up to date{RESET}")
        return stats

    print(f"     {YELLOW}New entries: {len(new_entries)}{RESET}")

    for canon_id in new_entries:
        # Fetch entry metadata
        entry_data = fetch_json(f"{url}/entries/{canon_id}.json")
        if entry_data is None:
            print(f"    {RED}✘ Could not fetch entry: {canon_id}{RESET}")
            stats["failed"] += 1
            continue

        corpus_id = entry_data.get("corpus_id", "puredhamma")
        print(f"\n    {GRAY}New entry: {canon_id} (corpus: {corpus_id}){RESET}")

        # Download seed
        ok = download_seed(url, canon_id, corpus_id, dry_run)
        if ok:
            # Write entry to local ledger entries (if not dry-run)
            if not dry_run:
                entry_path = LEDGER_ENTRIES / f"{canon_id}.json"
                entry_path.write_text(json.dumps(entry_data, indent=2), encoding="utf-8")

                # Append to local ledger
                if canon_id not in local_ledger["entries"]:
                    local_ledger["entries"].append(canon_id)
                    local_ledger["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    local_ledger["entry_count"] = len(local_ledger["entries"])
                    LEDGER_JSON.write_text(json.dumps(local_ledger, indent=2), encoding="utf-8")

            print(f"    {GREEN}✔ Synced: {canon_id}{RESET}")
            stats["new"] += 1
        else:
            stats["failed"] += 1

    return stats


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Sync ledger and seeds from AXIS mirrors")
    parser.add_argument("--dry-run", action="store_true", help="Simulate sync, do not write files")
    parser.add_argument("--mirror",  default=None, help="Sync from this URL only (overrides mirrors.json)")
    args = parser.parse_args()

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — Mirror Sync{RESET}")
    if args.dry_run:
        print(f"  {YELLOW}MODE: DRY-RUN — no files will be written{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    # Load mirrors
    if args.mirror:
        mirrors = [{"name": args.mirror, "url": args.mirror}]
    elif MIRRORS_JSON.exists():
        cfg     = json.loads(MIRRORS_JSON.read_text(encoding="utf-8"))
        mirrors = cfg.get("mirrors", [])
    else:
        mirrors = []

    if not mirrors:
        print(f"  {YELLOW}⚠ No mirrors configured.{RESET}")
        print(f"   Add mirrors to: {MIRRORS_JSON}")
        print(f"   Or use: --mirror file:///path/to/mirror_endpoint")
        print(f"   Or use: --mirror http://hostname/mirror_endpoint\n")
        return

    # Load local ledger
    if not LEDGER_JSON.exists():
        print(f"  {RED}❌ Local ledger not found: {LEDGER_JSON}{RESET}")
        print("   Run: axis ledger add")
        sys.exit(1)

    local_ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))

    # Sync each mirror
    total = {"new": 0, "skipped": 0, "failed": 0}
    for mirror in mirrors:
        stats = sync_mirror(mirror, local_ledger, args.dry_run)
        for k in total:
            total[k] += stats.get(k, 0)

    # Summary
    print(f"\n{GREEN if total['failed']==0 else YELLOW}{'='*62}{RESET}")
    if total["failed"] == 0:
        print(f"{GREEN}  ✅ MIRROR SYNC COMPLETE{RESET}")
    else:
        print(f"{YELLOW}  ⚠ MIRROR SYNC COMPLETE WITH FAILURES{RESET}")
    print(f"{'='*62}")
    print(f"  {GRAY}New entries synced : {total['new']}{RESET}")
    print(f"  {GRAY}Failed             : {total['failed']}{RESET}")
    if args.dry_run:
        print(f"  {YELLOW}DRY-RUN — no changes written{RESET}")
    print(f"{GREEN if total['failed']==0 else YELLOW}{'='*62}{RESET}\n")


if __name__ == "__main__":
    main()
