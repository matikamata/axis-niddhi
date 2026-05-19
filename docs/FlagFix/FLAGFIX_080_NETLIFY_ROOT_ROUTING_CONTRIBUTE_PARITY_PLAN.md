# FlagFix 080 - Netlify root routing and CONTRIBUTE CTA parity plan

Date: 2026-05-19

## Summary of #079 Findings

#FlagFix_079 established that the `CONTRIBUTE` / `COLABORAR` CTA is present in the approved local payload, but it does not appear on the Netlify public root URL.

Key findings carried forward:

- Local published payload contains `CONTRIBUTE` in `welcome.html`.
- Local published payload contains `contribute.html`.
- Local `index.html` does not contain the contribution CTA.
- Cloudflare public root `/` redirects to `/welcome`, so the root surface shows the CTA.
- Netlify public root `/` serves an index-style page directly, so the CTA is absent there.
- Netlify `/welcome`, `/welcome.html`, and `/contribute.html` do contain the contribution surface.

Conclusion:

- The issue is root routing and landing-surface parity.
- The issue is not the absence of the contribution page.

## Root Cause

The current Vitrine structure relies on a host-level redirect for the desired landing experience:

- `_redirects` contains `/ /welcome 302`
- `welcome.html` is the surface with the contribution CTA
- `index.html` is a different surface without the contribution CTA

This is fragile because different hosts may not honor or prioritize the root redirect in the same way when `index.html` also exists.

Evidence from the SSG source confirms the intended model:

- [index_renderer.py](/home/sanghop/axis/axis-niddhi-production/pipeline/13-ssg/src/renderers/index_renderer.py:8)
  - `index.html <- templates/welcome.html`
  - `archive.html <- templates/index.html`

However, the current generated/static state in the repo shows:

- `pipeline/13-static-site/index.html` is not the same as `pipeline/13-static-site/welcome.html`
- `welcome.html` includes `CONTRIBUTE`
- `index.html` does not

That mismatch is the direct source of the parity risk.

## Inspected Files

Production repo:

- `pipeline/13-static-site/_redirects`
- `pipeline/13-static-site/index.html`
- `pipeline/13-static-site/welcome.html`
- `pipeline/13-static-site/contribute.html`
- `pipeline/13-ssg/templates/index.html`
- `pipeline/13-ssg/templates/welcome.html`
- `pipeline/13-ssg/src/renderers/index_renderer.py`

Published payload:

- `pipeline/13-static-site/_redirects`
- `pipeline/13-static-site/index.html`
- `pipeline/13-static-site/welcome.html`
- `pipeline/13-static-site/contribute.html`

## Local File Findings

Production static:

- `_redirects`: `/ /welcome 302`
- `index.html`: contains `ENTER ARCHIVE` and `ACESSAR ACERVO`, but not `CONTRIBUTE`
- `welcome.html`: contains:
  - `ENTER ARCHIVE`
  - `CONTRIBUTE`
  - `ACESSAR ACERVO`
  - `COLABORAR`
- `contribute.html`: exists and links back to `welcome.html`

Published static:

- Same relevant shape as production for these front files:
  - `_redirects` present
  - `index.html` without `CONTRIBUTE`
  - `welcome.html` with `CONTRIBUTE`
  - `contribute.html` present

Template/source findings:

- `pipeline/13-ssg/templates/index.html` is the larger archive/library-oriented surface
- `pipeline/13-ssg/templates/welcome.html` is the discovery landing source
- Current generated root behavior is therefore too dependent on routing assumptions

## `index.html` vs `welcome.html` Diff Summary

Diff file:

- `/tmp/flagfix_080_index_vs_welcome.diff`

Diff length:

- `139` lines

Important differences:

- `welcome.html` includes the English and Portuguese contribution buttons
- `index.html` does not
- `welcome.html` has the approved CTA surface
- `index.html` has different copy, button set, and structure

This is not a tiny redirect-only discrepancy. These are materially different landing surfaces.

## Option Analysis

### Option A

Force root redirect `/ -> /welcome`.

Pros:

- Small conceptual change
- Preserves current CTA only in one place
- Minimal user-facing behavior change if routing works consistently

Cons:

- Relies on host-specific redirect behavior
- Fragile when `index.html` exists
- Already behaves differently across Cloudflare and Netlify
- Makes parity depend on deployment platform rather than on the payload itself

Portability:

- Weakest option across Netlify, Cloudflare, GitHub Pages, and basic local static serving

LABZ impact:

- None directly

Regeneration needed:

- Likely yes, if redirects or root files are changed later

### Option B

Make `index.html` and `welcome.html` both contain the approved CTA surface.

Pros:

- Root surface parity does not depend on redirects
- Safer across hosts
- Keeps back-compat for `/welcome`
- Makes the stable Vitrine experience explicit in both entry files

Cons:

- Duplicates landing logic unless templated carefully
- Requires deliberate source/template alignment

Portability:

- Strong

LABZ impact:

- None, if LABZ remains excluded from Vitrine scope

Regeneration needed:

- Yes, source-first then static output

### Option C

Make `index.html` the canonical welcome surface and keep `welcome.html` as alias/back-compat.

Pros:

- Cleanest long-term root model
- Root URL becomes authoritative
- Easier mental model for deployment targets

Cons:

- Requires clear SSG ownership of landing generation
- Slightly bigger implementation decision than just duplicating content
- Need to preserve `/welcome` compatibility intentionally

Portability:

- Strongest long-term option

LABZ impact:

- None, if Vitrine keeps LABZ excluded

Regeneration needed:

- Yes, source-first then static output

### Option D

Leave as-is.

Pros:

- No immediate work

Cons:

- Root parity remains broken
- Netlify root keeps omitting the approved CTA surface
- Host behavior remains inconsistent
- Future deploys remain confusing and harder to validate

Portability:

- Poor

LABZ impact:

- None

Regeneration needed:

- No

## Recommended Option

Recommended direction: `B / C`

Preferred product rule:

- `index.html` should render the same approved Vitrine landing surface as `welcome.html`
- `welcome.html` may remain as alias/back-compat
- Do not rely on host-specific root redirect behavior as the only path to the CTA

In practical terms:

- Treat root surface parity as a content/output problem first
- Treat redirect behavior as optional compatibility, not as the primary guarantee

## Proposed Implementation Sprint

`#FlagFix_081 — Align index and welcome Vitrine landing surface`

Proposed scope for that sprint:

- SSG/source first
- identify the authoritative landing template path
- make `index.html` and `welcome.html` intentionally aligned
- regenerate static output
- validate root CTA presence locally
- validate Netlify/Cloudflare parity after approved upload/deploy steps
- keep LABZ out of Vitrine unless separately approved

## LABZ Exclusion

LABZ is explicitly excluded from this parity fix.

This plan does not propose:

- promoting LABZ to Netlify/Vitrine
- changing LABZ CSS/HTML/JS
- using the closed flower preview work in the stable Vitrine

## Explicit Non-Actions

- No deploy
- No Netlify upload
- No push
- No build/pipeline run
- No DeepL call
- No translation
- No CSL changes
- No metadata CSV changes
- No `Translation_Control_Center.csv` changes
- No SP10/SP11 changes
- No sync/copy
- No `.gitignore` changes
- No `/home/sanghop/axis/axis-niddhi-published` changes
- No production static changes
- No website file changes
