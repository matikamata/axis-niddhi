# AXIS-NIDDHI — FLAGFIX Batch 03 Pāli Protection Audit

**Date:** 2026-05-04  
**Status:** Audit-only / Human review pending  
**Scope:** Batch 03 — Pāli Protection  
**Implementation:** Not authorized by this document

---

## Purpose

This document records a small read-only audit for Batch 03 — Pāli Protection.

The goal is to capture representative evidence from the current static-site output before any renderer, glossary, translation, CSS, JavaScript, metadata, or pipeline changes are considered.

No implementation is authorized by this audit.

---

## Current Batch 03 Posture

Batch 03 remains in `inventory / review` mode.

Current state by FlagFix:

- `FLAGFIX_002` — partially operational in the current `main` build:
  - glossary-only terms and audio-enabled terms already have distinct CSS/JS behavior;
  - print review also preserves the glossary/audio distinction.
- `FLAGFIX_003` — policy/inventory pending:
  - orthography, diacritics, compounds, and mixed forms still need deliberate inventory and review.
- `FLAGFIX_004` — policy/inventory pending:
  - preserved Pāli quote samples exist, but no implementation-safe protection layer is authorized yet.
- `FLAGFIX_009` — policy/inventory pending:
  - `Micchā Diṭṭhi` remains a protected doctrinal term with a visible title/body divergence sample.
- `FLAGFIX_007` — already integrated with Batch 02 / `FLAGFIX_020` for title workflow and not treated as a separate Batch 03 implementation track here.

---

## Audit Artifact

CSV audit artifact:

- `review/pali-protection/flagfix_batch03_pali_protection_audit.csv`

The CSV is a pilot evidence set. It does not attempt corpus-wide exhaustiveness.

It includes representative rows for:

- glossary-only / color-only terms;
- runtime audio candidates;
- preserved Pāli quotes;
- preserved diacritics;
- simplified or lost diacritics;
- `Miccha` / `Micchā Diṭṭhi` title/body divergence;
- at least one sample aligned to each of `FLAGFIX_002`, `FLAGFIX_003`, `FLAGFIX_004`, and `FLAGFIX_009`.

All rows are marked:

```text
decision=review_pending
```

---

## Key Findings

### 1. FLAGFIX_002 already has partial operational behavior

The current build already distinguishes glossary-only terms from audio-enabled terms.

Observed evidence includes:

- `.term-highlight` glossary styling;
- `.term-highlight.has-audio` runtime audio styling;
- print legend classes for glossary and audio distinction;
- `initPronunciation()` logic that applies `.has-audio` based on `pronunciation_manifest.json`.

This means Batch 03 is not purely hypothetical; some protection-adjacent behavior is already live.

### 2. Orthography remains mixed and review-sensitive

The audit found preserved forms such as:

- `Paṭicca Samuppāda`
- `Nibbāna`
- `micchā diṭṭhi`

It also found simplified or mixed forms such as:

- `Miccha Ditthi`
- `ārammana`
- explanatory `nivana` near preserved `Nibbāna`

This supports `FLAGFIX_003` as an inventory-first issue.

### 3. Pāli quotes are visibly preserved but not yet governed by an implementation layer

Representative inline quote evidence exists, such as:

- `cetanāhaṁ, bhikkhave, kammaṁ vadāmi.`

That is good evidence for `FLAGFIX_004`, but this audit does not establish a deterministic quote-protection system.

### 4. Micchā Diṭṭhi remains a clear protected-term risk

The strongest current `FLAGFIX_009` evidence remains:

- simplified EN title: `Miccha Ditthi Simpler Analysis`
- preserved body term: `micchā diṭṭhi`

This is exactly the kind of mismatch that must remain under human review and must not be patched mechanically.

---

## Recommended Next Steps

Safe next steps from this audit:

1. expand the CSV with more read-only evidence rows;
2. open sub-issues or follow-up audit artifacts only if a narrower review track is needed;
3. consider a future implementation branch only after review decisions are recorded.

Recommended minimum future direction:

- keep `FLAGFIX_002` in observation mode unless a concrete regression appears;
- prioritize further inventory for `FLAGFIX_003`, `FLAGFIX_004`, and `FLAGFIX_009`;
- continue treating `FLAGFIX_007` title-protection concerns through Batch 02 / `FLAGFIX_020`.

---

## Guardrails

This audit does not authorize:

- CSS changes;
- JavaScript changes;
- renderer changes;
- CSL changes;
- glossary implementation changes;
- metadata changes;
- template changes;
- pipeline changes;
- static-site output changes;
- rebuild/publication;
- title correction;
- glossary correction;
- Pāli normalization.

---

## Next Review Gate

Before any future functional patch:

1. expand or validate the inventory with human review;
2. decide which risks are display-only versus source-integrity risks;
3. identify exact candidate files for any proposed implementation;
4. separate Batch 03 policy work from Batch 02 title-review work where needed;
5. require a dedicated issue, branch, and PR for any implementation.
