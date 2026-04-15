#!/usr/bin/env python3
"""
💎 AXIS-NIDDHI — generate_concept_map.py
==========================================
Nome:       Concept Map Generator
Versão:     1.0 — Navigator Layer Phase
Autor:      Aloka + Vayo (AXIS-NIDDHI Architect)

PURPOSE:
  Build the AXIS Navigator files from the semantic concept layer.
  Reads semantic/concepts/*.json and CSL slug_map to produce:
    navigator/concept_map.json    ← concept graph with CSL links
    navigator/query_index.json    ← concept → slug lookup
    navigator/learning_paths.json ← preserved if exists, updated otherwise

  ADDITIVE ONLY — never modifies semantic layer or CSL.

USAGE:
  python3 scripts/tools/generate_concept_map.py
  python3 scripts/tools/generate_concept_map.py --regen-paths
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ==============================================================================
# ⚙️  BOOTSTRAP
# ==============================================================================
_SCRIPT_DIR = Path(__file__).resolve().parent
_CORE_DIR   = _SCRIPT_DIR.parent / "core"
if str(_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(_CORE_DIR))

from config import BASE_DIR, DIR_09_CSL, METADATA_DIR

SEMANTIC_DIR   = BASE_DIR / "semantic"
NAVIGATOR_DIR  = BASE_DIR / "navigator"
SLUG_MAP_PATH  = BASE_DIR / "metadata" / "slug_map.json"

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

_PDPN_RE = re.compile(r"^[A-Z]{2}\.[A-Z]{2}\.\d{3}$")


# ==============================================================================
# 🔍  HELPERS
# ==============================================================================
def load_slug_map() -> dict[str, str]:
    """Load pdpn→slug map from metadata/ or CSL meta/."""
    candidates = [
        SLUG_MAP_PATH,
        BASE_DIR / "slug_map.json",
        DIR_09_CSL / "meta" / "slug_map.json",
    ]
    for p in candidates:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {}


def load_csl_pdpns() -> set[str]:
    if not DIR_09_CSL.exists():
        return set()
    return {d.name for d in DIR_09_CSL.iterdir()
            if d.is_dir() and _PDPN_RE.match(d.name)}


def load_concepts() -> dict[str, dict]:
    """Load all concept files from semantic/concepts/."""
    concepts_dir = SEMANTIC_DIR / "concepts"
    if not concepts_dir.exists():
        return {}
    result = {}
    for f in sorted(concepts_dir.glob("*.json")):
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
            result[f.stem] = c
        except Exception as e:
            print(f"  {YELLOW}⚠ Could not load {f.name}: {e}{RESET}")
    return result


# ==============================================================================
# 🗺️  CONCEPT MAP BUILDER
# ==============================================================================
def build_concept_map(concepts: dict, slug_map: dict, csl_pdpns: set) -> dict:
    """Build concept graph nodes from semantic concept files."""
    nodes = {}
    NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for slug, concept in concepts.items():
        # Build CSL entries from occurrences + first_occurrence
        csl_entries = []
        seen_pdpns = set()

        # first_occurrence
        fo = concept.get("first_occurrence", "")
        if fo and _PDPN_RE.match(fo) and fo not in seen_pdpns:
            csl_slug = slug_map.get(fo, "")
            csl_entries.append({"pdpn": fo, "slug": csl_slug})
            seen_pdpns.add(fo)

        # occurrences
        for pdpn in concept.get("occurrences", []):
            if _PDPN_RE.match(pdpn) and pdpn not in seen_pdpns:
                csl_slug = slug_map.get(pdpn, "")
                csl_entries.append({"pdpn": pdpn, "slug": csl_slug})
                seen_pdpns.add(pdpn)

        # Warn on invalid CSL refs
        invalid = [e["pdpn"] for e in csl_entries if e["pdpn"] not in csl_pdpns and csl_pdpns]
        if invalid:
            print(f"  {YELLOW}⚠ {slug}: PDPNs not in CSL: {invalid}{RESET}")

        nodes[slug] = {
            "concept":     slug,
            "pali":        concept.get("pali", slug),
            "type":        concept.get("type", "other"),
            "label":       concept.get("translations", {"en": slug}),
            "edges":       concept.get("related", []),
            "csl_entries": csl_entries,
        }

    edge_count = sum(len(n["edges"]) for n in nodes.values())

    return {
        "layer":       "AXIS-NAVIGATOR",
        "version":     1,
        "corpus":      "puredhamma",
        "generated":   NOW,
        "description": "Semantic concept graph — non-canonical navigation layer.",
        "node_count":  len(nodes),
        "edge_count":  edge_count,
        "nodes":       nodes,
    }


# ==============================================================================
# 🔍  QUERY INDEX BUILDER
# ==============================================================================
def build_query_index(concept_map: dict) -> dict:
    NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index = {}
    for concept_id, node in concept_map["nodes"].items():
        index[concept_id] = {
            "pali":   node["pali"],
            "label":  node["label"].get("en", concept_id),
            "slugs":  [e["slug"] for e in node["csl_entries"] if e.get("slug")],
            "pdpns":  [e["pdpn"] for e in node["csl_entries"]],
        }
    return {
        "layer":       "AXIS-NAVIGATOR",
        "version":     1,
        "corpus":      "puredhamma",
        "generated":   NOW,
        "description": "Concept → CSL slug lookup index",
        "index":       index,
    }


# ==============================================================================
# ✅  VALIDATOR
# ==============================================================================
def validate_navigator(concept_map: dict, learning_paths: dict,
                        slug_map: dict, csl_pdpns: set) -> tuple[bool, list]:
    issues = []
    registered_concepts = set(concept_map["nodes"].keys())

    # Validate concept graph edges
    for slug, node in concept_map["nodes"].items():
        for edge in node.get("edges", []):
            if edge not in registered_concepts:
                issues.append(f"concept/{slug}: edge '{edge}' not registered")

    # Validate learning path PDPNs
    for path_id, path in learning_paths.get("paths", {}).items():
        for step in path.get("steps", []):
            pdpn = step.get("pdpn", "")
            if pdpn and csl_pdpns and pdpn not in csl_pdpns:
                issues.append(f"path/{path_id} step {step.get('step')}: PDPN '{pdpn}' not in CSL")
            if pdpn and not _PDPN_RE.match(pdpn):
                issues.append(f"path/{path_id} step {step.get('step')}: invalid PDPN format '{pdpn}'")

    return len(issues) == 0, issues


# ==============================================================================
# 🚀  MAIN
# ==============================================================================
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regen-paths", action="store_true",
                        help="Regenerate learning_paths.json from scratch (destructive)")
    args = parser.parse_args()

    print(f"\n{CYAN}{'='*62}{RESET}")
    print(f"{CYAN}  💎 AXIS-NIDDHI — Navigator Builder{RESET}")
    print(f"{CYAN}{'='*62}{RESET}\n")

    # Guards
    if not (SEMANTIC_DIR / "index.json").exists():
        print(f"  {RED}❌ Semantic index absent: {SEMANTIC_DIR}/index.json{RESET}")
        return 1

    # Load data
    print(f"  {GRAY}[1/5] Loading semantic concepts...{RESET}")
    concepts = load_concepts()
    if not concepts:
        print(f"  {YELLOW}⚠ No concept files found in {SEMANTIC_DIR}/concepts/{RESET}")
    print(f"     {GRAY}{len(concepts)} concepts loaded{RESET}")

    print(f"  {GRAY}[2/5] Loading slug map...{RESET}")
    slug_map = load_slug_map()
    print(f"     {GRAY}{len(slug_map)} slugs{RESET}")

    print(f"  {GRAY}[3/5] Loading CSL...{RESET}")
    csl_pdpns = load_csl_pdpns()
    print(f"     {GRAY}{len(csl_pdpns)} CSL entries{RESET}")

    NAVIGATOR_DIR.mkdir(parents=True, exist_ok=True)

    # Build concept map
    print(f"  {GRAY}[4/5] Building concept map...{RESET}")
    concept_map = build_concept_map(concepts, slug_map, csl_pdpns)

    # Merge with existing map if present (preserve manually-added CSL entries)
    existing_map_path = NAVIGATOR_DIR / "concept_map.json"
    if existing_map_path.exists() and not args.regen_paths:
        try:
            existing = json.loads(existing_map_path.read_text(encoding="utf-8"))
            for slug, existing_node in existing.get("nodes", {}).items():
                if slug in concept_map["nodes"]:
                    # Merge CSL entries — preserve manually added ones
                    existing_pdpns = {e["pdpn"] for e in existing_node.get("csl_entries", [])}
                    new_pdpns      = {e["pdpn"] for e in concept_map["nodes"][slug].get("csl_entries", [])}
                    merged_pdpns   = new_pdpns | existing_pdpns
                    merged_entries = []
                    seen = set()
                    for e in (concept_map["nodes"][slug]["csl_entries"] +
                              existing_node.get("csl_entries", [])):
                        if e["pdpn"] not in seen:
                            merged_entries.append(e)
                            seen.add(e["pdpn"])
                    concept_map["nodes"][slug]["csl_entries"] = merged_entries
                else:
                    # Preserve nodes not yet in semantic layer
                    concept_map["nodes"][slug] = existing_node
            concept_map["node_count"] = len(concept_map["nodes"])
            concept_map["edge_count"] = sum(len(n["edges"]) for n in concept_map["nodes"].values())
        except Exception:
            pass

    (NAVIGATOR_DIR / "concept_map.json").write_text(
        json.dumps(concept_map, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"     {GRAY}{concept_map['node_count']} nodes, {concept_map['edge_count']} edges{RESET}")

    # Build query index
    print(f"  {GRAY}[5/5] Building query index...{RESET}")
    query_index = build_query_index(concept_map)
    (NAVIGATOR_DIR / "query_index.json").write_text(
        json.dumps(query_index, indent=2, ensure_ascii=False), encoding="utf-8")

    # Load learning paths (preserve if exists unless --regen-paths)
    paths_path = NAVIGATOR_DIR / "learning_paths.json"
    if paths_path.exists() and not args.regen_paths:
        learning_paths = json.loads(paths_path.read_text(encoding="utf-8"))
        print(f"  {GRAY}learning_paths.json preserved ({len(learning_paths.get('paths',{}))} paths){RESET}")
    else:
        learning_paths = {"paths": {}}
        paths_path.write_text(json.dumps(learning_paths, indent=2), encoding="utf-8")

    # Validate
    print(f"\n  {GRAY}Validating...{RESET}")
    ok, issues = validate_navigator(concept_map, learning_paths, slug_map, csl_pdpns)

    warnings = [i for i in issues if "not registered" in i]
    errors   = [i for i in issues if i not in warnings]

    for w in warnings:
        print(f"  {YELLOW}⚠  {w}{RESET}")
    for e in errors:
        print(f"  {RED}✘  {e}{RESET}")

    print("")
    if not errors:
        print(f"{GREEN}{'='*62}{RESET}")
        print(f"{GREEN}  ✅ NAVIGATOR BUILT{RESET}")
        print(f"{'='*62}")
        print(f"  {GRAY}Concepts  : {concept_map['node_count']}{RESET}")
        print(f"  {GRAY}Edges     : {concept_map['edge_count']}{RESET}")
        print(f"  {GRAY}Paths     : {len(learning_paths.get('paths',{}))}{RESET}")
        print(f"  {GRAY}Warnings  : {len(warnings)}{RESET}")
        print(f"{GREEN}{'='*62}{RESET}\n")
        return 0
    else:
        print(f"{RED}{'='*62}{RESET}")
        print(f"{RED}  ❌ NAVIGATOR BUILD FAILED ({len(errors)} errors){RESET}")
        print(f"{RED}{'='*62}{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
