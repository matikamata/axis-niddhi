# FlagFix 007 — Title Translation Glossary Protection Policy

## Status

Planning / review policy only.

No translation, glossary, renderer, CSL, HTML, CSS, JavaScript, or static-site output changes are authorized by this document.

## Problem

AXIS-NIDDHI titles may contain doctrinal terms that must not be mechanically translated, normalized, simplified, or replaced by approximate Portuguese/English equivalents.

Title translation is especially risky because titles are:

- highly visible in archive/navigation/search interfaces;
- reused in pathway navigation and related-page contexts;
- often semantically compressed;
- likely to contain key doctrinal terms;
- vulnerable to machine translation over-normalization;
- part of long-term citation and review workflows.

## Principle

A doctrinal title is not ordinary UI copy.

If a title contains protected Dhamma/Pāli terminology, the title must be reviewed against a controlled glossary or source-bound human decision before any correction is applied.

## Protected title content

The following must be treated as protected when appearing in titles:

- Pāli terms;
- Sinhala/Pāli doctrinal terms preserved by PureDhamma usage;
- terms with established PureDhamma-specific translations;
- terms with no exact English or Portuguese equivalent;
- names of suttā, people, realms, concepts, lists, paths, stages, or doctrinal categories;
- terms already flagged by Batch 03 Pāli protection policies.

## Examples of protected or review-sensitive terms

Examples include, but are not limited to:

- `anicca`
- `dukkha`
- `anatta`
- `Nibbāna`
- `Paṭicca Samuppāda`
- `Tilakkhana`
- `Ariya`
- `Ariya Magga`
- `Sotāpanna`
- `Sakadāgāmi`
- `Anāgāmi`
- `Arahant`
- `kamma`
- `kamma patha`
- `akusala`
- `kusala`
- `saṅkhāra`
- `viññāṇa`
- `gati`
- `āsava`
- `taṇhā`
- `avijjā`
- `micchā diṭṭhi`
- `sammā diṭṭhi`

## Required review behavior

Before changing a title that contains protected terminology, reviewers must record:

1. PD#PN;
2. original PureDhamma title;
3. original slug/URL;
4. current AXIS en-US title;
5. current AXIS pt-BR title;
6. protected term(s);
7. glossary decision or reviewer note;
8. final approved title decision.

The FlagFix 020 title comparison matrix is the preferred review artifact.

## Forbidden automatic actions

Do not automatically:

- translate protected Pāli terms;
- replace Pāli terms with approximate Portuguese words;
- remove diacritics;
- normalize capitalization across protected terms;
- rewrite title punctuation if it affects doctrinal grouping;
- infer title meaning from slug alone;
- infer glossary decisions from frequency alone;
- apply bulk title changes from a translation engine.

## Allowed planning actions

Allowed:

- identify titles containing protected terms;
- add rows to the FlagFix 020 matrix;
- propose glossary candidate entries;
- document reviewer decisions;
- open downstream implementation issues after review.

## Relationship to other FlagFix items

This policy depends on:

- FlagFix 002 — Pāli term color/audio taxonomy;
- FlagFix 003 — Pāli grammar, diacritics, and orthography;
- FlagFix 004 — Protect Pāli quotes from translation;
- FlagFix 020 — Title comparison human review matrix.

It informs:

- FlagFix 009 — Title translation glossary protection for Micchā Diṭṭhi;
- future title correction implementation issues.

## Acceptance criteria

- Policy document exists.
- Title glossary protection is defined as human-review-first.
- Protected title terms are listed as examples.
- No title, glossary, renderer, CSL, HTML, CSS, JavaScript, or static-site output is changed.
