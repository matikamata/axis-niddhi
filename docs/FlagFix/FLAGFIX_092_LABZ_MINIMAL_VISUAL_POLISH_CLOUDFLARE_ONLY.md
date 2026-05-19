# #FlagFix_092 — LABZ Minimal Visual Polish Patch on Cloudflare Only

## Purpose
Apply a minimal, reversible LABZ visual polish patch for Cloudflare-facing production static/source only, without any Netlify/Vitrine promotion.

## Files changed
- `pipeline/13-ssg/static/css/style.css`
- `pipeline/13-static-site/css/style.css`

Patch type: `CSS-only`

## Design issue addressed
From #090/#091 hold:
- ambient visuals were too prominent for stable-facing hierarchy
- motion needed to be calmer
- print/reduced-motion guards needed explicit reinforcement

## Exact polish decisions
1. Reduced side-art prominence:
   - side image opacity: `0.44 -> 0.28`
   - motif opacity: `0.16 -> 0.09`
   - motif border/halo softened
2. Reduced visual footprint:
   - side panel width: `156px -> 128px`
   - side placement shifted farther from content edges
   - vertical bounds tightened (`top/bottom`)
3. Calmed animation:
   - base duration: `12s -> 18s`
   - stagger durations: `15/18s -> 22/26s`
   - float amplitude: `12px -> 6px`
4. Added explicit reduced-motion fallback:
   - `@media (prefers-reduced-motion: reduce)` disables ambient motif animation
5. Added explicit print isolation:
   - `@media print { .labz-ambient-layer { display: none !important; } }`

## Path scope result
`PATH_SCOPE_OK`

Changed paths are restricted to LABZ CSS counterparts plus this report.

## Print/reduced-motion/mobile considerations
- Print: LABZ ambient layer now explicitly forced off in print.
- Reduced motion: explicit animation disable for `prefers-reduced-motion: reduce`.
- Mobile/narrow: existing min-width gating (`@media (min-width: 1101px)`) remains in place.

## Netlify/Vitrine confirmation
- No sync/copy to published.
- No edit in `/home/sanghop/axis/axis-niddhi-published`.
- Published repo check remained unchanged in this sprint (`main...origin/main [ahead 2]`).

## Forbidden-scope confirmation
- No CSL/metadata/TCC/SP10/SP11/DeepL/translation changes.
- No `.gitignore` changes.

## Recommendation
Proceed with:

`#FlagFix_093 — LABZ post-polish Cloudflare visual review`

## No-change confirmations
- No deploy/manual upload
- No Netlify promotion
- No build/pipeline run
- No published repo modifications
