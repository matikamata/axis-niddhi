# FLAGFIX 028-034 - Batch closure index

Date: 2026-05-18
Workspace: `/home/sanghop/axis/axis-niddhi-production`
Scope: closure/index document for the title pipeline safety and translation preflight batch

## Scope summary

### FLAGFIX 028-031 - Title and translation pipeline safety

This block diagnosed and contained a PT title language contamination case, added a reusable title QA gate, and fenced retired/hardcoded/emergency translation scripts so old paths cannot be run by accident before the next translation batch.

### FLAGFIX 032-034 - Translation preflight and print workflow retirement

This block audited readiness for the next translation batch, confirmed the official Translation Control Center state, removed the stale print-specific control CSV, and fenced print-batch tooling that still referenced the removed file.

## Merged PRs

| PR | Sprint | Purpose |
|---:|---|---|
| #121 | `FLAGFIX_028` | Triage PT title contamination for `LD.AA.000`; record local CSL metadata correction from `Vivendo il Dhamma` to `Vivendo o Dhamma`; note static output remains stale. |
| #122 | `FLAGFIX_029` | Audit translation/title scripts, encoding risks, and temporary/legacy script risks around `SP10`/`SP11`. |
| #123 | `FLAGFIX_030` | Add read-only PT title language QA gate: `pipeline/scripts/tools/audit_pt_titles_language_contamination.py`. |
| #124 | `FLAGFIX_031` | Fence retired, hardcoded, and emergency translation scripts with explicit override environment variables. |
| #125 | `FLAGFIX_032` | Add dry-run preflight report for the next translation batch; confirm official TCC is coherent and print TCC is stale. |
| #126 | `FLAGFIX_033` | Remove stale `pipeline/metadata/Print_Translation_Control_Center.csv` and document the decision. |
| #127 | `FLAGFIX_034` | Fence/deprecate print-batch tools that referenced the removed print CSV. |

## Checkpoints

```text
checkpoint/flagfix-028-031-title-pipeline-safety-20260518
checkpoint/flagfix-032-034-translation-preflight-print-retirement-20260518
```

## Current operational truth

- `pipeline/metadata/Translation_Control_Center.csv` is the official selector for `SP10` / DeepL translation batches.
- `pipeline/metadata/Print_Translation_Control_Center.csv` is removed and retired.
- Retired translation scripts are fenced.
- Hardcoded legacy wrappers are fenced.
- Emergency remediation scripts are fenced.
- Print-batch tools that depended on the removed print CSV are fenced or redirected to retirement messaging.
- The title QA gate exists and should be run before and after any future title-writing batch:

```bash
python3 pipeline/scripts/tools/audit_pt_titles_language_contamination.py
```

## Known pending

- Static generated artifacts still contain stale `Vivendo il Dhamma`.
- CSL metadata already has the corrected `Vivendo o Dhamma`.
- No Netlify/Vitrine promotion has been done for this correction.
- The next DeepL batch is not selected: official `Translation_Control_Center.csv` currently has `COMMAND` blank.
- `439` `titles.pt` values are null/pending, which is expected until future translation batches.

## Explicit non-actions

Do not regenerate or publish static output just for one title until the next approved batch closure/promotion.

Do not use or recreate:

```text
pipeline/metadata/Print_Translation_Control_Center.csv
```

Do not use print workflow state as an `SP10` selector.

Do not run `SP10`/`SP11 --apply` without:

1. translation batch preflight;
2. explicit official TCC batch selection;
3. PT title QA gate before apply;
4. PT title QA gate after apply.

## Next recommended options

### Option A - Choose next translation batch

Select the next batch only in the official:

```text
pipeline/metadata/Translation_Control_Center.csv
```

Then rerun preflight and the PT title QA gate before any apply step.

### Option B - Regenerate and promote static later

Regenerate static output and promote Netlify/Vitrine only when batch closure is approved. This is the right moment to clear stale `Vivendo il Dhamma` from generated pages and indexes.

### Option C - Clean up retired print workflow references

If needed, run a future docs/tooling cleanup to update old references to the retired print workflow in historical docs and review tooling.

## No-change confirmation

This closure index is documentation only.

No DeepL call was made.
No translation was run.
No CSL content was modified.
No `Translation_Control_Center.csv` change was made.
No SP10/SP11 behavior was modified.
No build was run.
No pipeline was run.
No deploy was run.
No Netlify/Vitrine update was made.
No Cloudflare configuration was touched.
`/home/sanghop/axis/axis-niddhi-published` was not touched.
