# AXIS-NIDDHI V6 — ARCHITECTURAL OUTLINE
**Multi-Corpus Preservation Engine**  
**Status:** Design document — pre-implementation  
**Baseline:** V5.4 (frozen 2026-03-11, single-corpus, stable)  
**Author:** Vayo (Technical Architect)  
**Date:** 2026-03-11

---

## DESIGN PRINCIPLES

V6 introduces zero breaking changes to V5.4.  
Every change is additive or a controlled substitution in exactly three files.  
The CSL, the SSG, and all SP/SA/SD scripts remain untouched.  
A V5.4 operator who does not activate multi-corpus features notices nothing different.

---

## SECTION 1 — CORPUS COUPLING AUDIT (V5.4 baseline)

Before designing V6, the exact coupling points in the live codebase must be named.
The following is derived from code inspection, not documentation.

```
COUPLING MAP — files that know the corpus identity

FILE                    COUPLING                            HOW COUPLED
────────────────────────────────────────────────────────────────────────────────
config.py               DB_CONFIG['database'] = 'beng_wp_21'   hardcoded
                        WP_BASE_URL = '.../beng_feb2026'        hardcoded
                        WP_ADMIN_USER = 'axis_niddhi'           hardcoded
                        PDPN_CSV = metadata/PDPN_01_...csv      hardcoded name
                        SOURCE_LANG = (derived, ok)             env-aware
                        SCHEMA_VERSION = (derived, ok)          constant

SG00_reset_workspace.sh DB_NAME = 'beng_wp_21'                  hardcoded
                        WP_ALIAS = 'beng_feb2026'               hardcoded
                        ZIP detection: find *.zip | head -1     first-found

SG01_extract_html.py    row["id_10WEB.io"]                      column name
                        row["Fin-dex"]                          column name
                        row["PD#PN"]                            column name
                        row["Slug_Derived"]                     column name
                        filename = f"{findex}__{pdpn}__{slug}"  naming scheme

────────────────────────────────────────────────────────────────────────────────
ALL OTHER SCRIPTS       Zero corpus coupling                    operate on CSL
                        SG02, SG03, SG04, all SP, SA, SD        corpus-agnostic
────────────────────────────────────────────────────────────────────────────────
```

**Key finding:** the corpus coupling is contained in exactly 3 files.  
SG01's column-name coupling is the most fragile because it is inline in the
extraction loop — 4 hardcoded string literals that would silently produce empty
output for any corpus with different column headers.

---

## SECTION 2 — CORPUS.JSON SCHEMA PROPOSAL

Every corpus is described by a single `corpus.json` file.  
The pipeline reads this file at startup instead of hardcoded constants.

### Full schema with annotations

```json
{
  "$schema": "https://axis-niddhi.local/corpus-schema/v1.0.json",
  "$comment": "Corpus descriptor for AXIS-NIDDHI V6. One file per corpus.",

  "corpus_id":   "puredhamma",
  "corpus_name": "Pure Dhamma",
  "corpus_version": "2026-02",
  "description": "Teachings originally published at PureDhamma.net",
  "archived_at": "2026-03-11",

  "source": {
    "type": "wordpress_zip",
    "zip_filename": "corpus-puredhamma.zip",
    "$comment_type": "One of: wordpress_zip | ghost_export | markdown_tree"
  },

  "database": {
    "name":     "corpus_puredhamma",
    "user":     "wp_user",
    "password": "wp_pass123",
    "$comment": "Credentials may also be supplied via env vars (preferred)."
  },

  "wordpress": {
    "alias":      "puredhamma_local",
    "admin_user": "axis_niddhi"
  },

  "languages": {
    "source": "en",
    "targets": ["pt"]
  },

  "post_index": {
    "filename":   "PDPN_01_Operational.csv",
    "delimiter":  ";",
    "encoding":   "utf-8",
    "columns": {
      "fin_dex":  "Fin-dex",
      "post_id":  "id_10WEB.io",
      "pdpn":     "PD#PN",
      "slug":     "Slug_Derived"
    },
    "$comment_columns": "Maps canonical field names to actual CSV column headers."
  },

  "identifier": {
    "pattern":    "{fin_dex}__{pdpn}__{slug}",
    "pdpn_regex": "^[A-Z]{2}\\.[A-Z]{2}\\.[0-9]{3}$",
    "$comment":   "Pattern for canonical filename. pdpn_regex validates entries."
  },

  "sections_file":  "MasterPDPN_Sections.csv",
  "glossary_file":  "Glossario_v5.csv",
  "menu_file":      "Translation_Control_Center.csv",

  "corpus_class":   "dhamma",
  "$comment_class": "Optional. Classifies the corpus by knowledge domain.
                     Known values: dhamma | philosophy | historical | literary | other.
                     Not used by the engine. Available for cataloguing, UI filtering,
                     and future multi-corpus index generation. V5.4 compatible: if absent,
                     defaults to null and the engine proceeds without it."
}
```

### Minimal required fields for a new corpus

```json
{
  "corpus_id":    "waharaka",
  "corpus_name":  "Waharaka Thero Teachings",
  "corpus_class": "dhamma",
  "source": { "type": "wordpress_zip", "zip_filename": "corpus-waharaka.zip" },
  "database": { "name": "corpus_waharaka" },
  "wordpress": { "alias": "waharaka_local" },
  "languages": { "source": "si", "targets": ["en"] },
  "post_index": {
    "filename": "WaharakaIndex.csv",
    "delimiter": ",",
    "columns": {
      "fin_dex": "Index",
      "post_id": "WP_ID",
      "pdpn":    "PostCode",
      "slug":    "Slug"
    }
  }
}
```

`corpus_class` is optional in both the full and minimal schemas. The engine
reads it only for logging and identification purposes. It has no effect on
pipeline execution. Omitting it does not cause any warning or fallback —
the field is classified as advisory metadata, not operational configuration.

Known values at V6 design time: `dhamma`, `philosophy`, `historical`,
`literary`, `other`. The list is not enforced by the schema — any string
is accepted. Standardisation of values is an operator convention, not an
engine constraint.

A corpus with only these fields can run the full SG phase without any
modification to the pipeline scripts.

---

## SECTION 3 — REQUIRED CHANGES TO CONFIG.PY

### What changes

`config.py` currently hardcodes corpus identity in the body of the file.  
In V6, it reads from a `corpus.json` descriptor and derives all corpus-specific
constants from that descriptor.

### What does NOT change

- `BASE_DIR` derivation from `BENG_BASE` env or `__file__` — unchanged
- `SCRIPTS_DIR`, `METADATA_DIR`, `LOG_DIR` — unchanged
- All `DIR_0N_*` path constants — unchanged
- `DIR_13_SSG_ENGINE`, `DIR_13_SSG_OUTPUT` — unchanged
- All credential functions (`get_deepl_key`, `get_wp_password`) — unchanged
- `SCHEMA_VERSION`, `SOURCE_LANG` — unchanged (SOURCE_LANG now from descriptor)

### Proposed config.py V6 diff (additive changes only)

```python
# ==============================================================================
# V6 ADDITION — corpus descriptor loader
# Place this block AFTER BASE_DIR/SCRIPTS_DIR declarations,
# BEFORE DB_CONFIG and WP_BASE_URL.
# ==============================================================================

import json as _json

# Active corpus is selected via env var AXIS_CORPUS (default: puredhamma)
# This allows: AXIS_CORPUS=waharaka axis pipeline --full
_CORPUS_ID    = os.environ.get("AXIS_CORPUS", "puredhamma")
_CORPUS_DIR   = BASE_DIR.parent / "corpora" / _CORPUS_ID
_CORPUS_JSON  = _CORPUS_DIR / "corpus.json"

# Graceful degradation: if corpus.json not found, fall back to V5.4 hardcoded values.
# This makes V6 config.py backward-compatible with V5.4 deployments.
_CORPUS = {}
if _CORPUS_JSON.exists():
    try:
        _CORPUS = _json.loads(_CORPUS_JSON.read_text(encoding="utf-8"))
    except Exception as _e:
        print(f"⚠️  corpus.json load failed ({_e}) — using V5.4 hardcoded defaults")

def _corpus_get(path: str, default):
    """Safely read a dotted path from _CORPUS dict. E.g. 'database.name'"""
    keys = path.split(".")
    node = _CORPUS
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            return default
        node = node[k]
    return node

# ==============================================================================
# CORPUS-DERIVED CONSTANTS (replace V5.4 hardcoded values)
# ==============================================================================

# V5.4:  DB_CONFIG = {"database": "beng_wp_21", ...}
# V6:    reads from corpus.json, falls back to V5.4 value if not present
DB_CONFIG = {
    "host":     "localhost",
    "user":     _corpus_get("database.user",     "wp_user"),
    "password": _corpus_get("database.password", "wp_pass123"),
    "database": _corpus_get("database.name",     "beng_wp_21"),
}

# V5.4:  WP_BASE_URL = "http://localhost/beng_feb2026"
# V6:    derived from corpus.json wordpress.alias
_WP_ALIAS   = _corpus_get("wordpress.alias", "beng_feb2026")
WP_BASE_URL = f"http://localhost/{_WP_ALIAS}"
WP_API_URL  = f"{WP_BASE_URL}/wp-json/wp/v2"
WP_API_POSTS = f"{WP_API_URL}/posts"
WP_API_PAGES = f"{WP_API_URL}/pages"
WP_ADMIN_USER = _corpus_get("wordpress.admin_user", "axis_niddhi")

# V5.4:  PDPN_CSV = METADATA_DIR / "PDPN_01_Operational.csv"
# V6:    filename from corpus.json post_index.filename
_INDEX_FILENAME = _corpus_get("post_index.filename", "PDPN_01_Operational.csv")
PDPN_CSV = METADATA_DIR / _INDEX_FILENAME

# V5.4:  SOURCE_LANG = "en" (was already env-aware)
# V6:    from corpus.json languages.source (same fallback)
SOURCE_LANG = os.environ.get(
    "BENG_SOURCE_LANG",
    _corpus_get("languages.source", "en")
)

# NEW in V6: column mapping (accessed by SG01)
# Scripts read this dict instead of hardcoding column names
CORPUS_COLUMNS = {
    "fin_dex": _corpus_get("post_index.columns.fin_dex", "Fin-dex"),
    "post_id": _corpus_get("post_index.columns.post_id", "id_10WEB.io"),
    "pdpn":    _corpus_get("post_index.columns.pdpn",    "PD#PN"),
    "slug":    _corpus_get("post_index.columns.slug",    "Slug_Derived"),
}

# NEW in V6: corpus identity (used in logs, tattoos, CLS entries)
CORPUS_ID   = _corpus_get("corpus_id",   "puredhamma")
CORPUS_NAME = _corpus_get("corpus_name", "Pure Dhamma")
```

### V6 config.py backward-compatibility guarantee

```
If corpus.json does NOT exist → _CORPUS = {} → all _corpus_get() return defaults
→ DB_CONFIG, WP_BASE_URL, PDPN_CSV, SOURCE_LANG are identical to V5.4 values
→ A V5.4 deployment with no corpus.json runs identically to V5.4
→ Zero breaking change
```

---

## SECTION 4 — IMPACT ON SG00 (reset_workspace.sh)

### Current coupling (3 hardcoded lines)

```bash
DB_NAME="beng_wp_21"
WP_ALIAS="beng_feb2026"
ZIP_FILE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.zip" | head -1)  # first-found only
```

### V6 change: read from corpus.json via shell helper

```bash
# ── V6 ADDITION — read corpus descriptor ─────────────────────────────────
CORPUS_ID="${AXIS_CORPUS:-puredhamma}"
CORPUS_DIR="$BENG_ROOT/corpora/$CORPUS_ID"
CORPUS_JSON="$CORPUS_DIR/corpus.json"

# Shell JSON reader (no jq dependency — pure bash + python3)
corpus_get() {
    # corpus_get <dotted.path> <default>
    local path="$1" default="$2"
    python3 -c "
import json, sys
try:
    data = json.load(open('$CORPUS_JSON'))
    keys = '$path'.split('.')
    node = data
    for k in keys:
        node = node[k]
    print(node)
except:
    print('$default')
" 2>/dev/null || echo "$default"
}

# Fallback to V5.4 values if corpus.json absent
if [[ -f "$CORPUS_JSON" ]]; then
    DB_NAME="${BENG_DB_NAME:-$(corpus_get database.name beng_wp_21)}"
    WP_ALIAS="${BENG_WP_ALIAS:-$(corpus_get wordpress.alias beng_feb2026)}"
    ZIP_FILENAME="$(corpus_get source.zip_filename '')"
    [[ -n "$ZIP_FILENAME" ]] \
        && ZIP_FILE="$CORPUS_DIR/sources/$ZIP_FILENAME" \
        || ZIP_FILE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.zip" | head -1)
else
    # V5.4 compatible fallback
    DB_NAME="${BENG_DB_NAME:-beng_wp_21}"
    WP_ALIAS="${BENG_WP_ALIAS:-beng_feb2026}"
    ZIP_FILE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.zip" | head -1)
fi
# ─────────────────────────────────────────────────────────────────────────
```

All other logic in SG00 is unchanged. The reset procedure, WP setup,
exorcism, and DB restore operate identically — they simply use corpus-derived
variable values instead of hardcoded ones.

**Change footprint:** replace 3 lines, add ~25 lines of boilerplate. Zero
functional change for the PureDhamma corpus.

---

## SECTION 5 — IMPACT ON SG01 (extract_html.py)

### Current coupling (4 inline column literals)

```python
wp_id  = int(row["id_10WEB.io"])   # ← corpus-specific column name
findex = str(row["Fin-dex"]).zfill(4)
pdpn   = str(row["PD#PN"]).strip()
slug   = clean_slug(str(row.get("Slug_Derived", "")))
```

### V6 change: read column names from CORPUS_COLUMNS

```python
# V6 addition — import CORPUS_COLUMNS from config
from config import (
    BASE_DIR, LOG_DIR, DIR_01_EXTRACTED, DIR_09_CSL,
    PDPN_CSV, DB_CONFIG, SOURCE_LANG,
    CORPUS_COLUMNS,   # ← V6 addition only
    CORPUS_ID,        # ← V6 addition only (for tattoo)
)

# V6 extraction loop — replace 4 hardcoded column references:
#   BEFORE: row["id_10WEB.io"], row["Fin-dex"], row["PD#PN"], row["Slug_Derived"]
#   AFTER:  row[CORPUS_COLUMNS["post_id"]], etc.

for _, row in df.iterrows():
    wp_id  = int(row[CORPUS_COLUMNS["post_id"]])
    findex = str(row[CORPUS_COLUMNS["fin_dex"]]).zfill(4)
    pdpn   = str(row[CORPUS_COLUMNS["pdpn"]]).strip()
    slug   = clean_slug(str(row.get(CORPUS_COLUMNS["slug"], "")))
    # ... rest of loop unchanged
```

The tattoo generator also becomes corpus-aware:

```python
def generate_tattoo(row: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!--
💎 AXIS-NIDDHI — CANONICAL SOURCE ARTIFACT
===================================================
Corpus:       {CORPUS_ID}
Fin-dex:      {row[CORPUS_COLUMNS['fin_dex']]}
PD#PN:        {row[CORPUS_COLUMNS['pdpn']]}
Original-Slug:{row[CORPUS_COLUMNS['slug']]}
Source-ID:    {row[CORPUS_COLUMNS['post_id']]}
Language:     {SOURCE_LANG}
Extracted-At: {now}
Origin:       MySQL / {DB_CONFIG['database']}
===================================================
DO NOT EDIT THIS FILE MANUALLY. THIS IS THE TREASURE.
-->
"""
```

**Change footprint:** 4 line substitutions in the extraction loop, 2 additional
imports. Zero change to extraction logic, retry, CLS integration, or logging.

---

## SECTION 6 — MINIMAL ADAPTER INTERFACE

Adapters normalize different source formats into the existing pipeline intake
point: a directory of `.html` files at `01-extracted-htmls/{source_lang}/`
with the canonical tattoo header and filename pattern.

### Interface contract

Every adapter must implement one function:

```python
# adapters/base_adapter.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator
from dataclasses import dataclass

@dataclass
class ExtractedPost:
    """
    Normalized post as produced by any adapter.
    Adapters convert their native format to this structure.
    The SG01 loop writes this to disk.
    """
    fin_dex:  str    # zero-padded 4-digit index ("0001")
    pdpn:     str    # canonical identifier ("PD.AA.001")
    slug:     str    # sanitized slug ("meditation-and-mind")
    content:  str    # raw HTML content (no wrapper tags)
    source_id: str   # original ID in source system

class BaseAdapter(ABC):
    """
    Minimal interface all adapters must implement.
    Adapters are thin: they only parse the source and yield ExtractedPost.
    They do NOT write to disk. SG01 owns the write.
    """

    def __init__(self, corpus_descriptor: dict, source_path: Path):
        self.descriptor  = corpus_descriptor
        self.source_path = source_path
        self.columns     = corpus_descriptor.get("post_index", {}).get("columns", {})

    @abstractmethod
    def extract(self) -> Iterator[ExtractedPost]:
        """
        Yield one ExtractedPost per content item in the source.
        Must be lazy (generator) for large corpora.
        """
        ...

    @property
    def source_type(self) -> str:
        return self.descriptor.get("source", {}).get("type", "unknown")
```

### Adapter implementations

**Adapter A — wordpress_zip (existing corpus, V5.4 compatible)**

```python
# adapters/wordpress_zip.py

class WordPressZipAdapter(BaseAdapter):
    """
    Adapter for WordPress backup ZIPs.
    This is the existing SG00+SG01 behaviour, extracted into the adapter interface.
    Reads from MySQL (populated by SG00) via the post_index CSV.
    V5.4 pipeline = this adapter with corpus_descriptor = {"columns": {...V5.4 defaults...}}
    """

    def extract(self) -> Iterator[ExtractedPost]:
        import pandas as pd
        import pymysql

        col  = self.columns
        csv  = self.source_path / self.descriptor["post_index"]["filename"]
        sep  = self.descriptor.get("post_index", {}).get("delimiter", ";")
        db   = self.descriptor.get("database", {})

        df = pd.read_csv(csv, sep=sep, encoding="utf-8", dtype=str)
        df = df[df[col["post_id"]].notna()]

        conn = pymysql.connect(
            host="localhost",
            user=db.get("user", "wp_user"),
            password=db.get("password", "wp_pass123"),
            database=db.get("name"),
            cursorclass=pymysql.cursors.DictCursor
        )
        # ... table detection and extraction loop (same as SG01) ...
        # yields ExtractedPost for each row
        conn.close()
```

**Adapter B — ghost_export (future)**

```python
# adapters/ghost_export.py

class GhostExportAdapter(BaseAdapter):
    """
    Adapter for Ghost CMS JSON export files.
    Ghost exports contain posts as JSON with HTML content.
    No MySQL dependency — reads directly from the export JSON.
    """

    def extract(self) -> Iterator[ExtractedPost]:
        import json
        export = json.loads((self.source_path / "ghost-export.json").read_text())
        posts  = export.get("data", {}).get("posts", [])
        for i, post in enumerate(posts):
            yield ExtractedPost(
                fin_dex   = str(i + 1).zfill(4),
                pdpn      = post.get("slug", f"GH.XX.{i:03d}"),
                slug      = post.get("slug", "unknown"),
                content   = post.get("html", ""),
                source_id = str(post.get("id", ""))
            )
```

**Adapter C — markdown_tree (future)**

```python
# adapters/markdown_tree.py

class MarkdownTreeAdapter(BaseAdapter):
    """
    Adapter for a directory tree of Markdown files.
    No external system dependency — reads .md files directly.
    Converts Markdown → HTML using python-markdown.
    """

    def extract(self) -> Iterator[ExtractedPost]:
        import markdown
        md_files = sorted(self.source_path.glob("**/*.md"))
        for i, md_file in enumerate(md_files):
            html = markdown.markdown(md_file.read_text(encoding="utf-8"))
            yield ExtractedPost(
                fin_dex   = str(i + 1).zfill(4),
                pdpn      = md_file.stem,
                slug      = md_file.stem,
                content   = html,
                source_id = str(md_file)
            )
```

### Adapter registry

```python
# adapters/__init__.py

from .wordpress_zip import WordPressZipAdapter
from .ghost_export  import GhostExportAdapter
from .markdown_tree import MarkdownTreeAdapter

ADAPTERS = {
    "wordpress_zip":  WordPressZipAdapter,
    "ghost_export":   GhostExportAdapter,
    "markdown_tree":  MarkdownTreeAdapter,
}

def get_adapter(corpus_descriptor: dict, source_path) -> BaseAdapter:
    source_type = corpus_descriptor.get("source", {}).get("type", "wordpress_zip")
    cls = ADAPTERS.get(source_type)
    if cls is None:
        raise ValueError(f"Unknown source type: {source_type}. Known: {list(ADAPTERS)}")
    return cls(corpus_descriptor, source_path)
```

The critical design property: `SG01_extract_html.py` only needs to change its
extraction loop to call `adapter.extract()` instead of inline MySQL queries.
The rest of SG01 — tattoo generation, CLS integration, idempotency checks,
logging — is unchanged.

---

## SECTION 7 — CSL AS CANONICAL INTERMEDIATE MODEL

### Formal declaration

The CSL (Canonical Source Library) is the corpus-agnostic intermediate
representation of any corpus processed by AXIS-NIDDHI.

```
[ANY SOURCE FORMAT]
       │
       ▼  adapter.extract() → ExtractedPost
[01-extracted-htmls/{lang}/]
       │
       ▼  SG02_preprocess_html.py (unchanged)
[02-preprocessed/{lang}/]
       │
       ▼  SG03_build_csl.py (unchanged)
[09-csl/{PDPN}/]              ← CSL entry point
       │                         identity.json + content.html per language
       │
       ├──▶  SP phase (translation, migration)   — corpus-agnostic ✔
       ├──▶  SA phase (audit, freeze manifest)   — corpus-agnostic ✔
       └──▶  SD phase (SSG, static site, WP)     — corpus-agnostic ✔
```

Everything downstream of `09-csl/` is already V6-ready.  
The adapters are the only new layer. Everything else is unchanged.

### CSL identity.json remains the canonical post record

The `identity.json` schema (V3.1) already supports multi-corpus operation:

```json
{
  "pdpn": "PD.AA.001",
  "schema_version": "3.1",
  "titles": { "en": "...", "pt": "..." },
  "artifacts": {
    "en-US": { "status": "canonical", "integrity_sha256": "..." },
    "pt-BR": { "status": "derived",   "integrity_sha256": "..." }
  },
  "lineage": {
    "origin": {
      "corpus_id": "puredhamma",   ← V6 addition: one field in lineage.origin
      ...
    }
  }
}
```

V6 adds exactly one field to `lineage.origin`: `corpus_id`. This is written
by the adapter at extraction time and carried through the entire pipeline.
No schema migration required for existing V5.4 CSL entries — the field is
optional and defaults to `"puredhamma"` if absent.

---

## SECTION 8 — FILESYSTEM LAYOUT (V6)

```
/beng-engine/              ← engine (V6 rename of /beng-fut/pipeline)
├── scripts/               ← 28 CORE scripts (unchanged)
├── 13-ssg/                ← SSG engine (unchanged)
├── metadata/              ← engine-level metadata
└── logs/

/beng-corpora/             ← V6 addition: one directory per corpus
├── puredhamma/
│   ├── corpus.json        ← descriptor
│   ├── sources/
│   │   └── corpus-puredhamma.zip
│   ├── metadata/
│   │   ├── PDPN_01_Operational.csv
│   │   ├── MasterPDPN_Sections.csv
│   │   └── Glossario_v5.csv
│   ├── 01-extracted-htmls/
│   ├── 02-preprocessed/
│   ├── 09-csl/            ← corpus-specific CSL
│   ├── 13-static-site/    ← corpus-specific output
│   └── logs/
├── waharaka/
│   ├── corpus.json
│   ├── sources/
│   │   └── corpus-waharaka.zip
│   └── ...
└── other-teachings/
    └── ...
```

`BENG_BASE` in V6 would point to the corpus workspace, not the engine:

```bash
# V5.4 pattern (single corpus)
export BENG_BASE="/beng-fut/pipeline"

# V6 pattern (per corpus)
export BENG_BASE="/beng-corpora/puredhamma"
export AXIS_CORPUS="puredhamma"

# Or using the axis CLI
AXIS_CORPUS=waharaka axis pipeline --full
```

The engine (`scripts/`, `13-ssg/`) is shared. The workspace (`09-csl/`,
`01-extracted-htmls/`, etc.) is per-corpus.

---

## SECTION 9 — CLI EXTENSION (V6)

```bash
# Current V5.4 commands (unchanged)
axis build-site
axis preview
axis status
axis doctor
axis pipeline [--full | --genesis | --preservation | ...]
axis build-release

# V6 additions
axis corpus list                   # list all corpora in /beng-corpora/
axis corpus build <name>           # AXIS_CORPUS=<name> axis pipeline --full
axis corpus verify <name>          # run verify_pipeline_integrity against corpus
axis corpus status <name>          # CSL count, translation progress, last build
axis corpus release <name>         # build_release_snapshot for named corpus
```

Implementation: `axis corpus` is a dispatcher. Each subcommand sets
`AXIS_CORPUS=<name>` and `BENG_BASE=/beng-corpora/<name>`, then delegates
to the existing pipeline infrastructure. No pipeline script changes required.

---

## SECTION 10 — MIGRATION PATH FROM V5.4

### Phase 1 — V5.4 (current, frozen)
Single corpus. Hardcoded constants. Fully operational.
No changes required. No action needed.

### Phase 2 — V6.0: Descriptor layer (non-breaking)

**Step 1:** Create `corpus.json` for PureDhamma corpus.

```bash
mkdir -p /beng-corpora/puredhamma
cat > /beng-corpora/puredhamma/corpus.json << 'EOF'
{
  "corpus_id": "puredhamma",
  "corpus_name": "Pure Dhamma",
  "source": { "type": "wordpress_zip", "zip_filename": "corpus-puredhamma.zip" },
  "database": { "name": "beng_wp_21", "user": "wp_user", "password": "wp_pass123" },
  "wordpress": { "alias": "beng_feb2026", "admin_user": "axis_niddhi" },
  "languages": { "source": "en", "targets": ["pt"] },
  "post_index": {
    "filename": "PDPN_01_Operational.csv",
    "delimiter": ";",
    "columns": {
      "fin_dex": "Fin-dex",
      "post_id": "id_10WEB.io",
      "pdpn":    "PD#PN",
      "slug":    "Slug_Derived"
    }
  }
}
EOF
```

**Step 2:** Apply V6 patch to `config.py` (additive block, 45 lines).  
Backward-compatible: V5.4 deployments without `corpus.json` are unaffected.

**Step 3:** Apply V6 patch to `SG00_reset_workspace.sh` (replace 3 lines, add 25).  
Same behavior for PureDhamma. New corpora read their values from descriptor.

**Step 4:** Apply V6 patch to `SG01_extract_html.py` (4 line substitutions in loop).  
Column names now read from `CORPUS_COLUMNS` dict instead of string literals.

**Step 5:** Create `adapters/` directory with `base_adapter.py` and `wordpress_zip.py`.  
SG01 delegates extraction to adapter. All other logic unchanged.

**Step 6:** Run full rebuild verification.

```bash
AXIS_CORPUS=puredhamma axis pipeline --full
# Expected: identical output to V5.4 — same 748 posts, same CSL, same site
```

**Step 7:** Freeze V6.0 release with the same procedure as V5.4.

### Phase 3 — V6.1+: Second corpus onboarding

Once V6.0 is verified against PureDhamma:

```bash
# Create corpus descriptor for new corpus
mkdir -p /beng-corpora/waharaka
# ... write corpus.json ...

# Run genesis for new corpus
AXIS_CORPUS=waharaka axis pipeline --genesis

# Verify CSL
axis corpus verify waharaka
```

No engine changes required. The adapter handles source-format differences.
All SP, SA, SD scripts operate on the new corpus's `09-csl/` identically.

---

## SECTION 11 — CHANGE FOOTPRINT SUMMARY

```
FILE                        V6 CHANGE                    RISK
────────────────────────────────────────────────────────────────────────
config.py                   +45 lines (additive block)   LOW
                            Existing lines unchanged      Backward-compatible
                            via _corpus_get() fallbacks

SG00_reset_workspace.sh     3 lines replaced + 25 added  LOW
                            Behavior identical for        Env override preserved
                            PureDhamma (same defaults)

SG01_extract_html.py        4 line substitutions in loop  LOW
                            +2 imports (CORPUS_COLUMNS,   Fallback to V5.4 values
                            CORPUS_ID)                    if corpus.json absent

adapters/                   NEW directory (4 files)       ZERO
                            Not imported by any existing  Purely additive
                            V5.4 script

corpus.json (puredhamma)    NEW file                      ZERO
                            Describes existing corpus     No existing file touched

────────────────────────────────────────────────────────────────────────
ALL OTHER SCRIPTS           NO CHANGE                     —
SG02, SG03, SG04            Zero corpus coupling          Already V6-ready
All SP, SA, SD scripts      Operate on CSL               Already V6-ready
build.py (SSG)              Zero corpus coupling          Already V6-ready
verify_pipeline_integrity   +3 lines for corpus check     LOW
build_release_snapshot      +corpus-aware copy section    LOW
────────────────────────────────────────────────────────────────────────

TOTAL NEW CODE:     ~150 lines across 3 modified files + 4 new files
TOTAL RISK:         LOW — all changes are additive or backward-compatible
V5.4 IMPACT:        ZERO — V5.4 deployments without corpus.json unchanged
```

---

## SECTION 12 — WHAT V6 IS NOT

To prevent scope creep, the following are explicitly outside V6:

| Item | Status | Rationale |
|---|---|---|
| Multi-language SSG themes per corpus | Deferred V7 | Templates work for all corpora |
| Cloud deployment (S3, Netlify) | Out of scope | Offline-first principle |
| Database-backed corpus registry | Out of scope | Filesystem is the registry |
| Automated corpus ingestion pipeline | Deferred V7 | Manual ZIP provision is intentional |
| Git integration | Operator choice | Not an engine concern |
| Parallel multi-corpus builds | Deferred V7 | Sequential per-corpus is sufficient |

---

## APPENDIX — V5.4 → V6 TIMELINE RECOMMENDATION

V6 should not be implemented until a second corpus is acquired and ready for
onboarding. The V6 architecture is fully designed and the change footprint is
precisely quantified. Implementation is a controlled operation, not a research
problem.

```
Trigger for V6 implementation:
  A second corpus ZIP + post index is available for onboarding.

Estimated implementation time:
  Phase 2 (descriptor layer):  1–2 sessions
  Phase 3 (second corpus):     1 session

V5.4 remains the production baseline until V6.0 is verified against PureDhamma.
```

---

*AXIS-NIDDHI V6 — Architectural outline complete.*  
*Design finalized 2026-03-11. Implementation deferred pending second corpus.*
