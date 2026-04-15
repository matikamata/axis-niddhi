#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — list_ledger.py
================================
List all registered canon entries in the ledger.

USAGE:
  python3 scripts/tools/list_ledger.py
"""
import json, sys
from pathlib import Path

_SCRIPT_DIR   = Path(__file__).resolve().parent
_CORE_DIR     = _SCRIPT_DIR.parent / "core"
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from config import BASE_DIR

LEDGER_JSON    = BASE_DIR / "ledger" / "ledger.json"
LEDGER_ENTRIES = BASE_DIR / "ledger" / "entries"

CYAN  = "\033[96m"
GREEN = "\033[92m"
GRAY  = "\033[90m"
YELLOW= "\033[93m"
RED   = "\033[91m"
RESET = "\033[0m"

def main():
    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — Canon Ledger{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    if not LEDGER_JSON.exists():
        print(f"  {YELLOW}⚠ Ledger not initialized: {LEDGER_JSON}{RESET}")
        print("   Run: axis ledger add\n")
        sys.exit(0)

    ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
    entries = ledger.get("entries", [])

    print(f"  {GRAY}Engine  : {ledger.get('axis_engine','?')}{RESET}")
    print(f"  {GRAY}Version : {ledger.get('version','?')}{RESET}")
    print(f"  {GRAY}Entries : {len(entries)}{RESET}")
    if "last_updated" in ledger:
        print(f"  {GRAY}Updated : {ledger['last_updated']}{RESET}")
    print("")

    if not entries:
        print(f"  {YELLOW}(no canon entries registered){RESET}\n")
        return

    # Table header
    print(f"  {'CANON_ID':<22} {'ENTRIES':>7}  {'CANON_HASH':<28}  {'REGISTERED'}")
    print(f"  {'-'*22} {'-'*7}  {'-'*28}  {'-'*24}")

    for canon_id in entries:
        entry_path = LEDGER_ENTRIES / f"{canon_id}.json"
        if entry_path.exists():
            e = json.loads(entry_path.read_text(encoding="utf-8"))
            print(f"  {e.get('canon_id','?'):<22} {e.get('entries',0):>7}  "
                  f"{e.get('canon_hash','?')[:26]+'...':<28}  "
                  f"{e.get('registered','?')[:19]}")
        else:
            print(f"  {canon_id:<22} {'?':>7}  {'ENTRY FILE MISSING':<28}")

    print(f"\n{GREEN}{'='*62}{RESET}\n")

if __name__ == "__main__":
    main()
