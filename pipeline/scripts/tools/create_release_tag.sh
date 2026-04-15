#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — create_release_tag.sh
# Canon Release Tag Creator V1.0
# ==============================================================================
# Creates a versioned release tag snapshot.
#
# Output: releases/tags/<corpus_id>-v<N>/
#   canon_manifest.json  ← cryptographic proof
#   build_seal.json      ← reproducible build declaration
#   README_release.md    ← human-readable release note
#
# Usage:
#   bash scripts/tools/create_release_tag.sh
#   bash scripts/tools/create_release_tag.sh puredhamma v1
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

CORPUS_ID="${1:-puredhamma}"
VERSION="${2:-v1}"
TAG_NAME="${CORPUS_ID}-${VERSION}"
TAG_DIR="$BENG_BASE/releases/tags/$TAG_NAME"

MANIFEST_SRC="$BENG_BASE/metadata/canon_manifest.json"
SEAL_SRC="$BENG_BASE/metadata/build_seal.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💎 AXIS-NIDDHI — Canon Release Tag Creator          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo -e "   ${GRAY}Tag     : $TAG_NAME${NC}"
echo -e "   ${GRAY}Output  : $TAG_DIR${NC}\n"

# ==============================================================================
# GUARDS
# ==============================================================================
if [ ! -f "$MANIFEST_SRC" ]; then
    echo -e "${RED}❌ canon_manifest.json absent — run axis build first${NC}"
    exit 1
fi

if [ ! -f "$SEAL_SRC" ]; then
    echo -e "${YELLOW}⚠ build_seal.json absent — generating...${NC}"
    BENG_BASE="$BENG_BASE" python3 "$BENG_BASE/scripts/core/SA06_generate_build_seal.py"
fi

# Warn if tag already exists
if [ -d "$TAG_DIR" ]; then
    echo -e "${YELLOW}⚠ Tag already exists: $TAG_DIR — overwriting${NC}"
fi

# ==============================================================================
# CREATE TAG
# ==============================================================================
mkdir -p "$TAG_DIR"

cp "$MANIFEST_SRC" "$TAG_DIR/canon_manifest.json"
cp "$SEAL_SRC"     "$TAG_DIR/build_seal.json"

# Extract key values for README
CANON_HASH=$(python3 -c "import json; d=json.load(open('$MANIFEST_SRC')); print(d.get('canon_hash','UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
ENTRIES=$(python3 -c "import json; d=json.load(open('$MANIFEST_SRC')); print(d.get('csl_entries','?'))" 2>/dev/null || echo "?")
TRANSLATIONS=$(python3 -c "import json; d=json.load(open('$MANIFEST_SRC')); print(d.get('translations_frozen','?'))" 2>/dev/null || echo "?")
ENGINE_VER=$(python3 -c "import json; d=json.load(open('$MANIFEST_SRC')); print(d.get('engine_version','5.4'))" 2>/dev/null || echo "5.4")
SOURCE_ZIP=$(python3 -c "import json; d=json.load(open('$MANIFEST_SRC')); print(d.get('source_zip','?'))" 2>/dev/null || echo "?")

cat > "$TAG_DIR/README_release.md" << README
# PureDhamma Canon — Release ${VERSION^^}

**Tag:**     \`$TAG_NAME\`  
**Engine:**  AXIS-NIDDHI V$ENGINE_VER  
**Corpus:**  PureDhamma — Teachings of Professor Lal  
**Tagged:**  $TIMESTAMP  

---

## Canon Summary

| Field | Value |
|-------|-------|
| Posts | $ENTRIES |
| Translations (PT-BR) | $TRANSLATIONS |
| Source | $SOURCE_ZIP |
| Canon hash | \`${CANON_HASH:0:32}...\` |
| Reproducible | ✅ Yes |

---

## What this is

PureDhamma Canon ${VERSION^^} is the first formally sealed release of the
PureDhamma teachings archive, compiled by the AXIS-NIDDHI Canon Compilation Engine.

The canon contains $ENTRIES posts in English with $TRANSLATIONS posts translated into
Portuguese (PT-BR), extracted from the original WordPress backup dated
2025-12-31.

---

## Cryptographic integrity

\`\`\`bash
# Verify canon integrity
python3 scripts/core/SA05_verify_canon_integrity.py

# Expected output:
# ✅ CANON VERIFIED
\`\`\`

Verify canon hash manually:
\`\`\`bash
python3 -c "
import json
s = json.load(open('build_seal.json'))
print('Engine  :', s['engine'], 'V'+s['engine_version'])
print('Entries :', s['entries'])
print('Hash    :', s['canon_hash'][:32]+'...')
print('Sealed  :', s['reproducible'])
"
\`\`\`

---

## Rebuild from source

A Steward holding the source ZIP can reproduce this exact canon:

\`\`\`bash
# With source ZIP: $SOURCE_ZIP
bash scripts/core/run_full_pipeline.sh --full
python3 scripts/core/SA05_verify_canon_integrity.py
\`\`\`

The build is deterministic. Given the same source ZIP and pipeline,
the canon hash will match.

---

## Files in this tag

| File | Purpose |
|------|---------|
| \`canon_manifest.json\` | Cryptographic manifest of all canon components |
| \`build_seal.json\` | Reproducible build declaration |
| \`README_release.md\` | This file |
README

# ==============================================================================
# REPORT
# ==============================================================================
echo -e "  ${GREEN}✔ canon_manifest.json${NC}"
echo -e "  ${GREEN}✔ build_seal.json${NC}"
echo -e "  ${GREEN}✔ README_release.md${NC}"
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ RELEASE TAG CREATED: $TAG_NAME${NC}"
echo -e "══════════════════════════════════════════════════"
echo -e "  ${GRAY}Location   : $TAG_DIR${NC}"
echo -e "  ${GRAY}Entries    : $ENTRIES${NC}"
echo -e "  ${GRAY}Canon hash : ${CANON_HASH:0:24}...${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}\n"
