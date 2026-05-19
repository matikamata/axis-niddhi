# #FlagFix_091 — LABZ Design Polish Plan

## Purpose
Define a read-only design polish plan before any LABZ code/CSS/asset change. LABZ is structurally migratable, but currently under visual hold.

## Current decision chain
- `#088`: structurally possible; Netlify gap is payload/content, not host lock-in.
- `#089`: visual review required before promotion.
- `#090`: `VISUAL_HOLD_NEEDS_DESIGN_POLISH`.

## Current LABZ map (read-only snapshot)
- LABZ file inventory count (`/tmp/flagfix_091_labz_file_inventory.txt`): `12`
- LABZ reference hit count (`/tmp/flagfix_091_labz_reference_hits.txt`): `13821` (broad keyword match, includes content-text noise plus true LABZ implementation markers)
- Core implementation remains in:
  - `pipeline/13-ssg/templates/base.html`
  - `pipeline/13-ssg/static/css/style.css`
  - `pipeline/13-ssg/static/js/main.js`
  - `pipeline/13-static-site/css/style.css`
  - `pipeline/13-static-site/js/main.js`
  - `pipeline/13-static-site/assets/labz/*`

## Design problems to solve

### A. Landing hierarchy
- Ensure LABZ ambient layer does not compete with landing CTAs (`ENTER ARCHIVE` / `CONTRIBUTE`).
- Keep the “Vitrine Clara” first impression as the primary signal.

### B. Visual subtlety
- Reduce ornamental prominence (opacity, scale, contrast, density).
- Avoid “feature demo” feel on stable-facing surfaces.

### C. Copy/naming
- Avoid exposing experimental language in stable contexts.
- Keep labels neutral; no staging/experimental host copy leaks.

### D. Motion/interaction
- Minimize ambient animation amplitude/duration.
- Preserve calm reading posture; zero distracting movement bursts.

### E. Mobile/narrow viewport
- Confirm LABZ remains hidden/neutral on narrow viewports.
- Validate no overlap with navigation, CTA blocks, or reading columns.

### F. Asset quality
- Validate transparency edges and anti-aliasing quality.
- Confirm no artifacts (white box, halos, clipping).

### G. Performance
- Keep added weight low and predictable.
- Ensure no layout shift introduced by ambient layer.

### H. Accessibility
- Decorative layer must stay inert (`aria-hidden`, non-focusable behavior).
- Maintain readable contrast and unobstructed interactive controls.

### I. Print/noise isolation
- Guarantee no LABZ visuals in print surfaces.
- Keep print output canonically content-first.

### J. Promotion scope
- Promotion must be surgical and reversible.
- Separate Cloudflare polish validation from any Netlify/Vitrine promotion.

## Proposed polish principles
- LABZ must support the Vitrine, not compete with Archive/Contribute.
- Visual layer should be subtle and optional-looking.
- No experimental/staging wording on Netlify.
- No excessive animation or distraction.
- No print interference.
- No new canonical/content semantics.
- Static-only, reversible, minimal patch.

## Candidate implementation plan for future sprint (not executed now)
Proposed next sprint:

`#FlagFix_092 — LABZ minimal visual polish patch on Cloudflare only`

Proposed patch shape (future only):
- CSS class tuning only
- reduce opacity/motion
- constrain placement
- hide from print
- verify mobile viewport
- no Netlify promotion

## Acceptance criteria (future gate)
- Cloudflare visual review PASS
- mobile/narrow viewport PASS
- no print interference
- LABZ/Bodhi assets clean
- no host-specific copy
- no broad static sync
- no Netlify promotion until explicit approval

## Recommendation
`READY_FOR_POLISH_PATCH_ON_CLOUDFLARE_ONLY`

## Explicit non-actions
- No deploy
- No Netlify upload
- No sync/copy to published
- No build/pipeline run
- No website file changes in this sprint
- No LABZ/Bodhi/flower file changes in this sprint
- No DeepL/translation
- No CSL/metadata/TCC/SP10/SP11 changes
- No `.gitignore` changes
