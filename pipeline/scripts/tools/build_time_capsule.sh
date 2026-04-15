#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — build_time_capsule.sh
# Time Capsule Builder V1.0
# ==============================================================================
# PURPOSE:
#   Assemble a complete, self-contained long-term preservation snapshot
#   of the AXIS Canon Protocol and the PureDhamma corpus.
#
#   The capsule is designed to be:
#     • archived to cold storage (USB, optical disc, cloud vault)
#     • readable by a human with no prior context
#     • fully sufficient to reconstruct the pipeline from source
#
# OUTPUT: capsule/
#   README_HUMANS.md          ← human-readable guide
#   README_MACHINES.json      ← machine manifest with all hashes
#   AXIS_PROTOCOL.md          ← protocol description
#   seeds/                    ← canon seed (corpus + pipeline profile)
#   ledger/                   ← append-only canon registry
#   semantic/                 ← concept index
#   navigator/                ← concept map + study paths
#   mirror_endpoint/          ← distributable mirror snapshot
#   capsule_manifest.json     ← integrity manifest for this capsule
#
# USAGE:
#   bash scripts/tools/build_time_capsule.sh
#   BENG_BASE=/path bash scripts/tools/build_time_capsule.sh
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

CAPSULE_DIR="$BENG_BASE/capsule"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATESTAMP=$(date -u +"%Y%m%d")

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💎 AXIS-NIDDHI — Time Capsule Builder                   ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo -e "   ${GRAY}Base      : $BENG_BASE${NC}"
echo -e "   ${GRAY}Output    : $CAPSULE_DIR${NC}"
echo -e "   ${GRAY}Timestamp : $TIMESTAMP${NC}\n"

# ==============================================================================
# GUARDS
# ==============================================================================
for REQUIRED in \
    "$BENG_BASE/ledger/ledger.json" \
    "$BENG_BASE/seeds" \
    "$BENG_BASE/semantic/index.json"; do
    if [ ! -e "$REQUIRED" ]; then
        echo -e "${RED}❌ Required layer absent: $REQUIRED${NC}"
        echo -e "   Build all layers before running capsule build."
        exit 1
    fi
done

# ==============================================================================
# [1/7] PREPARE CAPSULE DIRECTORY
# ==============================================================================
echo -e "  ${GRAY}[1/7] Preparing capsule directory...${NC}"
rm -rf "$CAPSULE_DIR"
mkdir -p "$CAPSULE_DIR"

# ==============================================================================
# [2/7] COPY ALL LAYERS
# ==============================================================================
echo -e "  ${GRAY}[2/7] Copying layers...${NC}"

copy_layer() {
    local SRC="$1"
    local DST_NAME="$2"
    if [ -e "$SRC" ]; then
        cp -r "$SRC" "$CAPSULE_DIR/$DST_NAME"
        echo -e "     ${GRAY}$DST_NAME ✔${NC}"
    else
        echo -e "     ${YELLOW}⚠ $DST_NAME — absent, skipping${NC}"
    fi
}

copy_layer "$BENG_BASE/seeds"           "seeds"
copy_layer "$BENG_BASE/ledger"          "ledger"
copy_layer "$BENG_BASE/semantic"        "semantic"
copy_layer "$BENG_BASE/navigator"       "navigator"
copy_layer "$BENG_BASE/mirror_endpoint" "mirror_endpoint"

# ==============================================================================
# [3/7] COMPUTE LAYER HASHES
# ==============================================================================
echo -e "  ${GRAY}[3/7] Computing layer hashes...${NC}"

compute_dir_hash() {
    local DIR="$1"
    if [ -d "$DIR" ]; then
        find "$DIR" -type f | sort | xargs sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1
    else
        echo "ABSENT"
    fi
}

SEED_HASH=$(compute_dir_hash "$CAPSULE_DIR/seeds")
LEDGER_HASH=$(compute_dir_hash "$CAPSULE_DIR/ledger")
SEMANTIC_HASH=$(compute_dir_hash "$CAPSULE_DIR/semantic")
NAVIGATOR_HASH=$(compute_dir_hash "$CAPSULE_DIR/navigator")
MIRROR_HASH=$(compute_dir_hash "$CAPSULE_DIR/mirror_endpoint")

echo -e "     ${GRAY}seed_hash      : ${SEED_HASH:0:24}...${NC}"
echo -e "     ${GRAY}ledger_hash    : ${LEDGER_HASH:0:24}...${NC}"
echo -e "     ${GRAY}semantic_hash  : ${SEMANTIC_HASH:0:24}...${NC}"
echo -e "     ${GRAY}navigator_hash : ${NAVIGATOR_HASH:0:24}...${NC}"

# Read canon_hash from ledger
CANON_HASH=$(python3 -c "
import json
from pathlib import Path
j = Path('$BENG_BASE/ledger/ledger.json')
if j.exists():
    entries = json.loads(j.read_text()).get('entries',[])
    if entries:
        ef = Path('$BENG_BASE/ledger/entries') / f'{entries[-1]}.json'
        if ef.exists():
            print(json.loads(ef.read_text()).get('canon_hash','ABSENT'))
            exit()
print('ABSENT')
" 2>/dev/null || echo "ABSENT")

# Read engine version
ENGINE_VERSION=$(python3 -c "
import json
from pathlib import Path
p = Path('$BENG_BASE/metadata/axis_engine.json')
if p.exists():
    print(json.loads(p.read_text()).get('engine_version','5.4'))
else:
    print('5.4')
" 2>/dev/null || echo "5.4")

CORPUS_ENTRIES=$(python3 -c "
import json
from pathlib import Path
p = Path('$BENG_BASE/corpus/puredhamma/corpus.json')
if p.exists():
    print(json.loads(p.read_text()).get('entry_count', 748))
else:
    print(748)
" 2>/dev/null || echo "748")

# ==============================================================================
# [4/7] README_MACHINES.json
# ==============================================================================
echo -e "  ${GRAY}[4/7] Writing README_MACHINES.json...${NC}"

python3 - << PYEOF
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path

manifest = {
    "protocol":          "AXIS-CANON",
    "capsule_version":   "1.0",
    "engine":            "AXIS-NIDDHI",
    "engine_version":    "$ENGINE_VERSION",
    "built":             "$TIMESTAMP",
    "corpus": {
        "id":            "puredhamma",
        "name":          "PureDhamma",
        "source":        "PureDhamma.net",
        "entries":       int("$CORPUS_ENTRIES"),
        "languages":     ["en-US", "pt-BR"],
    },
    "hashes": {
        "canon_hash":      "$CANON_HASH",
        "seed_hash":       "$SEED_HASH",
        "ledger_hash":     "$LEDGER_HASH",
        "semantic_hash":   "$SEMANTIC_HASH",
        "navigator_hash":  "$NAVIGATOR_HASH",
        "mirror_hash":     "$MIRROR_HASH",
    },
    "layers": {
        "seeds":           "Canon seed — minimal corpus fingerprint for verification and distribution",
        "ledger":          "Append-only canon registry — immutable record of registered canon versions",
        "semantic":        "Concept index — non-canonical semantic layer over the corpus",
        "navigator":       "Concept graph and study paths — non-canonical navigation layer",
        "mirror_endpoint": "Distributable mirror snapshot — for peer-to-peer synchronization",
    },
    "rebuild_command":   "bash scripts/tools/run_full_pipeline.sh",
    "verify_command":    "bash scripts/tools/axis_cli.sh verify canon",
    "cli":               "bash scripts/tools/axis_cli.sh help",
    "invariants": [
        "Canon text is never modified after ingestion",
        "Ledger is append-only — existing entries never overwritten",
        "Semantic and Navigator layers are additive — never modify CSL",
        "seed_integrity_hash must match after every full rebuild",
    ]
}

out = Path("$CAPSULE_DIR/README_MACHINES.json")
out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
print(f"     README_MACHINES.json written")
PYEOF

# ==============================================================================
# [5/7] README_HUMANS.md
# ==============================================================================
echo -e "  ${GRAY}[5/7] Writing README_HUMANS.md...${NC}"

cat > "$CAPSULE_DIR/README_HUMANS.md" << 'MARKDOWN'
# AXIS-NIDDHI — Time Capsule
## A Preserved Archive of the PureDhamma Canon

---

## What is this?

This archive preserves the complete teachings originally published at **PureDhamma.net**
by Lal A. — a scientific interpretation of the Buddha's teaching based on the original
Pāli Canon.

The archive contains **748 posts** covering the full scope of Buddha Dhamma:
foundational ethics, Abhidhamma, dependent origination, meditation, and the path
to Nibbāna.

This capsule was produced by the **AXIS-NIDDHI Canon Compilation Engine**.

---

## What is AXIS-NIDDHI?

AXIS-NIDDHI is a deterministic content preservation pipeline.

It was designed to:
- Extract, clean, and version the original PureDhamma corpus
- Translate the corpus into Portuguese (pt-BR) via DeepL
- Generate a static website for offline reading
- Preserve the corpus with cryptographic integrity guarantees
- Distribute the corpus via a peer-to-peer mirror protocol

The system is fully reproducible: given the original source backup, every output
can be regenerated bit-for-bit.

---

## What is in this capsule?

```
capsule/
├── README_HUMANS.md        ← this file
├── README_MACHINES.json    ← machine-readable manifest with all hashes
├── AXIS_PROTOCOL.md        ← complete protocol description
├── seeds/                  ← minimal corpus fingerprint
│   └── puredhamma_seed/
│       ├── corpus.json             corpus registry (748 entries)
│       ├── pipeline_profile.json   pipeline stage map
│       ├── canon_manifest.json     cryptographic manifest
│       ├── build_seal.json         reproducibility declaration
│       └── seed_manifest.json      seed integrity hash
├── ledger/                 ← append-only canon registry
│   ├── ledger.json                 registry index
│   └── entries/
│       └── puredhamma-v1.json      registered canon entry
├── semantic/               ← concept index (non-canonical)
│   ├── index.json                  concept registry
│   ├── concept_schema.json         field definitions
│   └── concepts/
│       ├── anicca.json             Anicca — impermanence
│       └── nibbana.json            Nibbāna — liberation
├── navigator/              ← study paths (non-canonical)
│   ├── concept_map.json            concept graph (10 nodes, 35 edges)
│   ├── learning_paths.json         3 structured study paths
│   └── query_index.json            concept → post lookup
└── mirror_endpoint/        ← distributable mirror snapshot
    ├── ledger.json
    ├── seeds/
    └── tags/
```

---

## How to rebuild the full system

**Requirements:**
- Ubuntu / Debian Linux
- Python 3.10+
- The original PureDhamma backup ZIP
- A DeepL API key (for translation only)

**Full rebuild:**

```bash
# 1. Clone or restore the pipeline
cd /path/to/pipeline

# 2. Configure credentials
echo "YOUR_WP_PASS"   > scripts/private/wp_password.txt
echo "YOUR_DEEPL_KEY" > scripts/private/deepl_key.txt

# 3. Run the full pipeline
bash scripts/tools/run_full_pipeline.sh

# 4. Verify the output
bash scripts/tools/axis_cli.sh verify canon

# 5. Serve the static site locally
bash scripts/tools/axis_cli.sh serve
```

**Verify this capsule without rebuilding:**

```bash
bash scripts/tools/axis_cli.sh verify canon
bash scripts/tools/axis_cli.sh ledger verify
bash scripts/tools/axis_cli.sh seed verify
```

---

## The teaching

The Buddha's teaching is a science of the mind and reality.

Its core insight — that all conditioned things are impermanent (anicca), 
unsatisfactory (dukkha), and without a permanent self (anattā) — was discovered
through direct investigation, not faith.

The path described in this corpus leads from ordinary human experience through
the understanding of suffering, its origin, and its cessation, to Nibbāna —
the unconditioned, the permanent, the final liberation.

This archive exists so that this teaching is never lost.

---

## Contact / Origin

Source: PureDhamma.net  
Author: Lal A.  
Archive engine: AXIS-NIDDHI  
Archive date: SEE README_MACHINES.json → built  
MARKDOWN

echo -e "     ${GRAY}README_HUMANS.md written${NC}"

# ==============================================================================
# [6/7] AXIS_PROTOCOL.md
# ==============================================================================
echo -e "  ${GRAY}[6/7] Writing AXIS_PROTOCOL.md...${NC}"

cat > "$CAPSULE_DIR/AXIS_PROTOCOL.md" << 'MARKDOWN'
# AXIS Canon Protocol — Technical Description

**Protocol:** AXIS-CANON  
**Engine:** AXIS-NIDDHI  
**Version:** 5.4  

---

## Architecture Overview

```
SOURCE ZIP (PureDhamma backup)
       │
       ▼
[SG] STAGE: EXTRACTION
  SG00 reset_workspace
  SG01 extract_html         → raw HTML per post
  SG02 preprocess_html      → cleaned HTML + iframes
  SG03 build_csl            → 09-csl/ (Canon Source Library)
  SG04 harvest_assets       → images, audio
       │
       ▼
[SP] STAGE: PROCESSING
  SP01 migrate_ptbr         → pt-BR stubs
  SP02 upgrade_identity     → lineage blocks (PDPN, findex, slug)
  SP03 mass_migration       → bulk identity upgrade
  SP04 phase5_migration     → phase 5 content normalization
  SP05 fix_headers          → h1/h2 normalization
  SP06 audio_converter      → MP3 assets
  SP07 compile_glossary     → Glossario_v5 (986 terms)
  SP08 glossary_gate        → DeepL glossary upload
  SP09 translation_menu     → translation control manifest
  SP10 translate_deepl      → DeepL API translation
  SP11 translate_titles     → title translation
       │
       ▼
[SA] STAGE: AUDIT
  SA01 final_audit          → completeness check
  SA02 freeze_manifest      → translation freeze
  SA03 translation_progress → progress report
  SA04 generate_canon_manifest → cryptographic manifest (5 components)
  SA05 verify_canon_integrity  → verify all hashes
  SA06 generate_build_seal     → reproducibility declaration
       │
       ▼
[SD] STAGE: DEPLOYMENT
  SD01 generate_asset_map   → asset_map.json
  SD02 generate_slug_map    → slug_map.json (748 entries)
  SD04 wordpress_inject     → static site generation
       │
       ▼
13-static-site/ (748 HTML pages, bilingual)
```

---

## Canon Source Library (CSL)

The CSL is the canonical representation of the corpus.

```
09-csl/
└── <PDPN>/                   e.g. TL.BB.001/
    ├── identity.json          lineage block (PDPN, findex, slug, titles)
    ├── source/
    │   ├── en-US/content.html canonical English content
    │   └── pt-BR/content.html derived Portuguese translation
    └── assets/                images, audio
```

**PDPN format:** `SS.CC.NNN`  
- `SS` = section code (TL, BD, AB, DS, ...)  
- `CC` = category code  
- `NNN` = zero-padded sequence  

**Invariant:** CSL entries are never deleted. Content is never modified
after audit freeze. New entries are appended only.

---

## Seed Protocol

A **seed** is the minimal corpus fingerprint sufficient to:
- Verify corpus integrity
- Bootstrap a new AXIS node
- Confirm reproducibility without the full corpus

```
seeds/puredhamma_seed/
├── corpus.json            748 entries, language status, engine version
├── pipeline_profile.json  full stage map with all 34 scripts
├── canon_manifest.json    5-component cryptographic manifest
├── build_seal.json        reproducibility declaration
└── seed_manifest.json     seed_integrity_hash (SHA-256 of above)
```

**Verification:** `axis seed verify`

---

## Ledger Protocol

The ledger is an append-only registry of canon versions.

```
ledger/
├── ledger.json            index of registered entries
└── entries/
    └── puredhamma-v1.json full entry with all hashes
```

**Invariants:**
- Existing entries are never modified
- Duplicate tags are rejected
- `entry_hash` mismatch = structural failure
- `canon_hash` change after rebuild = informational (expected)

**Commands:** `axis ledger add | list | verify`

---

## Mirror Protocol

The mirror protocol enables lightweight synchronization between AXIS nodes.

```
mirror_endpoint/
├── ledger.json            remote-accessible ledger
├── endpoint_manifest.json endpoint integrity hash
├── entries/               per-canon entry metadata
├── seeds/                 seed packages
└── tags/                  release tag snapshots
```

**Transport:** HTTP / HTTPS / file://  
**Discovery:** `GET /ledger.json` → compare entries → download new seeds  
**Integrity:** seed_integrity_hash verified before writing  

**Commands:** `axis mirror sync | list | endpoint | add`

---

## Semantic Layer

The semantic layer is a non-canonical concept index.

```
semantic/
├── index.json             concept registry
├── concept_schema.json    field definitions
└── concepts/
    └── <concept>.json     concept entry
```

**Concept fields:** concept, type, pali, translations, first_occurrence,
occurrences, related, glossary_refs

**Types:** dhamma_characteristic, attainment, practice, mental_factor,
doctrine, person, place, text, other

**Invariant:** Additive only — never modifies CSL or canon text.

**Commands:** `axis semantic list | add | verify`

---

## Navigator Layer

The navigator layer provides non-canonical study paths through the corpus.

```
navigator/
├── concept_map.json       concept graph (nodes + edges + CSL links)
├── learning_paths.json    structured study sequences
└── query_index.json       concept → CSL slug lookup
```

**Concept graph:** 10 nodes, 35 edges (initial)  
**Study paths:** tilakkhana_intro, paticca_samuppada_intro, nibbana_path  

**Invariant:** Non-canonical — never modifies CSL or semantic layer.  
**Rebuild:** `axis navigator build`

---

## Integrity Model

```
canon_hash          SHA-256 of source ZIP
csl_hash            SHA-256 of 09-csl/ directory tree
translations_hash   SHA-256 of all pt-BR translations
site_build_hash     SHA-256 of 13-static-site/
pipeline_hash       SHA-256 of scripts/core/ (34 scripts)
manifest_hash       SHA-256 of all five above
seed_integrity_hash SHA-256 of 4 seed component hashes
entry_hash          SHA-256 of ledger entry content
```

A full rebuild from the same source ZIP must produce the same
`seed_integrity_hash`. This is the reproducibility guarantee.

---

## Full CLI Reference

```
axis build                    Full pipeline SG→SP→SA→SD
axis verify pipeline          Integrity guard (30 checks)
axis verify canon             SA05 — verify all canon hashes
axis report                   MI99 mission report
axis manifest                 SA04 canon manifest
axis serve [port]             Serve static site
axis package sojourner        Sojourner distribution (33MB)
axis package steward          Steward distribution (full)
axis corpus list / info       Corpus registry
axis tag [corpus] [version]   Release tag
axis seed generate / verify   Canon seed
axis ledger add / list / verify  Canon ledger
axis mirror sync / list / endpoint / add  Mirror protocol
axis semantic list / add / verify  Semantic concepts
axis navigator build / map / paths / query  Concept graph
axis capsule build            Time capsule
axis help                     Full command reference
```
MARKDOWN

echo -e "     ${GRAY}AXIS_PROTOCOL.md written${NC}"

# ==============================================================================
# [7/7] CAPSULE MANIFEST (integrity)
# ==============================================================================
echo -e "  ${GRAY}[7/7] Computing capsule integrity manifest...${NC}"

python3 - << PYEOF
import json, hashlib
from pathlib import Path

capsule = Path("$CAPSULE_DIR")

# Hash all files in capsule except capsule_manifest.json itself
h = hashlib.sha256()
file_count = 0
for f in sorted(capsule.rglob("*")):
    if f.is_file() and f.name != "capsule_manifest.json":
        h.update(str(f.relative_to(capsule)).encode())
        h.update(f.read_bytes())
        file_count += 1

capsule_hash = h.hexdigest()

manifest = {
    "protocol":         "AXIS-CAPSULE",
    "version":          "1.0",
    "engine":           "AXIS-NIDDHI",
    "engine_version":   "$ENGINE_VERSION",
    "built":            "$TIMESTAMP",
    "file_count":       file_count,
    "capsule_hash":     capsule_hash,
    "layer_hashes": {
        "canon_hash":      "$CANON_HASH",
        "seed_hash":       "$SEED_HASH",
        "ledger_hash":     "$LEDGER_HASH",
        "semantic_hash":   "$SEMANTIC_HASH",
        "navigator_hash":  "$NAVIGATOR_HASH",
        "mirror_hash":     "$MIRROR_HASH",
    },
    "includes": [
        "seeds", "ledger", "semantic", "navigator", "mirror_endpoint",
        "README_HUMANS.md", "README_MACHINES.json", "AXIS_PROTOCOL.md"
    ]
}

(capsule / "capsule_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False))
print(f"     capsule_hash  : {capsule_hash[:24]}...")
print(f"     files         : {file_count}")
PYEOF

# ==============================================================================
# SUMMARY
# ==============================================================================
TOTAL_SIZE=$(du -sh "$CAPSULE_DIR" | cut -f1)

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ TIME CAPSULE BUILT${NC}"
echo -e "══════════════════════════════════════════════════════════"
echo -e "  ${GRAY}Location  : $CAPSULE_DIR${NC}"
echo -e "  ${GRAY}Size      : $TOTAL_SIZE${NC}"
echo -e "  ${GRAY}Layers    : seeds / ledger / semantic / navigator / mirror_endpoint${NC}"
echo -e "  ${GRAY}Docs      : README_HUMANS.md / README_MACHINES.json / AXIS_PROTOCOL.md${NC}"
echo -e ""
echo -e "  ${CYAN}To archive:${NC}"
echo -e "  ${GRAY}tar -czf axis_capsule_$DATESTAMP.tar.gz -C $BENG_BASE capsule/${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}\n"
