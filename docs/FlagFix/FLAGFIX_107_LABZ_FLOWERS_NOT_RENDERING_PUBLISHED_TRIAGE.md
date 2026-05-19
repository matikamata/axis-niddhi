# #FlagFix_107 — LABZ Flowers Not Rendering in Published Payload (Triage)

Date: 2026-05-19  
Workspace: `/home/sanghop/axis`

## Source checkpoint
`checkpoint/flagfix-106-surface-status-snapshot-20260519`

## Symptom
With local serving of published payload (`/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`), LABZ can be toggled but flower visuals do not appear.

## Key conclusion
This is **not Netlify-specific** (reproduced in local published payload behavior).

## Production vs published LABZ inventory
- Production labz/bodhi/flower path count: `8`
- Published labz/bodhi/flower path count: `8`
- Asset inventory is present on both sides for:
  - `assets/labz/`
  - `assets/labz/labz-lily-right-mvp-01.webp`
  - `assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
  - Bodhi assets

## CSS reference comparison
- `style.css` production vs published diff: `160` lines (`/tmp/flagfix_107_style_css_diff.txt`).
- Production CSS contains explicit LABZ ambient rendering block:
  - `.labz-ambient-layer`
  - `@media (min-width: 1101px)`
  - `body[data-theme="stardust"] .labz-ambient-side...`
  - `background-image: url("../assets/labz/labz-ora-pro-nobis-left-mvp-01.webp")`
  - `background-image: url("../assets/labz/labz-lily-right-mvp-01.webp")`
- Published CSS **does not contain** this LABZ ambient rendering block (file jumps from previous section into FF-014 block where production has LABZ ambient layer rules).

## HTML reference comparison
- Landing files checked in production and published (`index.html`, `welcome.html`, `contribute.html`) have no LABZ ambient references by grep.
- Additional check:
  - Production `archive.html` includes `.labz-ambient-layer`.
  - Published `archive.html` has LABZ button/toggle but no `.labz-ambient-layer` container.

## Asset existence check
- Published referenced LABZ assets extraction from file content produced no direct `assets/labz/...` hits in published static (`/tmp/flagfix_107_published_referenced_labz_assets.txt` empty).
- Even so, assets exist on disk under `assets/labz/` in published.
- Interpretation: assets are available, but reference/render layer is incomplete in published payload.

## Likely root cause
Published payload has a **reference/render-layer gap**:
1. LABZ toggle logic exists (`js/main.js` and button present).
2. LABZ flower assets exist.
3. But published static is missing critical LABZ ambient CSS/markup needed to paint side flowers.

## Root cause classification
`LABZ_RENDERING_GAP_CONFIRMED_REFERENCE_LAYER_MISSING`

## Recommendation for #108
`#FlagFix_108 — promote LABZ reference layer to published payload`

Expected #108 scope should focus on promoting the missing LABZ reference/render layer (CSS + required markup locations) into published static, with path-scope controls and no broad sync.

## Explicit no-change confirmations
- Documentation/read-only triage only.
- No push.
- No deploy.
- No Netlify upload.
- No commit in `axis-niddhi-published`.
- No reset/rebase/merge.
- No branch deletion.
- No sync/copy.
- No `axis-niddhi-published` modifications.
- No production website edits.
- No build/pipeline run.
- No DeepL/translation.
- No CSL/metadata/TCC/SP10/SP11 changes.
- No `.gitignore` changes.
