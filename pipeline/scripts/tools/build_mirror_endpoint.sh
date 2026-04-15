#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — build_mirror_endpoint.sh
# Mirror Endpoint Builder V1.0
# ==============================================================================
# PURPOSE:
#   Build a local mirror endpoint directory that any AXIS node can sync from.
#   Can be served over HTTP, copied to USB, or shared via any transport.
#
# OUTPUT: mirror_endpoint/
#   ledger.json              ← ledger registry (for remote discovery)
#   entries/                 ← ledger entry files per canon
#     <canon_id>.json
#   seeds/                   ← seed packages per canon
#     <canon_id>/
#       corpus.json
#       pipeline_profile.json
#       canon_manifest.json
#       build_seal.json
#       seed_manifest.json
#   tags/                    ← release tag snapshots
#     <tag>/
#       canon_manifest.json
#       build_seal.json
#       README_release.md
#
# SERVE:
#   cd mirror_endpoint && python3 -m http.server 9090
#   Then: axis mirror sync --mirror http://localhost:9090
#
# USAGE:
#   bash scripts/tools/build_mirror_endpoint.sh
#   BENG_BASE=/path bash scripts/tools/build_mirror_endpoint.sh
# ==============================================================================
set -euo pipefail

_SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
BENG_BASE="${BENG_BASE:-$(cd "$_SELF_DIR/../.." && pwd)}"

GREEN='\033[0;32m'
CYAN='\033[0;96m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m'

ENDPOINT_DIR="$BENG_BASE/mirror_endpoint"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💎 AXIS-NIDDHI — Mirror Endpoint Builder            ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo -e "   ${GRAY}Base     : $BENG_BASE${NC}"
echo -e "   ${GRAY}Output   : $ENDPOINT_DIR${NC}"
echo -e "   ${GRAY}Build    : $TIMESTAMP${NC}\n"

# ==============================================================================
# GUARDS
# ==============================================================================
LEDGER_JSON="$BENG_BASE/ledger/ledger.json"
if [ ! -f "$LEDGER_JSON" ]; then
    echo -e "${RED}❌ Ledger not found: $LEDGER_JSON${NC}"
    echo -e "   Run: axis ledger add"
    exit 1
fi

# ==============================================================================
# PREPARE ENDPOINT
# ==============================================================================
echo -e "  ${GRAY}[1/4] Preparing endpoint directory...${NC}"
rm -rf "$ENDPOINT_DIR"
mkdir -p "$ENDPOINT_DIR/entries"
mkdir -p "$ENDPOINT_DIR/seeds"
mkdir -p "$ENDPOINT_DIR/tags"

# ==============================================================================
# COPY LEDGER
# ==============================================================================
echo -e "  ${GRAY}[2/4] Copying ledger...${NC}"
cp "$LEDGER_JSON" "$ENDPOINT_DIR/ledger.json"

# Copy all entry files
ENTRY_COUNT=0
if [ -d "$BENG_BASE/ledger/entries" ]; then
    for entry_file in "$BENG_BASE/ledger/entries"/*.json; do
        [ -f "$entry_file" ] || continue
        cp "$entry_file" "$ENDPOINT_DIR/entries/"
        ENTRY_COUNT=$((ENTRY_COUNT+1))
    done
fi
echo -e "     ${GRAY}$ENTRY_COUNT entries copied${NC}"

# ==============================================================================
# COPY SEEDS (per ledger entry)
# ==============================================================================
echo -e "  ${GRAY}[3/4] Copying seeds...${NC}"
SEED_COUNT=0

# Read entries from ledger
ENTRIES=$(python3 -c "
import json
l = json.load(open('$LEDGER_JSON'))
for e in l.get('entries',[]): print(e)
" 2>/dev/null || true)

for CANON_ID in $ENTRIES; do
    ENTRY_FILE="$BENG_BASE/ledger/entries/${CANON_ID}.json"
    if [ ! -f "$ENTRY_FILE" ]; then
        echo -e "     ${YELLOW}⚠ Entry file missing: $CANON_ID${NC}"
        continue
    fi

    # Get corpus_id from entry
    CORPUS_ID=$(python3 -c "import json; print(json.load(open('$ENTRY_FILE')).get('corpus_id','puredhamma'))" 2>/dev/null || echo "puredhamma")

    # Find seed — check canonical seed dir first, then tagged seed dir
    SEED_SRC=""
    for SEED_CANDIDATE in \
        "$BENG_BASE/seeds/${CORPUS_ID}_seed" \
        "$BENG_BASE/seeds/${CORPUS_ID}_seed_${CANON_ID}"; do
        if [ -f "$SEED_CANDIDATE/seed_manifest.json" ]; then
            SEED_SRC="$SEED_CANDIDATE"
            break
        fi
    done

    if [ -z "$SEED_SRC" ]; then
        echo -e "     ${YELLOW}⚠ Seed not found for: $CANON_ID (corpus: $CORPUS_ID)${NC}"
        # Create placeholder
        mkdir -p "$ENDPOINT_DIR/seeds/$CANON_ID"
        echo "{\"note\": \"seed not generated — run axis seed generate\"}" \
            > "$ENDPOINT_DIR/seeds/$CANON_ID/seed_manifest.json"
        continue
    fi

    # Copy seed files
    mkdir -p "$ENDPOINT_DIR/seeds/$CANON_ID"
    for SEED_FILE in corpus.json pipeline_profile.json canon_manifest.json build_seal.json seed_manifest.json; do
        [ -f "$SEED_SRC/$SEED_FILE" ] && cp "$SEED_SRC/$SEED_FILE" "$ENDPOINT_DIR/seeds/$CANON_ID/"
    done
    echo -e "     ${GRAY}$CANON_ID → seeds/$CANON_ID/ ✔${NC}"
    SEED_COUNT=$((SEED_COUNT+1))
done

echo -e "     ${GRAY}$SEED_COUNT seeds copied${NC}"

# ==============================================================================
# COPY RELEASE TAGS
# ==============================================================================
echo -e "  ${GRAY}[4/4] Copying release tags...${NC}"
TAG_COUNT=0
if [ -d "$BENG_BASE/releases/tags" ]; then
    for TAG_DIR in "$BENG_BASE/releases/tags"/*/; do
        [ -d "$TAG_DIR" ] || continue
        TAG_NAME=$(basename "$TAG_DIR")
        mkdir -p "$ENDPOINT_DIR/tags/$TAG_NAME"
        for TAG_FILE in canon_manifest.json build_seal.json README_release.md; do
            [ -f "$TAG_DIR/$TAG_FILE" ] && cp "$TAG_DIR/$TAG_FILE" "$ENDPOINT_DIR/tags/$TAG_NAME/"
        done
        echo -e "     ${GRAY}$TAG_NAME ✔${NC}"
        TAG_COUNT=$((TAG_COUNT+1))
    done
fi
echo -e "     ${GRAY}$TAG_COUNT tags copied${NC}"

# ==============================================================================
# ENDPOINT MANIFEST
# ==============================================================================
python3 - << PYEOF
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path

endpoint = Path("$ENDPOINT_DIR")
ledger   = json.loads((endpoint / "ledger.json").read_text())

h = hashlib.sha256()
for f in sorted(endpoint.rglob("*.json")):
    if f.name != "endpoint_manifest.json":
        h.update(f.read_bytes())
endpoint_hash = h.hexdigest()

manifest = {
    "protocol":       "AXIS-MIRROR",
    "version":        1,
    "engine":         "AXIS-NIDDHI",
    "built":          "$TIMESTAMP",
    "entries":        ledger.get("entries", []),
    "entry_count":    len(ledger.get("entries", [])),
    "endpoint_hash":  endpoint_hash,
}
(endpoint / "endpoint_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False)
)
print(f"  endpoint_hash: {endpoint_hash[:24]}...")
PYEOF

# ==============================================================================
# SIZE + SERVE HINT
# ==============================================================================
TOTAL_SIZE=$(du -sh "$ENDPOINT_DIR" | cut -f1)

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ MIRROR ENDPOINT BUILT${NC}"
echo -e "══════════════════════════════════════════════════"
echo -e "  ${GRAY}Location : $ENDPOINT_DIR${NC}"
echo -e "  ${GRAY}Entries  : $ENTRY_COUNT${NC}"
echo -e "  ${GRAY}Seeds    : $SEED_COUNT${NC}"
echo -e "  ${GRAY}Tags     : $TAG_COUNT${NC}"
echo -e "  ${GRAY}Size     : $TOTAL_SIZE${NC}"
echo -e ""
echo -e "  ${CYAN}Serve:${NC}"
echo -e "  ${GRAY}cd $ENDPOINT_DIR${NC}"
echo -e "  ${GRAY}python3 -m http.server 9090${NC}"
echo -e "  ${GRAY}axis mirror sync --mirror http://localhost:9090${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}\n"
