#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — package_sojourner_distribution.sh
# Sojourner Distribution Packager V1.0
# Tier: SOJOURNER — offline static canon viewer
# ==============================================================================
# Produces: releases/sojourner/
#   dist/                    ← complete static site
#   metadata/
#     canon_manifest.json    ← cryptographic proof
#     axis_engine.json       ← engine identity
#   README_sojourner.md
#
# Usage:
#   bash scripts/tools/package_sojourner_distribution.sh
#   BENG_BASE=/path/to/pipeline bash scripts/tools/package_sojourner_distribution.sh
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

RELEASE_DIR="$BENG_BASE/releases/sojourner"
SITE_SRC="$BENG_BASE/13-static-site"
MANIFEST_SRC="$BENG_BASE/metadata/canon_manifest.json"
ENGINE_SRC="$BENG_BASE/metadata/axis_engine.json"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💎 AXIS-NIDDHI — Sojourner Distribution Packager    ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo -e "   ${GRAY}Base    : $BENG_BASE${NC}"
echo -e "   ${GRAY}Output  : $RELEASE_DIR${NC}"
echo -e "   ${GRAY}Build   : $TIMESTAMP${NC}\n"

# ==============================================================================
# GUARD — static site must exist
# ==============================================================================
if [ ! -d "$SITE_SRC" ]; then
    echo -e "${RED}❌ Static site not found: $SITE_SRC${NC}"
    echo -e "   Run: axis build"
    exit 1
fi

SITE_POST_COUNT=$(find "$SITE_SRC" -name "index.html" | wc -l)
if [ "$SITE_POST_COUNT" -lt 100 ]; then
    echo -e "${YELLOW}⚠ Site appears incomplete: only $SITE_POST_COUNT index.html files found${NC}"
    echo -e "   Expected ~748. Run: axis build"
    exit 1
fi

# ==============================================================================
# PREPARE OUTPUT DIR
# ==============================================================================
echo -e "  ${GRAY}[1/4] Preparing output directory...${NC}"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR/dist"
mkdir -p "$RELEASE_DIR/metadata"

# ==============================================================================
# COPY STATIC SITE
# ==============================================================================
echo -e "  ${GRAY}[2/4] Copying static site ($SITE_POST_COUNT pages)...${NC}"
rsync -a --quiet "$SITE_SRC/" "$RELEASE_DIR/dist/"

# ==============================================================================
# COPY METADATA
# ==============================================================================
echo -e "  ${GRAY}[3/4] Copying metadata...${NC}"
if [ -f "$MANIFEST_SRC" ]; then
    cp "$MANIFEST_SRC" "$RELEASE_DIR/metadata/canon_manifest.json"
    CANON_HASH=$(python3 -c "import json; d=json.load(open('$MANIFEST_SRC')); print(d.get('canon_hash','UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
    echo -e "     ${GRAY}canon_manifest.json — hash: ${CANON_HASH:0:24}...${NC}"
else
    echo -e "  ${YELLOW}⚠ canon_manifest.json absent — generating...${NC}"
    python3 "$BENG_BASE/scripts/core/SA04_generate_canon_manifest.py"
    cp "$MANIFEST_SRC" "$RELEASE_DIR/metadata/canon_manifest.json"
fi

[ -f "$ENGINE_SRC" ] && cp "$ENGINE_SRC" "$RELEASE_DIR/metadata/axis_engine.json"

# ==============================================================================
# README
# ==============================================================================
echo -e "  ${GRAY}[4/4] Writing README_sojourner.md...${NC}"
cat > "$RELEASE_DIR/README_sojourner.md" << README
# PureDhamma — Sojourner Distribution

**Tier:** SOJOURNER — Offline Canon Viewer  
**Engine:** AXIS-NIDDHI V5.4  
**Corpus:** PureDhamma — Teachings of Professor Lal  
**Build:** $TIMESTAMP

---

## What is this?

This is a complete offline copy of the PureDhamma teachings archive.  
748 posts in English. 93 posts translated into Portuguese (PT-BR).

No internet connection required.  
No server required.  
No installation required.

---

## How to open

### Option A — Direct file
Open: \`dist/index.html\`  
in any modern web browser (Firefox, Chrome, Chromium).

### Option B — Local server (recommended for full navigation)
\`\`\`bash
cd dist && python3 -m http.server 8080
\`\`\`
Open: http://localhost:8080

---

## Contents

\`\`\`
sojourner/
├── dist/                  ← Complete static site (748 posts)
│   ├── index.html         ← Main index — start here
│   ├── en/                ← English posts
│   └── pt-BR/             ← Portuguese posts (93)
└── metadata/
    ├── canon_manifest.json  ← Cryptographic proof of integrity
    └── axis_engine.json     ← Engine identity
\`\`\`

---

## Verify integrity

\`\`\`bash
python3 -c "
import json
m = json.load(open('metadata/canon_manifest.json'))
print('Engine :', m['engine'], 'V'+m['engine_version'])
print('Corpus :', m['corpus'])
print('Posts  :', m['csl_entries'])
print('Transl.:', m['translations_frozen'])
print('Hash   :', m['canon_hash'][:32]+'...')
print('Status :', m['verification'])
"
\`\`\`

---

## About

The PureDhamma archive was compiled by the AXIS-NIDDHI Canon Compilation Engine.  
For rebuild capability, request the **Steward** distribution.
README

# ==============================================================================
# SIZE REPORT
# ==============================================================================
TOTAL_SIZE=$(du -sh "$RELEASE_DIR" | cut -f1)
DIST_SIZE=$(du -sh "$RELEASE_DIR/dist" | cut -f1)

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ SOJOURNER DISTRIBUTION PACKAGED${NC}"
echo -e "══════════════════════════════════════════════════"
echo -e "  ${GRAY}Location : $RELEASE_DIR${NC}"
echo -e "  ${GRAY}dist/    : $DIST_SIZE${NC}"
echo -e "  ${GRAY}Total    : $TOTAL_SIZE${NC}"
echo -e "  ${GRAY}Pages    : $SITE_POST_COUNT${NC}"
echo -e "  ${GRAY}Hash     : ${CANON_HASH:0:24}...${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}\n"
