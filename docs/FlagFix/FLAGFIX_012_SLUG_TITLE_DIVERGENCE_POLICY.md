# FlagFix 012 — Slug Title Divergence Policy

## Status

Planning / review policy only.

No slug, title, route, URL, metadata, CSL, or renderer changes are authorized by this document.

## Problem

Some AXIS-NIDDHI pages may have a visible human title that diverges from the canonical slug, source URL, or historical route naming.

This can happen for legitimate reasons:

- the original PureDhamma.net title changed over time;
- the WordPress slug preserved an older title;
- the translated title improves readability;
- the slug is shorter, normalized, or historically frozen;
- punctuation, capitalization, or Pāli terms differ between display title and route;
- canonical identifiers such as PD#PN are more stable than slugs.

Therefore, slug/title divergence is not automatically an error.

## Policy

Slug/title divergence must be treated as a human review signal, not as an automatic correction trigger.

AXIS-NIDDHI should preserve:

- canonical route stability;
- archival traceability;
- PD#PN identity;
- original source evidence;
- current human-readable title quality.

No automated process should rewrite slugs or titles only because they differ.

## Pale Blue Dot Review Signal

A future UI/review layer may show a discreet pale-blue-dot indicator when slug/title divergence is detected.

Purpose:

- alert reviewers that the title and slug should be compared;
- avoid visual alarm;
- avoid implying doctrinal or editorial error;
- keep the archive pleasant for normal readers;
- support later review matrix workflows.

The marker should be:

- subtle;
- non-blocking;
- hidden or minimized in print unless needed for review;
- linked to review metadata when available;
- removable after human review if the divergence is accepted.

## Human Review Required

Before any title or slug change, reviewers should compare:

- English title;
- Portuguese title;
- slug / route;
- PD#PN;
- source page title;
- source URL;
- historical title if available;
- doctrinal terminology;
- punctuation and capitalization.

## Allowed Outcomes

After review, a divergence may be classified as:

- accepted historical divergence;
- title needs correction;
- slug needs preservation despite mismatch;
- metadata note needed;
- requires source verification;
- blocked pending doctrinal review.

## Forbidden Automatic Actions

Do not automatically:

- rename slugs;
- rename folders;
- rewrite canonical routes;
- change titles;
- normalize punctuation;
- translate Pāli terms;
- remove historical wording;
- infer the “correct” title from URL text alone.

## Relationship to Other FlagFix Items

Related:

- FlagFix 011 — title punctuation semantic preservation;
- FlagFix 013 — PT title capitalization policy;
- FlagFix 020 — title comparison human review matrix;
- FlagFix 021 — missing date metadata review;
- FlagFix 023 — production build input contract.

## Recommended Next Step

Add slug/title divergence columns to the FlagFix 020 review matrix before implementing any visual indicator.

Suggested columns:

- `slug_or_route`
- `source_url_title_hint`
- `title_slug_divergence`
- `divergence_review_status`
- `pale_blue_dot_candidate`
- `reviewer_note`

