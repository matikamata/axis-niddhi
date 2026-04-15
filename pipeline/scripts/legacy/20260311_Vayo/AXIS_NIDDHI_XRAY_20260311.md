# AXIS-NIDDHI — FULL PIPELINE X-RAY
**Date:** 2026-03-11  
**Analyst:** Vayo (Technical Architect)  
**Source:** Code-level analysis — 82 scripts scanned  
**Version analyzed:** run_full_pipeline.sh V5.2 / config.py V2.1

---

## SECTION 1 — REAL PIPELINE FLOW

```
┌─────────────────────────────────────────────────────────────────────┐
│  ENTRY POINT: run_full_pipeline.sh  (--full / --genesis / etc.)     │
│  BENG_BASE = /beng-fut/pipeline  (via env or default)               │
└────────────────────────┬────────────────────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────────────┐
        │  [DI] DIAGNOSTIC  (optional pre-flight)               │
        │  DI00_sql_vs_csl_audit.py  ───► MI99_mission_report   │
        └────────────────┬──────────────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────────────┐
        │  [SG] GENESIS — Full rebuild from WP backup           │
        │                                                       │
        │  SG00_reset_workspace.sh   (MySQL + dirs reset)       │
        │        │                                              │
        │        ▼                                              │
        │  SG01_extract_html.py      ──► 01-extracted-htmls/    │
        │        │                       [SRO — READ-ONLY]      │
        │        ▼                                              │
        │  SG02_preprocess_html.py   ──► 02-preprocessed/       │
        │        │                                              │
        │        ▼                                              │
        │  SG03_build_csl.py --apply ──► 09-csl/[PDPN]/        │
        │        │                       source/en-US/          │
        │        │                       meta/identity.json     │
        │        ▼                                              │
        │  SG04_harvest_assets.py    ──► 09-csl/meta/pronun.    │
        │        │                       13-static-site/assets/ │
        │        ▼                                              │
        │  MI99_mission_report.py                               │
        └────────────────┬──────────────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────────────┐
        │  [SP] PRESERVATION — Identity + Translation           │
        │                                                       │
        │  SP01_migrate_ptbr.py --apply   (PT legacy import)    │
        │        │                                              │
        │        ▼                                              │
        │  SP02_upgrade_identity.py --apply  (schema → v3.1)    │
        │        │                                              │
        │        ▼                                              │
        │  SP03_mass_migration.py --apply    (Golden Sample)    │
        │        │                                              │
        │        ▼                                              │
        │  SP04_phase5_migration.py --apply  (v3.1 stamp)       │
        │        │                                              │
        │        ▼                                              │
        │  SP05_fix_headers.py --apply       (HTML headers)     │
        │        │                                              │
        │        ▼                                              │
        │  SP06_audio_converter.py --apply   (audio shortcodes) │
        │        │                                              │
        │        ▼  [SEAL 1]                                    │
        │  SP02_upgrade_identity.py --apply --force             │
        │        │                                              │
        │        ▼                                              │
        │  SP11_translate_titles.py --apply  (EN→PT titles)     │
        │        │                                              │
        │        ▼                                              │
        │  SP07_compile_glossary.py          (CSL→JSON)         │
        │        │                                              │
        │        ▼                                              │
        │  SP08_glossary_gate.py             (human review)     │
        │        │                                              │
        │        ▼                                              │
        │  SP09_translation_menu.py  ──► Translation_Control_   │
        │        │                       Center.csv (regenerated)│
        │        ▼                                              │
        │  [MANUAL GATE] ──── operator marks COMMAND=YES        │
        │        │                                              │
        │        ▼   (manual execution outside pipeline)        │
        │  SP10_translate_deepl.py   ──► 09-csl/*/pt-BR/        │
        │        │                                              │
        │        ▼   (manual, after SP10)                       │
        │  SP02_upgrade_identity.py --apply --force             │
        │                                                       │
        │  MI99_mission_report.py                               │
        └────────────────┬──────────────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────────────┐
        │  [SA] AUDIT — Integrity verification                  │
        │                                                       │
        │  SP02_upgrade_identity.py   (dry-run consistency)     │
        │  SA01_final_audit.py --apply                          │
        │  SA02_freeze_manifest.py    (SHA-256 manifest)        │
        │  SA03_translation_progress.py                         │
        └────────────────┬──────────────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────────────┐
        │  [SD] DISTRIBUTION                                    │
        │                                                       │
        │  SD01_generate_asset_map.py ──► asset_map.json        │
        │        │                                              │
        │        ▼                                              │
        │  [SD03] ─ ABORT if not found ─────────────────────►  │
        │  13-ssg/SD03_static_site_build.py  ←── ⚠️  MISSING   │
        │  (= build.py, deployed by setup_v54_static_site.sh)  │
        │        │                                              │
        │        ▼                                              │
        │  SD04_wordpress_inject.py  [human gate / auto]        │
        │        │                                              │
        │        ▼                                              │
        │  MI99_mission_report.py                               │
        └───────────────────────────────────────────────────────┘
```

---

## SECTION 2 — SCRIPT DEPENDENCY GRAPH

### Active Pipeline Scripts

| Script | Imports from | Calls | Stage |
|---|---|---|---|
| `config.py` | os, sys, pathlib | — | CORE/CONFIG |
| `pipeline_utils.py` | hashlib, json, os, shutil | — | CORE/LIB |
| `cls_tools.py` | pipeline_utils | — | CORE/LIB |
| `SG00_reset_workspace.sh` | — | MySQL, bash | SG |
| `SG01_extract_html.py` | config, pandas, pymysql, cls_tools (optional) | os.system chmod | SG |
| `SG02_preprocess_html.py` | config, bs4 | — | SG |
| `SG03_build_csl.py` | config | — | SG |
| `SG04_harvest_assets.py` | pathlib (**hardcoded /beng-fut**) | — | SG |
| `SP01_migrate_ptbr.py` | config | — | SP |
| `SP02_upgrade_identity.py` | config, pipeline_utils | — | SP |
| `SP03_mass_migration.py` | config | — | SP |
| `SP04_phase5_migration.py` | config | — | SP |
| `SP05_fix_headers.py` | config, pipeline_utils | — | SP |
| `SP06_audio_converter.py` | pathlib (**hardcoded /beng-fut**) | — | SP |
| `SP07_compile_glossary.py` | csv, json (**hardcoded /beng-fut**) | — | SP |
| `SP08_glossary_gate.py` | pathlib (**hardcoded /beng-fut**) | — | SP |
| `SP09_translation_menu.py` | config | — | SP |
| `SP10_translate_deepl.py` | config, pipeline_utils, requests | — | SP |
| `SP11_translate_titles.py` | config, pipeline_utils | — | SP |
| `SA01_final_audit.py` | config | — | SA |
| `SA02_freeze_manifest.py` | config | — | SA |
| `SA03_translation_progress.py` | config | — | SA |
| `SD01_generate_asset_map.py` | config | — | SD |
| `SD04_wordpress_inject.py` | config, requests | — | SD |
| `MI99_mission_report.py` | config | — | SUPPORT |
| `DI00_sql_vs_csl_audit.py` | (**hardcoded /media/sanghop**) | — | DI |
| `build.py` (= SD03) | config, src/loaders, src/renderers, src/transformers | — | SD/SSG |

### SSG Sub-modules (deployed to 13-ssg/src/ by setup_v54)

| Module | Resides in project as | Deployed to | Uses relative import |
|---|---|---|---|
| `csl_loader.py` | flat in scripts/ | `13-ssg/src/loaders/` | YES — `from .identity_loader` |
| `identity_loader.py` | flat in scripts/ | `13-ssg/src/loaders/` | YES |
| `post_renderer.py` | flat in scripts/ | `13-ssg/src/renderers/` | YES |
| `index_renderer.py` | flat in scripts/ | `13-ssg/src/renderers/` | YES |
| `nav_builder.py` | flat in scripts/ | `13-ssg/src/transformers/` | YES |
| `link_resolver.py` | flat in scripts/ | `13-ssg/src/transformers/` | YES |
| `asset_mapper.py` | flat in scripts/ | `13-ssg/src/transformers/` | YES |
| `language_router.py` | flat in scripts/ | `13-ssg/src/transformers/` | YES |
| `models.py` | flat in scripts/ | `13-ssg/src/` | NO |

---

## SECTION 3 — DATA FLOW GRAPH

```
WordPress backup (.ZIP / MySQL dump)
    │
    ▼  [SG00]
runtime_wp/wp-content/uploads/   ──────────────────────► [SG04]
    │
    ▼  [SG01]
01-extracted-htmls/en-US/          ← SRO (READ-ONLY after SG01)
    │
    ▼  [SG02]
02-preprocessed/en-US/
    │
    ▼  [SG03]
09-csl/[PDPN]/
    ├── source/en-US/content.html  ← canonical EN source
    ├── source/pt-BR/content.html  ← added by SP10 (DeepL)
    └── meta/identity.json         ← mutated by SP01→SP11 chain
              │
              ├── [SP09] ──────────► metadata/Translation_Control_Center.csv
              ├── [SP07] ──────────► metadata/glossary_config.json
              ├── [SA02] ──────────► metadata/freeze_manifest.json
              └── [SA03] ──────────► metadata/translation_progress.json
    │
    ▼  [SD01]
metadata/asset_map.json
    │
    ▼  [SD03 / build.py]
13-static-site/                    ← final static output
    ├── pages/[section]/[slug]/index.html
    ├── assets/
    └── index.html

    ▼  [SD04]
WordPress local (beng_wp_21) via REST API
    └── http://localhost/beng_feb2026
```

| Directory | Produced By | Consumed By |
|---|---|---|
| `01-extracted-htmls/en-US/` | SG01 | SG02 |
| `02-preprocessed/en-US/` | SG02 | SG03 |
| `09-csl/*/source/en-US/` | SG03 | SP02–SP11, SA01–SA03, SD01, SD03 |
| `09-csl/*/source/pt-BR/` | SP10 | SA03, SD03, SD04 |
| `09-csl/*/meta/identity.json` | SG03 | SP01–SP11 (mutated), SA01–SA03, SD03 |
| `metadata/Translation_Control_Center.csv` | SP09 | SP10 (manual) |
| `metadata/glossary_config.json` | SP07 | SP08, SP10 |
| `metadata/asset_map.json` | SD01 | SD03 (build.py) |
| `13-ssg/` (engine) | setup_v54_static_site.sh | SD03 (build.py) |
| `13-static-site/` (output) | SD03 (build.py) | axis preview / serve |
| `snapshots/` | SN01 | recovery only |
| `logs/` | all scripts | MI99 |

---

## SECTION 4 — SCRIPT CLASSIFICATION

### CORE (called by run_full_pipeline.sh)

```
config.py               pipeline_utils.py       cls_tools.py
SG00_reset_workspace.sh SG01_extract_html.py    SG02_preprocess_html.py
SG03_build_csl.py       SG04_harvest_assets.py
SP01_migrate_ptbr.py    SP02_upgrade_identity.py SP03_mass_migration.py
SP04_phase5_migration.py SP05_fix_headers.py    SP06_audio_converter.py
SP07_compile_glossary.py SP08_glossary_gate.py  SP09_translation_menu.py
SP10_translate_deepl.py  SP11_translate_titles.py
SA01_final_audit.py      SA02_freeze_manifest.py SA03_translation_progress.py
SD01_generate_asset_map.py SD04_wordpress_inject.py
MI99_mission_report.py   SN01_snapshot_csl.sh
build.py [= SD03]        models.py + SSG src/ modules
```

### SUPPORT (utility scripts, called independently)

```
DI00_sql_vs_csl_audit.py     axis_cli.sh            axis_runner.sh
run_sp11_and_report.sh       redeploy_cls_and_backfill.sh
activate_cls_v11.sh          setup_v54_static_site.sh
run_sp11_and_report.sh       run_full_pipeline.sh (orchestrator)
```

### DEPRECATED (superseded by SP series — confirmed by code comments)

```
01_extract_v3_global.py          → superseded by SG01
02_preprocess_v4_1_iframes.py    → superseded by SG02
03_build_csl_v1.py               → superseded by SG03
04_compile_glossary.py           → superseded by SP07
05_translate_pilot_v5_surgeon.py → superseded by SP10
05a_upload_glossary_deepl.py     → superseded by SP07/SP08
06_inject_pilot_v3_pages.py      → superseded by SD04
07a_generate_menu_v6_schema_aware.py → superseded by SP09
07b_execute_menu_v3_guardian.py  → superseded by SP09
08_mass_inject_v5_resilient.py   → superseded by SD04
09_upgrade_identity_v3_audited.py → superseded by SP02
10_mass_migration_phase5.py      → superseded by SP04
11_final_audit_and_cleanup.py    → superseded by SA01
12_fix_headers_and_identity.py   → superseded by SP05
14_sync_titles_from_ledger.py    → superseded by SP11
15_Relatório_de_Estrutura_de_Subpastas.py → audit utility
S04_upgrade_identity_v3.py       → superseded by SP02
S07_fix_headers_identity.py      → superseded by SP05
S10_execute_translation_deepl.py → superseded by SP10
S14_generate_asset_map.py        → superseded by SD01
SD02_generate_slug_map.py        → absorbed into build.py internally
SP05_fix_headers_v51.py          → superseded by SP05 (deploy_v51.sh copies it as SP05)
```

### ORPHAN (Cópia files — filesystem duplicates, never executed)

```
SG01_extract_html__Cópia_.py
SP02_upgrade_identity__Cópia_.py
SP10_translate_deepl__Cópia_.py
SP11_translate_titles__Cópia_.py
cls_tools__Cópia_.py
cls_tools__Cópia_2_.py
generate_asset_map__Cópia_.py
audit_ssg_zip.py                  (hardcoded /beng/pipeline, never called)
auditoria_forense_youtube_csl.py  (standalone forensic tool, not in pipeline)
ingest.py                         (S12b legacy, not in pipeline)
discovery.py                      (S12 legacy, not in pipeline)
```

---

## SECTION 5 — CRITICAL FRAGILITIES

### F1 — SOVEREIGN ABORT: SD03 NAME MISMATCH  ★ CRITICAL
```
run_full_pipeline.sh expects:  13-ssg/SD03_static_site_build.py
setup_v54_static_site.sh deploys: SD03_static_site_build.py (from $SCRIPTS/)
build.py in project is named:  build.py

Pipeline ABORTS at SD phase if setup_v54 was not run first.
The project has no file named SD03_static_site_build.py.
```
**Impact:** SD phase hard-abort on every fresh deploy.

---

### F2 — DI00 DEAD PATH: hardcoded to old machine  ★ HIGH
```python
# DI00_sql_vs_csl_audit.py line 41-43:
BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/Brasileirinho_Engine_v2/pipeline")
CSL_DIR  = BASE_DIR / "09-csl"
SQL_PATH = Path("/media/sanghop/BrasileirinhoHD/...")
```
**Impact:** DI phase fails immediately on any machine that is not the original dev machine. Script is unreachable.

---

### F3 — SP06, SP07, SP08, SG04: NOT importing config.py  ★ HIGH
```
SP06_audio_converter.py:  CSL_DIR = Path("/beng-fut/pipeline/09-csl")  — hardcoded
                           ASSETS_DIR = Path("/beng-fut/pipeline/13-ssg/assets/audio/en-US")
SP07_compile_glossary.py: BASE_DIR = "/beng-fut/pipeline"  — hardcoded string (not Path)
SP08_glossary_gate.py:    BASE_DIR = Path("/beng-fut/pipeline")  — hardcoded
SG04_harvest_assets.py:   BENG_ROOT = Path("/beng-fut")  — hardcoded
```
**Impact:** These 4 scripts break immediately if `BENG_BASE` is overridden or the pipeline is relocated. They ignore the canonical config.py entirely.

---

### F4 — SSG PACKAGE STRUCTURE: relative imports require deploy step  ★ MEDIUM
```
csl_loader.py line 4:  from .identity_loader import load_identity
```
These modules use relative imports — they **cannot** run from the flat `scripts/` directory. They require `setup_v54_static_site.sh` to first deploy them into `13-ssg/src/{loaders,renderers,transformers}/` with proper `__init__.py` files.

If `setup_v54_static_site.sh` is not run before `axis build-site` or SD phase, build.py will fail with `ImportError`.

**Impact:** SSG fails silently or with cryptic ImportError on clean environments.

---

### F5 — SP03 AND SP04: OVERLAPPING GOLDEN SAMPLE APPLICATION  ★ MEDIUM
```
SP03_mass_migration.py:    Applies schema v3.1 Golden Sample to all CSL posts
SP04_phase5_migration.py:  Applies schema v3.1 stamp to all CSL posts
```
Both scripts iterate all of `09-csl/`, both write `schema_version: "3.1"` to `identity.json`, both calculate SHA-256 hashes. SP04's own docstring references itself as `phase5_migration.py` — a legacy name. The functional distinction is thin (SP03 = full Golden Sample rewrite; SP04 = stamp pass).  
**Risk:** If run out of order, SP04 can overwrite SP03's Golden Sample fields. If SP02 is run between them (as it is), the sequencing is fragile.

---

### F6 — axis_runner.sh REFERENCES NON-EXISTENT sp12  ★ LOW
```bash
# axis_runner.sh:
streamlit run /beng-fut/pipeline/scripts/sp12_guardian/sp12_app.py
```
No `SP12` script or `sp12_guardian/` directory exists in the repository.  
**Impact:** `axis sp12` command fails. Does not affect pipeline execution.

---

### F7 — SN01 SNAPSHOT DIR: /beng-fut/snapshots not under BENG_BASE  ★ LOW
```bash
SNAP_DIR="/beng-fut/snapshots"  # hardcoded, not derived from BENG_BASE
```
If BENG_BASE is relocated, snapshots go to a disconnected path.

---

## SECTION 6 — MINIMAL STABILIZATION PLAN

Priority order. No architectural rewrites. Surgical corrections only.

---

### FIX 1 — Rename build.py → SD03_static_site_build.py in scripts/
```bash
# In the scripts/ directory:
cp build.py SD03_static_site_build.py
```
Or alternatively — add one line to `setup_v54_static_site.sh`:
```bash
# Change:
cp "$SCRIPTS/SD03_static_site_build.py" "$SSG/build.py"
# To: (also create symlink for run_full_pipeline.sh direct call)
cp "$SCRIPTS/build.py" "$SSG/SD03_static_site_build.py"
cp "$SCRIPTS/build.py" "$SSG/build.py"
```
**Eliminates F1.** Zero logic change.

---

### FIX 2 — Patch DI00 to use config.py
```python
# Replace lines 41-43 in DI00_sql_vs_csl_audit.py:
# OLD:
BASE_DIR = Path("/media/sanghop/...")
CSL_DIR  = BASE_DIR / "09-csl"
SQL_PATH = Path("/media/sanghop/...")

# NEW:
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import BASE_DIR, DIR_09_CSL
CSL_DIR  = DIR_09_CSL
SQL_PATH = BASE_DIR.parent / "sources" / "tenweb_backup_db.sql"
```
**Eliminates F2.** DI phase becomes runnable on any machine.

---

### FIX 3 — Patch SP06, SP07, SP08, SG04 to use config.py

**SP06_audio_converter.py** — replace lines 30-32:
```python
# OLD:
CSL_DIR   = Path("/beng-fut/pipeline/09-csl")
ASSETS_DIR = Path("/beng-fut/pipeline/13-ssg/assets/audio/en-US")
LOG_DIR   = Path("/beng-fut/pipeline/logs")

# NEW:
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DIR_09_CSL, DIR_13_SSG_ENGINE, LOG_DIR
CSL_DIR    = DIR_09_CSL
ASSETS_DIR = DIR_13_SSG_ENGINE / "assets" / "audio" / "en-US"
```

**SP07_compile_glossary.py** — replace lines 20-22:
```python
# OLD:
BASE_DIR    = "/beng-fut/pipeline"
INPUT_CSV   = os.path.join(BASE_DIR, "metadata", "Glossario_v5.csv")
OUTPUT_JSON = os.path.join(BASE_DIR, "metadata", "glossary_config.json")

# NEW:
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import METADATA_DIR, GLOSSARY_JSON
INPUT_CSV   = str(METADATA_DIR / "Glossario_v5.csv")
OUTPUT_JSON = str(GLOSSARY_JSON)
```

**SP08_glossary_gate.py** — replace lines 29-31:
```python
# OLD:
BASE_DIR      = Path("/beng-fut/pipeline")
GLOSSARY_CSV  = BASE_DIR / "metadata" / "Glossario_v5.csv"
GLOSSARY_JSON = BASE_DIR / "metadata" / "glossary_config.json"

# NEW:
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import METADATA_DIR, GLOSSARY_JSON as GLOSSARY_JSON_PATH
GLOSSARY_CSV  = METADATA_DIR / "Glossario_v5.csv"
GLOSSARY_JSON = GLOSSARY_JSON_PATH
```

**SG04_harvest_assets.py** — replace lines 28-32:
```python
# OLD:
BENG_ROOT      = Path("/beng-fut")
WP_UPLOADS_DIR = BENG_ROOT / "wordpress" / "runtime_wp" / "wp-content" / "uploads"
AUDIO_DEST     = BENG_ROOT / "pipeline" / "09-csl" / ...
IMAGE_DEST     = BENG_ROOT / "pipeline" / "13-static-site" / ...
LOG_DIR        = BENG_ROOT / "pipeline" / "logs"

# NEW:
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import BASE_DIR, DIR_09_CSL, DIR_STATIC_SITE, LOG_DIR
BENG_ROOT      = BASE_DIR.parent
WP_UPLOADS_DIR = BENG_ROOT / "wordpress" / "runtime_wp" / "wp-content" / "uploads"
AUDIO_DEST     = DIR_09_CSL / "meta" / "pronunciation"
IMAGE_DEST     = DIR_STATIC_SITE / "assets" / "images"
```

**Eliminates F3.** All 4 scripts become relocatable.

---

### FIX 4 — Add setup_v54 guard in run_full_pipeline.sh
```bash
# In run_sd() function, before SD03 block:
if [ ! -d "$ssg_dir/src" ]; then
    log_warn "[SD] 13-ssg/src/ not found. Running setup_v54_static_site.sh..."
    bash "$SCRIPTS_DIR/setup_v54_static_site.sh" || abort "SSG setup failed."
fi
```
**Eliminates F4.** Auto-deploys SSG package structure on first run.

---

### FIX 5 — Delete or archive Cópia files and legacy numbered scripts
```bash
# Archive, do not delete permanently:
mkdir -p $BENG_BASE/scripts/archive/legacy
mv $BENG_BASE/scripts/*Cópia*.py   $BENG_BASE/scripts/archive/legacy/
mv $BENG_BASE/scripts/[0-9]*.py    $BENG_BASE/scripts/archive/legacy/
mv $BENG_BASE/scripts/S04_*.py     $BENG_BASE/scripts/archive/legacy/
mv $BENG_BASE/scripts/S07_*.py     $BENG_BASE/scripts/archive/legacy/
mv $BENG_BASE/scripts/S10_*.py     $BENG_BASE/scripts/archive/legacy/
mv $BENG_BASE/scripts/S14_*.py     $BENG_BASE/scripts/archive/legacy/
```
**Reduces cognitive load.** No runtime impact. Prevents accidental execution.

---

## SUMMARY TABLE

| ID | Severity | Script(s) | Issue | Fix |
|---|---|---|---|---|
| F1 | ★ CRITICAL | `run_full_pipeline.sh`, `build.py` | SD03 name mismatch → hard abort | Rename or alias |
| F2 | ★ HIGH | `DI00_sql_vs_csl_audit.py` | Hardcoded `/media/sanghop` dead path | Patch to config.py |
| F3 | ★ HIGH | `SP06`, `SP07`, `SP08`, `SG04` | 4 scripts bypass config.py with hardcoded paths | Patch to config.py |
| F4 | ★ MEDIUM | `build.py` + SSG modules | Relative imports fail without deploy step | Auto-trigger setup_v54 |
| F5 | ★ MEDIUM | `SP03`, `SP04` | Overlapping schema v3.1 writes, fragile ordering | Document + guard |
| F6 | LOW | `axis_runner.sh` | `sp12_guardian/` non-existent | Stub or remove |
| F7 | LOW | `SN01_snapshot_csl.sh` | Snapshot dir hardcoded outside BENG_BASE | Derive from BENG_BASE |

**Total scripts in pipeline:** 27 active CORE + 10 SUPPORT  
**Total deprecated/orphan:** ~35 (should be archived)  
**Blocking issues before full pipeline run:** F1 + F3 (SP06/SP07/SP08 in SP phase, hard failure if BENG_BASE ≠ /beng-fut/pipeline)

---

*Report generated by code-level analysis. No documentation assumed correct.*
