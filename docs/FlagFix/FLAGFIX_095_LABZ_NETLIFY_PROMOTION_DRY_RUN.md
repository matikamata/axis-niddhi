# #FlagFix_095 — LABZ Netlify Promotion Dry-Run

## Purpose
Run a controlled dry-run only (no real sync) to identify exactly what LABZ-related files would be promoted from production static payload to published static payload.

## Source checkpoint
- `checkpoint/flagfix-094-labz-controlled-netlify-promotion-plan-20260519`

## Repository states (read-only)
- Production (`axis-niddhi-production`): `## main...origin/main`
- Published (`axis-niddhi-published`): `## main...origin/main [ahead 2]`

## Counts and comparison
- Production static LABZ candidate count: `8`
  - file: `/tmp/flagfix_095_static_labz_candidates_rel.txt`
- Published LABZ count: `5`
  - file: `/tmp/flagfix_095_published_labz_rel.txt`
- Missing from published count: `3`
  - file: `/tmp/flagfix_095_labz_missing_from_published_rel.txt`
- Common path count: `5`
  - file: `/tmp/flagfix_095_labz_common_rel.txt`

## Exact candidate promotion paths (missing from published)
- `assets/labz`
- `assets/labz/labz-lily-right-mvp-01.webp`
- `assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`

## Reference files considered (dry-run only)
From `/tmp/flagfix_095_reference_files_rel.txt`:
- `index.html`
- `welcome.html`
- `contribute.html`
- `css/style.css`

Context scan file:
- `/tmp/flagfix_095_labz_reference_context.txt` (`74` lines)

## Dry-run commands and outputs

### 1) Assets-only dry-run
Command:
- `rsync -avnc --files-from=/tmp/flagfix_095_labz_missing_from_published_rel.txt ...`

Output file:
- `/tmp/flagfix_095_rsync/labz_assets_only_dry_run.txt`

Line count:
- `8`

What would change:
- `assets/labz/`
- `assets/labz/labz-lily-right-mvp-01.webp`
- `assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`

### 2) Reference-files dry-run
Command:
- `rsync -avnc --files-from=/tmp/flagfix_095_reference_files_rel.txt ...`

Output file:
- `/tmp/flagfix_095_rsync/reference_files_dry_run.txt`

Line count:
- `6`

What would change:
- `css/style.css`

What would not change in this dry-run:
- `index.html`
- `welcome.html`
- `contribute.html`

## Dry-run interpretation
- Dry-run indicates both:
  1. LABZ assets would be newly copied (`assets/labz/*`)
  2. LABZ behavior/style parity would require `css/style.css` update
- No broad/static-wide copy was indicated by these scoped dry-runs.

## Safety confirmation
- No real copy/sync executed (`-n` dry-run only).
- No deploy, no Netlify upload.
- Published repo unchanged after dry-run:
  - `## main...origin/main [ahead 2]`

## Recommendation
`READY_FOR_SNAPSHOT_BEFORE_REAL_PROMOTION`

## Next sprint recommendation
`#FlagFix_096 — LABZ promotion snapshot before real copy`

## No-change confirmations
- No deploy
- No Netlify upload
- No sync/copy to published
- No edits in `axis-niddhi-published`
- No build/pipeline run
- No website/CSS/LABZ/Bodhi/flower edits
- No DeepL/translation
- No CSL/metadata/TCC/SP10/SP11 changes
- No `.gitignore` changes
