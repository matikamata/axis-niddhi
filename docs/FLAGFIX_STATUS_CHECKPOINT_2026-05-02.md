# FlagFix Status Checkpoint — 2026-05-02

## Repository State

Repository: `matikamata/axis-niddhi`  
Branch: `main`  
Purpose: checkpoint after FlagFix issue migration, batch planning, print/media fixes, and title/date review scaffolding.

## Completed / Merged Work

### Core Index and Batch Planning

- `docs/FLAGFIX_INDEX.md`
- `docs/FLAGFIX_BATCH_01_PRINT_REVIEW_UX_PLAN.md`
- `docs/FLAGFIX_BATCH_02_TITLE_METADATA_INTEGRITY_PLAN.md`
- `docs/FLAGFIX_BATCH_03_PALI_PROTECTION_PLAN.md`
- `docs/FLAGFIX_BATCH_04_MEDIA_ASSETS_PLAN.md`
- `docs/FLAGFIX_BATCH_05_ARCHITECTURE_STUDY_ORDER_PLAN.md`

### Production / Build Guardrails

- `docs/FLAGFIX_023_PRODUCTION_BUILD_INPUT_CONTRACT.md`

### Media / Shortcode Preservation

- `docs/FLAGFIX_MEDIA_SHORTCODE_PRESERVATION_PLAN.md`
- Legacy media shortcodes are preserved as explicit `axis-media-evidence` blocks.
- Raw corrupted shortcode evidence is preserved in HTML comments for audit.
- Shortcode garbage is no longer shown as editorial body text.

### Print Review UX

Implemented in CSS and deployed through Cloudflare:
- A4 print review layout rebalance.
- Compact print review banner.
- Previous/next transmission map hidden in printed review copies.
- Page/browser headers remain useful for traceability.
- PD#PN and page numbering remain essential for physical review workflows.

### Title / Metadata Review

- `docs/FLAGFIX_020_TITLE_COMPARISON_MATRIX.md`
- `review/title-matrix/flagfix_020_title_comparison_matrix.csv`
- `docs/FLAGFIX_021_MISSING_DATE_METADATA_REVIEW.md`

Status:
- Human review matrix exists.
- No automatic title corrections implemented.
- Date wording and blue didactic styling should be preserved unless reviewed.
- Missing/ambiguous dates require conservative display treatment only; do not invent dates.

## Current Open Issue Groups

### Batch 02 — Title and Metadata Integrity

- FlagFix 011
- FlagFix 012
- FlagFix 013
- FlagFix 020
- FlagFix 021

Recommended next action:
Curate a small pilot set in the title comparison matrix before any title correction code.

### Batch 03 — Pāli Protection

- FlagFix 002
- FlagFix 003
- FlagFix 004
- FlagFix 007
- FlagFix 009

Recommended next action:
Design source-bound protection rules before touching translation or renderer behavior.

### Batch 04 — Media and Assets

- FlagFix 005
- FlagFix 010
- FlagFix 014
- FlagFix 015

Recommended next action:
Inventory media/image/video cases before applying broad rendering fixes.

### Batch 05 — Architecture and Study Order

- FlagFix 000
- FlagFix 001
- FlagFix 008
- FlagFix 008b

Recommended next action:
Keep architecture work planning-only until production build input provenance is resolved.

## Operational Guardrail

`axis-niddhi-production` is currently a static publication repository.

Do not run full rebuilds from this clone unless:
1. approved `09-csl` provenance is present;
2. the build input contract is satisfied;
3. output diffs are expected and reviewed;
4. Cloudflare deployment impact is intentional.

## Suggested Next Step

Create a small branch protection / main safety guardrail document before enabling GitHub branch protection directly.

## Batch 02 Update — 2026-05-03

Closed after policy documentation:

- FlagFix 011 — Title punctuation semantic preservation
  - PR #51
  - Artifact: `docs/FLAGFIX_011_TITLE_PUNCTUATION_PRESERVATION_POLICY.md`

- FlagFix 012 — Slug/title divergence pale blue dot
  - PR #52
  - Artifact: `docs/FLAGFIX_012_SLUG_TITLE_DIVERGENCE_POLICY.md`

- FlagFix 013 — PT title capitalization policy
  - PR #50
  - Artifact: `docs/FLAGFIX_013_PT_TITLE_CAPITALIZATION_POLICY.md`

Remaining Batch 02 open work:

- FlagFix 020 — Title comparison human review matrix
- FlagFix 021 — Missing date metadata review box

Guardrail:
No automatic title, slug, route, metadata, CSL, or renderer corrections are authorized until the FlagFix 020 pilot matrix is curated and reviewed.

## Batch 02 Final Policy Checkpoint — 2026-05-03

Closed after policy documentation:

- FlagFix 011 — Title punctuation semantic preservation
  - PR #51
  - Artifact: `docs/FLAGFIX_011_TITLE_PUNCTUATION_PRESERVATION_POLICY.md`

- FlagFix 012 — Slug/title divergence pale blue dot
  - PR #52
  - Artifact: `docs/FLAGFIX_012_SLUG_TITLE_DIVERGENCE_POLICY.md`

- FlagFix 013 — PT title capitalization policy
  - PR #50
  - Artifact: `docs/FLAGFIX_013_PT_TITLE_CAPITALIZATION_POLICY.md`

- FlagFix 021 — Missing date metadata review box
  - PR #54
  - Artifact: `docs/FLAGFIX_021_MISSING_DATE_REVIEW_BOX_POLICY.md`

Remaining Batch 02 active item:

- FlagFix 020 — Title comparison human review matrix
  - Artifact already seeded:
    - `docs/FLAGFIX_020_TITLE_COMPARISON_MATRIX.md`
    - `review/title-matrix/flagfix_020_title_comparison_matrix.csv`

Guardrail:
Batch 02 implementation remains blocked until the FlagFix 020 pilot matrix is curated and reviewed.

No automatic title, slug, route, date, metadata, CSL, renderer, or URL correction is authorized by the closed policy issues alone.

## Batch 02 Closed — 2026-05-03

Batch 02 — Title and Metadata Integrity is now closed for policy/review-scaffold scope.

Closed items:

- FlagFix 011 — Title punctuation semantic preservation
- FlagFix 012 — Slug/title divergence pale blue dot
- FlagFix 013 — PT title capitalization policy
- FlagFix 020 — Title comparison human review matrix
- FlagFix 021 — Missing date metadata review box

Final Batch 02 artifacts:

- `docs/FLAGFIX_011_TITLE_PUNCTUATION_PRESERVATION_POLICY.md`
- `docs/FLAGFIX_012_SLUG_TITLE_DIVERGENCE_POLICY.md`
- `docs/FLAGFIX_013_PT_TITLE_CAPITALIZATION_POLICY.md`
- `docs/FLAGFIX_020_TITLE_COMPARISON_MATRIX.md`
- `review/title-matrix/flagfix_020_title_comparison_matrix.csv`
- `docs/FLAGFIX_021_MISSING_DATE_REVIEW_BOX_POLICY.md`

Guardrail:

No automatic title, slug, route, metadata, CSL, renderer, or static-site corrections are authorized from Batch 02 alone.

Any future implementation must start from a new issue/branch after a larger human-reviewed pilot matrix is approved.

## Batch 03 Start — 2026-05-03

Batch 03 — Pāli Protection is now the next active FlagFix planning group.

Open items:

- FlagFix 002 — Pāli term color audio taxonomy
- FlagFix 003 — Pāli grammar diacritics orthography
- FlagFix 004 — Protect Pāli quotes from translation
- FlagFix 007 — Title translation glossary protection
- FlagFix 009 — Title translation glossary protection Micchā Diṭṭhi

Guardrail:

No translation, glossary, renderer, CSL, HTML, or static-site output changes are authorized by this checkpoint.

Batch 03 must begin with source-bound policy/review documents only.

Recommended order:

1. document protected Pāli term taxonomy;
2. document diacritic/orthography preservation rules;
3. document quote-level protection rules;
4. document title/glossary protection rules;
5. only then consider implementation issues.

## Batch 03 Closed — 2026-05-03

Batch 03 — Pāli Protection is now closed for policy/review-scaffold scope.

Closed items:

- FlagFix 002 — Pāli term color audio taxonomy
- FlagFix 003 — Pāli grammar diacritics orthography
- FlagFix 004 — Protect Pāli quotes from translation
- FlagFix 007 — Title translation glossary protection
- FlagFix 009 — Title translation glossary protection Micchā Diṭṭhi

Final Batch 03 artifacts:

- `docs/FLAGFIX_002_PALI_TERM_COLOR_AUDIO_TAXONOMY_POLICY.md`
- `docs/FLAGFIX_003_PALI_GRAMMAR_DIACRITICS_ORTHOGRAPHY_POLICY.md`
- `docs/FLAGFIX_004_PALI_QUOTE_PROTECTION_POLICY.md`
- `docs/FLAGFIX_007_TITLE_TRANSLATION_GLOSSARY_PROTECTION_POLICY.md`
- `docs/FLAGFIX_009_MICCHA_DITTHI_GLOSSARY_PROTECTION_POLICY.md`

Guardrail:

No automatic Pāli, Dhamma term, quote, title, glossary, translation, CSL, renderer, HTML, CSS, JavaScript, or static-site output changes are authorized from Batch 03 alone.

Any future implementation must start from a new issue/branch after source-bound human review rules are approved.

## Batch 04 Start — 2026-05-03

Batch 04 — Media and Assets is now the next active FlagFix planning group.

Open items:

- FlagFix 005 — Translatable image flowchart assets
- FlagFix 010 — Audio offline placeholder language and external resolution
- FlagFix 014 — Image rendering size centering and zoom
- FlagFix 015 — YouTube print marker missing for embed variants

Guardrail:

No renderer, CSL, HTML, CSS, JavaScript, asset map, image, audio, YouTube, or static-site output changes are authorized by this checkpoint.

Batch 04 must begin with inventory and source-bound media review documents only.

Recommended order:

1. document translatable image/flowchart asset policy;
2. document audio offline/external resolution policy;
3. document image rendering and sizing review policy;
4. document YouTube/embed print marker policy;
5. only then consider implementation issues.

## Batch 04 Closed — 2026-05-03

Batch 04 — Media and Assets is now closed for policy/review-scaffold scope.

Closed items:

- FlagFix 005 — Translatable image flowchart assets
- FlagFix 010 — Audio offline placeholder language and external resolution
- FlagFix 014 — Image rendering size centering and zoom
- FlagFix 015 — YouTube print marker missing for embed variants

Final Batch 04 artifacts:

- `docs/FLAGFIX_005_TRANSLATABLE_IMAGE_FLOWCHART_ASSETS_POLICY.md`
- `docs/FLAGFIX_010_AUDIO_OFFLINE_PLACEHOLDER_POLICY.md`
- `docs/FLAGFIX_014_IMAGE_RENDERING_SIZE_CENTERING_ZOOM_POLICY.md`
- `docs/FLAGFIX_015_YOUTUBE_PRINT_MARKER_POLICY.md`

Guardrail:

No renderer, CSL, HTML, CSS, JavaScript, asset map, image, audio, YouTube, print, OCR, translation, external URL, or static-site output changes are authorized from Batch 04 alone.

Any future media implementation must start from a new issue/branch after source-bound media review is approved.
