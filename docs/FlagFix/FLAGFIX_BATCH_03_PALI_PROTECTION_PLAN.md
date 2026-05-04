# FlagFix Batch 03 — Pāli Protection Plan

Status: planning-only  
Scope: Pāli, glossary protection, diacritics, protected terms, title/source integrity  
Related issues: #11, #12, #13, #16, #19  
Do not implement code from this document without a separate scoped branch.

## Purpose

This batch exists to prevent AXIS-NIDDHI from accidentally damaging Pāli terms, doctrinal terminology, source quotations, title semantics, or protected glossary expressions during extraction, preprocessing, translation, rendering, or print review.

The core rule is simple:

> Pāli and protected doctrinal terminology must be preserved unless a human reviewer explicitly approves a transformation.

## Related FlagFix Issues

- #11 — FlagFix 002 Pāli term color/audio taxonomy
- #12 — FlagFix 003 Pāli grammar, diacritics, orthography
- #13 — FlagFix 004 Protect Pāli quotes from translation
- #16 — FlagFix 007 Title translation glossary protection
- #19 — FlagFix 009 Title translation glossary protection: Miccha Ditthi

## Current Known Problems

### 1. Pāli terms may be visually inconsistent

Current screen/print behavior distinguishes:

- glossary-only terms
- audio-linked terms
- undetected Pāli terms
- corrupted or partially transformed terms

However, not all Pāli terms are guaranteed to be in the glossary yet. Some are highlighted, some are audio-linked, and some remain plain text.

This is expected during the review phase, but must be tracked explicitly.

### 2. Audio-linked terms and glossary-only terms can collapse visually in print

The site uses different visual treatment for protected glossary terms and audio-enabled terms. In print, these distinctions must remain visible because reviewers use them cognitively.

Glossary-only terms should remain visually distinct from audio-linked terms.

### 3. DeepL or another translation stage may translate Pāli quotations

This is a high-risk content issue.

Pāli quotations, sutta names, canonical phrases, and preserved source fragments must not be sent through normal translation unprotected.

Possible future strategy:

- detect Pāli quote blocks before translation
- wrap them with `translate="no"`
- preserve original text in CSL
- record protection metadata
- audit for mixed-language corruption after translation

### 4. Title translation may lose protected terms

Examples already observed:

- Nibbāna without macron
- Micchā Diṭṭhi split or partially translated
- title fallback generated without glossary enforcement
- title punctuation removed, changing semantic meaning

Titles are high-visibility metadata and should be treated as controlled fields, not casual prose.

### 5. Orthography and grammar require human review

Questions such as:

- Anattā vs Anatta
- Apāya vs Apāyā vs Apayas
- singular/plural conventions
- Sanskritized vs Pāli spelling
- English legacy spellings used by PureDhamma.net

must not be guessed by an LLM without review.

## Proposed Future Work

### Phase 1 — Inventory

Generate a report of all detected Pāli/protected terms across:

- titles
- headings
- body text
- blockquotes
- glossary highlights
- audio-linked spans
- source URLs
- shortcode/evidence blocks

The report should include:

- PD#PN
- language
- URL
- term
- detected class/status
- whether audio exists
- whether glossary entry exists
- whether diacritics are present
- surrounding snippet

### Phase 2 — Translation Protection

Before DeepL or any translation engine touches content:

- protect known Pāli terms
- protect canonical quote blocks
- protect sutta references
- protect glossary phrases
- protect doctrinal compounds
- preserve source punctuation

Preferred mechanism:

- HTML spans/classes
- `translate="no"`
- deterministic placeholders
- restoration pass after translation
- audit pass comparing pre/post protected tokens

### Phase 3 — Title Protection

Create a title-specific validation layer.

The title layer should compare:

- PureDhamma.net original title
- extracted EN title
- canonical CSL title
- generated pt-BR title
- final rendered title
- slug

Flag title changes that alter:

- punctuation
- question marks
- em dashes
- ellipses
- capitalization
- protected terms
- diacritics
- doctrinal compounds

### Phase 4 — Human Review Matrix

Create a CSV/ODS title and Pāli review matrix with:

- PD#PN
- PureDhamma URL
- AXIS URL
- original title
- AXIS en-US title
- AXIS pt-BR title
- protected terms found
- suspected issue
- suggested correction
- reviewer decision
- review date
- reviewer notes

### Phase 5 — Print and Review UX

In printed/PDF copies:

- glossary-only terms should remain orange/dotted
- audio-linked terms should remain red/dashed
- protected Pāli quotes should be visibly preserved
- review banners should explain that terminology is under staged review
- no didactic PureDhamma color should be flattened into generic link styling

## Non-Goals

This batch should not:

- mass-correct Pāli spelling automatically
- override Prof. Lal's source conventions
- normalize all terms without review
- rewrite doctrinal language based on LLM preference
- hide uncertainty from future reviewers

## Acceptance Criteria

This batch is ready for implementation only when:

- there is a clear inventory strategy
- protected terms can be detected deterministically
- DeepL protection/restoration can be tested on a small sample
- title comparison can identify punctuation/diacritic drift
- print CSS preserves glossary/audio distinction
- human reviewers can override or approve corrections

## Recommended First Implementation Branches

Suggested future branches:

- `flagfix-batch03-pali-inventory`
- `flagfix-batch03-title-protection-audit`
- `flagfix-batch03-translation-no-translate-guard`
- `flagfix-batch03-print-term-distinction`

## Guiding Principle

AXIS-NIDDHI may translate explanatory language, but it must not casually mutate the doctrinal atoms of the transmission.

When uncertain, preserve, mark, and ask for review.
