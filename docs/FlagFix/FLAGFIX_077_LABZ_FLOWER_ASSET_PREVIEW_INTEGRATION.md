# FlagFix 077 - LABZ flower asset preview integration

Date: 2026-05-19

## Purpose

Integrate the two approved compressed LABZ flower WebP candidates into the LABZ ambient side layer for Cloudflare/production preview.

This is a preview integration only. It does not promote anything to Netlify/Vitrine.

## Source Assets

External source directory:

`/home/sanghop/axis/labz-ambient-candidates/flagfix_076_compressed_flowers/`

Approved assets copied:

| Asset | Size | SHA256 |
| --- | ---: | --- |
| `labz-ora-pro-nobis-left-mvp-01.webp` | 89046 bytes | `590ad14895dc5a394683d6f4b2a5bea174d50e5851a77a7e949038e87e4f1016` |
| `labz-lily-right-mvp-01.webp` | 85962 bytes | `4e0d1c419bfabcb9a69309622a7378d20a583e01a4f1e8b0d3b45a92e6206bb0` |

## Repo Asset Paths

SSG source assets:

- `pipeline/13-ssg/static/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
- `pipeline/13-ssg/static/assets/labz/labz-lily-right-mvp-01.webp`

Generated static assets:

- `pipeline/13-static-site/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
- `pipeline/13-static-site/assets/labz/labz-lily-right-mvp-01.webp`

The generated static hashes match the SSG source hashes.

## CSS Integration

Updated:

- `pipeline/13-ssg/static/css/style.css`

Behavior:

- LABZ-only selectors remain under `body[data-theme="stardust"]`.
- The left ambient side uses `labz-ora-pro-nobis-left-mvp-01.webp`.
- The right ambient side uses `labz-lily-right-mvp-01.webp`.
- Decorative side visuals remain outside the main reading flow.
- `pointer-events: none` is preserved.
- Existing mobile/narrow viewport hiding remains in place.
- Existing print hiding remains in place.
- Existing reduced-motion guard remains in place.
- No bee assets were integrated.

## Build Result

Command used:

```bash
python3 pipeline/13-ssg/build.py
```

Result:

- Status: `BUILD COMPLETO`
- Posts total: `748`
- PT-BR: `309 / 748`
- Rebuilt: `748`
- Skipped: `0`
- Errors: `0`
- Build ID: `bce88834c4eac268`
- Engine: `3.0.2-S14-S15-C1-C3`

## Verification

Static asset existence:

- `pipeline/13-static-site/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`: exists
- `pipeline/13-static-site/assets/labz/labz-lily-right-mvp-01.webp`: exists

CSS references:

- Source CSS references both WebP assets.
- Generated static CSS references both WebP assets.

String checks:

- Stale strings absent from targeted static checks:
  - `Vivendo il Dhamma`
  - `Viparie1B987Ama Two Meanings`
  - `pending translation / pendente de tradução`
- Corrected strings present in targeted static checks:
  - `Vivendo o Dhamma`
  - `Vipariṇāma Two Meanings`
  - `Awaiting translation / Aguardando tradução`

Path scope:

- Result: `PATH_SCOPE_OK`
- Changed paths are limited to the approved SSG asset/CSS paths, generated static output, build cache, and this report.

Claim-language scan:

- Result: `NO_FORBIDDEN_CLAIM_LANGUAGE`

## Non-Actions

- No Netlify/Vitrine update.
- No `/home/sanghop/axis/axis-niddhi-published` changes.
- No deploy or manual upload.
- No DeepL call.
- No translation.
- No CSL changes.
- No metadata CSV changes.
- No `Translation_Control_Center.csv` changes.
- No SP10/SP11 changes.
- No bee asset integration.

## Recommendation

`READY FOR CLOUDFLARE PREVIEW AFTER PR MERGE`

After merge, review the LABZ/stardust mode visually in Cloudflare/dev before considering any future Netlify/Vitrine promotion.
