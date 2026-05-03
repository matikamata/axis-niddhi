# FlagFix 003 — Pāli Grammar, Diacritics, and Orthography Policy

## Status

Planning / review policy only.

No translation, glossary, renderer, CSL, HTML, CSS, JavaScript, or static-site output changes are authorized by this document.

## Problem

Pāli terms in AXIS-NIDDHI must preserve doctrinal meaning, grammatical form, and orthographic integrity.

Risks include:

- losing diacritics such as ā, ī, ū, ṅ, ñ, ṭ, ḍ, ṇ, ḷ, ṃ;
- replacing Pāli terms with approximate Portuguese or English translations;
- normalizing terms mechanically across contexts;
- changing singular/plural or grammatical forms;
- damaging compounds or hyphenated forms;
- confusing related terms with different doctrinal meanings;
- flattening source-specific spellings without human review.

## Principle

Pāli text is source-bound evidence.

A Pāli term or phrase must not be treated as ordinary translatable prose unless explicitly approved by human review.

## Protected orthographic forms

The following must be preserved when present in source or approved canonical text:

- macrons: `ā`, `ī`, `ū`;
- retroflex consonants: `ṭ`, `ḍ`, `ṇ`, `ḷ`;
- nasal and palatal signs: `ṅ`, `ñ`, `ṃ`;
- capitalization when it carries title, quote, or source-context significance;
- compounds and phrase boundaries;
- source quotation wording.

## Examples of protected terms

Examples include, but are not limited to:

- `anicca`
- `dukkha`
- `anatta`
- `Nibbāna`
- `Tilakkhana`
- `Paṭicca Samuppāda`
- `Micchā Diṭṭhi`
- `Sammā Diṭṭhi`
- `kamma`
- `kamma patha`
- `gati`
- `āsava`
- `saṅkhāra`
- `viññāṇa`
- `paññā`
- `sīla`
- `samādhi`
- `Saṅgha`

## Forbidden automatic actions

Do not automatically:

1. remove Pāli diacritics;
2. add missing diacritics without source confirmation;
3. translate protected Pāli terms mechanically;
4. normalize spelling across the corpus without review;
5. alter capitalization in doctrinal terms;
6. rewrite compounds or grammatical endings;
7. replace source wording with glossary-preferred wording;
8. infer that two similar Pāli forms are equivalent.

## Allowed review actions

Allowed actions are limited to:

1. identifying Pāli terms and phrases;
2. recording source spelling;
3. comparing AXIS spelling against source spelling;
4. marking suspected orthographic drift;
5. adding human reviewer notes;
6. proposing downstream implementation issues after review.

## Human review requirement

Any correction to Pāli orthography must include:

- PD#PN;
- source URL or canonical source reference;
- current AXIS text;
- proposed corrected text;
- reason for correction;
- reviewer approval.

## Relationship to other FlagFix items

This policy supports:

- FlagFix 002 — Pāli term color/audio taxonomy;
- FlagFix 004 — Protect Pāli quotes from translation;
- FlagFix 007 — Title translation glossary protection;
- FlagFix 009 — Micchā Diṭṭhi glossary protection.

## Acceptance criteria

- Policy document exists.
- Pāli diacritic and orthography preservation rules are documented.
- No production text is changed.
- No renderer, CSL, glossary, translation, HTML, or static-site output is changed.
- Future implementation remains blocked pending human review.
