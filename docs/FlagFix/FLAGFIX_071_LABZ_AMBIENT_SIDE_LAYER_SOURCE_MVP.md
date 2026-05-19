# FlagFix 071 - LABZ Ambient Side Layer Source MVP

Date: 2026-05-19

## Context

#FlagFix_070 audited the LABZ ambient side layer concept and recommended: `GO WITH GUARDS`.

This sprint implements the smallest source-only MVP:

- inert markup in `pipeline/13-ssg/templates/base.html`;
- CSS-only placeholder visuals in `pipeline/13-ssg/static/css/style.css`;
- no JavaScript changes;
- no generated static output changes.

## Files Changed

- `pipeline/13-ssg/templates/base.html`
- `pipeline/13-ssg/static/css/style.css`
- `docs/FlagFix/FLAGFIX_071_LABZ_AMBIENT_SIDE_LAYER_SOURCE_MVP.md`

## LABZ Activation Mechanism

LABZ continues to be controlled by the existing stardust theme state:

- Active selector: `body[data-theme="stardust"]`
- Toggle function: `toggleLabz()` in `pipeline/13-ssg/static/js/main.js`
- No JavaScript was changed for this MVP.

The ambient layer is hidden by default and becomes visible only when stardust mode is active on sufficiently wide screens.

## Markup Summary

Added a decorative layer near the top of the body, outside `<main>`:

- `.labz-ambient-layer`
- `.labz-ambient-side-left`
- `.labz-ambient-side-right`
- six `.labz-ambient-motif` placeholder elements

The layer is inert:

- `aria-hidden="true"`
- no links;
- no buttons;
- no inputs;
- no focusable elements.

## CSS Behavior Summary

The CSS:

- keeps `.labz-ambient-layer` hidden by default;
- shows it only under `body[data-theme="stardust"]`;
- positions it fixed outside the main reading frame;
- keeps `main` above the decorative layer with `z-index: 1`;
- uses subtle abstract botanical placeholder motifs;
- uses CSS only;
- does not require final image assets yet;
- does not affect layout or text flow.

The implementation intentionally avoids final flora/fauna imagery in this sprint. The current shapes are placeholders for future visual direction.

## Accessibility Guards

Accessibility guardrails included:

- `aria-hidden="true"` on the decorative layer;
- `pointer-events: none`;
- no interactive descendants;
- no focusable elements;
- no semantic content;
- no text content inside the motifs.

## Mobile And Print Guards

Mobile/narrow viewport behavior:

- Ambient layer is only enabled inside `@media (min-width: 1101px)`.
- It remains hidden on narrower screens.

Print behavior:

- `.labz-ambient-layer` was added to the existing print exclusion list.
- It is hidden with `display: none !important` in print.

## Reduced-Motion Guard

The placeholder movement is only enabled under:

```css
@media (prefers-reduced-motion: no-preference)
```

Users requesting reduced motion receive the static decorative state.

## No-Claims Confirmation

This MVP adds decorative ambient visuals only.

No claim language was added to source UI, code comments, or visible copy. The feature does not describe or promise health, study, attention, learning, performance, or wellbeing effects.

## Validation Results

Path scope before report:

```text
pipeline/13-ssg/static/css/style.css
pipeline/13-ssg/templates/base.html
PATH_SCOPE_OK
```

Forbidden claim language scan on source diff:

```text
NO_FORBIDDEN_CLAIM_LANGUAGE
```

## No Static Regeneration

No build or SSG regeneration was run.

`pipeline/13-static-site/**` was not modified.

## Recommendation

Next recommended sprint:

- `#FlagFix_072 - LABZ ambient side layer visual asset design`

Suggested scope:

- design/select final decorative visual assets;
- keep assets compressed and decorative;
- preserve the existing source-only guards;
- do not regenerate static until a later approved sprint.

## Explicit Non-Actions

- No final images were created.
- No JavaScript was modified.
- No generated static output was modified.
- No build or pipeline run.
- No deploy.
- No Netlify upload.
- No push to `main`.
- No DeepL call.
- No translation.
- No CSL modification.
- No metadata CSV modification.
- No `Translation_Control_Center.csv` modification.
- No SP10/SP11 modification.
- No `axis-niddhi-published` modification.
