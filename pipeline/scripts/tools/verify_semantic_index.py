#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — verify_semantic_index.py
==========================================
Nome:       Semantic Index Verifier
Versão:     1.0 — Semantic Layer Phase
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)

PURPOSE:
  Verify the semantic concept index:
    1. semantic/index.json lists only concepts that have files
    2. Each concept file conforms to the concept schema
    3. first_occurrence and occurrences reference valid PDPN entries in CSL
    4. related[] concepts reference registered concept slugs
    5. glossary_refs[] terms exist in Glossario_v5.csv (if available)

  Additive only — never modifies semantic layer or CSL.

EXIT CODES:
  0 = SEMANTIC INDEX VERIFIED
  1 = VERIFICATION FAILURE
  2 = INDEX ABSENT

USAGE:
  python3 scripts/tools/verify_semantic_index.py
  python3 scripts/tools/verify_semantic_index.py --strict
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
_CORE_DIR   = _SCRIPT_DIR.parent / "core"
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from config import BASE_DIR, DIR_09_CSL, METADATA_DIR

SEMANTIC_DIR      = BASE_DIR / "semantic"
SEMANTIC_INDEX    = SEMANTIC_DIR / "index.json"
CONCEPTS_DIR      = SEMANTIC_DIR / "concepts"
GLOSSARY_CSV      = METADATA_DIR.parent / "metadata" / "Glossario_v5.csv"

_PDPN_RE          = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")
VALID_TYPES       = {
    "dhamma_characteristic", "attainment", "practice", "mental_factor",
    "doctrine", "person", "place", "text", "other"
}
REQUIRED_FIELDS   = {"concept", "type", "pali", "translations", "first_occurrence", "related"}

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GRAY   = "\033[90m"
RESET  = "\033[0m"


# ==============================================================================
# 🔍  HELPERS
# ==============================================================================
def load_csl_pdpns() -> set[str]:
    if not DIR_09_CSL.exists():
        return set()
    return {d.name for d in DIR_09_CSL.iterdir()
            if d.is_dir() and _PDPN_RE.match(d.name)}


def load_glossary_terms() -> set[str]:
    # Try multiple possible locations
    candidates = [
        METADATA_DIR / "Glossario_v5.csv",
        BASE_DIR / "metadata" / "Glossario_v5.csv",
        BASE_DIR / "Glossario_v5.csv",
    ]
    for path in candidates:
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    return {row.get("Pali Canon","").strip() for row in reader
                            if row.get("Pali Canon","").strip()}
            except Exception:
                pass
    return set()


def check(label: str, ok: bool, msg: str = "", width: int = 36) -> bool:
    if ok:
        print(f"  {GREEN}✔{RESET}  {label:<{width}}")
    else:
        print(f"  {RED}✘{RESET}  {label:<{width}}  {RED}{msg}{RESET}")
    return ok


def warn(label: str, msg: str = "", width: int = 36):
    print(f"  {YELLOW}⚠{RESET}  {label:<{width}}  {YELLOW}{msg}{RESET}")


# ==============================================================================
# 🔍  CONCEPT VERIFICATION
# ==============================================================================
def verify_concept_file(path: Path, csl_pdpns: set, glossary_terms: set,
                         registered_concepts: set, strict: bool) -> tuple[bool, int]:
    """Returns (all_pass, warning_count)."""
    issues    = []
    warnings  = 0

    try:
        concept = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  {RED}✘ JSON parse error: {path.name}: {e}{RESET}")
        return False, 0

    slug = path.stem

    # Required fields
    missing = REQUIRED_FIELDS - set(concept.keys())
    if missing:
        issues.append(f"missing fields: {missing}")

    # concept slug matches filename
    if concept.get("concept") != slug:
        issues.append(f"concept field '{concept.get('concept')}' != filename '{slug}'")

    # type valid
    ctype = concept.get("type","")
    if ctype not in VALID_TYPES:
        issues.append(f"invalid type: '{ctype}' — valid: {sorted(VALID_TYPES)}")

    # translations is dict with at least 'en'
    trans = concept.get("translations", {})
    if not isinstance(trans, dict) or "en" not in trans:
        issues.append("translations must be dict with at least 'en' key")

    # first_occurrence is valid PDPN (if set and CSL available)
    fo = concept.get("first_occurrence","")
    if fo and csl_pdpns and not _PDPN_RE.match(fo):
        issues.append(f"first_occurrence '{fo}' is not a valid PDPN")
    elif fo and csl_pdpns and _PDPN_RE.match(fo) and fo not in csl_pdpns:
        if strict:
            issues.append(f"first_occurrence '{fo}' not found in CSL")
        else:
            warn(f"  {slug} first_occurrence", f"'{fo}' not in CSL (non-blocking)")
            warnings += 1

    # occurrences: all valid PDPNs
    for pdpn in concept.get("occurrences", []):
        if not _PDPN_RE.match(pdpn):
            issues.append(f"invalid PDPN in occurrences: '{pdpn}'")
        elif csl_pdpns and pdpn not in csl_pdpns:
            if strict:
                issues.append(f"occurrence '{pdpn}' not found in CSL")
            else:
                warnings += 1

    # related: all registered concepts (warn if not found — may be added later)
    for rel in concept.get("related", []):
        if registered_concepts and rel not in registered_concepts:
            warn(f"  {slug} related", f"'{rel}' not yet registered (non-blocking)")
            warnings += 1

    # glossary_refs: warn if not in glossary (non-blocking)
    if glossary_terms:
        for ref in concept.get("glossary_refs", []):
            if ref not in glossary_terms:
                warn(f"  {slug} glossary_ref", f"'{ref}' not in Glossario_v5 (non-blocking)")
                warnings += 1

    ok = len(issues) == 0
    status = f"{GREEN}✔{RESET}" if ok else f"{RED}✘{RESET}"
    detail = f"  {RED}{'; '.join(issues)}{RESET}" if issues else ""
    print(f"  {status}  concept/{slug:<28} type={ctype}{detail}")

    return ok, warnings


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="Treat CSL-reference warnings as errors")
    args = parser.parse_args()

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — SA_S Semantic Index Verifier{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    if not SEMANTIC_INDEX.exists():
        print(f"  {RED}❌ Semantic index absent: {SEMANTIC_INDEX}{RESET}")
        print("   Run: axis semantic add <concept>")
        return 2

    index = json.loads(SEMANTIC_INDEX.read_text(encoding="utf-8"))

    # Load reference data
    print(f"  {GRAY}Loading CSL...{RESET}")
    csl_pdpns = load_csl_pdpns()
    print(f"  {GRAY}CSL entries: {len(csl_pdpns)}{RESET}")

    print(f"  {GRAY}Loading glossary...{RESET}")
    glossary_terms = load_glossary_terms()
    if glossary_terms:
        print(f"  {GRAY}Glossary terms: {len(glossary_terms)}{RESET}")
    else:
        warn("Glossary", "Glossario_v5.csv not found — glossary_refs not verified")

    # All registered concept slugs
    registered_concepts = set(index.get("concepts", []))

    # Collect concept files
    concept_files = sorted(CONCEPTS_DIR.glob("*.json")) if CONCEPTS_DIR.exists() else []

    print(f"\n  {GRAY}Index declares: {len(registered_concepts)} concepts{RESET}")
    print(f"  {GRAY}Files found   : {len(concept_files)}{RESET}\n")

    results   = []
    total_warn = 0

    # CHECK 1: index lists only concepts with files
    file_slugs = {f.stem for f in concept_files}
    orphan_in_index  = registered_concepts - file_slugs
    orphan_in_files  = file_slugs - registered_concepts

    if orphan_in_index:
        for slug in sorted(orphan_in_index):
            print(f"  {RED}✘  index entry '{slug}' has no concept file{RESET}")
        results.append(False)
    else:
        print(f"  {GREEN}✔  index/files consistent{RESET}")
        results.append(True)

    if orphan_in_files:
        for slug in sorted(orphan_in_files):
            warn("unregistered concept file", f"'{slug}' exists but not in index.json")
        total_warn += len(orphan_in_files)

    print("")

    # CHECK 2: verify each concept file
    for fpath in concept_files:
        ok, w = verify_concept_file(fpath, csl_pdpns, glossary_terms,
                                     file_slugs, args.strict)
        results.append(ok)
        total_warn += w

    # RESULT
    all_pass   = all(results)
    pass_count = sum(results)

    print("")
    if all_pass:
        print(f"{GREEN}{'='*62}{RESET}")
        print(f"{GREEN}  ✅ SEMANTIC INDEX VERIFIED{RESET}")
        print(f"{'='*62}")
        print(f"  {GRAY}Concepts  : {len(concept_files)}{RESET}")
        print(f"  {GRAY}Warnings  : {total_warn}{RESET}")
        print(f"{GREEN}{'='*62}{RESET}\n")
        return 0
    else:
        failures = results.count(False)
        print(f"{RED}{'='*62}{RESET}")
        print(f"{RED}  ❌ SEMANTIC INDEX VERIFICATION FAILURE{RESET}")
        print(f"{'='*62}")
        print(f"  {RED}{failures} check(s) failed{RESET}")
        print(f"{RED}{'='*62}{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
