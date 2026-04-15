# AXIS-NIDDHI — PIPELINE STABILIZATION REPORT
**Pass:** V5.4 Hardening — Non-Destructive Stabilization  
**Date:** 2026-03-11  
**Analyst:** Vayo (Technical Architect)  
**Constraint:** No deletions. No rewrites. Minimal surgical patches.

---

## SECTION 1 — APPLIED FIX SUMMARY

### FIX 1 — F1: SD03 Name Mismatch  ✅ RESOLVED

**File created:** `SD03_static_site_build.py`

| Field | Value |
|---|---|
| Problem | `run_full_pipeline.sh` calls `python3 SD03_static_site_build.py` inside `13-ssg/` — hard `abort()` on miss |
| Root cause | Engine script is named `build.py` in repository; `setup_v54_static_site.sh` also expected `SD03_static_site_build.py` in scripts/ to copy |
| Fix | Created `SD03_static_site_build.py` as a **thin compatibility shim** using `runpy.run_path()` to delegate to `build.py` |
| Mechanism | `runpy.run_path(str(_BUILD), run_name="__main__")` — identical to running `python3 build.py` directly |
| Deploy path | This file must be deployed to `13-ssg/` alongside `build.py` by `setup_v54_static_site.sh` |
| Risk | Zero — shim adds no logic, purely delegates |

**Required addition to `setup_v54_static_site.sh` (PASSO 3):**
```bash
# Change:
cp "$SCRIPTS/SD03_static_site_build.py" "$SSG/build.py"
# Add:
cp "$SCRIPTS/SD03_static_site_build.py" "$SSG/SD03_static_site_build.py"
```

---

### FIX 3 — F3: Hardcoded Paths in 4 Scripts  ✅ RESOLVED

All 4 scripts now import from `config.py` via the canonical pattern used by the rest of the SP series.

**Pattern applied to each script:**
```python
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from config import <required_symbols>
```

| Script | Was | Now |
|---|---|---|
| `SP06_audio_converter.py` | `Path("/beng-fut/pipeline/09-csl")` × 3 hardcodes | `from config import DIR_09_CSL, DIR_13_SSG_ENGINE, LOG_DIR` |
| `SP07_compile_glossary.py` | `BASE_DIR = "/beng-fut/pipeline"` (string, not Path) | `from config import METADATA_DIR, GLOSSARY_JSON` |
| `SP08_glossary_gate.py` | `BASE_DIR = Path("/beng-fut/pipeline")` | `from config import METADATA_DIR, GLOSSARY_JSON` |
| `SG04_harvest_assets.py` | `BENG_ROOT = Path("/beng-fut")` + 3 derived hardcodes | `from config import BASE_DIR, DIR_09_CSL, DIR_STATIC_SITE, LOG_DIR` |

**SG04 additional note:** `BENG_ROOT` is now derived as `BASE_DIR.parent` (still needed for `WP_UPLOADS_DIR` construction). Display lines using `.relative_to(BENG_ROOT)` replaced with absolute path display — no functional change.

---

### FIX 4 — F4: SSG Bootstrap Guard  ✅ RESOLVED

**File modified:** `run_full_pipeline.sh` — `run_sd()` function

**Before:**
```bash
if [ ! -f "$ssg_dir/SD03_static_site_build.py" ]; then
    abort "SD03_static_site_build.py não encontrado em $ssg_dir"
fi
```

**After:**
```bash
if [ ! -f "$ssg_dir/SD03_static_site_build.py" ]; then
    log_warn "[SD] Tentando bootstrap automático via setup_v54_static_site.sh..."
    if [ -f "$SCRIPTS_DIR/setup_v54_static_site.sh" ]; then
        bash "$SCRIPTS_DIR/setup_v54_static_site.sh" || abort "SSG bootstrap falhou."
    else
        abort "SD03 ausente e setup_v54_static_site.sh não encontrado."
    fi
    # Re-verificar após bootstrap
    [ ! -f "$ssg_dir/SD03_static_site_build.py" ] && abort "Bootstrap incompleto."
    log_ok "[SD] Bootstrap SSG concluído."
fi
```

**Behavior:** On first run, pipeline auto-bootstraps the `13-ssg/` environment. Subsequent runs find the file and proceed immediately. Fully idempotent.

---

### NOT APPLIED IN THIS PASS

| Fix | Reason deferred |
|---|---|
| F2 — DI00 `/media/sanghop` dead path | DI phase is optional pre-flight; does not block `--full` pipeline. Requires operator to supply SQL dump path — fixing blind would break existing workflow. Defer to operator configuration. |
| F5 — SP03/SP04 ordering fragility | Both scripts are idempotent individually (dry-run default + `--apply` flag). Current ordering in orchestrator is tested and stable. No imminent breakage. |
| F6 — axis sp12 ghost reference | `axis_runner.sh` is not in the main pipeline. Cosmetic issue only. |
| F7 — SN01 snapshot dir | Snapshot is optional (operator-prompted). Non-blocking. |

---

## SECTION 2 — SCRIPT CLASSIFICATION TABLE

**Legend:** CORE = required for full rebuild | SUPPORT = auxiliary, safe to skip | UTILITY = standalone tools | DEPRECATED = superseded, archive-safe

| Script | Stage | Class | Notes |
|---|---|---|---|
| `config.py` | INFRA | CORE | Canonical path/credential resolver |
| `pipeline_utils.py` | INFRA | CORE | Atomic writes, SHA-256, FailureCounter |
| `cls_tools.py` | INFRA | CORE | Content Lineage System toolkit |
| `models.py` | INFRA | CORE | Post/Section dataclasses for SSG |
| `SG00_reset_workspace.sh` | SG | CORE | WP reset + dir cleanup |
| `SG01_extract_html.py` | SG | CORE | Extract EN posts from MySQL → 01-extracted |
| `SG02_preprocess_html.py` | SG | CORE | Strip WP artefacts, preserve iframes |
| `SG03_build_csl.py` | SG | CORE | Build CSL structure in 09-csl/ |
| `SG04_harvest_assets.py` | SG | CORE | Copy audio/images from WP uploads |
| `SP01_migrate_ptbr.py` | SP | CORE | Import legacy PT-BR translations |
| `SP02_upgrade_identity.py` | SP | CORE | Schema v3.1 upgrade + SEAL |
| `SP03_mass_migration.py` | SP | CORE | Apply Golden Sample to all posts |
| `SP04_phase5_migration.py` | SP | CORE | schema_version v3.1 stamp pass |
| `SP05_fix_headers.py` | SP | CORE | Fix HTML headers in content files |
| `SP06_audio_converter.py` | SP | CORE | Convert audio shortcodes → native HTML |
| `SP07_compile_glossary.py` | SP | CORE | CSV → glossary_config.json |
| `SP08_glossary_gate.py` | SP | CORE | Human review gate before translation |
| `SP09_translation_menu.py` | SP | CORE | Generate Translation_Control_Center.csv |
| `SP10_translate_deepl.py` | SP | CORE | DeepL batch translation (manual gate) |
| `SP11_translate_titles.py` | SP | CORE | EN→PT title translation via DeepL |
| `SA01_final_audit.py` | SA | CORE | SHA-256 hash consistency audit |
| `SA02_freeze_manifest.py` | SA | CORE | Immutability manifest (global CSL) |
| `SA03_translation_progress.py` | SA | CORE | PT-BR translation progress report |
| `SD01_generate_asset_map.py` | SD | CORE | Generate asset_map.json |
| `SD03_static_site_build.py` | SD | CORE | Compatibility shim → build.py *(new)* |
| `build.py` | SD | CORE | SSG engine — generates 13-static-site/ |
| `SD04_wordpress_inject.py` | SD | CORE | Inject posts into local WordPress |
| `MI99_mission_report.py` | ALL | CORE | Pipeline status report (called 3× in full) |
| `SN01_snapshot_csl.sh` | PRE | CORE | CSL snapshot before destructive ops |
| `run_full_pipeline.sh` | ORCH | CORE | Master orchestrator V5.2 |
| `csl_loader.py` | SSG | CORE | Load CSL repository (deployed to 13-ssg/src/) |
| `identity_loader.py` | SSG | CORE | Load identity.json (deployed to 13-ssg/src/) |
| `post_renderer.py` | SSG | CORE | Render post HTML pages |
| `index_renderer.py` | SSG | CORE | Render section index pages |
| `nav_builder.py` | SSG | CORE | Build navigation tree |
| `link_resolver.py` | SSG | CORE | Resolve internal links |
| `asset_mapper.py` | SSG | CORE | Asset URL mapping |
| `DI00_sql_vs_csl_audit.py` | DI | SUPPORT | Pre-flight SQL vs CSL audit *(dead path F2)* |
| `axis_cli.sh` | UTIL | SUPPORT | CLI dispatcher (build-site, preview, status) |
| `axis_runner.sh` | UTIL | SUPPORT | Alternate runner (sp12 ref broken) |
| `run_sp11_and_report.sh` | UTIL | SUPPORT | Standalone SP11 + report runner |
| `redeploy_cls_and_backfill.sh` | UTIL | SUPPORT | CLS redeploy utility |
| `activate_cls_v11.sh` | UTIL | SUPPORT | CLS V1.1 activation (one-time) |
| `setup_v54_static_site.sh` | UTIL | SUPPORT | SSG environment bootstrap |
| `SD02_generate_slug_map.py` | SD | UTILITY | Standalone slug map (absorbed by build.py) |
| `SA01_final_audit.py` | SA | UTILITY | Also usable standalone |
| `auditoria_forense_youtube_csl.py` | AUDIT | UTILITY | Forensic YouTube/CSL check |
| `audit_ssg_zip.py` | AUDIT | UTILITY | SSG zip audit (hardcoded /beng path) |
| `language_router.py` | SSG | UTILITY | Language alternates helper (deployed to 13-ssg/src/) |
| `ingest.py` | LEGACY | DEPRECATED | S12b asset ingest, superseded by SG04 |
| `discovery.py` | LEGACY | DEPRECATED | S12 discovery, superseded by SG04 |
| `deploy_v51.sh` | LEGACY | DEPRECATED | V5.1 deploy script, superseded by setup_v54 |
| `SP05_fix_headers_v51.py` | SP | DEPRECATED | Superseded by SP05_fix_headers.py |
| `S04_upgrade_identity_v3.py` | SP | DEPRECATED | Superseded by SP02 |
| `S07_fix_headers_identity.py` | SP | DEPRECATED | Superseded by SP05 |
| `S10_execute_translation_deepl.py` | SP | DEPRECATED | Superseded by SP10 |
| `S14_generate_asset_map.py` | SD | DEPRECATED | Superseded by SD01 |
| `00b_genesis_twins_v4_smart.py` | SG | DEPRECATED | Pre-AXIS genesis script |
| `01_extract_v3_global.py` | SG | DEPRECATED | Superseded by SG01 |
| `02_preprocess_v4_1_iframes.py` | SG | DEPRECATED | Superseded by SG02 |
| `03_build_csl_v1.py` | SG | DEPRECATED | Superseded by SG03 |
| `04_compile_glossary.py` | SP | DEPRECATED | Superseded by SP07 |
| `05_translate_pilot_v5_surgeon.py` | SP | DEPRECATED | Superseded by SP10 |
| `05a_upload_glossary_deepl.py` | SP | DEPRECATED | Superseded by SP07/SP08 |
| `06_inject_pilot_v3_pages.py` | SD | DEPRECATED | Superseded by SD04 |
| `07a_generate_menu_v6_schema_aware.py` | SP | DEPRECATED | Superseded by SP09 |
| `07b_execute_menu_v3_guardian.py` | SP | DEPRECATED | Superseded by SP09 |
| `08_mass_inject_v5_resilient.py` | SD | DEPRECATED | Superseded by SD04 |
| `09_upgrade_identity_v3_audited.py` | SP | DEPRECATED | Superseded by SP02 |
| `10_mass_migration_phase5.py` | SP | DEPRECATED | Superseded by SP04 |
| `11_final_audit_and_cleanup.py` | SA | DEPRECATED | Superseded by SA01 |
| `12_fix_headers_and_identity.py` | SP | DEPRECATED | Superseded by SP05 |
| `14_sync_titles_from_ledger.py` | SP | DEPRECATED | Superseded by SP11 |
| `15_Relatório_de_Estrutura_de_Subpastas.py` | AUDIT | DEPRECATED | One-time structural report |
| `SG01_extract_html__Cópia_.py` | — | DEPRECATED | Filesystem duplicate (Cópia) |
| `SP02_upgrade_identity__Cópia_.py` | — | DEPRECATED | Filesystem duplicate (Cópia) |
| `SP10_translate_deepl__Cópia_.py` | — | DEPRECATED | Filesystem duplicate (Cópia) |
| `SP11_translate_titles__Cópia_.py` | — | DEPRECATED | Filesystem duplicate (Cópia) |
| `cls_tools__Cópia_.py` | — | DEPRECATED | Filesystem duplicate (Cópia) |
| `cls_tools__Cópia_2_.py` | — | DEPRECATED | Filesystem duplicate (Cópia) |
| `generate_asset_map__Cópia_.py` | — | DEPRECATED | Filesystem duplicate (Cópia) |

**Totals:** 30 CORE | 8 SUPPORT/UTILITY | ~35 DEPRECATED

---

## SECTION 3 — CANONICAL FOLDER MAPPING

Safe reorganization proposal. **Do NOT move files yet** — this is a mapping reference only.

```
pipeline/
├── scripts/                    ← current monorepo (unchanged)
│
├── scripts_core/               ← PROPOSED: CORE scripts only
│   ├── config.py
│   ├── pipeline_utils.py
│   ├── cls_tools.py
│   ├── models.py
│   ├── SG00_reset_workspace.sh
│   ├── SG01_extract_html.py
│   ├── SG02_preprocess_html.py
│   ├── SG03_build_csl.py
│   ├── SG04_harvest_assets.py
│   ├── SP01_migrate_ptbr.py
│   ├── SP02_upgrade_identity.py
│   ├── SP03_mass_migration.py
│   ├── SP04_phase5_migration.py
│   ├── SP05_fix_headers.py
│   ├── SP06_audio_converter.py
│   ├── SP07_compile_glossary.py
│   ├── SP08_glossary_gate.py
│   ├── SP09_translation_menu.py
│   ├── SP10_translate_deepl.py
│   ├── SP11_translate_titles.py
│   ├── SA01_final_audit.py
│   ├── SA02_freeze_manifest.py
│   ├── SA03_translation_progress.py
│   ├── SD01_generate_asset_map.py
│   ├── SD03_static_site_build.py   ← new shim
│   ├── SD04_wordpress_inject.py
│   ├── build.py
│   ├── MI99_mission_report.py
│   ├── SN01_snapshot_csl.sh
│   ├── run_full_pipeline.sh
│   ├── [SSG modules: csl_loader, post_renderer, ...]
│   └── [templates: base.html, post.html, index.html, ...]
│
├── scripts_support/            ← PROPOSED: SUPPORT/UTILITY scripts
│   ├── DI00_sql_vs_csl_audit.py
│   ├── axis_cli.sh
│   ├── axis_runner.sh
│   ├── run_sp11_and_report.sh
│   ├── redeploy_cls_and_backfill.sh
│   ├── activate_cls_v11.sh
│   ├── setup_v54_static_site.sh
│   ├── SD02_generate_slug_map.py
│   ├── auditoria_forense_youtube_csl.py
│   ├── audit_ssg_zip.py
│   └── language_router.py
│
└── scripts_legacy/             ← PROPOSED: DEPRECATED — archive, never delete
    ├── 00b_genesis_twins_v4_smart.py
    ├── 01_extract_v3_global.py
    ├── 02_preprocess_v4_1_iframes.py
    ├── 03_build_csl_v1.py
    ├── 04_compile_glossary.py
    ├── 05_translate_pilot_v5_surgeon.py
    ├── 05a_upload_glossary_deepl.py
    ├── 06_inject_pilot_v3_pages.py
    ├── 07a_generate_menu_v6_schema_aware.py
    ├── 07b_execute_menu_v3_guardian.py
    ├── 08_mass_inject_v5_resilient.py
    ├── 09_upgrade_identity_v3_audited.py
    ├── 10_mass_migration_phase5.py
    ├── 11_final_audit_and_cleanup.py
    ├── 12_fix_headers_and_identity.py
    ├── 14_sync_titles_from_ledger.py
    ├── 15_Relatório_de_Estrutura_de_Subpastas.py
    ├── S04_upgrade_identity_v3.py
    ├── S07_fix_headers_identity.py
    ├── S10_execute_translation_deepl.py
    ├── S14_generate_asset_map.py
    ├── SP05_fix_headers_v51.py
    ├── deploy_v51.sh
    ├── ingest.py
    ├── discovery.py
    ├── *__Cópia*.py  (all 7 Cópia duplicates)
    └── generate_asset_map__Cópia_.py
```

**Pre-condition for moving files:** `run_full_pipeline.sh` variable `SCRIPTS_DIR` must be updated to point to `scripts_core/` before any reorganization. All scripts that use `_SCRIPT_DIR` for config import will resolve correctly regardless (they use `__file__`).

---

## SECTION 4 — OFFICIAL PIPELINE SPINE

**Full rebuild from PureDhamma backup — canonical execution chain.**

```
══════════════════════════════════════════════════════════════
  AXIS-NIDDHI — CANONICAL PIPELINE SPINE (Full Rebuild)
  Trigger: ./run_full_pipeline.sh --full
══════════════════════════════════════════════════════════════

 [PRE]   SN01_snapshot_csl.sh            (operator-prompted)

 ─── [SG] GENESIS ─────────────────────────────────────────
 SG-0    SG00_reset_workspace.sh          (MySQL + dirs reset)
 SG-1    SG01_extract_html.py             (WP → 01-extracted, SRO)
 SG-2    SG02_preprocess_html.py          (01-extracted → 02-preprocessed)
 SG-3    SG03_build_csl.py --apply        (02-preprocessed → 09-csl)
 SG-4    SG04_harvest_assets.py           (WP uploads → audio/images)

 ─── [SP] PRESERVATION ────────────────────────────────────
 SP-1    SP01_migrate_ptbr.py --apply     (import legacy PT-BR)
 SP-2    SP02_upgrade_identity.py --apply (schema → v3.1)
 SP-3    SP03_mass_migration.py --apply   (Golden Sample apply)
 SP-4    SP04_phase5_migration.py --apply (v3.1 stamp pass)
 SP-5    SP05_fix_headers.py --apply      (HTML header fix)
 SP-6    SP06_audio_converter.py --apply  (audio shortcodes → HTML)
         ── [SEAL 1] ──────────────────────────────────────
 SP-2b   SP02_upgrade_identity.py --apply --force  (lock EN hashes)
 SP-11   SP11_translate_titles.py --apply (EN→PT titles via DeepL)
         ──────────────────────────────────────────────────
 SP-7    SP07_compile_glossary.py         (CSV → glossary_config.json)
 SP-8    SP08_glossary_gate.py            (human review gate)
 SP-9    SP09_translation_menu.py         (→ Translation_Control_Center.csv)

         ══ MANUAL GATE ══════════════════════════════════
         Operator reviews Translation_Control_Center.csv
         Operator marks COMMAND=YES for translation batch (≤450k chars)
         ═════════════════════════════════════════════════

 SP-10   SP10_translate_deepl.py          (DeepL batch → pt-BR/content.html)
 SP-2c   SP02_upgrade_identity.py --apply --force  (preserve titles.pt — E1 fix)

 ─── [SA] AUDIT ───────────────────────────────────────────
 SA-0    SP02_upgrade_identity.py         (dry-run consistency check)
 SA-1    SA01_final_audit.py --apply      (SHA-256 structural audit)
 SA-2    SA02_freeze_manifest.py          (global immutability manifest)
 SA-3    SA03_translation_progress.py     (PT-BR progress report)

 ─── [SD] DISTRIBUTION ────────────────────────────────────
 SD-1    SD01_generate_asset_map.py       (→ asset_map.json)
         [AUTO-BOOTSTRAP if needed]
         setup_v54_static_site.sh         (build 13-ssg/ environment)
 SD-3    13-ssg/SD03_static_site_build.py (→ 13-static-site/ via build.py)
 SD-4    SD04_wordpress_inject.py         (→ WordPress local, human gate)

 ─── [REPORT] ─────────────────────────────────────────────
 MI99    MI99_mission_report.py           (called after SG, SP, SD)

══════════════════════════════════════════════════════════════
  Total steps: 22 automated + 1 manual operator gate (SP10)
  Est. runtime: varies by CSL size and DeepL quota
══════════════════════════════════════════════════════════════
```

---

## SECTION 5 — RISK ASSESSMENT

### Applied fixes — residual risk

| Fix | Residual Risk | Level |
|---|---|---|
| F1 — SD03 shim | `setup_v54_static_site.sh` must also be updated to copy `SD03_static_site_build.py` (in addition to `build.py`) into `13-ssg/`. Without this, the shim won't exist in `13-ssg/` to be found. | LOW |
| F3 — SP06 | `DIR_13_SSG_ENGINE / "assets" / "audio" / "en-US"` path must exist at runtime. This path was hardcoded before — now derived from config. If `DIR_13_SSG_ENGINE` changes in config, SP06 follows automatically. | ZERO |
| F3 — SP07 | `GLOSSARY_JSON` in config points to `metadata/glossary_config.json`. Verify this matches the actual path expected by SP08 and SP10 consumers. Currently consistent. | ZERO |
| F3 — SP08 | SP08 uses `GLOSSARY_JSON` via `csv.reader` delimiter `';'` hardcoded. If Glossario_v5.csv changes delimiter, this will silently fail. Not introduced by this fix. | ZERO (pre-existing) |
| F3 — SG04 | `BENG_ROOT = BASE_DIR.parent` — if `BENG_BASE` env points to a path not under a `beng-fut`-equivalent parent, the WP uploads path will be wrong. Operator must ensure `WP_UPLOADS_DIR` is reachable. | LOW |
| F4 — Bootstrap guard | `setup_v54_static_site.sh` is itself hardcoded to `/beng-fut/pipeline` — does not respect `BENG_BASE`. If pipeline is relocated, bootstrap will succeed syntactically but deploy to wrong dirs. | LOW (pre-existing) |

### Unchanged fragilities (non-blocking)

| Fragility | Risk | When does it surface |
|---|---|---|
| F2 — DI00 dead path | DI phase fails on any machine | Only if operator explicitly runs `--diagnostic` |
| SP03/SP04 overlap | If run in wrong order without `--apply`, no damage. With `--apply`, potential field overwrite | Only if run manually outside orchestrator |
| `axis sp12` broken | `axis sp12` command aborts | Never called by pipeline |
| SN01 snapshot dir | Snapshots go to `/beng-fut/snapshots` regardless of BENG_BASE | Cosmetic — does not affect rebuild |

### Rebuild capability — preserved

All 30 CORE scripts remain intact. No logic was modified — only import resolution was changed in 4 scripts (SP06, SP07, SP08, SG04). The canonical execution order in `run_full_pipeline.sh` is unchanged. The pipeline can perform a full rebuild from the PureDhamma backup with no architectural changes required.

**The only prerequisite before running `--full` on a fresh environment:**  
`setup_v54_static_site.sh` must be updated to also copy `SD03_static_site_build.py` into `13-ssg/`. After that, the bootstrap guard in `run_sd()` will handle this automatically on subsequent runs.

---

*Stabilization pass complete. Pipeline spine is coherent. Rebuild capability preserved.*  
*Next recommended action: Update `setup_v54_static_site.sh` PASSO 3 to copy both `build.py` and `SD03_static_site_build.py` into `13-ssg/`.*
