# FlagFix 013 — PT Title Capitalization Policy

## Status

Planning / review policy only.

No automatic title changes are authorized by this document.

## Problem

Some Brazilian Portuguese post titles appear with inconsistent capitalization when compared with the English titles and with the desired AXIS-NIDDHI publication quality.

Example observed:

- EN: `Right Speech`
- PT: `Discurso correto`

The lowercase second word may be linguistically acceptable in normal Portuguese sentence-style capitalization, but visually it can make the publication look less polished or inconsistent in the archive/listing interface.

## Core Question

Should AXIS-NIDDHI use:

1. Portuguese sentence-style capitalization  
   Example: `Discurso correto`

2. Portuguese title-style capitalization for site titles  
   Example: `Discurso Correto`

3. A hybrid policy preserving doctrinal terms, Pāli terms, proper nouns, and established PureDhamma expressions exactly as reviewed.

## Recommended Policy

Use a conservative hybrid policy:

- Public-facing post titles may use polished title-style capitalization in Portuguese.
- Do not change Pāli terms automatically.
- Do not remove or normalize diacritics.
- Do not alter doctrinal expressions without human review.
- Do not infer meaning from title fragments if punctuation or source title integrity is uncertain.
- Prefer consistency across archive pages, post headers, print headers, and review matrices.

## Human Review Rule

Any title correction should pass through the title comparison matrix before being applied.

Relevant artifact:

- `review/title-matrix/flagfix_020_title_comparison_matrix.csv`

Recommended columns to use or add:

- `pdpn`
- `source_title_en`
- `axis_title_en`
- `axis_title_pt_current`
- `axis_title_pt_proposed`
- `capitalization_policy`
- `human_review_status`
- `review_notes`

## Do Not Automate Yet

This issue must not trigger a mass rewrite of titles until:

1. title source provenance is confirmed;
2. Pāli/glossary protection is respected;
3. punctuation preservation issues are addressed;
4. a pilot set is reviewed manually;
5. the production build input contract is satisfied.

## Pilot Recommendation

Start with a small Batch 02 pilot set:

- FlagFix 011 — punctuation semantic preservation
- FlagFix 012 — slug/title divergence
- FlagFix 013 — capitalization policy
- FlagFix 020 — title comparison matrix
- FlagFix 021 — date metadata review

## Suggested Resolution Path

1. Define the capitalization policy.
2. Add examples to the title comparison matrix.
3. Review titles manually.
4. Apply corrections only after review.
5. Keep source title, AXIS en-US title, and AXIS pt-BR title traceable.

## Initial Decision

Tentative preference:

Use polished Portuguese title-style capitalization for public-facing titles, while preserving doctrinal/Pāli/source-sensitive terms exactly as reviewed.

Final decision remains pending human review.
