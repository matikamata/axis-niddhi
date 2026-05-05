# AXIS-NIDDHI — FLAGFIX Batch 04 Media and Assets Audit

**Date:** 2026-05-04  
**Status:** Audit-only / Human review pending  
**Scope:** Batch 04 — Media and Assets  
**Implementation:** Not authorized by this document

---

## Purpose

This document records a small read-only audit for Batch 04 — Media and Assets.

The goal is to capture representative evidence from the current static-site output before any renderer, CSS, JavaScript, template, metadata, pipeline, or publication changes are considered.

No implementation is authorized by this audit.

---

## Current Batch 04 Posture

Batch 04 remains `audit-first`.

Current state by FlagFix:

- `FLAGFIX_005` — policy/inventory mode:
  - text-bearing images, diagrams, screenshots, and flowcharts still need explicit asset inventory.
- `FLAGFIX_010` — policy/inventory mode:
  - external audio, offline behavior, and placeholder wording still need traceability-first review.
- `FLAGFIX_014` — policy/inventory mode:
  - image rendering, centering, zoom, and per-context behavior remain split-friendly and should stay targeted rather than global.
- `FLAGFIX_015` — policy/inventory mode:
  - YouTube/iframe print-traceability still needs selector and variant audit before any new patch.
- `FLAGFIX_022` — already has its own audit and 022A/022B roadmap:
  - this audit references 022 only as cross-surface context and does not reopen that package.

---

## Audit Artifact

CSV audit artifact:

- `review/media-assets/flagfix_batch04_media_assets_audit.csv`

The CSV is a pilot evidence set and does not attempt corpus-wide exhaustiveness.

It includes representative rows for:

- large doctrinal images;
- text-bearing diagrams and flowcharts;
- images placed inside list items or headings;
- YouTube iframes and plain YouTube links;
- audio players with external/offline traceability implications;
- `axis-media-evidence` / legacy download cross-references;
- pages that should remain priority targets for future visual testing.

All rows are marked:

```text
human_review_status=review_pending
```

---

## Key Findings

### 1. Images and diagrams still need explicit inventory

Representative assets already show several structurally different contexts:

- normal inline images (`BD.AA.007`, `CH.BB.006`, `KD.JJ.010`);
- images inside list items (`KD.JJ.006`, `QD.DD.002`);
- image inside heading markup (`PS.GG.004`);
- small but text-bearing diagram (`TL.JJ.008 / climbers.png`).

This supports `FLAGFIX_005` and `FLAGFIX_014` remaining inventory-first.

### 2. `FLAGFIX_014` should remain split into narrower future tracks

The sampled cases show that image behavior is not one problem:

- very wide chart (`KD.JJ.006`);
- moderate text-bearing image (`TL.JJ.008`);
- doctrinal image plus download traceability (`BD.AA.007`);
- image in structurally odd wrappers (`PS.GG.004`, `QD.DD.002`).

A single global rendering patch would be too blunt.

### 3. YouTube/video traceability still needs variant audit

Observed current patterns include:

- many standard YouTube embeds in `BD.AA.007`;
- YouTube embed with query-string variant in `TL.JJ.008`;
- plain `youtu.be` link in `QD.DD.002`.

That is enough evidence to keep `FLAGFIX_015` in selector/variant-audit mode before any new implementation.

### 4. Audio traceability and media evidence overlap, but should stay separately scoped

`KD.FF.021` and `TL.EE.003` show audio plus `axis-media-evidence` download blocks.

This confirms:

- `FLAGFIX_010` should keep focusing on placeholder/external resolution behavior;
- `FLAGFIX_022` should keep its own hardening roadmap for evidence blocks and shortcode preservation.

The two areas touch each other, but should not be merged casually.

---

## Priority Future Visual-Test Pages

Suggested future priority pages for manual visual/print review:

- `BD.AA.007`
- `TL.JJ.008`
- `KD.JJ.006`
- `QD.DD.002`
- `PS.GG.004`
- `KD.FF.021`
- `TL.EE.003`

Secondary but still useful:

- `CH.BB.006`
- `KD.JJ.010`
- `BM.CC.006`

---

## Recommended Next Steps

Safe next steps from this audit:

1. expand the CSV with more read-only evidence rows;
2. create narrower sub-issues only if one asset class needs isolated treatment;
3. keep `FLAGFIX_014` split into sub-issues if future implementation is needed;
4. keep `FLAGFIX_022` hardening in its own 022A/022B roadmap package.

Future implementation, if any, must include:

- targeted issue;
- targeted branch and PR;
- explicit test plan;
- rollback plan;
- explicit publication/static-site approval if generated output is touched.

---

## Guardrails

This audit does not authorize:

- CSS changes;
- JavaScript changes;
- renderer changes;
- CSL changes;
- template changes;
- metadata operational changes;
- pipeline changes;
- static-site output changes;
- rebuild/publication;
- image replacement;
- audio placeholder implementation;
- YouTube print-marker implementation.

---

## Final Batch 04 Posture

Batch 04 should continue to be treated as:

- audited;
- inventory-first;
- review-controlled;
- not yet implementation-ready.
