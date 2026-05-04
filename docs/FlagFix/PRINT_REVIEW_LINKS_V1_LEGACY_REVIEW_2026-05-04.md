# AXIS-NIDDHI - Legacy Review: print-review-links-v1

**Date:** 2026-05-04  
**Status:** Review-only / No implementation  
**Scope:** Legacy branch assessment  
**Branch reviewed:** `print-review-links-v1`  
**Merge base reviewed:** `65e1c035d0575a2dfeb56be9ba679905839d7b52`  
**Implementation:** Not authorized by this document

---

## Purpose

This document reviews the legacy branch `print-review-links-v1` as a reference artifact.

The goal is to decide whether the idea behind the branch may be useful for a future controlled hotfix.

This document does not authorize merging, cherry-picking, patching, or reimplementing the branch.

---

## Branch Context

`print-review-links-v1` is an old functional branch related to print review traceability and visible links.

The branch exists only as a reference branch and must not be merged directly into `main`.

It contains one unique commit after the merge base with current `main`:

```text
0fd231c fix(print): add review traceability and visible links
```

The branch changes CSS and JavaScript files, including generated/static-site output mirrors.

---

## Files Changed in Legacy Branch

Read-only diff inspection found these changed files:

```text
M pipeline/13-ssg/static/css/style.css
M pipeline/13-ssg/static/js/main.js
M pipeline/13-static-site/css/style.css
M pipeline/13-static-site/js/main.js
```

Diff stat:

```text
pipeline/13-ssg/static/css/style.css  | 32 ++++++++++++++++++++++++++
pipeline/13-ssg/static/js/main.js     | 43 +++++++++++++++++++++++++++++++++++
pipeline/13-static-site/css/style.css | 32 ++++++++++++++++++++++++++
pipeline/13-static-site/js/main.js    | 43 +++++++++++++++++++++++++++++++++++
4 files changed, 150 insertions(+)
```

---

## Apparent Technical Intent

The patch appears intended to improve print-review traceability by adding a print-only review banner and ensuring visible review context in printed/PDF copies.

The JavaScript adds an `initPrintReviewBanner()` function that inserts a `.print-review-banner` before `article.content-block`. The banner includes:

- draft/review copy labeling;
- PureDhamma.net source reference;
- current AXIS-NIDDHI page URL;
- canonical ID from the article `data-pdpn` attribute;
- a note that the printed/PDF copy is for review and archival traceability.

The CSS hides the banner on screen and displays it under `@media print`. The CSS also centers `.title-pt` and `.title-en` in print.

The intent may still be useful for human review workflows, but the legacy implementation is functional code and static output, not a documentation-only change.

---

## Risk Assessment

### Functional Surface

The branch touches:

- CSS behavior;
- JavaScript behavior;
- print/PDF behavior;
- generated/static-site mirrored output.

These are functional changes, not policy changes.

### JavaScript Risk

The patch injects DOM content at runtime.

Future review should confirm:

- `article.content-block` exists consistently across target pages;
- `data-pdpn` is reliable and present where expected;
- the inserted banner does not duplicate existing print review banners;
- print output remains readable across languages and page sizes;
- runtime insertion does not affect screen behavior, accessibility, or search indexing unexpectedly.

### CSS Risk

The patch changes print styling and title alignment.

Future review should confirm:

- title centering is desired across all article types;
- the banner does not consume excessive print space;
- long URLs wrap cleanly;
- A4 and Letter print previews remain acceptable;
- existing print review CSS is not duplicated or contradicted.

### Deployment Risk

If merged to `main`, the change would trigger a Cloudflare production deploy.

Unlike docs-only PRs, this would represent an intended publication behavior change and must pass a dedicated implementation review.

### Static Output Risk

The branch includes changes under `pipeline/13-static-site/`.

Future implementation should decide explicitly whether generated output is allowed to be committed, regenerated, or excluded.

No generated static-site output should be changed without explicit approval.

---

## Decision

Do not merge `print-review-links-v1` directly.

Do not cherry-pick `0fd231c` blindly.

Do not apply the legacy patch as-is.

Treat the branch as a historical reference only.

---

## Future Reimplementation Recommendation

If this feature is approved later, create a fresh branch from current `main`.

Recommended future branch name:

```text
fix/print-review-links-traceability-YYYYMMDD
```

The future implementation should:

- start from current `main`;
- inspect the legacy diff;
- reimplement only the minimum necessary behavior;
- avoid touching generated static-site output unless explicitly approved;
- prefer source-side CSS/JS changes over generated mirrors when possible;
- include before/after screenshots or print/PDF evidence;
- include rollback instructions;
- document whether Cloudflare deploy is expected;
- keep the diff small and reviewable.

---

## Future Implementation Checklist

Before any future implementation:

- create a dedicated issue;
- create a dedicated implementation branch;
- define exact user-visible behavior;
- identify whether CSS only is sufficient;
- justify any JavaScript change;
- justify any generated output change;
- confirm no CSL or canonical content changes;
- confirm no renderer behavior changes unless explicitly approved;
- confirm no metadata or navigation behavior changes;
- test local static preview;
- test browser print preview;
- capture screenshots or PDF evidence;
- provide rollback plan;
- list expected changed files before commit.

---

## Rollback Strategy

A future implementation PR must be reversible with a clean revert commit.

If the change affects print output, rollback validation must include:

- local preview still loads;
- print preview returns to prior behavior;
- no generated content remains unexpectedly modified;
- `git diff --name-only` after rollback shows only the revert commit effect.

---

## Next Review Gate

A future implementation requires a separate issue, branch, PR, and explicit approval.

This review document is not sufficient authorization for code changes.

Until that review gate is approved, `print-review-links-v1` remains a reference branch only.
