# AXIS-NIDDHI — FLAGFIX_020 Title Matrix Expansion Plan

**Date:** 2026-05-04  
**Status:** Plan-only / No implementation  
**Scope:** Controlled expansion of the title comparison matrix  
**Implementation:** Not authorized by this document

---

## Purpose

This document defines a docs-only plan for expanding the `FLAGFIX_020` Title Comparison Matrix in a controlled human-review workflow.

The matrix exists to compare:

- PureDhamma original title;
- PureDhamma slug / URL;
- AXIS en-US title;
- AXIS pt-BR title;
- AXIS URL;
- issue type;
- human note;
- final human decision.

This plan does not authorize title corrections, CSV expansion, scripts, code changes, metadata changes, static-site output changes, or rebuilds.

---

## Current State

The seed matrix exists:

```text
review/title-matrix/flagfix_020_title_comparison_matrix.csv
```

It currently has a header plus seed rows for:

```text
TL.EE.008
TL.EE.011
```

It is a pilot human-review artifact, not an implementation artifact.

No title should be corrected automatically from the current matrix.

---

## Related Policies

The matrix is the coordination artifact for several Batch 02 title policies:

- `FLAGFIX_007` — title glossary / Pāli protection;
- `FLAGFIX_011` — punctuation preservation;
- `FLAGFIX_012` — slug/title divergence;
- `FLAGFIX_013` — pt-BR title capitalization.

These policies inform review classification. They do not authorize automatic correction.

---

## Guardrails

This plan does not authorize:

- automatic title correction;
- CSL edits;
- `identity.json` edits;
- `SP02` changes;
- `SP11` changes;
- renderer changes;
- SSG functional changes;
- metadata operational changes;
- static-site output changes;
- rebuilds;
- mass title rewrites.

The safe default remains:

```text
Preserve first. Compare second. Correct only after human review.
```

---

## Expansion Workflow

### Step 1 — Validate Matrix Columns and Decision Vocabulary

Confirm the matrix columns are sufficient for human review.

Recommended required fields:

- `PDPN`;
- `puredhamma_original_title`;
- `puredhamma_slug`;
- `puredhamma_url`;
- `axis_en_title`;
- `axis_pt_title`;
- `axis_url`;
- `issue_type`;
- `human_reviewer_note`;
- `decision`.

Confirm the decision vocabulary before adding more rows.

### Step 2 — Add a Small Pilot Batch of Title Cases

Add a small pilot batch from known policy examples.

Good candidates include titles flagged by:

- punctuation loss;
- slug/title divergence;
- Pāli or glossary term protection;
- pt-BR capitalization concerns;
- title fallback from slug;
- translation review concerns.

The pilot should be small enough for human review before any correction issue is opened.

### Step 3 — Human Review

A human reviewer should mark:

- issue type;
- review note;
- final decision.

The decision should distinguish between:

- no action;
- accepted divergence;
- needs title correction;
- needs slug/source verification;
- needs doctrinal/Pāli review;
- needs downstream implementation issue.

### Step 4 — Open Targeted Correction Issues Only After Review

Only after a human decision should targeted correction issues be opened.

Each correction issue should name the exact PD#PN rows, the approved title decision, the expected changed files, and the rollback strategy.

---

## Recommended Issue Types

Use a controlled issue-type vocabulary:

- `punctuation_loss`;
- `slug_title_divergence`;
- `pali_term_protection`;
- `pt_capitalization`;
- `title_missing`;
- `title_fallback_from_slug`;
- `translation_review`;
- `no_action`.

Additional values may be added later, but should be documented before use.

---

## Candidate Data Sources

Candidate read-only sources for future matrix expansion:

```text
pipeline/13-static-site/search_index.json
pipeline/13-static-site/pages/<PDPN>/index.html
pipeline/metadata/Translation_Control_Center.csv
pipeline/metadata/Print_Translation_Control_Center.csv
review/title-matrix/flagfix_020_title_comparison_matrix.csv
```

These sources may support review data collection. They do not authorize editing generated output or metadata.

---

## Out of Scope

This plan excludes:

- direct correction of titles;
- DeepL/API translation;
- automatic normalization;
- renderer changes;
- pipeline changes;
- metadata changes;
- SSG functional changes;
- rebuild/publication;
- static-site output changes.

CSV expansion is also out of scope for this plan PR. It should happen in a separate review artifact PR.

---

## Next Review Gate

Future matrix expansion should use a dedicated branch and PR.

That PR should state:

- exact rows added;
- source evidence used;
- issue-type vocabulary used;
- whether all rows are review-only;
- confirmation that no title corrections or generated output changes are included.
