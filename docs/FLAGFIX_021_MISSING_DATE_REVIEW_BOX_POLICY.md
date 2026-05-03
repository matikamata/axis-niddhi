# FlagFix 021 — Missing Date Review Box Policy

## Status

Planning / review policy only.

No metadata, CSL, renderer, template, route, title, or date correction changes are authorized by this document.

## Problem

Some AXIS-NIDDHI pages may have missing, ambiguous, incomplete, or historically inconsistent publication/revision date metadata.

Date metadata is important for review, citation, and archival traceability. However, dates must not be invented, normalized, or silently corrected without source-bound evidence.

## Preservation Rule

Existing date wording, ordering, and didactic styling should be preserved unless reviewed.

If a date is present and visibly styled in blue, that styling may be meaningful or editorially useful and should not be normalized away automatically.

## Missing / Ambiguous Date Rule

When date metadata is missing or ambiguous, AXIS-NIDDHI should eventually display a conservative review indicator rather than guessing a date.

Recommended future visible wording:

> Date metadata requires human review.

This wording should indicate uncertainty without implying that the original source is wrong.

## Review Box Requirements

A future review box should be:

- visibly distinct but calm;
- non-alarming;
- print-friendly;
- source-bound;
- clearly labeled as a review signal;
- not presented as canonical metadata;
- easy to search in generated HTML;
- easy to remove or resolve after review.

## Forbidden Automatic Actions

Do not automatically:

- invent publication dates;
- infer dates from file timestamps;
- infer dates from crawl time;
- overwrite original WordPress date wording;
- normalize blue date styling away;
- convert ambiguous dates into canonical metadata;
- mark missing dates as errors unless human review confirms a defect.

## Relationship to FlagFix 020

FlagFix 020 should remain the review matrix for title/metadata comparison.

Any date review result should be recorded in a human-review artifact before implementation.

## Future Implementation Gate

Before any implementation, define:

1. exact detection rule;
2. exact visible wording;
3. print behavior;
4. source evidence path;
5. audit/search marker;
6. rollback procedure.

## Current Decision

FlagFix 021 is a human-review and display-treatment issue, not an automatic metadata correction issue.
