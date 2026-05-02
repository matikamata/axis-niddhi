# FlagFix Status Checkpoint — 2026-05-02

## Current state

- Production branch: main
- Repository status: clean
- Batch plans merged:
  - Batch 01 — Print Review UX
  - Batch 02 — Title and Metadata Integrity
  - Batch 03 — Pāli Protection
  - Batch 04 — Media and Assets
  - Batch 05 — Architecture and Study Order
- Production build input contract documented.
- Media shortcode preservation layer merged.
- FlagFix issue index mapped to batch plans.

## Open FlagFix issues

Remaining open issues are intentionally preserved because they require either:
- human review,
- corpus-wide audit,
- source/title comparison,
- canonical policy decision,
- or future architectural work.

## Recommended next implementation target

Start with:

- #30 — FlagFix 020 TITLE COMPARISON HUMAN REVIEW MATRIX

Reason:
This creates the review matrix needed to resolve or guide:
- #21 title punctuation semantic preservation
- #22 slug/title divergence
- #23 PT title capitalization policy
- #31 missing date metadata review box

## Do not run full production rebuilds

axis-niddhi-production remains a static publication repository unless an approved 09-csl source contract is explicitly present.
