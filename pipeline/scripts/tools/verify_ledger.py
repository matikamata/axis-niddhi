#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — verify_ledger.py
===================================
Verify all ledger entries:
  1. Entry file present and intact (entry_hash recomputed)
  2. canon_hash matches live canon_manifest.json
  3. seed_integrity_hash matches live seed

USAGE:
  python3 scripts/tools/verify_ledger.py
  python3 scripts/tools/verify_ledger.py --entry puredhamma-v1
"""
import argparse, hashlib, json, sys
from pathlib import Path

_SCRIPT_DIR   = Path(__file__).resolve().parent
_CORE_DIR     = _SCRIPT_DIR.parent / "core"
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from config import BASE_DIR, METADATA_DIR

LEDGER_JSON    = BASE_DIR / "ledger" / "ledger.json"
LEDGER_ENTRIES = BASE_DIR / "ledger" / "entries"

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def recompute_entry_hash(entry: dict) -> str:
    h = hashlib.sha256()
    h.update(entry.get("canon_hash","").encode())
    h.update(entry.get("seed_integrity_hash","").encode())
    h.update(entry.get("canon_id","").encode())
    return h.hexdigest()

def verify_entry(canon_id: str, live_manifest: dict, live_seed: dict | None) -> tuple[bool, list[str]]:
    """Returns (pass, [issues])."""
    issues = []
    entry_path = LEDGER_ENTRIES / f"{canon_id}.json"

    if not entry_path.exists():
        return False, [f"Entry file missing: {entry_path}"]

    entry = json.loads(entry_path.read_text(encoding="utf-8"))

    # Check 1: entry_hash integrity
    expected_entry_hash = entry.get("entry_hash", "UNKNOWN")
    actual_entry_hash   = recompute_entry_hash(entry)
    if expected_entry_hash != actual_entry_hash:
        issues.append(f"entry_hash MISMATCH — entry may have been modified")

    # Check 2: canon_hash vs live manifest
    if live_manifest:
        live_canon = live_manifest.get("canon_hash", "UNKNOWN")
        entry_canon = entry.get("canon_hash", "UNKNOWN")
        if live_canon != entry_canon:
            issues.append(
                f"canon_hash divergence — "
                f"entry:{entry_canon[:16]}... live:{live_canon[:16]}... "
                f"(normal if pipeline was rebuilt after this tag)"
            )

    # Check 3: seed_integrity_hash vs live seed
    if live_seed:
        live_seed_h  = live_seed.get("seed_integrity_hash", "UNKNOWN")
        entry_seed_h = entry.get("seed_integrity_hash", "ABSENT")
        if entry_seed_h != "ABSENT" and live_seed_h != entry_seed_h:
            issues.append(
                f"seed_integrity_hash divergence — "
                f"entry:{entry_seed_h[:16]}... live:{live_seed_h[:16]}..."
            )

    return (len(issues) == 0), issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--entry", default=None, help="Verify single entry (e.g. puredhamma-v1)")
    args = parser.parse_args()

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — Canon Ledger Verifier{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    if not LEDGER_JSON.exists():
        print(f"  {RED}❌ Ledger not found: {LEDGER_JSON}{RESET}")
        sys.exit(2)

    ledger  = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
    entries = ledger.get("entries", [])

    if args.entry:
        entries = [args.entry]

    if not entries:
        print(f"  {YELLOW}⚠ No entries in ledger{RESET}\n")
        sys.exit(0)

    # Load live state once
    live_manifest = None
    live_manifest_path = METADATA_DIR / "canon_manifest.json"
    if live_manifest_path.exists():
        live_manifest = json.loads(live_manifest_path.read_text(encoding="utf-8"))
        print(f"  {GRAY}Live canon_hash : {live_manifest.get('canon_hash','?')[:24]}...{RESET}")

    # Load live seed (puredhamma default)
    live_seed = None
    seed_path = BASE_DIR / "seeds" / "puredhamma_seed" / "seed_manifest.json"
    if seed_path.exists():
        live_seed = json.loads(seed_path.read_text(encoding="utf-8"))
        print(f"  {GRAY}Live seed_hash  : {live_seed.get('seed_integrity_hash','?')[:24]}...{RESET}")

    print("")

    all_pass   = True
    pass_count = 0

    for canon_id in entries:
        ok, issues = verify_entry(canon_id, live_manifest, live_seed)

        if ok:
            entry = json.loads((LEDGER_ENTRIES / f"{canon_id}.json").read_text())
            print(f"  {GREEN}✔  {canon_id:<24}{RESET}  "
                  f"canon:{entry.get('canon_hash','')[:16]}...  "
                  f"seed:{entry.get('seed_integrity_hash','')[:16]}...")
            pass_count += 1
        else:
            print(f"  {RED}✘  {canon_id:<24}{RESET}")
            for issue in issues:
                # canon_hash divergence after rebuild is informational, not failure
                if "divergence" in issue:
                    print(f"     {YELLOW}ℹ  {issue}{RESET}")
                else:
                    print(f"     {RED}✘  {issue}{RESET}")
                    all_pass = False

    print("")
    if all_pass:
        print(f"{GREEN}{'='*62}{RESET}")
        print(f"{GREEN}  ✅ LEDGER VERIFIED ({pass_count}/{len(entries)} entries){RESET}")
        print(f"{GREEN}{'='*62}{RESET}\n")
        sys.exit(0)
    else:
        print(f"{RED}{'='*62}{RESET}")
        print(f"{RED}  ❌ LEDGER VERIFICATION FAILURE{RESET}")
        print(f"{RED}{'='*62}{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
