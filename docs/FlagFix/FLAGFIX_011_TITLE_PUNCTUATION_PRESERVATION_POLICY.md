# FlagFix 011 — Title Punctuation Semantic Preservation

## Status

Planning / review policy only.

No automatic title changes are authorized by this document.

## Problem

Some post titles may contain punctuation that carries semantic, doctrinal, rhetorical, or navigational meaning.

Examples of punctuation that may be meaningful:

- question marks: `?`
- exclamation marks: `!`
- colons: `:`
- semicolons: `;`
- parentheses: `( )`
- quotation marks: `" "`, `“ ”`
- dashes / em dashes: `–`, `—`
- ellipses: `...`
- comma structures that affect meaning

In title translation or title normalization workflows, punctuation must not be removed, added, or simplified merely for visual polish.

## Policy

Title punctuation is considered semantically protected unless human review determines otherwise.

Do not automatically:

- remove punctuation from a title;
- add punctuation to make a title look better;
- normalize punctuation style across English and Portuguese;
- convert question titles into statement titles;
- remove parentheses or quoted phrases;
- replace dash/colon structures without review;
- collapse punctuation that may encode emphasis, contrast, sequence, or doctrinal framing.

## Portuguese Title Handling

Brazilian Portuguese titles may naturally differ from English titles.

However:

- semantic punctuation from the English title should be reviewed before being omitted;
- punctuation added in Portuguese should be justified by readability or meaning;
- title punctuation should be compared in the FlagFix 020 human review matrix before correction.

## Human Review Required

Any title punctuation change must be reviewed with at least:

- PD#PN
- English title
- Portuguese title
- current slug
- proposed title
- punctuation difference
- reviewer decision
- rationale

Recommended review artifact:

- `review/title-matrix/flagfix_020_title_comparison_matrix.csv`

## Allowed Without Review

The following may be acceptable without doctrinal review only if they do not alter meaning:

- fixing obvious duplicated punctuation caused by rendering bugs;
- correcting encoding corruption;
- preserving existing punctuation exactly as source metadata provides it;
- documenting a punctuation mismatch without changing published output.

## Blocked Until Review

Do not implement automatic title punctuation correction until a small human-reviewed pilot set exists in the FlagFix 020 matrix.

## Relationship to Other FlagFix Items

Related:

- FlagFix 013 — PT Title Capitalization Policy
- FlagFix 020 — Title Comparison Human Review Matrix
- FlagFix 012 — Slug Title Divergence Pale Blue Dot
- FlagFix 021 — Missing Date Metadata Review Box

## Conclusion

AXIS-NIDDHI should preserve title punctuation as semantic metadata.

The safe default is:

> Preserve first. Compare second. Correct only after human review.
