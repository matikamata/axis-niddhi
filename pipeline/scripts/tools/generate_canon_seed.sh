#!/usr/bin/env bash
# ==============================================================================
# 💎 AXIS-NIDDHI — generate_canon_seed.sh
# Canon Seed Generator V1.0
# ==============================================================================
# PURPOSE:
#   Generate a minimal Canon Seed — the smallest set of files needed to
#   prove a specific canon build and guide deterministic reconstruction.
#
#   A seed is NOT a rebuild package (that is the Steward distribution).
#   A seed is a cryptographic declaration: "this canon was built, with
#   these hashes, from this source, by this engine."
#
# OUTPUT: seeds/puredhamma_seed/
#   corpus.json            ← corpus identity
#   pipeline_profile.json  ← stage map
#   canon_manifest.json    ← component hashes
#   build_seal.json        ← reproducibility declaration
#   seed_manifest.json     ← seed-level summary (generated here)
#
# USAGE:
#   bash scripts/tools/generate_canon_seed.sh
#   CORPUS_ID=puredhamma bash scripts/tools/generate_canon_seed.sh
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

CORPUS_ID="${CORPUS_ID:-puredhamma}"
SEED_DIR="$BENG_BASE/seeds/${CORPUS_ID}_seed"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo -e "\n${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  💎 AXIS-NIDDHI — Canon Seed Generator               ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo -e "   ${GRAY}Corpus  : $CORPUS_ID${NC}"
echo -e "   ${GRAY}Output  : $SEED_DIR${NC}"
echo -e "   ${GRAY}Build   : $TIMESTAMP${NC}\n"

# ==============================================================================
# SOURCE FILE GUARDS
# ==============================================================================
CORPUS_JSON="$BENG_BASE/corpus/$CORPUS_ID/corpus.json"
PIPELINE_JSON="$BENG_BASE/corpus/$CORPUS_ID/pipeline_profile.json"
MANIFEST_JSON="$BENG_BASE/metadata/canon_manifest.json"
SEAL_JSON="$BENG_BASE/metadata/build_seal.json"

MISSING=0
for f in "$CORPUS_JSON" "$PIPELINE_JSON" "$MANIFEST_JSON" "$SEAL_JSON"; do
    if [ ! -f "$f" ]; then
        echo -e "  ${RED}✘ MISSING: $f${NC}"
        MISSING=$((MISSING+1))
    fi
done
if [ "$MISSING" -gt 0 ]; then
    echo -e "${RED}❌ $MISSING required file(s) absent. Aborting.${NC}"
    echo -e "   Run: axis build"
    exit 1
fi

# ==============================================================================
# PREPARE SEED DIRECTORY
# ==============================================================================
echo -e "  ${GRAY}[1/3] Preparing seed directory...${NC}"
rm -rf "$SEED_DIR"
mkdir -p "$SEED_DIR"

# ==============================================================================
# COPY SEED FILES
# ==============================================================================
echo -e "  ${GRAY}[2/3] Copying seed files...${NC}"
cp "$CORPUS_JSON"   "$SEED_DIR/corpus.json"
cp "$PIPELINE_JSON" "$SEED_DIR/pipeline_profile.json"
cp "$MANIFEST_JSON" "$SEED_DIR/canon_manifest.json"
cp "$SEAL_JSON"     "$SEED_DIR/build_seal.json"
echo -e "     ${GRAY}corpus.json           ✔${NC}"
echo -e "     ${GRAY}pipeline_profile.json ✔${NC}"
echo -e "     ${GRAY}canon_manifest.json   ✔${NC}"
echo -e "     ${GRAY}build_seal.json       ✔${NC}"

# ==============================================================================
# GENERATE seed_manifest.json
# ==============================================================================
echo -e "  ${GRAY}[3/3] Generating seed_manifest.json...${NC}"
python3 - << PYEOF
import hashlib, json, sys
from pathlib import Path

seed_dir    = Path("$SEED_DIR")
manifest    = json.loads((seed_dir / "canon_manifest.json").read_text())
seal        = json.loads((seed_dir / "build_seal.json").read_text())
corpus      = json.loads((seed_dir / "corpus.json").read_text())

# Hash the manifest and seal files as they are in the seed
def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

manifest_hash_seed  = sha256(seed_dir / "canon_manifest.json")
seal_hash_seed      = sha256(seed_dir / "build_seal.json")
corpus_hash_seed    = sha256(seed_dir / "corpus.json")
pipeline_hash_seed  = sha256(seed_dir / "pipeline_profile.json")

# Seed integrity hash — hash of all four seed file hashes
seed_hasher = hashlib.sha256()
for h in sorted([manifest_hash_seed, seal_hash_seed, corpus_hash_seed, pipeline_hash_seed]):
    seed_hasher.update(h.encode())
seed_integrity_hash = seed_hasher.hexdigest()

# Compute semantic hash if semantic layer exists
semantic_dir = Path("$BENG_BASE") / "semantic"
semantic_hash = "ABSENT"
if semantic_dir.exists():
    h = hashlib.sha256()
    index_path = semantic_dir / "index.json"
    if index_path.exists():
        h.update(index_path.read_bytes())
    concepts_dir = semantic_dir / "concepts"
    if concepts_dir.exists():
        for cf in sorted(concepts_dir.glob("*.json")):
            h.update(cf.name.encode())
            h.update(cf.read_bytes())
    semantic_hash = h.hexdigest()

seed_manifest = {
    "seed_version":         "1.0",
    "engine":               manifest.get("engine", "AXIS-NIDDHI"),
    "engine_version":       manifest.get("engine_version", "5.4"),
    "corpus":               corpus.get("corpus_id", "puredhamma"),
    "corpus_name":          corpus.get("corpus_name", "PureDhamma"),
    "entries":              manifest.get("csl_entries", 0),
    "translations":         manifest.get("translations_frozen", 0),
    "languages":            corpus.get("languages", ["en", "pt-BR"]),
    "canon_hash":           manifest.get("canon_hash", "UNKNOWN"),
    "csl_hash":             manifest.get("csl_hash", "UNKNOWN"),
    "translations_hash":    manifest.get("translations_hash", "UNKNOWN"),
    "pipeline_hash":        manifest.get("pipeline_hash", "UNKNOWN"),
    "manifest_hash":        manifest_hash_seed,
    "build_seal_hash":      seal_hash_seed,
    "source_zip":           manifest.get("source_zip", "UNKNOWN"),
    "source_zip_sha256":    manifest.get("source_zip_sha256", "UNKNOWN"),
    "build_timestamp":      seal.get("build_timestamp", "UNKNOWN"),
    "reproducible":         seal.get("reproducible", True),
    "seed_integrity_hash":  seed_integrity_hash,
    "semantic_hash":        semantic_hash,
    "seed_generated":       "$TIMESTAMP",
    "seed_statement": (
        f"Canon seed for corpus '{corpus.get('corpus_id','')}' "
        f"({manifest.get('csl_entries',0)} entries). "
        f"Canon hash: {manifest.get('canon_hash','')[:16]}... "
        f"Reproducible from source: {manifest.get('source_zip','')}. "
        f"Engine: AXIS-NIDDHI V{manifest.get('engine_version','5.4')}."
    )
}

(seed_dir / "seed_manifest.json").write_text(
    json.dumps(seed_manifest, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"  seed_integrity_hash : {seed_integrity_hash[:24]}...")
print(f"  canon_hash          : {manifest.get('canon_hash','')[:24]}...")
print(f"  entries             : {manifest.get('csl_entries',0)}")
print(f"  reproducible        : {seal.get('reproducible',True)}")
PYEOF

# ==============================================================================
# SIZE + REPORT
# ==============================================================================
SEED_SIZE=$(du -sh "$SEED_DIR" | cut -f1)
FILE_COUNT=$(ls "$SEED_DIR" | wc -l)

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ CANON SEED GENERATED${NC}"
echo -e "══════════════════════════════════════════════════"
echo -e "  ${GRAY}Location : $SEED_DIR${NC}"
echo -e "  ${GRAY}Files    : $FILE_COUNT${NC}"
echo -e "  ${GRAY}Size     : $SEED_SIZE${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}\n"
