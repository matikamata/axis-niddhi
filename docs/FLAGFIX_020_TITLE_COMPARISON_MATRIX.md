# FlagFix 020 — Title Comparison Human Review Matrix

## Purpose

Create a human-reviewable title comparison matrix before changing any AXIS-NIDDHI titles.

This issue must not directly rewrite titles. Its role is to provide an auditable editorial workflow for comparing:

- PureDhamma.net original title
- PureDhamma.net slug
- PureDhamma.net URL
- AXIS en-US title
- AXIS pt-BR title
- AXIS URL
- issue type
- human reviewer note
- final decision

## Review artifact

Primary matrix:

```text
review/title-matrix/flagfix_020_title_comparison_matrix.csv
````

## Initial examples

The first two seed rows are:

* `TL.EE.008` — title punctuation / semantic preservation / translation risk.
* `TL.EE.011` — missing or ambiguous date metadata context.

## Policy

No title should be corrected automatically from this issue alone.

Allowed actions:

1. collect comparison data;
2. classify title problems;
3. identify source/title/slug divergences;
4. add human reviewer notes;
5. propose downstream correction issues or implementation branches.

Forbidden actions:

1. mass rewrite titles without review;
2. translate protected doctrinal terms mechanically;
3. infer missing publication/revision metadata as fact;
4. modify canonical CSL/title metadata without explicit approval.

## Suggested issue types

* `title_semantic_punctuation_translation`
* `slug_title_divergence`
* `pt_capitalization_policy`
* `protected_pali_term`
* `missing_or_ambiguous_date_metadata`
* `source_title_changed_upstream`
* `needs_human_doctrinal_review`

## Downstream issues informed by this matrix

* FlagFix 011 — Title punctuation semantic preservation
* FlagFix 012 — Slug/title divergence
* FlagFix 013 — PT title capitalization policy
* FlagFix 021 — Missing date metadata review box

## Acceptance criteria

* Matrix file exists.
* Matrix has canonical columns.
* At least the known examples are seeded.
* No production title text is modified.
* No build is run.
