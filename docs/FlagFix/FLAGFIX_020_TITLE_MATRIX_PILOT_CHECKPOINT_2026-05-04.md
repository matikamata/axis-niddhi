# AXIS-NIDDHI — FLAGFIX_020 Title Matrix Pilot Checkpoint

**Date:** 2026-05-04  
**Status:** Checkpoint / No implementation  
**Scope:** FLAGFIX_020 title comparison matrix pilot state  
**Implementation:** Not authorized by this document

---

## Purpose

This document records the state of `FLAGFIX_020` after the controlled pilot expansion of the title comparison matrix.

It is a docs-only checkpoint. It does not authorize title corrections, CSV changes, scripts, code changes, metadata changes, static-site output changes, or rebuilds.

---

## Matrix Location

The matrix exists at:

```text
review/title-matrix/flagfix_020_title_comparison_matrix.csv
```

Current state:

```text
pilot expanded / human review pending
```

Current total:

```text
header + 6 rows
```

---

## Original Seed Rows

The original seed rows are:

| PD#PN | Role |
|---|---|
| `TL.EE.008` | Seed title punctuation / semantic preservation / translation risk case. |
| `TL.EE.011` | Seed missing or ambiguous date metadata context case. |

---

## PR #98 Pilot Expansion Rows

PR #98 added four review-only pilot rows:

| PD#PN | Issue type |
|---|---|
| `TL.CC.003` | `punctuation_loss` |
| `TL.BB.002` | `slug_title_divergence` |
| `TL.CC.004` | `pt_capitalization` |
| `TL.BB.005` | `pali_term_protection` |

All new rows are marked:

```text
decision=review_pending
```

No title correction was applied.

---

## Current Decision

Do not expand the matrix in bulk yet.

The next step is human review of the six current rows.

Future corrections must become targeted issues and PRs.

This checkpoint does not authorize changes to:

- CSL;
- `identity.json`;
- `SP02`;
- `SP11`;
- renderer behavior;
- metadata;
- static-site output;
- rebuild/publication.

---

## Guardrails

This checkpoint does not authorize:

- automatic title correction;
- direct title correction;
- CSV expansion;
- scripts;
- code changes;
- metadata changes;
- static-site output changes;
- rebuilds;
- mass title rewrites.

The matrix remains a human-review artifact only.

---

## Next Review Gate

Before any implementation, reviewers should decide each current matrix row.

Only rows with explicit human approval should become downstream correction issues or implementation PRs.
