# #FlagFix_089 — LABZ Visual Design Review Checklist

## Purpose
Create a visual/design gate checklist before any LABZ promotion to Netlify/Vitrine.

## #088 summary (input)
- Production LABZ inventory count: `12`
- Published LABZ inventory count: `5`
- No direct LABZ host lock-in found
- Netlify non-visibility is a payload gap, not host limitation
- Prior recommendation: `NEEDS_VISUAL_DESIGN_REVIEW`

## LABZ visual inventory summary
- Current inventory snapshot count (`pipeline/13-static-site` + `pipeline/13-ssg`, labz/flower/flores/bodhi name filters): `12`
- Inventory file: `/tmp/flagfix_089_labz_visual_inventory.txt`
- Includes LABZ flower assets in production:
  - `pipeline/13-ssg/static/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
  - `pipeline/13-ssg/static/assets/labz/labz-lily-right-mvp-01.webp`
  - `pipeline/13-static-site/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
  - `pipeline/13-static-site/assets/labz/labz-lily-right-mvp-01.webp`

## Public Cloudflare observation summary (read-only)
- Checked:
  - `https://niddhi.pages.dev/`
  - `https://niddhi.pages.dev/welcome`
- Raw HTML grep for `LABZ/labz/stardust/ambient/flower/BodhiCircuitLeaf` yielded no direct text hits.
- Interpretation: LABZ visibility likely depends on runtime toggle/theme state and/or CSS behavior, so manual visual review is still required.

## Netlify promotion status in #089
No Netlify/LABZ promotion in this sprint.

## Visual Checklist

### A. Landing integration
- Does LABZ support the Vitrine without distracting from Archive/Contribute?
- Does it fit the approved “Vitrine Clara” surface?
- Does it avoid looking experimental on the stable Netlify homepage?

### B. Typography/copy
- Are labels neutral and understandable?
- No “LABZ” jargon exposed unless intentional?
- No Cloudflare/experimental/staging wording on Vitrine?

### C. Motion/interaction
- Are flowers subtle enough?
- No excessive motion?
- No mobile viewport issues?
- No print interference?

### D. Asset quality
- Transparent assets clean?
- No white square/background artifacts?
- Correct sizing/resolution?
- No missing assets?

### E. Performance
- Additional payload acceptable?
- No blocking script risk?
- No layout shift?

### F. Accessibility
- Does visual layer avoid obscuring content?
- Keyboard and links remain usable?
- Color contrast unaffected?

### G. Scope for future promotion
- Exact files likely needed:
  - `pipeline/13-static-site/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
  - `pipeline/13-static-site/assets/labz/labz-lily-right-mvp-01.webp`
  - `pipeline/13-static-site/css/style.css` (ambient side-layer block with image refs)
  - Any required base/welcome/index HTML that actually enables LABZ layer for target pages
- Exact files excluded:
  - CSL/metadata/TCC/SP10/SP11
  - translation pipelines
  - `.gitignore`
  - unrelated docs/scripts
- Snapshot/checkpoint required before any promotion: yes.

## Recommendation
`VISUAL_REVIEW_REQUIRED_BEFORE_PROMOTION`

## Suggested next sprint
`#FlagFix_090 — LABZ visual review on Cloudflare preview`

## No-change confirmations
- No deploy
- No Netlify upload
- No sync/copy to published
- No build/pipeline run
- No website file edits
- No LABZ/Bodhi/flower file edits
- No DeepL/translation
- No CSL/metadata/TCC/SP10/SP11 changes
- No `.gitignore` changes
