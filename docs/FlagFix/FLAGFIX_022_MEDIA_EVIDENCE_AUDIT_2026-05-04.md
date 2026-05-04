# AXIS-NIDDHI — FLAGFIX_022 Media Evidence Audit

**Date:** 2026-05-04  
**Status:** Audit-only / No implementation  
**Scope:** FLAGFIX_022 media evidence blocks and legacy shortcode remnants  
**Implementation:** Not authorized by this document

---

## Purpose

This document records a read-only audit of `axis-media-evidence` blocks related to `FLAGFIX_022`.

The audit exists to preserve the current operational findings before any future hardening work.

This document does not authorize code, CSS, JavaScript, pipeline, renderer, CSL, static-site output, metadata, navigation, or deployment changes.

---

## Summary

| Item | Count |
|---|---:|
| `axis-media-evidence` blocks | 41 |
| affected pages | 25 |
| `RAW_SHORTCODE` evidence | 7 |
| `LEGACY_MEDIA_CORRUPTED` | 7 |
| `LEGACY_MEDIA_UNKNOWN` | 0 |
| `LEGACY_MEDIA_DOWNLOAD` | 34 |
| heuristic problematic-markup lines | 17 |

The original reader-facing `TL.EE.003` raw shortcode leak is operationally resolved. Recognized legacy media shortcodes are represented as media evidence blocks.

Hardening remains necessary for corrupted URL cases, invalid surrounding markup, and corpus-wide review.

---

## Affected Pages

```text
BC.AA.003
BC.AA.004
BC.AA.005
BC.AA.006
BM.AA.001
DD.AA.002
DD.AA.003
DD.AA.006
DD.AA.007
KD.FF.021
KD.HH.009
LD.AA.004
LD.AA.007
LD.AA.008
LD.AA.009
LD.AA.010
LD.AA.011
LD.CC.003
LD.DD.002
LD.DD.003
LD.DD.004
MR.AA.005
MR.AA.008
SI.CC.002
TL.EE.003
```

---

## Corrupted Legacy Media Cases

Pages with `LEGACY_MEDIA_CORRUPTED`:

```text
MR.AA.008
DD.AA.003
DD.AA.007
BC.AA.005
KD.HH.009
BC.AA.004
```

Note: `BC.AA.004` has two corrupted cases.

The corrupted cases preserve `RAW_SHORTCODE` evidence in HTML comments. The observed corruption pattern suggests glossary/Pāli markup may have entered shortcode URLs before the media evidence rewrite.

---

## Visual Test Priorities

High priority:

- `TL.EE.003`
- `MR.AA.008`
- `BC.AA.004`
- `LD.AA.010`
- `LD.AA.011`
- `DD.AA.007`

Medium priority:

- `KD.FF.021`
- `LD.AA.009`
- `BM.AA.001`

---

## Recommended Sub-Issues

### Audit inventory

Inventory all `axis-media-evidence` blocks with page, PD#PN, label, URL state, and surrounding markup.

### Corrupted URL hardening

Investigate and prevent glossary/Pāli markup from entering shortcode URLs before media shortcode preservation runs.

### Markup normalization

Normalize evidence block placement so block-level evidence does not appear inside problematic surrounding tags such as `p`, `span`, `h5`, or `ul`.

### Visual print/screen validation

Review representative media evidence pages in screen and print/PDF output before any hardening patch is proposed.

### Approved rebuild gate

Only after audit and design review should pipeline hardening and an approved rebuild be considered.

---

## Guardrails

This audit does not authorize:

- CSL edits;
- renderer changes;
- `build.py` changes;
- CSS changes;
- JavaScript changes;
- pipeline changes;
- static-site output changes;
- metadata changes;
- navigation changes;
- deployment or Cloudflare configuration changes.

No manual CSL or static-site page edits are recommended.

---

## Next Review Gate

Any future FLAGFIX_022 hardening requires a separate issue or local task record, branch, PR, and explicit approval.

Future work must restate the exact implementation surface and whether a static-site rebuild is expected.
