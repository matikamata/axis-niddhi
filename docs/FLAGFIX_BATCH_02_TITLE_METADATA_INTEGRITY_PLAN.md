# FlagFix Batch 02 — Title and Metadata Integrity Plan

## Status

Planning-only document.

No pipeline/build/static output changes are authorized by this document.

## Scope

This batch groups title and metadata integrity issues found during print-review and live-site review.

Related GitHub Issues:

- #30 — FlagFix 020 TITLE COMPARISON HUMAN REVIEW MATRIX
- #31 — FlagFix 021 MISSING DATE METADATA REVIEW BOX
- #23 — FlagFix 013 PT TITLE CAPITALIZATION POLICY
- #22 — FlagFix 012 SLUG TITLE DIVERGENCE PALE BLUE DOT
- #21 — FlagFix 011 TITLE PUNCTUATION SEMANTIC PRESERVATION
- #16 — FlagFix 007 TITLE TRANSLATION GLOSSARY PROTECTION
- #19 — FlagFix 009 TITLE TRANSLATION GLOSSARY PROTECTION MICCHA DITTHI

## Core Problem

AXIS-NIDDHI currently preserves and publishes the corpus successfully, but some titles and metadata fields show evidence of transformation drift:

1. punctuation loss,
2. slug/title mismatch,
3. glossary-protected term drift,
4. missing macrons or incorrect Pāli spelling,
5. inconsistent Portuguese capitalization,
6. missing publication/revision dates,
7. occasional fallback title generation that may not preserve original semantic force.

These issues do not invalidate the preservation layer because the source reference remains PureDhamma.net.

However, they are important for long-term trust, print review, search, study order, and future human authentication.

## Principle

Titles are not decoration.

A title is part of the transmission map.

Therefore, title handling must preserve:

- original English title,
- original punctuation,
- original semantic question/exclamation/dash structure,
- canonical PureDhamma.net URL,
- AXIS PD#PN,
- slug,
- translated pt-BR title,
- glossary-protected doctrinal terms,
- Pāli diacritics,
- human-review status.

## First Deliverable

Create a human-review matrix for titles.

Recommended columns:

| Field | Description |
|---|---|
| PD#PN | AXIS canonical identifier |
| PureDhamma Original URL | Full original URL, not shortened |
| PureDhamma Slug | Original slug |
| PureDhamma Title | Original title exactly as source |
| AXIS en-US URL | Full AXIS URL |
| AXIS en-US Title | Current English title in AXIS |
| AXIS pt-BR Title | Current Portuguese title in AXIS |
| Title Status | OK / Needs Review / Broken / Unknown |
| Problem Type | punctuation / slug-title divergence / glossary / macron / capitalization / missing date |
| Suggested pt-BR Title | Human reviewer suggestion |
| Reviewer Notes | Free notes |
| Reviewed By | Human reviewer name/initials |
| Review Date | ISO date |

## Suggested Execution Strategy

Phase 1 — Inventory only

- Extract all current AXIS page titles from `pipeline/13-static-site/pages/*/index.html`.
- Extract URLs and PD#PN.
- Compare against known source metadata if available.
- Do not auto-fix titles.

Phase 2 — Human matrix

- Produce CSV/ODS for reviewer.
- Mark suspicious titles.
- Prioritize titles already reported in FlagFix issues.

Phase 3 — Policy

Define title policies before patching:

- Preserve original English punctuation exactly where possible.
- Do not derive title from slug when source title exists.
- Do not allow LLM fallback to silently invent title variants.
- Preserve protected glossary terms before translation.
- Preserve Pāli macrons and diacritics.
- Use pt-BR title capitalization policy consistently.

Phase 4 — Pipeline hardening

Only after review matrix exists:

- Update title extraction logic.
- Update title translation guard.
- Add title regression audit.
- Add report that blocks or warns on semantic punctuation loss.

## Current Known Examples

### FlagFix 011

Original:

`Solution to a Wandering Mind – Abandon Everything?`

AXIS en-US currently lost punctuation:

`Solution To A Wandering Mind Abandon Everything`

Risk:

The question mark and dash change the semantic force of the title.

### FlagFix 012

Original title:

`The Pale Blue Dot……..`

Slug differs from title.

Risk:

Pipeline may incorrectly trust slug-derived title.

### FlagFix 020

Original:

`Details of Kamma – Intention, Who Is Affected, Kamma Patha`

AXIS title became visually and semantically degraded.

Risk:

Title review must be human-visible and matrix-driven.

### FlagFix 007 / 009

Pāli / glossary title terms such as `Nibbāna`, `Micchā Diṭṭhi`, `Kamma`, etc. must not drift due to fallback translation.

## Non-Goals

This batch does not solve:

- full canonical study order,
- image translation,
- Pāli grammar taxonomy,
- audio/media handling,
- full rebuild contract.

Those are tracked in other FlagFix batches.

## Safety Rules

- Do not run full build from `axis-niddhi-production` unless `09-csl` provenance is explicitly approved.
- Do not use `git add .`.
- Do not patch titles directly until the matrix exists.
- Do not shorten URLs.
- Do not remove PureDhamma.net traceability.
- Do not “beautify” away source punctuation.

## Recommended Next Technical Artifact

A script or notebook that produces:

`metadata/review/title_review_matrix.csv`

or, if metadata output is not yet approved:

`review/title_review_matrix_draft.csv`

The first version should be audit-only and must not modify site files.
