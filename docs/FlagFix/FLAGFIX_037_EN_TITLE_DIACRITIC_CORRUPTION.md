# FlagFix 037 - EN Title Diacritic Corruption: BA.AA.004 Vipariṇāma

Date: 2026-05-18

## Scope

Observed URL:

- https://niddhi.pages.dev/pages/BA.AA.004/

Observed corrupted English title:

- `Viparie1B987Ama Two Meanings`

Expected English title:

- `Vipariṇāma Two Meanings`

This sprint started read-only and applied only one surgical metadata correction after the root cause was confirmed.

## Files Inspected

- `pipeline/09-csl/BA.AA.004/meta/identity.json`
- `pipeline/09-csl/BA.AA.004/meta/identity.json.bak`
- `pipeline/09-csl/BA.AA.004/source/en-US/content.html`
- `pipeline/09-csl/BA.AA.004/meta/semantic.json`
- `pipeline/metadata/PDPN_01_Operational.csv`
- `pipeline/metadata/Translation_Control_Center.csv`
- `pipeline/metadata/slug_map.json`
- `pipeline/13-static-site/pages/BA.AA.004/index.html`
- `pipeline/13-static-site/archive.html`
- `pipeline/13-static-site/index.json`
- `pipeline/13-static-site/search_index.json`

## Evidence

`pipeline/09-csl/BA.AA.004/meta/identity.json` contained:

```json
"en": "Viparie1B987Ama Two Meanings"
```

The body source at `pipeline/09-csl/BA.AA.004/source/en-US/content.html` already contained correct Unicode text, including `Vipariṇāma`.

The generated static artifacts also contain the corrupted title in page title, archive, and search/index JSON. The same generated page body contains the correct `Vipariṇāma`, confirming that the visible title problem came from metadata, not body content.

## Root Cause

Root cause for BA.AA.004:

- corrupted `identity.json` English title metadata;
- `titles.en_source` is `legacy_migration`;
- source body content is not corrupted;
- this is not a DeepL issue because PT translation is still null;
- this is not a renderer/template issue because the renderer is faithfully emitting the corrupted title metadata.

Related metadata files also show the corrupted ASCII/hex-like slug form, including `pipeline/metadata/Translation_Control_Center.csv` and `pipeline/metadata/slug_map.json`; those were inspected only and not modified in this sprint.

## Correction Applied

Changed only:

- `pipeline/09-csl/BA.AA.004/meta/identity.json`

From:

```json
"en": "Viparie1B987Ama Two Meanings"
```

To:

```json
"en": "Vipariṇāma Two Meanings"
```

No PT content or body content was changed.

Note: the CSL metadata directory does not appear in `git status` in this workspace, so this on-disk metadata correction is not reflected in the normal tracked diff.

## Corpus-Wide Audit

Pre-correction audit:

- checked: 748 identity files
- suspicious title hits: 24
- BA.AA.004 was one of the hits

Post-correction audit:

- checked: 748 identity files
- suspicious title hits: 23
- BA.AA.004 no longer appears

Remaining hits indicate this is likely a broader legacy metadata extraction/encoding issue, not an isolated BA.AA.004-only problem. They were not corrected in this sprint.

## Static Artifact Status

Static artifacts remain stale because no build, pipeline, regeneration, deployment, or Vitrine promotion was run.

Known stale generated locations include:

- `pipeline/13-static-site/pages/BA.AA.004/index.html`
- `pipeline/13-static-site/archive.html`
- `pipeline/13-static-site/index.json`
- `pipeline/13-static-site/search_index.json`

These should update only during an approved future static regeneration/promotion batch.

## No-Change Confirmations

- Did not touch `/home/sanghop/axis/axis-niddhi-published`.
- Did not update Netlify/Vitrine.
- Did not run build, pipeline, or deploy.
- Did not call DeepL.
- Did not translate anything.
- Did not modify PT content.
- Did not modify `Translation_Control_Center.csv`.
- Did not modify SP10/SP11 behavior.
