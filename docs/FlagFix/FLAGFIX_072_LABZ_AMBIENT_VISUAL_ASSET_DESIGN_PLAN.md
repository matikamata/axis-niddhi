# FlagFix 072 - LABZ Ambient Visual Asset Design Plan

Date: 2026-05-19

## Context

Latest checkpoint:

- `checkpoint/flagfix-071-labz-ambient-side-layer-source-mvp-20260519`

#FlagFix_071 merged the source-only LABZ ambient side layer MVP. This document plans the future visual asset system. It does not create images and does not change HTML, CSS, JavaScript, generated static output, deployment state, or published payloads.

## Current Implementation Summary

Markup lives in:

- `pipeline/13-ssg/templates/base.html`

CSS lives in:

- `pipeline/13-ssg/static/css/style.css`

Activation mode:

- LABZ is active when `body[data-theme="stardust"]` is present.
- The ambient layer is hidden by default.
- The ambient layer becomes visible only in stardust mode and only above the wide-screen breakpoint.

Current placeholder behavior:

- Source-only decorative side layer outside `<main>`.
- `aria-hidden="true"`.
- No focusable elements.
- `pointer-events: none`.
- Hidden in print.
- Hidden on narrow/mobile viewports.
- Motion only under `prefers-reduced-motion: no-preference`.
- CSS-only placeholder motifs; no final image assets.

## Asset Design Goals

The visual direction should remain:

- decorative ambient only;
- noble flora/fauna;
- quiet and contemplative;
- non-distracting during long reading;
- visually subordinate to the text;
- suitable for LABZ/stardust mode only;
- free of medical, therapeutic, cognitive, subliminal, healing, wellness, performance, or accelerated-learning claims.

No UI copy, code comments, filenames, alt text, commit messages, or docs should imply effects beyond decoration.

## Proposed Minimal Asset Set

Recommended first asset set:

- `labz-ora-pro-nobis-left.webp`
- `labz-lily-right.webp`
- `labz-bee-gold-soft.webp`
- `labz-bee-blue-soft.webp`
- `labz-bee-amber-soft.webp`

Suggested usage:

- Left side: one soft Ora-pro-nobis floral/vine cluster.
- Right side: one soft lily cluster.
- Bee assets: optional small accents used sparingly, with no rapid motion.

Format recommendation:

- Prefer WebP for first implementation.
- Use transparent PNG only if WebP transparency/edge quality is insufficient.
- Avoid SVG for painterly flora/fauna unless the artwork is deliberately flat/vector and very small.

Rationale:

- WebP gives good compression for soft raster artwork and supports transparency.
- PNG can preserve transparency well but may be much larger.
- SVG is excellent for simple shapes but can become heavy or brittle for organic artwork.

## Technical Constraints

Asset constraints:

- Transparent background when possible.
- No embedded text.
- No strong glow, blinking, flashing, or high-contrast edges.
- No rapid motion.
- No layout-shifting dimensions.
- No full-viewport photographic background.
- Avoid dense patterns behind or near text.
- Keep alpha edges soft enough for stardust background.

Recommended dimensions:

- Flora side cluster source images: maximum about `480px` wide by `900px` tall.
- Bee accents: maximum about `220px` wide by `220px` tall.
- Export at actual intended display size or at most 2x display size for high-DPI screens.

Recommended file budgets:

- Flora side cluster: target under `160KB` each, hard cap around `300KB`.
- Bee accent: target under `60KB` each, hard cap around `120KB`.
- Total LABZ ambient asset payload for MVP: target under `500KB`, hard cap around `900KB`.

CSS `background-image` vs `<img>` tradeoff:

| Approach | Pros | Cons | Recommendation |
|---|---|---|---|
| CSS `background-image` | Keeps decorative assets out of accessibility tree; simple with existing inert layer; no extra semantic markup. | Native lazy loading is not available; asset loading is tied to CSS. | Preferred for MVP if asset count stays small. |
| `<img>` with empty `alt` and `aria-hidden` wrapper | Can use `loading="lazy"`, explicit dimensions, and source-level asset references. | More DOM elements; higher risk of accidental semantics/focus if future edits drift. | Consider only if image loading/performance needs more control. |

Decorative images must remain hidden from assistive technology. For the CSS-background MVP, keep the existing `aria-hidden="true"` layer and no text content.

## Storage Location Recommendation

Recommended SSG source asset path:

- `pipeline/13-ssg/static/assets/labz/`

Expected generated static path after future regeneration:

- `pipeline/13-static-site/assets/labz/`

Do not add assets directly to generated static without an explicit source+generated parity decision.

## Naming Convention

Use lowercase, hyphenated, explicit names:

- `labz-ora-pro-nobis-left.webp`
- `labz-lily-right.webp`
- `labz-bee-gold-soft.webp`
- `labz-bee-blue-soft.webp`
- `labz-bee-amber-soft.webp`

Avoid:

- claim language;
- mood-altering language;
- medical/therapy terms;
- vague names such as `magic-focus.webp`;
- asset names implying subliminal, healing, cognition, performance, or accelerated learning effects.

## Integration Plan

Phase 1 - Candidate Assets Outside Repo:

- Create or select candidate assets outside the Git working tree.
- Check transparency, edge quality, dimensions, and visual tone.
- Review on dark/stardust background.
- No repo changes.

Phase 2 - Add Compressed Assets To SSG Source:

- Add approved assets under `pipeline/13-ssg/static/assets/labz/`.
- Keep file count small.
- Record file sizes and SHA256 values in a FlagFix report.
- Do not update generated static yet unless that sprint explicitly includes regeneration.

Phase 3 - Wire CSS Background Images:

- Update existing `.labz-ambient-*` CSS to use `background-image`.
- Keep placeholders as fallback if desired.
- Preserve `aria-hidden`, `pointer-events: none`, print hiding, narrow viewport hiding, and reduced-motion behavior.
- Avoid JavaScript unless clearly necessary.

Phase 4 - Controlled Static Regeneration And Preview:

- Run approved static regeneration in a separate sprint.
- Verify generated static changes are expected.
- Check representative pages in LABZ mode.
- Test wide desktop, laptop, mobile/narrow, print preview, and reduced-motion.

Phase 5 - Vitrine/Netlify Promotion:

- Promote only after explicit approval.
- Use the existing reviewed package/deployment discipline.
- Do not deploy directly from asset/design sprints.

## Risk Table

| Risk | Level | Concern | Guard |
|---|---:|---|---|
| Accessibility | Medium | Decorative assets could become screen-reader noise or intercept input. | Keep layer `aria-hidden`, no focusable elements, `pointer-events: none`. |
| Print | Medium | Decorative images could leak into PDFs. | Keep `.labz-ambient-layer` in print exclusion. |
| Mobile | High | Side visuals do not have lateral space on narrow screens. | Keep hidden below the existing wide-screen breakpoint. |
| Performance | Medium | Large transparent images can increase page weight. | WebP first, strict size budgets, small asset count, no full-screen backgrounds. |
| Visual distraction | Medium | Bees or flowers could compete with reading. | Low opacity, sparse placement, no rapid motion, no bright flicker. |
| Doctrinal seriousness/tone | Medium | Decorative fauna/flora could feel playful or unserious if overdone. | Noble, quiet, sparse, visually subordinate assets; review with representative pages. |
| Deployment | Medium | Source assets require static regeneration and later Vitrine promotion. | Separate asset, regeneration, preview, package, and deployment sprints. |

## Recommendation

Recommendation: GO WITH GUARDS.

Proceed only as a staged visual asset system:

- design/select assets outside repo first;
- add compressed source assets only after review;
- wire CSS separately;
- regenerate static only in an approved sprint;
- deploy to Vitrine/Netlify only after explicit approval.

The first implementation should stay decorative, quiet, and non-claiming. It should preserve all #FlagFix_071 guards.

## Explicit Non-Actions

- No images were created.
- No CSS was modified.
- No HTML was modified.
- No JavaScript was modified.
- No generated static output was modified.
- No build or pipeline run.
- No deploy.
- No Netlify upload.
- No DeepL call.
- No translation.
- No CSL modification.
- No metadata CSV modification.
- No `Translation_Control_Center.csv` modification.
- No TCC/SP10/SP11 modification.
- No `axis-niddhi-published` modification.
