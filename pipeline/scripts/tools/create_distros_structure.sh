#!/usr/bin/env bash
# ==============================================================================
# AXIS-NIDDHI — create_distros_structure.sh
# Distribution Tier Structure Creator
# Run from: /home/sanghop/beng_prelaunch/pipeline/
# ==============================================================================
set -euo pipefail

PIPELINE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DISTROS_DIR="$PIPELINE_DIR/distros"

GREEN='\033[0;32m'
CYAN='\033[0;96m'
GRAY='\033[0;37m'
NC='\033[0m'

echo -e "\n${CYAN}💎 AXIS-NIDDHI — Creating Distribution Structure${NC}"
echo -e "   Base: $PIPELINE_DIR\n"

# ==============================================================================
# USER TIER — offline static canon viewer
# ==============================================================================
mkdir -p "$DISTROS_DIR/user"

cat > "$DISTROS_DIR/user/README_user.md" << 'README'
# PureDhamma — Offline Canon Viewer

## Contents
- `dist/` — Complete PureDhamma static site (748 posts, EN + PT-BR)
- `canon_manifest.json` — Cryptographic proof of build integrity

## Usage
```bash
cd dist && python3 -m http.server 8080
```
Open: http://localhost:8080

## Verification
```bash
python3 -c "
import json, hashlib
m = json.load(open('canon_manifest.json'))
print('Engine :', m['engine'], 'V'+m['engine_version'])
print('Corpus :', m['corpus'])
print('Posts  :', m['csl_entries'])
print('Hash   :', m['canon_hash'][:24]+'...')
"
```

## About
PureDhamma — Teachings of Professor Lal
Compiled by the AXIS-NIDDHI Canon Compilation Engine V5.4
README

echo -e "  ${GREEN}✔ distros/user/${NC}"

# ==============================================================================
# GUARDIAN TIER — full rebuild capability
# ==============================================================================
mkdir -p "$DISTROS_DIR/guardian/pipeline/scripts"
mkdir -p "$DISTROS_DIR/guardian/pipeline/metadata"
mkdir -p "$DISTROS_DIR/guardian/pipeline/sources"
mkdir -p "$DISTROS_DIR/guardian/pipeline/03-translations"

cat > "$DISTROS_DIR/guardian/README_guardian.md" << 'README'
# AXIS-NIDDHI — Guardian Distribution

## Purpose
Full rebuild capability from source ZIP.
The Guardian can regenerate the complete PureDhamma canon independently.

## Contents
```
pipeline/
├── scripts/
│   ├── core/       ← 34 canonical pipeline scripts
│   └── tools/      ← utility scripts
├── metadata/       ← PDPN CSV, glossary, canon_manifest.json
├── sources/        ← PureDhamma source ZIP (2.2GB)
└── 03-translations/ ← 93 frozen PT-BR translations
```

## Rebuild
```bash
cd pipeline
BENG_BASE=$(pwd) bash scripts/core/run_full_pipeline.sh --full
```

## Verify integrity
```bash
BENG_BASE=$(pwd) bash scripts/core/verify_pipeline_integrity.sh
```

## Requirements
- Python 3.12+
- packages: pandas pymysql beautifulsoup4 requests jinja2
- MySQL (for SG phase only)

## About
AXIS-NIDDHI Canon Compilation Engine V5.4
Corpus: PureDhamma — Teachings of Professor Lal
README

cat > "$DISTROS_DIR/guardian/.gitignore" << 'GITIGNORE'
# Guardian distribution — never include credentials
pipeline/scripts/private/
*.key
*.password
*_key.txt
*_password.txt
GITIGNORE

echo -e "  ${GREEN}✔ distros/guardian/${NC}"

# ==============================================================================
# NINE TIER — bootable ISO (structure only)
# ==============================================================================
mkdir -p "$DISTROS_DIR/nine/guardian"
mkdir -p "$DISTROS_DIR/nine/boot"
mkdir -p "$DISTROS_DIR/nine/iso"

cat > "$DISTROS_DIR/nine/README_nine.md" << 'README'
# AXIS-NIDDHI — Nine Distribution (Bootable Archive)

## Status
STRUCTURE ONLY — ISO not yet built.

## Purpose
Offline bootable canon. No internet required.
Complete PureDhamma preservation system on bootable media.

## Planned Contents
```
nine/
├── guardian/   ← Full AXIS-NIDDHI Guardian (pipeline + corpus)
├── boot/       ← Bootloader configuration
│   ├── grub.cfg
│   └── isolinux/
└── iso/        ← ISO build artifacts
    ├── build_iso.sh
    └── axis_niddhi_v54.iso  ← (generated)
```

## Build ISO (future)
```bash
bash iso/build_iso.sh
```

## Target Media
- USB drive (4GB+)
- DVD-R
- SD card

## Lineage
V5.4 → V6 (multi-corpus) → V7 (multi-operator consensus)
README

cat > "$DISTROS_DIR/nine/boot/.gitkeep" << 'EOF'
# Boot configuration placeholder
# Future: grub.cfg, isolinux/, kernel params
EOF

cat > "$DISTROS_DIR/nine/iso/.gitkeep" << 'EOF'
# ISO build artifacts placeholder
# Future: build_iso.sh, axis_niddhi_v54.iso
EOF

echo -e "  ${GREEN}✔ distros/nine/${NC}"

# ==============================================================================
# SUMMARY
# ==============================================================================
echo ""
echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo -e "${CYAN}  DISTRIBUTION STRUCTURE CREATED${NC}"
echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo -e "  ${GRAY}distros/user/      → offline viewer tier${NC}"
echo -e "  ${GRAY}distros/guardian/  → rebuild capability tier${NC}"
echo -e "  ${GRAY}distros/nine/      → bootable ISO tier (structure only)${NC}"
echo ""
echo -e "  Next: populate tiers via packaging scripts"
echo -e "${CYAN}══════════════════════════════════════════${NC}\n"
