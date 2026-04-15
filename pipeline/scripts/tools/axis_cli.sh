#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — axis_cli.sh
# Canon Compiler Interface V1.9
# ==============================================================================
# Canonical entrypoint for the AXIS-NIDDHI Canon Compilation Engine.
#
# USAGE:
#   axis build    → run full pipeline (SG → SP → SA → SD)
#   axis verify   → run integrity guard
#   axis report   → run mission report
#   axis manifest → generate canon manifest only
#   axis serve    → serve static site at localhost:8080
#   axis package  → package sojourner / steward distributions
#   axis corpus   → corpus registry commands
#   axis tag      → create canon release tag
#   axis seed     → canon seed (generate, verify)
#   axis ledger   → canon ledger (add, list, verify)
#   axis mirror   → mirror protocol (sync, list, endpoint)
#   axis semantic → semantic concept index
#   axis navigator → concept map + study paths
#   axis capsule  → time capsule (build)
#   axis help     → show this message
#
# ENV:
#   BENG_BASE=/path/to/pipeline  (auto-detected if not set)
# ==============================================================================

set -euo pipefail

# ==============================================================================
# PATH RESOLUTION
# ==============================================================================
# axis_cli.sh lives in scripts/tools/ → scripts/ is parent → pipeline/ is grandparent
_SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
BENG_BASE="${BENG_BASE:-$(cd "$_SELF_DIR/../.." && pwd)}"
CORE_DIR="$BENG_BASE/scripts/core"

# Colours
GREEN='\033[0;32m'
CYAN='\033[0;96m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

# ==============================================================================
# GUARD
# ==============================================================================
if [ ! -d "$CORE_DIR" ]; then
    echo -e "${RED}❌ AXIS: scripts/core/ not found at: $BENG_BASE${NC}"
    echo "   Set BENG_BASE=/path/to/pipeline and retry."
    exit 1
fi

# ==============================================================================
# COMMANDS
# ==============================================================================

cmd_build() {
    echo -e "\n${CYAN}💎 AXIS → BUILD${NC}"
    echo -e "   ${GRAY}Pipeline: SG → SP → SA → SD${NC}"
    echo -e "   ${GRAY}Base: $BENG_BASE${NC}\n"
    BENG_BASE="$BENG_BASE" bash "$CORE_DIR/run_full_pipeline.sh" --full
}

cmd_verify() {
    local SUBCMD="${1:-pipeline}"
    case "$SUBCMD" in
        canon)
            echo -e "\n${CYAN}💎 AXIS → VERIFY CANON${NC}"
            BENG_BASE="$BENG_BASE" python3 "$CORE_DIR/SA05_verify_canon_integrity.py"
            ;;
        pipeline|*)
            echo -e "\n${CYAN}💎 AXIS → VERIFY PIPELINE${NC}"
            BENG_BASE="$BENG_BASE" bash "$CORE_DIR/verify_pipeline_integrity.sh"
            ;;
    esac
}

cmd_report() {
    echo -e "\n${CYAN}💎 AXIS → REPORT${NC}"
    BENG_BASE="$BENG_BASE" python3 "$CORE_DIR/MI99_mission_report.py"
}

cmd_manifest() {
    echo -e "\n${CYAN}💎 AXIS → CANON MANIFEST${NC}"
    BENG_BASE="$BENG_BASE" python3 "$CORE_DIR/SA04_generate_canon_manifest.py"
}

cmd_serve() {
    local port="${1:-8080}"
    local site_dir="$BENG_BASE/13-static-site"
    if [ ! -d "$site_dir" ]; then
        echo -e "${RED}❌ Static site not found: $site_dir${NC}"
        echo "   Run: axis build"
        exit 1
    fi
    echo -e "\n${CYAN}💎 AXIS → SERVE${NC}"
    echo -e "   ${GRAY}Site: $site_dir${NC}"
    echo -e "   ${GREEN}Open: http://localhost:$port${NC}\n"
    cd "$site_dir" && python3 -m http.server "$port"
}


cmd_version() {
    echo -e "\n${CYAN}  💎 AXIS-NIDDHI Canon Compiler Interface V1.9${NC}"
    echo -e "  ${GRAY}Engine    : AXIS-NIDDHI${NC}"
    echo -e "  ${GRAY}Codename  : NIDDHI${NC}"
    echo -e "  ${GRAY}Corpus    : puredhamma (748 entries)${NC}"
    echo -e "  ${GRAY}CLI       : V1.9${NC}"
    echo -e "  ${GRAY}Scripts   : 34 (core) + tools${NC}"
    echo -e "  ${GRAY}Layers    : build · verify · report · manifest · serve${NC}"
    echo -e "  ${GRAY}          : package · corpus · tag · seed · ledger${NC}"
    echo -e "  ${GRAY}          : mirror · semantic · navigator · capsule${NC}\n"
}


cmd_capsule() {
    local SUBCMD="${1:-build}"
    local TOOLS_DIR="$BENG_BASE/scripts/tools"
    local CAPSULE_DIR="$BENG_BASE/capsule"

    case "$SUBCMD" in
        build)
            echo -e "\n${CYAN}💎 AXIS → CAPSULE BUILD${NC}"
            BENG_BASE="$BENG_BASE" bash "$TOOLS_DIR/build_time_capsule.sh"
            ;;
        verify)
            echo -e "\n${CYAN}💎 AXIS → CAPSULE VERIFY${NC}"
            python3 - << PYEOF
import json, hashlib
from pathlib import Path

capsule = Path("$CAPSULE_DIR")
manifest_path = capsule / "capsule_manifest.json"

if not manifest_path.exists():
    print("  ❌ capsule_manifest.json not found — run: axis capsule build")
    exit(1)

manifest = json.loads(manifest_path.read_text())
declared_hash = manifest.get("capsule_hash","")
declared_files = manifest.get("file_count", 0)

# Recompute
h = hashlib.sha256()
file_count = 0
for f in sorted(capsule.rglob("*")):
    if f.is_file() and f.name != "capsule_manifest.json":
        h.update(str(f.relative_to(capsule)).encode())
        h.update(f.read_bytes())
        file_count += 1

actual_hash = h.hexdigest()

print(f"  declared_hash : {declared_hash[:32]}...")
print(f"  actual_hash   : {actual_hash[:32]}...")
print(f"  files declared: {declared_files}")
print(f"  files found   : {file_count}")

if declared_hash == actual_hash and declared_files == file_count:
    print("\n  ✅ CAPSULE VERIFIED — integrity intact")
else:
    print("\n  ❌ CAPSULE INTEGRITY FAILURE")
    exit(1)
PYEOF
            ;;
        info)
            echo -e "\n${CYAN}💎 AXIS → CAPSULE INFO${NC}"
            python3 - << PYEOF
import json
from pathlib import Path
m = Path("$CAPSULE_DIR/README_MACHINES.json")
if not m.exists():
    print("  No capsule found — run: axis capsule build")
else:
    d = json.loads(m.read_text())
    print(f"  Engine   : {d.get('engine')} {d.get('engine_version')}")
    print(f"  Built    : {d.get('built')}")
    print(f"  Corpus   : {d.get('corpus',{}).get('name')} ({d.get('corpus',{}).get('entries')} entries)")
    print(f"  Layers   : {', '.join(d.get('layers',{}).keys())}")
    print()
    print(f"  Hashes:")
    for k,v in d.get("hashes",{}).items():
        print(f"    {k:<20} {v[:32]}...")
PYEOF
            ;;
        *)
            echo -e "${RED}❌ Usage: axis capsule <build|verify|info>${NC}"
            echo -e "  ${GREEN}axis capsule build${NC}   Build time capsule from all live layers"
            echo -e "  ${GREEN}axis capsule verify${NC}  Verify capsule integrity"
            echo -e "  ${GREEN}axis capsule info${NC}    Show capsule metadata"
            exit 1
            ;;
    esac
}


cmd_navigator() {
    local SUBCMD="${1:-}"
    local TOOLS_DIR="$BENG_BASE/scripts/tools"
    local NAV_DIR="$BENG_BASE/navigator"

    case "$SUBCMD" in
        build)
            echo -e "\n${CYAN}💎 AXIS → NAVIGATOR BUILD${NC}"
            BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/generate_concept_map.py"
            ;;
        paths)
            echo -e "\n${CYAN}💎 AXIS → NAVIGATOR PATHS${NC}"
            python3 - << PYEOF
import json
from pathlib import Path
p = Path("$NAV_DIR/learning_paths.json")
if not p.exists():
    print("  learning_paths.json not found — run: axis navigator build")
else:
    lp = json.loads(p.read_text())
    paths = lp.get("paths", {})
    print(f"  Paths: {len(paths)}\n")
    for pid, path in paths.items():
        title = path.get("title",{}).get("en", pid)
        level = path.get("level","?")
        steps = len(path.get("steps",[]))
        concepts = ", ".join(path.get("concepts",[]))
        print(f"  [{pid}]")
        print(f"    Title    : {title}")
        print(f"    Level    : {level}")
        print(f"    Steps    : {steps}")
        print(f"    Concepts : {concepts}")
        print()
PYEOF
            ;;
        map)
            echo -e "\n${CYAN}💎 AXIS → NAVIGATOR MAP${NC}"
            python3 - << PYEOF
import json
from pathlib import Path
p = Path("$NAV_DIR/concept_map.json")
if not p.exists():
    print("  concept_map.json not found — run: axis navigator build")
else:
    cm = json.loads(p.read_text())
    print(f"  Nodes : {cm.get('node_count',0)}")
    print(f"  Edges : {cm.get('edge_count',0)}")
    print(f"  Built : {cm.get('generated','?')}")
    print()
    print(f"  {'CONCEPT':<24} {'TYPE':<22} {'EDGES':<6} {'CSL'}")
    print(f"  {'-'*24} {'-'*22} {'-'*6} {'-'*4}")
    for slug, node in cm.get("nodes",{}).items():
        edges = ", ".join(node.get("edges",[]))
        csl_n = len(node.get("csl_entries",[]))
        print(f"  {slug:<24} {node.get('type','?'):<22} {len(node.get('edges',[])):<6} {csl_n}")
PYEOF
            ;;
        query)
            local CONCEPT="${2:-}"
            if [ -z "$CONCEPT" ]; then
                echo -e "${RED}❌ Usage: axis navigator query <concept_slug>${NC}"
                exit 1
            fi
            echo -e "\n${CYAN}💎 AXIS → NAVIGATOR QUERY: $CONCEPT${NC}"
            python3 - << PYEOF
import json
from pathlib import Path
qi = Path("$NAV_DIR/query_index.json")
if not qi.exists():
    print("  query_index.json not found — run: axis navigator build")
else:
    idx = json.loads(qi.read_text()).get("index", {})
    if "$CONCEPT" not in idx:
        print(f"  Concept not found: $CONCEPT")
    else:
        c = idx["$CONCEPT"]
        print(f"  Pali  : {c.get('pali','?')}")
        print(f"  Label : {c.get('label','?')}")
        print(f"  Posts : {len(c.get('slugs',[]))}")
        print()
        for pdpn, slug in zip(c.get("pdpns",[]), c.get("slugs",[])):
            print(f"    {pdpn}  {slug}")
PYEOF
            ;;
        *)
            echo -e "${RED}❌ Usage: axis navigator <build|paths|map|query> [args]${NC}"
            echo -e "  ${GREEN}axis navigator build${NC}           Build concept map + query index"
            echo -e "  ${GREEN}axis navigator paths${NC}           List study paths"
            echo -e "  ${GREEN}axis navigator map${NC}             Show concept graph"
            echo -e "  ${GREEN}axis navigator query <slug>${NC}    Query CSL entries for concept"
            exit 1
            ;;
    esac
}


cmd_semantic() {
    local SUBCMD="${1:-}"
    local TOOLS_DIR="$BENG_BASE/scripts/tools"
    local SEMANTIC_DIR="$BENG_BASE/semantic"
    local INDEX="$SEMANTIC_DIR/index.json"
    local CONCEPTS_DIR="$SEMANTIC_DIR/concepts"

    case "$SUBCMD" in
        list)
            echo -e "\n${CYAN}💎 AXIS → SEMANTIC LIST${NC}"
            python3 - << PYEOF
import json
from pathlib import Path
index_path = Path("$INDEX")
if not index_path.exists():
    print("  Semantic index not initialized.")
else:
    index = json.loads(index_path.read_text())
    concepts = index.get("concepts", [])
    concepts_dir = Path("$CONCEPTS_DIR")
    print(f"  Layer   : {index.get('layer','?')}")
    print(f"  Version : {index.get('version','?')}")
    print(f"  Corpus  : {index.get('corpus','?')}")
    print(f"  Concepts: {len(concepts)}")
    print()
    if concepts:
        print(f"  {'CONCEPT':<24} {'TYPE':<24} {'PALI'}")
        print(f"  {'-'*24} {'-'*24} {'-'*20}")
        for slug in sorted(concepts):
            cf = concepts_dir / f"{slug}.json"
            if cf.exists():
                c = json.loads(cf.read_text())
                print(f"  {slug:<24} {c.get('type','?'):<24} {c.get('pali','?')}")
            else:
                print(f"  {slug:<24} {'FILE MISSING':<24}")
    else:
        print("  (no concepts registered)")
PYEOF
            ;;
        add)
            local CONCEPT="${2:-}"
            if [ -z "$CONCEPT" ]; then
                echo -e "${RED}❌ Usage: axis semantic add <concept_slug>${NC}"
                echo -e "   Example: axis semantic add anicca"
                exit 1
            fi
            echo -e "\n${CYAN}💎 AXIS → SEMANTIC ADD: $CONCEPT${NC}"
            mkdir -p "$CONCEPTS_DIR"
            local CONCEPT_FILE="$CONCEPTS_DIR/${CONCEPT}.json"
            if [ -f "$CONCEPT_FILE" ]; then
                echo -e "  ${YELLOW}⚠ Concept already exists: $CONCEPT${NC}"
                echo -e "  Edit: $CONCEPT_FILE"
            else
                python3 - << PYEOF
import json
from datetime import datetime, timezone
from pathlib import Path
concept = {
    "concept":          "$CONCEPT",
    "type":             "other",
    "pali":             "$CONCEPT",
    "translations":     {"en": "$CONCEPT", "pt-BR": ""},
    "description":      "",
    "first_occurrence": "",
    "occurrences":      [],
    "related":          [],
    "glossary_refs":    [],
    "schema_version":   "1.0"
}
path = Path("$CONCEPT_FILE")
path.write_text(json.dumps(concept, indent=2, ensure_ascii=False))
# Register in index
index_path = Path("$INDEX")
if index_path.exists():
    idx = json.loads(index_path.read_text())
else:
    idx = {"layer":"AXIS-SEMANTIC","version":1,"corpus":"puredhamma","concepts":[]}
if "$CONCEPT" not in idx["concepts"]:
    idx["concepts"].append("$CONCEPT")
    idx["concepts"] = sorted(idx["concepts"])
    idx["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False))
print(f"  ✅ Concept stub created: {path}")
print(f"  Edit to complete: type, pali, translations, first_occurrence, related")
PYEOF
            fi
            ;;
        verify)
            echo -e "\n${CYAN}💎 AXIS → SEMANTIC VERIFY${NC}"
            BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/verify_semantic_index.py"
            ;;
        *)
            echo -e "${RED}❌ Usage: axis semantic <list|add|verify> [args]${NC}"
            echo -e "  ${GREEN}axis semantic list${NC}           List all concepts"
            echo -e "  ${GREEN}axis semantic add <slug>${NC}     Add concept stub"
            echo -e "  ${GREEN}axis semantic verify${NC}         Verify concept files"
            exit 1
            ;;
    esac
}


cmd_mirror() {
    local SUBCMD="${1:-}"
    local TOOLS_DIR="$BENG_BASE/scripts/tools"

    case "$SUBCMD" in
        sync)
            local MIRROR_URL="${2:-}"
            echo -e "\n${CYAN}💎 AXIS → MIRROR SYNC${NC}"
            if [ -n "$MIRROR_URL" ]; then
                BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/mirror_sync.py" --mirror "$MIRROR_URL"
            else
                BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/mirror_sync.py"
            fi
            ;;
        sync-dry)
            local MIRROR_URL="${2:-}"
            echo -e "\n${CYAN}💎 AXIS → MIRROR SYNC (DRY-RUN)${NC}"
            if [ -n "$MIRROR_URL" ]; then
                BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/mirror_sync.py" --dry-run --mirror "$MIRROR_URL"
            else
                BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/mirror_sync.py" --dry-run
            fi
            ;;
        list)
            echo -e "\n${CYAN}💎 AXIS → MIRROR LIST${NC}"
            python3 - << PYEOF
import json
from pathlib import Path
mirrors_json = Path("$BENG_BASE/mirror/mirrors.json")
if not mirrors_json.exists():
    print("  No mirrors configured.")
else:
    cfg = json.loads(mirrors_json.read_text())
    mirrors = cfg.get("mirrors", [])
    if not mirrors:
        print("  No mirrors configured.")
    else:
        for m in mirrors:
            print(f"  {m.get('name','?'):<20} {m.get('url','?')}")
PYEOF
            ;;
        endpoint)
            echo -e "\n${CYAN}💎 AXIS → MIRROR ENDPOINT BUILD${NC}"
            BENG_BASE="$BENG_BASE" bash "$TOOLS_DIR/build_mirror_endpoint.sh"
            ;;
        add)
            local MIRROR_URL="${2:-}"
            local MIRROR_NAME="${3:-$2}"
            if [ -z "$MIRROR_URL" ]; then
                echo -e "${RED}❌ Usage: axis mirror add <url> [name]${NC}"
                exit 1
            fi
            echo -e "\n${CYAN}💎 AXIS → MIRROR ADD: $MIRROR_NAME${NC}"
            python3 - << PYEOF
import json
from datetime import datetime, timezone
from pathlib import Path
mirrors_json = Path("$BENG_BASE/mirror/mirrors.json")
cfg = json.loads(mirrors_json.read_text())
for m in cfg.get("mirrors",[]):
    if m.get("url") == "$MIRROR_URL":
        print("  Already registered:", "$MIRROR_URL")
        exit(0)
cfg.setdefault("mirrors",[]).append({
    "name": "$MIRROR_NAME",
    "url":  "$MIRROR_URL",
    "added": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
})
mirrors_json.write_text(json.dumps(cfg, indent=2))
print("  ✅ Mirror added:", "$MIRROR_NAME", "→", "$MIRROR_URL")
PYEOF
            ;;
        *)
            echo -e "${RED}❌ Usage: axis mirror <sync|list|endpoint|add> [args]${NC}"
            echo -e "  ${GREEN}axis mirror sync${NC}               Sync from all configured mirrors"
            echo -e "  ${GREEN}axis mirror sync <url>${NC}         Sync from specific mirror URL"
            echo -e "  ${GREEN}axis mirror sync-dry${NC}           Dry-run sync (no writes)"
            echo -e "  ${GREEN}axis mirror list${NC}               List configured mirrors"
            echo -e "  ${GREEN}axis mirror add <url> [name]${NC}   Add a mirror"
            echo -e "  ${GREEN}axis mirror endpoint${NC}           Build local mirror endpoint"
            exit 1
            ;;
    esac
}


cmd_ledger() {
    local SUBCMD="${1:-}"
    local TOOLS_DIR="$BENG_BASE/scripts/tools"

    case "$SUBCMD" in
        add)
            local TAG="${2:-puredhamma-v1}"
            local CORPUS="${3:-puredhamma}"
            echo -e "\n${CYAN}💎 AXIS → LEDGER ADD: $TAG${NC}"
            BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/add_canon_to_ledger.py"                 --tag "$TAG" --corpus "$CORPUS"
            ;;
        list)
            echo -e "\n${CYAN}💎 AXIS → LEDGER LIST${NC}"
            BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/list_ledger.py"
            ;;
        verify)
            local ENTRY="${2:-}"
            echo -e "\n${CYAN}💎 AXIS → LEDGER VERIFY${NC}"
            if [ -n "$ENTRY" ]; then
                BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/verify_ledger.py" --entry "$ENTRY"
            else
                BENG_BASE="$BENG_BASE" python3 "$TOOLS_DIR/verify_ledger.py"
            fi
            ;;
        *)
            echo -e "${RED}❌ Usage: axis ledger <add|list|verify> [args]${NC}"
            echo -e "  ${GREEN}axis ledger add${NC}                Add current build to ledger"
            echo -e "  ${GREEN}axis ledger add <tag> <corpus>${NC} Add with explicit tag"
            echo -e "  ${GREEN}axis ledger list${NC}               List all entries"
            echo -e "  ${GREEN}axis ledger verify${NC}             Verify all entries"
            echo -e "  ${GREEN}axis ledger verify <entry>${NC}     Verify single entry"
            exit 1
            ;;
    esac
}


cmd_seed() {
    local SUBCMD="${1:-}"
    local TOOLS_DIR="$BENG_BASE/scripts/tools"

    case "$SUBCMD" in
        generate)
            local CORPUS_ID="${2:-puredhamma}"
            echo -e "\n${CYAN}💎 AXIS → SEED GENERATE: $CORPUS_ID${NC}"
            BENG_BASE="$BENG_BASE" CORPUS_ID="$CORPUS_ID"                 bash "$TOOLS_DIR/generate_canon_seed.sh"
            ;;
        verify)
            local SEED_PATH="${2:-seeds/puredhamma_seed}"
            echo -e "\n${CYAN}💎 AXIS → SEED VERIFY: $SEED_PATH${NC}"
            BENG_BASE="$BENG_BASE"                 bash "$TOOLS_DIR/verify_canon_seed.sh" "$SEED_PATH"
            ;;
        *)
            echo -e "${RED}❌ Usage: axis seed <generate|verify> [args]${NC}"
            echo -e "  ${GREEN}axis seed generate${NC}              Generate puredhamma seed"
            echo -e "  ${GREEN}axis seed generate <corpus_id>${NC}  Generate seed for corpus"
            echo -e "  ${GREEN}axis seed verify <seed_path>${NC}    Verify a seed directory"
            exit 1
            ;;
    esac
}


cmd_tag() {
    local CORPUS_ID="${1:-puredhamma}"
    local VERSION="${2:-v1}"
    echo -e "\n${CYAN}💎 AXIS → TAG: ${CORPUS_ID}-${VERSION}${NC}"
    BENG_BASE="$BENG_BASE" bash "$BENG_BASE/scripts/tools/create_release_tag.sh" "$CORPUS_ID" "$VERSION"
}


cmd_corpus() {
    local SUBCMD="${1:-list}"
    local CORPUS_DIR="$BENG_BASE/corpus"

    case "$SUBCMD" in
        list)
            echo -e "\n${CYAN}💎 AXIS → CORPUS LIST${NC}"
            if [ ! -d "$CORPUS_DIR" ]; then
                echo -e "  ${YELLOW}⚠ No corpus registry found at: $CORPUS_DIR${NC}"
                exit 1
            fi
            local found=0
            for d in "$CORPUS_DIR"/*/; do
                if [ -f "$d/corpus.json" ]; then
                    local cname
                    cname=$(python3 -c "import json; print(json.load(open('$d/corpus.json')).get('corpus_id','?'))" 2>/dev/null || basename "$d")
                    echo "  $cname"
                    found=$((found+1))
                fi
            done
            [ "$found" -eq 0 ] && echo -e "  ${YELLOW}(no corpora registered)${NC}"
            echo ""
            ;;
        info)
            local CORPUS_ID="${2:-}"
            if [ -z "$CORPUS_ID" ]; then
                echo -e "${RED}❌ Usage: axis corpus info <corpus_id>${NC}"
                exit 1
            fi
            local CORPUS_JSON="$CORPUS_DIR/$CORPUS_ID/corpus.json"
            if [ ! -f "$CORPUS_JSON" ]; then
                echo -e "${RED}❌ Corpus not found: $CORPUS_ID${NC}"
                exit 1
            fi
            echo -e "\n${CYAN}💎 AXIS → CORPUS INFO: $CORPUS_ID${NC}"
            python3 - << PYEOF
import json
d = json.load(open('$CORPUS_JSON'))
print('  Name       :', d.get('corpus_name','?'))
print('  Entries    :', d.get('entries','?'))
print('  Languages  :', d.get('languages',[]))
print('  Translations:', str(d.get('translations_frozen',0)) + ' frozen')
print('  Source     :', d.get('source_type','?'))
print('  Engine     :', d.get('engine','?'), 'V' + str(d.get('engine_version','?')))
PYEOF
            echo ""
            ;;
        *)
            echo -e "${RED}❌ Unknown corpus subcommand: $SUBCMD${NC}"
            echo -e "  Valid: list, info <corpus_id>"
            exit 1
            ;;
    esac
}


cmd_package() {
    local TIER="${1:-}"
    local TOOLS_DIR="$BENG_BASE/scripts/tools"

    if [ -z "$TIER" ]; then
        echo -e "\n${YELLOW}Usage: axis package <tier>${NC}"
        echo -e "  ${GREEN}axis package sojourner${NC}  → offline viewer distribution"
        echo -e "  ${GREEN}axis package steward${NC}    → full rebuild distribution"
        echo ""
        exit 1
    fi

    case "$TIER" in
        sojourner)
            echo -e "\n${CYAN}💎 AXIS → PACKAGE SOJOURNER${NC}"
            BENG_BASE="$BENG_BASE" bash "$TOOLS_DIR/package_sojourner_distribution.sh"
            ;;
        steward)
            echo -e "\n${CYAN}💎 AXIS → PACKAGE STEWARD${NC}"
            BENG_BASE="$BENG_BASE" bash "$TOOLS_DIR/package_steward_distribution.sh"
            ;;
        *)
            echo -e "${RED}❌ Unknown tier: $TIER${NC}"
            echo -e "  Valid: sojourner, steward"
            exit 1
            ;;
    esac
}

cmd_help() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  💎 AXIS-NIDDHI Canon Compiler Interface V1.9        ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}axis build${NC}      Full pipeline rebuild (SG→SP→SA→SD)"
    echo -e "  ${GREEN}axis verify${NC}     Integrity guard (30 core scripts + CSL)"
    echo -e "  ${GREEN}axis report${NC}     Mission intelligence report"
    echo -e "  ${GREEN}axis manifest${NC}   Generate cryptographic canon manifest"
    echo -e "  ${GREEN}axis serve${NC}      Serve static site at localhost:8080"
    echo -e "  ${GREEN}axis package${NC}    Package sojourner / steward distribution"
    echo -e "  ${GREEN}axis corpus${NC}     Corpus registry (list, info <id>)"
    echo -e "  ${GREEN}axis verify canon${NC} Verify canon component hashes"
    echo -e "  ${GREEN}axis tag${NC}        Create canon release tag"
    echo -e "  ${GREEN}axis seed${NC}       Canon seed (generate, verify)"
    echo -e "  ${GREEN}axis ledger${NC}     Canon ledger (add, list, verify)"
    echo -e "  ${GREEN}axis mirror${NC}     Mirror protocol (sync, list, endpoint, add)"
    echo -e "  ${GREEN}axis semantic${NC}   Semantic concept index (list, add, verify)"
    echo -e "  ${GREEN}axis navigator${NC}  Concept map + study paths"
    echo -e "  ${GREEN}axis capsule${NC}    Time capsule (build, verify, info)"
    echo -e "  ${GREEN}axis version${NC}    Show engine version"
    echo -e "  ${GREEN}axis help${NC}       Show this message"
    echo ""
    echo -e "  ${GRAY}Base: $BENG_BASE${NC}"
    echo -e "  ${GRAY}Core: $CORE_DIR${NC}"
    echo ""
}

# ==============================================================================
# DISPATCH
# ==============================================================================
CMD="${1:-help}"

case "$CMD" in
    build)    cmd_build ;;
    verify)   cmd_verify "${2:-pipeline}" ;;
    report)   cmd_report ;;
    manifest) cmd_manifest ;;
    serve)    cmd_serve "${2:-8080}" ;;
    package)  cmd_package "${2:-}" ;;
    corpus)   cmd_corpus "${2:-list}" "${3:-}" ;;
    tag)      cmd_tag "${2:-puredhamma}" "${3:-v1}" ;;
    seed)     cmd_seed "${2:-}" "${3:-}" ;;
    ledger)   cmd_ledger "${2:-}" "${3:-}" "${4:-}" ;;
    mirror)   cmd_mirror "${2:-}" "${3:-}" "${4:-}" ;;
    semantic)  cmd_semantic "${2:-}" "${3:-}" ;;
    navigator) cmd_navigator "${2:-}" "${3:-}" ;;
    capsule)   cmd_capsule "${2:-build}" ;;
    version)   cmd_version ;;
    help|--help|-h) cmd_help ;;
    *)
        echo -e "${RED}❌ Unknown command: $CMD${NC}"
        cmd_help
        exit 1
        ;;
esac
