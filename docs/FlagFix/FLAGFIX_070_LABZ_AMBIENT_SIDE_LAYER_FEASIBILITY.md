# FlagFix 070 - LABZ Ambient Side Layer Feasibility Audit

Date: 2026-05-19

## Scope

This is a read-only feasibility audit for adding decorative ambient side imagery in LABZ / stardust mode. The concept is limited to visual atmosphere outside the compact reading/content box.

Important copy/design constraint:

- Treat flora/fauna imagery as decorative ambient visual design only.
- Do not make medical, therapeutic, cognitive, focus, healing, wellness, or performance claims in UI text, code comments, docs, filenames, alt text, or commit messages.

No implementation was performed.

## Current LABZ Implementation Map

Authoritative SSG source:

- `pipeline/13-ssg/templates/base.html`
- `pipeline/13-ssg/static/css/style.css`
- `pipeline/13-ssg/static/js/main.js`

Generated static mirrors:

- `pipeline/13-static-site/**`
- `pipeline/13-static-site/css/style.css`
- `pipeline/13-static-site/js/main.js`
- generated post pages containing `#labz-banner` and `#labz-btn`

LABZ activation:

- `pipeline/13-ssg/static/js/main.js`
- Function: `toggleLabz()`
- Active state: `document.body.getAttribute('data-theme') === 'stardust'`
- On enable:
  - saves previous theme in `axis-theme-pre-labz`;
  - sets `data-theme="stardust"`;
  - stores `axis-niddhi-theme = stardust`;
  - adds `.labz-active` to `#labz-btn`;
  - adds `.visible` to `#labz-banner`.
- On disable:
  - restores previous theme;
  - removes `axis-theme-pre-labz`;
  - removes `.labz-active`;
  - removes `.visible`.

LABZ UI:

- `pipeline/13-ssg/templates/base.html`
- `#labz-banner` lives inside `<main>` before page content.
- `#labz-entry` and `#labz-btn` live in the footer inside `<main>`.

LABZ visual state:

- `pipeline/13-ssg/static/css/style.css`
- Stardust rules are keyed from `body[data-theme="stardust"]`.
- The current stardust theme changes body colors, main box shadow, heading/link colors, archive grid styling, selection, banner styling, reading progress, CSL tattoo tables, and video containers.

Print behavior:

- `pipeline/13-ssg/static/css/style.css`
- `@media print` already hides `#labz-banner`, floating controls, search, modals, footer, videos, and other UI.
- Any future ambient side layer should be added to this print exclusion list.

Motion behavior:

- `pipeline/13-ssg/static/css/style.css`
- `main` has a small entrance animation.
- Existing `@media (prefers-reduced-motion: reduce)` disables that animation.
- Future side imagery should follow the same reduced-motion policy.

## Layout Feasibility

Current reading frame:

- `main` is the compact paper/content box.
- `main` has:
  - `max-width: 840px`;
  - centered margins;
  - padding;
  - `position: relative`;
  - paper-like background and shadow.
- Post content sits inside `.post-container`.
- Article content blocks use `.content-block`, `.content-en`, and `.content-pt`; typography limits content width further to `max-width: 720px`.

Feasibility finding:

- Fixed-position side visuals outside `main` are feasible without changing text flow.
- The safest layout is a global decorative layer as a sibling of `<main>`, not inside article content.
- The layer should use `position: fixed`, `pointer-events: none`, and a lower stacking context than floating utilities/modals.
- Visibility should be controlled by `body[data-theme="stardust"]`.
- The layer should be hidden by default and only visible on sufficiently wide viewports.

Recommended placement:

```html
<div class="labz-ambient-layer" aria-hidden="true">
  <div class="labz-ambient-side labz-ambient-side-left"></div>
  <div class="labz-ambient-side labz-ambient-side-right"></div>
</div>
```

Recommended DOM location:

- In `pipeline/13-ssg/templates/base.html`;
- after `#reading-progress`;
- before floating utilities or before `<main>`.

Reason:

- Keeps decoration global and outside content semantics.
- Avoids article/post template duplication.
- Avoids affecting language switching, TOC, content flow, search, print modal, and footer.

## Recommended Minimal Design

Minimal implementation should be CSS-first:

- Add inert decorative layer markup in `base.html`.
- Add CSS in `style.css`:
  - hidden by default;
  - visible only under `body[data-theme="stardust"]`;
  - fixed left/right side positions;
  - `pointer-events: none`;
  - `aria-hidden="true"` in markup;
  - `display: none` below a desktop breakpoint;
  - `display: none !important` in `@media print`;
  - no animation by default, or extremely subtle opacity transform only when reduced-motion is not requested.
- Add image assets only when approved in a later sprint.

Suggested visual principles:

- Low opacity.
- No text overlap.
- Never sit on top of `main`.
- Avoid bright moving objects near reading lines.
- Avoid full-screen particle effects for this feature.
- Keep flora/fauna symbolic and decorative.
- Keep all filenames and comments neutral, for example `labz-ambient-flora-left.webp`, not claim-oriented names.

## File Impact Estimate

Likely minimal source changes:

- `pipeline/13-ssg/templates/base.html`
  - add ambient layer markup with `aria-hidden="true"`.
- `pipeline/13-ssg/static/css/style.css`
  - add layout, visibility, print, responsive, and reduced-motion rules.
- `pipeline/13-ssg/static/assets/...`
  - future approved bitmap assets, preferably compressed `.webp`/`.avif` plus fallback if needed.

Possible but not required:

- `pipeline/13-ssg/static/js/main.js`
  - not needed if visibility is CSS-only via `body[data-theme="stardust"]`.
  - only needed if future variations require asset rotation or randomization; avoid for MVP.

Generated output:

- `pipeline/13-static-site/**`
  - should be updated only by a later static regeneration or by a deliberate source+generated parity sprint if that project convention is required.

## Source vs Static Recommendation

Implement SSG source first.

Preferred sequence:

1. Add markup/CSS/assets to `pipeline/13-ssg` source.
2. Validate locally on representative pages.
3. Regenerate static only in a separate approved sprint.
4. Review generated static diff.
5. Promote Vitrine only after explicit approval.

Do not hand-edit generated pages for the first implementation unless a later sprint explicitly chooses a source+generated parity patch without running build.

## Accessibility Risk Table

| Risk | Level | Notes | Guard |
|---|---:|---|---|
| Screen reader noise | Medium | Decorative flora/fauna should not enter the accessibility tree. | Use `aria-hidden="true"` and no meaningful alt text for decorative CSS backgrounds. |
| Keyboard/focus interference | Medium | Fixed layers can accidentally intercept clicks/focus if implemented as interactive elements. | Use `pointer-events: none`; no links/buttons inside the layer. |
| Reduced motion | Medium | Bees or floating particles could distract or affect users sensitive to motion. | Default to static imagery; if any animation exists, disable under `prefers-reduced-motion: reduce`. |
| Contrast/readability | Medium | Bright images can compete with reading text or the stardust green palette. | Keep outside `main`, low opacity, no overlap with text, test dark/bright edges. |
| Mobile/narrow viewport | High | Side imagery has no safe lateral space on phones. | Hide below a breakpoint such as `1100px` or `1200px`. |
| Print pollution | Medium | Decorative layers could appear in PDFs. | Add `.labz-ambient-layer { display: none !important; }` in print CSS. |
| Cognitive/medical claims | High | Concept language could drift into claims about attention, calm, therapy, or cognition. | Keep UI/docs/code neutral: decorative/ambient only. |

## Performance Risk Table

| Risk | Level | Notes | Guard |
|---|---:|---|---|
| Large image payload | High | Multiple high-res flora/fauna images could slow pages. | Use compressed responsive assets; cap dimensions; consider one sprite/layer per side. |
| Layout shift | Low if fixed | Fixed layers outside flow should not shift text. | Use fixed dimensions and `position: fixed`; do not inject above content after load. |
| Animation cost | Medium | CSS filters, blur, shadows, or many moving elements can be expensive. | Avoid filter-heavy animations; prefer static opacity; respect reduced motion. |
| Lazy loading | Medium | CSS background images do not use native `loading="lazy"`. | For MVP use few small images; if `<img>` tags are used, add `loading="lazy"` and dimensions. |
| Paint/compositing | Medium | Fixed semi-transparent images can increase repaint cost on scroll. | Keep layer simple; avoid large translucent full-height textures; test scroll performance. |

## Deployment Risk Table

| Risk | Level | Notes | Guard |
|---|---:|---|---|
| CSL changes | None needed | Feature is presentation-only. | Do not touch `pipeline/09-csl`. |
| Translation changes | None needed | No text translation required. | Do not touch DeepL/TCC/SP10/SP11. |
| Pipeline behavior changes | Low | Static generation can copy assets and templates as usual. | Avoid modifying build logic for MVP. |
| Netlify/Vitrine changes | Deferred | Any deployment should be explicit and later. | Implement in production/dev first, then regenerate/review, then package/deploy only by approval. |
| Static output churn | Medium | Every page may change if base template changes. | Expect broad generated HTML diff after regeneration; review path scope carefully. |

## Proposed Implementation Phases

Phase 1 - Source-only prototype plan:

- Add inert `.labz-ambient-layer` markup to `pipeline/13-ssg/templates/base.html`.
- Add CSS-only behavior to `pipeline/13-ssg/static/css/style.css`.
- Use placeholder CSS gradients or existing neutral test asset only if explicitly approved.
- No generated static update yet unless requested.

Phase 2 - Asset selection:

- Create/select compressed decorative images.
- Prefer transparent or softly masked flora/fauna assets.
- Store under a clear source asset path such as `pipeline/13-ssg/static/assets/labz/`.
- Avoid medical/therapeutic claim language in filenames and comments.

Phase 3 - Local static regeneration and visual QA:

- Run static generation only in an approved sprint.
- Verify desktop wide, laptop, tablet, and mobile/narrow behavior.
- Verify print preview excludes ambient layer.
- Verify no text overlap and no focus/click interference.

Phase 4 - Package/promotion:

- Promote to Vitrine only through the existing reviewed package/deployment process.
- No Netlify update without explicit operator approval.

## Final Recommendation

GO WITH GUARDS.

The current architecture can support decorative LABZ-only side imagery safely because LABZ already exposes a stable `body[data-theme="stardust"]` switch, and the reading layout centers `main` with enough lateral space on wide viewports. The MVP should be source-first, CSS-driven, inert, hidden on narrow screens and print, and strictly decorative.

Primary guardrails:

- no medical/therapeutic/cognitive claims;
- no JavaScript required for MVP;
- no interaction or focusable elements;
- `aria-hidden="true"`;
- `pointer-events: none`;
- reduced-motion compliance;
- hidden on mobile/narrow screens;
- hidden in print;
- compressed assets only;
- source first, generated static/deployment later by explicit approval.

## Explicit No-Change Confirmations

- No implementation was performed.
- No images were created.
- No CSS was modified.
- No JavaScript was modified.
- No templates were modified.
- No generated static output was modified.
- No build/pipeline/deploy was run.
- No Netlify/Vitrine update was performed.
- `/home/sanghop/axis/axis-niddhi-published` was not touched.
- No CSL content was modified.
- No translation/TCC/SP10/SP11 behavior was modified.
