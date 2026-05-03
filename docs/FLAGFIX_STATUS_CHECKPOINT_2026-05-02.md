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
