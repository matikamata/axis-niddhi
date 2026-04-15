# AXIS-NIDDHI — PIPELINE CANONICALIZATION PASS
**Version:** V5.4 Canonicalization  
**Date:** 2026-03-11  
**Analyst:** Vayo (Technical Architect)  
**Source:** Code-level analysis + real-world file tree (CONTEXTO_VAYO_20260309)  
**Constraint:** No deletions. No rewrites. Mapping only.

---

## SECTION 1 — CANONICAL FOLDER MAPPING

```
/beng-fut/pipeline/
│
├── scripts/                          ← current monorepo (untouched)
│
├── scripts_core/                     ← CANONICAL SPINE (30 scripts + SSG modules)
│   │
│   ├── ── INFRASTRUCTURE ──
│   ├── config.py                     [INFRA]  Canonical path/credential resolver
│   ├── pipeline_utils.py             [INFRA]  Atomic writes, SHA-256, FailureCounter
│   ├── cls_tools.py                  [INFRA]  Content Lineage System toolkit
│   ├── models.py                     [INFRA]  Post/Section dataclasses (SSG)
│   │
│   ├── ── ORCHESTRATION ──
│   ├── run_full_pipeline.sh          [ORCH]   Master orchestrator V5.2
│   ├── SN01_snapshot_csl.sh          [PRE]    CSL snapshot before destructive ops
│   │
│   ├── ── [SG] GENESIS ──
│   ├── SG00_reset_workspace.sh       [SG-0]   WP reset + dir cleanup
│   ├── SG01_extract_html.py          [SG-1]   MySQL → 01-extracted (SRO)
│   ├── SG02_preprocess_html.py       [SG-2]   01-extracted → 02-preprocessed
│   ├── SG03_build_csl.py             [SG-3]   02-preprocessed → 09-csl
│   ├── SG04_harvest_assets.py        [SG-4]   WP uploads → audio/images
│   │
│   ├── ── [SP] PRESERVATION ──
│   ├── SP01_migrate_ptbr.py          [SP-1]   Import legacy PT-BR translations
│   ├── SP02_upgrade_identity.py      [SP-2]   Schema v3.1 upgrade + SEAL
│   ├── SP03_mass_migration.py        [SP-3]   Apply Golden Sample to all posts
│   ├── SP04_phase5_migration.py      [SP-4]   schema_version v3.1 stamp pass
│   ├── SP05_fix_headers.py           [SP-5]   Fix HTML headers in content files
│   ├── SP06_audio_converter.py       [SP-6]   Audio shortcodes → native HTML
│   ├── SP07_compile_glossary.py      [SP-7]   CSV → glossary_config.json
│   ├── SP08_glossary_gate.py         [SP-8]   Human review gate
│   ├── SP09_translation_menu.py      [SP-9]   Generate Translation_Control_Center.csv
│   ├── SP10_translate_deepl.py       [SP-10]  DeepL batch translation (manual gate)
│   ├── SP11_translate_titles.py      [SP-11]  EN→PT title translation
│   │
│   ├── ── [SA] AUDIT ──
│   ├── SA01_final_audit.py           [SA-1]   SHA-256 structural audit
│   ├── SA02_freeze_manifest.py       [SA-2]   Global immutability manifest
│   ├── SA03_translation_progress.py  [SA-3]   PT-BR progress report
│   │
│   ├── ── [SD] DISTRIBUTION ──
│   ├── SD01_generate_asset_map.py    [SD-1]   Generate asset_map.json
│   ├── SD03_static_site_build.py     [SD-3]   Compatibility shim → build.py ★new
│   ├── build.py                      [SD-3b]  SSG engine (generates static site)
│   ├── SD04_wordpress_inject.py      [SD-4]   Inject posts into WordPress local
│   │
│   ├── ── [MI] REPORTING ──
│   ├── MI99_mission_report.py        [MI]     Pipeline status (called 3× in full)
│   │
│   └── ── SSG MODULES (deployed to 13-ssg/src/ by setup_v54) ──
│       ├── csl_loader.py             → 13-ssg/src/loaders/
│       ├── identity_loader.py        → 13-ssg/src/loaders/
│       ├── post_renderer.py          → 13-ssg/src/renderers/
│       ├── index_renderer.py         → 13-ssg/src/renderers/
│       ├── nav_builder.py            → 13-ssg/src/transformers/
│       ├── link_resolver.py          → 13-ssg/src/transformers/
│       ├── asset_mapper.py           → 13-ssg/src/transformers/
│       ├── language_router.py        → 13-ssg/src/transformers/
│       └── templates/
│           ├── base.html
│           ├── post.html
│           └── index.html
│
├── scripts_support/                  ← SUPPORT & UTILITY (operator tools)
│   │
│   ├── ── VALIDATION & HEALTH ──
│   ├── DI00_sql_vs_csl_audit.py      SQL vs CSL pre-flight audit (needs F2 fix)
│   ├── validate_cls_pipeline.sh      CLS validation + pipeline pre-check
│   ├── test_cls_integration_dryrun.sh CLS integration dry-run (5 posts)
│   │
│   ├── ── ENVIRONMENT SETUP ──
│   ├── setup_v54_static_site.sh      SSG environment bootstrap
│   ├── activate_cls_v11.sh           CLS V1.1 one-time activation
│   ├── redeploy_cls_and_backfill.sh  CLS redeploy after workspace reset
│   │
│   ├── ── CLI & RUNNERS ──
│   ├── axis_cli.sh                   CLI dispatcher (build-site, preview, status)
│   ├── axis_runner.sh                Alternate runner (sp12, audit, status)
│   ├── run_sp11_and_report.sh        Standalone SP11 + post-execution report
│   │
│   ├── ── SP12 GUARDIAN (human review tool) ──
│   └── sp12_guardian/
│       ├── sp12_app.py               Streamlit review UI
│       ├── sp12_logic.py             Business logic for review
│       └── install_sp12.sh           sp12 dependency installer
│
├── scripts_legacy/                   ← DEPRECATED — archive, never delete
│   │
│   ├── ── NUMBERED SERIES (pre-SP era) ──
│   ├── 00b_genesis_twins_v4_smart.py
│   ├── 01_extract_v3_global.py        → superseded by SG01
│   ├── 02_preprocess_v4_1_iframes.py  → superseded by SG02
│   ├── 03_build_csl_v1.py             → superseded by SG03
│   ├── 04_compile_glossary.py         → superseded by SP07
│   ├── 05_translate_pilot_v5_surgeon.py → superseded by SP10
│   ├── 05a_upload_glossary_deepl.py   → superseded by SP07/SP08
│   ├── 06_inject_pilot_v3_pages.py    → superseded by SD04
│   ├── 07a_generate_menu_v6_schema_aware.py → superseded by SP09
│   ├── 07b_execute_menu_v3_guardian.py → superseded by SP09
│   ├── 08_mass_inject_v5_resilient.py → superseded by SD04
│   ├── 09_upgrade_identity_v3_audited.py → superseded by SP02
│   ├── 10_mass_migration_phase5.py    → superseded by SP04
│   ├── 11_final_audit_and_cleanup.py  → superseded by SA01
│   ├── 12_fix_headers_and_identity.py → superseded by SP05
│   ├── 14_sync_titles_from_ledger.py  → superseded by SP11
│   ├── 15_Relatório_de_Estrutura_de_Subpastas.py
│   │
│   ├── ── S-SERIES (pre-SP canonicalization) ──
│   ├── S04_upgrade_identity_v3.py     → superseded by SP02
│   ├── S07_fix_headers_identity.py    → superseded by SP05
│   ├── S10_execute_translation_deepl.py → superseded by SP10
│   │
│   ├── ── VERSIONED VARIANTS (superseded by canonical) ──
│   ├── SP05_fix_headers_v51.py        → superseded by SP05_fix_headers.py
│   ├── deploy_v51.sh                  → superseded by setup_v54_static_site.sh
│   │
│   ├── ── STANDALONE UTILITIES (dead path or single-use) ──
│   ├── SD02_generate_slug_map.py      → absorbed into build.py internally
│   ├── S14_generate_asset_map.py      → superseded by SD01
│   ├── audit_ssg_zip.py               → hardcoded /beng path, one-time use
│   ├── auditoria_forense_youtube_csl.py → forensic tool, single-use
│   ├── ingest.py                      → S12b, superseded by SG04
│   ├── discovery.py                   → S12, superseded by SG04
│   ├── resultado_passo10.txt          → log artifact, not a script
│   ├── reset_brasileirinho_v12.2.sh   → superseded by SG00_reset_workspace.sh
│   │
│   └── ── CÓPIA DUPLICATES (filesystem duplicates) ──
│       ├── SG01_extract_html__Cópia_.py
│       ├── SP02_upgrade_identity__Cópia_.py
│       ├── SP10_translate_deepl__Cópia_.py
│       ├── SP11_translate_titles__Cópia_.py
│       ├── cls_tools__Cópia_.py
│       ├── cls_tools__Cópia_2_.py
│       └── generate_asset_map__Cópia_.py
│
└── [data directories — unchanged]
    ├── 01-extracted-htmls/   [SRO — Read-Only after SG01]
    ├── 02-preprocessed/
    ├── 09-csl/               [Canonical Source Library]
    ├── 13-ssg/               [SSG engine — deployed by setup_v54]
    ├── 13-static-site/       [SSG output]
    ├── metadata/
    ├── logs/
    └── snapshots/
```

---

### Count Summary

| Folder | Scripts | Purpose |
|---|---|---|
| `scripts_core/` | 30 Python/shell + 8 SSG modules + 3 templates | Full rebuild capability |
| `scripts_support/` | 11 scripts + sp12_guardian (3 files) | Operator tools, CI, review |
| `scripts_legacy/` | ~35 files | Archive — historical record |
| **Total** | **~82** | **No files deleted** |

---

## SECTION 2 — CANONICAL SPINE EXECUTION ORDER

```
╔══════════════════════════════════════════════════════════════════════╗
║   AXIS-NIDDHI — FULL REBUILD SPINE                                   ║
║   Trigger: ./run_full_pipeline.sh --full                             ║
║   Source of truth: run_full_pipeline.sh V5.2 (code-verified)        ║
╚══════════════════════════════════════════════════════════════════════╝

 ┌─ PRE-FLIGHT (optional, operator-prompted) ───────────────────────┐
 │  PRE-1   SN01_snapshot_csl.sh                                    │
 │          Purpose: compressed backup of 09-csl/ before any reset  │
 │          Gate: operator confirms Y/n                             │
 └──────────────────────────────────────────────────────────────────┘

 ┌─ [SG] GENESIS — Full rebuild from WP backup ─────────────────────┐
 │                                                                   │
 │  SG-0    SG00_reset_workspace.sh                                 │
 │          MySQL reset (beng_wp_21) + WP extract from .zip         │
 │          Cleans 01-extracted/ and 02-preprocessed/               │
 │          Does NOT touch 09-csl/, metadata/, logs/                │
 │          Gate: operator confirms reset (or BENG_AUTO_RESET=true) │
 │                                                                   │
 │  SG-1    SG01_extract_html.py                                    │
 │          MySQL beng_wp_21 + PDPN_01_Operational.csv              │
 │          → 01-extracted-htmls/en-US/[PDPN].html                  │
 │          → identity.json updated: origin.source_html_sha256      │
 │          SRO: chmod a-w applied after extraction                  │
 │                                                                   │
 │  SG-2    SG02_preprocess_html.py                                 │
 │          → 02-preprocessed/en-US/[PDPN].html                     │
 │          Strips WP artefacts, preserves iframes, normalizes links │
 │                                                                   │
 │  SG-3    SG03_build_csl.py --apply                               │
 │          → 09-csl/[PDPN]/source/en-US/content.html               │
 │          → 09-csl/[PDPN]/meta/identity.json  (schema v1.0 seed)  │
 │          Idempotent: skips existing posts without --force         │
 │                                                                   │
 │  SG-4    SG04_harvest_assets.py                                  │
 │          runtime_wp/wp-content/uploads/ →                        │
 │          → 09-csl/meta/pronunciation/ (audio)                    │
 │          → 13-static-site/assets/images/ (images)                │
 │                                                                   │
 │  [MI]    MI99_mission_report.py    (post-SG status report)       │
 └──────────────────────────────────────────────────────────────────┘

 ┌─ [SP] PRESERVATION — Identity + Translation ─────────────────────┐
 │                                                                   │
 │  SP-1    SP01_migrate_ptbr.py --apply                            │
 │          Import legacy PT-BR translations from external HD        │
 │          Skips: posts where pt-BR already exists (no overwrite)   │
 │                                                                   │
 │  SP-2    SP02_upgrade_identity.py --apply                        │
 │          Upgrade identity.json → schema v3.1                     │
 │          Populates: sro, titles.en, artifacts.en-US              │
 │          Skips: posts already at v3.1 (unless --force)           │
 │                                                                   │
 │  SP-3    SP03_mass_migration.py --apply                          │
 │          Apply Golden Sample (SI.AA.005) structure to all posts   │
 │          Recalculates SHA-256 after write (file-level, rb)       │
 │                                                                   │
 │  SP-4    SP04_phase5_migration.py --apply                        │
 │          schema_version stamp pass — ensures v3.1 on all entries  │
 │                                                                   │
 │  SP-5    SP05_fix_headers.py --apply                             │
 │          Normalize HTML headers in content.html (h1→h2, etc.)    │
 │          Uses atomic_write_bytes + backup_file                   │
 │                                                                   │
 │  SP-6    SP06_audio_converter.py --apply                         │
 │          [audio mp3=...] shortcodes → <audio> native HTML        │
 │          Idempotent: skips files with no shortcodes              │
 │                                                                   │
 │  ── [SEAL 1] ─────────────────────────────────────────────────── │
 │                                                                   │
 │  SP-2b   SP02_upgrade_identity.py --apply --force                │
 │          Re-runs with --force to lock EN hashes post-mutation    │
 │          Guard: preserves titles.pt if already populated (E1 fix) │
 │                                                                   │
 │  SP-11   SP11_translate_titles.py --apply                        │
 │          DeepL EN→PT title translation                           │
 │          Writes: identity.json → titles.pt + titles.pt_source    │
 │          Writes: lineage.translations[title_translated event]    │
 │          NOTE: runs after SEAL 1 so EN hashes are locked first   │
 │                                                                   │
 │  ── Glossary pipeline ──────────────────────────────────────────  │
 │                                                                   │
 │  SP-7    SP07_compile_glossary.py                                │
 │          Glossario_v5.csv → metadata/glossary_config.json        │
 │          Sorts by term length (longest first) — prevents partials │
 │                                                                   │
 │  SP-8    SP08_glossary_gate.py                                   │
 │          Displays glossary stats — human review checkpoint        │
 │          Requires: operator types GLOSSARY_OK                    │
 │          Bypass: BENG_AUTO_GLOSSARY_OK=true (CI)                 │
 │                                                                   │
 │  SP-9    SP09_translation_menu.py                                │
 │          Scans CSL → generates Translation_Control_Center.csv    │
 │          Columns: PDPN, Section, Slug, Status, Chars, Est_Cost   │
 │                                                                   │
 │  ═══════════════════════════════════════════════════════════════  │
 │  ║  MANUAL OPERATOR GATE                                        ║  │
 │  ║  1. Open Translation_Control_Center.csv                      ║  │
 │  ║  2. Mark COMMAND=YES for batch (≤ 450k chars / month)        ║  │
 │  ║  3. Execute SP10 manually (real DeepL cost)                  ║  │
 │  ═══════════════════════════════════════════════════════════════  │
 │                                                                   │
 │  SP-10   SP10_translate_deepl.py              [MANUAL EXECUTION] │
 │          Reads COMMAND=YES rows from Translation_Control_Center   │
 │          DeepL API → 09-csl/[PDPN]/source/pt-BR/content.html    │
 │          Uses: mark_in_progress / clear_in_progress (crash-safe) │
 │          Uses: FailureCounter (aborts after N consecutive errors) │
 │                                                                   │
 │  SP-2c   SP02_upgrade_identity.py --apply --force  [POST SP-10] │
 │          Updates artifacts.pt-BR hashes after translation        │
 │          Guard: preserves titles.pt (E1 fix — do not overwrite)  │
 │                                                                   │
 │  [MI]    MI99_mission_report.py    (post-SP status report)       │
 └──────────────────────────────────────────────────────────────────┘

 ┌─ [SA] AUDIT — Integrity Verification ────────────────────────────┐
 │                                                                   │
 │  SA-0    SP02_upgrade_identity.py           (dry-run only)       │
 │          No --apply flag — consistency check without mutation     │
 │                                                                   │
 │  SA-1    SA01_final_audit.py --apply                             │
 │          SHA-256 structural audit of all CSL entries             │
 │          Removes forbidden artefacts (content.json residuals)    │
 │          Reports: schema violations, missing files               │
 │                                                                   │
 │  SA-2    SA02_freeze_manifest.py                                 │
 │          Global SHA-256 manifest of entire CSL                   │
 │          Immutability baseline for archival                      │
 │                                                                   │
 │  SA-3    SA03_translation_progress.py                            │
 │          PT-BR translation coverage report                       │
 │          Output: translated / total / percentage per section     │
 └──────────────────────────────────────────────────────────────────┘

 ┌─ [SD] DISTRIBUTION — Static Site + WordPress ────────────────────┐
 │                                                                   │
 │  SD-1    SD01_generate_asset_map.py                              │
 │          Scans CSL for WP asset URLs                             │
 │          → S14_asset_resolver/asset_map.json                     │
 │                                                                   │
 │  [F4]    AUTO-BOOTSTRAP if 13-ssg/ not initialized:             │
 │          setup_v54_static_site.sh runs automatically             │
 │          Deploys: build.py + SD03_static_site_build.py shim      │
 │          Deploys: SSG modules to 13-ssg/src/{loaders,...}        │
 │          Deploys: templates/, static/css/, static/js/            │
 │                                                                   │
 │  SD-3    13-ssg/SD03_static_site_build.py  (= build.py via shim)│
 │          Loads CSL → renders 748 HTML pages                      │
 │          Generates: pages/, index.html, search_index.json        │
 │          Generates: slug_map.json (internal), build_meta.json    │
 │          Copies: audio files, static assets                      │
 │          Output: 13-static-site/ (or /beng-runtime/static-site/) │
 │                                                                   │
 │  SD-4    SD04_wordpress_inject.py                                │
 │          WordPress REST API → inject PT+EN posts                 │
 │          Gate: operator confirms (or BENG_AUTO_INJECT=true)      │
 │                                                                   │
 │  [MI]    MI99_mission_report.py    (post-SD final report)        │
 └──────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════╗
║   TOTAL AUTOMATED STEPS:  21                                         ║
║   MANUAL GATES:           3  (reset confirm, glossary OK, SP10)      ║
║   SEAL PASSES (SP02):     3  (SP-2, SP-2b, SP-2c)                   ║
║   MI REPORTS:             3  (post-SG, post-SP, post-SD)            ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## SECTION 3 — RESIDUAL FRAGILITY (non-blocking)

### A — DI00: Dead path to original machine (F2, unresolved)

```
DI00_sql_vs_csl_audit.py
  BASE_DIR = Path("/media/sanghop/BrasileirinhoHD/...")  ← old machine
  SQL_PATH = Path("/media/sanghop/...")
```

**Status:** DI phase is pre-flight only, not in `--full` spine. Does not block rebuild.  
**Resolution when needed:** patch to `from config import BASE_DIR, DIR_09_CSL`. SQL_PATH must be set by operator via env var or config.

---

### B — setup_v54_static_site.sh: PASSO 3 still needs manual update

```bash
# Current (copies build.py only):
cp "$SCRIPTS/SD03_static_site_build.py" "$SSG/build.py"

# Must become (copies both):
cp "$SCRIPTS/SD03_static_site_build.py" "$SSG/build.py"
cp "$SCRIPTS/SD03_static_site_build.py" "$SSG/SD03_static_site_build.py"
```

**Status:** The F4 bootstrap guard in `run_full_pipeline.sh` calls `setup_v54_static_site.sh` automatically, but after bootstrap the re-verification check for `SD03_static_site_build.py` in `13-ssg/` still fails because `setup_v54` only deploys `build.py`. This needs the one-line addition above before the bootstrap guard is fully effective.

---

### C — SP03 and SP04: thin functional boundary

Both apply `schema_version: "3.1"` to `identity.json`. SP03 does a full Golden Sample rewrite; SP04 is a stamp-only pass. In the orchestrator they run sequentially (SP03 → SP04), which is correct. If ever run in isolation or reversed, SP04 can overwrite SP03 fields.

**Operator rule:** never run SP04 without SP03 having run first in the same session.

---

### D — SP08: input delimiter hardcoded

```python
rows = list(csv.reader(f, delimiter=';'))
```

`SP08_glossary_gate.py` reads `Glossario_v5.csv` with a semicolon delimiter hardcoded. `SP07_compile_glossary.py` auto-detects the delimiter via `csv.Sniffer`. If the CSV changes to comma-separated, SP08 silently reads malformed rows. Not introduced by V5.4 hardening — pre-existing.

---

### E — SG04: BENG_ROOT derivation

After V5.4 patch, `BENG_ROOT = BASE_DIR.parent`. This assumes the pipeline directory is always one level under the server root (e.g., `/beng-fut/pipeline` → `BENG_ROOT = /beng-fut`). If `BENG_BASE` points to a non-standard location (e.g., `/home/operator/axis/pipeline`), `WP_UPLOADS_DIR` will be wrong.

**Operator rule:** `WP_UPLOADS_DIR` must always be verified in SG04 output before proceeding with SG-5 onwards.

---

### F — sp12_guardian: Streamlit dependency not in main requirements

`sp12_guardian/sp12_app.py` requires `streamlit`. This is not installed by the `activate_venv()` function in `run_full_pipeline.sh`. SP12 is a review tool, not in the pipeline spine — but `axis sp12` will fail on a fresh environment without `pip install streamlit`.

**Resolution:** `sp12_guardian/install_sp12.sh` exists for this. Operator must run it before using `axis sp12`.

---

## SECTION 4 — RECOMMENDATIONS FOR SAFE ARCHIVING OF LEGACY SCRIPTS

### Archive procedure

Do not delete. Use `git mv` (if repo is under version control) or a simple shell move:

```bash
#!/usr/bin/env bash
# archive_legacy.sh — run once from scripts/
# Creates scripts_legacy/ and moves deprecated scripts into it.
# REVERSIBLE: git mv can be undone; or simply mv back.

set -euo pipefail
SCRIPTS="/beng-fut/pipeline/scripts"
LEGACY="$SCRIPTS/../scripts_legacy"
mkdir -p "$LEGACY"

# ── Numbered series ──────────────────────────────────────────────────────────
for f in \
    00b_genesis_twins_v4_smart.py \
    01_extract_v3_global.py \
    02_preprocess_v4_1_iframes.py \
    03_build_csl_v1.py \
    04_compile_glossary.py \
    05_translate_pilot_v5_surgeon.py \
    05a_upload_glossary_deepl.py \
    06_inject_pilot_v3_pages.py \
    07a_generate_menu_v6_schema_aware.py \
    07b_execute_menu_v3_guardian.py \
    08_mass_inject_v5_resilient.py \
    09_upgrade_identity_v3_audited.py \
    10_mass_migration_phase5.py \
    11_final_audit_and_cleanup.py \
    12_fix_headers_and_identity.py \
    14_sync_titles_from_ledger.py \
    "15_Relatório_de_Estrutura_de_Subpastas.py"; do
    [ -f "$SCRIPTS/$f" ] && mv "$SCRIPTS/$f" "$LEGACY/$f" && echo "archived: $f"
done

# ── S-series ─────────────────────────────────────────────────────────────────
for f in S04_upgrade_identity_v3.py S07_fix_headers_identity.py S10_execute_translation_deepl.py; do
    [ -f "$SCRIPTS/$f" ] && mv "$SCRIPTS/$f" "$LEGACY/$f" && echo "archived: $f"
done

# ── Versioned variants ───────────────────────────────────────────────────────
for f in SP05_fix_headers_v51.py deploy_v51.sh reset_brasileirinho_v12.2.sh; do
    [ -f "$SCRIPTS/$f" ] && mv "$SCRIPTS/$f" "$LEGACY/$f" && echo "archived: $f"
done

# ── Cópia duplicates ─────────────────────────────────────────────────────────
for f in \
    "SG01_extract_html__Cópia_.py" \
    "SP02_upgrade_identity__Cópia_.py" \
    "SP10_translate_deepl__Cópia_.py" \
    "SP11_translate_titles__Cópia_.py" \
    "cls_tools__Cópia_.py" \
    "cls_tools__Cópia_2_.py" \
    "generate_asset_map__Cópia_.py"; do
    [ -f "$SCRIPTS/$f" ] && mv "$SCRIPTS/$f" "$LEGACY/$f" && echo "archived: $f"
done

# ── Standalone utilities (absorbed/dead path) ────────────────────────────────
for f in SD02_generate_slug_map.py S14_generate_asset_map.py audit_ssg_zip.py \
          auditoria_forense_youtube_csl.py resultado_passo10.txt; do
    [ -f "$SCRIPTS/$f" ] && mv "$SCRIPTS/$f" "$LEGACY/$f" && echo "archived: $f"
done

# ── S14_asset_resolver/ — move whole dir ────────────────────────────────────
[ -d "/beng-fut/pipeline/S14_asset_resolver" ] && \
    mv "/beng-fut/pipeline/S14_asset_resolver" "$LEGACY/S14_asset_resolver" && \
    echo "archived: S14_asset_resolver/"

echo ""
echo "✅ Archive complete. Verify scripts_core/ still has all 30 CORE scripts."
echo "   To restore any file: mv $LEGACY/<file> $SCRIPTS/<file>"
```

---

### Archiving Rules

| Rule | Rationale |
|---|---|
| **Never delete** | Historical record of pipeline evolution. Legal/audit value for archival distribution. |
| **Keep in scripts_legacy/** | Readable by operators who need to understand design decisions. |
| **Add README.md to scripts_legacy/** | One-line summary per file: `superseded by X in version Y`. |
| **Do not patch** | Legacy scripts may have hardcoded paths. Do not attempt to fix — they are historical artefacts. |
| **Run deploy_v51.sh check first** | `deploy_v51.sh` references legacy files by name. Archive it only after confirming `setup_v54_static_site.sh` has replaced its function entirely. |

---

### Suggested scripts_legacy/README.md content

```markdown
# scripts_legacy/ — AXIS-NIDDHI Archive

This directory contains scripts that have been superseded by the canonical SP/SG/SA/SD series.
These files are preserved for historical reference and audit purposes.
**Do not execute these scripts.** Use the canonical spine in scripts_core/ instead.

## Supersession Map

| Legacy script | Superseded by | Version |
|---|---|---|
| 01_extract_v3_global.py | SG01_extract_html.py | V5.0 |
| 02_preprocess_v4_1_iframes.py | SG02_preprocess_html.py | V5.0 |
| 03_build_csl_v1.py | SG03_build_csl.py | V5.0 |
| 04_compile_glossary.py | SP07_compile_glossary.py | V5.0 |
| 05_translate_pilot_v5_surgeon.py | SP10_translate_deepl.py | V5.0 |
| 09_upgrade_identity_v3_audited.py | SP02_upgrade_identity.py | V5.0 |
| 10_mass_migration_phase5.py | SP04_phase5_migration.py | V5.0 |
| 11_final_audit_and_cleanup.py | SA01_final_audit.py | V5.0 |
| deploy_v51.sh | setup_v54_static_site.sh | V5.4 |
| S04_upgrade_identity_v3.py | SP02_upgrade_identity.py | V5.1 |
| S10_execute_translation_deepl.py | SP10_translate_deepl.py | V5.1 |
| SP05_fix_headers_v51.py | SP05_fix_headers.py | V5.1 |
| *__Cópia_.py | (filesystem duplicates) | — |
```

---

*Canonicalization pass complete. Pipeline rebuild capability: 100% preserved. Cognitive load: reduced from 82 to 30 active scripts.*
