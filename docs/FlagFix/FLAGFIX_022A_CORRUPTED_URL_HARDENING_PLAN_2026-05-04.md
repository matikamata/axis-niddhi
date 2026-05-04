# AXIS-NIDDHI — FLAGFIX_022A Corrupted URL Hardening Plan

**Date:** 2026-05-04  
**Status:** Plan-only / No implementation  
**Scope:** Corrupted URL hardening for legacy media shortcodes  
**Implementation:** Not authorized by this document

---

## Purpose

This document records a docs-only plan for `FLAGFIX_022A` — corrupted URL hardening for legacy media shortcodes.

It is based on the read-only audit recorded in `docs/FlagFix/FLAGFIX_022_MEDIA_EVIDENCE_AUDIT_2026-05-04.md`.

This document does not authorize code, renderer, pipeline, CSS, JavaScript, template, CSL, static-site output, metadata, navigation, deployment, or Cloudflare changes.

---

## Problem Summary

Some legacy media shortcodes become `LEGACY_MEDIA_CORRUPTED`.

The likely cause is glossary/Pāli marginalia being injected into shortcode URLs before legacy shortcode rewriting.

The current preservation layer is conservative: when a shortcode appears contaminated by HTML markup, it preserves the raw source signal as review evidence instead of silently generating a broken media link.

---

## Current Suspected Transform Order

```text
raw content
→ link_resolver.resolve_links()
→ process_assets()
→ inject_marginalia()
→ modernize_iframes()
→ template render
→ _rewrite_legacy_shortcodes()
```

This order means `inject_marginalia()` can see shortcode URLs as normal text before `_rewrite_legacy_shortcodes()` extracts and preserves them.

---

## Suspected Root Cause

`inject_marginalia()` sees shortcode URLs as normal text.

Glossary/Pāli markup can be inserted into URL fragments such as `puredhamma` or Pāli terms.

`_rewrite_legacy_shortcodes()` later sees contaminated shortcode markup and safely preserves it as `LEGACY_MEDIA_CORRUPTED`.

This is preferable to publishing a corrupted clickable link, but it leaves hardening work for a future implementation PR.

---

## Affected Corrupted Cases

```text
MR.AA.008
DD.AA.003
DD.AA.007
BC.AA.005
KD.HH.009
BC.AA.004
```

Note: `BC.AA.004` has two corrupted cases.

---

## Future Patch Options

### Preferred

Protect or rewrite legacy media shortcodes before `inject_marginalia()`.

This would prevent shortcode URLs from being treated as normal text by the glossary/Pāli marginalia pass.

### Alternative

Make `inject_marginalia()` skip text nodes containing legacy shortcode patterns.

This may be smaller, but it is less comprehensive than moving shortcode protection earlier in the transform sequence.

---

## Expected Future Candidate Files

Future implementation may need to inspect or patch:

```text
pipeline/13-ssg/src/renderers/post_renderer.py
pipeline/13-ssg/build.py
```

No code change is authorized by this plan.

---

## Rebuild Gate

A source patch alone will not update published/static output.

Resolving the seven corrupted static cases requires an approved rebuild/static-site output publication.

No manual static-site page edits are allowed.

Any rebuild or static-site output publication must be explicitly approved in a separate implementation PR.

---

## Test Plan

Verify corrupted pages:

```text
MR.AA.008
DD.AA.003
DD.AA.007
BC.AA.005
KD.HH.009
BC.AA.004
```

Verify original valid case:

```text
TL.EE.003
```

Verify multiple-download case:

```text
KD.FF.021
```

Suggested future checks:

```bash
rg -n "LEGACY_MEDIA_CORRUPTED|RAW_SHORTCODE" pipeline/13-static-site/pages
rg -n "\\[easy_media_download" pipeline/13-static-site/pages
rg -n "axis-media-evidence" pipeline/13-static-site/pages
```

Expected future outcome after an approved implementation and rebuild:

- valid legacy media shortcode URLs remain preserved as evidence links;
- corrupted URL cases are reduced or eliminated;
- no glossary/Pāli markup appears inside shortcode URLs;
- `TL.EE.003` remains reader-safe;
- no manual page edits are required.

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

Implementation requires a separate PR.

Rebuild/static-site output requires explicit approval.

---

## Next Review Gate

Future `FLAGFIX_022A` implementation must use a dedicated branch and PR.

That PR must state whether it changes source code only or also requests a rebuild/static-site output publication.
