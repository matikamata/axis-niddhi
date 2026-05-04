# FlagFix 004 — Protect Pāli Quotes From Translation Policy

## Status

Planning / review policy only.

No translation, glossary, renderer, CSL, HTML, CSS, JavaScript, or static-site output changes are authorized by this document.

## Problem

Pāli quotes and canonical doctrinal passages must not be translated, normalized, paraphrased, reformatted, or partially rewritten by automated translation or rendering steps.

Risks include:

- translating Pāli quote text into English or Portuguese;
- altering diacritics inside quoted Pāli passages;
- changing punctuation, line breaks, verse structure, or emphasis;
- mixing translated commentary with protected source quotation;
- treating quoted Pāli as ordinary prose;
- losing the boundary between quote, translation, explanation, and citation;
- corrupting source-bound evidence during future multilingual expansion.

## Principle

A Pāli quote is source-bound evidence.

It must be preserved as quoted material unless a human reviewer explicitly authorizes a separate translation or explanatory rendering.

## Protected quote categories

The following should be treated as protected:

- standalone Pāli verses;
- inline Pāli quotations;
- canonical phrases cited as source evidence;
- Pāli passages followed by English or Portuguese explanation;
- Pāli passages with citation markers;
- Pāli terms embedded in doctrinal comparisons;
- historical or scriptural quotations where wording is doctrinally significant.

## Quote boundary rule

Future tooling must distinguish between:

1. the original Pāli quote;
2. a human-approved translation;
3. explanatory commentary;
4. source citation or attribution.

Automated tooling must not collapse these layers.

## Translation rule

A Pāli quote must not be translated automatically.

If a translation is needed, it must be stored or displayed as a separate human-reviewed translation, not as a replacement for the original quote.

## Orthography rule

Inside protected Pāli quotes, preserve:

- diacritics;
- capitalization;
- punctuation;
- line breaks;
- verse segmentation;
- compounds;
- spacing where meaningful;
- source-specific spelling unless reviewed.

## Renderer rule

A renderer may visually mark a protected quote in the future, but must not alter quote text.

Any future visual treatment must preserve the original quote and must be reviewed separately.

## Review rule

If a Pāli quote appears corrupted, ambiguous, or inconsistently formatted:

- do not auto-fix it;
- add it to a review matrix;
- preserve the original evidence;
- compare against the source;
- require human approval before remediation.

## Forbidden actions

The following are forbidden without explicit human review:

- replacing a Pāli quote with a translation;
- removing diacritics;
- normalizing spelling mechanically;
- merging quote and explanation;
- changing quote punctuation automatically;
- changing quote line breaks automatically;
- applying bulk corrections to all quote-like passages.

## Allowed planning actions

Allowed in this FlagFix scope:

- document quote protection rules;
- identify quote protection risks;
- collect examples for human review;
- propose future quote boundary metadata;
- propose future validation checks.

Forbidden in this FlagFix scope:

- modifying CSL content;
- modifying translated content;
- modifying renderer behavior;
- modifying static-site output;
- modifying glossary behavior;
- running bulk quote correction.

## Acceptance Criteria

- Policy document exists.
- Pāli quotes are documented as protected source-bound evidence.
- No production content is changed.
- No renderer, CSL, glossary, translation, HTML, CSS, JavaScript, or static-site output is changed.
- Future implementation remains blocked pending human review.
