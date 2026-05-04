# AXIS-NIDDHI — FLAGFIX_022 Hardening Roadmap

**Date:** 2026-05-04  
**Status:** Roadmap-only / No implementation  
**Scope:** FLAGFIX_022 coordination and closure planning  
**Implementation:** Not authorized by this document

---

## Purpose

This document consolidates the current FLAGFIX_022 hardening package and records the recommended order for any future implementation work.

It is a docs-only coordination roadmap.

This roadmap does not authorize code, renderer, pipeline, CSS, JavaScript, template, CSL, static-site output, metadata, navigation, deployment, or Cloudflare changes.

---

## Package Records

The current package is organized as follows:

| Record | Role |
|---|---|
| `docs/FlagFix/FLAGFIX_022_SHORTCODE_WORDPRESS_EASY_MEDIA_DOWNLOAD.md` | Umbrella/status record for WordPress `easy_media_download` shortcode leakage and hardening. |
| `docs/FlagFix/FLAGFIX_022_MEDIA_EVIDENCE_AUDIT_2026-05-04.md` | Quantified audit of media evidence blocks, corrupted shortcode evidence, affected pages, and future sub-issues. |
| `docs/FlagFix/FLAGFIX_022A_CORRUPTED_URL_HARDENING_PLAN_2026-05-04.md` | Plan for preventing glossary/Pāli marginalia from contaminating legacy media shortcode URLs before preservation. |
| `docs/FlagFix/FLAGFIX_022B_MEDIA_EVIDENCE_MARKUP_PLAN_2026-05-04.md` | Plan for normalizing structurally invalid parent contexts around `axis-media-evidence` blocks. |

---

## Current Decision

No immediate implementation is recommended.

No rebuild is authorized yet.

No manual CSL edits are authorized.

No manual static-site edits are authorized.

Future implementation must happen in separate PRs.

Future rebuild/static-site publication requires explicit approval.

---

## Recommended Future Order

### Step 1 — Implement 022A Source Protection First

Implement `FLAGFIX_022A` source protection before markup normalization.

Corrupted URLs should be prevented before normalizing surrounding evidence markup. This keeps the data protection problem separate from the layout/structure problem.

Expected focus:

- protect legacy media shortcode URLs before glossary/Pāli marginalia;
- preserve valid media evidence links;
- keep corrupted evidence auditable when a source cannot be safely recovered;
- avoid manual CSL or static-site page edits.

### Step 2 — Implement 022B Markup Normalization Second

Implement `FLAGFIX_022B` after the URL protection strategy is stable.

The markup normalization pass should focus on structurally safe placement of `axis-media-evidence` blocks.

Expected focus:

- move or emit evidence blocks outside invalid parent wrappers;
- avoid placing block-level evidence inside inline or list-only contexts;
- preserve consistent screen and print review behavior;
- avoid mixing URL hardening logic into markup normalization.

### Step 3 — Run Approved Rebuild/Publication Last

Run an approved rebuild/static-site publication only after source hardening is reviewed.

A source patch alone will not update current published/static output.

Publication must be explicit, reviewable, and scoped to the approved implementation.

---

## Risk Gate Before Implementation

Before any implementation PR, require:

- branch from clean `main`;
- read-only confirmation of current counts;
- explicit candidate files;
- explicit rebuild/publication decision;
- rollback plan.

Implementation PRs should also state whether the PR is source-only or includes approved static-site output.

---

## Guardrails

This roadmap does not authorize:

- changes to `pipeline/13-ssg/src/renderers/post_renderer.py`;
- changes to `pipeline/13-ssg/build.py`;
- CSS changes;
- JavaScript changes;
- template changes;
- CSL changes;
- renderer or pipeline functional changes;
- metadata changes;
- navigation changes;
- deployment or Cloudflare configuration changes;
- static-site output changes;
- manual static-site page edits.

No rebuild/static-site output publication is authorized by this roadmap.

No manual CSL edits are authorized by this roadmap.

---

## Next Review Gate

Future work should proceed through dedicated implementation PRs.

Recommended sequence:

1. `FLAGFIX_022A` implementation PR.
2. `FLAGFIX_022B` implementation PR.
3. Approved rebuild/static-site publication PR or explicitly approved publication step.

Do not combine these steps unless explicitly approved before implementation begins.
