# FlagFix Batch 01 — Print Review UX

Status: planning / triage  
Scope: printed/PDF review copies only  
Repository: https://github.com/matikamata/axis-niddhi  
Milestone: FlagFix Batch 01 — Print Review UX

---

## Purpose

This batch collects print-review improvements discovered while producing the first human review packet for the AXIS-NIDDHI pt-BR translation layer.

These issues do not block continued review. They are UX, layout, and traceability improvements for printed/PDF copies.

The canonical source remains PureDhamma.net. AXIS-NIDDHI printed copies are review artifacts, not doctrinal replacements.

---

## Included Issues

- #15 — FlagFix 006 PRINT NAV LABEL LOCALIZATION
- #26 — FlagFix 016 PRINT MARGIN CONTENT WIDTH ALIGNMENT
- #27 — FlagFix 017 PRINT GREEN LINE DECORATION STANDARDIZATION
- #28 — FlagFix 018 PRINT DRAFT BANNER TYPOGRAPHY GRAY TONE
- #29 — FlagFix 019 PRINT PREV NEXT NAV COMPACTION AND BOX DESIGN

---

## Execution Principle

Treat the printed page as a review instrument.

Do not change CSL source content.

Do not normalize didactic color semantics from PureDhamma content.

Do not shorten URLs.

Do not alter doctrinal terms.

Do not make browser-only beauty changes that harm print traceability.

---

## Proposed Execution Order

### 1. Print margin/content alignment

Start with issue #26 because it affects every printed page.

Goal: ensure printed review content is visually centered and balanced between left/right page margins.

Acceptance criteria:

- content block appears visually centered in browser print preview
- no clipped left border
- no unnecessary horizontal shrinkage
- A4 and Letter remain acceptable
- no change to screen layout

---

### 2. Draft banner typography

Handle issue #28 after print width is stable.

Goal: make the DRAFT / RASCUNHO block look more archival, technical, and less visually dominant.

Acceptance criteria:

- print-only
- gray-tone border and text
- typewriter/monospace feeling
- maintains full traceability text
- no screen impact

---

### 3. Prev/Next print navigation

Handle issues #15 and #29 together.

Goal: compact the final navigation block and localize/clarify the printed navigation labels.

Acceptance criteria:

- reduced vertical gap before final navigation
- boxed design similar in spirit to the screen version
- PT labels available where appropriate
- no extra page wasted only for navigation
- links remain visible and traceable

---

### 4. Green line / decorative rule standardization

Handle issue #27 last.

Goal: investigate whether the elegant green line seen in one printed copy came from CSS, browser rendering, or accidental page-break behavior.

Acceptance criteria:

- determine exact source of the line
- either standardize it as an intentional print ornament or remove inconsistency
- document the decision
- no accidental decoration dependent on browser state

---

## Implementation Surface

Likely files:

- pipeline/13-ssg/static/css/style.css
- pipeline/13-static-site/css/style.css
- pipeline/13-ssg/static/js/main.js
- pipeline/13-static-site/js/main.js
- possibly pipeline/13-ssg/templates/base.html or post.html if navigation markup must change

Any change to generated/static-site files must be mirrored carefully according to current repository practice.

---

## Validation Checklist

Before commit:

```bash
git status -sb
git diff --stat
git diff --name-only
````

Manual browser validation:

* open a representative page
* open print preview
* inspect first page banner
* inspect body margins
* inspect final navigation page
* test at default scale
* test with headers/footers off
* test at least one long essay and one short essay

Suggested sample pages:

* [https://niddhi.pages.dev/pages/TL.JJ.008/](https://niddhi.pages.dev/pages/TL.JJ.008/)
* [https://niddhi.pages.dev/pages/TL.DD.005/](https://niddhi.pages.dev/pages/TL.DD.005/)
* [https://niddhi.pages.dev/pages/TL.EE.003/](https://niddhi.pages.dev/pages/TL.EE.003/)
* [https://niddhi.pages.dev/pages/TL.EE.011/](https://niddhi.pages.dev/pages/TL.EE.011/)

---

## Non-Goals

This batch does not solve:

* title translation defects
* Pāli grammar or diacritics
* image/flowchart translation
* audio asset resolution
* canonical study order
* DeepL protection of Pāli quotes

Those are tracked in separate FlagFix batches.

---

## Suggested Branch Name

flagfix-batch01-print-review-ux

---

## Suggested Commit Message

fix(print): refine review copy layout and navigation

