# AXIS-NIDDHI — FLAGFIX_022B Media Evidence Markup Normalization Plan

**Date:** 2026-05-04  
**Status:** Plan-only / No implementation  
**Scope:** Media evidence block markup normalization  
**Implementation:** Not authorized by this document

---

## Purpose

This document records a docs-only plan for `FLAGFIX_022B` — normalize media evidence block markup.

It follows the read-only audit recorded in `docs/FlagFix/FLAGFIX_022_MEDIA_EVIDENCE_AUDIT_2026-05-04.md`.

This document does not authorize code, renderer, pipeline, CSS, JavaScript, template, CSL, static-site output, metadata, navigation, deployment, or Cloudflare changes.

---

## Problem Summary

`div.axis-media-evidence` blocks may appear in structurally invalid parent contexts.

Observed examples include evidence blocks inside:

- `<p>`;
- `<span>`;
- `<h5><strong>`;
- directly inside `<ul>`.

The issue is structural HTML validity and predictable rendering around preserved media evidence.

---

## Known Heuristic Count

The current read-only audit identified:

```text
17 problematic lines
```

This count is heuristic. A future implementation PR should confirm it with explicit structure checks before patching or rebuilding.

---

## Priority Pages

Priority pages for future inspection:

```text
MR.AA.008
LD.AA.010
LD.AA.011
TL.EE.003
BC.AA.004
BC.AA.005
DD.AA.003
DD.AA.007
KD.HH.009
LD.AA.009
BM.AA.001
```

---

## Suspected Cause

Legacy media evidence blocks are inserted after or during HTML transformation without normalizing invalid parent wrappers.

A block-level `div.axis-media-evidence` cannot safely remain inside inline or list-only contexts.

This can create invalid or browser-repaired HTML even when the evidence content itself is intentionally preserved.

---

## Future Patch Options

### Preferred

Emit media evidence as a structurally safe block outside invalid parent tags.

This keeps the reader-facing evidence component consistent and avoids placing block-level evidence inside inline or list-only contexts.

### Alternative

Use context-sensitive inline evidence markup only when inside inline contexts.

This may reduce restructuring, but it risks inconsistent UX and weaker visual traceability across screen and print review.

---

## Expected Future Candidate Files

Future implementation may need to inspect or patch:

```text
pipeline/13-ssg/build.py
pipeline/13-ssg/src/renderers/post_renderer.py
```

If HTML normalization helpers already exist, they may also be candidate files.

No code change is authorized by this plan.

---

## Relationship With FLAGFIX_022A

`FLAGFIX_022A` handles corrupted URL hardening.

`FLAGFIX_022B` handles surrounding markup normalization.

Do not mix both in one implementation PR unless explicitly approved.

Keeping the two workstreams separate preserves reviewability:

- `022A` protects shortcode URL content before preservation;
- `022B` normalizes where the preserved evidence block lands in the document structure.

---

## Rebuild Gate

A source patch alone will not update published/static output.

Resolving current static markup requires approved rebuild/static-site output publication.

No manual static-site page edits are allowed.

Any rebuild or static-site output publication must be explicitly approved in a separate implementation PR.

---

## Test Plan

Future implementation should inspect the priority pages listed above.

Required checks:

- verify `TL.EE.003` remains reader-safe;
- verify valid download links remain clickable;
- verify corrupted evidence remains auditable;
- verify screen layout for evidence blocks;
- verify print layout for evidence blocks;
- run HTML/structure checks if available.

Recommended validation focus:

- evidence blocks should not remain inside `<p>`, `<span>`, `<h5><strong>`, or directly inside `<ul>`;
- valid media evidence should remain visually recognizable;
- corrupted evidence should remain visible as review evidence rather than silently disappearing;
- no manual page edits should be needed.

---

## Guardrails

This plan does not authorize:

- manual CSL edits;
- manual static-site page edits;
- CSS changes;
- JavaScript changes;
- template changes;
- renderer changes;
- pipeline changes;
- metadata changes;
- navigation changes;
- deployment or Cloudflare configuration changes.

No CSS, JavaScript, or template change is authorized for this issue unless separately approved.

Implementation requires a separate PR.

Rebuild/static-site output requires explicit approval.

---

## Next Review Gate

Future `FLAGFIX_022B` implementation must use a dedicated branch and PR.

That PR must state whether it changes source code only or also requests a rebuild/static-site output publication.
